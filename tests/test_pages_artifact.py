from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pages_artifact import PUBLIC_FILES, prepare_artifact, validate_artifact  # noqa: E402


class PagesArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.artifact = self.base / "dist"
        for relative in PUBLIC_FILES:
            destination = self.repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        prepare_artifact(self.repo, self.artifact)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_prepares_exact_valid_artifact_with_canonical_snapshot(self):
        validate_artifact(self.repo, self.artifact)
        actual = {path.relative_to(self.artifact) for path in self.artifact.rglob("*") if path.is_file()}
        self.assertEqual(actual, set(PUBLIC_FILES))
        self.assertEqual((self.artifact / "data/opportunities.json").read_bytes(), (self.repo / "data/opportunities.json").read_bytes())

    def test_missing_required_resource_fails(self):
        (self.artifact / "styles.css").unlink()
        with self.assertRaisesRegex(ValueError, "Falta recurso requerido"):
            validate_artifact(self.repo, self.artifact)

    def test_malformed_catalog_fails(self):
        bad = b"{not-json"
        (self.repo / "data/opportunities.json").write_bytes(bad)
        (self.artifact / "data/opportunities.json").write_bytes(bad)
        with self.assertRaisesRegex(ValueError, "Catálogo ausente o inválido"):
            validate_artifact(self.repo, self.artifact)

    def test_incompatible_schema_fails(self):
        payload = json.loads((self.repo / "data/opportunities.json").read_text(encoding="utf-8"))
        payload["schemaVersion"] = 1
        raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
        (self.repo / "data/opportunities.json").write_bytes(raw)
        (self.artifact / "data/opportunities.json").write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "schemaVersion debe ser 2"):
            validate_artifact(self.repo, self.artifact)

    def test_root_absolute_resource_path_fails_pages_subpath_check(self):
        page = self.artifact / "index.html"
        page.write_text(page.read_text(encoding="utf-8").replace('href="styles.css"', 'href="/styles.css"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "styles.css como recurso local"):
            validate_artifact(self.repo, self.artifact)

    def test_artifact_snapshot_drift_fails(self):
        target = self.artifact / "data/opportunities.json"
        target.write_bytes(target.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "no coincide byte por byte"):
            validate_artifact(self.repo, self.artifact)

    def test_unexpected_extra_file_fails(self):
        (self.artifact / "old-catalog.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Contenido inesperado"):
            validate_artifact(self.repo, self.artifact)


if __name__ == "__main__":
    unittest.main()
