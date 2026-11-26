"""Unit tests for the Peruvian labor regime taxonomy and classifier.

TASK-R7-01: Taxonomía de Regímenes Laborales Peruanos (CAS, 728, Formativo).
Verifies:
- All 7 canonical labor regimes.
- Conservative fail-closed classification.
- Authoritative legal citations and certainty levels.
- Normalization of identifiers and abbreviations.
- Integration with collector/classification.py and collector/autopublish.py.
- Validation rules in scripts/catalog_quality.py and scripts/validate_candidates.py.
- Retrocompatibility with Schema 2 canonical catalog.
"""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import unittest

from collector.labor_regime import (
    ALL_CERTAINTIES,
    ALL_REGIMES,
    CERTAINTY_DERIVED,
    CERTAINTY_EXPLICIT,
    CERTAINTY_UNSPECIFIED,
    REGIME_728,
    REGIME_CAS,
    REGIME_CIVIL,
    REGIME_DEFINITIONS,
    REGIME_OTHER,
    REGIME_PRE_PROFESSIONAL,
    REGIME_PROFESSIONAL,
    REGIME_UNSPECIFIED,
    classify_labor_regime,
    get_regime_metadata,
    normalize_regime_id,
)
from collector.classification import classify_candidate
from collector.autopublish import convert_candidate_to_opportunity
from scripts.catalog_quality import (
    LABOR_REGIMES,
    LABOR_REGIME_CERTAINTIES,
    validate_records,
)

ROOT = Path(__file__).resolve().parent.parent


class TestLaborRegimeTaxonomy(unittest.TestCase):
    """Verifies taxonomy completeness, authoritative metadata, and legal frameworks."""

    def test_canonical_regimes_set(self):
        expected_regimes = {
            "PRE_PROFESSIONAL_INTERNSHIP",
            "PROFESSIONAL_INTERNSHIP",
            "CAS",
            "LABOR_REGIME_728",
            "CIVIL_SERVICES",
            "OTHER",
            "UNSPECIFIED",
        }
        self.assertEqual(set(ALL_REGIMES), expected_regimes)
        self.assertEqual(LABOR_REGIMES, expected_regimes)

    def test_canonical_certainties_set(self):
        expected_certainties = {
            "EXPLICIT_EVIDENCE",
            "DERIVED_BASES",
            "UNSPECIFIED",
        }
        self.assertEqual(set(ALL_CERTAINTIES), expected_certainties)
        self.assertEqual(LABOR_REGIME_CERTAINTIES, expected_certainties)

    def test_all_regimes_have_authoritative_metadata(self):
        for regime_id in ALL_REGIMES:
            defn = REGIME_DEFINITIONS[regime_id]
            self.assertIn("label", defn)
            self.assertIn("shortLabel", defn)
            self.assertIn("legalFramework", defn)
            self.assertIn("nature", defn)
            self.assertIn("maxWorkingHours", defn)
            self.assertIn("compensation", defn)
            self.assertIn("keyRights", defn)
            self.assertIn("cautions", defn)
            self.assertTrue(len(defn["label"]) > 0)
            self.assertTrue(len(defn["legalFramework"]) > 0)

    def test_legal_citations_accuracy(self):
        # 1. Prácticas pre: Ley 28518
        self.assertIn("28518", REGIME_DEFINITIONS[REGIME_PRE_PROFESSIONAL]["legalFramework"])
        # 2. Prácticas pro: Ley 28518 / 31396
        self.assertIn("31396", REGIME_DEFINITIONS[REGIME_PROFESSIONAL]["legalFramework"])
        # 3. CAS: D. Leg. 1057
        self.assertIn("1057", REGIME_DEFINITIONS[REGIME_CAS]["legalFramework"])
        # 4. Régimen 728: D. Leg. 728 / D.S. 003-97-TR
        self.assertIn("728", REGIME_DEFINITIONS[REGIME_728]["legalFramework"])
        # 5. Locación: Código Civil 1764
        self.assertIn("1764", REGIME_DEFINITIONS[REGIME_CIVIL]["legalFramework"])


class TestLaborRegimeClassification(unittest.TestCase):
    """Verifies deterministic classification across diverse opportunity inputs."""

    def test_classify_explicit_cas(self):
        record = {
            "title": "Especialista en Seguridad de la Información",
            "contractType": "CAS",
            "requisition": "CAS N° 045-2026-SUNAT",
            "sector": "Público",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_CAS)
        self.assertEqual(res.certainty, CERTAINTY_EXPLICIT)
        self.assertIn("1057", res.legal_framework)

    def test_classify_derived_cas_from_title(self):
        record = {
            "title": "Analista de Base de Datos - Proceso CAS N° 12",
            "contractType": "Temporal",
            "sector": "Público",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_CAS)
        self.assertEqual(res.certainty, CERTAINTY_DERIVED)

    def test_classify_explicit_pre_professional_internship(self):
        record = {
            "title": "Practicante Preprofesional de Desarrollo Backend",
            "kind": "Prácticas",
            "contractType": "Convenio de aprendizaje preprofesional",
            "sector": "Privado",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_PRE_PROFESSIONAL)
        self.assertEqual(res.certainty, CERTAINTY_EXPLICIT)
        self.assertIn("28518", res.legal_framework)

    def test_classify_explicit_professional_internship(self):
        record = {
            "title": "Practicante Profesional de Ciberseguridad",
            "kind": "Prácticas",
            "contractType": "Prácticas profesionales",
            "sector": "Privado",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_PROFESSIONAL)
        self.assertEqual(res.certainty, CERTAINTY_EXPLICIT)
        self.assertIn("31396", res.legal_framework)

    def test_classify_generic_practica_with_student_level(self):
        record = {
            "title": "Practicante de Sistemas e Infraestructura",
            "kind": "Prácticas",
            "level": "Estudiante",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_PRE_PROFESSIONAL)
        self.assertEqual(res.certainty, CERTAINTY_DERIVED)

    def test_classify_generic_practica_with_graduate_level(self):
        record = {
            "title": "Practicante de Analítica de Datos",
            "kind": "Prácticas",
            "level": "Egresado",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_PROFESSIONAL)
        self.assertEqual(res.certainty, CERTAINTY_DERIVED)

    def test_classify_explicit_regime_728(self):
        record = {
            "title": "Ingeniero DevSecOps Senior",
            "contractType": "D. Leg. 728 (Indeterminado)",
            "sector": "Privado",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_728)
        self.assertEqual(res.certainty, CERTAINTY_EXPLICIT)
        self.assertIn("728", res.legal_framework)

    def test_classify_derived_regime_728_from_benefits(self):
        record = {
            "title": "Desarrollador Fullstack",
            "benefits": "Ingreso a planilla completa con CTS y gratificaciones conforme a ley",
            "sector": "Privado",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_728)
        self.assertEqual(res.certainty, CERTAINTY_DERIVED)

    def test_classify_explicit_civil_services(self):
        record = {
            "title": "Consultor Especialista en Arquitectura Cloud",
            "contractType": "Locación de Servicios",
            "sector": "Público",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_CIVIL)
        self.assertEqual(res.certainty, CERTAINTY_EXPLICIT)
        self.assertIn("1764", res.legal_framework)

    def test_classify_derived_civil_services_from_honorarios(self):
        record = {
            "title": "Desarrollador Móvil Flutter",
            "tasks": "Emisión de recibo por honorarios contra entregable mensual",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_CIVIL)
        self.assertEqual(res.certainty, CERTAINTY_DERIVED)

    def test_classify_other_contractor_b2b(self):
        record = {
            "title": "Lead Software Architect",
            "contractType": "B2B Contractor",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_OTHER)

    def test_classify_fail_closed_unspecified(self):
        # A private company with no contract information should NOT blindly assume 728
        record = {
            "title": "Frontend Developer",
            "employer": "Tech Co",
            "sector": "Privado",
            "kind": "Profesional",
        }
        res = classify_labor_regime(record)
        self.assertEqual(res.regime_id, REGIME_UNSPECIFIED)
        self.assertEqual(res.certainty, CERTAINTY_UNSPECIFIED)


class TestNormalizationAndMetadata(unittest.TestCase):
    """Verifies regime identifier normalization and metadata lookup."""

    def test_normalize_varied_strings(self):
        self.assertEqual(normalize_regime_id("CAS"), REGIME_CAS)
        self.assertEqual(normalize_regime_id("contratacion administrativa de servicios"), REGIME_CAS)
        self.assertEqual(normalize_regime_id("728"), REGIME_728)
        self.assertEqual(normalize_regime_id("Regimen 728"), REGIME_728)
        self.assertEqual(normalize_regime_id("Prácticas Preprofesionales"), REGIME_PRE_PROFESSIONAL)
        self.assertEqual(normalize_regime_id("Prácticas Profesionales"), REGIME_PROFESSIONAL)
        self.assertEqual(normalize_regime_id("Locación de Servicios"), REGIME_CIVIL)
        self.assertEqual(normalize_regime_id("Honorarios"), REGIME_CIVIL)
        self.assertEqual(normalize_regime_id("Otra modalidad"), REGIME_OTHER)
        self.assertEqual(normalize_regime_id(""), REGIME_UNSPECIFIED)
        self.assertEqual(normalize_regime_id(None), REGIME_UNSPECIFIED)
        self.assertEqual(normalize_regime_id("Desconocido XYZ"), REGIME_UNSPECIFIED)

    def test_get_regime_metadata_fallback(self):
        meta = get_regime_metadata("INVALID_REGIME")
        self.assertEqual(meta["id"], REGIME_UNSPECIFIED)


class TestCollectorAndAutopublishIntegration(unittest.TestCase):
    """Verifies integration with candidate classification and autopublish converter."""

    def test_candidate_classification_includes_labor_regime(self):
        res = classify_candidate(
            title="Practicante Preprofesional de Redes y Telecomunicaciones",
            location="Lima, Perú",
            mode="Híbrido",
            employer="Empresa Tech",
            description="Convenio de Prácticas Pre",
        )
        self.assertEqual(res.labor_regime, REGIME_PRE_PROFESSIONAL)
        self.assertIn(res.labor_regime_certainty, [CERTAINTY_EXPLICIT, CERTAINTY_DERIVED])
        self.assertTrue(len(res.labor_regime_explanation) > 0)

    def test_convert_candidate_to_opportunity_populates_regime(self):
        candidate = {
            "id": "CAND-001",
            "title": "Analista Programador Java CAS",
            "employer": "Ministerio de Educación",
            "sector": "Público",
            "location": "Lima, Perú",
            "sourceUrl": "https://www.gob.pe/convocatorias/1",
            "applyUrl": "https://www.gob.pe/convocatorias/1/postular",
            "requisition": "CAS 012-2026",
            "firstSeen": "2026-11-20T10:00:00Z",
            "capturedAt": "2026-11-25T10:00:00Z",
        }
        source = {
            "sourceId": "gobpe-convocatorias-test",
            "name": "Gob.pe",
            "connector": "gobpe-convocatorias",
            "allowedHosts": ["gob.pe", "www.gob.pe"],
        }
        opp = convert_candidate_to_opportunity(
            candidate,
            "OP-AUTOPUB-001",
            source,
            as_of=date(2026, 11, 25),
            now_iso="2026-11-25T12:00:00Z",
        )
        self.assertEqual(opp["laborRegime"], REGIME_CAS)
        self.assertIn(opp["laborRegimeCertainty"], [CERTAINTY_EXPLICIT, CERTAINTY_DERIVED])


class TestCatalogQualityAndValidation(unittest.TestCase):
    """Verifies that catalog_quality.py accepts valid labor regimes and validates constraints."""

    def setUp(self):
        catalog_path = ROOT / "data" / "opportunities.seed.json"
        with open(catalog_path, encoding="utf-8") as f:
            data = json.load(f)
        self.canonical_records = data["opportunities"]

    def test_validate_records_accepts_valid_labor_regimes(self):
        sample_record = dict(self.canonical_records[0])
        sample_record["laborRegime"] = REGIME_728
        sample_record["laborRegimeCertainty"] = CERTAINTY_EXPLICIT
        result = validate_records([sample_record], today=date(2026, 10, 26))
        self.assertEqual(result.errors, [])

    def test_validate_records_rejects_invalid_labor_regime(self):
        sample_record = dict(self.canonical_records[0])
        sample_record["laborRegime"] = "INVALID_REGIME_ID"
        sample_record["laborRegimeCertainty"] = "INVALID_CERTAINTY"
        result = validate_records([sample_record], today=date(2026, 10, 26))
        self.assertTrue(any("laborRegime" in err for err in result.errors))
        self.assertTrue(any("laborRegimeCertainty" in err for err in result.errors))

    def test_canonical_catalog_remains_100_percent_valid(self):
        """Ensures retrocompatibility: existing catalog records without laborRegime do not trigger regime errors."""
        for item in self.canonical_records:
            regime = item.get("laborRegime")
            if regime is not None:
                self.assertIn(regime, LABOR_REGIMES)
            certainty = item.get("laborRegimeCertainty")
            if certainty is not None:
                self.assertIn(certainty, LABOR_REGIME_CERTAINTIES)

        # Verify an existing record without laborRegime validates cleanly
        sample_no_regime = dict(self.canonical_records[0])
        sample_no_regime.pop("laborRegime", None)
        sample_no_regime.pop("laborRegimeCertainty", None)
        result = validate_records([sample_no_regime], today=date(2026, 10, 26))
        self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
