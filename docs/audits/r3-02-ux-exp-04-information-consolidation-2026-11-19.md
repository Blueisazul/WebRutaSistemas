# AUDITORÍA DE CONSOLIDACIÓN DE INFORMACIÓN Y ELIMINACIÓN DE REDUNDANCIA — R3-02-UX-EXP-04

**Proyecto:** Ruta Sistemas
**Fecha:** 2026-11-19
**Fase:** R3 — Validación de Producto / Iteración de Claridad y Experiencia de Usuario
**Rama de trabajo:** `integration/r1-02c`
**Commit base (HEAD remoto):** `9d747c537039ecf6ea2a0f4cca68a44277c6ea2b` (`origin/integration/r1-02c`)
**Principio rector:** *«Un dato, una ubicación, una interpretación»*
**Clasificación:** `[CONSOLIDACIÓN_UX]` `[ARQUITECTURA_DE_INFORMACIÓN]` `[QA/VALIDACIÓN]` `[AUDITORÍA_TÉCNICA]`
**Resultado del Gate:** **DONE** (Consolidación de información completada, redundancias eliminadas, 14 pruebas E2E y 193 pruebas Python superadas).

---

## 1. Contexto y Objetivo

Tras las iteraciones exploratorias `R3-02-UX-EXP-01`, `02` y `03`, la ficha de oportunidad de Ruta Sistemas presentaba duplicaciones informativas y semánticas que aumentaban la carga cognitiva:
- La modalidad de trabajo se repetía en encabezado, triaje, cuadrícula de condiciones y continuidad/riesgos.
- La compensación se mostraba en el triaje, en la cuadrícula y en continuidad/riesgos.
- La ubicación y elegibilidad territorial se fragmentaban y repetían en múltiples bloques.
- Los requisitos del puesto contenían una concatenación redundante de las tecnologías declaradas, que a su vez se mostraban en el triaje.
- La continuidad y los riesgos actuaban como un contenedor residual donde se repetían salario, modalidad y experiencia.
- La información de verificación y vigencia aparecía reiteradamente en badges, alertas, cuadrícula y tarjeta de procedencia.

El objetivo de `R3-02-UX-EXP-04` ha sido reorganizar la presentación visual para que **cada dato tenga una única ubicación principal canónica**, eliminando repeticiones superficiales y semánticas sin perder datos, rigor técnico ni trazabilidad documental.

---

## 2. Fase A — Inventario de Redundancias (Matriz de Comparación)

| Dimensión Informativa | Ubicaciones Anteriores (Pre-UX-EXP-04) | Ubicación Canónica Adoptada (UX-EXP-04) | Decisión de Consolidación |
|---|---|---|---|
| **Modalidad de trabajo** | 1. Header tag (`modeTag` en encabezado)<br>2. Tarjeta en Triaje Rápido (`Modalidad de trabajo`)<br>3. Cuadrícula de condiciones (`Modalidad`)<br>4. Texto de riesgos (`job.risk`) | **Cuadrícula de condiciones** (`detail-grid` -> `Modalidad`). | Retirada de tags superiores, triaje y texto redundante. Si la fuente no la informa: se muestra *«No especificada»* una sola vez en la cuadrícula. |
| **Compensación económica** | 1. Tarjeta en Triaje Rápido (`Compensación económica`)<br>2. Cuadrícula de condiciones (`Compensación`)<br>3. Texto de riesgos (`job.risk`) | **Cuadrícula de condiciones** (`detail-grid` -> `Compensación`). | Retirada de triaje y riesgos. Si no se publica: se muestra *«No publicado»* (y su nota aclaratoria factual) una sola vez. |
| **Ubicación y elegibilidad** | 1. Tarjeta en Triaje Rápido (`Elegibilidad territorial`)<br>2. Cuadrícula de condiciones (`Elegibilidad / ubicación`)<br>3. Tarjeta de catálogo (`p.job-location`: `Lima, Perú · Perú`) | **Cuadrícula de condiciones:** item unificado `Ubicación y elegibilidad` formateado sin duplicaciones (`Lima, Perú`). **Tarjeta de catálogo:** formateo unificado. | Triaje conserva únicamente la señal de atención sobre elegibilidad desde Perú. La cuadrícula consolida lugar de trabajo y ámbito de contratación mediante helper determinista `formatLocationEligibility(job)`. |
| **Tecnologías y herramientas** | 1. Tarjeta en Triaje Rápido (`Tecnologías declaradas`)<br>2. Texto de requisitos (`<br><b>Tecnologías/señales:</b>`)<br>3. Sección narrativa de tecnologías | **Sección narrativa independiente:** `Tecnologías y herramientas declaradas`. | Separación estricta entre **Requisitos del puesto** (obligatorios) y **Tecnologías declaradas** (herramientas/lenguajes). Eliminada la duplicación dentro de requisitos y eliminada la tarjeta de triaje. |
| **Experiencia requerida** | 1. Tarjeta en Triaje Rápido (`Nivel y experiencia`)<br>2. Requisitos del puesto (`1+ años de experiencia`)<br>3. Continuidad y riesgos (`Exige 1+ años`) | **Requisitos del puesto** (detalle exhaustivo) + **Triaje Rápido** (señal de atención: `Por revisar: Nivel Junior: la convocatoria exige al menos 1 año de experiencia previa`). | Retirada de riesgos. En el triaje actúa como alerta de discrepancia entre nivel Junior y experiencia previa exigida, sin atribuir calificaciones al postulante. |
| **Vigencia y verificación** | 1. Tag de encabezado (`statusTag`)<br>2. Tarjeta en Triaje Rápido (`Vigencia y comprobación`)<br>3. Cuadro `Qué se verificó` / `evidence-box`<br>4. Cuadrícula de condiciones (`Última verificación o consulta`)<br>5. Tarjeta de fuente oficial (`Última comprobación registrada`) | **Cuadrícula de condiciones** (`Última verificación o consulta`), estado de postulación en **evidence-box** y badge oficial en **tarjeta de fuente**. | Retirada del triaje rápido y retirada del párrafo redundante de la tarjeta de fuente oficial. |
| **Continuidad y riesgos** | Sección narrativa completa (`Continuidad y riesgos`) que concatenaba `job.continuity` y `job.risk`. | **Consolidada en Cuadrícula** (`Contrato y plazo` vía `formatContractDuration(job)`). | **Sección narrativa eliminada por completo.** Las condiciones legítimas de permanencia y contrato se muestran en la cuadrícula de condiciones; los riesgos que repetían salario, modalidad y experiencia quedan resueltos en sus ubicaciones canónicas. |
| **Triaje Rápido** | 8 tarjetas que reproducían casi la totalidad de los campos de la ficha. | **3 indicadores de síntesis y atención clave:**<br>1. *Pertinencia técnica*<br>2. *Elegibilidad territorial*<br>3. *Nivel y experiencia* | Rediseñado a 3 tarjetas enfocadas en señales prioritarias para el perfil de egresados/estudiantes de Ingeniería de Sistemas. |

---

## 3. Arquitectura de Información Objetivo Adoptada

```
+------------------------------------------------------------------------------------+
| ENCABEZADO DE OPORTUNIDAD                                                          |
| Requisición · Fuente · Título · Empleador · Sector                                 |
| Tags: [Estado de revisión] [Familia profesional] [Tipo de oportunidad]             |
+------------------------------------------------------------------------------------+
| TRIAJE RÁPIDO DE LA CONVOCATORIA (3 Señales Clave)                                 |
| [1. Pertinencia técnica]  [2. Elegibilidad territorial]  [3. Nivel y experiencia]   |
+------------------------------------------------------------------------------------+
| QUÉ SE VERIFICÓ / ESTADO DE PUBLICACIÓN (evidence-box)                              |
+------------------------------------------------------------------------------------+
| CONDICIONES DE TRABAJO (detail-grid: Cuadrícula Canónica)                          |
| - Modalidad               - Entidad que difunde                                    |
| - Ubicación y elegibilidad - Compensación                                          |
| - Contrato y plazo        - Fecha límite                                           |
| - Fecha de publicación    - Última verificación o consulta                         |
+------------------------------------------------------------------------------------+
| CUERPO NARRATIVO Y CONTENIDO DETALLADO                                             |
| 1. Qué harías (tareas declaradas)                                                  |
| 2. Requisitos del puesto (exigencias formales sin duplicar herramientas)           |
| 3. Tecnologías y herramientas declaradas (lenguajes/plataformas observados)        |
| 4. Qué experiencia podrías llevar al siguiente paso (aprendizaje proyectado)       |
| 5. Beneficios publicados (si existen condiciones documentadas)                     |
+------------------------------------------------------------------------------------+
| PROCEDENCIA Y POSTULACIÓN                                                          |
| - Tarjeta de fuente oficial verificada (con enlace original y botón postular)     |
| - Desglose colapsable de procedencia por campo (21 evidencias históricas)          |
+------------------------------------------------------------------------------------+
```

---

## 4. Implementación Técnica y Cambios en Código

### 4.1 Modificaciones en `app.js`

1. **Helper `formatLocationEligibility(job)`:**
   - Resuelve de manera unificada y determinista la ubicación física y el territorio de contratación.
   - Si la ubicación contiene la elegibilidad (e.g. `Surquillo, Lima, Perú` y `Perú`), muestra la ubicación sin redundar `(Elegibilidad: Perú)`.
   - Si difieren, las presenta estructuradamente: `${location} (Elegibilidad: ${eligibility})`.
   - Utilizado tanto en la cuadrícula de condiciones de la ficha como en `renderCard()` en el listado general.

2. **Helper `formatContractDuration(job)`:**
   - Agrupa ordenadamente `contractType`, `duration` y `continuity`.
   - Filtra términos vacíos o nulos evitando redundancia léxica.
   - Para `OP-005`, consolida el régimen laboral y permanencia: `Full-time; duración no especificada · Puesto regular de tiempo completo; sujeto a desempeño y evaluación del empleador.`

3. **Rediseño de `quickTriage(job)` y `renderQuickTriage(job)`:**
   - Reducido de 8 a 3 tarjetas: `Pertinencia técnica`, `Elegibilidad territorial`, `Nivel y experiencia`.
   - Eliminadas las 5 tarjetas que duplicaban campos detallados: `tecnologias`, `modalidad`, `tipo`, `compensacion`, `vigencia`.
   - Subtítulo actualizado: *«Lectura factual de 3 señales clave de la convocatoria oficial. Describe hechos de la vacante, no evalúa tu perfil personal ni genera un puntaje global.»*

4. **Reestructuración de `renderDetailContent(job)`:**
   - Retiro de `modeTag(job)` de los tags de cabecera (`dialog-tags`), dejando únicamente el estado, familia y tipo.
   - Cuadrícula de 8 celdas limpias con ubicaciones canónicas exclusivas.
   - Sección `Requisitos del puesto` sin el sufijo redundante `Tecnologías/señales:`.
   - Sección independiente `Tecnologías y herramientas declaradas` condicional a `knownValue(job.skills)`.
   - Eliminación total de la sección `<section class="detail-section"><h3>Continuidad y riesgos</h3>`.
   - Retiro del párrafo redundante de verificación en `.official-source-card`.

### 4.2 Modificaciones en `src/site.css` y `styles.css`

- `.triage-grid`: Reconfigurado a `grid-template-columns: repeat(3, minmax(0, 1fr));` en pantallas de escritorio/tablet para disponer armónicamente los 3 indicadores clave.
- Mantenido en `grid-template-columns: 1fr;` en pantallas móviles (`<= 680px`).
- Clases de estilo sincronizadas para compatibilidad robusta: `.triage-card-header, .triage-card-top`, `.triage-label, .triage-indicator`, `.triage-detail, .triage-fact`.
- Recompilación exitosa a `styles.css` mediante `@tailwindcss/cli 4.3.3` minificado.

---

## 5. Validación Automatizada

### 5.1 Suite End-to-End Playwright (`tests/e2e/catalog.spec.cjs`)
Se añadió la prueba automatizada obligatoria: `eliminates informational redundancy and enforces canonical single locations (UX-EXP-04)`.

Ejecutada sobre Chromium y Mobile (Pixel 5 emulado):
- **OP-005 (Oportunidad Real):**
  - Triaje rápido contiene exactamente 3 tarjetas.
  - Subtítulo verifica lectura de «3 señales clave».
  - Verificada la ausencia en triaje de tecnologías, modalidad, tipo, compensación y vigencia.
  - Modalidad presente una sola vez en cuadrícula (`No especificada`), ausente de header tags y triaje.
  - Ubicación presente una sola vez en cuadrícula (`Lima, Perú`), sin repeticiones de «Perú».
  - Compensación presente una sola vez en cuadrícula (`No publicado · No informado en la convocatoria pública`).
  - Contrato y plazo consolida régimen y permanencia (`Full-time; duración no especificada · Puesto regular...`).
  - Requisitos y Tecnologías estrictamente separados; requisitos no contiene `Tecnologías/señales:`.
  - Tecnologías declaradas renderizadas en su propia sección.
  - Sección `Continuidad y riesgos` ausente en el DOM (count = 0).
  - Tarjeta oficial no repite la fecha de verificación.
  - Canal oficial de postulación preservado y visible.
- **OP-002 (Demostrativa Remota):**
  - Cuadrícula muestra `Remoto` y `Remoto (Chile, Perú o Colombia)`.
  - Triaje con 3 tarjetas sin duplicar modalidad.
  - Sección `Continuidad y riesgos` ausente.
- **OP-001 (Demostrativa con Beneficios):**
  - Triaje con 3 tarjetas.
  - `Beneficios publicados` renderiza limpiamente sin duplicaciones.
  - Sección `Continuidad y riesgos` ausente.

**Resultado Playwright:** **14/14 tests PASSED** en 11.9s.

### 5.2 Suite Unittest Python (`test_*.py`)
- Ejecución completa: `193 tests passed` en 4.3s.
- `test_static_contract.py` superado: preservados los identificadores contractuales (`Entidad que difunde`, `Ficha informativa`, `Procedencia por dato`, etc.).

### 5.3 Contrato de Catálogo y Browser (`catalog_ui.test.cjs`)
- Verificaciones de rutas relativas, payload de catálogo y degradación en fallo: **100% PASSED**.

### 5.4 Integridad de Datos Canónicos (`validate_catalog.py` & `build_catalog.py`)
- `validate_catalog.py`: 6 fichas válidas.
- `build_catalog.py --check`: Snapshot `data/opportunities.json` coincide exactamente con `data/opportunities.seed.json`.

---

## 6. Estado de Gobernanza y Gate

1. **Integridad de Datos:** `data/opportunities.seed.json` y `data/opportunities.json` permanecen estrictamente inalterados.
2. **Metadatos y Evidencias:** Se conservan las 21 evidencias por campo (`fieldEvidence`), la decisión editorial y las listas de hosts permitidos.
3. **Dependencias:** Cero dependencias añadidas a `package.json` o scripts de ejecución.
4. **Estado formal del proyecto:**
   - **R0, R1, R2, R2-OSS:** `DONE`.
   - **R3-01:** `DONE`.
   - **R3-02 formal (human fieldwork):** `NOT_STARTED` / `PENDING_HUMAN`.
   - **R3-03:** `BLOCKED`.
   - **Iteraciones exploratorias UX (UX-EXP-01 a UX-EXP-04):** `DONE` (circunscritas al working tree local para evaluación personal y círculo reducido).
5. **Git Push / Merge / Deploy:** No ejecutados. Requieren autorización explícita del propietario.
