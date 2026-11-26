"""Unit and integration test suite for Velora's Scheduled Revalidation Engine (TASK-R6-02).

Validates all 22 mandatory acceptance scenarios + TTL regression test:
1. Vacante abierta confirmada en ATS -> lastVerifiedAt actualizado, ausencias = 0.
2. Primera ausencia detectada -> DISAPPEARED_ONCE, no se cierra en catálogo (permanece activa).
3. Segunda ausencia consecutiva -> NOT_FOUND_CONFIRMED, marcada como histórica / cerrada.
4. Ausencia seguida de vacante abierta -> contador de ausencias reiniciado a 0.
5. Ausencia, error temporal y ausencia -> error temporal NO incrementa contador, segunda ausencia confirma cierre.
6. HTTP 404 manejado de forma segura sin cierre ciego.
7. HTTP 403 clasificado como TEMPORARY_ERROR, no es cierre.
8. HTTP 429 (rate-limit) clasificado como TEMPORARY_ERROR, no es cierre.
9. HTTP 500 clasificado como TEMPORARY_ERROR, no es cierre.
10. Timeout de red clasificado como TEMPORARY_ERROR, no es cierre.
11. JSON malformado clasificado como TEMPORARY_ERROR, no es cierre.
12. Cierre explícito informado por ATS -> CLOSED_CONFIRMED directamente sin requerir 2 ausencias.
13. Fuente no autorizada -> no se consulta ni se altera catálogo.
14. Fuente sin conector compatible -> SOURCE_UNSUPPORTED, no se asume cierre.
15. Oportunidad sin requisición -> se marca no verificable de forma automatizada, preservada activa.
16. Idempotencia -> segunda corrida con mismos datos produce estado idéntico.
17. Concurrencia -> RevalidationLock impide ejecuciones simultáneas del catálogo.
18. Aislamiento de errores -> fallo en una fuente permite que las demás continúen.
19. Integridad del catálogo -> oportunidades no involucradas se preservan intactas.
20. Persistencia -> el estado sobrevive entre ejecuciones a través de revalidation-state.json.
21. Revalidación de staging -> no promueve candidatos al catálogo ni toca archivos canónicos.
22. Fallo de validación final -> rollback seguro, no se reemplaza el catálogo ante error.
23. Regresión TTL R4-11-03 -> la revalidación exitosa actualiza lastCheckedDate dentro del TTL de 7 días.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from collector.revalidation import (
    DEFAULT_STATE_PATH,
    PROTECTED_PATHS,
    RESULT_CLOSED_CONFIRMED,
    RESULT_DISAPPEARED_ONCE,
    RESULT_NOT_FOUND_CONFIRMED,
    RESULT_OPEN_CONFIRMED,
    RESULT_SOURCE_UNSUPPORTED,
    RESULT_TEMPORARY_ERROR,
    RevalidationLock,
    _atomic_write_json,
    fetch_board_data,
    load_revalidation_state,
    revalidate_canonical_catalog,
    run_revalidation_job,
    save_revalidation_state,
)

LIMA_TZ = timezone(timedelta(hours=-5))
REF_DATE = date(2026, 11, 25)
NOW_ISO = "2026-11-25T12:00:00-05:00"


class TestRevalidationR602(unittest.TestCase):
    """Test suite for TASK-R6-02 Scheduled Revalidation and Lifecycle Management."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.tmp_dir.name)
        self.seed_path = self.work_dir / "opportunities.seed.json"
        self.snapshot_path = self.work_dir / "opportunities.json"
        self.state_path = self.work_dir / "revalidation-state.json"
        self.fixtures_dir = self.work_dir / "fixtures"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        # Load real Schema 2 compliant baseline opportunities from repository seed
        canonical_seed = json.loads(Path("data/opportunities.seed.json").read_text(encoding="utf-8"))
        self.opp1 = copy.deepcopy(next(o for o in canonical_seed["opportunities"] if o["id"] == "OP-006"))
        self.opp_other = copy.deepcopy(next(o for o in canonical_seed["opportunities"] if o["id"] == "OP-001"))

        # Synchronize opp1 observed timestamps with REF_DATE for fresh baseline
        self.opp1["lastCheckedDate"] = REF_DATE.isoformat()
        self.opp1["lastVerifiedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"
        if "verificationEvidence" in self.opp1:
            self.opp1["verificationEvidence"]["observedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"
        for fe in self.opp1.get("fieldEvidence", []):
            if isinstance(fe, dict):
                fe["observedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"

        self.seed_data = {
            "schemaVersion": 2,
            "verificationTtlDays": 7,
            "timezone": "America/Lima",
            "sourceNote": "Test catalog for R6-02 verification",
            "opportunities": [copy.deepcopy(self.opp1), copy.deepcopy(self.opp_other)],
        }
        self.seed_path.write_text(json.dumps(self.seed_data, indent=2), encoding="utf-8")
        self.snapshot_path.write_text(
            json.dumps({**self.seed_data, "generatedAt": NOW_ISO}, indent=2), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    # -------------------------------------------------------------------------
    # Scenario 1: Vacante abierta (active confirmed)
    # -------------------------------------------------------------------------
    def test_scenario_01_open_confirmed(self) -> None:
        """ATS returns the job -> lastVerifiedAt updated, absences reset to 0, remains active."""
        fixture_content = {
            "jobs": [
                {
                    "id": 8379825,
                    "title": "Software Engineer (Canonical)",
                    "company_name": "Canonical",
                    "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825",
                    "location": {"name": "Home Based - Americas"},
                    "updated_at": "2026-11-25T10:00:00Z",
                }
            ]
        }
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res["openConfirmedCount"], 1)
        self.assertEqual(res["firstAbsenceCount"], 0)
        self.assertEqual(res["secondAbsenceCount"], 0)

        # Check state file
        state = load_revalidation_state(self.state_path)
        opp_st = state["opportunities"]["OP-006"]
        self.assertEqual(opp_st["consecutiveMissingCount"], 0)
        self.assertEqual(opp_st["lastResult"], RESULT_OPEN_CONFIRMED)

        # Check catalog
        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["opportunityStatus"], "open")
        self.assertEqual(opp["publicationStatus"], "active")
        self.assertEqual(opp["lastCheckedDate"], REF_DATE.isoformat())

    # -------------------------------------------------------------------------
    # Scenario 2: Primera ausencia (missing once)
    # -------------------------------------------------------------------------
    def test_scenario_02_first_absence_remains_active(self) -> None:
        """Missing once in ATS -> DISAPPEARED_ONCE, consecutiveMissingCount=1, opportunity remains active."""
        fixture_content = {"jobs": []}
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res["firstAbsenceCount"], 1)
        self.assertEqual(res["secondAbsenceCount"], 0)
        self.assertEqual(res["becameHistoricalCount"], 0)

        # State records 1 absence
        state = load_revalidation_state(self.state_path)
        opp_st = state["opportunities"]["OP-006"]
        self.assertEqual(opp_st["consecutiveMissingCount"], 1)
        self.assertEqual(opp_st["lastResult"], RESULT_DISAPPEARED_ONCE)

        # Catalog opportunity MUST REMAIN ACTIVE (Anti-closure safeguard)
        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["opportunityStatus"], "open")
        self.assertEqual(opp["publicationStatus"], "active")

    # -------------------------------------------------------------------------
    # Scenario 3: Segunda ausencia consecutiva (missing twice)
    # -------------------------------------------------------------------------
    def test_scenario_03_second_consecutive_absence_confirmed_historical(self) -> None:
        """Missing twice consecutively -> NOT_FOUND_CONFIRMED, marked historical and closed."""
        fixture_content = {"jobs": []}
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        # Run 1: First absence
        revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        # Run 2: Second consecutive absence (next evaluation date)
        date_run2 = REF_DATE + timedelta(days=7)
        res2 = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=date_run2,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res2["secondAbsenceCount"], 1)
        self.assertEqual(res2["becameHistoricalCount"], 1)

        # State records 2 absences and closure
        state = load_revalidation_state(self.state_path)
        opp_st = state["opportunities"]["OP-006"]
        self.assertEqual(opp_st["consecutiveMissingCount"], 2)
        self.assertEqual(opp_st["lastResult"], RESULT_NOT_FOUND_CONFIRMED)

        # Catalog opportunity is now closed and historical
        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["opportunityStatus"], "closed")
        self.assertEqual(opp["publicationStatus"], "historical")
        self.assertEqual(opp["verificationStatus"], "stale")

    # -------------------------------------------------------------------------
    # Scenario 4: Ausencia seguida de vacante abierta
    # -------------------------------------------------------------------------
    def test_scenario_04_absence_followed_by_open_resets_counter(self) -> None:
        """Missing in run 1 (count=1), then reappears in run 2 -> count resets to 0, remains active."""
        # Run 1: Missing
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps({"jobs": []}), encoding="utf-8"
        )
        revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        state1 = load_revalidation_state(self.state_path)
        self.assertEqual(state1["opportunities"]["OP-006"]["consecutiveMissingCount"], 1)

        # Run 2: Reappears
        fixture_active = {
            "jobs": [
                {
                    "id": 8379825,
                    "title": "Software Engineer (Canonical)",
                    "company_name": "Canonical",
                    "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825",
                    "location": {"name": "Home Based - Americas"},
                }
            ]
        }
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_active), encoding="utf-8"
        )

        date_run2 = REF_DATE + timedelta(days=7)
        res2 = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=date_run2,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res2["openConfirmedCount"], 1)
        state2 = load_revalidation_state(self.state_path)
        self.assertEqual(state2["opportunities"]["OP-006"]["consecutiveMissingCount"], 0)
        self.assertEqual(state2["opportunities"]["OP-006"]["lastResult"], RESULT_OPEN_CONFIRMED)

    # -------------------------------------------------------------------------
    # Scenario 5: Ausencia, error temporal y ausencia
    # -------------------------------------------------------------------------
    def test_scenario_05_absence_temporary_error_and_absence(self) -> None:
        """Run 1: absent (1). Run 2: network error (count NOT incremented). Run 3: absent (2 -> closed)."""
        # Run 1: Absent
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps({"jobs": []}), encoding="utf-8"
        )
        revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        state1 = load_revalidation_state(self.state_path)
        self.assertEqual(state1["opportunities"]["OP-006"]["consecutiveMissingCount"], 1)

        # Run 2: Simulated network error during fetch
        with patch("collector.revalidation.fetch_board_data", side_effect=ConnectionResetError("Connection reset by peer")):
            res2 = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                threshold=2,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res2["temporaryErrorCount"], 1)

        # Counter MUST NOT be incremented on network error!
        state2 = load_revalidation_state(self.state_path)
        self.assertEqual(state2["opportunities"]["OP-006"]["consecutiveMissingCount"], 1)

        # Run 3: Absent again
        res3 = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE + timedelta(days=7),
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res3["secondAbsenceCount"], 1)
        self.assertEqual(res3["becameHistoricalCount"], 1)
        state3 = load_revalidation_state(self.state_path)
        self.assertEqual(state3["opportunities"]["OP-006"]["consecutiveMissingCount"], 2)
        self.assertEqual(state3["opportunities"]["OP-006"]["lastResult"], RESULT_NOT_FOUND_CONFIRMED)

    # -------------------------------------------------------------------------
    # Scenario 6: HTTP 404 manejado de forma segura
    # -------------------------------------------------------------------------
    def test_scenario_06_http_404_handled_safely(self) -> None:
        """HTTP 404 on endpoint is caught as TEMPORARY_ERROR, preventing blind mass closure."""
        from urllib.error import HTTPError

        err = HTTPError("https://boards-api.greenhouse.io", 404, "Not Found", {}, None)  # type: ignore[arg-type]
        with patch("collector.revalidation.fetch_board_data", side_effect=err):
            res = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                threshold=2,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res["temporaryErrorCount"], 1)
            self.assertEqual(res["secondAbsenceCount"], 0)

        # Catalog remains completely open
        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["opportunityStatus"], "open")

    # -------------------------------------------------------------------------
    # Scenario 7: HTTP 403 clasificado como TEMPORARY_ERROR
    # -------------------------------------------------------------------------
    def test_scenario_07_http_403_temporary_error(self) -> None:
        """HTTP 403 Forbidden is classified as TEMPORARY_ERROR, not closed."""
        from urllib.error import HTTPError

        err = HTTPError("https://boards-api.greenhouse.io", 403, "Forbidden", {}, None)  # type: ignore[arg-type]
        with patch("collector.revalidation.fetch_board_data", side_effect=err):
            res = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res["temporaryErrorCount"], 1)
            self.assertEqual(res["becameHistoricalCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 8: HTTP 429 (rate-limit) clasificado como TEMPORARY_ERROR
    # -------------------------------------------------------------------------
    def test_scenario_08_http_429_rate_limit_temporary_error(self) -> None:
        """HTTP 429 Too Many Requests is classified as TEMPORARY_ERROR."""
        from urllib.error import HTTPError

        err = HTTPError("https://boards-api.greenhouse.io", 429, "Too Many Requests", {}, None)  # type: ignore[arg-type]
        with patch("collector.revalidation.fetch_board_data", side_effect=err):
            res = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res["temporaryErrorCount"], 1)

    # -------------------------------------------------------------------------
    # Scenario 9: HTTP 500 clasificado como TEMPORARY_ERROR
    # -------------------------------------------------------------------------
    def test_scenario_09_http_500_server_error_temporary_error(self) -> None:
        """HTTP 500 Internal Server Error is classified as TEMPORARY_ERROR."""
        from urllib.error import HTTPError

        err = HTTPError("https://boards-api.greenhouse.io", 500, "Internal Server Error", {}, None)  # type: ignore[arg-type]
        with patch("collector.revalidation.fetch_board_data", side_effect=err):
            res = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res["temporaryErrorCount"], 1)

    # -------------------------------------------------------------------------
    # Scenario 10: Timeout de red clasificado como TEMPORARY_ERROR
    # -------------------------------------------------------------------------
    def test_scenario_10_network_timeout_temporary_error(self) -> None:
        """Network Timeout / socket.timeout is classified as TEMPORARY_ERROR."""
        import socket

        with patch("collector.revalidation.fetch_board_data", side_effect=socket.timeout("Operation timed out")):
            res = revalidate_canonical_catalog(
                seed_path=self.seed_path,
                snapshot_path=self.snapshot_path,
                state_path=self.state_path,
                fixtures_dir=self.fixtures_dir,
                as_of=REF_DATE,
                apply_updates=True,
                source_ids=["greenhouse-canonical"],
            )
            self.assertEqual(res["temporaryErrorCount"], 1)
            self.assertEqual(res["secondAbsenceCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 11: JSON malformado clasificado como TEMPORARY_ERROR
    # -------------------------------------------------------------------------
    def test_scenario_11_malformed_json_temporary_error(self) -> None:
        """Malformed JSON payload is classified as TEMPORARY_ERROR."""
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            "{ malformed json string ??? !!!", encoding="utf-8"
        )
        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )
        self.assertEqual(res["temporaryErrorCount"], 1)
        self.assertEqual(res["becameHistoricalCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 12: Cierre explícito informado por ATS
    # -------------------------------------------------------------------------
    def test_scenario_12_explicit_ats_closure(self) -> None:
        """Explicit closure reported in posting -> CLOSED_CONFIRMED directly without 2 absences."""
        fixture_content = {
            "jobs": [
                {
                    "id": 8379825,
                    "title": "Software Engineer (Canonical) - Convocatoria Concluida",
                    "company_name": "Canonical",
                    "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825",
                    "location": {"name": "Home Based - Americas"},
                    "updated_at": "2026-11-25T10:00:00Z",
                }
            ]
        }
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            threshold=2,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res["explicitClosedCount"], 1)
        self.assertEqual(res["becameHistoricalCount"], 1)

        state = load_revalidation_state(self.state_path)
        self.assertEqual(state["opportunities"]["OP-006"]["lastResult"], RESULT_CLOSED_CONFIRMED)

        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["opportunityStatus"], "closed")
        self.assertEqual(opp["publicationStatus"], "historical")

    # -------------------------------------------------------------------------
    # Scenario 13: Fuente no autorizada
    # -------------------------------------------------------------------------
    def test_scenario_13_unauthorized_source_ignored(self) -> None:
        """Unauthorized source ID is skipped and does not alter catalog."""
        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["unauthorized-fake-source"],
        )
        self.assertEqual(res["sourcesEvaluated"], 0)
        self.assertEqual(res["becameHistoricalCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 14: Fuente sin conector compatible
    # -------------------------------------------------------------------------
    def test_scenario_14_unsupported_connector_preserved(self) -> None:
        """Source without an automated connector returns SOURCE_UNSUPPORTED and preserves opportunity."""
        # Use an active opportunity whose employer is not in known sources
        opp_unsupported = copy.deepcopy(self.opp1)
        opp_unsupported["id"] = "OP-042"
        opp_unsupported["employer"] = "Empresa Sin Conector"
        opp_unsupported["sourceKind"] = "Sitio corporativo estático"
        
        current_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        current_seed["opportunities"].append(opp_unsupported)
        self.seed_path.write_text(json.dumps(current_seed, indent=2), encoding="utf-8")
        self.snapshot_path.write_text(json.dumps({**current_seed, "generatedAt": NOW_ISO}, indent=2), encoding="utf-8")

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
        )
        self.assertGreaterEqual(res["sourceUnsupportedCount"], 1)
        self.assertEqual(res["becameHistoricalCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 15: Oportunidad sin requisición
    # -------------------------------------------------------------------------
    def test_scenario_15_missing_requisition_unverifiable(self) -> None:
        """Opportunity without requisition or deducible ID is marked unverifiable automatedly."""
        opp_no_req = copy.deepcopy(self.opp1)
        opp_no_req["id"] = "OP-088"
        opp_no_req["requisition"] = None
        # Canonical careers URL is an allowed host
        opp_no_req["applyUrl"] = "https://canonical.com/careers"
        opp_no_req["evidenceUrl"] = "https://canonical.com/careers"
        if "verificationEvidence" in opp_no_req:
            opp_no_req["verificationEvidence"]["url"] = "https://canonical.com/careers"
        for fe in opp_no_req.get("fieldEvidence", []):
            if isinstance(fe, dict):
                fe["url"] = "https://canonical.com/careers"

        current_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        current_seed["opportunities"].append(opp_no_req)
        self.seed_path.write_text(json.dumps(current_seed, indent=2), encoding="utf-8")
        self.snapshot_path.write_text(json.dumps({**current_seed, "generatedAt": NOW_ISO}, indent=2), encoding="utf-8")

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )
        self.assertGreaterEqual(res["unverifiableCount"], 1)
        self.assertEqual(res["becameHistoricalCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 16: Idempotencia
    # -------------------------------------------------------------------------
    def test_scenario_16_idempotency(self) -> None:
        """Second run with identical inputs produces identical state."""
        fixture_content = {
            "jobs": [
                {
                    "id": 8379825,
                    "title": "Software Engineer (Canonical)",
                    "company_name": "Canonical",
                    "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825",
                    "location": {"name": "Home Based - Americas"},
                }
            ]
        }
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        res1 = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        res2 = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res1["openConfirmedCount"], res2["openConfirmedCount"])
        self.assertEqual(res1["becameHistoricalCount"], res2["becameHistoricalCount"])
        state = load_revalidation_state(self.state_path)
        self.assertEqual(state["opportunities"]["OP-006"]["consecutiveMissingCount"], 0)

    # -------------------------------------------------------------------------
    # Scenario 17: Concurrencia
    # -------------------------------------------------------------------------
    def test_scenario_17_concurrency_lock(self) -> None:
        """RevalidationLock prevents simultaneous execution when active lock exists."""
        lock_file = self.work_dir / ".revalidation.lock"

        # Manually acquire lock
        lock1 = RevalidationLock(lock_path=lock_file, timeout_seconds=300)
        acquired = lock1.acquire()
        self.assertTrue(acquired)
        self.assertTrue(lock1.acquired)

        # Attempt to acquire again from another instance
        lock2 = RevalidationLock(lock_path=lock_file, timeout_seconds=300)
        with self.assertRaises(RuntimeError):
            lock2.acquire()

        # Release lock
        lock1.release()
        self.assertFalse(lock_file.exists())

    # -------------------------------------------------------------------------
    # Scenario 18: Aislamiento de errores
    # -------------------------------------------------------------------------
    def test_scenario_18_source_error_isolation(self) -> None:
        """Failure in one source allows other sources to be evaluated successfully."""
        # Source 1 (greenhouse-canonical): Valid active job
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps({"jobs": [{"id": 8379825, "title": "SE", "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825", "location": {"name": "Remote"}}]}),
            encoding="utf-8",
        )
        # Source 2 (greenhouse-cookunity): Corrupt JSON file
        (self.fixtures_dir / "greenhouse-cookunity.json").write_text(
            "INVALID_JSON_CORRUPTED", encoding="utf-8"
        )

        canonical_seed = json.loads(Path("data/opportunities.seed.json").read_text(encoding="utf-8"))
        opp_cu = copy.deepcopy(next(o for o in canonical_seed["opportunities"] if o.get("employer") == "CookUnity"))
        opp_cu["lastCheckedDate"] = REF_DATE.isoformat()
        opp_cu["lastVerifiedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"
        if "verificationEvidence" in opp_cu:
            opp_cu["verificationEvidence"]["observedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"
        for fe in opp_cu.get("fieldEvidence", []):
            if isinstance(fe, dict):
                fe["observedAt"] = f"{REF_DATE.isoformat()}T08:00:00-05:00"

        self.seed_data["opportunities"].append(opp_cu)
        self.seed_path.write_text(json.dumps(self.seed_data, indent=2), encoding="utf-8")
        self.snapshot_path.write_text(json.dumps({**self.seed_data, "generatedAt": NOW_ISO}, indent=2), encoding="utf-8")

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical", "greenhouse-cookunity"],
        )

        self.assertEqual(res["sourcesSucceeded"], 1)
        self.assertEqual(res["sourcesFailed"], 1)
        self.assertEqual(res["openConfirmedCount"], 1)
        self.assertEqual(res["temporaryErrorCount"], 1)

    # -------------------------------------------------------------------------
    # Scenario 19: Integridad del catálogo
    # -------------------------------------------------------------------------
    def test_scenario_19_canonical_catalog_integrity(self) -> None:
        """Opportunities from other sources are preserved 100% intact."""
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps({"jobs": []}), encoding="utf-8"
        )

        revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        other = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-001")
        self.assertEqual(other["id"], self.opp_other["id"])
        self.assertEqual(other["title"], self.opp_other["title"])
        self.assertEqual(other["opportunityStatus"], self.opp_other["opportunityStatus"])

    # -------------------------------------------------------------------------
    # Scenario 20: Persistencia a través de revalidation-state.json
    # -------------------------------------------------------------------------
    def test_scenario_20_state_persistence_across_runs(self) -> None:
        """Absence count survives across runs via revalidation-state.json."""
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps({"jobs": []}), encoding="utf-8"
        )

        revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        # Check file exists on disk
        self.assertTrue(self.state_path.exists())
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["opportunities"]["OP-006"]["consecutiveMissingCount"], 1)

    # -------------------------------------------------------------------------
    # Scenario 21: Revalidación de staging no promueve candidatos
    # -------------------------------------------------------------------------
    def test_scenario_21_staging_revalidation_zero_promotion(self) -> None:
        """Revalidating staging inbox does not promote candidates to catalog."""
        inbox_file = self.work_dir / "inbox.local.json"
        inbox_data = {
            "schemaVersion": 2,
            "generatedAt": NOW_ISO,
            "candidates": [
                {
                    "candidateId": "CAND-001",
                    "sourceId": "greenhouse-canonical",
                    "employer": "Canonical",
                    "proposed": {
                        "title": "Staging Candidate",
                        "applyUrl": "https://job-boards.greenhouse.io/canonical/jobs/999999",
                        "requisition": "999999",
                    },
                    "capturedAt": NOW_ISO,
                    "reviewStatus": "pending_review",
                }
            ],
        }
        inbox_file.write_text(json.dumps(inbox_data), encoding="utf-8")

        # Staging revalidation
        report = run_revalidation_job(
            inbox_path=inbox_file,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            dry_run=True,
        )
        self.assertIsNotNone(report)

        # Catalog opportunities are untouched
        current_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        self.assertEqual(len(current_seed["opportunities"]), 2)
        self.assertFalse(any(o.get("title") == "Staging Candidate" for o in current_seed["opportunities"]))

    # -------------------------------------------------------------------------
    # Scenario 22: Fallo de validación final con rollback
    # -------------------------------------------------------------------------
    def test_scenario_22_final_validation_failure_rollback(self) -> None:
        """If catalog validation fails after update, disk catalog is not corrupted."""
        original_seed_bytes = self.seed_path.read_bytes()

        # Mock validate_payload to simulate Schema 2 validation failure
        mock_val = MagicMock()
        mock_val.ok = False
        mock_val.errors = ["Simulated Schema 2 validation failure"]

        with patch("catalog_quality.validate_payload", return_value=mock_val):
            with self.assertRaises(ValueError):
                revalidate_canonical_catalog(
                    seed_path=self.seed_path,
                    snapshot_path=self.snapshot_path,
                    state_path=self.state_path,
                    fixtures_dir=self.fixtures_dir,
                    as_of=REF_DATE,
                    apply_updates=True,
                    source_ids=["greenhouse-canonical"],
                )

        # Catalog on disk MUST be identical to original (unmodified)
        self.assertEqual(self.seed_path.read_bytes(), original_seed_bytes)

    # -------------------------------------------------------------------------
    # Scenario 23: Regresión TTL de frescura R4-11-03
    # -------------------------------------------------------------------------
    def test_scenario_23_freshness_ttl_regression_r4_11_03(self) -> None:
        """Successful revalidation refreshes lastCheckedDate to as_of date within 7-day TTL."""
        fixture_content = {
            "jobs": [
                {
                    "id": 8379825,
                    "title": "Software Engineer (Canonical)",
                    "company_name": "Canonical",
                    "absolute_url": "https://job-boards.greenhouse.io/canonical/jobs/8379825",
                    "location": {"name": "Home Based - Americas"},
                }
            ]
        }
        (self.fixtures_dir / "greenhouse-canonical.json").write_text(
            json.dumps(fixture_content), encoding="utf-8"
        )

        res = revalidate_canonical_catalog(
            seed_path=self.seed_path,
            snapshot_path=self.snapshot_path,
            state_path=self.state_path,
            fixtures_dir=self.fixtures_dir,
            as_of=REF_DATE,
            apply_updates=True,
            source_ids=["greenhouse-canonical"],
        )

        self.assertEqual(res["openConfirmedCount"], 1)

        updated_seed = json.loads(self.seed_path.read_text(encoding="utf-8"))
        opp = next(o for o in updated_seed["opportunities"] if o["id"] == "OP-006")
        self.assertEqual(opp["lastCheckedDate"], REF_DATE.isoformat())

        # Verify against 7-day TTL: difference between as_of and lastCheckedDate is 0 days
        diff_days = (REF_DATE - date.fromisoformat(opp["lastCheckedDate"])).days
        self.assertLessEqual(diff_days, 7)


if __name__ == "__main__":
    unittest.main()
