# VELORA-MASTER-ROADMAP — Roadmap Maestro Evolutivo de Velora

- **Versión:** 1.0.0
- **Fecha de emisión:** 23 de noviembre de 2026
- **Estado rector:** Aprobado para evaluación técnica y decisión del propietario
- **Fuente de verdad:** Este documento sustituye las referencias dispersas y unifica el estado histórico con la evolución futura de Velora.

---

## 1. Visión y Principios Rectores

### 1.1 Visión
Convertir a **Velora** en el catálogo nacional confiable de oportunidades profesionales para estudiantes, bachilleres, egresados y profesionales de **Ingeniería de Sistemas, Informática, Computación, Software, Ciberseguridad, Datos y Tecnología en el Perú**.

### 1.2 Principios Rectores de Ingeniería y Producto
1. **Verificabilidad Absoluta (*Fail-Closed*):** Ninguna oportunidad se publica sin evidencia de procedencia, enlace al canal oficial del empleador y confirmación de vigencia.
2. **Claridad sobre Promesas:** Velora no promete trabajo, ascensos ni continuidad; informa condiciones objetivas, modalidades contractuales y riesgos de forma explicable.
3. **OSS-First:** Priorizar herramientas abiertas y estándar (Python standard library, SQLite, Tailwind OSS, herramientas nativas) antes de incorporar servicios comerciales o frameworks pesados.
4. **Backend-less Ligero:** Mantener la distribución estática de alta disponibilidad y bajo costo, delegando la adquisición y validación a procesos locales o CI/CD reproducibles.
5. **No Exclusión por Nivel:** Los niveles formativos (Prácticas), Junior, Mid y Senior son facetas de filtrado para entender oportunidades, no motivos automáticos de exclusión.

---

## 2. Reconciliación Histórica de Hitos (R0 a R4)

Para garantizar trazabilidad sin reabrir bloques ya completados, se formaliza el estado de las fases anteriores:

| Fase / Hito | Denominación Histórica | Estado Real | Evidencia en Repositorio |
|---|---|---|---|
| **R0** | Diagnóstico y Alcance MVP | `DONE` | `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md` |
| **R1** | Estabilización Técnica y UI | `DONE` | `index.html`, `styles.css`, Canvas WebGL2, 0 errores sintácticos |
| **R2** | Flujo Editorial Real | `DONE` | Primera vacante real (`OP-005` CookUnity), contrato editorial de 21 campos |
| **R2-OSS** | Integración Tecnológica OSS | `DONE` | Conectores ATS, extractor JSON-LD, deduplicación determinista, CLI local |
| **R3** | Alpha Privada y Rediseño UX | `DONE` | Rediseño de tarjeta, modal de detalle, comparador, paginación, feedback interno |
| **R4-01 a R4-07** | Piloto Multifuente y Auditorías | `DONE` | Motor `collector/`, validación de evidencias, reconciliación editorial |
| **R4-08** | Promoción de Opción B | `DONE` | 84 vacantes aprobadas de Canonical y Sezzle desplegadas a producción |
| **R4-09** | Integración de Fuentes Peruanas | `DONE` | Conectores OSITRAN, Defensoría, UTP HiringRoom y extractor nativo PDF |
| **R4-10** | Release Nacional y Encora Perú | `DONE` | Incorporación de Encora (`encora10`), catálogo canónico ampliado a 112 fichas |

---

## 3. Estructura de Fases del Roadmap Maestro

```
Fase Inmediata (R4-11) ────────► Estabilización: Paridad Vercel/Pages, Branding Velora y Corrección TTL
       │
Fase Cobertura Nacional (R5) ──► Adquisición Estado (Gob.pe / SERVIR) + Empresas Privadas en Perú
       │
Fase Automatización (R6) ─────► Auto-Publicación Basada en Reglas + Revalidación Background
       │
Fase Valor Profesional (R7) ──► Régimen Laboral (CAS/728), Habilidades y Trayectorias
```

---

## 4. Matriz de Tareas del Roadmap

### FASE INMEDIATA: Estabilización Operativa, Marca y Resiliencia (R4-11)

#### `TASK-R4-11-01` — Sincronización y Despliegue de GitHub Pages
- **Prioridad:** `P0` (Bloqueante operativo)
- **Tipo:** `[REFACTOR/FIX]`
- **Estado:** `DONE` (Completado y verificado en producción el 24-11-2026)
- **Dependencias:** `TASK-R4-11-03` (Integrado en `main` previamente).
- **Objetivo:** Lograr paridad exacta del 100% entre GitHub Pages y Vercel (servir las 112 oportunidades en ambos).
- **Alcance y Ejecución:**
  - Integrado PR #1 (`8b87173`) con la lógica corregida de frescura.
  - Resuelto containment de desbordamiento horizontal en viewport estrecho (`88b244f`).
  - Workflow de CI/CD `.github/workflows/refresh-catalog.yml` ejecutado exitosamente (Run ID: `45433311932`).
  - Artefacto Pages generado con Python 3.12 y publicado a `blueisazul.github.io/WebRutaSistemas/`.
- **Criterios de Aceptación Verificados:**
  1. `https://blueisazul.github.io/WebRutaSistemas/data/opportunities.json` responde HTTP 200, tamaño 537,807 bytes, `total opps: 112` y `schemaVersion: 2` (paridad exacta con Vercel).
  2. En el navegador se renderizan 107 oportunidades activas verificadas, 12 tarjetas en la primera página y 0 errores de consola/página.
- **Evidencia:** Auditada y documentada en `docs/audits/R4-11-RELEASE-VERIFICATION.md`.

#### `TASK-R4-11-02` — Transición Oficial de Identidad Visual y Marca a "Velora"
- **Prioridad:** `P0` (Estratégico de producto)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `DONE` (Integrado en `main` mediante squash merge en PR #2 commit `54bab29`, verificado en CI run `45461949978` y desplegado en producción en GitHub Pages y Vercel)
- **Dependencias:** `TASK-R4-11-01` y `TASK-R4-11-03` (ambas DONE). Decisión 1 de `VELORA-OPEN-DECISIONS.md` aprobada por el propietario.
- **Objetivo:** Unificar la marca del producto bajo el nombre oficial **Velora** en toda la interfaz, metadatos, configuración y documentación.
- **Alcance y Ejecución:**
  - Actualizado `<title>Velora — Oportunidades y Trayectorias en Tecnología</title>` en `index.html`.
  - Actualizado logotipo y texto de cabecera en `index.html`: sustituido "Ruta Sistemas" por "Velora" conservando el distintivo tipográfico y accesibilidad WCAG 2.1 AA.
  - Actualizados textos del Hero (`<span>Oportunidades y trayectorias en tecnología</span>`) y pie de página.
  - Incorporados metadatos OpenGraph (`og:title`, `og:site_name`, `og:description`) y Twitter Cards.
  - Actualizado `app.js` (títulos en vista standalone, 404, retorno a catálogo y consola).
  - Actualizados `canvas.js` y `server.py` con la nueva identidad.
  - Actualizado `package.json` y `package-lock.json` (`name: "velora"`).
  - Reescrito completamente `README.md` público reflejando la escala real de 112 oportunidades, Schema 2, modelo de frescura desacoplado y guías operativas.
  - Actualizadas aserciones en `tests/test_static_contract.py` y `tests/e2e/catalog.spec.cjs`.
- **Criterios de Aceptación Cumplidos y Verificados en Producción:**
  1. La interfaz web muestra consistentemente "Velora" en cabecera, hero, footer y títulos de pestaña en GitHub Pages y Vercel Production.
  2. Todas las pruebas unitarias (232 Python + 14 JS) y 45 pruebas E2E de Playwright aprobaron tanto localmente como en el pipeline de GitHub Actions (`validate` step).
  3. Despliegue automático exitoso vía GitHub Actions run `45461949978` (jobs `validate` y `publish` exitosos).
  4. Cero violaciones de accesibilidad (WCAG 2.1 AA verificado con Axe-core).
  5. Ninguna dependencia externa nueva incorporada; esquema de catálogo Schema v2 intacto.
  6. Catálogo verificado en producción: 112 registros exactos, paridad byte a byte e igualdad de hash SHA-256 (`417b3847942b76dca5eb8750583656626517302637310ddc2759a3d656f62ed8`) entre GitHub Pages y Vercel.
- **Evidencia Documental:** `docs/audits/R4-11-02-VELORA-BRAND-VERIFICATION.md` y `docs/audits/R4-11-02-PR-FINAL-REVIEW.md`.

#### `TASK-R4-11-03` — Desacople del TTL de Frescura en Frontend (Protección contra Apagones y Corrección de Aceptación)
- **Prioridad:** `P0` (Resiliencia y veracidad del catálogo)
- **Tipo:** `[REFACTOR/FIX]`
- **Estado:** `DONE` (Fusionado en `main` mediante PR #1 commit `8b87173` y desplegado en producción)
- **Dependencias:** Ninguna.
- **Objetivo:** Separar ortogonalmente el estado editorial de publicación, el estado de verificación y la antigüedad de la evidencia, garantizando que ninguna oportunidad cuya evidencia superó el TTL se presente falsamente como activa y verificada, sin provocar la desaparición destructiva de las fichas ni un apagón informativo del catálogo.
- **Modelo de Tres Dimensiones Implementado:**
  1. **Estado de Publicación (`publicationStatus`):** Expresa si el registro puede presentarse como oportunidad activa (`active`), si necesita revisión (`unconfirmed`), o si es de consulta histórica (`historical`).
  2. **Estado de Verificación (`verificationStatus`):** Expresa si la vigencia fue confirmada recientemente (`verified`), si está pendiente de revalidación (`stale`), o si no cuenta con evidencia completa (`unverified`).
  3. **Antigüedad de la Evidencia (`lastVerifiedAt` vs `verificationTtlDays`):** Determina deterministamente si la comprobación se encuentra dentro de la ventana de frescura (<= 7 días) o si requiere revalidación (> 7 días, ausente, inválida o futura).
- **Comportamiento Final de los Estados:**
  - **Evidencia reciente y vigente (<= 7 días):** `publicationStatus: 'active'`, `verificationStatus: 'verified'`. Se muestra en la vista activa por defecto con badge `Activa · revisión reciente` y CTA `Ir a postulación`.
  - **Evidencia superior al TTL (> 7 días, ausente o futura):** `publicationStatus: 'unconfirmed'`, `verificationStatus: 'stale'`, `opportunityStatus: 'open'`. Deja de aparecer en la vista activa principal; se conserva accesible mediante el toggle de revisión (`#include-unconfirmed`). Se presenta con badge ámbar `Pendiente de revalidación`, alerta explícita de vigencia no confirmada, acceso a `Ver publicación original` y `Postulación deshabilitada`.
  - **Plazo vencido (`deadline < today`):** `opportunityStatus: 'expired'`, `publicationStatus: 'historical'`.
  - **Cierre confirmado:** `opportunityStatus: 'closed'`, `publicationStatus: 'historical'`.
  - **Inconsistencia estructural:** `publicationStatus: 'unconfirmed'`, `verificationStatus: 'unverified'`.
  - **Ficha demostrativa:** `recordKind: 'demonstration'`, nunca se publica como activa (`unconfirmed` o `historical`).
- **Criterios de Aceptación Cumplidos:**
  1. Registros con verificación reciente aparecen como activos verificados.
  2. Registros en el límite exacto (7 días) mantienen estado activo verificado.
  3. Registros que superan 7 días salen de los resultados activos y pasan a revisión como `stale / unconfirmed`.
  4. Fechas ausentes, inválidas o futuras no son consideradas evidencia vigente y pasan a revisión.
  5. Convocatorias vencidas o cerradas son clasificadas como históricas sin reactivación por TTL.
  6. Métricas segregan estrictamente `#metric-total` (activas verificadas) de `#metric-secondary` (sin evidencia vigente / en revisión).
  7. El comparador y el modal de detalle no inducen a postular a registros pendientes de revalidación.
  8. **Simulación masiva a +30 días:** Todas las 107 oportunidades salen del listado activo por defecto (0 activas mostradas), pero se conservan íntegras (107) y accesibles en la vista de revisión (`#include-unconfirmed`), preservando trazabilidad sin apagón informativo.
- **Pruebas y Resultados Reales:**
  - `node tests/catalog_ui.test.cjs`: 100% aprobado (14 escenarios de estados, filtros, métricas, UI y simulación masiva a +30 días).
  - `python -m pytest -q`: 232 passed, 43 subtests passed en 8.06s.
  - `scripts/build_catalog.py --check` y `scripts/validate_catalog.py`: 112 fichas válidas en paridad exacta con la fuente canónica.
- **Siguiente Acción Técnica Recomendada:**
  - Realizar la revisión de integración de `TASK-R4-11-03` (commit atómico, push a rama remota y Pull Request hacia `main`).
  - No ejecutar `TASK-R4-11-01` (despliegue en GitHub Pages) hasta que esta corrección de aceptación esté integrada en `main`.

---

### FASE COBERTURA NACIONAL: Sector Público y Ecosistema Privado Peruano (R5)

#### `TASK-R5-01` — Conector de Convocatorias Estatales Gob.pe (`gobpe-convocatorias`)
- **Prioridad:** `P1` (Alto impacto nacional)
- **Tipo:** `[INTEGRACIÓN_OSS]` (Reutilización de parsers HTML y PDF nativos)
- **Estado:** `COMPLETED_WITH_LIMITATIONS` (Software, conector, pruebas y Schema 2 completados y validados localmente; criterio de >= 5 oportunidades vigentes no cumplido por inexistencia coyuntural de vacantes abiertas de TI en la fuente oficial; 21 convocatorias históricas conservadas en staging)
- **Dependencias:** `TASK-R4-11-01` (DONE).
- **Objetivo:** Adquirir convocatorias públicas vigentes de TI y Sistemas publicadas en la plataforma única del Estado (`gob.pe`).
- **Alcance y Ejecución:**
  - Implementado en `collector/pe_connectors.py` el conector `gobpe-convocatorias` para rastrear convocatorias públicas estructuradas en portales institucionales de `gob.pe` (portal oficial de INDECOPI enlazado a publicaciones en `www.gob.pe` y documentos en `cdn.www.gob.pe`).
  - Integrada extracción defensiva de bases en PDF mediante `extract_text_from_pdf_bytes`.
  - Registrada fuente oficial en `collector/sources.json` (`gobpe-indecopi-convocatorias`), junto con registros deshabilitados *fail-closed* para entidades con restricciones de acceso o formularios dinámicos (SUNAT y RENIEC).
  - Validada clasificación determinista incorporando patrones directos (`desarrollo`, `help desk`).
  - Ejecutada adquisición controlada: 668 oportunidades evaluadas, 21 oportunidades tecnológicas capturadas y validadas con Schema 2 en `data/candidates/inbox.local.json`.
  - Realizada auditoría crítica de vigencia: se constató que los 21 candidatos tecnológicos capturados corresponden a procesos concluidos (`CLOSED` / `EXPIRED`). En la fuente oficial existen 16 procesos abiertos vigentes, pero todos corresponden a áreas legales/económicas/administrativas (cero de TI en la fecha de corte).
- **Criterios de Aceptación y Estado Real:**
  1. Extracción exitosa de convocatorias oficiales con enlaces a bases en CDN de Gob.pe y publicaciones legales de `gob.pe`: `CUMPLIDO`.
  2. Incorporación de al menos 5 oportunidades estatales vigentes al staging: `NO CUMPLIDO (NOT_MET)` debido a la realidad coyuntural de la fuente oficial (0 vacantes de TI abiertas; 21 vacantes de TI históricas concluidas).
  3. Integridad canónica certificada: `data/opportunities.seed.json` y `data/opportunities.json` 100% intactos: `CUMPLIDO`.
  4. Suite de pruebas: 235 pruebas pasando exitosamente en 4.34s, incluyendo cobertura explícita de los 12 escenarios de borde y ciclo de vida: `CUMPLIDO`.
  5. Cero exposición de PII y esquema Candidate Schema 2 conforme: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `docs/audits/R5-01-GOBPE-CONNECTOR-VERIFICATION.md` (Verificación técnica de software).
  - `docs/audits/R5-01-ACCEPTANCE-AND-FRESHNESS-REVIEW.md` (Auditoría crítica de vigencia y procedencia).
  - `docs/audits/VELORA-OPEN-DECISIONS.md` (Decisión 6: Términos de acceso automatizado a Gob.pe).

#### `TASK-R5-02` — Protocolo Institucional y Consulta Controlada de Talento Perú (SERVIR)
- **Prioridad:** `P1` (Estratégico estatal)
- **Tipo:** `[INVESTIGACIÓN_TÉCNICA - READ_ONLY]`
- **Estado:** `BLOCKED` (Preservado formalmente; inviabilidad técnica de scraping desatendido por WAF Imperva y JSF stateful; sometido a decisión del propietario)
- **Dependencias:** Aprobación del propietario en `VELORA-OPEN-DECISIONS.md` (Decisión 3).
- **Objetivo:** Determinar la viabilidad técnica y de gobernanza para incorporar las convocatorias de empleo público de SERVIR.
- **Alcance y Hallazgos de la Investigación (26-11-2026):**
  - **Arquitectura de Servidor:** JavaServer Faces 2.0 (Mojarra) con PrimeFaces 5.3 sobre Apache y clúster Tomcat/JBoss (`.node31`).
  - **Seguridad Perimetral:** Protegido activamente por WAF Imperva Incapsula (`X-CDN: Imperva`, cookies `visid_incap_*`, `incap_ses_*`, script `_Incapsula_Resource`) y librerías de CAPTCHA (`RealPerson`).
  - **Endpoints y Datos Abiertos:** Inexistencia absoluta de API REST/JSON/XML documentada o no documentada. La Plataforma Nacional de Datos Abiertos (`datosabiertos.gob.pe`) no cuenta con feeds diarios de convocatorias (solo compendios estadísticos anuales estáticos). `robots.txt` responde HTTP 404.
  - **Inexistencia de Permalinks:** Las URLs de detalle (`detalle_ofertas_laborales.xhtml`) son estrictamente *stateful*; peticiones GET directas sin sesión previa devuelven plantillas vacías sin datos de la vacante.
  - **Muestra en Vivo:** 210 vacantes vigentes de Sistemas e Informática identificadas mediante simulación AJAX controlada.
  - **Trazabilidad a Fuente Primaria:** El campo `DETALLE` de la vacante contiene el enlace oficial al portal de la entidad convocante donde residen las bases completas en PDF (ej. `https://redsaludhuaylasnorte.gob.pe/`).
  - **Clasificación:** `Escenario E / Escenario D (Híbrido)`.
- **Criterios de Aceptación:**
  1. Registro auditable de investigación técnica y viabilidad de gobernanza completado: `CUMPLIDO`.
  2. Preservación estricta de estado `BLOCKED` y prioridad `P1` sin modificaciones en código de producción ni catálogo canónico: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `docs/audits/R5-02-SERVIR-OFFICIAL-ENDPOINT-INVESTIGATION.md`
  - `docs/audits/VELORA-OPEN-DECISIONS.md` (Decisión 3)
- **Riesgo:** Alto riesgo de bloqueo perimetral por Imperva e inestabilidad de `ViewState` ante cualquier intento de scraping recurrente desatendido.


#### `TASK-R5-03` — Ampliación de Empresas de Tecnología y Finanzas en Perú
- **Prioridad:** `P1` (Diversificación privada)
- **Tipo:** `[ADAPTACIÓN_OSS]`
- **Estado:** `COMPLETED` (Cumplimiento del 100% de criterios; 4 nuevas fuentes aprobadas y 20 vacantes de TI locales en staging)
- **Dependencias:** Ninguna.
- **Objetivo:** Incorporar 3 a 5 nuevas fuentes corporativas de tecnología con presencia física y contratación directa en el Perú.
- **Alcance y Ejecución:**
  - Auditados los canales ATS del mercado corporativo peruano: constatado que HiringRoom (`*.hiringroom.com`) es el estándar *de facto* para consultoras de TI y banca, mientras que Belcorp (Rankmi/Pandapé SPA) y BCP/Yape (Krowdy/Bumeran) operan bajo portales dinámicos sin feed público desatendido (registrados como `pending_review` bajo el principio de *fail-closed*).
  - Generalizado el adaptador `hiringroom-board` en `collector/pe_connectors.py` para soporte multitenant integral, soportando extracción dual (JSON-LD Schema.org y metadatos OpenGraph/DOM con desescapado HTML y limpieza de prefijos).
  - Registradas y configuradas en `collector/sources.json` 4 fuentes corporativas privadas aprobadas:
    1. `stefanini-hiringroom` (Stefanini IT Solutions Perú S.A.C.)
    2. `canvia-hiringroom` (Canvia)
    3. `myapps-hiringroom` (MyApps Soluciones S.A.C.)
    4. `efitec-hiringroom` (Efitec Corporation S.A.C.)
  - Ejecutada adquisición controlada en vivo: 27 vacantes evaluadas, 7 descartadas (administrativas/talent pools) y **20 nuevas vacantes técnicas locales incorporadas** a `data/candidates/inbox.local.json`.
  - Todas las 20 vacantes verificadas en territorio peruano (Lima, Miraflores, San Isidro, Surquillo), con relevancia directa en Ingeniería de Sistemas/TI y 100% de conformidad con Candidate Schema 2 (0 errores).
  - Creados fixtures reproducibles offline en `tests/fixtures/ats/` y pruebas unitarias/de integración pasando al 100% (236 pruebas).
  - Catálogo canónico (`data/opportunities.seed.json` y `data/opportunities.json`) 100% intacto con hashes certificados.
- **Criterios de Aceptación:**
  1. Incorporación de al menos 20 nuevas vacantes privadas locales en staging: `CUMPLIDO` (20 vacantes técnicas incorporadas).
  2. Validación de elegibilidad y contrato en territorio peruano: `CUMPLIDO` (100% en territorio peruano bajo normativa laboral local).
  3. Integridad canónica y cero PII garantizadas: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `docs/audits/R5-03-CORPORATE-SOURCES-EXPANSION.md`
  - `docs/audits/VELORA-OPEN-DECISIONS.md` (Decisión 8)

#### `TASK-R5-04-01` — Evaluación Técnica de Plataformas Secundarias como Radares de Descubrimiento (Practicas.pe y Convocatorias de Trabajo)
- **Prioridad:** `P1` (Propuesta de investigación de cobertura nacional)
- **Tipo:** `[INVESTIGACIÓN_TÉCNICA]`
- **Estado:** `EVALUATED_PROPOSED` (Investigación técnica, funcional y de gobernanza completada; dictaminada como viable exclusivamente bajo Modelo B de Descubrimiento Asistido; pendiente de decisión del propietario)
- **Dependencias:** `TASK-R5-01` (DONE).
- **Objetivo:** Determinar la viabilidad técnica, operativa y de gobernanza de utilizar Practicas.pe y Convocatorias de Trabajo (operadas por IDEADS) como sensores y radares secundarios para detectar convocatorias estatales y privadas dispersas.
- **Alcance y Hallazgos:**
  - Evaluadas ambas plataformas: pertenecen a la misma entidad matriz (IDEADS), no cuentan con APIs públicas y sus términos de uso eximen responsabilidad derivando expresamente a las fuentes primarias.
  - El 100% de la muestra de convocatorias estatales analizadas contiene enlaces salientes directos a bases oficiales (`smv.gob.pe`, `ugel02.gob.pe`, `sedapal`, `portal.mpfn.gob.pe`, `intranet2.fondepes.gob.pe`, `cdn.www.gob.pe`).
  - Evaluadas 3 alternativas de integración: A (Radar Automatizado), B (Descubrimiento Asistido) y C (Descarte).
  - Recomendado el **Modelo B (Descubrimiento Asistido)**: utilizar los portales secundarios para extraer enlaces salientes a la fuente primaria e identificador de proceso, prohibiendo la copia de resúmenes textuales de IDEADS y condicionando la publicación a la verificación obligatoria en la fuente oficial.
- **Criterios de Aceptación Cumplidos en la Investigación:**
  1. Inspección técnica, de sitemaps y de políticas de acceso completada.
  2. Muestra reproducible de 10 oportunidades analizada y clasificada.
  3. Matriz comparativa de 10 criterios de integración documentada.
  4. Decisión 7 registrada en `VELORA-OPEN-DECISIONS.md`.
- **Evidencias Documentales:**
  - `docs/audits/R5-04-01-SECONDARY-SOURCES-RESEARCH.md`
  - `docs/audits/R5-04-01-DISCOVERY-SAMPLE.md`
  - `docs/audits/R5-04-01-INTEGRATION-DECISION.md`

#### `TASK-R5-04-02` — Conector Piloto de Descubrimiento Asistido para Enlaces Oficiales Secundarios
- **Prioridad:** `P1` (Cobertura nacional asistida)
- **Tipo:** `[DESARROLLO_PROPIO - JUSTIFICADO]` + `[REUTILIZACIÓN_OSS_FIRST]`
- **Estado:** `PILOT_FIELD_VALIDATED_WITH_LIMITATIONS` (Validación operativa de campo completada con 10 oportunidades reales; revisión editorial de candidatos ejecutada; 5 decisiones formalizadas y aprobadas por el propietario el 27 de noviembre de 2026: conservar postulate.pe como radar auxiliar manual, retirar laboral.pe del uso operativo, no ampliar allowedHosts para minam.gob.pe, mantener DEVIDA y HNHU en staging en revisión, y no descartar convocatorias con plazo menor a 24 horas; catálogo canónico intacto con paridad SHA-256; 342 pruebas pasando al 100%)
- **Dependencias:** Decisiones 7 y 9 en `VELORA-OPEN-DECISIONS.md`.
- **Objetivo:** Implementar un piloto técnico-operativo de descubrimiento asistido para registrar convocatorias descubiertas en `postulate.pe` y `laboral.pe`, verificándolas obligatoriamente contra su fuente primaria oficial.
- **Alcance y Componentes Implementados:**
  - Módulo de radar y validación estricta en `collector/assisted_discovery.py`:
    - Registro exclusivo de metadatos permitidos (`processCode`, `entity`, `shortTitle`, `secondaryUrl`, `officialUrl`, `detectedAt`, `verifiedAt`, `verificationStatus`, `officialEvidence`).
    - Prohibición estricta de almacenar descripciones, requisitos o textos secundarios (`PROHIBITED_RADAR_FIELDS`).
    - Conversión a Candidate Schema 2 condicionada a `verificationStatus == 'verified_official'` y evidencia en la fuente primaria.
  - Registro de fuentes de radar en `collector/sources.json` (`postulate-pe-radar` y `laboral-pe-radar`) con `enabled: false`, `autopublish: false`, `connector: 'manual-review'` (*fail-closed*).
  - Integración en `scripts/editorial_cli.py`: comandos `radar-record`, `radar-verify` y `radar-promote` (con soporte para `--dry-run` y `--json-report`), reforzado con validación de `allowedHosts` del registro de fuentes.
  - Validación operativa de campo con 10 oportunidades reales (5 de cada portal):
    - 2 promovidas a staging (`data/candidates/inbox.local.json`) con estado `pending_review` (DEVIDA e Hipólito Unanue).
    - 1 retenida por requerir alta de host oficial ministerial (`minam.gob.pe`).
    - 1 descartada por perfil no perteneciente a TI (`OSIPTEL` - Ciencias de la Comunicación).
    - 1 descartada por URL oficial genérica sin proceso específico (`MINCETUR`).
    - 5 descartadas por URL primaria rota HTTP 404 en Talento Perú / SERVIR (`laboral.pe`).
  - Formalización de Decisiones del Propietario (27 de noviembre de 2026):
    1. Criterio temporal: no descartar por plazo < 24 horas; mostrar fechas y horas oficiales sin inventar horarios.
    2. `postulate.pe`: conservado como radar auxiliar manual (no automatizado).
    3. `laboral.pe`: retirado del uso operativo por ineficiencia de enlaces (100% 404 a SERVIR), conservando su historial técnico.
    4. `minam.gob.pe`: no autorizado para inclusión en `allowedHosts`; se preserva la política *fail-closed*.
    5. Candidatos DEVIDA y HNHU: conservados en staging local bajo recomendación `RECOMMEND_KEEP_IN_REVIEW`, sin publicar en el catálogo activo ni canónico.
  - Suite de 14 pruebas específicas en `tests/test_assisted_discovery.py` y 342 pruebas globales pasando al 100%.
- **Criterios de Aceptación Cumplidos:**
  1. Registro de metadatos permitidos para `postulate.pe` y `laboral.pe`: `CUMPLIDO`.
  2. Rechazo de URLs no HTTPS o hosts no autorizados: `CUMPLIDO`.
  3. Rechazo estricto de campos de contenido no permitidos (descripciones extensas): `CUMPLIDO`.
  4. Separación entre fuente secundaria y fuente oficial: `CUMPLIDO`.
  5. Imposibilidad de certificar verificación sin evidencia oficial primaria: `CUMPLIDO`.
  6. Manejo de estados de descarte sin promover a staging: `CUMPLIDO`.
  7. Deduplicación mediante mecanismos existentes: `CUMPLIDO`.
  8. Ausencia de autopublicación o incorporación directa al catálogo público: `CUMPLIDO`.
  9. Preservación estricta de la integridad canónica (hashes certificados intactos): `CUMPLIDO`.
  10. Trazabilidad de detección y verificación: `CUMPLIDO`.
  11. Compatibilidad total con la suite de pruebas (342 pruebas pasando): `CUMPLIDO`.
  12. Formalización documental de gobernanza completada: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `docs/audits/TASK-R5-04-02-FIELD-VALIDATION.md`
  - `docs/audits/TASK-R5-04-02-EDITORIAL-REVIEW.md`
  - `docs/audits/R5-04-03-ASSISTED-DISCOVERY-PILOT.md`
  - `docs/audits/VELORA-OPEN-DECISIONS.md` (Decisiones 7 y 9)

##### Investigación Complementaria R5.4 — Evaluación de 8 Portales Secundarios y Taxonomía de Búsqueda
- **Prioridad:** `P2` (Evolución de cobertura nacional)
- **Tipo:** `[INVESTIGACIÓN_TÉCNICA]`
- **Estado:** `EVALUATED_PROPOSED` (Investigación técnica complementaria completada; evaluación individual de 8 portales peruanos, ratificación de Modelo B y propuesta de taxonomía desacoplada en 7 dimensiones; pendiente de decisión del propietario)
- **Alcance y Hallazgos:**
  - Inspeccionados 8 portales secundarios: `convocatoriasdetrabajo.pe`, `postulate.pe`, `peruconvoca.com`, `convocatoriasperu.net.pe`, `convocape.online`, `laboral.pe`, `portaltrabajos.pe`, `convocatoriascas.com`.
  - Diferenciación de operadores confirmada: `convocatoriasdetrabajo.pe` (LiteSpeed) es independiente de IDEADS (`convocatoriasdetrabajo.com`).
  - Hallazgo estructural: las plataformas públicas más estructuradas (`postulate.pe`, `laboral.pe`, `peruconvoca.com`) operan como agregadores secundarios del portal oficial **SERVIR – Talento Perú** (`app.servir.gob.pe`).
  - Identificado operador comercial formal de `postulate.pe`: INDEXCOM PERU E.I.R.L. (RUC 20601906792).
  - Ratificado el **Modelo B — Descubrimiento Asistido** sin excepciones; prohibida la copia de textos descriptivos protegidos.
  - Diseñada taxonomía desacoplada en 7 dimensiones (carrera solicitada, familia profesional, especialidad/área funcional, cargo, tecnologías, nivel académico, experiencia) extensible a otras profesiones.
  - Portales clasificados para eventual piloto asistido: `postulate.pe` y `laboral.pe` (`VIABLE_WITH_LIMITATIONS`).
- **Evidencias Documentales:**
  - `docs/audits/R5-04-02-SECONDARY-SOURCES-RESEARCH.md`

#### `TASK-R5-05` — Normalización Geográfica y Segmentación del Ámbito Territorial de las Oportunidades
- **Prioridad:** `P1` (Experiencia de descubrimiento y precisión territorial)
- **Tipo:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]` + `[MEJORA_UX]`
- **Estado:** `COMPLETED_VERIFIED` (Taxonomía tridimensional implementada en backend `collector/geography.py` y frontend `app.js`; selectores dinámicos integrados en `index.html`; 14 pruebas unitarias Python y suite UI en Node.js pasando; 329 pruebas globales del repositorio pasando)
- **Dependencias:** Ninguna (opera sobre el catálogo canónico Schema 2).
- **Objetivo:** Resolver la confusión entre convocatorias con presencia física local en Perú y vacantes remotas internacionales, proveyendo selectores visuales por ámbito territorial y por departamento peruano sin dependencias externas.
- **Alcance y Componentes Implementados:**
  - **Módulo Backend (`collector/geography.py`):**
    - Clasificación en 3 dimensiones independientes: Ámbito territorial (`PERU_LOCAL`, `PERU_REMOTE`, `INTERNATIONAL_REMOTE_PERU_ELIGIBLE`, `INTERNATIONAL_REMOTE_UNCONFIRMED`, `NOT_ELIGIBLE_PERU`, `UNSPECIFIED`), Modalidad físico-espacial (`ONSITE`, `HYBRID`, `REMOTE`, `UNSPECIFIED`) y Ubicación en Perú (25 departamentos/jurisdicciones).
    - Principio estricto *fail-closed* y *zero hallucination* sin servicios externos de geocodificación.
  - **Interfaz de Usuario (`index.html`):**
    - Incorporación de selectores `<select id="scope-filter">` y `<select id="department-filter">` en la barra de filtros secundarios.
    - Preservación y reorientación del campo `<input id="location">` para búsquedas por texto libre complementarias.
  - **Motor Frontend (`app.js`):**
    - Población dinámica de `#department-filter` con los departamentos efectivamente presentes en el catálogo cargado (eliminando opciones vacías).
    - Filtrado reactivo en `getVisibleJobs()`, soporte en `isFiltered` y limpieza integral en el evento `reset`.
    - Renderizado de etiquetas de ámbito territorial (`geographicScopeTag`) en tarjetas y ficha de detalle.
  - **Pruebas y Verificación:**
    - 14 pruebas unitarias en `tests/test_geography.py`.
    - Pruebas de integración UI en `tests/catalog_ui.test.cjs`.
- **Evidencias Documentales:**
  - `docs/audits/TASK-R5-05-GEOGRAPHIC-NORMALIZATION-AND-FILTERS.md`

#### `TASK-FIX-E2E-R5-05` — Corrección de Pruebas E2E tras la Integración de Normalización Geográfica
- **Prioridad:** `P0` (Bloqueante de CI y paridad Pages)
- **Tipo:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]`
- **Estado:** `COMPLETED_LOCALLY` (Aserciones actualizadas para las 7 tarjetas de resumen, icono SVG y aserción explícita de Ámbito territorial en `tests/e2e/catalog.spec.cjs`; suite E2E de Playwright pasando al 100% en Chromium, Mobile y Narrow; pendiente de commit y push)
- **Dependencias:** `TASK-R5-05` (Satisfecha en código y desplegada en Vercel).
- **Objetivo:** Resolver el fallo de aserción en el pipeline de GitHub Actions (`refresh-catalog.yml`, Run ID `46055123843`) provocado por la expectativa fija heredada de R7 de 6 tarjetas de resumen frente a las 7 tarjetas reales generadas tras la incorporación de la tarjeta de ámbito territorial por R5-05.
- **Alcance y Ejecución:**
  - Actualizadas las expectativas en `tests/e2e/catalog.spec.cjs:227` para reflejar las 7 tarjetas reales de `OP-005` y los 7 iconos SVG correspondientes.
  - Incorporada aserción funcional semántica explícita para la tarjeta de Ámbito territorial (`scopeCard`), verificando label, icono y valor (`Empleo en Perú (Presencial/Híbrido)`).
  - Verificada la integridad de las 6 tarjetas restantes y ausencia de tarjetas vacías o duplicadas.
  - Actualizados los conteos coherentes para `OP-002` (8 tarjetas, `Ámbito no especificado`) y `OP-001` (10 tarjetas, `Empleo en Perú (Presencial/Híbrido)`).
  - Ejecutada validación exhaustiva en Playwright (Chromium, Mobile, Narrow) y regresión completa.
- **Criterios de Aceptación:**
  1. Conteo de tarjetas coherente con las 7 tarjetas del diseño actual: `CUMPLIDO`.
  2. Aserción funcional explícita del Ámbito territorial: `CUMPLIDO`.
  3. Los tres proyectos de Playwright pasando: `CUMPLIDO`.
  4. Suite de regresión pasando al 100%: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `docs/audits/TASK-FIX-E2E-R5-05.md`

---

### FASE AUTOMATIZACIÓN OPERATIVA: Publicación Objetiva y Operación Continua (R6)

Estructura evolutiva de la Fase R6:
- **R6.1 / R6.2:** Política y motor determinista de autopublicación basada en reglas (`TASK-R6-01`) — `COMPLETED`.
- **R6.3:** Revalidación programada de oportunidades y automatización del ciclo de vida (`TASK-R6-02`) — `COMPLETED`.
- **R6.4:** Detección de cambios de requisitos y enlaces rotos — `PENDING (PROPUESTA FUTURA)`.
- **R6.5:** Alertas de fallos de fuentes y reportes de calidad ampliados — `PENDING (PROPUESTA FUTURA)`.

#### `TASK-R6-01` (R6.1 / R6.2) — Política y Motor de Auto-Publicación Basada en Reglas Objetivas
- **Prioridad:** `P1` (Escalabilidad de producto)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `COMPLETED` (Motor determinista fail-closed implementado en `collector/autopublish.py`, integrado en `scripts/editorial_cli.py autopublish` y certificado con 18 escenarios de prueba)
- **Dependencias:** Aprobación de política en `VELORA-OPEN-DECISIONS.md` (Decisión 2, Opción A aprobada).
- **Objetivo:** Eliminar el cuello de botella de aprobación manual individual para fuentes pre-autorizadas y confiables mediante evaluación determinista de 6 reglas obligatorias concurrentes.
- **Alcance y Ejecución:**
  - Implementado el motor determinista de autopublicación en `collector/autopublish.py` bajo el principio estricto de *fail-closed* y cero dependencias externas.
  - Implementadas y desacopladas las 6 reglas obligatorias:
    1. **Regla 1 (Fuente autorizada):** `decision == "approved"` y `automatedAccessStatus == "approved"` en `sources.json`.
    2. **Regla 2 (URL de postulación segura):** Protocolo HTTPS estricto y validación de host contra lista blanca autorizada (`allowedPostingHosts` y `allowedHosts`), rechazando ataques de subcadena (ej. `evil-encora.com`).
    3. **Regla 3 (Taxonomía técnica directa):** Relevancia estricta `DIRECT` en la taxonomía de Sistemas/Computación/Tecnología; roles adyacentes u operacionales son retenidos.
    4. **Regla 4 (Elegibilidad explícita para Perú):** Condición independiente y obligatoria que exige prueba de `PERU_LOCAL` o `PERU_REMOTE`; términos genéricos (`LATAM`, `GLOBAL_REMOTE` o remoto no calificado) son retenidos.
    5. **Regla 5 (Deduplicación sin colisiones):** Cero colisiones exactas (clave primaria, URL idéntica) ni de identificador o firma secundaria (`employer|title`) contra el catálogo canónico ni contra el lote en proceso.
    6. **Regla 6 (Vigencia y trazabilidad verificables):** Fecha límite futura (`deadline >= as_of`) O confirmación activa en ATS dentro de la ventana de frescura TTL (`<= 7` días), con trazabilidad completa de evidencias y rechazo si hay indicios de proceso cerrado.
  - Integrado el subcomando `autopublish` en `scripts/editorial_cli.py` con soporte para `--dry-run` (activo por defecto), `--apply`, `--as-of`, `--max-promote`, `--output` y `--json-report`.
  - Desarrollada la suite de pruebas `tests/test_autopublish.py` cubriendo exhaustivamente los 18 escenarios de aceptación requeridos.
  - Ejecutada la suite completa del proyecto: **254 pruebas pasando al 100% en 4.5s**, sin regresiones.
  - Ejecutada evaluación en seco (*dry-run*) sobre la bandeja real (`data/candidates/inbox.local.json`): 295 candidatos evaluados, 90 aprobados como aptos para publicación y 108 retenidos en revisión.
  - Salvaguarda canónica verificada: `data/opportunities.seed.json` y `data/opportunities.json` se mantuvieron 100% intactos con sus hashes SHA-256 inalterados.
- **Criterios de Aceptación:**
  1. Motor determinista fail-closed con 6 reglas objetivas: `CUMPLIDO`.
  2. Cobertura completa de los 18 escenarios de aceptación: `CUMPLIDO`.
  3. Integración en CLI editorial y modo dry-run seguro: `CUMPLIDO`.
  4. Protección canónica de archivos seed y snapshot: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `collector/autopublish.py`
  - `scripts/editorial_cli.py` (subcomando `autopublish`)
  - `tests/test_autopublish.py` (18 escenarios pasando)
  - `docs/audits/R6-01-AUTOPUBLICATION-ENGINE.md`
  - `docs/audits/VELORA-OPEN-DECISIONS.md` (Decisión 2)

#### `TASK-R6-02` (R6.3) — Revalidación Programada de Oportunidades en GitHub Actions
- **Prioridad:** `P2` (Frescura desatendida y ciclo de vida)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Correspondencia evolutiva:** `R6.3 — Revalidación programada de oportunidades`
- **Estado:** `COMPLETED` (Motor de revalidación determinista con Regla de Dos Ausencias Consecutivas implementado en `collector/revalidation.py`, integrado en `scripts/editorial_cli.py`, workflow de GitHub Actions actualizado en `.github/workflows/revalidation-audit.yml` y certificado con 23 escenarios de prueba)
- **Dependencias:** `TASK-R6-01` (COMPLETED).
- **Objetivo:** Automatizar la comprobación periódica de vigencia y ciclo de vida de oportunidades en el catálogo canónico y bandeja de staging, garantizando la transición segura a estado histórico sin intervención manual mediante la Regla de Dos Verificaciones Consecutivas.
- **Alcance y Ejecución:**
  - Implementada en `collector/revalidation.py` la **Regla de Dos Verificaciones Consecutivas** (*Two-Absence Rule*):
    - **Caso A (Confirmada abierta):** ATS confirma vacante activa -> `lastVerifiedAt` actualizado, contador de ausencias reiniciado a 0, permanece `active`/`open`.
    - **Caso B (Primera ausencia):** Vacante ausente una vez -> clasificada como `DISAPPEARED_ONCE`, contador = 1; **salvaguarda anti-cierre activa**: la oportunidad permanece `active`/`open` en catálogo.
    - **Caso C (Segunda ausencia consecutiva):** Vacante ausente en 2 verificaciones consecutivas exitosas -> `NOT_FOUND_CONFIRMED`, contador = 2; pasa automáticamente a `opportunityStatus: "closed"`, `publicationStatus: "historical"`, `verificationStatus: "stale"`.
    - **Caso D (Fallo temporal de red):** Error HTTP 403, 429, 500, timeout o fallo de red -> clasificado como `TEMPORARY_ERROR`; **el contador de ausencias NO se incrementa** y la oportunidad se preserva intacta.
    - **Caso E (Cierre explícito en ATS):** Fuente reporta estado cerrado/concluido/cancelado -> `CLOSED_CONFIRMED`; pasa directamente a estado histórico con evidencia sin requerir dos ausencias.
  - Implementada protección de concurrencia mediante `RevalidationLock` (`data/.revalidation.lock`) para prevenir colisiones o sobreescrituras concurrentes durante ejecuciones programadas.
  - Diseñada la separación de almacenamiento de estado persistente en `data/revalidation-state.json`, garantizando que el conteo de ausencias sobreviva entre corridas semanales independientes sin alterar la estructura del catálogo cliente.
  - Actualizado el CLI editorial (`scripts/editorial_cli.py revalidate --catalog`) con argumentos `--catalog`, `--apply`, `--state-file`, `--threshold`, `--as-of` y reportes JSON/estructurados.
  - Actualizado el workflow programado en `.github/workflows/revalidation-audit.yml` con ejecución semanal desatendida (`cron: "0 9 * * 0"`, domingos 04:00 AM Lima), `workflow_dispatch`, `concurrency`, permisos mínimos de solo lectura (`contents: read`) y salvaguardas de inmutabilidad en modo dry-run.
  - Desarrollada la suite de pruebas unitarias y de integración `tests/test_revalidation_r6_02.py` cubriendo exhaustivamente los 22 escenarios de aceptación obligatorios más la prueba de regresión de frescura TTL de R4-11-03 (23 pruebas).
  - Ejecutada la suite completa del proyecto: **277 pruebas pasando al 100%**, sin regresiones.
  - Verificada la inmutabilidad de los catálogos en modo dry-run: `data/opportunities.seed.json` y `data/opportunities.json` preservados con paridad de hash SHA-256 intacta.
- **Criterios de Aceptación:**
  1. Convocatorias cerradas o desaparecidas pasan automáticamente a estado histórico bajo la regla de dos ausencias: `CUMPLIDO`.
  2. Salvaguarda anti-cierre ante fallos transitorios de red o primera ausencia: `CUMPLIDO`.
  3. Workflow programado y concurrencia segura en GitHub Actions: `CUMPLIDO`.
  4. Persistencia de estado entre ejecuciones sin mutar Schema 2 del cliente: `CUMPLIDO`.
  5. 23 pruebas de aceptación y 277 pruebas globales pasando: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `collector/revalidation.py`
  - `scripts/editorial_cli.py`
  - `.github/workflows/revalidation-audit.yml`
  - `tests/test_revalidation_r6_02.py`
  - `docs/audits/R6-02-REVALIDATION-ENGINE.md`

---

### FASE VALOR PROFESIONAL Y UX: Modalidades, Habilidades y Trayectorias (R7)

#### `TASK-R7-01` — Taxonomía de Regímenes Laborales Peruanos (CAS, 728, Formativo)
- **Prioridad:** `P2` (Valor funcional Perú)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `COMPLETED`
- **Dependencias:** `TASK-R5-01`, `TASK-R6-01`, `TASK-R6-02`.
- **Objetivo:** Permitir al usuario filtrar y entender la modalidad de contratación en el sector público y privado con rigor normativo y certeza documental.
- **Alcance Implementado:**
  - Módulo normalizador `collector/labor_regime.py` con las 7 categorías canónicas: `PRE_PROFESSIONAL_INTERNSHIP`, `PROFESSIONAL_INTERNSHIP`, `CAS`, `LABOR_REGIME_728`, `CIVIL_SERVICES`, `OTHER`, `UNSPECIFIED`.
  - Clasificador determinista y fail-closed que analiza `contractType`, `opportunityType`, `requisition`, títulos, tareas, requisitos y beneficios.
  - Marco normativo peruano citado explícitamente: Ley 28518, D. Leg. 1057 / Ley 29849 / Ley 31131 (CAS), TUO D. Leg. 728 (D.S. 003-97-TR), Código Civil art. 1764 (locación), y Ley 31396.
  - Integración en `collector/classification.py`, `collector/autopublish.py` y validación en `scripts/catalog_quality.py`.
  - Frontend con selector `<select id="regime-filter">` en `index.html`, badges visuales temáticos en tarjetas (`app.js`), tarjeta de resumen y sección detallada de marco normativo con jornada, derechos y cautelas en el modal y vista de oportunidad.
  - Suite de pruebas unitarias exhaustiva en `tests/test_labor_regime.py` (23 pruebas) y validación en `tests/catalog_ui.test.cjs`.
  - Total global del proyecto: 300 pruebas unitarias y de integración pasando al 100%.
  - Integridad canónica preservada al 100% (paridad SHA-256 intacta en `data/opportunities.seed.json` y `data/opportunities.json`).
- **Criterios de Aceptación:**
  1. Filtro visible en UI que discrimina efectivamente puestos formativos de CAS y régimen privado: `CUMPLIDO`.
  2. Taxonomía de 7 modalidades con citas legales peruanas exactas: `CUMPLIDO`.
  3. Clasificación fail-closed sin presunciones ciegas: `CUMPLIDO`.
  4. Retrocompatibilidad total con Schema 2 del catálogo: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `collector/labor_regime.py`
  - `tests/test_labor_regime.py`
  - `docs/audits/R7-01-LABOR-REGIME-TAXONOMY.md`

#### `TASK-R7-02` — Comparador de Trayectorias y Requisitos Técnicos
- **Prioridad:** `P3` (Evolución de producto)
- **Tipo:** `[REUTILIZACIÓN_INTERNA]` + `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `COMPLETED`
- **Dependencias:** `TASK-R7-01` (Satisfecha).
- **Objetivo:** Brindar a los estudiantes y egresados de Ingeniería de Sistemas y TI herramientas de análisis de brechas de habilidades y requisitos técnicos frente a las demandas de mercado registradas en el catálogo.
- **Alcance Implementado:**
  - Taxonomía canónica de competencias técnicas normalizadas y alias (lenguajes, frameworks, bases de datos, cloud, DevOps, redes y seguridad) en `collector/skills.py` y `app.js`.
  - Extractor determinista y clasificador de prioridad (`REQUIRED`, `PREFERRED`, `MENTIONED`, `UNSPECIFIED`) con protección estricta contra falsos positivos (C vs palabras comunes, SQL vs SQL Server/SQLite, C++, redes telecomunicaciones vs redes sociales).
  - Jerarquía contextual donde los requisitos textuales explícitos prevalecen sobre etiquetas genéricas de habilidades.
  - Reutilización y extensión del comparador nativo `#compare-dialog` en `app.js`: matriz visual de 3 columnas (Coincidentes, Exclusivas A, Exclusivas B), badges temáticos con tooltips de trazabilidad textual y advertencias explícitas de requerimientos no declarados (fail-closed).
  - Inclusión del régimen contractual laboral (`TASK-R7-01`) en la tabla atributiva del comparador.
  - Suite de pruebas unitarias en `tests/test_skills.py` (13 pruebas) y pruebas de UI en `tests/catalog_ui.test.cjs`.
  - Suite global: 313 pruebas pasando al 100% sin regresiones. Catálogos canónicos 100% íntegros e inalterados.
- **Criterios de Aceptación:**
  1. Vista comparativa resalta competencias coincidentes y diferenciadoras: `CUMPLIDO`.
  2. Clasificación determinista de obligatoriedad sin modelos de caja negra ni sesgos: `CUMPLIDO`.
  3. Manejo transparente de vacíos de información sin hacer suposiciones: `CUMPLIDO`.
  4. Preservación estricta de retrocompatibilidad y paridad de datos: `CUMPLIDO`.
- **Evidencias Documentales:**
  - `collector/skills.py`
  - `tests/test_skills.py`
  - `docs/audits/R7-02-OPPORTUNITY-COMPARATOR.md`

#### `TASK-R7-RELEASE-AUDIT` — Auditoría de Consolidación y Verificación Integral Pre-Release de Fase R7
- **Prioridad:** `P2` (Consolidación operativa)
- **Tipo:** `[AUDITORÍA_TÉCNICA]`
- **Estado:** `COMPLETED`
- **Dictamen de Preparación:** `READY_WITH_LIMITATIONS`
- **Dependencias:** `TASK-R7-01`, `TASK-R7-02` (Satisfechas).
- **Objetivo:** Ejecutar la revisión final cruzada de frontend, tests globales, accesibilidad WCAG 2.1 AA del comparador y del filtro de regímenes, y certificar la preparación para merge/despliegue de las innovaciones de R7 en producción.
- **Alcance Auditado y Verificado:**
  - Verificación de integración frontend (`index.html`, `app.js`) y módulos Python (`collector/labor_regime.py`, `collector/skills.py`).
  - Pruebas reales en navegador Chromium automatizadas con Playwright evaluando interacción de filtros de régimen, modal de detalle, y matriz de competencias en `#compare-dialog`.
  - Auditoría de accesibilidad WCAG 2.1 AA con `@axe-core/playwright` en viewports Desktop (1280x800), Mobile (375x667) y Narrow (320x568): cero violaciones críticas o serias detectadas.
  - Suite global de regresión: 313 pruebas de Python aprobadas al 100% y `catalog_ui.test.cjs` aprobado con exit code 0.
  - Integridad canónica de datos: paridad SHA-256 intacta en `data/opportunities.seed.json` y `data/opportunities.json`.
  - Evidencias: DEF-R7-01 corregido en `tests/e2e/accessibility.spec.cjs` y `tests/e2e/catalog.spec.cjs`.
- **Evidencias Documentales:**
  - `docs/audits/R7-RELEASE-CONSOLIDATION-AUDIT.md`

#### `TASK-R7-RELEASE-EXECUTION` — Consolidación, Etiquetado y Despliegue de Release de Fase R7
- **Prioridad:** `P1` (Despliegue de producción autorizado)
- **Tipo:** `[CONSOLIDACIÓN_Y_RELEASE]`
- **Estado:** `COMPLETED`
- **Dictamen de Despliegue:** `DEPLOYED_AND_VERIFIED`
- **Dependencias:** `TASK-R7-RELEASE-AUDIT` (Satisfecha).
- **Objetivo:** Ejecutar la consolidación definitiva sobre `main`, crear el tag de release `v0.7.0`, realizar push a `origin/main` y verificar en vivo los despliegues automatizados de GitHub Pages y Vercel.
- **Alcance Ejecutado y Certificado:**
  - Creación del commit consolidado `4006413` sobre `main` y tag anotado `v0.7.0`.
  - Push exitoso a `origin/main` y tag remoto `v0.7.0`.
  - Pipeline GitHub Actions `Validate and publish Ruta Sistemas` (Run ID: `45876535680`): jobs `validate` y `publish` aprobados con éxito (`success`).
  - Verificación en vivo sobre GitHub Pages (`https://blueisazul.github.io/WebRutaSistemas/`) y Vercel (`https://velora-six-fawn.vercel.app/`): 0 errores de consola, 0 fallos de red.
  - Paridad criptográfica absoluta (100% bit a bit) del catálogo servido (`417B38...`, 537,807 bytes).
  - Verificación interactiva de funcionalidades R7 en vivo: selector `#regime-filter`, modal normativo, comparador con matriz de 3 columnas de habilidades y soporte fail-closed de oportunidades desactualizadas (`#include-unconfirmed`).
- **Evidencias Documentales:**
  - `docs/audits/TASK-R7-RELEASE-EXECUTION.md`
  - `docs/audits/R7-RELEASE-CONSOLIDATION-AUDIT.md`

---

## 5. Siguiente Acción Única Recomendada

**Cierre de Fase R7 y Planificación Operativa:**
Con la publicación exitosa del release `v0.7.0` en GitHub Pages y Vercel, la **Fase R7 — Valor Profesional y UX** queda formalmente concluida y en producción.

**Consolidación de Calidad de Catálogo y Cobertura Geográfica (TASK-FIX-URL-01 + TASK-R5-05):**
- **Identificadores Consolidados:** TASK-FIX-URL-01 (Corrección de URLs de publicación ATS) y TASK-R5-05 (Normalización geográfica y filtros territoriales).
- **Tipo:** [CONSOLIDACIÓN_TÉCNICA] + [REUTILIZACIÓN_INTERNA] + [REFACTOR/FIX]
- **Estado:** PUSHED_TO_MAIN_DEPLOYMENT_PARTIAL (Commit f861e06 publicado en origin/main; Vercel desplegado y 100% operativo en producción con URLs corregidas y filtros geográficos; GitHub Pages desfasado debido a fallo de aserción en job validate de refresh-catalog.yml resuelto localmente en TASK-FIX-E2E-R5-05).
- **Evidencias Documentales:**
  - docs/audits/TASK-FIX-E2E-R5-05.md
  - docs/audits/VELORA-PRE-RELEASE-URL-GEOGRAPHY-CONSOLIDATION.md
  - docs/audits/TASK-FIX-URL-01-ATS-PUBLICATION-URL-REMEDIATION.md
  - docs/audits/TASK-R5-05-GEOGRAPHIC-NORMALIZATION-AND-FILTERS.md

- **Definición de Prioridades para Próximas Fases:**
  - Decisión 8: Evaluación y eventual aprobación de adopción del ecosistema HiringRoom para cobertura privada en Perú.
  - Decisión 6: Definición de frecuencia y modo de ingestión automatizada de convocatorias CAS de Gob.pe.
  - Activación de ciclos programados de revalidación periódica de catálogo en background (Fase R6).
