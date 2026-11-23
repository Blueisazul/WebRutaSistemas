# Seguimiento de Fuentes y Autorización

**Actualización de Integración de Empresa Privada en Perú y Publicación en Catálogo (Hito R4-10-PE-CATALOG-RELEASE-01 — 2026-11-23):**
Se completó la investigación técnica de empresas privadas de tecnología con presencia y operaciones en Perú, revalidación de las fuentes del Estado y expansión del catálogo público:
1. **Encora Perú (`greenhouse-encora`):**
   - Tipo: Empresa multinacional de ingeniería de software y servicios digitales de primer nivel con sede corporativa en Perú (anteriormente Avantica Technologies, ubicada en Av. Antonio Miró Quesada 425, Piso 11, Magdalena del Mar - Torre Prisma, Lima).
   - Acceso: API pública oficial sin autenticación de Greenhouse Job Board (`https://boards-api.greenhouse.io/v1/boards/encora10/jobs`) y portal de aplicaciones (`https://job-boards.greenhouse.io/encora10/jobs/`).
   - Conector: `greenhouse-job-board` (`boardToken: "encora10"`).
   - Estado: `approved` (habilitada controlada, presupuesto: 5 peticiones/run, minDelay: 2000 ms).
   - Cobertura: 342 convocatorias totales evaluadas, 118 situadas en Perú, de las cuales 90 corresponden directamente a Ingeniería de Sistemas, Software, Datos, QA y Soporte IT.
   - Candidatos promovidos al catálogo canónico: 13 oportunidades verificadas activas (`OP-099` a `OP-111`), incluyendo 1 formativa (Practicante PreProfesional IT Support) y 12 técnicas de nivel medio/semisenior en Lima y Remoto nacional.
2. **Revalidación de Convocatorias del Estado (OSITRAN y Defensoría del Pueblo):**
   - Revalidación integral de los 10 candidatos capturados en R4-09.
   - Constatación: Las 3 convocatorias de OSITRAN (CP 029, CP 027, CP 026) y las 7 convocatorias de la Defensoría del Pueblo (CAS 185, 118, 117, 116, 21, 20, 17) alcanzaron publicación de Actas de Evaluación Final o Resultados de Mérito (concluidas/cerradas).
   - Decisión editorial: Marcadas como `rejected` con ciclo de vida `CLOSED` en staging bajo el principio fail-closed (cero publicación de ofertas cerradas o caducadas).
3. **Métricas de bandeja e inventario:**
   - Bandeja local (`data/candidates/inbox.local.json`): 254 candidatos (164 previos + 90 de Encora).
   - Catálogo canónico (`data/opportunities.seed.json`): ampliado de 99 a 112 oportunidades (107 activas + 5 históricas demostrativas).

**Actualización de Integración de Fuentes Peruanas (Hito R4-09-PE-SOURCES-01 — 2026-11-22):**
Se completó la prospección, evaluación técnica y autorización controlada de tres fuentes oficiales y verificables en el ámbito peruano para corregir la concentración excesiva en ofertas internacionales en inglés:
1. **OSITRAN Convocatorias (`ositran-convocatorias`):**
   - Tipo: Portal oficial de entidad del Estado peruano (Organismo Supervisor de la Inversión en Infraestructura de Transporte de Uso Público).
   - Acceso: HTTP GET directo a `https://oportunidadlaboral.ositran.gob.pe/convocatoria?nuevo=1` sin CAPTCHA, WAFs agresivos ni necesidad de credenciales.
   - Conector: `ositran-portal` (con soporte de extracción de bases PDF mediante descompresión zlib nativa estándar sin librerías externas).
   - Estado: `approved` (habilitada controlada, presupuesto: 5 peticiones/run, minDelay: 2000 ms).
   - Oportunidades relevantes identificadas: CP 029-2026 (Practicantes Profesionales de TI: Sistemas, Software, Informática), CP 027-2026 (Practicante Preprofesional de Sistemas e Informática), CP 026-2026 (Practicante Profesional de Sistemas e Informática).
2. **Defensoría del Pueblo CAS (`defensoria-del-pueblo-cas`):**
   - Tipo: Portal oficial de entidad constitucionalmente autónoma del Estado peruano.
   - Acceso: Tabla HTML accesible en `https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php` con canal de postulación oficial en `https://apps2.defensoria.gob.pe:8443/CasOnline/`.
   - Conector: `defensoria-cas`.
   - Estado: `approved` (habilitada controlada, presupuesto: 5 peticiones/run, minDelay: 2000 ms).
   - Oportunidades relevantes identificadas: CAS 185-2026-DP (Analista en Desarrollo de Sistemas), CAS 118-2026-DP (Analista en Desarrollo de Sistemas), CAS 117-2026-DP (Analista en Redes), CAS 116-2026-DP (Analista en Desarrollo de Sistemas), CAS 20-2026-DP (Especialista en Arquitectura de Software e Interoperabilidad III), CAS 17-2026-DP (Analista de Datos).
3. **UTP Empleos Campus HiringRoom (`utp-hiringroom-campus`):**
   - Tipo: Portal institucional de empleo universitario que canaliza vacantes verificadas para estudiantes y egresados en Perú.
   - Acceso: `https://utp.hiringroomcampus.com/` con especificación de metadatos abiertos Schema.org `JobPosting` en formato JSON-LD.
   - Conector: `hiringroom-board` (procesado mediante `jsonld_extractor.py`).
   - Estado: `approved` (habilitada controlada, presupuesto: 5 peticiones/run, minDelay: 2000 ms).
4. **Talento Perú (SERVIR):**
   - Estado: permanece `pending_review` (deshabilitada) debido a que su aplicativo oficial de búsqueda (`app.servir.gob.pe`) opera bajo Java Server Faces con estado de sesión y token dinámico, clasificándose como `MANUAL_ONLY` sin API pública documentada.
5. **Candidatos ingresados a staging:** 10 nuevos candidatos normalizados bajo Candidate Schema 2 con evidencias rastreables ingresados a `data/candidates/inbox.local.json` (total staging acumulado: 164 candidatos). Catálogo canónico (`data/opportunities.seed.json`) y snapshot público (`data/opportunities.json`) mantenidos 100% inalterados.

**Actualización de Revisión Editorial y Preparación de Aprobación (Hito R2-A-04 — 2026-11-18):**
Se completó la auditoría de evidencia y revisión editorial humana de la oportunidad seleccionada:
- **CookUnity Greenhouse ATS (`8039990003`):** *Supply Chain Analyst* en `Lima, Lima Province, Peru` (`PERU_LOCAL`).
  * Auditoría temporal: Verificación en tiempo real a las `2026-11-17T22:28:37-05:00` (HTTP 200 OK en Greenhouse API y portal oficial de carreras).
  * Dictamen editorial: `APPROVE_WITH_LIMITATIONS`. Se constató que es un puesto de tiempo completo enfocado en analítica de datos SQL y sistemas ERP/MRP que requiere 1+ años de experiencia (adecuado para bachilleres/egresados de Sistemas, no para estudiantes activos en ciclo regular ni prácticas de desarrollo de software puro).
  * Candidato en reserva: Canonical `8379825` (*Graduate Software Engineer*) preservado en staging en estado `pending_review` sin modificaciones.
  * Informe completo: [docs/audits/r2-a-04-editorial-decision-2026-11-18.md](../audits/r2-a-04-editorial-decision-2026-11-18.md).

**Actualización de Recaptura Controlada y Consolidación de Evidencia (Hito R2-A-03 — 2026-11-18):**
Se ejecutó la recaptura controlada y consolidación del expediente de la primera oportunidad real seleccionada:
- **CookUnity Greenhouse ATS (`8039990003`):** *Supply Chain Analyst* en `Lima, Lima Province, Peru` (`PERU_LOCAL`).
  * Verificación en tiempo real: HTTP 200 OK en Greenhouse API (`boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`), portal oficial de carreras (`careers.cookunity.com/jobs/8039990003`) y ATS Greenhouse (`job-boards.greenhouse.io/cookunity/jobs/8039990003`).
  * Datos enriquecidos con evidencia: `publishedAt` confirmado como `2026-10-21` (según `first_published` en API y `datePosted` en Schema.org JobPosting JSON-LD).
  * Evidencias: 7 evidencias verificadas con frescura inmediata (`ALL_FRESH`, TTL 7 días Lima).
  * Candidato en reserva: Canonical `8379825` (*Graduate Software Engineer*) preservado en staging en estado `pending_review` sin modificaciones.
  * Expediente completo documentado en [docs/audits/r2-a-03-controlled-capture-2026-11-18.md](../audits/r2-a-03-controlled-capture-2026-11-18.md).

**Actualización de Curaduría Editorial y Verificación de Elegibilidad (Hito R2-A-02 — 2026-11-17):**
La auditoría editorial sobre 7 oportunidades en staging (`data/candidates/inbox.local.json`) identificó dos oportunidades aptas para consideración del propietario del proyecto (`ESTADO A`):
1. **Canonical Greenhouse ATS (`8379825`):** *Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu* (Remoto global / huso horario AMER que incluye Perú, dirigida a recién graduados 2026/2027 en Ciencias de la Computación o Ingeniería de Sistemas).
2. **CookUnity Greenhouse ATS (`8039990003`):** *Supply Chain Analyst* (Presencial/Híbrida en Lima, Perú, con enfoque en consultas SQL, aseguramiento de calidad de datos, sistemas ERP y modelado de datos).

Los cuatro candidatos previos de Wikimedia Foundation fueron descartados formalmente: la vacante de prácticas (`8268853`) excluye postulantes fuera de ciertos estados de EE.UU. (`NOT_ELIGIBLE`) y las tres restantes exigen perfiles Senior (`NOT_RELEVANT`). El informe exhaustivo de curaduría se encuentra en [docs/audits/r2-a-02-editorial-review-2026-11-17.md](../audits/r2-a-02-editorial-review-2026-11-17.md).

**Actualización estratégica (Hito R2-A-01-REV — 2026-11-17):**
Ruta Sistemas ha ampliado su marco de adquisición hacia el **descubrimiento e integración de fuentes públicas, feeds abiertos y mecanismos documentados de sindicación de vacantes (APIs públicas keyless de ATS)**. La operación del proyecto no está supeditada de manera universal a la respuesta bilateral de una única entidad (como SERVIR o Canonical). Para fuentes públicas con APIs documentadas (como Greenhouse Job Board API y Lever Postings API), la ingestión a staging se rige por especificación técnica y directrices de uso público, manteniendo la verificación estricta de procedencia, TTL de 7 días y elegibilidad territorial para Perú. El informe exhaustivo de fuentes públicas y la muestra en staging se encuentran en [docs/audits/r2-a-01-rev-public-sources-discovery-2026-11-17.md](../audits/r2-a-01-rev-public-sources-discovery-2026-11-17.md).

**Historial de expedientes de autorización (Hito R2-A-01):**
Los borradores preparados para consulta bilateral formal se conservan intactos a continuación como parte del archivo histórico de gobernanza para entidades con términos restrictivos o portales sin APIs públicas. Ninguna solicitud ha sido enviada por el asistente ni se usan datos personales sin instrucción expresa del propietario.

## Evidencia y contactos oficiales

### SERVIR — Talento Perú

- Fuente: [página oficial Talento Perú](https://www.gob.pe/institucion/servir/campa%C3%B1as/4782-talento-peru).
- La [página oficial de canales de consulta](https://www.gob.pe/institucion/servir/informes-publicaciones/6182394-directorio-de-plataformas-para-canales-de-atencion-de-consultas) lista “Búsqueda de empleos y prácticas en el Estado — Talento Perú” y enlaza a la [aplicación de consulta pública](https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml). La herramienta de navegación recibió HTTP 403 al abrir esa URL; no permite concluir si el sitio requiere interacción, bloquea automatización o está inaccesible desde este entorno.
- La página institucional de Talento Perú publica `talentoperu@servir.gob.pe` y los anexos telefónicos para consultas; la nota oficial de lanzamiento también identifica ese correo y los anexos de ofertas laborales/prácticas: [contacto para Talento Perú](https://www.servir.gob.pe/servir-lanza-unico-portal-de-ofertas-de-empleos-y-practicas-en-el-estado-talento-peru/).
- Contacto de primer envío sugerido: `talentoperu@servir.gob.pe` (canal específico publicado por SERVIR). El teléfono publicado es (01) 206-3370, anexos 2519 para ofertas laborales y 2616 para prácticas, según la página de campaña.

### FISI — UNMSM

- Fuente: [portal oficial FISI](https://sistemas.unmsm.edu.pe/) y [sección Oportunidad Laboral](https://sistemas.unmsm.edu.pe/site/noticias/38-oportunidad-laboral).
- El [directorio institucional de FISI](https://sistemas.unmsm.edu.pe/posgrado/directorio/) identifica `decanato.fisi@unmsm.edu.pe` como correo del Decanato y `mesadepartes.fisi@unmsm.edu.pe` como Mesa de Partes. Contacto sugerido para la consulta: Decanato; Mesa de Partes queda como canal institucional alterno si no existe otro canal aplicable.
- El sitio muestra anuncios de empleadores externos y oportunidades institucionales. La autoridad del contenido y del canal de postulación debe evaluarse por cada ficha; no asumir que FISI es el empleador.

### Canonical Careers

- Fuente: [portal oficial de carreras](https://canonical.com/careers), [roles abiertos](https://canonical.com/careers/all) y [política de trabajo remoto](https://canonical.com/careers/company-culture/remote-work).
- Los [términos del sitio](https://canonical.com/legal/terms) limitan el uso visible del contenido a fines personales, educativos y no comerciales, conservando avisos. No acreditan extracción automatizada ni republicación pública en Ruta Sistemas.
- Contacto jurídico publicado: `legal@canonical.com`. El expediente detallado está en [canonical-careers-2026-11-11.md](canonical-careers-2026-11-11.md).
- Estado: `pending_review`, deshabilitada, presupuesto cero. La candidata es relevante por roles de ingeniería y trabajo remoto, pero la elegibilidad para Perú y los derechos de uso deben confirmarse por escrito.

## Borrador para SERVIR

**Para:** talentoperu@servir.gob.pe<br>
**Asunto:** Consulta sobre acceso y reutilización de metadatos públicos de Talento Perú

> Señores de SERVIR / equipo de Talento Perú:
>
> Estoy preparando Ruta Sistemas, un catálogo independiente para ayudar a estudiantes y profesionales de Ingeniería de Sistemas a encontrar convocatorias públicas y verificar siempre la fuente y el canal oficial de postulación. Antes de incorporar información de Talento Perú, quisiera confirmar las condiciones aplicables.
>
> 1. ¿Existe una API, feed, exportación o mecanismo oficial autorizado para consultas automatizadas por un proyecto externo? ¿La aplicación pública de consulta puede consultarse automáticamente o solo mediante navegación humana?
> 2. ¿Se permite almacenar y reutilizar en un catálogo público metadatos mínimos de una convocatoria (entidad, título, identificador, fechas, ubicación y enlace), sin copiar las bases ni la descripción completa?
> 3. ¿Qué atribución y enlaces de origen deben mostrarse? ¿Debe enlazarse siempre también al portal de la entidad convocante?
> 4. ¿Qué frecuencia, límites, identificación del cliente o condiciones técnicas deben respetarse?
> 5. ¿Qué política de retención, corrección y retirada recomienda o exige SERVIR para registros y metadatos derivados?
> 6. ¿Qué campo o enlace permite identificar el canal vigente de postulación? ¿La presencia de una ficha en Talento Perú significa que la postulación sigue abierta, o debe confirmarse en el portal de cada entidad?
> 7. ¿Hay términos, licencias o restricciones que impidan publicar esos metadatos en un catálogo de terceros, incluso citando y enlazando la fuente?
>
> Mantendremos la fuente deshabilitada hasta recibir orientación suficiente. Agradeceré que indiquen los términos/documentos oficiales aplicables o el área competente para responder.
>
> Atentamente,<br>
> Equipo Ruta Sistemas

## Borrador para FISI-UNMSM

**Para:** decanato.fisi@unmsm.edu.pe<br>
**Asunto:** Consulta sobre difusión y reutilización de avisos laborales publicados por FISI

> Señores del Decanato de la Facultad de Ingeniería de Sistemas e Informática:
>
> Estoy preparando Ruta Sistemas, un catálogo independiente para orientar a estudiantes y profesionales de Sistemas hacia oportunidades verificables. En el portal FISI observamos avisos laborales y de prácticas, algunos remitidos por empleadores externos. Antes de registrar esos avisos, quisiera confirmar el uso permitido.
>
> 1. ¿Existe una API, feed, exportación o mecanismo oficial para consultar avisos; se permite automatizar consultas a las páginas públicas de Oportunidad Laboral?
> 2. ¿FISI autoriza conservar y publicar metadatos mínimos (título, entidad anunciante, fecha y enlace), sin reproducir el texto íntegro ni anexos? ¿Debe solicitarse autorización a cada empleador anunciante?
> 3. ¿Qué atribución y enlaces de origen deben mantenerse?
> 4. ¿Qué frecuencia y límites técnicos deben respetarse?
> 5. ¿Cuál es el procedimiento para corregir o retirar un aviso, y cuánto tiempo puede conservarse la referencia?
> 6. ¿Cómo distinguir anuncios vigentes, cerrados o históricos y verificar el canal oficial de postulación?
> 7. ¿Qué condiciones del portal o de los avisos limitan republicar esos metadatos en un catálogo público?
>
> No automatizaremos consultas ni publicaremos avisos hasta aclarar estas condiciones. Si esta consulta corresponde a otra oficina, agradeceré nos indiquen el canal oficial adecuado.
>
> Atentamente,<br>
> Equipo Ruta Sistemas

## Borrador para Canonical Careers

**Para:** legal@canonical.com<br>
**Asunto:** Inquiry regarding non-commercial indexing of job metadata for Ruta Sistemas

> Dear Canonical Legal Team:
>
> I am writing on behalf of Ruta Sistemas, an independent, open, and non-commercial educational project based in Peru designed to help computer science and systems engineering students identify legitimate career and internship opportunities, with a special focus on remote roles eligible from Peru (https://github.com/Blueisazul/WebRutaSistemas).
>
> In reviewing your Website Terms and Conditions (https://canonical.com/legal/terms), we noted that content is authorized for personal, non-commercial, and educational use. To ensure absolute compliance with your guidelines, we are requesting explicit clarification regarding the indexing of select engineering opportunities in our curated directory.
>
> 1. Manual Query: Is our editorial team permitted to periodically review public postings at canonical.com/careers?
> 2. Minimal Metadata Retention & Display: Are we authorized to store and display minimal factual metadata (job title, department, location/country eligibility, publication date, and official canonical URLs)? We do NOT store full job descriptions, application forms, recruiter names, applicant CVs, or personal data.
> 3. Official Application Redirection: May we direct candidates exclusively to Canonical's official application URLs (never replacing or proxying Canonical's recruitment process)?
> 4. Automated Access / ATS Feeds (Optional): Does Canonical offer or permit a documented public feed, API endpoint, or low-frequency automated mechanism (e.g., 1 request per run, complying with User-Agent identification and rate limits)?
> 5. Attribution: What specific attribution notice and hyperlink format does Canonical require when displaying your opportunities?
> 6. Takedown & Deletion Policy: We enforce a strict editorial policy to remove or mark as closed any expired role within 7 days, and we commit to immediately removing any listing upon request from Canonical. Please confirm if you have a preferred contact channel for updates or takedown notices.
> 7. Remote Eligibility for Peru: Could you confirm whether remote engineering positions that indicate global or regional distribution accept applicants residing in Peru, or whether eligibility must be confirmed on an individual job basis?
>
> Our project keeps the source entirely disabled and stores zero candidate records pending your written guidance. We do not claim any endorsement or existing authorization from Canonical.
>
> Sincerely,<br>
> [Nombre del Responsable / Project Lead]<br>
> Ruta Sistemas

## Registro de seguimiento y decisión

| Fuente | Contacto verificado | Estado del borrador | Solicitud enviada | Respuesta | Decisión actual |
|---|---|---|---|---|---|
| OSITRAN Convocatorias (Estado PE) | Portal oficial `oportunidadlaboral.ositran.gob.pe` | Verificación técnica de portal público y bases PDF; conector `ositran-portal` | No requiere consulta bilateral (Portal público oficial) | HTTP 200 OK factual | `approved` (Habilitada en R4-09) |
| Defensoría del Pueblo CAS (Estado PE) | Portal oficial `defensoria.gob.pe` | Verificación técnica de portal público de convocatorias CAS; conector `defensoria-cas` | No requiere consulta bilateral (Portal público oficial) | HTTP 200 OK factual | `approved` (Habilitada en R4-09) |
| UTP HiringRoom Campus (Institucional PE) | Portal oficial `utp.hiringroomcampus.com` | Verificación técnica de especificación Schema.org JobPosting JSON-LD | No requiere consulta bilateral (Metadatos abiertos) | HTTP 200 OK factual | `approved` (Habilitada en R4-09) |
| Canonical Careers (Bilateral) | `legal@canonical.com`; términos oficiales | Preparado y revisado; listo para envío | No enviada | Pendiente | `pending_review` |
| Talento Perú / SERVIR | `talentoperu@servir.gob.pe`; página de campaña oficial | Preparado y revisado; listo para envío | No enviada | Pendiente | `pending_review` |
| FISI / UNMSM | `decanato.fisi@unmsm.edu.pe`; directorio oficial | Preparado; no enviado | No enviada | Pendiente | `pending_review` |
| Canonical (Greenhouse Public ATS) | API pública `boards-api.greenhouse.io` | Candidato `8379825` validado en staging (AMER/Worldwide) | No aplica (Pública) | Factual keyless | `pending_review` (En reserva; apta para futura promoción) |
| CookUnity (Greenhouse Public ATS) | API pública `boards-api.greenhouse.io` | Candidato `8039990003` auditado, revisado y promovido al catálogo (`OP-005`, R2-A-05) | No aplica (Pública) | Factual keyless | `published` (Promovida con limitaciones: rol profesional no inicial; 21 evidencias activas) |
| Wikimedia (Greenhouse Public ATS) | API pública `boards-api.greenhouse.io` | 4 candidatos evaluados en staging; descartados por territorio/seniority | No aplica (Pública) | Factual keyless | `pending_review` (Sin candidatos aptos) |

### Criterios para reabrir la decisión

- **Aprobar consulta automatizada:** obtener una fuente oficial que permita explícitamente el mecanismo y propósito; conocer hosts, límites, frecuencia y manejo de errores; confirmar que no se requieren credenciales o evasión de controles.
- **Aprobar almacenamiento/reutilización pública:** confirmar el conjunto mínimo de metadatos que puede conservarse/publicarse, atribución, enlaces, retención, corrección y retirada. Si el permiso cubre solo navegación manual, registrar la autorización manual por separado y mantener el adaptador deshabilitado.
- **Validar publicación de una ficha:** verificar individualmente que el anunciante/entidad de origen está identificado, que la fuente autoriza el uso del dato, y que el canal de postulación vigente y la evidencia reciente pertenecen al empleador o entidad responsable. El TTL y una respuesta HTTP no son prueba de vigencia.
- **Rechazar:** registrar una prohibición expresa, incompatibilidad de licencia/condiciones, necesidad de eludir controles o falta de canal/evidencia confiable que no pueda corregirse.
- **Mantener pendiente:** cualquier silencio, respuesta ambigua o evidencia incompleta. No habilitar solicitudes por defecto.

Una autorización manual nunca habilita automáticamente el conector. La configuración debe mantener separadas las decisiones de acceso manual, automatización y reutilización/publicación.
