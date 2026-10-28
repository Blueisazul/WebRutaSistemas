"""Validate canonical source and generated publication snapshot without network access."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from catalog_quality import load_json, validate_payload
from build_catalog import OUTPUT_PATH, SEED_PATH


def lima_today() -> date:
    return datetime.now(timezone(timedelta(hours=-5), "America/Lima")).date()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-empty", action="store_true", help="acepta catálogo vacío solo para una prueba explícita")
    parser.add_argument("--as-of", help="fecha civil Lima YYYY-MM-DD para validación reproducible")
    args = parser.parse_args(argv)
    try:
        today = date.fromisoformat(args.as_of) if args.as_of else lima_today()
        seed = load_json(SEED_PATH)
        snapshot = load_json(OUTPUT_PATH)
        if not isinstance(seed, dict) or not isinstance(snapshot, dict):
            raise ValueError("fuente y snapshot deben ser objetos JSON")
        seed_check = {**seed, "generatedAt": snapshot.get("generatedAt")}
        if seed_check != snapshot:
            print("ERROR: snapshot distinto de la fuente canónica (excepto generatedAt)", file=sys.stderr)
            return 1
        previous_ids = {
            item["id"] for item in snapshot.get("opportunities", []) if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        results = [
            ("fuente canónica", validate_payload(seed_check, today=today, allow_empty=args.allow_empty)),
            ("snapshot publicado", validate_payload(snapshot, today=today, allow_empty=args.allow_empty)),
        ]
        for label, result in results:
            for warning in result.warnings:
                print(f"ADVERTENCIA [{label}]: {warning}")
            for error in result.errors:
                print(f"ERROR [{label}]: {error}", file=sys.stderr)
        seed_rows = seed.get("opportunities", [])
        snapshot_rows = snapshot.get("opportunities", [])
        if {row.get("id") for row in seed_rows if isinstance(row, dict)} != {row.get("id") for row in snapshot_rows if isinstance(row, dict)}:
            print("ERROR: IDs de fuente y snapshot no coinciden", file=sys.stderr)
            return 1
        if any(not result.ok for _, result in results):
            return 1
        print(f"Válido: {len(snapshot_rows)} fichas; modo={'vacío permitido explícitamente' if args.allow_empty else 'publicación no vacía'}; fecha Lima={today.isoformat()}.")
        return 0
    except (ValueError, TypeError, OSError) as error:
        print(f"Error de validación: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
