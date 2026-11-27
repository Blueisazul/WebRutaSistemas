# INFORME DE CONSOLIDACIÓN PRE-RELEASE Y AUDITORÍA TÉCNICA
## Calidad de Catálogo (TASK-FIX-URL-01) y Normalización Geográfica (TASK-R5-05)

- **Proyecto:** Velora
- **Fase:** R5 — Cobertura nacional de oportunidades y Calidad Transversal de Catálogo
- **Tareas Consolidadas:** `TASK-FIX-URL-01` + `TASK-R5-05`
- **Prioridad:** P1 — Crítica
- **Clasificación:** `[CONSOLIDACIÓN_TÉCNICA]` + `[AUDITORÍA_PRE_RELEASE]` + `[REUTILIZACIÓN_INTERNA]`
- **Fecha de Auditoría:** 27 de noviembre de 2026, 13:35 PET
- **Auditor Técnico:** Principal Software Architect, Senior Software Engineer, Technical Auditor y Delivery Architect
- **Rama Documentada:** `main`
- **Commit Base HEAD:** `6b754daff24687c754dda94c303bb06a7e062732` (`6b754da`)
- **Release Base:** `v0.7.0` (commit `4006413`)
- **Dictamen Pre-Release:** **`READY_FOR_OWNER_APPROVAL`**

---

## 1. ESTADO INICIAL DEL WORKSPACE Y ALCANCE DE LA CONSOLIDACIÓN

La auditoría técnica constató que en el árbol de trabajo local residen dos bloques funcionales y de calidad plenamente concluidos y probados que aún no han sido comprometidos en Git:

1. **`TASK-FIX-URL-01` (Corrección de URLs de publicación original de ATS):** Remediación de 97 registros en el catálogo canónico donde `sourceUrl` apuntaba a endpoints JSON crudos de la API REST de Greenhouse (`boards-api.greenhouse.io`), sustituyéndolos por las URLs web canónicas de las vacantes (`job-boards.greenhouse.io`).
2. **`TASK-R5-05` (Normalización geográfica y segmentación del ámbito territorial):** Implementación de una taxonomía tridimensional independiente (`geographicScope`, `workMode`, `department`) en backend (`collector/geography.py`) y frontend (`app.js`, `index.html`), resolviendo la ambigüedad entre vacantes locales en el Perú y vacantes internacionales remotas elegibles para postulantes peruanos.

---

## 2. INVENTARIO Y CLASIFICACIÓN DE ARCHIVOS DEL WORKSPACE

Para garantizar la estricta separación de responsabilidades y evitar mezclas accidentales con tareas paralelas, se auditó y clasificó cada archivo presente en `git status`:

| Archivo | Estado Git | Tarea Atribuida | Naturaleza del Cambio |
|---|---|---|---|
| `collector/ats_connectors.py` | Modificado | `TASK-FIX-URL-01` | Mapeo de `sourceUrl` a URL web legible (`absolute_url` en Greenhouse, `hostedUrl` en Lever). |
| `scripts/catalog_quality.py` | Modificado | `TASK-FIX-URL-01` | Regla de calidad determinista que prohíbe endpoints API REST en `sourceUrl`. |
| `scripts/validate_candidates.py` | Modificado | `TASK-FIX-URL-01` | Validación de Candidate Schema 2 para rechazar endpoints API como URLs de origen. |
| `data/opportunities.seed.json` | Modificado | `TASK-FIX-URL-01` | Remediación de 97 registros con URLs web públicas en sustitución de API endpoints. |
| `data/opportunities.json` | Modificado | `TASK-FIX-URL-01` | Snapshot compilado reproducible correspondiente al seed remediado. |
| `tests/test_ats_connectors.py` | Modificado | `TASK-FIX-URL-01` | Pruebas unitarias de conectores validando URLs web en `sourceUrl`. |
| `tests/test_catalog_quality.py` | Modificado | `TASK-FIX-URL-01` | Pruebas de detección y rechazo de endpoints API REST. |
| `docs/audits/TASK-FIX-URL-01-ATS-PUBLICATION-URL-REMEDIATION.md` | No rastreado | `TASK-FIX-URL-01` | Informe de auditoría técnica y remediación de ATS. |
| `collector/geography.py` | No rastreado | `TASK-R5-05` | Módulo backend de taxonomía territorial y normalización tridimensional. |
| `tests/test_geography.py` | No rastreado | `TASK-R5-05` | 14 pruebas unitarias de clasificación geográfica y ámbitos territoriales. |
| `index.html` | Modificado | `TASK-R5-05` | Selectores `<select id="scope-filter">` y `<select id="department-filter">`. |
| `app.js` | Modificado | **Compartido** (`FIX-URL-01` + `R5-05`) | Sanitización fallback de URLs ATS + población dinámica de filtros y etiquetas de ámbito. |
| `tests/catalog_ui.test.cjs` | Modificado | **Compartido** (`FIX-URL-01` + `R5-05`) | Pruebas de integración UI de navegación web ATS y filtrado reactivo geográfico. |
| `docs/audits/TASK-R5-05-GEOGRAPHIC-NORMALIZATION-AND-FILTERS.md` | No rastreado | `TASK-R5-05` | Informe de implementación de taxonomía y filtros territoriales. |
| `collector/assisted_discovery.py` | No rastreado | `TASK-R5-04-02` | Módulo del piloto de radar asistido (preservado íntegro). |
| `tests/test_assisted_discovery.py` | No rastreado | `TASK-R5-04-02` | 14 pruebas unitarias de descubrimiento asistido (preservado íntegro). |
| `collector/sources.json` | Modificado | `TASK-R5-04-02` | Registro de fuentes `postulate-pe-radar` y `laboral-pe-radar` (`enabled: false`). |
| `scripts/editorial_cli.py` | Modificado | `TASK-R5-04-02` | Subcomandos de administración de radar `radar-record`, `radar-verify`, `radar-promote`. |
| `.gitignore` | Modificado | `TASK-R5-04-02` | Exclusión de `data/candidates/radar_discovery.local.json`. |
| `data/candidates/inbox.local.json` | Ignorado | **Staging local** | 297 candidatos validados en Schema 2 (preservado íntegro). |
| `data/candidates/radar_discovery.local.json` | Ignorado | **Staging local** | 10 entradas de prueba de campo del radar (preservado íntegro). |
| `docs/audits/R5-04-03-ASSISTED-DISCOVERY-PILOT.md` | No rastreado | `TASK-R5-04-02` | Informe de implementación del radar asistido. |
| `docs/audits/TASK-R5-04-02-FIELD-VALIDATION.md` | No rastreado | `TASK-R5-04-02` | Informe de prueba de campo con 10 casos reales. |
| `docs/audits/TASK-R5-04-02-EDITORIAL-REVIEW.md` | No rastreado | `TASK-R5-04-02` | Revisión editorial de candidatos DEVIDA y HNHU. |
| `docs/audits/R5-02-SERVIR-OFFICIAL-ENDPOINT-INVESTIGATION.md` | No rastreado | `TASK-R5-02` | Investigación técnica Talento Perú / SERVIR (preservada). |
| `docs/audits/VELORA-OPEN-DECISIONS.md` | Modificado | **Gobernanza** | Decisiones 7 y 9 formalizadas por el propietario. |
| `docs/roadmap/VELORA-MASTER-ROADMAP.md` | Modificado | **Roadmap** | Registro actualizado de R5, R6 y R7. |

---

## 3. AUDITORÍA TÉCNICA DETALLADA DE TASK-FIX-URL-01

### 3.1. Corrección en Conectores
- En `collector/ats_connectors.py`, la función `transform_greenhouse_payload()` extrae la URL web oficial del puesto mediante `job.get("absolute_url")`. Si el campo no estuviera presente, efectúa fallback determinista a `https://job-boards.greenhouse.io/{board_token}/jobs/{job_id}`, garantizando que jamás se persista un endpoint API `boards-api.greenhouse.io/v1/...` en `sourceUrl`.
- La función `transform_lever_payload()` utiliza `job.get("hostedUrl")`, garantizando la URL de la página pública en `jobs.lever.co/{site}/{id}`.
- Se mantiene la estricta separación semántica:
  - `sourceUrl`: Enlace a la página de publicación web original de la oportunidad.
  - `applyUrl`: Enlace directo al formulario o proceso de postulación.

### 3.2. Reglas de Calidad y Validadores
- En `scripts/catalog_quality.py`, se implementó la regla `_validate_source_url_not_api()`, que rechaza sistemáticamente cualquier registro cuyo `sourceUrl` apunte a `boards-api.greenhouse.io`, `api.lever.co`, `api.smartrecruiters.com` o formatos `/api/v[0-9]+/`.
- En `scripts/validate_candidates.py`, se integró la misma salvaguarda en la validación de Candidate Schema 2 para la bandeja de staging.
- En `app.js`, se implementó una función de sanitización en el cliente `sanitizeSourceUrl(url, applyUrl)` que asegura que, incluso ante cualquier dato histórico o inconsistente, el botón «Ver publicación original» nunca redirija a una respuesta JSON de API.

### 3.3. Remediación Canónica (97 Registros Verificados)
Se auditó la totalidad de los 112 registros del catálogo:
- Registros totales: **112**.
- Registros que utilizaban endpoints API REST antes de la tarea: **97** (75 de Canonical, 9 de Sezzle, 13 de Encora).
- Registros remediados exitosamente con URLs web válidas: **97 de 97 (100%)**.
- Endpoints API restantes en `data/opportunities.seed.json`: **0**.
- Endpoints API restantes en `data/opportunities.json`: **0**.
- Estabilidad de identificadores: 100% preservada (`OP-001` a `OP-111` y `QA-001`).

---

## 4. AUDITORÍA TÉCNICA DETALLADA DE TASK-R5-05

### 4.1. Taxonomía Tridimensional Independiente
El módulo `collector/geography.py` formaliza tres dimensiones ortogonales y *fail-closed*:

1. **Ámbito Territorial / Elegibilidad para el Perú (`geographicScope`):**
   - `PERU_LOCAL`: Empleo presencial o híbrido con sede en Perú (14 registros).
   - `PERU_REMOTE`: Remoto nacional reservado para residentes en Perú (2 registros).
   - `INTERNATIONAL_REMOTE_PERU_ELIGIBLE`: Remoto internacional con elegibilidad explícita confirmada para Perú (95 registros).
   - `INTERNATIONAL_REMOTE_UNCONFIRMED`: Remoto internacional con elegibilidad no confirmada (1 registro, `OP-004`).
   - `NOT_ELIGIBLE_PERU`: Oportunidades con exclusión explícita de postulantes en Perú (0 en catálogo actual).
   - `UNSPECIFIED`: Ubicación ambigua o no informada (0 en catálogo actual).
2. **Modalidad Físico-Espacial (`workMode`):**
   - `ONSITE` (Presencial), `HYBRID` (Híbrido), `REMOTE` (Remoto), `UNSPECIFIED`.
3. **Ubicación en el Perú (`department`):**
   - Normalización de los 24 departamentos más la Provincia Constitucional del Callao sin dependencias de red ni geocodificadores externos. En el catálogo actual, las 14 vacantes locales corresponden a **Lima**.

### 4.2. Interfaz y Experiencia de Descubrimiento
- `index.html`: Incorporados los controles `<select id="scope-filter">` y `<select id="department-filter">`, manteniendo el `<input id="location">` para búsquedas textuales libres complementarias.
- `app.js`:
  - Población dinámica de `#department-filter` únicamente con los departamentos con presencia real en el catálogo (evita opciones vacías que generen cero resultados).
  - Filtrado reactivo combinado: el usuario puede filtrar simultáneamente por régimen laboral (R7-01), carrera, ámbito territorial, departamento y texto libre.
  - Sincronización de limpieza (`#btn-clear-filters`) que restablece todos los controles y etiquetas a su estado inicial.
  - Renderizado de etiquetas de ámbito territorial (`geographicScopeTag`) en tarjetas y modal de detalle.

---

## 5. RESULTADOS DE PRUEBAS AUTOMATIZADAS Y REGRESIÓN

### 5.1. Pruebas Unitarias de los Bloques Consolidados
```bash
python -m unittest tests/test_ats_connectors.py tests/test_catalog_quality.py tests/test_geography.py
```
- **Resultado:** **56 pruebas ejecutadas y aprobadas al 100%** en 0.264s.

### 5.2. Pruebas de Interfaz y UI (Node.js)
```bash
node tests/catalog_ui.test.cjs
```
- **Resultado:** **Passed** (Escenarios de filtrado de catálogo, navegación, rutas root/Pages y degradación controlada aprobados).

### 5.3. Suite Completa del Proyecto (Pytest)
```bash
python -m pytest -q
```
- **Resultado:** **342 pruebas y 43 subtests aprobados al 100% en 8.10s** (Cero fallos, cero regresiones).

### 5.4. Verificación de Compilación y Calidad Canónica
```bash
python scripts/build_catalog.py --check --as-of 2026-11-23
```
- **Resultado:** `Catálogo válido: 112 registros; snapshot coincide con la fuente canónica.`
- Comprobación: El snapshot `data/opportunities.json` es 100% reproducible a partir de `data/opportunities.seed.json`.

---

## 6. INTEGRIDAD CRIPTOGRÁFICA Y CONTROL DE STAGING

### 6.1. Hashes Canónicos Certificados
Los hashes SHA-256 de los catálogos reflejan de forma verificable la remediación de las 97 URLs sin alteraciones adicionales:

```text
Archivo                           Hash SHA-256 Certificado
data/opportunities.seed.json      A465CD3D9D5072676CD6A1D505E18DAE541EB8D18E94812CFB9391C618BEC87C
data/opportunities.json           817D1A327F295367E9921C7D5982683F4113D44EECAEC1933353582A7949059D
```

### 6.2. Aislamiento Estricto de Staging
- `data/candidates/inbox.local.json` (297 candidatos): Totalmente aislado del catálogo canónico público. Ningún candidato en staging fue promovido o mezclado en esta ejecución.
- `data/candidates/radar_discovery.local.json` (10 entradas de radar): Aislado y protegido por regla en `.gitignore`.
- Cero exposición de información personal (PII) o datos privados.

---

## 7. POLÍTICA OSS-FIRST Y DEPENDENCIAS

- **Nuevas dependencias añadidas:** **0** (Uso exclusivo de la biblioteca estándar de Python: `re`, `unicodedata`, `dataclasses`, `json`, `pathlib`).
- **Nuevas librerías frontend añadidas:** **0** (Vanilla JavaScript, HTML5 y CSS nativos).
- **Servicios externos o APIs comerciales:** **0** (Cero consumo de APIs de geocodificación, Google Maps o servicios de terceros).

---

## 8. CONTROL DE DECISIONES DE GOBERNANZA

- **Decisión 7 (Postulate.pe y Laboral.pe):** Preservada al 100%. Ambas fuentes continúan en `enabled: false` y `autopublish: false`. Los candidatos DEVIDA y HNHU permanecen en `pending_review` dentro de staging.
- **Decisión 8 (HiringRoom):** Continúa como decisión abierta pendiente de aprobación del propietario. Las 20 vacantes de HiringRoom permanecen en staging.
- **Decisión 9 (Criterio temporal):** Respetada; no se descartó ninguna oportunidad por plazo corto y se mantuvieron las fechas oficiales ISO-8601.

---

## 9. DICTAMEN FINAL DE PREPARACIÓN PRE-RELEASE

**`READY_FOR_OWNER_APPROVAL`**

### Fundamentación del Dictamen:
1. `TASK-FIX-URL-01` resuelve definitivamente el defecto de enlaces de API REST en 97 oportunidades del catálogo, certificado por pruebas unitarias, de calidad y validadores de cliente.
2. `TASK-R5-05` proporciona una experiencia de búsqueda geográfica robusta, precisa y reactiva, distinguiendo empleos locales peruanos de vacantes internacionales remotas.
3. Las modificaciones coexisten sin conflictos, las suites de pruebas pasan al 100% (342/342 en Python y 100% en Node.js), la compilación canónica es reproducible y los datos de staging permanecen estrictamente aislados.
4. Las modificaciones de otras tareas (`TASK-R5-04-02`, `TASK-R5-02`) están claramente deslindadas y documentadas sin interferir con la entrega.

---

## 10. ACCIONES QUE REQUIEREN AUTORIZACIÓN DEL PROPIETARIO

Para hacer efectiva la entrega a los usuarios en producción, el propietario deberá autorizar expresamente:
1. Crear el commit de consolidación en la rama `main`.
2. Asignar el tag de release correspondiente (`v0.7.1` por remediación de calidad y parches territoriales, o `v0.8.0` según convención semántica del producto).
3. Efectuar el push a `origin/main` y del tag para disparar los workflows de GitHub Pages y Vercel.
