"""Validation and publication rules for the canonical opportunity catalog."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit


DEFAULT_TTL_DAYS = 7
LOCAL_TIMEZONE = "America/Lima"
OPPORTUNITY_STATES = {"open", "closed", "expired", "unknown"}
VERIFICATION_STATES = {"verified", "pending", "stale", "unverified"}
PUBLICATION_STATES = {"active", "unconfirmed", "historical"}
RECORD_KINDS = {"demonstration", "curated", "imported_unreviewed"}
EDITORIAL_DECISIONS = {"approved", "rejected", "withdrawn"}
EVIDENCE_FIELDS = {
    "employer", "publisher", "title", "sourceUrl", "applyUrl", "publishedAt", "deadline",
    "location", "mode", "salary", "benefits", "contractType", "duration", "requirements",
    "skills", "training", "tasks", "eligibility", "sector", "family", "level", "kind", "growth",
    "continuity", "risk",
}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LIMA_TZ = timezone(timedelta(hours=-5), "America/Lima")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_date(value: object, field_name: str) -> date | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        raise ValueError(f"{field_name} debe usar YYYY-MM-DD o quedar vacío")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} no es una fecha civil válida") from error


def parse_timestamp(value: object, field_name: str) -> datetime | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} debe ser un timestamp ISO 8601 con zona horaria")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} no es un timestamp ISO 8601 válido") from error
    if result.tzinfo is None:
        raise ValueError(f"{field_name} debe incluir zona horaria")
    return result.astimezone(timezone.utc)


def valid_https_url(value: object) -> tuple[bool, str | None]:
    if not isinstance(value, str) or not value:
        return False, None
    try:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return False, None
        if parsed.port not in (None, 443):
            return False, None
        return True, parsed.hostname.lower()
    except ValueError:
        return False, None


def effective_states(record: dict, *, today: date, ttl_days: int = DEFAULT_TTL_DAYS) -> dict[str, str]:
    """Derive conservative public states; catalog generation is not evidence."""
    opportunity = record.get("opportunityStatus", "unknown")
    verification = record.get("verificationStatus", "unverified")
    publication = record.get("publicationStatus", "unconfirmed")
    deadline = parse_date(record.get("deadline"), "deadline")
    checked = parse_timestamp(record.get("lastVerifiedAt"), "lastVerifiedAt")
    checked_local_date = checked.astimezone(LIMA_TZ).date() if checked else None

    if deadline and deadline < today and opportunity not in {"closed", "expired"}:
        opportunity = "expired"
    if verification == "verified":
        if checked_local_date is None or checked_local_date < today - timedelta(days=ttl_days):
            verification = "stale"
    evidence = record.get("verificationEvidence")
    evidence_url = evidence.get("url") if isinstance(evidence, dict) else None
    observed_at = parse_timestamp(evidence.get("observedAt"), "verificationEvidence.observedAt") if isinstance(evidence, dict) else None
    observed_local_date = observed_at.astimezone(LIMA_TZ).date() if observed_at else None
    source_ok, source_host = valid_https_url(record.get("sourceUrl"))
    evidence_ok, evidence_host = valid_https_url(evidence_url)
    apply_ok, apply_host = valid_https_url(record.get("applyUrl"))
    raw_hosts = record.get("allowedHosts", [])
    allowed_hosts = set(raw_hosts) if isinstance(raw_hosts, list) and all(isinstance(host, str) for host in raw_hosts) else set()
    hosts_ok = source_ok and evidence_ok and apply_ok and bool(allowed_hosts) and all(
        host in allowed_hosts for host in (source_host, evidence_host, apply_host)
    )
    evidence_complete = (
        isinstance(evidence, dict)
        and evidence.get("publisherRelation") == "employer_confirmed"
        and evidence.get("method") == "manual"
        and evidence.get("result") == "application_open"
        and observed_local_date is not None
        and today - timedelta(days=ttl_days) <= observed_local_date <= today
        and hosts_ok
    )
    can_publish = (
        publication == "active"
        and opportunity == "open"
        and verification == "verified"
        and checked is not None
        and checked_local_date is not None
        and checked_local_date >= today - timedelta(days=ttl_days)
        and (deadline is None or deadline >= today)
        and record.get("recordKind") != "demonstration"
        and evidence_complete
        and _active_editorial_evidence_complete(record, today=today, ttl_days=ttl_days)
    )
    if not can_publish and publication == "active":
        publication = "unconfirmed"
    return {
        "opportunityStatus": opportunity,
        "verificationStatus": verification,
        "publicationStatus": publication,
    }


def _active_editorial_evidence_complete(record: dict, *, today: date, ttl_days: int) -> bool:
    """Require traceable field claims and an explicit human approval for active cards."""
    decision = record.get("editorialDecision")
    if not isinstance(decision, dict) or decision.get("status") != "approved":
        return False
    if not all(isinstance(decision.get(key), str) and decision[key].strip() for key in ("reviewer", "reason")):
        return False
    try:
        decided_at = parse_timestamp(decision.get("decidedAt"), "editorialDecision.decidedAt")
    except ValueError:
        return False
    if decided_at is None or decided_at.astimezone(LIMA_TZ).date() > today:
        return False

    entries = record.get("fieldEvidence")
    if not isinstance(entries, list):
        return False
    by_field: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("field"), str):
            continue
        by_field[entry["field"]] = entry

    required = {"employer", "publisher", "title", "sourceUrl", "applyUrl"}
    if any(record.get(field_name) in (None, "") for field_name in ("employer", "publisher", "title", "sourceUrl", "applyUrl")):
        return False
    # Any supplied condition is a factual claim and therefore needs its own source.
    optional_facts = {"publishedAt", "deadline", "location", "mode", "salary", "benefits", "contractType", "duration", "requirements", "skills", "training", "tasks", "eligibility", "sector", "family", "level", "kind", "growth", "continuity", "risk"}
    required.update(field_name for field_name in optional_facts if record.get(field_name) not in (None, ""))
    for field_name in required:
        entry = by_field.get(field_name)
        if not entry:
            return False
        ok, host = valid_https_url(entry.get("url"))
        if not ok or host not in record.get("allowedHosts", []):
            return False
        try:
            observed = parse_timestamp(entry.get("observedAt"), f"fieldEvidence.{field_name}.observedAt")
        except ValueError:
            return False
        if observed is None:
            return False
        observed_day = observed.astimezone(LIMA_TZ).date()
        if observed_day > today or observed_day < today - timedelta(days=ttl_days):
            return False
    return True


def validate_records(
    records: object,
    *,
    today: date,
    ttl_days: int = DEFAULT_TTL_DAYS,
    allow_empty: bool = False,
    previous_ids: set[str] | None = None,
) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(records, list):
        result.errors.append("opportunities debe ser una lista")
        return result
    if not records and not allow_empty:
        result.errors.append("el catálogo de publicación no puede estar vacío")
        return result
    if ttl_days < 1 or ttl_days > 30:
        result.errors.append("verificationTtlDays debe estar entre 1 y 30 días")
    seen: set[str] = set()
    fingerprints: dict[tuple[str, str, str], str] = {}
    for index, item in enumerate(records):
        prefix = f"opportunities[{index}]"
        if not isinstance(item, dict):
            result.errors.append(f"{prefix} debe ser un objeto")
            continue
        record_id = item.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            result.errors.append(f"{prefix}.id es obligatorio")
        elif record_id in seen:
            result.errors.append(f"ID duplicado: {record_id}")
        else:
            seen.add(record_id)
        for key in ("employer", "title", "recordKind", "opportunityStatus", "verificationStatus", "publicationStatus"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                result.errors.append(f"{prefix}.{key} es obligatorio")
        if item.get("opportunityStatus") not in OPPORTUNITY_STATES:
            result.errors.append(f"{prefix}.opportunityStatus inválido")
        if item.get("verificationStatus") not in VERIFICATION_STATES:
            result.errors.append(f"{prefix}.verificationStatus inválido")
        if item.get("recordKind") not in RECORD_KINDS:
            result.errors.append(f"{prefix}.recordKind inválido")
        if item.get("publicationStatus") not in PUBLICATION_STATES:
            result.errors.append(f"{prefix}.publicationStatus inválido")
        try:
            deadline = parse_date(item.get("deadline"), f"{prefix}.deadline")
            parse_date(item.get("publishedAt"), f"{prefix}.publishedAt")
            parse_date(item.get("employmentEndDate"), f"{prefix}.employmentEndDate")
            parse_date(item.get("lastCheckedDate"), f"{prefix}.lastCheckedDate")
            checked = parse_timestamp(item.get("lastVerifiedAt"), f"{prefix}.lastVerifiedAt")
            if isinstance(item.get("verificationEvidence"), dict):
                observed = parse_timestamp(item["verificationEvidence"].get("observedAt"), f"{prefix}.verificationEvidence.observedAt")
                if observed and observed.astimezone(LIMA_TZ).date() > today:
                    result.errors.append(f"{prefix}: verificationEvidence.observedAt está en el futuro")
            if checked and checked.astimezone(LIMA_TZ).date() > today:
                result.errors.append(f"{prefix}: lastVerifiedAt está en el futuro")
            if item.get("verificationStatus") == "verified" and checked is None:
                result.errors.append(f"{prefix}: verificada requiere lastVerifiedAt")
            if deadline and deadline < today and item.get("opportunityStatus") not in {"expired", "closed"}:
                result.errors.append(f"{prefix}: fecha límite pasada; marcar opportunityStatus=expired")
            if deadline and deadline < today and item.get("publicationStatus") == "active":
                result.errors.append(f"{prefix}: fecha límite pasada; no puede publicarse como activa")
            states = effective_states(item, today=today, ttl_days=ttl_days)
            if item.get("opportunityStatus") == "open" and states["opportunityStatus"] != "open":
                result.errors.append(f"{prefix}: el estado declarado contradice la fecha límite; usar {states['opportunityStatus']}")
            if item.get("verificationStatus") == "verified" and states["verificationStatus"] != "verified":
                result.errors.append(f"{prefix}: la verificación excede el TTL; usar stale")
            if item.get("publicationStatus") == "active" and states["publicationStatus"] != "active":
                result.errors.append(f"{prefix}: faltan evidencia, vigencia o condiciones para publicación activa")
            if item.get("publicationStatus") == "historical" and item.get("recordKind") == "demonstration":
                result.warnings.append(f"{record_id}: registro histórico de demostración")
            elif item.get("publicationStatus") != "active":
                result.warnings.append(f"{record_id}: no se presenta como oportunidad activa")
            if item.get("recordKind") == "demonstration" and item.get("publicationStatus") == "active":
                result.errors.append(f"{prefix}: registro demostrativo no puede publicarse activo")
            for field_name in ("sector", "family", "level", "mode"):
                if item.get(field_name) in {"No especificado", "Por clasificar", "", None}:
                    result.warnings.append(f"{record_id}: {field_name} sin clasificar o no informado")
            fingerprint = tuple(str(item.get(name, "")).strip().casefold() for name in ("employer", "title", "location"))
            if all(fingerprint) and fingerprint in fingerprints:
                result.warnings.append(
                    f"{record_id}: posible duplicado de {fingerprints[fingerprint]}; revisar sin fusionar automáticamente"
                )
            elif all(fingerprint):
                fingerprints[fingerprint] = str(record_id)
        except ValueError as error:
            result.errors.append(f"{prefix}: {error}")
        source_ok, source_host = valid_https_url(item.get("sourceUrl"))
        if not source_ok:
            result.errors.append(f"{prefix}.sourceUrl debe ser HTTPS")
        allowed_hosts = item.get("allowedHosts", [])
        if not isinstance(allowed_hosts, list) or any(not isinstance(host, str) for host in allowed_hosts):
            result.errors.append(f"{prefix}.allowedHosts debe ser lista de hosts")
            allowed_hosts = []
        elif source_ok and source_host not in allowed_hosts:
            result.errors.append(f"{prefix}.sourceUrl host no está permitido")
        url_fields = ["applyUrl", "evidenceUrl"]
        evidence = item.get("verificationEvidence")
        if isinstance(evidence, dict):
            url_fields.append("verificationEvidence.url")
        for key in url_fields:
            value = evidence.get("url") if key == "verificationEvidence.url" and isinstance(evidence, dict) else item.get(key)
            if value:
                ok, host = valid_https_url(value)
                if not ok:
                    result.errors.append(f"{prefix}.{key} debe ser HTTPS y usar puerto estándar")
                elif host not in allowed_hosts:
                    result.errors.append(f"{prefix}.{key} host no está permitido")
        evidence = item.get("verificationEvidence")
        if item.get("publicationStatus") == "active" and not isinstance(evidence, dict):
            result.errors.append(f"{prefix}: oportunidad activa requiere verificationEvidence")
        publisher = item.get("publisher")
        if publisher is not None and not isinstance(publisher, str):
            result.errors.append(f"{prefix}.publisher debe ser texto o null; distingue a quien difunde del empleador")
        field_evidence = item.get("fieldEvidence", [])
        if not isinstance(field_evidence, list):
            result.errors.append(f"{prefix}.fieldEvidence debe ser una lista")
            field_evidence = []
        seen_evidence_fields: set[str] = set()
        for evidence_index, entry in enumerate(field_evidence):
            item_prefix = f"{prefix}.fieldEvidence[{evidence_index}]"
            if not isinstance(entry, dict) or entry.get("field") not in EVIDENCE_FIELDS:
                result.errors.append(f"{item_prefix}.field inválido")
                continue
            field_name = entry["field"]
            if field_name in seen_evidence_fields:
                result.errors.append(f"{prefix}.fieldEvidence repite el campo {field_name}")
            seen_evidence_fields.add(field_name)
            ok, host = valid_https_url(entry.get("url"))
            if not ok or host not in allowed_hosts:
                result.errors.append(f"{item_prefix}.url debe ser HTTPS en un host permitido")
            try:
                observed_at = parse_timestamp(entry.get("observedAt"), f"{item_prefix}.observedAt")
                if observed_at and observed_at.astimezone(LIMA_TZ).date() > today:
                    result.errors.append(f"{item_prefix}.observedAt no puede estar en el futuro")
            except ValueError as error:
                result.errors.append(f"{item_prefix}: {error}")
        decision = item.get("editorialDecision")
        if decision is not None:
            if not isinstance(decision, dict) or decision.get("status") not in EDITORIAL_DECISIONS:
                result.errors.append(f"{prefix}.editorialDecision debe registrar approved, rejected o withdrawn")
            elif decision.get("status") in {"rejected", "withdrawn"} and not str(decision.get("reason", "")).strip():
                result.errors.append(f"{prefix}.editorialDecision.reason es obligatorio para rechazar o retirar")
        if item.get("publicationStatus") == "active" and not _active_editorial_evidence_complete(item, today=today, ttl_days=ttl_days):
            result.errors.append(f"{prefix}: publicación activa requiere aprobación editorial y evidencia reciente por campo")
        if isinstance(decision, dict) and decision.get("decidedAt"):
            try:
                decided_at = parse_timestamp(decision.get("decidedAt"), f"{prefix}.editorialDecision.decidedAt")
                if decided_at and decided_at.astimezone(LIMA_TZ).date() > today:
                    result.errors.append(f"{prefix}.editorialDecision.decidedAt no puede estar en el futuro")
            except ValueError as error:
                result.errors.append(f"{prefix}: {error}")
    if previous_ids is not None:
        lost = sorted(previous_ids - seen)
        if lost:
            result.errors.append("la generación perdería registros previos: " + ", ".join(lost))
    return result


def validate_payload(payload: object, *, today: date, allow_empty: bool = False, previous_ids: set[str] | None = None) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(payload, dict):
        result.errors.append("el catálogo debe ser un objeto JSON")
        return result
    if payload.get("schemaVersion") != 2:
        result.errors.append("schemaVersion debe ser 2")
    if not isinstance(payload.get("sourceNote"), str) or not payload["sourceNote"].strip():
        result.errors.append("sourceNote es obligatorio")
    if payload.get("timezone") != LOCAL_TIMEZONE:
        result.errors.append(f"timezone debe ser {LOCAL_TIMEZONE}")
    try:
        generated = parse_timestamp(payload.get("generatedAt"), "generatedAt")
        if generated is None:
            result.errors.append("generatedAt es obligatorio")
        elif generated.astimezone(LIMA_TZ).date() > today:
            result.errors.append("generatedAt no puede estar en el futuro respecto de la fecha de validación")
    except ValueError as error:
        result.errors.append(str(error))
    ttl = payload.get("verificationTtlDays", DEFAULT_TTL_DAYS)
    if not isinstance(ttl, int) or isinstance(ttl, bool):
        result.errors.append("verificationTtlDays debe ser entero")
        ttl = DEFAULT_TTL_DAYS
    nested = validate_records(payload.get("opportunities"), today=today, ttl_days=ttl, allow_empty=allow_empty, previous_ids=previous_ids)
    result.errors.extend(nested.errors)
    result.warnings.extend(nested.warnings)
    return result


def load_json(path: Path) -> object:
    try:
        return parse_json_text(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"No se pudo leer JSON válido en {path}: {error}") from error


def parse_json_text(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON malformado: {error}") from error
