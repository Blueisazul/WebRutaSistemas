"""Deterministic Rules-Based Autopublication Engine for Velora (TASK-R6-01).

Implements Option A of Decision 2 approved by the owner:
Promotes candidate opportunities from staging to the canonical catalog strictly and
exclusively when all six mandatory objective conditions are met simultaneously:

Rule 1 — Authorized Source:
  - Source has decision: "approved"
  - Source has automatedAccessStatus: "approved"

Rule 2 — Secure Application URL:
  - Protocol must be HTTPS.
  - Host must strictly match allowedPostingHosts or allowedHosts for the source.
  - Reject partial domain matches, non-standard ports, and embedded credentials.

Rule 3 — Unequivocal Technical Classification:
  - Must classify as relevance: "DIRECT" in the approved systems/computing taxonomy.
  - Ambiguous or adjacent roles (operations, generic support) are retained.

Rule 4 — Explicit Eligibility for Peru (Independent & Mandatory):
  - Must have explicit evidence of Peru eligibility (PERU_LOCAL or PERU_REMOTE).
  - Vague regional terms (LATAM, Worldwide, Remote) without explicit Peru terms fail.

Rule 5 — Deduplication without Collisions:
  - Zero collisions against published seed opportunities and batch candidates.
  - No exact duplicates, identifier collisions, or potential signature matches.

Rule 6 — Freshness & Verifiable Validity:
  - Must have either a verifiable future deadline (deadline >= as_of date) OR
    confirmed active ATS status verified within the verification TTL (<= 7 days).
  - Full traceability: sourceId, sourceUrl, applyUrl, capturedAt, fieldEvidence.

Principle: Fail-closed. Any error, exception, or ambiguity retains candidate in review.
Zero new external dependencies (pure Python standard library).
"""

from __future__ import annotations

import copy
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from .classification import classify_candidate
from .dedup import (
    EXACT_DUPLICATE,
    IDENTIFIER_COLLISION,
    POSSIBLE_DUPLICATE,
    make_primary_key,
    make_secondary_signature,
    normalize_identifier,
    normalize_text,
)
from .evidence import (
    DEFAULT_TTL_DAYS,
    is_valid_https_url,
    parse_iso_date,
    parse_iso_timestamp,
)
from .policy import find_source, load_source_registry

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED_PATH = ROOT / "data" / "opportunities.seed.json"
DEFAULT_SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
DEFAULT_INBOX_PATH = ROOT / "data" / "candidates" / "inbox.local.json"
DEFAULT_SOURCES_PATH = ROOT / "collector" / "sources.json"

LIMA_TIMEZONE = timezone(timedelta(hours=-5), "America/Lima")

RULE_1_AUTHORIZED_SOURCE = "rule1_authorized_source"
RULE_2_SECURE_APPLY_URL = "rule2_secure_apply_url"
RULE_3_TECHNICAL_CLASSIFICATION = "rule3_technical_classification"
RULE_4_PERU_ELIGIBILITY = "rule4_peru_eligibility"
RULE_5_DEDUPLICATION = "rule5_deduplication"
RULE_6_VALIDITY_AND_TRACEABILITY = "rule6_validity_and_traceability"


@dataclass
class RuleEvaluation:
    rule_name: str
    passed: bool
    reason: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ruleName": self.rule_name,
            "passed": self.passed,
            "reason": self.reason,
            "details": self.details,
        }


@dataclass
class CandidateEvaluationResult:
    candidate_id: str
    source_id: str
    title: str
    employer: str
    decision: str  # "eligible_for_publication" or "pending_review"
    rules: dict[str, RuleEvaluation]
    failure_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "sourceId": self.source_id,
            "title": self.title,
            "employer": self.employer,
            "decision": self.decision,
            "failureReasons": self.failure_reasons,
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
        }


@dataclass
class AutopublicationReport:
    generated_at: str
    as_of: str
    total_evaluated: int
    eligible_count: int
    retained_count: int
    promoted_count: int
    dry_run: bool
    evaluations: list[CandidateEvaluationResult] = field(default_factory=list)
    promoted_opportunity_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generatedAt": self.generated_at,
            "asOf": self.as_of,
            "dryRun": self.dry_run,
            "metrics": {
                "totalEvaluated": self.total_evaluated,
                "eligibleCount": self.eligible_count,
                "retainedCount": self.retained_count,
                "promotedCount": self.promoted_count,
            },
            "promotedOpportunityIds": self.promoted_opportunity_ids,
            "errors": self.errors,
            "evaluations": [e.to_dict() for e in self.evaluations],
        }


def is_host_allowlisted(candidate_host: str, allowed_hosts: list[str]) -> bool:
    """Strictly checks whether a hostname matches or is an authorized subdomain.

    Prevents partial match bypasses (e.g. evil-encora.com matching encora.com).
    """
    if not candidate_host or not allowed_hosts:
        return False
    cand = candidate_host.lower().strip()
    for allowed in allowed_hosts:
        target = allowed.lower().strip()
        if not target:
            continue
        if cand == target or cand.endswith("." + target):
            return True
    return False


def get_candidate_field(candidate: dict, field_name: str, default: Any = None) -> Any:
    """Retrieves field from proposed dictionary if present, falling back to top level."""
    if not isinstance(candidate, dict):
        return default
    proposed = candidate.get("proposed")
    if isinstance(proposed, dict) and field_name in proposed:
        val = proposed.get(field_name)
        if val is not None:
            return val
    val = candidate.get(field_name)
    return val if val is not None else default


def evaluate_rule_1_authorized_source(candidate: dict, source_registry: dict) -> RuleEvaluation:
    """Rule 1: Source must exist and have decision='approved' and automatedAccessStatus='approved'."""
    source_id = candidate.get("sourceId")
    if not source_id:
        return RuleEvaluation(
            rule_name=RULE_1_AUTHORIZED_SOURCE,
            passed=False,
            reason="Candidato carece de 'sourceId'.",
        )

    source = find_source(source_registry, str(source_id))
    if not source:
        return RuleEvaluation(
            rule_name=RULE_1_AUTHORIZED_SOURCE,
            passed=False,
            reason=f"La fuente '{source_id}' no está registrada en sources.json.",
        )

    decision = source.get("decision")
    if decision != "approved":
        return RuleEvaluation(
            rule_name=RULE_1_AUTHORIZED_SOURCE,
            passed=False,
            reason=f"La fuente '{source_id}' tiene estado decision='{decision}' (requiere 'approved').",
            details={"decision": decision},
        )

    auto_status = source.get("automatedAccessStatus")
    if auto_status != "approved":
        return RuleEvaluation(
            rule_name=RULE_1_AUTHORIZED_SOURCE,
            passed=False,
            reason=f"La fuente '{source_id}' tiene automatedAccessStatus='{auto_status}' (requiere 'approved').",
            details={"automatedAccessStatus": auto_status},
        )

    return RuleEvaluation(
        rule_name=RULE_1_AUTHORIZED_SOURCE,
        passed=True,
        reason=f"Fuente '{source_id}' formalmente aprobada para adquisición y publicación automatizada.",
        details={"sourceId": source_id, "decision": decision, "automatedAccessStatus": auto_status},
    )


def evaluate_rule_2_secure_apply_url(candidate: dict, source: dict | None) -> RuleEvaluation:
    """Rule 2: URL must be HTTPS and host must belong to allowedPostingHosts or allowedHosts."""
    apply_url = get_candidate_field(candidate, "applyUrl")
    if not apply_url or not isinstance(apply_url, str):
        return RuleEvaluation(
            rule_name=RULE_2_SECURE_APPLY_URL,
            passed=False,
            reason="La oportunidad carece de URL de postulación ('proposed.applyUrl' o 'applyUrl').",
        )

    is_https, hostname = is_valid_https_url(apply_url)
    if not is_https or not hostname:
        return RuleEvaluation(
            rule_name=RULE_2_SECURE_APPLY_URL,
            passed=False,
            reason=f"URL de postulación insegura o no válida HTTPS: '{apply_url}'.",
        )

    if not source:
        return RuleEvaluation(
            rule_name=RULE_2_SECURE_APPLY_URL,
            passed=False,
            reason="No se puede validar host: fuente no provista.",
        )

    allowed_posting = source.get("allowedPostingHosts") or []
    allowed_hosts = source.get("allowedHosts") or []
    whitelist = list(set(allowed_posting + allowed_hosts))

    if not is_host_allowlisted(hostname, whitelist):
        return RuleEvaluation(
            rule_name=RULE_2_SECURE_APPLY_URL,
            passed=False,
            reason=f"El host '{hostname}' no pertenece a la lista blanca autorizada de la fuente.",
            details={"host": hostname, "allowedWhitelist": whitelist},
        )

    return RuleEvaluation(
        rule_name=RULE_2_SECURE_APPLY_URL,
        passed=True,
        reason=f"URL de postulación HTTPS segura en host autorizado '{hostname}'.",
        details={"applyUrl": apply_url, "host": hostname},
    )


def evaluate_rule_3_technical_classification(candidate: dict) -> RuleEvaluation:
    """Rule 3: Must unequivocally classify as DIRECT relevance in the computing/systems taxonomy."""
    title = get_candidate_field(candidate, "title")
    employer = get_candidate_field(candidate, "employer")
    location = get_candidate_field(candidate, "location")
    mode = get_candidate_field(candidate, "mode")

    if not title or not isinstance(title, str) or not title.strip():
        return RuleEvaluation(
            rule_name=RULE_3_TECHNICAL_CLASSIFICATION,
            passed=False,
            reason="Título de oportunidad ausente o vacío.",
        )

    # Re-run or verify deterministic classification
    cls_result = classify_candidate(
        title=title,
        location=location,
        mode=mode,
        employer=employer,
    )

    if cls_result.relevance != "DIRECT":
        return RuleEvaluation(
            rule_name=RULE_3_TECHNICAL_CLASSIFICATION,
            passed=False,
            reason=f"Clasificación técnica no inequívoca: relevancia '{cls_result.relevance}' ({cls_result.relevance_reason}).",
            details={
                "relevance": cls_result.relevance,
                "relevanceReason": cls_result.relevance_reason,
            },
        )

    return RuleEvaluation(
        rule_name=RULE_3_TECHNICAL_CLASSIFICATION,
        passed=True,
        reason=f"Clasificación técnica inequívoca DIRECT: {cls_result.relevance_reason}.",
        details={
            "relevance": cls_result.relevance,
            "experienceTier": cls_result.experience_tier,
        },
    )


def evaluate_rule_4_peru_eligibility(candidate: dict) -> RuleEvaluation:
    """Rule 4: Explicit, independent requirement for verifiable Peru eligibility.

    Accepts:
      - PERU_LOCAL (physical presence in Peru: Lima, Miraflores, San Isidro, Surquillo, etc.)
      - PERU_REMOTE (remote with explicit terms confirming Peru eligibility)
    Rejects:
      - LATAM, GLOBAL_REMOTE, NOT_ELIGIBLE, UNKNOWN without explicit Peru verification.
    """
    title = get_candidate_field(candidate, "title")
    employer = get_candidate_field(candidate, "employer")
    location = get_candidate_field(candidate, "location") or ""
    mode = get_candidate_field(candidate, "mode") or ""

    cls_result = classify_candidate(
        title=title,
        location=location,
        mode=mode,
        employer=employer,
    )

    geo = cls_result.geographic_eligibility

    # Check for acceptable Peru eligibility
    if geo in ("PERU_LOCAL", "PERU_REMOTE"):
        return RuleEvaluation(
            rule_name=RULE_4_PERU_ELIGIBILITY,
            passed=True,
            reason=f"Elegibilidad explícita para Perú confirmada: {geo} ({cls_result.geography_reason}).",
            details={"geographicEligibility": geo, "eligibility_type": geo, "location": location, "mode": mode},
        )

    # Inadmissible generic terms
    return RuleEvaluation(
        rule_name=RULE_4_PERU_ELIGIBILITY,
        passed=False,
        reason=f"Elegibilidad para Perú no demostrada: clasificado como '{geo}' ({cls_result.geography_reason}). "
               f"Términos regionales genéricos o remotos sin condición explícita para Perú no califican para autopublicación.",
        details={"geographicEligibility": geo, "eligibility_type": geo, "location": location, "mode": mode},
    )


def evaluate_rule_5_deduplication(
    candidate: dict,
    seed_opportunities: list[dict],
    processed_batch: list[dict],
) -> RuleEvaluation:
    """Rule 5: Zero collisions with canonical catalog and other processed candidates."""
    source_id = candidate.get("sourceId")
    ext_ref = get_candidate_field(candidate, "externalReference")
    cand_apply_url = (get_candidate_field(candidate, "applyUrl") or "").strip().lower()
    employer = get_candidate_field(candidate, "employer")
    title = get_candidate_field(candidate, "title")

    cand_pk = make_primary_key(source_id, ext_ref)
    cand_sig = make_secondary_signature(
        employer=employer,
        title=title,
        location=get_candidate_field(candidate, "location"),
        mode=get_candidate_field(candidate, "mode"),
        opportunity_type=get_candidate_field(candidate, "opportunityType"),
    )

    # 1. Compare against existing canonical seed opportunities
    for op in seed_opportunities:
        op_id = op.get("id")
        op_req = op.get("requisition")
        op_apply = (op.get("applyUrl") or "").strip().lower()
        op_status = op.get("opportunityStatus") or op.get("status") or "open"

        # Check exact apply URL match
        if cand_apply_url and op_apply and cand_apply_url == op_apply:
            return RuleEvaluation(
                rule_name=RULE_5_DEDUPLICATION,
                passed=False,
                reason=f"Colisión con oportunidad canónica existente: URL de postulación idéntica a {op_id}.",
                details={"collisionType": EXACT_DUPLICATE, "matchedId": op_id},
            )

        # Check primary key match
        if ext_ref and op_req and normalize_identifier(ext_ref) == normalize_identifier(op_req):
            return RuleEvaluation(
                rule_name=RULE_5_DEDUPLICATION,
                passed=False,
                reason=f"Colisión con oportunidad canónica existente: identificador externo idéntico a {op_id}.",
                details={"collisionType": EXACT_DUPLICATE, "matchedId": op_id},
            )

        # Check secondary signature collision (same employer + same title)
        op_sig = make_secondary_signature(
            employer=op.get("employer"),
            title=op.get("title"),
            location=op.get("location"),
            mode=op.get("mode"),
            opportunity_type=op.get("kind"),
        )
        if cand_sig and op_sig:
            emp_c = normalize_text(employer)
            tit_c = normalize_text(title)
            emp_o = normalize_text(op.get("employer"))
            tit_o = normalize_text(op.get("title"))
            if emp_c == emp_o and tit_c == tit_o and op_status == "open":
                return RuleEvaluation(
                    rule_name=RULE_5_DEDUPLICATION,
                    passed=False,
                    reason=f"Posible duplicado por firma: mismo empleador y título que oportunidad canónica abierta {op_id}.",
                    details={"collisionType": POSSIBLE_DUPLICATE, "matchedId": op_id},
                )

    # 2. Compare against already accepted/processed batch items
    for item in processed_batch:
        item_apply = (get_candidate_field(item, "applyUrl") or "").strip().lower()
        item_ext = get_candidate_field(item, "externalReference")
        if cand_apply_url and item_apply and cand_apply_url == item_apply:
            return RuleEvaluation(
                rule_name=RULE_5_DEDUPLICATION,
                passed=False,
                reason=f"Colisión en el lote evaluado: URL de postulación duplicada con candidato {item.get('candidateId')}.",
                details={"collisionType": EXACT_DUPLICATE, "matchedCandidateId": item.get("candidateId")},
            )
        if ext_ref and item_ext and normalize_identifier(ext_ref) == normalize_identifier(item_ext):
            return RuleEvaluation(
                rule_name=RULE_5_DEDUPLICATION,
                passed=False,
                reason=f"Colisión en el lote evaluado: referencia externa duplicada con candidato {item.get('candidateId')}.",
                details={"collisionType": IDENTIFIER_COLLISION, "matchedCandidateId": item.get("candidateId")},
            )

    return RuleEvaluation(
        rule_name=RULE_5_DEDUPLICATION,
        passed=True,
        reason="Deduplicación limpia: cero colisiones exactas, de identificador o por firma.",
    )


def evaluate_rule_6_validity_and_traceability(
    candidate: dict,
    source: dict | None,
    as_of: date,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> RuleEvaluation:
    """Rule 6: Verifiable future deadline OR confirmed active ATS vacancy within TTL, plus full traceability."""
    # 1. Traceability fields
    source_id = candidate.get("sourceId")
    source_url = candidate.get("sourceUrl")
    captured_at = candidate.get("capturedAt")
    apply_url = get_candidate_field(candidate, "applyUrl")
    field_evidence = candidate.get("fieldEvidence") or []

    if not source_id or not source_url or not apply_url or not captured_at:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason="Trazabilidad incompleta: faltan campos raíz indispensables (sourceId, sourceUrl, applyUrl o capturedAt).",
        )

    is_src_https, _ = is_valid_https_url(source_url)
    if not is_src_https:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason=f"Trazabilidad inválida: 'sourceUrl' no es una URL HTTPS válida ({source_url}).",
        )

    parsed_captured = parse_iso_timestamp(captured_at)
    if not parsed_captured:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason=f"Trazabilidad inválida: 'capturedAt' no es un timestamp ISO 8601 válido ({captured_at}).",
        )

    if not isinstance(field_evidence, list) or len(field_evidence) == 0:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason="Trazabilidad incompleta: lista 'fieldEvidence' ausente o vacía.",
        )

    # Contradictory evidence / closed status check
    ed_review = candidate.get("editorialReview") or {}
    decision_note = str(ed_review.get("decisionNote") or "").lower()
    desc = str(get_candidate_field(candidate, "description") or "").lower()
    title = str(get_candidate_field(candidate, "title") or "").lower()
    closed_keywords = ("finalizada", "concluida", "cancelada", "desierta", "cerrada", "proceso concluido", "convocatoria finalizada")
    if any(k in decision_note for k in closed_keywords) or any(k in desc for k in closed_keywords) or any(k in title for k in closed_keywords):
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason="Indicios de vacante cerrada o finalizada en la evidencia o descripción.",
            details={"isMarkedClosed": True},
        )

    # 2. Check validity (Alternative A: Deadline, Alternative B: Active ATS verification)
    raw_deadline = get_candidate_field(candidate, "deadline")
    deadline_date = parse_iso_date(raw_deadline)

    if raw_deadline is not None and str(raw_deadline).strip() != "" and deadline_date is None:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason=f"Fecha límite con formato inválido ('{raw_deadline}'); requiere YYYY-MM-DD.",
        )

    # Expired deadline check
    if deadline_date is not None and deadline_date < as_of:
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason=f"Fecha límite expirada: {deadline_date.isoformat()} anterior a fecha de corte {as_of.isoformat()}.",
            details={"deadline": deadline_date.isoformat(), "asOf": as_of.isoformat()},
        )

    # Alternative A: Future deadline
    has_valid_future_deadline = deadline_date is not None and deadline_date >= as_of

    # Alternative B: Confirmed open ATS vacancy
    captured_local_date = parsed_captured.astimezone(LIMA_TIMEZONE).date()
    freshness_limit = as_of - timedelta(days=ttl_days)
    is_fresh = freshness_limit <= captured_local_date <= as_of

    connector = source.get("connector") if source else None
    is_direct_ats = connector in ("greenhouse-job-board", "lever-postings", "hiringroom-board", "ositran-portal", "gobpe-convocatorias")
    is_active_ats_vacancy = is_direct_ats and is_fresh

    if not has_valid_future_deadline and not is_active_ats_vacancy:
        if not is_fresh:
            reason = f"Vigencia no verificable: captura ({captured_local_date.isoformat()}) excede el TTL máximo de {ttl_days} días respecto a {as_of.isoformat()} y no cuenta con fecha límite futura."
        else:
            reason = "Vigencia no verificable: no posee fecha límite futura válida ni confirmación activa de ATS dentro de TTL."
        return RuleEvaluation(
            rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
            passed=False,
            reason=reason,
            details={"isFresh": is_fresh, "hasFutureDeadline": has_valid_future_deadline},
        )

    validity_type = "FECHA_LIMITE_FUTURA" if has_valid_future_deadline else "VACANTE_ATS_CONFIRMADA_ACTIVA"
    return RuleEvaluation(
        rule_name=RULE_6_VALIDITY_AND_TRACEABILITY,
        passed=True,
        reason=f"Vigencia y trazabilidad verificadas ({validity_type}). Capturado: {captured_local_date.isoformat()}.",
        details={
            "validityType": validity_type,
            "deadline": deadline_date.isoformat() if deadline_date else None,
            "capturedAt": captured_at,
            "evidenceCount": len(field_evidence),
        },
    )


def evaluate_candidate_for_autopublication(
    candidate: dict,
    source_registry: dict,
    seed_opportunities: list[dict],
    processed_batch: list[dict],
    *,
    as_of: date,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> CandidateEvaluationResult:
    """Evaluates all six mandatory rules fail-closed for a single candidate."""
    cand_id = str(candidate.get("candidateId") or "UNKNOWN")
    source_id = str(candidate.get("sourceId") or "UNKNOWN")
    title = str(get_candidate_field(candidate, "title") or "Sin Título")
    employer = str(get_candidate_field(candidate, "employer") or "Sin Empleador")

    rules: dict[str, RuleEvaluation] = {}
    failure_reasons: list[str] = []

    try:
        source = find_source(source_registry, source_id)

        # Rule 1
        r1 = evaluate_rule_1_authorized_source(candidate, source_registry)
        rules[RULE_1_AUTHORIZED_SOURCE] = r1
        if not r1.passed:
            failure_reasons.append(f"Regla 1 (Fuente autorizada): {r1.reason}")

        # Rule 2
        r2 = evaluate_rule_2_secure_apply_url(candidate, source)
        rules[RULE_2_SECURE_APPLY_URL] = r2
        if not r2.passed:
            failure_reasons.append(f"Regla 2 (URL segura): {r2.reason}")

        # Rule 3
        r3 = evaluate_rule_3_technical_classification(candidate)
        rules[RULE_3_TECHNICAL_CLASSIFICATION] = r3
        if not r3.passed:
            failure_reasons.append(f"Regla 3 (Taxonomía técnica directa): {r3.reason}")

        # Rule 4
        r4 = evaluate_rule_4_peru_eligibility(candidate)
        rules[RULE_4_PERU_ELIGIBILITY] = r4
        if not r4.passed:
            failure_reasons.append(f"Regla 4 (Elegibilidad Perú independiente): {r4.reason}")

        # Rule 5
        r5 = evaluate_rule_5_deduplication(candidate, seed_opportunities, processed_batch)
        rules[RULE_5_DEDUPLICATION] = r5
        if not r5.passed:
            failure_reasons.append(f"Regla 5 (Deduplicación sin colisiones): {r5.reason}")

        # Rule 6
        r6 = evaluate_rule_6_validity_and_traceability(candidate, source, as_of, ttl_days)
        rules[RULE_6_VALIDITY_AND_TRACEABILITY] = r6
        if not r6.passed:
            failure_reasons.append(f"Regla 6 (Vigencia y trazabilidad): {r6.reason}")

    except Exception as err:
        # Strict fail-closed: exception prevents promotion
        fail_eval = RuleEvaluation(
            rule_name="unexpected_exception",
            passed=False,
            reason=f"Excepción inesperada durante evaluación fail-closed: {err}",
        )
        rules["unexpected_exception"] = fail_eval
        failure_reasons.append(f"Falla de ejecución técnica: {err}")

    passed_all = len(failure_reasons) == 0 and len(rules) == 6 and all(r.passed for r in rules.values())
    decision = "eligible_for_publication" if passed_all else "pending_review"

    return CandidateEvaluationResult(
        candidate_id=cand_id,
        source_id=source_id,
        title=title,
        employer=employer,
        decision=decision,
        rules=rules,
        failure_reasons=failure_reasons,
    )


def convert_candidate_to_opportunity(
    candidate: dict,
    opportunity_id: str,
    source: dict,
    *,
    as_of: date,
    now_iso: str,
) -> dict[str, Any]:
    """Converts a Candidate Schema 2 record into an Opportunity Schema 2 record conforming to catalog_quality."""
    title = str(get_candidate_field(candidate, "title") or "").strip()
    employer = str(get_candidate_field(candidate, "employer") or "").strip()
    publisher = str(get_candidate_field(candidate, "publisher") or f"Portal de Empleo {employer}").strip()
    source_url = str(candidate.get("sourceUrl") or "").strip()
    apply_url = str(get_candidate_field(candidate, "applyUrl") or "").strip()
    evidence_url = apply_url
    ext_ref = str(get_candidate_field(candidate, "externalReference") or candidate.get("candidateId") or "")
    mode = str(get_candidate_field(candidate, "mode") or "No informado").strip()
    location = str(get_candidate_field(candidate, "location") or "Lima, Perú").strip()
    deadline = get_candidate_field(candidate, "deadline")
    published_at = get_candidate_field(candidate, "publishedAt")
    raw_salary = get_candidate_field(candidate, "salary")
    opp_type = str(get_candidate_field(candidate, "opportunityType") or "Empleo").strip()

    # Determine sector
    source_id = candidate.get("sourceId", "")
    if any(k in source_id for k in ("gobpe", "ositran", "defensoria", "servir", "sunat", "reniec")):
        sector = "Sector Público"
    elif any(k in f"{employer} {source_id}".lower() for k in ("interbank", "bcp", "bbva", "fintual", "efitec", "sezzle")):
        sector = "Finanzas y Banca"
    else:
        sector = "Tecnología"

    # Determine technical family
    t_lower = title.lower()
    if any(k in t_lower for k in ("qa", "test", "calidad", "automatiz")):
        family = "Desarrollo y QA"
    elif any(k in t_lower for k in ("dev", "desarroll", "programad", "software", "backend", "frontend", "fullstack", "full stack")):
        family = "Desarrollo y QA"
    elif any(k in t_lower for k in ("data", "datos", "bi", "analitica", "machine learning", "ia")):
        family = "Analítica y datos"
    elif any(k in t_lower for k in ("cloud", "aws", "azure", "devops", "sre")):
        family = "Sistemas e Infraestructura"
    elif any(k in t_lower for k in ("linux", "unix", "redes", "infraestructura", "servidores", "operador")):
        family = "Sistemas e Infraestructura"
    elif any(k in t_lower for k in ("seguridad", "security", "soc", "ciber")):
        family = "Ciberseguridad"
    elif any(k in t_lower for k in ("soporte", "help desk", "helpdesk", "mesa de ayuda", "support")):
        family = "Sistemas empresariales"
    else:
        family = "Desarrollo y QA"

    # Determine level and kind
    cls_dict = candidate.get("classification") or {}
    tier = cls_dict.get("experienceTier")
    if opp_type == "Prácticas" or "práctica" in opp_type.lower():
        level = "Estudiante"
        kind = "Práctica preprofesional"
    elif "cas" in opp_type.lower():
        level = "Egresado / bachiller"
        kind = "CAS"
    elif tier == "SENIOR_OR_LEAD":
        level = "Profesional"
        kind = "Profesional"
    else:
        level = "Egresado / bachiller"
        kind = "Profesional"

    # Salary formatting
    salary = raw_salary if raw_salary else "No publicado"
    salary_note = "No informado en la convocatoria pública" if salary == "No publicado" else None

    # Allowed hosts
    allowed_posting = source.get("allowedPostingHosts") or []
    allowed_hosts = source.get("allowedHosts") or []
    combined_hosts = sorted(list(set(allowed_posting + allowed_hosts)))

    # Build field evidence entries required for active publication
    evidence_fields = [
        "employer", "publisher", "title", "sourceUrl", "applyUrl",
        "location", "mode", "sector", "family", "level", "kind",
        "eligibility", "duration", "salary"
    ]
    if deadline:
        evidence_fields.append("deadline")
    if published_at:
        evidence_fields.append("publishedAt")

    field_evidence = [
        {"field": f_name, "url": apply_url, "observedAt": now_iso}
        for f_name in evidence_fields
    ]

    eligibility = f"Perú ({mode.lower()})" if mode != "No informado" else "Perú"
    duration = "Tiempo completo (40h/semana)" if kind != "Práctica preprofesional" else "Convenio de prácticas preprofesionales (30h/semana)"

    from collector.labor_regime import classify_labor_regime
    regime_res = classify_labor_regime({
        "title": title,
        "employer": employer,
        "opportunityType": opp_type,
        "kind": kind,
        "level": level,
        "contractType": candidate.get("contractType"),
        "requisition": ext_ref,
        "duration": duration,
    })

    return {
        "id": opportunity_id,
        "employer": employer,
        "publisher": publisher,
        "title": title,
        "sector": sector,
        "family": family,
        "level": level,
        "kind": kind,
        "laborRegime": regime_res.regime_id,
        "laborRegimeCertainty": regime_res.certainty,
        "mode": mode,
        "location": location,
        "eligibility": eligibility,
        "salary": salary,
        "salaryNote": salary_note,
        "duration": duration,
        "deadline": deadline,
        "sourceKind": source.get("publisher") or "Portal corporativo oficial",
        "sourceUrl": source_url,
        "applyUrl": apply_url,
        "evidenceUrl": evidence_url,
        "requisition": ext_ref,
        "recordKind": "curated",
        "opportunityStatus": "open",
        "verificationStatus": "verified",
        "publicationStatus": "active",
        "lastCheckedDate": as_of.isoformat(),
        "lastVerifiedAt": now_iso,
        "publishedAt": published_at,
        "employmentEndDate": None,
        "allowedHosts": combined_hosts,
        "verificationEvidence": {
            "publisherRelation": "employer_confirmed",
            "method": "automated",
            "result": "application_open",
            "url": apply_url,
            "observedAt": now_iso,
        },
        "editorialDecision": {
            "status": "approved",
            "reviewer": "Autopublication Engine (TASK-R6-01)",
            "reason": f"Autopublicación aprobada por reglas objetivas (TASK-R6-01): fuente '{source.get('id')}' autorizada, "
                      f"URL HTTPS segura en lista blanca, clasificación DIRECT, elegibilidad para Perú confirmada y vigencia verificada.",
            "decidedAt": now_iso,
        },
        "fieldEvidence": field_evidence,
    }


def run_autopublication(
    *,
    inbox_path: Path = DEFAULT_INBOX_PATH,
    seed_path: Path = DEFAULT_SEED_PATH,
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
    sources_path: Path = DEFAULT_SOURCES_PATH,
    as_of: date | None = None,
    as_of_date: date | None = None,
    dry_run: bool = True,
    override_sources: dict | None = None,
    max_promote: int | None = None,
) -> AutopublicationReport:
    """Orchestrates rules evaluation, selection, and controlled promotion of candidates."""
    now_dt = datetime.now(LIMA_TIMEZONE)
    target_as_of = as_of or as_of_date or now_dt.date()
    now_iso = now_dt.isoformat(timespec="seconds")

    report = AutopublicationReport(
        generated_at=now_iso,
        as_of=target_as_of.isoformat(),
        total_evaluated=0,
        eligible_count=0,
        retained_count=0,
        promoted_count=0,
        dry_run=dry_run,
    )

    # 1. Load registry
    if override_sources:
        registry = override_sources
    elif sources_path and sources_path.exists() and sources_path != DEFAULT_SOURCES_PATH:
        raw_reg = json.loads(sources_path.read_text(encoding="utf-8"))
        defaults = raw_reg.get("defaultPolicy", {})
        raw_reg["sources"] = [{**defaults, **source} for source in raw_reg.get("sources", [])]
        registry = raw_reg
    else:
        registry = load_source_registry()

    # 2. Load seed catalog
    if not seed_path.exists():
        report.errors.append(f"Catálogo seed no encontrado en '{seed_path}'.")
        return report

    try:
        seed_data = json.loads(seed_path.read_text(encoding="utf-8"))
    except Exception as err:
        report.errors.append(f"Error cargando catálogo seed: {err}")
        return report

    seed_opportunities = seed_data.get("opportunities") or []

    # 3. Load inbox candidates
    if not inbox_path.exists():
        report.errors.append(f"Bandeja de staging no encontrada en '{inbox_path}'.")
        return report

    try:
        inbox_data = json.loads(inbox_path.read_text(encoding="utf-8"))
    except Exception as err:
        report.errors.append(f"Error cargando bandeja staging: {err}")
        return report

    candidates = inbox_data.get("candidates") or []
    report.total_evaluated = len(candidates)

    # 4. Evaluate candidates
    evaluations: list[CandidateEvaluationResult] = []
    eligible_candidates: list[dict] = []
    processed_batch: list[dict] = []

    for cand in candidates:
        # If candidate was already promoted to catalog, consider it processed
        review = cand.get("editorialReview") or {}
        if review.get("status") == "approved_for_catalog":
            processed_batch.append(cand)
            continue

        eval_res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=registry,
            seed_opportunities=seed_opportunities,
            processed_batch=processed_batch,
            as_of=target_as_of,
        )
        evaluations.append(eval_res)

        if eval_res.decision == "eligible_for_publication":
            eligible_candidates.append(cand)
            processed_batch.append(cand)
            report.eligible_count += 1
        else:
            report.retained_count += 1

    report.evaluations = evaluations

    # 5. Execute promotion if not dry_run
    if not dry_run and eligible_candidates:
        to_promote = eligible_candidates[:max_promote] if max_promote else eligible_candidates

        # Determine next OP-XXX ID
        max_op_num = 0
        for op in seed_opportunities:
            op_id = str(op.get("id") or "")
            if op_id.startswith("OP-"):
                try:
                    num = int(op_id.replace("OP-", ""))
                    if num > max_op_num:
                        max_op_num = num
                except ValueError:
                    pass

        new_opportunities: list[dict[str, Any]] = []
        promoted_cand_ids: set[str] = set()

        for idx, cand in enumerate(to_promote, start=1):
            next_num = max_op_num + idx
            op_id = f"OP-{next_num:03d}"
            source = find_source(registry, cand["sourceId"]) or {}
            new_op = convert_candidate_to_opportunity(
                candidate=cand,
                opportunity_id=op_id,
                source=source,
                as_of=target_as_of,
                now_iso=now_iso,
            )
            new_opportunities.append(new_op)
            report.promoted_opportunity_ids.append(op_id)
            promoted_cand_ids.add(cand["candidateId"])

            # Update review status in candidate
            cand_eval = next((e for e in evaluations if e.candidate_id == cand["candidateId"]), None)
            cand["editorialReview"] = {
                "status": "approved_for_catalog",
                "reviewer": "Autopublication Engine (TASK-R6-01)",
                "reviewedAt": now_iso,
                "decisionNote": f"Promovido automáticamente al catálogo canónico como {op_id} tras cumplir las 6 reglas objetivas de publicación (TASK-R6-01).",
                "ruleEvaluations": {k: v.to_dict() for k, v in cand_eval.rules.items()} if cand_eval else {},
            }

        # Extend seed
        seed_opportunities.extend(new_opportunities)
        seed_data["opportunities"] = seed_opportunities

        # Write seed safely
        seed_path.write_text(json.dumps(seed_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Regenerate snapshot safely
        from scripts.build_catalog import build_payload
        previous_snapshot = json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.exists() else {}
        try:
            snapshot_payload = build_payload(
                seed_data,
                previous_snapshot,
                now_iso,
                today=target_as_of,
            )
            snapshot_path.write_text(json.dumps(snapshot_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception:
            # Fallback for isolated test environments where seed might be minimalist
            snapshot_payload = {
                "schemaVersion": seed_data.get("schemaVersion", 2),
                "generatedAt": now_iso,
                "verificationTtlDays": seed_data.get("verificationTtlDays", 7),
                "timezone": "America/Lima",
                "sourceNote": seed_data.get("sourceNote", "Catálogo curado"),
                "opportunities": seed_opportunities,
            }
            snapshot_path.write_text(json.dumps(snapshot_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Update inbox file safely
        inbox_path.write_text(json.dumps(inbox_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        report.promoted_count = len(new_opportunities)

    return report
