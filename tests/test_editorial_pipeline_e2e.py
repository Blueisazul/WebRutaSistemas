"""Comprehensive End-to-End (E2E) integration, hardening, and offline verification of the OSS Editorial Pipeline (R2-OSS-07)."""

from __future__ import annotations

import hashlib
import io
import json
import os
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scripts.editorial_cli as cli
from collector.dedup import EXACT_DUPLICATE, IDENTIFIER_COLLISION, POSSIBLE_DUPLICATE


FIXTURES_ATS_DIR = ROOT / "tests" / "fixtures" / "ats"
FIXTURES_HTML_DIR = ROOT / "tests" / "fixtures" / "html"
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
SOURCES_PATH = ROOT / "collector" / "sources.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestEditorialPipelineE2E(unittest.TestCase):
    """Verifies the complete editorial pipeline in an isolated sandbox environment."""

    def setUp(self) -> None:
        self.seed_hash_before = _sha256(SEED_PATH)
        self.snap_hash_before = _sha256(SNAPSHOT_PATH)
        self.sources_hash_before = _sha256(SOURCES_PATH)

    def tearDown(self) -> None:
        # Guarantee no canonical files were touched
        self.assertEqual(_sha256(SEED_PATH), self.seed_hash_before, "La semilla canónica fue modificada")
        self.assertEqual(_sha256(SNAPSHOT_PATH), self.snap_hash_before, "El snapshot canónico fue modificado")
        self.assertEqual(_sha256(SOURCES_PATH), self.sources_hash_before, "El registro de fuentes fue modificado")

    def test_full_pipeline_e2e_isolated_sandbox(self) -> None:
        """Executes full lifecycle:
        1. Import ATS Greenhouse -> Schema 2
        2. Import ATS Lever -> Schema 2
        3. Import HTML/JSON-LD -> Schema 2
        4. Staging merge into isolated local inbox
        5. Validate Schema 2 + Evidence verification
        6. Deduplicate against batch and seed catalog
        7. Inspect metrics and review status
        8. Generate consolidated report
        9. Prepare and export candidates for human review
        10. Assert complete isolation, determinism, and zero network calls.
        """
        # Block network sockets at runtime to guarantee zero remote calls
        with patch("socket.socket", side_effect=RuntimeError("Red prohibida en pipeline offline")), \
             tempfile.TemporaryDirectory() as td:

            work_dir = Path(td)
            gh_out = work_dir / "gh_staging.json"
            lever_out = work_dir / "lever_staging.json"
            html_out = work_dir / "html_staging.json"
            merged_inbox = work_dir / "merged_inbox.json"
            consolidated_report = work_dir / "audit_report.json"
            review_export = work_dir / "review_export.json"

            # -------------------------------------------------------------
            # Stage 1: Import Greenhouse ATS fixture
            # -------------------------------------------------------------
            code = cli.main([
                "import",
                "--format", "greenhouse",
                "--source-id", "greenhouse-public-job-board-template",
                "--board-token", "empresa-ficticia",
                "--employer", "Empresa Ficticia Tech",
                "--input", str(FIXTURES_ATS_DIR / "greenhouse_complete.json"),
                "--output", str(gh_out),
            ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(gh_out.exists())
            gh_data = json.loads(gh_out.read_text(encoding="utf-8"))
            self.assertEqual(len(gh_data["candidates"]), 2)

            # -------------------------------------------------------------
            # Stage 2: Import Lever ATS fixture
            # -------------------------------------------------------------
            code = cli.main([
                "import",
                "--format", "lever",
                "--source-id", "lever-public-postings-template",
                "--site", "empresa-lever-test",
                "--employer", "Empresa Lever SAC",
                "--input", str(FIXTURES_ATS_DIR / "lever_complete.json"),
                "--output", str(lever_out),
            ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(lever_out.exists())
            lever_data = json.loads(lever_out.read_text(encoding="utf-8"))
            self.assertGreater(len(lever_data["candidates"]), 0)

            # -------------------------------------------------------------
            # Stage 3: Import HTML / JSON-LD JobPosting fixture
            # -------------------------------------------------------------
            code = cli.main([
                "import",
                "--format", "html",
                "--source-id", "talento-peru-servir",
                "--source-url", "https://talentoperu.servir.gob.pe/job-conv-2026",
                "--input", str(FIXTURES_HTML_DIR / "jobposting_complete.html"),
                "--output", str(html_out),
            ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(html_out.exists())
            html_data = json.loads(html_out.read_text(encoding="utf-8"))
            self.assertEqual(len(html_data["candidates"]), 1)

            # -------------------------------------------------------------
            # Stage 4: Merge normalized candidates into an isolated staging inbox
            # -------------------------------------------------------------
            all_candidates = (
                gh_data["candidates"]
                + lever_data["candidates"]
                + html_data["candidates"]
            )
            merged_payload = {
                "schemaVersion": 1,
                "candidates": all_candidates,
            }
            merged_inbox.write_text(json.dumps(merged_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(merged_inbox.exists())

            # -------------------------------------------------------------
            # Stage 5: Validate inbox with Schema 2 and evidence freshness
            # -------------------------------------------------------------
            val_buf = io.StringIO()
            with redirect_stdout(val_buf):
                val_code = cli.main([
                    "validate-inbox",
                    str(merged_inbox),
                    "--as-of", "2026-11-17",
                    "--verify-evidence",
                ])
            # Valid Schema 2 candidates (with expected editorial warnings)
            self.assertEqual(val_code, cli.EXIT_OK)
            self.assertIn("Resultado: VÁLIDO", val_buf.getvalue())
            self.assertIn("Verificación de Evidencias y Vigencia", val_buf.getvalue())

            # -------------------------------------------------------------
            # Stage 6: Deduplicate against batch and seed catalog
            # -------------------------------------------------------------
            dedup_buf = io.StringIO()
            with redirect_stdout(dedup_buf):
                dedup_code = cli.main([
                    "deduplicate",
                    str(merged_inbox),
                    "--seed", str(SEED_PATH),
                    "--fail-on-collision",
                ])
            # The fixtures contain distinct opportunities with no collisions
            self.assertEqual(dedup_code, cli.EXIT_OK)
            self.assertIn("Candidatos evaluados:", dedup_buf.getvalue())

            # -------------------------------------------------------------
            # Stage 7: Inspect metrics and review distributions
            # -------------------------------------------------------------
            insp_buf = io.StringIO()
            with redirect_stdout(insp_buf):
                insp_code = cli.main([
                    "inspect",
                    str(merged_inbox),
                    "--as-of", "2026-11-17",
                    "--verify-evidence",
                ])
            self.assertEqual(insp_code, cli.EXIT_OK)
            insp_out = insp_buf.getvalue()
            self.assertIn("Total de candidatos:", insp_out)
            self.assertIn("Estado de Revisión Editorial:", insp_out)
            self.assertIn("Frescura de Evidencias (TTL 7 días Lima):", insp_out)

            # -------------------------------------------------------------
            # Stage 8: Generate consolidated report
            # -------------------------------------------------------------
            rep_buf = io.StringIO()
            with redirect_stdout(rep_buf):
                rep_code = cli.main([
                    "report",
                    str(merged_inbox),
                    "--seed", str(SEED_PATH),
                    "--as-of", "2026-11-17",
                    "--output", str(consolidated_report),
                ])
            self.assertEqual(rep_code, cli.EXIT_OK)
            self.assertTrue(consolidated_report.exists())
            report_content = json.loads(consolidated_report.read_text(encoding="utf-8"))
            self.assertEqual(report_content["operation"], "report")
            self.assertEqual(report_content["asOf"], "2026-11-17")
            self.assertTrue(report_content["validationSummary"]["passed"])
            self.assertIn("itemsRequiringHumanReview", report_content)

            # -------------------------------------------------------------
            # Stage 9: Prepare and export candidates for human review
            # -------------------------------------------------------------
            prep_buf = io.StringIO()
            with redirect_stdout(prep_buf):
                prep_code = cli.main([
                    "prepare-review",
                    "--inbox", str(merged_inbox),
                    "--output", str(review_export),
                    "--status", "pending_review",
                ])
            self.assertEqual(prep_code, cli.EXIT_OK)
            self.assertTrue(review_export.exists())
            exported_data = json.loads(review_export.read_text(encoding="utf-8"))
            self.assertIn("exportNotice", exported_data)
            self.assertEqual(exported_data["filterStatus"], "pending_review")
            self.assertEqual(len(exported_data["candidates"]), len(all_candidates))

            # -------------------------------------------------------------
            # Stage 10: Repeatability and Determinism Verification
            # -------------------------------------------------------------
            rep_buf_2 = io.StringIO()
            with redirect_stdout(rep_buf_2):
                cli.main([
                    "report",
                    str(merged_inbox),
                    "--seed", str(SEED_PATH),
                    "--as-of", "2026-11-17",
                    "--json-report",
                ])
            report_run_1 = json.loads(rep_buf_2.getvalue())

            rep_buf_3 = io.StringIO()
            with redirect_stdout(rep_buf_3):
                cli.main([
                    "report",
                    str(merged_inbox),
                    "--seed", str(SEED_PATH),
                    "--as-of", "2026-11-17",
                    "--json-report",
                ])
            report_run_2 = json.loads(rep_buf_3.getvalue())

            # Excluding timestamp, reports must be 100% deterministic
            report_run_1.pop("generatedAt", None)
            report_run_2.pop("generatedAt", None)
            self.assertEqual(report_run_1, report_run_2, "Los reportes no fueron deterministas entre ejecuciones")

    def test_security_rejection_of_path_traversal_to_canonical(self) -> None:
        """Verifies that path traversal tricks cannot bypass canonical file protection."""
        traversal_attempts = [
            ROOT / "data" / "candidates" / ".." / "opportunities.seed.json",
            ROOT / "data" / "candidates" / ".." / "opportunities.json",
            ROOT / "collector" / ".." / "data" / "opportunities.seed.json",
            ROOT / "collector" / "sources.json",
            ROOT / ".git" / "hooks" / "malicious.json",
        ]
        for bad_target in traversal_attempts:
            with self.subTest(target=str(bad_target)):
                err_buf = io.StringIO()
                with redirect_stderr(err_buf):
                    code = cli.main([
                        "prepare-review",
                        "--inbox", str(ROOT / "data" / "candidates" / "inbox.example.json"),
                        "--output", str(bad_target),
                        "--force-write",
                    ])
                self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
                self.assertIn("estrictamente prohibido", err_buf.getvalue())

    def test_security_rejection_of_input_output_collisions(self) -> None:
        """Verifies that commands reject writing to the exact same input file."""
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            json.dump({"schemaVersion": 1, "candidates": []}, tf)
            tf_path = Path(tf.name)

        try:
            # 1. import with input == output
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                code = cli.main([
                    "import",
                    "--format", "html",
                    "--source-id", "talento-peru-servir",
                    "--source-url", "https://talentoperu.servir.gob.pe/job",
                    "--input", str(tf_path),
                    "--output", str(tf_path),
                    "--force-write",
                ])
            self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("no puede ser el mismo archivo de entrada", err_buf.getvalue())

            # 2. report with path == output
            err_buf2 = io.StringIO()
            with redirect_stderr(err_buf2):
                code2 = cli.main([
                    "report",
                    str(tf_path),
                    "--output", str(tf_path),
                ])
            self.assertEqual(code2, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("no puede ser el mismo archivo de entrada", err_buf2.getvalue())

            # 3. prepare-review with inbox == output
            err_buf3 = io.StringIO()
            with redirect_stderr(err_buf3):
                code3 = cli.main([
                    "prepare-review",
                    "--inbox", str(tf_path),
                    "--output", str(tf_path),
                    "--force-write",
                ])
            self.assertEqual(code3, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("no puede ser el mismo archivo de inbox", err_buf3.getvalue())
        finally:
            tf_path.unlink(missing_ok=True)

    def test_atomic_write_leaves_no_partial_files_on_error(self) -> None:
        """Verifies that atomic write mechanics clean up temp files on failures."""
        with tempfile.TemporaryDirectory() as td:
            target_dir = Path(td) / "protected_target"
            target_dir.mkdir()

            # Attempting to write to an existing directory must raise IsADirectoryError and leave no .tmp files
            with self.assertRaises(IsADirectoryError):
                cli._atomic_write_json(target_dir, {"data": 123})

            temp_files = list(Path(td).glob(".tmp_*"))
            self.assertEqual(len(temp_files), 0, "Archivos temporales no fueron limpiados tras error")


if __name__ == "__main__":
    unittest.main()
