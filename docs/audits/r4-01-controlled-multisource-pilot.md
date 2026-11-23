# INFORME DE PILOTO DE ADQUISICIÓN CONTROLADA MULTIFUENTE — R4-01
## Integración operativa de ATS, captura reproducible y staging editorial

- **Identificador de bloque:** `R4-01`
  - `R4-01A`: Reconciliación de gobernanza y fuentes `[REFACTOR/FIX]`
  - `R4-01B`: Piloto de adquisición ATS `[INTEGRACIÓN_OSS]`
  - `R4-01C`: Orquestación reproducible de captura `[ADAPTACIÓN_OSS]`
  - `R4-01D`: Ejecución controlada y operación local `[ADAPTACIÓN_OSS]`
- **Fecha de ejecución:** 2026-11-22 (Hora Lima, UTC-5)
- **Rol y especialidades:** Principal Software Architect, Senior Software Engineer, OSS Integration Specialist, Data Acquisition Engineer, Automation Engineer & Technical Auditor
- **Proyecto:** Ruta Sistemas (`https://github.com/Blueisazul/WebRutaSistemas`)
- **Rama objetivo:** `integration/r1-02c`
- **HEAD inicial y final:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d`
- **Estado final del bloque:** **`DONE`**

---

## 1. Contexto y Resoluciones de Gobernanza

El propietario del proyecto ha autorizado expresamente la apertura e inicio de la fase **R4 (Automatización Controlada)**.

Se formalizan las siguientes decisiones rectoras de arquitectura y gobernanza:

### R3 — Alpha Privada
1. **R3-01:** Se conserva intacto el protocolo de investigación cualitativa y su cierre formal.
2. **R3-02:** Las pruebas de uso realizadas por el propietario y sus compañeros constituyen formalmente **validación interna**. La investigación formal externa con participantes protocolizados (cuotas P01 a P08) queda formalmente marcada como **`DEFERRED_BY_OWNER`** (pospuesta por decisión soberana del propietario hasta la preparación de un futuro lanzamiento público).
3. **No bloqueo de la Alpha privada:** `R3-02` no bloquea el desarrollo ni la ampliación funcional de la Alpha privada ni el inicio de la adquisición controlada en `R4`.
4. **Veracidad documental estricta:** No se afirma que se haya realizado investigación formal externa; no se inventan participantes, sesiones ni métricas de campo. Las plantillas `P01.md` a `P08.md` permanecen íntegras en `PENDING_EXECUTION`.

### R4 — Automatización Controlada
1. **Apertura autorizada:** Se autoriza el avance progresivo de R4.
2. **Incorporación selectiva:** Las fuentes se incorporan individualmente y con criterios técnicos y legales verificables.
3. **Límite de automatización:** La automatización recopila, normaliza a Candidate Schema 2, adjunta evidencias, deduplica y prepara candidatos en la bandeja de staging.
4. **Puerta editorial humana innegociable:** La publicación en el catálogo canónico continúa requiriendo revisión y aprobación editorial humana explícita (*fail-closed*). Ningún proceso automatizado escribe en `data/opportunities.seed.json` ni en `data/opportunities.json`.

---

## 2. Reconciliación Documental: Porcentaje de Fuentes Viables (R4-01A)

Se auditó la aparente discrepancia documental entre los valores de **52.9%** y **55.9%** identificados en el informe de viabilidad técnica [docs/audits/r3-source-feasibility-01-peru-2026-11-21.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-source-feasibility-01-peru-2026-11-21.md):

- **Total de fuentes evaluadas empíricamente:** Exactamente **34 fuentes** (26 de referencia inicial + 8 descubiertas).
- **Cálculo exacto de 18 fuentes:** $\frac{18}{34} = 52.941\%$ (redondeado a **52.9%**). Corresponde al conjunto estricto de fuentes con adaptabilidad directa (`READY`: 6 plataformas ATS y empleadores directos) más fuentes viables con restricciones (`READY_WITH_LIMITS`: 12 fuentes con HTML accesible o PDF institucional).
- **Cálculo exacto de 19 fuentes:** $\frac{19}{34} = 55.882\%$ (redondeado a **55.9%**). Esta cifra preliminar incluía en borradores previos a *Stefanini Perú* o *Culqi/BambooHR* bajo criterios de evaluación preliminar antes del descarte por CMS dependiente de sesión.
- **Dictamen pericial definitivo:** Se ratifica como cifra matemática y metodológicamente canónica **18 fuentes aprovechables (52.9%)** sobre las 34 evaluadas, desglosadas en 10 bloqueadas por WAF/Anti-Bot (29.4%) y 6 inalcanzables o de intranet (17.6%). No se alteran retrospectivamente los resultados empíricos registrados.

---

## 3. Selección y Habilitación de Fuentes del Piloto (R4-01B)

En estricto cumplimiento de los requisitos técnicos, éticos y de seguridad (P0), se seleccionaron **5 tableros oficiales** que reutilizan los conectores genéricos existentes (`greenhouse-job-board` y `lever-postings`), sin duplicar conectores por empresa:

| ID de Fuente | Empleador | Conector ATS OSS | Endpoint Oficial Documentado | Host Verificado | Filtro Geográfico / Perfil |
|---|---|:---:|---|:---:|:---:|
| `greenhouse-canonical` | Canonical | `greenhouse-job-board` | `https://boards-api.greenhouse.io/v1/boards/canonical/jobs` | `boards-api.greenhouse.io` | Remoto / Américas / Worldwide |
| `greenhouse-sezzle` | Sezzle | `greenhouse-job-board` | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | `boards-api.greenhouse.io` | Remoto / Perú |
| `greenhouse-cookunity` | CookUnity | `greenhouse-job-board` | `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs` | `boards-api.greenhouse.io` | Remoto / LATAM / Lima |
| `lever-fintual` | Fintual | `lever-postings` | `https://api.lever.co/v0/postings/fintual?mode=json` | `api.lever.co` | Remoto / LATAM / Chile / México |
| `lever-kavak` | Kavak | `lever-postings` | `https://api.lever.co/v0/postings/kavak?mode=json` | `api.lever.co` | Remoto / LATAM / Brasil / México |

### Verificación Técnica en Tiempo Real de los Endpoints
- **Greenhouse REST API:**
  - `canonical`: HTTP 200 OK (318 vacantes globales activas).
  - `sezzle`: HTTP 200 OK (228 vacantes globales activas).
  - `cookunity`: HTTP 200 OK (137 vacantes globales activas).
- **Lever Postings REST API:**
  - `fintual`: HTTP 200 OK (4 vacantes activas).
  - `kavak`: HTTP 200 OK (5 vacantes activas).
- **Fuentes no piloto:** Todas las demás fuentes (`talento-peru-servir`, `unmsm-fisi-employment-board`, `ositran-manual-review`, `canonical-careers`, etc.) preservan su estado inalterado (`enabled: false`, `pending_review`).

---

## 4. Arquitectura de Orquestación y Deduplicación (R4-01C)

Se diseñó e implementó el módulo [collector/acquisition_runner.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/acquisition_runner.py), integrando de forma reutilizable y sin dependencias externas:

```
[ FLUJO ORQUESTADO DE ADQUISICIÓN CONTROLADA R4-01 ]
                        │
                        ▼
    ┌───────────────────────────────────────┐
    │ 1. Carga de Registro y Políticas      │  load_source_registry()
    │    (collector/sources.json)           │  find_source()
    └───────────────────┬───────────────────┘
                        ▼
    ┌───────────────────────────────────────┐
    │ 2. Extracción ATS y Normalización     │  fetch_greenhouse_board() / fetch_lever_board()
    │    a Candidate Schema 2               │  transform_greenhouse_payload() / transform_lever_payload()
    └───────────────────┬───────────────────┘
                        ▼
    ┌───────────────────────────────────────┐
    │ 3. Filtrado por Perfil y Geografía    │  filter_candidate_for_target_profile()
    │    (Ubicación, Remoto, Nivel Junior)  │  (Descarte motivado de cargos incompatibles)
    └───────────────────┬───────────────────┘
                        ▼
    ┌───────────────────────────────────────┐
    │ 4. Deduplicación Determinista Multi-v │  deduplicate_candidates()
    │    - Contra lote actual               │  make_primary_key() [sourceId:externalRef]
    │    - Contra bandeja staging           │  make_secondary_signature() [emp|tit|loc|mod|opp]
    │    - Contra catálogo canónico (seed)  │  Cross-check contra requisiciones aprobadas
    └───────────────────┬───────────────────┘
                        ▼
    ┌───────────────────────────────────────┐
    │ 5. Validación Estructural y Evidencia │  validate_payload() [validate_candidates.py]
    │    (TTL 7 días Lima, Procedencia HTTPS)│  verify_candidates_evidence() [collector/evidence.py]
    └───────────────────┬───────────────────┘
                        ▼
    ┌───────────────────────────────────────┐
    │ 6. Persistencia Segura en Staging     │  _atomic_write_json()
    │    (Solo en bandeja local aislada)    │  Catálogo canónico 100% INTACTO
    └───────────────────────────────────────┘
```

### Componentes OSS Reutilizados:
- `collector/ats_connectors.py`: Conectores nativos Greenhouse y Lever.
- `collector/dedup.py`: Deduplicación exacta y por firma secundaria sin algoritmos probabilísticos.
- `collector/evidence.py`: Verificación estricta de procedencia HTTPS y cálculo de frescura temporal.
- `collector/policy.py`: Autorización estricta de hosts permitidos, presupuestos y esquemas.
- `scripts/validate_candidates.py`: Validador canónico de Schema 2.

---

## 5. Operación Local y Ejecución por CLI (R4-01D)

Se extendió la CLI editorial [scripts/editorial_cli.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/scripts/editorial_cli.py) con el subcomando `acquire`:

```bash
# Ayuda y sintaxis del comando
python scripts/editorial_cli.py acquire --help

# Ejecución de simulación (Dry-Run) con fixtures reproducibles offline
python scripts/editorial_cli.py acquire --fixtures-dir tests/fixtures/ats --as-of 2026-11-22 --dry-run

# Ejecución de una fuente individual
python scripts/editorial_cli.py acquire --source greenhouse-canonical --fixtures-dir tests/fixtures/ats --dry-run

# Ejecución real contra API en vivo
python scripts/editorial_cli.py acquire --source lever-fintual --as-of 2026-11-22 --dry-run
```

### Características Operativas Verificadas:
1. **Ejecución multivariable:** Permite ejecutar la totalidad de fuentes piloto o una fuente específica (`--source <id>`).
2. **Aislamiento de fallos (*Fault-Tolerance*):** Si una fuente experimenta timeout, error HTTP 404/500 o fallo de transporte, el error se registra en el sumario y la orquestación continúa procesando las demás fuentes sin abortar el proceso.
3. **Idempotencia estricta:** Una segunda ejecución sobre el mismo lote detecta el 100% de duplicados y añade exactamente 0 registros redundantes a staging.
4. **Trazabilidad y métricas completas:** Registro de marca temporal ISO, fecha de corte Lima, capturados, filtrados, descartados, duplicados y nuevos.
5. **Generación de informe estructurado:** Admite `--json-report` por stdout o persistencia mediante `--output <path>`.

---

## 6. Resultados de las Pruebas y Aseguramiento Técnico

### Suite de Pruebas Unitarias e Integración (Python)
Se ejecutó la suite completa incluyendo las 10 nuevas pruebas específicas de [tests/test_acquisition_pilot.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/test_acquisition_pilot.py):
- **Total pruebas unitarias e integración ejecutadas:** **203 pruebas** (ampliada de 193).
- **Resultado:** **`203 passed in 3.41s. OK.`**
- **Cobertura de pruebas del piloto:**
  - `test_registry_contains_approved_pilot_sources`: Conforme.
  - `test_legacy_and_unapproved_sources_remain_disabled`: Conforme.
  - `test_candidate_filtering_respects_geographic_filters`: Conforme.
  - `test_orchestration_with_fixtures_captures_normalizes_and_stages`: Conforme.
  - `test_orchestration_idempotency_second_run_produces_zero_duplicates`: Conforme.
  - `test_orchestration_isolates_source_failure_and_continues`: Conforme.
  - `test_orchestration_handles_http_errors_gracefully`: Conforme.
  - `test_deduplication_against_canonical_seed_opportunities`: Conforme.
  - `test_cli_acquire_dry_run_does_not_modify_inbox`: Conforme.
  - `test_cli_acquire_json_report_output`: Conforme.

### Suite de Pruebas E2E (Playwright)
- **Total pruebas Playwright ejecutadas:** **20 pruebas** (10 Chromium Desktop + 10 Mobile Pixel 5).
- **Resultado:** **`20 passed. OK.`** (Cero regresiones en la interfaz de catálogo, detalle, paginación y comparador).

### Verificación de Contratos y Esquemas
- `python scripts/validate_catalog.py`: Válido (15 fichas canónicas, modo no vacío).
- `python scripts/build_catalog.py --check`: Catálogo válido (15 registros, snapshot sincronizado).
- `python scripts/validate_candidates.py data/candidates/inbox.local.json --as-of 2026-11-22`: Válido (24 candidatos conformes en staging).
- `node tests/catalog_ui.test.cjs`: Conforme.
- `git diff --check`: 0 errores de sintaxis o espacios.

---

## 7. Integridad Canónica Criptográfica

| Archivo Auditado | Estado | Hash SHA-256 Verificado |
|---|:---:|---|
| `data/opportunities.seed.json` | **100% INTACTO** | `cfa5f73257ac92738d1973b8acced4e04b42b9bfaa439bb93d6adb3ad147201a` |
| `data/opportunities.json` | **100% INTACTO** | `f5649e59863b0ee600627348fe8f72f74ae02539a06d70bb4a311380dc2e1bbb` |
| `collector/sources.json` | **Actualizado (5 fuentes piloto añadidas)** | Modificación controlada de configuración |
| `collector/acquisition_runner.py` | **Nuevo módulo OSS** | Orquestador de adquisición multifuente |
| `tests/test_acquisition_pilot.py` | **Nueva suite de pruebas** | 10 pruebas unitarias/integración |

- **Nuevas dependencias:** **0** (0 npm, 0 pip añadidos).
- **Despliegues externos:** **0** (Sin push remoto, sin merge a `main`, sin commit, sin GitHub Pages).

---

## 8. Estado del Roadmap y Siguiente Bloque Recomendado

- **R3 — Alpha Privada:**
  - `R3-01`: `DONE` (Cierre preservado).
  - `R3-02`: `DEFERRED_BY_OWNER` para trabajo de campo formal externo; validación interna completada satisfactoriamente con el propietario y círculo cercano.
  - `R3-03`, `R3-04`, `R3-05`: Permanecen en pausa hasta la futura preparación para audiencia general.
- **R4 — Automatización Controlada:**
  - `R4-01`: **`DONE`** (Piloto de adquisición controlada multifuente operativo, reproducible y validado).
- **Siguiente paso recomendado:**
  - `R4-02 — INGESTA DE STAGING Y EVALUACIÓN DE CANDIDATOS DEL PILOTO`: Ejecutar una primera sesión formal de adquisición sobre las 5 fuentes piloto aprobadas para poblar la bandeja de staging, documentar descartes técnicos y preparar el expediente de revisión humana para la próxima promoción editorial.
