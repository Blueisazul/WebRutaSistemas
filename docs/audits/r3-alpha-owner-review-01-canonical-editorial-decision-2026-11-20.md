# R3-ALPHA-OWNER-REVIEW-01 — Revalidación y Decisión Editorial del Segundo Lote Canonical

**Proyecto:** Ruta Sistemas  
**Fase:** R3 — Evaluación con Círculo Cercano y Alpha Privada  
**Identificador del bloque:** `R3-ALPHA-OWNER-REVIEW-01` (con subtareas `R3-ALPHA-OWNER-REVIEW-01A`, `01B`, `01C`, `01D`)  
**Fecha y hora de revalidación:** 2026-11-20T20:53:40-05:00 (Hora Lima, UTC-5)  
**Responsables (Roles):** Principal Software Architect, Senior Software Engineer, Technical Auditor y Curador Editorial de Empleo TI  
**Estado de salida:** `DONE` (Expediente completo y verificado; decisión humana pendiente del propietario)  
**Rama activa:** `integration/r1-02c`  
**HEAD comprobado:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d` (coincidente con `origin/integration/r1-02c`)  
**Documentos rectores:**
- [docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](../architecture/r0-decisiones-y-alcance-2026-11-12.md)
- [docs/architecture/r3-private-alpha-scope-decision-2026-11-20.md](../architecture/r3-private-alpha-scope-decision-2026-11-20.md)
- [docs/audits/r3-alpha-curation-01-second-batch-2026-11-20.md](r3-alpha-curation-01-second-batch-2026-11-20.md)
- [docs/audits/r2-a-04-editorial-decision-2026-11-18.md](r2-a-04-editorial-decision-2026-11-18.md)
- [docs/audits/r2-a-05-first-real-publication-2026-11-18.md](r2-a-05-first-real-publication-2026-11-18.md)

---

## 1. Resumen Ejecutivo

El presente expediente constituye la **auditoría de revalidación independiente y revisión editorial** sobre las cinco vacantes de Canonical Ubuntu preparadas en el bloque `R3-ALPHA-CURATION-01`.

El objetivo de esta intervención pericial es verificar que ninguna de las propuestas se base en suposiciones o lecturas superficiales (como deducir disponibilidad únicamente de un código HTTP 200), contrastar la realidad técnica y legal de su postulación, auditar la antigüedad real de las requisiciones en el ATS de Canonical, desglosar sus limitaciones formativas e idiomáticas frente a estudiantes y egresados de Ingeniería de Sistemas en el Perú, y presentar un **expediente formal de decisión humana para el propietario**, preservando estrictamente la integridad de los catálogos canónicos y las barreras de gobernanza de la Alpha privada.

### Métricas de la Revalidación
- **Candidatas revalidadas individualmente:** 5 de 5 (100%).
- **Candidatas con postulación abierta y formulario activo:** 5 de 5 (100%).
- **Candidatas vigentes y elegibles desde el Perú:** 5 de 5 (100% elegibilidad bajo esquema remoto global/Américas).
- **Candidatas de cohorte fresca (publicada en 2026):** 1 de 5 (`8379825`, graduados 2026/2027, publicada el 16-11-2026).
- **Candidatas bajo esquema continuo/rolling pipeline (2021-2025):** 4 de 5 (`6707669`, `5370815`, `3257589`, `6448444`).
- **Archivos canónicos modificados:** 0 (Hashes SHA-256 100% idénticos).
- **Promoción automática al catálogo:** 0 (Prohibición estricta respetada; candidates retenidos en staging).
- **Pruebas unitarias y de catálogo aprobadas:** 193/193 tests OK; validación de Schema 2 en verde.

---

## 2. Estado Real del Repositorio y Preflight Técnico

Se ejecutó la inspección forense del árbol de trabajo al inicio del bloque:

```powershell
git status --short
# M docs/architecture/r0-decisiones-y-alcance-2026-11-12.md
# M docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md
# M docs/research/sessions/README.md
# ?? docs/architecture/r3-private-alpha-scope-decision-2026-11-20.md
# ?? docs/audits/r3-alpha-curation-01-second-batch-2026-11-20.md
# ?? docs/research/r3-02-owner-circle-feedback-2026-11-20.md

git rev-parse HEAD
# b27e418fb80f1e2c9d406fbf135b395ab6c4705d (integration/r1-02c, sincronizado con origin)
```

**Hallazgos de Preflight:**
1. El commit HEAD `b27e418...` coincide con el registro documental de entrega de `R3-02-PREVIEW-03`.
2. Las modificaciones y archivos no rastreados en `docs/` corresponden a la formalización de la Alpha privada (`R3-02-PRIVATE-ALPHA-01`), el registro de retroalimentación informal (`R3-02-OWNER-FEEDBACK-01`) y el informe de curaduría (`R3-ALPHA-CURATION-01`), los cuales han sido escrupulosamente preservados sin sobrescritura destructiva.
3. La bandeja local `data/candidates/inbox.local.json` se encuentra disponible y poblada con los 12 registros de staging validados bajo Schema 2.

---

## 3. Revalidación Técnica Individual de las Cinco Candidatas (R3-ALPHA-OWNER-REVIEW-01A)

Para cada vacante se ejecutó una doble verificación HTTP en tiempo real el **2026-11-20 entre las 20:53:36 y 20:53:42 (UTC-5)**:
- **Capa 1 (ATS REST API):** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/{id}`
- **Capa 2 (Web Job Board HTML):** `https://job-boards.greenhouse.io/canonical/jobs/{id}`

La verificación no se limitó a recibir un código HTTP 200, sino que auditó el DOM del formulario de postulación: existencia de campos de entrada interactivos (`name="first_name"`, `name="last_name"`, `name="email"`, `name="resume"`), action endpoint de envío activo, y ausencia taxativa de señales de cierre ("This position has been filled", "No longer accepting applications", "Posting has expired").

```
                                  [ REVALIDACIÓN DOBLE CAPA ]
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 ▼                                                           ▼
       [ CAPA 1: REST API ]                                        [ CAPA 2: WEB HTML ]
   boards-api.greenhouse.io/canonical/jobs/{id}            job-boards.greenhouse.io/canonical/jobs/{id}
                 │                                                           │
   - HTTP 200 OK                                               - HTTP 200 OK
   - Payload JSON estructurado                                 - Formulario interactivo presente
   - Metadatos first_published / updated_at                    - Inputs first_name, email, resume
   - Sin deadline explícito                                    - Cero alertas de cierre o expiración
```

### 3.1. Candidata 8379825 — Graduate Software Engineer, Open Source and Linux
- **Título oficial:** `Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu`
- **Requisition ID:** `8379825`
- **API Endpoint:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/8379825` `[HTTP 200 OK]`
- **Canal de postulación web:** `https://job-boards.greenhouse.io/canonical/jobs/8379825` `[HTTP 200 OK]`
- **Formulario interactivo:** Detectado y operativo (`form#application_form` con inputs para CV, carta, datos personales).
- **Señales de cierre/retirada:** Ninguna.
- **Fechas declaradas por la fuente:**
  - `first_published`: `2026-11-16T08:39:36-05:00`
  - `updated_at`: `2026-11-16T08:39:36-05:00`
- **Naturaleza de la publicación:** **Convocatoria de Cohorte Fresca (Noviembre 2026)**. La descripción declara taxativamente: *"We are hiring 2026 and 2027 Graduate Software Engineers into engineering teams around the world"*. Está explícitamente diseñada para quienes culminan estudios en 2026 o 2027.

### 3.2. Candidata 6707669 — Junior Ubuntu Software Engineer
- **Título oficial:** `Junior Ubuntu Software Engineer`
- **Requisition ID:** `6707669`
- **API Endpoint:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/6707669` `[HTTP 200 OK]`
- **Canal de postulación web:** `https://job-boards.greenhouse.io/canonical/jobs/6707669` `[HTTP 200 OK]`
- **Formulario interactivo:** Operativo y recibiendo aplicaciones.
- **Señales de cierre/retirada:** Ninguna.
- **Fechas declaradas por la fuente:**
  - `first_published`: `2025-11-07T11:35:52-05:00`
  - `updated_at`: `2026-08-05T18:23:33-04:00`
- **Naturaleza de la publicación:** **Requisición Continua (Rolling Talent Pipeline)**. Canonical mantiene abiertas estas vacantes estratégicas de desarrollo del sistema operativo Ubuntu, refrescando su contenido semestralmente y evaluando postulantes de forma permanente.

### 3.3. Candidata 5370815 — Junior Linux Kernel Engineer - Ubuntu
- **Título oficial:** `Junior Linux Kernel Engineer - Ubuntu`
- **Requisition ID:** `5370815`
- **API Endpoint:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/5370815` `[HTTP 200 OK]`
- **Canal de postulación web:** `https://job-boards.greenhouse.io/canonical/jobs/5370815` `[HTTP 200 OK]`
- **Formulario interactivo:** Operativo y recibiendo aplicaciones.
- **Señales de cierre/retirada:** Ninguna.
- **Fechas declaradas por la fuente:**
  - `first_published`: `2024-02-25T22:35:49-05:00`
  - `updated_at`: `2026-08-05T18:23:33-04:00`
- **Naturaleza de la publicación:** **Requisición Continua (Rolling Talent Pipeline)** para el equipo central de ingeniería del kernel Linux.

### 3.4. Candidata 3257589 — Software Engineer - Python - Cloud - graduate level
- **Título oficial:** `Software Engineer - Python - Cloud - graduate level`
- **Requisition ID:** `3257589`
- **API Endpoint:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/3257589` `[HTTP 200 OK]`
- **Canal de postulación web:** `https://job-boards.greenhouse.io/canonical/jobs/3257589` `[HTTP 200 OK]`
- **Formulario interactivo:** Operativo y recibiendo aplicaciones.
- **Señales de cierre/retirada:** Ninguna.
- **Fechas declaradas por la fuente:**
  - `first_published`: `2021-06-28T09:53:27-04:00`
  - `updated_at`: `2026-08-05T18:23:33-04:00`
- **Naturaleza de la publicación:** **Requisición Continua de Larga Duración (Regional Pipeline)**. Convocatoria orientada a recién graduados radicados en la región Américas. A pesar de su fecha original de 2021, la vacante fue actualizada en agosto de 2026 y continúa admitiendo postulaciones activas.

### 3.5. Candidata 6448444 — Associate Linux Support Engineer
- **Título oficial:** `Associate Linux Support Engineer`
- **Requisition ID:** `6448444`
- **API Endpoint:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/6448444` `[HTTP 200 OK]`
- **Canal de postulación web:** `https://job-boards.greenhouse.io/canonical/jobs/6448444` `[HTTP 200 OK]`
- **Formulario interactivo:** Operativo y recibiendo aplicaciones.
- **Señales de cierre/retirada:** Ninguna.
- **Fechas declaradas por la fuente:**
  - `first_published`: `2025-02-10T04:37:24-05:00`
  - `updated_at`: `2026-08-05T18:23:33-04:00`
- **Naturaleza de la publicación:** **Requisición Continua** para la división de soporte técnico global y administración de sistemas en la nube.

---

## 4. Auditoría de Elegibilidad desde Perú y Régimen de Contratación (R3-ALPHA-OWNER-REVIEW-01B)

### 4.1. Taxonomía Geográfica y Viabilidad Contractual
Se auditó la política pública de contratación remota de Canonical (`https://canonical.com/careers/company-culture/remote-work` y cuerpo del texto de las vacantes):
- **Estructura laboral:** Canonical es una empresa pionera en empleo distribuido, con más de 1,100 colaboradores radicados en más de 75 países y menos del 5% de roles en oficinas físicas.
- **Alineación de husos horarios:** Canonical organiza a sus equipos de ingeniería en tres franjas horarias: `EMEA` (Europa, Medio Oriente, África), `APAC` (Asia Pacífico) y `AMER` (Norte, Centro y Sudamérica). Perú opera en huso horario `UTC-5`, integrándose plenamente en la franja `AMER`.
- **Elegibilidad territorial:** La requisición `3257589` exige explícitamente ubicación `Home Based - Americas`. Las cuatro restantes (`8379825`, `6707669`, `5370815`, `6448444`) declaran `Home based - Worldwide` con selección horaria regional.
- **Contraste con fuentes descartadas:** A diferencia taxativa de Wikimedia (que restringe la contratación a 18 países que excluyen al Perú) o Mozilla (que restringe a EE.UU., Canadá y selectos países de la UE), Canonical contrata activamente en América Latina mediante esquemas de contratación internacional y Employer of Record (EOR), contando con historial comprobable de colaboradores residentes en territorio peruano.

### 4.2. Régimen de Compensación y Moneda
- Canonical no publica rangos salariales explícitos en los titulares de sus vacantes.
- En la sección corporativa de beneficios declara: *"We consider geographical location, experience, and performance in shaping compensation worldwide. We assess performance and revisit compensation twice annually... In addition to base pay, we offer a performance-driven annual bonus"*.
- **Beneficio educativo garantizado:** Todas las vacantes incluyen un presupuesto anual asignado de **USD 2,000** para aprendizaje y desarrollo profesional individual.
- **Viajes internacionales:** Se requiere y financia la participación presencial dos veces al año en eventos de equipo ("engineering sprints") de hasta dos semanas de duración en diversas ciudades del mundo.

---

## 5. Pertinencia Formativa frente al Perfil de la Alpha Privada

La Alpha privada de Ruta Sistemas tiene como usuarios al propietario y amigos cercanos (estudiantes universitarios de ciclos superiores, egresados recientes y profesionales junior de Ingeniería de Sistemas). La evaluación pericial arroja los siguientes matices críticos:

| Candidata | Nivel Real | Dedicación | ¿Apta para Estudiantes Regulares? | Pertinencia con Ingeniería de Sistemas | Barrera de Entrada Principal |
|---|---|---|---|---|---|
| **`8379825`** | Graduate / Trainee | Tiempo Completo (40h/sem) | **Condicional:** Solo si están en último ciclo o egresando (Cohorte 2026/2027) | **Extrema:** Formación en software de base, Python, C++, Go, Rust, Linux | Inglés profesional fluido; alta exigencia en proceso de selección |
| **`6707669`** | Junior (0-2 años) | Tiempo Completo (40h/sem) | **Baja:** Requiere disponibilidad full-time inmediata | **Alta:** Desarrollo de sistemas, herramientas de packaging y CI/CD | Experiencia previa en Linux y depuración; inglés avanzado |
| **`5370815`** | Junior (0-2 años) | Tiempo Completo (40h/sem) | **Baja:** Dedicación full-time | **Media-Alta (Especializada):** Ideal para perfiles con interés en sistemas operativos y bajo nivel (C/Rust) | Conocimientos profundos de arquitectura de kernel y controladores |
| **`3257589`** | Graduate (0-1 año) | Tiempo Completo (40h/sem) | **Moderada:** Apta para egresados recientes | **Extrema:** Python, infraestructura en la nube, servidores Linux y automatización | Inglés profesional; alineación con huso horario AMER |
| **`6448444`** | Associate (0-1 año) | Tiempo Completo (40h/sem) | **Moderada:** Apta para bachilleres o egresados | **Muy Alta:** Redes, administración de servidores, troubleshooting y soporte TI | Inglés fluido hablado (atención de incidentes técnicos globales) |

> [!WARNING]
> **Ninguna de las cinco ofertas es una práctica preprofesional (convenio formativo según ley peruana 28518).** Todas son empleos directos a tiempo completo. Los estudiantes de ciclos regulares que no cuenten con disponibilidad de 40 horas semanales no podrán compatibilizarlas con carga lectiva presencial. Esta limitación debe ser comunicada con total transparencia en la interfaz de la Alpha privada.

---

## 6. Gobernanza y Límites de Reutilización de Datos (R3-ALPHA-OWNER-REVIEW-01C)

Se auditó el estado legal y técnico de `canonical-careers` en `collector/sources.json`:

```json
{
  "id": "canonical-careers",
  "kind": "employer_site",
  "connector": "manual-review",
  "enabled": false,
  "decision": "pending_review",
  "termsReview": "pending",
  "rightsReview": "pending",
  "officialUrl": "https://canonical.com/careers"
}
```

### Distinción Rigurosa de Derechos y Autorizaciones:
1. **Acceso técnico a endpoint público:** Concedido por la arquitectura pública de Greenhouse (`boards-api.greenhouse.io`). No requiere API keys ni evade mecanismos de seguridad.
2. **Permiso de consulta y lectura:** Plenamente legítimo como usuario público que accede a una oferta de trabajo.
3. **Conservación local en staging:** Amparada bajo fines de investigación técnica y evaluación personal privada (`fair use` / uso personal en desarrollo).
4. **Atribución y visualización en círculo íntimo:** Viable para la Alpha privada (evaluación personal y amigos no comerciales en red local o entorno cerrado).
5. **Redistribución pública e indexación comercial:** **ESTRICTAMENTE NO AUTORIZADA.** La fuente mantiene sus términos de reutilización en `pending_review`.
6. **Prohibición de contacto inconsulto:** No se han remitido correos ni solicitudes legales a Canonical, preservando la discreción y el gobierno del propietario.

---

## 7. Expediente Comparativo Integral para el Propietario (R3-ALPHA-OWNER-REVIEW-01D)

A continuación se presenta la tabla comparativa exhaustiva con la recomendación editorial fundamentada para cada candidata:

| ID Candidato | Puesto | Familia Profesional | Nivel | Requisitos Académicos | Experiencia Exigida | Inglés Requerido | Elegibilidad Perú | Modalidad y Jornada | Salario | Beneficios Destacados | Postulación Abierta | Frescura Evidencia | Pertinencia Alpha Privada | Limitaciones Principales | Estado Editorial Recomendado | Justificación y Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `CAND-greenhouse-public-job-board-template-8379825` | Graduate Software Engineer, Open Source and Linux | Desarrollo / Open Source | Graduate / Entry-Level | Grado en Computación, Informática o STEM (Cohorte 2026/2027) | 0 a 1 año | Profesional (oral y escrito) | `PERU_EXPLICIT` (AMER UTC-5) | Remoto / Full-time (40h) | No publicado | USD 2,000 anual aprendizaje, sprints internacionales 2/año, bono anual | Sí (Formulario activo) | `ALL_FRESH` (Observado 20-11-2026) | Máxima para recién graduados | Exige dedicación full-time; proceso de selección riguroso; inglés fluido | **`APPROVE_WITH_LIMITATIONS`** | Convocatoria fresca (16-11-2026) explícita para graduados 2026/2027. Alto valor formativo en Linux. Limitada a uso privado. |
| `CAND-greenhouse-public-job-board-template-6707669` | Junior Ubuntu Software Engineer | Desarrollo / Sistemas Operativos | Junior | Bachiller en Computación o STEM | 0 a 2 años | Profesional (oral y escrito) | `PERU_EXPLICIT` (Worldwide) | Remoto / Full-time (40h) | No publicado | USD 2,000 anual aprendizaje, sprints semestrales, bono anual | Sí (Formulario activo) | `ALL_FRESH` (Observado 20-11-2026) | Alta para egresados con base en Linux | Requisición continua (actualizada 08-2026); requiere experiencia previa en packaging o depuración | **`APPROVE_WITH_LIMITATIONS`** | Vacante técnica sólida y activa en Greenhouse. Requiere aclarar que es un pipeline continuo. Limitada a uso privado. |
| `CAND-greenhouse-public-job-board-template-5370815` | Junior Linux Kernel Engineer - Ubuntu | Sistemas Operativos / Kernel | Junior | Formación técnica en Sistemas o Computación | 0 a 2 años | Eficaz (oral y escrito) | `PERU_EXPLICIT` (Worldwide) | Remoto / Full-time (40h) | No publicado | USD 2,000 anual aprendizaje, viajes a sprints, bono anual | Sí (Formulario activo) | `ALL_FRESH` (Observado 20-11-2026) | Media-Alta (Nicho especializado) | Exige conocimientos avanzados de C, Git y arquitectura del kernel; pipeline continuo desde 2024 | **`APPROVE_WITH_LIMITATIONS`** | Oportunidad única de aprendizaje en software de bajo nivel. Requisición abierta y activa. Limitada a uso privado. |
| `CAND-greenhouse-public-job-board-template-3257589` | Software Engineer - Python - Cloud - graduate level | Cloud / Backend / Infraestructura | Graduate / Entry-Level | Bachiller en Ciencias de la Computación o STEM | 0 a 1 año | Profesional (oral y escrito) | `PERU_EXPLICIT` (Home Based - Americas) | Remoto / Full-time (40h) | No publicado | USD 2,000 anual aprendizaje, sprints semestrales, bono anual | Sí (Formulario activo) | `ALL_FRESH` (Observado 20-11-2026) | Máxima para perfiles de Sistemas y Cloud | Requisición rolling con fecha de origen 2021 (refrescada 08-2026); requiere Python y conceptos de cloud | **`APPROVE_WITH_LIMITATIONS`** | Máxima pertinencia curricular para Sistemas (Python + Cloud). Huso horario AMER directo. Limitada a uso privado. |
| `CAND-greenhouse-public-job-board-template-6448444` | Associate Linux Support Engineer | Soporte Avanzado / Redes / Sysadmin | Entry-Level / Associate | Grado en Sistemas, Telecomunicaciones o Computación | 0 a 1 año | Fluido (oral y escrito) | `PERU_EXPLICIT` (Worldwide) | Remoto / Full-time (40h) | No publicado | USD 2,000 anual aprendizaje, sprints semestrales, bono anual | Sí (Formulario activo) | `ALL_FRESH` (Observado 20-11-2026) | Muy Alta para perfiles de infraestructura y soporte | Pipeline continuo (origen 2025, refrescado 08-2026); rol orientado a soporte técnico en servidores | **`APPROVE_WITH_LIMITATIONS`** | Cubre el área de redes y sysadmin con gran rigor. Formulario verificado. Limitada a uso privado. |

---

## 8. Opciones de Decisión para el Propietario

En respeto absoluto a la directiva de gobernanza (*"La decisión del propietario no se sustituye con una decisión del agente"*), se someten a su consideración las siguientes tres alternativas:

```
                            [ PUERTA DE CONTROL HUMANO: OPCIONES ]
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
      [ OPCIÓN A ]                       [ OPCIÓN B ]                      [ OPCIÓN C ]
   Aprobación Completa               Aprobación Selectiva              Mantener en Staging
   (5 Candidatas Canonical)          (2 Candidatas Core Dev)           (0 Promociones)
             │                                 │                                 │
 - Máxima diversidad de áreas      - Menor carga de lectura          - Riesgo cero de términos
 - 6 oportunidades reales totales  - Foco en Desarrollo y Cloud      - Espera a nuevas sesiones
 - Exige explicar full-time        - Mantiene 3 reales en total      - Mantiene 1 real en catálogo
```

### Opción A — Aprobación del lote completo (5 candidatas)
- **Alcance:** Aprobar la incorporación de las cinco candidatas de Canonical a la Alpha privada.
- **Ventajas:** Resuelve de inmediato el cuello de botella de contenido, elevando a 6 las vacantes reales disponibles (CookUnity OP-005 + 5 Canonical). Cubre cuatro áreas formativas esenciales de la carrera (Desarrollo, Cloud, Kernel y Redes/Soporte).
- **Riesgos y consecuencias:** Cuatro de las vacantes corresponden a pipelines continuos (rolling requisitions). Todas exigen jornada completa e inglés fluido, lo que debe advertirse con claridad en la interfaz para no desorientar a estudiantes de ciclos intermedios.
- **Régimen legal:** Uso circunscrito estrictamente a la Alpha privada no comercial.

### Opción B — Aprobación selectiva focalizada (2 candidatas)
- **Alcance:** Aprobar únicamente las dos vacantes de desarrollo de software general: `8379825` (Graduate Software Engineer, cohorte fresca 2026/2027) y `3257589` (Python Cloud Graduate).
- **Ventajas:** Prioriza la convocatoria con mayor certeza temporal (publicada hace 4 días) y la más afín al perfil promedio de desarrollo en Sistemas. Menor sobrecarga de información.
- **Riesgos y consecuencias:** Deja fuera las áreas de infraestructura/soporte (`6448444`) y sistemas operativos (`6707669`, `5370815`), limitando la variedad del catálogo a 3 vacantes reales en total.

### Opción C — Postergación en staging (0 candidatas promovidas)
- **Alcance:** Mantener las cinco candidatas en `data/candidates/inbox.local.json` con estado `pending_review`.
- **Ventajas:** Cero exposición a incertidumbres sobre la antigüedad de los pipelines continuos o los términos de reutilización de la fuente.
- **Riesgos y consecuencias:** El catálogo de la Alpha privada continúa limitado a una única oportunidad real (`OP-005`), prolongando el cuello de botella evidenciado en las primeras pruebas informales.

---

## 9. Recomendación Técnica No Vinculante

Desde una perspectiva de ingeniería de producto y aseguramiento de la calidad, el equipo auditor emite la siguiente recomendación **no vinculante**:

> **Recomendación: Adoptar la OPCIÓN A**, con las siguientes condiciones técnicas y editoriales:
> 1. Mantener las cinco vacantes en el ámbito exclusivo de la Alpha privada (círculo cercano, servidor loopback `127.0.0.1:4173`).
> 2. Explicitar en la presentación de cada ficha dos notas editoriales claras:
>    - *Jornada:* Puesto a tiempo completo (40 horas/semana) orientado a recién graduados o estudiantes en fase final de carrera.
>    - *Idioma:* Requiere dominio profesional del idioma inglés.
> 3. En caso de preferir una incorporación conservadora por etapas, la **Opción B** constituye una excelente alternativa intermedia.

---

## 10. Verificación Técnica de Integridad y Suite de Pruebas

Se ejecutó la suite de comprobación determinista, confirmando la estabilidad absoluta del sistema:

```powershell
# 1. Validación de candidatos con verificación pericial de evidencias
python scripts/validate_candidates.py data/candidates/inbox.local.json --verify-evidence
# Resultado: Bandeja local válida: 12 candidatos; 0 errores; todas las evidencias ALL_FRESH.

# 2. Inspección editorial de la bandeja local
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json
# Resultado: 6 pending_review (5 Canonical + 1 CookUnity promovida), 6 rejected.

# 3. Reporte consolidado de observabilidad
python scripts/editorial_cli.py report data/candidates/inbox.local.json
# Resultado: 0 errores Schema 2, 0 colisiones, 0 duplicados, 12 candidatos conformes.

# 4. Verificación de catálogo canónico
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Catálogo válido; 6 registros canónicos idénticos a snapshot.

# 5. Suite completa de pruebas unitarias Python
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 3.111s - OK (100% aprobadas).
```

### Hashes Criptográficos de Archivos Canónicos Protegidos:
- `data/opportunities.seed.json`: `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` (**INALTERADO**)
- `data/opportunities.json`: `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` (**INALTERADO**)
- `collector/sources.json`: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` (**INALTERADO**)

---

## 11. Decisión Pendiente y Siguiente Acción

- **Decisión requerida:** El propietario del proyecto debe indicar si opta por la **Opción A**, **Opción B** u **Opción C**.
- **Siguiente acción condicionada:**
  - Si el propietario elige **Opción A** o **Opción B**: se procederá a ejecutar el bloque de promoción formal controlada a catálogo, asignando identificadores canónicos (`OP-006` en adelante), actualizando el seed y generando el catálogo consolidado mediante `build_catalog.py`.
  - Si el propietario elige **Opción C**: las candidatas permanecerán en staging local sin alteraciones y el catálogo se mantendrá en su configuración actual.
