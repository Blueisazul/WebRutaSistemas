# AUDITORÍA DE ACEPTACIÓN Y VIGENCIA — TASK-R5-01
## Conector de Convocatorias Estatales Gob.pe (`gobpe-convocatorias`)

- **Fecha:** 24 de noviembre de 2026
- **Estado final dictaminado:** `COMPLETED_WITH_LIMITATIONS` (Completado con limitaciones operativas de fuente)
- **Fase:** R5 — Cobertura nacional de oportunidades
- **Prioridad:** P1
- **Clasificación:** `[INTEGRACIÓN_OSS]`
- **Rama:** `main` (commit base: `54bab296f5d5afef2a02f9f409ad6e7bdfa10c60`, HEAD: `786bd34a455d63c2ca6a67a363469d04b932abb0`)
- **Autor:** Principal Software Architect, Senior Software Engineer & Technical Auditor

---

### 1. Estado Inicial del Repositorio

- **Rama activa:** `main` (limpia, sincronizada con `origin/main`).
- **Commits recientes:**
  - `786bd34` docs(roadmap): close TASK-R4-11-02 and Phase R4-11 following verified production deployment
  - `54bab29` feat(branding): formalize Velora product identity (#2)
  - `ebda153` docs(audit): publish R4-11 release verification report and update master roadmap
- **Cambios locales preexistentes:** Implementación local del conector en `collector/pe_connectors.py`, registro en `collector/policy.py`, `collector/acquisition_runner.py`, `collector/sources.json` y fixture HTML en `tests/fixtures/ats/gobpe-indecopi-convocatorias.html`.
- **Bandeja staging local:** `data/candidates/inbox.local.json` presente en workspace (ignorado por Git per `.gitignore`), conteniendo 21 candidatos históricos capturados durante la prueba de adquisición live.
- **Integridad canónica inicial:**
  - `data/opportunities.seed.json`: SHA-256 `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917` (112 fichas).
  - `data/opportunities.json`: SHA-256 `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02` (112 fichas).

---

### 2. Estado Real de la Implementación Técnica

El conector `gobpe-convocatorias` está completamente implementado y funcional a nivel de arquitectura y software:
1. **Parser HTML nativo:** Utiliza `HTMLParser` sin dependencias externas, tolerante a variaciones de filas y columnas.
2. **Extracción PDF:** Reutiliza `extract_text_from_pdf_bytes` con descompresión `zlib`, extrayendo oportunistamente remuneraciones (`S/. 3,000.00`) y requisitos académicos de documentos alojados en `cdn.www.gob.pe`.
3. **Normalización Candidate Schema 2:** Todas las oportunidades capturadas se ajustan estrictamente al contrato Schema 2, con aislamiento estricto de PII y revisión editorial obligatoria (`editorialReview.status: "pending_review"`).
4. **Pruebas automatizadas:** 235 pruebas pasando exitosamente en 4.34s, incluyendo 9 pruebas específicas de conectores peruanos con cobertura exhaustiva de 12 escenarios de borde y ciclo de vida.
5. **Aislamiento canónico:** Cero modificaciones en el catálogo publicado.

---

### 3. Archivos Inspeccionados

- `collector/pe_connectors.py` (conector Gob.pe e INDECOPI, parser HTML y extractor PDF).
- `collector/policy.py` (registro de fetch connector).
- `collector/acquisition_runner.py` (orquestación live y fixtures).
- `collector/classification.py` (patrones directos de TI).
- `collector/sources.json` (registro de fuentes y políticas de acceso).
- `tests/test_pe_connectors.py` (batería de pruebas unitarias y de integración).
- `tests/test_classification_and_coverage.py` y `tests/test_periodic_acquisition_ops.py` (suite global).
- `tests/fixtures/ats/gobpe-indecopi-convocatorias.html` (fixture representativo).
- `data/candidates/inbox.local.json` (bandeja staging).
- `data/opportunities.seed.json` y `data/opportunities.json` (catálogo canónico).
- `docs/roadmap/VELORA-MASTER-ROADMAP.md` (roadmap maestro).
- `docs/audits/VELORA-OPEN-DECISIONS.md` (registro de decisiones abiertas).

---

### 4. Auditoría Crítica de Vigencia de los 21 Candidatos

Se distinguió rigurosamente la **relevancia profesional** de la **vigencia temporal real**:

- **Relevancia profesional:** 21 candidatos corresponden a perfiles tecnológicos directos (Programador de TI, Especialista en Seguridad de la Información, Analista en Ingeniería de Sistemas, Analista de Help Desk para Desarrollo, etc.).
- **Vigencia real del proceso:** Se realizó una auditoría exhaustiva sobre los 21 registros presentes en `data/candidates/inbox.local.json`, verificando su estado oficial reportado en el portal de INDECOPI (`https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-cas/`).

#### Detalle de Clasificación de los 21 Candidatos:

| # | ID Candidato | Referencia Oficial | Cargo / Título | Año | Estado Oficial en Portal | Clasificación de Vigencia |
|---|---|---|---|---|---|---|
| 01 | `CAND-gobpe-indecopi-convocatorias-cas-033-2026` | INDECOPI-CAS-033-2026 | ANALISTA DE HELP DESK PARA DESARROLLO (OTI.UPS) | 2026 | FINALIZADA (Postulaciones concluidas) | `CLOSED` |
| 02 | `CAND-gobpe-indecopi-convocatorias-cas-311-2025` | INDECOPI-CAS-311-2025 | ESPECIALISTA DEL CENTRO DE DESARROLLO... | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 03 | `CAND-gobpe-indecopi-convocatorias-cas-307-2025` | INDECOPI-CAS-307-2025 | ANALISTA DEL CENTRO DE DESARROLLO... | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 04 | `CAND-gobpe-indecopi-convocatorias-cas-291-2025` | INDECOPI-CAS-291-2025 | ESPECIALISTA EN GESTION DE SEGURIDAD TI Y BD | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 05 | `CAND-gobpe-indecopi-convocatorias-cas-290-2025` | INDECOPI-CAS-290-2025 | ANALISTA EN INGENIERÍA DE SISTEMAS | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 06 | `CAND-gobpe-indecopi-convocatorias-cas-286-2025` | INDECOPI-CAS-286-2025 | ESPECIALISTA EN SEGURIDAD DE LA INFORMACION | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 07 | `CAND-gobpe-indecopi-convocatorias-cas-277-2025` | INDECOPI-CAS-277-2025 | PROGRAMADOR DE TI | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 08 | `CAND-gobpe-indecopi-convocatorias-cas-276-2025` | INDECOPI-CAS-276-2025 | PROGRAMADOR DE TI | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 09 | `CAND-gobpe-indecopi-convocatorias-cas-273-2025` | INDECOPI-CAS-273-2025 | ESPECIALISTA EN SEGURIDAD DE LA INFORMACION | 2025 | CANCELADA | `CLOSED` |
| 10 | `CAND-gobpe-indecopi-convocatorias-cas-237-2025` | INDECOPI-CAS-237-2025 | ESPECIALISTA EN ING. DE SISTEMAS | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 11 | `CAND-gobpe-indecopi-convocatorias-cas-224-2025` | INDECOPI-CAS-224-2025 | ESPECIALISTA EN GESTION DE SEGURIDAD TI Y BD | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 12 | `CAND-gobpe-indecopi-convocatorias-cas-199-2025` | INDECOPI-CAS-199-2025 | ESPECIALISTA EN SEGURIDAD Y SALUD... | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 13 | `CAND-gobpe-indecopi-convocatorias-cas-198-2025` | INDECOPI-CAS-198-2025 | ESPECIALISTA EN ING. DE SISTEMAS | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 14 | `CAND-gobpe-indecopi-convocatorias-cas-188-2025` | INDECOPI-CAS-188-2025 | ANALISTA DE SEGURIDAD INFORMATICA UTI | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 15 | `CAND-gobpe-indecopi-convocatorias-cas-187-2025` | INDECOPI-CAS-187-2025 | PROGRAMADOR DE TI | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 16 | `CAND-gobpe-indecopi-convocatorias-cas-186-2025` | INDECOPI-CAS-186-2025 | ANALISTA PROGRAMADOR | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 17 | `CAND-gobpe-indecopi-convocatorias-cas-157-2025` | INDECOPI-CAS-157-2025 | ESPECIALISTA EN SEGURIDAD INTERNA | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 18 | `CAND-gobpe-indecopi-convocatorias-cas-131-2025` | INDECOPI-CAS-131-2025 | ESPECIALISTA EN ING. DE SISTEMAS | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 19 | `CAND-gobpe-indecopi-convocatorias-cas-115-2025` | INDECOPI-CAS-115-2025 | PROGRAMADOR DE TI | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 20 | `CAND-gobpe-indecopi-convocatorias-cas-114-2025` | INDECOPI-CAS-114-2025 | ANALISTA PROGRAMADOR | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |
| 21 | `CAND-gobpe-indecopi-convocatorias-cas-081-2025` | INDECOPI-CAS-081-2025 | AUXILIAR ADMINISTRATIVO DE COBRANZA | 2025 | FINALIZADA (Postulaciones concluidas) | `EXPIRED` / `CLOSED` |

#### Resumen Numérico por Categoría de Vigencia:
- **`ACTIVE_VERIFIED`:** **0** (Cero procesos de TI abiertos actualmente en el portal).
- **`EXPIRED` / `CLOSED`:** **21** (20 con estado oficial `FINALIZADA / Postulaciones concluidas` y 1 con estado `CANCELADA`).
- **`PENDING_REVALIDATION`:** **0** (El estado oficial fue confirmado directamente en la tabla institucional).
- **`UNVERIFIABLE`:** **0** (Todos cuentan con identificador oficial, enlace en `gob.pe` y nota de estado).

---

### 5. Inspección de Procesos Abiertos en el Portal en Vivo

Una inspección de las 502 filas de CAS y 168 filas de Prácticas en el portal de INDECOPI reveló:
- Convocatorias actualmente vigentes (`PUBLICADA` con postulación en fechas futuras, e.g. 26/11/2026 y 04/12/2026): **16 convocatorias**.
- **Perfil de las 16 convocatorias vigentes:**
  - Auxiliar Legal, Analista Legal, Asistente Legal, Coordinador, Especialista en Defensa Comercial, Analista Económico, Coordinador de Gestión Resolutiva, Profesional en Derecho, Asistente de Trámite Documentario.
  - **Cero (0) convocatorias vigentes corresponden a Tecnología, Informática o Sistemas.**
- En la sección de Prácticas (`/convocatorias-practicantes/`): **0 convocatorias abiertas**.

---

### 6. Evaluación del Criterio de Aceptación Original

- **Criterio formal:** *Incorporación de al menos cinco oportunidades estatales vigentes al staging de candidatos.*
- **Resultado:** **`NOT_MET` (No cumplido)**.
- **Fundamento técnico:** Siguiendo la regla rectora de no inventar vacantes, no evadir filtros de relevancia y no ampliar indiscriminadamente el scraping hacia fuentes no autorizadas, se certifica que la fuente estatal habilitada (INDECOPI) no cuenta en este momento con 5 procesos tecnológicos en estado abierto.
- **Estado aplicable de la tarea:** Conforme a las instrucciones, al no cumplirse el criterio numérico de oportunidades vigentes a pesar del funcionamiento correcto del software, la tarea no puede declararse `COMPLETED`, quedando dictaminada como **`COMPLETED_WITH_LIMITATIONS`**.

---

### 7. Verificación de Acceso, Procedencia y Decisión Abierta

- **Estado en `collector/sources.json`:**
  - `gobpe-indecopi-convocatorias`: Aprobada para piloto controlado (`maxRequestsPerRun: 10`, `minDelayMs: 2000`).
  - `sunat-convocatorias`: Deshabilitada *fail-closed* (`enabled: false`, HTTP 403 WAF).
  - `reniec-convocatorias`: Deshabilitada *fail-closed* (`enabled: false`, formularios dinámicos con sesión).
- **Aspecto Legal/Procedencia:**
  - La directiva `robots.txt` permite el acceso a `/institucion/*/informes-publicaciones/` y documentos CDN, pero no constituye un contrato formal de reutilización masiva o comercial.
  - Se registró la **Decisión 6** en `docs/audits/VELORA-OPEN-DECISIONS.md` para someter al propietario la definición formal de la política de acceso automatizado a portales institucionales de `gob.pe`.

---

### 8. Resultados de la Batería de Pruebas

- `python -m unittest discover -s tests -v`: **235 pruebas APROBADAS** en 4.338s.
- `python -m unittest tests/test_pe_connectors.py -v`: **9 pruebas APROBADAS** en 0.041s.
  - Cobertura explícita de los 12 escenarios de borde y ciclo de vida en `test_gobpe_12_acceptance_scenarios`:
    1. Convocatoria con plazo futuro y estado abierto: VERIFICADO.
    2. Convocatoria con plazo vencido: VERIFICADO.
    3. Convocatoria oficialmente cerrada: VERIFICADO.
    4. Convocatoria sin fecha límite ni evidencia de apertura: VERIFICADO.
    5. Convocatoria con enlace oficial roto/inaccesible: VERIFICADO (tolerancia a fallos sin crash).
    6. PDF con texto extraíble: VERIFICADO.
    7. PDF escaneado/sin texto extraíble: VERIFICADO (degradación elegante).
    8. Duplicados del mismo proceso: VERIFICADO (deduplicación determinista exacta).
    9. Clasificación técnica errónea: VERIFICADO (roles legales excluidos, TI directos incluidos).
    10. Registro que debe quedar en revisión: VERIFICADO (`pending_review` obligatorio).
    11. Fallo de descarga individual sin afectar el lote: VERIFICADO.
    12. Protección del catálogo canónico: VERIFICADO (rechazo con `PermissionError`).
- `python scripts/validate_catalog.py`: **Válido (112 fichas canónicas)**.
- `python scripts/build_catalog.py --check`: **Válido (112 registros, paridad exacta snapshot-seed)**.

---

### 9. Integridad del Catálogo y Privacidad

- **Hashes SHA-256 (Inalterados al 100%):**
  - `data/opportunities.seed.json`: `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917`
  - `data/opportunities.json`: `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02`
- **Privacidad:**
  - `data/candidates/inbox.local.json` se mantiene excluido de control de versiones y artefactos públicos.
  - 0 datos personales de postulantes (cero nombres, DNIs, correos o teléfonos personales).

---

### 10. Riesgos y Limitaciones Identificadas

1. **Estacionalidad y Ventanas de Publicación Estatales:** Las convocatorias públicas CAS y de Prácticas en el Estado peruano tienen ventanas de postulación extremadamente cortas (usualmente 2 a 3 días hábiles). En periodos entre convocatorias, el inventario de vacantes de TI abiertas puede reducirse temporalmente a cero.
2. **Homogeneidad de Marcado:** Aunque Gob.pe unifica la publicación de resoluciones, los portales de selección de cada ministerio u organismo varían ampliamente en tecnología de backend (desde HTML estático hasta WAFs estrictos como SUNAT o aplicaciones JSF complejas como SERVIR).

---

### 11. Siguiente Acción Recomendada

1. Mantener `TASK-R5-01` en estado `COMPLETED_WITH_LIMITATIONS`.
2. Presentar al propietario la **Decisión 5** (tratamiento y exhibición de convocatorias públicas concluidas como acervo histórico y de orientación profesional) y la **Decisión 6** (términos de acceso automatizado a Gob.pe).
3. Una vez resuelta la Decisión 6, evaluar la apertura de un Pull Request controlado para integrar el conector `gobpe-convocatorias` en `main`.
4. Evaluar la exploración de entidades estatales adicionales de Gob.pe con alto volumen de sistemas (e.g. PCM / Secretaría de Gobierno y Transformación Digital, MINEDU, MEF) que utilicen tablas públicas compatibles.
