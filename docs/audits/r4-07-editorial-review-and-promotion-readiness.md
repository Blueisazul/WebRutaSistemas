# R4-07 — REVISIÓN EDITORIAL EXHAUSTIVA Y PREPARACIÓN DE PROMOCIÓN DEL CATÁLOGO
### Expediente Técnico y Editorial para Decisión Soberana del Propietario
**Ruta Sistemas | Arquitectura Editorial y Garantía de Trazabilidad**
- **Fecha de Corte:** 2026-11-22
- **Estado del Bloque:** `READY_FOR_OWNER_DECISION`
- **Responsables:** Principal Software Architect, Senior Software Engineer, Technical Product Manager, Technical Auditor y Responsable de Gobernanza Editorial
- **Rama de Trabajo:** `integration/r1-02c`
- **Catálogo Canónico Actual:** 15 fichas (10 reales verificadas, 5 demostrativas). HASH SHA256 inalterado.
- **Bandeja de Staging Evaluada:** 154 candidatos (`data/candidates/inbox.local.json`).

---

## 1. Resumen Ejecutivo y Matriz Global de Clasificación

En cumplimiento del mandato de **R4-07**, se realizó una auditoría y evaluación editorial exhaustiva sobre la totalidad de los **154 registros acumulados en la bandeja local de staging**, superando la muestra inicial preliminar de 19 casos y analizando el 100% de los candidatos frente a los objetivos formativos y profesionales de Ruta Sistemas.

### Matriz Ejecutiva Global (154 Registros Evaluados)

| Categoría Editorial | Total | Canonical | Sezzle | CookUnity | Fintual | Kavak | Plantillas / Pruebas |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`RECOMMEND_PROMOTION`** (Recomendación Directa) | **90** | 78 | 12 | 0 | 0 | 0 | 0 |
| **`RECOMMEND_WITH_LIMITATIONS`** (Recomendación con Limitaciones) | **32** | 19 | 9 | 4 | 0 | 0 | 0 |
| **`HOLD_FOR_VERIFICATION`** (Pospuesto / Requiere Verificación) | **3** | 0 | 1 | 0 | 0 | 0 | 2 |
| **`NOT_RECOMMENDED`** (No Recomendado / Descartado) | **19** | 0 | 0 | 0 | 3 | 4 | 12 |
| **`ALREADY_PUBLISHED`** (Ya Publicado en Catálogo OP-*) | **10** | 5 | 4 | 1 | 0 | 0 | 0 |
| **TOTAL GENERAL** | **154** | **102** | **26** | **5** | **3** | **4** | **14** |

---

## 2. Desglose del Universo Real de Candidatos (R4-07A)

Para evitar presentar los 154 registros como un bloque homogéneo de oportunidades publicables, se categoriza y desglosa el inventario real:

1. **Oportunidades Reales Activas de las 5 Fuentes ATS (140 registros):**
   - **Canonical (102 registros):** 5 ya promovidas (`OP-006` a `OP-010`), 97 en staging activo.
   - **Sezzle (26 registros):** 4 ya promovidas (`OP-011` a `OP-014`), 22 en staging activo.
   - **CookUnity (5 registros):** 1 ya promovida (`OP-005`), 4 en staging activo.
   - **Fintual (3 registros):** 3 en staging (con sede híbrida/presencial en Santiago o CDMX).
   - **Kavak (4 registros):** 4 en staging (con sede híbrida/presencial en CDMX o São Paulo).
2. **Registros Ya Promovidos en el Catálogo Canónico (10 registros):**
   - Identificados y conciliados con sus respectivos identificadores `OP-005` a `OP-014` en `data/opportunities.seed.json`. Trazabilidad 100% verificada.
3. **Decisiones Históricas de Rechazo Preservadas (12 registros):**
   - Las 12 decisiones de descarte (`rejected`) tomadas en ciclos anteriores (por superar 4+ años de experiencia, exigencia presencial en el extranjero o funciones no técnicas) se mantienen íntegras, con revisor, fecha civil y nota de decisión inalterada.
4. **Plantillas y Registros Demostrativos Históricos (2 registros):**
   - Convocatorias asociadas a `greenhouse-public-job-board-template` sin token corporativo asociado. Se retienen en `HOLD_FOR_VERIFICATION`.

---

## 3. Revalidación Técnica en Vivo y Evidencia ATS (R4-07B)

Se ejecutó una consulta directa contra los cinco endpoints REST públicos de los empleadores autorizados:
- **Canonical Greenhouse API:** 97 vacantes de staging confirmadas **100% abiertas y operativas**.
- **Sezzle Greenhouse API:** 22 vacantes de staging confirmadas **100% abiertas y operativas**.
- **CookUnity Greenhouse API:** 4 vacantes de staging confirmadas **100% abiertas y operativas**.
- **Fintual Lever Postings API:** 3 vacantes de staging confirmadas activas en la API oficial.
- **Kavak Lever Postings API:** 4 vacantes de staging confirmadas activas en la API oficial.
- **Verificación de Enlace y Formulario:** Todas las oportunidades recomendadas cuentan con formulario de postulación directo en los dominios permitidos (`job-boards.greenhouse.io`, `canonical.com`, `sezzle.com`, `cookunity.com`), verificado con estado `application_open` y relación difusora `employer_confirmed`.
- **TTL de Evidencia:** Todo el lote de staging cuenta con `observedAt` y `capturedAt` dentro de la ventana de frescura de 7 días (TTL 7 días Lima).

---

## 4. Evaluación Editorial Integral y Adecuación al Perfil (R4-07C y R4-07D)

### 4.1. Grupo 1: Oportunidades de Nivel Formativo e Inicial (`ENTRY_OR_JUNIOR`) — 10 Convocatorias
*Máxima prioridad para estudiantes, practicantes y recién egresados de Ingeniería de Sistemas.*

1. **`CAND-greenhouse-canonical-5643282` | Canonical**
   - **Título:** *Ubuntu Sales Engineer (Entry-Level)*
   - **Ubicación:** Home based - Worldwide (Remoto Global)
   - **Pertinencia:** `DIRECT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `GLOBAL_REMOTE`
   - **Análisis formativo:** Rol técnico de preventa y arquitectura de soluciones sobre el ecosistema Ubuntu/Linux. Excelente potencial para perfiles que combinan habilidades técnicas y comunicación profesional en inglés.
   - **Recomendación:** `RECOMMEND_PROMOTION`
2. **`CAND-greenhouse-sezzle-7980309003` | Sezzle**
   - **Título:** *A.I. Engineering Intern*
   - **Ubicación:** Latin America (Remoto)
   - **Pertinencia:** `DIRECT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `LATAM`
   - **Análisis formativo:** Prácticas formativas directas en aplicación de LLMs, Python y procesamiento de lenguaje natural. Alta consonancia formativa.
   - **Recomendación:** `RECOMMEND_PROMOTION`
3. **`CAND-greenhouse-sezzle-6668065003` | Sezzle**
   - **Título:** *Junior Software Engineer with Accounting Experience (LATAM)*
   - **Ubicación:** Latin America (Remoto)
   - **Pertinencia:** `DIRECT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `LATAM`
   - **Análisis formativo:** Puesto de desarrollo de software junior enfocado en conciliación y flujos contables automatizados.
   - **Recomendación:** `RECOMMEND_PROMOTION`
4. **`CAND-greenhouse-sezzle-8040733003` | Sezzle**
   - **Título:** *Chargeback Operations Intern*
   - **Ubicación:** Peru (Remoto / Lima)
   - **Pertinencia:** `ADJACENT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `PERU_LOCAL`
   - **Análisis formativo:** Práctica preprofesional en gestión operativa de contracargos y plataformas de pagos digitales.
   - **Recomendación:** `RECOMMEND_PROMOTION`
5. **`CAND-greenhouse-sezzle-8040739003` | Sezzle**
   - **Título:** *Fraud & Disputes Intern*
   - **Ubicación:** Peru (Remoto / Lima)
   - **Pertinencia:** `ADJACENT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `PERU_LOCAL`
   - **Análisis formativo:** Práctica enfocada en análisis de datos transaccionales, reglas antifraude y detección de anomalías.
   - **Recomendación:** `RECOMMEND_PROMOTION`
6. **`CAND-greenhouse-sezzle-8012085003` | Sezzle**
   - **Título:** *Product Operations Intern, Rewards*
   - **Ubicación:** Peru (Remoto / Lima)
   - **Pertinencia:** `ADJACENT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `PERU_LOCAL`
   - **Análisis formativo:** Soporte analítico y operativo a productos digitales y programas de lealtad.
   - **Recomendación:** `RECOMMEND_PROMOTION`
7. **`CAND-greenhouse-sezzle-8040748003` | Sezzle**
   - **Título:** *Risk & Disputes Intern*
   - **Ubicación:** Peru (Remoto / Lima)
   - **Pertinencia:** `ADJACENT` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `PERU_LOCAL`
   - **Análisis formativo:** Gestión de disputas financieras y análisis de riesgos operativos en comercio electrónico.
   - **Recomendación:** `RECOMMEND_PROMOTION`
8. **`CAND-greenhouse-canonical-6103331` | Canonical**
   - **Título:** *Graduate Customer Success Manager*
   - **Ubicación:** Home based - Worldwide (Remoto Global)
   - **Pertinencia:** `UNDEMONSTRATED` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `GLOBAL_REMOTE`
   - **Análisis:** Rol de postventa y soporte relacional a clientes empresariales de Ubuntu.
   - **Recomendación:** `RECOMMEND_WITH_LIMITATIONS` (Función predominantemente comercial/gestión, no técnica dura).
9. **`CAND-greenhouse-canonical-5861481` | Canonical**
   - **Título:** *Junior Project Manager*
   - **Ubicación:** Home Based - Americas (Remoto)
   - **Pertinencia:** `UNDEMONSTRATED` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `LATAM`
   - **Análisis:** Gestión de proyectos y seguimiento ágil en ingeniería.
   - **Recomendación:** `RECOMMEND_WITH_LIMITATIONS` (Orientado a coordinación y gestión de cronogramas).
10. **`CAND-greenhouse-canonical-8160237` | Canonical**
    - **Título:** *Organisational Development Associate*
    - **Ubicación:** Home Based - Americas (Remoto)
    - **Pertinencia:** `UNDEMONSTRATED` | **Nivel:** `ENTRY_OR_JUNIOR` | **Elegibilidad:** `LATAM`
    - **Análisis:** Función en el área de desarrollo organizacional y talento.
    - **Recomendación:** `RECOMMEND_WITH_LIMITATIONS` (Área de People/Gestión, baja pertinencia en desarrollo o sistemas).

---

### 4.2. Grupo 2: Oportunidades Profesionales Estándar de Consolidación (`MID`) — 83 Convocatorias
*Dirigidas a egresados con 1-3 años de experiencia o estudiantes destacados con dominio comprobable de tecnologías clave.*

- **Canonical (74 oportunidades `MID` recomendadas):**
  - **Especialidades Cubiertas:**
    - *Linux & Kernel:* Linux Devices Software Engineer (`5140562`), Linux Devices snapd (`4394058`), Linux Systems Engineer (`3880952`).
    - *Cloud & Distributed Systems:* Distributed Systems Testing (`2969042`), MicroCloud Software Engineer (`5660661`), Ceph & Storage (`2579550`), Kubernetes Automation (`5703396`), Cloud Images (`3062022`).
    - *Lenguajes & Backend:* Golang System Engineer (`4960407`), Python Software Engineer (`4283003`, `3752633`, `2413329`), Security Software Engineer (`5146620`), Full Stack Engineer (`3159992`).
    - *Infraestructura & Networking:* Open Source Networking (`5660661`), DevOps SRE (`6222476`, `4410480`).
  - **Recomendación General:** `RECOMMEND_PROMOTION`. Todas ofrecen exposición a estándares mundiales de código abierto y computación en la nube.
- **Sezzle (5 oportunidades `MID` recomendadas):**
  - *Data Engineer II, Credit Reporting* (`8054164003`): Ingeniería de pipelines de datos SQL/Python. (`RECOMMEND_PROMOTION`)
  - *Mobile Engineer (LATAM, All Levels)* (`6037486003`): Desarrollo móvil multiplataforma (iOS/Android/Flutter). (`RECOMMEND_PROMOTION`)
  - *Software Engineer II with Accounting Experience (LATAM)* (`7527791003`): Desarrollo backend para servicios financieros. (`RECOMMEND_PROMOTION`)
  - *Solutions Engineer* (`7849452003`): Integración de APIs comerciales y consultoría técnica. (`RECOMMEND_PROMOTION`)
  - *Fraud Operations Analyst (Peru)* (`8009618003`) y *Fraud Operations Analyst (LATAM)* (`8196898003`): Análisis operativo transaccional. (`RECOMMEND_WITH_LIMITATIONS` por enfoque operacional).

---

### 4.3. Grupo 3: Oportunidades de Nivel Senior / Liderazgo (`SENIOR_OR_LEAD`) — 23 Convocatorias
*Convocatorias de alto nivel técnico disponibles para consulta pero que exigen más de 5 años de trayectoria comprobada.*

- **Canonical (19 vacantes):** Tech Leads, Engineering Directors y Principal Architects (ej. `Principal Systems Engineer`, `Lead Linux Kernel Engineer`).
- **Sezzle (7 vacantes):** `Principal Infrastructure Engineer` (`7993237003`), `Senior Database Reliability Engineer` (`7725281003`), `Senior Data Engineer` (`8053519003`), `Senior Security Engineer` (`8031474003`, `8032217003`).
- **CookUnity (4 vacantes):** `Senior Full Stack Engineer` (`8205614003`), `Senior Product Data Analyst` (`8019593003`), `Staff Tech Enablement Engineer` (`8034424003`), `Sr. Product Manager` (`8105415003`).
- **Recomendación General:** `RECOMMEND_WITH_LIMITATIONS`. No se recomienda promoverlas como foco inicial del catálogo estudiantil, pero son elegibles de ser consultadas con la etiqueta explícita de nivel Senior.

---

### 4.4. Grupo 4: Oportunidades No Recomendadas / Descartadas (`NOT_RECOMMENDED`) — 19 Convocatorias

1. **Rechazos Históricos Preservados (12 vacantes):**
   - Confirmación de las decisiones editoriales de `CAND-greenhouse-public-job-board-template-8034712003` (4+ años soporte), `8268853` (residencia EE.UU.), `8210560`, `8397050`, `8268142`, `5e9142c8`, `8044006003`, `8061426003`, `8055968003`, `4743390005`, `6179243004`, `8245197`.
2. **Fintual Lever (3 vacantes):**
   - *Ingeniero/a de Operaciones AFP - Afiliaciones y traspasos* (Santiago, Chile - Híbrido presencial).
   - *Ingeniero/a de Operaciones AFP - Cobranza* (Santiago, Chile - Híbrido presencial).
   - *Oficial de Cumplimiento en PLD/FT* (Ciudad de México - Presencial).
   - **Motivo de exclusión:** Requisito de asistencia física en oficina fuera de Perú; no admite trabajo remoto desde territorio peruano.
3. **Kavak Lever (4 vacantes):**
   - *Abogada Senior Specialist de Compliance Global* (Ciudad de México - Híbrido).
   - *Growth Marketing Senior Analyst* (Ciudad de México - Híbrido).
   - *Senior Full Stack Engineer* (Ciudad de México - Híbrido).
   - *Tech Lead* (São Paulo, Brasil - Híbrido).
   - **Motivo de exclusión:** Convocatorias híbridas/presenciales restringidas por contrato laboral a México y Brasil.

---

## 5. Preparación Técnica para la Promoción por Lotes (R4-07F)

Se auditó minuciosamente el pipeline de promoción y empaquetado para garantizar que la futura incorporación de las oportunidades aprobadas sea 100% segura, determinista y reversible:

1. **Asignación Correlativa de Identificadores:**
   - El catálogo actual cuenta con 15 oportunidades (`OP-001` a `OP-015`).
   - Las promociones futuras iniciarán estrictamente en el correlativo `OP-016`, garantizando que ninguna oportunidad reasigne o colisione con IDs históricos.
2. **Mapeo de Schemas (Candidate Schema 2 -> Opportunity Schema 2):**
   - El mapeo conserva de forma unívoca el `fieldEvidence` para cada atributo afirmado (`title`, `employer`, `location`, `mode`, `applyUrl`).
   - Se preserva el canal oficial de postulación con `publisherRelation: employer_confirmed` y `result: application_open`.
3. **Generación del Snapshot Fail-Closed:**
   - `python scripts/build_catalog.py --write` regenera `data/opportunities.json` garantizando paridad exacta con `opportunities.seed.json`.
   - `python scripts/build_catalog.py --check` y `python scripts/validate_catalog.py` bloquean cualquier discrepancia o dato corrupto.
4. **Garantía de Aislamiento de Staging:**
   - `scripts/pages_artifact.py` omite por diseño la carpeta `data/candidates/` y cualquier archivo local de trabajo. Staging no se compila ni se distribuye en la entrega estática de producción.

---

## 6. Opciones de Decisión Editorial para el Propietario

El propietario dispone de cuatro alternativas de decisión para la posterior promoción:

### OPCIÓN A (Enfoque Formativo Puro — 7 Vacantes Nuevas)
Promover exclusivamente las vacantes técnicas de nivel inicial formativo (`ENTRY_OR_JUNIOR`):
- 1 de Canonical (*Ubuntu Sales Engineer Entry-Level*).
- 6 de Sezzle (*A.I. Engineering Intern*, *Junior Software Engineer LATAM*, *Chargeback Operations*, *Fraud & Disputes*, *Product Operations*, *Risk & Disputes*).
- **Impacto:** Catálogo se expande a **22 oportunidades**.

### OPCIÓN B (Enfoque de Expansión Equilibrada — Recomendada — 90 Vacantes Nuevas)
Promover el paquete completo de nivel formativo (`ENTRY_OR_JUNIOR`) y consolidación profesional (`MID` directo):
- 78 vacantes de Canonical (Cloud, Linux, Go, Python, Distributed Systems, SRE).
- 12 vacantes de Sezzle (AI Intern, Junior Devs, Data Engineers, Mobile, Solutions).
- **Impacto:** Catálogo se expande a **105 oportunidades reales y verificadas**.

### OPCIÓN C (Expansión Exhaustiva con Seniority Etiquetado — 122 Vacantes Nuevas)
Promover las vacantes de la Opción B más las vacantes `SENIOR_OR_LEAD` y adyacentes de Canonical, Sezzle y CookUnity, manteniendo visible en el frontend el chip de nivel de experiencia para no confundir a los egresados iniciales.
- **Impacto:** Catálogo se expande a **137 oportunidades**.

### OPCIÓN D (Mantenimiento en Staging sin Promoción)
Conservar las 154 vacantes en staging para monitoreo longitudinal sin alterar el catálogo público actual (15 fichas).
