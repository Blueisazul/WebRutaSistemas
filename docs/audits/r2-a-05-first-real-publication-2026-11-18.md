# Informe de Auditoría y Publicación Editorial R2-A-05
**Primera Oportunidad Real Publicada en Ruta Sistemas**

- **Fecha de ejecución (UTC):** 2026-11-18
- **Fecha civil de referencia (America/Lima, UTC-05:00):** 2026-11-17
- **Fase del Proyecto:** R2 — Flujo editorial real
- **Clasificación:** `[GOBERNANZA_DE_DATOS]` `[REVISIÓN_EDITORIAL]` `[ADAPTACIÓN_OSS]` `[PUBLICACIÓN_CONTROLADA]`
- **Rama de integración:** `integration/r1-02c` -> `main`
- **Identificador en Catálogo:** `OP-005`
- **Identificador de Candidato Staging:** `CAND-greenhouse-public-job-board-template-8039990003`

---

## 1. Autorización y Mandato Editorial

En cumplimiento de la recomendación editorial emanada del bloque **R2-A-04** (`APPROVE_WITH_LIMITATIONS`), el propietario del proyecto autorizó formalmente proceder con la promoción al catálogo canónico, compilación estática y publicación en producción de la oportunidad laboral correspondiente a:

- **Empleador:** CookUnity
- **Entidad difusora:** CookUnity (`employer_confirmed`)
- **Puesto:** Supply Chain Analyst
- **ID Externo (ATS):** `8039990003` (Greenhouse Public ATS)
- **Ubicación:** Lima, Lima Province, Peru (`PERU_LOCAL`)

La autorización condicionó la incorporación a preservar estrictamente las limitaciones editoriales identificadas:
1. No clasificar la vacante como de ingeniería de software pura ni como práctica preprofesional.
2. Identificarla con precisión en la familia `Sistemas empresariales` y nivel `Profesional / junior` (requiere al menos 1 año de experiencia profesional).
3. No inferir modalidad de trabajo presencial ni híbrida (`mode: null`), manteniéndola visualmente como «No especificada».
4. Proporcionar desglose íntegro de evidencia HTTPS por cada afirmación fáctica.
5. Mantener al candidato alternativo de Canonical (`8379825`) en reserva en staging.

---

## 2. Identidad y Atributos de la Oportunidad Promovida (`OP-005`)

| Campo | Valor Canónico | Fuente de Evidencia Directa |
|---|---|---|
| `id` | `OP-005` | Asignación secuencial de catálogo Ruta Sistemas |
| `requisition` | `COOKUNITY-LIMA-SCA-8039990003` | Greenhouse Public Job Board Template (`8039990003`) |
| `employer` | `CookUnity` | boards-api.greenhouse.io / careers.cookunity.com |
| `publisher` | `CookUnity` | careers.cookunity.com (`employer_confirmed`) |
| `title` | `Supply Chain Analyst` | boards-api.greenhouse.io / careers.cookunity.com |
| `sector` | `Tecnología / Logística de alimentos (FoodTech)` | Análisis de modelo operativo de CookUnity |
| `family` | `Sistemas empresariales` | Enfoque SQL, ERP, calidad de datos y modelado |
| `level` | `Profesional / junior` | Requisito explícito de 1+ años en roles analíticos |
| `kind` | `Profesional` | Contrato profesional de analítica/sistemas |
| `mode` | `null` | **No informado en origen** (no inferido) |
| `location` | `Lima, Perú` | Confirmado en Greenhouse ATS (`Lima, Lima Province, Peru`) |
| `eligibility` | `Elegible desde Perú (puesto radicado en Lima, Perú)` | Puesto local confirmado |
| `salary` | `No publicado` | No especificado en la oferta pública del ATS |
| `salaryNote` | `La compensación no fue detallada en el anuncio oficial; confirmar en entrevista.` | Transparencia salarial fail-closed |
| `duration` | `Tiempo completo / Indeterminado según legislación laboral peruana` | Puesto regular de nómina técnica |
| `deadline` | `null` | No informado en la vacante; vigencia sujeta a TTL (7 días) |
| `publishedAt` | `2026-10-15` | Timestamp de apertura verificado en Greenhouse API |
| `lastVerifiedAt`| `2026-11-18` | Verificación técnica y comprobación HTTP 200 en vivo |
| `sourceUrl` | `https://careers.cookunity.com/jobs/8039990003` | Portal de carreras oficial del empleador |
| `applyUrl` | `https://job-boards.greenhouse.io/cookunity/jobs/8039990003` | Canal oficial de postulación Greenhouse ATS |
| `recordKind` | `curated` | Oportunidad real aprobada y curada |
| `opportunityStatus`| `open` | Formulario de postulación activo y abierto |
| `verificationStatus`| `verified` | Verificación manual directa del empleador |
| `publicationStatus`| `active` | Publicación activa con botón de postulación habilitado |

---

## 3. Desglose de Evidencia por Campo (`fieldEvidence`)

Se vincularon 21 registros de evidencia fáctica bajo esquema HTTPS estricto con fecha de observación `2026-11-18`, cubriendo la totalidad de datos afirmados en la ficha:

1. `employer` -> `https://careers.cookunity.com/jobs/8039990003`
2. `publisher` -> `https://careers.cookunity.com/jobs/8039990003`
3. `title` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
4. `applyUrl` -> `https://job-boards.greenhouse.io/cookunity/jobs/8039990003`
5. `location` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
6. `eligibility` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
7. `requirements` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
8. `skills` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
9. `tasks` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
10. `training` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
11. `growth` -> `https://careers.cookunity.com/jobs/8039990003`
12. `sector` -> `https://www.cookunity.com/`
13. `family` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
14. `level` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
15. `kind` -> `https://careers.cookunity.com/jobs/8039990003`
16. `duration` -> `https://careers.cookunity.com/jobs/8039990003`
17. `publishedAt` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
18. `benefits` -> `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
19. `continuity` -> `https://careers.cookunity.com/jobs/8039990003`
20. `risk` -> `https://careers.cookunity.com/jobs/8039990003`
21. `salary` -> `https://careers.cookunity.com/jobs/8039990003`

Hosts declarados y autorizados en `allowedHosts`:
- `boards-api.greenhouse.io`
- `careers.cookunity.com`
- `job-boards.greenhouse.io`
- `www.cookunity.com`

---

## 4. Estado de Candidatos en Reserva

El candidato de Canonical (`CAND-greenhouse-public-job-board-template-8379825`, *Junior Operations Analyst*, Remote Worldwide/AMER) se mantiene **inalterado en staging** (`data/candidates/inbox.local.json`) como reserva técnica para una posterior promoción tras la evaluación de este primer ciclo.

---

## 5. Compilación y Validación Integral

1. **Generación del Catálogo:**
   `python scripts/build_catalog.py --write` generó 6 registros consolidados en `data/opportunities.json` partiendo de la fuente canónica `data/opportunities.seed.json`.

2. **Validación de Calidad del Catálogo:**
   `python scripts/build_catalog.py --check` y `python scripts/validate_catalog.py` confirmaron que el snapshot publicado coincide exactamente byte por byte con la semilla, verificando 0 errores de esquema y las advertencias esperadas de registros demostrativos y modalidad no informada de OP-005.

3. **Validación de Bandeja Staging:**
   `python scripts/validate_candidates.py data/candidates/inbox.local.json` ratificó que los 8 candidatos en bandeja local satisfacen Schema 2 sin mutación indebida.

4. **Suite de Pruebas Unitarias:**
   `python -m unittest discover -s tests -p "test_*.py"`: **193 pruebas ejecutadas, 193 exitosas** (0 fallos, 0 errores).

5. **Pruebas de Interfaz y Regresión:**
   - `node --check app.js`: Sintaxis JavaScript válida.
   - `node tests/catalog_ui.test.cjs`: Escenarios de filtrado y degradación conformes.
   - `npx playwright test`: **8 pruebas E2E aprobadas** (Chromium y viewport móvil).
   - `git diff --check`: Sin conflictos de espacios ni saltos de línea.

---

## 6. Integración y Despliegue en Producción

- **Rama de origen:** `integration/r1-02c`
- **Rama de publicación remota:** `main` (fast-forward)
- **Flujo CI/CD:** `.github/workflows/refresh-catalog.yml`
- **URL Canónica del Portal:** https://blueisazul.github.io/WebRutaSistemas/
- **URL del Snapshot Público:** https://blueisazul.github.io/WebRutaSistemas/data/opportunities.json

---

## 7. Cierre de Fase R2 y Desbloqueo de R3

Con la culminación de este bloque:
- La fase **R2 (Obtener primera oportunidad real)** queda formalmente en estado **DONE**.
- Se desbloquea la fase **R3 (Validar utilidad del MVP)**, orientada a pruebas de usabilidad, relevancia profesional y evaluación comparativa con usuarios reales del perfil objetivo en Perú.
