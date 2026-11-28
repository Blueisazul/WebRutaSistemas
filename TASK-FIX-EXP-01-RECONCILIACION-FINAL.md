# TASK-FIX-EXP-01 · RECONCILIACIÓN FINAL DEL WORKSPACE Y PREPARACIÓN DE CONSOLIDACIÓN

**Proyecto:** Velora (`WebRutaSistemas`)  
**Tarea:** `TASK-FIX-EXP-01`  
**Prioridad:** P0 — Confiabilidad y veracidad del catálogo  
**Modo:** READ-ONLY · AUDITORÍA DE ESTADO · SIN MODIFICACIONES  
**Fecha y Hora de Inspección:** 27 de noviembre de 2026, 21:26 (UTC-5 / America/Lima)  
**Ruta del Workspace:** `c:\Users\sant1\Downloads\EmpleoWeb`  

---

## 1. IDENTIDAD GIT Y CRONOLOGÍA COMPROBADA (FASE A)

### 1.1 Estado Actual de Git
- **Rama activa:** `main`
- **HEAD actual:** `dca999d92d1b9ee1831e6d19a4c0865e584c8474`
- **origin/main:** `dca999d92d1b9ee1831e6d19a4c0865e584c8474`
- **Diferencia HEAD...origin/main:** `0 0` (0 commits adelante, 0 commits atrás).
- **Estado de Staging (`index`):** Vacío (`git diff --cached` retorna vacío). Ningún archivo se encuentra preparado para commit.
- **Commit local pendiente de publicación:** **NINGUNO**. No existe ningún commit local retenido o pendiente de push. Todos los commits locales hasta `dca999d` ya están integrados en `origin/main` en GitHub.

### 1.2 Contrastación con Estados Históricos
1. `6b754daff24687c754dda94c303bb06a7e062732`: Commit correspondiente al cierre de release `v0.7.0` (`docs(release): publish TASK-R7-RELEASE-EXECUTION report and update master roadmap`). Ancestro directo de `f861e06`.
2. `f861e06899604bd08dcd8f05c6a4244c6621c308`: Commit de consolidación técnica de `TASK-FIX-URL-01` y `TASK-R5-05` (`feat(catalog): consolidate URL remediation and geographic filters`). Ancestro directo de `dca999d`.
3. `dca999d92d1b9ee1831e6d19a4c0865e584c8474`: Commit de remediación de pruebas E2E `TASK-FIX-E2E-R5-05` (`fix(e2e): update geographic summary card expectations (TASK-FIX-E2E-R5-05)`). **Es el HEAD real actual tanto en el repositorio local como en origin/main**.

**Conclusión Cronológica Demostrada:**  
Los cambios de `TASK-FIX-EXP-01` (y los cambios no integrados de R5) residen **exclusivamente en el árbol de trabajo local (working tree)**. No han sido comprometidos en ningún commit local ni empujados a ningún remoto.

---

## 2. INVENTARIO DEL ÁRBOL DE TRABAJO (FASE B)

### 2.1 Archivos Modificados Rastreados (20 archivos):
1. `.gitignore`
2. `app.js`
3. `collector/evidence.py`
4. `collector/pe_connectors.py`
5. `collector/revalidation.py`
6. `collector/sources.json`
7. `docs/audits/TASK-FIX-E2E-R5-05.md`
8. `docs/audits/VELORA-OPEN-DECISIONS.md`
9. `docs/audits/VELORA-PRE-RELEASE-URL-GEOGRAPHY-CONSOLIDATION.md`
10. `docs/roadmap/VELORA-MASTER-ROADMAP.md`
11. `scripts/catalog_quality.py`
12. `scripts/editorial_cli.py`
13. `tests/catalog_ui.test.cjs`
14. `tests/e2e/catalog.spec.cjs`
15. `tests/test_acquisition_pilot.py`
16. `tests/test_autopublish.py`
17. `tests/test_classification_and_coverage.py`
18. `tests/test_pe_connectors.py`
19. `tests/test_periodic_acquisition_ops.py`
20. `tests/test_source_evaluation.py`

### 2.2 Archivos Nuevos No Rastreados (`??`, 9 archivos):
1. `tests/test_lifecycle_expiration.py` *(TASK-FIX-EXP-01)*
2. `docs/audits/TASK-FIX-EXP-01.md` *(TASK-FIX-EXP-01)*
3. `collector/assisted_discovery.py` *(TASK-R5-04-03)*
4. `tests/test_assisted_discovery.py` *(TASK-R5-04-03)*
5. `docs/audits/R5-02-SERVIR-OFFICIAL-ENDPOINT-INVESTIGATION.md` *(TASK-R5-02)*
6. `docs/audits/R5-04-02-SECONDARY-SOURCES-RESEARCH.md` *(TASK-R5-04-02)*
7. `docs/audits/R5-04-03-ASSISTED-DISCOVERY-PILOT.md` *(TASK-R5-04-03)*
8. `docs/audits/TASK-R5-04-02-EDITORIAL-REVIEW.md` *(TASK-R5-04-02)*
9. `docs/audits/TASK-R5-04-02-FIELD-VALIDATION.md` *(TASK-R5-04-02)*

### 2.3 Archivos Eliminados:
- **0 archivos**.

### 2.4 Archivos Ignorados Relevantes (`!!`):
- `data/candidates/inbox.local.json` (bandeja de staging de candidatos; protegida por `.gitignore`).
- `data/candidates/radar_discovery.local.json` (bandeja de radar; protegida por `.gitignore`).
- `data/opportunities.sqlite3`, `node_modules/`, `test-results/`, `__pycache__/`.

---

## 3. MATRIZ DE SEGREGACIÓN POR TAREA (FASE C)

| Archivo | Estado Git | Tarea atribuida | Evidencia técnica real | Confianza | Acción propuesta |
|---|---|---|---|---|---|
| `app.js` | `M` | `TASK-FIX-EXP-01` | Lógica `isDeadlineExpired`, forzado de `expired`/`historical`, desactivación de botones CTA de postulación, métricas. | Alta | **Conservar para consolidación** |
| `collector/evidence.py` | `M` | `TASK-FIX-EXP-01` | Soporte de timestamps ISO 8601 con zona horaria en la sección 6 de vigencia. | Alta | **Conservar para consolidación** |
| `collector/revalidation.py` | `M` | `TASK-FIX-EXP-01` | Evaluación de expiración de deadline antes de confirmar vacante como abierta; habilitación de fixtures offline. | Alta | **Conservar para consolidación** |
| `scripts/catalog_quality.py` | `M` | `TASK-FIX-EXP-01` | Admisión de `withdrawn` en `OPPORTUNITY_STATES`, `parse_date` con ISO 8601 y validación de expiración. | Alta | **Conservar para consolidación** |
| `tests/test_lifecycle_expiration.py` | `??` | `TASK-FIX-EXP-01` | Suite unitaria dedicada (11 pruebas) cubriendo fechas civiles, timestamps, separación de fin de contrato y retiro de Greenhouse. | Alta | **Conservar para consolidación** |
| `docs/audits/TASK-FIX-EXP-01.md` | `??` | `TASK-FIX-EXP-01` | Informe de auditoría técnica pre-release de la tarea. | Alta | **Conservar para consolidación** |
| `tests/catalog_ui.test.cjs` | `M` | `TASK-FIX-EXP-01` | Suite de pruebas Node VM validando `isDeadlineExpired`, degradación a histórico y conteo en métricas. | Alta | **Conservar para consolidación** |
| `tests/e2e/catalog.spec.cjs` | `M` | `TASK-FIX-EXP-01` | Timeout defensivo de 10s en la navegación a `#QA-001`. | Alta | **Conservar para consolidación** |
| `tests/test_acquisition_pilot.py` | `M` | `TASK-FIX-EXP-01` | Aserción de que fuentes Greenhouse están retiradas y solo Lever permanece activa para el piloto ATS. | Alta | **Conservar para consolidación** |
| `tests/test_autopublish.py` | `M` | `TASK-FIX-EXP-01` | Adaptación de fixtures de autopublicación a la fuente autorizada `lever-kavak` (reemplazando `greenhouse-encora`). | Alta | **Conservar para consolidación** |
| `tests/test_classification_and_coverage.py` | `M` | `TASK-FIX-EXP-01` | Ajuste de aserción a 10 fuentes aprobadas limpias (excluyendo las 4 Greenhouse retiradas). | Alta | **Conservar para consolidación** |
| `tests/test_periodic_acquisition_ops.py` | `M` | `TASK-FIX-EXP-01` | Ajuste de métricas a 10 fuentes activas evaluadas en el piloto periódico. | Alta | **Conservar para consolidación** |
| `tests/test_source_evaluation.py` | `M` | `TASK-FIX-EXP-01` | Aserción de que `canonical-careers` tiene estado `withdrawn` (en lugar de `pending_review`). | Alta | **Conservar para consolidación** |
| `collector/sources.json` | `M` | **Compartido** | Hunks 1 a 6: Retirada de 6 fuentes Greenhouse (`decision: "withdrawn"`). Hunk 7: Fuentes secundarias radar `postulate-pe-radar` y `laboral-pe-radar` (`TASK-R5-04-02`). | Alta | **Separar selectivamente por hunks** (incluir hunks 1-6; excluir hunk 7) |
| `docs/audits/VELORA-OPEN-DECISIONS.md` | `M` | **Compartido** | Decisiones 10 (Retirada Greenhouse) y 11 (Ciclo de vida y expiración). Decisiones 8 (HiringRoom) y 9 (Criterio temporal) de R5. | Alta | **Separar selectivamente por hunks** (incluir Decisiones 10 y 11) |
| `docs/roadmap/VELORA-MASTER-ROADMAP.md` | `M` | **Compartido** | Entrada de `TASK-FIX-EXP-01` bajo `COMPLETED_VERIFIED [Local] — Pendiente de consolidación`. Sección de cierre de `TASK-FIX-E2E-R5-05` (commit `dca999d`). | Alta | **Separar selectivamente por hunks** (incluir bloque de `TASK-FIX-EXP-01`) |
| `collector/pe_connectors.py` | `M` | `TASK-R5-03` | Conector `fetch_hiringroom_board`, límite duro de 15 peticiones y retardo de 1500 ms (Decisión 8). | Alta | **Separar / Preservar intacto en working tree** |
| `tests/test_pe_connectors.py` | `M` | `TASK-R5-03` | Pruebas unitarias de límites de tasa y 20 candidatos en staging de HiringRoom. | Alta | **Separar / Preservar intacto en working tree** |
| `scripts/editorial_cli.py` | `M` | `TASK-R5-04-03` | Subcomandos de radar `radar-record`, `radar-verify` y `radar-promote`. | Alta | **Separar / Preservar intacto en working tree** |
| `.gitignore` | `M` | `TASK-R5-04-03` | Regla `+data/candidates/radar_discovery.local.json`. | Alta | **Separar / Preservar intacto en working tree** |
| `collector/assisted_discovery.py` | `??` | `TASK-R5-04-03` | Módulo del piloto de descubrimiento asistido. | Alta | **Separar / Preservar intacto en working tree** |
| `tests/test_assisted_discovery.py` | `??` | `TASK-R5-04-03` | Pruebas del piloto de descubrimiento asistido. | Alta | **Separar / Preservar intacto en working tree** |
| `docs/audits/R5-02-*` (1 archivo) | `??` | `TASK-R5-02` | Investigación técnica de SERVIR / Talento Perú. | Alta | **Separar / Preservar intacto en working tree** |
| `docs/audits/R5-04-*` (4 archivos) | `??` | `TASK-R5-04-02` | Informes de investigación y prueba de campo de fuentes secundarias. | Alta | **Separar / Preservar intacto en working tree** |
| `docs/audits/TASK-FIX-E2E-R5-05.md` | `M` | `TASK-FIX-E2E-R5-05` | Documentación retrospectiva de la remediación ya desplegada en `dca999d`. | Alta | **Separar / Preservar intacto en working tree** |
| `docs/audits/VELORA-PRE-RELEASE-URL-GEOGRAPHY-CONSOLIDATION.md` | `M` | `Consolidación previa` | Documentación retrospectiva del commit `f861e06`. | Alta | **Separar / Preservar intacto en working tree** |
| `data/candidates/inbox.local.json` | `!!` | Staging local | 236 candidatos Greenhouse en `rejected`. 20 candidatos HiringRoom en `pending_review`. Ignorado por `.gitignore`. | Alta | **Conservar localmente sin versionar** |

---

## 4. EVIDENCIA SOBRE EXPIRACIÓN Y DECISIÓN 9 (FASE D)

La inspección directa del código fuente local demuestra el cumplimiento estricto de las reglas temporales:

1. **Semántica de fecha civil en `America/Lima`:**
   - En `app.js` (`isDeadlineExpired`): si el valor es `YYYY-MM-DD`, se compara contra `limaDateString(referenceDate)`. La condición de vencimiento es estrictamente `trimmed < todayStr`. Por tanto, si `deadline == todayStr`, la función retorna `false` (vigente durante todo el día civil, respetando la Decisión 9).
2. **Semántica de timestamp ISO 8601:**
   - Si incluye hora (`/^\d{4}-\d{2}-\d{2}T/`), se convierte a timestamp numérico y expira en el instante exacto (`parsed.getTime() < referenceDate.getTime()`).
3. **Tratamiento conservador de fechas ausentes:**
   - Si `deadline` es `null`, `undefined` o cadena vacía, `isDeadlineExpired` retorna `false`. No se marca como vencida por inferencia.
4. **Desacoplamiento total:**
   - `deadline` no se confunde con `employmentEndDate` (fin de contrato), ni con `lastVerifiedAt`, ni con el TTL de verificación de 7 días.
5. **Comportamiento en UI y llamadas a la acción:**
   - En tarjetas (`renderCard`), detalle (`renderDetailContent`) y comparador (`renderComparison`), toda oportunidad en estado `expired`, `closed` o `withdrawn` recibe `aria-disabled="true"` y se despoja de atributos `href` interactivos.
   - En métricas (`publicCatalogMetrics`), las vacantes `expired`, `closed` y `withdrawn` computan exclusivamente bajo `expiredOrHistorical`, excluidas de las vacantes activas.
6. **Retirada de Greenhouse sin pérdida histórica:**
   - 6 fuentes Greenhouse retiradas (`decision: "withdrawn"`).
   - 236 candidatos en staging pasados a `rejected` (0 en `pending_review`).
   - Registros históricos canónicos de Canonical o CookUnity preservados intactos en `data/opportunities.seed.json`.

---

## 5. ESTADO ACTUAL DE LAS PRUEBAS

Ejecutadas en la sesión de auditoría:
- `node --check app.js`: **0 errores de sintaxis**.
- `python scripts/validate_catalog.py`: **112 fichas conformes (100% OK)**.
- `python scripts/build_catalog.py --check --as-of 2026-11-23`: **Paridad bit a bit certificada**.
- `python -m unittest tests/test_lifecycle_expiration.py`: **11/11 aprobadas al 100%**.
- `node tests/catalog_ui.test.cjs`: **16/16 escenarios aprobados al 100%**.
- `python -m unittest discover -s tests`: **356/356 pruebas aprobadas al 100% en 9.64s**.
- `npx playwright test tests/e2e/catalog.spec.cjs`: **30/30 pruebas E2E aprobadas en 3.7m**.

---

## 6. RIESGOS Y ARCHIVOS QUE DEBEN PRESERVARSE

1. **Riesgo de inclusión accidental de HiringRoom (`TASK-R5-03`):**
   - [collector/pe_connectors.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/pe_connectors.py) y [tests/test_pe_connectors.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/test_pe_connectors.py) contienen el conector con límite duro de 15 peticiones y retardo de 1500 ms.
   - **Acción:** No indexar estos archivos. Permanecen intactos en el working tree.
2. **Riesgo de inclusión accidental de Descubrimiento Asistido (`TASK-R5-04-03`):**
   - `scripts/editorial_cli.py`, `collector/assisted_discovery.py`, `tests/test_assisted_discovery.py` y el Hunk 7 de `collector/sources.json`.
   - **Acción:** No indexar estos archivos ni el Hunk 7. Permanecen intactos en el working tree.
3. **Riesgo de alteración de la bandeja de staging:**
   - `data/candidates/inbox.local.json` es ignorado por `.gitignore`.
   - **Acción:** No forzar su indexación (`git add -f`). Mantenerlo estrictamente como dato de trabajo local.
4. **Riesgo de mutación de datos canónicos:**
   - `data/opportunities.seed.json` y `data/opportunities.json` están intactos.
   - **Acción:** Ninguna regla de expiración debe editar estos archivos para forzar estados.

---

## 7. DICTAMEN FINAL

### **`READY_FOR_SELECTIVE_CONSOLIDATION`**

**Demostración inequívoca:**  
Es técnica y operativamente posible consolidar **exclusivamente `TASK-FIX-EXP-01`** sin mezclar, perder ni publicar accidentalmente cambios de otras tareas. Los cambios ajenos se encuentran en archivos independientes o en fragmentos perfectamente acotados que pueden excluirse de la preparación sin riesgo de regresión ni conflicto.

---

## 8. PLAN EXACTO DE CONSOLIDACIÓN SELECTIVA (PROPUESTA TEXTUAL · NO EJECUTADA)

Cuando el propietario autorice la consolidación, los comandos exactos a ejecutar son:

### Paso 1: Indexar archivos exclusivos de código y pruebas (12 archivos)
```bash
git add app.js
git add collector/evidence.py
git add collector/revalidation.py
git scripts/catalog_quality.py
git add tests/test_lifecycle_expiration.py
git add tests/catalog_ui.test.cjs
git add tests/e2e/catalog.spec.cjs
git add tests/test_acquisition_pilot.py
git add tests/test_autopublish.py
git add tests/test_classification_and_coverage.py
git add tests/test_periodic_acquisition_ops.py
git add tests/test_source_evaluation.py
```

### Paso 2: Indexar selectivamente por hunks `collector/sources.json`
Indexar los Hunks 1 al 6 (retirada de fuentes Greenhouse) y omitir el Hunk 7 (radares secundarios de R5-04):
```bash
git add -p collector/sources.json
# Seleccionar 'y' para los 6 bloques de Greenhouse y 'n' para el bloque final de postulate-pe y laboral-pe.
```

### Paso 3: Indexar reportes de auditoría y gobernanza de la tarea
```bash
git add docs/audits/TASK-FIX-EXP-01.md
git add TASK-FIX-EXP-01-RECONCILIACION-FINAL.md
git add -p docs/audits/VELORA-OPEN-DECISIONS.md
# Seleccionar 'y' en los hunks de Decisiones 10 y 11; 'n' en Decisiones 8 y 9.
git add -p docs/roadmap/VELORA-MASTER-ROADMAP.md
# Seleccionar 'y' en la entrada de TASK-FIX-EXP-01.
```

### Paso 4: Certificar el contenido del índice antes de crear el commit
```bash
git diff --cached --stat
# Debe listar exclusivamente los archivos de TASK-FIX-EXP-01 (15 archivos).
# collector/pe_connectors.py, tests/test_pe_connectors.py y scripts/editorial_cli.py NO deben aparecer.
```

### Paso 5: Creación del commit consolidado (Solo bajo autorización del propietario)
```bash
git commit -m "fix(catalog): enforce strict opportunity deadline expiration and withdraw greenhouse (TASK-FIX-EXP-01)"
```

---

## 9. SIGUIENTE ACCIÓN RECOMENDADA

Presentar este informe al propietario y solicitar su **autorización explícita para ejecutar el Plan de Consolidación Selectiva de `TASK-FIX-EXP-01`** (Paso 1 al Paso 5), manteniendo inalterados en el árbol de trabajo los desarrollos de HiringRoom y Descubrimiento Asistido.
