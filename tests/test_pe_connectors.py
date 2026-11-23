"""Unit and integration tests for Peruvian sources and connectors (R4-09).

Tests OSITRAN, Defensoría del Pueblo, and HiringRoom (UTP) connectors,
PDF text extraction without third-party libraries, fail-closed policy
compliance, and Candidate Schema 2 normalization.
"""

from __future__ import annotations

import sys
import unittest
import zlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from collector.acquisition_runner import run_pilot_acquisition
from collector.classification import classify_candidate
from collector.pe_connectors import (
    extract_text_from_pdf_bytes,
    transform_defensoria_html,
    transform_hiringroom_html,
    transform_ositran_html,
)
from collector.policy import authorize_fetch, find_source, load_source_registry
from validate_candidates import validate_payload


class TestPeConnectors(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = load_source_registry()
        self.fixtures_dir = ROOT / "tests" / "fixtures" / "ats"

    # =========================================================================
    # 1. Zero-dependency PDF Stream Decompressor
    # =========================================================================

    def test_extract_text_from_pdf_bytes_synthetic(self) -> None:
        """Verifies text extraction from raw uncompressed and zlib-compressed PDF streams."""
        # Uncompressed stream
        raw_stream = b"BT /F1 12 Tf (Ingenieria de Sistemas e Informatica) Tj ET"
        pdf_uncompressed = (
            b"%PDF-1.4\n1 0 obj\n<< /Length 58 >>\nstream\n"
            + raw_stream
            + b"\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        )
        extracted = extract_text_from_pdf_bytes(pdf_uncompressed)
        self.assertIn("Ingenieria de Sistemas e Informatica", extracted)

        # FlateDecode (zlib-compressed) stream
        compressed_stream = zlib.compress(b"BT /F1 12 Tf (Practicas Profesionales TI S/. 1,530.00) Tj ET")
        pdf_compressed = (
            b"%PDF-1.5\n2 0 obj\n<< /Filter /FlateDecode /Length "
            + str(len(compressed_stream)).encode("ascii")
            + b" >>\nstream\n"
            + compressed_stream
            + b"\nendstream\nendobj\ntrailer\n<< /Root 2 0 R >>\n%%EOF"
        )
        extracted_comp = extract_text_from_pdf_bytes(pdf_compressed)
        self.assertIn("Practicas Profesionales TI", extracted_comp)

    # =========================================================================
    # 2. OSITRAN Convocatorias Adapter
    # =========================================================================

    def test_transform_ositran_html_parsing(self) -> None:
        """Verifies parsing of OSITRAN HTML fixture, status detection and Schema 2 fields."""
        source = find_source(self.registry, "ositran-convocatorias")
        self.assertIsNotNone(source, "Fuente ositran-convocatorias debe existir en sources.json")

        fixture_path = self.fixtures_dir / "ositran-convocatorias.html"
        html_content = fixture_path.read_text(encoding="utf-8")

        candidates = transform_ositran_html(
            source,
            html_content,
            captured_at="2026-11-22T20:00:00-05:00",
            include_closed=False,
        )
        
        # Concurso 020 has "Resultados Finales" so it is skipped.
        # Active: 029 (Sistemas), 027 (Sistemas), 028 (Derecho) -> 3 candidates
        self.assertEqual(len(candidates), 3)

        cand_029 = next(c for c in candidates if "029-2026" in c["proposed"]["externalReference"])
        self.assertEqual(cand_029["proposed"]["employer"], "OSITRAN")
        self.assertEqual(cand_029["proposed"]["location"], "Lima, Perú")
        self.assertEqual(cand_029["proposed"]["mode"], "No informado")  # Fail-closed
        self.assertIn("Bases CP_029-2026.pdf", cand_029["sourceUrl"])
        self.assertEqual(cand_029["proposed"]["applyUrl"], "https://oportunidadlaboral.ositran.gob.pe/postular?id=029-2026")

        # Schema 2 validation
        errors, warnings = validate_payload(
            {"schemaVersion": 1, "candidates": [cand_029]},
            sources=self.registry,
            today=date(2026, 11, 22),
        )
        self.assertEqual(errors, [], f"Errores de schema en candidato OSITRAN: {errors}")

        # Classification check
        cls_res = classify_candidate(
            title=cand_029["proposed"]["title"],
            location=cand_029["proposed"]["location"],
            mode=cand_029["proposed"]["mode"],
            employer=cand_029["proposed"]["employer"],
        )
        self.assertEqual(cls_res.relevance, "DIRECT")
        self.assertEqual(cls_res.geographic_eligibility, "PERU_LOCAL")
        self.assertIn(cls_res.experience_tier, ("EGRESADO_BACHILLER", "ENTRY_OR_JUNIOR"))
        self.assertTrue(cls_res.is_staging_eligible)

    # =========================================================================
    # 3. Defensoría del Pueblo CAS Adapter
    # =========================================================================

    def test_transform_defensoria_html_parsing(self) -> None:
        """Verifies parsing of Defensoría del Pueblo CAS HTML table fixture."""
        source = find_source(self.registry, "defensoria-del-pueblo-cas")
        self.assertIsNotNone(source, "Fuente defensoria-del-pueblo-cas debe existir en sources.json")

        fixture_path = self.fixtures_dir / "defensoria-del-pueblo-cas.html"
        html_content = fixture_path.read_text(encoding="utf-8")

        candidates = transform_defensoria_html(
            source,
            html_content,
            captured_at="2026-11-22T20:00:00-05:00",
            include_closed=False,
        )
        
        # CAS 099 has "Resultado Final" so it is skipped.
        # Active: CAS 185, CAS 117, CAS 120 -> 3 candidates
        self.assertEqual(len(candidates), 3)

        cand_185 = next(c for c in candidates if "185-2026" in c["proposed"]["externalReference"])
        self.assertEqual(cand_185["proposed"]["employer"], "Defensoría del Pueblo")
        self.assertEqual(cand_185["proposed"]["location"], "Lima, Perú")
        self.assertEqual(cand_185["proposed"]["mode"], "No informado")  # Fail-closed
        self.assertEqual(cand_185["proposed"]["applyUrl"], "https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php")
        self.assertIn("CAS-185-2026.pdf", cand_185["sourceUrl"])

        # Schema 2 validation
        errors, warnings = validate_payload(
            {"schemaVersion": 1, "candidates": [cand_185]},
            sources=self.registry,
            today=date(2026, 11, 22),
        )
        self.assertEqual(errors, [], f"Errores de schema en candidato Defensoría: {errors}")

        # Classification check: CAS 185 is DIRECT, CAS 120 (Legal) is NOT_RELEVANT
        cls_185 = classify_candidate(
            title=cand_185["proposed"]["title"],
            location=cand_185["proposed"]["location"],
            mode=cand_185["proposed"]["mode"],
            employer=cand_185["proposed"]["employer"],
        )
        self.assertEqual(cls_185.relevance, "DIRECT")
        self.assertTrue(cls_185.is_staging_eligible)

        cand_120 = next(c for c in candidates if "120-2026" in c["proposed"]["externalReference"])
        cls_120 = classify_candidate(
            title=cand_120["proposed"]["title"],
            location=cand_120["proposed"]["location"],
            mode=cand_120["proposed"]["mode"],
            employer=cand_120["proposed"]["employer"],
        )
        self.assertEqual(cls_120.relevance, "NOT_RELEVANT")
        self.assertFalse(cls_120.is_staging_eligible)

    # =========================================================================
    # 4. UTP HiringRoom Campus Adapter
    # =========================================================================

    def test_transform_hiringroom_html_parsing(self) -> None:
        """Verifies JSON-LD Schema.org JobPosting parsing in HiringRoom HTML fixture."""
        source = find_source(self.registry, "utp-hiringroom-campus")
        self.assertIsNotNone(source, "Fuente utp-hiringroom-campus debe existir en sources.json")

        fixture_path = self.fixtures_dir / "utp-hiringroom-campus.html"
        html_content = fixture_path.read_text(encoding="utf-8")

        candidates = transform_hiringroom_html(source, html_content, captured_at="2026-11-22T20:00:00-05:00")
        self.assertEqual(len(candidates), 1)

        c = candidates[0]
        self.assertEqual(c["proposed"]["employer"], "Interbank")
        self.assertEqual(c["proposed"]["title"], "Practicante Pre Profesional de Sistemas y TI")
        self.assertEqual(c["proposed"]["externalReference"], "UTP-HR-2026-001")
        self.assertIn("Lima", c["proposed"]["location"])
        self.assertIn(c["proposed"]["mode"], ("No informado", None))

        # Schema 2 validation
        errors, warnings = validate_payload(
            {"schemaVersion": 1, "candidates": [c]},
            sources=self.registry,
            today=date(2026, 11, 22),
        )
        self.assertEqual(errors, [], f"Errores de schema en candidato HiringRoom: {errors}")

    # =========================================================================
    # 5. Acquisition Runner Integration
    # =========================================================================

    def test_run_pilot_acquisition_with_pe_fixtures(self) -> None:
        """Verifies full runner pipeline (fetch, filter, dedup, validation) using PE fixtures."""
        report = run_pilot_acquisition(
            source_ids=["ositran-convocatorias", "defensoria-del-pueblo-cas", "utp-hiringroom-campus"],
            fixtures_dir=self.fixtures_dir,
            dry_run=True,
        )
        self.assertEqual(report.sources_evaluated, 3)
        self.assertEqual(report.sources_succeeded, 3)
        self.assertEqual(report.sources_failed, 0)
        self.assertTrue(report.validation_passed)
        self.assertEqual(len(report.validation_errors), 0)
        # Should have captured candidates from each source and filtered out non-systems roles
        self.assertGreaterEqual(report.total_captured, 5)
        self.assertGreaterEqual(report.total_filtered, 3)
        self.assertGreaterEqual(report.total_discarded, 2)  # Legal roles discarded

    # =========================================================================
    # 6. Security & Policy Authorization
    # =========================================================================

    def test_pe_sources_policy_authorization(self) -> None:
        """Ensures authorize_fetch approves authorized hosts and rejects untrusted ones."""
        ositran_src = find_source(self.registry, "ositran-convocatorias")
        auth_ok = authorize_fetch(ositran_src, "https://oportunidadlaboral.ositran.gob.pe/convocatoria?nuevo=1", 0)
        self.assertTrue(auth_ok["allowed"])

        auth_bad_host = authorize_fetch(ositran_src, "https://malicious.ositran.gob.pe.evil.com/fake", 0)
        self.assertFalse(auth_bad_host["allowed"])
        self.assertEqual(auth_bad_host["reason"], "host_not_allowlisted")

        auth_http = authorize_fetch(ositran_src, "http://oportunidadlaboral.ositran.gob.pe/convocatoria", 0)
        self.assertFalse(auth_http["allowed"])
        self.assertEqual(auth_http["reason"], "https_required")


if __name__ == "__main__":
    unittest.main()
