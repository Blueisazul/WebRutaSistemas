"""Unit tests for Geographic Normalization and Territorial Scope Taxonomy (TASK-R5-05)."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from collector.geography import (  # noqa: E402
    ALL_SCOPES,
    PERUVIAN_DEPARTMENTS,
    SCOPE_DEFINITIONS,
    SCOPE_INTL_ELIGIBLE,
    SCOPE_INTL_UNCONFIRMED,
    SCOPE_NOT_ELIGIBLE,
    SCOPE_PERU_LOCAL,
    SCOPE_PERU_REMOTE,
    SCOPE_UNSPECIFIED,
    classify_opportunity_geography,
    extract_city_or_district,
    extract_peruvian_department,
    normalize_workplace_mode,
)


class TestGeographicNormalization(unittest.TestCase):
    def test_canonical_scopes_defined(self):
        self.assertEqual(len(ALL_SCOPES), 6)
        for s in ALL_SCOPES:
            self.assertIn(s, SCOPE_DEFINITIONS)
            self.assertTrue(SCOPE_DEFINITIONS[s]["label"])
            self.assertTrue(SCOPE_DEFINITIONS[s]["shortLabel"])

    def test_peruvian_departments_coverage(self):
        # 24 departamentos + 1 Provincia Constitucional (Callao)
        self.assertEqual(len(PERUVIAN_DEPARTMENTS), 25)
        self.assertIn("Lima", PERUVIAN_DEPARTMENTS)
        self.assertIn("Arequipa", PERUVIAN_DEPARTMENTS)
        self.assertIn("Callao", PERUVIAN_DEPARTMENTS)
        self.assertIn("Cusco", PERUVIAN_DEPARTMENTS)

    def test_peru_local_onsite_lima(self):
        res = classify_opportunity_geography(
            location="Surquillo, Lima, Perú",
            mode="Presencial",
            eligibility="Perú",
            employer="OSITRAN",
        )
        self.assertEqual(res.scope, SCOPE_PERU_LOCAL)
        self.assertEqual(res.workplace_mode, "ONSITE")
        self.assertEqual(res.country_code, "PE")
        self.assertEqual(res.department, "Lima")
        self.assertEqual(res.city_or_district, "Surquillo")

    def test_peru_local_hybrid_lima_district(self):
        res = classify_opportunity_geography(
            location="Lima (Torre Prisma, Magdalena del Mar)",
            mode="Híbrido",
            eligibility="Estudiantes universitarios en Perú",
            employer="Encora",
        )
        self.assertEqual(res.scope, SCOPE_PERU_LOCAL)
        self.assertEqual(res.workplace_mode, "HYBRID")
        self.assertEqual(res.department, "Lima")
        self.assertEqual(res.city_or_district, "Magdalena del Mar")

    def test_peru_local_regional_department(self):
        res = classify_opportunity_geography(
            location="Arequipa, Perú",
            mode="Presencial",
            eligibility="Perú",
            employer="Empresa Minera",
        )
        self.assertEqual(res.scope, SCOPE_PERU_LOCAL)
        self.assertEqual(res.department, "Arequipa")
        self.assertEqual(res.city_or_district, "Arequipa")

    def test_peru_remote_national(self):
        res = classify_opportunity_geography(
            location="Perú (Remoto nacional)",
            mode="Remoto",
            eligibility="Perú (trabajo remoto en territorio peruano)",
            employer="Encora",
        )
        self.assertEqual(res.scope, SCOPE_PERU_REMOTE)
        self.assertEqual(res.workplace_mode, "REMOTE")
        self.assertEqual(res.country_code, "PE")

    def test_international_remote_peru_eligible(self):
        res = classify_opportunity_geography(
            location="Home based - Worldwide (Perú elegible)",
            mode="Remoto",
            eligibility="Perú (remoto internacional)",
            employer="Canonical",
        )
        self.assertEqual(res.scope, SCOPE_INTL_ELIGIBLE)
        self.assertEqual(res.workplace_mode, "REMOTE")
        self.assertIsNone(res.department)

    def test_international_remote_regional_americas_eligible(self):
        res = classify_opportunity_geography(
            location="Latin America (Perú elegible)",
            mode="Remoto",
            eligibility="Perú (remoto internacional en América Latina)",
            employer="Sezzle",
        )
        self.assertEqual(res.scope, SCOPE_INTL_ELIGIBLE)
        self.assertEqual(res.workplace_mode, "REMOTE")

    def test_multicountry_remote_with_peru(self):
        res = classify_opportunity_geography(
            location="Remoto (Chile, Perú o Colombia)",
            mode="Remoto",
            eligibility="Chile, Perú o Colombia",
            employer="42Labs",
        )
        self.assertEqual(res.scope, SCOPE_INTL_ELIGIBLE)
        self.assertEqual(res.workplace_mode, "REMOTE")
        self.assertIsNone(res.department)

    def test_international_remote_unconfirmed(self):
        res = classify_opportunity_geography(
            location="Remoto global",
            mode="Remoto",
            eligibility="Global según el anuncio; confirmar contratación desde Perú",
            employer="Launchpad Technologies",
        )
        self.assertEqual(res.scope, SCOPE_INTL_UNCONFIRMED)
        self.assertEqual(res.workplace_mode, "REMOTE")

    def test_not_eligible_peru_exclusion(self):
        res = classify_opportunity_geography(
            location="Remote — US residents only",
            mode="Remoto",
            eligibility="US only",
            employer="US Corp",
        )
        self.assertEqual(res.scope, SCOPE_NOT_ELIGIBLE)
        self.assertEqual(res.workplace_mode, "REMOTE")

    def test_unspecified_empty_location(self):
        res = classify_opportunity_geography(
            location="",
            mode="",
            eligibility="",
        )
        self.assertEqual(res.scope, SCOPE_UNSPECIFIED)
        self.assertIsNone(res.department)

    def test_department_extraction_case_and_accents(self):
        self.assertEqual(extract_peruvian_department("Áncash"), "Áncash")
        self.assertEqual(extract_peruvian_department("ancash"), "Áncash")
        self.assertEqual(extract_peruvian_department("Chimbote, Perú"), "Áncash")
        self.assertEqual(extract_peruvian_department("Trujillo"), "La Libertad")
        self.assertEqual(extract_peruvian_department("Huancayo"), "Junín")
        self.assertEqual(extract_peruvian_department("Cusco"), "Cusco")
        self.assertEqual(extract_peruvian_department("Iquitos"), "Loreto")
        self.assertIsNone(extract_peruvian_department("Madrid, España"))

    def test_workplace_mode_normalization(self):
        self.assertEqual(normalize_workplace_mode("Presencial"), "ONSITE")
        self.assertEqual(normalize_workplace_mode("Híbrido"), "HYBRID")
        self.assertEqual(normalize_workplace_mode("Remoto"), "REMOTE")
        self.assertEqual(normalize_workplace_mode("home based - worldwide"), "REMOTE")
        self.assertEqual(normalize_workplace_mode("Flexible / según área"), "UNSPECIFIED")


if __name__ == "__main__":
    unittest.main()
