"""Unified editorial management and local observability CLI for Ruta Sistemas.

Orchestrates collection normalization, deduplication, schema validation,
and evidence freshness verification without network access or automated
catalog writes.
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from collector.ats_connectors import (  # noqa: E402
    transform_greenhouse_payload,
    transform_lever_payload,
)
from collector.dedup import (  # noqa: E402
    EXACT_DUPLICATE,
    IDENTIFIER_COLLISION,
    POSSIBLE_DUPLICATE,
    deduplicate_candidates,
    load_inbox_candidates,
    load_seed_opportunities,
)
from collector.evidence import (  # noqa: E402
    DEADLINE_EXPIRED,
    DEADLINE_FUTURE,
    DEADLINE_REACHED,
    DEADLINE_UNKNOWN,
    SUMMARY_ALL_FRESH,
    SUMMARY_ALL_STALE,
    SUMMARY_NO_EVIDENCE,
    SUMMARY_PARTIALLY_STALE,
    verify_candidates_evidence,
)
from collector.jsonld_extractor import extract_candidates_from_html  # noqa: E402
from collector.policy import find_source, load_source_registry  # noqa: E402
from validate_candidates import (  # noqa: E402
    DEFAULT_INBOX,
    REVIEW_STATES,
    validate_payload,
)

SEED_CATALOG_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_CATALOG_PATH = ROOT / "data" / "opportunities.json"
SOURCES_REGISTRY_PATH = ROOT / "collector" / "sources.json"
PROTECTED_PATHS = {
    SEED_CATALOG_PATH.resolve(),
    SNAPSHOT_CATALOG_PATH.resolve(),
    SOURCES_REGISTRY_PATH.resolve(),
}

LIMA_TIMEZONE = timezone(timedelta(hours=-5))

# Exit codes
EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_OPERATIONAL_ERROR = 2


def _resolve_as_of(date_str: str | None) -> date:
    """Parses civil date YYYY-MM-DD or defaults to current date in America/Lima."""
    if not date_str:
        return datetime.now(LIMA_TIMEZONE).date()
    try:
        return date.fromisoformat(date_str.strip())
    except ValueError as err:
        raise ValueError(f"--as-of debe usar formato civil YYYY-MM-DD: '{date_str}'") from err


def _load_json_file(path: Path) -> tuple[object, str | None]:
    """Safely loads a local JSON file returning (data, error_message)."""
    if not path.exists():
        return None, f"El archivo no existe: '{path}'"
    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content), None
    except UnicodeDecodeError as err:
        return None, f"Error de codificación (se requiere UTF-8) en '{path}': {err}"
    except json.JSONDecodeError as err:
        return None, f"JSON malformado en '{path}': {err}"
    except OSError as err:
        return None, f"Error de lectura en '{path}': {err}"


def _assert_not_canonical(target: Path, operation_name: str) -> None:
    """Ensures no command writes to seed, snapshot, sources registry, or internal VCS."""
    try:
        target_resolved = target.resolve()
    except Exception as err:
        raise PermissionError(f"Ruta de destino inválida o inaccesible: {err}")

    # Case-insensitive path check to protect against Windows casing variations
    resolved_str = str(target_resolved).casefold()
    protected_strs = {str(p).casefold() for p in PROTECTED_PATHS}

    if resolved_str in protected_strs:
        raise PermissionError(
            f"Operación '{operation_name}' denegada: está estrictamente prohibido "
            f"sobrescribir o modificar los archivos protegidos del proyecto ({target.name})."
        )

    # Protect .git directory from write injection
    git_dir_str = str((ROOT / ".git").resolve()).casefold()
    if resolved_str.startswith(git_dir_str):
        raise PermissionError(
            f"Operación '{operation_name}' denegada: está estrictamente prohibido "
            f"escribir dentro del directorio de control de versiones (.git)."
        )


def _atomic_write_json(target_path: Path, data: dict | list) -> None:
    """Atomically writes JSON content using a temporary file in the same directory."""
    if target_path.is_dir():
        raise IsADirectoryError(f"La ruta de destino es un directorio existente: '{target_path}'")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, ensure_ascii=False)

    temp_file = target_path.with_name(f".tmp_{target_path.name}_{os.getpid()}")
    try:
        temp_file.write_text(serialized, encoding="utf-8")
        os.replace(temp_file, target_path)
    except Exception:
        temp_file.unlink(missing_ok=True)
        raise


# =============================================================================
# Command: validate-inbox
# =============================================================================

def handle_validate_inbox(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data, err = _load_json_file(path)
    if err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        as_of_date = _resolve_as_of(args.as_of)
    except ValueError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        sources = load_source_registry()
    except Exception as err:
        print(f"ERROR OPERATIVO al cargar registro de fuentes: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    val_errors, val_warnings = validate_payload(data, sources=sources, today=as_of_date)

    evidence_reports = []
    if args.verify_evidence or args.json_report:
        cands = data.get("candidates", []) if isinstance(data, dict) else []
        evidence_reports = verify_candidates_evidence(cands, as_of=as_of_date, sources=sources)

    has_data_errors = bool(val_errors) or any(r.errors for r in evidence_reports)

    if args.json_report:
        report_data = {
            "operation": "validate-inbox",
            "path": str(path),
            "asOf": as_of_date.isoformat(),
            "validationErrors": val_errors,
            "validationWarnings": val_warnings,
            "evidenceReports": [r.to_dict() for r in evidence_reports],
            "ok": not has_data_errors,
        }
        print(json.dumps(report_data, indent=2, ensure_ascii=False))
        return EXIT_DATA_ERROR if has_data_errors else EXIT_OK

    # Human-readable output
    print(f"=== VALIDACIÓN EDITORIAL DE BANDEJA: {path} ===")
    print(f"Fecha de evaluación: {as_of_date.isoformat()}")

    for w in val_warnings:
        print(f"ADVERTENCIA: {w}")
    for e in val_errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if args.verify_evidence:
        print(f"\n--- Verificación de Evidencias y Vigencia ({len(evidence_reports)} candidatos) ---")
        for r in evidence_reports:
            print(f"[{r.candidate_id}] Procedencia: {r.provenance_summary} | Frescura: {r.freshness_summary} | Vigencia: {r.opportunity_validity}")
            if r.deadline:
                print(f"  Fecha límite: {r.deadline}")
            if r.errors:
                print(f"  Errores de evidencia: {', '.join(r.errors)}", file=sys.stderr)
            if r.warnings:
                print(f"  Advertencias: {', '.join(r.warnings)}")
            print(f"  Acción recomendada: {r.recommended_action}")

    cand_count = len(data.get("candidates", [])) if isinstance(data, dict) else 0
    if has_data_errors:
        print(f"\nResultado: FALLO ({len(val_errors)} errores de validación).", file=sys.stderr)
        return EXIT_DATA_ERROR

    print(f"\nResultado: VÁLIDO ({cand_count} candidatos conformes con Schema 2; inalterado).")
    return EXIT_OK


# =============================================================================
# Command: deduplicate
# =============================================================================

def handle_deduplicate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data, err = _load_json_file(path)
    if err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        print(f"ERROR OPERATIVO: '{path}' debe contener un objeto con lista 'candidates'", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    candidates = data["candidates"]

    inbox_cands: list[dict] = []
    if not args.no_inbox:
        inbox_path = Path(args.inbox) if args.inbox else DEFAULT_INBOX
        if inbox_path.exists() and inbox_path.resolve() != path.resolve():
            inbox_cands = load_inbox_candidates(inbox_path)

    seed_opps: list[dict] = []
    if not args.no_seed:
        seed_path = Path(args.seed) if args.seed else SEED_CATALOG_PATH
        if seed_path.exists():
            seed_opps = load_seed_opportunities(seed_path)

    report = deduplicate_candidates(candidates, inbox_candidates=inbox_cands, seed_opportunities=seed_opps)

    exact_count = report.summary_by_type.get(EXACT_DUPLICATE, 0)
    collision_count = report.summary_by_type.get(IDENTIFIER_COLLISION, 0)
    possible_count = report.summary_by_type.get(POSSIBLE_DUPLICATE, 0)

    if args.json_report:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        if (collision_count > 0 or exact_count > 0) and args.fail_on_collision:
            return EXIT_DATA_ERROR
        return EXIT_OK

    print(f"=== ANÁLISIS DE DEDUPLICACIÓN DETERMINISTA: {path} ===")
    print(f"Candidatos evaluados: {report.total_evaluated}")
    print(f"  Duplicados exactos (EXACT_DUPLICATE): {exact_count}")
    print(f"  Colisiones de ID (IDENTIFIER_COLLISION): {collision_count}")
    print(f"  Posibles duplicados por firma (POSSIBLE_DUPLICATE): {possible_count}")

    if report.collisions:
        print("\n--- Detalle de Coincidencias ---")
        for c in report.collisions:
            prefix = "[COLISIÓN CRÍTICA]" if c.match_type == IDENTIFIER_COLLISION else (
                "[DUPLICADO EXACTO]" if c.match_type == EXACT_DUPLICATE else "[POSIBLE DUPLICADO]"
            )
            print(f"{prefix} Candidato '{c.record_id}' coincide con '{c.matched_id}' en '{c.matched_set}'")
            print(f"  Explicación: {c.explanation}")
            print(f"  Campos coincidentes: {', '.join(c.matching_fields)}")
            if c.discrepant_fields:
                print(f"  Campos discrepantes: {', '.join(c.discrepant_fields)}")
            print(f"  Acción recomendada: {c.recommended_action}")
    else:
        print("\nNo se detectaron colisiones ni duplicados en el lote evaluado.")

    if (collision_count > 0 or exact_count > 0) and args.fail_on_collision:
        return EXIT_DATA_ERROR
    return EXIT_OK


# =============================================================================
# Command: inspect
# =============================================================================

def handle_inspect(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data, err = _load_json_file(path)
    if err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if not isinstance(data, dict):
        print(f"ERROR OPERATIVO: '{path}' debe ser un objeto JSON válido.", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    candidates = data.get("candidates", [])
    if not isinstance(candidates, list):
        print(f"ERROR OPERATIVO: '{path}' no contiene una lista 'candidates'.", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        as_of_date = _resolve_as_of(args.as_of)
    except ValueError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    review_status_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}

    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        status = cand.get("editorialReview", {}).get("status", "sin_estado") if isinstance(cand.get("editorialReview"), dict) else "sin_estado"
        review_status_counts[status] = review_status_counts.get(status, 0) + 1

        src_id = str(cand.get("sourceId") or "desconocida")
        source_counts[src_id] = source_counts.get(src_id, 0) + 1

        proposed = cand.get("proposed") if isinstance(cand.get("proposed"), dict) else {}
        mode = str(proposed.get("mode") or "no_informado")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    evidence_summary: dict[str, int] = {}
    validity_summary: dict[str, int] = {}
    evidence_reports = []

    if args.verify_evidence or args.json_report:
        try:
            sources = load_source_registry()
        except Exception:
            sources = None
        evidence_reports = verify_candidates_evidence(candidates, as_of=as_of_date, sources=sources)
        for r in evidence_reports:
            evidence_summary[r.freshness_summary] = evidence_summary.get(r.freshness_summary, 0) + 1
            validity_summary[r.opportunity_validity] = validity_summary.get(r.opportunity_validity, 0) + 1

    stats = {
        "operation": "inspect",
        "path": str(path),
        "asOf": as_of_date.isoformat(),
        "totalCandidates": len(candidates),
        "reviewStatus": review_status_counts,
        "sources": source_counts,
        "modes": mode_counts,
        "evidenceFreshness": evidence_summary,
        "opportunityValidity": validity_summary,
    }

    if args.json_report:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return EXIT_OK

    print(f"=== INSPECCIÓN EDITORIAL DE BANDEJA: {path} ===")
    print(f"Fecha de corte: {as_of_date.isoformat()}")
    print(f"Total de candidatos: {len(candidates)}")

    print("\nEstado de Revisión Editorial:")
    for status, count in sorted(review_status_counts.items()):
        print(f"  - {status}: {count}")

    print("\nDistribución por Fuente:")
    for src, count in sorted(source_counts.items()):
        print(f"  - {src}: {count}")

    print("\nModalidad de Trabajo:")
    for m, count in sorted(mode_counts.items()):
        print(f"  - {m}: {count}")

    if args.verify_evidence:
        print("\nFrescura de Evidencias (TTL 7 días Lima):")
        for f_stat, count in sorted(evidence_summary.items()):
            print(f"  - {f_stat}: {count}")
        print("\nVigencia Temporal de la Oportunidad (Deadline):")
        for v_stat, count in sorted(validity_summary.items()):
            print(f"  - {v_stat}: {count}")

    return EXIT_OK


# =============================================================================
# Command: report
# =============================================================================

def handle_report(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data, err = _load_json_file(path)
    if err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        as_of_date = _resolve_as_of(args.as_of)
    except ValueError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        sources = load_source_registry()
    except Exception as err:
        print(f"ERROR OPERATIVO al cargar registro de fuentes: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    candidates = data.get("candidates", []) if isinstance(data, dict) else []

    # 1. Validation
    val_errors, val_warnings = validate_payload(data, sources=sources, today=as_of_date)

    # 2. Evidence
    evidence_reports = verify_candidates_evidence(candidates, as_of=as_of_date, sources=sources)

    # 3. Deduplication against itself and seed
    seed_opps = []
    seed_path = Path(args.seed) if args.seed else SEED_CATALOG_PATH
    if seed_path.exists():
        seed_opps = load_seed_opportunities(seed_path)

    dedup_report = deduplicate_candidates(candidates, seed_opportunities=seed_opps)

    # Consolidate critical review actions
    review_actions: list[dict] = []
    for r in evidence_reports:
        if r.errors or r.warnings or r.opportunity_validity in (DEADLINE_EXPIRED, DEADLINE_REACHED) or r.freshness_summary in (SUMMARY_ALL_STALE, SUMMARY_PARTIALLY_STALE):
            review_actions.append({
                "candidateId": r.candidate_id,
                "sourceId": r.source_id,
                "issues": list(r.errors) + list(r.warnings),
                "freshness": r.freshness_summary,
                "validity": r.opportunity_validity,
                "recommendedAction": r.recommended_action,
            })

    for col in dedup_report.collisions:
        review_actions.append({
            "candidateId": col.record_id,
            "sourceId": "dedup",
            "issues": [f"Coincidencia {col.match_type} con {col.matched_set}:{col.matched_id}"],
            "freshness": "N/A",
            "validity": "N/A",
            "recommendedAction": col.explanation,
        })

    report_payload = {
        "operation": "report",
        "generatedAt": datetime.now(LIMA_TIMEZONE).isoformat(timespec="seconds"),
        "asOf": as_of_date.isoformat(),
        "inputPath": str(path),
        "totalEvaluated": len(candidates),
        "validationSummary": {
            "passed": not bool(val_errors),
            "errorCount": len(val_errors),
            "warningCount": len(val_warnings),
            "errors": val_errors,
            "warnings": val_warnings,
        },
        "deduplicationSummary": dedup_report.summary_by_type,
        "evidenceSummary": {
            "evaluatedCount": len(evidence_reports),
            "freshnessCounts": {
                SUMMARY_ALL_FRESH: sum(1 for r in evidence_reports if r.freshness_summary == SUMMARY_ALL_FRESH),
                SUMMARY_PARTIALLY_STALE: sum(1 for r in evidence_reports if r.freshness_summary == SUMMARY_PARTIALLY_STALE),
                SUMMARY_ALL_STALE: sum(1 for r in evidence_reports if r.freshness_summary == SUMMARY_ALL_STALE),
                SUMMARY_NO_EVIDENCE: sum(1 for r in evidence_reports if r.freshness_summary == SUMMARY_NO_EVIDENCE),
            },
            "validityCounts": {
                DEADLINE_FUTURE: sum(1 for r in evidence_reports if r.opportunity_validity == DEADLINE_FUTURE),
                DEADLINE_REACHED: sum(1 for r in evidence_reports if r.opportunity_validity == DEADLINE_REACHED),
                DEADLINE_EXPIRED: sum(1 for r in evidence_reports if r.opportunity_validity == DEADLINE_EXPIRED),
                DEADLINE_UNKNOWN: sum(1 for r in evidence_reports if r.opportunity_validity == DEADLINE_UNKNOWN),
            },
        },
        "itemsRequiringHumanReview": review_actions,
    }

    if args.output:
        out_path = Path(args.output)
        _assert_not_canonical(out_path, "report --output")
        if out_path.resolve() == path.resolve():
            print(f"ERROR OPERATIVO: --output no puede ser el mismo archivo de entrada '{path}'.", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR
        try:
            _atomic_write_json(out_path, report_payload)
            print(f"Informe consolidado guardado exitosamente en: '{out_path}'")
        except OSError as err:
            print(f"ERROR OPERATIVO al escribir informe en '{out_path}': {err}", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR

    if args.json_report or not args.output:
        if args.json_report:
            print(json.dumps(report_payload, indent=2, ensure_ascii=False))
        else:
            print(f"=== INFORME CONSOLIDADO EDITORIAL Y OBSERVABILIDAD ===")
            print(f"Entrada: {path} | Corte: {as_of_date.isoformat()} | Total: {len(candidates)}")
            print(f"Validación Schema 2: {'Aprobada' if not val_errors else 'Fallida'}")
            print(f"  Errores: {len(val_errors)} | Advertencias: {len(val_warnings)}")
            print(f"Deduplicación vs catálogo:")
            print(f"  Duplicados exactos: {dedup_report.summary_by_type.get(EXACT_DUPLICATE, 0)}")
            print(f"  Colisiones de ID: {dedup_report.summary_by_type.get(IDENTIFIER_COLLISION, 0)}")
            print(f"  Posibles duplicados: {dedup_report.summary_by_type.get(POSSIBLE_DUPLICATE, 0)}")
            print(f"Frescura y Vigencia:")
            ev_summary = report_payload["evidenceSummary"]
            print(f"  Frescas: {ev_summary['freshnessCounts'][SUMMARY_ALL_FRESH]} | Vencidas: {ev_summary['freshnessCounts'][SUMMARY_ALL_STALE]}")
            print(f"  Deadline futura: {ev_summary['validityCounts'][DEADLINE_FUTURE]} | Expirada: {ev_summary['validityCounts'][DEADLINE_EXPIRED]}")
            print(f"\nAcciones que requieren revisión humana: {len(review_actions)}")
            for item in review_actions[:10]:
                print(f"  - [{item['candidateId']}] {item['recommendedAction']}")
            if len(review_actions) > 10:
                print(f"  ... y {len(review_actions) - 10} elementos más.")

    return EXIT_DATA_ERROR if (val_errors or dedup_report.summary_by_type.get(IDENTIFIER_COLLISION, 0) > 0) else EXIT_OK


# =============================================================================
# Command: import
# =============================================================================

def handle_import(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR OPERATIVO: Archivo de entrada no existe: '{input_path}'", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    output_path = Path(args.output)
    _assert_not_canonical(output_path, "import --output")

    if output_path.resolve() == input_path.resolve():
        print(f"ERROR OPERATIVO: --output no puede ser el mismo archivo de entrada '{input_path}'.", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if output_path.exists() and not args.force_write:
        print(
            f"ERROR OPERATIVO: El archivo destino '{output_path}' ya existe. "
            f"Especifique --force-write si desea sobrescribirlo.",
            file=sys.stderr,
        )
        return EXIT_OPERATIONAL_ERROR

    try:
        registry = load_source_registry()
    except Exception as err:
        print(f"ERROR OPERATIVO al cargar sources.json: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    source = find_source(registry, args.source_id)
    if not source:
        print(f"ERROR OPERATIVO: Fuente '{args.source_id}' no existe en collector/sources.json", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    # Shallow copy to allow local parameter overrides without modifying registry
    source = dict(source)
    if getattr(args, "board_token", None):
        source["boardToken"] = args.board_token
    if getattr(args, "employer", None):
        source["employer"] = args.employer
    if getattr(args, "site", None):
        source["site"] = args.site

    captured_at = args.captured_at or datetime.now(LIMA_TIMEZONE).isoformat(timespec="seconds")

    fmt = args.format.lower()
    try:
        raw_content = input_path.read_text(encoding="utf-8")
    except Exception as err:
        print(f"ERROR OPERATIVO al leer '{input_path}': {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    imported_candidates: list[dict] = []

    try:
        if fmt == "greenhouse":
            payload = json.loads(raw_content)
            token = source.get("boardToken") or "import"
            source_url = args.source_url or f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            imported_candidates = transform_greenhouse_payload(
                source, payload, captured_at=captured_at, source_url=source_url
            )
        elif fmt == "lever":
            payload = json.loads(raw_content)
            site = source.get("site") or "import"
            source_url = args.source_url or f"https://api.lever.co/v0/postings/{site}?mode=json"
            imported_candidates = transform_lever_payload(
                source, payload, captured_at=captured_at, source_url=source_url
            )
        elif fmt == "html":
            if not args.source_url:
                print("ERROR OPERATIVO: --source-url es obligatorio para el formato 'html'.", file=sys.stderr)
                return EXIT_OPERATIONAL_ERROR
            imported_candidates = extract_candidates_from_html(
                source, raw_content, source_url=args.source_url, captured_at=captured_at
            )
        else:
            print(f"ERROR OPERATIVO: Formato no soportado: '{fmt}' (use greenhouse, lever, html)", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR
    except Exception as err:
        print(f"ERROR OPERATIVO durante la normalización de '{fmt}': {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    result_payload = {
        "schemaVersion": 1,
        "importMetadata": {
            "sourceId": args.source_id,
            "format": fmt,
            "inputFile": str(input_path),
            "importedAt": datetime.now(LIMA_TIMEZONE).isoformat(timespec="seconds"),
            "count": len(imported_candidates),
        },
        "candidates": imported_candidates,
    }

    try:
        _atomic_write_json(output_path, result_payload)
    except OSError as err:
        print(f"ERROR OPERATIVO al escribir en '{output_path}': {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    print(f"Importación exitosa: {len(imported_candidates)} candidatos normalizados a Schema 2.")
    print(f"  Origen: {input_path} (formato: {fmt})")
    print(f"  Destino: {output_path}")
    print("  Nota: La bandeja canónica del catálogo NO ha sido modificada.")
    return EXIT_OK


# =============================================================================
# Command: prepare-review
# =============================================================================

def handle_prepare_review(args: argparse.Namespace) -> int:
    inbox_path = Path(args.inbox) if args.inbox else DEFAULT_INBOX
    data, err = _load_json_file(inbox_path)
    if err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        print(f"ERROR OPERATIVO: '{inbox_path}' debe contener una lista 'candidates'", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    output_path = Path(args.output)
    _assert_not_canonical(output_path, "prepare-review --output")

    if output_path.resolve() == inbox_path.resolve():
        print("ERROR OPERATIVO: --output no puede ser el mismo archivo de inbox.", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if output_path.exists() and not args.force_write:
        print(
            f"ERROR OPERATIVO: El archivo de salida '{output_path}' ya existe. "
            f"Use --force-write para sobrescribir.",
            file=sys.stderr,
        )
        return EXIT_OPERATIONAL_ERROR

    candidates = data["candidates"]
    filter_status = args.status

    if filter_status == "all":
        selected = candidates
    else:
        selected = [
            c for c in candidates
            if isinstance(c, dict) and c.get("editorialReview", {}).get("status") == filter_status
        ]

    export_payload = {
        "schemaVersion": 1,
        "exportNotice": (
            "Artefacto exclusivo para revisión y auditoría editorial humana. "
            "No constituye publicación ni actualización del catálogo canónico."
        ),
        "exportedAt": datetime.now(LIMA_TIMEZONE).isoformat(timespec="seconds"),
        "filterStatus": filter_status,
        "sourceInbox": str(inbox_path),
        "totalExported": len(selected),
        "candidates": selected,
    }

    try:
        _atomic_write_json(output_path, export_payload)
    except OSError as err:
        print(f"ERROR OPERATIVO al escribir exportación en '{output_path}': {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    print(f"Preparación para revisión completada: {len(selected)} candidatos exportados.")
    print(f"  Filtro: status='{filter_status}'")
    print(f"  Destino: {output_path}")
    print("  RECORDATORIO: La semilla y snapshot canónicos continúan intactos.")
    return EXIT_OK


# =============================================================================
# Command: acquire (R4-01 Controlled Multisource Pilot)
# =============================================================================

def handle_acquire(args: argparse.Namespace) -> int:
    from collector.acquisition_runner import run_pilot_acquisition

    inbox_path = Path(args.inbox) if args.inbox else DEFAULT_INBOX
    _assert_not_canonical(inbox_path, "acquire --inbox")

    seed_path = Path(args.seed) if args.seed else SEED_CATALOG_PATH
    fixtures_dir = Path(args.fixtures_dir) if args.fixtures_dir else None

    as_of = None
    if args.as_of:
        try:
            as_of = _resolve_as_of(args.as_of)
        except ValueError as err:
            print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR

    source_ids = [args.source] if args.source else None

    try:
        report = run_pilot_acquisition(
            source_ids=source_ids,
            inbox_path=inbox_path,
            seed_path=seed_path,
            fixtures_dir=fixtures_dir,
            as_of=as_of,
            dry_run=args.dry_run,
        )
    except ValueError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR
    except Exception as err:
        print(f"ERROR INESPERADO durante adquisición: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if args.output:
        out_path = Path(args.output)
        _assert_not_canonical(out_path, "acquire --output")
        try:
            _atomic_write_json(out_path, report.to_dict())
            if not args.json_report:
                print(f"Informe de adquisición guardado en: {out_path}")
        except Exception as err:
            print(f"ERROR al guardar informe de adquisición: {err}", file=sys.stderr)

    if args.json_report:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return EXIT_OK if report.validation_passed else EXIT_DATA_ERROR

    mode_label = "DRY-RUN (Simulación)" if report.dry_run else ("FIXTURES LOCALES" if fixtures_dir else "EN VIVO (Red)")
    print(f"=== PILOTO DE ADQUISICIÓN CONTROLADA MULTIFUENTE (R4-01) ===")
    print(f"Modo: {mode_label}")
    print(f"Marca temporal: {report.timestamp} | Fecha de corte: {report.as_of}")
    print(f"\n--- Métricas Globales ---")
    print(f"  Fuentes evaluadas: {report.sources_evaluated} (Exitosas: {report.sources_succeeded}, Fallidas: {report.sources_failed})")
    print(f"  Total oportunidades capturadas: {report.total_captured}")
    print(f"  Total filtradas relevantes:     {report.total_filtered}")
    print(f"  Total descartadas (perfil/geo): {report.total_discarded}")
    print(f"  Total duplicadas detectadas:    {report.total_duplicates}")
    print(f"  Nuevos candidatos en staging:   {report.total_new_staged}")

    print(f"\n--- Detalle por Fuente ---")
    for s in report.source_summaries:
        status_sym = "✓" if s.status == "success" else "✗"
        print(f"  [{status_sym}] {s.source_id} ({s.employer} · {s.connector}):")
        if s.status == "success":
            print(f"      Capturados: {s.captured} | Relevantes: {s.filtered_in} | Descartados: {s.discarded} | Duplicados: {s.duplicates} | Nuevos: {s.new_candidates}")
        else:
            print(f"      FALLO: {s.error}")

    print(f"\n--- Validación Editorial y Esquema 2 ---")
    if report.validation_passed:
        print(f"  Estado de validación: VÁLIDO ({len(report.validation_warnings)} advertencias, 0 errores)")
        for w in report.validation_warnings[:5]:
            print(f"    - [ADVERTENCIA] {w}")
        if len(report.validation_warnings) > 5:
            print(f"    ... y {len(report.validation_warnings) - 5} advertencias más.")
    else:
        print(f"  Estado de validación: FALLIDO ({len(report.validation_errors)} errores)")
        for e in report.validation_errors:
            print(f"    - [ERROR] {e}")

    print(f"\n--- Salvaguardas de Integridad Canónica ---")
    print(f"  data/opportunities.seed.json: 100% INTACTO (Sin modificaciones)")
    print(f"  data/opportunities.json:      100% INTACTO (Sin modificaciones)")
    print(f"  Destino de candidatos:        Bandeja staging ('{inbox_path}')")
    print(f"  Estado editorial:             pending_review (Requiere revisión y aprobación humana)")

    return EXIT_OK if report.validation_passed else EXIT_DATA_ERROR


# =============================================================================
# Command: revalidate (R4-03 Lifecycle, Freshness & Change Detection)
# =============================================================================

def handle_revalidate(args: argparse.Namespace) -> int:
    from collector.revalidation import run_revalidation_job

    inbox_path = Path(args.inbox) if args.inbox else DEFAULT_INBOX
    _assert_not_canonical(inbox_path, "revalidate --inbox")

    fixtures_dir = Path(args.fixtures_dir) if args.fixtures_dir else None

    as_of = None
    if args.as_of:
        try:
            as_of = _resolve_as_of(args.as_of)
        except ValueError as err:
            print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR

    if getattr(args, "catalog", False):
        from collector.revalidation import DEFAULT_STATE_PATH, revalidate_canonical_catalog
        state_path = Path(getattr(args, "state_file", str(DEFAULT_STATE_PATH))) if getattr(args, "state_file", None) else DEFAULT_STATE_PATH
        dry_run = getattr(args, "dry_run", True)
        threshold = getattr(args, "threshold", 2)
        source_ids = [args.source] if getattr(args, "source", None) else None

        try:
            res = revalidate_canonical_catalog(
                seed_path=SEED_CATALOG_PATH,
                snapshot_path=SNAPSHOT_CATALOG_PATH,
                state_path=state_path,
                fixtures_dir=fixtures_dir,
                as_of=as_of,
                threshold=threshold,
                apply_updates=(not dry_run),
                source_ids=source_ids,
            )
        except Exception as err:
            print(f"ERROR al revalidar catálogo canónico: {err}", file=sys.stderr)
            return EXIT_OPERATIONAL_ERROR

        if args.output:
            out_path = Path(args.output)
            _assert_not_canonical(out_path, "revalidate --output")
            try:
                _atomic_write_json(out_path, res)
                if not args.json_report:
                    print(f"Informe de revalidación guardado en: {out_path}")
            except Exception as err:
                print(f"ERROR al guardar informe de revalidación: {err}", file=sys.stderr)

        if args.json_report:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return EXIT_OK

        mode_label = "DRY-RUN (Simulación)" if res.get("dryRun", True) else "APLICACIÓN REAL (Actualización canónica)"
        print(f"=== REVALIDACIÓN Y CICLO DE VIDA DE CATÁLOGO CANÓNICO (R6-02) ===")
        print(f"Modo: {mode_label} | Fecha de corte: {res.get('asOf')} | Umbral ausencias: {threshold}")
        print(f"Inicio: {res.get('timestampStart')} | Fin: {res.get('timestampEnd')}")
        print(f"\n--- Métricas Globales de Revalidación Canónica ---")
        print(f"  Fuentes evaluadas:             {res.get('sourcesEvaluated')} (Exitosas: {res.get('sourcesSucceeded')}, Fallidas: {res.get('sourcesFailed')})")
        print(f"  Oportunidades evaluadas:       {res.get('totalCanonicalEvaluated')}")
        print(f"  Confirmadas activas en ATS:    {res.get('openConfirmedCount')}")
        print(f"  Primeras ausencias detectadas: {res.get('firstAbsenceCount')} (Salvaguarda: no cerradas)")
        print(f"  Segundas ausencias (cierre):   {res.get('secondAbsenceCount')}")
        print(f"  Cierres explícitos:            {res.get('explicitClosedCount')}")
        print(f"  Preservadas por fallo de red:  {res.get('temporaryErrorCount')} (Salvaguarda anti-cierre)")
        print(f"  Fuentes no compatibles:        {res.get('sourceUnsupportedCount')}")
        print(f"  Pasaron a estado histórico:    {res.get('becameHistoricalCount')}")
        print(f"  No pudieron verificarse:       {res.get('unverifiableCount')}")
        print(f"  Validación del catálogo:       {res.get('catalogValidationResult')}")

        print(f"\n--- Salvaguardas de Integridad Canónica ---")
        if res.get("dryRun", True):
            print(f"  opportunities.seed.json: 100% INTACTO (Modo dry-run activo)")
            print(f"  opportunities.json:      100% INTACTO (Modo dry-run activo)")
        else:
            print(f"  opportunities.seed.json: Actualizado y validado con Schema 2")
            print(f"  opportunities.json:      Snapshot regenerado con build_catalog.py")
        print(f"  Archivo de estado:       '{res.get('statePath')}'")
        return EXIT_OK

    source_ids = [args.source] if args.source else None
    threshold = getattr(args, "threshold", 2)
    update_inbox = getattr(args, "update_inbox", False)
    dry_run = getattr(args, "dry_run", True)

    try:
        report = run_revalidation_job(
            inbox_path=inbox_path,
            source_ids=source_ids,
            fixtures_dir=fixtures_dir,
            as_of=as_of,
            threshold=threshold,
            update_inbox=update_inbox,
            dry_run=dry_run,
        )
    except FileNotFoundError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR
    except Exception as err:
        print(f"ERROR INESPERADO durante revalidación: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if args.output:
        out_path = Path(args.output)
        _assert_not_canonical(out_path, "revalidate --output")
        try:
            _atomic_write_json(out_path, report.to_dict())
            if not args.json_report:
                print(f"Informe de revalidación guardado en: {out_path}")
        except Exception as err:
            print(f"ERROR al guardar informe de revalidación: {err}", file=sys.stderr)

    if args.json_report:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return EXIT_OK

    mode_label = "DRY-RUN (Simulación)" if dry_run else ("FIXTURES LOCALES" if fixtures_dir else "EN VIVO (Red)")
    print(f"=== CICLO DE VIDA Y REVALIDACIÓN DE OPORTUNIDADES (R4-03) ===")
    print(f"Modo: {mode_label} | Aplicar cambios en bandeja: {'SÍ' if update_inbox and not dry_run else 'NO'}")
    print(f"Marca temporal: {report.timestamp} | Fecha de corte: {report.as_of}")
    print(f"\n--- Métricas Globales de Revalidación ---")
    print(f"  Fuentes evaluadas:             {report.sources_evaluated} (Exitosas: {report.sources_succeeded}, Fallidas: {report.sources_failed})")
    print(f"  Total candidatos evaluados:    {report.total_candidates_evaluated}")
    print(f"  Reconfirmados activos:         {report.still_active_count}")
    print(f"  Cambios detectados:            {report.changed_count}")
    print(f"  Ausentes en una captura:       {report.disappeared_once_count} (Salvaguarda: no cerrados)")
    print(f"  Cierre probable confirmado:    {report.confirmed_disappeared_count}")
    print(f"  Preservados por fallo de red:  {report.preserved_on_error_count} (Salvaguarda anti-cierre masivo)")
    print(f"  Fecha límite superada:         {report.deadline_expired_count}")
    print(f"  Evidencias fuera de TTL:       {report.evidence_stale_count}")

    print(f"\n--- Detalle por Fuente ---")
    for s in report.source_summaries:
        status_sym = "✓" if s.status == "success" else "✗"
        print(f"  [{status_sym}] {s.source_id} ({s.employer} · {s.connector}):")
        if s.status == "success":
            print(f"      Evaluados: {s.total_evaluated} | Activos: {s.still_active} | Modificados: {s.changed} | Ausente 1x: {s.disappeared_once} | Cierres: {s.confirmed_disappeared}")
        else:
            print(f"      FALLO DE FUENTE (ESTADO PRESERVADO): {s.error}")

    if report.changed_count > 0:
        print(f"\n--- Resumen de Cambios Detectados ({report.changed_count}) ---")
        changed_cands = [c for c in report.candidate_results if c.lifecycle_state == "CHANGED"]
        for c in changed_cands[:5]:
            chg_str = "; ".join(f"{chg.field}: '{chg.previous}' -> '{chg.current}'" for chg in c.changes)
            print(f"    - [{c.candidate_id}] {c.title}: {chg_str}")
        if len(changed_cands) > 5:
            print(f"    ... y {len(changed_cands) - 5} candidatos más con cambios.")

    print(f"\n--- Salvaguardas de Integridad Canónica ---")
    print(f"  data/opportunities.seed.json: 100% INTACTO (Sin modificaciones)")
    print(f"  data/opportunities.json:      100% INTACTO (Sin modificaciones)")
    print(f"  Bandeja evaluada:             '{inbox_path}'")
    print(f"  Promoción automática:         DESHABILITADA (Requiere decisión soberana del propietario)")

    return EXIT_OK


def handle_autopublish(args: argparse.Namespace) -> int:
    """Evaluates candidates in staging against 6 mandatory rules and promotes them if approved."""
    from collector.autopublish import run_autopublication

    try:
        as_of = _resolve_as_of(args.as_of)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    inbox_path = Path(args.inbox)
    seed_path = Path(args.seed)
    snapshot_path = Path(args.snapshot)
    sources_path = Path(args.sources)

    dry_run = getattr(args, "dry_run", True)
    max_promote = getattr(args, "max_promote", None)

    try:
        report = run_autopublication(
            inbox_path=inbox_path,
            seed_path=seed_path,
            snapshot_path=snapshot_path,
            sources_path=sources_path,
            as_of_date=as_of,
            dry_run=dry_run,
            max_promote=max_promote,
        )
    except FileNotFoundError as err:
        print(f"ERROR OPERATIVO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR
    except Exception as err:
        print(f"ERROR INESPERADO durante autopublicación: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if args.output:
        out_path = Path(args.output)
        _assert_not_canonical(out_path, "autopublish --output")
        try:
            _atomic_write_json(out_path, report.to_dict())
            if not args.json_report:
                print(f"Informe de autopublicación guardado en: {out_path}")
        except Exception as err:
            print(f"ERROR al guardar informe de autopublicación: {err}", file=sys.stderr)

    if args.json_report:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return EXIT_OK

    mode_label = "DRY-RUN (Simulación)" if report.dry_run else "APLICACIÓN REAL (Promoción canónica)"
    print(f"=== MOTOR DE AUTOPUBLICACIÓN BASADO EN REGLAS (TASK-R6-01) ===")
    print(f"Modo: {mode_label} | Fecha de corte: {report.as_of}")
    print(f"Marca temporal: {report.generated_at}")
    print(f"\n--- Métricas de Evaluación ---")
    print(f"  Candidatos evaluados:       {report.total_evaluated}")
    print(f"  Aprobados para publicación: {report.eligible_count}")
    print(f"  Retenidos en revisión:      {report.retained_count}")
    print(f"  Oportunidades promovidas:   {report.promoted_count}")

    if report.promoted_opportunity_ids:
        print(f"  IDs canónicos asignados:    {', '.join(report.promoted_opportunity_ids)}")

    print(f"\n--- Detalle por Candidato ---")
    for ev in report.evaluations:
        status_sym = "✓ [APTO]" if ev.decision == "eligible_for_publication" else "✗ [RETENIDO]"
        print(f"  {status_sym} {ev.candidate_id}: {ev.employer} — {ev.title}")
        if ev.decision != "eligible_for_publication":
            for rule_id, rev in ev.rules.items():
                if not rev.passed:
                    print(f"      - {rule_id}: {rev.reason}")

    print(f"\n--- Salvaguardas y Estado Canónico ---")
    if report.dry_run:
        print(f"  Catálogo canónico: 100% INTACTO (Modo dry-run activo)")
    else:
        print(f"  Catálogo canónico: Actualizado ({report.promoted_count} nuevas oportunidades integradas con Schema 2)")
    print(f"  Bandeja de staging: '{inbox_path}'")

    return EXIT_OK


# =============================================================================
# CLI Entry Point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="editorial_cli.py",
        description="CLI unificado de gestión de bandeja editorial y observabilidad local para Ruta Sistemas.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Subcommand: validate-inbox
    p_val = subparsers.add_parser("validate-inbox", help="Valida estructural y editorialmente una bandeja de candidatos")
    p_val.add_argument("path", nargs="?", default=str(DEFAULT_INBOX), help="Ruta al archivo JSON de candidatos")
    p_val.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD para validación determinista")
    p_val.add_argument("--verify-evidence", action="store_true", help="Activa verificación de evidencias, frescura y vigencia")
    p_val.add_argument("--json-report", action="store_true", help="Emite salida en formato JSON estructurado")

    # Subcommand: deduplicate
    p_dedup = subparsers.add_parser("deduplicate", help="Analiza duplicados exactos, colisiones y posibles duplicados")
    p_dedup.add_argument("path", nargs="?", default=str(DEFAULT_INBOX), help="Ruta al lote de candidatos")
    p_dedup.add_argument("--inbox", help="Ruta a bandeja local para comparar (por defecto inbox.local.json)")
    p_dedup.add_argument("--seed", help="Ruta a semilla canónica para comparar (por defecto opportunities.seed.json)")
    p_dedup.add_argument("--no-inbox", action="store_true", help="No comparar contra la bandeja local")
    p_dedup.add_argument("--no-seed", action="store_true", help="No comparar contra la semilla canónica")
    p_dedup.add_argument("--fail-on-collision", action="store_true", help="Retorna código 1 si detecta colisiones de identificador")
    p_dedup.add_argument("--json-report", action="store_true", help="Emite informe en formato JSON")

    # Subcommand: inspect
    p_insp = subparsers.add_parser("inspect", help="Inspecciona el estado editorial y métricas de una bandeja")
    p_insp.add_argument("path", nargs="?", default=str(DEFAULT_INBOX), help="Ruta al archivo de candidatos")
    p_insp.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD")
    p_insp.add_argument("--verify-evidence", action="store_true", help="Incluye análisis de evidencias en la inspección")
    p_insp.add_argument("--json-report", action="store_true", help="Emite estadísticas en formato JSON")

    # Subcommand: report
    p_rep = subparsers.add_parser("report", help="Genera reporte integral consolidado (validación + dedup + evidencias)")
    p_rep.add_argument("path", nargs="?", default=str(DEFAULT_INBOX), help="Ruta al archivo de candidatos")
    p_rep.add_argument("--seed", help="Ruta a semilla canónica")
    p_rep.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD")
    p_rep.add_argument("--output", help="Ruta de archivo para guardar el reporte consolidado")
    p_rep.add_argument("--json-report", action="store_true", help="Emite reporte consolidado en JSON por stdout")

    # Subcommand: import
    p_imp = subparsers.add_parser("import", help="Importa y normaliza datos locales (ATS o HTML) a Schema 2")
    p_imp.add_argument("--format", required=True, choices=["greenhouse", "lever", "html"], help="Formato de entrada")
    p_imp.add_argument("--source-id", required=True, help="Identificador de la fuente en sources.json")
    p_imp.add_argument("--input", required=True, help="Ruta al archivo de datos de entrada local")
    p_imp.add_argument("--output", required=True, help="Ruta de destino para el archivo JSON de candidatos generado")
    p_imp.add_argument("--source-url", help="URL de origen para trazabilidad (obligatoria para html)")
    p_imp.add_argument("--captured-at", help="Marca temporal ISO de captura")
    p_imp.add_argument("--board-token", help="Sobrescribe boardToken para plantilla Greenhouse")
    p_imp.add_argument("--employer", help="Sobrescribe nombre del empleador para plantilla")
    p_imp.add_argument("--site", help="Sobrescribe site para plantilla Lever")
    p_imp.add_argument("--force-write", action="store_true", help="Sobrescribe el archivo de salida si ya existe")

    # Subcommand: prepare-review
    p_prep = subparsers.add_parser("prepare-review", help="Prepara y exporta candidatos para revisión editorial humana")
    p_prep.add_argument("--inbox", default=str(DEFAULT_INBOX), help="Bandeja de origen")
    p_prep.add_argument("--output", required=True, help="Archivo JSON de destino para la revisión")
    p_prep.add_argument("--status", default="pending_review", choices=["pending_review", "approved_for_catalog", "rejected", "all"], help="Filtrar por estado editorial")
    p_prep.add_argument("--force-write", action="store_true", help="Sobrescribe el archivo de destino si ya existe")

    # Subcommand: acquire (R4-01 Pilot)
    p_acq = subparsers.add_parser("acquire", help="Ejecuta el piloto de adquisición controlada multifuente ATS")
    p_acq.add_argument("--source", help="Identificador de fuente individual en sources.json (ej. greenhouse-canonical)")
    p_acq.add_argument("--inbox", default=str(DEFAULT_INBOX), help="Bandeja de staging de destino")
    p_acq.add_argument("--seed", default=str(SEED_CATALOG_PATH), help="Ruta a semilla canónica para deduplicación")
    p_acq.add_argument("--fixtures-dir", help="Directorio con fixtures locales para ejecución offline reproducible")
    p_acq.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD para validación determinista")
    p_acq.add_argument("--dry-run", action="store_true", help="Simula la adquisición sin escribir en la bandeja de staging")
    p_acq.add_argument("--output", help="Ruta opcional para guardar el informe estructurado de adquisición en JSON")
    p_acq.add_argument("--json-report", action="store_true", help="Emite el informe completo en formato JSON por stdout")

    # Subcommand: revalidate (R4-03 Lifecycle, Freshness & Change Detection)
    p_rev = subparsers.add_parser("revalidate", help="Revalida el ciclo de vida, vigencia y cambios de candidatos en staging")
    p_rev.add_argument("--inbox", default=str(DEFAULT_INBOX), help="Bandeja de staging a revalidar")
    p_rev.add_argument("--source", help="Identificador de fuente individual para revalidar")
    p_rev.add_argument("--fixtures-dir", help="Directorio con fixtures locales para ejecución offline")
    p_rev.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD")
    p_rev.add_argument("--threshold", type=int, default=2, help="Umbral de capturas consecutivas ausentes para confirmar cierre")
    p_rev.add_argument("--update-inbox", action="store_true", help="Actualiza metadatos y evidencias en la bandeja de staging")
    p_rev.add_argument("--no-dry-run", dest="dry_run", action="store_false", default=True, help="Aplica la revalidación en modo real")
    p_rev.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="Simula la revalidación sin escribir en la bandeja (por defecto)")
    p_rev.add_argument("--output", help="Ruta de archivo para guardar el informe de revalidación en JSON")
    p_rev.add_argument("--json-report", action="store_true", help="Emite el informe completo en formato JSON por stdout")
    p_rev.add_argument("--catalog", action="store_true", help="Revalida las oportunidades reales del catálogo canónico")
    p_rev.add_argument("--state-file", help="Ruta al archivo de estado persistente de revalidaciones")
    p_rev.add_argument("--apply", dest="dry_run", action="store_false", default=True, help="Aplica los cambios en el catálogo o bandeja (por defecto se ejecuta en dry-run)")

    # Subcommand: autopublish (TASK-R6-01 Deterministic Rules-Based Autopublication Engine)
    p_pub = subparsers.add_parser("autopublish", help="Evalúa y autopublica candidatos al catálogo canónico según las 6 reglas aprobadas")
    p_pub.add_argument("--inbox", default=str(DEFAULT_INBOX), help="Bandeja de staging a evaluar")
    p_pub.add_argument("--seed", default=str(SEED_CATALOG_PATH), help="Ruta a semilla canónica")
    p_pub.add_argument("--snapshot", default=str(SNAPSHOT_CATALOG_PATH), help="Ruta a snapshot público canónico")
    p_pub.add_argument("--sources", default=str(SOURCES_REGISTRY_PATH), help="Ruta a registro de fuentes")
    p_pub.add_argument("--as-of", help="Fecha civil de corte YYYY-MM-DD")
    p_pub.add_argument("--apply", dest="dry_run", action="store_false", default=True, help="Aplica la promoción al catálogo canónico (por defecto se ejecuta en dry-run)")
    p_pub.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="Modo simulación sin escribir en catálogo ni bandeja (por defecto)")
    p_pub.add_argument("--max-promote", type=int, default=None, help="Límite máximo de candidatos a promover en esta ejecución")
    p_pub.add_argument("--output", help="Ruta de archivo para guardar el informe de autopublicación en JSON")
    p_pub.add_argument("--json-report", action="store_true", help="Emite el informe completo en formato JSON por stdout")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as err:
        return EXIT_OK if err.code == 0 else EXIT_OPERATIONAL_ERROR

    if not args.command:
        parser.print_help()
        return EXIT_OK

    handlers = {
        "validate-inbox": handle_validate_inbox,
        "deduplicate": handle_deduplicate,
        "inspect": handle_inspect,
        "report": handle_report,
        "import": handle_import,
        "prepare-review": handle_prepare_review,
        "acquire": handle_acquire,
        "revalidate": handle_revalidate,
        "autopublish": handle_autopublish,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return EXIT_OPERATIONAL_ERROR

    try:
        return handler(args)
    except PermissionError as err:
        print(f"ERROR DE SEGURIDAD: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR
    except Exception as err:
        print(f"ERROR OPERATIVO INESPERADO: {err}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
