# Cuaderno de Campo y Seguimiento de Reclutamiento R3-02
**Operacionalización y Control de Sesiones de Validación con Participantes Reales**

- **Fase:** R3 — Validación del producto (Subfase R3-02)
- **Fecha de apertura:** 2026-11-18
- **Estado actual del trabajo de campo:** `NOT_STARTED` (Cero sesiones reales ejecutadas; reclutamiento en preparación)
- **Meta de participantes:** 5 a 8 participantes reales
- **Entorno de prueba:** Producción oficial en vivo ([https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/))

---

## 1. Objetivo y Criterios de Calidad del Trabajo de Campo

Este documento sirve como bitácora y guía operativa para el equipo humano de investigación de Ruta Sistemas encargado de convocar, coordinar, moderar y registrar las sesiones de prueba con usuarios.

> [!IMPORTANT]
> **Principio de Veracidad Científica y Gobernanza de Datos:**  
> Ninguna sesión se considerará iniciada o ejecutada sin la participación efectiva de una persona real que cumpla los criterios de inclusión y haya otorgado su consentimiento informado. Los datos simulados o ficticios están estrictamente prohibidos en el repositorio.

---

## 2. Cuadro de Control y Cuotas de Reclutamiento

Para garantizar una evaluación formativa rigurosa, la muestra de 5 a 8 participantes se divide en tres segmentos con cuotas obligatorias:

| Perfil | Código | Segmento Objetivo | Cuota Meta | Estado de Reclutamiento | Sesiones Completadas |
|---|---|---|:---:|:---:|:---:|
| **Estudiantes** | `P-EST` | Estudiantes de 8vo a 10mo ciclo de Ingeniería de Sistemas, Software o Computación en universidades peruanas. | 2 a 3 | `PENDIENTE_CONVOCATORIA` | 0 |
| **Egresados** | `P-EGR` | Egresados o bachilleres recientes (últimos 12 meses) en búsqueda de su primera oportunidad profesional estable. | 2 a 3 | `PENDIENTE_CONVOCATORIA` | 0 |
| **Juniors** | `P-JUN` | Profesionales con 1 a 2 años de experiencia laboral inicial en áreas de TI, desarrollo o sistemas. | 1 a 2 | `PENDIENTE_CONVOCATORIA` | 0 |
| **TOTAL** | — | — | **5 a 8** | **EN ESPERA DE PARTICIPANTES** | **0** |

---

## 3. Matriz de Seguimiento Individual de Participantes

| ID | Perfil Asignado | Estado de Sesión | Fecha Programada | Moderador / Observador | QA Sesión | Archivo de Registro |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `P01` | `P-EST` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P01.md`](./sessions/P01.md) |
| `P02` | `P-EST` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P02.md`](./sessions/P02.md) |
| `P03` | `P-EST` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P03.md`](./sessions/P03.md) |
| `P04` | `P-EGR` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P04.md`](./sessions/P04.md) |
| `P05` | `P-EGR` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P05.md`](./sessions/P05.md) |
| `P06` | `P-EGR` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P06.md`](./sessions/P06.md) |
| `P07` | `P-JUN` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P07.md`](./sessions/P07.md) |
| `P08` | `P-JUN` | `PENDING_EXECUTION` | Por agendar | Por asignar | Pendiente | [`docs/research/sessions/P08.md`](./sessions/P08.md) |

---

## 4. Guía Operativa de Moderación: Observación de Fricciones Críticas

Durante la ejecución de los 5 escenarios (A–E) detallados en el protocolo ([`docs/research/r3-01-user-research-protocol-2026-11-18.md`](./r3-01-user-research-protocol-2026-11-18.md)), el moderador y observador deben prestar especial atención a las **6 fricciones heurísticas previas** detectadas en R3-01, sin inducir al usuario:

```
+--------+------------------------------------+---------------------------------------------------------------+
| ID     | Fricción Heurística Identificada   | Comportamiento y Señales a Observar en la Sesión              |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B01 | Inconsistencia de estado en        | En TAREA C: ¿Nota el participante la etiqueta superior verde  |
|        | tarjeta activa                     | "Activa · revisión reciente" y luego lee "Vigencia no         |
|        |                                    | confirmada" en el bloque central? ¿Expresa confusión sobre si  |
|        |                                    | la oferta está abierta o no?                                  |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B02 | Mensaje engañoso en búsqueda sin   | En TAREA A: Si el usuario busca un término sin coincidencia   |
|        | resultados                         | (ej. "python"), ¿cree que el catálogo general no tiene        |
|        |                                    | vacantes o entiende que se debe a su filtro de búsqueda?      |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B03 | Estados técnicos en inglés en      | En TAREA D: Al revisar la fila "Estado de verificación",       |
|        | tabla comparativa                  | ¿entiende "open · verified · active" o pregunta qué significan |
|        |                                    | esos términos de base de datos?                               |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B04 | Exposición de timestamp ISO 8601   | En TAREA C: Al leer el cuadro de verificación en el modal,    |
|        | crudo                              | ¿reacciona ante "2026-11-17T22:28:37-05:00" o le parece        |
|        |                                    | confuso / código de máquina?                                 |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B05 | Disonancia entre Hero y única      | En TAREA A: Al ver "Fullstack Dev" y "DevOps" en el Hero,    |
|        | vacante real                       | ¿se frustra o sorprende al ver que la única vacante real es   |
|        |                                    | "Supply Chain Analyst" (Sistemas empresariales)?             |
+--------+------------------------------------+---------------------------------------------------------------+
| UX-B06 | Baja visibilidad del switch de     | En TAREA D: ¿Encuentra por sí mismo el botón "Incluir         |
|        | ejemplos demostrativos             | ejemplos demostrativos" o se queda atascado sin saber cómo    |
|        |                                    | comparar dos vacantes? (Registrar si requirió ayuda).         |
+--------+------------------------------------+---------------------------------------------------------------+
```

---

## 5. Rúbrica de Control de Calidad (QA) para Cada Sesión

Antes de consolidar los resultados de una sesión en la matriz de hallazgos ([`docs/research/r3-01-findings-template-2026-11-18.md`](./r3-01-findings-template-2026-11-18.md)), el auditor de UX debe evaluar:

1. **Consentimiento y Privacidad (`PASS`/`FAIL`):**
   - Confirmación explícita de consentimiento registrada.
   - Ningún dato personal identificable (DNI, nombres, teléfonos, CVs) presente en el texto.
2. **Neutralidad de la Moderación (`PASS`/`FAIL`):**
   - El moderador no indicó las respuestas ni justificó el diseño de la web.
   - Si se brindó asistencia para desbloquear una tarea, fue consignada obligatoriamente como `SUCCESS_WITH_HELP` y documentada en la fila *Intervención del Moderador*.
3. **Completitud de Evidencia (`PASS`/`FAIL`):**
   - Métricas cuantitativas completas: Resultado (`SUCCESS_WITHOUT_HELP`, `SUCCESS_WITH_HELP`, `ABANDONED`, `NOT_EXECUTED`), Tiempo en minutos y segundos, Nivel de confianza (1 a 5).
   - Notas cualitativas y al menos 2 citas textuales directas en pensamiento en voz alta.
4. **Veredicto QA:**
   - `VALID`: Sesión completa y objetiva. Se suma al conteo oficial.
   - `INCOMPLETE`: Tareas omitidas sin justificación o datos incompletos. No se contabiliza.
   - `INVALID`: Sesión con inducción grave de respuestas o violación de anonimato. Descartada.

---

## 6. Procedimiento para el Equipo Humano tras Completar las Sesiones

1. **Reclutamiento y Moderación:** Conducir las sesiones utilizando el [Kit de Convocatoria y Consentimiento](./r3-02-recruitment-materials-kit-2026-11-18.md) y la [Guía de Moderación Paso a Paso](./r3-02-moderator-field-guide-2026-11-18.md) sobre la versión oficial de producción ([https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/)).
2. **Volcado Inmediato:** Volcar las notas y citas de cada entrevista en su archivo correspondiente: `docs/research/sessions/P01.md` a `P08.md`.
3. **Aplicación de QA:** Completar la Sección 6 de control de calidad en la plantilla individual y actualizar el estado de cada sesión en la tabla del apartado 3 (`VALID`, `INCOMPLETE` o `INVALID`).
4. **Desbloqueo de R3-03:** Cuando se alcance la cuota de al menos **5 sesiones válidas** cubriendo los 3 perfiles (`P-EST`, `P-EGR` y `P-JUN`):
   - Notificar al agente para proceder con el cierre de **R3-02** y apertura de **R3-03 (Análisis y Priorización de Hallazgos)**.
