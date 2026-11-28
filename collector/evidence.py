"""Verification of provenance, validity, and freshness of field evidence for Ruta Sistemas.

Operates 100% offline using Python standard library (datetime, urllib.parse).
Zero network requests, zero external scraping, zero automated candidate mutations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlsplit


LIMA_TIMEZONE = timezone(timedelta(hours=-5))
DEFAULT_TTL_DAYS = 7
ISO_DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Status constants
URL_VALID = "URL_STRUCTURE_VALID"
URL_INVALID = "URL_STRUCTURE_INVALID"

PROVENANCE_ALLOWED = "PROVENANCE_ALLOWED"
PROVENANCE_HOST_NOT_ALLOWLISTED = "PROVENANCE_HOST_NOT_ALLOWLISTED"
SOURCE_PENDING = "SOURCE_AUTHORIZATION_PENDING"

REMOTE_NOT_CHECKED = "REMOTE_AVAILABILITY_NOT_CHECKED"

FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"
FRESHNESS_FUTURE = "FUTURE"
FRESHNESS_INVALID = "INVALID"
FRESHNESS_UNKNOWN = "UNKNOWN"

DEADLINE_FUTURE = "DEADLINE_FUTURE"
DEADLINE_REACHED = "DEADLINE_REACHED"
DEADLINE_EXPIRED = "DEADLINE_EXPIRED"
DEADLINE_UNKNOWN = "DEADLINE_UNKNOWN"
DEADLINE_INVALID = "DEADLINE_INVALID"

STRUCTURAL_VALID = "STRUCTURAL_VALID"
STRUCTURAL_INVALID = "STRUCTURAL_INVALID"

PROVENANCE_VALID = "PROVENANCE_VALID"
PROVENANCE_INVALID = "PROVENANCE_INVALID"

SUMMARY_ALL_FRESH = "ALL_FRESH"
SUMMARY_PARTIALLY_STALE = "PARTIALLY_STALE"
SUMMARY_ALL_STALE = "ALL_STALE"
SUMMARY_INVALID_TEMPORALITY = "INVALID_TEMPORALITY"
SUMMARY_NO_EVIDENCE = "NO_EVIDENCE"


def is_valid_https_url(value: object) -> tuple[bool, str | None]:
    """Validates HTTPS scheme, non-empty host, absence of embedded credentials, and valid port."""
    if not isinstance(value, str) or not value.strip():
        return False, None
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme != "https":
            return False, None
        if not parsed.hostname:
            return False, None
        if parsed.username or parsed.password:
            return False, None
        if parsed.port not in (None, 443):
            return False, None
        return True, parsed.hostname.lower()
    except (ValueError, AttributeError):
        return False, None


def parse_iso_date(value: object) -> date | None:
    """Parses strict civil date in YYYY-MM-DD format."""
    if value in (None, "") or not isinstance(value, str):
        return None
    val_str = value.strip()
    if not ISO_DATE_REGEX.fullmatch(val_str):
        return None
    try:
        return date.fromisoformat(val_str)
    except ValueError:
        return None


def parse_iso_timestamp(value: object) -> datetime | None:
    """Parses ISO 8601 timestamp and ensures an explicit timezone is present."""
    if value in (None, "") or not isinstance(value, str):
        return None
    val_str = value.strip()
    try:
        dt = datetime.fromisoformat(val_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt
    except (ValueError, OverflowError):
        return None


@dataclass(frozen=True)
class FieldEvidenceEvaluation:
    field: str
    url: str | None
    url_status: str
    provenance_status: str
    observed_at: str | None
    observed_date: str | None
    freshness_status: str
    age_days: int | None
    is_orphan: bool
    remote_availability: str
    notes: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "url": self.url,
            "urlStatus": self.url_status,
            "provenanceStatus": self.provenance_status,
            "observedAt": self.observed_at,
            "observedDate": self.observed_date,
            "freshnessStatus": self.freshness_status,
            "ageDays": self.age_days,
            "isOrphan": self.is_orphan,
            "remoteAvailability": self.remote_availability,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class CandidateEvidenceReport:
    candidate_id: str
    source_id: str
    as_of: str
    ttl_days: int
    structural_status: str
    provenance_summary: str
    freshness_summary: str
    opportunity_validity: str
    deadline: str | None
    field_evaluations: tuple[FieldEvidenceEvaluation, ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    affected_fields: tuple[str, ...]
    explanation: str
    recommended_action: str

    def to_dict(self) -> dict:
        return {
            "candidateId": self.candidate_id,
            "sourceId": self.source_id,
            "asOf": self.as_of,
            "ttlDays": self.ttl_days,
            "structuralStatus": self.structural_status,
            "provenanceSummary": self.provenance_summary,
            "freshnessSummary": self.freshness_summary,
            "opportunityValidity": self.opportunity_validity,
            "deadline": self.deadline,
            "fieldEvaluations": [e.to_dict() for e in self.field_evaluations],
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "affectedFields": list(self.affected_fields),
            "explanation": self.explanation,
            "recommendedAction": self.recommended_action,
        }


def verify_candidate_evidence(
    candidate: dict,
    *,
    as_of: date | str | None = None,
    ttl_days: int | None = None,
    source: dict | None = None,
) -> CandidateEvidenceReport:
    """Evaluates the structural integrity, provenance, freshness, and temporal validity of a candidate."""
    errors: list[str] = []
    warnings: list[str] = []
    affected_fields_set: set[str] = set()

    # 1. Resolve evaluation date (as_of)
    if as_of is None:
        eval_date = datetime.now(LIMA_TIMEZONE).date()
    elif isinstance(as_of, date):
        eval_date = as_of
    elif isinstance(as_of, str):
        parsed = parse_iso_date(as_of)
        if parsed is None:
            raise ValueError(f"as_of debe ser una fecha civil válida YYYY-MM-DD: '{as_of}'")
        eval_date = parsed
    else:
        raise TypeError("as_of debe ser date, str YYYY-MM-DD o None")

    as_of_str = eval_date.isoformat()

    # 2. Candidate structure check
    if not isinstance(candidate, dict):
        return CandidateEvidenceReport(
            candidate_id="unknown",
            source_id="unknown",
            as_of=as_of_str,
            ttl_days=DEFAULT_TTL_DAYS,
            structural_status=STRUCTURAL_INVALID,
            provenance_summary=PROVENANCE_INVALID,
            freshness_summary=SUMMARY_NO_EVIDENCE,
            opportunity_validity=DEADLINE_UNKNOWN,
            deadline=None,
            field_evaluations=(),
            errors=("El candidato debe ser un diccionario",),
            warnings=(),
            affected_fields=(),
            explanation="Estructura de candidato no válida",
            recommended_action="Corregir formato de entrada antes de evaluar.",
        )

    candidate_id = str(candidate.get("candidateId") or "unknown")
    source_id = str(candidate.get("sourceId") or "unknown")

    # Resolve TTL days
    if ttl_days is not None:
        effective_ttl = int(ttl_days)
    elif source and isinstance(source.get("verificationTtlDays"), (int, float)):
        effective_ttl = int(source["verificationTtlDays"])
    else:
        effective_ttl = DEFAULT_TTL_DAYS

    stale_before = eval_date - timedelta(days=effective_ttl)

    # 3. Source policy checks
    allowed_hosts: set[str] = set()
    source_pending_review = False
    if source:
        for h in source.get("allowedHosts", []):
            allowed_hosts.add(h.lower())
        for h in source.get("allowedPostingHosts", []):
            allowed_hosts.add(h.lower())
        if source.get("decision") != "approved":
            source_pending_review = True
            warnings.append("Fuente en estado pending_review; candidato no promocionable")

    # 4. Check sourceUrl provenance
    source_url = candidate.get("sourceUrl")
    src_ok = False
    src_host = None
    if source_url:
        src_ok, src_host = is_valid_https_url(source_url)
        if not src_ok:
            errors.append("sourceUrl debe ser HTTPS válido sin credenciales")
            affected_fields_set.add("sourceUrl")
        elif allowed_hosts and src_host not in allowed_hosts:
            errors.append(f"Host '{src_host}' de sourceUrl no está en la lista permitida de la fuente")
            affected_fields_set.add("sourceUrl")
    else:
        errors.append("sourceUrl es obligatorio en la ficha del candidato")
        affected_fields_set.add("sourceUrl")

    # 5. Proposed fields map
    proposed = candidate.get("proposed")
    if not isinstance(proposed, dict):
        proposed = {}
        errors.append("proposed debe ser un objeto")
        affected_fields_set.add("proposed")

    non_null_proposed = {k for k, v in proposed.items() if v not in (None, "")}

    # 6. Deadline and Opportunity Validity
    raw_deadline = proposed.get("deadline")
    if raw_deadline is None or raw_deadline == "":
        opp_validity = DEADLINE_UNKNOWN
        deadline_str = None
    elif isinstance(raw_deadline, str):
        val_str = raw_deadline.strip()
        parsed_deadline = parse_iso_date(val_str)
        if parsed_deadline is not None:
            deadline_str = parsed_deadline.isoformat()
            if parsed_deadline > eval_date:
                opp_validity = DEADLINE_FUTURE
            elif parsed_deadline == eval_date:
                opp_validity = DEADLINE_REACHED
            else:
                opp_validity = DEADLINE_EXPIRED
                warnings.append(f"Oportunidad vencida por fecha límite ({deadline_str} < {as_of_str})")
                affected_fields_set.add("deadline")
        else:
            parsed_dt = parse_iso_timestamp(val_str)
            if parsed_dt is not None:
                deadline_str = parsed_dt.isoformat()
                dt_lima = parsed_dt.astimezone(LIMA_TIMEZONE)
                if dt_lima.date() > eval_date:
                    opp_validity = DEADLINE_FUTURE
                elif dt_lima.date() == eval_date:
                    opp_validity = DEADLINE_REACHED
                else:
                    opp_validity = DEADLINE_EXPIRED
                    warnings.append(f"Oportunidad vencida por fecha límite ({deadline_str} < {as_of_str})")
                    affected_fields_set.add("deadline")
            else:
                opp_validity = DEADLINE_INVALID
                deadline_str = str(raw_deadline)
                errors.append(f"Formato deadline '{raw_deadline}' inválido; debe ser YYYY-MM-DD o ISO 8601 con zona horaria")
                affected_fields_set.add("deadline")
    else:
        opp_validity = DEADLINE_INVALID
        deadline_str = str(raw_deadline)
        errors.append(f"Formato deadline '{raw_deadline}' inválido; debe ser YYYY-MM-DD o ISO 8601 con zona horaria")
        affected_fields_set.add("deadline")

    # 7. Evaluate Field Evidence
    raw_evidence = candidate.get("fieldEvidence")
    if not isinstance(raw_evidence, list):
        errors.append("fieldEvidence debe ser una lista")
        raw_evidence = []

    field_evaluations: list[FieldEvidenceEvaluation] = []
    evidenced_fields_counts: dict[str, int] = {}

    for idx, item in enumerate(raw_evidence):
        item_notes: list[str] = []
        if not isinstance(item, dict):
            errors.append(f"fieldEvidence[{idx}] debe ser un objeto")
            continue

        field_name = str(item.get("field") or "unknown")
        evidenced_fields_counts[field_name] = evidenced_fields_counts.get(field_name, 0) + 1

        is_orphan = field_name not in non_null_proposed
        if is_orphan:
            item_notes.append("Evidencia para campo ausente o nulo en proposed (huérfana)")
            warnings.append(f"Evidencia huérfana para campo '{field_name}'")

        # URL validation
        ev_url = item.get("url")
        if not ev_url or not isinstance(ev_url, str):
            url_status = URL_INVALID
            prov_status = PROVENANCE_HOST_NOT_ALLOWLISTED
            errors.append(f"Evidencia para '{field_name}' carece de URL")
            affected_fields_set.add(field_name)
        else:
            is_https, host = is_valid_https_url(ev_url)
            if not is_https:
                url_status = URL_INVALID
                prov_status = PROVENANCE_HOST_NOT_ALLOWLISTED
                errors.append(f"URL de evidencia para '{field_name}' debe ser HTTPS válida y sin credenciales")
                affected_fields_set.add(field_name)
            else:
                url_status = URL_VALID
                if allowed_hosts and host not in allowed_hosts:
                    prov_status = PROVENANCE_HOST_NOT_ALLOWLISTED
                    errors.append(f"Host '{host}' en evidencia de '{field_name}' no está permitido")
                    affected_fields_set.add(field_name)
                elif not allowed_hosts and src_host and host != src_host:
                    prov_status = PROVENANCE_HOST_NOT_ALLOWLISTED
                    errors.append(f"Host '{host}' en evidencia de '{field_name}' no coincide con el host de sourceUrl '{src_host}'")
                    affected_fields_set.add(field_name)
                elif source_pending_review:
                    prov_status = SOURCE_PENDING
                else:
                    prov_status = PROVENANCE_ALLOWED

        # Freshness validation
        raw_observed = item.get("observedAt")
        if not raw_observed:
            freshness = FRESHNESS_UNKNOWN
            obs_date_str = None
            age_days = None
            errors.append(f"Evidencia para '{field_name}' carece de observedAt")
            affected_fields_set.add(field_name)
        else:
            parsed_dt = parse_iso_timestamp(raw_observed)
            if parsed_dt is None:
                freshness = FRESHNESS_INVALID
                obs_date_str = None
                age_days = None
                errors.append(f"observedAt '{raw_observed}' en '{field_name}' debe ser ISO 8601 con zona horaria")
                affected_fields_set.add(field_name)
            else:
                lima_date = parsed_dt.astimezone(LIMA_TIMEZONE).date()
                obs_date_str = lima_date.isoformat()
                age_days = (eval_date - lima_date).days

                if age_days < 0:
                    freshness = FRESHNESS_FUTURE
                    errors.append(f"observedAt en '{field_name}' está en el futuro ({obs_date_str} > {as_of_str})")
                    affected_fields_set.add(field_name)
                elif age_days <= effective_ttl:
                    freshness = FRESHNESS_FRESH
                else:
                    freshness = FRESHNESS_STALE
                    warnings.append(f"Evidencia en '{field_name}' fuera de TTL ({age_days}d > {effective_ttl}d)")
                    affected_fields_set.add(field_name)

        field_evaluations.append(
            FieldEvidenceEvaluation(
                field=field_name,
                url=str(ev_url) if ev_url else None,
                url_status=url_status,
                provenance_status=prov_status,
                observed_at=str(raw_observed) if raw_observed else None,
                observed_date=obs_date_str,
                freshness_status=freshness,
                age_days=age_days,
                is_orphan=is_orphan,
                remote_availability=REMOTE_NOT_CHECKED,
                notes=tuple(item_notes),
            )
        )

    # 8. Check missing evidence for non-null proposed fields
    for field_name in sorted(non_null_proposed):
        if field_name not in evidenced_fields_counts:
            errors.append(f"Campo propuesto '{field_name}' carece de evidencia de campo")
            affected_fields_set.add(field_name)
        elif evidenced_fields_counts[field_name] > 1:
            warnings.append(f"Campo '{field_name}' tiene múltiples evidencias asociadas ({evidenced_fields_counts[field_name]})")

    # 9. Synthesize Summaries
    structural_status = STRUCTURAL_INVALID if errors else STRUCTURAL_VALID

    has_prov_invalid = (
        (not src_ok)
        or (allowed_hosts and src_host not in allowed_hosts)
        or any(
            e.url_status == URL_INVALID or e.provenance_status == PROVENANCE_HOST_NOT_ALLOWLISTED
            for e in field_evaluations
        )
    )
    if has_prov_invalid:
        prov_summary = PROVENANCE_INVALID
    elif source_pending_review:
        prov_summary = SOURCE_PENDING
    else:
        prov_summary = PROVENANCE_VALID

    if not field_evaluations:
        freshness_summary = SUMMARY_NO_EVIDENCE
    elif any(e.freshness_status in (FRESHNESS_FUTURE, FRESHNESS_INVALID) for e in field_evaluations):
        freshness_summary = SUMMARY_INVALID_TEMPORALITY
    elif all(e.freshness_status == FRESHNESS_FRESH for e in field_evaluations):
        freshness_summary = SUMMARY_ALL_FRESH
    elif all(e.freshness_status in (FRESHNESS_STALE, FRESHNESS_UNKNOWN) for e in field_evaluations):
        freshness_summary = SUMMARY_ALL_STALE
    else:
        freshness_summary = SUMMARY_PARTIALLY_STALE

    # 10. Explanation and Recommended Action
    if opp_validity == DEADLINE_EXPIRED:
        explanation = f"Oportunidad con fecha límite vencida el {deadline_str}."
        action = "Archivar o registrar como histórica; no mantener como activa."
    elif opp_validity == DEADLINE_REACHED:
        explanation = f"Oportunidad alcanza su fecha límite hoy ({as_of_str})."
        action = "Revisar inmediatamente si el canal oficial continúa abierto."
    elif freshness_summary in (SUMMARY_ALL_STALE, SUMMARY_PARTIALLY_STALE):
        explanation = f"Evidencias fuera del TTL editorial ({effective_ttl} días)."
        action = "Revisar nuevamente la fuente para renovar evidencias antes de aprobar."
    elif structural_status == STRUCTURAL_INVALID:
        explanation = "Inconsistencias estructurales o evidencias ausentes detectadas."
        action = "Subsanar campos requeridos y referencias HTTPS antes de revisión."
    elif prov_summary == SOURCE_PENDING:
        explanation = "Fuente en estado pending_review sin autorización formal de uso."
        action = "Completar autorización de fuente antes de promocionar a catálogo."
    else:
        explanation = "Evidencias y vigencia conformes con los criterios vigentes."
        action = "Proceder con la revisión editorial humana."

    return CandidateEvidenceReport(
        candidate_id=candidate_id,
        source_id=source_id,
        as_of=as_of_str,
        ttl_days=effective_ttl,
        structural_status=structural_status,
        provenance_summary=prov_summary,
        freshness_summary=freshness_summary,
        opportunity_validity=opp_validity,
        deadline=deadline_str,
        field_evaluations=tuple(field_evaluations),
        errors=tuple(errors),
        warnings=tuple(warnings),
        affected_fields=tuple(sorted(affected_fields_set)),
        explanation=explanation,
        recommended_action=action,
    )


def verify_candidates_evidence(
    candidates: list[dict],
    *,
    as_of: date | str | None = None,
    sources: dict | None = None,
) -> list[CandidateEvidenceReport]:
    """Verifies a collection of candidates against source definitions and temporal policies."""
    source_map: dict[str, dict] = {}
    if sources and isinstance(sources.get("sources"), list):
        for s in sources["sources"]:
            if isinstance(s, dict) and s.get("id"):
                source_map[s["id"]] = s

    reports: list[CandidateEvidenceReport] = []
    for cand in candidates:
        s_id = cand.get("sourceId") if isinstance(cand, dict) else None
        src = source_map.get(s_id) if s_id else None
        report = verify_candidate_evidence(cand, as_of=as_of, source=src)
        reports.append(report)

    return reports
