"""Build the public static catalog from the curated seed data."""

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
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceNote": "Muestra curada de demostración; no representa un inventario actualizado en tiempo real.",
        "opportunities": records,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
