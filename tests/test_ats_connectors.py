from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from collector.ats_connectors import (  # noqa: E402
    fetch_greenhouse_board,
    fetch_lever_board,
    transform_greenhouse_payload,
    transform_lever_payload,
)
from collector.policy import load_source_registry  # noqa: E402
from validate_candidates import main as validate_candidates_main, validate_payload  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "ats"
TODAY = date(2026, 11, 17)
SAMPLE_TIMESTAMP = "2026-11-17T12:00:00-05:00"


def load_fixture(filename: str) -> dict | list:
    path = FIXTURES_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


class AtsConnectorsSchema2Tests(unittest.TestCase):
    def setUp(self):
        self.sources = load_source_registry()
        self.greenhouse_source = next(
            s for s in self.sources["sources"] if s["id"] == "greenhouse-public-job-board-template"
        ).copy()
        self.greenhouse_source.update({
            "boardToken": "empresa-ficticia",
            "employer": "Empresa Ficticia Tech",
            "publisher": "Greenhouse Job Board",
        })

        self.lever_source = next(
            s for s in self.sources["sources"] if s["id"] == "lever-public-postings-template"
        ).copy()
        self.lever_source.update({
            "site": "empresa-ficticia",
            "employer": "Empresa Ficticia Tech",
            "publisher": "Lever Postings",
        })

    def test_greenhouse_complete_produces_valid_schema2_candidates(self):
        payload = load_fixture("greenhouse_complete.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 2)

        first = candidates[0]
        self.assertEqual(first["candidateId"], "CAND-greenhouse-public-job-board-template-990101")
        self.assertEqual(first["sourceId"], "greenhouse-public-job-board-template")
        self.assertEqual(first["sourceUrl"], "https://boards-api.greenhouse.io/v1/boards/empresa-ficticia/jobs")
        self.assertEqual(first["capturedAt"], SAMPLE_TIMESTAMP)
        self.assertEqual(first["captureMethod"], "manual")
        self.assertEqual(first["editorialReview"]["status"], "pending_review")

        # Proposed fields
        prop = first["proposed"]
        self.assertEqual(prop["title"], "Practicante Preprofesional de Desarrollo Backend (Sintético)")
        self.assertEqual(prop["employer"], "Empresa Ficticia Tech")
        self.assertEqual(prop["publisher"], "Greenhouse Job Board")
        self.assertEqual(prop["externalReference"], "990101")
        self.assertEqual(prop["applyUrl"], "https://boards.greenhouse.io/empresa-ficticia/jobs/990101")
        self.assertEqual(prop["location"], "Lima, Perú")
        self.assertIsNone(prop["mode"])  # Not inferred from local city name
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["deadline"])
        self.assertIsNone(prop["benefits"])
        self.assertIsNone(prop["requirements"])

        # Second job has location "Remote" -> mode "Remoto"
        second = candidates[1]
        self.assertEqual(second["proposed"]["location"], "Remote")
        self.assertEqual(second["proposed"]["mode"], "Remoto")

        # Field evidence
        evidence_fields = {item["field"] for item in first["fieldEvidence"]}
        for field, value in prop.items():
            if value is not None:
                self.assertIn(field, evidence_fields)
            else:
                self.assertNotIn(field, evidence_fields)

        # Validate with official candidate validator
        inbox_payload = {"schemaVersion": 1, "candidates": candidates}
        errors, warnings = validate_payload(inbox_payload, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertTrue(any("fuente pendiente" in w for w in warnings))

    def test_greenhouse_missing_optional_does_not_invent_data(self):
        payload = load_fixture("greenhouse_missing_optional.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["publishedAt"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_greenhouse_null_values_are_handled_gracefully(self):
        payload = load_fixture("greenhouse_null_values.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_greenhouse_invalid_and_insecure_urls_are_skipped(self):
        payload = load_fixture("greenhouse_invalid_urls.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 0)

    def test_greenhouse_missing_identifiers_are_skipped(self):
        payload = load_fixture("greenhouse_missing_id.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 0)

    def test_greenhouse_duplicate_jobs_in_batch_are_deduplicated(self):
        payload = load_fixture("greenhouse_duplicates.json")
        candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)

    def test_greenhouse_malformed_shape_raises_error(self):
        payload = load_fixture("greenhouse_malformed.json")
        with self.assertRaisesRegex(ValueError, "greenhouse_unexpected_response_shape"):
            transform_greenhouse_payload(self.greenhouse_source, payload)

    def test_lever_complete_produces_valid_schema2_candidates(self):
        payload = load_fixture("lever_complete.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 2)

        first = candidates[0]
        self.assertEqual(first["candidateId"], "CAND-lever-public-postings-template-lev-uuid-990201")
        self.assertEqual(first["sourceId"], "lever-public-postings-template")
        self.assertEqual(first["sourceUrl"], "https://api.lever.co/v0/postings/empresa-ficticia?mode=json")
        self.assertEqual(first["capturedAt"], SAMPLE_TIMESTAMP)
        self.assertEqual(first["captureMethod"], "manual")
        self.assertEqual(first["editorialReview"]["status"], "pending_review")

        # Proposed fields
        prop = first["proposed"]
        self.assertEqual(prop["title"], "Practicante Preprofesional de DevOps (Sintético)")
        self.assertEqual(prop["employer"], "Empresa Ficticia Tech")
        self.assertEqual(prop["publisher"], "Lever Postings")
        self.assertEqual(prop["externalReference"], "lev-uuid-990201")
        self.assertEqual(prop["applyUrl"], "https://jobs.lever.co/empresa-ficticia/lev-uuid-990201/apply")
        self.assertEqual(prop["location"], "Lima, Perú")
        self.assertEqual(prop["mode"], "Híbrido")
        self.assertEqual(prop["opportunityType"], "Prácticas")
        self.assertEqual(prop["publishedAt"], "2024-10-26")
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["deadline"])

        # Second job has remote mode
        second = candidates[1]
        self.assertEqual(second["proposed"]["mode"], "Remoto")
        self.assertEqual(second["proposed"]["opportunityType"], "Tiempo completo")

        # Field evidence
        evidence_fields = {item["field"] for item in first["fieldEvidence"]}
        for field, value in prop.items():
            if value is not None:
                self.assertIn(field, evidence_fields)
            else:
                self.assertNotIn(field, evidence_fields)

        # Validate with official candidate validator
        inbox_payload = {"schemaVersion": 1, "candidates": candidates}
        errors, warnings = validate_payload(inbox_payload, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertTrue(any("fuente pendiente" in w for w in warnings))

    def test_lever_missing_optional_does_not_invent_data(self):
        payload = load_fixture("lever_missing_optional.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])
        self.assertIsNone(prop["opportunityType"])
        self.assertIsNone(prop["publishedAt"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_lever_null_values_are_handled_gracefully(self):
        payload = load_fixture("lever_null_values.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])
        self.assertIsNone(prop["publishedAt"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_lever_invalid_dates_remain_null(self):
        payload = load_fixture("lever_invalid_dates.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 3)
        for c in candidates:
            self.assertIsNone(c["proposed"]["publishedAt"])

    def test_lever_invalid_urls_are_skipped(self):
        payload = load_fixture("lever_invalid_urls.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 0)

    def test_lever_duplicate_postings_are_deduplicated(self):
        payload = load_fixture("lever_duplicates.json")
        candidates = transform_lever_payload(
            self.lever_source,
            payload,
            captured_at=SAMPLE_TIMESTAMP,
        )
        self.assertEqual(len(candidates), 1)

    def test_lever_malformed_shape_raises_error(self):
        payload = load_fixture("lever_malformed.json")
        with self.assertRaisesRegex(ValueError, "lever_unexpected_response_shape"):
            transform_lever_payload(self.lever_source, payload)

    def test_forbidden_catalog_fields_are_absent(self):
        gh_candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            load_fixture("greenhouse_complete.json"),
            captured_at=SAMPLE_TIMESTAMP,
        )
        lev_candidates = transform_lever_payload(
            self.lever_source,
            load_fixture("lever_complete.json"),
            captured_at=SAMPLE_TIMESTAMP,
        )

        forbidden_fields = ("opportunityStatus", "verificationStatus", "publicationStatus", "lastVerifiedAt")
        for c in gh_candidates + lev_candidates:
            for field in forbidden_fields:
                self.assertNotIn(field, c)

    def test_fetch_functions_fail_closed_without_network_when_unauthorized(self):
        # The registered sources in sources.json have enabled: false, decision: pending_review
        raw_sources = load_source_registry()
        gh_raw = next(s for s in raw_sources["sources"] if s["id"] == "greenhouse-public-job-board-template")
        gh_raw.update({"boardToken": "demo", "employer": "Demo"})

        lev_raw = next(s for s in raw_sources["sources"] if s["id"] == "lever-public-postings-template")
        lev_raw.update({"site": "demo", "employer": "Demo"})

        # Greenhouse fetch fails closed immediately on policy
        with self.assertRaisesRegex(ValueError, "source_policy_source_disabled"):
            fetch_greenhouse_board(gh_raw, request_count=0)

        # Lever fetch fails closed immediately on policy
        with self.assertRaisesRegex(ValueError, "source_policy_source_disabled"):
            fetch_lever_board(lev_raw, request_count=0)

    def test_canonical_seed_and_snapshot_remain_unchanged(self):
        seed_path = ROOT / "data" / "opportunities.seed.json"
        snapshot_path = ROOT / "data" / "opportunities.json"
        seed_before = seed_path.read_bytes()
        snapshot_before = snapshot_path.read_bytes()

        # Run transformations multiple times
        transform_greenhouse_payload(self.greenhouse_source, load_fixture("greenhouse_complete.json"))
        transform_lever_payload(self.lever_source, load_fixture("lever_complete.json"))

        self.assertEqual(seed_path.read_bytes(), seed_before)
        self.assertEqual(snapshot_path.read_bytes(), snapshot_before)

    def test_local_end_to_end_inbox_integration_via_cli(self):
        gh_candidates = transform_greenhouse_payload(
            self.greenhouse_source,
            load_fixture("greenhouse_complete.json"),
            captured_at=SAMPLE_TIMESTAMP,
        )
        lev_candidates = transform_lever_payload(
            self.lever_source,
            load_fixture("lever_complete.json"),
            captured_at=SAMPLE_TIMESTAMP,
        )

        all_candidates = gh_candidates + lev_candidates
        inbox_payload = {
            "schemaVersion": 1,
            "candidates": all_candidates,
        }

        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmpdir:
            inbox_file = Path(tmpdir) / "inbox.local.json"
            inbox_file.write_text(json.dumps(inbox_payload, indent=2), encoding="utf-8")

            with patch("sys.stdout"):
                exit_code = validate_candidates_main([str(inbox_file), "--as-of", "2026-11-17"])

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
