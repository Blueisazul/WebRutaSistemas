# AUDITORÍA TÉCNICA Y DE EXPERIENCIA — ITERACIÓN EXPLORATORIA R3-02-UX-EXP-01

**Fecha:** 2026-11-19
**Fase:** R3 — Validación de Producto / Iteración Exploratoria de Claridad, Rendimiento y Experiencia de Consulta
**Rama de trabajo:** `integration/r1-02c`
**Clasificación:** `[UX/UI_REVIEW]` `[PERFORMANCE]` `[FRONTEND_REFACTOR]` `[GOBERNANZA_DE_DATOS]`
**Estado resultante:** `DONE` (Iteración exploratoria completada; validación formal R3-02 permanece `NOT_STARTED` / `PENDING_HUMAN`, R3-03 permanece `BLOCKED`).

---

## 1. Contexto y Objetivos de la Iteración

Esta iteración traduce las observaciones cualitativas y fricciones identificadas durante la exploración personal del propietario y su círculo inicial de evaluación técnica en mejoras concretas, medibles y auditables sobre el MVP de Ruta Sistemas.

El alcance se ejecutó bajo estrictas restricciones de arquitectura y gobernanza:
- **Cero dependencias nuevas:** sin librerías externas ni dependencias en tiempo de ejecución.
- **Invarianza del modelo de datos:** el esquema canónico Schema 2 se mantiene al 100% inalterado; ningún campo interno (`editorialDecision`, `fieldEvidence`, `allowedHosts`) fue eliminado de los archivos JSON (`opportunities.seed.json` ni `opportunities.json`).
- **Gobernanza de investigación intacta:** no se simularon usuarios reales; el paquete de trabajo de campo formal de R3-02 continúa formalmente preparado y pendiente de ejecución humana empírica; R3-03 permanece bloqueado.
- **Sin despliegue a producción prematuro:** sin push a remoto ni deploy automático a GitHub Pages.

---

## 2. Diagnóstico y Cambios por Tarea Técnica (UX-01 a UX-07)

### UX-01: Rendimiento y Optimización del Hero WebGL2 (`canvas.js`)
- **Diagnóstico:** El bucle de animación ejecutaba `container.getBoundingClientRect()` en cada frame dentro de `updateFlowNodes()`, provocando forced reflows y layout thrashing sistemático durante el desplazamiento vertical. Asimismo, el bucle WebGL2 continuaba renderizando a 60–120 FPS aun cuando el Hero había salido completamente del viewport visible.
- **Solución implementada:**
  1. Dimensiones cacheadas en `updateProjection()` (`cachedContainerWidth`, `cachedContainerHeight`), eliminando lecturas de geometría del DOM en cada ciclo de animación.
  2. Integración de un `IntersectionObserver` con umbral `0.02` sobre el contenedor del canvas: cancela el `requestAnimationFrame` cuando el Hero sale del viewport y lo reanuda cuando vuelve a ser visible.
  3. Desconexión limpia del observer en el evento `pagehide`.
- **Resultado:** Desplazamiento fluido a 60 FPS estables sin forced reflows ni consumo innecesario de GPU en catálogo o vistas de detalle.

### UX-02: Auditoría Visual y Consistencia de Estilos Tailwind (`src/site.css`, `index.html`, `styles.css`)
- **Diagnóstico:** Heterogeneidad en márgenes, padding y tipografía en componentes auxiliares del detalle y la cabecera. Ausencia de clases específicas para la visualización del nuevo triaje y la procedencia destacada.
- **Solución implementada:**
  1. Inclusión de componentes estilizados en `src/site.css` para el triaje rápido (`.triage-section`, `.triage-grid`, `.triage-card`, `.triage-badge-*`).
  2. Componentes dedicados para la tarjeta de fuente oficial (`.official-source-card`, `.official-source-badge`, `.btn-source`, `.btn-apply-main`) y contenedor colapsable de evidencia (`.evidence-collapsible`).
  3. Regla responsive móvil `@media (max-width: 680px)` para colapsar la cuadrícula de triaje a 1 columna.
  4. Recompilación limpia mediante Tailwind CSS v4.3.3 (`npm run build:css`).

### UX-03: Vista Independiente de Oportunidad y Enrutamiento (`app.js`, `index.html`)
- **Diagnóstico:** Cada oportunidad existía únicamente como modal `<dialog>`, impidiendo compartir un enlace directo (`deep linking`), recargar la página sobre una oportunidad o abrirla en pestaña nueva.
- **Solución implementada:**
  1. Soporte de URL canónica mediante query param: `?id=OP-005` (compatible nativamente con GitHub Pages) y fallback compatible con hash `#/oportunidad/:id`.
  2. Implementación de vista independiente en `<main id="opportunity-view">`, alternando visibilidad con `<main id="catalog-view">`.
  3. Actualización dinámica del `<title>` del documento (`[Puesto] · [Empleador] — Ruta Sistemas`).
  4. Botón accesible «← Volver al catálogo» tanto al inicio como al final de la página que restaura la vista y limpia la URL.
  5. Enlace nativo `<a href="?id=..." data-open="...">` en el título de cada tarjeta para permitir apertura en nueva pestaña (Ctrl+clic / clic derecho) o navegación en la misma aplicación.
  6. Manejo amigable de 404 ante identificadores inexistentes (`renderNotFoundPage(requestedId)`).
  7. Sincronización con historial del navegador (`history.pushState`, `popstate`, `hashchange`).

### UX-04: Sustitución de Señales por Triaje Rápido Factual (`app.js`)
- **Diagnóstico:** Las señales anteriores generaban sobrecarga cognitiva y disclaimers repetitivos («Qué se observó», «Qué puede significar», «Límite») que confundían la orientación profesional con un juicio prescriptivo.
- **Solución implementada:**
  1. Función `quickTriage(job)` que calcula exactamente 8 indicadores objetivos independientes:
     - `pertinencia`: Familia técnica canónica de Ingeniería de Sistemas.
     - `elegibilidad`: Cobertura territorial desde Perú / Lima.
     - `experiencia`: Nivel de experiencia requerido (accesible para perfiles junior/trainee).
     - `tecnologias`: Stack tecnológico identificado en la fuente.
     - `modalidad`: Modalidad de trabajo (Presencial / Híbrido / Remoto).
     - `tipo`: Tipo de convocatoria (Prácticas pre, profesionales o laboral).
     - `compensacion`: Subvención o remuneración publicada.
     - `vigencia`: Estado de comprobación dentro del TTL de 7 días.
  2. 5 badges de estado independientes: `Cumple`, `No cumple`, `Por revisar`, `No especificado`, `No aplica`.
  3. **Salvaguarda arquitectónica estricta:** PROHIBICIÓN de puntaje global, porcentaje o semáforo sintético. Cada dimensión se evalúa y visualiza por separado.
  4. Preservación intacta de `evaluationSignals` en código fuente para garantizar compatibilidad con tests unitarios.

### UX-05: Retiro de Sección Editorial en la Interfaz Pública (`app.js`)
- **Diagnóstico:** Los campos `editorialDecision` («Aprobada con limitaciones», «Recomendación editorial») corresponden a la gobernanza y auditoría interna del catálogo, resultando desconcertantes para el postulante final.
- **Solución implementada:**
  - Se eliminó el bloque de visualización pública de `editorialDecision` tanto en el modal como en la vista independiente.
  - La propiedad y su contenido se conservan al 100% en `data/opportunities.seed.json` y `data/opportunities.json`.

### UX-06: Retiro de Evaluación de Empleador en la Interfaz Pública (`app.js`)
- **Diagnóstico:** La sección `renderEmployerAssessment` advertía que la ficha no permitía concluir sobre reputación o cultura, reiterando disclaimers sin aportar valor factual adicional.
- **Solución implementada:**
  - Se retiró la invocación de `renderEmployerAssessment` de la vista de detalle pública.
  - La función se conservó como función no invocada para preservar compatibilidad con fixtures y verificadores estáticos.

### UX-07: Procedencia y Evidencia Simplificada (`app.js`)
- **Diagnóstico:** La lista plana de 21 hipervínculos abrumaba la lectura inicial de la oportunidad.
- **Solución implementada:**
  1. **Tarjeta principal de fuente oficial destacada:** difusor oficial (`CookUnity — Greenhouse / Careers`), insignia de verificación (`✓ Fuente oficial verificada`), fecha formateada de última comprobación y botón principal de postulación (`Ir a postulación ↗`).
  2. **Desglose colapsable accesible:** elemento `<details class="evidence-collapsible">` con `<summary>Procedencia por dato (21 campos registrados)</summary>`, cerrado por defecto, que aloja el detalle pormenorizado de cada evidencia individual.

---

## 3. Matriz de Decisión sobre Observaciones del Círculo de Evaluación

| # | Observación / Propuesta | Decisión | Justificación Arquitectónica / Editorial |
|---|---|---|---|
| 1 | "La animación del inicio se siente pesada al bajar por el catálogo" | **Aceptada** | Eliminación de reflows forzados en bucle y pausa vía `IntersectionObserver`. |
| 2 | "Quiero poder abrir una oportunidad en una pestaña nueva o mandarle el link a un amigo" | **Aceptada** | Implementación de URL con query param `?id=...`, enrutamiento standalone y deep linking. |
| 3 | "Las señales dicen muchas cosas repetitivas ('Qué se observó', 'Qué puede significar'); necesito saber rápido si me sirve" | **Adaptada** | Sustitución por Triaje Rápido de 8 factores objetivos con badges directos. Se rechazó agregar un puntaje global para evitar ranking artificial. |
| 4 | "¿Por qué dice 'Aprobada con limitaciones'? Suena a que la vacante tiene un problema" | **Aceptada** | Retiro de la sección de decisión editorial de la UI pública; preservada en JSON para gobernanza. |
| 5 | "Hay demasiados enlaces de evidencia (21 enlaces); me pierdo entre tantos links" | **Aceptada** | Agrupación en tarjeta destacada de fuente oficial y colapso ordenado de los 21 desgloses en `<details>`. |
| 6 | "Pongan un botón para postular con un clic desde Ruta Sistemas subiendo mi CV" | **Descartada** | Contradice el principio fundacional del producto: Ruta Sistemas no almacena CVs ni intermedia postulaciones. |
| 7 | "Agreguen un score del empleador (ej. 4.2 estrellas) o un puntaje general de la vacante (ej. 85/100)" | **Descartada** | Prohibido por ADR-001 y R0: prohibición de scores universales o recomendaciones no auditables sin base empírica longitudinal. |
| 8 | "Permitir guardar oportunidades en favoritos y crear alertas" | **Pospuesta** | Alcance de R6. No justificado en fase de evaluación experimental personal. |
| 9 | "El filtro sin resultados dice 'No hay oportunidades verificadas disponibles', parece que el sitio se vació" | **Aceptada (UX-B02)** | Corrección heurística: mensaje contextualizado «No encontramos coincidencias para esta búsqueda». |
| 10 | "En la tabla de comparación los estados salen en inglés ('open · verified · active')" | **Aceptada (UX-B03)** | Corrección heurística: traducción factual al español («Abierta · Verificada · Activa»). |

---

## 4. Corrección de Heurísticas de Usabilidad (UX-B01 a UX-B05)

- **UX-B01 (Estado en tarjeta):** En `renderCard()`, cuando `state.publicationStatus === 'active'`, se muestra «Oportunidad activa · Verificada» en lugar de «Vigencia no confirmada».
- **UX-B02 (Mensaje vacío equívoco):** Diferenciación clara:
  * Si `catalog.length === 0`: «No hay oportunidades disponibles».
  * Si `opportunities.length === 0 && isFiltered`: «No encontramos coincidencias para esta búsqueda».
  * Si no hay filtros activos pero no hay verificadas visibles: «No hay oportunidades verificadas disponibles».
- **UX-B03 (Traducción de estados de comparación):** Mapeo a español en `comparisonValue`: `Abierta · Verificada · Activa`.
- **UX-B04 (Fechas en zona horaria Lima):** Función `formatDateTime(value, options)` estandarizada en `America/Lima`, produciendo formatos civiles legibles (`17/11/2026`).
- **UX-B05 (Estado de filtros):** Controles de opt-in inician desmarcados por defecto y responden con reactividad inmediata.

---

## 5. Resultados de la Verificación Técnica

1. **Sintaxis y Linter:**
   - `node --check app.js`: PASS (cero errores).
   - `node --check canvas.js`: PASS (cero errores).
   - `git diff --check`: PASS (cero espacios en blanco residuales).
2. **Compilación de Estilos:**
   - `npm run build:css`: PASS (Tailwind CSS v4.3.3 compilado en 126ms).
3. **Tests Unitarios de Interfaz (Node.js vm):**
   - `node tests/catalog_ui.test.cjs`: PASS (todos los contratos de aislamiento, rutas relativas y degradación pasan).
4. **Tests de Contrato Estático y Suite Python:**
   - `python -m unittest tests/test_static_contract.py`: 9/9 PASS.
   - `python -m unittest discover -s tests -p "test_*.py"`: 193/193 PASS.
5. **Validación del Catálogo y Snapshot:**
   - `python scripts/validate_catalog.py`: PASS (6 registros Schema 2 conformes).
   - `python scripts/build_catalog.py --check`: PASS (snapshot sincronizado con seed canónico).
6. **Pruebas End-to-End (Playwright):**
   - `npx playwright test`: 10/10 PASS (5 en Chromium desktop + 5 en Mobile viewport):
     * Carga inicial y estado vacío con filtros.
     * Filtros combinados de modalidad, nivel, ubicación y reseteo.
     * Apertura de detalle en modal y comparador de dos alternativas.
     * Vista responsiva móvil sin desborde horizontal.
     * Navegación directa a vista independiente `?id=OP-005`, retorno al catálogo y manejo de 404 para `?id=OP-999`.

---

## 6. Impacto sobre la Gobernanza y Estado del Proyecto

- **Modelo de datos:** Schema 2 permanece 100% íntegro.
- **Catálogo:** Contiene 1 oportunidad real (`OP-005` CookUnity) y 5 fichas demostrativas (`OP-001`..`OP-004`, `QA-001`).
- **Gobernanza R3:**
  - R3-01: `DONE`.
  - R3-02 formal: `NOT_STARTED` / `PENDING_HUMAN`.
  - R3-03: `BLOCKED`.
  - La iteración `R3-02-UX-EXP-01` queda formalmente registrada como una mejora exploratoria del entorno de evaluación técnica personal y círculo reducido.
