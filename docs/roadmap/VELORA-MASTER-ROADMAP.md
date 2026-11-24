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
- **Estado:** `PENDING`
- **Dependencias:** Aprobación del propietario en `VELORA-OPEN-DECISIONS.md`.
- **Objetivo:** Unificar la marca del producto bajo el nombre oficial **Velora** en toda la interfaz y metadatos.
- **Alcance:**
  - Actualizar `<title>Velora — Oportunidades y Trayectorias en Tecnología</title>` en `index.html`.
  - Actualizar logotipo y texto de cabecera en `index.html`: sustituir "Ruta Sistemas" por "Velora".
  - Actualizar textos del hero y metadatos OpenGraph.
  - Actualizar `package.json` (`name: "velora"`).
  - Actualizar `README.md` público reflejando la identidad de Velora, la escala real de 112 oportunidades y la arquitectura actual.
- **Criterios de Aceptación:**
  1. La interfaz web muestra consistentemente "Velora".
  2. Todas las pruebas unitarias y E2E de Playwright actualizadas aprueban sin fallas de selectores.
- **Riesgo:** Ruptura de tests de integración que buscan el string literal "Ruta Sistemas" (requiere actualizar aserciones).

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
- **Estado:** `PENDING`
- **Dependencias:** `TASK-R4-11-01`.
- **Objetivo:** Adquirir convocatorias públicas vigentes de TI y Sistemas publicadas en la plataforma única del Estado (`gob.pe`).
- **Alcance:**
  - Implementar en `collector/pe_connectors.py` el conector `gobpe-convocatorias` para rastrear secciones de "Informes y Publicaciones" (tipo: Convocatorias de Trabajo) de entidades priorizadas (INDECOPI, SUNAT, RENIEC, Ministerios).
  - Integrar la descarga controlada de PDFs de bases oficiales y extracción de requisitos, perfil y cronograma mediante `extract_text_from_pdf_bytes`.
  - Registrar la fuente en `collector/sources.json` bajo directiva *fail-closed*.
- **Criterios de Aceptación:**
  1. Extracción exitosa de convocatorias con enlaces oficiales a bases en CDN de Gob.pe.
  2. Incorporación de al menos 5 oportunidades estatales vigentes al staging de candidatos.
- **Riesgo:** Estructura HTML dispar entre distintas entidades en Gob.pe (mitigado con parsing defensivo).

#### `TASK-R5-02` — Protocolo Institucional y Consulta Controlada de Talento Perú (SERVIR)
- **Prioridad:** `P1` (Estratégico estatal)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `BLOCKED` (Pendiente de decisión editorial y autorización)
- **Dependencias:** Aprobación del propietario en `VELORA-OPEN-DECISIONS.md`.
- **Objetivo:** Establecer un canal regular y autorizado para incorporar el volumen masivo de convocatorias de SERVIR.
- **Alcance:**
  - Vía A (Institucional): Tramitar comunicación formal de datos abiertos a SERVIR (`talentoperu@servir.gob.pe`).
  - Vía B (Técnica asistida): Implementar un extractor local que consulte el formulario JSF `ofertas_laborales.xhtml` respetando estrictamente `minDelayMs: 10000`, extrayendo únicamente metadatos de puestos de Sistemas para contrastar contra fuentes oficiales.
- **Criterios de Aceptación:**
  1. Registro auditable de autorización o mecanismo de consulta de bajo impacto sin violar términos del servicio.
- **Riesgo:** Bloqueo de IP o rechazo institucional.

#### `TASK-R5-03` — Ampliación de Empresas de Tecnología y Finanzas en Perú
- **Prioridad:** `P1` (Diversificación privada)
- **Tipo:** `[ADAPTACIÓN_OSS]`
- **Estado:** `PENDING`
- **Dependencias:** Ninguna.
- **Objetivo:** Incorporar 3 a 5 nuevas fuentes corporativas de tecnología con presencia física y contratación directa en el Perú.
- **Alcance:**
  - Auditar e integrar bolsas públicas en Greenhouse/Lever de: Belcorp, BCP / Yape (mediante su ATS correspondiente), Stefanini Perú y consultoras de software locales.
  - Configurar filtros geográficos estrictos (`locationFilter: ["peru", "lima"]`).
- **Criterios de Aceptación:**
  1. Incorporación de al menos 20 nuevas vacantes privadas locales en staging.
  2. Validación de elegibilidad y contrato en territorio peruano.

---

### FASE AUTOMATIZACIÓN OPERATIVA: Publicación Objetiva y Operación Continua (R6)

#### `TASK-R6-01` — Política y Motor de Auto-Publicación Basada en Reglas Objetivas
- **Prioridad:** `P1` (Escalabilidad de producto)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `PENDING`
- **Dependencias:** Aprobación de política en `VELORA-OPEN-DECISIONS.md`.
- **Objetivo:** Eliminar el cuello de botella de aprobación manual individual para fuentes pre-autorizadas y confiables.
- **Alcance:**
  - Implementar en `collector/` el módulo de promoción automática: un candidato en staging se promueve automáticamente al catálogo canónico si cumple al 100% las siguientes condiciones:
    1. Proviene de una fuente con `decision: "approved"` y `automatedAccessStatus: "approved"`.
    2. Enlace de postulación HTTPS válido en host de lista blanca.
    3. Clasificación técnica inequívoca en taxonomía de Sistemas/Tecnología.
    4. Cero colisiones en deduplicación determinista.
    5. Fecha límite futura o vacante abierta confirmada en ATS.
    6. Trazabilidad completa de evidencias requeridas.
  - Los casos dudosos o con alertas de taxonomía se retienen en `pending_review` para inspección humana.
- **Criterios de Aceptación:**
  1. Ejecución de prueba con fixtures: candidatos válidos se publican automáticamente; candidatos ambiguos quedan retenidos.
- **Riesgo:** Inclusión involuntaria de un rol no afín si la taxonomía falla (mitigado con lista de exclusión de palabras clave).

#### `TASK-R6-02` — Revalidación Programada en GitHub Actions
- **Prioridad:** `P2` (Frescura desatendida)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `PENDING`
- **Dependencias:** `TASK-R6-01`.
- **Objetivo:** Automatizar la comprobación semanal de vacantes cerradas y refresco de timestamps.
- **Alcance:**
  - Activar un workflow cron en `.github/workflows/revalidation-audit.yml` (ejecución semanal).
  - Cerrar automáticamente registros cuya vacante desapareció del ATS tras 2 verificaciones consecutivas.
- **Criterios de Aceptación:**
  1. Convocatorias cerradas pasan automáticamente a estado histórico sin intervención manual.

---

### FASE VALOR PROFESIONAL Y UX: Modalidades, Habilidades y Trayectorias (R7)

#### `TASK-R7-01` — Taxonomía de Regímenes Laborales Peruanos (CAS, 728, Formativo)
- **Prioridad:** `P2` (Valor funcional Perú)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `PENDING`
- **Dependencias:** `TASK-R5-01`.
- **Objetivo:** Permitir al usuario filtrar y entender la modalidad de contratación en el sector público y privado.
- **Alcance:**
  - Añadir filtro en frontend y campo en esquema: `Modalidad Formativa (Ley 28518)`, `CAS (D.L. 1057)`, `Régimen 728 (Privado/Público)`, `Locación de Servicios / Honorarios`.
  - Explicar en la tarjeta los derechos básicos asociados a cada modalidad (ej. subvención, seguro, vacaciones).
- **Criterios de Aceptación:**
  1. Filtro visible en UI que discrimina efectivamente puestos formativos de CAS y régimen privado.

#### `TASK-R7-02` — Comparador de Trayectorias y Requisitos Técnicos
- **Prioridad:** `P3` (Evolución de producto)
- **Tipo:** `[DESARROLLO_PROPIO - Justificado]`
- **Estado:** `PENDING`
- **Dependencias:** `TASK-R7-01`.
- **Objetivo:** Brindar a los estudiantes herramientas de análisis de brechas de habilidades frente a los requisitos del mercado.
- **Alcance:**
  - Extraer nube de tecnologías y competencias requeridas (Python, Java, Cloud, SQL, Redes) y contrastar requisitos entre dos oportunidades en el comparador actual.
- **Criterios de Aceptación:**
  1. Vista comparativa resalta competencias coincidentes y diferenciadoras.

---

## 5. Siguiente Acción Única Recomendada

**`TASK-R4-11-02` (Transición Oficial de Identidad Visual y Marca a "Velora"):**
Una vez asegurada la paridad operativa y resuelto el desacople de frescura en producción (`TASK-R4-11-01` y `TASK-R4-11-03` en DONE), la siguiente acción es unificar la identidad de marca bajo el nombre oficial **Velora** en toda la interfaz de usuario, títulos, meta tags, package.json y documentación pública.
