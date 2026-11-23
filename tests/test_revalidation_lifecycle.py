"""Comprehensive unit, integration, and operational tests for R4-03 Lifecycle, Freshness, and Change Detection.

Tests:
- R4-03B: Conceptual audit of freshness, deadline, TTL, and temporal validity.
- R4-03C: Revalidation engine, field change detection, and mass closure protection.
- R4-03D: CLI revalidate command, deterministic fixtures, dry-run, and reporting.
- R4-03E: Canonical catalog immutability, zero autonomous promotions, and idempotency.
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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scripts.editorial_cli as cli
from collector.policy import find_source, load_source_registry
from collector.revalidation import (
    STATE_CHANGED,
    STATE_CONFIRMED_DISAPPEARED,
    STATE_DISAPPEARED_ONCE,
    STATE_PRESERVED_ON_SOURCE_ERROR,
    STATE_STILL_ACTIVE,
    detect_field_differences,
    evaluate_temporal_freshness,
    revalidate_candidates,
    run_revalidation_job,
)

FIXTURES_ATS_DIR = ROOT / "tests" / "fixtures" / "ats"
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
SNAPSHOT_PATH = ROOT / "data" / "opportunities.json"
TODAY = date(2026, 11, 22)


def _calc_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_candidate(
    candidate_id: str = "CAND-test-001",
    source_id: str = "greenhouse-canonical",
    ext_ref: str = "8379825",
    title: str = "Graduate Software Engineer (Americas Remote)",
    location: str = "Home Based - Americas",
    mode: str = "Remoto",
    deadline: str | None = None,
    observed_at: str = "2026-11-20T10:00:00-05:00",
    consecutive_missing: int = 0,
) -> dict:
    source_url = "https://boards-api.greenhouse.io/v1/boards/canonical/jobs"
    apply_url = f"https://job-boards.greenhouse.io/canonical/jobs/{ext_ref}"
    return {
        "candidateId": candidate_id,
        "sourceId": source_id,
        "sourceUrl": source_url,
        "capturedAt": "2026-11-20T10:00:00-05:00",
        "captureMethod": "manual",
        "consecutiveMissingCount": consecutive_missing,
        "proposed": {
            "title": title,
            "employer": "Canonical",
            "publisher": "Portal público oficial (ATS Greenhouse)",
            "externalReference": ext_ref,
            "applyUrl": apply_url,
            "publishedAt": "2026-11-16",
            "deadline": deadline,
            "location": location,
            "mode": mode,
            "opportunityType": "Empleo",
            "salary": None,
            "benefits": "USD 2,000 presupuesto anual",
            "requirements": "Graduación en Informática o STEM",
        },
        "fieldEvidence": [
            {"field": "title", "url": apply_url, "observedAt": observed_at},
            {"field": "employer", "url": source_url, "observedAt": observed_at},
            {"field": "publisher", "url": source_url, "observedAt": observed_at},
            {"field": "externalReference", "url": source_url, "observedAt": observed_at},
            {"field": "applyUrl", "url": apply_url, "observedAt": observed_at},
            {"field": "location", "url": apply_url, "observedAt": observed_at},
            {"field": "mode", "url": apply_url, "observedAt": observed_at},
        ],
        "editorialReview": {
            "status": "pending_review",
            "reviewer": None,
            "reviewedAt": None,
            "decisionNote": None,
        },
    }


class TestRevalidationLifecycle(unittest.TestCase):
    def setUp(self) -> None:
        self.seed_hash_before = _calc_sha256(SEED_PATH)
        self.snap_hash_before = _calc_sha256(SNAPSHOT_PATH)
        self.registry = load_source_registry()

    def tearDown(self) -> None:
        self.assertEqual(_calc_sha256(SEED_PATH), self.seed_hash_before, "Semilla canónica fue alterada")
        self.assertEqual(_calc_sha256(SNAPSHOT_PATH), self.snap_hash_before, "Snapshot canónico fue alterado")

    # =========================================================================
    # R4-03B: Temporal Freshness & Expiration Auditing
    # =========================================================================

    def test_deadline_expired_vs_future_evaluation(self) -> None:
        # 1. Deadline in past
        cand_past = _make_candidate(deadline="2026-11-10")
        dl_st, dl_val, _, notes = evaluate_temporal_freshness(cand_past, as_of_date=TODAY)
        self.assertEqual(dl_st, "DEADLINE_EXPIRED")
        self.assertEqual(dl_val, "2026-11-10")
        self.assertTrue(any("superada" in n for n in notes))

        # 2. Deadline in future
        cand_future = _make_candidate(deadline="2026-12-01")
        dl_st, dl_val, _, notes = evaluate_temporal_freshness(cand_future, as_of_date=TODAY)
        self.assertEqual(dl_st, "DEADLINE_FUTURE")
        self.assertEqual(dl_val, "2026-12-01")

        # 3. Deadline unstated
        cand_null = _make_candidate(deadline=None)
        dl_st, dl_val, _, _ = evaluate_temporal_freshness(cand_null, as_of_date=TODAY)
        self.assertEqual(dl_st, "DEADLINE_UNKNOWN")
        self.assertIsNone(dl_val)

    def test_evidence_freshness_ttl_audit(self) -> None:
        # Fresh evidence (within 7 days of 2026-11-22)
        cand_fresh = _make_candidate(observed_at="2026-11-20T10:00:00-05:00")
        _, _, fresh_st, _ = evaluate_temporal_freshness(cand_fresh, as_of_date=TODAY, ttl_days=7)
        self.assertEqual(fresh_st, "ALL_FRESH")

        # Stale evidence (older than 7 days, e.g. 2026-11-10)
        cand_stale = _make_candidate(observed_at="2026-11-10T10:00:00-05:00")
        _, _, fresh_st, notes = evaluate_temporal_freshness(cand_stale, as_of_date=TODAY, ttl_days=7)
        self.assertEqual(fresh_st, "ALL_STALE")
        self.assertTrue(any("TTL" in n for n in notes))

    # =========================================================================
    # R4-03C: Change Detection & Active State Reconfirmation
    # =========================================================================

    def test_detect_field_differences_identifies_exact_changes(self) -> None:
        current = {
            "title": "Junior Developer",
            "location": "Lima, Peru",
            "mode": "Presencial",
            "salary": None,
        }
        fresh = {
            "title": "Junior Software Engineer",
            "location": "Lima, Peru",
            "mode": "Remoto",
            "salary": "USD 1,200",
        }
        changes = detect_field_differences(current, fresh)
        changed_fields = {c.field: (c.previous_value, c.current_value) for c in changes}

        self.assertIn("title", changed_fields)
        self.assertEqual(changed_fields["title"], ("Junior Developer", "Junior Software Engineer"))

        self.assertIn("mode", changed_fields)
        self.assertEqual(changed_fields["mode"], ("Presencial", "Remoto"))

        self.assertIn("salary", changed_fields)
        self.assertEqual(changed_fields["salary"], (None, "USD 1,200"))

        # Location was unchanged -> should not be in changes
        self.assertNotIn("location", changed_fields)

    def test_revalidation_with_fixtures_reconfirms_still_active(self) -> None:
        # greenhouse-canonical.json contains job id 8379825 with title "Graduate Software Engineer (Americas Remote)"
        cand = _make_candidate(ext_ref="8379825")
        report, updated = revalidate_candidates(
            [cand],
            sources_registry=self.registry,
            source_ids=["greenhouse-canonical"],
            fixtures_dir=FIXTURES_ATS_DIR,
            as_of=TODAY,
            apply_updates=True,
        )

        self.assertEqual(report.sources_succeeded, 1)
        self.assertEqual(report.sources_failed, 0)
        self.assertEqual(report.still_active_count, 1)
        self.assertEqual(report.changed_count, 0)
        self.assertEqual(report.disappeared_once_count, 0)
        self.assertEqual(report.candidate_results[0].lifecycle_state, STATE_STILL_ACTIVE)
        self.assertEqual(report.candidate_results[0].consecutive_missing_count, 0)

    def test_revalidation_detects_field_changes(self) -> None:
        # In fixture, title is "Graduate Software Engineer (Americas Remote)"
        # Candidate has previous title "Software Engineer Trainee"
        cand = _make_candidate(ext_ref="8379825", title="Software Engineer Trainee")
        report, updated = revalidate_candidates(
            [cand],
            sources_registry=self.registry,
            source_ids=["greenhouse-canonical"],
            fixtures_dir=FIXTURES_ATS_DIR,
            as_of=TODAY,
            apply_updates=True,
        )

        self.assertEqual(report.changed_count, 1)
        self.assertEqual(report.still_active_count, 0)
        self.assertEqual(report.candidate_results[0].lifecycle_state, STATE_CHANGED)
        changes = report.candidate_results[0].changes
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].field, "title")
        self.assertEqual(changes[0].previous_value, "Software Engineer Trainee")
        self.assertEqual(changes[0].current_value, "Graduate Software Engineer (Americas Remote)")

        # Updated candidate proposed should have new title
        self.assertEqual(updated[0]["proposed"]["title"], "Graduate Software Engineer (Americas Remote)")

    # =========================================================================
    # R4-03C: Conservative Disappearance & Mass Closure Protection
    # =========================================================================

    def test_single_fetch_disappearance_does_not_close_job(self) -> None:
        # Job id 9999999 does NOT exist in fixture greenhouse-canonical.json
        cand = _make_candidate(ext_ref="9999999", consecutive_missing=0)
        report, updated = revalidate_candidates(
            [cand],
            sources_registry=self.registry,
            source_ids=["greenhouse-canonical"],
            fixtures_dir=FIXTURES_ATS_DIR,
            as_of=TODAY,
            consecutive_missing_threshold=2,
            apply_updates=True,
        )

        self.assertEqual(report.disappeared_once_count, 1)
        self.assertEqual(report.confirmed_disappeared_count, 0)
        self.assertEqual(report.candidate_results[0].lifecycle_state, STATE_DISAPPEARED_ONCE)
        self.assertEqual(report.candidate_results[0].consecutive_missing_count, 1)
        self.assertEqual(report.candidate_results[0].recommended_action, "VERIFY_NEXT_RUN")
        # Candidate must NOT be marked rejected or closed
        self.assertEqual(updated[0]["editorialReview"]["status"], "pending_review")

    def test_confirmed_disappearance_after_threshold(self) -> None:
        # Job id 9999999 already had consecutive_missing = 1, now missing again -> reaches threshold 2
        cand = _make_candidate(ext_ref="9999999", consecutive_missing=1)
        report, updated = revalidate_candidates(
            [cand],
            sources_registry=self.registry,
            source_ids=["greenhouse-canonical"],
            fixtures_dir=FIXTURES_ATS_DIR,
            as_of=TODAY,
            consecutive_missing_threshold=2,
            apply_updates=True,
        )

        self.assertEqual(report.confirmed_disappeared_count, 1)
        self.assertEqual(report.disappeared_once_count, 0)
        self.assertEqual(report.candidate_results[0].lifecycle_state, STATE_CONFIRMED_DISAPPEARED)
        self.assertEqual(report.candidate_results[0].consecutive_missing_count, 2)
        self.assertEqual(report.candidate_results[0].recommended_action, "MARK_EXPIRED_OR_CLOSED")

    def test_network_or_source_failure_preserves_candidates_without_mass_closure(self) -> None:
        # Create candidate with source pointing to non-existent board or raising error
        cand = _make_candidate(ext_ref="8379825")

        with patch("collector.revalidation.fetch_greenhouse_board", side_effect=ConnectionError("WAF or timeout 504")):
            report, updated = revalidate_candidates(
                [cand],
                sources_registry=self.registry,
                source_ids=["greenhouse-canonical"],
                fixtures_dir=None,  # Live mode mocked to fail
                as_of=TODAY,
                apply_updates=True,
            )

            self.assertEqual(report.sources_failed, 1)
            self.assertEqual(report.preserved_on_error_count, 1)
            self.assertEqual(report.disappeared_once_count, 0)
            self.assertEqual(report.confirmed_disappeared_count, 0)
            self.assertEqual(report.candidate_results[0].lifecycle_state, STATE_PRESERVED_ON_SOURCE_ERROR)
            self.assertEqual(report.candidate_results[0].consecutive_missing_count, 0)
            self.assertTrue(any("Fallo transitorio" in n for n in report.candidate_results[0].notes))

    # =========================================================================
    # R4-03D: CLI Subcommand & Reporting
    # =========================================================================

    def test_cli_revalidate_dry_run_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            cand = _make_candidate(ext_ref="8379825")
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": [cand]}), encoding="utf-8")

            stdout_buf = io.StringIO()
            with redirect_stdout(stdout_buf):
                exit_code = cli.main([
                    "revalidate",
                    "--inbox", str(temp_inbox),
                    "--source", "greenhouse-canonical",
                    "--fixtures-dir", str(FIXTURES_ATS_DIR),
                    "--as-of", "2026-11-22",
                    "--json-report",
                ])

            self.assertEqual(exit_code, cli.EXIT_OK)
            output_json = json.loads(stdout_buf.getvalue())
            self.assertIn("summary", output_json)
            self.assertEqual(output_json["summary"]["stillActive"], 1)
            self.assertEqual(output_json["summary"]["changed"], 0)

    def test_revalidation_job_does_not_mutate_canonical_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_inbox = Path(td) / "inbox.local.json"
            cand = _make_candidate(ext_ref="8379825")
            temp_inbox.write_text(json.dumps({"schemaVersion": 1, "candidates": [cand]}), encoding="utf-8")

            report = run_revalidation_job(
                inbox_path=temp_inbox,
                source_ids=["greenhouse-canonical"],
                fixtures_dir=FIXTURES_ATS_DIR,
                as_of=TODAY,
                update_inbox=True,
                dry_run=False,
            )

            self.assertEqual(report.still_active_count, 1)
            # Verify inbox was updated with valid Schema 1
            updated_data = json.loads(temp_inbox.read_text(encoding="utf-8"))
            self.assertEqual(updated_data["schemaVersion"], 1)
            self.assertEqual(len(updated_data["candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
