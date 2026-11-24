# VELORA-AUDIT-02 — Auditoría de Fuentes Nacionales: Cobertura, Viabilidad y Estrategia de Adquisición

- **Fecha de evaluación:** 23 de noviembre de 2026
- **Ámbito:** Fuentes del Estado Peruano, Fuentes Privadas Peruanas, ATS Corporativos y Plataformas Secundarias.
- **Responsables periciales:** Principal Data Acquisition Engineer, Compliance & Rights Auditor, OSS Integration Specialist.

---

## 1. Resumen Ejecutivo de Cobertura

Para convertir a **Velora** en el catálogo nacional de referencia en Ingeniería de Sistemas, Computación y Tecnología en el Perú, es imperativo contar con un flujo continuo y confiable de oportunidades de los tres sectores definidos:
1. **Sector Público Peruano:** Modalidades formativas (Prácticas pre y profesionales bajo Ley N° 28518), CAS (D.L. 1057) y Régimen 728.
2. **Sector Privado Peruano:** Empresas tecnológicas, banca, fintechs, telecomunicaciones, consultoras y corporaciones con centros de desarrollo en Lima y regiones.
3. **Puestos Remotos Internacionales con Elegibilidad Confirmada en Perú:** Posiciones globales o LATAM con evidencia documental de contratación a residentes peruanos.

### Hallazgo Central de la Auditoría de Fuentes:
Actualmente, el catálogo activo solo se nutre de **Greenhouse ATS** (privado/remoto). A pesar de contar con conectores nativos para el Estado (OSITRAN y Defensoría) en `collector/pe_connectors.py`, estos se encuentran inactivos en el catálogo publicado debido a que los procesos evaluados concluyeron su convocatoria. Las fuentes de mayor volumen estatal (**Talento Perú / SERVIR** y **Gob.pe**) aún no disponen de conectores automáticos aprobados.

---

## 2. Matriz Obligatoria de Fuentes Nacionales

| Fuente / Entidad | Sector | Cobertura Potencial | Mecanismo Técnico | Estado de Integración | Restricciones / Riesgos | Viabilidad | Próxima Acción |
|---|---|---|---|---|---|---|---|
| **OSITRAN Convocatorias** | Público (Regulador) | Prácticas y CAS de TI / Sistemas | HTML parsing + Extracción PDF nativa | **Implementado y Probado** (`ositran-convocatorias`) | Baja rotación; ventanas cortas (1-3 días) | `READY` | Mantener conector; ejecutar adquisición semanal continua. |
| **Defensoría del Pueblo** | Público (Constitucional) | CAS Sistemas, Redes, Datos, Arquitectura | HTML table parsing + Enlaces PDF | **Implementado y Probado** (`defensoria-del-pueblo-cas`) | Procesos CAS concluyen en pocas semanas | `READY` | Mantener conector; capturar apenas inicie convocatoria. |
| **UTP HiringRoom Campus** | Privado / Formativo | Ofertas y prácticas para universitarios | HTML + JSON-LD Schema.org `JobPosting` | **Implementado y Probado** (`utp-hiringroom-campus`) | Alcance mixto; vacantes no exclusivas | `READY_WITH_LIMITS` | Habilitar filtro estricto de carrera de Sistemas. |
| **Encora Perú (`encora10`)** | Privado (Tech Services) | Software, Datos, QA, Cloud, Prácticas | Greenhouse Job Board REST API (Keyless) | **En Producción Activa** (`greenhouse-encora`) | Límites de tasa estándar de Greenhouse | `READY` | Optimizar polling a 1 vez por semana. |
| **CookUnity Perú** | Privado (Foodtech) | Supply Chain, Operaciones, Tech Lima | Greenhouse Job Board REST API (Keyless) | **En Producción Activa** (`greenhouse-cookunity`) | Volumen muy bajo de vacantes en Lima | `READY` | Mantener monitoreo. |
| **Canonical** | Remoto Internacional | Software, Linux, Cloud, SRE (Perú elegible) | Greenhouse Job Board REST API (Keyless) | **En Producción Activa** (`greenhouse-canonical`) | Puestos en inglés; evaluación técnica rigurosa | `READY` | Mantener cuota actual. |
| **Sezzle** | Remoto LATAM | Software, QA, Soporte (Perú elegible) | Greenhouse Job Board REST API (Keyless) | **En Producción Activa** (`greenhouse-sezzle`) | Volumen moderado; compensación publicada en USD | `READY` | Mantener cuota actual. |
| **Gob.pe (Informes y Publicaciones)** | Público (Centralizado) | Altísimo: Ministerios, INDECOPI, SUNAT, etc. | HTML semántico + Descarga y parsing de PDF | **Pendiente de Desarrollo** (Analizado empíricamente) | Variación en estructura por entidad; PDFs escaneados | `READY_WITH_LIMITS` | Desarrollar adaptador `gobpe-convocatorias` para bases oficiales. |
| **Talento Perú / SERVIR** | Público (Autoridad Civil) | Máximo agregador estatal oficial | Aplicación web JavaServer Faces (JSF) | **Deshabilitado** (`pending_review` en `sources.json`) | Sin API/RSS; estado de sesión JSF; requiere autorización | `NEEDS_AUTHORIZATION` | Solicitar formalmente acceso o datos abiertos a SERVIR; o scraping defensivo con browserless. |
| **FISI - UNMSM** | Académico / Bolsa local | Prácticas y empleo de Sistemas | Portal Joomla informal | **Deshabilitado** (`pending_review`) | Estructura no estandarizada; requiere curación manual | `MANUAL_ONLY` | Mantener como fuente manual para contrastar. |
| **Practicas.pe** | Secundario / Agregador | Prácticas formativas a nivel nacional | Web scraping de resultados HTML | **No integrado** (Evaluado) | Es un agregador secundario; riesgo de desactualización | `PENDING_REVIEW` | Utilizar exclusivamente como **fuente de descubrimiento**, verificando siempre la fuente oficial. |
| **Convocatorias de Trabajo** | Secundario / Agregador | Convocatorias CAS y Régimen 728 | Web scraping de listados HTML | **No integrado** (Evaluado) | Republicación no autorizada; enlaces de terceros | `PENDING_REVIEW` | Usar como radar de alertas; prohibido usar como autoridad de postulación. |
| **Computrabajo / Bumeran** | Portales comerciales | Empleos masivos privados | Páginas web con Cloudflare Turnstile / Imperva | **No integrado** | Bloqueo activo anti-bot; violaría ToS y directrices | `BLOCKED` | **Descartar completamente**. |

---

## 3. Análisis Detallado de Fuentes Estatales Críticas

### 3.1 Talento Perú (SERVIR)
- **URL Oficial:** `https://talentoperu.servir.gob.pe/`
- **Portal de Consulta Pública:** `https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml`
- **Diagnóstico Técnico:**
  - El portal opera sobre tecnología **JavaServer Faces (JSF / Mojarra)** con almacenamiento de estado del lado del servidor (`javax.faces.ViewState`).
  - No existe API REST, JSON-LD, ni canal RSS/Atom documentado ni disponible.
  - La consulta requiere enviar formularios POST simulando la selección de filtros geográficos y ocupacionales, manteniendo cookies de sesión y tokens de estado dinámicos.
- **Aspectos Legales y de Cumplimiento:**
  - Los Términos de Uso de SERVIR y el Estado peruano no autorizan explícitamente la extracción automatizada masiva.
  - La entidad cuenta con canales de atención institucional (`talentoperu@servir.gob.pe`).
- **Veredicto:** `NEEDS_AUTHORIZATION`. La vía técnica más limpia y sostenible es gestionar una solicitud de colaboración o apertura de datos con SERVIR. De no obtenerse, la alternativa es implementar un scraper headless de bajo impacto (1 consulta diaria en horario no pico) únicamente para metadatos de descubrimiento.

### 3.2 Gob.pe — El Ecosistema de Informes y Publicaciones de Convocatorias
- **Caso Testeado:** INDECOPI (`https://www.gob.pe/institucion/indecopi/informes-publicaciones/8797503-convocatoria-prac-n-092-2026-practicante-profesional-oti`)
- **Diagnóstico Técnico:**
  - **HTTP:** Responde `200 OK` (33 KB de HTML ligero), sin barreras anti-bot ni CAPTCHA.
  - **Estructura semántica:** Contiene títulos claros (`PRAC N° 092-2026 PRACTICANTE PROFESIONAL - OTI`), fechas de publicación y entidad emisora.
  - **Archivos adjuntos:** Enlaza directamente a los PDFs de Bases, Cronograma e Instructivo en `https://cdn.www.gob.pe/uploads/document/file/...`.
  - **Compatibilidad con arquitectura existente:** Nuestro extractor nativo de PDF en `collector/pe_connectors.py` (`extract_text_from_pdf_bytes`) puede procesar estos PDFs directamente sin instalar librerías pesadas.
- **Veredicto:** `READY_WITH_LIMITS`. Es la fuente pública de mayor valor inmediato y legalmente segura (documentos oficiales de transparencia del Estado peruano).

### 3.3 Organismos Reguladores y Convocatorias Propias
- **OSITRAN:** Conector funcional. Problema: solo publica 2-4 convocatorias de TI al año, y el ciclo de postulación suele durar entre 2 y 5 días hábiles. Si la auditoría o ingesta se ejecuta fuera de esa ventana, el candidato aparece como cerrado.
- **SUNASS, OSINERGMIN, OSIPTEL:**
  - Operan con esquemas similares a OSITRAN o publican en Gob.pe.
  - Se deben crear adaptadores específicos o consolidar un adaptador genérico para portales de selección de reguladores peruanos.

---

## 4. Análisis de Fuentes Privadas Peruanas (ATS Corporativos)

El mercado laboral tecnológico formal en Perú utiliza de forma predominante sistemas ATS modernos:

1. **Greenhouse (`boards-api.greenhouse.io`):**
   - **Ventaja:** APIs públicas oficiales, sin autenticación requerida para listar empleos públicos por empresa (`boards-api.greenhouse.io/v1/boards/{boardToken}/jobs`).
   - **Empresas peruanas identificadas viables:**
     - **Encora Perú (`encora10`):** Ya integrada en R4-10. 13 vacantes en catálogo.
     - **CookUnity (`cookunity`):** Ya integrada.
     - **Belcorp:** Utiliza Greenhouse para roles regionales y tecnológicos.
     - **Stefanini LATAM:** Emplea Greenhouse / SmartRecruiters según unidad.
2. **Lever (`api.lever.co/v0/postings/{site}`):**
   - **Ventaja:** Endpoint JSON público nativo para portales de empleo de empresas.
   - **Empresas evaluadas en R4:** Fintual, Kavak.
   - **Oportunidad en Perú:** Varias startups y fintechs operando en Lima utilizan Lever.
3. **Ashby (`api.ashbyhq.com`):**
   - Empleado crecientemente por empresas de software modernas y scaleups con operaciones en Perú y LATAM.
   - Cuenta con endpoints públicos accesibles.

---

## 5. Plataformas Secundarias: Rol de Descubrimiento frente a Autoridad

1. **Practicas.pe:**
   - **Evaluación:** Gran volumen de recopilación de prácticas de Sistemas en Lima y provincias.
   - **Riesgo:** Copia bases y cronogramas, pero frecuentemente no actualiza prórrogas o cancelaciones de las entidades.
   - **Directriz Velora:** **Prohibido** utilizar Practicas.pe como `sourceUrl` o `applyUrl`. Puede utilizarse únicamente como índice secundario de descubrimiento para detectar que una entidad (ej. Municipalidad de Miraflores o Ministerio de Cultura) abrió una plaza, e inmediatamente el collector debe ir al portal oficial de dicha entidad a extraer la evidencia real.
2. **Convocatorias de Trabajo (`convocatoriasdetrabajo.com`):**
   - Mismo rol: canal de alerta temprana, jamás fuente de autoridad.

---

## 6. Plan de Acción Inmediato para Cobertura Nacional

1. **Desarrollar el conector `gobpe-convocatorias`:**
   - Aprovechar el extractor HTML y PDF ya validado en el repositorio.
   - Configurar rastreo de las páginas de Informes y Publicaciones de INDECOPI, SUNAT, MINSA, MEF, RENIEC y Poder Judicial para la carrera de Sistemas.
2. **Incorporar 3 nuevas empresas de tecnología en Perú vía Greenhouse/Lever:**
   - Evaluar bolsas de Belcorp, Yape/BCP (si tienen ATS compatible) y consultoras de software en Lima.
3. **Formalizar la consulta a SERVIR:**
   - Remitir comunicación institucional solicitando acceso a datos abiertos del catálogo de convocatorias de Talento Perú.
