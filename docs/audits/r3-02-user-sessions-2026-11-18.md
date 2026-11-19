# Auditoría de Ejecución y Estado del Trabajo de Campo R3-02
**Informe de Sesiones de Usabilidad y Validación con Participantes Reales**

- **Fecha de auditoría:** 2026-11-18
- **Fase del Proyecto:** R3 — Validación del producto (Subfase R3-02)
- **Estado Oficial del Bloque:** **`NOT_STARTED`** *(Reclutamiento en preparación; cero sesiones reales ejecutadas)*
- **Compromiso / Versión evaluada:** Producción oficial en vivo (commit `28b7a9e`, [https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/))
- **Rama de trabajo local:** `integration/r1-02c`

---

## 1. Declaración Deontológica y Estado del Bloque

En estricta observancia de los mandatos rectores de gobernanza de **Ruta Sistemas** y las instrucciones del bloque R3-02:

> [!CAUTION]
> **Prohibición Absoluta de Fabricación de Evidencia:**  
> Los agentes automatizados e integrantes de ingeniería **no deben inventar participantes, simular respuestas, crear consentimientos ficticios ni completar métricas de usabilidad con valores supuestos**. La validación de producto es un proceso empírico que exige personas reales interactuando con la interfaz.

Dado que a la fecha de este informe el equipo humano de moderación no ha ejecutado ni volcado aún sesiones presenciales o remotas con participantes reales en el repositorio, el estado del bloque R3-02 se declara formalmente como:

### **`ESTADO: NOT_STARTED`**

*(Operacionalmente preparado: infraestructura documental, plantillas de captura, matriz de seguimiento y rúbricas de QA completadas).*

---

## 2. Participantes Confirmados y Cuotas por Perfil

- **Participantes confirmados a la fecha:** `0`
- **Sesiones válidas registradas:** `0`
- **Sesiones inválidas o incompletas:** `0`

### Distribución de Cuotas Exigidas para Cierre:
| Perfil | Código | Descripción del Segmento | Cuota Mínima | Cuota Máxima | Registradas a la fecha |
|---|---|---|:---:|:---:|:---:|
| **Estudiantes** | `P-EST` | Estudiantes de 8vo a 10mo ciclo de Ingeniería de Sistemas / Software en Perú. | 2 | 3 | 0 |
| **Egresados** | `P-EGR` | Egresados o bachilleres recientes (últimos 12 meses) sin empleo formal. | 2 | 3 | 0 |
| **Juniors** | `P-JUN` | Profesionales con 1 a 2 años de experiencia laboral inicial en TI. | 1 | 2 | 0 |
| **TOTAL** | — | — | **5** | **8** | **0** |

---

## 3. Cobertura de Escenarios y Estado Operativo

El paquete de trabajo de campo se encuentra 100% articulado sobre los 5 escenarios diseñados en R3-01:

| Escenario | Objetivo Específico | Estado Operativo | Registro Asignado |
|---|---|---|---|
| **A. Pertinencia** | Búsqueda libre y evaluación de adecuación del puesto al perfil de Sistemas. | Preparado en protocolo | Tarea A en plantillas `P01` a `P08` |
| **B. Requisitos** | Análisis de CookUnity (*Supply Chain Analyst*): SQL, ERP, 1+ años de experiencia y empleo formal vs práctica. | Preparado en protocolo | Tarea B en plantillas `P01` a `P08` |
| **C. Estados** | Comprensión de publicación activa, verificación de empleador, caducidad por TTL y modalidad no informada. | Preparado en protocolo | Tarea C en plantillas `P01` a `P08` |
| **D. Comparación** | Opt-in de ejemplos demostrativos, tabla comparativa de 14 atributos y ausencia de ganador universal. | Preparado en protocolo | Tarea D en plantillas `P01` a `P08` |
| **E. Decisión** | Localización de enlace de postulación oficial, no intermediación de CVs y datos faltantes antes de postular. | Preparado en protocolo | Tarea E en plantillas `P01` a `P08` |

---

## 4. Fricciones Heurísticas Bajo Observación Empírica

Se establecieron como focos de observación obligatoria las 6 fricciones identificadas durante la auditoría de línea base R3-01. **No se realizarán modificaciones en el código antes de obtener la evidencia de usuario**:

1. **`UX-B01` (Inconsistencia de estado en tarjeta activa):** Verificar si el usuario detecta el choque entre la etiqueta *"Activa · revisión reciente"* y el texto *"Vigencia no confirmada"* en `job-fit`.
2. **`UX-B02` (Mensaje engañoso en búsqueda sin resultados):** Verificar si al buscar un término inexistente (ej. "python") el texto *"No hay oportunidades verificadas disponibles"* induce a creer que el catálogo global está vacío.
3. **`UX-B03` (Estados técnicos en inglés en comparador):** Verificar la incomprensión de los enums `open · verified · active` y `unknown · unverified · unconfirmed`.
4. **`UX-B04` (Timestamp ISO 8601 crudo):** Evaluar el impacto de legibilidad de `2026-11-17T22:28:37-05:00` en el modal de verificación.
5. **`UX-B05` (Disonancia entre Hero y única vacante real):** Observar si la promesa visual de "Fullstack Dev" y "Data & DevOps" defrauda las expectativas al encontrar únicamente una vacante de analítica logística.
6. **`UX-B06` (Baja visibilidad del toggle de ejemplos):** Medir cuántos participantes requieren ayuda del facilitador para activar *"Incluir ejemplos demostrativos"* al intentar comparar.

---

## 5. Control de Calidad y Prevención de Sesgos

Se formalizó la rúbrica de QA en [`docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md):
- **Cero datos personales:** Ningún CV, teléfono, DNI o nombre completo será admitido en las carpetas públicas de `docs/research/sessions/`.
- **Criterio de inducción:** Cualquier sesión donde el facilitador explique cómo resolver la tarea o justifique la plataforma será catalogada como `INVALID` o degradada a *"Éxito con ayuda"*.
- **Completitud métrica:** Se exige registro de tiempo con cronómetro, nivel de confianza (1 a 5) y al menos dos citas textuales directas anonimizadas por sesión.

---

## 6. Limitaciones Metodológicas de la Muestra

- La muestra de 5 a 8 participantes permite descubrir hasta el ~80-85% de los problemas cualitativos de usabilidad según la literatura estándar de HCI.
- Los hallazgos resultantes **no serán generalizables estadísticamente** a la totalidad de egresados de Ingeniería de Sistemas del Perú.
- El propósito de R3 es formativo: corregir fricciones graves y validar la comprensión del modelo editorial, no emitir métricas cuantitativas concluyentes de mercado.

---

## 7. Inventario de Entregables Operativos Generados

1. **Directorio y Repositorio de Sesiones:** [`docs/research/sessions/`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/)
   - [`README.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/README.md) *(Normas de gobernanza, privacidad y tabla de control).*
   - [`P01.md` a `P08.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/) *(8 plantillas individuales en blanco listas para captura con enum estandarizado y Sección 6 de QA).*
2. **Cuaderno de Campo y Reclutamiento:** [`docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md)
   - Embudo de convocatoria, perfiles, guía de observación de las 6 fricciones y rúbrica de control de calidad.
3. **Kit de Materiales de Convocatoria y Consentimiento:** [`docs/research/r3-02-recruitment-materials-kit-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-recruitment-materials-kit-2026-11-18.md)
   - Plantillas oficiales de invitación por canal (WhatsApp/correo/LinkedIn) y consentimiento informado.
4. **Guía de Moderación y Campo Paso a Paso:** [`docs/research/r3-02-moderator-field-guide-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-moderator-field-guide-2026-11-18.md)
   - Protocolo 45 min, guiones de observación para escenarios A–E y reglas de oro anti-inducción.
5. **Auditoría de Preparación Operativa:** [`docs/audits/r3-02-fieldwork-readiness-review-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-02-fieldwork-readiness-review-2026-11-18.md)
   - Dictamen A (Preparación Operativa Confirmada) y verificación de integridad documental.
6. **Informe de Auditoría de Campo y Sesiones:** [`docs/audits/r3-02-user-sessions-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-02-user-sessions-2026-11-18.md) *(Este documento).*

---

## 8. Tareas Pendientes y Requisitos para Avanzar a R3-03

Para que R3-02 pueda cerrarse con veredicto `DONE` y dar paso a **R3-03 (Análisis y Priorización de Hallazgos)**, el equipo humano debe completar las siguientes acciones de campo:

1. [ ] Difundir la convocatoria en grupos universitarios y comunidades técnicas de Sistemas en Perú.
2. [ ] Agendar y confirmar entre 5 y 8 participantes que cumplan los criterios de inclusión.
3. [ ] Ejecutar las sesiones siguiendo estrictamente el protocolo de moderación no directiva sobre el portal en vivo.
4. [ ] Volcar las notas y citas en los archivos correspondientes `docs/research/sessions/P01.md` a `P08.md`.
5. [ ] Aplicar la rúbrica de QA y verificar que existan al menos 5 sesiones con veredicto `VALID`.
6. [ ] Actualizar la matriz de hallazgos en [`docs/research/r3-01-findings-template-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-findings-template-2026-11-18.md).

Una vez cumplidos estos puntos, se declarará `R3-02 DONE` y se autorizará la apertura del análisis y priorización en **R3-03**.
