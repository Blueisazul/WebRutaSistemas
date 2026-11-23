# INFORME DE PROMOCIÓN EDITORIAL APROBADA — R3-ALPHA-PROMOTION-03
## Promoción editorial del paquete completo de cuatro oportunidades Sezzle a la Alpha privada

- **Identificador de bloque:** `R3-ALPHA-PROMOTION-03`
- **Fecha de ejecución:** 2026-11-22
- **Rol y especialidad:** Principal Software Engineer, Senior Software Architect, Technical Auditor y responsable del flujo editorial
- **Proyecto:** Ruta Sistemas (`https://github.com/Blueisazul/WebRutaSistemas`)
- **Rama objetivo:** `integration/r1-02c`
- **HEAD verificado:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d`
- **Decisión humana soberana:** **`APROBACIÓN DE OPCIÓN A — LAS CUATRO OPORTUNIDADES DE SEZZLE`** (emitida expresamente por el propietario el 2026-11-22)
- **Estado final del bloque:** **`DONE`**

---

## 1. Contexto, Gobernanza y Autorización Humana

En el ciclo inmediatamente anterior (`R3-ALPHA-PROMOTION-02`), el sistema activó la salvaguarda de gobernanza *fail-closed* (`BLOCKED_PENDING_OWNER_DECISION`, preservado en [docs/audits/r3-alpha-promotion-02-blocked.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-alpha-promotion-02-blocked.md)) debido a que el propietario no había seleccionado formalmente entre las Opciones A, B, C o D preparadas en el expediente [docs/audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md).

Con fecha **2026-11-22**, el propietario emitió la autorización editorial taxativa e inequívoca:
> **«APROBACIÓN DE OPCIÓN A — LAS CUATRO OPORTUNIDADES DE SEZZLE»**

Dicha instrucción constituyó mandato suficiente y vinculante para ejecutar la promoción editorial controlada y local de las cuatro candidatas al catálogo canónico de la Alpha privada, habiendo verificado previamente su vigencia técnica en vivo contra las APIs públicas oficiales de Greenhouse.

---

## 2. Revalidación Técnica en Tiempo Real de las Oportunidades (Greenhouse ATS)

Previo a la incorporación en el catálogo canónico, se efectuó una revalidación técnica contra los endpoints REST públicos oficiales (`https://boards-api.greenhouse.io/v1/boards/sezzle/jobs`) y los formularios de postulación directa en `https://job-boards.greenhouse.io/sezzle/jobs/`:

| Requisición Greenhouse | Puesto / Título | Modalidad / Ubicación | Compensación Declarada | Estado Endpoint REST (2026-11-22) | Formulario de Postulación Web |
|:---:|---|---|:---:|:---:|:---:|
| `7906563003` | AI Engineering Intern | Remoto (Perú) | USD 1,000 / mes | HTTP 200 OK (`updated_at: 2026-11-12`) | Abierto y operativo (`application_open`) |
| `7907182003` | IT Operations Intern | Remoto (Perú) | USD 800 / mes | HTTP 200 OK (`updated_at: 2026-11-12`) | Abierto y operativo (`application_open`) |
| `8000825003` | Product Data Intern | Remoto (Perú) | USD 800 / mes | HTTP 200 OK (`updated_at: 2026-11-12`) | Abierto y operativo (`application_open`) |
| `8001111003` | Junior Software Engineer with Accounting Experience (Peru) | Remoto (Perú) | USD 1,500 - 4,000 / mes | HTTP 200 OK (`updated_at: 2026-11-12`) | Abierto y operativo (`application_open`) |

Las 4 requisiciones están 100% activas, sin indicios de cierre, orientadas contractualmente a residentes en Perú, y con remuneración en USD transparente y verificable.

---

## 3. Oportunidades Promovidas al Catálogo Canónico de la Alpha Privada

Las cuatro candidatas fueron asignadas con identificadores canónicos correlativos bajo **Opportunity Schema 2**:

### 1. `OP-011` — AI Engineering Intern (Sezzle)
- **ID Externo:** `7906563003`
- **Empleador / Difusor:** Sezzle / Portal público oficial (ATS Greenhouse)
- **Nivel:** Intern / Prácticas
- **Familia profesional:** Inteligencia Artificial / Ciencia de Datos
- **Modalidad y Ubicación:** Remoto (Perú)
- **Compensación:** USD 1,000 / mes (`amount: 1000`, `currency: USD`, `period: monthly`)
- **Tipo de contrato:** Prácticas pre/profesionales full-time (40h/semana)
- **Requisitos clave:** Estudiantes de últimos ciclos o egresados de Ingeniería de Sistemas o afines; Python avanzado; fundamentos de Machine Learning y LLMs; inglés profesional.
- **Canal de postulación:** Directo vía Greenhouse con `publisherRelation: employer_confirmed`.

### 2. `OP-012` — IT Operations Intern (Sezzle)
- **ID Externo:** `7907182003`
- **Empleador / Difusor:** Sezzle / Portal público oficial (ATS Greenhouse)
- **Nivel:** Intern / Prácticas
- **Familia profesional:** Soporte y Operaciones TI
- **Modalidad y Ubicación:** Remoto (Perú)
- **Compensación:** USD 800 / mes (`amount: 800`, `currency: USD`, `period: monthly`)
- **Tipo de contrato:** Prácticas pre/profesionales full-time (40h/semana)
- **Requisitos clave:** Estudiantes o egresados de Ingeniería de Sistemas; soporte de hardware/software corporativo; gestión de identidades y accesos (Google Workspace, Okta, Jira); inglés conversacional y escrito fluido.
- **Canal de postulación:** Directo vía Greenhouse con `publisherRelation: employer_confirmed`.

### 3. `OP-013` — Product Data Intern (Sezzle)
- **ID Externo:** `8000825003`
- **Empleador / Difusor:** Sezzle / Portal público oficial (ATS Greenhouse)
- **Nivel:** Intern / Prácticas
- **Familia profesional:** Analítica de Datos / Inteligencia de Negocios
- **Modalidad y Ubicación:** Remoto (Perú)
- **Compensación:** USD 800 / mes (`amount: 800`, `currency: USD`, `period: monthly`)
- **Tipo de contrato:** Prácticas pre/profesionales full-time (40h/semana)
- **Requisitos clave:** Estudiantes de últimos ciclos o recién egresados; SQL intermedio-avanzado; herramientas de visualización de datos (Tableau, Power BI o Metabase); pensamiento analítico orientado a producto e inglés profesional.
- **Canal de postulación:** Directo vía Greenhouse con `publisherRelation: employer_confirmed`.

### 4. `OP-014` — Junior Software Engineer with Accounting Experience (Peru) (Sezzle)
- **ID Externo:** `8001111003`
- **Empleador / Difusor:** Sezzle / Portal público oficial (ATS Greenhouse)
- **Nivel:** Junior
- **Familia profesional:** Desarrollo de Software / FinTech
- **Modalidad y Ubicación:** Remoto (Perú)
- **Compensación:** USD 1,500 – 4,000 / mes (`range: 1500-4000`, `currency: USD`, `period: monthly`)
- **Tipo de contrato:** Full-time (indefinido/planilla internacional)
- **Requisitos clave:** Grado en Ingeniería de Sistemas, Software o Informática; experiencia o conocimientos sólidos de contabilidad/conciliación financiera aplicados a desarrollo backend; Python, Java o Go; SQL; inglés profesional para trabajo en equipo distribuido internacional.
- **Canal de postulación:** Directo vía Greenhouse con `publisherRelation: employer_confirmed`.

---

## 4. Evolución del Inventario y Estructura del Catálogo

| Métrica de Catálogo | Estado Previo (`R3-ALPHA-PROMOTION-01`) | Estado Nuevo (`R3-ALPHA-PROMOTION-03`) | Variación |
|---|:---:|:---:|:---:|
| Total oportunidades canónicas | 11 | **15** | +4 vacantes reales |
| Oportunidades reales activas | 6 (CookUnity OP-005, Canonical OP-006..OP-010) | **10** (+ Sezzle OP-011..OP-014) | +4 vacantes activas (+66.7%) |
| Oportunidades remotas activas | 5 (Canonical OP-006..OP-010) | **9** (+ Sezzle OP-011..OP-014) | +4 vacantes remotas (+80%) |
| Oportunidades con salario en USD | 1 (Canonical OP-006) | **5** (Canonical OP-006 + Sezzle OP-011..OP-014) | +4 vacantes con salario transparente |
| Oportunidades formativas (Intern) | 0 | **3** (Sezzle OP-011, OP-012, OP-013) | +3 pasantías universitarias |
| Fichas demostrativas | 5 (OP-001..OP-004, QA-001) | 5 (OP-001..OP-004, QA-001) | Sin cambios |
| Bandeja staging (`inbox.local.json`) | 24 candidatos | 24 candidatos (4 en `pending_review` con nota de promoción) | 0 duplicados, trazabilidad preservada |

---

## 5. Trazabilidad Criptográfica de Archivos y Datos

| Archivo Modificado / Auditado | Estado | Hash SHA-256 Verificado |
|---|:---:|---|
| `data/opportunities.seed.json` | **Actualizado (15 fichas)** | `cfa5f73257ac92738d1973b8acced4e04b42b9bfaa439bb93d6adb3ad147201a` |
| `data/opportunities.json` | **Regenerado (15 fichas)** | `f5649e59863b0ee600627348fe8f72f74ae02539a06d70bb4a311380dc2e1bbb` |
| `data/candidates/inbox.local.json` | **Actualizado (trazabilidad de promoción)** | `fecc1d7b14fac206b337b3df237c02eb5eb5f5a41540dbd5c8dcfc41b60bfd8d` |
| `collector/sources.json` | **100% INTACTO** | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` |
| `docs/audits/r3-alpha-promotion-02-blocked.md` | **PRESERVADO INTACTO** | Registro histórico del bloqueo previo |

---

## 6. Resultados de la Suite Completa de Verificación

Se ejecutó la totalidad de las verificaciones automatizadas sin ninguna omisión:

1. **`python scripts/validate_catalog.py`:**
   - Resultado: `Válido: 15 fichas; modo=publicación no vacía; fecha Lima=2026-11-22.`
2. **`python scripts/build_catalog.py --check`:**
   - Resultado: `Catálogo válido: 15 registros; snapshot coincide con la fuente canónica.`
3. **`python scripts/validate_candidates.py data/candidates/inbox.local.json --as-of 2026-11-22`:**
   - Resultado: `Bandeja local válida: 24 candidatos; no se modificó ni se publicó el catálogo.`
4. **`python -m unittest discover -s tests -p "test_*.py"`:**
   - Resultado: `Ran 193 tests in 3.510s. OK.` (193/193 pruebas unitarias y de integración aprobadas).
5. **`node tests/catalog_ui.test.cjs`:**
   - Resultado: `OK: public catalog filtering scenarios passed. OK: root/Pages paths and failed-catalog degradation scenarios passed.`
6. **`npx playwright test`:**
   - Resultado: `20 passed (32.7s)` (10 pruebas en Chromium Desktop + 10 pruebas en Mobile Pixel 5, cubriendo paginación, filtros de modo remoto, modal de detalle, comparador lado a lado con requisitos y omisión estricta de datos desconocidos).
7. **`git diff --check`:**
   - Resultado: 0 errores de sintaxis o espacios en blanco.

---

## 7. Preservación Estricta de Restricciones y Gobernanza

- **Cero nuevas dependencias:** 0 npm, 0 pip añadidos.
- **Cero publicación externa:** Sin despliegue en GitHub Pages, sin merge a `main`, sin push remoto, sin `git commit`.
- **Ámbito estricto de Alpha privada:** Servidor loopback local `127.0.0.1:4173`.
- **Fuentes en `collector/sources.json`:** Permanece con `enabled: false` y términos en `pending_review`.
- **R3-02 formal:** Permanece en `NOT_STARTED` / `PENDING_HUMAN`.
- **R3-03, R3-04, R3-05 y R4:** Permanecen estrictamente `BLOCKED`.
