"""Unit tests for classification and coverage expansion (R4-06)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collector.classification import classify_candidate
from collector.policy import load_source_registry


class TestClassificationAndCoverage(unittest.TestCase):
    def test_relevance_direct(self):
        titles = [
            "Software Engineer",
            "Junior Fullstack Developer",
            "DevOps / SRE Specialist",
            "Cloud Security Engineer",
            "Data Engineer II",
            "Linux Kernel Developer",
            "QA Automation Engineer",
            "Technical Support Specialist",
        ]
        for t in titles:
            res = classify_candidate(title=t, location="Lima, Peru", mode="Remoto")
            self.assertEqual(res.relevance, "DIRECT", f"Failed for {t}")
            self.assertTrue(res.is_staging_eligible, f"Should be eligible: {t}")

    def test_relevance_adjacent(self):
        titles = [
            "Operations Analyst",
            "Fraud Operations Analyst",
            "Disputes and Chargebacks Specialist",
            "Process Automation Analyst",
            "BI Analyst",
            "IT Audit Specialist",
        ]
        for t in titles:
            res = classify_candidate(title=t, location="Latin America", mode="Remoto")
            self.assertEqual(res.relevance, "ADJACENT", f"Failed for {t}")
            self.assertTrue(res.is_staging_eligible, f"Should be eligible: {t}")

    def test_relevance_not_relevant(self):
        titles = [
            "Chef de Partie",
            "Executive Recruiter",
            "Warehouse Associate",
            "Commercial Counsel - Legal",
            "Growth Marketing Senior Analyst",
            "Accounting Clerk",
        ]
        for t in titles:
            res = classify_candidate(title=t, location="Lima, Peru", mode="Presencial")
            self.assertEqual(res.relevance, "NOT_RELEVANT", f"Failed for {t}")
            self.assertFalse(res.is_staging_eligible, f"Should NOT be eligible: {t}")

    def test_geographic_eligibility(self):
        cases = [
            ("Lima, Peru", "Presencial", "PERU_LOCAL", True),
            ("Peru", "Remoto", "PERU_REMOTE", True),
            ("Home Based - Americas", "Remoto", "LATAM", True),
            ("Latin America", "Remoto", "LATAM", True),
            ("Home based - Worldwide", "Remoto", "GLOBAL_REMOTE", True),
            ("Beijing, China", "Presencial", "NOT_ELIGIBLE", False),
            ("London, UK", "Presencial", "NOT_ELIGIBLE", False),
            ("Poland, Remote", "Remoto", "NOT_ELIGIBLE", False),
            ("Atlanta, Georgia, United States", "Presencial", "NOT_ELIGIBLE", False),
        ]
        for loc, mode, expected_geo, expected_staging in cases:
            res = classify_candidate(title="Software Engineer", location=loc, mode=mode)
            self.assertEqual(res.geographic_eligibility, expected_geo, f"Failed for {loc}")
            self.assertEqual(res.is_staging_eligible, expected_staging, f"Failed eligible for {loc}")

    def test_experience_tiers(self):
        cases = [
            ("Graduate Software Engineer", "ENTRY_OR_JUNIOR"),
            ("Junior QA Analyst", "ENTRY_OR_JUNIOR"),
            ("Engineering Intern", "ENTRY_OR_JUNIOR"),
            ("Associate Cloud Engineer", "ENTRY_OR_JUNIOR"),
            ("Software Engineer", "MID"),
            ("Linux Systems Engineer", "MID"),
            ("Senior Software Engineer", "SENIOR_OR_LEAD"),
            ("Tech Lead", "SENIOR_OR_LEAD"),
            ("Engineering Director", "SENIOR_OR_LEAD"),
            ("Principal SRE", "SENIOR_OR_LEAD"),
        ]
        for title, expected_tier in cases:
            res = classify_candidate(title=title, location="Lima, Peru", mode="Remoto")
            self.assertEqual(res.experience_tier, expected_tier, f"Failed for {title}")

    def test_approved_sources_configured_cleanly(self):
        reg = load_source_registry()
        approved = [s for s in reg["sources"] if s.get("enabled") and s.get("decision") == "approved"]
        self.assertEqual(len(approved), 14, "Must have exactly 14 approved sources (6 ATS + 4 Initial PE + 4 Corporate PE)")
        source_ids = {s["id"] for s in approved}
        expected_ids = {
            "greenhouse-canonical",
            "greenhouse-sezzle",
            "greenhouse-cookunity",
            "greenhouse-encora",
            "lever-fintual",
            "lever-kavak",
            "ositran-convocatorias",
            "defensoria-del-pueblo-cas",
            "utp-hiringroom-campus",
            "gobpe-indecopi-convocatorias",
            "stefanini-hiringroom",
            "canvia-hiringroom",
            "myapps-hiringroom",
            "efitec-hiringroom",
        }
        self.assertEqual(source_ids, expected_ids)


if __name__ == "__main__":
    unittest.main()
