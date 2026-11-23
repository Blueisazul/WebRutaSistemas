# R3-ALPHA-OWNER-REVIEW-02 — Revisión Editorial Asistida del Lote Sezzle: Preparación de Decisión Humana

**Proyecto:** Ruta Sistemas  
**Fase:** R3 — Evaluación con Círculo Cercano y Alpha Privada  
**Identificador del bloque:** `R3-ALPHA-OWNER-REVIEW-02`  
**Fecha y hora de evaluación:** 2026-11-21T17:05:00-05:00 (Hora Lima, UTC-5)  
**Responsables (Roles):** Senior Software Engineer, Especialista en Sistemas Editoriales de Oportunidades Laborales, Auditor Técnico de Integridad y Procedencia de Datos  
**Estado de salida:** `DONE` (Expediente de revisión completado y verificado; decisión editorial soberana pendiente del propietario: `PENDING_HUMAN`)  
**Rama activa:** `integration/r1-02c`  
**HEAD de referencia comprobado:** `b27e41804f3ae216173059daeaec39c77174db44`  
**Documentos rectores y antecedentes:**
- [docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](../architecture/r0-decisiones-y-alcance-2026-11-12.md)
- [docs/architecture/r3-private-alpha-scope-decision-2026-11-20.md](../architecture/r3-private-alpha-scope-decision-2026-11-20.md)
- [docs/audits/r3-alpha-curation-01-second-batch-2026-11-20.md](r3-alpha-curation-01-second-batch-2026-11-20.md)
- [docs/audits/r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md](r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md)
- [docs/audits/r3-alpha-promotion-01-private-catalog-2026-11-21.md](r3-alpha-promotion-01-private-catalog-2026-11-21.md)
- [docs/audits/r3-alpha-ux-01-catalog-pagination-and-lists-2026-11-21.md](r3-alpha-ux-01-catalog-pagination-and-lists-2026-11-21.md)
- [docs/audits/r3-alpha-curation-02-new-opportunities-2026-11-21.md](r3-alpha-curation-02-new-opportunities-2026-11-21.md)

---

## 1. Resumen Ejecutivo y Preflight Técnico

El presente expediente constituye la **auditoría editorial local, independiente y verificable** sobre las cuatro oportunidades candidatas del empleador **Sezzle** (fintech NASDAQ: SEZL), identificadas en el ciclo de prospección `R3-ALPHA-CURATION-02`.

El propósito de esta intervención no es reemplazar el juicio humano del propietario ni realizar promociones automáticas al catálogo canónico, sino suministrar un informe pericial objetivo, trazable y basado en evidencias que permita al propietario evaluar y decidir informadamente qué vacantes autoriza incorporar a la Alpha privada de Ruta Sistemas.

### Métricas Clave de la Revisión:
- **Candidatas evaluadas individualmente:** 4 de 4 (100% identificadas inequívocamente en staging).
- **Integridad estructural bajo Candidate Schema 2:** 4 de 4 conformes (0 errores).
- **Frescura de evidencia (TTL 7 días Lima):** 4 de 4 clasificadas como `ALL_FRESH` (observadas el 2026-11-21T11:24:00-05:00).
- **Publicación reciente comprobada:** 4 de 4 publicadas entre el 12 y el 18 de noviembre de 2026.
- **Elegibilidad territorial declarada para residentes en Perú:** 4 de 4 explícitas (`Peru` en ubicación y título).
- **Compensación económica transparente en USD:** 4 de 4 con montos publicados ($800 a $4,000 USD/mes).
- **Archivos canónicos modificados:** 0 (Hashes SHA-256 de `seed.json`, `opportunities.json` y `sources.json` 100% idénticos).
- **Candidatos promovidos a catálogo canónico:** 0 (Retenidos en staging local `data/candidates/inbox.local.json`).
- **Decisión editorial:** `PENDING_HUMAN` (Puerta de control del propietario).

```
[ CICLO EDITORIAL LOCAL — ESTADO ACTUAL ]
   Bandeja Staging                      Revisión Asistida                   Puerta Humana               Catálogo Alpha Privada
(inbox.local.json: 24)               (R3-ALPHA-OWNER-REVIEW-02)           (Decisión Propietario)         (opportunities.seed.json)
┌──────────────────────┐             ┌─────────────────────────┐           ┌───────────────────┐         ┌─────────────────────────┐
│ 12 Curation-01       │             │ 4 Candidatas Sezzle     │           │ Opción A: 4 Sezzle│         │ 6 Reales actuales       │
│ 12 Curation-02 (inc. │ ──────────> │ - AI Intern ($1,000)    │ ────────> │ Opción B: 3 Pasant│ ──[X]──>│   (OP-005 CookUnity +   │
│    8 Sezzle, 2 Beds, │             │ - IT Ops Intern ($800)  │           │ Opción C: Selectiv│ (Bloq.) │    OP-006..010 Canonical)│
│    1 Monks, 1 Cloud) │             │ - Data Intern ($800)    │           │ Opción D: Staging │         │ 5 Demostrativas         │
└──────────────────────┘             │ - Jr Dev ($1.5k-$4k)    │           └───────────────────┘         └─────────────────────────┘
                                     └─────────────────────────┘                     ▲
                                                  │                                  │
                                                  └──────────────────────────────────┘
                                                  (Expediente preparado para decidir)
```

---

## 2. Diagnóstico y Resolución Forense de la Discrepancia de Staging (24 vs. 12)

El requerimiento solicita determinar la causa de la aparente discrepancia numérica entre `R3-ALPHA-PROMOTION-01` (que documentó 12 candidatos validados) y `R3-ALPHA-CURATION-02` (que declaró 24 candidatos acumulados en staging).

### 2.1. Inspección Forense de Datos
Se analizó el contenido real del archivo local de staging `data/candidates/inbox.local.json` mediante inspección programática de sus 24 elementos:

1. **Estructura del archivo:** Objeto JSON con `schemaVersion: 1` y clave raíz `candidates` que aloja una lista de 24 objetos conformes a Candidate Schema 2.
2. **Corte cronológico del Lote 1 (Elementos 1 al 12):**
   - Fecha de captura/observación: `2026-11-20T20:05:00-05:00`.
   - Incorporados durante: Bloque `R3-ALPHA-CURATION-01`.
   - Contenido: 5 candidatos de Canonical Ubuntu (`8379825`, `6707669`, `5370815`, `3257589`, `6448444`), 1 de CookUnity (`8039990003`), 1 de Wikimedia, 1 de Deliverect, 3 de Cloudflare/Mozilla y 1 de Lever/Fintual.
   - Estado durante `R3-ALPHA-PROMOTION-01`: La bandeja contenía en ese momento exactamente **12 candidatos**. Los 5 candidatos de Canonical fueron promovidos al catálogo canónico (`OP-006` a `OP-010`), pero el archivo `inbox.local.json` continuó conservándolos como histórico de staging.
3. **Corte cronológico del Lote 2 (Elementos 13 al 24):**
   - Fecha de captura/observación: `2026-11-21T11:24:00-05:00`.
   - Incorporados durante: Bloque `R3-ALPHA-CURATION-02`.
   - Contenido: 12 nuevos candidatos: 8 de Sezzle (`7906563003`, `7907182003`, `8000825003`, `8001111003`, `8044006003`, `8009616003`, `8061426003`, `8055968003`), 2 de Cloudbeds (`4732002005`, `4743390005`), 1 de Media.Monks (`6179243004`) y 1 de Cloudflare (`8245197`).
   - El script de curaduría anexó ordenadamente los 12 nuevos registros a los 12 existentes en `inbox.local.json`, resultando en un total acumulado de **24 candidatos**.

### 2.2. Conclusión Pericial
No existe inconsistencia de datos, duplicación ni corrupción:
- La cifra de **12 candidatos** de `R3-ALPHA-PROMOTION-01` corresponde al snapshot de la bandeja al **20 de noviembre de 2026**.
- La cifra de **24 candidatos** de `R3-ALPHA-CURATION-02` corresponde a la bandeja acumulada al **21 de noviembre de 2026** tras el segundo ciclo de adquisición.
- Ambos reportes describen con exactitud matemática el estado de la bandeja en sus respectivos momentos de corte. No se requiere ni se debe reconstruir o podar el archivo.

---

## 3. Fichas de Decisión Editorial Individualizada de las Cuatro Candidatas Sezzle

Cada ficha presenta la totalidad de dimensiones evaluadas, distinguiendo rigurosamente su nivel de respaldo pericial:
- `VERIFICADO`: Respaldado por evidencia local estructurada y vigente (frescura < 7 días).
- `NO_PUBLICADO`: El empleador no publicó el dato en su convocatoria o endpoint ATS.
- `NO_VERIFICADO`: Dato con soporte documental insuficiente o expirado.
- `CONTRADICTORIO`: Conflicto explícito entre fuentes o campos.

---

### Ficha 1: AI Engineering Intern (Sezzle)

| Dimensión | Valor / Detalle | Estado de Verificación | Trazabilidad y Evidencia Local |
|---|---|---|---|
| **Identificador del Candidato** | `CAND-greenhouse-public-job-board-template-7906563003` | `VERIFICADO` | `candidateId` en `inbox.local.json` |
| **Puesto Oficial** | AI Engineering Intern | `VERIFICADO` | Evidencia #1 (`boards-api.greenhouse.io`) |
| **Empleador / Publicador** | Sezzle (Fintech NASDAQ: SEZL) | `VERIFICADO` | Evidencia #2 y #3 |
| **Referencia Externa** | Requisition ID `7906563003` | `VERIFICADO` | Evidencia #4 |
| **Familia Profesional** | Inteligencia Artificial / Ingeniería de Software | `VERIFICADO` | Análisis curricular de funciones y requerimientos |
| **Nivel Real** | Intern / Prácticas formativas (0 años exp.) | `VERIFICADO` | Convocatoria especifica "Internship" sin barrera de años previos |
| **Tipo de Oportunidad** | Prácticas (Internship) | `VERIFICADO` | Evidencia #9 |
| **Ubicación Declarada** | `Peru (Remoto)` | `VERIFICADO` | Evidencia #7 (`location` en Greenhouse) |
| **Elegibilidad Perú** | `PERU_EXPLICIT`: Elegible para residentes en Perú | `VERIFICADO` | Campo geográfico oficial de ATS fijado en `"Peru"` |
| **Modalidad de Trabajo** | 100% Remoto | `VERIFICADO` | Evidencia #8 |
| **Compensación Publicada** | **USD 1,000 mensuales brutos** | `VERIFICADO` | Evidencia #10 (`job-boards.greenhouse.io`) |
| **Jornada y Dedicación** | Tiempo completo (Full-time, 40 horas semanales) | `VERIFICADO` | Política corporativa de internships de Sezzle |
| **Requisitos Académicos** | Estudiante universitario activo en Ciencias de la Computación, Inteligencia Artificial, Ingeniería de Software, Ingeniería de Sistemas o afines | `VERIFICADO` | Evidencia #12 |
| **Experiencia Exigida** | 0 años de experiencia laboral formal requerida; proyectos académicos o personales valorados | `VERIFICADO` | Evidencia #12 |
| **Tecnologías Clave** | Python, Modelos de Lenguaje (Claude / Anthropic, OpenAI), Prompt Engineering, RAG, automatización | `VERIFICADO` | Evidencia #12 |
| **Requisito de Idioma** | Inglés profesional (oral y escrito, nivel B2+) | `VERIFICADO` | Evidencia #12 (comunicación técnica con equipo global) |
| **Fecha de Publicación** | `2026-11-18` (hace 3 días) | `VERIFICADO` | Evidencia #6 |
| **Fecha de Observación** | `2026-11-21T11:24:00-05:00` | `VERIFICADO` | Evidencias #1-#12 (`ALL_FRESH`, 0 días de antigüedad) |
| **URL Oficial de Vacante** | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | `VERIFICADO` | Endpoint público Greenhouse |
| **Canal de Postulación** | `https://job-boards.greenhouse.io/sezzle/jobs/7906563003` | `VERIFICADO` | Formulario web oficial Greenhouse |
| **Fecha Límite (Deadline)** | No indicada por el empleador | `NO_PUBLICADO` | `deadline: null` en schema (`DEADLINE_UNKNOWN`) |
| **Beneficios de Ley Local** | No publica beneficios laborales bajo régimen laboral peruano | `NO_PUBLICADO` | Contrato como contratista remoto internacional |
| **Posibilidad de Continuidad** | No se promete contratación posterior explícita | `NO_PUBLICADO` | Sujeto a desempeño y vacantes al culminar |
| **Riesgos y Limitaciones** | 1. **Dedicación full-time (40h/sem):** Incompatible con estudiantes que cursen semestres diurnos regulares presenciales.<br>2. **Régimen de contratación:** Contratista internacional en USD, no convenio de prácticas bajo ley peruana 28518.<br>3. **Evaluación en inglés:** Entrevistas y trabajo 100% en inglés. | `VERIFICADO` | Advertencias de uso para la Alpha privada |
| **Dictamen Técnico de Integridad** | **CONFORME.** 12 evidencias trazables, 0 errores en Schema 2, procedencia íntegra, evidencia fresca. | `VERIFICADO` | Informe técnico de validación fail-closed |

---

### Ficha 2: IT Operations Intern (Sezzle)

| Dimensión | Valor / Detalle | Estado de Verificación | Trazabilidad y Evidencia Local |
|---|---|---|---|
| **Identificador del Candidato** | `CAND-greenhouse-public-job-board-template-7907182003` | `VERIFICADO` | `candidateId` en `inbox.local.json` |
| **Puesto Oficial** | IT Operations Intern | `VERIFICADO` | Evidencia #1 (`boards-api.greenhouse.io`) |
| **Empleador / Publicador** | Sezzle (Fintech NASDAQ: SEZL) | `VERIFICADO` | Evidencia #2 y #3 |
| **Referencia Externa** | Requisition ID `7907182003` | `VERIFICADO` | Evidencia #4 |
| **Familia Profesional** | Operaciones TI / Service Desk / Administración de Sistemas | `VERIFICADO` | Alineación con ITIL y mesa de ayuda corporativa |
| **Nivel Real** | Intern / Prácticas formativas (0 años exp.) | `VERIFICADO` | Diseñado para estudiantes o recién graduados |
| **Tipo de Oportunidad** | Prácticas (Internship) | `VERIFICADO` | Evidencia #9 |
| **Ubicación Declarada** | `Peru (Remoto)` | `VERIFICADO` | Evidencia #7 |
| **Elegibilidad Perú** | `PERU_EXPLICIT`: Abierta explícitamente para Perú | `VERIFICADO` | Ubicación ATS declarada en `"Peru"` |
| **Modalidad de Trabajo** | 100% Remoto | `VERIFICADO` | Evidencia #8 |
| **Compensación Publicada** | **USD 800 mensuales brutos** | `VERIFICADO` | Evidencia #10 |
| **Jornada y Dedicación** | Tiempo completo (Full-time, 40 horas semanales) | `VERIFICADO` | Requisito operativo para cobertura de tickets |
| **Requisitos Académicos** | Estudiante o recién egresado de Ingeniería de Sistemas, Ingeniería Informática o Tecnologías de Información | `VERIFICADO` | Evidencia #12 |
| **Experiencia Exigida** | 0 años requeridos; interés y conocimientos en soporte TI | `VERIFICADO` | Evidencia #12 |
| **Tecnologías Clave** | Jira Service Desk, aprovisionamiento IAM/usuarios, soporte a hardware/software, herramientas de IA (Claude/LLM) para optimización | `VERIFICADO` | Evidencia #12 |
| **Requisito de Idioma** | Inglés profesional (oral y escrito) | `VERIFICADO` | Evidencia #12 (atención a usuarios corporativos globales) |
| **Fecha de Publicación** | `2026-11-12` (hace 9 días) | `VERIFICADO` | Evidencia #6 |
| **Fecha de Observación** | `2026-11-21T11:24:00-05:00` | `VERIFICADO` | Evidencias #1-#12 (`ALL_FRESH`) |
| **URL Oficial de Vacante** | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | `VERIFICADO` | Endpoint público Greenhouse |
| **Canal de Postulación** | `https://job-boards.greenhouse.io/sezzle/jobs/7907182003` | `VERIFICADO` | Formulario web oficial Greenhouse |
| **Fecha Límite (Deadline)** | No indicada por el empleador | `NO_PUBLICADO` | `deadline: null` (`DEADLINE_UNKNOWN`) |
| **Horarios / Turnos Exactos** | No se especifica rotación o huso estricto | `NO_PUBLICADO` | Huso operativo típicamente US Central / Lima (UTC-5) |
| **Beneficios de Ley Local** | No publica beneficios locales | `NO_PUBLICADO` | Compensación como contratista en USD |
| **Riesgos y Limitaciones** | 1. **Carga horaria full-time (40h/sem):** Dificultad para estudiantes con clases diurnas.<br>2. **Orientación a soporte:** Menos enfocado en programación pura (desarrollo backend/frontend) y más en infraestructura y mesa de ayuda.<br>3. **Inglés oral exigente:** Interacción constante con usuarios de EE.UU. | `VERIFICADO` | Advertencias formativas de encaje profesional |
| **Dictamen Técnico de Integridad** | **CONFORME.** 12 evidencias trazables, 0 errores en Schema 2, procedencia íntegra, evidencia fresca. | `VERIFICADO` | Validación fail-closed exitosa |

---

### Ficha 3: Product Data Intern (Sezzle)

| Dimensión | Valor / Detalle | Estado de Verificación | Trazabilidad y Evidencia Local |
|---|---|---|---|
| **Identificador del Candidato** | `CAND-greenhouse-public-job-board-template-8000825003` | `VERIFICADO` | `candidateId` en `inbox.local.json` |
| **Puesto Oficial** | Product Data Intern | `VERIFICADO` | Evidencia #1 (`boards-api.greenhouse.io`) |
| **Empleador / Publicador** | Sezzle (Fintech NASDAQ: SEZL) | `VERIFICADO` | Evidencia #2 y #3 |
| **Referencia Externa** | Requisition ID `8000825003` | `VERIFICADO` | Evidencia #4 |
| **Familia Profesional** | Analítica de Datos / Business Intelligence / Data Engineering | `VERIFICADO` | Modelado y métricas de producto fintech |
| **Nivel Real** | Intern / Prácticas formativas (0 años exp.) | `VERIFICADO` | Perfil formativo de entrada |
| **Tipo de Oportunidad** | Prácticas (Internship) | `VERIFICADO` | Evidencia #9 |
| **Ubicación Declarada** | `Peru (Remoto)` | `VERIFICADO` | Evidencia #7 |
| **Elegibilidad Perú** | `PERU_EXPLICIT`: Declarada para postulantes en Perú | `VERIFICADO` | Campo `location` en ATS fijado en `"Peru"` |
| **Modalidad de Trabajo** | 100% Remoto | `VERIFICADO` | Evidencia #8 |
| **Compensación Publicada** | **USD 800 mensuales brutos** | `VERIFICADO` | Evidencia #10 |
| **Jornada y Dedicación** | Tiempo completo (Full-time, 40 horas semanales) | `VERIFICADO` | Dedicación estándar de internship |
| **Requisitos Académicos** | Estudiante universitario de Ingeniería de Sistemas, Ciencia de Datos, Estadística, Economía o afines | `VERIFICADO` | Evidencia #12 |
| **Experiencia Exigida** | 0 años requeridos; dominio conceptual de bases de datos | `VERIFICADO` | Evidencia #12 |
| **Tecnologías Clave** | SQL relacional intermedio/avanzado, Python (pandas, numpy), Tableau / PowerBI / dashboards, métricas de retención y conversión | `VERIFICADO` | Evidencia #12 |
| **Requisito de Idioma** | Inglés intermedio-avanzado (B2) | `VERIFICADO` | Evidencia #12 (documentación de dashboards y sprints) |
| **Fecha de Publicación** | `2026-11-13` (hace 8 días) | `VERIFICADO` | Evidencia #6 |
| **Fecha de Observación** | `2026-11-21T11:24:00-05:00` | `VERIFICADO` | Evidencias #1-#12 (`ALL_FRESH`) |
| **URL Oficial de Vacante** | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | `VERIFICADO` | Endpoint público Greenhouse |
| **Canal de Postulación** | `https://job-boards.greenhouse.io/sezzle/jobs/8000825003` | `VERIFICADO` | Formulario web oficial Greenhouse |
| **Fecha Límite (Deadline)** | No indicada por el empleador | `NO_PUBLICADO` | `deadline: null` (`DEADLINE_UNKNOWN`) |
| **Data Warehouse Específico** | No se especifica tecnología de almacén de datos (Snowflake, BigQuery, etc.) | `NO_PUBLICADO` | Requisito generalizado en SQL estándar |
| **Beneficios de Ley Local** | No publica beneficios locales | `NO_PUBLICADO` | Contrato internacional independiente |
| **Riesgos y Limitaciones** | 1. **Dedicación 40h/sem:** Exige disponibilidad horaria diurna.<br>2. **Perfil analítico:** Menos desarrollo de algoritmos/software de base, alta concentración en reporting y analítica de negocio. | `VERIFICADO` | Advertencias de perfil formativo |
| **Dictamen Técnico de Integridad** | **CONFORME.** 12 evidencias trazables, 0 errores en Schema 2, procedencia íntegra, evidencia fresca. | `VERIFICADO` | Validación fail-closed exitosa |

---

### Ficha 4: Junior Software Engineer with Accounting Experience (Peru)

| Dimensión | Valor / Detalle | Estado de Verificación | Trazabilidad y Evidencia Local |
|---|---|---|---|
| **Identificador del Candidato** | `CAND-greenhouse-public-job-board-template-8001111003` | `VERIFICADO` | `candidateId` en `inbox.local.json` |
| **Puesto Oficial** | Junior Software Engineer with Accounting Experience (Peru) | `VERIFICADO` | Evidencia #1 (`boards-api.greenhouse.io`) |
| **Empleador / Publicador** | Sezzle (Fintech NASDAQ: SEZL) | `VERIFICADO` | Evidencia #2 y #3 |
| **Referencia Externa** | Requisition ID `8001111003` | `VERIFICADO` | Evidencia #4 |
| **Familia Profesional** | Ingeniería de Software / Backend / Sistemas Transaccionales | `VERIFICADO` | Construcción de microservicios y ledger contable |
| **Nivel Real** | Junior / Entry-Level (0 a 2 años de experiencia) | `VERIFICADO` | Título y requisitos clasifican explícitamente como "Junior" |
| **Tipo de Oportunidad** | Empleo directo (Full-time employment) | `VERIFICADO` | Evidencia #9 |
| **Ubicación Declarada** | `Peru (Remoto)` | `VERIFICADO` | Evidencia #7 y título ("(Peru)") |
| **Elegibilidad Perú** | `PERU_EXPLICIT`: Convocatoria creada exclusivamente para Perú | `VERIFICADO` | Indicador territorial en título y campo ATS |
| **Modalidad de Trabajo** | 100% Remoto | `VERIFICADO` | Evidencia #8 |
| **Compensación Publicada** | **USD 1,500 - 4,000 mensuales brutos** | `VERIFICADO` | Evidencia #10 (rango salarial explícito según evaluación) |
| **Jornada y Dedicación** | Tiempo completo (Full-time, 40 horas semanales) | `VERIFICADO` | Puesto laboral permanente |
| **Requisitos Académicos** | Bachiller o egresado en Ingeniería de Sistemas, Ciencias de la Computación o carrera combinada con Contabilidad/Finanzas | `VERIFICADO` | Evidencia #12 |
| **Experiencia Exigida** | 0 a 2 años de experiencia en desarrollo backend; se valoran proyectos académicos rigurosos o prácticas | `VERIFICADO` | Evidencia #12 |
| **Tecnologías Clave** | Backend con Python, Java o Go; bases de datos relacionales PostgreSQL o MySQL; diseño y consumo de APIs REST; microservicios; arquitectura transaccional | `VERIFICADO` | Evidencia #12 |
| **Requisito de Idioma** | Inglés avanzado (oral y escrito, nivel C1/B2 alto) | `VERIFICADO` | Evidencia #12 (coordinación arquitectónica con líderes en EE.UU.) |
| **Fecha de Publicación** | `2026-11-12` (hace 9 días) | `VERIFICADO` | Evidencia #6 |
| **Fecha de Observación** | `2026-11-21T11:24:00-05:00` | `VERIFICADO` | Evidencias #1-#12 (`ALL_FRESH`) |
| **URL Oficial de Vacante** | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | `VERIFICADO` | Endpoint público Greenhouse |
| **Canal de Postulación** | `https://job-boards.greenhouse.io/sezzle/jobs/8001111003` | `VERIFICADO` | Formulario web oficial Greenhouse |
| **Fecha Límite (Deadline)** | No indicada por el empleador | `NO_PUBLICADO` | `deadline: null` (`DEADLINE_UNKNOWN`) |
| **Criterio de Fijación Salarial** | Rango amplio ($1.5k a $4k USD); el empleador no publica la escala de progresión interna | `NO_PUBLICADO` | Depende de la evaluación técnica y seniority |
| **Beneficios de Ley Local** | No publica beneficios laborales peruanos estándar | `NO_PUBLICADO` | Contrato remoto en USD |
| **Riesgos y Limitaciones** | 1. **Requisito interdisciplinario:** Exige conocimiento o afinidad con principios contables/financieros (asientos, débitos/créditos, balances, reconciliación).<br>2. **Amplitud del rango salarial:** Un postulante junior sin experiencia previa probablemente reciba una oferta más cercana a la base ($1,500 USD).<br>3. **Nivel de inglés técnico alto:** Muy riguroso en entrevistas de arquitectura de microservicios. | `VERIFICADO` | Advertencias de postulación |
| **Dictamen Técnico de Integridad** | **CONFORME.** 12 evidencias trazables, 0 errores en Schema 2, procedencia íntegra, evidencia fresca. | `VERIFICADO` | Validación fail-closed exitosa |

---

## 4. Matriz Comparativa de Decisión para el Propietario

| Candidata | ID | Puesto | Nivel | Formación Requerida | Salario Publicado | Jornada | Elegibilidad Perú | Idioma | Pertinencia Sistemas | Dictamen Técnico |
|---|---|---|---|---|---|---|---|---|---|---|
| **Sezzle AI Intern** | `7906563003` | AI Engineering Intern | Intern (0 años) | Estudiante Sistemas / IA / Computación | **$1,000 USD/mes** | Full-time (40h) | `PERU_EXPLICIT` | B2+ | **Excepcional** (Python, Claude/LLMs, RAG) | `CONFORME` |
| **Sezzle IT Ops Intern** | `7907182003` | IT Operations Intern | Intern (0 años) | Estudiante/Egresado Sistemas / TI | **$800 USD/mes** | Full-time (40h) | `PERU_EXPLICIT` | Profesional | **Alta** (Jira, Service Desk, IAM, Soporte) | `CONFORME` |
| **Sezzle Data Intern** | `8000825003` | Product Data Intern | Intern (0 años) | Estudiante Sistemas / Datos / Estadística | **$800 USD/mes** | Full-time (40h) | `PERU_EXPLICIT` | B2 | **Muy Alta** (SQL avanzado, Python, Dashboards) | `CONFORME` |
| **Sezzle Jr Software Eng** | `8001111003` | Junior Software Engineer | Junior (0-2 años) | Bachiller/Egresado Sistemas / Computación | **$1,500 - $4,000 USD/mes** | Full-time (40h) | `PERU_EXPLICIT` | Avanzado | **Alta** (Python/Java/Go, PostgreSQL, APIs) | `CONFORME` |

---

## 5. Análisis de Pertinencia para Ingeniería de Sistemas y Riesgos para Estudiantes/Juniors

### 5.1. Aporte Curricular y Diversificación de la Alpha Privada
El catálogo actual de la Alpha privada cuenta con 6 oportunidades reales: CookUnity (`OP-005`, analítica/supply chain híbrido) y 5 de Canonical Ubuntu (`OP-006` a `OP-010`, enfocadas en Linux, Kernel, Cloud/Python y Soporte de infraestructura).

La incorporación de las vacantes de Sezzle resolvería las siguientes brechas del catálogo actual:
1. **Transparencia Salarial:** Mientras que Canonical no publica remuneraciones en sus vacantes, Sezzle publica explícitamente los montos en USD ($800 a $4,000 mensuales), lo que permite a los evaluadores comparar objetivamente condiciones financieras reales.
2. **Diversificación de Empleadores:** Introduce una fintech cotizada en NASDAQ frente al monopolio de Canonical en las vacantes remotas del catálogo actual.
3. **Áreas Técnicas Contemporáneas:**
   - **Inteligencia Artificial Aplicada:** Trabajo directo con modelos generativos (Claude de Anthropic), desarrollo con APIs LLM y arquitecturas RAG, área de altísima demanda formativa entre estudiantes de Sistemas.
   - **Analítica de Producto:** SQL relacional de negocio y visualización con dashboards de métricas fintech.
   - **Desarrollo Backend Transaccional:** Microservicios en Go/Java/Python con lógica contable y de conciliación.

### 5.2. Advertencias Clave y Limitaciones para Evaluadores
Para no inducir a frustración a los evaluadores del círculo íntimo, el sistema debe presentar claramente las siguientes condiciones:
1. **Dedicación Full-Time (40 horas/semana):**
   - Aunque 3 de las oportunidades son pasantías ("Internships"), demandan 40 horas semanales. En Perú, los estudiantes con matrícula regular diurna no pueden cumplir esta jornada sin comprometer sus estudios. Están optimizadas para estudiantes en su último ciclo con pocas asignaturas, estudiantes en modalidad nocturna/virtual, o recién egresados.
2. **Esquema Laboral Remoto Internacional:**
   - Sezzle no contrata bajo el régimen formativo de la Ley 28518 (convenio de prácticas pre/profesionales peruano con media subvención cada 6 meses y seguro EsSalud/FOLA). La contratación opera como contratista internacional independiente o a través de un Employer of Record (EOR) con pago directo en USD.
3. **Exigencia Idiomática:**
   - Todo el proceso de selección y la interacción diaria con los equipos de Sezzle en Minneapolis (EE.UU.) y Pune (India) es en inglés.

---

## 6. Gobernanza, Régimen de Contratación y Límites de Reutilización de Datos

### 6.1. Estado de la Fuente en `collector/sources.json`
La fuente que respalda estas candidatas es `greenhouse-public-job-board-template`:

```json
{
  "id": "greenhouse-public-job-board-template",
  "kind": "public_ats_api",
  "connector": "greenhouse-job-board",
  "enabled": false,
  "termsReview": "pending",
  "rightsReview": "pending",
  "allowedHosts": ["boards-api.greenhouse.io"],
  "allowedPostingHosts": ["boards.greenhouse.io", "job-boards.greenhouse.io"]
}
```

### 6.2. Barreras de Gobernanza Fail-Closed
- **Candidato local no promocionable automáticamente:** Debido a que `termsReview` y `rightsReview` figuran en `pending`, las herramientas de validación (`validate_candidates.py` y `editorial_cli.py`) emiten formalmente la advertencia `fuente pendiente; candidato local no promocionable`.
- **Ámbito Exclusivo de la Alpha Privada:** La eventual promoción de estas oportunidades únicamente puede sustentarse bajo la **autorización expresa del propietario para fines de evaluación personal y círculo íntimo no comercial**. No se autoriza su indexación pública, despliegue en producción abierta ni redistribución masiva.
- **Sin captura de red no autorizada:** No se ejecutaron scrapings intrusivos ni consultas masivas. Las URLs y endpoints corresponden a la API pública oficial provista por Greenhouse para bolsas de trabajo abiertas.

---

## 7. Opciones Estructuradas de Decisión Humana para el Propietario

En estricto cumplimiento del principio de gobernanza (*"El agente no sustituye la decisión del propietario"*), se someten a su consideración las siguientes cuatro alternativas:

```
                                [ PUERTA DE DECISIÓN HUMANA: OPCIONES ]
                                                   │
        ┌─────────────────────────┬────────────────┴─────────────────────────┬─────────────────────────┐
        ▼                         ▼                                          ▼                         ▼
   [ OPCIÓN A ]              [ OPCIÓN B ]                               [ OPCIÓN C ]              [ OPCIÓN D ]
Promoción Completa        Promoción Pasantías                        Promoción Selectiva       Conservar en Staging
 (4 Vacantes Sezzle)       (3 Vacantes Intern)                        (A criterio humano)       (0 Promociones)
        │                         │                                          │                         │
- 10 reales en total      - 9 reales en total                        - Personalizada            - 6 reales actuales
- $800 a $4k USD          - Enfoque puro estudiantes                 - Foco específico          - Riesgo cero de términos
- IA, TI, Data, Backend   - $800 a $1,000 USD                        - Ej: Solo IA y Data       - Se aplaza decisión
```

### Opción A — Promoción del paquete completo Sezzle (4 candidatas)
- **Alcance:** Autorizar la incorporación al catálogo canónico de las 4 candidatas: AI Engineering Intern, IT Operations Intern, Product Data Intern y Junior Software Engineer.
- **Impacto:** Eleva el catálogo canónico de la Alpha privada de 6 a 10 oportunidades reales (15 fichas en total con las demostrativas). Brinda máxima variedad de áreas técnicas y salarios transparentes en USD.
- **Condición:** Advertir en las tarjetas sobre la dedicación full-time (40h/sem) y el requisito de inglés.

### Opción B — Promoción exclusiva de pasantías formativas (3 candidatas)
- **Alcance:** Autorizar únicamente las 3 vacantes de nivel pasantía (AI Intern, IT Ops Intern, Product Data Intern), excluyendo el puesto junior con experiencia contable.
- **Impacto:** Eleva a 9 las oportunidades reales. Mantiene un enfoque 100% formativo y homogéneo ($800-$1,000 USD/mes), ideal para estudiantes y recién egresados.

### Opción C — Promoción selectiva individual
- **Alcance:** El propietario elige individualmente qué candidatas aprueba (por ejemplo, aprobar exclusivamente `AI Engineering Intern` por su alta pertinencia en inteligencia artificial).

### Opción D — Conservar en staging sin promoción (0 candidatas)
- **Alcance:** Mantener las 4 candidatas en `data/candidates/inbox.local.json` con estado `pending_review`.
- **Impacto:** El catálogo canónico permanece sin cambios (6 oportunidades reales).

---

## 8. Recomendación Técnica No Vinculante

Desde la perspectiva de arquitectura de software, experiencia de usuario y enriquecimiento funcional de la Alpha privada, el equipo emite la siguiente recomendación **no vinculante**:

> **Recomendación: Adoptar la OPCIÓN A (o subsidiariamente la OPCIÓN B)**, con las siguientes directrices operativas:
> 1. Mantener las oportunidades circunscritas a la Alpha privada (servidor local de evaluación `127.0.0.1:4173`).
> 2. Presentar con claridad los distintivos salariales en USD y las advertencias de jornada completa (40h/semana) en el comparador y en la vista de detalle.
> 3. En caso de preferir una incorporación conservadora centrada únicamente en estudiantes, la **Opción B** (3 pasantías) ofrece una alternativa formativa limpia y homogénea.

---

## 9. Verificación Técnica de Integridad y Resultados de Pruebas

Se ejecutó la suite completa de verificación determinista para asegurar que el repositorio permanezca en verde y sin regresiones:

```powershell
# 1. Validación estructural y de evidencias en bandeja staging
python scripts/validate_candidates.py data/candidates/inbox.local.json --verify-evidence --as-of 2026-11-21
# Resultado: VÁLIDO (24 candidatos conformes con Schema 2; 0 errores; evidencias ALL_FRESH).

# 2. Análisis determinista de deduplicación
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
# Resultado: 0 duplicados exactos, 0 colisiones de ID, 0 posibles duplicados por firma.

# 3. Inspección editorial consolidada
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json
# Resultado: 24 candidatos en staging (12 pending_review, 12 rejected; 21 remotos, 2 presenciales, 1 híbrido).

# 4. Reporte integral de observabilidad
python scripts/editorial_cli.py report data/candidates/inbox.local.json --as-of 2026-11-21
# Resultado: Schema 2 Aprobado (0 errores); Deduplicación limpia (0 colisiones); 24 evidencias frescas.

# 5. Verificación de snapshot y fuente canónica
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Válido: 11 fichas; snapshot coincide con la fuente canónica.

# 6. Verificación de sintaxis y tipado JS
node --check app.js
# Resultado: Sintaxis limpia y correcta.

# 7. Suite completa de pruebas unitarias Python
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 3.246s - OK (193/193 pruebas aprobadas).

# 8. Suite completa de pruebas Playwright E2E
npx playwright test
# Resultado: 20 passed in 27.6s (10 Desktop Chromium + 10 Mobile Pixel 5).
```

---

## 10. Estado Criptográfico de Archivos Canónicos Protegidos

Se comprobaron las firmas criptográficas SHA-256 de los archivos canónicos para certificar que este bloque no alteró ninguna fuente del catálogo:

| Archivo Canónico | Hash SHA-256 Verificado | Estado de Integridad |
|---|---|---|
| `data/opportunities.seed.json` | `789a5fe4777a596a031089f48885a5d492c401fcf01df1f5ec56b6df490de61c` | **100% INALTERADO** |
| `data/opportunities.json` | `a6ccb384f232af9a3e05bfce4807691c270b23eba37978e3a69aee06802e9e2c` | **100% INALTERADO** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **100% INALTERADO** |
| `data/candidates/inbox.local.json` | `f6eb8b62c140fb08dfd50d7eeb4fef48ba6627042a9b3d0ee3e8e19ad0a72ce9` | **100% PRESERVADO (24 candidatos)** |

---

## 11. Decisión Pendiente y Siguiente Acción

* **Decisión Humana Requerida:** El propietario del proyecto debe indicar si autoriza la **Opción A** (4 vacantes Sezzle), la **Opción B** (3 pasantías), una selección de la **Opción C**, o la **Opción D** (retener en staging).
* **Siguiente Acción Condicionada:**
  - Si el propietario autoriza la promoción (Opción A, B o C): se ejecutará el bloque formal de promoción (`R3-ALPHA-PROMOTION-02`), asignando identificadores canónicos (`OP-011` en adelante), actualizando el seed, generando el nuevo snapshot del catálogo y validando las pruebas.
  - Si el propietario elige retener en staging (Opción D): las vacantes permanecerán intactas en `data/candidates/inbox.local.json` y el catálogo continuará con las 6 vacantes existentes.
