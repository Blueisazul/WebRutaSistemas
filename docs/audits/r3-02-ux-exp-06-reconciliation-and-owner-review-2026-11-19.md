# AUDITORÍA TÉCNICA Y DE LIBERACIÓN: R3-02-UX-EXP-06
## Reconciliación Post-Implementación, Auditoría de UX-EXP-05 y Preparación de Revisión del Propietario

**Fecha de evaluación:** 19 de noviembre de 2026
**Proyecto:** Ruta Sistemas — WebRutaSistemas
**Rama objetivo:** `integration/r1-02c`
**Commit base en HEAD:** `9d747c537039ecf6ea2a0f4cca68a44277c6ea2b` (`origin/integration/r1-02c`)
**Tipo de intervención:** [QA/VALIDACIÓN] + [RELEASE-READINESS] Auditoría forense de cambios, verificación criptográfica, suite de pruebas y guía de revisión local
**Veredicto del Gate:** **`READY_FOR_OWNER_REVIEW`** (Listo para revisión local interactiva por el propietario y círculo reducido)
**Estado de gobernanza:** R3-02 formal continúa en `NOT_STARTED` / `PENDING_HUMAN`; R3-03 a R3-05 y R4 permanecen estrictamente `BLOCKED`.

---

## 1. Resumen Ejecutivo y Estado de Integración

Este bloque tuvo como misión auditar de forma independiente y forense el repositorio local para determinar si las modificaciones anunciadas en `R3-02-UX-EXP-05` (rediseño de la ficha de oportunidad, erradicación del triaje rápido, incorporación de cabecera de fuente oficial verificada, resumen con iconos Lucide, omisión estricta de datos no publicados y corrección de tokens en Tailwind CSS v4) estaban efectivamente presentes, integradas, operativas y verificables en el código.

### Hallazgos Principales:
1. **Presencia Efectiva:** Todos los cambios comprometidos en UX-EXP-05 están implementados en el árbol de trabajo local (`app.js`, `index.html`, `src/input.css`, `src/site.css`, `styles.css`, `tests/e2e/catalog.spec.cjs`).
2. **Reconciliación Git:** El commit base es `9d747c5`. Los informes previos de `Git Sync` y `Preview-01` corresponden a la sincronización de `9d747c5`. Todo el trabajo de UX-EXP-01 a UX-EXP-05 se preserva intacto en el working tree sin haberse realizado commit, push, merge ni deploy a producción.
3. **Invariabilidad Criptográfica de Schema 2:** Los archivos de datos canónicos (`data/opportunities.seed.json`, `data/opportunities.json`, `collector/sources.json`) tienen un diff nulo (`git diff HEAD` vacío) respecto al commit `9d747c5`. Cero bytes alterados en los esquemas.
4. **Validación Exhaustiva:** 193 pruebas unitarias e integrales en Python, 14 pruebas E2E en Playwright (Chromium y Mobile Pixel 5), 9 pruebas de contrato estático y scripts de catálogo pasan con 100% de éxito.
5. **Entorno Local Reproducible:** El servidor nativo sin dependencias externas (`python server.py`) se comprobó funcional en el puerto `4173`, sirviendo correctamente todos los activos estáticos y el endpoint de salud `/api/health`.

---

## 2. Fase A — Reconciliación Git Obligatoria

Se ejecutaron los comandos de inspección sobre el repositorio:

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
git log -8 --oneline --decorate
git status -sb
git diff --stat
git diff --cached --stat
git ls-files --others --exclude-standard
git rev-parse origin/integration/r1-02c
```

### Resultados de la Auditoría Git:
- **Rama local actual:** `integration/r1-02c`
- **HEAD actual:** `9d747c537039ecf6ea2a0f4cca68a44277c6ea2b`
- **HEAD remoto (`origin/integration/r1-02c`):** `9d747c537039ecf6ea2a0f4cca68a44277c6ea2b`
- **Paridad con remoto:** El commit local coincide con el remoto. No hay commits locales adelantados (`ahead 0`) ni atrasados (`behind 0`).
- **Estado de Staging (`git diff --cached`):** Vacío. 0 archivos staged.
- **Archivos modificados en Working Tree (`git status -s`):**
  - `M app.js`: Lógica de renderizado de detalle, iconos Lucide, fuente verificada, resumen y omisión estricta.
  - `M canvas.js`: Optimización de WebGL2 y observador de intersección (de UX-EXP-01).
  - `M docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Trazabilidad y roadmap actualizado.
  - `M index.html`: Estructura HTML del contenedor de vista independiente y ajustes de catálogo.
  - `M src/input.css`: Inyección de tokens `@theme` para compatibilidad de color en Tailwind v4.
  - `M src/site.css`: Reglas de estilo para vistas independientes y tablas comparativas.
  - `M styles.css`: CSS minificado compilado vía CLI de Tailwind v4.3.3 (65.311 bytes).
  - `M tests/e2e/catalog.spec.cjs`: 14 pruebas E2E cubriendo escenarios completos de catálogo y detalle.
- **Archivos no rastreados (`git ls-files --others --exclude-standard`):**
  - `docs/audits/r3-02-preview-readiness-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-02-acceptance-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-03-reconciliation-acceptance-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-04-information-consolidation-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-05-opportunity-detail-visual-redesign-2026-11-19.md`
  - `docs/audits/r3-02-ux-exploratory-iteration-2026-11-19.md`
  - `docs/research/r3-02-informal-feedback-template.md`

### Comparación con Informes Anteriores:
- **Git Sync (`R3-02-GIT-SYNC`):** Sincronizó formalmente hasta el commit `9d747c5`. Los archivos en el remoto `origin/integration/r1-02c` reflejan exactamente ese commit.
- **Preview-01 (`R3-02-PREVIEW-01`):** Documentó la preparación del entorno de pruebas para `9d747c5` antes de las iteraciones de experiencia.
- **UX-EXP-01 a UX-EXP-05:** Se desarrollaron como iteraciones locales consecutivas en el working tree sin hacer commit ni push, cumpliendo con la directiva de no tocar el historial remoto hasta contar con la aprobación del propietario.

---

## 3. Fase B — Auditoría Funcional de UX-EXP-05

Se verificó el cumplimiento de las decisiones de diseño mediante inspección estática del código y pruebas dinámicas:

### 3.1 Estructura Secuencial de la Ficha (`renderDetailContent` en `app.js`)
1. **Encabezado de oportunidad (`opportunity-header`):** Código de requisición, difusor, título del puesto (`dialog-title` / `opportunity-page-title`), empleador, sector y badges de estado/familia/nivel.
2. **Fuente oficial verificada (`official-source-hero`):** Ubicada en la parte superior. Tarjeta destacada con borde suave y gradiente; badge verificado (`✓ Fuente oficial verificada` con icono Lucide `check` o `Fuente de consulta` con `shield`); nombre del difusor y empleador contratante; fecha de verificación; botón «Ver publicación original ↗»; y botón «Ir a postulación ↗» (o `Postulación deshabilitada` si no cumple condiciones de postulación directa).
3. **Resumen (`summary-section`):** Cuadrícula visual con encabezado «Resumen» y tarjetas individuales dotadas de iconos SVG Lucide inlined.
4. **Tecnologías y herramientas declaradas (`skills-section`):** Situada inmediatamente debajo de Resumen, encabezada por el icono Lucide `code` y mostrando los conocimientos técnicos solicitados como tags visuales (`bg-emerald-50 text-emerald-900 border-emerald-200/80`).
5. **Qué se verificó (`verification-section`):** Caja informativa de estado (`evidence-box`) y acordeón colapsable (`details.evidence-collapsible`) con los 21 campos de procedencia por dato de OP-005.
6. **Contenido complementario con valor:** Tareas principales («Qué harías»), «Requisitos del puesto» (conservando *«1+ años de experiencia previa...»*), «Qué experiencia podrías llevar al siguiente paso» y «Beneficios publicados».
7. **Pie de detalle y navegación:** Aviso ético de prototipo (*«No guardamos tu CV ni enviamos postulaciones desde este prototipo»*) y botones de retorno al catálogo.

### 3.2 Verificación de Criterios Negativos y Omisión:
- **Triaje Rápido:** Completamente erradicado. No existe ninguna invocación a `renderQuickTriage` ni se renderizan `.triage-section`, `.triage-grid` ni `.triage-card`.
- **Omisión estricta:** En `OP-005`, las tarjetas de `Modalidad`, `Compensación` y `Fecha límite` no se renderizan al no estar declaradas en la fuente pública.
- **Depuración de especulación:** Se eliminó la frase *«sujeto a desempeño y evaluación del empleador»* mediante la función `cleanContractDuration(job)`.
- **Navegación robusta:** Comprobada tanto para modal como para vista independiente (`/?id=OP-005`), rutas hash (`/#/oportunidad/OP-005`), anclas locales (`/#inicio` no dispara 404) y escenarios de ID inexistente (`/?id=OP-999` muestra pantalla amigable de no encontrado con retorno al catálogo).

---

## 4. Fase C — Integración Real de Tailwind CSS v4.3.3

### 4.1 Cadena de Compilación
- **Dependencias en `package.json`:**
  - `@tailwindcss/cli`: `4.3.3`
  - `tailwindcss`: `4.3.3`
  - Total dependencias añadidas en runtime: **0**.
- **Entrada CSS (`src/input.css`):**
  - `@import "tailwindcss" source("../");`
  - `@import "./site.css";`
  - `@source "../index.html";`
  - `@source "../app.js";`
  - `@theme { ... }` con variables `--color-ice-blue`, `--color-crystal-blue`, `--color-arctic-blue`, `--color-brand-black`, `--color-brand-dark`, `--color-brand-muted`, `--color-surface-raised`, `--color-border-muted`, así como sus variantes en camelCase.
- **Salida Compilada (`styles.css`):**
  - Generada en 123 ms mediante `npm run build:css`.
  - Tamaño: 65.311 bytes minificados.
  - Contiene las definiciones `:root { --color-brandBlack: #202120; ... }` y clases generadas como `.text-brandBlack`, `.bg-emerald-50`, `.grid-cols-4`, etc.
  - Cargada en `index.html` mediante `<link rel="stylesheet" href="styles.css" />`.
  - Cero peticiones a CDN o librerías externas en runtime.

---

## 5. Fase D — Caso de Regresión OP-005 (CookUnity — Supply Chain Analyst)

Se auditó minuciosamente la oportunidad activa real `OP-005`:

| Atributo Requerido | Valor Esperado | Estado en Implementación |
|---|---|---|
| **ID** | `OP-005` | Presente y verificado |
| **Puesto** | `Supply Chain Analyst` | Presente y verificado |
| **Empleador** | `CookUnity` | Presente y verificado |
| **Nivel** | `Junior` | Presente en tags y metadatos |
| **Requisito de Experiencia** | `1+ años de experiencia previa...` | Presente en «Requisitos del puesto» |
| **Ubicación y Elegibilidad** | `Lima, Perú` / `Perú` | Presente en tarjeta de Resumen |
| **Fuente Oficial** | CookUnity / Greenhouse | Enlace HTTPS seguro verificado |
| **Canal de Postulación** | Greenhouse ATS | Botón directo habilitado (`Ir a postulación ↗`) |
| **Desglose de Evidencias** | 21 campos registrados | 21 campos presentes en acordeón colapsable |
| **Modalidad no publicada** | Omitida visualmente | No se muestra tarjeta de modalidad |
| **Compensación no publicada** | Omitida visualmente | No se muestra tarjeta de compensación |
| **Fecha límite no publicada** | Omitida visualmente | No se muestra tarjeta de fecha límite |
| **Frase especulativa** | *«sujeto a desempeño...»* eliminada | Totalmente ausente |

---

## 6. Fase E — Integridad Criptográfica y Resultados de Pruebas

### 6.1 Hashes Criptográficos SHA-256 de Archivos Canónicos
Se calcularon los hashes de los archivos protegidos:

| Archivo Canónico | Hash SHA-256 Actual | Estado vs HEAD (`9d747c5`) |
|---|---|---|
| `data/opportunities.seed.json` | `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` | **Idéntico (diff nulo)** |
| `data/opportunities.json` | `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` | **Idéntico (diff nulo)** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **Idéntico (diff nulo)** |

### 6.2 Resumen de Pruebas Ejecutadas

```
====================================================================================================
PRUEBA / COMANDO DE AUDITORÍA                                   RESULTADO   DETALLE TÉCNICO
====================================================================================================
1. Compilación CSS (npm run build:css)                          APROBADO    tailwindcss v4.3.3 en 123ms
2. Sintaxis JS (node --check app.js canvas.js)                  APROBADO    0 errores sintácticos
3. Catálogo UI Unitario (node tests/catalog_ui.test.cjs)        APROBADO    2/2 suites aprobadas
4. Contrato Estático Python (tests/test_static_contract.py)     APROBADO    9/9 tests pasaron (0.014s)
5. Validación de Catálogo (python scripts/validate_catalog.py)  APROBADO    6 fichas válidas (Lima)
6. Verificación de Build (python scripts/build_catalog.py)      APROBADO    Snapshot canónico coincide
7. Suite Completa Python (tests/test_*.py)                      APROBADO    193/193 tests pasaron (2.63s)
8. Suite E2E Playwright (tests/e2e/catalog.spec.cjs)            APROBADO    14/14 tests pasaron (12.6s)
   - Desktop Chromium (1440x900)                                APROBADO    0 overflow horizontal
   - Tablet Viewport (768x1024)                                 APROBADO    0 overflow horizontal
   - Mobile Pixel 5 (390x844)                                   APROBADO    0 overflow horizontal
9. Integridad Git Diff (git diff --check)                       APROBADO    0 conflictos / whitespace OK
====================================================================================================
```

---

## 7. Fase F — Preparación y Guía de Revisión Local para el Propietario

El servidor loopback integrado `server.py` fue verificado con peticiones HTTP locales automáticas:
- `http://127.0.0.1:4173/` $\rightarrow$ `200 OK` (`text/html`)
- `http://127.0.0.1:4173/styles.css` $\rightarrow$ `200 OK` (`text/css`)
- `http://127.0.0.1:4173/app.js` $\rightarrow$ `200 OK` (`text/javascript`)
- `http://127.0.0.1:4173/canvas.js` $\rightarrow$ `200 OK` (`text/javascript`)
- `http://127.0.0.1:4173/data/opportunities.json` $\rightarrow$ `200 OK` (`application/json`)
- `http://127.0.0.1:4173/api/health` $\rightarrow$ `200 OK` (`application/json`)

### Guía de Revisión Local para el Propietario

#### Paso 1: Iniciar el servidor local
Abre una terminal PowerShell o Bash en la raíz del repositorio y ejecuta:
```bash
python server.py
```
*El servidor confirmará en consola:*
`Ruta Sistemas está disponible solo en esta computadora: http://127.0.0.1:4173`

#### Paso 2: Abrir el navegador
- **Vista general del catálogo:** Abre en tu navegador favorito:
  `http://127.0.0.1:4173/`
- **Acceso directo a la oportunidad real OP-005:**
  `http://127.0.0.1:4173/?id=OP-005`
  *(O alternativamente vía hash: `http://127.0.0.1:4173/#/oportunidad/OP-005`)*

#### Paso 3: Qué elementos verificar en la ficha OP-005
1. **Cabecera destacada:** Comprueba la sección superior verde con el badge `✓ Fuente oficial verificada`, nombre de `CookUnity`, fecha de consulta y el botón amarillo `Ir a postulación ↗`.
2. **Resumen visual:** Revisa las 5 tarjetas con iconos vectoriales Lucide: difusor, ubicación Lima, contrato full-time, fecha de publicación y última verificación. Observa que **no aparecen** tarjetas vacías ni textos de "No informado" para modalidad, salario ni fecha límite.
3. **Tecnologías declaradas:** Observa las etiquetas destacadas inmediatamente abajo (`SQL`, `Analítica de operaciones`, `Google Sheets`, `ERP/MRP`).
4. **Qué se verificó:** Despliega el acordeón interactivo «Procedencia por dato (21 campos registrados)» para comprobar los enlaces a Greenhouse.
5. **Requisitos:** Confirma que se mantiene el requisito de nivel Junior y `1+ años de experiencia previa`.
6. **Responsividad:** Prueba redimensionar la ventana o inspeccionar en modo móvil (390 px) para verificar que las tarjetas se adaptan limpiamente a 1 columna sin desbordamiento horizontal.

#### Paso 4: Detener el servidor
En la terminal donde iniciaste `python server.py`, presiona:
```
Ctrl + C
```
*El servidor finalizará limpiamente mostrando `Servidor local detenido.`*

---

## 8. Defectos Encontrados y Correcciones Efectuadas

Durante la auditoría del bloque previo UX-EXP-05 se detectó una discrepancia de texto en la etiqueta de postulación deshabilitada:
- **Defecto:** `app.js` renderizaba `<span class="apply-disabled">Postulación no habilitada</span>`, mientras que las aserciones de regresión esperaban `Postulación deshabilitada`.
- **Corrección:** Se ajustó la cadena en `app.js` a `Postulación deshabilitada`.
- **Resultado:** Las 14 pruebas de Playwright pasaron inmediatamente en 12.6s sin ninguna falla.

---

## 9. Estado del Roadmap y Gobernanza

- **Iteraciones Exploratorias:**
  - `UX-EXP-01` a `UX-EXP-06` documentadas secuencialmente como iteraciones locales de preparación y aceptación previa para el propietario y círculo reducido.
- **R3-02 Formal:** Permanece en estado **`NOT_STARTED` / `PENDING_HUMAN`**. La preparación operativa está completada, pero la ejecución empírica requiere trabajo de campo real con moderadores y participantes humanos (P01 a P08).
- **R3-03 a R3-05 y R4:** Permanecen formalmente **`BLOCKED`**.
- **Acciones Git:** El repositorio permanece exactamente en la rama `integration/r1-02c` sin commits, push, merge ni despliegues en producción.
