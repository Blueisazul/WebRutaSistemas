"""Unit tests for evidence provenance, freshness, and opportunity validity verification (R2-OSS-05)."""

from __future__ import annotations

import copy
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from collector.evidence import (
    CandidateEvidenceReport,
    FieldEvidenceEvaluation,
    is_valid_https_url,
    parse_iso_date,
    parse_iso_timestamp,
    verify_candidate_evidence,
    verify_candidates_evidence,
    DEADLINE_EXPIRED,
    DEADLINE_FUTURE,
    DEADLINE_INVALID,
    DEADLINE_REACHED,
    DEADLINE_UNKNOWN,
    FRESHNESS_FRESH,
    FRESHNESS_FUTURE,
    FRESHNESS_INVALID,
    FRESHNESS_STALE,
    PROVENANCE_ALLOWED,
    PROVENANCE_HOST_NOT_ALLOWLISTED,
    PROVENANCE_INVALID,
    PROVENANCE_VALID,
    REMOTE_NOT_CHECKED,
    SOURCE_PENDING,
    STRUCTURAL_INVALID,
    STRUCTURAL_VALID,
    SUMMARY_ALL_FRESH,
    SUMMARY_ALL_STALE,
    SUMMARY_INVALID_TEMPORALITY,
    SUMMARY_NO_EVIDENCE,
    SUMMARY_PARTIALLY_STALE,
)
import scripts.validate_candidates as validate_candidates_script


FIXTURES_PATH = Path(__file__).resolve().parent / "fixtures" / "evidence" / "evidence_cases.json"


class TestEvidenceHelpers(unittest.TestCase):
    """Low-level helper validation tests."""

    def test_is_valid_https_url(self) -> None:
        self.assertEqual(is_valid_https_url("https://example.com/path"), (True, "example.com"))
        self.assertEqual(is_valid_https_url("https://sub.domain.pe:443/job"), (True, "sub.domain.pe"))
        self.assertEqual(is_valid_https_url("http://insecure.com"), (False, None))
        self.assertEqual(is_valid_https_url("https:///no-host"), (False, None))
        self.assertEqual(is_valid_https_url("https://user:pass@host.com/"), (False, None))
        self.assertEqual(is_valid_https_url("https://host.com:8080/"), (False, None))
        self.assertEqual(is_valid_https_url(""), (False, None))
        self.assertEqual(is_valid_https_url(None), (False, None))
        self.assertEqual(is_valid_https_url(123), (False, None))

    def test_parse_iso_date(self) -> None:
        self.assertEqual(parse_iso_date("2026-11-17"), date(2026, 11, 17))
        self.assertIsNone(parse_iso_date("2026-02-30"))
        self.assertIsNone(parse_iso_date("17-11-2026"))
        self.assertIsNone(parse_iso_date("2026/11/17"))
        self.assertIsNone(parse_iso_date(None))
        self.assertIsNone(parse_iso_date(""))

    def test_parse_iso_timestamp(self) -> None:
        dt = parse_iso_timestamp("2026-11-17T12:00:00-05:00")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.utcoffset().total_seconds(), -5 * 3600)

        dt_z = parse_iso_timestamp("2026-11-17T17:00:00Z")
        self.assertIsNotNone(dt_z)
        self.assertEqual(dt_z.utcoffset().total_seconds(), 0)

        # Naive timestamps without timezone offset must return None
        self.assertIsNone(parse_iso_timestamp("2026-11-17T12:00:00"))
        self.assertIsNone(parse_iso_timestamp("invalid-date"))
        self.assertIsNone(parse_iso_timestamp(None))


class TestEvidenceCasesFromFixtures(unittest.TestCase):
    """Automated execution and verification of all 30 scenarios from fixtures."""

    cases_data: dict

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases_data = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))

    def test_fixtures_count(self) -> None:
        cases = self.cases_data["cases"]
        self.assertGreaterEqual(len(cases), 30, "Deben existir al menos 30 casos de prueba en fixtures")

    def test_all_30_fixture_cases(self) -> None:
        sources_map = {
            "source_bcp": self.cases_data.get("source_bcp"),
            "source_pending": self.cases_data.get("source_pending"),
        }
        cases = self.cases_data["cases"]

        for case_id, case in sorted(cases.items()):
            with self.subTest(case_id=case_id):
                cand = case["candidate"]
                source = sources_map.get(case.get("source_key"))
                as_of = case.get("as_of", "2026-11-17")
                expected = case.get("expected", {})

                report = verify_candidate_evidence(cand, as_of=as_of, source=source)

                if "structural_status" in expected:
                    self.assertEqual(report.structural_status, expected["structural_status"])
                if "provenance_summary" in expected:
                    self.assertEqual(report.provenance_summary, expected["provenance_summary"])
                if "freshness_summary" in expected:
                    self.assertEqual(report.freshness_summary, expected["freshness_summary"])
                if "opportunity_validity" in expected:
                    self.assertEqual(report.opportunity_validity, expected["opportunity_validity"])
                if "has_errors" in expected:
                    self.assertEqual(bool(report.errors), expected["has_errors"])
                if "has_warnings" in expected:
                    self.assertEqual(bool(report.warnings), expected["has_warnings"])
                if "age_days" in expected and report.field_evaluations:
                    self.assertEqual(report.field_evaluations[0].age_days, expected["age_days"])
                if "evidence_count" in expected:
                    self.assertEqual(len(report.field_evaluations), expected["evidence_count"])


class TestProvenanceDimension(unittest.TestCase):
    """Detailed unit tests for Dimension 1: Provenance and URL Structure."""

    def setUp(self) -> None:
        self.source = {
            "id": "src-test",
            "decision": "approved",
            "allowedHosts": ["careers.test.org"],
            "verificationTtlDays": 7,
        }
        self.as_of = "2026-11-17"

    def test_case_01_valid_https(self) -> None:
        candidate = {
            "candidateId": "c1",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-1",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-1", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_VALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_VALID)
        self.assertEqual(report.field_evaluations[0].provenance_status, PROVENANCE_ALLOWED)

    def test_case_02_http_rejected(self) -> None:
        candidate = {
            "candidateId": "c2",
            "sourceId": "src-test",
            "sourceUrl": "http://careers.test.org/job-2",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "http://careers.test.org/job-2", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_INVALID)

    def test_case_03_malformed_url_no_host(self) -> None:
        candidate = {
            "candidateId": "c3",
            "sourceId": "src-test",
            "sourceUrl": "https:///no-host",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https:///no-host", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_INVALID)

    def test_case_04_credentials_in_url(self) -> None:
        candidate = {
            "candidateId": "c4",
            "sourceId": "src-test",
            "sourceUrl": "https://admin:pwd@careers.test.org/job-4",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://admin:pwd@careers.test.org/job-4", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_INVALID)

    def test_case_05_non_standard_port(self) -> None:
        candidate = {
            "candidateId": "c5",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org:8080/job-5",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org:8080/job-5", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_INVALID)

    def test_case_06_unallowed_host(self) -> None:
        candidate = {
            "candidateId": "c6",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-6",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://unauthorized.org/job-6", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.provenance_summary, PROVENANCE_INVALID)
        self.assertEqual(report.field_evaluations[0].provenance_status, PROVENANCE_HOST_NOT_ALLOWLISTED)

    def test_case_07_missing_evidence_url(self) -> None:
        candidate = {
            "candidateId": "c7",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-7",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": None, "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertTrue(any("carece de URL" in e for e in report.errors))

    def test_case_08_inconsistent_evidence_url(self) -> None:
        candidate = {
            "candidateId": "c8",
            "sourceId": "src-no-hosts",
            "sourceUrl": "https://careers.test.org/job-8",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://other-domain.net/job-8", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        # With no allowedHosts specified in source, mismatch with sourceUrl host is flagged
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=None)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertTrue(any("no coincide con el host de sourceUrl" in e for e in report.errors))

    def test_case_09_orphan_evidence(self) -> None:
        candidate = {
            "candidateId": "c9",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-9",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-9", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "salary", "url": "https://careers.test.org/job-9", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_VALID)
        self.assertTrue(report.field_evaluations[1].is_orphan)
        self.assertTrue(any("Evidencia huérfana" in w for w in report.warnings))

    def test_case_10_missing_evidence_for_proposed_field(self) -> None:
        candidate = {
            "candidateId": "c10",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-10",
            "proposed": {"title": "Dev", "employer": "Empresa"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-10", "observedAt": "2026-11-16T10:00:00-05:00"}
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertIn("employer", report.affected_fields)
        self.assertTrue(any("carece de evidencia" in e for e in report.errors))


class TestFreshnessDimension(unittest.TestCase):
    """Detailed unit tests for Dimension 2: Freshness and TTL Temporality."""

    def setUp(self) -> None:
        self.source = {
            "id": "src-test",
            "decision": "approved",
            "allowedHosts": ["careers.test.org"],
            "verificationTtlDays": 7,
        }
        self.as_of = "2026-11-17"

    def test_case_11_observed_today(self) -> None:
        candidate = {
            "candidateId": "c11",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-11",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-11", "observedAt": "2026-11-17T08:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(report.field_evaluations[0].age_days, 0)
        self.assertEqual(report.field_evaluations[0].freshness_status, FRESHNESS_FRESH)

    def test_case_12_within_ttl(self) -> None:
        candidate = {
            "candidateId": "c12",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-12",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-12", "observedAt": "2026-11-14T08:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(report.field_evaluations[0].age_days, 3)

    def test_case_13_exact_ttl_boundary(self) -> None:
        candidate = {
            "candidateId": "c13",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-13",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-13", "observedAt": "2026-11-10T08:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(report.field_evaluations[0].age_days, 7)

    def test_case_14_stale_1_day_over(self) -> None:
        candidate = {
            "candidateId": "c14",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-14",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-14", "observedAt": "2026-11-09T08:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_STALE)
        self.assertEqual(report.field_evaluations[0].age_days, 8)
        self.assertEqual(report.field_evaluations[0].freshness_status, FRESHNESS_STALE)

    def test_case_15_deeply_stale_60_days(self) -> None:
        candidate = {
            "candidateId": "c15",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-15",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-15", "observedAt": "2026-09-18T08:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_STALE)
        self.assertEqual(report.field_evaluations[0].age_days, 60)

    def test_case_16_missing_observed_at(self) -> None:
        candidate = {
            "candidateId": "c16",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-16",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-16", "observedAt": None}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertTrue(any("carece de observedAt" in e for e in report.errors))

    def test_case_17_malformed_observed_at(self) -> None:
        candidate = {
            "candidateId": "c17",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-17",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-17", "observedAt": "invalid-timestamp"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.freshness_summary, SUMMARY_INVALID_TEMPORALITY)

    def test_case_18_future_observed_at(self) -> None:
        candidate = {
            "candidateId": "c18",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-18",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-18", "observedAt": "2026-11-18T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.freshness_summary, SUMMARY_INVALID_TEMPORALITY)
        self.assertEqual(report.field_evaluations[0].freshness_status, FRESHNESS_FUTURE)


class TestValidityDimension(unittest.TestCase):
    """Detailed unit tests for Dimension 3: Opportunity Validity and Deadlines."""

    def setUp(self) -> None:
        self.source = {
            "id": "src-test",
            "decision": "approved",
            "allowedHosts": ["careers.test.org"],
            "verificationTtlDays": 7,
        }
        self.as_of = "2026-11-17"

    def test_case_19_future_deadline(self) -> None:
        candidate = {
            "candidateId": "c19",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-19",
            "proposed": {"title": "Dev", "deadline": "2026-11-30"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-19", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-19", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.opportunity_validity, DEADLINE_FUTURE)
        self.assertEqual(report.deadline, "2026-11-30")

    def test_case_20_deadline_reached_today(self) -> None:
        candidate = {
            "candidateId": "c20",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-20",
            "proposed": {"title": "Dev", "deadline": "2026-11-17"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-20", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-20", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.opportunity_validity, DEADLINE_REACHED)

    def test_case_21_expired_deadline(self) -> None:
        candidate = {
            "candidateId": "c21",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-21",
            "proposed": {"title": "Dev", "deadline": "2026-11-10"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-21", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-21", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.opportunity_validity, DEADLINE_EXPIRED)
        self.assertTrue(any("Oportunidad vencida por fecha límite" in w for w in report.warnings))

    def test_case_22_missing_deadline(self) -> None:
        candidate = {
            "candidateId": "c22",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-22",
            "proposed": {"title": "Dev", "deadline": None},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-22", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.opportunity_validity, DEADLINE_UNKNOWN)
        self.assertIsNone(report.deadline)

    def test_case_23_invalid_deadline_format(self) -> None:
        candidate = {
            "candidateId": "c23",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-23",
            "proposed": {"title": "Dev", "deadline": "17/11/2026"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-23", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-23", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of=self.as_of, source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertEqual(report.opportunity_validity, DEADLINE_INVALID)

    def test_case_24_timezone_offset_no_drift(self) -> None:
        # 23:30 Lima time on Nov 17 is 04:30 UTC Nov 18.
        # Lima date is Nov 17; compared with as_of="2026-11-17", age must be 0, not -1.
        candidate = {
            "candidateId": "c24",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-24",
            "proposed": {"title": "Dev", "deadline": "2026-11-17"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-24", "observedAt": "2026-11-17T23:30:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-24", "observedAt": "2026-11-17T23:30:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.field_evaluations[0].age_days, 0)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(report.opportunity_validity, DEADLINE_REACHED)

    def test_case_25_fresh_evidence_expired_deadline_separation(self) -> None:
        """Verifies clear separation: fresh evidence does NOT make an expired deadline valid."""
        candidate = {
            "candidateId": "c25",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-25",
            "proposed": {"title": "Dev", "deadline": "2026-11-10"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-25", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-25", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(report.opportunity_validity, DEADLINE_EXPIRED)
        self.assertIn("vencida el 2026-11-10", report.explanation)

    def test_case_26_future_deadline_stale_evidence_separation(self) -> None:
        """Verifies clear separation: a future deadline does NOT excuse stale evidence."""
        candidate = {
            "candidateId": "c26",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-26",
            "proposed": {"title": "Dev", "deadline": "2026-12-31"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-26", "observedAt": "2026-11-01T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-26", "observedAt": "2026-11-01T10:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.freshness_summary, SUMMARY_ALL_STALE)
        self.assertEqual(report.opportunity_validity, DEADLINE_FUTURE)
        self.assertIn("fuera del TTL editorial", report.explanation)


class TestIntegrityDimension(unittest.TestCase):
    """Detailed unit tests for Dimension 4: Candidate Structure & Resilience."""

    def setUp(self) -> None:
        self.source = {
            "id": "src-test",
            "decision": "approved",
            "allowedHosts": ["careers.test.org"],
            "verificationTtlDays": 7,
        }

    def test_case_27_empty_proposed(self) -> None:
        candidate = {
            "candidateId": "c27",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-27",
            "proposed": {},
            "fieldEvidence": [],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_VALID)
        self.assertEqual(report.freshness_summary, SUMMARY_NO_EVIDENCE)
        self.assertEqual(report.opportunity_validity, DEADLINE_UNKNOWN)

    def test_case_28_multiple_evidences_single_field(self) -> None:
        candidate = {
            "candidateId": "c28",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-28",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-28a", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "title", "url": "https://careers.test.org/job-28b", "observedAt": "2026-11-16T11:00:00-05:00"},
            ],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_VALID)
        self.assertEqual(len(report.field_evaluations), 2)
        self.assertTrue(any("múltiples evidencias asociadas" in w for w in report.warnings))

    def test_case_29_optional_fields_null_no_evidence(self) -> None:
        candidate = {
            "candidateId": "c29",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-29",
            "proposed": {"title": "Dev", "salary": None, "benefits": None, "requirements": ""},
            "fieldEvidence": [{"field": "title", "url": "https://careers.test.org/job-29", "observedAt": "2026-11-16T10:00:00-05:00"}],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_VALID)
        self.assertEqual(len(report.errors), 0)

    def test_case_30_malformed_candidate_types(self) -> None:
        candidate = {
            "candidateId": "c30",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-30",
            "proposed": "not-a-dict",
            "fieldEvidence": "not-a-list",
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=self.source)
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertTrue(len(report.errors) > 0)

    def test_candidate_not_dict(self) -> None:
        report = verify_candidate_evidence("not-a-dict", as_of="2026-11-17", source=self.source)  # type: ignore[arg-type]
        self.assertEqual(report.structural_status, STRUCTURAL_INVALID)
        self.assertIn("El candidato debe ser un diccionario", report.errors)


class TestEvidenceVerificationIntegration(unittest.TestCase):
    """Integration, immutability, batch processing, and CLI tests."""

    def test_immutability_of_candidate_inputs(self) -> None:
        candidate = {
            "candidateId": "c-immut",
            "sourceId": "src-test",
            "sourceUrl": "https://careers.test.org/job-immut",
            "proposed": {"title": "Dev", "deadline": "2026-11-20"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-immut", "observedAt": "2026-11-16T10:00:00-05:00"},
                {"field": "deadline", "url": "https://careers.test.org/job-immut", "observedAt": "2026-11-16T10:00:00-05:00"},
            ],
        }
        candidate_copy = copy.deepcopy(candidate)
        verify_candidate_evidence(candidate, as_of="2026-11-17")
        self.assertEqual(candidate, candidate_copy, "verify_candidate_evidence no debe mutar el objeto candidato")

    def test_source_pending_review_provenance(self) -> None:
        source_pending = {
            "id": "src-pend",
            "decision": "pending_review",
            "allowedHosts": ["careers.test.org"],
            "verificationTtlDays": 7,
        }
        candidate = {
            "candidateId": "c-pend",
            "sourceId": "src-pend",
            "sourceUrl": "https://careers.test.org/job-pend",
            "proposed": {"title": "Dev"},
            "fieldEvidence": [
                {"field": "title", "url": "https://careers.test.org/job-pend", "observedAt": "2026-11-16T10:00:00-05:00"}
            ],
        }
        report = verify_candidate_evidence(candidate, as_of="2026-11-17", source=source_pending)
        self.assertEqual(report.provenance_summary, SOURCE_PENDING)
        self.assertTrue(any("pending_review" in w for w in report.warnings))

    def test_batch_verify_candidates_evidence(self) -> None:
        sources_payload = {
            "sources": [
                {
                    "id": "src-bcp",
                    "decision": "approved",
                    "allowedHosts": ["jobs.bcp.com.pe"],
                    "verificationTtlDays": 7,
                }
            ]
        }
        candidates = [
            {
                "candidateId": "c1",
                "sourceId": "src-bcp",
                "sourceUrl": "https://jobs.bcp.com.pe/job1",
                "proposed": {"title": "Dev"},
                "fieldEvidence": [{"field": "title", "url": "https://jobs.bcp.com.pe/job1", "observedAt": "2026-11-16T10:00:00-05:00"}],
            },
            {
                "candidateId": "c2",
                "sourceId": "src-bcp",
                "sourceUrl": "https://jobs.bcp.com.pe/job2",
                "proposed": {"title": "Dev"},
                "fieldEvidence": [{"field": "title", "url": "https://jobs.bcp.com.pe/job2", "observedAt": "2026-11-01T10:00:00-05:00"}],
            },
        ]
        reports = verify_candidates_evidence(candidates, as_of="2026-11-17", sources=sources_payload)
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].freshness_summary, SUMMARY_ALL_FRESH)
        self.assertEqual(reports[1].freshness_summary, SUMMARY_ALL_STALE)

    def test_candidate_evidence_report_serialization(self) -> None:
        report = CandidateEvidenceReport(
            candidate_id="c-test",
            source_id="s-test",
            as_of="2026-11-17",
            ttl_days=7,
            structural_status=STRUCTURAL_VALID,
            provenance_summary=PROVENANCE_VALID,
            freshness_summary=SUMMARY_ALL_FRESH,
            opportunity_validity=DEADLINE_FUTURE,
            deadline="2026-11-30",
            field_evaluations=(
                FieldEvidenceEvaluation(
                    field="title",
                    url="https://example.com/job",
                    url_status="URL_STRUCTURE_VALID",
                    provenance_status=PROVENANCE_ALLOWED,
                    observed_at="2026-11-16T10:00:00-05:00",
                    observed_date="2026-11-16",
                    freshness_status=FRESHNESS_FRESH,
                    age_days=1,
                    is_orphan=False,
                    remote_availability=REMOTE_NOT_CHECKED,
                    notes=(),
                ),
            ),
            errors=(),
            warnings=(),
            affected_fields=(),
            explanation="OK",
            recommended_action="Proceder",
        )
        as_dict = report.to_dict()
        self.assertEqual(as_dict["candidateId"], "c-test")
        self.assertEqual(len(as_dict["fieldEvaluations"]), 1)
        self.assertEqual(as_dict["fieldEvaluations"][0]["field"], "title")
        # Ensure it serializes cleanly to JSON string
        json_str = json.dumps(as_dict)
        self.assertIn('"candidateId": "c-test"', json_str)

    def test_validate_candidates_cli_with_verify_evidence(self) -> None:
        inbox_example = Path(__file__).resolve().parent.parent / "data" / "candidates" / "inbox.example.json"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = validate_candidates_script.main([
                str(inbox_example),
                "--as-of", "2026-11-17",
                "--verify-evidence",
            ])
        output = buffer.getvalue()
        self.assertIn("INFORME DE EVIDENCIAS Y VIGENCIA", output)
        self.assertIn("Candidatos evaluados: 0", output)
        self.assertEqual(exit_code, 0)

    def test_validate_candidates_cli_with_candidate_inbox(self) -> None:
        import tempfile
        test_inbox = {
            "schemaVersion": 1,
            "candidates": [
                {
                    "candidateId": "cand-cli-1",
                    "sourceId": "talento-peru-servir",
                    "sourceUrl": "https://talentoperu.servir.gob.pe/job-1",
                    "capturedAt": "2026-11-16T10:00:00-05:00",
                    "captureMethod": "manual",
                    "editorialReview": {
                        "status": "pending_review"
                    },
                    "proposed": {
                        "title": "Ingeniero Cloud",
                        "deadline": "2026-11-30"
                    },
                    "fieldEvidence": [
                        {"field": "title", "url": "https://talentoperu.servir.gob.pe/job-1", "observedAt": "2026-11-16T10:00:00-05:00"},
                        {"field": "deadline", "url": "https://talentoperu.servir.gob.pe/job-1", "observedAt": "2026-11-16T10:00:00-05:00"}
                    ]
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(test_inbox, tf)
            tf_path = Path(tf.name)

        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = validate_candidates_script.main([
                    str(tf_path),
                    "--as-of", "2026-11-17",
                    "--verify-evidence",
                ])
            output = buffer.getvalue()
            self.assertIn("Candidatos evaluados: 1", output)
            self.assertIn("Frescura: ALL_FRESH", output)
            self.assertIn("Vigencia: DEADLINE_FUTURE", output)
            self.assertEqual(exit_code, 0)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_validate_candidates_cli_with_json_report(self) -> None:
        inbox_example = Path(__file__).resolve().parent.parent / "data" / "candidates" / "inbox.example.json"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = validate_candidates_script.main([
                str(inbox_example),
                "--as-of", "2026-11-17",
                "--json-report",
            ])
        output = buffer.getvalue()
        data = json.loads(output)
        self.assertIn("evidenceReports", data)
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
