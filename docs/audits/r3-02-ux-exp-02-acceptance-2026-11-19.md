# AUDITORÍA DE ACEPTACIÓN, VALIDACIÓN LOCAL Y PREPARACIÓN PARA SINCRONIZACIÓN — R3-02-UX-EXP-02

**Proyecto:** Ruta Sistemas
**Fecha:** 2026-11-19
**Fase:** R3 — Validación de Producto / Ciclo de Aceptación y Estabilización Técnica
**Rama de trabajo:** `integration/r1-02c`
**Commit base (HEAD remoto):** `9d747c5` (`origin/integration/r1-02c`)
**Clasificación:** `[REFACTOR/FIX]` `[QA/VALIDACIÓN]` `[AUDITORÍA_TÉCNICA]` `[PREPARACIÓN_DE_RELEASE]`
**Veredicto de aceptación:** **DONE** (Listo para revisión humana y sincronización por el propietario; R3-02 formal permanece `NOT_STARTED` / `PENDING_HUMAN`, R3-03 permanece `BLOCKED`).

---

## 1. Estado Git Inicial y Reconciliación con UX-EXP-01

### 1.1 Estado de partida
- **Rama:** `integration/r1-02c`, sincronizada con `origin/integration/r1-02c` en el commit `9d747c5`.
- **Working Tree:** Contenía las modificaciones introducidas durante la iteración exploratoria `R3-02-UX-EXP-01`, sin commits ni pushes intermedios, preservando intacta la política de no modificar el historial remoto sin autorización explícita.
- **Reconciliación documental:** La referencia a «15 archivos modificados, un `canvas.js` no rastreado y cuatro documentos nuevos» corresponde al inventario histórico de R0 (2026-11-12, sección 4). En el estado actual de `integration/r1-02c`, el diff activo consta de 7 archivos modificados y 3 documentos nuevos no rastreados (más la presente auditoría de aceptación).

### 1.2 Inventario de archivos del bloque

| Archivo | Categoría | Estado Git | Propósito / Cambio verificado |
|---|---|---|---|
| `app.js` | Frontend | Modificado | Triaje factual auditado semánticamente, enrutamiento `?id=...`, detalle independiente, retiro de decisión editorial/empleador, fechas Lima y traducción de estados. |
| `canvas.js` | Frontend / WebGL2 | Modificado | Caché de geometría en resize, eliminación de reflows en bucle, pausa y reanudación con `IntersectionObserver`, `pagehide` y `prefers-reduced-motion`. |
| `index.html` | Maquetación | Modificado | Contenedores semánticos `<main id="catalog-view">` y `<main id="opportunity-view">`. |
| `src/site.css` | Estilos fuente | Modificado | Clases para triaje rápido, fuente oficial destacada, evidencia colapsable y regla responsive móvil. |
| `styles.css` | CSS compilado | Modificado | Artefacto minificado generado reproduciblemente por Tailwind CSS v4.3.3. |
| `tests/e2e/catalog.spec.cjs` | Pruebas E2E | Modificado | 12 pruebas Playwright (navegación independiente, triaje semántico, estados vacíos, modal, comparador y viewports 1440px, 768px, 390px). |
| `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md` | Arquitectura | Modificado | Registro de las iteraciones `R3-02-UX-EXP-01` y `R3-02-UX-EXP-02` sin alterar la gobernanza. |
| `docs/audits/r3-02-preview-readiness-2026-11-19.md` | Auditoría | Untracked | Diagnóstico previo de preparación de entorno no productivo. |
| `docs/research/r3-02-informal-feedback-template.md` | Investigación | Untracked | Plantilla cualitativa para registrar impresiones informales del círculo de amigos. |
| `docs/audits/r3-02-ux-exploratory-iteration-2026-11-19.md` | Auditoría | Untracked | Informe de diseño e implementación técnica de UX-EXP-01. |
| `docs/audits/r3-02-ux-exp-02-acceptance-2026-11-19.md` | Auditoría | Nuevo (este doc) | Informe integral de aceptación, auditoría semántica y verificación. |

---

## 2. Auditoría Semántica Obligatoria del Triaje Rápido (B.4)

### 2.1 Hallazgo crítico detectado
En `R3-02-UX-EXP-01`, la función `quickTriage(job)` asignaba `Experiencia: Cumple` para la oportunidad real CookUnity (`OP-005`) porque el puesto estaba clasificado formalmente como `level: "Junior"`.

Sin embargo, la convocatoria en su publicación oficial exige explícitamente:
> *"1+ años de experiencia previa en áreas analíticas o cadena de suministro"*.

**Defecto conceptual identificado:**
1. Ruta Sistemas no recopila CVs ni conoce el perfil personal del usuario. Afirmar `Cumple` sugiere erróneamente que el usuario califica para la vacante o que la oportunidad es accesible sin experiencia previa.
2. Un estudiante de ciclos intermedios o egresado reciente con 0 años no cumple un requisito de 1+ años de experiencia previa.
3. El regex inicial `/\b(?:1|2)\s*a[ñn]o/i` no detectaba la notación `"1+ años"` (por la ausencia de espacio entre el dígito `1` y el signo `+`).

### 2.2 Corrección aplicada
1. **Separación estricta entre hechos de la vacante y perfil del postulante:**
   - Se ajustó el título del bloque a: `Triaje rápido de la convocatoria`.
   - Se actualizó el subtítulo explicativo: *"Lectura factual de 8 condiciones publicadas en la fuente oficial. Describe hechos de la vacante, no evalúa tu perfil personal ni genera un puntaje global."*
2. **Corrección del detector de experiencia previa en `quickTriage`:**
   - Regex actualizado a `/\b(?:1|2)\+?\s*a[ñn]os?/i`.
   - Si la vacante exige 1 o 2 años previos (caso `OP-005`), el badge asignado es **`Por revisar`** (aviso amarillo), con detalle factual:
     *`Nivel Junior: la convocatoria exige al menos 1 año de experiencia previa`*.
   - Si la vacante exige 3+ años o Senior (caso `OP-004`), el badge es **`No cumple`** (rojo/ámbar).
   - Si la vacante es explícitamente formativa, sin experiencia o prácticas preprofesionales (casos `OP-001`, `OP-002`, `QA-001`), el badge es **`Cumple`** (verde):
     *`Convocatoria formativa o sin experiencia previa requerida`*.
   - Si la experiencia no está informada en la fuente, el badge es **`No especificado`** (gris neutro).

### 2.3 Matriz de evaluación factual final de los 8 indicadores para OP-005

| Indicador | Dimensión Factual Evaluada | Badge | Detalle Factual Renderizado |
|---|---|---|---|
| **Pertinencia técnica** | Familia canónica de Ing. de Sistemas | **Cumple** | `Sistemas empresariales (área de Ingeniería de Sistemas)` |
| **Elegibilidad territorial** | Ámbito geográfico y contratación | **Cumple** | `Lima, Perú — contratación local verificable` |
| **Nivel y experiencia** | Experiencia previa exigida en fuente | **Por revisar** | `Nivel Junior: la convocatoria exige al menos 1 año de experiencia previa` |
| **Tecnologías declaradas** | Herramientas / stack publicado | **Cumple** | `SQL · Analítica de operaciones · Google Sheets · ERP/MRP` |
| **Modalidad de trabajo** | Modalidad declarada (Pres./Híb./Rem.) | **No especificado** | `Modalidad no precisada en la convocatoria` |
| **Tipo de oportunidad** | Naturaleza laboral o formativa | **Cumple** | `Oportunidad laboral junior/profesional` |
| **Compensación económica** | Rango salarial o subvención | **No especificado** | `No publicada en la convocatoria (la ausencia no es cero)` |
| **Vigencia y comprobación** | Comprobación activa dentro de TTL (7d) | **Cumple** | `Verificada recientemente (17/11/2026)` |

**Gobernanza confirmada:** Sin score sintético ("6/8"), sin porcentaje, sin ranking y sin penalización artificial por datos ausentes.

---

## 3. Revisión Técnica del Diff y Arquitectura

### 3.1 WebGL2 y Canvas (`canvas.js`)
- **Dimensiones:** `cachedContainerWidth` y `cachedContainerHeight` se actualizan exclusivamente en `updateProjection()` ante eventos de redimensionamiento (`ResizeObserver` y `window.resize`), eliminando llamadas a `getBoundingClientRect()` dentro del bucle de animación.
- **Pausa automática:** `IntersectionObserver` con umbral `0.02` pausa el renderizado (`cancelAnimationFrame`) cuando el Hero sale del viewport y lo reanuda con un único frame id cuando vuelve a ser visible.
- **Ciclo de vida:** El evento `pagehide` cancela la animación y desconecta ambos observers (`heroObserver`, `resizeObserver`).
- **Accesibilidad:** `prefers-reduced-motion: reduce` desactiva la animación continua y renderiza un único frame estático.
- **Degradación:** Ante ausencia de WebGL2 o canvas, oculta el lienzo y activa la clase `.canvas-unavailable` para usar el fondo estático de contingencia sin errores de consola.
- *Nota metodológica:* Se omite deliberadamente afirmar "0% de CPU/GPU" sin instrumentación de hardware especializada; se certifica la suspensión efectiva de llamadas a `requestAnimationFrame`.

### 3.2 Tailwind CSS y Estilos (`src/site.css`, `styles.css`, `package.json`)
- **Versión:** Tailwind CSS v4.3.3 y `@tailwindcss/cli` v4.3.3 fijados en `devDependencies`.
- **Compilación:** `npm run build:css` ejecuta `tailwindcss -i src/input.css -o styles.css --minify` en ~130ms.
- **Reproducibilidad:** Correspondencia 1:1 entre los componentes de `src/site.css` y el CSS compilado en `styles.css`.
- **Autonomía:** Cero llamadas a CDN o scripts externos (verificado por `test_static_contract.py`).

### 3.3 Navegación, Detalle y Rutas (`app.js`, `index.html`)
- **Deep Linking:** Parámetro `?id=OP-005` abre directamente la vista completa en `#opportunity-view`, actualiza el `<title>` del documento (`Supply Chain Analyst · CookUnity — Ruta Sistemas`) y oculta `#catalog-view`.
- **Navegación nativa en pestañas:** El título de cada tarjeta es un hipervínculo `<a href="?id=..." role="button" tabindex="0" data-open="...">` que permite Ctrl+clic o clic derecho para abrir en nueva pestaña, manteniendo compatibilidad con clics normales y navegación por teclado (Enter / Espacio).
- **Control de errores 404:** Identificadores inexistentes (ej. `?id=OP-999`) renderizan un mensaje amigable con botón «← Volver al catálogo».
- **Retorno al catálogo:** Botones superior e inferior restauran el catálogo, devuelven el título a `Ruta Sistemas` y limpian la URL mediante `history.pushState`.
- **Rutas relativas:** Todos los assets se resuelven mediante rutas relativas (`styles.css`, `app.js`, `./data/opportunities.json`), preservando compatibilidad tanto con el servidor local como con el prefijo de proyecto en GitHub Pages.

### 3.4 Información Interna y Trazabilidad de Procedencia
- `editorialDecision`: Retirada de la UI pública (modal y vista independiente). Conservada al 100% en `data/opportunities.seed.json` y `data/opportunities.json` para trazabilidad interna.
- `renderEmployerAssessment`: Retirada de la UI pública. Los metadatos de difusor, empleador y sector se presentan de manera clara en la cabecera y en la tarjeta de fuente oficial.
- **Tarjeta de fuente oficial:** Identifica `CookUnity — Greenhouse / Careers`, badge de verificación y enlace directo a postulación.
- **Desglose colapsable:** `<details class="evidence-collapsible">` aloja las 21 evidencias por campo ordenadas y colapsadas por defecto, manteniendo intacta la trazabilidad factual.

---

## 4. Pruebas Funcionales, Visuales y Responsive

Las pruebas automatizadas de extremo a extremo mediante Playwright (`tests/e2e/catalog.spec.cjs`) se ampliaron a 12 escenarios completos ejecutados tanto en motor Chromium Desktop como en emulación móvil (Pixel 5):

1. **Carga inicial y estado vacío:**
   - 1 oportunidad real visible por defecto (`OP-005`).
   - Búsqueda sin coincidencias muestra: `No encontramos coincidencias para esta búsqueda`.
   - Limpieza de filtros restaura el resultado. Atajo `/` enfoca el campo de búsqueda.
2. **Filtros combinados:**
   - Activación de ejemplos demostrativos (6 resultados).
   - Filtros por modalidad (`Remoto`), nivel (`Senior`), ubicación (`Perú`) y reseteo funcional.
3. **Detalle modal y comparador:**
   - Apertura de `OP-005`: verificación de títulos, fuente oficial, canal de postulación, Triaje rápido, ausencia de decisión editorial y ausencia de evaluación de empleador.
   - Apertura de demo `OP-003`: advertencia de ficha demostrativa y postulación deshabilitada.
   - Navegación por teclado (Enter / Espacio).
   - Selección de 2 elementos y apertura del modal comparativo sin puntuaciones ni ganadores.
4. **Vista independiente (Deep linking y 404):**
   - Carga directa de `/?id=OP-005`: visualización en `#opportunity-view`, ocultamiento de `#catalog-view`, título dinámico y retorno al catálogo con botón.
   - Carga de `/?id=OP-999`: mensaje amigable de registro no encontrado y retorno al catálogo.
5. **Auditoría responsive y ausencia de scroll horizontal:**
   - **Escritorio (1440 × 900):** Visualización limpia a 2 columnas en triaje y catálogo; `scrollWidth <= clientWidth`.
   - **Tablet / Ancho intermedio (768 × 1024):** Grid responsivo adaptado; sin solapamiento de tarjetas ni recorte de textos; `scrollWidth <= clientWidth`.
   - **Móvil (390 × 844):** Triaje colapsado a 1 columna; controles táctiles accesibles; `scrollWidth <= clientWidth`.

---

## 5. Matriz de Pruebas Técnicas Ejecutadas

| Prueba / Verificación | Comando de Ejecución | Resultado | Detalle |
|---|---|---|---|
| **Compilación CSS Tailwind** | `npm run build:css` | **PASS (0)** | Tailwind CSS v4.3.3 compilado en 133ms sin errores. |
| **Sintaxis de JavaScript (app)** | `node --check app.js` | **PASS (0)** | Cero errores de sintaxis o referencias inválidas. |
| **Sintaxis de JavaScript (canvas)** | `node --check canvas.js` | **PASS (0)** | Cero errores de sintaxis en el shader y bucle. |
| **Tests de UI en Node.js (vm)** | `node tests/catalog_ui.test.cjs` | **PASS (0)** | Pasan filtros, aislamiento, rutas relativas y degradación. |
| **Consistencia de Snapshot** | `python scripts/build_catalog.py --check` | **PASS (0)** | Snapshot de 6 registros idéntico al seed canónico. |
| **Calidad de Catálogo Schema 2** | `python scripts/validate_catalog.py` | **PASS (0)** | Catálogo canónico y publicado 100% conformes. |
| **Suite Completa Python** | `python -m unittest discover -s tests -p "test_*.py"` | **PASS (0)** | 193/193 pruebas aprobadas en 2.86s. |
| **Pruebas E2E Playwright** | `npx playwright test` | **PASS (0)** | 12/12 pruebas aprobadas (Chromium Desktop + Mobile Pixel 5). |
| **Linter de Diff Git** | `git diff --check` | **PASS (0)** | Cero espacios en blanco residuales o conflictos de formato. |

---

## 6. Procedimiento para Evaluación Local Privada

Para que el propietario y su círculo reducido puedan evaluar la aplicación localmente sin exponer servicios en Internet:

1. **Requisitos:** Python 3.10+ instalado. (Node.js solo se requiere si se desea recompilar CSS o ejecutar Playwright).
2. **Iniciar el servidor local:**
   ```bash
   python server.py
   ```
   *Salida esperada:*
   ```text
   Servidor local en http://127.0.0.1:4173/ (Ctrl+C para detener)
   ```
3. **Flujos recomendados para evaluación:**
   - **Flujo 1 (Catálogo general):** Abrir `http://127.0.0.1:4173/` y probar el desplazamiento suave sobre el Hero. Probar el filtro de búsqueda y el checkbox de ejemplos demostrativos.
   - **Flujo 2 (Detalle independiente):** Abrir directamente `http://127.0.0.1:4173/?id=OP-005`. Verificar el triaje rápido de la convocatoria, la tarjeta de fuente oficial y el enlace a postulación.
   - **Flujo 3 (Navegación e historial):** Hacer clic en «← Volver al catálogo», comprobar que la URL se limpia y usar los botones Atrás / Adelante del navegador.
   - **Flujo 4 (Comparación):** Activar ejemplos, seleccionar dos oportunidades y pulsar «Comparar» para verificar la tabla en español sin ganadores universales.
   - **Flujo 5 (Manejo de errores):** Abrir `http://127.0.0.1:4173/?id=OP-999` y comprobar la pantalla de oportunidad no encontrada.
4. **Detener el servidor:** Presionar `Ctrl+C` en la terminal.

---

## 7. Veredicto de Aceptación y Estado de Gobernanza

- **Veredicto:** **DONE**. La iteración `R3-02-UX-EXP-02` ha estabilizado y verificado integralmente el código, resolviendo el sesgo semántico del triaje para `OP-005`, validando los viewports responsive y garantizando que el proyecto se encuentra en condiciones óptimas para evaluación privada.
- **Gobernanza:**
  - Modelo Schema 2: Inalterado.
  - Catálogo: 1 oportunidad real (`OP-005` CookUnity) + 5 demostrativas (`OP-001`..`OP-004`, `QA-001`).
  - R3-02 formal: `NOT_STARTED` / `PENDING_HUMAN` (trabajo de campo con usuarios reales pendiente de convocatoria humana).
  - R3-03: `BLOCKED` (hasta contar con al menos 5 sesiones humanas válidas).
  - Git: No se han realizado commits ni pushes en este bloque, preservando la decisión de sincronización en manos del propietario.
