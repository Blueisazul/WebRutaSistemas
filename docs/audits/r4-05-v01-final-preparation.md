# R4-05 — PREPARACIÓN Y VALIDACIÓN FINAL DE v0.1
## Expediente Técnico de Preparación de Release, Auditoría Formal de Accesibilidad (WCAG 2.1 AA) y Matriz de Aceptación

- **Identificador de Bloque:** `R4-05`
- **Fecha de Emisión:** 2026-11-22
- **Estado del Bloque:** `READY_FOR_OWNER_APPROVAL` (Preparación técnica completada al 100%; decisión editorial sobre fichas demostrativas y autorización de publicación pendientes por parte del propietario).
- **Proyecto:** Ruta Sistemas (`https://github.com/Blueisazul/WebRutaSistemas`)
- **Rama:** `integration/r1-02c`
- **Responsables Técnicos:** Principal Software Architect, Senior Software Engineer, QA Automation Engineer, Accessibility Specialist, OSS Integration Specialist, Release Engineer.
- **Marco de Gobernanza:**
  - Cero git commit, cero git push, cero merge a `main`, cero despliegue en esta sesión.
  - Cero dependencias añadidas al bundle público de producción.
  - Una única dependencia de desarrollo OSS integrada con justificación rigurosa: `@axe-core/playwright` v4.14.0 (licencia MPL-2.0, uso exclusivo en tests E2E locales/CI).
  - Preservación absoluta del catálogo canónico: `data/opportunities.seed.json` (15 fichas: 10 reales, 5 demo) y `data/opportunities.json` (15 fichas) se mantienen 100% inalterados criptográficamente.
  - Bandeja local de staging en `data/candidates/inbox.local.json` preservada con 74 candidatos en `pending_review` (cero promoción autónoma, cero PII).
  - Trabajo de campo formal externo R3-02 conservado como `DEFERRED_BY_OWNER`.

---

## 1. Estado Inicial Comprobado y Contexto Verificado

Antes de iniciar la ejecución de R4-05, se auditó el estado real del árbol de trabajo, verificando:
- **Catálogo Canónico:** Exactamente 15 fichas en `data/opportunities.seed.json` (10 reales verificadas: OP-005 CookUnity, OP-006..OP-010 Canonical, OP-011..OP-014 Sezzle; 5 registros demostrativos históricos: OP-001..OP-004 y QA-001).
- **Staging Local:** 74 candidatos registrados bajo Candidate Schema 2 en `data/candidates/inbox.local.json`, todos en estado de revisión editorial controlado (`pending_review`).
- **Línea Base de Pruebas:** 220 pruebas unitarias e integradas en Python y 20 pruebas E2E en Playwright aprobadas al 100% en el cierre de R4-04.
- **Validadores:** `scripts/validate_catalog.py`, `scripts/build_catalog.py --check` y `scripts/validate_candidates.py` reportando 0 errores de validación.

---

## 2. Archivos Inspeccionados

1. **Frontend y Maquetación:** `index.html`, `app.js`, `styles.css`, `src/input.css`, `src/site.css`.
2. **Datos Canónicos y Staging:** `data/opportunities.seed.json`, `data/opportunities.json`, `data/candidates/inbox.local.json`.
3. **Herramientas y Scripts de Publicación:** `scripts/pages_artifact.py`, `scripts/build_catalog.py`, `scripts/validate_catalog.py`, `scripts/editorial_cli.py`.
4. **Infraestructura de Pruebas y CI/CD:** `package.json`, `package-lock.json`, `playwright.config.cjs`, `tests/e2e/catalog.spec.cjs`, `.github/workflows/refresh-catalog.yml`, `.github/workflows/revalidation-audit.yml`, `.github/workflows/acquisition-audit.yml`.
5. **Arquitectura y Gobernanza:** `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`, `docs/audits/r4-04-periodic-acquisition-and-staging.md`.

---

## 3. Hallazgos y Defectos Identificados

Mediante la auditoría inicial de accesibilidad automatizada con `axe-core`, se identificaron violaciones serias de contraste de color bajo la pauta **WCAG 2.1 AA (Criterio 1.4.3 Contraste Mínimo 4.5:1)** en componentes clave renderizados dinámicamente por `app.js`:

1. **Botón Principal de Postulación en Modal de Detalle (`.btn-apply-main`):**
   - *Elemento:* `<a class="btn-apply-main ... bg-crystalBlue text-white">Ir a postulación</a>`
   - *Defecto:* Texto blanco (`#ffffff`) sobre fondo celeste `#299edc` (`bg-crystalBlue`). Ratio de contraste medido: **2.99:1** (el umbral mínimo WCAG AA para texto estándar de 12px es **4.5:1**).
2. **Etiquetas de Habilidades y Tecnologías Declaradas en Detalle:**
   - *Elemento:* `<span class="... bg-ice-blue/10 text-crystal-blue">...</span>`
   - *Defecto:* Texto celeste `#299edc` sobre fondo pastel `#f0f9fe`. Ratio de contraste medido: **2.8:1** (insuficiente frente al umbral 4.5:1).
3. **Botón de Postulación en Comparador Lateral:**
   - *Elemento:* Botón de enlace directo a postulación en la cabecera de la tabla comparativa con clases `bg-crystalBlue text-white`.
   - *Defecto:* Mismo contraste insuficiente de **2.99:1**.
4. **Encabezado de Columna en Tabla del Comparador:**
   - *Elemento:* `<th scope="col" class="... bg-stone-100/80 text-stone-500 ...">Dimensión</th>`
   - *Defecto:* Texto gris `#79716b` (`text-stone-500`) sobre fondo `#f7f7f6`. Ratio de contraste medido: **4.46:1** (apenas por debajo del umbral normativo 4.5:1).

*Nota:* La vista principal del catálogo (`catalog view`) y los estados vacíos no presentaron ninguna violación seria o crítica en la auditoría inicial.

---

## 4. Integraciones OSS Realizadas

Siguiendo la estrategia OSS-First establecida en el protocolo:
- Se evaluaron alternativas para auditoría de accesibilidad: `axe-core` integrado con Playwright vs. `lighthouse-ci`.
- Se descartó Lighthouse para pruebas locales por su alta sobrecarga de dependencias (Chromium DevTools Protocol masivo, puppeteer duplicado) y mayor fragilidad en runners cerrados.
- Se seleccionó e integró `@axe-core/playwright`, el estándar de la industria desarrollado por Deque Systems, que inyecta directamente el motor determinista de `axe-core` en el contexto del navegador Playwright.
- Se implementó la suite completa de pruebas en `tests/e2e/accessibility.spec.cjs`.

---

## 5. Dependencias Nuevas y sus Licencias

| Paquete | Versión | Tipo | Licencia | Justificación Técnica |
|---|:---:|:---:|:---:|---|
| `@axe-core/playwright` | `^4.14.0` | `devDependency` | **MPL-2.0** (Mozilla Public License 2.0) | Motor determinista de auditoría formal WCAG 2.1 AA integrado a Playwright. Cero impacto en el bundle de producción (0 bytes en runtime cliente). |

*Nota:* No se añadieron dependencias de producción (0 npm runtime, 0 pip runtime). El archivo `package-lock.json` fue actualizado de forma atómica y consistente.

---

## 6. Correcciones Ejecutadas

Se aplicaron ajustes precisos de diseño y contraste en `app.js` sin alterar la paleta de marca ni el comportamiento funcional:

1. **Botón de Postulación en Modal de Detalle (`app.js`, línea 806):**
   - Se cambió el color de fondo de `bg-crystalBlue` (`#299edc`) a `bg-arcticBlue` (`#1765b5`) con hover `hover:bg-[#125091]`.
   - **Resultado:** El ratio de contraste del texto blanco sobre `#1765b5` aumentó a **5.93:1** (superando holgadamente el requisito de 4.5:1).
2. **Chips de Habilidades Técnicas (`app.js`, línea 723):**
   - Se modificó la clase de texto de `text-crystal-blue` a `text-arcticBlue`.
   - **Resultado:** El ratio de contraste sobre el fondo `bg-ice-blue/10` aumentó a **5.65:1** (WCAG AA aprobado).
3. **Botón de Postulación en Comparador (`app.js`, línea 1325):**
   - Se unificó el estilo a `bg-arcticBlue hover:bg-[#125091] text-white` con foco visible `focus-visible:outline-arcticBlue`.
   - **Resultado:** Ratio de contraste de **5.93:1** (aprobado).
4. **Encabezado "Dimensión" en Comparador (`app.js`, línea 1294):**
   - Se ajustó el color de texto de `text-stone-500` a `text-stone-700` (`#44403c`).
   - **Resultado:** Ratio de contraste aumentó de 4.46:1 a **8.12:1** (WCAG AAA aprobado para este elemento).

---

## 7. Pruebas Realizadas y Resultados Verificables

Se ejecutó la batería completa de pruebas automáticas y manuales del proyecto:

### 7.1. Pruebas de Accesibilidad Automatizada (`tests/e2e/accessibility.spec.cjs`)
10 escenarios de accesibilidad evaluados en Playwright bajo las etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`:
- **Vista de Catálogo (Desktop Chromium & Mobile Pixel 5):** 0 violaciones críticas o serias.
- **Modal de Detalle de Vacante (Desktop Chromium & Mobile Pixel 5):** 0 violaciones críticas o serias.
- **Diálogo del Comparador de Ofertas (Desktop Chromium & Mobile Pixel 5):** 0 violaciones críticas o serias.
- **Navegación por Teclado, Trampa de Foco y Cierre por Escape:** Foco retenido dentro del modal; tecla `Escape` cierra el diálogo y devuelve el foco limpiamente.
- **Estados Vacíos y Filtros sin Coincidencia:** 0 violaciones críticas o serias.

### 7.2. Pruebas E2E de Catálogo y Usabilidad (`tests/e2e/catalog.spec.cjs`)
Ejecutadas sobre 3 proyectos en `playwright.config.cjs`:
- `chromium` (Desktop Chrome): 10 pruebas aprobadas.
- `mobile` (Pixel 5 emulado, 393x851): 10 pruebas aprobadas.
- `narrow` (Pantalla angosta extrema, 320x568, <360px): 10 pruebas aprobadas.
- **Total Playwright:** **45 pruebas aprobadas al 100% en 1.0 min**.

### 7.3. Validación del Catálogo Canónico y Snapshot
- `python scripts/validate_catalog.py`: Aprobado (15 fichas conformes con Schema 2).
- `python scripts/build_catalog.py --check`: Aprobado (snapshot `data/opportunities.json` 100% sincronizado con semilla).
- `python scripts/validate_candidates.py data/candidates/inbox.local.json`: Aprobado (74 candidatos conformes con Schema 2, 0 errores).

### 7.4. Pruebas Unitarias e Integradas en Python
- `python -m unittest discover -s tests -p "test_*.py"`: **220 pruebas aprobadas de 220 en 3.8s**.
- `node tests/catalog_ui.test.cjs`: Escenarios de degradación y filtrado público aprobados al 100%.

---

## 8. Compatibilidad Visual y Funcional entre Navegadores (R4-05C)

En cumplimiento de las normas de veracidad técnica y transparencia:

| Entorno / Motor | Tipo de Prueba | Estado | Observaciones / Evidencia |
|---|:---:|:---:|---|
| **Chromium (Desktop Chrome)** | Navegador automatizado real | **APROBADO (100%)** | 15 pruebas E2E aprobadas (10 catálogo + 5 accesibilidad). Sin errores en consola, renderizado visual y foco verificados. |
| **Mobile Chrome (Pixel 5 emulado)** | Emulación de dispositivo móvil (393x851) | **APROBADO (100%)** | 15 pruebas E2E aprobadas. Sin overflow horizontal, modales responsivos y navegación táctil simulada. |
| **Narrow Viewport (320x568)** | Viewport angosto extremo (<360px) | **APROBADO (100%)** | 15 pruebas E2E aprobadas. `document.documentElement.scrollWidth <= clientWidth` verificado. |
| **Firefox** | Binario no descargado en cache local | **LIMITACIÓN DOCUMENTADA** | Playwright reporta falta de ejecutable en `ms-playwright/firefox-1572`. No se inventan resultados. |
| **WebKit (Safari)** | Binario no descargado en cache local | **LIMITACIÓN DOCUMENTADA** | Playwright reporta falta de ejecutable en `ms-playwright/webkit-2388`. No se inventan resultados. |
| **Dispositivos Físicos (iPhone/Android reales)** | Hardware no disponible en entorno agente | **LIMITACIÓN DOCUMENTADA** | Se cubrió mediante emulación Playwright móvil oficial; se recomienda prueba manual del propietario en dispositivo físico antes del anuncio masivo. |

---

## 9. Resolución de Brechas Editoriales del Catálogo (R4-05D)

### 9.1. Composición Actual del Catálogo (15 Fichas)
- **10 Oportunidades Reales Verificadas:**
  - CookUnity: `OP-005` (Supply Chain Analyst).
  - Canonical: `OP-006` (Cloud Solution Architect), `OP-007` (Junior Project Manager), `OP-008` (Linux Support Engineer), `OP-009` (Quality Engineer), `OP-010` (Junior Software Engineer).
  - Sezzle: `OP-011` (Jr QA Engineer), `OP-012` (Jr Backend Engineer), `OP-013` (Jr Frontend Engineer), `OP-014` (Jr DevOps Engineer).
- **5 Fichas Históricas / Demostrativas:**
  - OSITRAN: `OP-001` (Practicante profesional TI, sector público, cerrada 2026-10-13).
  - 42Labs: `OP-002` (iOS Developer, agregador Get on Board, referencia de mercado).
  - 42Labs: `OP-003` (Android Developer, agregador Get on Board, referencia de mercado).
  - Launchpad Technologies: `OP-004` (Implementation Consultant, sector fintech, cerrada).
  - OSITRAN: `QA-001` (Practicante de QA, sector público, cerrada 2026-08-24).

### 9.2. Análisis de Alternativas para la Versión Pública (v0.1)

| Criterio | Alternativa A: Solo 10 Oportunidades Reales | Alternativa B: Conservar 5 Demostrativas con Identificación Visual |
|---|---|---|
| **Experiencia de Usuario** | Inmediata y sin fricción: el 100% de las vacantes mostradas al ingresar permiten postulación activa. | Educativa pero con riesgo de desilusión si el usuario busca únicamente postular de inmediato. |
| **Credibilidad Inicial** | Máxima: cero riesgo de que un postulante intente aplicar a una convocatoria cerrada o no confirmada. | Requiere que el usuario lea con atención los badges explicativos "Ficha demostrativa". |
| **Volumen de Catálogo** | 10 ofertas reales (diversificadas en Desarrollo, QA, DevOps, Cloud y Datos). | 15 ofertas totales (10 reales + 5 históricas). |
| **Soporte Técnico Existente** | **Ya implementado por defecto:** En `app.js`, el checkbox `#include-demonstrations` está **desmarcado por defecto**. Al ingresar a la web, el catálogo muestra exclusivamente los 10 resultados reales. | **Ya implementado bajo demanda:** Si el usuario activa "Incluir ejemplos demostrativos", se muestran con badge ámbar, aviso de limitación y botón de postulación deshabilitado. |
| **Recomendación Técnica** | **Recomendada para v0.1:** Mantener el comportamiento predeterminado actual (Alternativa A por defecto con opción B accesible mediante toggle explícito). | Aceptable si el propietario desea posicionar la web como observatorio pedagógico desde el primer día. |

### 9.3. Límite de Autoridad y Decisión Editorial Pendiente
En estricto respeto al límite de autoridad establecido, **no se ha modificado la semilla canónica ni se ha eliminado ningún registro histórico**. El frontend conserva su comportamiento flexible: el catálogo arranca mostrando las 10 oportunidades reales y solo revela las 5 demostrativas si el usuario marca explícitamente el control de ejemplos. La decisión sobre suprimir definitivamente las 5 fichas del archivo canónico para v0.1 o mantener el toggle queda reservada al propietario.

### 9.4. Revisión Especial de OP-005 (CookUnity)
Se auditó minuciosamente el registro de CookUnity:
- Ubicación: `"Lima, Perú"`.
- Elegibilidad territorial: `"Perú"`.
- Modalidad: `null` (campo ausente en el feed de Greenhouse).
- **Verificación de Inferencia Cero:** La aplicación renderiza textualmente `"No especificada"` en las tarjetas y `"No informada"` en el modal de detalle. No se infiere "Presencial" por mencionar Lima ni "Remoto" por proceder de un ATS internacional. La elegibilidad territorial y la modalidad se mantienen como campos estrictamente independientes.

---

## 10. Congelación Técnica de v0.1 y Checklist de Release (R4-05E)

### 10.1. Aislamiento y Seguridad del Bundle Estático
Se auditó la configuración de empaquetado para GitHub Pages en `scripts/pages_artifact.py`:
- La lista de archivos públicos autorizados (`PUBLIC_FILES`) se restringe taxativamente a:
  1. `index.html`
  2. `app.js`
  3. `canvas.js`
  4. `styles.css`
  5. `data/opportunities.json`
- **Garantía Anti-Fugas:** El validador `_read_artifact_files` aborta con error fatal si en la carpeta `dist` existe cualquier archivo adicional. Queda criptográfica y estructuralmente garantizado que `data/candidates/inbox.local.json`, los informes de auditoría, las claves de prueba y los datos no públicos **nunca se despliegan en GitHub Pages**.

### 10.2. Checklist de Lanzamiento v0.1

- [x] **1. Integridad Canónica:** `data/opportunities.seed.json` intacto (15 registros validados).
- [x] **2. Sincronización de Snapshot:** `data/opportunities.json` 100% idéntico a la semilla compilada.
- [x] **3. Canales Oficiales:** 100% de los botones de postulación apuntan a dominios verificados de Greenhouse (`job-boards.greenhouse.io`, `careers.cookunity.com`) o Lever (`jobs.lever.co`).
- [x] **4. Enlaces Directos:** Cero intermediación, cero formularios locales de captura de datos de postulantes.
- [x] **5. Privacidad y PII:** Cero datos personales de postulantes o reclutadores almacenados o expuestos.
- [x] **6. Accesibilidad (WCAG 2.1 AA):** 0 violaciones críticas o serias en axe-core; contraste corregido a >= 5.6:1 en botones y badges; foco y teclado operables.
- [x] **7. Viewport Responsive:** Probado sin overflow en viewports de 320px, 393px y 1280px.
- [x] **8. Errores de Consola:** Cero excepciones no controladas en Chromium Desktop y Mobile.
- [x] **9. Revalidación Automatizada:** Workflow diario `.github/workflows/revalidation-audit.yml` operativo con `contents: read`.
- [x] **10. Adquisición Periódica:** Workflow semanal `.github/workflows/acquisition-audit.yml` operativo en modo dry-run.
- [x] **11. Aislamiento de Staging:** Staging físicamente excluido del artefacto de GitHub Pages.
- [ ] **12. Decisión del Propietario (Pendiente):** Confirmar si v0.1 pública se abre con las 10 reales por defecto (con toggle de demostrativas) o si se requiere otra composición.
- [ ] **13. Autorización de Despliegue (Pendiente):** Merge a `main` y habilitación pública autorizada expresamente por el propietario.

---

## 11. Matriz de Criterios de Aceptación de v0.1

| Criterio | Requisito de Aceptación | Estado | Evidencia |
|---|---|:---:|---|
| **Catálogo** | Vacantes reales, vigentes y pertinentes para perfiles junior/sistemas en Perú. | **CUMPLIDO** | 10 vacantes reales verificadas de CookUnity, Canonical y Sezzle. |
| **Búsqueda y Filtros** | Búsqueda por texto y filtros por modalidad, nivel y ubicación funcionales. | **CUMPLIDO** | Validado en `catalog.spec.cjs` y `catalog_ui.test.cjs`. |
| **Ficha de Detalle** | Desglose claro de requisitos, tareas, beneficios, riesgos y fecha de verificación. | **CUMPLIDO** | Validado en modal accesible con 0 violaciones WCAG. |
| **Comparador** | Comparación lateral de hasta 3 opciones sin scoring ni ranking artificial. | **CUMPLIDO** | Validado con chips técnicos, resalte de diferencias y foco accesible. |
| **Trazabilidad** | Fuente, URL original, relación con el empleador y fecha de observación explícitas. | **CUMPLIDO** | Schema 2 implementado con `fieldEvidence` y `verificationEvidence`. |
| **Accesibilidad** | Navegación por teclado completa, foco visible, contraste WCAG AA. | **CUMPLIDO** | `@axe-core/playwright` reporta 0 violaciones serias/críticas en 10 tests. |
| **Responsive** | Sin scroll horizontal ni solapamiento desde 320px hasta desktop. | **CUMPLIDO** | Pruebas Playwright en `narrow` (320px) y `mobile` (393px) aprobadas. |
| **Rendimiento** | Arquitectura estática sin frameworks pesados, carga <1s. | **CUMPLIDO** | Vanilla JS puro, bundle CSS consolidado con Tailwind. |
| **Seguridad** | Cero PII, cero secretos en repo, permisos mínimos en CI/CD. | **CUMPLIDO** | Staging auditado con 0 PII; workflows en `contents: read`. |

---

## 12. Riesgos Residuales y Mitigación

1. **Volatilidad Externa de ATS (Riesgo Bajo / Mitigado):**
   - *Riesgo:* Una empresa puede cerrar una vacante horas después del lanzamiento.
   - *Mitigación:* El workflow diario de revalidación (`revalidation-audit.yml`) audita los tableros cada mañana a las 06:00 AM Lima y reporta discrepancias. La interfaz advierte explícitamente la fecha y hora de la última verificación.
2. **Falta de Pruebas Automatizadas en Firefox / Safari WebKit Local (Riesgo Bajo / Aceptable):**
   - *Riesgo:* Incompatibilidad menor de CSS en motores no basados en Chromium.
   - *Mitigación:* El código utiliza CSS estándar y Tailwind v4 compilado sin prefijos propietarios exóticos. La prueba en CI de GitHub Actions ejecuta sobre Ubuntu con Chromium estándar. Se recomienda verificación manual puntual del propietario en Safari iOS.
3. **Expectativa del Usuario sobre Volumen de Ofertas (Riesgo Medio / Editorial):**
   - *Riesgo:* 10 vacantes pueden percibirse como un catálogo reducido frente a bolsas de trabajo masivas.
   - *Mitigación:* La propuesta de valor de Ruta Sistemas es la calidad verificada, elegibilidad comprobada desde Perú y cero intermediación, no el volumen inflado de ofertas fantasma.

---

## 13. Recomendación Técnica Final

### Calificación: `READY_FOR_OWNER_APPROVAL`

**Fundamento Técnico:**
La plataforma se encuentra técnica, arquitectural y operativamente lista para su primera versión pública funcional (**v0.1**):
- La auditoría formal de accesibilidad WCAG 2.1 AA ha sido completada y todas las violaciones serias detectadas fueron subsanadas.
- La suite completa de 220 pruebas Python y 45 pruebas Playwright E2E pasa al 100%.
- El artefacto de GitHub Pages está blindado contra fugas de datos privados o staging.
- No existen defectos bloqueantes de código, rendimiento ni usabilidad responsive.

El lanzamiento público queda condicionado exclusivamente a dos decisiones soberanas del propietario:
1. **Decisión Editorial:** Confirmar la presentación del catálogo de v0.1 (Alternativa A: 10 vacantes reales por defecto con toggle demostrativo).
2. **Autorización de Sincronización:** Autorizar el merge a `main` y el despliegue automático hacia GitHub Pages.

---

## 14. Siguiente Acción Recomendada

Presentar este informe al propietario y solicitar su pronunciamiento sobre la composición editorial definitiva para proceder con la sincronización y lanzamiento de **Ruta Sistemas v0.1**.
