# VELORA — AUDITORÍA TÉCNICA Y CIERRE DE TAREA R5-03
## Ampliación de Fuentes Corporativas Privadas de Tecnología y Finanzas en Perú

**Proyecto:** Velora  
**Fase:** R5 — Cobertura nacional de oportunidades  
**Tarea:** `TASK-R5-03 — Ampliación de Empresas de Tecnología y Finanzas en Perú`  
**Prioridad:** P1  
**Clasificación:** `[ADAPTACIÓN_OSS]`  
**Dictamen Técnico:** `COMPLETED` (Cumplimiento integral de objetivos técnicos, arquitectónicos y de datos)  
**Fecha de Ejecución:** 2026-11-24  
**Auditor / Ingeniero Responsable:** Senior Software Engineer & Technical Auditor  
**Repositorio:** `Blueisazul/WebRutaSistemas` (Rama de trabajo: `main`)

---

## 1. Dictamen de la Tarea

### **ESTADO FINAL: `COMPLETED`**

La tarea `TASK-R5-03` ha alcanzado todos sus criterios de éxito funcionales, operativos, técnicos y de gobernanza:

1. **Incorporación de fuentes corporativas privadas en Perú:** Se evaluaron 6 empresas de tecnología, banca y consultoría en Perú. Se aprobaron y configuraron exitosamente **4 nuevas fuentes corporativas privadas** (`stefanini-hiringroom`, `canvia-hiringroom`, `myapps-hiringroom`, `efitec-hiringroom`), cumpliendo el rango objetivo de 3 a 5 fuentes.
2. **Meta de vacantes en staging cumplida:** Se capturaron, normalizaron y validaron **20 nuevas oportunidades técnicas privadas locales** en `data/candidates/inbox.local.json`, todas con contratación directa en territorio peruano y relevancia verificada en Ingeniería de Sistemas, TI, Software y Cloud.
3. **Conformidad con Candidate Schema 2:** 100% de los 20 candidatos cumplen rigurosamente el esquema, sin errores de validación.
4. **Cero dependencias externas:** Implementado con la librería estándar de Python (`html`, `re`, `urllib`, `hashlib`, `json`).
5. **Integridad canónica intacta:** Los catálogos oficiales `data/opportunities.seed.json` y `data/opportunities.json` permanecieron 100% intactos con paridad SHA-256 certificada.
6. **Cero PII:** Cero datos personales expuestos en la bandeja de staging.
7. **Regresión y pruebas automatizadas:** 236 pruebas unitarias y de integración pasando al 100% en 5.4 segundos.

---

## 2. Resumen Ejecutivo de la Ampliación Privada

La fase R4 dotó a Velora de un motor de adquisición capaz de consultar ATS globales (Greenhouse y Lever) e instituciones públicas (OSITRAN, Defensoría, Indecopi). No obstante, la masa crítica de empleo privado en tecnología en el Perú no reside en Greenhouse ni en Lever, sino en portales corporativos multitenant y plataformas de gestión del talento locales.

Durante la auditoría de canales ATS en el Perú realizada en `TASK-R5-03`, se constató que la infraestructura multitenant de **HiringRoom** (`*.hiringroom.com`) es el estándar *de facto* adoptado por consultoras tecnológicas líderes, empresas de infraestructura y proveedores de soluciones bancarias en Lima. 

En lugar de construir raspadores *ad-hoc* frágiles o introducir librerías de terceros, Velora generalizó su adaptador `hiringroom-board` existente en `collector/pe_connectors.py`, extendiendo su capacidad desde portales de empleo universitarios (como UTP) hacia portales corporativos de consultoría e ingeniería. Mediante extracción dual (Schema.org JSON-LD cuando está disponible y metadatos estructurados OpenGraph / DOM semántico cuando no lo está), el sistema ahora extrae vacantes directamente de los empleadores sin riesgo de bloqueo y con fidelidad garantizada.

---

## 3. Matriz de Empresas Evaluadas y Estado de sus Canales de Empleo

Se inspeccionaron empresas representativas de tecnología, consultoría, banca y retail en el Perú:

| Empresa | Razón Social / Giro | Canal / ATS Detectado | Vacantes TI Perú | Estado en Velora | Justificación Técnica / Gobernanza |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Stefanini Perú** | Stefanini IT Solutions Perú S.A.C. (Consultoría TI global) | HiringRoom (`stefaniniitsolutionsperu.hiringroom.com`) | 21 activas | **APPROVED** (`stefanini-hiringroom`) | Acceso público unauthenticated; vacantes directas de TI en Lima (Help Desk, .NET, Java, QA, Cloud); OpenGraph limpio. |
| **Canvia** | Canvia / GMD (Líder en transformación digital e infraestructura TI) | HiringRoom (`canvia.hiringroom.com`) | 4 activas | **APPROVED** (`canvia-hiringroom`) | Acceso público sin WAF; puestos directos de infraestructura, administración Linux/Unix y operaciones TI en Cercado de Lima. |
| **MyApps** | MyApps Soluciones S.A.C. (Firma de software y QA en San Isidro) | HiringRoom (`myapps.hiringroom.com`) | 5 activas | **APPROVED** (`myapps-hiringroom`) | Acceso público; vacantes de desarrollo Full Stack con IA, backend Python y automatización QA en San Isidro, Lima. |
| **Efitec Corporation** | Efitec Corporation S.A.C. (Banca, software financiero y Cloud AWS) | HiringRoom (`efitec.hiringroom.com`) | 4 activas | **APPROVED** (`efitec-hiringroom`) | Acceso público; vacantes de arquitectura cloud AWS, programación .NET y bases de datos para sector financiero en Lima. |
| **Belcorp** | Belcorp Perú (Corporativo de belleza y tecnología) | Rankmi / Pandapé (`trabajaenbelcorp.biz`) | N/A (SPA) | **PENDING_REVIEW** (`belcorp-careers`) | Requiere cliente JavaScript reactivo SPA; no expone API REST pública ni feed desatendido unauthenticated. Fail-closed activado. |
| **BCP / Yape** | Banco de Crédito del Perú (Banca digital y fintech) | Krowdy / Portales comerciales (`viabcp.com`) | 50+ externas | **PENDING_REVIEW** (`bcp-yape-krowdy`) | Gestionado mediante intermediario Krowdy y portales comerciales (Bumeran/Laborum) sin endpoint headless directo de libre acceso. Fail-closed activado. |

---

## 4. Conectores Adaptados y Configuración Implementada

### 4.1. Generalización del Conector `hiringroom-board` (`collector/pe_connectors.py`)

Se implementó el soporte multitenant integral en `pe_connectors.py` con las siguientes capacidades:

1. **Extracción Semántica Dual:**
   - **Vía A (JSON-LD):** Si el portal o la página de detalle incluye `<script type="application/ld+json">` con `@type: "JobPosting"`, se procesa de forma nativa mediante `jsonld_extractor.py`.
   - **Vía B (OpenGraph & Microdata):** Si el detalle no provee JSON-LD (comportamiento habitual de los portales corporativos de HiringRoom), la nueva función `_parse_hiringroom_vacancy_html` extrae de forma determinista:
     - `og:title` o `<title>`: Limpieza de prefijos corporativos (`Oportunidad de Empleo:`, `Nuevas oportunidades de empleo:`, sufijos de empresa y emojis como 🚀).
     - `og:description`: Desescapado de entidades HTML (`html.unescape`) y remoción de etiquetas residuales.
     - `og:url`: Identificación unívoca del enlace canónico de postulación y extracción del identificador de 24 caracteres hexadecimales de la vacante.
2. **Normalización Geográfica:**
   - Detección de distritos de Lima Metropolitana (`Surquillo`, `San Isidro`, `Miraflores`, `Cercado de Lima`) y provincias del Perú (`Arequipa`, `La Libertad`), mapeándolos a cadenas normalizadas compatibles con la taxonomía geográfica (`Lima, Perú`, `San Isidro, Lima, Perú`, etc.).
3. **Detección Determinista de Modalidad:**
   - Detección basada en tokens de título (`Remoto`, `Híbrido`, `Presencial`) combinada con selectores DOM del frontend de HiringRoom (`hr-Remote`, `hr-Company`, `hrc-black`).
4. **Descarte de Bolsas Generales:**
   - Detección automática y omisión de perfiles genéricos no postulables (ej. vacante interna `"Base general"`).

### 4.2. Registro en `collector/sources.json`

Se agregaron las 4 fuentes aprobadas y 2 fuentes documentadas en `pending_review`:
- Total de fuentes en el registro: 22 fuentes.
- Total de fuentes aprobadas y habilitadas (`enabled: true`, `decision: "approved"`): **14 fuentes** (6 ATS globales + 4 peruanas iniciales + 4 corporativas privadas peruanas).

---

## 5. Políticas de Rate Limiting, Términos y Robots

Las 4 fuentes aprobadas cumplen estrictamente con la política de adquisición ética y de bajo impacto:

- **Protocolo:** HTTPS unidireccional de solo lectura.
- **Tasa de consulta (`minDelayMs`):** 1500 ms entre peticiones consecutivas a un mismo subdominio.
- **Tope de peticiones (`maxRequestsPerRun`):**
  - `stefanini-hiringroom`: Máximo 15 peticiones por corrida.
  - `canvia-hiringroom`: Máximo 10 peticiones por corrida.
  - `myapps-hiringroom`: Máximo 10 peticiones por corrida.
  - `efitec-hiringroom`: Máximo 10 peticiones por corrida.
- **Términos de servicio (`termsReview`):** `approved_employer_site`. El portal está expresamente destinado por el empleador para la difusión pública de sus convocatorias.
- **Derechos de reutilización (`rightsReview`):** `metadata_only_approved`. Solo se capturan metadatos fácticos esenciales (título, empleador, enlace, ubicación, modalidad y resumen de requisitos) para permitir que el postulante sea redirigido al portal original del empleador.
- **Cumplimiento robots (`robotsReview`):** `reviewed_allowed`. Los subdominios de HiringRoom permiten el acceso público de navegadores e indexadores a las rutas `/jobs` y `/jobs/get_vacancy/*`.

---

## 6. Deduplicación Determinista y Prevención de Colisiones

El motor de deduplicación determinista (`collector/deduplication.py`) garantiza:

1. **Clave Primaria Compuesta:** Cada candidato se indexa bajo `{sourceId}:{externalReference}`, donde `externalReference` es el código unívoco de la vacante (ej. `STEFANINI-HIRINGROOM-66984666bb7169324800e116`).
2. **Firma Canónica Cruzada:** `{employer}:{externalReference}` previene colisiones si dos fuentes diferentes intentaran registrar la misma vacante.
3. **Idempotencia:** Ejecuciones subsiguientes contra las mismas fuentes detectan las oportunidades existentes como duplicados exactos (`EXACT_DUPLICATE`) y agregan 0 registros duplicados a la bandeja.

---

## 7. Evidencias de Extracción y Candidatos Capturados

Durante la corrida en vivo, se evaluaron 27 vacantes totales en las 4 empresas. Se descartaron 7 vacantes no afines o genéricas (ej. bases generales o roles administrativos/comerciales) y se incorporaron **exactamente 20 candidatos relevantes** a la bandeja de staging:

### Detalle de los 20 Candidatos Corporativos Privados en Staging (`inbox.local.json`)

| # | Fuente | Título de la Oportunidad | Empleador Directo | Ubicación Verificada | Modalidad | Candidate ID |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `stefanini-hiringroom` | Mesa de Ayuda / Help Desk - Jr. | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-64af48605f965d380ea593a1` |
| **2** | `stefanini-hiringroom` | On-Site Technical Support | Stefanini IT Solutions Perú S.A.C. | Lima, Perú | Presencial | `CAND-stefanini-hiringroom-64b69ac46092b4e91dad77ff` |
| **3** | `stefanini-hiringroom` | Help Desk / Mesa de Ayuda | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-64e54adf0825c945afec6688` |
| **4** | `stefanini-hiringroom` | Soporte Técnico N2 | Stefanini IT Solutions Perú S.A.C. | Lima, Perú | Presencial | `CAND-stefanini-hiringroom-64f78b9cafb991f0d5d7b8a2` |
| **5** | `stefanini-hiringroom` | Mesa de Ayuda / Help Desk - Jr. | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-64ff951be9e801a376b48609` |
| **6** | `stefanini-hiringroom` | Desarrollador.Net | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-650a2a6329fdaaeb9b2cea2f` |
| **7** | `stefanini-hiringroom` | Help Desk / Mesa de Ayuda | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-651d9911c8450a5edc503e88` |
| **8** | `stefanini-hiringroom` | Help Desk / Mesa de Ayuda | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Presencial | `CAND-stefanini-hiringroom-6557d7a1e37ac98280c5efce` |
| **9** | `stefanini-hiringroom` | QA Funcional Jr. | Stefanini IT Solutions Perú S.A.C. | Miraflores, Lima, Perú | Híbrido | `CAND-stefanini-hiringroom-6557ea71cdab771fa67230fe` |
| **10** | `stefanini-hiringroom` | Desarrollador Java - Remoto | Stefanini IT Solutions Perú S.A.C. | Lima, Perú | Remoto | `CAND-stefanini-hiringroom-656f92cc26c837694570e211` |
| **11** | `canvia-hiringroom` | Operador de sistemas | Canvia | Lima, Perú | Presencial | `CAND-canvia-hiringroom-6aea5eb0ea91c20358a28731` |
| **12** | `canvia-hiringroom` | Administrador de sistemas Linux/ Unix | Canvia | Lima, Perú | Híbrido | `CAND-canvia-hiringroom-6b049ed1dc729c9e2c4299d4` |
| **13** | `canvia-hiringroom` | Especialista de Sistemas Aix Linux | Canvia | Lima, Perú | Híbrido | `CAND-canvia-hiringroom-6b04bdd9af6d6050ee6ccf23` |
| **14** | `myapps-hiringroom` | Desarrollador(a) Full Stack con IA | MyApps Soluciones S.A.C. | San Isidro, Lima, Perú | Presencial | `CAND-myapps-hiringroom-6aedfa885782670c140945b0` |
| **15** | `myapps-hiringroom` | Desarrollador Backend | MyApps Soluciones S.A.C. | San Isidro, Lima, Perú | Presencial | `CAND-myapps-hiringroom-6af24fcede025ef7de2b0a19` |
| **16** | `myapps-hiringroom` | Analista QA Automatizador | MyApps Soluciones S.A.C. | San Isidro, Lima, Perú | Presencial | `CAND-myapps-hiringroom-6afb908dbb6faad099eece66` |
| **17** | `efitec-hiringroom` | Analista Programador Fullstack Semi Senior (.NET/AWS) | Efitec Corporation S.A.C. | Lima, Perú | Remoto | `CAND-efitec-hiringroom-6a4dc426d1eb96c6d5667008` |
| **18** | `efitec-hiringroom` | Desarrollador Fullstack Senior I Frontend & E-Commerce | Efitec Corporation S.A.C. | Lima, Perú | Híbrido | `CAND-efitec-hiringroom-6ac022fea173774fc20a503f` |
| **19** | `efitec-hiringroom` | Especialista de Infraestructura y Redes Senior | Efitec Corporation S.A.C. | Lima, Perú | Híbrido | `CAND-efitec-hiringroom-6b061ad502f8dbcb78962d4d` |
| **20** | `efitec-hiringroom` | Especialista Senior BD y Cloud AWS | Efitec Corporation S.A.C. | Lima, Perú | Híbrido | `CAND-efitec-hiringroom-6b0638a76bff669a730ab8fc` |

---

## 8. Clasificación de las Oportunidades Capturadas

El módulo de clasificación determinista (`collector/classification.py`) categorizó los 20 puestos a lo largo de los tres ejes del producto:

1. **Relevancia Técnica:**
   - `DIRECT` (100% de los 20 candidatos): Roles en Ingeniería de Software, Desarrollo .NET/Java/Fullstack, Administración de Sistemas Unix/Linux, Soporte TI y Mesa de Ayuda, Calidad de Software (QA Funcional y Automatizado), Infraestructura y Redes, y Arquitectura Cloud AWS / Bases de Datos.
   - Puestos administrativos, comerciales y talent pools fueron descartados (`NOT_RELEVANT`) durante el pipeline sin contaminar la bandeja.
2. **Elegibilidad Geográfica:**
   - `PERU_LOCAL` (100% de los 20 candidatos): Empleos localizados en Lima Metropolitana (distritos de Miraflores, San Isidro, Cercado de Lima y Surquillo) o de alcance nacional con contratación bajo la legislación laboral peruana.
3. **Distribución por Nivel de Experiencia (`experienceTier`):**
   - `ENTRY_OR_JUNIOR`: 5 vacantes (Help Desk Jr, QA Funcional Jr).
   - `MID`: 9 vacantes (Soporte Técnico N2, Desarrollador .NET, Dev Java, Operador de Sistemas, Full Stack AI, Backend Dev, Analista QA).
   - `SENIOR_OR_LEAD`: 6 vacantes (Admin Linux/Unix, Especialista AIX Linux, Dev Senior Frontend, Especialista Infraestructura Senior, Especialista Senior BD y Cloud AWS).
4. **Distribución por Modalidad de Trabajo:**
   - **Presencial:** 12 vacantes (60%)
   - **Híbrido:** 6 vacantes (30%)
   - **Remoto:** 2 vacantes (10%)

---

## 9. Métricas de la Adquisición en Staging

- **Bandeja de Staging:** `data/candidates/inbox.local.json`
- **Total de candidatos en staging antes de la corrida:** 275 candidatos.
- **Nuevos candidatos incorporados por `TASK-R5-03`:** **20 candidatos**.
- **Total de candidatos en staging tras la corrida:** **295 candidatos**.
- **Resultado de Validación (`validate_candidates.py`):** **VÁLIDO (0 errores)**.
- **Estado editorial:** `pending_review` (Aislados estrictamente en staging; ninguna vacante promocionada automáticamente a catálogo canónico).

---

## 10. Verificación de Integridad Canónica

Se verificaron las sumas de verificación criptográfica (SHA-256) de los archivos canónicos del catálogo antes y después de toda la ejecución:

| Archivo | Hash SHA-256 Certificado | Estado |
| :--- | :--- | :---: |
| `data/opportunities.seed.json` | `710d7722856665c42483babd2202ab851839bb4557ae454692e6d6508b7c1917` | **100% INTACTO** |
| `data/opportunities.json` | `1d96ecacdb6f07572509484ba1a562e039d2600050a79bb9d09addb576a8af02` | **100% INTACTO** |

Comprobaciones adicionales:
- `python scripts/validate_catalog.py`: Válido (112 fichas).
- `python scripts/build_catalog.py --check`: Catálogo válido (112 registros; snapshot coincide exactamente con la fuente canónica).

---

## 11. Verificación de Seguridad y Cero PII

Se auditó exhaustivamente la estructura de los 20 nuevos candidatos para verificar la ausencia total de datos de carácter personal:

- Campos prohibidos ausentes: `applicantName`, `candidateName`, `email`, `phone`, `recruiterEmail`, `recruiterPhone`, `dni`, `ssn`, `passport`, `birthDate`, `address`.
- Solo se almacenan metadatos públicos provistos por el empleador en su aviso de empleo.
- La postulación se realiza exclusivamente derivando al usuario al portal oficial mediante `applyUrl`.

---

## 12. Suite de Pruebas y Cobertura de Regresión

Se crearon fixtures reproducibles offline para las 4 fuentes en `tests/fixtures/ats/`:
- `tests/fixtures/ats/stefanini-hiringroom.html`
- `tests/fixtures/ats/canvia-hiringroom.html`
- `tests/fixtures/ats/myapps-hiringroom.html`
- `tests/fixtures/ats/efitec-hiringroom.html`

Se añadieron pruebas de unidad y de integración en:
- `tests/test_pe_connectors.py`: `test_transform_corporate_hiringroom_fixtures` (validación de parsing, atributos, Schema 2 y clasificación).
- `tests/test_classification_and_coverage.py`: `test_approved_sources_configured_cleanly` (verificación de los 14 IDs de fuentes aprobadas).
- `tests/test_periodic_acquisition_ops.py`: Actualización de métricas de adquisición multisource (14 fuentes evaluadas y exitosas).

### Resultado de la Suite Completa:
```
Ran 236 tests in 5.407s
OK
```
**0 fallos, 0 errores, 100% de pruebas pasando.**

---

## 13. Estado Actualizado del Roadmap Maestro

En `docs/roadmap/VELORA-MASTER-ROADMAP.md`:
- `TASK-R5-03`: Pasa de `PENDING` a **`COMPLETED`**.
- Fuentes aprobadas registradas: Aumentan de 10 a **14 fuentes**.
- Candidatos en staging: Aumentan de 275 a **295 candidatos**.
- Catálogo canónico publicado: Permanece estable en **112 registros**.

---

## 14. Recomendación Operativa y Siguiente Paso Único

1. **Estado de la Rama:** Todos los cambios técnicos, conectores, fixtures y pruebas residen en el espacio de trabajo local listos para su revisión.
2. **Salvaguardas Respetadas:** No se realizaron commits en git, push a ramas remotas, merges ni despliegues en producción.
3. **Siguiente Acción Única Recomendada del Roadmap Maestro:**  
   Habiendo completado `TASK-R5-01` (`COMPLETED_WITH_LIMITATIONS`), `TASK-R5-04-01` (`EVALUATED_PROPOSED`) y `TASK-R5-03` (`COMPLETED`), la siguiente tarea en el Roadmap Maestro es:
   - **`TASK-R6-01` — Política y Motor de Auto-Publicación Basada en Reglas Objetivas** (Prioridad `P1`), para eliminar el cuello de botella de revisión manual y permitir la promoción automática al catálogo de candidatos provenientes de fuentes con `decision: "approved"` que cumplan el 100% de los criterios de calidad y elegibilidad.
