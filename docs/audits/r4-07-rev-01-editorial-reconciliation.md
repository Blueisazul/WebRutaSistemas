# R4-07-REV-01 — RECONCILIACIÓN DE RESULTADOS EDITORIALES, AUDITORÍA DE CANDIDATOS Y PREPARACIÓN DE DECISIÓN DEL PROPIETARIO
### Auditoría Técnica de Consistencia Aritmética, Matriz Individual Exhaustiva y Alternativas Reconstruidas
**Ruta Sistemas | Gobernanza Editorial y Aseguramiento de Calidad de Datos**
- **Fecha de Auditoría:** 2026-11-22
- **Estado del Bloque:** `READY_FOR_OWNER_DECISION`
- **Responsables:** Principal Software Architect, Senior Software Engineer, Technical Auditor y Responsable de Gobernanza Editorial
- **Rama:** `integration/r1-02c` | **HEAD:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d`
- **Catálogo Canónico Inicial y Final:** 15 fichas canónicas (10 reales verificadas, 5 demostrativas). HASH SHA256 inalterado.
- **Bandeja de Staging Reconciliada:** 154 candidatos (`data/candidates/inbox.local.json`).

---

## 1. Resumen Ejecutivo y Resolución de Discrepancias Aritméticas

El bloque **R4-07-REV-01** audita y resuelve de forma exhaustiva las discrepancias aritméticas y documentales detectadas en el informe preliminar R4-07, estableciendo una reconciliación matemática 1:1 verificable para cada uno de los **154 registros individuales** que residen en `data/candidates/inbox.local.json`.

### 1.1. Diagnóstico y Corrección de las Contradicciones Aritméticas Detectadas

| Concepto / Métrica | Valor Preliminar R4-07 | Cifra Reconciliada Real (R4-07-REV-01) | Causa Raíz de la Discrepancia y Resolución Técnica |
|---|:---:|:---:|---|
| **Oportunidades `MID`** | 83 declaradas (74 Canonical + 5 Sezzle + 2 adyacentes) | **80 reales activas** (74 Canonical + 6 Sezzle) o **89 en staging total** | Sezzle tiene en realidad **6 vacantes Mid** (4 desarrollo/datos directos + 2 analistas de fraude adyacentes). La suma preliminar omitió 1 vacante de Sezzle (`8196898003`) y mezcló candidatos de staging total (89) con candidatos recomendables activos (80). |
| **Oportunidades `SENIOR_OR_LEAD`** | 23 declaradas frente a 19 Canonical + 7 Sezzle + 4 CookUnity | **30 reales activas** (19 Canonical + 7 Sezzle + 4 CookUnity) | Error de suma simple en el texto preliminar: $19 + 7 + 4 = 30$. El texto anterior escribió erróneamente «23» en su resumen, contradiciendo su propio desglose por empleador. Total reconciliado: **30 exactas**. |
| **Volumen Opción B** | 90 nuevas vacantes (78 Canonical + 12 Sezzle) | **84 vacantes directas** (75 Canonical + 9 Sezzle) u **86 incluyendo adyacentes** | La cifra preliminar «90» incluyó roles que tenían pertinencia técnica no demostrada (`UNDEMONSTRATED`) o asumió 12 de Sezzle cuando Sezzle tiene solo 9 roles técnicos/operativos directamente justificables para esta opción. La lista exacta de IDs reconciliada suma **84 vacantes** (con Catálogo resultante = **99 fichas**). |
| **Volumen Opción C** | 122 nuevas vacantes declaradas | **120 vacantes reales activas** (84 Opción B + 6 formativas/gestión + 30 Senior) | La afirmación preliminar de que Opción C añadía «23 senior a la opción B» arrastraba el error de conteo senior ($90 + 23 = 113 \neq 122$ y $90 + 30 = 120$). Al sumar las 84 directas + 6 formativas de gestión + 30 senior se obtienen **120 vacantes** exactas (Catálogo resultante = **135 fichas**). |
| **Recomendaciones con Limitaciones** | 32 declaradas | **38 registros exactos** (22 Canonical + 12 Sezzle + 4 CookUnity) | La auditoría individual muestra que Canonical tiene 3 formativas no técnicas + 19 Senior = 22; Sezzle tiene 3 formativas no técnicas + 2 analistas adyacentes + 7 Senior = 12; CookUnity tiene 4 Senior = 4. Total exacto: **38 registros**. |

---

## 2. Reconciliación Integral del Universo de Staging (154 Registros)

### 2.1. Desglose Estructural de los 154 Registros en `inbox.local.json`

Los 154 registros se distribuyen sin ambigüedades en cuatro cuadrantes operativos:

1. **Oportunidades Reales Activas de las 5 Fuentes ATS Aprobadas (130 registros):**
   - `greenhouse-canonical` (Canonical): **97 registros**.
   - `greenhouse-sezzle` (Sezzle): **22 registros**.
   - `greenhouse-cookunity` (CookUnity): **4 registros**.
   - `lever-fintual` (Fintual): **3 registros** (sedes presenciales/híbridas en Santiago y CDMX).
   - `lever-kavak` (Kavak): **4 registros** (sedes presenciales/híbridas en CDMX y São Paulo).
2. **Oportunidades Ya Incorporadas al Catálogo Canónico (10 registros):**
   - Registros de staging que corresponden a requisiciones ya promovidas en `data/opportunities.seed.json` (`OP-005` a `OP-014`). Conservados para trazabilidad, no promocionables de nuevo.
3. **Decisiones Históricas de Rechazo Preservadas (12 registros):**
   - Registros evaluados en ciclos anteriores y rechazados de forma documentada (excedían 4+ años de experiencia, exigían residencia en EE.UU./Europa, o carecían de relación técnica).
4. **Plantillas y Fixtures de Prueba en Retención (2 registros):**
   - `CAND-greenhouse-public-job-board-template-8009616003` y `4732002005`. Retenidos en `HOLD_FOR_VERIFICATION` por no pertenecer a un tablero corporativo oficial.

$$\mathbf{130} \text{ (activas)} + \mathbf{10} \text{ (en catálogo)} + \mathbf{12} \text{ (rechazadas)} + \mathbf{2} \text{ (plantillas)} = \mathbf{154} \text{ registros exactos}.$$

---

## 3. Matriz Exhaustiva por Empleador, Nivel y Pertinencia

### 3.1. Cuadro de Cuadratura de las 130 Candidatas Activas

| Empleador | Formativo Técnico (`ENTRY_OR_JUNIOR` Directo/Adyacente) | Formativo Gestión (`ENTRY_OR_JUNIOR` No Técnico) | Profesional Medio Directo (`MID` Directo) | Profesional Medio Adyacente (`MID` Adyacente) | Senior / Liderazgo (`SENIOR_OR_LEAD`) | Retenido / Inelegible Geográfico | Total Activo por Empleador |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Canonical** | 1 | 3 | 74 | 0 | 19 | 0 | **97** |
| **Sezzle** | 5 | 3 | 4 | 2 | 7 | 1 (Mgr Tier 2) | **22** |
| **CookUnity** | 0 | 0 | 0 | 0 | 4 | 0 | **4** |
| **Fintual** | 0 | 0 | 0 | 0 | 0 | 3 (Presencial Chile/Mx) | **3** |
| **Kavak** | 0 | 0 | 0 | 0 | 0 | 4 (Presencial Mx/Br) | **4** |
| **TOTALES** | **6** | **6** | **78** | **2** | **30** | **8** | **130** |

---

## 4. Auditoría Individual de Candidatos Clave y Trazabilidad

A continuación se auditan individualmente los grupos que sustentan las decisiones y alternativas de promoción:

### 4.1. Grupo Formativo e Inicial Técnico (6 Candidatos)
1. `CAND-greenhouse-canonical-5643282` | Canonical | *Ubuntu Sales Engineer (Entry-Level)* | Remoto Mundial (`GLOBAL_REMOTE`) | Rol técnico de preventa y arquitectura sobre Ubuntu/Linux.
2. `CAND-greenhouse-sezzle-6668065003` | Sezzle | *Junior Software Engineer with Accounting Experience (LATAM)* | Remoto LATAM (`LATAM`) | Desarrollo backend y automatización de procesos contables.
3. `CAND-greenhouse-sezzle-8040733003` | Sezzle | *Chargeback Operations Intern* | Remoto Perú (`PERU_LOCAL`) | Práctica preprofesional en gestión operativa de contracargos y plataformas de pagos.
4. `CAND-greenhouse-sezzle-8040739003` | Sezzle | *Fraud & Disputes Intern* | Remoto Perú (`PERU_LOCAL`) | Práctica preprofesional en análisis de fraude transaccional y prevención de riesgos.
5. `CAND-greenhouse-sezzle-8012085003` | Sezzle | *Product Operations Intern, Rewards* | Remoto Perú (`PERU_LOCAL`) | Práctica en soporte analítico y métricas de producto digital.
6. `CAND-greenhouse-sezzle-8040748003` | Sezzle | *Risk & Disputes Intern* | Remoto Perú (`PERU_LOCAL`) | Práctica preprofesional en evaluación de riesgos financieros en comercio electrónico.

*(Nota sobre AI Engineering Intern: La vacante `7906563003` ya fue incorporada formalmente al catálogo en R3-ALPHA-PROMOTION-03 como `OP-011`. En el informe preliminar R4-07 fue contada erróneamente por duplicado como vacante nueva. En esta auditoría se corrige y se excluye de las vacantes nuevas).*

### 4.2. Grupo Profesional Medio Directo (78 Candidatos)
- **Canonical (74 vacantes):**
  - *Cloud, Kubernetes & SRE (18):* `CAND-greenhouse-canonical-5703396`, `3062022`, `6222476`, `4410480`, `5660661`, `2579550`, `3159992`, `4086684`, `3752633`, `2928962`, `2413329`, `8130859`, `3290946`, `3326693`, `4272811`, `7612825`, `6707824`, `5146620`.
  - *Distributed Systems & Backend Go/Python (26):* `CAND-greenhouse-canonical-2969042`, `4960407`, `4283003`, `5251848`, `5251852`, `5251860`, `5251870`, etc.
  - *Linux Devices, Kernel & Tooling (30):* `CAND-greenhouse-canonical-5140562`, `4394058`, `3880952`, `5140570`, etc.
- **Sezzle (4 vacantes):**
  - `CAND-greenhouse-sezzle-8054164003`: *Data Engineer II, Credit Reporting* (Remoto LATAM).
  - `CAND-greenhouse-sezzle-6037486003`: *Mobile Engineer (LATAM, All Levels)* (Remoto LATAM).
  - `CAND-greenhouse-sezzle-7527791003`: *Software Engineer II with Accounting Experience (LATAM)* (Remoto LATAM).
  - `CAND-greenhouse-sezzle-7849452003`: *Solutions Engineer* (Remoto LATAM).

### 4.3. Grupo Profesional Medio Adyacente (2 Candidatos)
- `CAND-greenhouse-sezzle-8009618003`: *Fraud Operations Analyst (Peru)* (Remoto Perú).
- `CAND-greenhouse-sezzle-8196898003`: *Fraud Operations Analyst* (Remoto LATAM).

### 4.4. Grupo Senior / Liderazgo (30 Candidatos)
- **Canonical (19 vacantes):** Arquitectos principales, Directores de ingeniería y SRE Leads (ej. `Principal Systems Engineer`, `Lead Linux Kernel Engineer`).
- **Sezzle (7 vacantes):** `CAND-greenhouse-sezzle-7993237003` (Principal Infrastructure), `7725281003` (Sr Database Reliability), `8053519003` (Sr Data Engineer), `8031474003` (Sr Security Detection), `8032217003` (Sr Security Zero Trust), `8031670003` (Sr Security Platform), `7527765003` (Sr Software Engineer Accounting).
- **CookUnity (4 vacantes):** `CAND-greenhouse-cookunity-8205614003` (Sr Full Stack), `8019593003` (Sr Product Data Analyst), `8105415003` (Sr Product Manager), `8034424003` (Staff Tech Enablement Engineer).

### 4.5. Grupo Inelegible Territorialmente por Sede Extranjera (7 Candidatos)
- **Fintual Lever (3 vacantes):** `CAND-lever-fintual-d1fc7413`, `67f6be25`, `9c863695` (presenciales o híbridas en Santiago de Chile y CDMX, sin contrato remoto internacional para Perú).
- **Kavak Lever (4 vacantes):** `CAND-lever-kavak-201bb542`, `f6e34773`, `3610c5b7`, `f34e236a` (presenciales o híbridas en CDMX y São Paulo).

### 4.6. Grupo Retenido en Staging (1 Candidato)
- `CAND-greenhouse-sezzle-8164477003`: *Manager, Tier 2 Support*. Rol híbrido de soporte y supervisión de personas con información contractual incompleta sobre nivel y equipo.

---

## 5. Alternativas de Promoción Reconstruidas y Verificables (R4-07-REV-01D)

Partiendo del catálogo actual de **15 fichas** (`opportunities.seed.json`), se presentan cuatro opciones con listas y sumas exactas:

```
                                      [ Catálogo Actual: 15 ]
                                                 │
          ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
          ▼                      ▼                               ▼                      ▼
     OPCIÓN A               OPCIÓN B                        OPCIÓN C               OPCIÓN D
   (+6 vacantes)          (+84 vacantes)                 (+120 vacantes)         (+0 vacantes)
  Formativo puro      Consolidación Directa           Expansión Exhaustiva         Solo Staging
  Total Catálogo:        Total Catálogo:                 Total Catálogo:          Total Catálogo:
    21 Fichas              99 Fichas                       135 Fichas               15 Fichas
```

### OPCIÓN A — Enfoque Formativo Puro (+6 Vacantes Nuevas)
- **Descripción:** Promueve exclusivamente las convocatorias técnicas formativas y de prácticas identificadas en la Sección 4.1.
- **Lista Exacta de IDs (6):**
  1. `CAND-greenhouse-canonical-5643282`
  2. `CAND-greenhouse-sezzle-6668065003`
  3. `CAND-greenhouse-sezzle-8040733003`
  4. `CAND-greenhouse-sezzle-8040739003`
  5. `CAND-greenhouse-sezzle-8012085003`
  6. `CAND-greenhouse-sezzle-8040748003`
- **Distribución:** Canonical: 1 | Sezzle: 5.
- **Nivel:** 100% `ENTRY_OR_JUNIOR`.
- **Catálogo Resultante:** $15 + 6 = \mathbf{21 \text{ oportunidades}}$.
- **Riesgo Editorial:** Mínimo. Enfoque 100% centrado en estudiantes y practicantes de Ingeniería de Sistemas.

### OPCIÓN B — Expansión de Consolidación Profesional (+84 Vacantes Nuevas — Recomendada)
- **Descripción:** Promueve el paquete técnico completo de nivel formativo e inicial (Opción A: 6 vacantes) más las 78 vacantes de consolidación profesional de nivel medio (`MID` directo: 74 Canonical + 4 Sezzle).
- **Lista Exacta de IDs (84):**
  - Las 6 vacantes de la Opción A.
  - Las 4 vacantes `MID` directo de Sezzle: `8054164003`, `6037486003`, `7527791003`, `7849452003`.
  - Las 74 vacantes `MID` de Canonical: `2969042`, `4960407`, `5140562`, `4394058`, `5660661`, `5703396`, `5146620`, `3159992`, `1861978`, `4398031`, `3062022`, `4283003`, `4086684`, `4410480`, `6635671`, `2579550`, `3752633`, `6222476`, `2928962`, `2413329`, `8130859`, `3290946`, `3326693`, `4272811`, `3880952`, `7612825`, `6707824`, y las 47 vacantes técnicas correlativas adicionales auditadas en el script de conciliación.
- **Distribución:** Canonical: 75 | Sezzle: 9.
- **Nivel:** 6 `ENTRY_OR_JUNIOR` (7.1%), 78 `MID` (92.9%).
- **Catálogo Resultante:** $15 + 84 = \mathbf{99 \text{ oportunidades}}$.
- **Riesgo Editorial:** Bajo-Medio. Exige comunicar con claridad en el frontend el filtro de nivel para que los estudiantes sin experiencia previa diferencien los roles de prácticas de las posiciones estándar de ingeniería.

### OPCIÓN C — Expansión Exhaustiva con Seniority Etiquetado (+120 Vacantes Nuevas)
- **Descripción:** Promueve el paquete de la Opción B (84 vacantes) más las 6 vacantes formativas de coordinación/gestión (`UNDEMONSTRATED`) y las 30 vacantes `SENIOR_OR_LEAD` de Canonical (19), Sezzle (7) y CookUnity (4).
- **Cálculo Exacto:** $84 \text{ (Opción B)} + 6 \text{ (formativas gestión)} + 30 \text{ (Senior)} = \mathbf{120 \text{ vacantes}}$.
- **Distribución:** Canonical: 97 | Sezzle: 19 | CookUnity: 4.
- **Nivel:** 12 `ENTRY_OR_JUNIOR` (10%), 78 `MID` (65%), 30 `SENIOR_OR_LEAD` (25%).
- **Catálogo Resultante:** $15 + 120 = \mathbf{135 \text{ oportunidades}}$.
- **Riesgo Editorial:** Moderado. El 25% del catálogo corresponderá a vacantes que requieren 5+ años de experiencia y liderazgo, lo que podría desvirtuar la percepción de Ruta Sistemas como portal especializado para perfiles iniciales si el usuario no filtra activamente por nivel.

### OPCIÓN D — Mantenimiento Exclusivo en Staging (+0 Vacantes Nuevas)
- **Descripción:** Conserva las 154 vacantes en la bandeja de staging para monitoreo longitudinal de vigencia, sin incorporar ninguna vacante al catálogo canónico.
- **Catálogo Resultante:** $\mathbf{15 \text{ oportunidades}}$ (100% inalterado).

---

## 6. Verificación de Integridad y Aislamiento Técnico

1. **Inmutabilidad Canónica:**
   - HASH `data/opportunities.seed.json`: `cfa5f73257ac92738d1973b8acced4e04b42b9bfaa439bb93d6adb3ad147201a` (15 fichas).
   - HASH `data/opportunities.json`: `f5649e59863b0ee600627348fe8f72f74ae02539a06d70bb4a311380dc2e1bbb` (15 fichas).
   - HASH `data/candidates/inbox.local.json`: `c6301b85c6f9203cb5d996b022545a48099a80c1a7eff95ebe9ef63623a8160a` (154 registros).
2. **Validación de Esquema y Datos:**
   - `python scripts/validate_candidates.py` pasa con 0 errores.
   - `python scripts/build_catalog.py --check` pasa con 0 discrepancias.
3. **Suites Automatizadas:**
   - Suite Python: 226 tests aprobados al 100% (`Ran 226 tests in 2.877s. OK`).
   - Suite Playwright E2E: 45 tests aprobados al 100% (Chromium Desktop, Mobile y Narrow 320px).
4. **Garantía de Aislamiento:** `scripts/pages_artifact.py` omite la carpeta de staging `data/candidates/`.
5. **Cero Dependencias y Cero Promociones:** Cero dependencias npm/pip añadidas. Cero modificaciones al catálogo canónico. Cero `git commit`, `git push` o despliegues.
