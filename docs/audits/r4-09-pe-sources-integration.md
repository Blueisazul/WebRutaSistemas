# R4-09-PE-SOURCES-01 — Integración de Fuentes Peruanas: Estado, Empresas y Oportunidades de Sistemas

**Fecha de evaluación:** 22 de noviembre de 2026  
**Rama de trabajo:** `integration/r1-02c`  
**Estado:** `DONE` / `READY_FOR_OWNER_REVIEW`  
**Responsables periciales:** Principal Software Architect, Senior Software Engineer, OSS Integration Specialist, Data Acquisition Engineer, Technical Auditor.

---

## 1. Resumen Ejecutivo

El catálogo publicado de Ruta Sistemas (v0.1-pre / R4-08) presentaba una notable asimetría geográfica y lingüística: tras la promoción de la Opción B de R4-07-REV-01, 93 de las 99 oportunidades del catálogo corresponden a vacantes remotas de empleadores internacionales publicadas en inglés (Canonical y Sezzle), con una única vacante profesional en Perú (*Supply Chain Analyst* en CookUnity, `OP-005`) y 5 fichas históricas/demostrativas.

La misión de **R4-09-PE-SOURCES-01** fue resolver esta brecha de manera estructural, incorporando fuentes oficiales y sostenibles en el Perú para estudiantes, egresados y profesionales iniciales de Ingeniería de Sistemas, Computación e Informática.

### Logros Principales de R4-09:
1. **Prospección y Verificación en Vivo de Fuentes Peruanas:**
   - Se evaluaron empíricamente 9 fuentes peruanas. Se verificó el acceso público factual (HTTP 200 OK) sin CAPTCHA ni barreras anti-bot en:
     * **OSITRAN Convocatorias** (`oportunidadlaboral.ositran.gob.pe`): portal público con convocatorias CAS y prácticas pre/profesionales de TI.
     * **Defensoría del Pueblo CAS** (`www.defensoria.gob.pe`): tabla oficial de convocatorias CAS de nivel nacional con canal de postulación en línea.
     * **UTP HiringRoom Campus** (`utp.hiringroomcampus.com`): portal universitario con especificación Schema.org `JobPosting` en JSON-LD.
2. **Extracción PDF Nativa sin Dependencias Externas (Zero-Dependency OSS):**
   - Se desarrolló un extractor de texto plano para bases y perfiles en formato PDF (`extract_text_from_pdf_bytes`) utilizando el módulo nativo `zlib` de Python para descomprimir flujos `FlateDecode` (`stream...endstream`) e interpretar operadores PDF estándar (`Tj` y `TJ`). Se verificó la extracción de perfiles y subvención económica sin añadir librerías pesadas (cero paquetes pip/npm nuevos).
3. **Adaptadores Conectores Especializados:**
   - Se implementó `collector/pe_connectors.py` con los conectores `ositran-portal`, `defensoria-cas` y `hiringroom-board`, integrados en `collector/policy.py`, `collector/acquisition_runner.py` y `collector/revalidation.py`.
4. **Ingesta Controlada en Staging:**
   - Se ejecutó la ingesta sobre la red viva. De 319 registros evaluados en las fuentes peruanas, 10 fueron clasificados como directamente afines a Sistemas en Perú e ingresados a la bandeja de staging local (`data/candidates/inbox.local.json`), elevando la bandeja a 164 candidatos con 100% de cumplimiento en Candidate Schema 2.
5. **Gobernanza y Salvaguardas de Integridad:**
   - **Catálogo canónico inalterado:** `data/opportunities.seed.json` (99 fichas) y `data/opportunities.json` se conservaron intactos criptográficamente.
   - **Aislamiento de distribución:** `dist/` permanece estrictamente libre de información de staging o datos privados.
   - **Zero deploy:** Ningún commit, push, merge ni despliegue fue realizado en esta fase de adquisición.

---

## 2. Diagnóstico del Catálogo y Justificación de la Brecha

Al cierre de R4-08, la distribución del catálogo canónico de 99 oportunidades reflejaba la siguiente composición:

| Empleador / Entidad | Conector / Origen | Idioma | Nivel | Modalidad | Fichas en Catálogo |
|---|---|---|---|---|---|
| Canonical | Greenhouse ATS | Inglés | Profesional Medio (75) / Junior (5) | Remoto global (Perú elegible) | 80 |
| Sezzle | Greenhouse ATS | Inglés | Profesional Medio (9) / Intern (1) | Remoto global (Perú elegible) | 10 |
| CookUnity | Greenhouse ATS | Español/Inglés | Profesional Medio (1) | Presencial Lima (`OP-005`) | 1 |
| OSITRAN | Registro semilla inicial | Español | Práctica profesional (1) / Preprofesional (1) | Presencial Lima (`OP-001`, `QA-001`) | 2 |
| 42Labs / Launchpad | Registro demostrativo | Español/Inglés | Senior (3) | Remoto (`OP-002`, `OP-003`, `OP-004`) | 3 |
| Otras entidades del Estado peruano | Ninguna | N/A | N/A | N/A | 0 |
| Empresas locales en Perú | Ninguna adicional | N/A | N/A | N/A | 0 |
| **Total** | | | | | **99** |

**Diagnóstico Pericial:**  
Aunque el catálogo ofrece excelentes oportunidades técnicas de trabajo remoto para profesionales con dominio de inglés, la cobertura de vacantes locales en el Estado peruano (modalidades formativas de la Ley N° 28518 y contratos CAS bajo D.L. 1057) y de empresas que contratan directamente en el ecosistema nacional era prácticamente nula. El estudiante o bachiller peruano que busca su primera práctica oficial en Lima o provincias requería fuentes nacionales auditables.

---

## 3. Matriz de Prospección y Viabilidad de Fuentes Peruanas

Se evaluaron empíricamente 9 fuentes potenciales en el ámbito peruano para determinar su viabilidad técnica, legal y operativa:

| Fuente / Entidad | URL Oficial | Inspección HTTP / WAF | Anti-bot / Bloqueos | Clasificación de Viabilidad | Decisión R4-09 |
|---|---|---|---|---|---|
| **OSITRAN Convocatorias** | `https://oportunidadlaboral.ositran.gob.pe/convocatoria?nuevo=1` | HTTP 200 OK (46 KB HTML) | Ninguno; GET directo sin cookies obligatorias | `FEASIBLE_DIRECT` | **Aprobada** (`ositran-convocatorias`) |
| **Defensoría del Pueblo CAS** | `https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php` | HTTP 200 OK (765 KB HTML) | Ninguno; tabla HTML pública accesible | `FEASIBLE_DIRECT` | **Aprobada** (`defensoria-del-pueblo-cas`) |
| **UTP HiringRoom Campus** | `https://utp.hiringroomcampus.com/` | HTTP 200 OK (108 KB HTML) | Ninguno; JSON-LD Schema.org `JobPosting` nativo | `FEASIBLE_DIRECT` | **Aprobada** (`utp-hiringroom-campus`) |
| **Talento Perú (SERVIR)** | `https://www.gob.pe/talento-peru` | HTTP 200 en landing; `app.servir.gob.pe` requiere estado de sesión JSF | Java Server Faces dinámico; sin API REST/JSON pública | `MANUAL_ONLY` | Mantener `pending_review` (deshabilitada) |
| **FISI - UNMSM** | `https://sistemas.unmsm.edu.pe/` | HTTP 200 en portal institucional | Tablero informal sin estructuración | `MANUAL_ONLY` | Mantener `pending_review` (deshabilitada) |
| **Culqi (BambooHR)** | `https://culqi.bamboohr.com/careers` | HTTP 200 OK | Requiere renderizado JS pesado en SPA | `FEASIBLE_DEFERRED` | Diferida para fase de ATS privados |
| **Stefanini Perú** | Portal corporativo | HTTP 200 OK | Redirige a portal multinacional con filtros dinámicos | `FEASIBLE_DEFERRED` | Diferida para fase de ATS privados |
| **Computrabajo Perú** | Portal de empleo | HTTP 403 / Cloudflare Turnstile | Anti-bot estricto; prohíbe scraping en ToS | `BLOCKED_ANTI_BOT` | Descartada formalmente |
| **Bumeran Perú** | Portal de empleo | HTTP 403 / Imperva WAF | Anti-bot estricto; prohíbe scraping en ToS | `BLOCKED_ANTI_BOT` | Descartada formalmente |

---

## 4. Solución Técnica e Implementación de Adaptadores

### 4.1 Extractor de Texto PDF Estándar (Zero-Dependency)
En `collector/pe_connectors.py`, la función `extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str` realiza la extracción de documentos PDF mediante:
- Búsqueda de bloques binarios `stream...endstream`.
- Descompresión en memoria con `zlib.decompress(stream)` (con fallback para streams raw deflate `zlib.decompress(stream, -15)` o streams ya en texto plano).
- Decodificación de operadores gráficos de texto PDF:
  * Operador `Tj`: `(texto) Tj`
  * Operador `TJ`: `[(texto) -100 (otro texto)] TJ`
- Extracción de subvención mensual (e.g. `S/. 1,530.00`) y requisitos académicos mínimos.

### 4.2 Conectores Especializados
- **`ositran-portal` (`transform_ositran_html`, `fetch_ositran_convocatorias`):**
  * Parsea bloques `<h3>` que identifican cada concurso de prácticas o CAS.
  * Extrae código de convocatoria (`029-2026`, `027-2026`), título y tipo de oportunidad (*Prácticas* o *CAS*).
  * Asocia enlaces de bases PDF y portal de postulación directa (`https://oportunidadlaboral.ositran.gob.pe/postular?id=...`).
  * Registra estado de resultados finales en `decisionNote`.
- **`defensoria-cas` (`transform_defensoria_html`, `fetch_defensoria_cas`):**
  * Analiza la tabla `summary="listado de convocatorias"` identificando filas con código oficial `CAS XXX-2026-DP`.
  * Extrae la denominación del cargo desde la columna "Objeto de la Convocatoria".
  * Enlaza a las bases oficiales en PDF y fija el portal oficial de postulación institucional (`https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php`).
- **`hiringroom-board` (`transform_hiringroom_html`, `fetch_hiringroom_board`):**
  * Procesa la especificación semántica estándar `JobPosting` de Schema.org en JSON-LD embebido en las páginas de detalle de UTP HiringRoom.

---

## 5. Gobernanza de Acceso y Actualización de Políticas

En `collector/sources.json` y `collector/policy.py`:
- Se amplió `FETCH_CONNECTORS` para autorizar:
  ```python
  FETCH_CONNECTORS = {
      "greenhouse-job-board",
      "lever-postings",
      "ositran-portal",
      "defensoria-cas",
      "hiringroom-board",
  }
  ```
- Se registraron formalmente las 3 fuentes peruanas con políticas conservadoras:
  * `maxRequestsPerRun`: 5 peticiones máximas por ejecución.
  * `minDelayMs`: 2000 ms entre solicitudes.
  * `allowedHosts` y `allowedPostingHosts` estrictamente acotados a dominios oficiales (`.gob.pe` y `.hiringroomcampus.com`).
  * `termsReview`: `"approved_employer_site"`.
  * `robotsReview`: `"reviewed_allowed"`.
  * `rightsReview`: `"metadata_only_approved"`.

---

## 6. Resultados de la Ingesta Controlada en Staging

Ejecución pericial con `collector/acquisition_runner.py`:

```
=== PILOTO DE ADQUISICIÓN CONTROLADA MULTIFUENTE (R4-09) ===
Fuentes evaluadas:              3 (Exitosas: 3, Fallidas: 0)
Total oportunidades capturadas: 319
Total filtradas relevantes:     10
Total descartadas (perfil/geo): 309
Total duplicadas detectadas:    0
Nuevos candidatos en staging:   10
Estado de validación:           VÁLIDO (0 errores de esquema)
```

### Distribución de Candidatos en Staging Acumulado (`data/candidates/inbox.local.json`):

| Fuente | Entidad / Empleador | Conector | Previo R4-08 | Nuevos R4-09 | Total Staging |
|---|---|---|---|---|---|
| `greenhouse-canonical` | Canonical | Greenhouse ATS | 97 | 0 | 97 |
| `greenhouse-public-job-board-template` | Canonical (Piloto) | Greenhouse ATS | 23 | 0 | 23 |
| `greenhouse-sezzle` | Sezzle | Greenhouse ATS | 22 | 0 | 22 |
| `greenhouse-cookunity` | CookUnity | Greenhouse ATS | 4 | 0 | 4 |
| `lever-kavak` | Kavak | Lever ATS | 4 | 0 | 4 |
| `lever-fintual` | Fintual | Lever ATS | 3 | 0 | 3 |
| `lever-public-postings-template` | Fintual (Piloto) | Lever ATS | 1 | 0 | 1 |
| **`ositran-convocatorias`** | **OSITRAN** | **`ositran-portal`** | **0** | **3** | **3** |
| **`defensoria-del-pueblo-cas`** | **Defensoría del Pueblo** | **`defensoria-cas`** | **0** | **7** | **7** |
| **Total General** | | | **154** | **10** | **164** |

---

## 7. Análisis Editorial de Candidatos Peruanos Ingestados

### 7.1 OSITRAN (3 Candidatos Formativos / Prácticas)
1. **`CAND-ositran-convocatorias-029-2026`:**
   - **Título:** *Practicantes Profesionales universitarios (3 vacantes) - Especialidad: Ing. Sistemas, Software, Informática, Mecatrónica para Jefatura de TI*.
   - **Tipo:** Prácticas Profesionales.
   - **Nivel:** Egresado / Bachiller (Nivel Inicial/Medio).
   - **Ubicación / Modalidad:** Lima, Perú | No informado (*fail-closed*).
   - **Subvención estimada en bases:** S/. 1,530.00 mensual.
   - **Pertinencia:** `DIRECT`. Alta idoneidad para soporte de sistemas e infraestructura TI.
2. **`CAND-ositran-convocatorias-027-2026`:**
   - **Título:** *Practicante Preprofesional de Ingeniería de Sistemas, Computación e Informática para la Jefatura de Contratos Portuarios*.
   - **Tipo:** Prácticas Preprofesionales.
   - **Nivel:** Estudiante universitario activo.
   - **Ubicación / Modalidad:** Lima, Perú | No informado.
   - **Pertinencia:** `DIRECT`. Gestión de sistemas de información contractual.
3. **`CAND-ositran-convocatorias-026-2026`:**
   - **Título:** *Practicante Profesional de Ingeniería de Sistemas, Computación e Informática para la Jefatura de Contratos Portuarios*.
   - **Tipo:** Prácticas Profesionales.
   - **Nivel:** Egresado / Bachiller.
   - **Ubicación / Modalidad:** Lima, Perú | No informado.
   - **Pertinencia:** `DIRECT`.

### 7.2 Defensoría del Pueblo (7 Candidatos CAS Profesionales)
1. **`CAND-defensoria-del-pueblo-cas-CAS-185-2026-DP`:**
   - **Título:** *Analista en Desarrollo de Sistemas* (Oficina de Tecnologías de la Información).
   - **Tipo:** Contratación Administrativa de Servicios (CAS).
   - **Nivel:** Bachiller en Ing. de Sistemas, Computación o Software.
   - **Ubicación / Modalidad:** Lima, Perú | No informado.
   - **Pertinencia:** `DIRECT`. Desarrollo y mantenimiento de aplicativos institucionales.
2. **`CAND-defensoria-del-pueblo-cas-CAS-118-2026-DP`:**
   - **Título:** *Analista en Desarrollo de Sistemas* (OTI).
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`.
3. **`CAND-defensoria-del-pueblo-cas-CAS-117-2026-DP`:**
   - **Título:** *Analista en Redes* (OTI).
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`. Redes de comunicación, cableado estructurado, switches y telecomunicaciones.
4. **`CAND-defensoria-del-pueblo-cas-CAS-116-2026-DP`:**
   - **Título:** *Analista en Desarrollo de Sistemas* (OTI - 3 vacantes).
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`.
5. **`CAND-defensoria-del-pueblo-cas-CAS-21-2026-DP`:**
   - **Título:** *CAS 21-2026-DP - Oficina de Infraestructura y Seguridad Integral*.
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`. Seguridad física e infraestructura tecnológica.
6. **`CAND-defensoria-del-pueblo-cas-CAS-20-2026-DP`:**
   - **Título:** *Especialista en Arquitectura de Software e Interoperabilidad III*.
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`. Arquitectura SOA, APIs institucionales e interoperabilidad estatal (PIDE).
7. **`CAND-defensoria-del-pueblo-cas-CAS-17-2026-DP`:**
   - **Título:** *Analista de Datos*.
   - **Tipo:** CAS.
   - **Pertinencia:** `DIRECT`. Analítica de datos, tableros de control y bases de datos relacionales.

---

## 8. Análisis de Deduplicación y Detección de Colisiones

El motor determinista `collector/dedup.py` evaluó los 10 nuevos candidatos frente a:
1. El lote entrante (*batch*).
2. La bandeja existente de staging (`inbox.local.json`).
3. El catálogo canónico (`opportunities.seed.json` de 99 fichas).

### Resultados de Deduplicación:
- **`EXACT_DUPLICATE`:** 0 casos. Cada candidato cuenta con una clave primaria única (`sourceId` + `externalReference`).
- **`IDENTIFIER_COLLISION`:** 0 casos. No hubo reutilización indebida de identificadores entre distintas entidades.
- **`POSSIBLE_DUPLICATE`:** 3 avisos informativos detectados entre los CAS de Defensoría:
  * `CAS-116-2026-DP`, `CAS-118-2026-DP` y `CAS-185-2026-DP` comparten el mismo empleador (*Defensoría del Pueblo*) y título normalizado (*Analista en Desarrollo de Sistemas*).
  * El motor emitió la recomendación: `"Revisar manualmente: posible duplicado; no fusionar automáticamente"`.
  * La inspección pericial confirmó que corresponden a tres convocatorias separadas en fechas y bases distintas, por lo que su mantenimiento como registros independientes en staging es técnicamente correcto.

---

## 9. Evidencias Rastreables y Principio Fail-Closed

De acuerdo con las directrices de gobernanza de Ruta Sistemas:
1. **Modalidad de Trabajo:** Ni en OSITRAN ni en Defensoría se asumió modalidad "Presencial" ni "Remota" sin declaración explícita en las bases del anuncio. En ambos casos, el campo `mode` quedó registrado estrictamente como `"No informado"` (*fail-closed*).
2. **Salarios y Fechas Límite:** Ningún dato no acreditado documentalmente fue inferido. Los campos no informados en la tabla pública permanecen como `None`, acompañados de las advertencias correspondientes en `validate_candidates.py`.
3. **Evidencias Estructuradas:** Cada candidato incluye 5 objetos en `fieldEvidence` vinculados a URLs HTTPS válidas (enlaces a bases oficiales en PDF y portales institucionales de postulación).

---

## 10. Verificación de Integridad Canónica y Aislamiento

- **Catálogo Canónico Semilla (`data/opportunities.seed.json`):**  
  * Hash SHA-256 verificado e inalterado.
  * Total de fichas: **99** (94 activas + 5 demostrativas).
- **Snapshot de Producción (`data/opportunities.json`):**  
  * 100% idéntico y sincronizado con el catálogo semilla (`build_catalog.py --check` exitoso).
- **Directorio de Distribución (`dist/`):**  
  * `python scripts/pages_artifact.py` ejecutado limpiamente.
  * Contiene únicamente el catálogo de 99 fichas, sin filtración de archivos `.local.json` ni candidatos en borrador.

---

## 11. Batería Completa de Aseguramiento de Calidad

| Suite / Herramienta de Prueba | Pruebas Ejecutadas | Resultado | Observaciones |
|---|:---:|:---:|---|
| **Python Unit Tests** (`test_*.py`) | **232** | **APROBADO (100%)** | 6 nuevas pruebas en `test_pe_connectors.py` |
| **Playwright E2E Suite** (Chromium) | **15** | **APROBADO (100%)** | UI, filtros, navegación y detalle |
| **Playwright E2E Suite** (Mobile) | **15** | **APROBADO (100%)** | Vista estrecha y responsividad móvil |
| **Playwright E2E Suite** (Narrow) | **15** | **APROBADO (100%)** | Accesibilidad WCAG 2.1 AA |
| **Total Playwright E2E** | **45** | **APROBADO (100%)** | Duración: ~58s |
| **Validador de Candidatos** (`validate_candidates.py`) | 164 candidatos | **VÁLIDO** | 0 errores de esquema |
| **Validador de Catálogo** (`validate_catalog.py`) | 99 oportunidades | **VÁLIDO** | 99 fichas conformes |
| **Sincronización de Catálogo** (`build_catalog.py --check`) | 99 oportunidades | **VÁLIDO** | Paridad semilla / snapshot |
| **Integridad de Artefacto Pages** (`pages_artifact.py`) | Directorio `dist/` | **VÁLIDO** | Cero fugas de staging |

---

## 12. Estado del Roadmap Maestro y Próximos Pasos

### Estado Actual:
- `R4-09-PE-SOURCES-01` queda registrado formalmente como **`DONE`**.
- La bandeja de staging cuenta con 10 candidatos peruanos de alta calidad técnica listos para evaluación editorial humana.
- Se respetó la prohibición expresa de realizar commit, push, merge a `main` o despliegue a GitHub Pages en este bloque.

### Próximos Pasos para el Propietario del Proyecto:
1. **Revisión Editorial Humana:** El propietario puede inspeccionar los 10 candidatos peruanos en `data/candidates/inbox.local.json` para definir qué oportunidades merecen promoción al catálogo activo en la siguiente sesión editorial.
2. **Autorización de Promoción (Futuro R4-10):** En caso de decidirse la incorporación de los puestos de OSITRAN y Defensoría del Pueblo, se asignarán identificadores de catálogo (`OP-099` en adelante), actualizando el catálogo canónico y ejecutando el despliegue a producción bajo autorización formal.
