from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collector.dedup import (  # noqa: E402
    EXACT_DUPLICATE,
    IDENTIFIER_COLLISION,
    NO_MATCH,
    POSSIBLE_DUPLICATE,
    SET_BATCH,
    SET_INBOX,
    SET_SEED,
    compare_records,
    deduplicate_candidates,
    extract_fields,
    load_seed_opportunities,
    make_primary_key,
    make_secondary_signature,
    normalize_identifier,
    normalize_text,
)


FIXTURES_PATH = ROOT / "tests" / "fixtures" / "dedup" / "dedup_cases.json"


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


class CanonicalDeduplicatorTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = load_fixtures()

    def test_exact_duplicate_same_source_same_ref(self):
        cases = self.fixtures["sameSourceSameRef"]
        report = deduplicate_candidates(cases)
        self.assertEqual(report.total_evaluated, 2)
        self.assertEqual(len(report.collisions), 1)

        col = report.collisions[0]
        self.assertEqual(col.record_id, "CAND-001-B")
        self.assertEqual(col.matched_id, "CAND-001-A")
        self.assertEqual(col.matched_set, SET_BATCH)
        self.assertEqual(col.match_type, EXACT_DUPLICATE)
        self.assertEqual(col.match_key, "fuente-alfa:ref-001")
        self.assertIn("title", col.matching_fields)
        self.assertIn("employer", col.matching_fields)

    def test_different_source_same_ref_no_primary_match(self):
        cases = self.fixtures["diffSourceSameRef"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 0)

    def test_different_location_no_secondary_match(self):
        cases = self.fixtures["diffLocation"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 0)

    def test_different_mode_no_secondary_match(self):
        cases = self.fixtures["diffMode"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 0)

    def test_different_opportunity_type_no_secondary_match(self):
        cases = self.fixtures["diffType"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 0)

    def test_different_title_same_employer_no_match(self):
        cases = self.fixtures["diffTitleSameEmployer"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 0)

    def test_leading_zeros_preservation(self):
        # Case identical zeros: "00123" vs "00123"
        cases_identical = self.fixtures["leadingZeros"]["identical"]
        rep_id = deduplicate_candidates(cases_identical)
        self.assertEqual(len(rep_id.collisions), 1)
        self.assertEqual(rep_id.collisions[0].match_type, EXACT_DUPLICATE)
        self.assertEqual(rep_id.collisions[0].match_key, "fuente-alfa:00123")

        # Case different zeros: "00123" vs "123"
        cases_diff = self.fixtures["leadingZeros"]["different"]
        rep_diff = deduplicate_candidates(cases_diff)
        # Primary key doesn't match; secondary matches because title/employer are same
        self.assertEqual(len(rep_diff.collisions), 1)
        self.assertEqual(rep_diff.collisions[0].match_type, POSSIBLE_DUPLICATE)
        self.assertIn("externalReference", rep_diff.collisions[0].discrepant_fields)

    def test_missing_identifiers_do_not_produce_primary_match(self):
        cand1 = {"candidateId": "C-1", "sourceId": "fuente", "proposed": {"title": "Dev", "employer": "E1", "externalReference": None}}
        cand2 = {"candidateId": "C-2", "sourceId": "fuente", "proposed": {"title": "Dev", "employer": "E2", "externalReference": None}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 0)

    def test_employer_case_and_whitespace_normalization(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "Junior Dev", "employer": "  EMPRESA FICTICIA  "}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": "Junior Dev", "employer": "Empresa Ficticia"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].match_type, POSSIBLE_DUPLICATE)

    def test_title_accents_and_unicode_normalization(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "Ingeniería de Software", "employer": "Empresa"}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": "Ingenieria de Software", "employer": "Empresa"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].match_type, POSSIBLE_DUPLICATE)

    def test_title_punctuation_normalization(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "TI / Sistemas", "employer": "Empresa"}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": "TI - Sistemas", "employer": "Empresa"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].match_type, POSSIBLE_DUPLICATE)

    def test_null_values_handled_gracefully(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": None, "employer": None}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": None, "employer": None}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 0)

    def test_different_dates_flagged_in_discrepant_fields(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "Dev", "employer": "Emp", "publishedAt": "2026-10-01"}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": "Dev", "employer": "Emp", "publishedAt": "2026-11-01"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 1)
        self.assertIn("publishedAt", report.collisions[0].discrepant_fields)

    def test_batch_duplicates_detected(self):
        cand1 = {"candidateId": "C-1", "sourceId": "src", "proposed": {"title": "Dev", "employer": "Emp", "externalReference": "X1"}}
        cand2 = {"candidateId": "C-2", "sourceId": "src", "proposed": {"title": "Dev", "employer": "Emp", "externalReference": "X1"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].matched_set, SET_BATCH)

    def test_inter_batch_duplicates_detected(self):
        batch1 = [{"candidateId": "B1-1", "sourceId": "src", "proposed": {"title": "Dev", "employer": "Emp", "externalReference": "X1"}}]
        batch2 = [{"candidateId": "B2-1", "sourceId": "src", "proposed": {"title": "Dev", "employer": "Emp", "externalReference": "X1"}}]
        report = deduplicate_candidates(batch2, inbox_candidates=batch1)
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].matched_set, SET_INBOX)

    def test_inbox_matches_detected(self):
        inbox = [{"candidateId": "INBOX-10", "sourceId": "servir", "proposed": {"title": "Practicante TI", "employer": "OSITRAN", "externalReference": "REF-10"}}]
        batch = [{"candidateId": "NEW-1", "sourceId": "servir", "proposed": {"title": "Practicante TI", "employer": "OSITRAN", "externalReference": "REF-10"}}]
        report = deduplicate_candidates(batch, inbox_candidates=inbox)
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].matched_id, "INBOX-10")
        self.assertEqual(report.collisions[0].matched_set, SET_INBOX)

    def test_seed_matches_detected(self):
        seed_opps = load_seed_opportunities()
        self.assertGreater(len(seed_opps), 0)

        # Match against OP-001 (OSITRAN Practicante profesional de TI)
        cand = {
            "candidateId": "CAND-CHECK-OP1",
            "sourceId": "otra-fuente",
            "proposed": {
                "title": "Practicante profesional de TI",
                "employer": "OSITRAN",
                "location": "Surquillo, Lima, Perú",
                "mode": "Flexible / según área",
                "opportunityType": "Práctica profesional",
            },
        }
        report = deduplicate_candidates([cand], seed_opportunities=seed_opps)
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].matched_id, "OP-001")
        self.assertEqual(report.collisions[0].matched_set, SET_SEED)
        self.assertEqual(report.collisions[0].match_type, POSSIBLE_DUPLICATE)

    def test_identifier_collision_contradictory_data(self):
        cases = self.fixtures["identifierCollision"]
        report = deduplicate_candidates(cases)
        self.assertEqual(len(report.collisions), 1)
        col = report.collisions[0]
        self.assertEqual(col.match_type, IDENTIFIER_COLLISION)
        self.assertIn("título", col.explanation)
        self.assertIn("empleador", col.explanation)
        self.assertIn("conflicto crítico", col.recommended_action)

    def test_similar_titles_different_fields_no_match(self):
        cand1 = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "Practicante de Sistemas", "employer": "Ministerio"}}
        cand2 = {"candidateId": "C-2", "sourceId": "s2", "proposed": {"title": "Practicante de Finanzas", "employer": "Ministerio"}}
        report = deduplicate_candidates([cand1, cand2])
        self.assertEqual(len(report.collisions), 0)

    def test_empty_input_returns_zero_collisions(self):
        report = deduplicate_candidates([])
        self.assertEqual(report.total_evaluated, 0)
        self.assertEqual(len(report.collisions), 0)
        self.assertEqual(report.summary_by_type[EXACT_DUPLICATE], 0)

    def test_immutability_of_inputs_and_seed(self):
        cand = {"candidateId": "C-1", "sourceId": "s1", "proposed": {"title": "Dev", "employer": "E1"}}
        cand_copy = json.loads(json.dumps(cand))

        seed_path = ROOT / "data" / "opportunities.seed.json"
        seed_before = seed_path.read_bytes()

        deduplicate_candidates([cand], seed_opportunities=load_seed_opportunities())

        self.assertEqual(cand, cand_copy)
        self.assertEqual(seed_path.read_bytes(), seed_before)

    def test_deterministic_order_of_report(self):
        cand_a = {"candidateId": "CAND-A", "sourceId": "src", "proposed": {"title": "Dev", "employer": "E", "externalReference": "1"}}
        cand_b = {"candidateId": "CAND-B", "sourceId": "src", "proposed": {"title": "Dev", "employer": "E", "externalReference": "1"}}
        cand_c = {"candidateId": "CAND-C", "sourceId": "src", "proposed": {"title": "Dev", "employer": "E", "externalReference": "1"}}

        rep1 = deduplicate_candidates([cand_a, cand_b, cand_c]).to_dict()
        rep2 = deduplicate_candidates([cand_a, cand_b, cand_c]).to_dict()

        self.assertEqual(rep1, rep2)


if __name__ == "__main__":
    unittest.main()
