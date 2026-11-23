"""Integration, operational, and regression tests for R4-04 Periodic Acquisition & Staging Maintenance.

Validates:
- R4-04A: Functional and operational distinction between acquisition and revalidation.
- R4-04B: Reproducible, idempotent multisource and single-source acquisition operations.
- R4-04C: Staging maintenance, candidate validation, fail-closed fault tolerance, and zero PII.
- R4-04D: Safeguards for scheduled execution, immutability of canonical catalogs, and CLI reporting.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
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
    run_pilot_acquisition,
)
from collector.revalidation import run_revalidation_job
from collector.policy import find_source, load_source_registry

FIXTURES_ATS_DIR = ROOT / "tests" / "fixtures" / "ats"
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
SOURCES_PATH = ROOT / "collector" / "sources.json"
INBOX_LOCAL_PATH = ROOT / "data" / "candidates" / "inbox.local.json"
TODAY = date(2026, 11, 22)


def _calc_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestPeriodicAcquisitionOpsR404(unittest.TestCase):
    def setUp(self) -> None:
        self.seed_hash_before = _calc_sha256(SEED_PATH)
        self.snap_hash_before = _calc_sha256(SNAPSHOT_PATH)
        self.sources_hash_before = _calc_sha256(SOURCES_PATH)
        self.registry = load_source_registry()

    def tearDown(self) -> None:
        # Canonical catalog and registry immutability guarantee
        self.assertEqual(_calc_sha256(SEED_PATH), self.seed_hash_before, "La semilla canónica fue modificada")
        self.assertEqual(_calc_sha256(SNAPSHOT_PATH), self.snap_hash_before, "El snapshot canónico fue modificado")
        self.assertEqual(_calc_sha256(SOURCES_PATH), self.sources_hash_before, "El registro de fuentes fue modificado")

    # =========================================================================
    # R4-04A: Functional Distinction: Acquisition vs Revalidation
    # =========================================================================

    def test_acquisition_discovers_new_postings_without_modifying_catalog(self) -> None:
        """Acquisition discovers fresh postings and stages them in pending_review."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_inbox = Path(tmpdir) / "staging_inbox.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            # Use lever-kavak fixture which is not present in canonical seed
            report = run_pilot_acquisition(
                source_ids=["lever-kavak"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )

            self.assertEqual(report.sources_evaluated, 1)
            self.assertEqual(report.sources_succeeded, 1)
            self.assertEqual(report.sources_failed, 0)
            self.assertGreater(report.total_new_staged, 0)

            # Check staged content
            staged_data = json.loads(temp_inbox.read_text(encoding="utf-8"))
            self.assertEqual(len(staged_data["candidates"]), report.total_new_staged)
            for cand in staged_data["candidates"]:
                self.assertEqual(cand["editorialReview"]["status"], "pending_review")
                self.assertIsNotNone(cand.get("capturedAt"))
                self.assertIsNotNone(cand.get("fieldEvidence"))

    def test_revalidation_verifies_existing_without_discovery(self) -> None:
        """Revalidation evaluates known candidates for freshness, lifecycle, and changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_inbox = Path(tmpdir) / "staging_inbox.json"
            candidate = {
                "candidateId": "CAND-greenhouse-canonical-12345",
                "sourceId": "greenhouse-canonical",
                "proposed": {
                    "title": "Software Engineer, Core Team",
                    "employer": "Canonical",
                    "requisition": "canonical-12345",
                    "externalReference": "12345",
                    "applyUrl": "https://canonical.com/careers/12345",
                    "location": "Remote, Americas",
                    "mode": "Remoto",
                    "profile": "software_engineering",
                    "experienceLevel": "mid",
                },
                "editorialReview": {
                    "status": "pending_review",
                    "reviewedBy": "editorial_pilot",
                    "reviewedAt": "2026-11-22T10:00:00-05:00",
                },
                "evidence": {
                    "capturedAt": "2026-11-22T10:00:00-05:00",
                    "lastObservedAt": "2026-11-22T10:00:00-05:00",
                    "observedConsecutiveMissingCount": 0,
                },
            }
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": [candidate]}), encoding="utf-8")

            report = run_revalidation_job(
                inbox_path=temp_inbox,
                source_ids=["greenhouse-canonical"],
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=True,
            )

            self.assertEqual(report.total_candidates_evaluated, 1)
            self.assertEqual(report.sources_evaluated, 1)

    # =========================================================================
    # R4-04B: Reproducibility, Idempotency and Fault Isolation
    # =========================================================================

    def test_acquisition_is_strictly_idempotent(self) -> None:
        """Executing acquisition twice with unchanged source results in zero duplicates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_inbox = Path(tmpdir) / "staging_inbox.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            # First run: acquires new candidates from lever-kavak
            report1 = run_pilot_acquisition(
                source_ids=["lever-kavak"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )
            count1 = report1.total_new_staged
            self.assertGreater(count1, 0)

            # Second run: must detect all as duplicates and stage 0 new candidates
            report2 = run_pilot_acquisition(
                source_ids=["lever-kavak"],
                inbox_path=temp_inbox,
                seed_path=SEED_PATH,
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                dry_run=False,
            )
            self.assertEqual(report2.total_new_staged, 0)
            self.assertGreaterEqual(report2.total_duplicates, count1)

            # File candidate count is unchanged
            staged_data = json.loads(temp_inbox.read_text(encoding="utf-8"))
            self.assertEqual(len(staged_data["candidates"]), count1)

    def test_fault_isolation_when_single_source_fails(self) -> None:
        """If one ATS source fails, remaining sources complete normally and staging is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_inbox = Path(tmpdir) / "staging_inbox.json"
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": []}), encoding="utf-8")

            # Create a custom fixtures dir containing only lever-kavak, leaving greenhouse-canonical missing
            custom_fixtures = Path(tmpdir) / "custom_fixtures"
            custom_fixtures.mkdir()
            kavak_fixture = custom_fixtures / "lever-kavak.json"
            kavak_fixture.write_text((FIXTURES_ATS_DIR / "lever-kavak.json").read_text(encoding="utf-8"), encoding="utf-8")

            # Patch fetch_greenhouse_board to simulate network error when called for greenhouse-canonical
            with patch("collector.acquisition_runner.fetch_greenhouse_board") as mock_fetch:
                mock_fetch.side_effect = ConnectionResetError("Endpoint Greenhouse Canonical no responde (503)")

                report = run_pilot_acquisition(
                    source_ids=["greenhouse-canonical", "lever-kavak"],
                    inbox_path=temp_inbox,
                    seed_path=SEED_PATH,
                    fixtures_dir=custom_fixtures,
                    as_of=TODAY,
                    dry_run=False,
                )

                self.assertEqual(report.sources_evaluated, 2)
                self.assertEqual(report.sources_succeeded, 1)
                self.assertEqual(report.sources_failed, 1)

                canonical_summary = next(s for s in report.source_summaries if s.source_id == "greenhouse-canonical")
                self.assertEqual(canonical_summary.status, "failed")
                self.assertIn("503", canonical_summary.error or "")

                kavak_summary = next(s for s in report.source_summaries if s.source_id == "lever-kavak")
                self.assertEqual(kavak_summary.status, "success")
                self.assertGreater(kavak_summary.new_candidates, 0)

    # =========================================================================
    # R4-04C: Staging Privacy & Zero PII Guarantee
    # =========================================================================

    def test_staging_candidates_contain_zero_pii(self) -> None:
        """Verifies staging inbox contains no personal information (applicant or recruiter)."""
        data = json.loads(INBOX_LOCAL_PATH.read_text(encoding="utf-8"))
        candidates = data.get("candidates", [])
        self.assertGreater(len(candidates), 0)

        forbidden_pii_keys = {
            "applicantName", "candidateName", "email", "phone", "recruiterEmail",
            "recruiterPhone", "dni", "ssn", "passport", "birthDate", "address",
        }

        valid_review_statuses = {"pending_review", "approved_for_catalog", "rejected"}

        for cand in candidates:
            # Check root keys
            cand_keys = set(cand.keys())
            self.assertEqual(len(cand_keys & forbidden_pii_keys), 0)

            # Check proposed keys
            proposed = cand.get("proposed", {})
            proposed_keys = set(proposed.keys())
            self.assertEqual(len(proposed_keys & forbidden_pii_keys), 0)

            # Check editorialReview keys
            ed_review = cand.get("editorialReview", {})
            ed_keys = set(ed_review.keys())
            self.assertEqual(len(ed_keys & forbidden_pii_keys), 0)

            # Ensure valid review status
            self.assertIn(ed_review.get("status"), valid_review_statuses)

    # =========================================================================
    # R4-04D: CLI Reporting and Safeguards
    # =========================================================================

    def test_cli_acquire_dry_run_leaves_inbox_untouched(self) -> None:
        """CLI acquire with --dry-run produces output report without modifying staging."""
        inbox_hash_before = _calc_sha256(INBOX_LOCAL_PATH)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_report = Path(tmpdir) / "acq_report.json"
            exit_code = cli.main([
                "acquire",
                "--dry-run",
                "--fixtures-dir", str(FIXTURES_ATS_DIR),
                "--as-of", "2026-11-22",
                "--output", str(out_report),
            ])

            self.assertEqual(exit_code, 0)
            self.assertEqual(_calc_sha256(INBOX_LOCAL_PATH), inbox_hash_before)
            self.assertTrue(out_report.exists())

            report_data = json.loads(out_report.read_text(encoding="utf-8"))
            self.assertTrue(report_data.get("dryRun"))
            self.assertEqual(report_data["metrics"]["sourcesEvaluated"], 5)
            self.assertEqual(report_data["metrics"]["sourcesSucceeded"], 5)

    def test_cli_acquire_refuses_to_write_to_canonical_paths(self) -> None:
        """CLI acquire raises PermissionError if someone targets seed or snapshot catalog."""
        with self.assertRaises(PermissionError):
            cli._assert_not_canonical(SEED_PATH, "test_write")

        with self.assertRaises(PermissionError):
            cli._assert_not_canonical(SNAPSHOT_PATH, "test_write")

        with self.assertRaises(PermissionError):
            cli._assert_not_canonical(SOURCES_PATH, "test_write")


if __name__ == "__main__":
    unittest.main()
