# Registro de Evaluación Informal del Círculo Cercano — R3-02-OWNER-FEEDBACK-01

**Identificador de bloque:** `R3-02-OWNER-FEEDBACK-01`
**Fecha de registro:** 20 de noviembre de 2026
**Tipo de intervención:** `[DOCUMENTACIÓN]` + `[INVESTIGACIÓN_CUALITATIVA]` + `[QA/UX_REVIEW]`
**Estado documental:** **`COMPLETED_WITH_LIMITED_FEEDBACK`** (Evaluación informal completada con feedback general limitado)
**Versión evaluada:** Rama `integration/r1-02c` (sincronizada en commit `b27e418`)
**Entorno de ejecución:** Servidor local nativo (`http://127.0.0.1:4173/`, `python server.py`)

---

## 1. Contexto y Origen de la Información

Tras la preparación, verificación y entrega del entorno de evaluación no productivo en los bloques `R3-02-PREVIEW-02` y `R3-02-PREVIEW-03`, el propietario de Ruta Sistemas probó la versión de evaluación local con personas de su círculo cercano (amistades y colegas).

Posteriormente a dicha exploración, el propietario comunicó los resultados al equipo de ingeniería y autorizó continuar con el avance del proyecto.

> [!NOTE]
> **Naturaleza del Registro:**
> La información aquí consignada proviene exclusivamente de la **comunicación verbal/general transmitida por el propietario** como síntesis de las pruebas con su círculo cercano. No constituye citas textuales directas de participantes individuales ni surge de una sesión de investigación formal moderada.

---

## 2. Observaciones Comunicadas por el Propietario

El propietario transmitió de manera textual y concisa tres observaciones generales:

1. **Valoración favorable del diseño:** *"El diseño está bien."*
2. **Percepción de facilidad de uso e intuición:** *"La aplicación resulta intuitiva."*
3. **Percepción de suficiencia de la información:** *"La aplicación proporciona la información necesaria."*

Asimismo, sobre la base de esta experiencia satisfactoria, el propietario **autorizó continuar con el proyecto**.

---

## 3. Limitaciones Metodológicas de la Evidencia

En estricta aplicación del principio de veracidad científica, rigor QA y transparencia de Ruta Sistemas, se declaran las siguientes limitaciones objetivas de este registro:

1. **Carácter general y sintético:** Las observaciones representan una apreciación global y cualitativa. No se desglosan por pantalla, componente o interacción específica.
2. **Sin datos demográficos ni perfiles:** No se dispone del número exacto de participantes, nombres, edades, ocupaciones ni clasificación en los perfiles objetivo de investigación (`P-EST`, `P-EGR`, `P-JUN`).
3. **Sin métricas cuantitativas:** No se midieron tiempos de realización de tareas, tasas de éxito/fracaso, niveles numéricos de satisfacción ni curvas de aprendizaje.
4. **Sin cobertura estructurada de escenarios:** No se evaluó de forma protocolizada la ejecución individual de los escenarios A (búsqueda y filtros), B (identificación de vacante activa), C (comprensión de evidencias y requisitos), D (comparador de ofertas) ni E (canal de postulación oficial).
5. **No implica ausencia de fricciones:** Una valoración general positiva no garantiza que no existan fricciones heurísticas menores o casos de borde que requieran observación empírica sistemática.
6. **No habilita conclusiones de validación final:** Este feedback informal no autoriza declarar validado el MVP ante el mercado ni ante usuarios externos no vinculados al propietario.

---

## 4. Separación Deontológica Respecto a la Investigación Formal R3-02

Este registro se mantiene **estrictamente aislado** del corpus de investigación formal de usuarios:

| Aspecto | Evaluación Informal del Círculo Cercano | Investigación Formal R3-02 |
|---|---|---|
| **Instrumento de registro** | Este documento (`r3-02-owner-circle-feedback-2026-11-20.md`) | Plantillas individuales `docs/research/sessions/P01.md` a `P08.md` |
| **Consentimiento informado** | No aplica (interacción informal en círculo de confianza) | Obligatorio y firmado previo a la sesión |
| **Moderación** | Libre / espontánea por el propietario | Protocolizada con guía del moderador (`r3-02-moderator-field-guide-2026-11-18.md`) |
| **Rúbrica QA** | No requerida | Obligatoria (criterios de neutralidad, completitud y veredicto `PASS`/`FAIL`) |
| **Cómputo en muestra** | **0 sesiones** (no suma a la cuota formal) | Requiere entre 5 y 8 participantes reales con cuotas `P-EST`, `P-EGR`, `P-JUN` |
| **Clasificación de sesión** | No aplica (no es sesión formal) | `VALID`, `INCOMPLETE` o `INVALID` |

**Gobernanza de las plantillas `P01.md` a `P08.md`:**
Las ocho plantillas permanecen intactas en estado `PENDING_EXECUTION`. Ningún dato de este feedback informal ha sido volcado ni atribuido a ningún participante formal.

---

## 5. Impacto en el Roadmap y Fases Posteriores

El feedback informal favorable permite al propietario confirmar la dirección general del diseño y la experiencia de usuario, pero no altera los requisitos de rigor para las fases subsiguientes:

- **`R3-02-PREVIEW-02`:** `DONE` (entorno verificado).
- **`R3-02-PREVIEW-03`:** `DONE` (sincronización Git confirmada en commit `b27e418`).
- **`R3-02-OWNER-FEEDBACK-01`:** `COMPLETED_WITH_LIMITED_FEEDBACK` (evaluación informal registrada).
- **`R3-02 formal (Sesiones de campo):`** Se mantiene en **`NOT_STARTED` / `PENDING_HUMAN`**, a la espera de la convocatoria y ejecución de las sesiones formales con participantes elegibles.
- **`R3-03 (Consolidación y análisis de hallazgos):`** Permanece estrictamente **`BLOCKED`** hasta contar con al menos 5 sesiones formales válidas.
- **`R3-04 (Refactor/Fix UX justificado):`** Permanece estrictamente **`BLOCKED`**.
- **`R3-05 (Decisión sobre el MVP):`** Permanece estrictamente **`BLOCKED`**.
- **`R4 (Automatización controlada):`** Permanece estrictamente **`BLOCKED`**.
- **`R5 (Evaluación profesional explicable):`** Permanece **`APLAZADA`**.

---

## 6. Documentos Relacionados

- [r3-02-owner-circle-evaluation-guide.md](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-owner-circle-evaluation-guide.md): Guía de exploración que sirvió de base para las pruebas informales.
- [r3-02-informal-feedback-template.md](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-informal-feedback-template.md): Plantilla marco para anotaciones cualitativas informales.
- [r3-02-preview-03-git-delivery-2026-11-20.md](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-02-preview-03-git-delivery-2026-11-20.md): Auditoría de entrega y sincronización de la versión evaluada.
- [README.md](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/README.md): Repositorio e índice de sesiones formales individuales.
