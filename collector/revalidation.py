"""Opportunity and Candidate Lifecycle Management & Revalidation for Ruta Sistemas (R4-03).

Provides:
- Re-querying configured ATS sources (Greenhouse and Lever).
- Change detection (title, location, mode, applyUrl, salary, benefits, requirements).
- Conservative lifecycle tracking (safeguard against mass closure on network error).
- Disappearance tracking (distinguishing single-fetch transient drop from confirmed closure).
- Temporal validity (deadline expiration) and evidence freshness (TTL verification).
- Strict non-mutation of canonical catalog files.
"""

from __future__ import annotations

import copy
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
from collector.dedup import normalize_identifier, normalize_text
from collector.evidence import (
    DEFAULT_TTL_DAYS,
    is_valid_https_url,
    parse_iso_date,
    parse_iso_timestamp,
)
from collector.policy import find_source, load_source_registry

LIMA_TIMEZONE = timezone(timedelta(hours=-5))

# Lifecycle state constants
STATE_STILL_ACTIVE = "STILL_ACTIVE"
STATE_CHANGED = "CHANGED"
STATE_DISAPPEARED_ONCE = "DISAPPEARED_ONCE"
STATE_CONFIRMED_DISAPPEARED = "CONFIRMED_DISAPPEARED"
STATE_PRESERVED_ON_SOURCE_ERROR = "PRESERVED_ON_SOURCE_ERROR"
STATE_UNKNOWN = "UNKNOWN"

RELEVANT_COMPARISON_FIELDS = (
    "title",
    "location",
    "mode",
    "applyUrl",
    "salary",
    "benefits",
    "requirements",
)

SEED_CATALOG_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_CATALOG_PATH = ROOT / "data" / "opportunities.json"
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
class FieldChange:
    field: str
    previous_value: Any
    current_value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "previous": self.previous_value,
            "current": self.current_value,
        }


@dataclass
class CandidateRevalidationResult:
    candidate_id: str
    source_id: str
    external_reference: str
    title: str
    lifecycle_state: str
    consecutive_missing_count: int
    changes: list[FieldChange] = field(default_factory=list)
    last_observed_at: str | None = None
    deadline_status: str = "DEADLINE_UNKNOWN"
    deadline: str | None = None
    evidence_freshness: str = "FRESH"
    notes: list[str] = field(default_factory=list)
    recommended_action: str = "CONTINUE_MONITORING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "sourceId": self.source_id,
            "externalReference": self.external_reference,
            "title": self.title,
            "lifecycleState": self.lifecycle_state,
            "consecutiveMissingCount": self.consecutive_missing_count,
            "changes": [c.to_dict() for c in self.changes],
            "lastObservedAt": self.last_observed_at,
            "deadlineStatus": self.deadline_status,
            "deadline": self.deadline,
            "evidenceFreshness": self.evidence_freshness,
            "notes": self.notes,
            "recommendedAction": self.recommended_action,
        }


@dataclass
class SourceRevalidationSummary:
    source_id: str
    employer: str
    connector: str
    status: str  # "success", "failed", "skipped"
    total_evaluated: int = 0
    still_active: int = 0
    changed: int = 0
    disappeared_once: int = 0
    confirmed_disappeared: int = 0
    preserved_on_error: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sourceId": self.source_id,
            "employer": self.employer,
            "connector": self.connector,
            "status": self.status,
            "totalEvaluated": self.total_evaluated,
            "stillActive": self.still_active,
            "changed": self.changed,
            "disappearedOnce": self.disappeared_once,
            "confirmedDisappeared": self.confirmed_disappeared,
            "preservedOnError": self.preserved_on_error,
            "error": self.error,
        }


@dataclass
class RevalidationReport:
    timestamp: str
    as_of: str
    sources_evaluated: int
    sources_succeeded: int
    sources_failed: int
    total_candidates_evaluated: int
    still_active_count: int
    changed_count: int
    disappeared_once_count: int
    confirmed_disappeared_count: int
    preserved_on_error_count: int
    deadline_expired_count: int
    evidence_stale_count: int
    source_summaries: list[SourceRevalidationSummary]
    candidate_results: list[CandidateRevalidationResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "asOf": self.as_of,
            "summary": {
                "sourcesEvaluated": self.sources_evaluated,
                "sourcesSucceeded": self.sources_succeeded,
                "sourcesFailed": self.sources_failed,
                "totalCandidatesEvaluated": self.total_candidates_evaluated,
                "stillActive": self.still_active_count,
                "changed": self.changed_count,
                "disappearedOnce": self.disappeared_once_count,
                "confirmedDisappeared": self.confirmed_disappeared_count,
                "preservedOnError": self.preserved_on_error_count,
                "deadlineExpired": self.deadline_expired_count,
                "evidenceStale": self.evidence_stale_count,
            },
            "sourceSummaries": [s.to_dict() for s in self.source_summaries],
            "candidateResults": [c.to_dict() for c in self.candidate_results],
        }


def detect_field_differences(
    current_proposed: dict,
    fresh_proposed: dict,
    fields_to_compare: tuple[str, ...] = RELEVANT_COMPARISON_FIELDS,
) -> list[FieldChange]:
    """Compares relevant fields between an existing candidate and fresh ATS data.

    Returns a list of FieldChange instances representing actual modifications.
    Considers normalization to prevent false positives due to whitespace or trailing characters.
    Avoids false positives when fresh list endpoints omit optional fields (e.g. requirements/benefits).
    """
    changes: list[FieldChange] = []
    for f in fields_to_compare:
        val_cur = current_proposed.get(f)
        val_fresh = fresh_proposed.get(f)

        # Normalize strings for comparison
        norm_cur = normalize_text(val_cur) if isinstance(val_cur, str) else val_cur
        norm_fresh = normalize_text(val_fresh) if isinstance(val_fresh, str) else val_fresh

        # If fresh data provides a value that differs from current value
        if norm_fresh is not None and norm_cur != norm_fresh:
            changes.append(FieldChange(
                field=f,
                previous_value=val_cur,
                current_value=val_fresh,
            ))
        elif norm_fresh is None and norm_cur is not None and f in ("title", "applyUrl", "location"):
            # Core field disappeared from fresh data
            changes.append(FieldChange(
                field=f,
                previous_value=val_cur,
                current_value=val_fresh,
            ))
    return changes


def evaluate_temporal_freshness(
    candidate: dict,
    as_of_date: date,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> tuple[str, str | None, str, list[str]]:
    """Evaluates deadline expiration and evidence freshness for a candidate.

    Returns:
        (deadline_status, deadline_str, freshness_status, notes)
    """
    proposed = candidate.get("proposed") or {}
    notes: list[str] = []

    # 1. Deadline check
    raw_deadline = proposed.get("deadline")
    deadline_str = None
    if raw_deadline:
        parsed_deadline = parse_iso_date(raw_deadline)
        if parsed_deadline:
            deadline_str = parsed_deadline.isoformat()
            if parsed_deadline < as_of_date:
                deadline_status = "DEADLINE_EXPIRED"
                notes.append(f"Fecha límite de postulación superada ({deadline_str} < {as_of_date.isoformat()})")
            elif parsed_deadline == as_of_date:
                deadline_status = "DEADLINE_REACHED"
                notes.append(f"Fecha límite de postulación concluye hoy ({deadline_str})")
            else:
                deadline_status = "DEADLINE_FUTURE"
        else:
            deadline_status = "DEADLINE_INVALID"
            notes.append(f"Fecha deadline no válida: '{raw_deadline}'")
    else:
        deadline_status = "DEADLINE_UNKNOWN"

    # 2. Evidence freshness check
    raw_evidence = candidate.get("fieldEvidence") or []
    stale_before = as_of_date - timedelta(days=ttl_days)
    has_fresh = False
    has_stale = False
    has_evidence = False

    for item in raw_evidence:
        if not isinstance(item, dict):
            continue
        has_evidence = True
        obs_raw = item.get("observedAt")
        if not obs_raw:
            continue
        parsed_dt = parse_iso_timestamp(obs_raw)
        if parsed_dt:
            obs_date = parsed_dt.astimezone(LIMA_TIMEZONE).date()
            if obs_date < stale_before:
                has_stale = True
            else:
                has_fresh = True

    if not has_evidence:
        freshness_status = "NO_EVIDENCE"
    elif has_fresh and not has_stale:
        freshness_status = "ALL_FRESH"
    elif has_fresh and has_stale:
        freshness_status = "PARTIALLY_STALE"
        notes.append(f"Parte de la evidencia superó el TTL de {ttl_days} días")
    elif has_stale and not has_fresh:
        freshness_status = "ALL_STALE"
        notes.append(f"Toda la evidencia superó el TTL de {ttl_days} días")
    else:
        freshness_status = "UNKNOWN"

    return deadline_status, deadline_str, freshness_status, notes


def revalidate_candidates(
    candidates: list[dict],
    *,
    sources_registry: dict | None = None,
    source_ids: list[str] | None = None,
    fixtures_dir: Path | None = None,
    as_of: date | None = None,
    consecutive_missing_threshold: int = 2,
    apply_updates: bool = False,
) -> tuple[RevalidationReport, list[dict]]:
    """Executes lifecycle revalidation and change detection over candidate records.

    Safeguards:
    - Never mutates canonical catalog files.
    - Source network errors/timeouts do NOT cause job closures (preserved on error).
    - Single-fetch disappearance is marked as DISAPPEARED_ONCE without closing.
    - Confirmed closure requires consecutive_missing >= threshold or explicit closure.

    Returns:
        (RevalidationReport, updated_candidates_list)
    """
    now_dt = datetime.now(LIMA_TIMEZONE)
    as_of_date = as_of or now_dt.date()
    revalidated_at_str = now_dt.isoformat(timespec="seconds")

    registry = sources_registry or load_source_registry()
    all_sources = registry.get("sources", [])
    source_by_id = {s["id"]: s for s in all_sources if isinstance(s, dict) and "id" in s}

    # Deep copy candidates to avoid mutating inputs when apply_updates is False
    working_candidates = copy.deepcopy(candidates)

    # Group candidates by sourceId
    candidates_by_source: dict[str, list[dict]] = {}
    for c in working_candidates:
        s_id = str(c.get("sourceId") or "unknown")
        candidates_by_source.setdefault(s_id, []).append(c)

    # Determine sources to evaluate
    if source_ids:
        target_source_ids = [sid for sid in source_ids if sid in source_by_id]
    else:
        target_source_ids = list(candidates_by_source.keys())

    source_summaries: list[SourceRevalidationSummary] = []
    candidate_results: list[CandidateRevalidationResult] = []

    still_active_total = 0
    changed_total = 0
    disappeared_once_total = 0
    confirmed_disappeared_total = 0
    preserved_on_error_total = 0
    deadline_expired_total = 0
    evidence_stale_total = 0

    for s_id in target_source_ids:
        source = source_by_id.get(s_id)
        if not source:
            continue

        cands_for_source = candidates_by_source.get(s_id, [])
        employer = str(source.get("employer") or "Desconocido")
        connector = str(source.get("connector") or "desconocido")
        ttl_days = int(source.get("verificationTtlDays", DEFAULT_TTL_DAYS))

        summary = SourceRevalidationSummary(
            source_id=s_id,
            employer=employer,
            connector=connector,
            status="pending",
            total_evaluated=len(cands_for_source),
        )

        fresh_by_ref: dict[str, dict] = {}
        fetch_error: str | None = None

        # 1. Fetch current board state
        try:
            raw_fresh: list[dict] = []
            fixture_loaded = False

            if fixtures_dir:
                fixture_file = fixtures_dir / f"{s_id}.json"
                if fixture_file.exists():
                    fixture_data = json.loads(fixture_file.read_text(encoding="utf-8"))
                    if connector == "greenhouse-job-board":
                        raw_fresh = transform_greenhouse_payload(source, fixture_data, captured_at=revalidated_at_str)
                    elif connector == "lever-postings":
                        raw_fresh = transform_lever_payload(source, fixture_data, captured_at=revalidated_at_str)
                    fixture_loaded = True

            if not fixture_loaded:
                if connector == "greenhouse-job-board":
                    raw_fresh = fetch_greenhouse_board(source, request_count=0, captured_at=revalidated_at_str)
                elif connector == "lever-postings":
                    raw_fresh = fetch_lever_board(source, request_count=0, captured_at=revalidated_at_str)
                else:
                    # Non-ATS connectors (e.g. manual-review, template) cannot be auto-fetched
                    raise ValueError(f"Conector '{connector}' no admite revalidación automatizada en red")

            # Map fresh postings by externalReference
            for f_cand in raw_fresh:
                ref = normalize_identifier(f_cand.get("proposed", {}).get("externalReference"))
                if ref:
                    fresh_by_ref[ref] = f_cand

            summary.status = "success"

        except Exception as err:
            # SOURCE FETCH FAILED: Network error, timeout, HTTP 5xx, or offline
            summary.status = "failed"
            summary.error = str(err)
            fetch_error = str(err)

        # 2. Evaluate each candidate of this source
        for cand in cands_for_source:
            c_id = str(cand.get("candidateId") or "unknown")
            proposed = cand.get("proposed") or {}
            ext_ref = normalize_identifier(proposed.get("externalReference")) or "unknown"
            title = str(proposed.get("title") or "Sin título")

            # Evaluate deadline and freshness
            deadline_st, dl_val, fresh_st, eval_notes = evaluate_temporal_freshness(
                cand, as_of_date=as_of_date, ttl_days=ttl_days
            )

            if deadline_st == "DEADLINE_EXPIRED":
                deadline_expired_total += 1
            if fresh_st in ("ALL_STALE", "PARTIALLY_STALE"):
                evidence_stale_total += 1

            # SAFEGUARD: If source fetch failed, preserve candidate state untouched
            if fetch_error is not None:
                summary.preserved_on_error += 1
                preserved_on_error_total += 1
                notes = list(eval_notes)
                notes.append(f"Fallo transitorio al consultar la fuente ({fetch_error}); estado preservado sin mutación.")

                result = CandidateRevalidationResult(
                    candidate_id=c_id,
                    source_id=s_id,
                    external_reference=ext_ref,
                    title=title,
                    lifecycle_state=STATE_PRESERVED_ON_SOURCE_ERROR,
                    consecutive_missing_count=int(cand.get("consecutiveMissingCount") or 0),
                    changes=[],
                    last_observed_at=cand.get("lastObservedAt") or cand.get("capturedAt"),
                    deadline_status=deadline_st,
                    deadline=dl_val,
                    evidence_freshness=fresh_st,
                    notes=notes,
                    recommended_action="RETRY_LATER",
                )
                candidate_results.append(result)
                continue

            # Source fetch SUCCEEDED: evaluate match against current board
            prev_missing_count = int(cand.get("consecutiveMissingCount") or 0)

            if ext_ref in fresh_by_ref:
                # Vacancy FOUND on source!
                fresh_match = fresh_by_ref[ext_ref]
                fresh_proposed = fresh_match.get("proposed") or {}

                # Detect changes in relevant fields
                detected_changes = detect_field_differences(proposed, fresh_proposed)

                if detected_changes:
                    summary.changed += 1
                    changed_total += 1
                    notes = list(eval_notes)
                    changed_fields_str = ", ".join(c.field for c in detected_changes)
                    notes.append(f"Se detectaron cambios en campos: {changed_fields_str}")

                    result = CandidateRevalidationResult(
                        candidate_id=c_id,
                        source_id=s_id,
                        external_reference=ext_ref,
                        title=title,
                        lifecycle_state=STATE_CHANGED,
                        consecutive_missing_count=0,
                        changes=detected_changes,
                        last_observed_at=revalidated_at_str,
                        deadline_status=deadline_st,
                        deadline=dl_val,
                        evidence_freshness="ALL_FRESH",
                        notes=notes,
                        recommended_action="REVIEW_CHANGES",
                    )

                    if apply_updates:
                        cand["consecutiveMissingCount"] = 0
                        cand["lastObservedAt"] = revalidated_at_str
                        cand["lifecycleStatus"] = STATE_CHANGED
                        # Apply fresh changes to proposed
                        for chg in detected_changes:
                            proposed[chg.field] = chg.current_value
                        # Update field evidence with fresh observation
                        field_ev = cand.setdefault("fieldEvidence", [])
                        apply_url = proposed.get("applyUrl") or cand.get("sourceUrl")
                        for chg in detected_changes:
                            field_ev.append({
                                "field": chg.field,
                                "url": apply_url,
                                "observedAt": revalidated_at_str,
                            })

                else:
                    summary.still_active += 1
                    still_active_total += 1
                    notes = list(eval_notes)
                    notes.append("Vacante reconfirmada activa con datos idénticos.")

                    result = CandidateRevalidationResult(
                        candidate_id=c_id,
                        source_id=s_id,
                        external_reference=ext_ref,
                        title=title,
                        lifecycle_state=STATE_STILL_ACTIVE,
                        consecutive_missing_count=0,
                        changes=[],
                        last_observed_at=revalidated_at_str,
                        deadline_status=deadline_st,
                        deadline=dl_val,
                        evidence_freshness="ALL_FRESH",
                        notes=notes,
                        recommended_action="KEEP_ACTIVE",
                    )

                    if apply_updates:
                        cand["consecutiveMissingCount"] = 0
                        cand["lastObservedAt"] = revalidated_at_str
                        cand["lifecycleStatus"] = STATE_STILL_ACTIVE
                        # Refresh observedAt timestamp on existing evidence
                        for ev in cand.get("fieldEvidence", []):
                            if isinstance(ev, dict):
                                ev["observedAt"] = revalidated_at_str

            else:
                # Vacancy NOT FOUND on source!
                new_missing_count = prev_missing_count + 1
                notes = list(eval_notes)

                if new_missing_count < consecutive_missing_threshold:
                    summary.disappeared_once += 1
                    disappeared_once_total += 1
                    notes.append(
                        f"Vacante ausente en captura actual ({new_missing_count}/{consecutive_missing_threshold}). "
                        "Salvaguarda activa: no se cierra automáticamente tras una sola ausencia."
                    )

                    result = CandidateRevalidationResult(
                        candidate_id=c_id,
                        source_id=s_id,
                        external_reference=ext_ref,
                        title=title,
                        lifecycle_state=STATE_DISAPPEARED_ONCE,
                        consecutive_missing_count=new_missing_count,
                        changes=[],
                        last_observed_at=cand.get("lastObservedAt") or cand.get("capturedAt"),
                        deadline_status=deadline_st,
                        deadline=dl_val,
                        evidence_freshness=fresh_st,
                        notes=notes,
                        recommended_action="VERIFY_NEXT_RUN",
                    )

                    if apply_updates:
                        cand["consecutiveMissingCount"] = new_missing_count
                        cand["lifecycleStatus"] = STATE_DISAPPEARED_ONCE

                else:
                    summary.confirmed_disappeared += 1
                    confirmed_disappeared_total += 1
                    notes.append(
                        f"Vacante ausente tras {new_missing_count} capturas consecutivas. "
                        "Cierre probable confirmado en la fuente de origen."
                    )

                    result = CandidateRevalidationResult(
                        candidate_id=c_id,
                        source_id=s_id,
                        external_reference=ext_ref,
                        title=title,
                        lifecycle_state=STATE_CONFIRMED_DISAPPEARED,
                        consecutive_missing_count=new_missing_count,
                        changes=[],
                        last_observed_at=cand.get("lastObservedAt") or cand.get("capturedAt"),
                        deadline_status=deadline_st,
                        deadline=dl_val,
                        evidence_freshness=fresh_st,
                        notes=notes,
                        recommended_action="MARK_EXPIRED_OR_CLOSED",
                    )

                    if apply_updates:
                        cand["consecutiveMissingCount"] = new_missing_count
                        cand["lifecycleStatus"] = STATE_CONFIRMED_DISAPPEARED

            candidate_results.append(result)

        source_summaries.append(summary)

    sources_succeeded = sum(1 for s in source_summaries if s.status == "success")
    sources_failed = sum(1 for s in source_summaries if s.status == "failed")

    report = RevalidationReport(
        timestamp=revalidated_at_str,
        as_of=as_of_date.isoformat(),
        sources_evaluated=len(target_source_ids),
        sources_succeeded=sources_succeeded,
        sources_failed=sources_failed,
        total_candidates_evaluated=len(candidate_results),
        still_active_count=still_active_total,
        changed_count=changed_total,
        disappeared_once_count=disappeared_once_total,
        confirmed_disappeared_count=confirmed_disappeared_total,
        preserved_on_error_count=preserved_on_error_total,
        deadline_expired_count=deadline_expired_total,
        evidence_stale_count=evidence_stale_total,
        source_summaries=source_summaries,
        candidate_results=candidate_results,
    )

    return report, working_candidates


def run_revalidation_job(
    *,
    inbox_path: Path = Path(ROOT / "data" / "candidates" / "inbox.local.json"),
    sources_registry_path: Path = SOURCES_REGISTRY_PATH,
    source_ids: list[str] | None = None,
    fixtures_dir: Path | None = None,
    as_of: date | None = None,
    threshold: int = 2,
    update_inbox: bool = False,
    dry_run: bool = True,
) -> RevalidationReport:
    """Executes a complete revalidation job over the local staging inbox."""
    if not inbox_path.exists():
        raise FileNotFoundError(f"La bandeja de entrada no existe: '{inbox_path}'")

    inbox_data = json.loads(inbox_path.read_text(encoding="utf-8"))
    candidates = inbox_data.get("candidates") or []

    sources_registry = load_source_registry()

    report, updated_candidates = revalidate_candidates(
        candidates,
        sources_registry=sources_registry,
        source_ids=source_ids,
        fixtures_dir=fixtures_dir,
        as_of=as_of,
        consecutive_missing_threshold=threshold,
        apply_updates=(update_inbox and not dry_run),
    )

    if update_inbox and not dry_run:
        inbox_data["candidates"] = updated_candidates
        _atomic_write_json(inbox_path, inbox_data)

    return report


def revalidate_canonical_catalog(
    *,
    seed_path: Path = SEED_CATALOG_PATH,
    fixtures_dir: Path | None = None,
    as_of: date | None = None,
) -> dict[str, Any]:
    """Audits the active opportunities in the canonical seed catalog against ATS boards.

    SAFEGUARD: Read-only operation. NEVER mutates opportunities.seed.json or opportunities.json.
    """
    if not seed_path.exists():
        raise FileNotFoundError(f"Catálogo canónico no encontrado en '{seed_path}'")

    seed_data = json.loads(seed_path.read_text(encoding="utf-8"))
    opps = seed_data.get("opportunities") or []

    employer_to_source = {
        "Canonical": "greenhouse-canonical",
        "Sezzle": "greenhouse-sezzle",
        "CookUnity": "greenhouse-cookunity",
        "Fintual": "lever-fintual",
        "Kavak": "lever-kavak",
    }

    audit_candidates = []
    for opp in opps:
        opp_id = opp.get("id")
        emp = opp.get("employer")
        s_id = employer_to_source.get(emp)
        rec_kind = opp.get("recordKind")
        req = opp.get("requisition")

        if rec_kind == "demonstration" or not s_id or not req:
            continue

        check_date = opp.get("lastCheckedDate") or "2026-11-22"
        apply_url = opp.get("applyUrl") or opp.get("sourceUrl") or "https://canonical.com"

        pseudo_cand = {
            "candidateId": f"CATALOG-{opp_id}",
            "sourceId": s_id,
            "sourceUrl": opp.get("sourceUrl") or apply_url,
            "capturedAt": f"{check_date}T10:00:00-05:00",
            "captureMethod": "manual",
            "proposed": {
                "title": opp.get("title"),
                "employer": emp,
                "publisher": opp.get("sourceKind"),
                "externalReference": req,
                "applyUrl": apply_url,
                "publishedAt": opp.get("publishedAt"),
                "deadline": opp.get("deadline"),
                "location": opp.get("location"),
                "mode": opp.get("mode"),
                "opportunityType": opp.get("kind"),
                "salary": opp.get("salary"),
                "benefits": opp.get("benefits"),
                "requirements": opp.get("requirements"),
            },
            "fieldEvidence": [
                {"field": "title", "url": apply_url, "observedAt": f"{check_date}T10:00:00-05:00"}
            ],
            "editorialReview": {
                "status": "approved_for_catalog",
                "reviewer": "human_editor",
                "reviewedAt": f"{check_date}T10:00:00-05:00",
                "decisionNote": f"Ficha canónica {opp_id}",
            },
        }
        audit_candidates.append(pseudo_cand)

    report, _ = revalidate_candidates(
        audit_candidates,
        fixtures_dir=fixtures_dir,
        as_of=as_of,
        apply_updates=False,
    )

    return {
        "catalogPath": str(seed_path),
        "totalCanonicalEvaluated": len(audit_candidates),
        "stillActiveCount": report.still_active_count,
        "changedCount": report.changed_count,
        "disappearedCount": report.disappeared_once_count + report.confirmed_disappeared_count,
        "preservedOnErrorCount": report.preserved_on_error_count,
        "candidateResults": [c.to_dict() for c in report.candidate_results],
    }
