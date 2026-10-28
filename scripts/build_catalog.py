"""Build the public snapshot from the sole editable, versioned seed catalog."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from catalog_quality import DEFAULT_TTL_DAYS, load_json, validate_payload


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
OUTPUT_PATH = ROOT / "data" / "opportunities.json"


def build_payload(seed: object, previous: object, generated_at: str, *, today: date) -> dict:
    if not isinstance(seed, dict) or not isinstance(seed.get("opportunities"), list):
        raise ValueError("La fuente canónica debe contener schemaVersion y opportunities")
    previous_ids = {
        item.get("id") for item in previous.get("opportunities", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } if isinstance(previous, dict) else set()
    ttl_days = seed.get("verificationTtlDays", DEFAULT_TTL_DAYS)
    candidate = {**seed, "generatedAt": generated_at}
    result = validate_payload(candidate, today=today, previous_ids=previous_ids)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    return {
        "schemaVersion": 2,
        "generatedAt": generated_at,
        "verificationTtlDays": ttl_days,
        "timezone": seed.get("timezone", "America/Lima"),
        "sourceNote": seed.get("sourceNote", "Catálogo curado versionado; la generación no comprueba vigencia."),
        "opportunities": seed["opportunities"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="valida fuente y snapshot sin escribir (predeterminado)")
    mode.add_argument("--write", action="store_true", help="genera explícitamente el snapshot")
    parser.add_argument("--generated-at", help="timestamp ISO 8601 para una generación reproducible")
    args = parser.parse_args(argv)
    try:
        seed = load_json(SEED_PATH)
        previous = load_json(OUTPUT_PATH) if OUTPUT_PATH.exists() else {}
        now = args.generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        # Peru uses UTC-05:00 without seasonal clock changes. A fixed offset
        # keeps this standard-library-only script portable on Windows too.
        lima_tz = timezone(timedelta(hours=-5), "America/Lima")
        today = datetime.now(lima_tz).date()
        payload = build_payload(seed, previous, now, today=today)
        if not args.write:
            comparable = dict(previous) if isinstance(previous, dict) else {}
            comparable.pop("generatedAt", None)
            expected = dict(payload)
            expected.pop("generatedAt", None)
            if comparable != expected:
                raise ValueError("el snapshot difiere de su fuente canónica; revisar y regenerar explícitamente con --write")
            print(f"Catálogo válido: {len(payload['opportunities'])} registros; snapshot coincide con la fuente canónica.")
            return 0
        OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Catálogo generado explícitamente: {len(payload['opportunities'])} registros desde {SEED_PATH.relative_to(ROOT)}.")
        return 0
    except (ValueError, OSError, TypeError) as error:
        print(f"Error de catálogo: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
