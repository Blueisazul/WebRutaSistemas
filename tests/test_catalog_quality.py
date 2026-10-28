from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import date
from pathlib import Path
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from catalog_quality import effective_states, parse_json_text, validate_payload, validate_records  # noqa: E402
from build_catalog import build_payload  # noqa: E402
import build_catalog as catalog_builder  # noqa: E402


TODAY = date(2026, 10, 26)


def active_record(**changes):
    record = {
        "id": "JOB-1",
        "employer": "Example Corp",
        "publisher": "Example Corp",
        "title": "Junior Developer",
        "recordKind": "curated",
        "opportunityStatus": "open",
        "verificationStatus": "verified",
        "publicationStatus": "active",
        "sourceUrl": "https://jobs.example.test/1",
        "applyUrl": "https://jobs.example.test/1/apply",
        "allowedHosts": ["jobs.example.test"],
        "deadline": "2026-10-30",
        "lastVerifiedAt": "2026-10-20T12:00:00-05:00",
        "verificationEvidence": {
            "url": "https://jobs.example.test/1",
            "observedAt": "2026-10-20T12:00:00-05:00",
            "method": "manual",
            "result": "application_open",
            "publisherRelation": "employer_confirmed",
        },
        "editorialDecision": {
            "status": "approved", "reviewer": "editor-1", "decidedAt": "2026-10-20T12:00:00-05:00",
            "reason": "Datos cotejados con la convocatoria y el canal oficial de postulación.",
        },
        "fieldEvidence": [
            {"field": field_name, "url": "https://jobs.example.test/1", "observedAt": "2026-10-20T12:00:00-05:00"}
            for field_name in ("employer", "publisher", "title", "sourceUrl", "applyUrl", "deadline")
        ],
    }
    record.update(changes)
    return record


class CatalogQualityTests(unittest.TestCase):
    def test_future_deadline_and_recent_employer_evidence_can_be_active(self):
        result = validate_records([active_record()], today=TODAY)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(effective_states(active_record(), today=TODAY)["publicationStatus"], "active")

    def test_active_requires_separate_publisher_field_evidence_and_human_decision(self):
        for record in (
            active_record(fieldEvidence=[]),
            active_record(publisher=None),
            active_record(editorialDecision={"status": "pending_review"}),
        ):
            result = validate_records([record], today=TODAY)
            self.assertFalse(result.ok)
            self.assertEqual(effective_states(record, today=TODAY)["publicationStatus"], "unconfirmed")

    def test_demonstration_is_never_active_even_with_complete_evidence(self):
        record = active_record(recordKind="demonstration")
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("demostrativo no puede publicarse activo", " ".join(result.errors))
        self.assertEqual(effective_states(record, today=TODAY)["publicationStatus"], "unconfirmed")

    def test_supplied_salary_without_field_evidence_blocks_active(self):
        record = active_record(salary="S/ 2,000")
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("evidencia reciente por campo", " ".join(result.errors))

    def test_withdrawal_or_rejection_requires_reason(self):
        record = active_record(publicationStatus="historical", editorialDecision={"status": "withdrawn"})
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("reason es obligatorio", " ".join(result.errors))

    def test_field_evidence_url_and_timestamp_are_validated(self):
        record = active_record(fieldEvidence=[{"field": "salary", "url": "http://jobs.example.test/1", "observedAt": "2026-10-20T12:00:00-05:00"}])
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("debe ser HTTPS en un host permitido", " ".join(result.errors))

    def test_stale_field_evidence_blocks_current_publication(self):
        record = active_record(fieldEvidence=[
            {"field": "employer", "url": "https://jobs.example.test/1", "observedAt": "2026-10-18T12:00:00-05:00"},
        ])
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertEqual(effective_states(record, today=TODAY)["publicationStatus"], "unconfirmed")

    def test_past_deadline_blocks_active_even_if_employment_end_is_future(self):
        record = active_record(deadline="2026-10-25", employmentEndDate="2026-12-31")
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("fecha límite pasada", " ".join(result.errors))
        self.assertEqual(effective_states(record, today=TODAY)["opportunityStatus"], "expired")

    def test_missing_deadline_is_not_inferred_but_ttl_still_bounds_active_state(self):
        record = active_record(deadline=None)
        self.assertTrue(validate_records([record], today=TODAY).ok)
        old = active_record(deadline=None, lastVerifiedAt="2026-10-18T12:00:00-05:00")
        self.assertEqual(effective_states(old, today=TODAY)["verificationStatus"], "stale")
        self.assertEqual(effective_states(old, today=TODAY)["publicationStatus"], "unconfirmed")

    def test_verification_ttl_boundary(self):
        inside = active_record(lastVerifiedAt="2026-10-19T23:59:59-05:00")
        outside = active_record(lastVerifiedAt="2026-10-18T23:59:59-05:00")
        self.assertEqual(effective_states(inside, today=TODAY)["verificationStatus"], "verified")
        self.assertEqual(effective_states(outside, today=TODAY)["verificationStatus"], "stale")

    def test_past_deadline_does_not_override_known_closed_state(self):
        record = active_record(opportunityStatus="closed", publicationStatus="historical", deadline="2026-10-25")
        self.assertEqual(effective_states(record, today=TODAY)["opportunityStatus"], "closed")

    def test_timezone_is_required_and_normalized(self):
        record = active_record(lastVerifiedAt="2026-10-20T12:00:00")
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)
        self.assertIn("debe incluir zona horaria", " ".join(result.errors))

    def test_secondary_or_unverified_source_cannot_be_active(self):
        record = active_record(verificationStatus="unverified", verificationEvidence=None)
        result = validate_records([record], today=TODAY)
        self.assertFalse(result.ok)

    def test_duplicate_ids_block_publication(self):
        result = validate_records([active_record(), active_record()], today=TODAY)
        self.assertIn("ID duplicado", " ".join(result.errors))

    def test_http_and_non_allowlisted_hosts_are_rejected(self):
        for record in (
            active_record(sourceUrl="http://jobs.example.test/1"),
            active_record(applyUrl="https://apply.other.test/1"),
            active_record(allowedHosts=["other.test"]),
        ):
            self.assertFalse(validate_records([record], today=TODAY).ok)

    def test_malformed_json_is_not_accepted(self):
        with self.assertRaisesRegex(ValueError, "JSON malformado"):
            parse_json_text('{"opportunities": [}')

    def test_empty_catalog_requires_explicit_mode(self):
        self.assertFalse(validate_records([], today=TODAY).ok)
        self.assertTrue(validate_records([], today=TODAY, allow_empty=True).ok)

    def test_historical_entry_is_retained_without_active_cta_semantics(self):
        record = active_record(
            recordKind="demonstration", opportunityStatus="closed",
            verificationStatus="unverified", publicationStatus="historical",
            lastVerifiedAt=None, verificationEvidence=None,
        )
        result = validate_records([record], today=TODAY)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(effective_states(record, today=TODAY)["publicationStatus"], "historical")

    def test_source_failure_does_not_change_catalog_fixture(self):
        from collector.refresh_catalog import CATALOG_PATH, refresh

        before = CATALOG_PATH.read_bytes()
        # Collection failures are fail-closed in collector.refresh_catalog; this
        # asserts they stop before any read/modify/write of the public snapshot.
        with patch("collector.refresh_catalog.load_source_registry", return_value={"sources": [{"id": "test", "enabled": True}]}):
            with self.assertRaisesRegex(RuntimeError, "Ingesta automática bloqueada"):
                refresh()
        after = CATALOG_PATH.read_bytes()
        self.assertEqual(before, after)

    def test_recent_generation_does_not_refresh_old_verification(self):
        record = active_record(lastVerifiedAt="2026-10-01T12:00:00-05:00")
        payload = {
            "schemaVersion": 2,
            "generatedAt": "2026-10-26T12:00:00Z",
            "verificationTtlDays": 7,
            "timezone": "America/Lima",
            "sourceNote": "test",
            "opportunities": [record],
        }
        result = validate_payload(payload, today=TODAY)
        self.assertFalse(result.ok)
        self.assertEqual(effective_states(record, today=TODAY)["publicationStatus"], "unconfirmed")

    def test_generator_refuses_to_drop_prior_records(self):
        with self.assertRaisesRegex(ValueError, "perdería registros previos"):
            build_payload(
                {"schemaVersion": 2, "opportunities": [active_record()]},
                {"opportunities": [{"id": "OLD-2"}]},
                "2026-10-26T00:00:00Z",
                today=TODAY,
            )

    def test_build_check_mode_is_read_only(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            seed_path = Path(directory) / "seed.json"
            snapshot_path = Path(directory) / "snapshot.json"
            seed_path.write_bytes((ROOT / "data/opportunities.seed.json").read_bytes())
            snapshot_path.write_bytes((ROOT / "data/opportunities.json").read_bytes())
            before_seed, before_snapshot = seed_path.read_bytes(), snapshot_path.read_bytes()
            with patch.object(catalog_builder, "SEED_PATH", seed_path), patch.object(catalog_builder, "OUTPUT_PATH", snapshot_path), patch("sys.stdout"):
                result = catalog_builder.main(["--check"])
            self.assertEqual(result, 0)
            self.assertEqual(seed_path.read_bytes(), before_seed)
            self.assertEqual(snapshot_path.read_bytes(), before_snapshot)

    def test_inaccessible_source_and_redirect_fail_closed(self):
        from collector import ats_connectors

        with patch("collector.ats_connectors.build_opener") as make_opener:
            make_opener.return_value.open.side_effect = URLError("offline")
            with self.assertRaisesRegex(ValueError, "source_network_error"):
                ats_connectors._fetch_json("https://jobs.example.test/api")
        with patch("collector.ats_connectors.build_opener") as make_opener:
            make_opener.return_value.open.side_effect = HTTPError("https://jobs.example.test", 302, "redirect", {}, None)
            with self.assertRaisesRegex(ValueError, "redirect_requires_explicit_source_review"):
                ats_connectors._fetch_json("https://jobs.example.test/api")


if __name__ == "__main__":
    unittest.main()
