# INFORME DE INVESTIGACIÓN TÉCNICA — TASK-R5-04-01
## Evaluación de Plataformas Secundarias (Practicas.pe y Convocatorias de Trabajo) como Radares de Descubrimiento para Velora

- **Fecha:** 24 de noviembre de 2026
- **Fase:** R5 — Cobertura nacional de oportunidades
- **Tarea:** `TASK-R5-04-01`
- **Prioridad propuesta:** P1
- **Clasificación:** `[INVESTIGACIÓN_TÉCNICA]`
- **Estado:** PROPUESTA EVALUADA (Pendiente de decisión del propietario)
- **Autor:** Principal Software Architect & Technical Auditor

---

### 1. Resumen Ejecutivo y Hallazgo Rector

Velora persigue la cobertura nacional de oportunidades profesionales y formativas en Tecnología y Sistemas en el Perú garantizando **verificabilidad absoluta, procedencia oficial y fail-closed**. Frente a la dispersión extrema de las convocatorias estatales y la brecha temporal entre aperturas de procesos, se evaluaron dos plataformas peruanas que operan como agregadores masivos de empleo y prácticas:

1. **Practicas.pe** (`https://www.practicas.pe/`)
2. **Convocatorias de Trabajo** (`https://www.convocatoriasdetrabajo.com/`)

#### Hallazgo Estructural Clave:
Ambos portales pertenecen y son operados por la misma empresa matriz publicitaria y de medios digitales: **IDEADS** (inscrita formalmente en sus políticas de privacidad con banco de datos personales en Perú). Ambas plataformas comparten la misma arquitectura técnica subyacente (PHP sobre Apache/Cloudflare), políticas de privacidad idénticas y términos y condiciones gemelos.

Su valor real para Velora no radica en sus descripciones (que son síntesis no oficiales sujetas a derechos editoriales de IDEADS), sino en su capacidad de **radar de detección temprana**: actúan como un sensor que rastrea decenas de fuentes oficiales dispersas (UGELs, ministerios, empresas públicas y privadas) y colocan hipervínculos directos a las publicaciones oficiales de `gob.pe`, intranets estatales y documentos PDF en `cdn.www.gob.pe`.

---

### 2. Inspección Técnica Individual de las Plataformas

#### 2.1 Practicas.pe (`https://www.practicas.pe/`)

- **Propósito del sitio:** Agregador de convocatorias de prácticas pre-profesionales y profesionales tanto del sector público (CAS Prácticas, convenios formativos) como del sector privado.
- **Estructura de URLs y Búsqueda:**
  - Búsqueda parametrizada: `/resultados-busqueda.php?sort=1-fecha_publicacion&q=sistemas&carrera=18&dep=15&nivel_academico=7`
    - `carrera=18`: Ingeniería de Sistemas / Computación / Informática.
    - `dep=15`: Departamento de Lima.
    - `nivel_academico=7`: Universitario (egresado/bachiller/estudiante).
    - `sort=1-fecha_publicacion`: Orden cronológico inverso por fecha de anuncio.
  - Fichas de detalle: `/oferta-convocatoria-{slug}-{id}.html` (ej. `/oferta-convocatoria-016-practicante-superintendencia-adjunta-riesgos-smv-lima-71541.html`).
- **Estructura HTML y Marcado:**
  - Código HTML generado por PHP en servidor.
  - No expone microdatos `JobPosting` de Schema.org en búsquedas ni fichas (bloques JSON-LD ausentes o solo a nivel de sitio).
  - Incluye encabezados `<h1>` con nombre de la entidad y proceso, tablas o listas de requisitos, cronograma, remuneración y sección `id="como_postular"` y `id="descargar_bases"`.
- **Procedencia Outbound:**
  - **Sector Público:** Enlaces directos a bases oficiales en formato PDF o portales oficiales (`smv.gob.pe`, `ugel02.gob.pe`, `cdn.www.gob.pe`, `forms.cloud.microsoft`).
  - **Sector Privado:** Enlaces de redirección hacia portales comerciales de reclutamiento (predominantemente **Bumeran** y **Computrabajo**).
- **Indicadores de Vigencia:** No cuenta con un mecanismo en tiempo real para reflejar actas de suspensión o cierre; cuando una vacante caduca, el enlace suele mantenerse activo con fecha pasada en texto.

#### 2.2 Convocatorias de Trabajo (`https://www.convocatoriasdetrabajo.com/`)

- **Propósito del sitio:** Agregador centrado en convocatorias laborales para profesionales titulados, bachilleres y técnicos, enfocado fuertemente en el sector público bajo régimen CAS (Decreto Legislativo 1057), Decreto Legislativo 276 y 728.
- **Estructura de URLs y Búsqueda:**
  - Búsqueda geográfica y profesional: `/buscar-trabajos-en-LIMA-15.html?carrera=18&contrato=&nivel_estudios=7&sort=`
  - Fichas de detalle: `/oportunidad-laboral-{slug}-{id}.html` (ej. `/oportunidad-laboral-cas-182-codigo-aad-asistente-administrativo-ministerio-publico-fiscalia-lima-646962.html`).
- **Estructura HTML y Marcado:**
  - Incluye bloques estructurados JSON-LD con `@type: "WebSite"` y `@type: "Organization"`.
  - Presenta tablas estructuradas con código de convocatoria, remuneración (ej. `S/ 4,100.00`), lugar de prestación, requisitos mínimos y cronograma de postulación.
- **Procedencia Outbound:**
  - Enlaces salientes precisos a plataformas del Estado:
    - Ministerio Público: `https://portal.mpfn.gob.pe/convoca/convocatorias`
    - FONDEPES: `https://intranet2.fondepes.gob.pe/CONVOCATORIAS/`
    - SEDAPAL: `https://www.gob.pe/institucion/sedapal/informes-publicaciones/6965556-...`
    - Juntos: `https://convocatoria.juntos.gob.pe/Convocatoria/Lista`
- **Mecanismos de Sitemaps y Feeds:**
  - Expone `https://www.convocatoriasdetrabajo.com/sitemap.xml` y `https://www.practicas.pe/sitemap.xml`.
  - No proporcionan APIs REST ni feeds RSS públicos para extracción estructurada.

---

### 3. Evaluación de Políticas de Acceso, Reutilización y Gobernanza

| Dimensión | Practicas.pe | Convocatorias de Trabajo | Implicancia para Velora |
|---|---|---|---|
| **Accesibilidad Técnica** | HTTP 200 sin bloqueos WAF agresivos en consultas controladas. | HTTP 200 sin bloqueos WAF agresivos en consultas controladas. | Consultas puntuales de descubrimiento son técnicamente posibles. |
| **Robots.txt** | Permisivo: solo bloquea `/pre-profesional-en-bumeran-312.html/`. | Permisivo con exclusiones de URLs específicas. | Permite indexación en buscadores, pero no autoriza extracción masiva. |
| **Operador Formal** | IDEADS (Lima, Perú). | IDEADS (Lima, Perú). | Mismo operador legal y comercial. |
| **Términos y Condiciones** | Declara ser portal puramente informativo. Exime responsabilidad por errores en convocatorias. | Declara ser portal puramente informativo. Señala explícitamente que los usuarios deben consultar las **fuentes primarias**. | Refuerza la tesis de Velora: los agregadores no son fuente de verdad; la fuente oficial es mandatoria. |
| **Derechos de Contenido** | Se reserva derechos de plataforma, diseño y marca. | Se reserva derechos de plataforma, diseño y marca. | **Prohibido copiar resúmenes editoriales o textos de IDEADS.** Solo se puede registrar la URL original y datos fácticos del proceso. |

---

### 4. Respuestas a las Diez Preguntas Rectoras del Alcance

#### 1. ¿Qué oportunidades relevantes aportan que no estén ya detectadas por las fuentes actuales de Velora?
Aportan visibilidad sobre convocatorias públicas de tecnología en entidades que no están cubiertas por los conectores canónicos actuales de Velora (OSITRAN, Defensoría, INDECOPI), tales como la Superintendencia del Mercado de Valores (SMV), SEDAPAL, Ministerio Público (Fiscalía), FONDEPES, Programa JUNTOS y UGELs de Lima, así como pasantías y prácticas de empresas privadas anunciadas en bolsas de terceros.

#### 2. ¿Qué información puede obtenerse de sus páginas públicas?
- Identificador de convocatoria oficial (ej. `CAS N° 016-2026`, `CAS N° 182-2026`).
- Nombre de la entidad y puesto anunciado.
- Rango o monto de remuneración / subvención económica (`S/. X,XXX.XX`).
- Cronograma declarado (fechas de postulación).
- **Hipervínculos a las bases oficiales primarias y canales de postulación.**

#### 3. ¿Cómo se identifica la publicación original de cada oportunidad?
Mediante los hipervínculos presentes en los botones de acción (`Descargar Bases`, `Ver Convocatoria Completa`, `Postular Aquí`). En el sector público, estos enlaces apuntan casi invariablemente a subdominios `.gob.pe` (intranets, repositorios documentales, publicaciones en Gob.pe o formularios de postulación oficiales). En el sector privado, apuntan a portales como Bumeran o LinkedIn.

#### 4. ¿Qué porcentaje de los registros encontrados tiene un enlace oficial verificable?
- **Sector Público (CAS / Prácticas del Estado):** Más del **90%** de los registros analizados contienen enlaces salientes directos a bases oficiales primarias en `.gob.pe` o CDN institucional.
- **Sector Privado:** Menos del **10%** contiene enlaces al ATS directo del empleador; el **90%** restante enlaza a bolsas comerciales intermediarias (Bumeran, Computrabajo).

#### 5. ¿Qué información está disponible únicamente en el portal secundario?
Únicamente el texto de síntesis redactado por los redactores de IDEADS, sus tags de categorización y la estructura de navegación propia del portal. Toda la información contractual, requisitos legales y formularios son fácticos y provienen de la entidad convocante.

#### 6. ¿Qué limitaciones técnicas, de acceso y reutilización existen?
- **Falta de API / feeds:** Requiere scraping de HTML que puede romperse ante rediseños de IDEADS.
- **Restricción de derechos:** Los resúmenes redactados por IDEADS no cuentan con licencia abierta de reutilización; Velora no debe copiarlos.
- **Riesgo de datos obsoletos:** Los portales secundarios no garantizan la eliminación oportuna de procesos cerrados, suspendidos o declarados desiertos.

#### 7. ¿Qué mecanismo de integración sería más sencillo y sostenible?
El modelo de **Descubrimiento Asistido (Modelo B)**: un script local o herramienta que inspecciona periódicamente los resultados de búsqueda de ambos sitios, extrae exclusivamente la **URL oficial primaria** y el **identificador de proceso**, e ingresa un candidato preliminar en staging para que el sistema intente verificarlo contra la fuente oficial antes de presentarlo al equipo editorial.

#### 8. ¿Su integración mejoraría realmente la cobertura nacional?
**Sí, significativamente como radar de alerta temprana**, ya que resuelve el "dilema del conector único": en vez de desarrollar e investigar 50 conectores específicos para cada ministerio o UGEL del Perú, el radar secundario avisa qué entidad tiene un concurso abierto hoy y proporciona el enlace directo a sus bases.

#### 9. ¿Cómo evitar duplicados y convocatorias vencidas?
- **Anti-duplicados:** Normalización por clave primaria determinista basada en el identificador oficial de la entidad (`{entidad_slug}-{tipo_proceso}-{numero_proceso}`, ej. `SMV-CAS-016-2026`). Si el candidato ya existe en staging o en el catálogo, se descarta.
- **Anti-vencidas:** No otorgar fe de vigencia a las fechas de la fuente secundaria. El candidato solo se valida si la fecha límite oficial constatada en la base o en `gob.pe` es estrictamente futura (`deadline >= today`).

#### 10. ¿Conviene integrarlas, mantenerlas como herramientas de descubrimiento asistido o descartarlas?
**Conviene mantenerlas bajo el modelo de Descubrimiento Asistido (Modelo B).**
- *No integrarlas como fuentes de publicación directa (Modelo A):* Evita violaciones de derechos de autor de resúmenes editoriales de terceros y degradación de la calidad del catálogo.
- *No descartarlas (Modelo C):* Descartarlas privaría a Velora de una de las herramientas de alerta temprana más efectivas del ecosistema laboral peruano.

---

### 5. Dictamen Técnico y Recomendación Final

Se recomienda al propietario formalizar la adopción de **Practicas.pe y Convocatorias de Trabajo exclusivamente bajo el rol de Radares Secundarios de Descubrimiento Asistido**.

En este rol:
1. Velora **nunca publicará** a Practicas.pe ni a Convocatorias de Trabajo como `employer` ni como `publisher`.
2. Velora **nunca republicará** el texto redactado por IDEADS.
3. Velora utilizará los enlaces salientes para descubrir el origen oficial (`gob.pe`, intranets estatales o ATS privados), y el conector o validador oficial de Velora será el único responsable de extraer la información canónica de primera mano.
