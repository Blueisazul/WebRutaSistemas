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

from collector.policy import load_source_registry  # noqa: E402
from validate_candidates import main, validate_payload  # noqa: E402


TODAY = date(2026, 10, 26)
SOURCE_URL = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"


def candidate(**changes):
    value = {
        "candidateId": "CAND-001",
        "sourceId": "talento-peru-servir",
        "sourceUrl": SOURCE_URL,
        "capturedAt": "2026-10-26T12:00:00-05:00",
        "captureMethod": "manual",
        "proposed": {
            "title": None,
            "employer": None,
            "publisher": None,
            "externalReference": None,
            "applyUrl": None,
            "publishedAt": None,
            "deadline": None,
            "location": None,
            "mode": None,
            "opportunityType": None,
            "salary": None,
            "benefits": None,
            "requirements": None,
        },
        "fieldEvidence": [],
        "editorialReview": {
            "status": "pending_review",
            "reviewer": None,
            "reviewedAt": None,
            "decisionNote": None,
        },
    }
    value.update(changes)
    return value


class EditorialCandidateTests(unittest.TestCase):
    def setUp(self):
        self.sources = load_source_registry()

    def test_empty_inbox_example_is_valid(self):
        payload = json.loads((ROOT / "data/candidates/inbox.example.json").read_text(encoding="utf-8"))
        errors, warnings = validate_payload(payload, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_pending_candidate_is_staged_with_warning_not_promoted(self):
        errors, warnings = validate_payload({"schemaVersion": 1, "candidates": [candidate()]}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertTrue(any("fuente pendiente" in warning for warning in warnings))

    def test_pending_source_cannot_be_approved_for_catalog(self):
        proposed = candidate()["proposed"]
        proposed.update({"title": "Puesto de prueba", "employer": "Entidad de prueba", "publisher": "Talento Perú", "applyUrl": "https://empleo.example.test/postular"})
        item = candidate(
            proposed=proposed,
            fieldEvidence=[
                {"field": field, "url": SOURCE_URL if field != "applyUrl" else proposed["applyUrl"], "observedAt": "2026-10-26T12:00:00-05:00"}
                for field in ("title", "employer", "publisher", "applyUrl")
            ],
            editorialReview={"status": "approved_for_catalog", "reviewer": "editor", "reviewedAt": "2026-10-26T13:00:00-05:00", "decisionNote": "Revisión de prueba"},
        )
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=self.sources, today=TODAY)
        self.assertTrue(any("fuente no autorizada" in error for error in errors))

    def test_manual_reuse_can_be_approved_without_automated_ingestion(self):
        sources = json.loads(json.dumps(self.sources))
        source = next(item for item in sources["sources"] if item["id"] == "talento-peru-servir")
        source.update({
            "decision": "approved",
            "manualReviewStatus": "approved",
            "publicReuseStatus": "approved",
            "automatedAccessStatus": "pending_review",
            "rightsReview": "metadata_only_approved",
        })
        proposed = candidate()["proposed"]
        proposed.update({"title": "Puesto de prueba", "employer": "Entidad de prueba", "publisher": "Talento Perú", "applyUrl": "https://empleo.example.test/postular"})
        item = candidate(
            proposed=proposed,
            fieldEvidence=[
                {"field": field, "url": SOURCE_URL if field != "applyUrl" else proposed["applyUrl"], "observedAt": "2026-10-26T12:00:00-05:00"}
                for field in ("title", "employer", "publisher", "applyUrl")
            ],
            editorialReview={"status": "approved_for_catalog", "reviewer": "editor", "reviewedAt": "2026-10-26T13:00:00-05:00", "decisionNote": "Aprobación manual con fuente permitida"},
        )
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_approved_candidate_with_stale_field_evidence_is_blocked(self):
        sources = json.loads(json.dumps(self.sources))
        source = next(item for item in sources["sources"] if item["id"] == "talento-peru-servir")
        source.update({"decision": "approved", "manualReviewStatus": "approved", "publicReuseStatus": "approved", "rightsReview": "metadata_only_approved"})
        proposed = candidate()["proposed"]
        proposed.update({"title": "Puesto de prueba", "employer": "Entidad de prueba", "publisher": "Talento Perú", "applyUrl": "https://empleo.example.test/postular"})
        item = candidate(
            proposed=proposed,
            fieldEvidence=[
                {"field": field, "url": SOURCE_URL if field != "applyUrl" else proposed["applyUrl"], "observedAt": "2026-10-01T12:00:00-05:00"}
                for field in ("title", "employer", "publisher", "applyUrl")
            ],
            editorialReview={"status": "approved_for_catalog", "reviewer": "editor", "reviewedAt": "2026-10-26T13:00:00-05:00", "decisionNote": "Revisión de prueba"},
        )
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=sources, today=TODAY)
        self.assertTrue(any("fuera del TTL" in error for error in errors))

    def test_candidate_cannot_claim_catalog_or_verification_states(self):
        item = candidate(publicationStatus="active", verificationStatus="verified")
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=self.sources, today=TODAY)
        self.assertTrue(any("no puede declarar estados" in error for error in errors))

    def test_incomplete_fields_remain_null_and_warn(self):
        item = candidate()
        errors, warnings = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertIsNone(item["proposed"]["salary"])
        self.assertTrue(any("salary desconocido" in warning for warning in warnings))

    def test_duplicate_candidate_ids_block_inbox(self):
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [candidate(), candidate()]}, sources=self.sources, today=TODAY)
        self.assertTrue(any("ID de candidato duplicado" in error for error in errors))

    def test_http_source_url_and_invalid_date_are_rejected(self):
        item = candidate(sourceUrl="http://www.gob.pe/convocatoria")
        item["proposed"]["deadline"] = "26/10/2026"
        errors, _ = validate_payload({"schemaVersion": 1, "candidates": [item]}, sources=self.sources, today=TODAY)
        self.assertTrue(any("sourceUrl debe ser HTTPS" in error for error in errors))
        self.assertTrue(any("YYYY-MM-DD" in error for error in errors))

    def test_local_validation_does_not_modify_canonical_seed(self):
        seed = ROOT / "data/opportunities.seed.json"
        snapshot = ROOT / "data/opportunities.json"
        before = seed.read_bytes()
        snapshot_before = snapshot.read_bytes()
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            inbox_path = Path(directory) / "inbox.json"
            inbox_path.write_text(json.dumps({"schemaVersion": 1, "candidates": [candidate()]}), encoding="utf-8")
            with patch("sys.stdout"):
                code = main([str(inbox_path)])
        self.assertEqual(code, 0)
        self.assertEqual(seed.read_bytes(), before)
        self.assertEqual(snapshot.read_bytes(), snapshot_before)

    def test_approved_for_catalog_candidate_does_not_publish_automatically(self):
        sources = json.loads(json.dumps(self.sources))
        source = next(item for item in sources["sources"] if item["id"] == "talento-peru-servir")
        source.update({
            "decision": "approved", "manualReviewStatus": "approved", "publicReuseStatus": "approved",
            "automatedAccessStatus": "pending_review", "rightsReview": "metadata_only_approved",
        })
        proposed = candidate()["proposed"]
        proposed.update({
            "title": "Puesto de fixture", "employer": "Empleador de fixture", "publisher": "Talento Perú",
            "applyUrl": "https://www.gob.pe/postular-fixture",
        })
        item = candidate(
            proposed=proposed,
            fieldEvidence=[
                {"field": field, "url": SOURCE_URL, "observedAt": "2026-10-26T12:00:00-05:00"}
                for field in ("title", "employer", "publisher", "applyUrl")
            ],
            editorialReview={
                "status": "approved_for_catalog", "reviewer": "editor-fixture",
                "reviewedAt": "2026-10-26T13:00:00-05:00", "decisionNote": "Fixture de prueba; no es una oferta real.",
            },
        )
        seed = ROOT / "data/opportunities.seed.json"
        snapshot = ROOT / "data/opportunities.json"
        seed_before, snapshot_before = seed.read_bytes(), snapshot.read_bytes()
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            inbox_path = Path(directory) / "approved-inbox.json"
            inbox_path.write_text(json.dumps({"schemaVersion": 1, "candidates": [item]}), encoding="utf-8")
            with patch("validate_candidates.load_source_registry", return_value=sources), patch("sys.stdout"):
                code = main([str(inbox_path)])
        self.assertEqual(code, 0)
        self.assertEqual(seed.read_bytes(), seed_before)
        self.assertEqual(snapshot.read_bytes(), snapshot_before)


if __name__ == "__main__":
    unittest.main()
