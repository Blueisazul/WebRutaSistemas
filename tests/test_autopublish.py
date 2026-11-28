"""Unit and integration test suite for Velora's Rules-Based Autopublication Engine (TASK-R6-01).

Validates all 18 mandatory acceptance scenarios defined in the prompt:
1. Candidate meeting all 6 rules -> eligible_for_publication.
2. Source not approved -> retained (pending_review).
3. Automated access not approved -> retained.
4. Non-secure HTTP applyUrl -> retained.
5. Host not in allowlist (including substring attack evil-encora.com) -> retained.
6. Ambiguous technical classification (ADJACENT or OUT_OF_SCOPE) -> retained.
7. Remote candidate without explicit Peru eligibility (LATAM / GLOBAL_REMOTE) -> retained.
8. Candidate with explicit Peru eligibility (PERU_LOCAL or PERU_REMOTE) -> passes Rule 4.
9. Exact duplicate collision against seed -> retained.
10. Secondary signature collision against seed -> retained.
11. Expired deadline (deadline < as_of) -> retained.
12. Stale ATS capture exceeding verification TTL (> 7 days) without deadline -> retained.
13. Incomplete evidence / missing mandatory fields -> retained.
14. Contradictory evidence (e.g., closed/inactive status in text or status) -> retained.
15. Unexpected exception during validation -> fail-closed (pending_review).
16. Idempotence of execution -> second run produces zero duplicate opportunities.
17. Canonical catalog opportunities preserved intact during promotion.
18. Mixed candidate batch -> only 100% compliant candidates promoted, others retained.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from collector.autopublish import (
    RULE_1_AUTHORIZED_SOURCE,
    RULE_2_SECURE_APPLY_URL,
    RULE_3_TECHNICAL_CLASSIFICATION,
    RULE_4_PERU_ELIGIBILITY,
    RULE_5_DEDUPLICATION,
    RULE_6_VALIDITY_AND_TRACEABILITY,
    CandidateEvaluationResult,
    convert_candidate_to_opportunity,
    evaluate_candidate_for_autopublication,
    evaluate_rule_1_authorized_source,
    evaluate_rule_2_secure_apply_url,
    evaluate_rule_3_technical_classification,
    evaluate_rule_4_peru_eligibility,
    evaluate_rule_5_deduplication,
    evaluate_rule_6_validity_and_traceability,
    is_host_allowlisted,
    run_autopublication,
)
from collector.policy import load_source_registry

LIMA_TZ = timezone(timedelta(hours=-5))
REF_DATE = date(2026, 11, 25)
NOW_ISO = "2026-11-25T12:00:00-05:00"


def _make_valid_candidate(
    candidate_id: str = "CAN-TEST-001",
    source_id: str = "lever-kavak",
    title: str = "Software Engineer Backend",
    employer: str = "Kavak",
    apply_url: str = "https://jobs.lever.co/kavak/12345",
    location: str = "Lima, Perú",
    mode: str = "hybrid",
    deadline: str = "2026-12-15",
    captured_at: str = "2026-11-24T10:00:00-05:00",
) -> dict[str, Any]:
    """Builds a candidate that fully satisfies all 6 rules under lever-kavak."""
    return {
        "candidateId": candidate_id,
        "sourceId": source_id,
        "sourceUrl": "https://api.lever.co/v0/postings/kavak",
        "capturedAt": captured_at,
        "payloadSchemaVersion": "2.0",
        "proposed": {
            "title": title,
            "employer": employer,
            "publisher": employer,
            "description": "Buscamos un Ingeniero de Sistemas / Software Engineer con experiencia en Python, APIs y SQL para nuestro equipo en Lima, Perú.",
            "applyUrl": apply_url,
            "location": location,
            "mode": mode,
            "sector": "private",
            "family": "development",
            "level": "mid",
            "kind": "job",
            "eligibility": "Peru-based or authorized to work in Peru",
            "duration": "Indefinido",
            "salary": "Competitivo según mercado",
            "deadline": deadline,
            "publishedAt": "2026-11-20",
            "requirements": ["Python", "SQL", "Git", "REST APIs"],
        },
        "editorialReview": {
            "status": "pending_review",
            "reviewer": None,
            "reviewedAt": None,
            "decisionNote": "",
        },
        "fieldEvidence": [
            {
                "field": "title",
                "url": apply_url,
                "observedAt": captured_at,
            },
            {
                "field": "employer",
                "url": apply_url,
                "observedAt": captured_at,
            },
            {
                "field": "applyUrl",
                "url": apply_url,
                "observedAt": captured_at,
            },
            {
                "field": "location",
                "url": apply_url,
                "observedAt": captured_at,
            },
            {
                "field": "mode",
                "url": apply_url,
                "observedAt": captured_at,
            },
            {
                "field": "deadline",
                "url": apply_url,
                "observedAt": captured_at,
            },
        ],
    }


class TestAutopublishEngineScenarios(unittest.TestCase):
    """Test suite executing the 18 mandatory acceptance scenarios for TASK-R6-01."""

    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="velora_autopub_test_"))
        # Load real sources registry
        self.registry = load_source_registry()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_scenario_01_all_rules_satisfied_eligible(self) -> None:
        """Scenario 1: Candidate meeting all 6 rules is marked eligible_for_publication."""
        cand = _make_valid_candidate()
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "eligible_for_publication")
        self.assertEqual(len(res.failure_reasons), 0)
        for r_name, r_eval in res.rules.items():
            self.assertTrue(r_eval.passed, f"Regla {r_name} debió pasar: {r_eval.reason}")

    def test_scenario_02_source_not_approved_retained(self) -> None:
        """Scenario 2: Source with decision != 'approved' is retained."""
        cand = _make_valid_candidate()
        custom_registry = copy.deepcopy(self.registry)
        for s in custom_registry.get("sources", []):
            if s.get("id") == cand["sourceId"]:
                s["decision"] = "review_needed"

        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=custom_registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_1_AUTHORIZED_SOURCE].passed)
        self.assertIn("decision='review_needed'", res.rules[RULE_1_AUTHORIZED_SOURCE].reason)

    def test_scenario_03_automated_access_not_approved_retained(self) -> None:
        """Scenario 3: Source with automatedAccessStatus != 'approved' is retained."""
        cand = _make_valid_candidate()
        custom_registry = copy.deepcopy(self.registry)
        for s in custom_registry.get("sources", []):
            if s.get("id") == cand["sourceId"]:
                s["automatedAccessStatus"] = "manual_only"

        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=custom_registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_1_AUTHORIZED_SOURCE].passed)
        self.assertIn("automatedAccessStatus='manual_only'", res.rules[RULE_1_AUTHORIZED_SOURCE].reason)

    def test_scenario_04_insecure_http_url_retained(self) -> None:
        """Scenario 4: Non-HTTPS applyUrl is retained."""
        cand = _make_valid_candidate(apply_url="http://jobs.lever.co/kavak/12345")
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_2_SECURE_APPLY_URL].passed)
        self.assertIn("URL de postulación insegura o no válida HTTPS", res.rules[RULE_2_SECURE_APPLY_URL].reason)

    def test_scenario_05_host_not_in_allowlist_retained(self) -> None:
        """Scenario 5: Host not in allowlist (including substring attack) is retained."""
        # Test 1: attacker host evil-encora.com
        cand_evil = _make_valid_candidate(apply_url="https://evil-encora.com/jobs/apply")
        res_evil = evaluate_candidate_for_autopublication(
            candidate=cand_evil,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res_evil.decision, "pending_review")
        self.assertFalse(res_evil.rules[RULE_2_SECURE_APPLY_URL].passed)
        self.assertIn("no pertenece a la lista blanca autorizada", res_evil.rules[RULE_2_SECURE_APPLY_URL].reason)

        # Test 2: completely foreign domain
        cand_other = _make_valid_candidate(apply_url="https://external-phishing.org/apply")
        res_other = evaluate_candidate_for_autopublication(
            candidate=cand_other,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res_other.decision, "pending_review")
        self.assertFalse(res_other.rules[RULE_2_SECURE_APPLY_URL].passed)

    def test_scenario_06_ambiguous_technical_classification_retained(self) -> None:
        """Scenario 6: Role that does not classify as DIRECT systems/computing is retained."""
        cand = _make_valid_candidate(
            title="Asistente de Contabilidad y Finanzas",
            employer="Encora",
        )
        cand["proposed"]["description"] = "Registro contable, conciliaciones bancarias y facturación electrónica de compras y ventas."
        cand["proposed"]["requirements"] = ["Excel avanzado", "Concar", "Normas tributarias SUNAT"]

        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_3_TECHNICAL_CLASSIFICATION].passed)
        self.assertIn("no inequívoca", res.rules[RULE_3_TECHNICAL_CLASSIFICATION].reason)

    def test_scenario_07_remote_without_explicit_peru_eligibility_retained(self) -> None:
        """Scenario 7: Remote candidate with generic LATAM or Worldwide location fails Rule 4."""
        cand = _make_valid_candidate(
            location="LATAM (Remote)",
            mode="remote",
        )
        cand["proposed"]["description"] = "Buscamos Software Engineer Remoto para toda Latinoamérica. Horario flexible."
        cand["proposed"]["eligibility"] = "América Latina"

        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_4_PERU_ELIGIBILITY].passed)
        self.assertIn("Elegibilidad para Perú no demostrada", res.rules[RULE_4_PERU_ELIGIBILITY].reason)

    def test_scenario_08_explicit_peru_eligibility_passes_rule_4(self) -> None:
        """Scenario 8: Explicit Peru eligibility (PERU_LOCAL or PERU_REMOTE) passes Rule 4."""
        # Case A: Local Peru
        cand_local = _make_valid_candidate(location="Arequipa, Perú", mode="on_site")
        res_local = evaluate_rule_4_peru_eligibility(cand_local)
        self.assertTrue(res_local.passed)
        self.assertEqual(res_local.details.get("eligibility_type"), "PERU_LOCAL")

        # Case B: Explicit Peru Remote
        cand_remote = _make_valid_candidate(location="Remoto - Perú", mode="remote")
        cand_remote["proposed"]["description"] = "Rol 100% remoto para desarrolladores ubicados en territorio peruano."
        res_remote = evaluate_rule_4_peru_eligibility(cand_remote)
        self.assertTrue(res_remote.passed)
        self.assertEqual(res_remote.details.get("eligibility_type"), "PERU_REMOTE")

    def test_scenario_09_exact_duplicate_collision_against_seed_retained(self) -> None:
        """Scenario 9: Candidate that collides via exact URL or primary key with seed is retained."""
        cand = _make_valid_candidate(
            apply_url="https://job-boards.greenhouse.io/encora/jobs/already-published",
        )
        seed_ops = [
            {
                "id": "OP-050",
                "title": "Software Engineer Backend",
                "employer": "Encora",
                "applyUrl": "https://job-boards.greenhouse.io/encora/jobs/already-published",
                "opportunityStatus": "open",
            }
        ]
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=seed_ops,
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_5_DEDUPLICATION].passed)
        self.assertIn("Colisión con oportunidad canónica existente", res.rules[RULE_5_DEDUPLICATION].reason)

    def test_scenario_10_secondary_signature_collision_against_seed_retained(self) -> None:
        """Scenario 10: Candidate that matches open seed opportunity by secondary signature is retained."""
        cand = _make_valid_candidate(
            title="Senior DevOps Engineer",
            employer="Encora",
            apply_url="https://job-boards.greenhouse.io/encora/jobs/devops-new-link",
        )
        seed_ops = [
            {
                "id": "OP-051",
                "title": "Senior DevOps Engineer",
                "employer": "Encora",
                "applyUrl": "https://job-boards.greenhouse.io/encora/jobs/devops-old-link",
                "opportunityStatus": "open",
            }
        ]
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=seed_ops,
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_5_DEDUPLICATION].passed)
        self.assertIn("Posible duplicado", res.rules[RULE_5_DEDUPLICATION].reason)

    def test_scenario_11_expired_deadline_retained(self) -> None:
        """Scenario 11: Candidate with deadline < as_of date is retained."""
        cand = _make_valid_candidate(deadline="2026-11-20")  # As of is 2026-11-25
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].passed)
        self.assertIn("Fecha límite expirada", res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].reason)

    def test_scenario_12_stale_ats_capture_exceeding_ttl_retained(self) -> None:
        """Scenario 12: ATS candidate without deadline and captured > 7 days ago is retained."""
        cand = _make_valid_candidate(
            deadline="",
            captured_at="2026-11-10T10:00:00-05:00",  # 15 days before 2026-11-25
        )
        cand["proposed"]["deadline"] = None
        cand["fieldEvidence"] = [e for e in cand["fieldEvidence"] if e.get("field") != "deadline"]

        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].passed)
        self.assertIn("excede el TTL máximo", res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].reason)

    def test_scenario_13_incomplete_evidence_missing_fields_retained(self) -> None:
        """Scenario 13: Candidate with missing mandatory fields or empty fieldEvidence is retained."""
        # Case A: Missing sourceUrl
        cand_no_src = _make_valid_candidate()
        cand_no_src["sourceUrl"] = ""
        res_a = evaluate_candidate_for_autopublication(
            candidate=cand_no_src,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res_a.decision, "pending_review")
        self.assertFalse(res_a.rules[RULE_6_VALIDITY_AND_TRACEABILITY].passed)

        # Case B: Empty fieldEvidence
        cand_no_ev = _make_valid_candidate()
        cand_no_ev["fieldEvidence"] = []
        res_b = evaluate_candidate_for_autopublication(
            candidate=cand_no_ev,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res_b.decision, "pending_review")
        self.assertFalse(res_b.rules[RULE_6_VALIDITY_AND_TRACEABILITY].passed)

    def test_scenario_14_contradictory_evidence_closed_status_retained(self) -> None:
        """Scenario 14: Candidate with text or field evidence indicating closed/finalized vacancy is retained."""
        cand = _make_valid_candidate()
        cand["proposed"]["description"] += " NOTA: Esta convocatoria ha concluido. Convocatoria finalizada."
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertFalse(res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].passed)
        self.assertIn("Indicios de vacante cerrada o finalizada", res.rules[RULE_6_VALIDITY_AND_TRACEABILITY].reason)

    def test_scenario_15_unexpected_exception_fail_closed(self) -> None:
        """Scenario 15: Unexpected exception in validation fails closed without unhandled crashing."""
        cand = _make_valid_candidate()
        cand["sourceId"] = None
        cand["proposed"] = None
        res = evaluate_candidate_for_autopublication(
            candidate=cand,
            source_registry=self.registry,
            seed_opportunities=[],
            processed_batch=[],
            as_of=REF_DATE,
        )
        self.assertEqual(res.decision, "pending_review")
        self.assertTrue(len(res.failure_reasons) > 0)

    def test_scenario_16_idempotence_no_duplicates_on_second_run(self) -> None:
        """Scenario 16: Running autopublication twice produces zero duplicate opportunities."""
        inbox_file = self.tmp_dir / "inbox.json"
        seed_file = self.tmp_dir / "opportunities.seed.json"
        snap_file = self.tmp_dir / "opportunities.json"
        sources_file = self.tmp_dir / "sources.json"

        # Initialize mock sources
        sources_file.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

        # Initialize seed with 1 existing opportunity
        initial_seed = {
            "schemaVersion": 2,
            "verificationTtlDays": 7,
            "timezone": "America/Lima",
            "sourceNote": "Catálogo curado",
            "opportunities": [
                {
                    "id": "OP-001",
                    "title": "Ingeniero Cloud",
                    "employer": "Tech Corp",
                    "applyUrl": "https://techcorp.com/jobs/1",
                    "status": "open",
                }
            ],
        }
        seed_file.write_text(json.dumps(initial_seed, indent=2), encoding="utf-8")

        # Initialize snapshot
        initial_snapshot = {
            "schemaVersion": 2,
            "generatedAt": NOW_ISO,
            "total": 1,
            "opportunities": initial_seed["opportunities"],
        }
        snap_file.write_text(json.dumps(initial_snapshot, indent=2), encoding="utf-8")

        # Initialize inbox with 1 valid candidate
        cand = _make_valid_candidate()
        inbox_data = {"schemaVersion": 1, "candidates": [cand]}
        inbox_file.write_text(json.dumps(inbox_data, indent=2), encoding="utf-8")

        # Run 1: Apply promotion
        report1 = run_autopublication(
            inbox_path=inbox_file,
            seed_path=seed_file,
            snapshot_path=snap_file,
            sources_path=sources_file,
            as_of=REF_DATE,
            dry_run=False,
        )
        self.assertEqual(report1.promoted_count, 1)
        self.assertEqual(report1.promoted_opportunity_ids, ["OP-002"])

        # Check seed has 2 ops
        seed_after_1 = json.loads(seed_file.read_text(encoding="utf-8"))
        self.assertEqual(len(seed_after_1["opportunities"]), 2)

        # Run 2: Apply promotion again on same files
        report2 = run_autopublication(
            inbox_path=inbox_file,
            seed_path=seed_file,
            snapshot_path=snap_file,
            sources_path=sources_file,
            as_of=REF_DATE,
            dry_run=False,
        )
        self.assertEqual(report2.promoted_count, 0)
        self.assertEqual(len(report2.promoted_opportunity_ids), 0)

        # Check seed STILL has 2 ops (zero duplicate creation)
        seed_after_2 = json.loads(seed_file.read_text(encoding="utf-8"))
        self.assertEqual(len(seed_after_2["opportunities"]), 2)

    def test_scenario_17_pre_existing_catalog_opportunities_preserved(self) -> None:
        """Scenario 17: Pre-existing catalog opportunities are untouched during promotion."""
        inbox_file = self.tmp_dir / "inbox.json"
        seed_file = self.tmp_dir / "opportunities.seed.json"
        snap_file = self.tmp_dir / "opportunities.json"
        sources_file = self.tmp_dir / "sources.json"

        sources_file.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

        original_op = {
            "id": "OP-010",
            "title": "Arquitecto de Software",
            "employer": "Tech Corp",
            "applyUrl": "https://techcorp.com/jobs/10",
            "status": "open",
            "location": "Lima, Perú",
            "specialCustomField": "PRESERVE_ME_EXACTLY",
        }
        seed_data = {
            "schemaVersion": 2,
            "verificationTtlDays": 7,
            "timezone": "America/Lima",
            "sourceNote": "Catálogo curado",
            "opportunities": [copy.deepcopy(original_op)],
        }
        seed_file.write_text(json.dumps(seed_data, indent=2), encoding="utf-8")

        snapshot_data = {
            "schemaVersion": 2,
            "generatedAt": NOW_ISO,
            "total": 1,
            "opportunities": [copy.deepcopy(original_op)],
        }
        snap_file.write_text(json.dumps(snapshot_data, indent=2), encoding="utf-8")

        cand = _make_valid_candidate(candidate_id="CAN-NEW-001")
        inbox_data = {"schemaVersion": 1, "candidates": [cand]}
        inbox_file.write_text(json.dumps(inbox_data, indent=2), encoding="utf-8")

        run_autopublication(
            inbox_path=inbox_file,
            seed_path=seed_file,
            snapshot_path=snap_file,
            sources_path=sources_file,
            as_of=REF_DATE,
            dry_run=False,
        )

        updated_seed = json.loads(seed_file.read_text(encoding="utf-8"))
        self.assertEqual(len(updated_seed["opportunities"]), 2)
        # Verify first item is exactly identical
        self.assertEqual(updated_seed["opportunities"][0]["id"], "OP-010")
        self.assertEqual(updated_seed["opportunities"][0]["specialCustomField"], "PRESERVE_ME_EXACTLY")

    def test_scenario_18_mixed_candidate_batch_only_compliant_promoted(self) -> None:
        """Scenario 18: In a mixed batch, only 100% compliant candidates are promoted."""
        inbox_file = self.tmp_dir / "inbox.json"
        seed_file = self.tmp_dir / "opportunities.seed.json"
        snap_file = self.tmp_dir / "opportunities.json"
        sources_file = self.tmp_dir / "sources.json"

        sources_file.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

        seed_file.write_text(json.dumps({
            "schemaVersion": 2,
            "verificationTtlDays": 7,
            "timezone": "America/Lima",
            "sourceNote": "Catálogo curado",
            "opportunities": [],
        }, indent=2), encoding="utf-8")
        snap_file.write_text(json.dumps({
            "schemaVersion": 2,
            "generatedAt": NOW_ISO,
            "total": 0,
            "opportunities": [],
        }, indent=2), encoding="utf-8")

        c1 = _make_valid_candidate(candidate_id="CAN-VALID-1", apply_url="https://jobs.lever.co/kavak/valid-1")
        c2_bad_source = _make_valid_candidate(candidate_id="CAN-BAD-SRC", source_id="unregistered-source")
        c3_bad_proto = _make_valid_candidate(candidate_id="CAN-BAD-PROTO", apply_url="http://jobs.lever.co/kavak/bad")
        c4_valid_2 = _make_valid_candidate(candidate_id="CAN-VALID-2", title="Full Stack Developer", apply_url="https://jobs.lever.co/kavak/valid-2")
        c5_remote_no_peru = _make_valid_candidate(candidate_id="CAN-NO-PERU", location="LATAM (Remote)", mode="remote")
        c5_remote_no_peru["proposed"]["description"] = "Desarrollador para América Latina."

        inbox_data = {"schemaVersion": 1, "candidates": [c1, c2_bad_source, c3_bad_proto, c4_valid_2, c5_remote_no_peru]}
        inbox_file.write_text(json.dumps(inbox_data, indent=2), encoding="utf-8")

        report = run_autopublication(
            inbox_path=inbox_file,
            seed_path=seed_file,
            snapshot_path=snap_file,
            sources_path=sources_file,
            as_of=REF_DATE,
            dry_run=False,
        )

        self.assertEqual(report.total_evaluated, 5)
        self.assertEqual(report.eligible_count, 2)
        self.assertEqual(report.retained_count, 3)
        self.assertEqual(report.promoted_count, 2)
        self.assertEqual(report.promoted_opportunity_ids, ["OP-001", "OP-002"])

        # Check resulting inbox states
        updated_inbox = json.loads(inbox_file.read_text(encoding="utf-8"))
        cands_by_id = {c["candidateId"]: c for c in updated_inbox["candidates"]}

        self.assertEqual(cands_by_id["CAN-VALID-1"]["editorialReview"]["status"], "approved_for_catalog")
        self.assertEqual(cands_by_id["CAN-VALID-2"]["editorialReview"]["status"], "approved_for_catalog")
        self.assertEqual(cands_by_id["CAN-BAD-SRC"]["editorialReview"]["status"], "pending_review")
        self.assertEqual(cands_by_id["CAN-BAD-PROTO"]["editorialReview"]["status"], "pending_review")
        self.assertEqual(cands_by_id["CAN-NO-PERU"]["editorialReview"]["status"], "pending_review")


if __name__ == "__main__":
    unittest.main()
