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

from collector.acquisition_runner import _atomic_write_json, run_pilot_acquisition, SEED_CATALOG_PATH, SNAPSHOT_CATALOG_PATH
from collector.classification import classify_candidate
from collector.dedup import deduplicate_candidates
from collector.pe_connectors import (
    extract_text_from_pdf_bytes,
    transform_defensoria_html,
    transform_gobpe_indecopi_html,
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

    def test_transform_corporate_hiringroom_fixtures(self) -> None:
        """Verifies OpenGraph and DOM parsing for corporate HiringRoom private tech employers (R5-03)."""
        test_cases = [
            (
                "stefanini-hiringroom",
                "stefanini-hiringroom.html",
                "CAND-stefanini-hiringroom-66984666bb7169324800e116",
                "Analista Programador .NET / AWS - Remoto",
                "Stefanini IT Solutions Perú S.A.C.",
                "Surquillo, Lima, Perú",
                "Remoto",
            ),
            (
                "canvia-hiringroom",
                "canvia-hiringroom.html",
                "CAND-canvia-hiringroom-6b049ed15603062d6c332355",
                "Administrador de Sistemas Linux / Unix",
                "Canvia",
                "Lima, Perú",
                "Híbrido",
            ),
            (
                "myapps-hiringroom",
                "myapps-hiringroom.html",
                "CAND-myapps-hiringroom-6aedfa885603062d6c332356",
                "Desarrollador(a) Full Stack con IA",
                "MyApps Soluciones S.A.C.",
                "San Isidro, Lima, Perú",
                "Presencial",
            ),
            (
                "efitec-hiringroom",
                "efitec-hiringroom.html",
                "CAND-efitec-hiringroom-6b0638a75603062d6c332357",
                "Especialista Senior BD y Cloud AWS",
                "Efitec Corporation S.A.C.",
                "Lima, Perú",
                "Híbrido",
            ),
        ]

        for s_id, fixture_name, expected_id, expected_title, expected_emp, expected_loc, expected_mode in test_cases:
            source = find_source(self.registry, s_id)
            self.assertIsNotNone(source, f"Fuente {s_id} debe existir en sources.json")

            fixture_path = self.fixtures_dir / fixture_name
            html_content = fixture_path.read_text(encoding="utf-8")

            candidates = transform_hiringroom_html(
                source,
                html_content,
                source_url=source.get("officialUrl"),
                captured_at="2026-11-24T20:00:00-05:00",
            )
            self.assertEqual(len(candidates), 1, f"Debe extraer 1 candidato de {fixture_name}")

            cand = candidates[0]
            self.assertEqual(cand["candidateId"], expected_id)
            self.assertEqual(cand["proposed"]["title"], expected_title)
            self.assertEqual(cand["proposed"]["employer"], expected_emp)
            self.assertEqual(cand["proposed"]["location"], expected_loc)
            self.assertEqual(cand["proposed"]["mode"], expected_mode)
            self.assertEqual(cand["proposed"]["opportunityType"], "Empleo")

            # Validate Candidate Schema 2
            errors, warnings = validate_payload(
                {"schemaVersion": 1, "candidates": [cand]},
                sources=self.registry,
                today=date(2026, 11, 24),
            )
            self.assertEqual(errors, [], f"Errores de schema en candidato {s_id}: {errors}")

            # Verify classification
            cls = classify_candidate(
                title=cand["proposed"]["title"],
                location=cand["proposed"]["location"],
                mode=cand["proposed"]["mode"],
                employer=cand["proposed"]["employer"],
            )
            self.assertEqual(cls.relevance, "DIRECT", f"Candidato {s_id} debe ser relevante DIRECT")
            self.assertTrue(cls.is_staging_eligible, f"Candidato {s_id} debe ser elegible para staging")

    # =========================================================================
    # 4B. Gob.pe Convocatorias Adapter (INDECOPI & State Entities - R5-01)
    # =========================================================================

    def test_transform_gobpe_indecopi_html_parsing(self) -> None:
        """Verifies parsing of Gob.pe / INDECOPI HTML table fixture and Schema 2 fields."""
        source = find_source(self.registry, "gobpe-indecopi-convocatorias")
        self.assertIsNotNone(source, "Fuente gobpe-indecopi-convocatorias debe existir en sources.json")

        fixture_path = self.fixtures_dir / "gobpe-indecopi-convocatorias.html"
        html_content = fixture_path.read_text(encoding="utf-8")

        candidates = transform_gobpe_indecopi_html(
            source,
            html_content,
            captured_at="2026-11-24T14:00:00-05:00",
            include_closed=False,
        )

        # In fixture: 7 rows total. 135-2025 is FINALIZADA so it is skipped.
        # Remaining: 033-2026, 290-2025, 277-2025, 291-2025, 092-2026, 180-2026 -> 6 candidates
        self.assertEqual(len(candidates), 6)

        # Check CAS tech opportunity (033-2026)
        cand_033 = next(c for c in candidates if "033-2026" in c["proposed"]["externalReference"])
        self.assertEqual(cand_033["proposed"]["employer"], "INDECOPI")
        self.assertEqual(cand_033["proposed"]["location"], "Lima, Perú")
        self.assertEqual(cand_033["proposed"]["mode"], "No informado")
        self.assertEqual(cand_033["proposed"]["opportunityType"], "Contratación Administrativa de Servicios (CAS)")
        self.assertEqual(cand_033["proposed"]["deadline"], "2026-12-10")
        self.assertIn("7645090", cand_033["sourceUrl"])
        self.assertEqual(cand_033["proposed"]["applyUrl"], "https://oportunidadeslaborales.indecopi.gob.pe/")

        # Check Prácticas opportunity (092-2026)
        cand_092 = next(c for c in candidates if "092-2026" in c["proposed"]["externalReference"])
        self.assertEqual(cand_092["proposed"]["opportunityType"], "Prácticas")
        self.assertEqual(cand_092["proposed"]["deadline"], "2026-12-01")
        self.assertIn("8797503", cand_092["sourceUrl"])

        # Validate Candidate Schema 2
        errors, warnings = validate_payload(
            {"schemaVersion": 1, "candidates": candidates},
            sources=self.registry,
            today=date(2026, 11, 24),
        )
        self.assertEqual(errors, [], f"Errores de schema en candidatos Gob.pe: {errors}")

        # Classification verification
        # 033-2026 (Analista de Help Desk) -> DIRECT
        cls_033 = classify_candidate(
            title=cand_033["proposed"]["title"],
            location=cand_033["proposed"]["location"],
            mode=cand_033["proposed"]["mode"],
            employer=cand_033["proposed"]["employer"],
        )
        self.assertEqual(cls_033.relevance, "DIRECT")
        self.assertTrue(cls_033.is_staging_eligible)

        # 180-2026 (Auxiliar Legal) -> NOT_RELEVANT
        cand_180 = next(c for c in candidates if "180-2026" in c["proposed"]["externalReference"])
        cls_180 = classify_candidate(
            title=cand_180["proposed"]["title"],
            location=cand_180["proposed"]["location"],
            mode=cand_180["proposed"]["mode"],
            employer=cand_180["proposed"]["employer"],
        )
        self.assertEqual(cls_180.relevance, "NOT_RELEVANT")
        self.assertFalse(cls_180.is_staging_eligible)

    def test_gobpe_indecopi_with_pdf_extraction(self) -> None:
        """Verifies detail page and PDF bases text extraction for Gob.pe Indecopi."""
        source = find_source(self.registry, "gobpe-indecopi-convocatorias")
        self.assertIsNotNone(source)

        fixture_path = self.fixtures_dir / "gobpe-indecopi-convocatorias.html"
        html_content = fixture_path.read_text(encoding="utf-8")

        mock_gobpe_detail = """
        <html><body>
          <h1>Convocatoria CAS 033-2026</h1>
          <a href="https://cdn.www.gob.pe/uploads/document/file/9321764/7645090-cas-033-2025-informacion-general-y-perfil.pdf">Bases</a>
        </body></html>
        """
        mock_pdf_text = "Contratar los servicios de un ANALISTA DE SISTEMAS. Remuneracion mensual S/. 3,000.00. Perfil: Bachiller en Ingenieria de Sistemas."

        candidates = transform_gobpe_indecopi_html(
            source,
            html_content,
            captured_at="2026-11-24T14:00:00-05:00",
            detail_fetcher=lambda url: mock_gobpe_detail,
            pdf_fetcher=lambda url: mock_pdf_text,
            include_closed=False,
        )

        cand_033 = next(c for c in candidates if "033-2026" in c["proposed"]["externalReference"])
        self.assertEqual(cand_033["proposed"]["salary"], "S/.3,000.00")
        self.assertIn("Bachiller en Ingenieria de Sistemas", cand_033["proposed"]["requirements"])
        self.assertIn("7645090-cas-033-2025-informacion-general-y-perfil.pdf", cand_033["sourceUrl"])

    # =========================================================================
    # 5. Acquisition Runner Integration
    # =========================================================================

    def test_run_pilot_acquisition_with_pe_fixtures(self) -> None:
        """Verifies full runner pipeline (fetch, filter, dedup, validation) using PE fixtures."""
        report = run_pilot_acquisition(
            source_ids=[
                "ositran-convocatorias",
                "defensoria-del-pueblo-cas",
                "utp-hiringroom-campus",
                "gobpe-indecopi-convocatorias",
            ],
            fixtures_dir=self.fixtures_dir,
            dry_run=True,
        )
        self.assertEqual(report.sources_evaluated, 4)
        self.assertEqual(report.sources_succeeded, 4)
        self.assertEqual(report.sources_failed, 0)
        self.assertTrue(report.validation_passed)
        self.assertEqual(len(report.validation_errors), 0)
        # Should have captured candidates from each source and filtered out non-systems roles
        self.assertGreaterEqual(report.total_captured, 10)
        self.assertGreaterEqual(report.total_filtered, 7)
        self.assertGreaterEqual(report.total_discarded, 3)  # Legal roles discarded

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

        # Gob.pe authorization check
        gobpe_src = find_source(self.registry, "gobpe-indecopi-convocatorias")
        self.assertIsNotNone(gobpe_src)
        auth_gobpe = authorize_fetch(gobpe_src, "https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-cas/", 0)
        self.assertTrue(auth_gobpe["allowed"])

        auth_gobpe_cdn = authorize_fetch(gobpe_src, "https://cdn.www.gob.pe/uploads/document/file/123/bases.pdf", 0)
        self.assertTrue(auth_gobpe_cdn["allowed"])

        auth_gobpe_bad = authorize_fetch(gobpe_src, "https://fake.indecopi.gob.pe.attacker.com/malicious", 0)
        self.assertFalse(auth_gobpe_bad["allowed"])

    # =========================================================================
    # 7. Comprehensive Acceptance & Edge Scenarios (TASK-R5-01 Cierre)
    # =========================================================================

    def test_gobpe_12_acceptance_scenarios(self) -> None:
        """Covers all 12 mandatory acceptance & edge scenarios for Gob.pe / state connectors."""
        source = find_source(self.registry, "gobpe-indecopi-convocatorias")
        self.assertIsNotNone(source)

        # 1. Convocatoria con plazo futuro y estado oficial abierto
        future_html = """
        <table>
          <tr>
            <td>100-2026</td>
            <td>DESARROLLADOR PYTHON</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/999901">Bases</a></td>
            <td>PUBLICADA</td>
            <td>Podrás postular el 15/12/2026 (de 08:30 am a 5:00 pm)</td>
          </tr>
        </table>
        """
        cands_future = transform_gobpe_indecopi_html(source, future_html, include_closed=False)
        self.assertEqual(len(cands_future), 1)
        self.assertEqual(cands_future[0]["proposed"]["deadline"], "2026-12-15")
        self.assertIn("15/12/2026", cands_future[0]["editorialReview"]["decisionNote"])

        # 2. Convocatoria con plazo vencido
        expired_html = """
        <table>
          <tr>
            <td>050-2025</td>
            <td>ANALISTA DE SISTEMAS</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/999902">Bases</a></td>
            <td>PUBLICADA</td>
            <td>Podrás postular el 15/01/2025 (de 08:30 am a 5:00 pm)</td>
          </tr>
        </table>
        """
        cands_expired = transform_gobpe_indecopi_html(source, expired_html, include_closed=True)
        self.assertEqual(len(cands_expired), 1)
        self.assertEqual(cands_expired[0]["proposed"]["deadline"], "2025-01-15")
        # When evaluated against today (2026-11-24), 2025-01-15 is expired
        self.assertLess(cands_expired[0]["proposed"]["deadline"], "2026-11-24")

        # 3. Convocatoria oficialmente cerrada
        closed_html = """
        <table>
          <tr>
            <td>080-2025</td>
            <td>ESPECIALISTA EN SEGURIDAD</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/999903">Bases</a></td>
            <td>FINALIZADA</td>
            <td>Postulaciones concluidas</td>
          </tr>
        </table>
        """
        cands_closed_skip = transform_gobpe_indecopi_html(source, closed_html, include_closed=False)
        self.assertEqual(len(cands_closed_skip), 0)
        cands_closed_keep = transform_gobpe_indecopi_html(source, closed_html, include_closed=True)
        self.assertEqual(len(cands_closed_keep), 1)
        self.assertIn("FINALIZADA", cands_closed_keep[0]["editorialReview"]["decisionNote"])

        # 4. Convocatoria sin fecha límite ni evidencia de apertura
        no_deadline_html = """
        <table>
          <tr>
            <td>090-2026</td>
            <td>ADMINISTRADOR DE REDES</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/999904">Bases</a></td>
            <td>EN REVISION</td>
            <td>------</td>
          </tr>
        </table>
        """
        cands_no_deadline = transform_gobpe_indecopi_html(source, no_deadline_html)
        self.assertEqual(len(cands_no_deadline), 1)
        self.assertIsNone(cands_no_deadline[0]["proposed"]["deadline"])

        # 5. Convocatoria con enlace oficial roto o inaccesible (handled gracefully without crash)
        broken_link_html = """
        <table>
          <tr>
            <td>091-2026</td>
            <td>PROGRAMADOR SENIOR</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/broken">Bases</a></td>
            <td>PUBLICADA</td>
            <td>Podrás postular el 20/12/2026</td>
          </tr>
        </table>
        """
        def broken_detail_fetcher(url):
            raise ConnectionError("503 Service Unavailable")

        cands_broken = transform_gobpe_indecopi_html(source, broken_link_html, detail_fetcher=broken_detail_fetcher)
        self.assertEqual(len(cands_broken), 1)
        self.assertEqual(cands_broken[0]["proposed"]["title"], "PROGRAMADOR SENIOR (OTI)")

        # 6. PDF con texto extraíble
        pdf_extractable = "Honorarios: Remuneracion S/. 4,500.00. Perfil: Titulado en Ingenieria de Software."
        mock_detail = '<html><body><a href="https://cdn.www.gob.pe/uploads/document/file/11/bases.pdf">Bases</a></body></html>'
        cands_pdf_ok = transform_gobpe_indecopi_html(
            source,
            broken_link_html,
            detail_fetcher=lambda u: mock_detail,
            pdf_fetcher=lambda u: pdf_extractable,
        )
        self.assertEqual(cands_pdf_ok[0]["proposed"]["salary"], "S/.4,500.00")
        self.assertIn("Titulado en Ingenieria de Software", cands_pdf_ok[0]["proposed"]["requirements"])

        # 7. PDF escaneado o sin texto extraíble (returns empty string)
        cands_pdf_scanned = transform_gobpe_indecopi_html(
            source,
            broken_link_html,
            detail_fetcher=lambda u: mock_detail,
            pdf_fetcher=lambda u: "",  # Scanned image with no text layer
        )
        self.assertEqual(len(cands_pdf_scanned), 1)
        self.assertIsNone(cands_pdf_scanned[0]["proposed"]["salary"])
        self.assertIn("Bases oficiales publicadas", cands_pdf_scanned[0]["proposed"]["requirements"])

        # 8. Duplicados del mismo proceso
        import copy
        cand_dup = copy.deepcopy(cands_future[0])
        cand_dup["candidateId"] = "CAND-gobpe-indecopi-convocatorias-cas-100-2026-dup"
        dup_batch = [cands_future[0], cand_dup]
        dedup_result = deduplicate_candidates(dup_batch)
        self.assertEqual(dedup_result.total_evaluated, 2)
        self.assertGreaterEqual(len(dedup_result.collisions), 1)
        self.assertEqual(dedup_result.collisions[0].match_type, "EXACT_DUPLICATE")

        # 9. Registro con clasificación técnica incorrecta / no relevante
        cls_legal = classify_candidate(
            title="ASISTENTE LEGAL EN DERECHO CIVIL",
            location="Lima, Perú",
            mode="No informado",
            employer="INDECOPI",
        )
        self.assertEqual(cls_legal.relevance, "NOT_RELEVANT")
        self.assertFalse(cls_legal.is_staging_eligible)

        cls_tech = classify_candidate(
            title="ANALISTA PROGRAMADOR DE SISTEMAS",
            location="Lima, Perú",
            mode="No informado",
            employer="INDECOPI",
        )
        self.assertEqual(cls_tech.relevance, "DIRECT")
        self.assertTrue(cls_tech.is_staging_eligible)

        # 10. Registro que debe quedar en revisión (pending_review)
        self.assertEqual(cands_future[0]["editorialReview"]["status"], "pending_review")
        self.assertFalse(cands_future[0]["editorialReview"].get("reviewedBy"))

        # 11. Fallo de descarga de un documento sin interrumpir los demás
        two_row_html = """
        <table>
          <tr>
            <td>101-2026</td>
            <td>ANALISTA QA</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/row1">Bases 1</a></td>
            <td>PUBLICADA</td>
            <td>Podrás postular el 22/12/2026</td>
          </tr>
          <tr>
            <td>102-2026</td>
            <td>DEVOPS ENGINEER</td>
            <td>1</td>
            <td>OTI</td>
            <td><a href="https://www.gob.pe/institucion/indecopi/informes-publicaciones/row2">Bases 2</a></td>
            <td>PUBLICADA</td>
            <td>Podrás postular el 23/12/2026</td>
          </tr>
        </table>
        """
        def selective_detail_fetcher(url):
            if "row1" in url:
                raise TimeoutError("Connection timed out")
            return '<html><body><a href="https://cdn.www.gob.pe/uploads/document/file/22/bases2.pdf">Bases</a></body></html>'

        cands_multi = transform_gobpe_indecopi_html(source, two_row_html, detail_fetcher=selective_detail_fetcher)
        self.assertEqual(len(cands_multi), 2)
        self.assertEqual(cands_multi[0]["proposed"]["externalReference"], "INDECOPI-CAS-101-2026")
        self.assertEqual(cands_multi[1]["proposed"]["externalReference"], "INDECOPI-CAS-102-2026")

        # 12. Protección del catálogo canónico
        with self.assertRaises(PermissionError):
            _atomic_write_json(SEED_CATALOG_PATH, {"test": True})
        with self.assertRaises(PermissionError):
            _atomic_write_json(SNAPSHOT_CATALOG_PATH, {"test": True})


if __name__ == "__main__":
    unittest.main()
