# Informe de Auditoría y Verificación: R2-A-01 — Preparación y Verificación del Expediente de Autorización de Fuente Piloto

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2 Línea A — Preparación y Verificación del Expediente de Autorización de Fuente Piloto  
**Veredicto del Bloque:** **EXPEDIENTE DE AUTORIZACIÓN VERIFICADO Y LISTO PARA REVISIÓN HUMANA**  
**Estado de Producto (Línea A - Fase R2 Real):** **ABIERTA Y BLOQUEADA POR AUTORIZACIÓN EXTERNA**  
**Roles:** Principal Software Architect, Technical Product Manager, OSS Integration Specialist, Analista de Fuentes y Políticas de Publicación, Technical Auditor, Especialista en Gobernanza de Datos y Trazabilidad.  
**Clasificación técnica:** `[GOBERNANZA_DE_DATOS]` `[AUDITORÍA_EDITORIAL]` `[PREPARACIÓN_EXTERNA]`  

---

## 1. Fuentes Revisadas en el Repositorio

Se realizó una inspección exhaustiva de la totalidad de las fuentes registradas en la arquitectura documental y en `collector/sources.json`. No se incorporaron fuentes nuevas ajenas al historial del proyecto.

| ID en `sources.json` | Entidad Responsable | Tipo / Conector | Decisión Actual | Presupuesto (`maxRequestsPerRun`) |
|---|---|---|---|---|
| `canonical-careers` | Canonical Group Limited | `employer_site` (`manual-review`) | `pending_review` | `0` (deshabilitada) |
| `talento-peru-servir` | Autoridad Nacional del Servicio Civil (SERVIR) | `official_discovery_portal` (`manual-review`) | `pending_review` | `0` (deshabilitada) |
| `unmsm-fisi-employment-board` | Facultad de Ing. de Sistemas e Informática (UNMSM) | `institutional_employment_board` (`manual-review`) | `pending_review` | `0` (deshabilitada) |
| `ositran-manual-review` | Organismo Supervisor de la Inversión en Infraestructura de Transporte (OSITRAN) | `employer_site` (`manual-review`) | `pending_review` | `1` (deshabilitada, `enabled: false`) |
| `greenhouse-public-job-board-template` | ATS Greenhouse (plantilla abstracta sin empleador) | `public_ats_api` (`greenhouse-job-board`) | `pending_review` | `1` (deshabilitada, `employer: null`) |
| `lever-public-postings-template` | ATS Lever (plantilla abstracta sin empleador) | `public_ats_api` (`lever-postings`) | `pending_review` | `1` (deshabilitada, `employer: null`) |
| `freehire-discovery-reference` | Freehire (índice de terceros) | `third_party_index` (`disabled`) | `pending_review` | `0` (deshabilitada) |

---

## 2. Evidencia Documental Encontrada

A partir de la inspección de `docs/sources/canonical-careers-2026-11-11.md`, `docs/sources/talento-peru-servir-2026-10-26.md`, `docs/sources/seguimiento-autorizacion-fuentes.md`, `collector/sources.json`, `docs/adr/ADR-001-catalogo-curado-publicacion-segura.md`, `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md` y `Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`, se constata la siguiente evidencia objetiva:

### A. Canonical Careers (`canonical-careers`)
1. **Identificación institucional:** Empleador corporativo único (Canonical Group Limited), con portal oficial en `https://canonical.com/careers`.
2. **Políticas y términos del sitio:** En `https://canonical.com/legal/terms`, se especifica que el contenido del sitio web está protegido y que su descarga e impresión se autorizan exclusivamente para uso *personal, educativo y no comercial, conservando los avisos de copyright y marcas*. Esta cláusula general no autoriza expresamente a un tercero como Ruta Sistemas a almacenar, estructurar ni republicar ofertas de trabajo en un catálogo web público.
3. **Privacidad de postulantes:** En `https://canonical.com/legal/data-privacy/recruitment`, la política regula la recopilación de datos de aplicantes. El modelo de Ruta Sistemas respeta esto al no recopilar CVs, formularios ni datos personales, pero requiere confirmación de que enlazar directamente a la ficha corporativa de postulación es conforme a sus directrices.
4. **Política remota y elegibilidad para Perú:** En `https://canonical.com/careers/company-culture/remote-work`, se describe un modelo global de trabajo distribuido. Sin embargo, no todas las posiciones abiertas en Canonical son elegibles para contratación remota desde Perú (varían por zona horaria, entidad legal de contratación o requerimientos regulatorios). La etiqueta "remote" no prueba elegibilidad territorial.
5. **Canal de contacto jurídico verificado:** Los términos legales del sitio publican explícitamente `legal@canonical.com`.

### B. SERVIR — Talento Perú (`talento-peru-servir`)
1. **Identificación institucional:** Autoridad Nacional del Servicio Civil (SERVIR), entidad rectora del empleo público en Perú.
2. **Portal y mecanismo de difusión:** Difunde convocatorias del régimen público a través de la campaña oficial `https://www.gob.pe/institucion/servir/campañas/4782-talento-peru` y la aplicación web de consulta pública `https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml`.
3. **Naturaleza jurídica de difusor vs. empleador:** Talento Perú actúa como *publisher* agregador oficial del Estado. Las preguntas frecuentes oficiales aclaran que la postulación efectiva y las bases completas residen en la entidad estatal convocante (Ministerio, Municipalidad, etc.). Por tanto, Talento Perú no es el empleador ni el canal final de postulación.
4. **Restricciones técnicas y regulatorias:** No existe una API pública documentada ni un catálogo abierto con licencia libre para redistribución automatizada de vacantes. Intentos previos de consulta automatizada recibieron códigos HTTP 403.
5. **Canales de contacto verificados:** El directorio oficial publica `talentoperu@servir.gob.pe` y la central telefónica (01) 206-3370 (anexo 2519 para empleos, 2616 para prácticas).

### C. FISI — UNMSM (`unmsm-fisi-employment-board`)
1. **Identificación institucional:** Facultad de Ingeniería de Sistemas e Informática de la Universidad Nacional Mayor de San Marcos.
2. **Naturaleza de los avisos:** Sección de noticias y bolsa institucional en `https://sistemas.unmsm.edu.pe/site/noticias/38-oportunidad-laboral`.
3. **Restricciones:** Los avisos corresponden a convocatorias remitidas por empresas externas variadas o prácticas institucionales. FISI no es el empleador de los avisos privados. En pruebas documentales pasadas la web arrojó HTTP 502 y no dispone de API ni términos de reutilización estructurada.
4. **Canales verificados:** Directorio oficial lista `decanato.fisi@unmsm.edu.pe` y `mesadepartes.fisi@unmsm.edu.pe`.

---

## 3. Estado Real de Solicitudes y Respuestas

Conforme a la auditoría técnica de los registros de seguimiento:

- **Solicitudes formalmente enviadas:** **NINGUNA (0).** En ningún momento el asistente ni el equipo han enviado correos electrónicos, peticiones formales ni formularios a Canonical, SERVIR, FISI ni a otra entidad.
- **Borradores preparados:** Existen borradores preliminares en `docs/sources/seguimiento-autorizacion-fuentes.md` para SERVIR y FISI, y puntos temáticos para Canonical en `docs/sources/canonical-careers-2026-11-11.md`.
- **Respuestas documentales recibidas:** **NINGUNA (0).** El estado de respuesta para todas las candidatas es taxativamente `Pendiente`.
- **Restricciones comprobadas:**
  - Disponibilidad técnica pública ≠ Autorización de reutilización.
  - No existe consentimiento tácito ni silencio administrativo positivo aplicable a la reutilización de bases de datos o portales de empleo de terceros.
  - La línea offline R2-OSS cerrada en R2-OSS-08 no habilita la captura de datos reales; la política fail-closed permanece activa (`budget: 0`, `enabled: false`).
- **Información no verificada que requiere confirmación explícita:**
  - Si se admite la extracción o recopilación periódica manual y/o automatizada de metadatos mínimos.
  - Requisitos de atribución y formato exacto de enlaces de procedencia.
  - Mecanismos de baja y eliminación inmediata ante cierre o solicitud de la entidad.
  - Confirmación fehaciente de contratación remota admitida para personas con residencia fiscal en Perú.

---

## 4. Comparación de Candidatas a Fuente Piloto

Se evalúan y contrastan las dos candidatas prioritarias documentadas en el repositorio: **Canonical Careers** (sector tecnológico privado internacional) y **SERVIR — Talento Perú** (sector público nacional).

| Criterio de Evaluación | Canonical Careers (`canonical-careers`) | SERVIR — Talento Perú (`talento-peru-servir`) | FISI — UNMSM (`unmsm-fisi-employment-board`) |
|---|---|---|---|
| **1. Afinidad con la población objetivo** | **Alta en contenido técnico:** Roles de Ingeniería de Software, Linux, Cloud, QA, SRE, pertinentes para egresados e iniciales. Exige inglés. | **Alta en territorio e idioma:** Convocatorias nacionales peruanas y prácticas directas para estudiantes en Perú en español. | **Alta para Sistemas:** Estudiantes y egresados de Sistemas de Perú. |
| **2. Existencia de vacantes relevantes** | Permanente catálogo de ingeniería a nivel global/regional. Requiere verificar elegibilidad desde Perú puesto por puesto. | Alto volumen de convocatorias CAS y prácticas pre/profesionales, pero requiere filtrar puestos de TI/Sistemas. | Volumen variable y esporádico en formato noticia/comunicado. |
| **3. Canal oficial de postulación** | **Unificado y directo:** Canonical es el empleador directo (`applyUrl` corporativo en canonical.com / ATS directo). | **Descentralizado:** Talento Perú es difusor; cada postulación se ejecuta en la web de la entidad convocante específica. | **Descentralizado:** Cada aviso pertenece a una empresa externa diferente. |
| **4. Claridad de la entidad responsable** | **Óptima:** Una única persona jurídica privada (Canonical Group Limited / Canonical). | **Compleja:** SERVIR es el difusor oficial rector, pero cada entidad pública es el empleador responsable de su concurso. | **Compleja:** FISI difunde, pero la empresa anunciante es la responsable legal. |
| **5. Disponibilidad de documentación de uso** | **Clara:** Términos de sitio web y política de privacidad de reclutamiento explícitamente redactadas. | **Incompleta:** No hay términos de reutilización digital de vacantes ni API documentada. | **Inexistente:** Portal de noticias universitario estándar sin términos de API/reuso. |
| **6. Posibilidad de solicitar autorización** | **Factible:** Canal jurídico institucional publicado (`legal@canonical.com`). | **Burocrática:** `talentoperu@servir.gob.pe` es mesa de atención; consultas legales suelen requerir trámite documentario. | Factible vía Decanato / Mesa de Partes, pero requiere autorizar avisos de terceros. |
| **7. Complejidad de reutilización** | Autorización bilateral privada sobre metadatos mínimos con atribución y enlace. | Marco normativo del sector público peruano y multiplicidad de convocatorias. | Ambigüedad sobre si FISI puede licenciar avisos que terceros le remitieron. |
| **8. Valor para validar el producto** | **Excelente para validar puestos remotos e ingeniería:** Prueba el modelo de datos canónico con empleador directo y remoto. | **Excelente para validar prácticas y empleo público:** Prueba el modelo con empleo local en Perú. | Moderado; útil como fuente secundaria complementaria. |

---

## 5. Fuente Piloto Recomendada

### Recomendación Técnica Justificada:
Con base en la evidencia documental analizada desde los hitos R0, R2, R4 y P3, se confirma que:

1. **Fuente Piloto Prioritaria:** **Canonical Careers (`canonical-careers`)** es la candidata técnica prioritaria para el primer piloto de Ruta Sistemas.
   - **Justificación:** Posee un único interlocutor jurídico claro (`legal@canonical.com`), un canal canónico corporativo de postulación unificado, roles técnicos directos de ingeniería de sistemas y una política formal de trabajo remoto. Permite validar de manera limpia el contrato Schema 2 (`employer: Canonical`, `publisherRelation: direct_employer`, `sourceKind: corporate_ats`).
2. **Fuente Piloto Nacional Alternativa:** **SERVIR — Talento Perú (`talento-peru-servir`)**.
   - **Justificación:** Es la opción de mayor pertinencia territorial para empleo estatal y prácticas pre/profesionales en Perú, pero presenta mayor complejidad operativa al ser difusor intermediario y no el empleador directo de las convocatorias.

> [!IMPORTANT]
> **Aviso de Gobernanza y Alcance Legal:**  
> La recomendación técnica **NO constituye autorización legal ni operativa**. Ninguna fuente está aprobada. La decisión de priorizar, contactar y remitir las solicitudes corresponde exclusivamente al propietario del proyecto.

---

## 6. Solicitudes Listas para Revisión y Envío Humano

Se preparan dos expedientes de solicitud estructurados, profesionales, breves y estrictamente alineados con los límites del proyecto.

---

### Expediente A: Solicitud a Canonical Careers

- **Destinatario:** `legal@canonical.com`  
- **Canal:** Correo electrónico institucional  
- **Idioma principal:** Inglés (idioma corporativo de Canonical Group Limited)  
- **Idioma de referencia técnica:** Español  

#### Versión para Envío (English):

```text
To: legal@canonical.com
Subject: Inquiry regarding non-commercial indexing of job metadata for Ruta Sistemas

Dear Canonical Legal Team,

I am writing on behalf of Ruta Sistemas, an independent, open, and non-commercial educational project based in Peru designed to help computer science and systems engineering students identify legitimate career and internship opportunities, with a special focus on remote roles eligible from Peru (https://github.com/Blueisazul/WebRutaSistemas).

We greatly admire Canonical’s commitment to open source and remote work. In reviewing your Website Terms and Conditions (https://canonical.com/legal/terms), we noted that content is authorized for personal, non-commercial, and educational use. To ensure absolute compliance with your guidelines, we are requesting explicit clarification regarding the indexing of select engineering opportunities in our curated directory.

Specifically, we seek written confirmation on the following points:

1. Manual Query & Discovery: Is our editorial team permitted to periodically review public postings at canonical.com/careers?
2. Minimal Metadata Retention & Display: Are we authorized to store and display minimal factual metadata (job title, department, location/country eligibility, publication date, and official canonical URLs)? We do NOT store full job descriptions, application forms, recruiter names, applicant CVs, or personal data.
3. Official Application Redirection: May we direct candidates exclusively to Canonical's official application URLs (never replacing or proxying Canonical's recruitment process)?
4. Automated Access / ATS Feeds (Optional): Does Canonical offer or permit a documented public feed, API endpoint, or low-frequency automated mechanism (e.g., 1 request per run, complying with User-Agent identification and rate limits)?
5. Attribution: What specific attribution notice and hyperlink format does Canonical require when displaying your opportunities?
6. Takedown & Deletion Policy: We enforce a strict editorial policy to remove or mark as closed any expired role within 7 days, and we commit to immediately removing any listing upon request from Canonical. Please confirm if you have a preferred contact channel for updates or takedown notices.
7. Remote Eligibility for Peru: Could you confirm whether remote engineering positions that indicate global or regional distribution accept applicants residing in Peru, or whether eligibility must be confirmed on an individual job basis?

Our project keeps the source entirely disabled and stores zero candidate records pending your written guidance. We do not claim any endorsement or existing authorization from Canonical.

Thank you very much for your time and guidance.

Sincerely,

[NAME OF PROJECT OWNER / LEAD]
Project Lead, Ruta Sistemas
Email: [OWNER EMAIL]
Repository: https://github.com/Blueisazul/WebRutaSistemas
Lima, Peru
```

#### Versión de Referencia (Español):

```text
Para: legal@canonical.com
Asunto: Consulta sobre indexación no comercial de metadatos de vacantes para Ruta Sistemas

Estimado equipo legal de Canonical:

Me dirijo a ustedes en nombre de Ruta Sistemas, un proyecto educativo independiente y sin fines de lucro desarrollado en Perú para orientar a estudiantes de Ingeniería de Sistemas e Informática hacia oportunidades laborales verificables, con especial interés en posiciones remotas elegibles desde Perú (https://github.com/Blueisazul/WebRutaSistemas).

Al revisar los Términos y Condiciones de su sitio web (https://canonical.com/legal/terms), observamos que el contenido está autorizado para uso personal, educativo y no comercial. Con el fin de garantizar el estricto cumplimiento de sus directrices, solicitamos su orientación formal respecto a la inclusión de oportunidades técnicas en nuestro catálogo curado.

Puntualmente, deseamos consultar:

1. Consulta manual: ¿Está autorizada la revisión periódica manual de publicaciones públicas en canonical.com/careers por parte de nuestro equipo curador?
2. Conservación y publicación de metadatos mínimos: ¿Se autoriza conservar y mostrar metadatos puramente factuales (título, área, país/modalidad elegible, fechas y enlaces oficiales)? Aclaramos que NO almacenamos descripciones completas, formularios, datos personales de postulantes ni CVs.
3. Redirección oficial de postulación: ¿Es conforme redirigir a las personas exclusivamente a la URL oficial de postulación de Canonical, sin intermediar el proceso de selección?
4. Mecanismos automatizados o feeds (opcional): ¿Dispone Canonical de un feed público, API o límite autorizado de frecuencia para consultas automatizadas de bajo impacto?
5. Atribución requerida: ¿Qué fórmula de atribución y enlaces de origen exige Canonical para referenciar sus oportunidades?
6. Política de retiro (takedown): Mantenemos una política editorial de retiro de fichas expiradas (TTL máximo de 7 días) y compromiso de baja inmediata ante cualquier solicitud de Canonical.
7. Elegibilidad remota desde Perú: ¿Las vacantes remotas de ingeniería que señalan distribución global/regional admiten postulantes residentes en Perú, o dicha elegibilidad se evalúa estrictamente por convocatoria?

Mantenemos la fuente completamente deshabilitada hasta recibir su respuesta escrita.

Agradecemos de antemano su atención y orientación.

Atentamente,

[NOMBRE DEL PROPIETARIO / RESPONSABLE]
Responsable de Proyecto, Ruta Sistemas
Correo: [CORREO DEL PROPIETARIO]
Repositorio: https://github.com/Blueisazul/WebRutaSistemas
Lima, Perú
```

---

### Expediente B: Solicitud a SERVIR — Talento Perú

- **Destinatario:** `talentoperu@servir.gob.pe`  
- **Canal:** Correo electrónico institucional  
- **Idioma:** Español  

```text
Para: talentoperu@servir.gob.pe
Asunto: Consulta formal sobre difusión no comercial de metadatos públicos de convocatorias de Talento Perú

Señores
Autoridad Nacional del Servicio Civil — SERVIR
Equipo de Talento Perú:

Me dirijo a ustedes en el marco de la iniciativa Ruta Sistemas (https://github.com/Blueisazul/WebRutaSistemas), un catálogo digital independiente y de fines estrictamente educativos diseñado para facilitar que estudiantes y egresados de Ingeniería de Sistemas de universidades peruanas identifiquen oportunidades laborales y prácticas en el sector público.

Con el objetivo de garantizar una gobernanza de datos transparente, respetuosa de la infraestructura pública y alineada con las directrices de SERVIR, nos ponemos en contacto antes de incorporar cualquier referencia a convocatorias difundidas en Talento Perú.

Agradeceremos nos brinden su orientación respecto a los siguientes puntos:

1. Consulta y difusión de metadatos mínimos: ¿Autoriza SERVIR la recopilación y publicación en un catálogo educativo de metadatos factuales mínimos (entidad convocante, puesto/práctica, identificador del proceso, fechas límite y enlace oficial), sin copiar el texto íntegro de las bases ni anexos administrativos?
2. Mecanismos de acceso: ¿Existe un catálogo de datos abiertos, API pública o feed oficial para consultar estas convocatorias? En su defecto, ¿está permitida la consulta manual por parte de nuestro equipo de revisión editorial?
3. Enlaces y postulación: Entendemos que Talento Perú actúa como portal difusor y que la postulación se realiza en la entidad convocante. ¿Qué pautas de atribución y redirección sugiere SERVIR mantener para que la ciudadanía distinga claramente el portal difusor de la sede de postulación?
4. Límites de consulta: En caso de permitirse consultas periódicas, ¿cuáles son los límites de frecuencia, horarios y políticas de cabecera (User-Agent) que deben respetarse?
5. Actualización y retiro: ¿Existe un mecanismo oficial o canal de contacto preferente para notificar despublicaciones, rectificaciones o cancelaciones de convocatorias?
6. Términos oficiales aplicables: ¿Dispone SERVIR de términos de uso, directivas de interoperabilidad o licencias de datos abiertos específicas para la difusión de información de Talento Perú por terceros?

Informamos que en nuestro repositorio la fuente permanece totalmente deshabilitada (presupuesto cero de solicitudes) y que no publicaremos ninguna información vinculada a Talento Perú hasta contar con su confirmación escrita.

Agradeciendo su valioso tiempo y orientación en beneficio de los estudiantes y jóvenes profesionales de nuestro país, quedo a su disposición.

Atentamente,

[NOMBRE DEL PROPIETARIO / RESPONSABLE]
Responsable de Proyecto, Ruta Sistemas
DNI: [DNI DEL RESPONSABLE]
Correo: [CORREO DEL PROPIETARIO]
Teléfono: [TELÉFONO DE CONTACTO]
Repositorio: https://github.com/Blueisazul/WebRutaSistemas
Lima, Perú
```

---

## 7. Matriz de Autorización de Actividades

La siguiente matriz documenta el estado de autorización desagregado por cada actividad operativa para las dos candidatas evaluadas. Conforme a las directrices de auditoría, cada permiso se evalúa de manera taxativamente independiente: la autorización de una actividad **no presupone ni extiende** la autorización sobre las demás.

| Actividad Operativa | Canonical Careers (`canonical-careers`) | SERVIR — Talento Perú (`talento-peru-servir`) | Justificación Técnica y Evidencia Documental |
|---|---|---|---|
| **Consulta manual de oportunidades** | **PENDIENTE** | **PENDIENTE** | Aunque los sitios son accesibles al público mediante navegador web, la consulta sistemática para alimentación de un catálogo externo requiere confirmación escrita de no objeción. |
| **Consulta automatizada (scraping / bots)** | **NO AUTORIZADA** | **NO AUTORIZADA** | Términos de Canonical restringen uso no personal; SERVIR bloqueó solicitudes en evaluaciones previas (HTTP 403). Presupuesto configurado en `maxRequestsPerRun: 0`. |
| **Uso de ATS / API / feed público** | **PENDIENTE** (no documentado) | **NO AUTORIZADA** (no existe API) | No se ha proporcionado credencial, token ni endpoint oficial autorizado. |
| **Conservación de metadatos mínimos** | **PENDIENTE** | **PENDIENTE** | No hay contrato ni licencia que autorice el almacenamiento local o en base de datos de los registros de vacantes de la entidad. |
| **Publicación de metadatos mínimos** | **PENDIENTE** | **PENDIENTE** | La republicación en un sitio web público de terceros requiere autorización expresa del titular de los derechos del contenido. |
| **Publicación de resúmenes propios factuales** | **PENDIENTE** | **PENDIENTE** | El resumen propio de requisitos no infringe derechos si es factual y breve, pero su asociación al catálogo depende de la autorización de difusión general. |
| **Conservación de evidencia y timestamps** | **PENDIENTE** | **PENDIENTE** | Guardar URLs HTTPS y fechas de observación para fines de trazabilidad y auditoría debe ser explícitamente informado y aceptado por la fuente. |
| **Uso de enlaces oficiales de postulación** | **PENDIENTE** | **PENDIENTE** | Se debe garantizar que la entidad autoriza el enlace profundo (*deep linking*) directo a su sistema de postulaciones sin intermediación. |
| **Elegibilidad remota desde Perú** | **NO CONFIRMADA** | **NO APLICABLE / CONFIRMADA LOCAL** | Canonical tiene política global remota, pero la elegibilidad para postulantes en Perú debe ser validada puesto por puesto. En SERVIR los puestos son nacionales en Perú. |

*Regla rectora:* El estado `PENDIENTE` rige mientras no exista documento escrito emitido por la entidad. El silencio no constituye autorización bajo ninguna circunstancia.

---

## 8. Información que Debe Proporcionar el Propietario

El agente y el equipo técnico no tienen personería jurídica ni facultades de representación. El propietario del proyecto debe definir y completar los siguientes datos antes de efectuar el envío:

1. **Datos de identidad del remitente:**
   - Nombre y apellidos completos del responsable del proyecto.
   - Rol o afiliación institucional (e.g., Fundador / Investigador Principal / Desarrollador Líder).
   - Documento de Identidad (DNI) en el caso de la solicitud a SERVIR (requerimiento habitual para trámites y consultas ciudadanas ante el Estado peruano).
2. **Canales de comunicación oficiales:**
   - Correo electrónico formal del remitente (preferentemente asociado al dominio o cuenta oficial del proyecto/autor).
   - Teléfono de contacto directo.
3. **Decisión estratégica de canal de envío:**
   - Confirmar si se remitirá primero el Expediente A (Canonical Careers) como piloto privado internacional, o el Expediente B (SERVIR) como piloto público nacional, o ambos de forma paralela.
   - Si se decide enviar a Canonical: enviar vía cliente de correo personal/institucional a `legal@canonical.com`.
   - Si se decide enviar a SERVIR: enviar a `talentoperu@servir.gob.pe`.
4. **Declaración de canal público:**
   - URL definitiva de visualización (por ahora `https://github.com/Blueisazul/WebRutaSistemas` y su despliegue en Pages).

---

## 9. Condiciones Taxativas para Desbloquear R2

Para que el estado de una fuente cambie de `pending_review` a autorizada en el repositorio y se proceda a desbloquear la fase R2 real, se debe contar con un expediente de respuesta que contenga:

1. **Respuesta escrita verificable:** Comunicación formal recibida por correo electrónico institucional o documento en soporte oficial proveniente del dominio oficial de la entidad (`canonical.com` o `servir.gob.pe`).
2. **Identificación suficiente del emisor:** Nombre, cargo o área responsable (e.g., Legal Counsel, Oficina de Comunicaciones, Dirección de Gestión del Servicio Civil) con facultades para fijar condiciones de uso.
3. **Delimitación explícita de actividades:**
   - Expresar con claridad si permite la consulta manual, la automatizada o ambas.
   - Indicar límites de frecuencia (máximo de solicitudes por minuto/hora) y User-Agent requerido.
4. **Términos de almacenamiento y publicación:** Autorización para almacenar metadatos factuales básicos y publicarlos en un catálogo web público sin fines de lucro.
5. **Directrices de atribución:** Requisitos explícitos sobre textos, logos o enlaces de atribución requeridos.
6. **Compromiso y procedimiento de retiro (takedown):** Confirmación de que las políticas editoriales de Ruta Sistemas (TTL de 7 días y retiro a solicitud) satisfacen sus exigencias.
7. **Resolución de ambigüedades:** Si la respuesta de la entidad es ambigua, evasiva, contradictoria o no responde a los puntos esenciales, la fuente **permanecerá en estado pendiente**. No se presumirá permiso bajo ninguna circunstancia.

---

## 10. Siguiente Acción Humana

El propietario del proyecto debe ejecutar los siguientes pasos en el plano exterior (fuera del repositorio):

1. **Revisión del Expediente:** Revisar los textos redactados en la Sección 6 de este informe.
2. **Completar datos de remitente:** Insertar su nombre, correo y datos de contacto en los campos marcados entre corchetes `[...]`.
3. **Envío formal:** Enviar el correo electrónico correspondiente desde su cuenta de correo a la entidad seleccionada (`legal@canonical.com` para Canonical o `talentoperu@servir.gob.pe` para SERVIR).
4. **Registro de fecha de envío:** Una vez enviado, notificar o registrar en el archivo de seguimiento la fecha civil exacta del envío y el código/asunto del mensaje.
5. **Espera de respuesta:** Mantener la política fail-closed en el código y pruebas. Una vez recibida la respuesta escrita, presentar el texto al equipo técnico para auditar el alcance de la autorización antes de activar cualquier conector en `collector/sources.json`.
