# Auditoría Técnica de Preparación para la Validación con Usuarios R3-01
**Research Readiness & Product State Audit**

- **Fecha de auditoría:** 2026-11-18
- **Fase:** R3 — Validación del producto (Subfase R3-01)
- **Estado de Preparación:** `READY_FOR_RESEARCH`
- **Resultado del Bloque R3-01:** `DONE` (Investigación y protocolo preparados; validación empírica en curso)
- **Compromiso / Versión de Producción:** Commit `28b7a9e` en rama `main`
- **URL Pública Auditada:** https://blueisazul.github.io/WebRutaSistemas/

---

## 1. Objetivo de la Auditoría

Verificar que la versión de producción y el entorno local de Ruta Sistemas cumplan con todos los requisitos técnicos, de usabilidad y de gobernanza para iniciar las sesiones de prueba con usuarios reales sin riesgos de inestabilidad, bloqueos en los flujos principales ni vulneración de la privacidad de los participantes.

---

## 2. Verificación de Flujos Críticos en Producción

Se auditaron y ejecutaron manualmente y mediante pruebas automatizadas los 10 flujos indispensables para la investigación:

| # | Flujo Auditado | Estado | Evidencia y Comportamiento Observado |
|---|---|---|---|
| **1** | Carga inicial del catálogo | **Aprobado** | Petición local a `./data/opportunities.json` responde HTTP 200. Muestra 1 resultado activo real (`OP-005`: CookUnity) y contadores sincronizados. |
| **2** | Búsqueda y filtros | **Aprobado** | Reactividad fluida con debounce de 120 ms. Atajo `/` enfoca la caja de búsqueda. Filtros de facetas (modalidad, tipo, sector, nivel, familia) operativos. |
| **3** | Visualización de oportunidad real | **Aprobado** | `OP-005` renderiza como tarjeta principal con etiquetas `Activa · revisión reciente`, `Sistemas empresariales`, `Profesional / junior` y compensación `No publicado`. |
| **4** | Visualización de ejemplos demostrativos | **Aprobado** | El toggle *"Incluir ejemplos demostrativos"* amplía la lista a 6 registros (`OP-001`..`OP-005`, `QA-001`), claramente identificados como fichas de prueba. |
| **5** | Detalle de oportunidad (`<dialog>`) | **Aprobado** | Apertura fluida al pulsar título o botón *"Ver evaluación ↗"*. Despliega cuadro de verificación, matriz de datos, 7 tarjetas de señales, tareas, requisitos y 21 enlaces de procedencia. |
| **6** | Comparador local | **Aprobado** | Selección de hasta 2 fichas mediante botón *"Añadir a comparación"*. Barra inferior `#compare-panel` emerge y habilita el botón *"Comparar"*. Modal con tabla dimensional sin ranking ni ganador universal. |
| **7** | Interpretación de estados | **Aprobado** | Distingue visualmente `Activa · revisión reciente` de `Ficha demostrativa` y `Referencia histórica`. Fricción menor identificada en texto `Vigencia no confirmada` documentada en línea base. |
| **8** | Enlace de postulación | **Aprobado** | Botón *"Ir a postulación ↗"* habilitado exclusivamente para `OP-005` apuntando a `https://job-boards.greenhouse.io/cookunity/jobs/8039990003` con `target="_blank"` y `rel="noopener noreferrer"`. En ejemplos permanece inactivo. |
| **9** | Diseño responsive | **Aprobado** | Verificado en Chromium de escritorio y emulación móvil (Pixel 5, 393x851 px). Sin desbordamientos horizontales (`scrollWidth <= clientWidth`), modales adaptados y botones táctiles accesibles. |
| **10** | Accesibilidad básica y teclado | **Aprobado** | Navegación por foco secuencial con `Tab`. Apertura de detalle con `Enter` y `Espacio` en títulos (`role="button"`, `tabindex="0"`). Cierre nativo con `Escape`. Etiquetas `aria-live="polite"` en contadores. |

---

## 3. Línea Base Técnica y Ejecución de Pruebas

Se ejecutó la suite completa de pruebas locales para certificar la integridad del repositorio:

```powershell
# 1. Consistencia de Catálogo Canónico y Snapshot Publicado
python scripts/build_catalog.py --check
# Resultado: Catálogo válido: 6 registros; snapshot coincide con la fuente canónica.

# 2. Validación Estricta de Calidad Schema 2
python scripts/validate_catalog.py
# Resultado: Válido: 6 fichas; modo=publicación no vacía; fecha Lima=2026-11-17. (0 errores).

# 3. Validación de Bandeja Local de Candidatos (Staging)
python scripts/validate_candidates.py data/candidates/inbox.local.json
# Resultado: Bandeja local válida: 8 candidatos; no se modificó ni se publicó el catálogo.

# 4. Pruebas Unitarias de Python (Ingesta, Calidad, Servidor, Evidencias, CLI)
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 3.125s - OK. (0 fallos, 0 errores).

# 5. Sintaxis y Contratos de Frontend
node --check app.js
node tests/catalog_ui.test.cjs
# Resultado: OK: public catalog filtering scenarios passed.
#            OK: root/Pages paths and failed-catalog degradation scenarios passed.

# 6. Pruebas End-to-End de Interfaz con Playwright
npx playwright test
# Resultado: 8 passed (Chromium desktop y Pixel 5 mobile).

# 7. Formato y Espaciado en Git
git diff --check
# Resultado: Sin conflictos ni espacios espurios.
```

---

## 4. Auditoría de Entregables de Investigación R3-01

Se constata la existencia, completitud y conformidad documental de los entregables preparados para la fase de investigación:

1. **Línea Base UX y Fricciones Heurísticas:**  
   [docs/research/r3-01-ux-baseline-2026-11-18.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-ux-baseline-2026-11-18.md)  
   *Contenido:* Diagnóstico de los 5 flujos del MVP, matriz de 6 fricciones heurísticas previas (`UX-B01` a `UX-B06`), rendimiento estático y cero scripts de terceros.

2. **Protocolo de Pruebas de Usabilidad con Usuarios:**  
   [docs/research/r3-01-user-research-protocol-2026-11-18.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-user-research-protocol-2026-11-18.md)  
   *Contenido:* 5 preguntas rectoras, perfiles de inclusión (estudiantes, egresados, juniors), limitaciones de muestra (5 a 8 participantes), guion de moderación neutral, consentimiento informado, 5 escenarios basados en situaciones reales (A, B, C, D, E), métricas observables y taxonomía de 6 categorías.

3. **Plantilla de Registro de Sesión Individual:**  
   [docs/research/r3-01-usability-test-template-2026-11-18.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-usability-test-template-2026-11-18.md)  
   *Contenido:* Formato disociado (código `P01..P08`), métricas por tarea (éxito, tiempo, confianza 1-5), registro de pensamiento en voz alta, fricciones observadas, debriefing y clasificación de incidentes.

4. **Matriz y Repositorio de Hallazgos Consolidados:**  
   [docs/research/r3-01-findings-template-2026-11-18.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-findings-template-2026-11-18.md)  
   *Contenido:* Método de agregación de datos, matriz de Severidad × Frecuencia × Impacto, reglas de priorización (P0 a P4), estructura uniforme para `HAL-R3-XX` y filtro crítico contra sobre-ingeniería en solicitudes de usuarios.

---

## 5. Criterios de Entrada a las Sesiones con Usuarios (Entry Criteria)

Para proceder al reclutamiento y ejecución de las sesiones en **R3-02**, deben cumplirse las siguientes condiciones operativas:

- [x] **Disponibilidad del MVP:** Desplegado de forma pública y estable en https://blueisazul.github.io/WebRutaSistemas/.
- [x] **Protocolo Operativo:** Guion neutral, consignas y preguntas de debriefing formalizadas.
- [x] **Herramientas de Registro:** Plantillas individuales (`docs/research/r3-01-usability-test-template-2026-11-18.md`) y matriz consolidadora listas.
- [x] **Gobernanza de Privacidad:** Mecanismo estricto de disociación de identidad (`P-01`..`P-08`) sin recolección de CVs ni datos sensibles.
- [ ] **Reclutamiento de Participantes:** Identificar y agendar entre 5 y 8 personas reales distribuidas en:
  - 2 a 3 estudiantes de 8vo a 10mo ciclo de Ingeniería de Sistemas.
  - 2 a 3 egresados o bachilleres con menos de 1 año de graduación.
  - 1 a 2 profesionales junior con 1 a 2 años de experiencia laboral.

---

## 6. Dictamen de Auditoría y Próximos Pasos

### 6.1 Dictamen
**`R3-01 CONCLUIDO SATISFACTORIAMENTE (DONE)`**  
El entorno técnico, la interfaz de producción y el marco metodológico de investigación se encuentran 100% listos. No existen impedimentos técnicos para iniciar la validación empírica.

### 6.2 Próximo Paso Recomendado
Proceder con el bloque **R3-02 (Ejecución de Sesiones de Usabilidad y Validación con Participantes Reales)**:
- Reclutar los 5 a 8 participantes según los criterios de inclusión.
- Ejecutar las sesiones siguiendo estrictamente el protocolo neutral sin orientar las acciones del usuario.
- Registrar las evidencias en plantillas individuales para su posterior síntesis en **R3-03**.
