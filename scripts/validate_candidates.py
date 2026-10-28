"""Validate a local editorial inbox without network access or catalog writes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collector.policy import load_source_registry  # noqa: E402
from catalog_quality import parse_date, parse_timestamp, valid_https_url  # noqa: E402


DEFAULT_INBOX = ROOT / "data" / "candidates" / "inbox.local.json"
DEFAULT_TTL_DAYS = 7
REVIEW_STATES = {"pending_review", "approved_for_catalog", "rejected"}
PROPOSED_FIELDS = {
    "title", "employer", "publisher", "externalReference", "applyUrl", "publishedAt", "deadline",
    "location", "mode", "opportunityType", "salary", "benefits", "requirements",
}


def validate_payload(payload: object, *, sources: dict, today: date) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict) or payload.get("schemaVersion") != 1:
        return ["inbox debe ser un objeto JSON con schemaVersion=1"], warnings
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return ["candidates debe ser una lista"], warnings

    source_by_id = {item.get("id"): item for item in sources.get("sources", []) if isinstance(item, dict)}
    seen_ids: set[str] = set()
    seen_refs: set[tuple[str, str]] = set()
    for index, candidate in enumerate(candidates):
        prefix = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix} debe ser un objeto")
            continue
        candidate_id = candidate.get("candidateId")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{prefix}.candidateId es obligatorio")
        elif candidate_id in seen_ids:
            errors.append(f"ID de candidato duplicado: {candidate_id}")
        else:
            seen_ids.add(candidate_id)

        source_id = candidate.get("sourceId")
        source = source_by_id.get(source_id)
        if source is None:
            errors.append(f"{prefix}.sourceId no existe en collector/sources.json")
        elif source.get("decision") == "rejected":
            errors.append(f"{prefix}: la fuente está rechazada")
        elif source.get("decision") != "approved":
            warnings.append(f"{candidate_id}: fuente pendiente; candidato local no promocionable")

        source_url = candidate.get("sourceUrl")
        source_ok, source_host = valid_https_url(source_url)
        if not source_ok:
            errors.append(f"{prefix}.sourceUrl debe ser HTTPS")
        elif source and source_host not in source.get("allowedHosts", []):
            errors.append(f"{prefix}.sourceUrl host no está permitido para la fuente")

        try:
            captured = parse_timestamp(candidate.get("capturedAt"), f"{prefix}.capturedAt")
            if captured is None:
                errors.append(f"{prefix}.capturedAt es obligatorio")
            elif captured.astimezone(timezone(timedelta(hours=-5))).date() > today:
                errors.append(f"{prefix}.capturedAt está en el futuro")
        except ValueError as error:
            errors.append(str(error))
        if candidate.get("captureMethod") != "manual":
            errors.append(f"{prefix}.captureMethod debe ser manual (no hay conector autorizado)")

        review = candidate.get("editorialReview")
        if not isinstance(review, dict) or review.get("status") not in REVIEW_STATES:
            errors.append(f"{prefix}.editorialReview.status debe ser pending_review, approved_for_catalog o rejected")
            review = {}
        if any(key in candidate for key in ("opportunityStatus", "verificationStatus", "publicationStatus", "lastVerifiedAt")):
            errors.append(f"{prefix}: un candidato no puede declarar estados del catálogo ni vigencia verificada")

        proposed = candidate.get("proposed")
        if not isinstance(proposed, dict):
            errors.append(f"{prefix}.proposed debe ser un objeto")
            proposed = {}
        extra = set(proposed) - PROPOSED_FIELDS
        if extra:
            errors.append(f"{prefix}.proposed contiene campos desconocidos: {', '.join(sorted(extra))}")
        for field in PROPOSED_FIELDS:
            if field in proposed and proposed[field] is not None and not isinstance(proposed[field], str):
                errors.append(f"{prefix}.proposed.{field} debe ser texto o null")
        for field in ("publishedAt", "deadline"):
            try:
                parse_date(proposed.get(field), f"{prefix}.proposed.{field}")
            except ValueError as error:
                errors.append(str(error))
        apply_url = proposed.get("applyUrl")
        if apply_url:
            if not valid_https_url(apply_url)[0]:
                errors.append(f"{prefix}.proposed.applyUrl debe ser HTTPS")

        evidence = candidate.get("fieldEvidence")
        if not isinstance(evidence, list):
            errors.append(f"{prefix}.fieldEvidence debe ser una lista")
            evidence = []
        evidenced_fields: set[str] = set()
        for evidence_index, item in enumerate(evidence):
            evidence_prefix = f"{prefix}.fieldEvidence[{evidence_index}]"
            if not isinstance(item, dict):
                errors.append(f"{evidence_prefix} debe ser un objeto")
                continue
            field_name = item.get("field")
            if field_name not in PROPOSED_FIELDS:
                errors.append(f"{evidence_prefix}.field no corresponde a un campo propuesto")
            else:
                evidenced_fields.add(field_name)
            if not valid_https_url(item.get("url"))[0]:
                errors.append(f"{evidence_prefix}.url debe ser HTTPS")
            try:
                observed = parse_timestamp(item.get("observedAt"), f"{evidence_prefix}.observedAt")
                if observed is None:
                    errors.append(f"{evidence_prefix}.observedAt es obligatorio")
                elif observed.astimezone(timezone(timedelta(hours=-5))).date() > today:
                    errors.append(f"{evidence_prefix}.observedAt está en el futuro")
            except ValueError as error:
                errors.append(str(error))
        for field, value in proposed.items():
            if value not in (None, "") and field not in evidenced_fields:
                errors.append(f"{prefix}.proposed.{field} carece de evidencia de campo")
            if value in (None, ""):
                warnings.append(f"{candidate_id}: {field} desconocido/no informado")

        external_ref = proposed.get("externalReference")
        if source_id and isinstance(external_ref, str) and external_ref:
            fingerprint = (source_id, external_ref.strip().casefold())
            if fingerprint in seen_refs:
                warnings.append(f"{candidate_id}: posible referencia duplicada; revisar manualmente, sin fusionar")
            seen_refs.add(fingerprint)

        review_status = review.get("status")
        if review_status in {"approved_for_catalog", "rejected"}:
            if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
                errors.append(f"{prefix}.editorialReview.reviewer es obligatorio para una decisión")
            if not isinstance(review.get("decisionNote"), str) or not review["decisionNote"].strip():
                errors.append(f"{prefix}.editorialReview.decisionNote es obligatorio para una decisión")
            try:
                decided = parse_timestamp(review.get("reviewedAt"), f"{prefix}.editorialReview.reviewedAt")
                if decided is None:
                    errors.append(f"{prefix}.editorialReview.reviewedAt es obligatorio para una decisión")
                elif decided.astimezone(timezone(timedelta(hours=-5))).date() > today:
                    errors.append(f"{prefix}.editorialReview.reviewedAt está en el futuro")
            except ValueError as error:
                errors.append(str(error))
        if review_status == "approved_for_catalog":
            if (
                not source
                or source.get("decision") != "approved"
                or source.get("manualReviewStatus") != "approved"
                or source.get("publicReuseStatus") != "approved"
                or source.get("rightsReview") not in {"metadata_only_approved", "content_reuse_approved"}
            ):
                errors.append(f"{prefix}: no puede aprobarse para catálogo con una fuente no autorizada")
            if not evidence:
                errors.append(f"{prefix}: la aprobación editorial requiere evidencia de campo")
            ttl = int(source.get("verificationTtlDays", DEFAULT_TTL_DAYS)) if source else DEFAULT_TTL_DAYS
            stale_before = today - timedelta(days=ttl)
            for item in evidence:
                if not isinstance(item, dict):
                    continue
                try:
                    observed = parse_timestamp(item.get("observedAt"), f"{prefix}.fieldEvidence.observedAt")
                    if observed and observed.astimezone(timezone(timedelta(hours=-5))).date() < stale_before:
                        errors.append(f"{prefix}: evidencia fuera del TTL; revisar de nuevo antes de aprobar")
                        break
                except ValueError:
                    pass
            if not proposed.get("title") or not proposed.get("employer") or not proposed.get("publisher") or not apply_url:
                errors.append(f"{prefix}: título, empleador, entidad difusora y canal de postulación deben estar confirmados para aprobar")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_INBOX)
    args = parser.parse_args(argv)
    if not args.path.exists():
        print(f"No existe {args.path}. Copia data/candidates/inbox.example.json a inbox.local.json para iniciar.", file=sys.stderr)
        return 1
    try:
        payload = json.loads(args.path.read_text(encoding="utf-8"))
        sources = load_source_registry()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"No se pudo validar la bandeja editorial: {error}", file=sys.stderr)
        return 1
    lima_tz = timezone(timedelta(hours=-5))
    errors, warnings = validate_payload(payload, sources=sources, today=datetime.now(lima_tz).date())
    for warning in warnings:
        print(f"ADVERTENCIA: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    count = len(payload["candidates"])
    print(f"Bandeja local válida: {count} candidatos; no se modificó ni se publicó el catálogo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
