# INFORME DE AUDITORÍA Y CONSOLIDACIÓN PRE-RELEASE — FASE R7
## Verificación Técnica, Funcional, Visual, Accesibilidad y Preparación para Release

- **Identificador de Tarea:** `TASK-R7-RELEASE-AUDIT`
- **Fase:** R7 — Inteligencia de condiciones laborales y profesionales
- **Proyecto:** Velora
- **Prioridad:** `P2` (Consolidación operativa)
- **Clasificación:** `[REUTILIZACIÓN_INTERNA]` / `[AUDITORÍA_TÉCNICA]`
- **Fecha de Certificación:** 2026-11-26
- **Estado Resultante de la Auditoría:** `COMPLETED`
- **Dictamen de Preparación para Release:** `DEPLOYED_AND_VERIFIED (v0.7.0)` (Despliegue verificado en producción)

---

## 1. Resumen Ejecutivo

En cumplimiento de la directiva técnica para **`TASK-R7-RELEASE-AUDIT`**, se ha ejecutado la auditoría integral técnica, funcional, visual, de accesibilidad y regresión de la **Fase R7** de Velora.

La evaluación comprobó la integración efectiva y convivencia de las dos implementaciones funcionales:
1. **`TASK-R7-01` — Taxonomía de Regímenes Laborales Peruanos:** Clasificación determinista de 7 regímenes normativos peruanos (Ley 28518, D. Leg. 1057 / CAS, TUO D. Leg. 728, C.C. 1764, Ley 31396), filtro reactivo en UI (`#regime-filter`), badges temáticos y sección de marco contractual en el modal y vista de oportunidad.
2. **`TASK-R7-02` — Comparador de Trayectorias y Requisitos Técnicos:** Extensión del comparador nativo (`#compare-dialog`) con matriz visual de 3 columnas (`Coincidentes`, `Exclusivas Oportunidad A`, `Exclusivas Oportunidad B`), badges semánticos de obligatoriedad (`REQUIRED`, `PREFERRED`, `MENTIONED`), manejo transparente de vacíos técnicos (`UNSPECIFIED`) y trazabilidad textual de procedencia con citas exactas.

**Conclusiones Clave de la Certificación:**
- **Integración y Convivencia:** Ambos módulos conviven armónicamente sin colisiones en frontend ni en backend.
- **Pruebas Unitarias e Integración:** 313 de 313 pruebas de Python aprobadas (100% OK), y suite de frontend en Node.js/VM aprobada con exit code 0.
- **Navegador Real y Accesibilidad WCAG 2.1 AA:** Batería automatizada con Chromium y `@axe-core/playwright` certifica **0 violaciones críticas o serias** en Desktop (1280x800), Mobile (375x667) y Narrow (320x568).
- **Integridad de Catálogos Canónicos:** Paridad criptográfica SHA-256 intacta al 100% (`710D77...` y `1D96EC...`). Cero dependencias externas agregadas.
- **Dictamen Resultante:** `READY_FOR_RELEASE`. El defecto menor DEF-R7-01 ha sido resuelto y verificado integralmente; las suites Playwright E2E y axe-core aprueban 45 de 45 pruebas (100% OK) en Chromium, Mobile y Narrow sin violaciones WCAG 2.1 AA, alineadas con la gobernanza fail-closed del TTL de 7 días.

---

## 2. Rama y Commit Auditados

- **Rama:** `main` (sincronizada con `origin/main`).
- **Commit HEAD en repositorio:** `786bd34 docs(roadmap): close TASK-R4-11-02 and Phase R4-11 following verified production deployment`.
- **Hash de referencia remoto:** `786bd3469176ba09bb997bbbb761e0959fc922e9`.
- **URL remota:** `https://github.com/Blueisazul/WebRutaSistemas.git`.

---

## 3. Estado de Git y Clasificación de Integración

Se auditó minuciosamente el estado del árbol de trabajo para clasificar con precisión la presencia de R7:
- **Estado Real:** **SOLO EN CAMBIOS LOCALES (Working Tree)**.
- **Detalle de Integración:**
  - Los archivos de `TASK-R7-01` y `TASK-R7-02` están completamente implementados, verificados y presentes en el working tree local sobre la rama `main`.
  - **NO** han sido objeto de `git commit` local.
  - **NO** han sido objeto de `git push` a `origin/main`.
  - **NO** forman parte de un Pull Request integrado ni fusionado.
  - **NO** están desplegados en los entornos de producción (GitHub Pages / Vercel).
  - La producción actual sirve el commit `786bd34` (cierre de R4-11).

---

## 4. Verificación de Integración de R7-01

- **Componente Normalizador (`collector/labor_regime.py`):** Define los 7 identificadores canónicos (`PRE_PROFESSIONAL_INTERNSHIP`, `PROFESSIONAL_INTERNSHIP`, `CAS`, `LABOR_REGIME_728`, `CIVIL_SERVICES`, `OTHER`, `UNSPECIFIED`) con citas legales peruanas exactas.
- **Pipeline de Datos (`collector/classification.py`, `collector/autopublish.py`, `scripts/catalog_quality.py`):** Integración completa para el enriquecimiento retrocompatible de nuevas oportunidades.
- **Frontend UI (`index.html`, `app.js`):**
  - Selector `<select id="regime-filter">` en el grid de filtros secundarios.
  - Renderizado dinámico de badges con estilos temáticos y tooltips explicativos.
  - Sección detallada *"Régimen Contractual y Marco Normativo"* en modal y vista independiente.
  - Manejo estricto *fail-closed*: `UNSPECIFIED` jamás se asume como 728 o CAS.
- **Evaluación:** `PASS`.

---

## 5. Verificación de Integración de R7-02

- **Componente Normalizador (`collector/skills.py`):** Taxonomía de +80 tecnologías, normalización de alias (`Postgres` $\to$ `PostgreSQL`, `AWS` $\to$ `Amazon Web Services`) y protección determinista de falsos positivos (Lenguaje C, SQL Server vs SQL, C++, telecomunicaciones vs redes sociales).
- **Frontend UI (`app.js`):**
  - Matriz visual de 3 columnas en `#compare-dialog` (`Coincidentes`, `Exclusivas Oportunidad A`, `Exclusivas Oportunidad B`).
  - Badges semánticos de obligatoriedad (`REQUIRED`, `PREFERRED`, `MENTIONED`) con extractos textuales contextuales.
  - Alerta destacada cuando una vacante no declara requisitos técnicos estructurados (`UNSPECIFIED`).
  - Fila *"Régimen contractual"* incorporada en la tabla atributiva de comparación.
- **Evaluación:** `PASS`.

---

## 6. Resultados Funcionales

Se comprobó la convivencia interactiva de ambos componentes:

| Escenario Funcional | Tipo de Verificación | Estado | Detalle del Resultado |
|---|---|:---:|---|
| Carga de catálogo y filtros base | Interacción real | `PASS` | 106 oportunidades activas en vista por defecto tras política TTL fail-closed. |
| Filtro interactivo de régimen | Navegador real | `PASS` | Filtra 8 prácticas preprofesionales, 97 no especificadas, 0 CAS en catálogo privado. |
| Interacción cruzada de filtros | Navegador real | `PASS` | El filtro de régimen se combina perfectamente con filtros de modo (remoto), nivel y texto. |
| Modal de detalle con marco legal | Navegador real | `PASS` | Muestra sección normativa con jornada, derechos y cautelas; cierre vía X y Escape. |
| Apertura y selección en comparador | Navegador real | `PASS` | Permite seleccionar 2 empleos y abre `#compare-dialog` con contraste atributivo. |
| Matriz técnica de competencias | Navegador real | `PASS` | Despliega columnas coincidentes y exclusivas, badges de prioridad y régimen contractual. |
| Manejo fail-closed de vacíos técnicos | Navegador real | `PASS` | Alerta informativa visible si un empleo no declara requisitos técnicos estructurados. |
| Limpieza y remoción de comparación | Navegador real | `PASS` | Botones de eliminación y vaciado restauran el estado interactivo. |

---

## 7. Resultados de Pruebas de Navegador

Se ejecutaron pruebas automatizadas sobre una instancia de servidor local loopback (`http://127.0.0.1:4173/`):
- **Desktop (1280x800):** Carga completa del catálogo, renderizado del grid de 8 filtros, modal de detalle fluido, diálogo comparador sin desbordamientos horizontales.
- **Mobile (375x667):** Modal responsivo adaptado al viewport, matriz de competencias apilada legiblemente, sin scroll horizontal accidental.
- **Narrow (320x568):** Adaptación correcta de tarjetas, textos legibles y botones táctiles accesibles.
- **Consola del Navegador:** Cero errores JavaScript (`uncaught exceptions`) y cero recursos 404.
- **Evaluación:** `PASS`.

---

## 8. Resultados de Accesibilidad WCAG 2.1 AA

Se ejecutó auditoría automatizada con `@axe-core/playwright` cubriendo los tags `['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']`:

| Vista / Componente Auditado | Viewport | Violaciones Críticas | Violaciones Serias | Dictamen WCAG |
|---|---|:---:|:---:|:---:|
| Catálogo Principal (Filtros R7-01) | Desktop (1280x800) | **0** | **0** | `PASS` |
| Diálogo de Detalle (Sección Normativa R7-01) | Desktop (1280x800) | **0** | **0** | `PASS` |
| Diálogo Comparador (Matriz R7-02) | Desktop (1280x800) | **0** | **0** | `PASS` |
| Vista Principal Catálogo | Mobile (375x667) | **0** | **0** | `PASS` |
| Vista Principal Catálogo | Narrow (320x568) | **0** | **0** | `PASS` |
| Estado Vacío y Búsquedas sin Coincidencia | Multi-viewport | **0** | **0** | `PASS` |

**Comprobaciones Manuales:**
- Navegación por teclado completa (Tab / Shift+Tab) sobre `<select id="regime-filter">` y controles de comparación: `PASS`.
- Atrapamiento de foco (*focus trap*) en diálogos modales nativos `<dialog>`: `PASS`.
- Descarte y cierre inmediato con tecla `Escape`: `PASS`.
- Jerarquía semántica de encabezados y nombres accesibles en botones interactivos: `PASS`.

---

## 9. Resultados de Regresión e Integridad

- **Pruebas de Regímenes Laborales (`tests/test_labor_regime.py`):** 23/23 passing (`PASS`).
- **Pruebas de Competencias y Comparador (`tests/test_skills.py`):** 13/13 passing (`PASS`).
- **Pruebas Frontend VM (`tests/catalog_ui.test.cjs`):** 100% passing (`PASS`).
- **Suite Global de Pruebas Python:** 313 de 313 pruebas pasando en 8.27s sin errores ni regresiones (`PASS`).
- **Validación de Calidad de Catálogo (`scripts/catalog_quality.py`):** Aprobada (`PASS`).
- **Pruebas E2E (Playwright + axe-core):** 45/45 passing (`PASS` - 15/15 en `accessibility.spec.cjs` y 30/30 en `catalog.spec.cjs` en viewports Chromium, Mobile y Narrow). Defecto DEF-R7-01 resuelto desacoplando aserciones de recuentos estáticos y validando dinámicamente la degradación fail-closed de `OP-005`.

---

## 10. Integridad de Catálogos Canónicos y Hashes

Se calcularon los hashes criptográficos SHA-256 de los catálogos antes y después de la auditoría:
- `data/opportunities.seed.json`:
  - Hash calculado: `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917`
  - Estado: **112 registros, 100% INTACTO** (coincide exactamente con el hash histórico).
- `data/opportunities.json`:
  - Hash calculado: `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02`
  - Estado: **112 registros, 100% INTACTO** (coincide exactamente con el hash histórico).
- `git diff --exit-code data/`: Código de salida `0` (cero modificaciones accidentales).

---

## 11. Dependencias Verificadas

- **Nuevas dependencias de producción agregadas:** **0** (*Zero New Dependencies*).
- **Herramientas utilizadas:** Módulos estándar de Python (`re`, `unicodedata`, `json`, `dataclasses`, `unittest`), JavaScript vanilla en cliente, y dependencias de desarrollo existentes (`@playwright/test`, `@axe-core/playwright`).
- **Manifests:** `package.json` intacto sin alteraciones de paquetes ni dependencias adicionales.

---

## 12. Defectos Clasificados

### Hallazgo DEF-R7-01: Aserción Estática de Recuento en Tests E2E vs. Política Dinámica de TTL [RESUELTO]
- **Identificador:** `DEF-R7-01`
- **Severidad:** `LOW` (Fragilidad de test fixture / no afectaba al usuario final).
- **Estado Actual:** `RESOLVED` / `CLOSED` (Verificado en `TASK-R7-RELEASE-EXECUTION`).
- **Archivos y Componentes:** `tests/e2e/accessibility.spec.cjs` y `tests/e2e/catalog.spec.cjs`.
- **Comportamiento Observado:** Los tests E2E históricos creados en fases previas contenían aserciones rígidas de texto (`toHaveText('107 resultados')`) y una búsqueda no condicionada del botón `button.card-button[data-open="OP-005"]` sin marcar la casilla *"Incluir no confirmadas"*. Al transcurrir más de 7 días desde la última verificación de `OP-005` (`2026-11-17`), la gobernanza *fail-closed* degradó automáticamente `OP-005` a `unconfirmed`/`stale` (106 resultados activos visibles por defecto).
- **Solución Implementada:**
  1. Flexibilización de aserciones de recuento a patrones dinámicos (`/\d+\s+resultados/`) en suites de accesibilidad y catálogo.
  2. Aserción dual para `OP-005`: se valida que esté oculta por defecto en la vista canónica activa, y accesible únicamente tras marcar `#include-unconfirmed`.
  3. Comprobación explícita de badges y estados en modal y comparador: `OP-006` muestra *"Fuente oficial verificada"* y enlace de postulación activo, mientras `OP-005` muestra *"Verificación pendiente de revalidar"* y oculta el botón de postulación.
  4. Paginación y conteo dinámicos en base a `totalItems` reales.
  5. Desambiguación de selectores CSS en la cuadrícula de resumen ante el nuevo card de *Régimen y modalidad*.
- **Resultado de la Verificación:** 45 de 45 pruebas E2E aprobadas al 100% en Chromium, Mobile y Narrow con 0 violaciones WCAG 2.1 AA.

---

## 13. Riesgos Residuales

1. **Riesgo de Interpretación Legal Errónea por el Usuario:**
   - *Mitigación:* Se implementó un descargo de responsabilidad claro en la sección normativa de `app.js` y `index.html`, enfatizando que la clasificación es orientativa y que el postulante debe verificar las bases oficiales.
2. **Riesgo de Vacíos Técnicos en Ofertas Laborales Antiguas:**
   - *Mitigación:* El comparador activa de forma fail-closed un banner de alerta amarilla cuando una vacante no declara habilidades estructuradas, evitando deducciones arbitrarias.
3. **Riesgo de Regresiones en Revalidación Programada:**
   - *Mitigación:* Suite de 313 pruebas unitarias de Python y 23 escenarios de revalidación pasan al 100%, con anclaje temporal de fechas de evaluación `as_of`.

---

## 14. Dictamen de Preparación para Release

### Dictamen Oficial: `READY_FOR_RELEASE`

La Fase R7 está técnicamente consolidada, integrada y validada al 100%. Tras la resolución de `DEF-R7-01`, tanto las suites de pruebas unitarias, UI en VM, pruebas E2E en Playwright multi-dispositivo y auditoría de accesibilidad WCAG 2.1 AA pasan sin observaciones ni violaciones. Los catálogos canónicos conservan su integridad criptográfica inalterada. El código local se encuentra preparado para la revisión, autorización y despliegue del propietario.

---

## 15. Propuesta de Release Unificado (Fase R7)

1. **Alcance a Desplegar:**
   - Módulo de regímenes laborales peruanos: `collector/labor_regime.py`.
   - Módulo normalizador de competencias y comparador: `collector/skills.py`.
   - Frontend interactivo: `index.html` y `app.js`.
   - Suites de pruebas: `tests/test_labor_regime.py`, `tests/test_skills.py`, `tests/catalog_ui.test.cjs`, `tests/e2e/accessibility.spec.cjs` y `tests/e2e/catalog.spec.cjs`.
   - Informes de auditoría: `docs/audits/R7-01-LABOR-REGIME-TAXONOMY.md`, `docs/audits/R7-02-OPPORTUNITY-COMPARATOR.md` y `docs/audits/R7-RELEASE-CONSOLIDATION-AUDIT.md`.
2. **Rama y Commit Base:**
   - Rama: `main`
   - Commit Base: `786bd34`
3. **Estrategia de Despliegue:**
   - Distribución Jamstack desacoplada en GitHub Pages y Vercel sin servidor de backend en producción.
4. **Comprobaciones Post-Despliegue:**
   - Validación de paridad SHA-256 en endpoints de producción.
   - Comprobación en vivo del selector de régimen y el comparador en navegadores reales.
5. **Estrategia de Reversión (*Rollback*):**
   - Reversión atómica mediante `git revert` hacia el commit base `786bd34` preservando la inmutabilidad de los catálogos.

---

## 16. Estado de Publicación y Despliegue en Producción

El release de la Fase R7 ha sido formalmente ejecutado y verificado en producción bajo la autorización del propietario (`[EJECUTAR_RELEASE_R7_AUTORIZADO]`):

- **Commit Consolidado:** `4006413d7b6284fdfe32c359b39b5c72e7ab55c0` en `main`.
- **Tag Oficial:** `v0.7.0` (anotado).
- **Pipeline Automatizado:** GitHub Actions Run ID `45876535680` (`Validate and publish Ruta Sistemas` - conclusion: `success`).
- **Despliegues Verificados:**
  - GitHub Pages: `https://blueisazul.github.io/WebRutaSistemas/` (HTTP 200, 0 errores de consola, 0 fallos de red).
  - Vercel Production: `https://velora-six-fawn.vercel.app/` (HTTP 200, 0 errores de consola, 0 fallos de red).
- **Paridad Criptográfica de Catálogo:** 100% idéntico bit a bit entre ambas plataformas (`417B3847942B76DCA5EB8750583656626517302637310DDC2759A3D656F62ED8`, 537,807 bytes).
- **Evidencias Completas:** Véase [`docs/audits/TASK-R7-RELEASE-EXECUTION.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/TASK-R7-RELEASE-EXECUTION.md).
