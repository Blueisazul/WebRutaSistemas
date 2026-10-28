"""Prepare and validate the exact, dependency-free GitHub Pages artifact."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from catalog_quality import LIMA_TZ, load_json, validate_payload


# The sole selection list for public files. The same staged directory is
# validated and then passed unchanged to upload-pages-artifact.
PUBLIC_FILES = (
    Path("index.html"),
    Path("app.js"),
    Path("styles.css"),
    Path("data/opportunities.json"),
)
PAGES_BASE = "https://blueisazul.github.io/WebRutaSistemas/"
FRONTEND_SCHEMA = "payload.schemaVersion !== 2"
CATALOG_FETCH = "fetch('./data/opportunities.json'"


class _ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if tag == "link" and "stylesheet" in (attrs_map.get("rel") or "").split():
            if attrs_map.get("href"):
                self.stylesheets.append(attrs_map["href"] or "")
        if tag == "script" and attrs_map.get("src"):
            self.scripts.append(attrs_map["src"] or "")


def _read_artifact_files(root: Path) -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}
    for relative in PUBLIC_FILES:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"Falta recurso requerido en el artefacto: {relative.as_posix()}")
        files[relative] = path.read_bytes()
    actual = {path.relative_to(root) for path in root.rglob("*") if path.is_file()}
    expected = set(PUBLIC_FILES)
    if actual != expected:
        extra = sorted(p.as_posix() for p in actual - expected)
        missing = sorted(p.as_posix() for p in expected - actual)
        raise ValueError(f"Contenido inesperado del artefacto; faltan={missing}, sobran={extra}")
    return files


def validate_artifact(repo_root: Path, artifact_dir: Path) -> None:
    files = _read_artifact_files(artifact_dir)
    html = files[Path("index.html")].decode("utf-8")
    app = files[Path("app.js")].decode("utf-8")
    parser = _ResourceParser()
    parser.feed(html)
    if parser.stylesheets != ["styles.css"]:
        raise ValueError("index.html debe referenciar exactamente styles.css como recurso local")
    if parser.scripts != ["app.js"]:
        raise ValueError("index.html debe referenciar exactamente app.js como recurso local")
    for resource in (*parser.stylesheets, *parser.scripts):
        resolved = urlsplit(urljoin(PAGES_BASE, resource))
        if resolved.path != f"/WebRutaSistemas/{resource}":
            raise ValueError(f"Recurso incompatible con el subpath de Pages: {resource}")
    if CATALOG_FETCH not in app or FRONTEND_SCHEMA not in app:
        raise ValueError("El frontend no declara el contrato schema 2 y la carga relativa del catálogo")
    catalog_url = urlsplit(urljoin(PAGES_BASE, "./data/opportunities.json"))
    if catalog_url.path != "/WebRutaSistemas/data/opportunities.json":
        raise ValueError("La ruta del catálogo no resuelve bajo /WebRutaSistemas/")
    if "/api/opportunities" in app:
        raise ValueError("El artefacto no puede depender del endpoint local /api/opportunities")
    css = files[Path("styles.css")].decode("utf-8")
    if re.search(r"@import\s+(?:url\()?['\"]?https?://|url\(\s*['\"]?https?://", css, re.IGNORECASE):
        raise ValueError("La hoja de estilos no puede depender de recursos remotos en tiempo de ejecución")
    snapshot_path = Path("data/opportunities.json")
    source_snapshot = (repo_root / snapshot_path).read_bytes()
    if files[snapshot_path] != source_snapshot:
        raise ValueError("El JSON del artefacto no coincide byte por byte con el snapshot validado")
    try:
        payload = json.loads(files[snapshot_path].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Catálogo ausente o inválido en el artefacto: {error}") from error
    today = datetime.now(LIMA_TZ).date()
    result = validate_payload(payload, today=today)
    if not result.ok:
        raise ValueError("Catálogo del artefacto incompatible: " + "; ".join(result.errors))


def prepare_artifact(repo_root: Path, artifact_dir: Path) -> None:
    if artifact_dir.exists() and any(artifact_dir.iterdir()):
        raise ValueError(f"El directorio de salida no está vacío: {artifact_dir}")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for relative in PUBLIC_FILES:
        source = repo_root / relative
        if not source.is_file():
            raise ValueError(f"Falta archivo fuente requerido: {relative.as_posix()}")
        destination = artifact_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    validate_artifact(repo_root, artifact_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"), help="directorio de staging vacío")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        prepare_artifact(root, output)
    except (OSError, ValueError) as error:
        print(f"Artefacto Pages inválido: {error}", file=sys.stderr)
        return 1
    print(f"Artefacto Pages preparado y validado: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
