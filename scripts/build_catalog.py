"""Rebuild the catalog without discarding previously collected ATS records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
OUTPUT_PATH = ROOT / "data" / "opportunities.json"


def main() -> None:
    records = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("La muestra de oportunidades debe ser una lista JSON.")
    previous = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")) if OUTPUT_PATH.exists() else {}
    prior_ats = [record for record in previous.get("opportunities", []) if record.get("sourceId")]
    by_id = {record.get("id"): record for record in records}
    by_id.update({record.get("id"): record for record in prior_ats})
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": "Muestra curada y registros ATS previamente recolectados; la ejecución manual no consulta fuentes en vivo.",
        "opportunities": list(by_id.values()),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
