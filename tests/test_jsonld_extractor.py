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

from collector.jsonld_extractor import (  # noqa: E402
    extract_candidates_from_html,
    extract_jsonld_scripts,
    find_job_postings,
    parse_jsonld_payloads,
)
from collector.policy import load_source_registry  # noqa: E402
from validate_candidates import main as validate_candidates_main, validate_payload  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "html"
TODAY = date(2026, 11, 17)
SAMPLE_TIMESTAMP = "2026-11-17T12:00:00-05:00"


def load_html_fixture(filename: str) -> str:
    path = FIXTURES_DIR / filename
    return path.read_text(encoding="utf-8")


class JsonLdExtractorTests(unittest.TestCase):
    def setUp(self):
        self.sources = load_source_registry()
        self.servir_source = next(
            s for s in self.sources["sources"] if s["id"] == "talento-peru-servir"
        ).copy()
        self.fisi_source = next(
            s for s in self.sources["sources"] if s["id"] == "unmsm-fisi-employment-board"
        ).copy()

    def test_jobposting_complete_extracts_clean_schema2_candidate(self):
        html = load_html_fixture("jobposting_complete.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c["candidateId"], "CAND-talento-peru-servir-CONV-2026-001")
        self.assertEqual(c["sourceId"], "talento-peru-servir")
        self.assertEqual(c["sourceUrl"], source_url)
        self.assertEqual(c["capturedAt"], SAMPLE_TIMESTAMP)
        self.assertEqual(c["captureMethod"], "manual")
        self.assertEqual(c["editorialReview"]["status"], "pending_review")

        # Proposed fields
        prop = c["proposed"]
        self.assertEqual(prop["title"], "Practicante Profesional de Sistemas e Infraestructura (Sintético)")
        self.assertEqual(prop["employer"], "Entidad Estatal de Prueba")
        self.assertEqual(prop["publisher"], "Entidad Estatal de Prueba")
        self.assertEqual(prop["externalReference"], "CONV-2026-001")
        self.assertEqual(prop["publishedAt"], "2026-10-15")
        self.assertEqual(prop["deadline"], "2026-11-20")
        self.assertEqual(prop["location"], "Av. República de Panamá 1234, San Isidro, Lima, PE")
        self.assertEqual(prop["mode"], "Remoto")  # TELECOMMUTE
        self.assertEqual(prop["opportunityType"], "Prácticas")
        self.assertEqual(prop["salary"], "PEN 1530")
        self.assertEqual(prop["applyUrl"], "https://www.gob.pe/institucion/entidad-prueba/convocatorias/conv-2026-001")

        # Evidence
        evidence_fields = {item["field"] for item in c["fieldEvidence"]}
        for field, value in prop.items():
            if value is not None:
                self.assertIn(field, evidence_fields)
            else:
                self.assertNotIn(field, evidence_fields)

        # Validate with official candidate validator
        errors, warnings = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])
        self.assertTrue(any("fuente pendiente" in w for w in warnings))

    def test_jobposting_missing_optional_does_not_invent_data(self):
        html = load_html_fixture("jobposting_missing_optional.html")
        source_url = "https://sistemas.unmsm.edu.pe/noticias/conv-2026-002"
        candidates = extract_candidates_from_html(
            self.fisi_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertEqual(prop["title"], "Practicante Preprofesional de Soporte (Sintético)")
        self.assertEqual(prop["employer"], "Facultad Universitaria de Prueba")
        self.assertIsNone(prop["publishedAt"])
        self.assertIsNone(prop["deadline"])
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_jobposting_null_values_are_handled_gracefully(self):
        html = load_html_fixture("jobposting_null_values.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["publishedAt"])
        self.assertIsNone(prop["deadline"])
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["mode"])

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_jobposting_list_extracts_all_items(self):
        html = load_html_fixture("jobposting_list.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0]["candidateId"], "CAND-talento-peru-servir-LIST-001")
        self.assertEqual(candidates[1]["candidateId"], "CAND-talento-peru-servir-LIST-002")

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_jobposting_graph_extracts_from_nested_graph(self):
        html = load_html_fixture("jobposting_graph.html")
        source_url = "https://sistemas.unmsm.edu.pe/noticias/convocatoria-ti/"
        candidates = extract_candidates_from_html(
            self.fisi_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c["proposed"]["title"], "Practicante de Laboratorio de Cómputo (Sintético)")
        self.assertEqual(c["proposed"]["employer"], "Laboratorios FISI UNMSM")
        self.assertEqual(c["proposed"]["opportunityType"], "Medio tiempo")
        self.assertEqual(c["proposed"]["location"], "Ciudad Universitaria, Lima")

        errors, _ = validate_payload({"schemaVersion": 1, "candidates": candidates}, sources=self.sources, today=TODAY)
        self.assertEqual(errors, [])

    def test_jobposting_multiple_scripts_extracts_correct_block(self):
        html = load_html_fixture("jobposting_multiple_scripts.html")
        source_url = "https://www.gob.pe/min-tec"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["proposed"]["title"], "Practicante de Gobernanza Digital (Sintético)")

    def test_jobposting_type_array_is_supported(self):
        html = load_html_fixture("jobposting_type_array.html")
        source_url = "https://www.gob.pe/investigacion"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["proposed"]["title"], "Practicante Preprofesional de IA y Ciencia de Datos (Sintético)")

    def test_jobposting_malformed_json_fails_gracefully(self):
        html = load_html_fixture("jobposting_malformed_json.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(candidates, [])

    def test_non_jobposting_is_ignored(self):
        html = load_html_fixture("non_jobposting.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(candidates, [])

    def test_html_without_jsonld_returns_empty(self):
        html = load_html_fixture("html_without_jsonld.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(candidates, [])

    def test_incomplete_metadata_missing_title_is_skipped(self):
        html = load_html_fixture("html_incomplete_metadata.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(candidates, [])

    def test_invalid_urls_omit_apply_url(self):
        html = load_html_fixture("invalid_urls.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0]["proposed"]["applyUrl"])

    def test_invalid_dates_remain_null(self):
        html = load_html_fixture("invalid_dates.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0]["proposed"]["publishedAt"])
        self.assertIsNone(candidates[0]["proposed"]["deadline"])

    def test_unexpected_nested_structure_does_not_crash(self):
        html = load_html_fixture("unexpected_nested_structure.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["location"])

    def test_ambiguous_data_is_not_falsely_normalized(self):
        html = load_html_fixture("ambiguous_data.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        self.assertEqual(len(candidates), 1)
        prop = candidates[0]["proposed"]
        self.assertIsNone(prop["salary"])
        self.assertIsNone(prop["mode"])

    def test_disallowed_source_url_host_fails_closed(self):
        html = load_html_fixture("jobposting_complete.html")
        with self.assertRaisesRegex(ValueError, "source_url_not_allowlisted"):
            extract_candidates_from_html(
                self.servir_source,
                html,
                source_url="https://unauthorized-domain.example.test/convocatoria",
            )

    def test_forbidden_catalog_fields_are_absent(self):
        html = load_html_fixture("jobposting_complete.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        forbidden_fields = ("opportunityStatus", "verificationStatus", "publicationStatus", "lastVerifiedAt")
        for c in candidates:
            for field in forbidden_fields:
                self.assertNotIn(field, c)

    def test_canonical_seed_and_snapshot_remain_unchanged(self):
        seed_path = ROOT / "data" / "opportunities.seed.json"
        snapshot_path = ROOT / "data" / "opportunities.json"
        seed_before = seed_path.read_bytes()
        snapshot_before = snapshot_path.read_bytes()

        html = load_html_fixture("jobposting_complete.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        extract_candidates_from_html(self.servir_source, html, source_url=source_url)

        self.assertEqual(seed_path.read_bytes(), seed_before)
        self.assertEqual(snapshot_path.read_bytes(), snapshot_before)

    def test_local_end_to_end_inbox_integration_via_cli(self):
        html = load_html_fixture("jobposting_complete.html")
        source_url = "https://www.gob.pe/institucion/servir/campanas/4782-talento-peru"
        candidates = extract_candidates_from_html(
            self.servir_source,
            html,
            source_url=source_url,
            captured_at=SAMPLE_TIMESTAMP,
        )

        inbox_payload = {
            "schemaVersion": 1,
            "candidates": candidates,
        }

        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmpdir:
            inbox_file = Path(tmpdir) / "inbox.local.json"
            inbox_file.write_text(json.dumps(inbox_payload, indent=2), encoding="utf-8")

            with patch("sys.stdout"):
                exit_code = validate_candidates_main([str(inbox_file), "--as-of", "2026-11-17"])

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
