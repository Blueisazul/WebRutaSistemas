"""Fail-closed placeholder until a source and schema-2 review flow are approved.

Connectors are intentionally not run by this command. A future source pilot
must introduce each record into the canonical seed through human review.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .policy import load_source_registry

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "opportunities.json"


def refresh() -> tuple[bool, str]:
    registry = load_source_registry()
    enabled = [source.get("id", "(sin ID)") for source in registry["sources"] if source.get("enabled")]
    if enabled:
        raise RuntimeError(
            "Ingesta automática bloqueada: las fuentes habilitadas requieren migración a schema 2 "
            "y revisión humana antes de modificar el catálogo canónico: " + ", ".join(enabled)
        )
    return False, "No hay fuentes activadas; no se consultó ningún portal ni se modificó el catálogo."


def main() -> int:
    try:
        changed, message = refresh()
    except Exception as error:
        print(f"Actualización detenida sin modificar el catálogo: {error}", file=sys.stderr)
        return 1
    print(message)
    return 0 if not changed else 1


if __name__ == "__main__":
    raise SystemExit(main())
