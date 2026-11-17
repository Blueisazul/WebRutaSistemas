"""Unit, integration, and security tests for the unified editorial CLI (R2-OSS-06)."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scripts.editorial_cli as cli
from collector.dedup import EXACT_DUPLICATE, IDENTIFIER_COLLISION


FIXTURES_ATS_DIR = ROOT / "tests" / "fixtures" / "ats"
FIXTURES_HTML_DIR = ROOT / "tests" / "fixtures" / "html"
INBOX_EXAMPLE_PATH = ROOT / "data" / "candidates" / "inbox.example.json"
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
SOURCES_PATH = ROOT / "collector" / "sources.json"


def _calc_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestEditorialCliHelpAndParsing(unittest.TestCase):
    """Verifies help output and CLI argument parsing."""

    def test_main_help_message(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["--help"])
        self.assertEqual(code, cli.EXIT_OK)
        out = buf.getvalue()
        self.assertIn("editorial_cli.py", out)
        for subcmd in ("validate-inbox", "deduplicate", "inspect", "report", "import", "prepare-review"):
            self.assertIn(subcmd, out)

    def test_no_arguments_prints_help(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main([])
        self.assertEqual(code, cli.EXIT_OK)
        self.assertIn("Comandos disponibles", buf.getvalue())

    def test_subcommand_help_messages(self) -> None:
        for subcmd in ("validate-inbox", "deduplicate", "inspect", "report", "import", "prepare-review"):
            with self.subTest(subcommand=subcmd):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = cli.main([subcmd, "--help"])
                self.assertEqual(code, cli.EXIT_OK)
                self.assertIn(f"editorial_cli.py {subcmd}", buf.getvalue())


class TestValidateInboxCommand(unittest.TestCase):
    """Tests the validate-inbox subcommand."""

    def test_validate_inbox_example(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["validate-inbox", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17"])
        self.assertEqual(code, cli.EXIT_OK)
        self.assertIn("Resultado: VÁLIDO", buf.getvalue())

    def test_validate_inbox_with_evidence_verification(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["validate-inbox", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17", "--verify-evidence"])
        self.assertEqual(code, cli.EXIT_OK)
        out = buf.getvalue()
        self.assertIn("Verificación de Evidencias y Vigencia", out)
        self.assertIn("Resultado: VÁLIDO", out)

    def test_validate_inbox_json_report(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["validate-inbox", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17", "--json-report"])
        self.assertEqual(code, cli.EXIT_OK)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["operation"], "validate-inbox")
        self.assertTrue(data["ok"])
        self.assertEqual(data["asOf"], "2026-11-17")

    def test_validate_inbox_data_error_exit_code(self) -> None:
        invalid_inbox = {
            "schemaVersion": 1,
            "candidates": [
                {"candidateId": "cand-invalid", "sourceId": "non-existent-source"}
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(invalid_inbox, tf)
            tf_path = Path(tf.name)

        try:
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                code = cli.main(["validate-inbox", str(tf_path), "--as-of", "2026-11-17"])
            self.assertEqual(code, cli.EXIT_DATA_ERROR)
            self.assertIn("ERROR:", err_buf.getvalue())
        finally:
            tf_path.unlink(missing_ok=True)

    def test_validate_inbox_nonexistent_file(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main(["validate-inbox", "non_existent_file_xyz.json"])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("El archivo no existe", err_buf.getvalue())

    def test_validate_inbox_malformed_json(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            tf.write("{ this is invalid json ]")
            tf_path = Path(tf.name)

        try:
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                code = cli.main(["validate-inbox", str(tf_path)])
            self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("JSON malformado", err_buf.getvalue())
        finally:
            tf_path.unlink(missing_ok=True)


class TestDeduplicateCommand(unittest.TestCase):
    """Tests the deduplicate subcommand."""

    def test_deduplicate_empty_inbox(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["deduplicate", str(INBOX_EXAMPLE_PATH), "--no-seed"])
        self.assertEqual(code, cli.EXIT_OK)
        out = buf.getvalue()
        self.assertIn("ANÁLISIS DE DEDUPLICACIÓN DETERMINISTA", out)
        self.assertIn("Candidatos evaluados: 0", out)

    def test_deduplicate_collision_detection(self) -> None:
        batch_with_collision = {
            "schemaVersion": 1,
            "candidates": [
                {
                    "candidateId": "cand-col-1",
                    "sourceId": "src-bcp",
                    "sourceUrl": "https://jobs.bcp.com.pe/job1",
                    "proposed": {"title": "Dev Junior", "externalReference": "REF-100"}
                },
                {
                    "candidateId": "cand-col-2",
                    "sourceId": "src-bcp",
                    "sourceUrl": "https://jobs.bcp.com.pe/job2",
                    "proposed": {"title": "Senior Cloud Architect", "externalReference": "REF-100"}
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(batch_with_collision, tf)
            tf_path = Path(tf.name)

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main(["deduplicate", str(tf_path), "--no-seed", "--fail-on-collision"])
            self.assertEqual(code, cli.EXIT_DATA_ERROR)
            out = buf.getvalue()
            self.assertIn("Colisiones de ID (IDENTIFIER_COLLISION): 1", out)
            self.assertIn("[COLISIÓN CRÍTICA]", out)

            # Also check JSON format
            buf_json = io.StringIO()
            with redirect_stdout(buf_json):
                code_json = cli.main(["deduplicate", str(tf_path), "--no-seed", "--fail-on-collision", "--json-report"])
            self.assertEqual(code_json, cli.EXIT_DATA_ERROR)
            data = json.loads(buf_json.getvalue())
            self.assertEqual(data["summaryByType"][IDENTIFIER_COLLISION], 1)
        finally:
            tf_path.unlink(missing_ok=True)


class TestInspectCommand(unittest.TestCase):
    """Tests the inspect subcommand."""

    def test_inspect_basic(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["inspect", str(INBOX_EXAMPLE_PATH)])
        self.assertEqual(code, cli.EXIT_OK)
        out = buf.getvalue()
        self.assertIn("INSPECCIÓN EDITORIAL DE BANDEJA", out)
        self.assertIn("Total de candidatos: 0", out)

    def test_inspect_with_candidates_and_evidence(self) -> None:
        inbox = {
            "schemaVersion": 1,
            "candidates": [
                {
                    "candidateId": "c1",
                    "sourceId": "talento-peru-servir",
                    "sourceUrl": "https://talentoperu.servir.gob.pe/job1",
                    "editorialReview": {"status": "pending_review"},
                    "proposed": {"title": "Dev Junior", "mode": "Remoto", "deadline": "2026-11-30"},
                    "fieldEvidence": [
                        {"field": "title", "url": "https://talentoperu.servir.gob.pe/job1", "observedAt": "2026-11-16T10:00:00-05:00"},
                        {"field": "mode", "url": "https://talentoperu.servir.gob.pe/job1", "observedAt": "2026-11-16T10:00:00-05:00"},
                        {"field": "deadline", "url": "https://talentoperu.servir.gob.pe/job1", "observedAt": "2026-11-16T10:00:00-05:00"}
                    ]
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(inbox, tf)
            tf_path = Path(tf.name)

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main(["inspect", str(tf_path), "--as-of", "2026-11-17", "--verify-evidence"])
            self.assertEqual(code, cli.EXIT_OK)
            out = buf.getvalue()
            self.assertIn("Total de candidatos: 1", out)
            self.assertIn("pending_review: 1", out)
            self.assertIn("talento-peru-servir: 1", out)
            self.assertIn("Remoto: 1", out)
            self.assertIn("ALL_FRESH: 1", out)
            self.assertIn("DEADLINE_FUTURE: 1", out)

            # Test JSON format
            buf_json = io.StringIO()
            with redirect_stdout(buf_json):
                code_json = cli.main(["inspect", str(tf_path), "--as-of", "2026-11-17", "--json-report"])
            self.assertEqual(code_json, cli.EXIT_OK)
            stats = json.loads(buf_json.getvalue())
            self.assertEqual(stats["totalCandidates"], 1)
            self.assertEqual(stats["reviewStatus"]["pending_review"], 1)
            self.assertEqual(stats["sources"]["talento-peru-servir"], 1)
        finally:
            tf_path.unlink(missing_ok=True)


class TestReportCommand(unittest.TestCase):
    """Tests the report subcommand."""

    def test_report_json_output(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["report", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17", "--json-report"])
        self.assertEqual(code, cli.EXIT_OK)
        report = json.loads(buf.getvalue())
        self.assertEqual(report["operation"], "report")
        self.assertEqual(report["totalEvaluated"], 0)
        self.assertTrue(report["validationSummary"]["passed"])

    def test_report_save_to_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "consolidated_report.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main([
                    "report", str(INBOX_EXAMPLE_PATH),
                    "--as-of", "2026-11-17",
                    "--output", str(out_file),
                ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(out_file.exists())
            report = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(report["operation"], "report")
            self.assertEqual(report["asOf"], "2026-11-17")

    def test_report_rejects_output_same_as_input(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main(["report", str(INBOX_EXAMPLE_PATH), "--output", str(INBOX_EXAMPLE_PATH)])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("no puede ser el mismo archivo de entrada", err_buf.getvalue())


class TestImportCommand(unittest.TestCase):
    """Tests the import subcommand with various fixture formats."""

    def test_import_greenhouse_fixture(self) -> None:
        gh_fixture = FIXTURES_ATS_DIR / "greenhouse_complete.json"
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "imported_gh.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main([
                    "import",
                    "--format", "greenhouse",
                    "--source-id", "greenhouse-public-job-board-template",
                    "--board-token", "empresa-ficticia",
                    "--employer", "Empresa Ficticia Tech",
                    "--input", str(gh_fixture),
                    "--output", str(out_file),
                ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(out_file.exists())
            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data["schemaVersion"], 1)
            self.assertEqual(len(data["candidates"]), 2)
            self.assertEqual(data["candidates"][0]["sourceId"], "greenhouse-public-job-board-template")
            self.assertEqual(data["candidates"][0]["captureMethod"], "manual")

    def test_import_lever_fixture(self) -> None:
        lever_fixture = FIXTURES_ATS_DIR / "lever_complete.json"
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "imported_lever.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main([
                    "import",
                    "--format", "lever",
                    "--source-id", "lever-public-postings-template",
                    "--site", "empresa-lever-test",
                    "--employer", "Empresa Lever SAC",
                    "--input", str(lever_fixture),
                    "--output", str(out_file),
                ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(out_file.exists())
            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data["schemaVersion"], 1)
            self.assertGreater(len(data["candidates"]), 0)

    def test_import_html_fixture(self) -> None:
        html_fixture = FIXTURES_HTML_DIR / "jobposting_complete.html"
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "imported_html.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main([
                    "import",
                    "--format", "html",
                    "--source-id", "talento-peru-servir",
                    "--source-url", "https://talentoperu.servir.gob.pe/job1",
                    "--input", str(html_fixture),
                    "--output", str(out_file),
                ])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertTrue(out_file.exists())
            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data["schemaVersion"], 1)
            self.assertEqual(len(data["candidates"]), 1)
            self.assertIn("Practicante", data["candidates"][0]["proposed"]["title"])

    def test_import_protects_against_overwrite_without_force(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            tf.write("{}")
            tf_path = Path(tf.name)

        try:
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                code = cli.main([
                    "import",
                    "--format", "greenhouse",
                    "--source-id", "greenhouse-public-job-board-template",
                    "--board-token", "empresa-ficticia",
                    "--employer", "Empresa",
                    "--input", str(FIXTURES_ATS_DIR / "greenhouse_complete.json"),
                    "--output", str(tf_path),
                ])
            self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("ya existe", err_buf.getvalue())
        finally:
            tf_path.unlink(missing_ok=True)

    def test_import_rejects_unknown_source(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main([
                "import",
                "--format", "greenhouse",
                "--source-id", "unknown-source-id-12345",
                "--input", str(FIXTURES_ATS_DIR / "greenhouse_complete.json"),
                "--output", "some_out.json",
            ])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("no existe en collector/sources.json", err_buf.getvalue())

    def test_import_html_missing_source_url(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main([
                "import",
                "--format", "html",
                "--source-id", "talento-peru-servir",
                "--input", str(FIXTURES_HTML_DIR / "jobposting_complete.html"),
                "--output", "out_html.json",
            ])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("--source-url es obligatorio", err_buf.getvalue())


class TestPrepareReviewCommand(unittest.TestCase):
    """Tests the prepare-review subcommand."""

    def test_prepare_review_export(self) -> None:
        sample_inbox = {
            "schemaVersion": 1,
            "candidates": [
                {
                    "candidateId": "cand-p1",
                    "sourceId": "talento-peru-servir",
                    "editorialReview": {"status": "pending_review"},
                    "proposed": {"title": "Dev Pending"}
                },
                {
                    "candidateId": "cand-a1",
                    "sourceId": "talento-peru-servir",
                    "editorialReview": {"status": "approved_for_catalog"},
                    "proposed": {"title": "Dev Approved"}
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(sample_inbox, tf)
            inbox_path = Path(tf.name)

        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "review_export.json"
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = cli.main([
                        "prepare-review",
                        "--inbox", str(inbox_path),
                        "--output", str(out_file),
                        "--status", "approved_for_catalog",
                    ])
                self.assertEqual(code, cli.EXIT_OK)
                self.assertTrue(out_file.exists())
                exported = json.loads(out_file.read_text(encoding="utf-8"))
                self.assertEqual(exported["totalExported"], 1)
                self.assertEqual(exported["candidates"][0]["candidateId"], "cand-a1")
                self.assertIn("exportNotice", exported)
            finally:
                inbox_path.unlink(missing_ok=True)

    def test_prepare_review_rejects_output_same_as_inbox(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump({"schemaVersion": 1, "candidates": []}, tf)
            inbox_path = Path(tf.name)

        try:
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                code = cli.main([
                    "prepare-review",
                    "--inbox", str(inbox_path),
                    "--output", str(inbox_path),
                    "--force-write",
                ])
            self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
            self.assertIn("no puede ser el mismo archivo de inbox", err_buf.getvalue())
        finally:
            inbox_path.unlink(missing_ok=True)


class TestSecurityAndInviolability(unittest.TestCase):
    """Rigorous tests proving zero canonical file writes and safety boundary enforcement."""

    def test_forbids_writing_to_seed_catalog(self) -> None:
        for subcmd in ("import", "prepare-review"):
            with self.subTest(command=subcmd):
                err_buf = io.StringIO()
                with redirect_stderr(err_buf):
                    if subcmd == "import":
                        code = cli.main([
                            "import",
                            "--format", "greenhouse",
                            "--source-id", "greenhouse-public-job-board-template",
                            "--board-token", "test",
                            "--employer", "test",
                            "--input", str(FIXTURES_ATS_DIR / "greenhouse_complete.json"),
                            "--output", str(SEED_PATH),
                            "--force-write",
                        ])
                    else:
                        code = cli.main([
                            "prepare-review",
                            "--inbox", str(INBOX_EXAMPLE_PATH),
                            "--output", str(SEED_PATH),
                            "--force-write",
                        ])
                self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
                self.assertIn("estrictamente prohibido", err_buf.getvalue())

    def test_forbids_writing_to_snapshot_catalog(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main([
                "prepare-review",
                "--inbox", str(INBOX_EXAMPLE_PATH),
                "--output", str(SNAPSHOT_PATH),
                "--force-write",
            ])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("estrictamente prohibido", err_buf.getvalue())

    def test_canonical_hashes_remain_intact_after_cli_runs(self) -> None:
        seed_hash_before = _calc_sha256(SEED_PATH)
        snap_hash_before = _calc_sha256(SNAPSHOT_PATH)
        sources_hash_before = _calc_sha256(SOURCES_PATH)

        # Run several operations
        cli.main(["validate-inbox", str(INBOX_EXAMPLE_PATH), "--verify-evidence"])
        cli.main(["inspect", str(INBOX_EXAMPLE_PATH), "--verify-evidence"])
        cli.main(["deduplicate", str(INBOX_EXAMPLE_PATH)])
        cli.main(["report", str(INBOX_EXAMPLE_PATH), "--json-report"])

        self.assertEqual(_calc_sha256(SEED_PATH), seed_hash_before)
        self.assertEqual(_calc_sha256(SNAPSHOT_PATH), snap_hash_before)
        self.assertEqual(_calc_sha256(SOURCES_PATH), sources_hash_before)

    def test_paths_with_spaces_handled_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spaced_dir = Path(td) / "dir with spaces"
            spaced_dir.mkdir()
            spaced_inbox = spaced_dir / "inbox with spaces.json"
            spaced_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main(["validate-inbox", str(spaced_inbox)])
            self.assertEqual(code, cli.EXIT_OK)
            self.assertIn("VÁLIDO", buf.getvalue())

    def test_invalid_as_of_format_produces_operational_error(self) -> None:
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            code = cli.main(["validate-inbox", str(INBOX_EXAMPLE_PATH), "--as-of", "invalid-date"])
        self.assertEqual(code, cli.EXIT_OPERATIONAL_ERROR)
        self.assertIn("--as-of debe usar formato civil YYYY-MM-DD", err_buf.getvalue())

    def test_determinism_across_multiple_runs(self) -> None:
        buf1 = io.StringIO()
        with redirect_stdout(buf1):
            cli.main(["report", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17", "--json-report"])
        data1 = json.loads(buf1.getvalue())

        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            cli.main(["report", str(INBOX_EXAMPLE_PATH), "--as-of", "2026-11-17", "--json-report"])
        data2 = json.loads(buf2.getvalue())

        # Excluding generatedAt timestamp, report contents must be strictly equal
        data1.pop("generatedAt", None)
        data2.pop("generatedAt", None)
        self.assertEqual(data1, data2)


if __name__ == "__main__":
    unittest.main()
