# Registro de Feedback Interno y Reconciliación de Pruebas — R3-02-INTERNAL-FEEDBACK-01
## Reconciliación de Pruebas del Propietario y Círculo Cercano con el Protocolo Formal R3-02

- **Identificador de bloque:** `R3-02-INTERNAL-FEEDBACK-01` (asociado a `R3-02-FIELDWORK-RECONCILIATION-01`)
- **Fecha de registro:** 2026-11-22
- **Tipo de intervención:** `[REFACTOR/FIX]` (Trazabilidad documental) + `[INVESTIGACIÓN_CUALITATIVA]` + `[AUDITORÍA_UX]`
- **Estado documental:** **`RECONCILED_WITH_PENDING_FORMAL_GAPS`** (Reconciliado con brechas de formalización documentadas)
- **Versión de software evaluada:** Rama `integration/r1-02c` (evolucionada tras la consolidación CSS de `R3-ALPHA-UX-02`, comparador razonado de `R3-ALPHA-IMPLEMENTATION-01`, paginación de `R3-ALPHA-UX-01` y catálogo ampliado con 6 vacantes reales de `R3-ALPHA-PROMOTION-01`)
- **Entorno de ejecución:** Servidor local de desarrollo (`http://127.0.0.1:4173/`, `python server.py`)
- **Responsable de registro:** Principal Product Engineer, UX Research Analyst & Technical Auditor

---

## 1. Contexto y Hechos Comunicados por el Propietario

Tras los avances en la experiencia de usuario y la ampliación del catálogo en la etapa de Alpha privada (bloques `R3-ALPHA-PROMOTION-01`, `R3-ALPHA-UX-01`, `R3-ALPHA-IMPLEMENTATION-01` y `R3-ALPHA-UX-02`), el propietario del proyecto coordinó y llevó a cabo una nueva ronda de pruebas de la aplicación web junto a sus compañeros de círculo cercano (amistades y colegas de Ingeniería de Sistemas).

El propietario comunicó formalmente al equipo los siguientes hechos observables:

1. **Prueba efectiva del sitio:** El propietario y sus compañeros han navegado y probado directamente la página web en su versión local.
2. **Conformidad general con los resultados:** El grupo evaluador manifestó satisfacción y conformidad con los resultados ofrecidos por la herramienta.
3. **Facilidad de uso e intuición:** La interfaz fue calificada como intuitiva y de fácil comprensión durante la navegación.
4. **Suficiencia y pertinencia de la información:** La información laboral presentada (requisitos, condiciones, modalidades y procedencia) fue considerada satisfactoria para sus necesidades.
5. **Alcance de la prueba:** Se realizaron pruebas orientadas a la experiencia general del sitio (flujo completo de exploración, consulta de detalle y comparación).

> [!NOTE]
> **Tratamiento Epistemológico de la Comunicación:**  
> Esta información se registra y valora como **evidencia cualitativa directa proporcionada por el propietario**. No se descarta por provenir de un entorno no controlado, pero tampoco se equipara artificialmente a una sesión formal de usabilidad moderada bajo el protocolo R3-02.

---

## 2. Caracterización del Feedback: Hechos Conocidos vs. Información Pendiente

Para garantizar el principio de veracidad científica y evitar sobreinterpretaciones, se desglosa con exactitud qué datos están respaldados por la comunicación y cuáles permanecen pendientes de documentación:

### 2.1 Hechos Conocidos y Verificados
- **Ejecución real de pruebas:** La plataforma fue ejecutada y probada por personas reales del entorno del propietario en un contexto cotidiano.
- **Percepción cualitativa positiva unánime:** Ninguno de los participantes del grupo comunicó bloqueadores críticos de diseño, errores de visualización insalvables ni confusión generalizada con la propuesta de valor.
- **Aceptación de la experiencia consolidada:** El grupo confirmó que el producto es utilizable y aporta valor respecto a la búsqueda laboral tradicional en Sistemas.

### 2.2 Información Pendiente (No disponible en este corte)
- **Número exacto de participantes:** No se ha informado el conteo preciso de personas que participaron en la sesión.
- **Segmentación por perfil metodológico:** Se desconoce la proporción exacta de estudiantes universitarios (`P-EST`), egresados recientes (`P-EGR`) y profesionales junior (`P-JUN`) dentro del grupo evaluador.
- **Duración y condiciones de entorno:** No se registraron los tiempos individuales por participante, tipos de dispositivos específicos (dimensiones de pantalla) ni navegadores empleados.
- **Métricas cuantitativas de usabilidad:** No se midieron tiempos de tarea (*Time on Task*), tasas de éxito sin asistencia (*Completion Rate*) ni escalas estandarizadas (SUS, SEQ).
- **Transcripciones y citas textuales disociadas:** No se levantaron grabaciones ni notas textuales de pensamiento en voz alta asociadas a componentes o campos individuales.
- **Ejecución estructurada de escenarios A a E:** No se cuenta con una bitácora que certifique la realización independiente de cada uno de los 5 escenarios protocolizados en `R3-01`.

---

## 3. Taxonomía de Evidencia en Cuatro Capas

Para resolver de manera transparente el nivel de cobertura de Ruta Sistemas, se establece una separación estricta en cuatro niveles de evidencia:

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAPA 1: Pruebas Técnicas Automatizadas                                 │
│ 193 pruebas Python + 20 pruebas Playwright E2E (Desktop y Móvil)       │
│ Evidencia: Objetiva, determinista, sintáctica y de renderizado headless│
├────────────────────────────────────────────────────────────────────────┤
│ CAPA 2: Feedback Cualitativo del Propietario y Círculo Cercano         │
│ Evaluaciones informales (R3-02-OWNER-FEEDBACK-01 e INTERNAL-01)        │
│ Evidencia: Real, cualitativa, empírica formativa, pero no protocolizada │
├────────────────────────────────────────────────────────────────────────┤
│ CAPA 3: Sesiones Formales de Usabilidad R3-02                          │
│ Plantillas P01 a P08 con consentimiento, moderación neutral y rúbrica  │
│ Evidencia: Auditada, estructurada por escenarios A-E y métricas QA     │
├────────────────────────────────────────────────────────────────────────┤
│ CAPA 4: Validación Empírica Poblacional Externa                        │
│ Muestra independiente fuera del círculo de influencia del propietario   │
│ Evidencia: Concluyente para lanzamiento público y mercado              │
└────────────────────────────────────────────────────────────────────────┘
```

- **Estado actual de Ruta Sistemas:** La herramienta cuenta con cobertura total y sólida en la **Capa 1** (automatización técnica) y respaldo exploratorio positivo en la **Capa 2** (Alpha privada para el propietario y su grupo).
- **Brecha de R3-02:** La **Capa 3** (sesiones formales protocolizadas) permanece en `PENDING_EXECUTION`, lo que impide cerrar formalmente la fase R3-02 o desbloquear R3-03.

---

## 4. Matriz de Cobertura de Objetivos de R3-02

A continuación se evalúa el estado de cumplimiento de los 7 objetivos clave de usabilidad definidos en el protocolo `R3-01-user-research-protocol-2026-11-18.md`:

| # | Objetivo de Investigación / Validación | Estado de Cobertura | Evidencia Disponible | Tipo de Evidencia | Limitaciones Detectadas | Acción Necesaria para Cerrar Brecha |
|:---:|:---|:---:|:---|:---|:---|:---|
| **1** | **Comprensión de la pertinencia de las oportunidades** *(¿El usuario distingue si la vacante encaja con su formación en Sistemas?)* | `PARTIAL` | Comunicación del grupo ("información satisfactoria"); catálogo ampliado a 6 vacantes reales de diversas familias (Cloud, Kernel, Software, Supply Chain); pruebas E2E de filtrado por familia. | Cualitativa informal + Automatizada técnica | No hay registro de qué vacantes exploraron individualmente ni de sus justificaciones verbales sobre pertinencia curricular. | Observar y registrar en plantilla individual la evaluación de pertinencia en Tarea A. |
| **2** | **Identificación de requisitos que cumple o no cumple** *(¿El usuario discierne requisitos obligatorios, deseables y vacíos?)* | `PARTIAL` | Comparador razonado con dimensión `requirements` estructurada con viñetas; llamada de atención de dedicación/idioma en callouts; pruebas Playwright de requisitos. | Cualitativa informal + Automatizada técnica | La percepción de que la información "resulta satisfactoria" no desglosa si comprendieron los requisitos de 1+ años o dedicación 40h/sem. | Documentar en Tarea B si un estudiante o egresado identifica que no cumple la experiencia previa requerida. |
| **3** | **Comprensión de los estados de verificación** *(¿Comprende 'activa · revisión reciente', vigencia temporal y ausencia de garantías?)* | `PARTIAL` | Badges visuales normalizados con Tailwind en `app.js`; eliminación de contradicciones en cabecera oficial verificada; pruebas unitarias de TTL y Schema 2. | Cualitativa informal + Automatizada técnica | No se ha verificado si el usuario interpreta la fecha de revisión como garantía absoluta de vacante abierta o como revisión estática. | Aplicar las preguntas de debriefing de Tarea C (interpretación de fecha de última verificación). |
| **4** | **Comparación de dos oportunidades sin clasificaciones engañosas** *(¿Compara neutralmente sin asumir ranking algorítmico o ganador?)* | `PARTIAL` | Implementación del comparador de 14 atributos con opción "Destacar diferencias", chips de habilidades y celdas neutras "No publicado"; 2 pruebas E2E específicas. | Cualitativa informal + Automatizada técnica | El grupo reportó conformidad general, pero no se constató si el toggle de diferencias fue descubierto y entendido como neutral. | Observar en Tarea D si el participante busca o espera un puntaje algorítmico ganador. |
| **5** | **Identificación de información necesaria antes de postular** *(¿Localiza canal oficial del empleador y entiende que la web no almacena CVs?)* | `PARTIAL` | Sección destacada "Fuente oficial verificada" con botón "Ir a postulación ↗"; deslinde explícito en pie de página y cabecera; pruebas Playwright. | Cualitativa informal + Automatizada técnica | No hay evidencia registrada de que comprendan que Ruta Sistemas no custodia sus currículums ni intermedia postulaciones. | Realizar Tarea E y verificar que el usuario identifique el canal externo del ATS original. |
| **6** | **Facilidad de navegación y comprensión general** *(¿La interfaz resulta intuitiva, clara y libre de fricciones de orientación?)* | `PARTIAL` | Reporte verbal unánime del grupo ("la interfaz se considera intuitiva"); navegación entre catálogo, modal y vista independiente `?id=...`; breadcrumbs y paginación probadas en E2E. | Cualitativa informal + Automatizada técnica | El juicio de que es "intuitiva" proviene de usuarios con afinidad al propietario (sesgo de cortesía potencial) y sin registro de rutas de navegación. | Medir tiempos de navegación y tasa de éxito sin asistencia en sesiones protocolizadas independientes. |
| **7** | **Problemas de interacción o visualización en dispositivos móviles** *(¿Existen desbordamientos, textos ilegibles o botones inaccesibles en pantallas pequeñas?)* | `PARTIAL` | Consolidación Tailwind CSS v4 (`R3-ALPHA-UX-02`); auditoría de viewport móvil Playwright (`scrollWidth === clientWidth` a 393x851); `@layer base` tap highlight reset. | Automatizada técnica | La prueba informal del grupo no especificó si se utilizaron teléfonos celulares reales, qué modelos ni qué experiencia táctil tuvieron. | Ejecutar al menos 2 sesiones formales en dispositivos móviles reales (Android/iOS) con registro de interacción táctil. |

> [!IMPORTANT]
> **Criterio de Rigor:**  
> Ningún objetivo ha sido clasificado como `VERIFIED`. Aunque el feedback interno y las pruebas automatizadas respaldan que la aplicación funciona correctamente y satisface a sus usuarios inmediatos, la calificación `VERIFIED` está reservada exclusivamente para objetivos respaldados por evidencia empírica protocolizada (Capa 3).

---

## 5. Decisión sobre el Trabajo de Campo y Admisibilidad Metodológica

### 5.1 Admisibilidad de las Pruebas Internas
1. **Para la Alpha Privada (Uso Personal y Círculo Reducido):**  
   **PLENAMENTE ADMISIBLE Y SUFICIENTE**. La conformidad comunicada por el propietario y sus compañeros confirma que el producto cumple su objetivo actual: ser una herramienta de apoyo personal y colectivo directo para explorar convocatorias de Sistemas en Perú sin fricciones bloqueantes.
2. **Para la Investigación Formal R3-02 (Validación de Producto):**  
   **NO ADMISIBLE COMO SUSTITUTO DE SESIONES FORMALES**. No es metodológicamente válido homologar estas pruebas como equivalentes a las sesiones formales `P01` a `P08`. La falta de asignación de perfiles, la ausencia de moderador neutral independiente y la omisión del registro sistemático de tareas violarían los principios de reproducibilidad y neutralidad deontológica.

### 5.2 Gobernanza de las Plantillas de Sesión (`P01.md` a `P08.md`)
- Las 8 plantillas en `docs/research/sessions/` **permanecen intactas** en estado `PENDING_EXECUTION`.
- No se volcarán datos sintéticos ni se forzará la imputación de este feedback general a ningún participante en particular.
- El conteo de sesiones formales completadas en el Cuaderno de Campo se mantiene en **0 / 8**.

---

## 6. Brechas de Evidencia Identificadas y Requisitos Pendientes

Para que el proyecto pueda transitar formalmente hacia el cierre de R3-02 y el desbloqueo de R3-03 (Consolidación de Hallazgos), se requiere subsanar las siguientes brechas:

1. **Brecha de Representatividad por Cuotas:** Contar con al menos 5 sesiones formales con participantes que cumplan estrictamente los perfiles `P-EST` (2-3), `P-EGR` (2-3) y `P-JUN` (1-2), externos al equipo promotor.
2. **Brecha de Consentimiento Formal:** Disponer de confirmaciones de consentimiento informado disociado registrado en cada sesión.
3. **Brecha de Observación Directa en Tareas A–E:** Completar las hojas de registro individual con tiempos, nivel de asistencia (`SUCCESS_WITHOUT_HELP`, `SUCCESS_WITH_HELP`, `ABANDONED`) y escala de confianza (1 a 5).
4. **Brecha de Fricciones Heurísticas:** Contrastar de forma no directiva si las 6 fricciones históricas de R3-01 (`UX-B01` a `UX-B06`) fueron superadas con las mejoras introducidas en `R3-ALPHA-UX-01`, `R3-ALPHA-IMPLEMENTATION-01` y `R3-ALPHA-UX-02`.
5. **Brecha de Diversidad de Dispositivos:** Registrar explícitamente el uso de dispositivos móviles y navegadores variados en condiciones reales de red.

---

## 7. Recomendaciones y Siguiente Acción Operativa

1. **Aprovechar el impulso del grupo interno como semillero de participantes:**  
   Si alguno de los compañeros del propietario cumple con los perfiles `P-EST`, `P-EGR` o `P-JUN` y está dispuesto a participar en una sesión protocolizada de 30-45 minutos conducida por un facilitador con el guion neutral de `r3-02-moderator-field-guide-2026-11-18.md`, se le puede convocar formalmente y documentar bajo el código correspondiente (`P01`, `P04` o `P07`).
2. **Mantener la distinción de niveles de madurez:**  
   Preservar el desacoplamiento formal establecido en `R3-02-PRIVATE-ALPHA-01`:
   - *Nivel 1 (Alpha Privada):* Funcional, validada internamente y lista para uso personal cotidiano.
   - *Nivel 2 (Validación R3 Formal):* Requiere completar el trabajo de campo formal protocolizado antes de emitir decisiones de salida a mercado o servicio público.
3. **Siguiente acción recomendada en el repositorio:**  
   Atender las decisiones editoriales pendientes en staging (revisión de candidatos de Sezzle bajo `R3-ALPHA-OWNER-REVIEW-02`) o, si el propietario desea avanzar con la validación de usuarios, coordinar la primera sesión formal protocolizada `P01`.
