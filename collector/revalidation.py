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
from collector.dedup import normalize_identifier, normalize_text
from collector.evidence import (
    DEFAULT_TTL_DAYS,
    is_valid_https_url,
    parse_iso_date,
    parse_iso_timestamp,
)
from collector.policy import find_source, load_source_registry

LIMA_TIMEZONE = timezone(timedelta(hours=-5))

# Lifecycle state constants (Legacy compatibility)
STATE_STILL_ACTIVE = "STILL_ACTIVE"
STATE_CHANGED = "CHANGED"
STATE_DISAPPEARED_ONCE = "DISAPPEARED_ONCE"
STATE_CONFIRMED_DISAPPEARED = "CONFIRMED_DISAPPEARED"
STATE_PRESERVED_ON_SOURCE_ERROR = "PRESERVED_ON_SOURCE_ERROR"
STATE_UNKNOWN = "UNKNOWN"

# Semantic result taxonomy (TASK-R6-02 Specification)
RESULT_OPEN_CONFIRMED = "OPEN_CONFIRMED"
RESULT_CLOSED_CONFIRMED = "CLOSED_CONFIRMED"
RESULT_NOT_FOUND_CONFIRMED = "NOT_FOUND_CONFIRMED"
RESULT_DISAPPEARED_ONCE = "DISAPPEARED_ONCE"
RESULT_TEMPORARY_ERROR = "TEMPORARY_ERROR"
RESULT_UNKNOWN = "UNKNOWN"
RESULT_SOURCE_UNSUPPORTED = "SOURCE_UNSUPPORTED"

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
DEFAULT_STATE_PATH = ROOT / "data" / "revalidation-state.json"
DEFAULT_LOCK_PATH = ROOT / "data" / ".revalidation.lock"

PROTECTED_PATHS = {
    SEED_CATALOG_PATH.resolve(),
    SNAPSHOT_CATALOG_PATH.resolve(),
    SOURCES_REGISTRY_PATH.resolve(),
}

KNOWN_EMPLOYER_SOURCES = {
    "canonical": "greenhouse-canonical",
    "sezzle": "greenhouse-sezzle",
    "cookunity": "greenhouse-cookunity",
    "encora": "greenhouse-encora",
    "ositran": "ositran-convocatorias",
    "defensoría del pueblo": "defensoria-del-pueblo-cas",
    "defensoria del pueblo": "defensoria-del-pueblo-cas",
    "universidad tecnológica del perú (utp)": "utp-hiringroom-campus",
    "utp": "utp-hiringroom-campus",
    "stefanini it solutions perú s.a.c.": "stefanini-hiringroom",
    "stefanini": "stefanini-hiringroom",
    "canvia": "canvia-hiringroom",
    "myapps soluciones s.a.c.": "myapps-hiringroom",
    "myapps": "myapps-hiringroom",
    "efitec corporation s.a.c.": "efitec-hiringroom",
    "efitec": "efitec-hiringroom",
    "indecopi": "gobpe-indecopi-convocatorias",
    "fintual": "lever-fintual",
    "kavak": "lever-kavak",
}


class RevalidationLock:
    """Acquires a file-based lock to prevent concurrent catalog revalidation."""

    def __init__(self, lock_path: Path = DEFAULT_LOCK_PATH, timeout_seconds: int = 600):
        self.lock_path = lock_path
        self.timeout_seconds = timeout_seconds
        self.acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self) -> bool:
        now = datetime.now(timezone.utc).timestamp()
        if self.lock_path.exists():
            try:
                content = json.loads(self.lock_path.read_text(encoding="utf-8"))
                lock_time = float(content.get("timestamp", 0))
                pid = content.get("pid")
                if now - lock_time < self.timeout_seconds:
                    raise RuntimeError(
                        f"Bloqueo de concurrencia activo (PID {pid}, iniciado hace {int(now - lock_time)}s). "
                        f"Otro proceso de revalidación está en ejecución: '{self.lock_path}'"
                    )
            except (json.JSONDecodeError, OSError):
                pass  # Stale lock file override

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "pid": os.getpid(),
            "timestamp": now,
            "iso": datetime.now(timezone.utc).isoformat(),
        }
        self.lock_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.acquired = True
        return True

    def release(self):
        if self.acquired and self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except OSError:
                pass
            self.acquired = False


def load_revalidation_state(path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    """Safely loads persisted revalidation state or returns default schema."""
    if not path.exists():
        return {
            "schemaVersion": 1,
            "lastRunAt": None,
            "opportunities": {},
        }
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            return {"schemaVersion": 1, "lastRunAt": None, "opportunities": {}}
        content.setdefault("opportunities", {})
        return content
    except Exception:
        return {"schemaVersion": 1, "lastRunAt": None, "opportunities": {}}


def save_revalidation_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically writes revalidation state to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(path, state)


def get_source_for_opportunity(opp: dict, source_registry: dict) -> dict | None:
    """Resolves the authorized source record for a given canonical opportunity."""
    all_sources = source_registry.get("sources", [])
    source_by_id = {s["id"]: s for s in all_sources if isinstance(s, dict) and "id" in s}

    # 1. Direct sourceId field if declared
    s_id = opp.get("sourceId")
    if s_id and s_id in source_by_id:
        return source_by_id[s_id]

    # 2. Known employer dictionary mapping
    emp = (opp.get("employer") or "").strip().lower()
    known_id = KNOWN_EMPLOYER_SOURCES.get(emp)
    if known_id and known_id in source_by_id:
        return source_by_id[known_id]

    # 3. Match by employer name in sources registry
    for s in all_sources:
        s_emp = (s.get("employer") or "").strip().lower()
        if s_emp and s_emp == emp:
            return s

    return None


def _atomic_write_json(path: Path, data: Any, allow_canonical: bool = False) -> None:
    """Atomically writes JSON using a temporary file in the same directory."""
    path_resolved = path.resolve()
    if not allow_canonical and path_resolved in PROTECTED_PATHS:
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
            parsed_dt = parse_iso_timestamp(raw_deadline)
            if parsed_dt:
                deadline_str = parsed_dt.isoformat()
                dt_lima = parsed_dt.astimezone(LIMA_TIMEZONE)
                if dt_lima.date() < as_of_date:
                    deadline_status = "DEADLINE_EXPIRED"
                    notes.append(f"Fecha límite de postulación superada ({deadline_str} < {as_of_date.isoformat()})")
                elif dt_lima.date() == as_of_date:
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
    if as_of is not None:
        now_dt = datetime(as_of.year, as_of.month, as_of.day, 12, 0, 0, tzinfo=LIMA_TIMEZONE)
    else:
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
                if not fixture_file.exists():
                    fixture_file = fixtures_dir / f"{s_id}.html"
                if fixture_file.exists():
                    if connector == "greenhouse-job-board":
                        fixture_data = json.loads(fixture_file.read_text(encoding="utf-8"))
                        raw_fresh = transform_greenhouse_payload(source, fixture_data, captured_at=revalidated_at_str)
                    elif connector == "lever-postings":
                        fixture_data = json.loads(fixture_file.read_text(encoding="utf-8"))
                        raw_fresh = transform_lever_payload(source, fixture_data, captured_at=revalidated_at_str)
                    elif connector == "ositran-portal":
                        raw_fresh = transform_ositran_html(source, fixture_file.read_text(encoding="utf-8"), captured_at=revalidated_at_str)
                    elif connector == "defensoria-cas":
                        raw_fresh = transform_defensoria_html(source, fixture_file.read_text(encoding="utf-8"), captured_at=revalidated_at_str)
                    elif connector == "hiringroom-board":
                        raw_fresh = transform_hiringroom_html(source, fixture_file.read_text(encoding="utf-8"), captured_at=revalidated_at_str)
                    fixture_loaded = True

            if not fixture_loaded:
                if connector == "greenhouse-job-board":
                    raw_fresh = fetch_greenhouse_board(source, request_count=0, captured_at=revalidated_at_str)
                elif connector == "lever-postings":
                    raw_fresh = fetch_lever_board(source, request_count=0, captured_at=revalidated_at_str)
                elif connector == "ositran-portal":
                    raw_fresh = fetch_ositran_convocatorias(source, request_count=0, captured_at=revalidated_at_str)
                elif connector == "defensoria-cas":
                    raw_fresh = fetch_defensoria_cas(source, request_count=0, captured_at=revalidated_at_str)
                elif connector == "hiringroom-board":
                    raw_fresh = fetch_hiringroom_board(source, request_count=0, captured_at=revalidated_at_str)
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


def fetch_board_data(source: dict, fixtures_dir: Path | None, now_iso: str) -> list[dict]:
    """Fetches or loads board postings for an authorized source."""
    s_id = source.get("id")
    connector = source.get("connector")
    raw_fresh: list[dict] = []

    if fixtures_dir:
        for ext in (".json", ".html"):
            fixture_file = fixtures_dir / f"{s_id}{ext}"
            if fixture_file.exists():
                text = fixture_file.read_text(encoding="utf-8")
                if connector == "greenhouse-job-board":
                    raw_fresh = transform_greenhouse_payload(source, json.loads(text), captured_at=now_iso)
                elif connector == "lever-postings":
                    raw_fresh = transform_lever_payload(source, json.loads(text), captured_at=now_iso)
                elif connector == "ositran-portal":
                    raw_fresh = transform_ositran_html(source, text, captured_at=now_iso)
                elif connector == "defensoria-cas":
                    raw_fresh = transform_defensoria_html(source, text, captured_at=now_iso)
                elif connector == "hiringroom-board":
                    raw_fresh = transform_hiringroom_html(source, text, captured_at=now_iso)
                elif connector == "gobpe-convocatorias":
                    raw_fresh = transform_gobpe_indecopi_html(source, text, captured_at=now_iso)
                else:
                    raise ValueError(f"Conector '{connector}' no admite revalidación en fixtures")
                return raw_fresh

    if connector == "greenhouse-job-board":
        return fetch_greenhouse_board(source, request_count=0, captured_at=now_iso)
    elif connector == "lever-postings":
        return fetch_lever_board(source, request_count=0, captured_at=now_iso)
    elif connector == "ositran-portal":
        return fetch_ositran_convocatorias(source, request_count=0, captured_at=now_iso)
    elif connector == "defensoria-cas":
        return fetch_defensoria_cas(source, request_count=0, captured_at=now_iso)
    elif connector == "hiringroom-board":
        return fetch_hiringroom_board(source, request_count=0, captured_at=now_iso)
    elif connector == "gobpe-convocatorias":
        return fetch_gobpe_convocatorias(source, request_count=0, captured_at=now_iso)
    else:
        raise ValueError(f"Conector '{connector}' no admite revalidación automatizada en red")


def revalidate_canonical_catalog(
    *,
    seed_path: Path = SEED_CATALOG_PATH,
    snapshot_path: Path = SNAPSHOT_CATALOG_PATH,
    state_path: Path = DEFAULT_STATE_PATH,
    sources_registry_path: Path = SOURCES_REGISTRY_PATH,
    fixtures_dir: Path | None = None,
    as_of: date | None = None,
    threshold: int = 2,
    apply_updates: bool = False,
    source_ids: list[str] | None = None,
    lock_path: Path = DEFAULT_LOCK_PATH,
) -> dict[str, Any]:
    """Revalidates active opportunities in the canonical catalog with the Two-Absence Rule (TASK-R6-02).

    Governed by:
    - Case A: Open confirmed -> lastVerifiedAt updated, consecutive absences reset to 0.
    - Case B: First absence -> DISAPPEARED_ONCE, preserved active, counter = 1.
    - Case C: Second consecutive absence -> NOT_FOUND_CONFIRMED, closed as historical.
    - Case D: Temporary error (5xx, 403, 429, timeout) -> TEMPORARY_ERROR, preserved on error.
    - Case E: Explicit ATS closure -> CLOSED_CONFIRMED, closed directly with evidence.
    """
    if as_of is not None:
        now_dt = datetime(as_of.year, as_of.month, as_of.day, 12, 0, 0, tzinfo=LIMA_TIMEZONE)
    else:
        now_dt = datetime.now(LIMA_TIMEZONE)
    as_of_date = as_of or now_dt.date()
    now_iso = now_dt.isoformat(timespec="seconds")
    timestamp_start = now_iso

    if not seed_path.exists():
        raise FileNotFoundError(f"Catálogo canónico no encontrado en '{seed_path}'")

    # 1. Acquire concurrency lock if applying updates
    lock_ctx = RevalidationLock(lock_path) if apply_updates else None
    if lock_ctx:
        lock_ctx.acquire()

    try:
        seed_data = json.loads(seed_path.read_text(encoding="utf-8"))
        opps = seed_data.get("opportunities") or []

        sources_registry = load_source_registry()
        state = load_revalidation_state(state_path)
        opp_states = state.setdefault("opportunities", {})

        # 2. Filter opportunities to evaluate
        eligible_opps: list[dict] = []
        for opp in opps:
            opp_id = opp.get("id")
            rec_kind = opp.get("recordKind")
            # Always evaluate open opportunities (skip demonstration)
            if rec_kind == "demonstration":
                continue
            eligible_opps.append(opp)

        # 3. Group opportunities by source
        opps_by_source: dict[str, list[dict]] = {}
        unsupported_opps: list[dict] = []

        for opp in eligible_opps:
            src = get_source_for_opportunity(opp, sources_registry)
            if not src:
                unsupported_opps.append(opp)
                continue
            src_id = src.get("id", "unknown")
            if source_ids and src_id not in source_ids:
                continue
            opps_by_source.setdefault(src_id, []).append(opp)

        candidate_results: list[dict[str, Any]] = []
        sources_evaluated = 0
        sources_succeeded = 0
        sources_failed = 0

        open_confirmed_count = 0
        first_absence_count = 0
        second_absence_count = 0
        explicit_closed_count = 0
        temporary_error_count = 0
        source_unsupported_count = len(unsupported_opps)
        became_historical_count = 0
        unverifiable_count = 0

        # Mark unsupported opportunities
        for opp in unsupported_opps:
            opp_id = opp.get("id", "unknown")
            res_entry = {
                "candidateId": f"CATALOG-{opp_id}",
                "opportunityId": opp_id,
                "title": opp.get("title", "Sin título"),
                "employer": opp.get("employer", "Desconocido"),
                "sourceId": "unsupported",
                "lifecycleState": RESULT_SOURCE_UNSUPPORTED,
                "consecutiveMissingCount": 0,
                "lastObservedAt": opp.get("lastVerifiedAt"),
                "notes": ["Fuente sin conector automatizado compatible o no autorizada."],
                "recommendedAction": "MANUAL_INSPECTION",
            }
            candidate_results.append(res_entry)
            unverifiable_count += 1

        # 4. Evaluate each source and its opportunities
        for s_id, source_opps in opps_by_source.items():
            sources_evaluated += 1
            src = find_source(sources_registry, s_id)
            if not src:
                for opp in source_opps:
                    opp_id = opp.get("id")
                    candidate_results.append({
                        "candidateId": f"CATALOG-{opp_id}",
                        "opportunityId": opp_id,
                        "title": opp.get("title"),
                        "employer": opp.get("employer"),
                        "sourceId": s_id,
                        "lifecycleState": RESULT_SOURCE_UNSUPPORTED,
                        "consecutiveMissingCount": 0,
                        "lastObservedAt": opp.get("lastVerifiedAt"),
                        "notes": [f"Fuente '{s_id}' no encontrada en sources.json."],
                        "recommendedAction": "MANUAL_INSPECTION",
                    })
                    source_unsupported_count += 1
                continue

            # Check source authorization (fixtures_dir allows offline testing of fixtures)
            is_authorized = (
                src.get("decision") == "approved"
                and src.get("automatedAccessStatus") == "approved"
                and src.get("enabled", True)
            ) or (fixtures_dir is not None)
            if not is_authorized:
                for opp in source_opps:
                    opp_id = opp.get("id")
                    candidate_results.append({
                        "candidateId": f"CATALOG-{opp_id}",
                        "opportunityId": opp_id,
                        "title": opp.get("title"),
                        "employer": opp.get("employer"),
                        "sourceId": s_id,
                        "lifecycleState": RESULT_SOURCE_UNSUPPORTED,
                        "consecutiveMissingCount": 0,
                        "lastObservedAt": opp.get("lastVerifiedAt"),
                        "notes": [f"Fuente '{s_id}' no autorizada para acceso automatizado (decision: {src.get('decision')})."],
                        "recommendedAction": "SOURCE_NOT_AUTHORIZED",
                    })
                    source_unsupported_count += 1
                continue

            # Fetch fresh board data
            fresh_postings: list[dict] = []
            fetch_error: str | None = None
            try:
                fresh_postings = fetch_board_data(src, fixtures_dir, now_iso)
                sources_succeeded += 1
            except Exception as err:
                sources_failed += 1
                fetch_error = str(err)

            # SAFEGUARD (Case D): If source fetch failed with network/timeout/5xx, PRESERVE opportunities
            if fetch_error is not None:
                for opp in source_opps:
                    opp_id = opp.get("id")
                    temporary_error_count += 1
                    unverifiable_count += 1
                    st_entry = opp_states.setdefault(opp_id, {
                        "opportunityId": opp_id,
                        "sourceId": s_id,
                        "requisition": opp.get("requisition"),
                        "employer": opp.get("employer"),
                        "consecutiveMissingCount": 0,
                        "firstAbsentAt": None,
                        "lastAbsentAt": None,
                        "lastCheckedAt": None,
                        "lastResult": None,
                        "history": [],
                    })
                    st_entry["lastCheckedAt"] = now_iso
                    st_entry["lastResult"] = RESULT_TEMPORARY_ERROR
                    st_entry.setdefault("history", []).append({
                        "timestamp": now_iso,
                        "result": RESULT_TEMPORARY_ERROR,
                        "asOf": as_of_date.isoformat(),
                        "note": f"Fallo temporal al consultar fuente ({fetch_error}); estado preservado.",
                    })
                    st_entry["history"] = st_entry["history"][-10:]

                    candidate_results.append({
                        "candidateId": f"CATALOG-{opp_id}",
                        "opportunityId": opp_id,
                        "title": opp.get("title"),
                        "employer": opp.get("employer"),
                        "sourceId": s_id,
                        "lifecycleState": RESULT_TEMPORARY_ERROR,
                        "consecutiveMissingCount": st_entry.get("consecutiveMissingCount", 0),
                        "lastObservedAt": opp.get("lastVerifiedAt"),
                        "notes": [f"Error temporal en la fuente ({fetch_error}); vacante preservada sin modificación."],
                        "recommendedAction": "RETRY_LATER",
                    })
                continue

            # Source fetch SUCCEEDED: Map fresh postings by normalized identifier
            fresh_by_ref: dict[str, dict] = {}
            for fp in fresh_postings:
                prop = fp.get("proposed") or {}
                ref_norm = normalize_identifier(prop.get("externalReference"))
                if ref_norm:
                    fresh_by_ref[ref_norm] = fp

            # Evaluate each opportunity of this source
            for opp in source_opps:
                opp_id = opp.get("id")
                req_raw = opp.get("requisition")
                if not req_raw:
                    # Opportunity without external reference
                    candidate_results.append({
                        "candidateId": f"CATALOG-{opp_id}",
                        "opportunityId": opp_id,
                        "title": opp.get("title"),
                        "employer": opp.get("employer"),
                        "sourceId": s_id,
                        "lifecycleState": RESULT_SOURCE_UNSUPPORTED,
                        "consecutiveMissingCount": 0,
                        "lastObservedAt": opp.get("lastVerifiedAt"),
                        "notes": ["Oportunidad carece de requisition/externalReference; no se intenta consulta insegura."],
                        "recommendedAction": "MISSING_REQUISITION",
                    })
                    source_unsupported_count += 1
                    unverifiable_count += 1
                    continue

                req_norm = normalize_identifier(req_raw)
                st_entry = opp_states.setdefault(opp_id, {
                    "opportunityId": opp_id,
                    "sourceId": s_id,
                    "requisition": req_raw,
                    "employer": opp.get("employer"),
                    "consecutiveMissingCount": 0,
                    "firstAbsentAt": None,
                    "lastAbsentAt": None,
                    "lastCheckedAt": None,
                    "lastResult": None,
                    "history": [],
                })

                prev_missing = int(st_entry.get("consecutiveMissingCount") or 0)

                # MATCH EVALUATION
                if req_norm in fresh_by_ref:
                    # Found in fresh postings!
                    matched_fp = fresh_by_ref[req_norm]
                    fp_prop = matched_fp.get("proposed") or {}
                    fp_status = matched_fp.get("opportunityStatus") or fp_prop.get("opportunityStatus") or ""
                    fp_desc = str(fp_prop.get("description") or "").lower()
                    fp_title = str(fp_prop.get("title") or "").lower()

                    # Case E: Explicit closure check
                    explicit_closed_terms = ("finalizada", "concluida", "cancelada", "desierta", "cerrada", "proceso concluido")
                    is_explicit_closed = fp_status in ("closed", "expired") or any(t in fp_desc for t in explicit_closed_terms) or any(t in fp_title for t in explicit_closed_terms)

                    # Deadline expiration check
                    opp_dl = opp.get("deadline") or (matched_fp.get("proposed") or {}).get("deadline")
                    is_deadline_expired = False
                    dl_str = None
                    if opp_dl:
                        dl_status, dl_str, _, _ = evaluate_temporal_freshness(
                            {"proposed": {"deadline": opp_dl}}, as_of_date=as_of_date
                        )
                        if dl_status == "DEADLINE_EXPIRED":
                            is_deadline_expired = True

                    if is_explicit_closed or is_deadline_expired:
                        # Case E or Deadline Expired: Explicit closure / deadline passed
                        if is_deadline_expired:
                            closure_reason = "deadline_expired"
                            res_note = f"Plazo de postulación vencido ({dl_str})."
                            ed_note = f"Marcada como vencida el {as_of_date.isoformat()} tras cumplirse la fecha límite ({dl_str})."
                            opp_status = "expired"
                        else:
                            closure_reason = "source_confirmed_closed"
                            res_note = "Cierre explícito confirmado por la fuente oficial."
                            ed_note = f"Marcada como cerrada el {as_of_date.isoformat()} tras confirmación explícita de cierre en {s_id}."
                            opp_status = "closed"
                            explicit_closed_count += 1

                        became_historical_count += 1
                        st_entry["lastCheckedAt"] = now_iso
                        st_entry["lastResult"] = RESULT_CLOSED_CONFIRMED
                        st_entry["closedAt"] = now_iso
                        st_entry.setdefault("history", []).append({
                            "timestamp": now_iso,
                            "result": RESULT_CLOSED_CONFIRMED,
                            "asOf": as_of_date.isoformat(),
                            "note": res_note,
                        })
                        st_entry["history"] = st_entry["history"][-10:]

                        if apply_updates:
                            opp["opportunityStatus"] = opp_status
                            opp["publicationStatus"] = "historical"
                            opp["verificationStatus"] = "stale"
                            opp["lastCheckedDate"] = as_of_date.isoformat()
                            opp["closureReason"] = closure_reason
                            ed = opp.setdefault("editorialDecision", {})
                            ed["decisionNote"] = ed_note

                        candidate_results.append({
                            "candidateId": f"CATALOG-{opp_id}",
                            "opportunityId": opp_id,
                            "title": opp.get("title"),
                            "employer": opp.get("employer"),
                            "sourceId": s_id,
                            "lifecycleState": RESULT_CLOSED_CONFIRMED,
                            "consecutiveMissingCount": prev_missing,
                            "lastObservedAt": now_iso,
                            "notes": [res_note],
                            "recommendedAction": "MARK_HISTORICAL",
                        })

                    else:
                        # Case A: Open confirmed!
                        open_confirmed_count += 1
                        st_entry["consecutiveMissingCount"] = 0
                        st_entry["firstAbsentAt"] = None
                        st_entry["lastAbsentAt"] = None
                        st_entry["lastCheckedAt"] = now_iso
                        st_entry["lastResult"] = RESULT_OPEN_CONFIRMED
                        st_entry.setdefault("history", []).append({
                            "timestamp": now_iso,
                            "result": RESULT_OPEN_CONFIRMED,
                            "asOf": as_of_date.isoformat(),
                            "note": "Vacante confirmada activa en ATS oficial.",
                        })
                        st_entry["history"] = st_entry["history"][-10:]

                        if apply_updates:
                            opp["opportunityStatus"] = "open"
                            opp["publicationStatus"] = "active"
                            opp["verificationStatus"] = "verified"
                            opp["lastCheckedDate"] = as_of_date.isoformat()
                            opp["lastVerifiedAt"] = now_iso
                            ve = opp.setdefault("verificationEvidence", {})
                            ve["observedAt"] = now_iso
                            for fe in opp.get("fieldEvidence", []):
                                if isinstance(fe, dict):
                                    fe["observedAt"] = now_iso

                        candidate_results.append({
                            "candidateId": f"CATALOG-{opp_id}",
                            "opportunityId": opp_id,
                            "title": opp.get("title"),
                            "employer": opp.get("employer"),
                            "sourceId": s_id,
                            "lifecycleState": RESULT_OPEN_CONFIRMED,
                            "consecutiveMissingCount": 0,
                            "lastObservedAt": now_iso,
                            "notes": ["Vacante confirmada activa con datos vigentes."],
                            "recommendedAction": "KEEP_ACTIVE",
                        })

                else:
                    # NOT in fresh postings -> Absence!
                    new_missing = prev_missing + 1

                    if new_missing < threshold:
                        # Case B: First absence
                        first_absence_count += 1
                        st_entry["consecutiveMissingCount"] = new_missing
                        if not st_entry.get("firstAbsentAt"):
                            st_entry["firstAbsentAt"] = now_iso
                        st_entry["lastAbsentAt"] = now_iso
                        st_entry["lastCheckedAt"] = now_iso
                        st_entry["lastResult"] = RESULT_DISAPPEARED_ONCE
                        st_entry.setdefault("history", []).append({
                            "timestamp": now_iso,
                            "result": RESULT_DISAPPEARED_ONCE,
                            "asOf": as_of_date.isoformat(),
                            "note": f"Primera ausencia detectada en la fuente oficial ({new_missing}/{threshold}). Salvaguarda activa: conservada activa.",
                        })
                        st_entry["history"] = st_entry["history"][-10:]

                        if apply_updates:
                            # SAFEGUARD: Keep opportunityStatus="open" and publicationStatus="active"
                            opp["lastCheckedDate"] = as_of_date.isoformat()

                        candidate_results.append({
                            "candidateId": f"CATALOG-{opp_id}",
                            "opportunityId": opp_id,
                            "title": opp.get("title"),
                            "employer": opp.get("employer"),
                            "sourceId": s_id,
                            "lifecycleState": RESULT_DISAPPEARED_ONCE,
                            "consecutiveMissingCount": new_missing,
                            "lastObservedAt": st_entry.get("firstAbsentAt"),
                            "notes": [f"Vacante ausente en la captura actual ({new_missing}/{threshold}). Salvaguarda activa: no se cierra."],
                            "recommendedAction": "VERIFY_NEXT_RUN",
                        })

                    else:
                        # Case C: Second consecutive absence -> Confirmed missing!
                        second_absence_count += 1
                        became_historical_count += 1
                        st_entry["consecutiveMissingCount"] = new_missing
                        st_entry["lastAbsentAt"] = now_iso
                        st_entry["lastCheckedAt"] = now_iso
                        st_entry["lastResult"] = RESULT_NOT_FOUND_CONFIRMED
                        st_entry["closedAt"] = now_iso
                        st_entry.setdefault("history", []).append({
                            "timestamp": now_iso,
                            "result": RESULT_NOT_FOUND_CONFIRMED,
                            "asOf": as_of_date.isoformat(),
                            "note": f"Segunda ausencia consecutiva confirmada ({new_missing}/{threshold}). Marcada como histórica.",
                        })
                        st_entry["history"] = st_entry["history"][-10:]

                        if apply_updates:
                            opp["opportunityStatus"] = "closed"
                            opp["publicationStatus"] = "historical"
                            opp["verificationStatus"] = "stale"
                            opp["lastCheckedDate"] = as_of_date.isoformat()
                            opp["closureReason"] = "two_consecutive_absences_confirmed"
                            ed = opp.setdefault("editorialDecision", {})
                            ed["decisionNote"] = f"Marcada como histórica el {as_of_date.isoformat()} tras confirmar ausencia en 2 verificaciones consecutivas de {s_id}."

                        candidate_results.append({
                            "candidateId": f"CATALOG-{opp_id}",
                            "opportunityId": opp_id,
                            "title": opp.get("title"),
                            "employer": opp.get("employer"),
                            "sourceId": s_id,
                            "lifecycleState": RESULT_NOT_FOUND_CONFIRMED,
                            "consecutiveMissingCount": new_missing,
                            "lastObservedAt": st_entry.get("lastAbsentAt"),
                            "notes": [f"Ausencia confirmada tras {new_missing} verificaciones consecutivas. Marcada como histórica."],
                            "recommendedAction": "MARK_HISTORICAL",
                        })

        # 5. If applying updates, validate final catalog quality and persist atomically
        catalog_validation_status = "VALID"
        if apply_updates:
            from catalog_quality import validate_payload
            from build_catalog import build_payload

            # Validate before writing
            val_result = validate_payload(
                {**seed_data, "generatedAt": now_iso},
                today=as_of_date,
            )
            if not val_result.ok:
                catalog_validation_status = f"FAILED: {'; '.join(val_result.errors)}"
                raise ValueError(f"Fallo de validación del catálogo tras revalidación: {'; '.join(val_result.errors)}")

            # Atomic write seed
            _atomic_write_json(seed_path, seed_data, allow_canonical=True)

            # Rebuild and atomic write snapshot
            previous_snap = json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.exists() else {}
            new_payload = build_payload(seed_data, previous_snap, now_iso, today=as_of_date)
            _atomic_write_json(snapshot_path, new_payload, allow_canonical=True)

            # Atomic write state
            state["lastRunAt"] = now_iso
            save_revalidation_state(state_path, state)

        timestamp_end = datetime.now(LIMA_TIMEZONE).isoformat(timespec="seconds")

        return {
            "timestampStart": timestamp_start,
            "timestampEnd": timestamp_end,
            "asOf": as_of_date.isoformat(),
            "catalogPath": str(seed_path),
            "snapshotPath": str(snapshot_path),
            "statePath": str(state_path),
            "dryRun": not apply_updates,
            "totalCanonicalEvaluated": len(eligible_opps),
            "sourcesEvaluated": sources_evaluated,
            "sourcesSucceeded": sources_succeeded,
            "sourcesFailed": sources_failed,
            "openConfirmedCount": open_confirmed_count,
            "firstAbsenceCount": first_absence_count,
            "secondAbsenceCount": second_absence_count,
            "explicitClosedCount": explicit_closed_count,
            "temporaryErrorCount": temporary_error_count,
            "sourceUnsupportedCount": source_unsupported_count,
            "becameHistoricalCount": became_historical_count,
            "unverifiableCount": unverifiable_count,
            "catalogValidationResult": catalog_validation_status,
            # Backward-compatible keys
            "stillActiveCount": open_confirmed_count,
            "changedCount": 0,
            "disappearedCount": first_absence_count + second_absence_count,
            "preservedOnErrorCount": temporary_error_count,
            "candidateResults": candidate_results,
        }

    finally:
        if lock_ctx:
            lock_ctx.release()
