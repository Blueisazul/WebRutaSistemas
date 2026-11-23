# Registro y Análisis de Respuestas a Tareas A–E — R3-02-INTERNAL-FEEDBACK-02
## Análisis Estructurado de Pruebas Internas de Usabilidad de Ruta Sistemas

- **Identificador:** `R3-02-INTERNAL-FEEDBACK-02`
- **Fecha de registro:** 2026-11-22
- **Tipo de intervención:** `[INVESTIGACIÓN_CUALITATIVA]` + `[RECONCILIACIÓN_DE_EVIDENCIA]` + `[AUDITORÍA_UX]`
- **Estado documental:** **`RECONCILED_QUALITATIVE_EVIDENCE`** (Evidencia cualitativa interna reconciliada; sesiones formales pendientes)
- **Versión evaluada:** Rama `integration/r1-02c` (HEAD `b27e418fb80f1e2c9d406fbf135b395ab6c4705d` con working tree local consolidado)
- **Entorno de ejecución:** Servidor local de desarrollo (`http://127.0.0.1:4173/`, `python server.py`)
- **Responsables de análisis:** Principal Product Engineer, UX Research Analyst & Technical Auditor

---

## 1. Contexto, Procedencia y Diferenciación Metodológica

El propietario de Ruta Sistemas comunicó un segundo corte de resultados tras las pruebas realizadas en el entorno local junto a sus compañeros de carrera (Ingeniería de Sistemas). A diferencia de los bloques previos (`R3-02-OWNER-FEEDBACK-01` y `R3-02-INTERNAL-FEEDBACK-01`), donde únicamente se transmitió una valoración general y sintética de satisfacción, en este corte se proporcionó un **conjunto estructurado de respuestas alineadas directamente con los cinco escenarios y tareas (A–E)** establecidos en el protocolo rector [`docs/research/r3-01-user-research-protocol-2026-11-18.md`](./r3-01-user-research-protocol-2026-11-18.md).

> [!IMPORTANT]
> **Deslinde Metodológico y Deontológico:**  
> 1. Este registro documenta **evidencia cualitativa interna suministrada por el propietario**. Representa la exploración informal de un usuario o grupo de usuarios cercanos en condiciones no moderadas.
> 2. **No constituye una sesión formal de usabilidad auditada.** No se han registrado datos de consentimiento informado individual, no hubo moderación neutral no directiva en tiempo real, se desconoce el número exacto y segmentación de los evaluadores (`P-EST`, `P-EGR`, `P-JUN`), y no se cronometraron los tiempos de tarea ni tasas de éxito estandarizadas.
> 3. Las plantillas formales [`P01.md`](./sessions/P01.md) a [`P08.md`](./sessions/P08.md) **permanecen estrictamente intactas en estado `PENDING_EXECUTION`**. Ningún campo ha sido completado con datos asumidos.

---

## 2. Registro Fiel y Análisis de Respuestas por Escenario (Tareas A–E)

A continuación se desglosan las respuestas comunicadas, separando los hechos observados, las declaraciones o paráfrasis textuales, las interpretaciones del usuario, las limitaciones de la evidencia y los hallazgos críticos de usabilidad:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAREA A: BÚSQUEDA Y PERTINENCIA DE LA OPORTUNIDAD                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Consigna del protocolo: Explorar catálogo y explicar adecuación a Ingeniería de Sistemas.         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Hechos comunicados:** La respuesta se centró en la vacante de **Supply Chain Analyst** en **CookUnity** (Lima, Perú).
- **Paráfrasis fiel de la respuesta:** El evaluador identificó que el puesto se relaciona directamente con Ingeniería de Sistemas debido al uso intensivo de SQL (consultas JOIN y agregaciones), análisis de datos, Google Sheets avanzado y sistemas de planificación de recursos empresariales (ERP/MRP). Destacó que el rol permite aplicar tecnologías de información a la optimización de procesos operativos y de negocio, sirviendo como puente para desarrollar experiencia profesional en análisis de datos y sistemas de información.
- **Interpretación analítica:** El usuario demuestra capacidad de abstracción para entender que la Ingeniería de Sistemas trasciende el desarrollo de software puro, abarcando análisis de sistemas de información empresarial y datos. Esto valida positivamente la presencia de vacantes interdisciplinarias en el catálogo.
- **Limitaciones de la evidencia:** No se registró si el evaluador utilizó la barra de búsqueda, atajos de teclado (`/`), filtros de familia o scroll libre para llegar a la vacante, ni si revisó las oportunidades de Canonical incorporadas recientemente.

---

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAREA B: EVALUACIÓN CRÍTICA DE REQUISITOS Y NATURALEZA DEL ROL                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Consigna del protocolo: Identificar requisitos técnicos, experiencia y si es práctica o empleo.  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Hechos comunicados:** Se desglosaron fielmente los requisitos explícitos de la ficha de CookUnity.
- **Paráfrasis fiel de la respuesta:**
  - *Conocimientos y herramientas identificadas:* SQL (JOINs, funciones de agregación), Google Sheets a nivel avanzado, sistemas ERP/MRP, análisis de datos operativos, inglés profesional.
  - *Experiencia exigida:* Mínimo 1 año de experiencia previa en áreas analíticas o de cadena de suministro.
  - *Naturaleza del rol:* Concluyó correctamente que se trata de un **empleo formal a tiempo completo** y **no** de una práctica preprofesional.
  - *Formación académica:* Identificó formación en Ingeniería de Sistemas, Industrial o carreras afines.
  - *Autoevaluación del evaluador:* Manifestó poseer conocimientos teóricos/académicos en bases de datos y sistemas de información, pero reconoció que debería reforzar o comprobar su dominio práctico en SQL avanzado, Sheets avanzado, ERP/MRP, fluidez en inglés y acreditar el año de experiencia previa.
- **Interpretación analítica:** La ficha de oportunidad y la estructuración de requisitos en viñetas facilitaron una lectura nítida de los requerimientos excluyentes.
- **Tratamiento metodológico:** La autoevaluación expresada por el evaluador se registra como una **percepción subjetiva de adecuación personal**, no como una comprobación técnica objetiva de sus competencias.

---

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAREA C: INTERPRETACIÓN DE ESTADOS, VERIFICACIÓN Y MODALIDAD                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Consigna del protocolo: Interpretar etiquetas de estado, fecha de revisión y modalidad laboral.  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Hechos comunicados:** Comprensión de estados temporales y metadatos de procedencia.
- **Paráfrasis fiel de la respuesta:**
  - *Estado:* Comprendió que «Activa · revisión reciente» refleja el estado documentado en la última revisión editorial y **no constituye una garantía matemática de vacante abierta en tiempo real**.
  - *Fecha de corte:* Identificó correctamente la fecha de última verificación indicada en la ficha (17/11/2026).
  - *Vigencia y acción:* Comprendió que es indispensable visitar la publicación original en el ATS para confirmar si el proceso de selección sigue recibiendo postulaciones hoy.
  - *Modalidad de trabajo:* **Concluyó que el puesto es presencial porque la tarjeta indica «Lima, Perú» y no muestra la etiqueta de «Remoto».**

> [!CAUTION]
> **HALLAZGO CRÍTICO DE USABILIDAD (HEURÍSTICA UX-B07 / CONFUSIÓN MODALIDAD-UBICACIÓN):**  
> La inferencia de que la vacante es «presencial» por el solo hecho de situarse en Lima y carecer de etiqueta «remoto» es **metodológicamente y fácticamente incorrecta**.  
> - **Causa raíz:** En la fuente canónica de CookUnity (ATS Greenhouse), el empleador **no publicó** la modalidad contractual (remoto, híbrido o presencial). La política estricta de Ruta Sistemas es no inventar datos y clasificar la modalidad como «No especificada / No informado».  
> - **Fricción cognitiva del usuario:** El usuario aplicó una heurística de falso dilema (*«Si no dice remoto y dice Lima, entonces debe ser presencial en oficina»*), confundiendo la **ubicación geográfica del empleador** con la **modalidad de trabajo**.  
> - **Acción de trazabilidad:** Este hallazgo se cataloga formalmente como **`UX-B07` (Sesgo de inferencia de modalidad por ausencia de etiqueta)**. No se modificará el código ni el catálogo canónico en este bloque, pero se agenda como punto focal de observación obligatoria en las sesiones formales `P01` a `P08`.

---

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAREA D: COMPARACIÓN LOCAL DE ALTERNATIVAS SIN GANADOR UNIVERSAL                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Consigna del protocolo: Seleccionar dos vacantes, comparar atributos y evaluar neutralidad.       │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Hechos comunicados:** Exploración de la tabla comparativa lado a lado (14 atributos).
- **Paráfrasis fiel de la respuesta:**
  - *Estructura:* Comprendió que la tabla organiza y contrasta requisitos, experiencia, conocimientos, modalidad y condiciones laborales.
  - *Neutralidad algorítmica:* Entendió con claridad que la plataforma **no asigna puntajes sintéticos, no ranquea ni declara un ganador universal**.
  - *Vacíos de datos:* Interpretó correctamente que los textos «No informado» y «No publicado» reflejan transparencia factual (ausencia de publicación por el empleador) y no una penalización algorítmica.
  - *Control interactivo:* Notó que el control «Destacar diferencias» (o similar) resalta visualmente los atributos divergentes o comunes entre ambas ofertas.
- **Limitación crítica de la evidencia:** La respuesta **no especificó cuáles fueron las dos oportunidades seleccionadas para la comparación** (si fue CookUnity contra un ejemplo demostrativo o contra una vacante de Canonical), ni se dispone de registro sobre el tiempo empleado ni la facilidad para activar la selección. Se registra esta carencia sin realizar conjeturas.

---

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAREA E: DECISIÓN DE POSTULACIÓN Y VERIFICACIÓN DE PROCEDENCIA                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Consigna del protocolo: Localizar canal oficial y comprender rol de la web ante los datos.      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Hechos comunicados:** Identificación del flujo de salida hacia la fuente original.
- **Paráfrasis fiel de la respuesta:**
  - *Canales:* Identificó con precisión los botones de acción «Ver publicación original» (enlace a fuente) e «Ir a postulación ↗» (enlace directo al formulario del ATS).
  - *Deslinde de custodia:* Comprendió con exactitud que **Ruta Sistemas no recibe currículums vitae, no almacena postulaciones ni intermedia laboralmente**, redirigiendo siempre hacia el portal externo oficial del empleador.
  - *Suficiencia percibida:* El evaluador declaró que, por el momento, considera **suficiente** la información mostrada para orientar una decisión inicial.
- **Tratamiento metodológico:** La declaración de suficiencia se registra estrictamente como una **percepción cualitativa personal del evaluador**. No constituye prueba fehaciente de que toda la información contractual o laboral de fondo esté completamente cubierta, dado que salarios o detalles de beneficios no estaban publicados en la fuente original.

---

## 3. Contraste Evolutivo de Evidencias Internas

| Dimensión | `R3-02-OWNER-FEEDBACK-01` (20-11-2026) | `R3-02-INTERNAL-FEEDBACK-01` (22-11-2026) | `R3-02-INTERNAL-FEEDBACK-02` (22-11-2026) |
|---|---|---|---|
| **Alcance** | Impresión general del diseño y navegación. | Conformidad general del grupo con resultados. | Respuestas específicas estructuradas a Tareas A, B, C, D y E. |
| **Catálogo evaluado** | 1 vacante real (CookUnity) + ejemplos demostrativos. | Catálogo Alpha ampliado (6 reales Canonical/CookUnity). | Evaluación puntual sobre CookUnity y comparador de 2 vacantes. |
| **Nivel de detalle** | 3 frases verbales breves. | 5 afirmaciones globales de satisfacción. | Respuestas técnicas sobre requisitos, estados, comparación y canales. |
| **Identificación de sesgos** | No identificado. | No identificado (solo reporte de satisfacción). | **Identificado hallazgo crítico `UX-B07` (confusión ubicación/modalidad).** |
| **Estado metodológico** | Evidencia cualitativa informal. | Evidencia cualitativa informal reconciliada. | **Evidencia cualitativa informal estructurada por tareas.** |
| **Cómputo en sesiones P01–P08** | **0 / 8** (Sin cambios) | **0 / 8** (Sin cambios) | **0 / 8 (Permanece intacto en `PENDING_EXECUTION`)** |

---

## 4. Matriz de Cobertura de Objetivos de R3-02 (Corte Estructurado A–E)

A partir de las respuestas registradas, se reevalúa la matriz de los 7 objetivos clave de usabilidad del protocolo formal R3-02:

| # | Objetivo de Investigación / Validación | Estado de Cobertura | Evidencia Específica Aportada en INTERNAL-02 | Limitaciones Metodológicas Subsistentes |
|:---:|:---|:---:|:---|:---|
| **1** | **Comprensión de pertinencia (Tarea A)** | `PARTIAL` | El evaluador justificó la pertinencia curricular mediante SQL, Sheets, ERP/MRP y análisis operativo en CookUnity. | Proviene de una sola respuesta agregada; no se midió en participantes de los tres perfiles cuota (`P-EST`, `P-EGR`, `P-JUN`). |
| **2** | **Identificación de requisitos (Tarea B)** | `PARTIAL` | Distinción clara de conocimientos obligatorios, inglés, 1 año de experiencia y naturaleza de empleo formal a tiempo completo. | Autoevaluación subjetiva de competencias personales; sin cronómetro ni verificación de lectura de vacíos no publicados. |
| **3** | **Comprensión de estados y vigencia (Tarea C)** | `PARTIAL` | Comprensión adecuada de que la etiqueta no garantiza vacante abierta y que debe comprobarse el ATS oficial. | **Presencia de la confusión heurística `UX-B07`:** inferencia infundada de modalidad presencial por ubicación en Lima. |
| **4** | **Comparación neutral sin sesgos (Tarea D)** | `PARTIAL` | Comprensión explícita de que no hay ganador algorítmico y de que «No informado» refleja ausencia factual. | No se documentó cuáles fueron las dos ofertas contrastadas ni se observó el proceso de selección e interacción en la tabla. |
| **5** | **Decisión de postulación y procedencia (Tarea E)** | `PARTIAL` | Reconocimiento efectivo de la redirección hacia el ATS externo y comprensión de que la web no retiene CVs. | Declaración subjetiva de «suficiencia de información»; no se probó el clic real externo ni el formulario final del ATS. |
| **6** | **Facilidad de navegación e intuición** | `PARTIAL` | Capacidad demostrada para transitar por catálogo, ficha de detalle, comparador y botones de postulación. | Sesgo de afinidad personal con el propietario; ausencia de observador externo que registre titubeos o bloqueos. |
| **7** | **Visualización e interacción en móvil** | `UNVERIFIED` | Las respuestas A–E no aportaron ningún dato sobre el tipo de dispositivo, resolución, táctil ni visualización móvil. | La experiencia móvil se encuentra validada técnicamente en Playwright E2E, pero **no evaluada empíricamente** en este reporte. |

> [!NOTE]
> **Criterio de Rigor:**  
> Los objetivos 1 a 6 se mantienen en estado `PARTIAL`. El objetivo 7 (móvil) permanece en `UNVERIFIED` a nivel empírico en este bloque. **Ningún objetivo alcanza la condición de `VERIFIED`**, la cual exige validación protocolizada con participantes independientes en sesiones formales auditadas.

---

## 5. Requisitos Faltantes para Homologar Sesiones Formales

Para que los resultados de usabilidad puedan computar dentro de la cuota oficial de R3-02 (5 a 8 participantes) y habilitar la fase posterior R3-03 (Consolidación de Hallazgos), es indispensable cumplir los siguientes requisitos que **siguen ausentes**:

1. **Identificación disociada de participantes individuales:** Cada sesión debe corresponder a un individuo real único con identificador `P01` a `P08`.
2. **Cumplimiento de cuotas muestrales:** Comprobación estricta de pertenencia a `P-EST` (2-3 estudiantes), `P-EGR` (2-3 egresados) o `P-JUN` (1-2 juniors).
3. **Consentimiento informado formal registrado:** Aceptación documentada previa al inicio de la sesión.
4. **Facilitación neutral no directiva:** Aplicación de la guía del moderador (`r3-02-moderator-field-guide-2026-11-18.md`) por un facilitador que no induzca respuestas.
5. **Registro métrico estructurado:** Conteo de tiempo de tarea (*Time on Task*), calificación de asistencia (`SUCCESS_WITHOUT_HELP`, `SUCCESS_WITH_HELP`, `ABANDONED`) y escala de confianza (1 a 5).
6. **Notas empíricas y pensamiento en voz alta:** Transcripción de citas textuales anonimizadas y registro de expresiones de duda en tiempo real.
7. **Rúbrica de Control de Calidad (QA):** Dictamen formal de sesión (`PASS` / `FAIL`).

---

## 6. Estado de Gobernanza de Fases Maestras

Con base en la evidencia analizada, se ratifica el estado de las fases del proyecto:

- **Alpha Privada (Uso personal y círculo cercano):** **`OPERATIVA Y REVALIDADA`**. El feedback estructurado confirma que la aplicación es intuitiva, informativa y útil para el grupo evaluador.
- **`R3-02` (Trabajo de campo formal):** **`NOT_STARTED` / `PENDING_HUMAN`** (0 sesiones formales completadas en el Cuaderno de Campo).
- **`R3-03` (Consolidación y análisis de hallazgos):** **`BLOCKED`** (requiere >= 5 sesiones formales válidas).
- **`R3-04` (Refactor/Fix UX justificado):** **`BLOCKED`**.
- **`R3-05` (Decisión sobre el MVP):** **`BLOCKED`**.
- **`R4` (Automatización controlada):** **`BLOCKED`**.

---

## 7. Recomendaciones Operativas

### A. Trabajo que requiere acción humana (Propietario / Equipo de Investigación)
1. **Atención al sesgo de modalidad (`UX-B07`):** Instruir a los evaluadores en futuras sesiones para observar específicamente cómo interpretan el campo «Modalidad» cuando figura como «No especificada» o «No informado».
2. **Convocatoria formal:** Si alguno de los colegas evaluadores cumple los criterios de `P-EST`, `P-EGR` o `P-JUN` y está dispuesto a participar en una prueba formal de 30-45 minutos con observador neutral, agendarlo bajo las plantillas `P01` a `P08`.
3. **Decisión editorial en staging:** Resolver la decisión editorial humana sobre las 4 oportunidades de Sezzle preparadas en [`docs/audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md`](../audits/r3-alpha-owner-review-02-sezzle-editorial-decision-2026-11-21.md).

### B. Trabajo ejecutable por el asistente técnico
1. Mantener los contratos estáticos, la suite de pruebas automatizadas y los linters en verde.
2. Preservar la integridad de los datos canónicos (`data/opportunities.seed.json`, `data/opportunities.json`, `collector/sources.json`).
3. Registrar la trazabilidad documental y actualizar los índices del repositorio sin alterar estados de forma artificial.
