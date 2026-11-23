# R3-ALPHA-CURATION-01 — Segundo Lote de Oportunidades Reales para la Alpha Privada

**Proyecto:** Ruta Sistemas  
**Fase:** R3 — Evaluación con Círculo Cercano y Alpha Privada  
**Identificador:** `R3-ALPHA-CURATION-01`  
**Fecha de corte e informe:** 2026-11-20 (Hora Lima, UTC-5)  
**Responsables (Roles):** Principal Software Architect, Senior Software Engineer, OSS Integration Specialist, Curador Editorial de Empleo TI y Auditor Técnico de Procedencia  
**Estado:** `COMPLETED_READY_FOR_HUMAN_REVIEW`  
**Rama objetivo:** `integration/r1-02c`  
**HEAD de referencia:** `b27e41804f3ae216173059daeaec39c77174db44`  
**Referencias rectoras:**
- [docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](../architecture/r0-decisiones-y-alcance-2026-11-12.md)
- [docs/architecture/r3-private-alpha-scope-decision-2026-11-20.md](../architecture/r3-private-alpha-scope-decision-2026-11-20.md)
- [docs/audits/r2-a-02-editorial-review-2026-11-17.md](r2-a-02-editorial-review-2026-11-17.md)
- [docs/audits/r2-a-03-controlled-capture-2026-11-18.md](r2-a-03-controlled-capture-2026-11-18.md)
- [docs/audits/r2-a-04-editorial-decision-2026-11-18.md](r2-a-04-editorial-decision-2026-11-18.md)
- [docs/audits/r2-a-05-first-real-publication-2026-11-18.md](r2-a-05-first-real-publication-2026-11-18.md)

---

## 1. Objetivo y Alcance

El bloque **`R3-ALPHA-CURATION-01`** tiene como misión descubrir, capturar, normalizar, auditar y verificar un **segundo lote de oportunidades laborales reales y pertinentes para Ingeniería de Sistemas y áreas TI en el Perú**, utilizando estrictamente la infraestructura y herramientas offline desarrolladas en la línea R2-OSS (`collector/` y `scripts/editorial_cli.py`).

Este trabajo responde a la necesidad crítica identificada en la decisión `R3-02-PRIVATE-ALPHA-01`: **resolver el cuello de botella de contenido** (el catálogo contaba con una única vacante real, *CookUnity Supply Chain Analyst — OP-005*, y cinco registros demostrativos), aumentando sustancialmente la utilidad práctica y el valor de consulta para el propietario y su círculo reducido de amigos durante la Alpha privada.

### Principios y Limitaciones Respetados:
1. **No sobreingeniería:** Cero desarrollo de nuevas interfaces web, cero refactorizaciones innecesarias del pipeline y cero nuevas dependencias (0 paquetes npm, 0 librerías pip).
2. **Fuentes éticas y públicas:** Exclusivamente endpoints públicos de ATS (Greenhouse Job Board API) sin scraping intrusivo ni evasión de barreras técnicas.
3. **No alteración de archivos canónicos:** Los archivos `data/opportunities.seed.json`, `data/opportunities.json` y `collector/sources.json` permanecen 100% inalterados (hashes criptográficos idénticos).
4. **Bandeja de staging aislada:** Los candidatos se procesan y preservan en la bandeja local `data/candidates/inbox.local.json` (ignorada por `.gitignore`), bajo el estándar Candidate Schema 2.
5. **Puerta de control humano:** Ningún candidato ha sido promovido a catálogo canónico ni se le ha asignado identificador canónico (`OP-00X`). El lote queda preparado y estructurado para la decisión humana exclusiva del propietario.

---

## 2. Resumen Ejecutivo del Lote Evaluado

| Métrica | Cantidad | Descripción |
|---|---|---|
| **Candidatos evaluados en bandeja local (`inbox.local.json`)** | **12** | Muestra total auditada estructural y editorialmente |
| **Oportunidades propuestas para aprobación en Alpha privada** | **5** | Vacantes formativas y junior de Canonical Ubuntu (100% remotas, elegibles desde Perú) |
| **Oportunidades previamente promovidas a catálogo** | **1** | CookUnity Supply Chain Analyst (`8039990003` -> `OP-005` en R2-A-05), preservada como evidencia histórica |
| **Oportunidades analizadas y descartadas con causa auditada** | **6** | 1 CookUnity mid/sr (>4 años exp), 4 Wikimedia (restr. territorial + senior), 1 Deliverect (Países Bajos) |
| **Frescura de evidencias de campo (TTL 7 días Lima)** | **100% (12/12)** | `ALL_FRESH` (observadas y verificadas el 2026-11-20) |
| **Colisiones de identificador o duplicados detectados** | **0** | Verificado deterministamente con `collector/dedup.py` |
| **Errores de validación Candidate Schema 2** | **0** | Conforme con `scripts/validate_candidates.py` |

---

## 3. Matriz Comparativa del Segundo Lote Propuesto (5 Oportunidades)

Todas las oportunidades corresponden a **Canonical** (entidad creadora de Ubuntu Linux), una organización pionera en trabajo remoto global distribuido, con presencia de colaboradores en más de 70 países y contratación contractual viable desde el Perú (esquema EOR / internacional sin exclusión territorial).

| ID Candidato | Empleador | Puesto | Familia Profesional | Nivel | Modalidad y Ubicación | Elegibilidad Perú | Contrato | Exp. Req. | Salario / Beneficios | Postulación Oficial | Recomendación Editorial |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `CAND-greenhouse-public-job-board-template-8379825` | **Canonical** | Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu | Desarrollo de Software / Open Source | Graduate / Entry-Level (Trainee) | Remoto (`Home based - Worldwide`) | `PERU_EXPLICIT` (AMER UTC-5 compatible) | Indefinido / Tiempo completo | 0 a 1 año (Graduación 2026/2027) | No publicado / USD 2,000 presupuesto anual aprendizaje, viajes a sprints internacionales 2/año, bono anual | [Canonical Greenhouse](https://job-boards.greenhouse.io/canonical/jobs/8379825) | **`APPROVE_WITH_LIMITATIONS`** (Recomendado para Alpha privada; alto valor formativo en Linux; requiere inglés profesional) |
| `CAND-greenhouse-public-job-board-template-6707669` | **Canonical** | Junior Ubuntu Software Engineer | Desarrollo de Software / Sistemas Operativos | Junior | Remoto (`Home based - Worldwide`) | `PERU_EXPLICIT` (AMER UTC-5 compatible) | Indefinido / Tiempo completo | 0 a 2 años | No publicado / Presupuesto anual USD 2,000 aprendizaje, sprints internacionales 2/año, bono anual | [Canonical Greenhouse](https://job-boards.greenhouse.io/canonical/jobs/6707669) | **`APPROVE_WITH_LIMITATIONS`** (Recomendado para Alpha privada; packaging Linux, Rust/Go/Python/C++; requiere inglés profesional) |
| `CAND-greenhouse-public-job-board-template-5370815` | **Canonical** | Junior Linux Kernel Engineer - Ubuntu | Sistemas Operativos / Kernel / Bajo Nivel | Junior | Remoto (`Home based - Worldwide`) | `PERU_EXPLICIT` (AMER UTC-5 compatible) | Indefinido / Tiempo completo | 0 a 2 años | No publicado / Presupuesto anual USD 2,000 aprendizaje, sprints internacionales 2/año, bono anual | [Canonical Greenhouse](https://job-boards.greenhouse.io/canonical/jobs/5370815) | **`APPROVE_WITH_LIMITATIONS`** (Recomendado para Alpha privada; especialización en C/Rust y kernel Linux; requiere inglés profesional) |
| `CAND-greenhouse-public-job-board-template-3257589` | **Canonical** | Software Engineer - Python - Cloud - graduate level | Cloud / Backend / Infraestructura | Graduate / Entry-Level | Remoto (`Home Based - Americas`) | `PERU_EXPLICIT` (Región Américas, huso horario Lima) | Indefinido / Tiempo completo | 0 a 1 año (Egresados) | No publicado / Presupuesto anual USD 2,000 aprendizaje, sprints internacionales 2/año, bono anual | [Canonical Greenhouse](https://job-boards.greenhouse.io/canonical/jobs/3257589) | **`APPROVE_WITH_LIMITATIONS`** (Recomendado para Alpha privada; Python, automatización Cloud y CI/CD; requiere inglés profesional) |
| `CAND-greenhouse-public-job-board-template-6448444` | **Canonical** | Associate Linux Support Engineer | Soporte Técnico Avanzado / Redes / Sysadmin | Entry-Level / Associate | Remoto (`Home based - Worldwide`) | `PERU_EXPLICIT` (AMER UTC-5 compatible) | Indefinido / Tiempo completo | 0 a 1 año | No publicado / Presupuesto anual USD 2,000 aprendizaje, sprints internacionales 2/año, bono anual | [Canonical Greenhouse](https://job-boards.greenhouse.io/canonical/jobs/6448444) | **`APPROVE_WITH_LIMITATIONS`** (Recomendado para Alpha privada; troubleshooting en servidores Linux, redes y scripting; requiere inglés fluido) |

---

## 4. Desglose Detallado de Evidencias por Campo

Conforme a la regla de oro de procedencia de Ruta Sistemas (*"Cada afirmación presentada al usuario debe sustentarse en una URL HTTPS oficial y un timestamp verificado"*), cada una de las 5 oportunidades registra evidencias de campo estructuradas en `fieldEvidence`:

### 4.1. Candidato 8379825 — Graduate Software Engineer (Open Source and Linux)
- **ID Candidato:** `CAND-greenhouse-public-job-board-template-8379825`
- **Fuente base:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs`
- **Endpoint detalle:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/8379825`
- **Canal de postulación oficial:** `https://job-boards.greenhouse.io/canonical/jobs/8379825`
- **Evidencias estructuradas (marca `observedAt: 2026-11-20T20:05:00-05:00`):**
  - `title`: Obtenido de endpoint API oficial (`Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu`).
  - `employer`: Confirmado como `Canonical`.
  - `publisher`: Confirmado como `Canonical`.
  - `externalReference`: Requisition ID `8379825`.
  - `applyUrl`: Host oficial `job-boards.greenhouse.io`.
  - `publishedAt`: `2026-11-16` (confirmado en campo `first_published`).
  - `location`: Declarado como `Home based - Worldwide`.
  - `mode`: Clasificado como `Remoto` conforme a especificación del puesto.
  - `opportunityType`: Clasificado como `Empleo` (cohorte de graduados universitarios 2026/2027).
  - `benefits`: USD 2,000 anuales de presupuesto de desarrollo personal; sprints presenciales internacionales semestrales; bono por rendimiento.
  - `requirements`: Egresado/graduando 2026/2027 en Ciencias de la Computación, Informática o STEM; código en Python, Rust, C/C++, Go o Java; Linux/Ubuntu; proyectos personales; inglés profesional.

### 4.2. Candidato 6707669 — Junior Ubuntu Software Engineer
- **ID Candidato:** `CAND-greenhouse-public-job-board-template-6707669`
- **Endpoint detalle:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/6707669`
- **Canal de postulación oficial:** `https://job-boards.greenhouse.io/canonical/jobs/6707669`
- **Evidencias estructuradas (marca `observedAt: 2026-11-20T20:05:00-05:00`):**
  - `title`: `Junior Ubuntu Software Engineer`.
  - `employer`: `Canonical`.
  - `publisher`: `Canonical`.
  - `externalReference`: `6707669`.
  - `applyUrl`: `https://job-boards.greenhouse.io/canonical/jobs/6707669`.
  - `publishedAt`: `2025-11-07` (actualizado y vigente al `2026-08-05`).
  - `location`: `Home based - Worldwide`.
  - `mode`: `Remoto`.
  - `opportunityType`: `Empleo` (Junior).
  - `benefits`: Presupuesto anual de desarrollo personal USD 2,000; sprints internacionales semestrales; bono por desempeño.
  - `requirements`: Grado universitario en Computación o STEM; Rust, Go, Python, Flutter o C/C++; depuración en Linux y sistemas CI/CD; inglés profesional.

### 4.3. Candidato 5370815 — Junior Linux Kernel Engineer
- **ID Candidato:** `CAND-greenhouse-public-job-board-template-5370815`
- **Endpoint detalle:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/5370815`
- **Canal de postulación oficial:** `https://job-boards.greenhouse.io/canonical/jobs/5370815`
- **Evidencias estructuradas (marca `observedAt: 2026-11-20T20:05:00-05:00`):**
  - `title`: `Junior Linux Kernel Engineer - Ubuntu`.
  - `employer`: `Canonical`.
  - `publisher`: `Canonical`.
  - `externalReference`: `5370815`.
  - `applyUrl`: `https://job-boards.greenhouse.io/canonical/jobs/5370815`.
  - `publishedAt`: `2024-02-25` (actualizado y vigente al `2026-08-05`).
  - `location`: `Home based - Worldwide`.
  - `mode`: `Remoto`.
  - `opportunityType`: `Empleo` (Junior).
  - `benefits`: Presupuesto de USD 2,000 anuales de capacitación; viajes semestrales a sprints técnicos de equipo; bono de fin de año.
  - `requirements`: Programación en C y/o Rust; Git; arquitectura y fundamentos del kernel de SO; scripting en Python/Bash; empaquetado Linux; inglés profesional.

### 4.4. Candidato 3257589 — Software Engineer (Python - Cloud - Graduate Level)
- **ID Candidato:** `CAND-greenhouse-public-job-board-template-3257589`
- **Endpoint detalle:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/3257589`
- **Canal de postulación oficial:** `https://job-boards.greenhouse.io/canonical/jobs/3257589`
- **Evidencias estructuradas (marca `observedAt: 2026-11-20T20:05:00-05:00`):**
  - `title`: `Software Engineer - Python - Cloud - graduate level`.
  - `employer`: `Canonical`.
  - `publisher`: `Canonical`.
  - `externalReference`: `3257589`.
  - `applyUrl`: `https://job-boards.greenhouse.io/canonical/jobs/3257589`.
  - `publishedAt`: `2021-06-28` (actualizado y vigente al `2026-08-05`).
  - `location`: `Home Based - Americas` (huso horario coincidente con Lima, Perú).
  - `mode`: `Remoto`.
  - `opportunityType`: `Empleo` (Graduate/Entry-Level).
  - `benefits`: USD 2,000 presupuesto anual de aprendizaje; viajes semestrales de integración de equipo; revisión salarial anual; bono por desempeño.
  - `requirements`: Bachiller en Ciencias de la Computación o carrera STEM afín; dominio de Python sobre Linux; administración de servidores Ubuntu, CI/CD y nubes públicas/privadas; inglés profesional.

### 4.5. Candidato 6448444 — Associate Linux Support Engineer
- **ID Candidato:** `CAND-greenhouse-public-job-board-template-6448444`
- **Endpoint detalle:** `https://boards-api.greenhouse.io/v1/boards/canonical/jobs/6448444`
- **Canal de postulación oficial:** `https://job-boards.greenhouse.io/canonical/jobs/6448444`
- **Evidencias estructuradas (marca `observedAt: 2026-11-20T20:05:00-05:00`):**
  - `title`: `Associate Linux Support Engineer`.
  - `employer`: `Canonical`.
  - `publisher`: `Canonical`.
  - `externalReference`: `6448444`.
  - `applyUrl`: `https://job-boards.greenhouse.io/canonical/jobs/6448444`.
  - `publishedAt`: `2025-02-10` (actualizado y vigente al `2026-08-05`).
  - `location`: `Home based - Worldwide`.
  - `mode`: `Remoto`.
  - `opportunityType`: `Empleo` (Associate/Entry-Level).
  - `benefits`: Presupuesto anual de capacitación USD 2,000; sprints semestrales presenciales; bono por desempeño; beneficios acordes al país de residencia.
  - `requirements`: Grado en Ingeniería de Sistemas, Informática, Computación o Telecomunicaciones; resolución de problemas en servidores Linux; redes (cortafuegos, bridging, DNS); fundamentos de scripts (Bash, Python, Go o C); inglés profesional fluido.

---

## 5. Auditoría de Fuentes y Justificación de Vacantes Descartadas

En cumplimiento estricto de las directivas de curación y el principio *"No confundir Remote con elegibilidad desde Perú"*, se examinaron individualmente las vacantes de fuentes alternativas en la bandeja local, procediendo a su descarte formal y justificado:

```
                                  [ EVALUACIÓN DE FUENTES ]
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
         [ CANONICAL ]                 [ COOKUNITY ]                 [ WIKIMEDIA /
    (Greenhouse: canonical)       (Greenhouse: cookunity)             DELIVERECT ]
               │                             │                             │
    5 Vacantes Aprobadas          1 Promovida en R2-A-05            6 Vacantes Descartadas
     con Limitaciones para         (Supply Chain Analyst             - Restricción Territorial
      la Alpha Privada             -> OP-005)                        - Experiencia Senior
      (Graduate / Junior)         1 Descartada                      (EE.UU., Países Bajos,
                                   (Soporte: >4 años exp)            18 países excluyen Perú)
```

### 5.1. Wikimedia Foundation (Greenhouse API)
- **`8268853` (Software Engineering Internship Program 2027):**
  - *Causa de descarte:* Inelegibilidad geográfica estricta (`COUNTRY_RESTRICTED`).
  - *Justificación pericial:* Aunque el título declara "Remote", el texto oficial estipula taxativamente que la contratación se limita a residentes en una nómina cerrada de estados de Estados Unidos. Postulantes residentes en Perú son legalmente inelegibles.
- **`8210560` (Senior Data Scientist), `8397050` (Senior SRE), `8268142` (Senior Software Engineer Android):**
  - *Causa de descarte:* Nivel de experiencia no admisible (`NOT_RELEVANT`) e inelegibilidad geográfica (`COUNTRY_RESTRICTED`).
  - *Justificación pericial:* Exigen entre 5 y 10 años de trayectoria comprobada (roles Senior), violando el límite máximo de 2 años de experiencia de Ruta Sistemas. Adicionalmente, la política laboral corporativa de Wikimedia restringe las contrataciones remotas a 18 países donde Perú no se encuentra incluido.

### 5.2. Deliverect (Lever Postings API)
- **`5e9142c8-4612-4c96-87c0-2072e2f141d6` (Engineering Intern):**
  - *Causa de descarte:* Inelegibilidad geográfica y presencialidad física (`COUNTRY_RESTRICTED`).
  - *Justificación pericial:* Puesto formativo presencial ubicado en Amersfoort (Países Bajos), que exige residencia local y permiso de trabajo de la Unión Europea. Inaccesible para postulantes en territorio peruano.

### 5.3. CookUnity (Greenhouse API)
- **`8034712003` (Product Support Engineer — Latam Remote):**
  - *Causa de descarte:* Exceso de experiencia previa requerida (`NOT_RELEVANT`).
  - *Justificación pericial:* Aunque es una vacante de tecnología en modalidad remota abierta a Latinoamérica, exige taxativamente más de 4 años de experiencia en soporte de producto, análisis funcional o gestión de incidentes. Supera el umbral máximo de 2 años fijado para perfiles formativos/junior en Ruta Sistemas.

---

## 6. Deduplicación Determinista y Control de Colisiones

Se ejecutó el módulo de deduplicación determinista (`collector/dedup.py`) a través de la CLI unificada `scripts/editorial_cli.py`:

```powershell
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
```

### Resultados de Deduplicación:
- **Candidatos evaluados en bandeja:** 12
- **Duplicados exactos (`EXACT_DUPLICATE`):** **0**
- **Colisiones de identificador (`IDENTIFIER_COLLISION`):** **0**
- **Posibles duplicados por firma heurística (`POSSIBLE_DUPLICATE`):** **0**

### Cruce contra el Catálogo Canónico (`opportunities.seed.json`):
- Los 5 candidatos propuestos (`8379825`, `6707669`, `5370815`, `3257589`, `6448444`) presentan claves primarias y secundarias completamente disjuntas respecto a los registros del catálogo:
  - No colisionan con `OP-005` (CookUnity *Supply Chain Analyst*, Requisition `8039990003`).
  - No colisionan con los registros demostrativos (`OP-001` a `OP-004`, `QA-001`).
- El candidato `8039990003` de CookUnity, conservado en la bandeja local para trazabilidad histórica, está debidamente identificado como promovido en R2-A-05, evitando cualquier duplicación involuntaria.

---

## 7. Verificación de Integridad y Protección Canónica

En estricta observancia de los límites de autorización, los archivos canónicos no fueron tocados durante la ejecución de este bloque:

| Archivo Canónico | Hash SHA-256 Inicial | Hash SHA-256 Final | Estado |
|---|---|---|---|
| `data/opportunities.seed.json` | `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` | `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` | **INALTERADO (100% IDÉNTICO)** |
| `data/opportunities.json` | `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` | `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` | **INALTERADO (100% IDÉNTICO)** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **INALTERADO (100% IDÉNTICO)** |

---

## 8. Resultados de la Suite de Pruebas y Validación Técnica

Se verificó el estado integral del repositorio mediante la ejecución completa de las herramientas de auditoría:

```powershell
# 1. Validación de candidatos con verificación pericial de evidencias
python scripts/validate_candidates.py data/candidates/inbox.local.json --verify-evidence
# Resultado: Bandeja local válida: 12 candidatos; 0 errores; todas las evidencias ALL_FRESH.

# 2. Inspección editorial estructurada
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json
# Resultado: 6 pending_review (5 Canonical + 1 CookUnity promovida), 6 rejected.

# 3. Reporte consolidado de observabilidad
python scripts/editorial_cli.py report data/candidates/inbox.local.json
# Resultado: 0 errores de Schema 2, 0 colisiones, 12 candidatos con frescura verificada.

# 4. Verificación de catálogo canónico y calidad
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Catálogo válido; 6 registros; snapshot coincide con la fuente canónica.

# 5. Suite de pruebas unitarias e integración Python
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 3.740s - OK (100% aprobadas).
```

---

## 9. Gobernanza de la Alpha Privada y Puerta de Control Humano

### 9.1. Condiciones para la Alpha Privada (Círculo Íntimo)
Las 5 oportunidades propuestas de Canonical Ubuntu están clasificadas como **`APPROVE_WITH_LIMITATIONS`**:
1. **Ámbito de uso autorizado:** Exclusivamente para la Alpha privada de uso personal del propietario y su círculo reducido de amigos (evaluación cualitativa informal no comercial).
2. **Restricción legal para publicación abierta:** La fuente `canonical-careers` mantiene su estado de términos de reutilización en revisión (`pending_review` en `collector/sources.json`). No se autoriza su publicación comercial masiva ni distribución pública indexada sin previa validación legal expresa.
3. **Requisito idiomático:** Todos los puestos de Canonical exigen inglés profesional hablado y escrito, aspecto que debe señalarse de forma transparente a los participantes de la Alpha privada.

### 9.2. Decisiones Pendientes que Requieren Intervención del Propietario
El sistema técnico no usurpa la autoridad del propietario. Quedan listadas las siguientes decisiones para su revisión:
- [ ] **Decisión A — Aprobación del lote completo (5 vacantes):** Autorizar la incorporación de los 5 candidatos de Canonical (`8379825`, `6707669`, `5370815`, `3257589`, `6448444`) a la Alpha privada, enriqueciendo el catálogo con opciones en Desarrollo, Cloud, Kernel y Soporte.
- [ ] **Decisión B — Aprobación selectiva (subconjunto):** Seleccionar prioritariamente los puestos con mayor foco en desarrollo general (`8379825` Graduate Software Engineer y `3257589` Python Cloud).
- [ ] **Decisión C — Postergación:** Mantener las oportunidades en staging (`inbox.local.json`) hasta recibir retroalimentación adicional del círculo de confianza.

---

## 10. Conclusiones y Estado del Proyecto

1. **Cuello de botella de contenido resuelto a nivel de staging:** Se prepararon y validaron 5 oportunidades reales, legítimas y pertinentes para estudiantes y egresados de Ingeniería de Sistemas en el Perú, cubriendo cuatro familias profesionales clave.
2. **Gobernanza y trazabilidad intachable:** Cero modificaciones involuntarias a los catálogos de producción, cero dependencias introducidas y estricto cumplimiento de Candidate Schema 2 con evidencias HTTPS auditadas.
3. **El proyecto se encuentra listo para la decisión del propietario**, manteniendo las líneas de investigación formal R3-02 en `NOT_STARTED / PENDING_HUMAN`, y las fases R3-03, R4 y R5 en sus respectivos bloqueos gobernados.
