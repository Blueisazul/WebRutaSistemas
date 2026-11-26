"""Controlled multisource acquisition runner for Ruta Sistemas (R4-01).

Coordinates fail-closed fetching, Schema 2 normalization, field evidence attachment,
deterministic deduplication, candidate validation, and staging persistence for approved
ATS sources. Does NOT write to the canonical seed catalog or the snapshot catalog.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from collector.ats_connectors import (
    fetch_greenhouse_board,
    fetch_lever_board,
    transform_greenhouse_payload,
    transform_lever_payload,
)
from collector.pe_connectors import (
    fetch_defensoria_cas,
    fetch_gobpe_convocatorias,
    fetch_hiringroom_board,
    fetch_ositran_convocatorias,
    transform_defensoria_html,
    transform_gobpe_indecopi_html,
    transform_hiringroom_html,
    transform_ositran_html,
)
from collector.classification import classify_candidate
from collector.dedup import (
    EXACT_DUPLICATE,
    IDENTIFIER_COLLISION,
    POSSIBLE_DUPLICATE,
    deduplicate_candidates,
    extract_fields,
    load_inbox_candidates,
    load_seed_opportunities,
    normalize_identifier,
    normalize_text,
)
from collector.evidence import verify_candidates_evidence
from collector.policy import find_source, load_source_registry
from validate_candidates import validate_payload

LIMA_TIMEZONE = timezone(timedelta(hours=-5))

SEED_CATALOG_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_CATALOG_PATH = ROOT / "data" / "opportunities.json"
DEFAULT_INBOX_PATH = ROOT / "data" / "candidates" / "inbox.local.json"
SOURCES_REGISTRY_PATH = ROOT / "collector" / "sources.json"

PROTECTED_PATHS = {
    SEED_CATALOG_PATH.resolve(),
    SNAPSHOT_CATALOG_PATH.resolve(),
    SOURCES_REGISTRY_PATH.resolve(),
}


def _atomic_write_json(path: Path, data: Any) -> None:
    """Atomically writes JSON using a temporary file in the same directory."""
    path_resolved = path.resolve()
    if path_resolved in PROTECTED_PATHS:
        raise PermissionError(f"Escritura prohibida en ruta canónica protegida: '{path}'")

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    )
    try:
        json.dump(data, temp_file, indent=2, ensure_ascii=False)
        temp_file.write("\n")
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        os.replace(temp_file.name, str(path))
    except Exception:
        if os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass
        raise


@dataclass
class SourceRunSummary:
    source_id: str
    employer: str
    connector: str
    status: str  # "success", "failed", "skipped"
    captured: int = 0
    filtered_in: int = 0
    discarded: int = 0
    duplicates: int = 0
    new_candidates: int = 0
    error: str | None = None
    discarded_details: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AcquisitionReport:
    timestamp: str
    as_of: str
    dry_run: bool
    sources_evaluated: int
    sources_succeeded: int
    sources_failed: int
    total_captured: int
    total_filtered: int
    total_discarded: int
    total_duplicates: int
    total_new_staged: int
    source_summaries: list[SourceRunSummary]
    validation_passed: bool
    validation_errors: list[str]
    validation_warnings: list[str]
    new_candidates: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "asOf": self.as_of,
            "dryRun": self.dry_run,
            "metrics": {
                "sourcesEvaluated": self.sources_evaluated,
                "sourcesSucceeded": self.sources_succeeded,
                "sourcesFailed": self.sources_failed,
                "totalCaptured": self.total_captured,
                "totalFiltered": self.total_filtered,
                "totalDiscarded": self.total_discarded,
                "totalDuplicates": self.total_duplicates,
                "totalNewStaged": self.total_new_staged,
            },
            "validation": {
                "passed": self.validation_passed,
                "errorCount": len(self.validation_errors),
                "warningCount": len(self.validation_warnings),
                "errors": self.validation_errors,
                "warnings": self.validation_warnings,
            },
            "sources": [
                {
                    "sourceId": s.source_id,
                    "employer": s.employer,
                    "connector": s.connector,
                    "status": s.status,
                    "captured": s.captured,
                    "filteredIn": s.filtered_in,
                    "discarded": s.discarded,
                    "duplicates": s.duplicates,
                    "newCandidates": s.new_candidates,
                    "error": s.error,
                    "discardedDetails": s.discarded_details,
                }
                for s in self.source_summaries
            ],
            "stagedCandidateIds": [c["candidateId"] for c in self.new_candidates],
        }


def filter_candidate_for_target_profile(
    candidate: dict,
    source: dict,
) -> tuple[bool, str | None, dict | None]:
    """Evaluates candidate opportunity against target profile and geographic eligibility.

    Applies deterministic, explainable classification:
    - Analyzes title, location, mode, and employer.
    - Classifies along three axes: relevance, geographicEligibility, experienceTier.
    - Returns (is_eligible, reason, classification_dict).
    """
    proposed = candidate.get("proposed") or {}
    title = proposed.get("title")
    location = proposed.get("location")
    mode = proposed.get("mode")
    employer = proposed.get("employer")

    res = classify_candidate(
        title=title,
        location=location,
        mode=mode,
        employer=employer,
    )

    cls_dict = res.to_dict()

    if not res.is_staging_eligible:
        reason_parts = []
        if res.relevance in ("NOT_RELEVANT", "UNDEMONSTRATED"):
            reason_parts.append(res.relevance_reason)
        if res.geographic_eligibility in ("NOT_ELIGIBLE", "UNKNOWN"):
            reason_parts.append(res.geography_reason)
        full_reason = " | ".join(reason_parts) if reason_parts else "Descartado por perfil no afín a sistemas o jurisdicción inelegible."
        return False, full_reason, cls_dict

    return True, None, cls_dict


def _load_existing_inbox_data(inbox_path: Path) -> tuple[dict, list[dict], set[str], set[str], set[str]]:
    """Loads existing inbox payload and builds lookup sets for deduplication."""
    if not inbox_path.exists():
        inbox_payload = {"schemaVersion": 1, "candidates": []}
        return inbox_payload, [], set(), set(), set()

    try:
        data = json.loads(inbox_path.read_text(encoding="utf-8"))
    except Exception as err:
        raise ValueError(f"No se pudo cargar la bandeja de staging '{inbox_path}': {err}")

    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        raise ValueError(f"Formato inválido de bandeja en '{inbox_path}': se requiere schemaVersion=1 y lista 'candidates'")

    candidates = data["candidates"]
    existing_ids: set[str] = set()
    existing_primary_keys: set[str] = set()
    existing_employer_refs: set[str] = set()

    for c in candidates:
        if not isinstance(c, dict):
            continue
        c_id = c.get("candidateId")
        if c_id:
            existing_ids.add(str(c_id))
        s_id = str(c.get("sourceId") or "").strip().casefold()
        proposed = c.get("proposed") or {}
        ext_ref = normalize_identifier(proposed.get("externalReference"))
        if s_id and ext_ref:
            existing_primary_keys.add(f"{s_id}:{ext_ref}")
        emp = normalize_text(proposed.get("employer"))
        if emp and ext_ref:
            existing_employer_refs.add(f"{emp}:{ext_ref}")

    return data, candidates, existing_ids, existing_primary_keys, existing_employer_refs


def _load_canonical_seed_keys(seed_path: Path) -> tuple[set[str], set[str]]:
    """Loads primary and employer keys from the canonical seed catalog."""
    if not seed_path.exists():
        return set(), set()
    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
    except Exception:
        return set(), set()

    opps = data.get("opportunities") if isinstance(data, dict) else []
    seed_keys: set[str] = set()
    seed_emp_refs: set[str] = set()
    for opp in opps:
        if not isinstance(opp, dict):
            continue
        req = normalize_identifier(opp.get("requisition"))
        s_id = str(opp.get("sourceKind") or "").strip().casefold()
        emp = normalize_text(opp.get("employer"))
        if s_id and req:
            seed_keys.add(f"{s_id}:{req}")
        if emp and req:
            seed_emp_refs.add(f"{emp}:{req}")

    return seed_keys, seed_emp_refs


def run_pilot_acquisition(
    *,
    source_ids: list[str] | None = None,
    inbox_path: Path = DEFAULT_INBOX_PATH,
    seed_path: Path = SEED_CATALOG_PATH,
    fixtures_dir: Path | None = None,
    as_of: date | None = None,
    dry_run: bool = False,
    override_sources_registry: dict | None = None,
) -> AcquisitionReport:
    """Executes a controlled, reproducible multisource acquisition run."""
    now_dt = datetime.now(LIMA_TIMEZONE)
    as_of_date = as_of or now_dt.date()
    captured_at_str = now_dt.isoformat(timespec="seconds")

    registry = override_sources_registry or load_source_registry()
    all_sources = registry.get("sources", [])

    # 1. Determine target sources
    if source_ids:
        target_sources = []
        for sid in source_ids:
            found = find_source(registry, sid)
            if not found:
                raise ValueError(f"La fuente solicitada '{sid}' no existe en collector/sources.json")
            target_sources.append(found)
    else:
        # Select all enabled pilot sources
        target_sources = [
            s for s in all_sources
            if s.get("enabled") is True
            and s.get("decision") == "approved"
            and s.get("connector") in (
                "greenhouse-job-board",
                "lever-postings",
                "ositran-portal",
                "defensoria-cas",
                "hiringroom-board",
                "gobpe-convocatorias",
            )
        ]

    # 2. Load existing staging inbox and canonical seed data
    inbox_payload, existing_candidates, existing_ids, existing_pks, existing_emp_refs = _load_existing_inbox_data(inbox_path)
    seed_keys, seed_emp_refs = _load_canonical_seed_keys(seed_path)

    source_summaries: list[SourceRunSummary] = []
    new_candidates_all: list[dict] = []
    run_batch_ids: set[str] = set()
    run_batch_pks: set[str] = set()

    total_captured = 0
    total_filtered = 0
    total_discarded = 0
    total_duplicates = 0

    # 3. Process each target source independently (failure isolation)
    for source in target_sources:
        s_id = source.get("id", "unknown")
        employer = source.get("employer", "Desconocido")
        connector = source.get("connector", "desconocido")
        summary = SourceRunSummary(
            source_id=s_id,
            employer=employer,
            connector=connector,
            status="pending",
        )

        try:
            raw_candidates: list[dict] = []

            # Check if offline fixture is available
            fixture_loaded = False
            if fixtures_dir:
                fixture_file = fixtures_dir / f"{s_id}.json"
                if not fixture_file.exists():
                    fixture_file = fixtures_dir / f"{s_id}.html"
                if not fixture_file.exists():
                    # Fallback to general ats fixture matching connector
                    if connector == "greenhouse-job-board":
                        fixture_file = fixtures_dir / "greenhouse_complete.json"
                    elif connector == "lever-postings":
                        fixture_file = fixtures_dir / "lever_complete.json"
                    elif connector == "ositran-portal":
                        fixture_file = fixtures_dir / "ositran_sample.html"
                    elif connector == "defensoria-cas":
                        fixture_file = fixtures_dir / "defensoria_sample.html"
                    elif connector == "hiringroom-board":
                        fixture_file = fixtures_dir / "hiringroom_sample.html"
                    elif connector == "gobpe-convocatorias":
                        fixture_file = fixtures_dir / "gobpe-indecopi-convocatorias.html"

                if fixture_file.exists():
                    if connector == "greenhouse-job-board":
                        fixture_data = json.loads(fixture_file.read_text(encoding="utf-8"))
                        raw_candidates = transform_greenhouse_payload(
                            source,
                            fixture_data,
                            captured_at=captured_at_str,
                        )
                    elif connector == "lever-postings":
                        fixture_data = json.loads(fixture_file.read_text(encoding="utf-8"))
                        raw_candidates = transform_lever_payload(
                            source,
                            fixture_data,
                            captured_at=captured_at_str,
                        )
                    elif connector == "ositran-portal":
                        html_text = fixture_file.read_text(encoding="utf-8")
                        raw_candidates = transform_ositran_html(
                            source,
                            html_text,
                            captured_at=captured_at_str,
                        )
                    elif connector == "defensoria-cas":
                        html_text = fixture_file.read_text(encoding="utf-8")
                        raw_candidates = transform_defensoria_html(
                            source,
                            html_text,
                            captured_at=captured_at_str,
                        )
                    elif connector == "hiringroom-board":
                        html_text = fixture_file.read_text(encoding="utf-8")
                        raw_candidates = transform_hiringroom_html(
                            source,
                            html_text,
                            captured_at=captured_at_str,
                        )
                    elif connector == "gobpe-convocatorias":
                        html_text = fixture_file.read_text(encoding="utf-8")
                        raw_candidates = transform_gobpe_indecopi_html(
                            source,
                            html_text,
                            captured_at=captured_at_str,
                        )
                    fixture_loaded = True

            # If no fixture loaded, execute real fetch
            if not fixture_loaded:
                if connector == "greenhouse-job-board":
                    raw_candidates = fetch_greenhouse_board(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                elif connector == "lever-postings":
                    raw_candidates = fetch_lever_board(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                elif connector == "ositran-portal":
                    raw_candidates = fetch_ositran_convocatorias(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                elif connector == "defensoria-cas":
                    raw_candidates = fetch_defensoria_cas(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                elif connector == "hiringroom-board":
                    raw_candidates = fetch_hiringroom_board(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                elif connector == "gobpe-convocatorias":
                    raw_candidates = fetch_gobpe_convocatorias(
                        source,
                        request_count=0,
                        captured_at=captured_at_str,
                    )
                else:
                    raise ValueError(f"Conector no soportado: '{connector}'")

            summary.captured = len(raw_candidates)
            total_captured += summary.captured

            # 4. Filter and deduplicate candidates
            for cand in raw_candidates:
                # Eligibility / target profile filter
                is_eligible, discard_reason, classification_meta = filter_candidate_for_target_profile(cand, source)
                if classification_meta:
                    cand["classification"] = classification_meta

                if not is_eligible:
                    summary.discarded += 1
                    total_discarded += 1
                    summary.discarded_details.append({
                        "candidateId": cand.get("candidateId", ""),
                        "title": cand.get("proposed", {}).get("title", ""),
                        "reason": discard_reason or "Descartado por criterio editorial",
                    })
                    continue

                summary.filtered_in += 1
                total_filtered += 1

                # Deduplication evaluation
                c_id = cand["candidateId"]
                s_key = f"{cand.get('sourceId', '').strip().casefold()}:{normalize_identifier(cand.get('proposed', {}).get('externalReference'))}"
                e_key = f"{normalize_text(cand.get('proposed', {}).get('employer'))}:{normalize_identifier(cand.get('proposed', {}).get('externalReference'))}"

                # Check if already seen in current run batch
                if c_id in run_batch_ids or (s_key and s_key in run_batch_pks):
                    summary.duplicates += 1
                    total_duplicates += 1
                    continue

                # Check if already exists in staging inbox
                if c_id in existing_ids or (s_key and s_key in existing_pks) or (e_key and e_key in existing_emp_refs):
                    summary.duplicates += 1
                    total_duplicates += 1
                    continue

                # Check if already present in canonical seed catalog
                if (s_key and s_key in seed_keys) or (e_key and e_key in seed_emp_refs):
                    summary.duplicates += 1
                    total_duplicates += 1
                    continue

                # Candidate is genuinely new!
                summary.new_candidates += 1
                new_candidates_all.append(cand)
                run_batch_ids.add(c_id)
                if s_key:
                    run_batch_pks.add(s_key)

            summary.status = "success"

        except Exception as err:
            summary.status = "failed"
            summary.error = str(err)

        source_summaries.append(summary)

    sources_succeeded = sum(1 for s in source_summaries if s.status == "success")
    sources_failed = sum(1 for s in source_summaries if s.status == "failed")

    # 5. Full validation of combined staging candidates
    combined_candidates = existing_candidates + new_candidates_all
    validation_payload = {
        "schemaVersion": 1,
        "candidates": combined_candidates,
    }

    val_errors, val_warnings = validate_payload(
        validation_payload,
        sources=registry,
        today=as_of_date,
    )

    validation_passed = (len(val_errors) == 0)

    # 6. Freshness and evidence verification of new candidates
    if new_candidates_all:
        evidence_reports = verify_candidates_evidence(
            new_candidates_all,
            sources=registry,
            as_of=as_of_date,
        )
        for rep in evidence_reports:
            if rep.structural_status == "STRUCTURAL_INVALID":
                val_errors.extend(rep.errors)
                validation_passed = False

    # 7. Safe atomic staging persistence (never writes to canonical files)
    if validation_passed and not dry_run and new_candidates_all:
        inbox_payload["candidates"] = combined_candidates
        _atomic_write_json(inbox_path, inbox_payload)

    return AcquisitionReport(
        timestamp=captured_at_str,
        as_of=as_of_date.isoformat(),
        dry_run=dry_run,
        sources_evaluated=len(target_sources),
        sources_succeeded=sources_succeeded,
        sources_failed=sources_failed,
        total_captured=total_captured,
        total_filtered=total_filtered,
        total_discarded=total_discarded,
        total_duplicates=total_duplicates,
        total_new_staged=len(new_candidates_all) if validation_passed and not dry_run else 0,
        source_summaries=source_summaries,
        validation_passed=validation_passed,
        validation_errors=val_errors,
        validation_warnings=val_warnings,
        new_candidates=new_candidates_all,
    )
