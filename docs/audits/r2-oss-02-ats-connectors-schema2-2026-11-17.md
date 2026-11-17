# R2-OSS-02 — Informe de Adaptación de Conectores ATS a Schema 2
**Proyecto:** Ruta Sistemas  
**Fecha de ejecución:** 2026-11-17  
**Rama:** `integration/r1-02c`  
**Commit base:** `5489715`  
**Roles del auditor e ingeniero:** Principal Software Architect, Senior Python Engineer, OSS Integration Specialist, Data Pipeline Engineer, Software Quality Engineer, Technical Auditor, Engineering Lead.

---

## 1. Resumen Ejecutivo

- **[HECHO] Conectores ATS adaptados con éxito a Schema 2:** Se refactorizaron los adaptadores para Greenhouse (`greenhouse-job-board`) y Lever (`lever-postings`) en [collector/ats_connectors.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/ats_connectors.py) para transformar cargas JSON crudas en fichas de candidatos compatibles al 100% con el esquema de candidatos canónico Schema 2 y con [scripts/validate_candidates.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/scripts/validate_candidates.py).
- **[HECHO] Desacoplamiento estricto de I/O y normalización:** Se crearon las funciones puras `transform_greenhouse_payload()` y `transform_lever_payload()`, permitiendo ejecución, pruebas y validaciones 100% locales y offline sin solicitudes de red.
- **[HECHO] Cero dependencias nuevas:** La adaptación se realizó utilizando exclusivamente la biblioteca estándar de Python (`urllib.parse`, `datetime`, `json`), cumpliendo la restricción estricta de no incorporar Scrapy, Crawlee, selectolax ni otras dependencias externas en este bloque.
- **[HECHO] Batería de fixtures sintéticos completa:** Se generaron 14 fixtures JSON sintéticos en `tests/fixtures/ats/` cubriendo casos completos, valores nulos, campos opcionales ausentes, URLs inválidas/inseguras, identificadores ausentes, fechas inválidas, duplicados en lote y respuestas malformadas.
- **[HECHO] Aprobación total de pruebas:** La suite de pruebas de Python aumentó de 57 a 75 pruebas unitarias (`Ran 75 tests in 2.131s: OK`). La suite Playwright E2E aprobó 8/8 pruebas (`8 passed`).
- **[HECHO] Integridad garantizada:** La semilla canónica ([data/opportunities.seed.json](file:///c:/Users/sant1/Downloads/EmpleoWeb/data/opportunities.seed.json)) y el snapshot público ([data/opportunities.json](file:///c:/Users/sant1/Downloads/EmpleoWeb/data/opportunities.json)) permanecieron intactos byte por byte.

---

## 2. Estado Inicial (Fase 0 — Inspección)

- **Rama:** `integration/r1-02c`
- **Commit HEAD:** `54897155a5069207ce7b798f6f96d00600209225`
- **Working Tree:** Limpio en código funcional y datos; modificaciones previas limitadas a documentación de auditoría y cierre R1.
- **Archivos inspeccionados:**
  - `collector/ats_connectors.py`
  - `collector/policy.py`
  - `collector/sources.json`
  - `collector/refresh_catalog.py`
  - `scripts/validate_candidates.py`
  - `scripts/build_catalog.py`
  - `scripts/catalog_quality.py`
  - `data/candidates/inbox.example.json`
  - `data/candidates/README.md`
  - `tests/test_candidates.py`
  - `tests/test_source_evaluation.py`
  - `tests/test_catalog_quality.py`

---

## 3. Diagnóstico Técnico

### 3.1. Conectores existentes en el repositorio
- `greenhouse-job-board`: Conector para la API pública de vacantes de Greenhouse (`https://boards-api.greenhouse.io/v1/boards/{boardToken}/jobs`).
- `lever-postings`: Conector para la API pública de vacantes de Lever (`https://api.lever.co/v0/postings/{site}?mode=json`).
- Otros registros en `collector/sources.json`: `manual-review` (SERVIR, FISI UNMSM, OSITRAN, Canonical) y `disabled` (Freehire). No existen otros adaptadores de código funcional ATS en el repositorio.

### 3.2. Discrepancias frente a Schema 2 identificadas antes de la intervención
1. **Emisión de campos prohibidos:** El conector anterior delegaba en `public_record_from_posting()` de `collector/policy.py`, el cual emitía `"verificationStatus": "unverified"` y `"publicationStatus": "unknown"`. En Schema 2, los candidatos tienen expresamente prohibido declarar estados de verificación o publicación del catálogo (`opportunityStatus`, `verificationStatus`, `publicationStatus`, `lastVerifiedAt`).
2. **Estructura plana y desalineada:** Emitía campos raíz (`departments`, `offices`, `canonicalUrl`) en lugar de agrupar los datos en el objeto `proposed` con campos estrictos (`title`, `employer`, `publisher`, `externalReference`, `applyUrl`, `location`, `mode`, etc.).
3. **Ausencia total de evidencias por campo (`fieldEvidence`):** El conector no generaba la lista de evidencias HTTPS con timestamp de observación requerida por `scripts/validate_candidates.py`.
4. **Ausencia de `editorialReview`:** No incluía el bloque obligatorio `{ status: "pending_review", reviewer: null, reviewedAt: null, decisionNote: null }`.
5. **Acoplamiento de red:** La lógica de transformación estaba incrustada dentro de las funciones de fetch HTTP, imposibilitando procesar fixtures offline de forma limpia.

---

## 4. Implementación y Decisiones Técnicas (Fases 1 y 2)

### 4.1. Archivos modificados y creados
- **Modificado:** [collector/ats_connectors.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/ats_connectors.py) (refactorización completa modular a Schema 2).
- **Creado:** [tests/test_ats_connectors.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/test_ats_connectors.py) (suite exhaustiva de 18 pruebas automatizadas).
- **Creado:** `tests/fixtures/ats/*.json` (14 archivos de fixtures sintéticos).

### 4.2. Responsabilidad de las funciones implementadas
- `_safe_str(val)`: Sanitización de cadenas; devuelve cadena limpia o `None` (evita cadenas vacías no significativas).
- `_is_valid_https_url(url)`: Validador estricto de URLs HTTPS con netloc y sin credenciales incrustadas.
- `_empty_proposed()`: Generador de plantilla con todas las 13 claves de `PROPOSED_FIELDS` inicializadas en `None`.
- `_build_candidate_record()`: Ensamblador del contrato canónico de candidato Schema 2:
  - Genera `candidateId`: `CAND-{sourceId}-{externalReference}`.
  - Asigna `captureMethod`: `"manual"` (requerido por el validador vigente mientras no existan fuentes formalmente aprobadas).
  - Ensambla `fieldEvidence`: genera automáticamente una entrada `{ field, url, observedAt }` para cada campo propuesto con valor no nulo, garantizando correspondencia biunívoca.
  - Fija `editorialReview.status`: `"pending_review"`.
  - Omite cualquier campo de estado de catálogo.
- `transform_greenhouse_payload(source, payload, *, captured_at, source_url)`:
  - Transforma de forma determinista y pura el payload de Greenhouse.
  - Deduplica registros por `externalReference` dentro del mismo lote.
  - Mapea modalidad `"Remoto"` si la ubicación indica explícitamente `"Remote"` o `"Remoto"`; en caso contrario, preserva `mode = None` (no inventa modalidades).
  - Valida que `absolute_url` sea HTTPS y su dominio pertenezca a `allowedPostingHosts` o `allowedHosts`.
- `transform_lever_payload(source, payload, *, captured_at, source_url)`:
  - Transforma de forma determinista el payload de Lever.
  - Extrae `location`, `commitment` (hacia `opportunityType`) y `workplaceType` (mapeo a `"Remoto"`, `"Híbrido"` o `"Presencial"`).
  - Convierte marcas de tiempo epoch `createdAt` (milisegundos) a fechas civiles `YYYY-MM-DD` en UTC (validando rango razonable de años).
  - Prioriza el canal directo de postulación (`applyUrl`) sobre `hostedUrl`.
- `fetch_greenhouse_board()` y `fetch_lever_board()`:
  - Conservan la política fail-closed mediante `_checked_url()` y `_fetch_json()`.
  - Fallan inmediatamente si la fuente no está autorizada, impidiendo tráfico de red.

---

## 5. Fixtures Locales Sintéticos (Fase 3)

Se crearon 14 fixtures exclusivamente sintéticos con empresas, cargos y URLs ficticias en `tests/fixtures/ats/`:

| Fixture | ATS | Caso de prueba cubierto |
| :--- | :--- | :--- |
| `greenhouse_complete.json` | Greenhouse | Registro completo, múltiples cargos, ubicación local y remota |
| `greenhouse_missing_optional.json` | Greenhouse | Campos opcionales ausentes (sin ubicación, departamentos ni oficinas) |
| `greenhouse_null_values.json` | Greenhouse | Valores nulos explícitos en ubicación y metadatos |
| `greenhouse_invalid_urls.json` | Greenhouse | URLs HTTP inseguras, dominios no permitidos y URLs malformadas |
| `greenhouse_missing_id.json` | Greenhouse | Identificadores ausentes, títulos vacíos o IDs nulos |
| `greenhouse_duplicates.json` | Greenhouse | Trabajos con el mismo ID en el mismo feed |
| `greenhouse_malformed.json` | Greenhouse | Respuesta no válida (dict de error en vez de `{"jobs": [...]}`) |
| `lever_complete.json` | Lever | Registro completo con `createdAt`, `categories`, `workplaceType` |
| `lever_missing_optional.json` | Lever | Sin categorías, sin workplaceType, sin fechas |
| `lever_null_values.json` | Lever | Valores nulos explícitos en categorías y fechas |
| `lever_invalid_dates.json` | Lever | Fechas epoch negativas, cadenas no numéricas y fechas desbordadas |
| `lever_invalid_urls.json` | Lever | URLs HTTP inseguras, dominios externos no permitidos y vacías |
| `lever_duplicates.json` | Lever | Postings con ID duplicado en el mismo feed |
| `lever_malformed.json` | Lever | Respuesta no válida (objeto de error en vez de lista) |

---

## 6. Pruebas y Validación (Fases 4 y 5)

### 6.1. Ejecución de pruebas unitarias y de regresión
```bash
# 1. Batería de pruebas Python (incluye las 18 nuevas pruebas de conectores)
python -m unittest discover -s tests -p "test_*.py"
Ran 75 tests in 2.131s: OK

# 2. Batería E2E Playwright
npx playwright test
8 passed (5.4s)
```

### 6.2. Cobertura de las 18 nuevas pruebas en `tests/test_ats_connectors.py`
1. `test_greenhouse_complete_produces_valid_schema2_candidates`: Verificación de campos obligatorios, evidencia por campo y compatibilidad con `validate_payload` (0 errores).
2. `test_greenhouse_missing_optional_does_not_invent_data`: Garantiza que campos ausentes permanecen `None`.
3. `test_greenhouse_null_values_are_handled_gracefully`: Manejo robusto sin excepciones de valores `null`.
4. `test_greenhouse_invalid_and_insecure_urls_are_skipped`: Omisión segura de URLs inseguras o fuera de allowlist.
5. `test_greenhouse_missing_identifiers_are_skipped`: Omisión de ofertas sin ID o sin título.
6. `test_greenhouse_duplicate_jobs_in_batch_are_deduplicated`: Deduplicación en lote para evitar colisiones de `candidateId`.
7. `test_greenhouse_malformed_shape_raises_error`: Detección explícita de respuestas malformadas.
8. `test_lever_complete_produces_valid_schema2_candidates`: Mapeo completo de categorías, fechas, modalidad y compatibilidad con `validate_payload` (0 errores).
9. `test_lever_missing_optional_does_not_invent_data`: Validación de no invención de datos.
10. `test_lever_null_values_are_handled_gracefully`: Manejo de campos nulos en Lever.
11. `test_lever_invalid_dates_remain_null`: Fechas anómalas no rompen el adaptador y quedan como `None`.
12. `test_lever_invalid_urls_are_skipped`: Omisión de URLs inválidas en Lever.
13. `test_lever_duplicate_postings_are_deduplicated`: Deduplicación en lote de Lever.
14. `test_lever_malformed_shape_raises_error`: Detección explícita de errores de forma.
15. `test_forbidden_catalog_fields_are_absent`: Verificación estricta de que ningún candidato contiene `verificationStatus`, `publicationStatus`, etc.
16. `test_fetch_functions_fail_closed_without_network_when_unauthorized`: Demostración de fallo preventivo en `fetch_greenhouse_board` y `fetch_lever_board` cuando la fuente no está autorizada.
17. `test_canonical_seed_and_snapshot_remain_unchanged`: Verificación de inmutabilidad de la semilla y el snapshot.
18. `test_local_end_to_end_inbox_integration_via_cli`: Prueba de integración local completa (fixture $\to$ conector $\to$ archivo `inbox.local.json` $\to$ ejecución CLI `scripts/validate_candidates.py` con código de salida 0).

---

## 7. Verificación de Seguridad e Integridad

- **[HECHO] Ausencia de solicitudes de red:** Las pruebas y transformaciones se ejecutaron en modo estrictamente offline utilizando fixtures en disco.
- **[HECHO] Fuentes reales no consultadas:** Ninguna de las fuentes reales listadas en `sources.json` fue activada ni consultada.
- **[HECHO] Inmutabilidad de la semilla y snapshot:** Se comprobó mediante `git status -- data/` y verificación de bytes en pruebas automatizadas que `data/opportunities.seed.json` y `data/opportunities.json` permanecieron inalterados.
- **[HECHO] Ninguna oportunidad publicada:** Los candidatos generados se limitan a estructuras de staging editorial local (`data/candidates/inbox.local.json` sintético en entorno temporal).

---

## 8. Estado Final y Cumplimiento de Criterios

### 8.1. Estado del repositorio
- **Rama:** `integration/r1-02c`
- **Commit HEAD:** `54897155a5069207ce7b798f6f96d00600209225`
- **Working Tree:**
  - `collector/ats_connectors.py` (adaptación modular completada).
  - `tests/test_ats_connectors.py` (nueva suite de pruebas).
  - `tests/fixtures/ats/*.json` (14 fixtures sintéticos).
  - Documentos de auditoría en `docs/audits/`.
  - Código de catálogo, frontend y datos canónicos 100% limpios e intactos.

### 8.2. Criterios de Aceptación del Bloque

| Criterio | Estado | Evidencia |
| :--- | :--- | :--- |
| Conectores existentes identificados y evaluados | **CUMPLIDO** | `greenhouse-job-board` y `lever-postings` evaluados |
| Adaptadores funcionales cumplen Schema 2 | **CUMPLIDO** | Superan `validate_candidates.py` con 0 errores |
| Entradas incompletas/malformadas gestionadas | **CUMPLIDO** | Cubiertas por 14 fixtures y pruebas dedicadas |
| Fixtures exclusivamente sintéticos y locales | **CUMPLIDO** | Creados en `tests/fixtures/ats/` sin datos reales |
| Candidatos superan validadores existentes | **CUMPLIDO** | `validate_payload()` retorna 0 errores |
| Procedencia y evidencias conservadas | **CUMPLIDO** | Generación de `fieldEvidence` biunívoca |
| Pruebas nuevas y regresiones aprobadas | **CUMPLIDO** | 75/75 tests unitarios OK, 8/8 Playwright OK |
| Semilla y snapshot público intactos | **CUMPLIDO** | Verificado por hash de bytes y git status |
| Cero dependencias nuevas incorporadas | **CUMPLIDO** | 100% biblioteca estándar de Python |
| Fuentes reales no habilitadas / No publicación | **CUMPLIDO** | Fuentes permanecen `enabled: false`, `budget: 0` |

---

## 9. Clasificación de Conclusiones

- **[HECHO]** Los conectores ATS de Greenhouse y Lever quedan formalmente adaptados a Schema 2 y son capaces de alimentar la bandeja editorial local con candidatos estructurados y verificables.
- **[HECHO]** No se realizaron llamadas de red ni se alteraron los datos de producción o catálogo público.
- **[INFERENCIA]** El esquema de candidatos actual requiere `captureMethod: "manual"` porque fue concebido durante una fase donde no existían conectores automáticos autorizados. Cuando se autorice formalmente el primer conector en producción, `scripts/validate_candidates.py` podrá aceptar métodos tipados adicionales (ej. `"ats_connector"`) si el propietario lo aprueba.
- **[PROPUESTA]** Conservar el valor por defecto `captureMethod: "manual"` en la salida de los adaptadores para mantener compatibilidad inmediata con el validador estricto vigente sin necesidad de modificar el validador en esta etapa.
- **[PENDIENTE]** Autorización explícita del propietario para el alta de fuentes reales y activación de presupuestos en `collector/sources.json`.

---

## 10. Siguiente Bloque Recomendado: R2-OSS-03

El bloque **R2-OSS-02** se encuentra satisfactoriamente cerrado y validado.

**Recomendación técnica para R2-OSS-03:**
Proceder con la preparación del micro-extractor HTML y JSON-LD (`selectolax` + Schema.org `JobPosting`) para portales institucionales de empleo (convocatorias en HTML como SERVIR / FISI), continuando bajo la misma disciplina:
1. Pruebas exclusivamente offline contra volcados HTML estáticos y fixtures locales en `tests/fixtures/html/`.
2. Emisión de candidatos bajo el mismo contrato canónico de Schema 2 validado en este bloque.
3. Evaluación y aprobación previa para la inclusión de la dependencia `selectolax` en `requirements.txt`.
