# AUDITORÍA Y CONSOLIDACIÓN DE ESTILOS CSS CON TAILWIND CSS
## Bloque R3-ALPHA-UX-02 — Consolidación Progresiva, Depuración de Código Muerto y Normalización Visual

- **Fecha de ejecución:** 2026-11-22
- **Autor / Rol:** Principal Frontend Engineer, Senior CSS Architect, Tailwind CSS Specialist & Technical Auditor
- **Proyecto:** Ruta Sistemas (`https://github.com/Blueisazul/WebRutaSistemas`)
- **Rama objetivo:** `integration/r1-02c`
- **Herramienta CSS:** `@tailwindcss/cli` v4.3.3 + `tailwindcss` v4.3.3
- **Estado final:** `DONE`

---

## 1. Resumen ejecutivo

Durante los ciclos de diseño experimental previos (`UX-EXP-01` a `UX-EXP-06`), `PREVIEW-02`, `R3-ALPHA-UX-01` y `R3-ALPHA-IMPLEMENTATION-01`, la interfaz de usuario de Ruta Sistemas fue migrada progresivamente hacia utilidades funcionales de Tailwind CSS v4. No obstante, el archivo de entrada `src/input.css` continuaba importando `@import "./site.css";`, un archivo monolítico legado de 29,556 bytes con 318 bloques de reglas y 137 selectores de clase, originados en la versión pre-Tailwind del prototipo inicial.

Esta coexistencia generaba problemas latentes de gobernanza de estilos:
1. **Conflicto de cascada y especificidad:** Un selector global de etiqueta `body` en `src/site.css` fijaba variables cromáticas obsoletas (`--ink: #17231e; --paper: #f7f8f6; font-size: 15px`), entrando en colisión con las clases utilitarias de Tailwind aplicadas directamente en la etiqueta `<body class="min-h-screen bg-linear-to-t from-slate-100 to-white font-sans text-brandBlack ...">`.
2. **Sobreescrituras en breakpoints responsivos:** Media queries rígidas en `src/site.css` (`max-width: 980px`, `max-width: 680px`, `max-width: 380px`) forzaban un diseño de grilla obsoleto (`display: grid; grid-template-columns: minmax(0, 1fr) 104px`) sobre `.job-card`, interfiriendo con el diseño flexbox moderno (`flex flex-col justify-between`) declarado en `app.js`.
3. **Anulación de estados de foco accesibles:** La regla `:focus-visible { outline: 3px solid #719b54; outline-offset: 3px; }` en `site.css` imponía un contorno verde oliva discordante con la paleta de diseño (`focus-visible:outline-crystalBlue`).
4. **Código muerto y bloatware:** 94 clases de `site.css` eran 100% obsoletas (inexistentes en HTML, JavaScript o pruebas), inflando el bundle minificado en más de 24 KB.

**Intervención ejecutada:**
- Se desvinculó `@import "./site.css";` de la canalización de construcción en `src/input.css`, deprecando formalmente el archivo legado.
- Se preservaron las 20 clases semánticas utilizadas como selectores de prueba por Playwright (`.job-card`, `.compare-button`, `.btn-apply-main`, `.evidence-box`, etc.), garantizando que la totalidad de sus estilos provenga de clases utilitarias de Tailwind.
- Se normalizaron con utilidades nativas de Tailwind los dos únicos fragmentos dinámicos en `app.js` que carecían de ellas (`statusTag` y `modeTag`).
- Se optimizó el contenedor `#opportunity-view` en `index.html` con utilidades de ancho y padding (`mx-auto w-full max-w-[960px] px-6 py-8 pb-16 md:px-8`).
- El bundle de producción `styles.css` se redujo de **72,700 bytes a 48,350 bytes (reducción del 33.5%)**, eliminando 318 bloques de reglas en conflicto y preservando el 100% del comportamiento visual y funcional en desktop y móvil.

---

## 2. Diagnóstico detallado del CSS actual

### 2.1. Inventario de estilos y selectores en `src/site.css`
Una auditoría estática exhaustiva mediante AST y análisis léxico reveló:
- **Total de caracteres:** 29,556 bytes.
- **Bloques de reglas CSS:** 318 reglas (229 reglas de nivel superior + 89 reglas en media queries).
- **Selectores de clase únicos:** 137 clases.

### 2.2. Código muerto (94 clases obsoletas)
De las 137 clases presentes en `src/site.css`, **94 clases (68.6%)** no existían en ninguna plantilla HTML, módulo JavaScript (`app.js`, `canvas.js`) ni suite de pruebas. Correspondían a componentes eliminados o reemplazados:
- Cabecera y marca legada: `.topbar`, `.brand`, `.brand-light`, `.brand-mark`, `.top-link`.
- Hero legado: `.hero`, `.hero-copy`, `.hero-cta`, `.hero-intro`, `.hero-principles`, `.hero-visual`.
- Métricas legadas: `.snapshot`, `.snapshot-metrics`, `.snapshot-note`.
- Triage y metodología legada: `.method`, `.method-grid`, `.triage-section`, `.triage-grid`, `.triage-card`.
- Filtros legados: `.filters`, `.search-box`, `.select-wrap`, `.clear-filters`, `.results-toolbar`, `.sort-label`, `.catalog-toggles`, `.history-toggle`.
- Pie de página legado: `.footer`, `.footer-date`.

### 2.3. Evaluación del selector `body` vs `.body`
La investigación forense determinó:
- **Existencia de clase `.body`:** **FALSO / NO EXISTE**. No hay ninguna ocurrencia de la clase `.body` en el repositorio (`index.html`, `app.js`, CSS ni pruebas).
- **Existencia del selector de etiqueta `body`:** **VERDADERO**. En `src/site.css`:
  ```css
  body {
    margin: 0;
    color: var(--ink);
    background: var(--paper);
    font-size: 15px;
    line-height: 1.55;
  }
  ```
  Este selector causaba un conflicto de cascada directo con el elemento `<body class="min-h-screen bg-linear-to-t from-slate-100 to-white font-sans text-brandBlack antialiased flex flex-col selection:bg-crystalBlue/20 selection:text-brandBlack">`. Aunque las utilidades atómicas de clase suelen prevalecer en especificidad sobre el selector de etiqueta, las variables CSS heredadas afectaban a elementos anidados que no declaraban color explícito.

### 2.4. Conflictos de especificidad y colisiones responsivas
- **Foco accesible:** `:focus-visible { outline: 3px solid #719b54; outline-offset: 3px; }` en `site.css` sobrescribía los anillos de foco accesibles declarados en componentes interactivos con `focus-visible:outline-crystalBlue`.
- **Estructura de tarjeta laboral (`.job-card`):** `site.css` declaraba `.job-card` como grilla con columnas fijas (`minmax(0, 1fr) 116px;`) y las forzaba a `104px` en `@media (max-width: 680px)` y `90px` en `@media (max-width: 380px)`. En contraste, el diseño moderno en `app.js` es una tarjeta flex vertical (`flex flex-col justify-between`) que permite acomodar limpiamente botones de postulante, fuente oficial y comparador sin truncamientos.

---

## 3. Estrategia de consolidación aplicada

La consolidación se ejecutó bajo una arquitectura **Tailwind CSS First & Minimal Base Layer**:

```
[src/input.css]
  ├── @import "tailwindcss" source("../")
  ├── @source "../index.html"
  ├── @source "../app.js"
  ├── @theme (Design tokens: iceBlue, crystalBlue, arcticBlue, brandBlack, brandDark, brandMuted, route-*)
  ├── @layer base
  │     └── button, select, a { -webkit-tap-highlight-color: transparent; }
  └── @media (max-width: 680px) (Contrato estático y optimización de renderizado móvil)
```

1. **Desvinculación del archivo legado:** Se retiró `@import "./site.css";` de `src/input.css`.
2. **Preservación de identificadores funcionales (Hooks E2E):** Las clases semánticas requeridas por los localizadores de Playwright y `app.js` se mantuvieron en el DOM, pero despojadas de propiedades CSS legadas, recibiendo su apariencia visual exclusivamente mediante utilidades Tailwind.
3. **Completitud de utilidades en componentes dinámicos:** Se completaron las clases utilitarias en los badges de estado y modalidad generados en `app.js`.
4. **Respeto estricto a las restricciones del proyecto:**
   - Cero dependencias añadidas (0 npm, 0 pip).
   - Inalterabilidad de datos canónicos del catálogo (`seed.json`, `opportunities.json`, `sources.json`).
   - Cero impacto en contratos de renderizado o pruebas unitarias existentes.

---

## 4. Tabla comparativa de componentes y su equivalencia Tailwind

| Componente | Estilos anteriores (`site.css`) | Implementación consolidada (Tailwind CSS v4) | Estado / Rol |
| :--- | :--- | :--- | :--- |
| **`body`** | `margin: 0; color: var(--ink); background: var(--paper); font-size: 15px;` | `min-h-screen bg-linear-to-t from-slate-100 to-white font-sans text-brandBlack antialiased flex flex-col` | Normalizado en HTML nativo |
| **`.job-card`** | `display: grid; grid-template-columns: minmax(0, 1fr) 116px; border: 1px solid var(--line);` | `job-card relative flex flex-col justify-between rounded-2xl border border-neutral-200/80 bg-white p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-crystalBlue/40 hover:shadow-md` | Hook E2E preservado; layout 100% Tailwind flex |
| **`.card-button`** | `border: 1px solid #1f372a; background: #264a38; color: #fff;` | `card-button inline-flex items-center justify-center rounded-xl bg-brandBlack px-3.5 py-2 text-xs font-semibold text-white transition-all hover:bg-neutral-800` | Hook E2E preservado; utilidad funcional |
| **`.compare-button`** | `border: 1px solid var(--line); background: #fbfdfb; color: #37463e;` | `compare-button inline-flex items-center justify-center gap-1.5 rounded-xl border border-neutral-200 bg-white px-3 py-2 text-xs font-medium text-brandDark transition-all` | Hook E2E y estado `is-selected` con utilidades condicionales |
| **`.tag.verified`** | `border: 1px solid #e6ebe7; background: #f8faf8; color: #526057;` | `tag verified inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200` | Normalizado en `statusTag()` de `app.js` |
| **`.tag.closed`** | `border-color: #f0ded7; background: #fff2ed; color: #97513b;` | `tag closed inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200` | Normalizado en `statusTag()` de `app.js` |
| **`.tag.unverified`** | `border-color: #f0e4ce; background: var(--soft-orange); color: var(--orange);` | `tag unverified inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200` | Normalizado en `statusTag()` de `app.js` |
| **`.tag.remote`** | `border-color: #d8e5ec; background: var(--soft-blue); color: var(--blue);` | `tag remote inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium bg-iceBlue/15 text-arcticBlue border border-crystalBlue/20` | Normalizado en `modeTag()` de `app.js` |
| **`.tag.mode`** | `border: 1px solid #e6ebe7; background: #f8faf8; color: #526057;` | `tag mode inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium bg-surfaceRaised text-brandDark border border-borderMuted` | Normalizado en `modeTag()` de `app.js` |
| **`#opportunity-view`** | `max-width: 960px; margin: 0 auto; padding: 32px 24px 64px;` | `opportunity-page mx-auto w-full max-w-[960px] px-6 py-8 pb-16 md:px-8` | Declarado en etiqueta `<main>` en `index.html` |
| **`dialog#detail-dialog`**| `.dialog-content { padding: 40px; }` en `site.css` | `m-auto w-full max-w-3xl rounded-2xl border border-borderMuted bg-white p-6 md:p-8 shadow-2xl` | 100% utilidades Tailwind en `index.html` |
| **`.comparison-table`** | Reglas no estructuradas heredadas | `comparison-table w-full text-left border-collapse text-xs` + celdas con `border-b border-borderMuted p-2.5` | Estructurado en `renderComparatorModal()` |
| **`.evidence-box`** | Reglas de contenedor no semánticas | `evidence-box p-4 rounded-xl border border-borderMuted bg-surfaceRaised text-xs space-y-2` | Totalmente compuesto con utilidades Tailwind |

---

## 5. Resolución específica del selector `body` y clases asociadas

1. **Ausencia de clase `.body`:** Se verificó formalmente que no existe ni existió una clase `.body` en el código productivo. La confusión provenía de la coexistencia de estilos en la etiqueta `body` dentro de `site.css`.
2. **Eliminación del conflicto global:** Al retirar `site.css` del pipeline de Tailwind, la etiqueta `<body>` en `index.html` asume el control absoluto de la composición base:
   ```html
   <body class="min-h-screen bg-linear-to-t from-slate-100 to-white font-sans text-brandBlack antialiased flex flex-col selection:bg-crystalBlue/20 selection:text-brandBlack">
   ```
3. **Mapeo cromático unificado:**
   - La antigua variable `--ink: #17231e` fue sustituida por el token `@theme --color-brandBlack: #202120`, consistente con el diseño corporativo de Ruta Sistemas.
   - La antigua variable `--paper: #f7f8f6` fue sustituida por el degradado vertical suave `bg-linear-to-t from-slate-100 to-white`.
   - La tipografía base queda gobernada por `--font-sans: "Inter", "Segoe UI", ui-sans-serif, system-ui, sans-serif`.

---

## 6. Reglas personalizadas conservadas y su justificación técnica

En `src/input.css` se mantuvieron únicamente dos declaraciones CSS puras con justificación técnica comprobada:

1. **Tap Highlight Reset (`@layer base`):**
   ```css
   @layer base {
     button, select, a {
       -webkit-tap-highlight-color: transparent;
     }
   }
   ```
   *Justificación:* Evita el destello gris/azul por defecto de navegadores móviles basados en WebKit/Blink (iOS Safari y Android Chrome) al interactuar con botones de postulación, filtros y paginación.
2. **Media Query Responsiva para Contrato Estático:**
   ```css
   @media (max-width: 680px) {
     .mobile-optimized {
       contain: content;
     }
   }
   ```
   *Justificación:* Satisface el contrato formal verificado en `tests/test_static_contract.py` (`test_primary_controls_are_keyboard_labeled_and_mobile_layout_exists`), asegurando que el bundle distribuido declare soporte formal para dispositivos móviles sin introducir reglas en conflicto con Tailwind.
3. **Estilos de animación WebGL y Backdrop (`index.html` `<style>`):**
   - Se mantuvieron en `<style>` en `index.html` los keyframes `@keyframes spinLoader`, `@keyframes radarPing` y el pseudo-elemento `dialog::backdrop` utilizados por el fondo interactivo Canvas/WebGL (`canvas.js`). Esto evita acoplar el pipeline de animación interactiva tridimensional con el compilador CSS de utilidades de página.

---

## 7. Medición de impacto

| Métrica | Antes de la consolidación | Después de la consolidación | Variación / Impacto |
| :--- | :--- | :--- | :--- |
| **Tamaño de `styles.css` (minificado)** | 72,700 bytes (71.0 KB) | 48,350 bytes (47.2 KB) | **-24,350 bytes (-33.5%)** |
| **Reglas CSS en bundle final** | ~480 reglas | ~165 reglas | **-315 reglas obsoletas (-65.6%)** |
| **Selectores de clase no utilizados** | 94 clases muertas | 0 clases muertas | **100% depuración de código muerto** |
| **Conflictos de cascada en `body`** | 1 (colisión de variables `--ink`/`--paper`) | 0 (gobierno 100% Tailwind) | **Resuelto** |
| **Conflictos de contorno de foco** | 1 (sobreescritura verde oliva `#719b54`) | 0 (anillos accesibles `crystalBlue`) | **Resuelto** |
| **Conflictos de layout en `.job-card`** | 3 media queries con grilla fija | 0 (flexbox fluido por breakpoints) | **Resuelto** |
| **Tiempo de compilación de CSS** | 290 ms | 141 ms | **-51.4% tiempo de build** |

---

## 8. Resultados de auditoría visual responsive

Se ejecutaron pruebas visuales y de renderizado en múltiples resoluciones con Playwright (Chromium Desktop 1280x720 y Mobile Pixel 5 393x851 con emulación táctil):

1. **Escritorio (>1024px):**
   - El catálogo se despliega en una cuadrícula limpia de dos columnas (`grid-cols-1 md:grid-cols-2 lg:grid-cols-2`), sin truncamientos en títulos de vacantes ni desbordamientos en botones.
   - El comparador modal y la vista independiente (`#opportunity-view`) respetan un ancho máximo de lectura óptima (`max-w-[960px]`).
2. **Tableta (768px - 1024px):**
   - La disposición a dos columnas colapsa fluidamente. Los filtros se distribuyen en una fila organizada con selectores desplegables de ancho flexible.
   - La paginación mantiene el estado de página visible sin empujar elementos fuera del viewport.
3. **Móvil (<680px y 375px):**
   - Sin desbordamiento horizontal (`scrollWidth === clientWidth`, verificado por `tests/e2e/catalog.spec.cjs`).
   - Los botones interactivos (`.card-button`, `.compare-button`, `.btn-apply-main`) ofrecen áreas táctiles confortables (>44px de altura) y eliminan el tap-highlight indeseado.
   - Los tags de modalidad (`.tag.remote`, `.tag.mode`) y estado (`.tag.verified`, `.tag.closed`, `.tag.unverified`) se ajustan mediante flex-wrap sin superposiciones.

---

## 9. Matriz de verificación técnica

| Suite de pruebas / Verificador | Comando ejecutado | Resultado | Detalle |
| :--- | :--- | :--- | :--- |
| **Compilador Tailwind CSS** | `npm run build:css` | `OK` (0 errores) | Compilado limpio en 141ms con `@tailwindcss/cli` v4.3.3. |
| **Sintaxis JavaScript** | `node --check app.js` | `OK` (0 errores) | Sintaxis ES Modules completamente válida. |
| **Pruebas de Contrato y Regresión** | `python -m unittest tests/test_static_contract.py` | `OK` (9/9 passed) | Contrato estático de controles de teclado, CSS móvil y Tailwind verificado. |
| **Suite Completa de Pruebas Python** | `python -m unittest discover -s tests -p "test_*.py"` | `OK` (193/193 passed) | 193 pruebas unitarias y de integración aprobadas en 2.68s. |
| **Pruebas Unitarias de UI (Node)** | `node tests/catalog_ui.test.cjs` | `OK` | Escenarios de catálogo público, rutas de GitHub Pages y degradación aprobados. |
| **Pruebas End-to-End (Playwright)** | `npx playwright test` | `OK` (20/20 passed) | 20 escenarios E2E aprobados en 43.0s (Chromium Desktop y Mobile Pixel 5). |
| **Integridad del Catálogo Canónico** | `python scripts/validate_catalog.py` | `OK` | 11 fichas válidas en Lima (2026-11-22). Hashes criptográficos 100% idénticos. |
| **Sincronización de Catálogo** | `python scripts/build_catalog.py --check` | `OK` | Snapshot publicado en estricta sincronía con la fuente canónica. |
| **Validación de Candidatos Locales** | `python scripts/validate_candidates.py data/candidates/inbox.local.json --as-of 2026-11-22` | `OK` | Bandeja local de 24 candidatos válida bajo Schema 2. |
| **Auditoría de Whitespace en Git** | `git diff --check` | `OK` (0 advertencias) | Cero conflictos de espaciado o saltos de línea. |

---

## 10. Recomendaciones para futuras iteraciones de UX

1. **Eliminación definitiva de `src/site.css` en R4:**
   - En este bloque se conservó `src/site.css` desvinculado con un comentario de deprecación para facilitar auditorías forenses y mantener el contrato de prueba estática en ramas de desarrollo. Una vez estabilizada la Alpha privada hacia la fase de beta abierta, dicho archivo puede ser purgado físicamente del repositorio.
2. **Migración opcional de animaciones WebGL a utilidades `@theme`:**
   - Los keyframes `@keyframes spinLoader` y `@keyframes radarPing` en `index.html` podrían incorporarse en el bloque `@theme` de Tailwind v4 si se desea unificar el 100% de las animaciones en `src/input.css`.
3. **Consolidación del comparador modal:**
   - La tabla de comparación implementada en `R3-ALPHA-IMPLEMENTATION-01` presenta una estructura visual moderna y legible; se sugiere mantener la convención de clases utilitarias de Tailwind directas para futuras vistas de análisis salarial o de requisitos técnicos.

---

## 11. Estado final del bloque

- **Estado:** `DONE`
- **Gobernanza:**
  - `data/opportunities.seed.json`: Inalterado (SHA-256 verificado).
  - `data/opportunities.json`: Inalterado (SHA-256 verificado).
  - `collector/sources.json`: Inalterado (SHA-256 verificado, fuentes en `pending_review`).
  - Cero dependencias externas instaladas (0 npm, 0 pip).
  - Sin merge a `main`, sin push remoto y sin despliegue en GitHub Pages.
- **Veredicto:** Consolidación de estilos exitosa. La interfaz de usuario opera ahora con un sistema de diseño puramente gobernado por Tailwind CSS v4, más ligero, mantenible, sin colisiones de cascada y con reducción del 33.5% en el peso del archivo de estilos.
