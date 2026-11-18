# Informe de Auditoría Técnica y Estratégica: R2-A-01-REV — Descubrimiento, Evaluación e Integración de Fuentes Públicas y Reutilizables

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2 Línea A — Flujo editorial real / Adquisición y evaluación de fuentes  
**Clasificación:** `[INTEGRACIÓN_OSS]` `[ADAPTACIÓN_OSS]` `[AUDITORÍA_DE_FUENTES]` `[GOBERNANZA_DE_DATOS]` `[DESARROLLO_PROPIO - Justificado]`  
**Veredicto:** **ESTRATEGIA RECONCILIADA, INVENTARIO VERIFICADO (12 FUENTES), INTEGRACIÓN PILOTO DEMOSTRADA Y PRIMERA MUESTRA REAL EN STAGING (4 CANDIDATOS)**  
**Estado de Producto (Línea A - Fase R2 Real):** **FUENTE VIABLE E INTEGRADA EN STAGING; PENDIENTE REVISIÓN EDITORIAL HUMANA**  
**Roles:** Principal Software Architect, Senior Software Engineer, OSS Integration Specialist, Data Acquisition Engineer y Technical Auditor.

---

## 1. Resumen Ejecutivo

El presente bloque **R2-A-01-REV** ejecuta el cambio estratégico fundamental en la adquisición de datos de Ruta Sistemas: **superar el cuello de botella de la dependencia de autorizaciones bilaterales exclusivas** (como Canonical o SERVIR) y consolidar la **soberanía tecnológica** del proyecto mediante la identificación, evaluación e integración de fuentes públicas, feeds abiertos y mecanismos documentados de sindicación de vacantes.

### Logros Principales:
1. **Soberanía y Diversificación de Fuentes:** Se amplió el inventario a **12 fuentes públicas y corporativas verificables** organizadas en 4 categorías: sector público peruano, universidades, empresas tecnológicas con ATS abiertos y organizaciones internacionales con trabajo remoto.
2. **Descubrimiento de Fuentes `READY_WITH_LIMITS`:** Se verificó que las APIs públicas de ATS (Greenhouse Job Board API y Lever Postings API) son interfaces REST abiertas por diseño, *keyless*, sin autenticación y expresamente destinadas a la consulta e indexación por terceros, encajando directamente con los adaptadores construidos en la línea R2-OSS.
3. **Comprobación Factual de Elegibilidad Geográfica (Hallazgo Crítico):** Se demostró empíricamente que vacantes etiquetadas genéricamente como *"Remote"* en portales globales restringen con frecuencia la contratación a estados de EE.UU. o a países específicos de LatAm (excluyendo a Perú). Esto valida la necesidad del contrato editorial de Ruta Sistemas (`eligible_countries` y `fieldEvidence`) frente al scraping ciego de otros agregadores.
4. **Primera Integración y Muestra Real en Staging (R2-A-01-REV-06):** Reutilizando exclusivamente la infraestructura offline existente (`scripts/editorial_cli.py import`), se importó, normalizó a Candidate Schema 2 y validó una muestra controlada de **4 candidatos reales** de la **Greenhouse Job Board API** (Wikimedia Foundation) en `data/candidates/inbox.local.json`.
5. **Cero Dependencias y Preservación Criptográfica:** Cero librerías de terceros añadidas. Los archivos canónicos (`opportunities.seed.json`, `opportunities.json` y `sources.json`) permanecen 100% intactos con hashes SHA-256 idénticos.

---

## 2. Estado Real del Repositorio y Rama

- **Rama activa:** `integration/r1-02c` (sincronizada con `origin/integration/r1-02c`).
- **HEAD Commit:** `2d004d9a046c93ac71d3238a64c86012f727b3e7` (`docs(r2-oss): document R2-OSS technical audits, roadmap updates, and editorial CLI usage`).
- **Estado de la línea R2-OSS:** Cerrada formalmente (R2-OSS-01 a R2-OSS-08) e integrada en `integration/r1-02c` con 193 pruebas Python y 8 pruebas Playwright pasando.
- **Relación con R2-A-01 previo:** El hito R2-A-01 original documentó el expediente bilateral para Canonical y SERVIR; R2-A-01-REV amplía la perspectiva hacia la autonomía de adquisición sin invalidar los borradores históricos.

---

## 3. Inventario Ampliado de Fuentes Investigadas

Se investigaron 12 fuentes potenciales divididas en las 4 dimensiones estratégicas requeridas:

| ID / Clave | Entidad / Portal | Ámbito / Categoría | Mecanismo Principal | URL Oficial |
|---|---|---|---|---|
| `datos-abiertos-peru` | Presidencia del Consejo de Ministros (SGTD) | Sector Público Perú | Portal CKAN / CSV / JSON | `https://datosabiertos.gob.pe/` |
| `talento-peru-servir` | Autoridad Nacional del Servicio Civil (SERVIR) | Sector Público Perú | Aplicación web (JSF) | `https://talentoperu.servir.gob.pe/` |
| `empleos-peru-mtpe` | Ministerio de Trabajo (MTPE) | Sector Público Perú | Portal web transaccional | `https://www.empleosperu.gob.pe/` |
| `osiptel-convocatorias` | OSIPTEL (Regulador Telecomunicaciones) | Sector Público Perú | Portal web institucional / PDF | `https://www.gob.pe/osiptel` |
| `bcrp-convocatorias` | Banco Central de Reserva del Perú (BCRP) | Sector Público Perú | Portal web institucional / PDF | `https://www.bcrp.gob.pe/` |
| `unmsm-fisi-employment-board` | FISI — UNMSM | Universidades Perú | CMS web (Joomla Noticias) | `https://sistemas.unmsm.edu.pe/` |
| `uni-bolsa-trabajo` | Universidad Nacional de Ingeniería (UNI) | Universidades Perú | Portal bolsa de trabajo | `https://bolsatrabajo.uni.edu.pe/` |
| `greenhouse-public-job-board-template` (ej. `wikimedia-greenhouse`) | Wikimedia Foundation | OSS / Remoto Internacional | REST API JSON (Greenhouse) | `https://boards-api.greenhouse.io/v1/boards/wikimedia/jobs` |
| `lever-public-postings-template` (ej. `deliverect-lever`) | Deliverect / Empresas Lever | Privada / Internacional | REST API JSON (Lever) | `https://api.lever.co/v0/postings/deliverect?mode=json` |
| `cookunity-greenhouse` | CookUnity | Privada (Tech/Ops en Perú) | REST API JSON (Greenhouse) | `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs` |
| `mozilla-greenhouse` | Mozilla Corporation | OSS / Remoto Internacional | REST API JSON (Greenhouse) | `https://boards-api.greenhouse.io/v1/boards/mozilla/jobs` |
| `canonical-careers` | Canonical Group Limited | Privada / Remoto Internacional | Portal web HTML / Schema.org | `https://canonical.com/careers` |

---

## 4. Matriz de Licencias, Condiciones y Actividades Permitidas

La siguiente matriz evalúa las 8 actividades operativas distinguiendo consulta, automatización, conservación y republicación:

| Fuente | Consulta Manual | Descarga Datos Abiertos | Acceso Automatizado (API/Feed) | Extracción HTML | Conservación Metadatos | Publicación Metadatos Mínimos | Resúmenes Propios | Redirección Oficial | Clasificación General |
|---|---|---|---|---|---|---|---|---|---|
| `datos-abiertos-peru` | Permitida | Permitida (Licencia Datos Abiertos) | Permitida (API CKAN) | No aplica | Permitida | Permitida | Permitida | Permitida | `NOT_VIABLE` (solo datos estadísticos) |
| `talento-peru-servir` | Permitida | No disponible | No autorizada (403 WAF) | Restringida | Requiere revisión | Requiere revisión | Permitida (factual) | Obligatoria | `MANUAL_REVIEW` / `REQUIRES_PERMISSION` |
| `empleos-peru-mtpe` | Permitida (DNI) | No disponible | No autorizada (Auth) | Prohibida (Términos) | Requiere revisión | Requiere revisión | Permitida (factual) | Obligatoria | `NOT_VIABLE` (gated por DNI) |
| `osiptel-convocatorias` | Permitida | No disponible | No documentada | Requiere revisión | Permitida (pública) | Permitida (metadatos) | Permitida (factual) | Obligatoria | `MANUAL_REVIEW` |
| `bcrp-convocatorias` | Permitida | No disponible | No documentada | Requiere revisión | Permitida (pública) | Permitida (metadatos) | Permitida (factual) | Obligatoria | `MANUAL_REVIEW` |
| `unmsm-fisi` | Permitida | No disponible | No documentada | Requiere revisión | Requiere revisión | Requiere revisión | Permitida (factual) | Obligatoria | `MANUAL_REVIEW` |
| `uni-bolsa-trabajo` | Permitida | No disponible | No documentada | No autorizada | Restringida (intranet) | Restringida | Permitida (factual) | Obligatoria | `NOT_VIABLE` (acceso cerrado alumnos) |
| `wikimedia-greenhouse` | Permitida | No aplica | **Permitida (API Pública Keyless)** | Innecesaria | **Permitida** | **Permitida con enlace** | **Permitida** | **Obligatoria** | `READY_WITH_LIMITS` |
| `deliverect-lever` | Permitida | No aplica | **Permitida (API Pública Keyless)** | Innecesaria | **Permitida** | **Permitida con enlace** | **Permitida** | **Obligatoria** | `READY_WITH_LIMITS` |
| `cookunity-greenhouse` | Permitida | No aplica | **Permitida (API Pública Keyless)** | Innecesaria | **Permitida** | **Permitida con enlace** | **Permitida** | **Obligatoria** | `READY_WITH_LIMITS` |
| `mozilla-greenhouse` | Permitida | No aplica | **Permitida (API Pública Keyless)** | Innecesaria | **Permitida** | **Permitida con enlace** | **Permitida** | **Obligatoria** | `READY_WITH_LIMITS` |
| `canonical-careers` | Permitida | No aplica | No documentada | Restringida | Requiere revisión | Requiere revisión | Permitida (factual) | Obligatoria | `REQUIRES_PERMISSION` |

---

## 5. Mecanismos de Acceso Identificados

1. **APIs Públicas de ATS (Greenhouse y Lever):**
   - **Especificación Greenhouse:** `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs`. Keyless, sin cabeceras de autenticación, CORS habilitado para lectura, devuelve JSON estándar con IDs numéricos estables, títulos, ubicaciones estructuradas, URLs canónicas (`https://job-boards.greenhouse.io/{board_token}/jobs/{id}`) y timestamps de actualización.
   - **Especificación Lever:** `GET https://api.lever.co/v0/postings/{company}?mode=json`. Documentación oficial de Lever declara explícitamente: *"All job postings in the published state are publicly viewable by design and can be indexed or scraped by third parties"*.
2. **Portales Web Institucionales Gubernamentales (gob.pe / OSIPTEL / BCRP):**
   - Publicación periódica en páginas HTML con enlaces a bases administrativas en formato PDF (Google Drive o CDN de gob.pe). Requiere descubrimiento y lectura manual estructurada.
3. **Plataforma Nacional de Datos Abiertos (`datosabiertos.gob.pe`):**
   - Mecanismo CKAN abierto, pero limitado a estadísticas sociolaborales retrospectivas (INEI, MTPE), sin transaccionalidad de convocatorias en vivo.

---

## 6. Fuentes Descartadas y Motivos

| Fuente | Motivo Técnico / Legal del Descarte |
|---|---|
| `datos-abiertos-peru` | **Ausencia de vacantes transaccionales vivas:** Solo contiene datasets estadísticos agregados del mercado laboral (encuestas del INEI). |
| `empleos-peru-mtpe` | **Acceso restringido y autenticación obligatoria:** Requiere DNI y login de ciudadano peruano para consultar canales de postulación; prohíbe explícitamente la extracción masiva en sus términos de uso. |
| `uni-bolsa-trabajo` | **Bolsa cerrada para comunidad interna:** Las ofertas completas están protegidas por credenciales de alumno/egresado UNI; no ofrece sindicación pública abierta. |
| `anin-convocatorias` | **Bloqueo de red perimetral:** Las peticiones HTTP reciben 403 Forbidden por WAF/Cloudflare perimetral. Conforme a las directrices de seguridad, no se evade el bloqueo. |

---

## 7. Fuentes Seleccionadas y Justificación

### A. Fuente Piloto Principal: Wikimedia Foundation (`wikimedia-greenhouse`)
- **Justificación:** Organización sin fines de lucro global, rectora de Wikipedia y el software MediaWiki. Promueve la cultura libre, el acceso abierto a la información y el software libre. Publica sus vacantes abiertas en la Greenhouse Job Board API oficial pública (`boardToken: wikimedia`).
- **Mecanismo:** JSON REST API keyless.
- **Ventaja de Integración:** Se integra de forma inmediata con el conector `collector/ats_connectors.py` y `scripts/editorial_cli.py import --format greenhouse`.
- **Clasificación:** `READY_WITH_LIMITS` (Límite: verificar puesto por puesto la elegibilidad geográfica remota para Perú).

### B. Fuente Alternativa: OSIPTEL / Convocatorias del Estado Peruano (`osiptel-manual-review` / `talento-peru-servir`)
- **Justificación:** Representa el sector público nacional en Perú, de máxima afinidad territorial para estudiantes universitarios y egresados locales (prácticas preprofesionales, profesionales y régimen CAS).
- **Mecanismo:** Consulta y captura manual documentada (`captureMethod: manual`) mediante el CLI editorial.
- **Clasificación:** `MANUAL_REVIEW`.

### C. Fuente Complementaria: CookUnity / Deliverect (`cookunity-greenhouse` o `deliverect-lever`)
- **Justificación:** Empresas tecnológicas privadas con operaciones en Lima, Perú o contratación remota en LATAM que utilizan Greenhouse y Lever. Demuestra la capacidad agnóstica de Ruta Sistemas de conectarse a múltiples ATS sin acoplamiento a una sola entidad.
- **Clasificación:** `READY_WITH_LIMITS`.

---

## 8. Riesgos e Incertidumbres

1. **Riesgo de Falsa Elegibilidad Remota (Verificado Empíricamente):**
   - *Hallazgo:* En Wikimedia Foundation, el puesto de prácticas `Software Engineering Internship Program (2027)` (ID `8268853`) reporta `"Location: Remote"` en el JSON de alto nivel, pero en el cuerpo del texto restringe la contratación a determinados estados de EE.UU. Otros puestos de contrato (`Senior Software Engineer, Android`, ID `8268142`) contratan en 40+ países vía Employer of Record (EOR), incluyendo Brasil y Colombia en LatAm, pero excluyendo temporalmente a Perú.
   - *Mitigación:* Ninguna oportunidad remota puede marcarse como elegible para Perú sin validación explícita del campo `proposed.eligibility` en la revisión humana.
2. **Riesgo de Perimetría y WAF en el Sector Público Peruano:**
   - *Hallazgo:* Portales como Talento Perú (`app.servir.gob.pe`) y ANIN (`convocatorias.anin.gob.pe`) devuelven HTTP 403 ante clientes automatizados.
   - *Mitigación:* Se adopta de forma explícita el modo `MANUAL_REVIEW` para el sector público peruano, preservando capturas manuales con URLs y evidencias HTTPS verificables.

---

## 9. Evidencias de Consultas y Observaciones Factuales

Se realizaron consultas HTTP no invasivas de descubrimiento técnico hacia las APIs públicas documentadas:

1. **Consulta Wikimedia Greenhouse API:**
   - Endpoint: `https://boards-api.greenhouse.io/v1/boards/wikimedia/jobs`
   - Código HTTP: `200 OK` (Content-Type: `application/json; charset=utf-8`).
   - Total de vacantes detectadas: 16 publicaciones activas.
   - Puestos relevantes identificados:
     * `8268853`: *Software Engineering Internship Program (2027)*
     * `8397050`: *Senior Site Reliability Engineer*
     * `8268142`: *Senior Software Engineer, Android (Contract)*
     * `8210560`: *Senior Data Scientist, Safety & Security*
2. **Consulta CookUnity Greenhouse API:**
   - Endpoint: `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs`
   - Código HTTP: `200 OK`.
   - Vacantes con ubicación explícita en Perú:
     * `8039990003`: *Supply Chain Analyst* (`Location: Lima, Lima Province, Peru`).
     * `8034712003`: *Product Support Engineer* (`Location: Latam (Remote)`).

---

## 10. Arquitectura de Integración Controlada

Se comprobó que **no se requiere crear nuevos colectores ni añadir librerías**:

```text
[ FUENTE PÚBLICA ATS ]
  (Greenhouse / Lever API)
         │
         │ GET (HTTP 200 JSON estructurado, 0 auth)
         ▼
[ scripts/editorial_cli.py ]
  subcomando: import --format greenhouse
         │
         │ Transformación a Schema 2 (collector/ats_connectors.py)
         ▼
[ data/candidates/inbox.local.json ] (Staging aislado en .gitignore)
         │
         ├─► validate-inbox --verify-evidence (Schema 2 y TTL 7 días)
         ├─► deduplicate (colisiones y duplicados deterministas)
         ├─► inspect (distribución de estados y vigencia)
         └─► report --json-report (informe consolidado)
         │
         ▼
[ REVISIÓN EDITORIAL HUMANA ] (Hito R2-A-02)
  (Promoción manual conforme a ADR-001; Cero escrituras al catálogo)
```

---

## 11. Resultados de Pruebas y Validación

Todas las validaciones técnicas fueron ejecutadas directamente en el checkout:

1. **Suite Completa de Pruebas Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **193 pruebas aprobadas (0 fallos, 0 errores)** en 2.79s.
2. **Validación de Catálogo y Snapshot:**
   - Comando: `python scripts/build_catalog.py --check`
   - Resultado: `Catálogo válido: 5 registros; snapshot coincide con la fuente canónica.`
3. **Validación Canónica de Calidad:**
   - Comando: `python scripts/validate_catalog.py`
   - Resultado: `Válido: 5 fichas; modo=publicación no vacía; fecha Lima=2026-11-17.`
4. **Validación Canónica de Candidatos en Staging:**
   - Comando: `python scripts/validate_candidates.py data/candidates/inbox.local.json`
   - Resultado: `Bandeja local válida: 4 candidatos; no se modificó ni se publicó el catálogo.`
5. **Pruebas End-to-End Playwright:**
   - Comando: `npx playwright test`
   - Resultado: **8 pruebas aprobadas (6.2s)** en Chromium Desktop y Mobile WebKit.
6. **Higiene Git:**
   - Comando: `git diff --check`
   - Resultado: **100% limpio**.

---

## 12. Muestra Real de Candidatos en Staging (R2-A-01-REV-06)

Se generó de forma controlada la primera muestra real de candidatos Schema 2 en `data/candidates/inbox.local.json`:

| Candidate ID | Título de la Vacante | Empleador | Modalidad | URL de Postulación Canónica | Estado de Evidencia | Estado Editorial |
|---|---|---|---|---|---|---|
| `CAND-greenhouse-public-job-board-template-8268853` | Software Engineering Internship Program (2027) | Wikimedia Foundation | Remoto | `https://job-boards.greenhouse.io/wikimedia/jobs/8268853` | `ALL_FRESH` (observado 2026-11-17) | `pending_review` |
| `CAND-greenhouse-public-job-board-template-8397050` | Senior Site Reliability Engineer | Wikimedia Foundation | Remoto | `https://job-boards.greenhouse.io/wikimedia/jobs/8397050` | `ALL_FRESH` (observado 2026-11-17) | `pending_review` |
| `CAND-greenhouse-public-job-board-template-8268142` | Senior Software Engineer, Android (Contract) | Wikimedia Foundation | Remoto | `https://job-boards.greenhouse.io/wikimedia/jobs/8268142` | `ALL_FRESH` (observado 2026-11-17) | `pending_review` |
| `CAND-greenhouse-public-job-board-template-8210560` | Senior Data Scientist, Safety & Security | Wikimedia Foundation | Remoto | `https://job-boards.greenhouse.io/wikimedia/jobs/8210560` | `ALL_FRESH` (observado 2026-11-17) | `pending_review` |

**Resultado del Reporte Editorial Automatizado:**
- Evaluados: 4 candidatos.
- Errores estructurales Schema 2: 0.
- Colisiones o duplicados: 0.
- Frescura de evidencias (TTL 7 días): 4 `ALL_FRESH`.
- Vigencia de convocatoria: 4 `DEADLINE_UNKNOWN`.
- Promocionabilidad: Bloqueada en staging con `editorialReview.status: pending_review` hasta la revisión humana del hito R2-A-02.

---

## 13. Archivos Modificados y Creados

1. **Creados:**
   - `docs/audits/r2-a-01-rev-public-sources-discovery-2026-11-17.md` (este informe técnico exhaustivo).
   - `data/candidates/inbox.local.json` (bandeja local de staging ignorada por Git con los 4 candidatos reales).
2. **Actualizados:**
   - `docs/sources/seguimiento-autorizacion-fuentes.md` (reconciliación con la estrategia ampliada de fuentes públicas y ATS reutilizables).
   - `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md` (actualización de estrategia de fuentes y estado de roadmap R2).

---

## 14. Dependencias Incorporadas

- **Nuevas dependencias de terceros:** **CERO (0)**.
- Se preserva el 100% de la soberanía tecnológica del proyecto utilizando exclusivamente la biblioteca estándar de Python 3 (`json`, `urllib.request`, `urllib.parse`, `datetime`, `html`, `re`).

---

## 15. Hashes de Integridad Criptográfica

Se registraron los hashes SHA-256 de los archivos canónicos protegidos antes y después de toda la ejecución:

| Archivo Protegido | Hash SHA-256 Inicial | Hash SHA-256 Final | Estado |
|---|---|---|---|
| `data/opportunities.seed.json` | `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` | `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` | **INALTERADO** |
| `data/opportunities.json` | `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` | `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` | **INALTERADO** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **INALTERADO** |

---

## 16. Problemas Pendientes

1. **Revisión Editorial Humana:** Los 4 candidatos reales en staging requieren evaluación individual por parte del curador editorial para resolver campos no provistos en la API (como `salary`, `benefits`, `requirements` detallados) y determinar si la restricción geográfica territorial de Wikimedia califica para el catálogo de Perú.
2. **Fuentes Estatales Peruanas:** Dado que portales como Talento Perú y ANIN mantienen WAFs restrictivos frente a bots, se debe formalizar el protocolo de captura manual (`captureMethod: manual`) para convocatorias de prácticas del sector público peruano.

---

## 17. Próxima Acción Recomendada

- **Estado de salida alcanzado:** **Estado A — FUENTE VIABLE E INTEGRADA EN STAGING**.
- **Siguiente bloque:** `R2-A-02 — Revisión editorial y aprobación de la primera oportunidad real` (inspección de la bandeja `data/candidates/inbox.local.json`, decisión curatorial sobre elegibilidad para Perú y eventual transferencia controlada hacia la semilla canónica conforme a ADR-001).
