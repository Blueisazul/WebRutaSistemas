"""Comprehensive unit, integration, and operational tests for R4-01 Controlled Multisource Pilot.

Tests:
- R4-01A: Governance and source registry reconciliation.
- R4-01B: Greenhouse and Lever ATS adapter integration.
- R4-01C: Reproducible capture orchestration, normalization, filtering, and deduplication.
- R4-01D: Controlled CLI execution, single-source mode, fault tolerance, and idempotency.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scripts.editorial_cli as cli
from collector.acquisition_runner import (
    AcquisitionReport,
    filter_candidate_for_target_profile,
    run_pilot_acquisition,
)
from collector.policy import find_source, load_source_registry

FIXTURES_ATS_DIR = ROOT / "tests" / "fixtures" / "ats"
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
TODAY = date(2026, 11, 22)


def _calc_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestAcquisitionPilotR4(unittest.TestCase):
    def setUp(self) -> None:
        self.seed_hash_before = _calc_sha256(SEED_PATH)
        self.snap_hash_before = _calc_sha256(SNAPSHOT_PATH)
        self.registry = load_source_registry()

    def tearDown(self) -> None:
        # Guarantee no canonical catalog modifications occurred
        self.assertEqual(_calc_sha256(SEED_PATH), self.seed_hash_before, "La semilla canónica fue modificada")
        self.assertEqual(_calc_sha256(SNAPSHOT_PATH), self.snap_hash_before, "El snapshot canónico fue modificado")

    # =========================================================================
    # R4-01A: Governance and Registry Reconciliation
    # =========================================================================

    def test_registry_contains_approved_pilot_sources(self) -> None:
        pilot_ids = [
            "greenhouse-canonical",
            "greenhouse-sezzle",
            "greenhouse-cookunity",
            "lever-fintual",
            "lever-kavak",
        ]
        for sid in pilot_ids:
            source = find_source(self.registry, sid)
            self.assertIsNotNone(source, f"Fuente piloto '{sid}' no encontrada en registry")
            self.assertTrue(source.get("enabled"), f"Fuente '{sid}' debe estar habilitada para el piloto")
            self.assertEqual(source.get("decision"), "approved")
            self.assertEqual(source.get("automatedAccessStatus"), "approved")
            self.assertIn(source.get("connector"), ("greenhouse-job-board", "lever-postings"))

    def test_legacy_and_unapproved_sources_remain_disabled(self) -> None:
        legacy_disabled_ids = [
            "talento-peru-servir",
            "unmsm-fisi-employment-board",
            "ositran-manual-review",
            "canonical-careers",
        ]
        for sid in legacy_disabled_ids:
            source = find_source(self.registry, sid)
            self.assertIsNotNone(source)
            self.assertFalse(source.get("enabled"), f"Fuente '{sid}' debe permanecer deshabilitada")
            self.assertNotEqual(source.get("decision"), "approved")

    # =========================================================================
    # R4-01B: ATS Connector Integration & Filtering
    # =========================================================================

    def test_candidate_filtering_respects_geographic_filters(self) -> None:
        source = find_source(self.registry, "greenhouse-canonical")
        self.assertIsNotNone(source)

        # 1. Americas remote -> should pass
        candidate_americas = {
            "proposed": {
                "title": "Software Engineer",
                "location": "Home Based - Americas",
                "mode": "Remoto",
            }
        }
        eligible, reason, _ = filter_candidate_for_target_profile(candidate_americas, source)
        self.assertTrue(eligible)
        self.assertIsNone(reason)

        # 2. London onsite -> should be discarded by geographic filter
        candidate_london = {
            "proposed": {
                "title": "Office Facilities Coordinator",
                "location": "London, United Kingdom",
                "mode": "Presencial",
            }
        }
        eligible, reason, _ = filter_candidate_for_target_profile(candidate_london, source)
        self.assertFalse(eligible)
        self.assertTrue("sede extranjera" in reason or "Ubicación no compatible" in reason)

    # =========================================================================
    # R4-01C: Capture Orchestration & Deduplication (Offline / Deterministic)
    # =========================================================================

    def test_orchestration_with_fixtures_captures_normalizes_and_stages(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            # Start with empty staging inbox
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            report = run_pilot_acquisition(
                source_ids=["greenhouse-canonical", "lever-fintual"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )

            self.assertTrue(report.validation_passed)
            self.assertEqual(report.sources_evaluated, 2)
            self.assertEqual(report.sources_succeeded, 2)
            self.assertEqual(report.sources_failed, 0)
            self.assertGreater(report.total_captured, 0)
            self.assertGreater(report.total_new_staged, 0)

            # Check that staging inbox was written with valid Schema 2 candidates
            staged_data = json.loads(temp_inbox.read_text(encoding="utf-8"))
            self.assertEqual(len(staged_data["candidates"]), report.total_new_staged)
            for c in staged_data["candidates"]:
                self.assertTrue(c["candidateId"].startswith("CAND-"))
                self.assertEqual(c["editorialReview"]["status"], "pending_review")
                self.assertIsNotNone(c["proposed"]["title"])
                self.assertIsNotNone(c["proposed"]["applyUrl"])
                self.assertTrue(len(c["fieldEvidence"]) > 0)

    def test_orchestration_idempotency_second_run_produces_zero_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            # First run: acquires new candidates
            report1 = run_pilot_acquisition(
                source_ids=["greenhouse-canonical", "lever-fintual"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )
            initial_staged = report1.total_new_staged
            self.assertGreater(initial_staged, 0)

            # Second run: identical sources and fixtures
            report2 = run_pilot_acquisition(
                source_ids=["greenhouse-canonical", "lever-fintual"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )

            # Second run must stage 0 new candidates and detect all as duplicates
            self.assertEqual(report2.total_new_staged, 0)
            self.assertGreater(report2.total_duplicates, 0)

            # Inbox candidate count must remain strictly identical
            staged_data = json.loads(temp_inbox.read_text(encoding="utf-8"))
            self.assertEqual(len(staged_data["candidates"]), initial_staged)

    def test_orchestration_isolates_source_failure_and_continues(self) -> None:
        # Create a modified registry where one source has an invalid connector/configuration
        custom_registry = copy.deepcopy(self.registry)
        broken_source = {
            "id": "broken-source-simulated",
            "kind": "public_ats_api",
            "connector": "greenhouse-job-board",
            "enabled": True,
            "decision": "approved",
            "automatedAccessStatus": "approved",
            "termsReview": "approved_public_api",
            "rightsReview": "metadata_only_approved",
            "boardToken": "invalid!token*forbidden",
            "employer": "Broken Corp",
            "allowedHosts": ["boards-api.greenhouse.io"],
            "maxRequestsPerRun": 1,
        }
        custom_registry["sources"].append(broken_source)

        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            report = run_pilot_acquisition(
                source_ids=["broken-source-simulated", "lever-fintual"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
                override_sources_registry=custom_registry,
            )

            self.assertEqual(report.sources_evaluated, 2)
            self.assertEqual(report.sources_succeeded, 1)
            self.assertEqual(report.sources_failed, 1)

            # Broken source recorded failure
            failed_sum = next(s for s in report.source_summaries if s.source_id == "broken-source-simulated")
            self.assertEqual(failed_sum.status, "failed")
            self.assertIsNotNone(failed_sum.error)

            # Working source succeeded
            success_sum = next(s for s in report.source_summaries if s.source_id == "lever-fintual")
            self.assertEqual(success_sum.status, "success")
            self.assertGreater(success_sum.new_candidates, 0)

    def test_orchestration_handles_http_errors_gracefully(self) -> None:
        """Simulates network HTTP error on one source while other source succeeds."""
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            def mock_fetch(source, *args, **kwargs):
                if source.get("id") == "greenhouse-canonical":
                    raise ValueError("source_http_500")
                return [
                    {
                        "candidateId": "CAND-lever-fintual-99901",
                        "sourceId": "lever-fintual",
                        "sourceUrl": "https://api.lever.co/v0/postings/fintual?mode=json",
                        "capturedAt": "2026-11-22T12:00:00-05:00",
                        "captureMethod": "manual",
                        "proposed": {
                            "title": "Software Engineer",
                            "employer": "Fintual",
                            "publisher": "Portal público oficial (ATS Lever)",
                            "externalReference": "99901",
                            "applyUrl": "https://jobs.lever.co/fintual/99901",
                            "location": "Remoto (LATAM)",
                            "mode": "Remoto",
                            "opportunityType": "Full-time",
                            "publishedAt": "2026-11-20",
                            "deadline": None,
                            "salary": None,
                            "benefits": None,
                            "requirements": None,
                        },
                        "fieldEvidence": [
                            {"field": "title", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "employer", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "publisher", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "externalReference", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "applyUrl", "url": "https://jobs.lever.co/fintual/99901", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "location", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "mode", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "opportunityType", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                            {"field": "publishedAt", "url": "https://api.lever.co/v0/postings/fintual?mode=json", "observedAt": "2026-11-22T12:00:00-05:00"},
                        ],
                        "editorialReview": {
                            "status": "pending_review",
                            "reviewer": None,
                            "reviewedAt": None,
                            "decisionNote": None,
                        },
                    }
                ]

            with patch("collector.acquisition_runner.fetch_greenhouse_board", side_effect=mock_fetch), \
                 patch("collector.acquisition_runner.fetch_lever_board", side_effect=mock_fetch):
                report = run_pilot_acquisition(
                    source_ids=["greenhouse-canonical", "lever-fintual"],
                    inbox_path=temp_inbox,
                    seed_path=SEED_PATH,
                    fixtures_dir=None,
                    as_of=TODAY,
                    dry_run=False,
                )

            self.assertEqual(report.sources_evaluated, 2)
            self.assertEqual(report.sources_succeeded, 1)
            self.assertEqual(report.sources_failed, 1)
            self.assertIn("source_http_500", report.source_summaries[0].error)
            self.assertEqual(report.total_new_staged, 1)

    def test_deduplication_against_canonical_seed_opportunities(self) -> None:
        """Verifies that jobs matching opportunities already promoted to canonical seed are detected as duplicates."""
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            # CookUnity fixture contains 8039990003, which is already OP-005 in opportunities.seed.json
            report = run_pilot_acquisition(
                source_ids=["greenhouse-cookunity"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )

            # 8039990003 is matched as duplicate against seed!
            self.assertEqual(report.sources_succeeded, 1)
            self.assertGreater(report.total_duplicates, 0)
            self.assertEqual(report.total_new_staged, 0)

    # =========================================================================
    # R4-01D: CLI Execution & Local Operation
    # =========================================================================

    def test_cli_acquire_dry_run_does_not_modify_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")
            inbox_before = temp_inbox.read_bytes()

            out_buf = io.StringIO()
            with redirect_stdout(out_buf):
                exit_code = cli.main([
                    "acquire",
                    "--source", "greenhouse-canonical",
                    "--inbox", str(temp_inbox),
                    "--fixtures-dir", str(FIXTURES_ATS_DIR),
                    "--as-of", "2026-11-22",
                    "--dry-run",
                ])

            self.assertEqual(exit_code, cli.EXIT_OK)
            self.assertIn("DRY-RUN (Simulación)", out_buf.getvalue())
            self.assertEqual(temp_inbox.read_bytes(), inbox_before, "Dry-run no debe modificar la bandeja")

    def test_cli_acquire_json_report_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")
            report_file = Path(td) / "report.json"

            out_buf = io.StringIO()
            with redirect_stdout(out_buf):
                exit_code = cli.main([
                    "acquire",
                    "--source", "lever-kavak",
                    "--inbox", str(temp_inbox),
                    "--fixtures-dir", str(FIXTURES_ATS_DIR),
                    "--as-of", "2026-11-22",
                    "--output", str(report_file),
                    "--json-report",
                ])

            self.assertEqual(exit_code, cli.EXIT_OK)
            parsed_json = json.loads(out_buf.getvalue())
            self.assertIn("metrics", parsed_json)
            self.assertIn("sources", parsed_json)
            self.assertTrue(report_file.exists())


if __name__ == "__main__":
    unittest.main()
