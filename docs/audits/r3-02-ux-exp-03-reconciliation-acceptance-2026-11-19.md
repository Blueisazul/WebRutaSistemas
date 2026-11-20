# AUDITORÍA DE RECONCILIACIÓN FINAL, ACEPTACIÓN TÉCNICA Y GATE DE SINCRONIZACIÓN — R3-02-UX-EXP-03

**Proyecto:** Ruta Sistemas
**Fecha:** 2026-11-19
**Fase:** R3 — Validación de Producto / Control de Calidad y Reconciliación de Estabilización
**Rama de trabajo:** `integration/r1-02c`
**Commit base (HEAD remoto):** `9d747c537039ecf6ea2a0f4cca68a44277c6ea2b` (`origin/integration/r1-02c`)
**Clasificación:** `[REFACTOR/FIX]` `[QA/VALIDACIÓN]` `[AUDITORÍA_TÉCNICA]` `[GATE_DE_ACEPTACIÓN]`
**Decisión del Gate:** **READY_FOR_OWNER_REVIEW** (Aprobado para revisión humana y autorización de sincronización por el propietario).

---

## 1. Estado Git Inicial y Final

### 1.1 Estado inicial verificado
- **Rama activa:** `integration/r1-02c`, apuntando al commit `9d747c5`.
- **Relación con remoto:** En paridad con `origin/integration/r1-02c` (sin commits locales por delante ni por detrás).
- **Working Tree inicial:** 7 archivos modificados acumulados tras las iteraciones exploratorias `UX-EXP-01` y `UX-EXP-02`, y 4 documentos no rastreados en `docs/`.

### 1.2 Estado final del working tree
- **Archivos modificados rastreados (7):**
  1. `app.js`: Enrutamiento canónico (`?id=...` y `#/oportunidad/:id`), triaje factual auditado semánticamente (clasificación de `1+ años` como `Por revisar`), separación explícita de hechos de la vacante respecto al perfil del postulante, fechas en formato civil Lima (`17/11/2026`), traducción de estados de comparación y retiro de decisión editorial/empleador en la interfaz pública.
  2. `canvas.js`: Dimensiones cacheadas en redimensionamiento, eliminación de reflows forzados en el bucle continuo, suspensión de `requestAnimationFrame` vía `IntersectionObserver` fuera del viewport, limpieza en `pagehide` y respeto a `prefers-reduced-motion`.
  3. `index.html`: División estructural limpia entre `<main id="catalog-view">` y `<main id="opportunity-view">`.
  4. `src/site.css`: Definición modular de estilos para el triaje factual, tarjeta destacada de fuente oficial, bloque colapsable de procedencia y regla responsive `@media (max-width: 680px)`.
  5. `styles.css`: Compilación local minificada mediante Tailwind CSS v4.3.3.
  6. `tests/e2e/catalog.spec.cjs`: 12 pruebas automatizadas Playwright (catálogo, filtros, detalle, triaje, compatibilidad hash, prevención de 404 en anclas locales y auditoría de anchos 1440px, 768px y 390px).
  7. `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Roadmap maestro actualizado documentando las iteraciones exploratorias sin alterar la gobernanza.
- **Archivos no rastreados generados (5):**
  - `docs/audits/r3-02-preview-readiness-2026-11-19.md`
  - `docs/audits/r3-02-ux-exploratory-iteration-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-02-acceptance-2026-11-19.md`
  - `docs/audits/r3-02-ux-exp-03-reconciliation-acceptance-2026-11-19.md` (este documento)
  - `docs/research/r3-02-informal-feedback-template.md`
- **Operaciones Git destructivas:** Cero. No se ejecutó commit, push, merge, reset ni checkout que alterara el historial.

---

## 2. Reconciliación entre UX-EXP-01, UX-EXP-02 y el Estado Real

| Componente / Tarea | Declarado en UX-EXP-01 | Auditado en UX-EXP-02 | Verificado Realmente en UX-EXP-03 |
|---|---|---|---|
| **Hero WebGL2 (`canvas.js`)** | Sin reflows; afirmación de "0% GPU/CPU". | Caching de geometría confirmado; eliminación de afirmación empírica no instrumental de 0% GPU. | Verificado en código: `cancelAnimationFrame` suspende efectivamente el bucle cuando `isHeroVisible === false`. Cero lecturas DOM en `updateFlowNodes()`. |
| **Tailwind CSS (`styles.css`)** | v4.3.3 compilado. | Correspondencia fuente-artefacto validada. | `npm run build:css` compila limpiamente en 117ms. Cero llamadas a CDNs externas. |
| **Enrutamiento y Detalle** | Query param `?id=...` y modal. | Deep linking y navegación directa validados. | Resuelto en `UX-EXP-03`: se corrigió el regex de hash routing que causaba falsos positivos 404 al hacer clic en anclas locales (`#inicio`, `#fuentes`). |
| **Triaje Rápido Factual** | 8 indicadores; `OP-005: Cumple`. | Detección de sesgo: OP-005 exige 1 año de experiencia previa. | Corregido: `OP-005` clasificado estrictamente como `Por revisar` (aviso amarillo factual). Desacoplamiento explícito entre vacante y perfil del postulante. |
| **Contenido Editorial** | Ocultamiento de decisión editorial y empleador. | Confirmación de preservación en Schema 2. | Verificado: `editorialDecision` y `renderEmployerAssessment` ausentes de la UI pública, pero 100% íntegros en seed y JSON publicado. |
| **Procedencia** | Tarjeta oficial + 21 campos colapsados. | Trazabilidad intacta. | Verificado en DOM: tarjeta destacada visible y 21 evidencias agrupadas en `<details>` cerrado por defecto. |
| **Heurísticas UX-B01 a UX-B05** | Resueltas. | Verificadas en Playwright y Node. | Verificado: estados en tarjeta, mensaje vacío adaptado, estados en español (`Abierta · Verificada · Activa`) y fechas civiles Lima (`17/11/2026`). |

---

## 3. Hallazgos Técnicos y UX Detectados y Resueltos en este Bloque

### 3.1 Defecto de colisión entre hash routing y anclas de página (`app.js`)
- **Problema:** La función `getOpportunityIdFromUrl()` utilizaba la expresión regular `/#\/?(?:oportunidad\/)?([A-Za-z0-9_-]+)/`. Debido a que el prefijo `oportunidad/` era opcional, cualquier enlace de ancla interna de la página principal (como `<a href="#inicio">`, `<a href="#fuentes">` o `<a href="#como-evaluamos">`) extraía `"inicio"` o `"fuentes"` como identificador de oportunidad. Al no existir en el catálogo, activaba erróneamente la pantalla de error 404 («Oportunidad no encontrada»), ocultando el catálogo.
- **Causa:** Expresión regular permisiva sin delimitador de anclaje estricto.
- **Corrección aplicada:** Se modificó la expresión a `^#\/?oportunidad\/([A-Za-z0-9_-]+)$`. Ahora únicamente los hashes que sigan explícitamente el patrón canónico `#/oportunidad/:id` o `#oportunidad/:id` se interpretan como solicitudes de detalle; las anclas convencionales de navegación dentro del documento son ignoradas por el enrutador de oportunidades.
- **Prueba de regresión:** Se añadieron aserciones específicas en Playwright (`tests/e2e/catalog.spec.cjs`) comprobando que `/#/oportunidad/OP-005` abre la vacante y que `/#inicio` mantiene el catálogo visible sin disparar la vista de error.

### 3.2 Precisión semántica del Triaje para OP-005
- **Confirmación:** La oportunidad real CookUnity (`OP-005`) exige en sus requisitos oficiales: *"1+ años de experiencia previa en áreas analíticas o cadena de suministro"*.
- **Semántica consolidada:**
  - `quickTriage(job)` detecta `1+ años` mediante `/\b(?:1|2)\+?\s*a[ñn]os?/i`.
  - Asigna el badge **`Por revisar`** (aviso amarillo) y el detalle factual: *`Nivel Junior: la convocatoria exige al menos 1 año de experiencia previa`*.
  - No afirma que el usuario califique ni lo califica como `No cumple`, protegiendo la neutralidad de la plataforma.

---

## 4. Matriz de Validación Integral

| Verificador / Suite | Comando Ejecutado | Resultado | Detalle de Ejecución |
|---|---|---|---|
| **Compilación CSS** | `npm run build:css` | **PASS (0)** | Tailwind CSS v4.3.3 minificado en 117ms. |
| **Sintaxis JavaScript (app)** | `node --check app.js` | **PASS (0)** | Cero errores de sintaxis en `app.js`. |
| **Sintaxis JavaScript (canvas)** | `node --check canvas.js` | **PASS (0)** | Cero errores de sintaxis en `canvas.js`. |
| **Contrato UI en Node.js (`vm`)** | `node tests/catalog_ui.test.cjs` | **PASS (0)** | Rutas relativas, filtrado por opt-ins y degradación fail-closed comprobados. |
| **Contrato Estático Frontend** | `python -m unittest tests/test_static_contract.py` | **PASS (0)** | 9/9 pruebas aprobadas (ausencia de CDN, estilos locales, scripts relativos). |
| **Suite Completa Python** | `python -m unittest discover -s tests -p "test_*.py"` | **PASS (0)** | 193/193 pruebas aprobadas en 2.70s (incluye dedup, ingesta, calidad y CLI). |
| **Validación de Calidad del Catálogo** | `python scripts/validate_catalog.py` | **PASS (0)** | Catálogo canónico y snapshot conforme con Schema 2 (6 registros). |
| **Chequeo de Integridad de Snapshot** | `python scripts/build_catalog.py --check` | **PASS (0)** | `opportunities.json` coincide exactamente con `opportunities.seed.json`. |
| **Suite End-to-End Playwright** | `npx playwright test` | **PASS (0)** | 12/12 pruebas aprobadas (6 Chromium desktop + 6 Mobile Pixel 5). |
| **Linter de Diff Git** | `git diff --check` | **PASS (0)** | Sin espacios en blanco residuales ni conflictos de formato. |

---

## 5. Integridad de Datos y Modelo Schema 2

Se verificó mediante inspección directa y scripts de validación:
- `data/opportunities.seed.json`: 100% inalterado (hash y estructura intactos).
- `data/opportunities.json`: 100% inalterado (hash y estructura intactos).
- `collector/sources.json`: 100% inalterado.
- **Campos internos de trazabilidad de OP-005:**
  - `editorialDecision`: Conservado intacto (`status: "approved"`, `reviewer: "Equipo Editorial / Propietario Ruta Sistemas"`, motivo de promoción R2-A-04).
  - `fieldEvidence`: 21 evidencias por campo preservadas con sus URLs oficiales y fechas de observación.
  - `allowedHosts`: Lista autorizada intacta (`careers.cookunity.com`, `job-boards.greenhouse.io`, `boards-api.greenhouse.io`).

---

## 6. Riesgos y Bloqueos Identificados

1. **Riesgo de desalineación si se confunde validación técnica con validación de producto:**
   - La presente auditoría certifica que el software funciona técnicamente, es accesible, rápido y respeta los contratos de datos.
   - **No sustituye** el trabajo de campo humano con estudiantes y egresados reales planificado en R3-02.
2. **Dependencias y conectividad:**
   - Riesgo nulo: La aplicación se ejecuta de forma 100% autónoma en bucle local (`127.0.0.1:4173`) sin dependencias de red externa.

---

## 7. Decisión del Gate de Sincronización

**Clasificación:** **`READY_FOR_OWNER_REVIEW`**

**Criterios cumplidos:**
- [x] Rama `integration/r1-02c` y cambios reales totalmente reconciliados.
- [x] Ejecución local limpia en puerto 4173 sin dependencias externas.
- [x] Enrutamiento por URL `?id=OP-005` y compatibilidad con hash `#/oportunidad/:id` operativos; anclas de página `#inicio` blindadas contra 404.
- [x] Triaje rápido factual auditado: no confunde requisitos con perfil de usuario y advierte la exigencia de 1 año en `OP-005`.
- [x] Información editorial interna protegida de la visualización pública pero intacta en Schema 2.
- [x] Rendimiento de Hero WebGL2 optimizado sin forced reflows y con pausa efectiva fuera de viewport.
- [x] Diseño adaptable verificado en 1440px, 768px y 390px sin scroll horizontal involuntario.
- [x] 193 pruebas Python y 12 pruebas Playwright aprobadas al 100%.

---

## 8. Siguiente Acción Recomendada

Se recomienda que el propietario del proyecto:
1. Inicie el servidor local mediante `python server.py`.
2. Realice la inspección visual y funcional en `http://127.0.0.1:4173/`.
3. Valide el diff local (`git diff`).
4. Autorice la creación del commit de consolidación de `R3-02-UX-EXP` y el posterior `git push` a `origin/integration/r1-02c`.
