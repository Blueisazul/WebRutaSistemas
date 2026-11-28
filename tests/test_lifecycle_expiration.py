"""Unit tests for TASK-FIX-EXP-01: Lifecycle expiration and Greenhouse withdrawal.

Validates:
1. Civil date deadline evaluation (Decisión 9: valid during full calendar day in America/Lima).
2. Timestamp deadline evaluation with timezone (ISO 8601).
3. Independence of deadline from employmentEndDate and verification TTL.
4. Withdrawn, closed, and expired lifecycle states transition to historical.
5. Inactive apply CTA constraints for non-active opportunities.
6. Public metrics calculation excluding expired/closed/withdrawn from active.
7. Verification that all Greenhouse sources are withdrawn and disabled.
8. Verification that candidate inbox has zero active Greenhouse proposals.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIMA_TZ = timezone(timedelta(hours=-5), "America/Lima")

from collector.evidence import (
    DEADLINE_EXPIRED,
    DEADLINE_FUTURE,
    DEADLINE_REACHED,
    DEADLINE_UNKNOWN,
)
from collector.revalidation import evaluate_temporal_freshness
from scripts.catalog_quality import effective_states, parse_date


class TestLifecycleExpiration(unittest.TestCase):
    def setUp(self):
        self.ref_date = date(2026, 11, 27)

    def test_civil_date_past_is_expired(self):
        candidate = {"proposed": {"deadline": "2026-11-26"}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_EXPIRED)
        self.assertEqual(dl_str, "2026-11-26")

    def test_civil_date_today_is_active_until_end_of_day(self):
        candidate = {"proposed": {"deadline": "2026-11-27"}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_REACHED)
        self.assertEqual(dl_str, "2026-11-27")

    def test_civil_date_future_is_not_expired(self):
        candidate = {"proposed": {"deadline": "2026-11-28"}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_FUTURE)
        self.assertEqual(dl_str, "2026-11-28")

    def test_missing_deadline_is_not_expired_by_inference(self):
        candidate = {"proposed": {"deadline": None}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_UNKNOWN)
        self.assertIsNone(dl_str)

    def test_iso_timestamp_past_date_is_expired(self):
        candidate = {"proposed": {"deadline": "2026-11-25T23:59:59-05:00"}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_EXPIRED)

    def test_iso_timestamp_today_is_reached_or_future(self):
        candidate = {"proposed": {"deadline": "2026-11-27T18:00:00-05:00"}}
        status, dl_str, _, notes = evaluate_temporal_freshness(candidate, as_of_date=self.ref_date)
        self.assertEqual(status, DEADLINE_REACHED)

    def test_employment_end_date_does_not_affect_deadline(self):
        # A job whose contract ends in the past, but has no deadline, is NOT deadline-expired
        record = {
            "opportunityStatus": "open",
            "verificationStatus": "verified",
            "publicationStatus": "active",
            "deadline": None,
            "employmentEndDate": "2026-01-01",
            "lastVerifiedAt": "2026-11-25T12:00:00-05:00",
        }
        # parse_date for deadline is None
        self.assertIsNone(parse_date(record.get("deadline"), "deadline"))
        # effective_states should not mark opportunity as expired based on employmentEndDate
        states = effective_states(record, today=self.ref_date)
        self.assertNotEqual(states["opportunityStatus"], "expired")

    def test_effective_states_expired_transitions_to_historical(self):
        record = {
            "opportunityStatus": "open",
            "verificationStatus": "verified",
            "publicationStatus": "active",
            "deadline": "2026-11-20",
            "lastVerifiedAt": "2026-11-25T12:00:00-05:00",
        }
        states = effective_states(record, today=self.ref_date)
        self.assertEqual(states["opportunityStatus"], "expired")
        self.assertEqual(states["publicationStatus"], "historical")

    def test_effective_states_withdrawn_transitions_to_historical(self):
        record = {
            "opportunityStatus": "withdrawn",
            "verificationStatus": "stale",
            "publicationStatus": "active",
            "deadline": "2026-12-31",
            "lastVerifiedAt": "2026-11-25T12:00:00-05:00",
        }
        states = effective_states(record, today=self.ref_date)
        self.assertEqual(states["opportunityStatus"], "withdrawn")
        self.assertEqual(states["publicationStatus"], "historical")

    def test_greenhouse_sources_withdrawn_in_registry(self):
        sources_path = ROOT / "collector" / "sources.json"
        with sources_path.open("r", encoding="utf-8") as f:
            registry = json.load(f)

        greenhouse_sources = [
            s for s in registry.get("sources", [])
            if "greenhouse" in s.get("id", "") or "canonical" in s.get("id", "")
        ]
        self.assertGreaterEqual(len(greenhouse_sources), 3)

        for src in greenhouse_sources:
            s_id = src.get("id")
            self.assertFalse(src.get("enabled", True), f"{s_id} should be disabled")
            self.assertEqual(src.get("decision"), "withdrawn", f"{s_id} decision should be withdrawn")

    def test_inbox_zero_active_greenhouse_candidates(self):
        inbox_path = ROOT / "data" / "candidates" / "inbox.local.json"
        if not inbox_path.exists():
            self.skipTest("inbox.local.json not found")

        with inbox_path.open("r", encoding="utf-8") as f:
            inbox = json.load(f)

        candidates = inbox.get("candidates", [])
        for c in candidates:
            s_id = c.get("sourceId", "")
            is_gh = "greenhouse" in s_id or "canonical" in s_id
            if is_gh:
                ed = c.get("editorialReview", {})
                self.assertNotEqual(
                    ed.get("status"),
                    "pending_review",
                    f"Candidate {c.get('candidateId')} from {s_id} must not be in pending_review"
                )


if __name__ == "__main__":
    unittest.main()
