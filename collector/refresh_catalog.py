"""Refresh the public catalog from individually approved ATS sources.

Only source metadata is collected. No dependencies beyond Python's standard
library are required. Disabled/unreviewed sources are never contacted.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .ats_connectors import fetch_greenhouse_board, fetch_lever_board
from .policy import load_source_registry


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
CATALOG_PATH = ROOT / "data" / "opportunities.json"
FETCHERS = {
    "greenhouse-job-board": fetch_greenhouse_board,
    "lever-postings": fetch_lever_board,
}


def _date(iso_value: str) -> str:
    return datetime.fromisoformat(iso_value).astimezone(timezone.utc).strftime("%d/%m/%Y")


def _as_public_opportunity(record: dict) -> dict:
    checked = _date(record["capturedAt"])
    workplace = (record.get("workplaceType") or "").lower()
    mode = next((value for key, value in (
        ("remote", "Remoto"), ("hybrid", "Híbrido"), ("on-site", "Presencial"), ("onsite", "Presencial")
    ) if key in workplace), "No especificado")
    location = record.get("location") or "No especificada"
    location = f"{location} · {mode}" if mode != "No especificado" else location
    stable_id = f"ATS-{record['sourceId']}-{record['externalId']}"
    return {
        "id": stable_id,
        "employer": record["employer"],
        "title": record["title"],
        "sector": "Por clasificar",
        "family": "Por clasificar",
        "level": "No especificado",
        "kind": "No especificado",
        "mode": mode,
        "location": location,
        "eligibility": "No especificado",
        "salary": "No publicado",
        "duration": "No especificada",
        "published": "No especificada",
        "checked": checked,
        "status": "verified",
        "sourceKind": "Portal oficial (ATS)",
        "sourceUrl": record["canonicalUrl"],
        "applyUrl": record["canonicalUrl"],
        "requisition": record["externalId"],
        "tasks": "No especificadas en la ficha automática. Consultar la fuente oficial.",
        "requirements": "No especificados en la ficha automática. Consultar la fuente oficial.",
        "skills": "No especificadas",
        "growth": "Aún no evaluado; requiere revisión del contenido y del puesto.",
        "risk": "La publicación se encontró en el tablero oficial el " + checked + ". Las condiciones y funciones requieren revisión.",
        "continuity": "No especificada; no implica continuidad asegurada.",
        "benefits": "No especificados",
        "history": False,
        "sourceId": record["sourceId"],
        "externalId": record["externalId"],
        "publicationStatus": "open",
        "verificationStatus": "official_board_present",
    }


def refresh() -> tuple[bool, str]:
    registry = load_source_registry()
    enabled = [source for source in registry["sources"] if source.get("enabled")]
    if not enabled:
        return False, "No hay fuentes activadas y aprobadas; no se consultó ningún portal."

    collected = []
    errors = []
    for source in enabled:
        fetcher = FETCHERS.get(source.get("connector"))
        if fetcher is None:
            errors.append(f"{source['id']}: conector no implementado")
            continue
        try:
            records = fetcher(source, request_count=0)
            collected.extend(_as_public_opportunity(record) for record in records)
        except Exception as error:  # Fail the run closed; do not publish partial results.
            errors.append(f"{source['id']}: {error}")
        delay = max(0, int(source.get("minDelayMs", 0))) / 1000
        if delay:
            time.sleep(delay)
    if errors:
        raise RuntimeError("; ".join(errors))

    curated = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    previous = json.loads(CATALOG_PATH.read_text(encoding="utf-8")) if CATALOG_PATH.exists() else {}
    old_records = previous.get("opportunities", [])
    # Retain previously collected official records when a complete source run
    # no longer returns them. They are downgraded until checked again rather
    # than disappearing silently from the catalog.
    collected_keys = {(item["sourceId"], item["externalId"]) for item in collected}
    for old in old_records:
        key = (old.get("sourceId"), old.get("externalId"))
        if old.get("sourceId") and key not in collected_keys:
            old = {**old, "status": "secondary", "publicationStatus": "unknown",
                   "verificationStatus": "not_seen_in_latest_run",
                   "risk": "No apareció en la última consulta del tablero oficial; volver a comprobar antes de postular."}
            collected.append(old)

    combined = curated + collected
    deduped = {}
    for item in combined:
        key = (item.get("sourceId"), item.get("externalId")) if item.get("sourceId") else ("curated", item.get("id"))
        deduped[key] = item
    opportunities = list(deduped.values())
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": "Catálogo curado y fuentes ATS oficiales revisadas. Verifica siempre condiciones y vigencia en la publicación original.",
        "opportunities": opportunities,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    old_content = CATALOG_PATH.read_text(encoding="utf-8") if CATALOG_PATH.exists() else ""
    # Avoid repeated publication churn when the result is identical apart from
    # generatedAt. A successful source check still updates each posting's checked date.
    old_payload = json.loads(old_content) if old_content else {}
    if old_payload.get("opportunities") == opportunities:
        return False, f"Consulta correcta; sin cambios en {len(opportunities)} oportunidades."
    CATALOG_PATH.write_text(serialized, encoding="utf-8")
    current_count = sum(1 for item in collected if item.get("publicationStatus") == "open")
    return True, f"Catálogo actualizado con {len(opportunities)} oportunidades ({current_count} registros presentes en fuentes ATS)."


def main() -> int:
    try:
        changed, message = refresh()
    except Exception as error:
        print(f"Error de actualización; se conserva el catálogo anterior: {error}", file=sys.stderr)
        return 1
    print(message)
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"publish={'true' if changed else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
