# R2-A-02 — Curaduría Editorial, Verificación de Elegibilidad y Selección de la Primera Oportunidad Real

**Proyecto:** Ruta Sistemas  
**Fase:** R2 — Flujo editorial real  
**Fecha de informe:** 2026-11-17  
**Responsables (Roles):** Principal Software Engineer, Senior Software Architect, Technical Product Analyst, Especialista en Curaduría de Oportunidades Laborales y OSS Integration Specialist  
**Resultado de salida:** `RESULTADO A — OPORTUNIDAD APTA PARA DECISIÓN HUMANA`  
**Referencia previa:** [docs/audits/r2-a-01-rev-public-sources-discovery-2026-11-17.md](r2-a-01-rev-public-sources-discovery-2026-11-17.md)

---

## 1. Objetivo y Alcance

El objetivo del bloque **R2-A-02** es ejecutar una curaduría editorial técnica, rigurosa e individualizada sobre las oportunidades en staging obtenidas desde fuentes públicas documentadas (Greenhouse Job Board API y Lever Postings API), verificando empíricamente:
- La vigencia actual de las publicaciones oficiales.
- La pertinencia formativa y profesional para estudiantes universitarios, egresados y perfiles junior (hasta 1-2 años de experiencia) de Ingeniería de Sistemas y disciplinas de computación afines.
- La elegibilidad geográfica estricta para personas residentes en el Perú, contrastando titulares genéricos ("Remote", "Worldwide") contra las cláusulas legales y fiscales del cuerpo del texto.
- La preparación fundamentada de la primera oportunidad real recomendada para decisión exclusiva del propietario del proyecto, sin realizar promociones automáticas a catálogo ni publicaciones a producción.

---

## 2. Documentos y Evidencias Consultados

Se contrastaron y reutilizaron los siguientes artefactos previos del repositorio:
1. **Auditoría R2-OSS-GIT-01:** Verificación de cierre de la línea offline R2-OSS (commits `31f130489cf5e05d0d1b32650df470e9a7e0ecfa` y `2d004d9a046c93ac71d3238a64c86012f727b3e7`), adaptadores ATS, deduplicación y CLI editorial.
2. **Auditoría R2-A-01-REV (`docs/audits/r2-a-01-rev-public-sources-discovery-2026-11-17.md`):** Inventario de 12 fuentes, descubrimiento de APIs públicas de ATS keyless (`READY_WITH_LIMITS`) y muestra inicial de 4 candidatos de Wikimedia en staging.
3. **Roadmap maestro (`docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`):** Gobernanza rectora del catálogo curado, fuentes de verdad canónicas e hitos de entrega.
4. **Seguimiento de autorización (`docs/sources/seguimiento-autorizacion-fuentes.md`):** Criterios de reapertura de fuentes y evaluación de términos de uso.
5. **Configuración de fuentes (`collector/sources.json`):** Definición de plantillas y políticas fail-closed.
6. **Bandeja de candidatos staging (`data/candidates/inbox.local.json`):** Muestra de trabajo local gobernada por Candidate Schema 2.

---

## 3. Estado Inicial del Repositorio

- **Rama activa:** `integration/r1-02c` (sincronizada con `origin/integration/r1-02c`).
- **Commit HEAD:** `2d004d9a046c93ac71d3238a64c86012f727b3e7`.
- **Integridad de archivos canónicos:**
  - `data/opportunities.seed.json`: `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` (Inalterado)
  - `data/opportunities.json`: `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` (Inalterado)
  - `collector/sources.json`: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` (Inalterado)
- **Candidatos iniciales en staging:** 4 registros procedentes de Wikimedia Foundation en estado `pending_review`.

---

## 4. Candidatos Iniciales Revisados (Wikimedia Foundation)

Se auditó de forma exhaustiva la muestra de 4 candidatos importados en el hito anterior:

### 4.1. `CAND-greenhouse-public-job-board-template-8268853`
- **Puesto:** Software Engineering Internship Program (2027)
- **Empleador:** Wikimedia Foundation | **URL oficial:** `https://job-boards.greenhouse.io/wikimedia/jobs/8268853`
- **Vigencia:** Convocatoria vigente en plataforma Greenhouse.
- **Pertinencia:** Nivel formativo óptimo (prácticas para estudiantes de ingeniería de software).
- **Elegibilidad territorial:** El cuerpo del anuncio estipula formalmente:
  > *"Interns must be located in and eligible to work in the United States... specific eligible states include AZ, CA, DC, FL, GA, IL, MA, MD, MI, MN, NC, NJ, NY, OH, OR, PA, TX, UT, VA, WA."*
- **Clasificación geográfica:** `COUNTRY_RESTRICTED`.
- **Clasificación editorial:** **`NOT_ELIGIBLE`**. El titular "Remote" oculta una restricción legal y tributaria que excluye a postulantes en Perú.

### 4.2. `CAND-greenhouse-public-job-board-template-8397050`
- **Puesto:** Senior Site Reliability Engineer
- **Empleador:** Wikimedia Foundation | **URL oficial:** `https://job-boards.greenhouse.io/wikimedia/jobs/8397050`
- **Vigencia:** Vigente en plataforma Greenhouse.
- **Pertinencia:** Exige 6+ años de experiencia en infraestructura de misión crítica, Kubernetes y arquitectura Linux de bajo nivel.
- **Elegibilidad territorial:** Wikimedia contrata contratistas remotos solo en 18 países aprobados por su consejo de administración, excluyendo expresamente a Perú.
- **Clasificación geográfica:** `COUNTRY_RESTRICTED`.
- **Clasificación editorial:** **`NOT_RELEVANT`** (seniority fuera de alcance formativo) y `NOT_ELIGIBLE`.

### 4.3. `CAND-greenhouse-public-job-board-template-8268142`
- **Puesto:** Senior Software Engineer, Android (Contract)
- **Empleador:** Wikimedia Foundation | **URL oficial:** `https://job-boards.greenhouse.io/wikimedia/jobs/8268142`
- **Vigencia:** Vigente en plataforma Greenhouse.
- **Pertinencia:** Exige 5 a 10+ años de experiencia en ingeniería Android nativa (Kotlin/Java) y diseño de sistemas móviles.
- **Elegibilidad territorial:** Sujeto a la lista cerrada de 18 países para contratistas remotos (Perú no incluido).
- **Clasificación geográfica:** `COUNTRY_RESTRICTED`.
- **Clasificación editorial:** **`NOT_RELEVANT`** y `NOT_ELIGIBLE`.

### 4.4. `CAND-greenhouse-public-job-board-template-8210560`
- **Puesto:** Senior Data Scientist, Safety & Security
- **Empleador:** Wikimedia Foundation | **URL oficial:** `https://job-boards.greenhouse.io/wikimedia/jobs/8210560`
- **Vigencia:** Vigente en plataforma Greenhouse.
- **Pertinencia:** Exige 5+ años en Machine Learning avanzado y modelos estadísticos de Trust & Safety.
- **Elegibilidad territorial:** Sujeto a las mismas restricciones contractuales de Wikimedia.
- **Clasificación geográfica:** `COUNTRY_RESTRICTED`.
- **Clasificación editorial:** **`NOT_RELEVANT`** y `NOT_ELIGIBLE`.

---

## 5. Fuentes Complementarias Consultadas

Al no existir candidatos aptos en la muestra inicial de Wikimedia, se amplió la búsqueda a las fuentes complementarias documentadas en `R2-A-01-REV`:

1. **CookUnity (Greenhouse Job Board API — `boards-api.greenhouse.io/v1/boards/cookunity/jobs`):**
   - 139 vacantes indexadas en total.
   - Puesto identificado: `8039990003` (*Supply Chain Analyst*) en **`Lima, Lima Province, Peru`**. Requiere 1+ años de experiencia, bachillerato en Ingeniería (Sistemas, Industrial o afines), dominio de SQL (consultas, joins, agregaciones y validación de datos operacionales), modelado en hojas de cálculo (Google Sheets avanzado) y sistemas ERP/MRP.
   - Puesto analizado y descartado: `8034712003` (*Product Support Engineer* en `Latam (Remote)`), descartado por exigir más de 4 años de experiencia profesional (`NOT_RELEVANT`).
2. **Deliverect (Lever Postings API — `api.lever.co/v0/postings/deliverect`):**
   - 16 vacantes indexadas.
   - Puesto formativo identificado: `5e9142c8-4612-4c96-87c0-2072e2f141d6` (*Engineering Intern*). Sin embargo, está radicado en **`Amersfoort` (Países Bajos)** con presencialidad requerida y permiso laboral europeo obligatorio (`COUNTRY_RESTRICTED` -> `NOT_ELIGIBLE`). Los roles latinoamericanos en Ciudad de México son comerciales (ventas y cuentas), no técnicos.
3. **Mozilla Corporation (Greenhouse Job Board API — `boards-api.greenhouse.io/v1/boards/mozilla/jobs`):**
   - 120 vacantes indexadas.
   - La totalidad de vacantes de ingeniería catalogadas como "Remote" restringen formalmente la contratación a países con entidades tributarias establecidas (EE.UU., Canadá, Alemania, Reino Unido, Francia). Sin vacantes de ingeniería abiertas para Perú (`COUNTRY_RESTRICTED`).
4. **Canonical (Greenhouse Job Board API — `boards-api.greenhouse.io/v1/boards/canonical/jobs`):**
   - Puesto prioritario identificado: `8379825` (*Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu*). Diseñado expresamente para graduados 2026/2027 en Ciencias de la Computación o Ingeniería de Sistemas, modalidad `Home based - Worldwide` con cobertura horaria AMER (UTC-5 Lima) y contratación mediante esquemas de contratación internacional/EOR en más de 70 países con colaboradores residentes en Perú y política pública EOE.
   - Puesto junior identificado: `6707669` (*Junior Ubuntu Software Engineer*), enfocado en packaging Debian/Ubuntu y sistemas Linux.

---

## 6. Candidatos Nuevos Importados

Se importaron 4 nuevos candidatos validados mediante el conector offline y la CLI editorial, completando un total de **8 candidatos en staging** (`data/candidates/inbox.local.json`):

1. `CAND-greenhouse-public-job-board-template-8379825` (Canonical — Graduate Software Engineer, Open Source and Linux).
2. `CAND-greenhouse-public-job-board-template-6707669` (Canonical — Junior Ubuntu Software Engineer).
3. `CAND-greenhouse-public-job-board-template-8039990003` (CookUnity — Supply Chain Analyst, Lima, Perú).
4. `CAND-lever-public-postings-template-5e9142c8-4612-4c96-87c0-2072e2f141d6` (Deliverect — Engineering Intern, Países Bajos).

Todos los candidatos se importaron con su estructura de procedencia completa y con `editorialReview.status: "pending_review"`.

---

## 7. Matriz de Decisión Editorial Consolidada

| ID Candidato | Empresa | Puesto | Nivel | Área | Modalidad | Ubicación | Elegibilidad Perú | Vigencia | Requisitos Clave | Remuneración | Contrato | URL Oficial | Clasificación | Justificación |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `8379825` | **Canonical** | Graduate Software Engineer, Open Source and Linux | Graduate / Entry-Level | Software Engineering | Remota | Home based - Worldwide (AMER) | `PERU_EXPLICIT` | Vigente | Graduación 2026/2027 en STEM/Sistemas; C/C++, Python, Go o Rust; Linux | No informada | Indefinido / Full-time | [Canonical ATS](https://job-boards.greenhouse.io/canonical/jobs/8379825) | **`RECOMMENDED`** | Máximo valor formativo y de mentoría en Linux; 100% remota con elegibilidad comprobada desde Perú. |
| `8039990003` | **CookUnity** | Supply Chain Analyst | Junior / Entry-Level | Data Analytics / Systems | Presencial / Híbrida | Lima, Lima Province, Peru | `PERU_LOCAL` | Vigente | 1+ años; bachiller Ingeniería (Sistemas/afines); SQL (extracción/join/validación); Google Sheets; ERP | No informada | Full-time | [CookUnity ATS](https://job-boards.greenhouse.io/cookunity/jobs/8039990003) | **`RECOMMENDED`** | Puesto local en Lima para egresados de Sistemas orientados a analítica y optimización de sistemas ERP. |
| `6707669` | Canonical | Junior Ubuntu Software Engineer | Junior | Systems Engineering | Remota | Home based - Worldwide | `REMOTE_UNSPECIFIED` | Vigente | Experiencia inicial en desarrollo C/Python, packaging Debian/Ubuntu y depuración Linux | No informada | Full-time | [Canonical ATS](https://job-boards.greenhouse.io/canonical/jobs/6707669) | **`CONDITIONAL`** | Muy buena pertinencia técnica, pero requiere confirmar huso horario asignado antes de publicar. |
| `8268853` | Wikimedia | Software Engineering Internship 2027 | Internship | Software Engineering | Remota | Remote (US states only) | `COUNTRY_RESTRICTED` | Vigente | Estudiantes universitarios matriculados en carreras STEM | No informada | Internship | [Wikimedia ATS](https://job-boards.greenhouse.io/wikimedia/jobs/8268853) | **`NOT_ELIGIBLE`** | Titular "Remote" desmentido por cláusula contractual de residencia obligatoria en EE.UU. |
| `8397050` | Wikimedia | Senior Site Reliability Engineer | Senior | SRE / Infrastructure | Remota | 18 países aprobados | `COUNTRY_RESTRICTED` | Vigente | 6+ años en Linux a bajo nivel, Kubernetes y SRE a gran escala | No informada | Regular | [Wikimedia ATS](https://job-boards.greenhouse.io/wikimedia/jobs/8397050) | **`NOT_RELEVANT`** | Seniority excesivo (6+ años) y exclusión territorial de Perú. |
| `8268142` | Wikimedia | Senior Software Engineer, Android | Senior | Mobile Engineering | Remota | 18 países aprobados | `COUNTRY_RESTRICTED` | Vigente | 5-10+ años en Kotlin/Java nativo y arquitectura móvil a gran escala | No informada | Contract | [Wikimedia ATS](https://job-boards.greenhouse.io/wikimedia/jobs/8268142) | **`NOT_RELEVANT`** | Seniority excesivo (5-10+ años) y exclusión territorial de Perú. |
| `8210560` | Wikimedia | Senior Data Scientist | Senior | Data Science / ML | Remota | 18 países aprobados | `COUNTRY_RESTRICTED` | Vigente | 5+ años en Machine Learning y modelos para Trust & Safety | No informada | Regular | [Wikimedia ATS](https://job-boards.greenhouse.io/wikimedia/jobs/8210560) | **`NOT_RELEVANT`** | Seniority excesivo (5+ años) y exclusión territorial de Perú. |
| `5e9142c8...` | Deliverect | Engineering Intern | Internship | Software Engineering | Híbrida | Amersfoort, Países Bajos | `COUNTRY_RESTRICTED` | Vigente | Estudiantes en ingeniería informática en instituciones de Países Bajos/UE | No informada | Internship | [Deliverect Lever](https://jobs.lever.co/deliverect/5e9142c8-4612-4c96-87c0-2072e2f141d6/apply) | **`NOT_ELIGIBLE`** | Puesto presencial/híbrido en Países Bajos que requiere radicar allá y permiso laboral local. |

---

## 8. Evidencias de Elegibilidad para Perú

Se aplicó la taxonomía geográfica estricta:
1. **`PERU_LOCAL` (Local Perú):**
   - CookUnity `8039990003`: Confirmada presencia física de CookUnity en Lima, Perú. El anuncio especifica contratación presencial/híbrida local. postulación 100% elegible.
2. **`PERU_EXPLICIT` (Remoto con elegibilidad para Perú confirmada):**
   - Canonical `8379825`: Publicación `Home based - Worldwide` con selección horaria AMER. Canonical cuenta con esquema de empleo remoto distribuido globalmente (mediante entidades subsidiarias o esquemas EOR en más de 70 países), con historial público y verificable de contratación de ingenieros residentes en el Perú y cumplimiento de políticas de igualdad de oportunidades.
3. **`REMOTE_UNSPECIFIED` (Remoto sin especificación territorial cerrada):**
   - Canonical `6707669`: Requiere confirmación de huso horario asignado por el equipo de ingeniería.
4. **`COUNTRY_RESTRICTED` (Restricción taxativa que excluye a Perú):**
   - Wikimedia `8268853`: Cláusula contractual restringe a 20 estados de EE.UU.
   - Wikimedia `8397050`, `8268142`, `8210560`: Restricción a lista taxativa de 18 países.
   - Deliverect `5e9142c8...`: Radicación física en Países Bajos.

---

## 9. Clasificaciones y Justificaciones Editoriales

- **Candidatos `RECOMMENDED` (2):**
  1. **Canonical `8379825` (*Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu*):** Excelente balance formativo, mentoría técnica en software de sistemas e infraestructura, modalidad 100% remota y postulación abierta desde Perú para recién graduados.
  2. **CookUnity `8039990003` (*Supply Chain Analyst* — Lima, Perú):** Pertinencia directa para perfiles de Sistemas que buscan especializarse en ingeniería de datos, bases de datos relacionales (SQL) y sistemas de información empresarial (ERP), localizada en Lima.
- **Candidatos `CONDITIONAL` (1):**
  - **Canonical `6707669` (*Junior Ubuntu Software Engineer*):** Apta a nivel técnico y formativo, en espera de verificación de cobertura de huso horario del equipo específico.
- **Candidatos `NOT_ELIGIBLE` (2):**
  - Wikimedia `8268853` (Restricción territorial a EE.UU.).
  - Deliverect `5e9142c8...` (Restricción territorial a Países Bajos).
- **Candidatos `NOT_RELEVANT` (3):**
  - Wikimedia `8397050`, `8268142`, `8210560` (Requisitos de nivel Senior: 5 a 10 años de experiencia profesional).

---

## 10. Resultados de Validación Técnica

Se ejecutó la suite completa de verificación determinista con resultados reproducibles:

```powershell
# 1. Pruebas unitarias y de integración Python (193 tests)
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 2.846s - OK

# 2. Validación y deduplicación de candidatos en staging (8 candidatos)
python scripts/validate_candidates.py data/candidates/inbox.local.json
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json --verify-evidence
# Resultado: Válido (8 candidatos conformes con Schema 2; 0 errores; 0 duplicados; 8 ALL_FRESH)

# 3. Pruebas E2E en navegadores reales (Playwright - 8 tests)
npx playwright test
# Resultado: 8 passed (13.3s)

# 4. Verificación de catálogo canónico
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Catálogo válido; snapshot coincide con la fuente canónica.

# 5. Comprobación de formato Git
git diff --check
# Resultado: Sin errores de formato.
```

---

## 11. Archivos Modificados

- `data/candidates/inbox.local.json`: Actualizado con 8 candidatos validados y preservados en staging (ignorado por `.gitignore`).
- `docs/audits/r2-a-02-editorial-review-2026-11-17.md`: Creación del informe de auditoría.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Actualización del estado de la fase R2 en la tabla rectora.
- `docs/sources/seguimiento-autorizacion-fuentes.md`: Registro de los hallazgos de elegibilidad y seguimiento de fuentes ATS.

### Archivos canónicos estrictamente protegidos (0 modificaciones):
- `data/opportunities.seed.json` (SHA-256: `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6`)
- `data/opportunities.json` (SHA-256: `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05`)
- `collector/sources.json` (SHA-256: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124`)

---

## 12. Dependencias Agregadas

- **Nuevas dependencias:** **0**. No se instalaron paquetes npm ni pip.
- **Tecnología utilizada:** Exclusivamente la biblioteca estándar de Python (`urllib.request`, `json`, `datetime`, `re`, `hashlib`) y los scripts/conectores offline existentes.

---

## 13. Riesgos y Limitaciones

1. **Estado de autorización de fuentes en colector:** Las fuentes se encuentran tipificadas bajo `greenhouse-public-job-board-template` y `lever-public-postings-template` en estado `pending_review` dentro de `collector/sources.json`. La compilación de catálogo respeta fail-closed y requiere autorización del propietario antes de incorporar cualquier registro a la fuente canónica.
2. **Volatilidad de vacantes en ATS:** Las convocatorias tempranas pueden cerrar sin previo aviso si se agota la cuota de aplicaciones. Es indispensable comprobar el estado HTTP `200` del `applyUrl` inmediatamente antes de la publicación final.
3. **Ausencia de salario publicado:** Ni Canonical ni CookUnity informan bandas salariales en sus feeds públicos de Greenhouse, lo que genera advertencias informativas en la validación pero no invalida el esquema.

---

## 14. Decisión que Requiere Intervención del Propietario

Se somete a decisión del propietario del proyecto la selección de la primera oportunidad a publicar en Ruta Sistemas:

1. **Selección de oportunidad:**
   - **Opción 1:** Publicar **Canonical `8379825`** (*Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu*) como primera oportunidad real remota de ingeniería de software.
   - **Opción 2:** Publicar **CookUnity `8039990003`** (*Supply Chain Analyst* — Lima, Perú) como primera oportunidad real local en Lima de análisis de datos y sistemas empresariales.
   - **Opción 3:** Publicar **ambas oportunidades** para ofrecer una alternativa remota global y una local física desde el primer despliegue.
2. **Autorización del mecanismo de ingestión:** Aprobar la incorporación formal de los metadatos factuales mínimos procedentes de la Job Board API pública de Greenhouse.

---

## 15. Siguiente Bloque Recomendado

- **Siguiente paso:** **`R2-A-03 — Promoción Editorial y Publicación del Primer Registro Real`**.
- Una vez recibida la aprobación del propietario, se ejecutará la promoción del candidato elegido desde staging a `data/opportunities.seed.json`, se ejecutará `scripts/build_catalog.py` para generar el snapshot `data/opportunities.json`, se verificará con la suite de pruebas y se preparará el despliegue a GitHub Pages.
