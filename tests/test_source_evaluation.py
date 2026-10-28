from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collector.policy import authorize_fetch, find_source, load_source_registry  # noqa: E402


class SourceEvaluationTests(unittest.TestCase):
    def test_talento_peru_remains_pending_and_disabled(self):
        source = find_source(load_source_registry(), "talento-peru-servir")
        self.assertIsNotNone(source)
        self.assertEqual(source["decision"], "pending_review")
        self.assertFalse(source["enabled"])
        self.assertEqual(source["maxRequestsPerRun"], 0)
        self.assertEqual(source["automatedAccessStatus"], "pending_review")
        self.assertEqual(source["publicReuseStatus"], "pending_review")

    def test_pending_source_cannot_be_fetched(self):
        source = find_source(load_source_registry(), "talento-peru-servir")
        result = authorize_fetch(source, "https://talentoperu.servir.gob.pe/", 0)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "source_disabled")

    def test_pending_decision_blocks_even_if_enabled_and_other_flags_look_approved(self):
        source = copy.deepcopy(find_source(load_source_registry(), "talento-peru-servir"))
        source.update({
            "enabled": True,
            "connector": "greenhouse-job-board",
            "kind": "public_ats_api",
            "termsReview": "approved_public_api",
            "rightsReview": "metadata_only_approved",
            "automatedAccessStatus": "approved",
            "maxRequestsPerRun": 1,
        })
        result = authorize_fetch(source, "https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml", 0)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "source_decision_not_approved")

    def test_missing_decision_is_not_implicit_authorization(self):
        source = {
            "enabled": True,
            "connector": "greenhouse-job-board",
            "kind": "public_ats_api",
            "termsReview": "approved_public_api",
            "rightsReview": "metadata_only_approved",
            "automatedAccessStatus": "approved",
            "maxRequestsPerRun": 1,
            "allowedHosts": ["boards-api.greenhouse.io"],
        }
        result = authorize_fetch(source, "https://boards-api.greenhouse.io/v1/boards/demo/jobs", 0)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "source_decision_not_approved")

    def test_unmsm_alternative_also_remains_pending_and_cannot_be_fetched(self):
        source = find_source(load_source_registry(), "unmsm-fisi-employment-board")
        self.assertIsNotNone(source)
        self.assertEqual(source["decision"], "pending_review")
        self.assertFalse(source["enabled"])
        self.assertEqual(source["maxRequestsPerRun"], 0)
        result = authorize_fetch(source, "https://sistemas.unmsm.edu.pe/", 0)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "source_disabled")


if __name__ == "__main__":
    unittest.main()
