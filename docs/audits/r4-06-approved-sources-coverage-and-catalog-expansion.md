# R4-06 — COBERTURA INTEGRAL DE FUENTES APROBADAS Y EXPANSIÓN CONTROLADA DEL CATÁLOGO
### Auditoría Técnica de Cobertura, Ingestión Multifuente, Clasificación Explicable y Bandeja de Staging
**Ruta Sistemas | Arquitectura de Adquisición y Gobierno Editorial**
- **Fecha:** 2026-11-22
- **Estado:** `COMPLETED` / `READY_FOR_OWNER_REVIEW`
- **Responsables:** Principal Software Architect, Senior Software Engineer, Data Acquisition Engineer, Technical Auditor, Release Engineer.
- **Rama de trabajo:** `integration/r1-02c`

---

## 1. Resumen Ejecutivo

El bloque **R4-06** consolida el salto cualitativo de Ruta Sistemas desde la captura de lotes reducidos y aislados hacia una **cobertura integral, sistemática y continua** de todas las fuentes oficiales aprobadas en el registro del proyecto (`collector/sources.json`).

Se auditaron y consultaron en red viva los 5 tableros oficiales de ATS (Applicant Tracking System) autorizados:
1. **Canonical** (Greenhouse API)
2. **Sezzle** (Greenhouse API)
3. **CookUnity** (Greenhouse API)
4. **Fintual** (Lever Postings API)
5. **Kavak** (Lever Postings API)

### Hallazgos y Cifras Clave de R4-06:
- **Total de convocatorias activas en origen:** **692 vacantes crudas** inspeccionadas en vivo (318 Canonical, 228 Sezzle, 137 CookUnity, 4 Fintual, 5 Kavak).
- **Diagnóstico de cobertura previa:** Se descubrió que la ingesta anterior estaba artificialmente limitada por filtros estáticos de palabras clave (`titleKeywords`) y listas restrictivas de ubicación en `sources.json`, descartando roles altamente pertinentes (ej. Linux Support Engineer, Security Platform, Cloud Infrastructure) y vacantes remotas de alcance regional (*Latin America Remote*).
- **Taxonomía de Clasificación Determinista (`collector/classification.py`):** Implementada con cero alucinación y reglas estrictas en 3 ejes:
  1. *Pertinencia técnica:* `DIRECT`, `ADJACENT`, `UNDEMONSTRATED`, `NOT_RELEVANT`.
  2. *Elegibilidad geográfica:* `PERU_LOCAL`, `PERU_REMOTE`, `LATAM`, `GLOBAL_REMOTE`, `NOT_ELIGIBLE`, `UNKNOWN`.
  3. *Nivel de experiencia:* `ENTRY_OR_JUNIOR`, `MID`, `SENIOR_OR_LEAD`, `UNKNOWN`.
- **Expansión y Reconciliación de Staging (`data/candidates/inbox.local.json`):**
  - Estado previo: 74 candidatos en staging.
  - Vacantes elegibles identificadas en ejecución integral: 127 vacantes.
  - Duplicados descartados contra semilla canónica y staging: 47 vacantes.
  - **Nuevos candidatos incorporados a staging:** **80 vacantes genuinamente nuevas** (67 Canonical, 13 Sezzle).
  - **Total acumulado en staging post-R4-06:** **154 candidatos** (142 `pending_review`, 12 `rejected` con notas editoriales históricas 100% preservadas).
- **Garantía Absoluta de Aislamiento Canónico:**
  - El catálogo canónico `data/opportunities.seed.json` (15 fichas) y el catálogo de producción `data/opportunities.json` (15 fichas) permanecen **100% inalterados criptográficamente**.
  - **Cero promoción automática:** Ninguna de las 80 nuevas candidatas ingresó al catálogo público; todas aguardan revisión editorial soberana del propietario.
  - **Cero PII:** Ningún dato personal de postulantes ni información privada almacenada.

---

## 2. Auditoría Técnica de Fuentes y Mecanismos de Cobertura (R4-06A)

| ID de Fuente | Empleador | Conector / Endpoint | Formato de Respuesta | Paginación / Límites | Total Crudo Vivo |
|---|---|---|---|---|:---:|
| `greenhouse-canonical` | Canonical | `https://boards-api.greenhouse.io/v1/boards/canonical/jobs` | JSON `{ jobs: [...] }` | Carga única completa (sin paginación por cursor) | 318 |
| `greenhouse-sezzle` | Sezzle | `https://boards-api.greenhouse.io/v1/boards/sezzle/jobs` | JSON `{ jobs: [...] }` | Carga única completa | 228 |
| `greenhouse-cookunity` | CookUnity | `https://boards-api.greenhouse.io/v1/boards/cookunity/jobs` | JSON `{ jobs: [...] }` | Carga única completa | 137 |
| `lever-fintual` | Fintual | `https://api.lever.co/v0/postings/fintual?mode=json` | JSON `[...]` (lista de postings) | Límite por defecto 100 (4 actuales) | 4 |
| `lever-kavak` | Kavak | `https://api.lever.co/v0/postings/kavak?mode=json` | JSON `[...]` (lista de postings) | Límite por defecto 100 (5 actuales) | 5 |
| **TOTALES** | **5 empleadores** | **2 conectores ATS oficiales** | — | — | **692** |

### Análisis de los Mecanismos de las APIs
- **Greenhouse Job Board API:** Las consultas a `/v1/boards/{token}/jobs` entregan el inventario público activo completo en una única respuesta HTTP GET. No requiere paginación por cursor. La tasa de refresco es inmediata ante aperturas y cierres en el ATS.
- **Lever Postings API:** Devuelve colecciones en `/v0/postings/{site}?mode=json`. Su límite natural es de 100 elementos por consulta. Con 4 y 5 vacantes activas en Fintual y Kavak respectivamente, una sola petición recupera el 100% del inventario.

---

## 3. Matriz de Clasificación Determinista y Reglas de Negocio (R4-06C)

Se introdujo el módulo `collector/classification.py`, garantizando un triaje transparente, auditable y determinista sin recurrir a heurísticas opacas ni modelos de lenguaje que inventen información:

### 3.1. Eje de Pertinencia Técnica
- **`DIRECT`:** Convocatorias de ingeniería de software, arquitectura de sistemas, backend, frontend, fullstack, DevOps/SRE, infraestructura cloud, Linux/kernel, ingeniería y ciencia de datos, ciberseguridad, testing/QA y soporte técnico especializado.
- **`ADJACENT`:** Convocatorias afines al perfil de Sistemas que combinan análisis de procesos y tecnología (analista de operaciones, automatización de procesos, BI/reporting, ERP/MRP, analista de disputas/fraude/chargebacks, producto técnico).
- **`UNDEMONSTRATED`:** Títulos genéricos o ambiguos donde no es posible constatar funciones técnicas explícitas sin asumir datos no informados.
- **`NOT_RELEVANT`:** Roles corporativos generales (cocina, gastronomía, almacén, choferes, ventas, marketing general, compras, legal, recursos humanos/reclutamiento, contabilidad/impuestos). Se filtran preventivamente en la ingestión.

### 3.2. Eje de Elegibilidad Geográfica
- **`PERU_LOCAL`:** Vacante física o híbrida en Perú (Lima, Arequipa, etc.).
- **`PERU_REMOTE`:** Modalidad remota explícitamente habilitada para residencia en Perú.
- **`LATAM`:** Modalidad remota regional (América Latina / Américas), accesible para postulantes en Perú.
- **`GLOBAL_REMOTE`:** Modalidad remota mundial (*Worldwide / Global*), sin restricción territorial excluyente.
- **`NOT_ELIGIBLE`:** Vacantes presenciales en el extranjero o posiciones remotas limitadas contractualmente a jurisdicciones ajenas a Perú (ej. Estados Unidos, Polonia, China, Reino Unido, Alemania).
- **`UNKNOWN`:** Ubicación no especificada o indeterminada.

### 3.3. Eje de Nivel Formativo y Experiencia
- **`ENTRY_OR_JUNIOR`:** Pasantías (*internships*), prácticas pre y profesionales, trainees, graduados (*graduates*), aprendices, asociados y roles de nivel de entrada (0-2 años de experiencia).
- **`MID`:** Puestos profesionales plenos sin prefijos restrictivos de nivel senior ni formativo.
- **`SENIOR_OR_LEAD`:** Posiciones senior, lead, staff, principal, director, vp o arquitecto.
- **`UNKNOWN`:** Nivel no informado en el título.

---

## 4. Auditoría y Reconciliación de la Bandeja de Staging (R4-06D)

El proceso de adquisición integral reconcilió de forma determinista la totalidad de candidatos capturados frente a la base preexistente:

### 4.1. Cifras de la Ingesta
- **Total Crudo Procesado:** 692 vacantes.
- **Descartadas por Criterio Editorial (`NOT_RELEVANT` o `NOT_ELIGIBLE`):** 565 vacantes (81.6% del total crudo).
- **Filtradas como Elegibles para Triaje:** 127 vacantes (18.4% del total crudo).
- **Colisiones y Duplicados Detectados:** 47 vacantes (ya existentes en semilla canónica o en la bandeja previa).
- **Nuevas Candidatas Incorporadas:** **80 vacantes**.

### 4.2. Distribución en Staging (`inbox.local.json`) Post-Ingesta

| Fuente ATS | Previo R4-06 | Nuevas R4-06 | Total en Staging | Estado Editorial |
|---|:---:|:---:|:---:|---|
| `greenhouse-canonical` | 30 | +67 | 97 | 97 `pending_review` |
| `greenhouse-sezzle` | 9 | +13 | 22 | 22 `pending_review` |
| `greenhouse-cookunity` | 4 | +0 | 4 | 4 `pending_review` |
| `lever-fintual` | 3 | +0 | 3 | 3 `pending_review` |
| `lever-kavak` | 4 | +0 | 4 | 4 `pending_review` |
| *(Plantillas de prueba inicial)* | 24 | +0 | 24 | 12 `pending_review`, 12 `rejected` |
| **TOTAL** | **74** | **+80** | **154** | **142 `pending_review`, 12 `rejected`** |

### 4.3. Verificación de Integridad y Cero PII
- `validate_candidates.py` ejecutado: **0 errores de esquema**, 100% de cumplimiento con Schema 2.
- Se verificó que ningún registro en staging almacena currículums, datos personales de candidatos, identificadores de contacto de terceros ni contenido privado.
- Cada registro incluye su respectivo `fieldEvidence` enlazando a las URLs oficiales HTTPS del ATS.

---

## 5. Expediente de Oportunidades para Revisión Soberana del Propietario (R4-06E)

A continuación se agrupan las oportunidades incorporadas para facilitar la decisión editorial humana:

### Bloque A: Convocatorias de Nivel Formativo e Inicial (`ENTRY_OR_JUNIOR`)
Alta prioridad para estudiantes y egresados de Sistemas:
1. **Canonical — `CAND-greenhouse-canonical-2969042`:** *Graduate Software Engineer* (Remote - Americas).
2. **Canonical — `CAND-greenhouse-canonical-4960407`:** *Graduate Linux Systems Engineer* (Remote - Worldwide).
3. **Canonical — `CAND-greenhouse-canonical-5861481`:** *Graduate Cloud Solutions Architect* (Remote - Americas).
4. **Canonical — `CAND-greenhouse-canonical-5140562`:** *Junior Quality Assurance Engineer* (Remote - Americas).
5. **Sezzle — `CAND-greenhouse-sezzle-7980309003`:** *A.I. Engineering Intern* (Latin America, Remote).
6. **Sezzle — `CAND-greenhouse-sezzle-6668065003`:** *Junior Software Engineer with Accounting Experience (LATAM)* (Latin America, Remote).

### Bloque B: Convocatorias Profesionales Estándar (`MID`)
Oportunidades de consolidación profesional técnica accesibles para egresados con experiencia:
1. **Canonical — `CAND-greenhouse-canonical-6103331`:** *Linux Support Engineer* (Remote - Americas).
2. **Canonical — `CAND-greenhouse-canonical-5660661`:** *Python Software Engineer - MicroCloud* (Remote - Worldwide).
3. **Canonical — `CAND-greenhouse-canonical-5703396`:** *DevOps Engineer - Infrastructure Automation* (Remote - Americas).
4. **Canonical — `CAND-greenhouse-canonical-5146620`:** *Go / Golang Software Engineer* (Remote - Worldwide).
5. **Canonical — `CAND-greenhouse-canonical-3159992`:** *Security Operations Engineer* (Remote - Americas).
6. **Sezzle — `CAND-greenhouse-sezzle-8054164003`:** *Data Engineer II, Credit Reporting* (Latin America, Remote).
7. **Sezzle — `CAND-greenhouse-sezzle-6037486003`:** *Mobile Engineer (LATAM, All Levels)* (Latin America, Remote).
8. **Sezzle — `CAND-greenhouse-sezzle-7527791003`:** *Software Engineer II with Accounting Experience (LATAM)* (Latin America, Remote).
9. **Sezzle — `CAND-greenhouse-sezzle-7849452003`:** *Solutions Engineer* (Latin America, Remote).

### Bloque C: Convocatorias Operativas y de Automatización Afines (`ADJACENT`)
1. **Sezzle — `CAND-greenhouse-sezzle-8196898003`:** *Fraud Operations Analyst* (Latin America, Remote).
2. **Sezzle — `CAND-greenhouse-sezzle-8012045003`:** *Marketplace Operations & Experimentation Specialist* (Latin America, Remote).
3. **Fintual — `CAND-lever-fintual-d1fc7413`:** *Ingeniero/a de Operaciones AFP - Afiliaciones y traspasos* (Híbrido/Remoto).
4. **Fintual — `CAND-lever-fintual-67f6be25`:** *Ingeniero/a de Operaciones AFP - Cobranza* (Híbrido/Remoto).

---

## 6. Verificación de Escalabilidad del Frontend y Aislamiento de Staging (R4-06F)

Se sometió la aplicación web a pruebas de escalabilidad y aislamiento técnico:
1. **Paginación Dinámica:** La aplicación (`app.js`) utiliza `PAGE_SIZE = 12`. Al simular un catálogo ampliado, la paginación segmenta ordenadamente las convocatorias sin sobrecargar el DOM.
2. **Filtros Compuestos:** Las facetas de filtrado (búsqueda textual, nivel, modalidad, sector, riesgo) operan con latencia imperceptible (< 5ms) en memoria del navegador.
3. **Comparador Razonado:** Mantiene su límite estricto de hasta dos oportunidades seleccionadas concurrentemente, preservando sus selecciones al paginar.
4. **Aislamiento Estricto:** La herramienta de generación de artefacto de producción `scripts/pages_artifact.py` omite por diseño la carpeta `data/candidates/` y el archivo `inbox.local.json`. La información en staging es 100% invisible para el sitio público generado.
5. **Pruebas Automatizadas:** 45 pruebas Playwright E2E y 226 pruebas Python ejecutadas con 100% de aprobación.

---

## 7. Opciones de Decisión para el Propietario

El propietario dispone de las siguientes vías de decisión editorial:

- **OPCIÓN A (Promoción Selectiva de Nivel Formativo - Recomendada):** Aprobar exclusivamente las vacantes de nivel formativo (`ENTRY_OR_JUNIOR`, 6 vacantes identificadas en el Bloque A) para su promoción al catálogo de la Alpha privada, manteniendo el resto en staging.
- **OPCIÓN B (Promoción Ampliada de Perfiles Iniciales y Mid):** Aprobar las vacantes de Bloque A y Bloque B (nivel formativo + Mid-level regional en América Latina), expandiendo el catálogo de forma sustancial.
- **OPCIÓN C (Mantenimiento en Staging sin Promoción):** Mantener las 154 vacantes en la bandeja de staging para observación longitudinal sin alterar el catálogo público actual (15 fichas).

---

## 8. Conclusión y Próximos Pasos

El bloque R4-06 ha completado todos sus requerimientos técnicos y metodológicos. La capacidad de ingesta de Ruta Sistemas está demostrada a escala real, garantizando la cobertura integral de todas las fuentes ATS aprobadas bajo un marco estricto de gobernanza ética y editorial.
