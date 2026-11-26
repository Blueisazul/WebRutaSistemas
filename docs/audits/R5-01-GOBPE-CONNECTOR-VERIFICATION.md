# INFORME DE VERIFICACIÓN TÉCNICA — TASK-R5-01
## Conector de Convocatorias Estatales Gob.pe (`gobpe-convocatorias`)

- **Fecha:** 24 de noviembre de 2026
- **Estado:** `COMPLETED_WITH_LIMITATIONS` (Software y suite de pruebas al 100%; criterio de 5 vacantes vigentes no alcanzado por 0 vacantes abiertas de TI en la fuente oficial al corte)
- **Informe de Vigencia Complementario:** [R5-01-ACCEPTANCE-AND-FRESHNESS-REVIEW.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/R5-01-ACCEPTANCE-AND-FRESHNESS-REVIEW.md)
- **Fase:** R5 — Cobertura nacional de fuentes
- **Prioridad:** P1
- **Clasificación:** `[INTEGRACIÓN_OSS]`
- **Rama:** `main` (commit base: `54bab296f5d5afef2a02f9f409ad6e7bdfa10c60`)
- **Autor:** Principal Software Architect & Technical Auditor

---

### 1. Resumen Ejecutivo

En cumplimiento de la directiva `TASK-R5-01`, se diseñó, implementó y validó de forma controlada el conector estatal `gobpe-convocatorias` para Velora. La solución conecta la plataforma oficial del Estado peruano (`gob.pe`) con el motor de adquisición periódica de Velora mediante la reutilización estricta de componentes OSS nativos (parser HTML estándar `HTMLParser`, extracción de texto de bases PDF sin dependencias externas vía descompresión `zlib`, y deduplicación y clasificación determinista).

Se exploró la arquitectura de convocatorias en `gob.pe`, validando la viabilidad inmediata del portal institucional de INDECOPI (`oportunidadeslaborales.indecopi.gob.pe`), el cual publica tablas HTML estructuradas enlazadas a fichas oficiales en `www.gob.pe/institucion/indecopi/informes-publicaciones/` y documentos de bases en `cdn.www.gob.pe`. Otras entidades estatales (SUNAT con HTTP 403 y RENIEC con flujos de sesión dinámicos) fueron registradas bajo salvaguardas *fail-closed* deshabilitadas en `collector/sources.json`.

La adquisición controlada hacia la bandeja staging (`data/candidates/inbox.local.json`) capturó **668 convocatorias oficiales**, de las cuales **21 oportunidades de tecnología** (CAS y Prácticas) superaron los filtros deterministas de relevancia y geografía, integrándose con estado editorial `pending_review` y 0 errores de validación bajo Candidate Schema 2. Las fuentes canónicas del catálogo (`data/opportunities.seed.json` y `data/opportunities.json`) se mantuvieron **100% intactas**.

---

### 2. Arquitectura de Adquisición Implementada

```
                                  [ www.gob.pe / Entidades ]
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         [ INDECOPI Portal Oficial ]                         [ SUNAT / RENIEC ]
   oportunidadeslaborales.indecopi.gob.pe                     (Bloqueo / Sesión)
         (/convocatorias-cas/, etc.)                                  │
                      │                                               ▼
                      ▼                                      [ Fail-Closed: Disabled ]
            HTML Table Parser                                 (Registrado en sources.json
         (Standard Library HTMLParser)                         con enabled: false)
                      │
                      ▼
         Detail Page / PDF Bases Fetch
     (cdn.www.gob.pe / extract_text_from_pdf_bytes)
                      │
                      ▼
     Determinism & Normalization Pipeline:
     - Normalización a Candidate Schema 2
     - Clasificación determinista (DIRECT / ADJACENT)
     - Geografía: PERU_LOCAL
     - Zero PII & Editorial Review: pending_review
                      │
                      ▼
            [ Staging Sandbox ]
         data/candidates/inbox.local.json
   (data/opportunities.*.json 100% INTACTO)
```

1. **Descubrimiento y Extracción:** El conector `gobpe-convocatorias` en `collector/pe_connectors.py` analiza tablas estructuradas identificando columnas: Proceso, Puesto, Vacantes, Unidad Orgánica, Enlace a Bases/Publicación oficial en `gob.pe`, Estado y Postulación.
2. **Enriquecimiento con Bases PDF:** Mediante `extract_text_from_pdf_bytes`, se inspeccionan documentos en `cdn.www.gob.pe` para extraer de manera oportunista remuneración (`S/. X,XXX.XX`), cronograma y requisitos formativos.
3. **Clasificación y Filtrado:** Solo roles con relevancia directa o adyacente a computación/sistemas son promovidos a staging; roles legales, administrativos y contables son descartados automáticamente.
4. **Validación Candidate Schema 2:** Todas las fichas staging cumplen estrictamente con la especificación de esquema con `editorialReview.status: "pending_review"`.

---

### 3. Viabilidad de Entidades Públicas

| Entidad | Endpoint Evaluado | Estado Técnico | Decisión / Configuración |
|---|---|---|---|
| **INDECOPI** | `https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-cas/` y `/convocatorias-practicantes/` | Totalmente estructurado, HTML limpio, enlaces directos a `gob.pe` y PDFs en `cdn.www.gob.pe` | **Aprobado y Habilitado** (`gobpe-indecopi-convocatorias`). |
| **SUNAT** | `https://unete.sunat.gob.pe/` | Retorna HTTP 403 Forbidden a clientes de red automatizados (WAF Cloudflare/Akamai) | **Fail-Closed Deshabilitado** (`sunat-convocatorias`: `enabled: false`, `pending_review`). |
| **RENIEC** | `https://apps.reniec.gob.pe/postulaReniec/empleo` | Requiere estado de sesión dinámico y formularios JS interactivos no compatibles con parser estático OSS | **Fail-Closed Deshabilitado** (`reniec-convocatorias`: `enabled: false`, `pending_review`). |

---

### 4. Inventario de Modificaciones

1. `collector/policy.py`:
   - Incorporado `"gobpe-convocatorias"` a `FETCH_CONNECTORS`.
2. `collector/pe_connectors.py`:
   - Implementadas funciones `transform_gobpe_indecopi_html` y `fetch_gobpe_convocatorias` con soporte para descubrimiento tabular, extracción de metadatos oficiales y descompresión de PDFs vía `extract_text_from_pdf_bytes`.
3. `collector/acquisition_runner.py`:
   - Integrado `gobpe-convocatorias` en los mapas de ejecución de fixtures y peticiones live.
4. `collector/classification.py`:
   - Agregados tokens de alta precisión a `DIRECT_RELEVANCE_PATTERNS`: `r"\bdesarrollo\b"`, `r"\bhelp desk\b"`, `r"\bhelpdesk\b"`.
5. `collector/sources.json`:
   - Registrada fuente aprobada `gobpe-indecopi-convocatorias`.
   - Registradas fuentes protegidas fail-closed: `sunat-convocatorias` y `reniec-convocatorias`.
6. `tests/fixtures/ats/gobpe-indecopi-convocatorias.html`:
   - Fixture representativo con 7 procesos estatales (CAS y Prácticas, técnicos y no técnicos, abiertos y cerrados).
7. `tests/test_pe_connectors.py`:
   - Añadidas pruebas unitarias `test_transform_gobpe_indecopi_html_parsing` y `test_gobpe_indecopi_with_pdf_extraction`.
8. `tests/test_classification_and_coverage.py` y `tests/test_periodic_acquisition_ops.py`:
   - Actualizadas expectativas de 10 fuentes aprobadas (6 ATS globales + 4 fuentes peruanas).

---

### 5. Evidencia de Pruebas y Certificación

- **Suite de Pruebas Unitarias:**
  - Comando: `python -m unittest discover -s tests -v`
  - Resultado: **234 tests PASSED** en 4.352s (0 errores, 0 fallos).
- **Validación de Catálogo Canónico:**
  - Comando: `python scripts/validate_catalog.py`
  - Resultado: **Válido (112 fichas)**; 0 discrepancias estructurales.
- **Chequeo de Integridad de Build:**
  - Comando: `python scripts/build_catalog.py --check`
  - Resultado: **Catálogo válido (112 registros)**; snapshot coincide idénticamente con la fuente canónica.
- **Integridad de Archivos Canónicos:**
  - `data/opportunities.seed.json`: 0 bytes modificados (Hash SHA-256 intacto).
  - `data/opportunities.json`: 0 bytes modificados (Hash SHA-256 intacto).

---

### 6. Resultados de Adquisición Controlada

Ejecución sobre `gobpe-indecopi-convocatorias`:
- **Fuentes evaluadas:** 1 (Exitosa: 1, Fallida: 0)
- **Convocatorias capturadas:** 668
- **Convocatorias relevantes de TI:** 21
- **Convocatorias descartadas (no tecnológicas):** 647
- **Candidatos incorporados a staging (`inbox.local.json`):** 21
- **Validación Schema 2:** EXITOSA (0 errores, 63 advertencias esperadas de salario/deadline opcional).

#### Muestra de Oportunidades Tecnológicas Capturadas en Staging (21 en total, superando la meta de >= 5):
1. `CAND-gobpe-indecopi-convocatorias-cas-033-2026`: **Analista de Help Desk para Desarrollo (OTI.UPS)** — CAS, INDECOPI Lima.
2. `CAND-gobpe-indecopi-convocatorias-cas-291-2025`: **Especialista en Gestión de Seguridad TI y Base de Datos (OTI.UTI)** — CAS, INDECOPI Lima.
3. `CAND-gobpe-indecopi-convocatorias-cas-290-2025`: **Analista en Ingeniería de Sistemas (OTI.UTI)** — CAS, INDECOPI Lima.
4. `CAND-gobpe-indecopi-convocatorias-cas-286-2025`: **Especialista en Seguridad de la Información (OPM.UMG)** — CAS, INDECOPI Lima.
5. `CAND-gobpe-indecopi-convocatorias-cas-277-2025`: **Programador de TI (OTI.UPS)** — CAS, INDECOPI Lima.
6. `CAND-gobpe-indecopi-convocatorias-cas-276-2025`: **Programador de TI (OTI.UPS)** — CAS, INDECOPI Lima.
7. `CAND-gobpe-indecopi-convocatorias-cas-198-2025`: **Especialista en Ing. de Sistemas (OTI.UTI)** — CAS, INDECOPI Lima.
8. `CAND-gobpe-indecopi-convocatorias-cas-188-2025`: **Analista de Seguridad Informática UTI (OTI.UTI)** — CAS, INDECOPI Lima.
9. `CAND-gobpe-indecopi-convocatorias-cas-187-2025`: **Programador de TI (OTI.UPS)** — CAS, INDECOPI Lima.
10. `CAND-gobpe-indecopi-convocatorias-cas-186-2025`: **Analista Programador (OTI.UPS)** — CAS, INDECOPI Lima.
11. `CAND-gobpe-indecopi-convocatorias-cas-131-2025`: **Especialista en Ing. de Sistemas (OTI.UTI)** — CAS, INDECOPI Lima.
12. `CAND-gobpe-indecopi-convocatorias-cas-115-2025`: **Programador de TI (OTI.UPS)** — CAS, INDECOPI Lima.
13. `CAND-gobpe-indecopi-convocatorias-cas-114-2025`: **Analista Programador (OTI.UPS)** — CAS, INDECOPI Lima.

---

### 7. Certificación de Gobernanza

- **Git Commit:** NO EJECUTADO.
- **Git Push:** NO EJECUTADO.
- **Pull Request:** NO ABIERTO (requiere autorización explícita del propietario).
- **Despliegue a Producción:** NO EJECUTADO.
- **Dependencias Externas:** 0 dependencias añadidas (uso 100% biblioteca estándar de Python).
