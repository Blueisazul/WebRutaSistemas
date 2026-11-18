# R2-A-03 — Recaptura Controlada y Consolidación de Evidencia de la Primera Oportunidad Real

**Proyecto:** Ruta Sistemas  
**Fase:** R2 — Flujo editorial real  
**Fecha de informe:** 2026-11-18  
**Responsables (Roles):** Principal Software Engineer, Senior Software Architect, OSS Integration Specialist y Responsable Técnico del Flujo de Adquisición  
**Resultado de salida:** `RESULTADO A — CAPTURA CONTROLADA COMPLETA`  
**Referencia previa:** [docs/audits/r2-a-02-editorial-review-2026-11-17.md](r2-a-02-editorial-review-2026-11-17.md)

---

## 1. Objetivo y Alcance

El objetivo del bloque **R2-A-03** es ejecutar una recaptura controlada y consolidar un expediente reproducible y verificable para la primera oportunidad real seleccionada en `R2-A-02`:

**CookUnity — Supply Chain Analyst**
- **Candidate ID:** `CAND-greenhouse-public-job-board-template-8039990003`
- **External job ID:** `8039990003`
- **Ubicación:** `Lima, Lima Province, Peru` (`PERU_LOCAL`).

Se verifica exhaustivamente:
- Que la vacante continúe activa y publicada en su fuente oficial.
- La coincidencia punto a punto entre la API pública de Greenhouse (`boards-api.greenhouse.io`) y la página oficial del empleador (`careers.cookunity.com/jobs/8039990003`).
- La conservación de evidencias HTTPS estructuradas por cada campo observado con marcas de frescura recientes.
- La preservación en reserva del candidato complementario de Canonical (`CAND-greenhouse-public-job-board-template-8379825`) en staging sin alteraciones.
- La permanencia estricta del candidato en staging con estado editorial `pending_review`, sin modificar los archivos canónicos (`data/opportunities.seed.json`, `data/opportunities.json`).

---

## 2. Estado Inicial del Repositorio

- **Rama activa:** `integration/r1-02c` (rastreando `origin/integration/r1-02c`).
- **Commit HEAD:** `2d004d9a046c93ac71d3238a64c86012f727b3e7`.
- **Integridad de archivos canónicos:**
  - `data/opportunities.seed.json`: `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` (Inalterado)
  - `data/opportunities.json`: `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` (Inalterado)
  - `collector/sources.json`: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` (Inalterado)
- **Candidatos en staging previos:** 8 registros en `data/candidates/inbox.local.json` validados bajo Candidate Schema 2.

---

## 3. Fuente y Mecanismo Utilizados

Se utilizaron exclusivamente los componentes estándar del colector de Ruta Sistemas sin añadir herramientas externas:
1. **Greenhouse Job Board REST API (Endpoint Individual):**
   - URL: `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`
   - Mecanismo: Solicitud GET con cabecera `Accept: application/json` y User-Agent identificativo.
   - Naturaleza: API pública documentada, keyless, sin autenticación ni evasión de controles.
2. **Página Oficial de Carreras CookUnity (Verificación de Concordancia):**
   - URL: `https://careers.cookunity.com/jobs/8039990003` (también `https://careers.cookunity.com/open-roles?gh_jid=8039990003`).
   - Mecanismo: Inspección de microdatos Schema.org (`JobPosting` en `<script type="application/ld+json">`) mediante el módulo institucional `collector/jsonld_extractor.py`.

---

## 4. Condiciones de Uso Verificadas

- **Clasificación en inventario:** `cookunity-greenhouse` tipificada como `READY_WITH_LIMITS`.
- **Límites de acceso:** 1 solicitud HTTP por ejecución, sin concurrencia, respetando la política de no almacenar código HTML completo ni descripciones íntegras de manera masiva.
- **Trazabilidad:** Se almacena únicamente el conjunto mínimo factual de metadatos (título, empleador, fecha, identificador, ubicación y URL oficial de postulación).
- **Redirección de postulación:** La URL de postulación redirige de forma directa al formulario de postulación del empleador en Greenhouse / CookUnity, preservando la exclusividad del canal de captación de la entidad.

---

## 5. Estado Actual de la Publicación Oficial

Se verificó el estado en tiempo real (2026-11-18):
- **API Greenhouse (`boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`):** Respondió **`HTTP 200 OK`**.
- **Portal oficial (`careers.cookunity.com/jobs/8039990003`):** Respondió **`HTTP 200 OK`**.
- **Portal ATS Greenhouse (`job-boards.greenhouse.io/cookunity/jobs/8039990003`):** Respondió **`HTTP 200 OK`** (redireccionando transparentemente a la URL canónica del empleador).
- **Conclusión de vigencia:** **VIGENTE Y ACTIVA**. No ha sido cerrada, retirada ni modificada en su identidad esencial.

---

## 6. Datos Capturados

A partir de la recaptura focalizada sobre el endpoint individual y la página oficial, se consolidaron los siguientes campos estructurados:

| Campo | Valor Capturado | Fuente de Verificación |
|---|---|---|
| `candidateId` | `CAND-greenhouse-public-job-board-template-8039990003` | Determinista por conector |
| `externalReference` | `8039990003` | Greenhouse Job ID |
| `employer` | `CookUnity` | Greenhouse API / JSON-LD |
| `publisher` | `CookUnity` | Greenhouse API / JSON-LD |
| `title` | `Supply Chain Analyst` | Greenhouse API / JSON-LD |
| `publishedAt` | `2026-10-21` | `first_published` en API y `datePosted` en JSON-LD |
| `deadline` | `null` (No informado) | `application_deadline: null` en API |
| `location` | `Lima, Lima Province, Peru` | Greenhouse API / JSON-LD |
| `mode` | `null` (No informado explícitamente) | Regla de no-inferencia; sede física en Lima |
| `opportunityType` | `null` (No informado en API) | Requiere confirmación editorial en ficha |
| `salary` | `null` (No informado) | No expuesto en feed público |
| `benefits` | `null` (No estructurado) | Descrito textualmente en cuerpo |
| `requirements` | `null` (Enriquecido en ficha editorial) | Registrado en cuerpo textual de la convocatoria |
| `applyUrl` | `https://job-boards.greenhouse.io/cookunity/jobs/8039990003` | Greenhouse Posting Canonical URL |

---

## 7. Evidencias por Campo

Cada campo propuesto cuenta con su respectiva evidencia HTTPS y marca temporal:

```json
[
  {
    "field": "title",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "employer",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "publisher",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "externalReference",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "applyUrl",
    "url": "https://job-boards.greenhouse.io/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "publishedAt",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  },
  {
    "field": "location",
    "url": "https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003",
    "observedAt": "2026-11-17T21:24:51-05:00"
  }
]
```

---

## 8. Comparación con el Candidato Anterior

| Dimensión | Captura Inicial (R2-A-02) | Recaptura Controlada (R2-A-03) | Variación / Análisis |
|---|---|---|---|
| **URL de origen** | `.../boards/cookunity/jobs` (lista general) | `.../boards/cookunity/jobs/8039990003` (individual) | Enriquecimiento a endpoint específico |
| **Fecha de publicación (`publishedAt`)** | `null` | `2026-10-21` | **Enriquecido.** Constatado en `first_published` y `datePosted` de JSON-LD |
| **Título y Empleador** | `Supply Chain Analyst` / `CookUnity` | `Supply Chain Analyst` / `CookUnity` | Idénticos |
| **Ubicación** | `Lima, Lima Province, Peru` | `Lima, Lima Province, Peru` | Idéntico (`PERU_LOCAL`) |
| **Modalidad (`mode`)** | `null` | `null` | Sin cambios. Se preserva regla de no-inferencia |
| **Fecha de captura (`capturedAt`)** | `2026-11-17T20:16:31-05:00` | `2026-11-17T21:24:51-05:00` | Marca temporal renovada |
| **Evidencias** | 6 campos | 7 campos (incluye `publishedAt`) | Evidencias ampliadas y verificadas |
| **Estado editorial** | `pending_review` | `pending_review` | Inalterado |

---

## 9. Estado de Frescura y Vigencia

- **Política de frescura:** TTL de 7 días calculado con zona horaria de Lima (`America/Lima`).
- **Estado de evidencias:** **`ALL_FRESH` (8/8 candidatos en bandeja local)**.
- **Vigencia temporal:** `DEADLINE_UNKNOWN`. La ausencia de fecha de expiración formal en el ATS requiere verificación de estado HTTP 200 previo a cualquier despliegue.

---

## 10. Resultado de Deduplicación

Se ejecutó el módulo de deduplicación determinista:
- **Candidatos evaluados:** 8
- **Duplicados exactos (`EXACT_DUPLICATE`):** 0
- **Colisiones de ID (`IDENTIFIER_COLLISION`):** 0
- **Posibles duplicados por firma (`POSSIBLE_DUPLICATE`):** 0
- **Conclusión:** No se generaron registros duplicados; la recaptura actualizó el registro existente sin colisión.

---

## 11. Estado Editorial Final

- **Estado en staging (`inbox.local.json`):** `pending_review`.
- **Clasificación editorial técnica:** `RECOMMENDED`.
- **Candidato en reserva (Canonical `8379825`):** Preservado intacto en staging en estado `pending_review` para evaluación posterior cuando se resuelva la consulta de republicación de Canonical.

---

## 12. Pruebas y Comandos Ejecutados

```powershell
# 1. Validación de candidatos Candidate Schema 2 (8 candidatos)
python scripts/validate_candidates.py data/candidates/inbox.local.json
# Resultado: Bandeja local válida (0 errores).

# 2. Análisis de deduplicación determinista
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
# Resultado: 0 colisiones, 0 duplicados.

# 3. Inspección editorial y frescura de evidencias
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json --verify-evidence
# Resultado: 8 ALL_FRESH, 8 pending_review.

# 4. Pruebas unitarias y de integración Python (193 tests)
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 2.466s - OK.

# 5. Pruebas E2E Playwright en Chromium Desktop y Mobile (8 tests)
npx playwright test
# Resultado: 8 passed (7.4s).

# 6. Comprobación de catálogo canónico y snapshot
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Catálogo válido; snapshot coincide con la fuente canónica.

# 7. Comprobación de diferencias Git
git diff --check
# Resultado: Sin errores de formato.
```

---

## 13. Archivos Modificados

- `data/candidates/inbox.local.json`: Actualizado con la recaptura enriquecida de CookUnity `8039990003` (ignorado por `.gitignore`).
- `docs/audits/r2-a-03-controlled-capture-2026-11-18.md`: Creación del presente informe de recaptura.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Actualización del estado del hito R2 en la tabla rectora.
- `docs/sources/seguimiento-autorizacion-fuentes.md`: Registro de la recaptura de CookUnity `8039990003`.

### Archivos canónicos estrictamente protegidos (0 modificaciones):
- `data/opportunities.seed.json`: `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` (Inalterado)
- `data/opportunities.json`: `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` (Inalterado)
- `collector/sources.json`: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` (Inalterado)

---

## 14. Dependencias Agregadas

- **Nuevas dependencias:** **0**. No se instalaron librerías de terceros (cero pip, cero npm).

---

## 15. Riesgos y Limitaciones

1. **Advertencia editorial sobre el rol:** El puesto *Supply Chain Analyst* pertenece al área de análisis de operaciones, gestión de datos relacionales en SQL y sistemas ERP empresariales. **No debe etiquetarse artificialmente como puesto de ingeniería o desarrollo de software**. Debe catalogarse fielmente dentro de su familia profesional (Datos / Sistemas Operacionales).
2. **Modalidad no informada en metadatos estructurados:** La vacante tiene sede en Lima, pero la API no contiene un campo explícito que indique si es presencial al 100% o híbrida. Se mantiene `mode: null` por política fail-closed.
3. **Ausencia de salario publicado:** La API pública no contiene rango salarial para esta posición.

---

## 16. Ficha Consolidada para Decisión Humana

```yaml
Ficha Editorial de Oportunidad Real:
-----------------------------------
Candidato ID: CAND-greenhouse-public-job-board-template-8039990003
Empleador: CookUnity
Puesto: Supply Chain Analyst
Área Profesional: Analítica de Datos / Sistemas de Información Empresarial (ERP/MRP)
Ubicación: Lima, Lima Province, Peru (PERU_LOCAL)
Modalidad: Presencial / Híbrida en sede Lima (No informada taxativamente en API; mode=null)
Tipo de Contrato: Tiempo Completo (Full-Time)
Requisitos Académicos: Bachiller o egresado en Ingeniería (Sistemas, Industrial o carreras afines)
Requisitos Técnicos: 
  - Consultas SQL: extracción, cruce (joins), agregación y validación de datos operacionales.
  - Hojas de cálculo avanzadas: Google Sheets (fórmulas complejas, búsquedas, tablas dinámicas).
  - Sistemas de planificación de recursos: conocimiento operativo de ERP / MRP.
  - Inglés: nivel profesional para interacción con casa matriz en Nueva York.
Experiencia Requerida: 1+ años en áreas analíticas o de cadena de suministro / operaciones.
Remuneración: No informada en la publicación oficial.
Fecha de Publicación Original: 2026-10-21
Fecha Límite: No informada (DEADLINE_UNKNOWN)
Canal Oficial de Postulación: https://job-boards.greenhouse.io/cookunity/jobs/8039990003
Fecha de Última Verificación: 2026-11-17T21:24:51-05:00 (HTTP 200 OK)
Evidencias Asociadas: 7 evidencias verificadas ALL_FRESH
Pertinencia para Ingeniería de Sistemas: Alta para perfiles iniciales interesados en bases de datos relacionales, analítica operativa y optimización de sistemas empresariales.
```

---

## 17. Siguiente Bloque Recomendado

- **`R2-A-04 — Revisión Editorial Humana y Aprobación de Promoción`**:
  El propietario del proyecto debe revisar la ficha consolidada y emitir la decisión formal de aprobación o rechazo editorial para autorizar el paso a `R2-A-05` (promoción a semilla canónica y publicación).
