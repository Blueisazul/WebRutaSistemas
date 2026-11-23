# INFORME DE BLOQUEO POR PUERTA DE DECISIÓN HUMANA — R3-ALPHA-PROMOTION-02-BLOCKED
## Promoción Editorial Controlada de Oportunidades Sezzle a la Alpha Privada

- **Identificador de bloque:** `R3-ALPHA-PROMOTION-02`
- **Fecha de evaluación:** 2026-11-22
- **Rol y especialidad:** Principal Software Engineer, Senior Software Architect & Technical Auditor
- **Proyecto:** Ruta Sistemas (`https://github.com/Blueisazul/WebRutaSistemas`)
- **Rama objetivo:** `integration/r1-02c`
- **HEAD verificado:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d`
- **Estado final:** **`BLOCKED_PENDING_OWNER_DECISION`** (Bloqueado a la espera de decisión editorial soberana del propietario)

---

## 1. Diagnóstico de la Puerta de Decisión Obligatoria

En estricto cumplimiento de la **Sección 2 (Puerta de Decisión Obligatoria)** de las directrices rectoras de `R3-ALPHA-PROMOTION-02`, se procedió a verificar la existencia de una autorización editorial explícita, verificable y unívoca emitida por el propietario del proyecto respecto a las cuatro candidatas de Sezzle evaluadas en el expediente `R3-ALPHA-OWNER-REVIEW-02` ([docs/audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md)).

### Resultado de la inspección de gobernanza:
1. **Ausencia de elección expresa de opción:** Tras auditar la totalidad de los documentos del repositorio, los registros de investigación cualitativa (`INTERNAL-FEEDBACK-01` e `INTERNAL-FEEDBACK-02`) y el contexto de instrucciones recibidas, **no existe ningún registro de selección entre las Opciones A, B, C o D**.
2. **Aplicación del principio de no asunción de autorizaciones genéricas:** La directriz prohíbe taxativamente interpretar afirmaciones como *"continúa"*, *"tienes autorización para avanzar"* o la conformidad cualitativa con el prototipo como una aprobación tácita para modificar los archivos canónicos del catálogo.
3. **Activación de la salvaguarda de bloqueo (*Fail-Closed*):** Al no concurrir una resolución humana explícita, se activan inmediatamente las medidas de preservación:
   - **No se ejecuta la promoción editorial.**
   - **No se modifica el catálogo canónico (`data/opportunities.seed.json` y `data/opportunities.json`).**
   - **No se altera la bandeja de staging (`data/candidates/inbox.local.json`).**
   - **El estado del bloque se fija formalmente en `BLOCKED_PENDING_OWNER_DECISION`.**

---

## 2. Decisión Concreta Pendiente y Opciones a Disposición del Propietario

El expediente técnico `R3-ALPHA-OWNER-REVIEW-02` acreditó que las cuatro vacantes de Sezzle cumplen los requisitos técnicos (remotas, elegibles explícitamente desde Perú, salarios publicados en USD y conformes a Schema 2). Para desbloquear la promoción hacia el catálogo canónico de la Alpha privada, el propietario debe manifestar expresamente cuál de las siguientes opciones adopta:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OPCIONES DE DECISIÓN EDITORIAL PARA EL PROPIETARIO (EXPEDIENTE SEZZLE)                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPCIÓN A: Aprobación del lote completo (4 vacantes)                                              │
│ - Incorpora: AI Intern ($1,000), IT Ops Intern ($800), Data Intern ($800) y Jr Software Dev     │
│ - Impacto: Catálogo real de Alpha privada crece de 6 a 10 vacantes (15 fichas totales).          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPCIÓN B: Aprobación exclusiva de pasantías formativas (3 vacantes)                              │
│ - Incorpora: AI Intern ($1,000), IT Ops Intern ($800) y Data Intern ($800).                      │
│ - Descarta / retiene: Jr Software Engineer with Accounting Experience ($1,500-$4,000).           │
│ - Impacto: Catálogo real crece a 9 vacantes, con enfoque 100% formativo universitario.           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPCIÓN C: Aprobación selectiva individual personalizada                                          │
│ - El propietario indica taxativamente cuáles candidatos específicos autoriza y cuáles no.        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPCIÓN D: Conservación íntegra en staging sin promoción (0 vacantes)                             │
│ - Todas las candidatas permanecen en data/candidates/inbox.local.json con estado pending_review.  │
│ - Catálogo canónico permanece inalterado en 6 vacantes reales y 5 demostrativas.                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Inventario de Candidatas Evaluadas en Staging (En Espera de Decisión)

Las cuatro posiciones se encuentran íntegras y validadas en `data/candidates/inbox.local.json`:

| ID Staging | ID Externo ATS | Puesto / Título Convocatoria | Empleador | Modalidad | Compensación Declarada | Decisión Editorial Actual |
|---|:---:|---|---|:---:|:---:|:---:|
| `CAND-greenhouse-public-job-board-template-7906563003` | `7906563003` | AI Engineering Intern | Sezzle | Remoto (Perú) | $1,000 USD / mes | `pending_review` (`PENDING_HUMAN`) |
| `CAND-greenhouse-public-job-board-template-7907182003` | `7907182003` | IT Operations Intern | Sezzle | Remoto (Perú) | $800 USD / mes | `pending_review` (`PENDING_HUMAN`) |
| `CAND-greenhouse-public-job-board-template-8000825003` | `8000825003` | Product Data Intern | Sezzle | Remoto (Perú) | $800 USD / mes | `pending_review` (`PENDING_HUMAN`) |
| `CAND-greenhouse-public-job-board-template-8001111003` | `8001111003` | Junior Software Engineer with Accounting Experience (Peru) | Sezzle | Remoto (Perú) | $1,500 - $4,000 USD / mes | `pending_review` (`PENDING_HUMAN`) |

---

## 4. Confirmación de Integridad Criptográfica y Preservación de Datos

Se ejecutó una verificación de hashes SHA-256 para constatar que ningún archivo canónico ni bandeja de trabajo ha sufrido modificaciones:

| Archivo Auditado | Estado | Hash SHA-256 Verificado |
|---|:---:|---|
| `data/opportunities.seed.json` | **100% INTACTO** | `789a5fe4777a596a031089f48885a5d492c401fcf01df1f5ec56b6df490de61c` |
| `data/opportunities.json` | **100% INTACTO** | `a6ccb384f232af9a3e05bfce4807691c270b23eba37978e3a69aee06802e9e2c` |
| `collector/sources.json` | **100% INTACTO** | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` |
| `data/candidates/inbox.local.json`| **100% INTACTO** | `9b8baf519f713906a45ba2a33d593d8a27049475594afa8e49f78a32483192b3` |

- **Dependencias añadidas:** 0 (0 npm, 0 pip).
- **Publicación externa:** Cero (sin despliegues en GitHub Pages, sin merge a `main`, sin push remoto).

---

## 5. Estado de Gobernanza de Fases Maestras

- **`R3-ALPHA-PROMOTION-02`:** **`BLOCKED_PENDING_OWNER_DECISION`**.
- **`R3-02` formal (Trabajo de campo con usuarios reales):** Permanece en **`NOT_STARTED` / `PENDING_HUMAN`** (0 sesiones formales completadas en `docs/research/sessions/`).
- **`R3-03` (Consolidación de hallazgos):** Permanece estrictamente **`BLOCKED`**.
- **`R3-04` (Refactor UX):** Permanece estrictamente **`BLOCKED`**.
- **`R3-05` (Decisión sobre MVP):** Permanece estrictamente **`BLOCKED`**.
- **`R4` (Automatización controlada):** Permanece estrictamente **`BLOCKED`**.

---

## 6. Siguiente Acción para Desbloquear

Para reanudar la ejecución técnica de la promoción, el propietario del proyecto debe emitir una instrucción explícita indicando la opción seleccionada. Por ejemplo:
> *"Autorizo la Opción A del expediente Sezzle"* (o *Opción B*, *Opción C*, u *Opción D*).

Tan pronto como se reciba dicha indicación inequívoca, el agente procederá inmediatamente con la revalidación de vigencia, deduplicación, asignación de identificadores canónicos (`OP-011` a `OP-014`), actualización de `data/opportunities.seed.json`, sincronización de `data/opportunities.json` y corrida de las suites de prueba completas (Playwright, Python unittests y validadores de catálogo).
