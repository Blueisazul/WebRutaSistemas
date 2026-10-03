# Informe de investigación: mercado, fuentes y alcance del MVP

**Proyecto:** Plataforma de oportunidades y carrera para Sistemas  
**Ámbito inicial:** Perú y vacantes remotas que admitan postulantes desde Perú  
**Fecha de revisión:** 3 de octubre de 2026  
**Estado:** investigación de escritorio; antes de automatizar o republicar datos hay que confirmar las condiciones de cada fuente y, cuando corresponda, solicitar permiso.

## 1. Resumen ejecutivo

La oportunidad de producto no es reemplazar a LinkedIn, Computrabajo o las páginas de empleo de las empresas. Es resolver una parte que esos servicios no presentan de manera uniforme: **si una vacante sigue realmente abierta, qué tipo de trabajo ofrece para una persona de Sistemas, qué condiciones constan en la fuente y cuáles son sus riesgos o vacíos**.

La ruta más prudente para un primer catálogo es combinar:

1. **Fuentes oficiales peruanas** (páginas de empresas y entidades públicas) para comprobar convocatorias y bases.
2. **Portales ATS oficiales** (por ejemplo, Greenhouse y Lever) únicamente cuando una empresa publique allí sus vacantes y los términos de acceso sean adecuados.
3. **Agregadores y bolsas universitarias** para descubrir posibles oportunidades, no para confirmar vigencia o atribuir una vacante al empleador sin evidencia.
4. Una revisión manual inicial y un enlace directo a la publicación donde se postula.

No recomiendo prometer “buen futuro”, seguridad laboral ni ascensos. El producto puede mostrar señales observables: responsabilidades, tecnologías, duración, contrato, beneficios, formación declarada, salario publicado, alcance remoto y vacantes posteriores relacionadas.

## 2. Qué ofrecen las plataformas existentes y dónde queda espacio

| Plataforma / grupo | Utilidad para el usuario | Límite frente al objetivo del proyecto | Uso recomendado en el MVP |
|---|---|---|---|
| LinkedIn | Descubrimiento amplio, búsqueda y alertas; perfiles y red profesional | No garantiza que la oferta siga abierta ni evalúa continuidad o calidad del puesto. Sus términos prohíben scraping/copia automatizada y redistribuir contenido sin consentimiento. | Enlace y descubrimiento manual. No usar como fuente automatizada sin acuerdo explícito. |
| Indeed | Búsqueda general y agregación de avisos | La presencia en el portal no sustituye la comprobación en el empleador. Sus términos prohíben rastrear, extraer, reproducir o revender contenido salvo autorización aplicable. | Descubrimiento manual; no copiar anuncios ni automatizar el sitio por defecto. |
| Computrabajo | Cobertura local amplia, alertas, filtros y postulación | El volumen favorece cobertura, pero no resuelve por sí solo deduplicación, fuente original, temporalidad o ajuste técnico para Sistemas. | Canal de descubrimiento; guardar URL y buscar corroboración oficial antes de publicar como verificada. |
| Bumeran | Cobertura general en Perú y herramientas de postulación/seguimiento | Igual que otros agregadores: el anuncio no siempre acredita por sí mismo que siga activo o que el vínculo con el empleador sea directo. | Descubrimiento manual y enlace, sujeto a sus términos. |
| Get on Board | Especialización en tecnología y startups; en varias fichas muestra modalidad, países elegibles y salario si se publica | Sigue siendo necesario evaluar seniority, elegibilidad geográfica, contrato y vigencia. Puede ser la única página de postulación conocida. | Fuente secundaria especializada; distinguir “anuncio alojado allí por el empleador” de “portal corporativo propio”. |
| Bolsas universitarias | Descubren prácticas y acercan convocatorias a estudiantes | Una ficha universitaria puede copiar o resumir el aviso y quedar desactualizada; comprobar formulario y empleador original. | Descubrimiento, nunca única evidencia para marcar activa verificada. |
| Talento Perú / SERVIR y portales de entidades | Convocatorias públicas, bases, cronogramas y resultados | La página de índice y los avisos secundarios pueden discrepar; hay que leer cronograma, fe de erratas y resultados. | Fuente primaria para convocatorias públicas cuando conduce a bases y postulación oficial. |
| Portales corporativos y ATS del empleador | Mejor evidencia disponible de la vacante y su formulario de aplicación | La publicación puede desaparecer o estar cerrada; sistemas distintos no comparten un catálogo universal. | Fuente primaria preferida; revisar la vacante individual y el enlace de postulación. |

La diferenciación defendible es una **capa de evidencia y lectura profesional**, no una lista más grande: separar empresa de puesto, etiquetar modalidad y seniority con evidencia, mostrar lo no informado, identificar sustitución/temporalidad y mantener visible la fuente original.

## 3. Fuentes: factibilidad técnica y límites observados

### Fuentes oficiales y ATS

| Fuente | Qué se encontró | Decisión inicial |
|---|---|---|
| OSITRAN | Portal oficial de oportunidades y bases en PDF con funciones, requisitos, subvención, fechas, modalidad y término del convenio. | Muy buen caso de referencia para prácticas públicas y extracción de documentos. Registrar fecha y reglas de renovación tal como están escritas. |
| MEF / ConvoMEF | Índice oficial que etiqueta procesos como vigentes y enlaza procesos para prácticas. | Revisar el cronograma y sistema de postulación por convocatoria. No confiar ciegamente en el estado del índice. |
| Banco de la Nación | Portal oficial publica concursos, bases y resultados. | Útil para vacantes laborales; cualquier ficha de práctica hallada en otra bolsa requiere comprobación directa antes de considerarse oficial. |
| Scotiabank | Portal de empleo corporativo con una vacante individual reciente de práctica y página institucional de carreras tecnológicas. | Excelente fuente para contrastar nivel, tareas y ruta profesional; la página individual y el listado general pueden discrepar. |
| Greenhouse Job Board API | Documentación oficial: vacantes públicas consultables por GET sin autenticación; expone título, URL, ubicación y, con `content=true`, descripción. | Candidato a conector de bajo esfuerzo por empresa. La documentación habilita acceso técnico a datos públicos, pero no debe interpretarse por sí sola como licencia general para almacenar/republicar descripciones. Revisar términos y pedir permiso si el uso no está claro. |
| Lever Postings API | Documentación pública para obtener vacantes publicadas por empleador. Aclara límites, entre ellos que la API no hace búsqueda global de empleos y que las vacantes publicadas son visibles públicamente. | Candidato a conector por empresa; conservar enlace del portal Lever para postulación. Aclarar derechos de almacenamiento y republicación antes de escalar. |
| Ashby | Documentación de API para crear páginas de carrera y listar vacantes abiertas; también ofrece feeds de empleos para socios. | Priorizar un feed de socio cuando se quiera cobertura sostenida. No asumir que una API documentada concede a terceros licencia ilimitada. |
| Workday y otros portales | No se identificó en esta revisión una interfaz pública uniforme aplicable a todas las empresas; cada instancia cambia. | Tratar caso por caso. Preferir feed, API o permiso; manual mientras no exista una vía estable y permitida. |

### Agregadores y condiciones de acceso

- **LinkedIn:** el acuerdo de usuario prohíbe desarrollar o usar robots, scripts o procesos para extraer/copiar el servicio y también restringe copiar o distribuir información sin consentimiento del titular. Debe quedar fuera del scraping del MVP, salvo autorización escrita o integración oficial aprobada.
- **Indeed:** los términos vigentes prohíben rastrear, extraer, reproducir, duplicar, copiar, vender o revender partes del sitio, con excepciones sujetas a sus propias interfaces y acuerdos. No automatizar el portal por defecto.
- **Computrabajo, Bumeran, Get on Board y bolsas universitarias:** que la web sea visible no equivale a permiso para hacer scraping o republicar su contenido. Para cada uno habrá que revisar términos, robots.txt, APIs/feeds disponibles, límites y atribución. Hasta entonces, uso manual para descubrir y enlaces, sin copiar textos completos.

**Importante:** este informe registra una evaluación de producto y técnica, no una opinión legal. Un endpoint público facilita el acceso, pero no responde automáticamente cuánto tiempo se pueden guardar los datos, si se puede redistribuir el texto, qué atribución se exige ni qué cambios contractuales aplican. Esas preguntas deben resolverse fuente por fuente antes de un colector persistente.

## 4. Muestra de vacantes y lo que enseña

| Caso | Evidencia observada | Lectura para el producto |
|---|---|---|
| OSITRAN CP 029-2026, práctica profesional TI | Portal y bases oficiales; 3 vacantes; S/ 1,530 mensual; fecha de inscripción 13/10/2026; tareas de análisis, desarrollo, documentación y pruebas; convenio al 31/12/2026, renovable según necesidades y presupuesto; modalidad presencial y/o teletrabajo según área. | Alta relevancia técnica y condiciones mejor documentadas que muchos anuncios, pero temporalidad explícita y modalidad ambigua. No presentar como empleo estable. |
| Scotiabank, práctica preprofesional en gestión comercial de banca privada | Portal corporativo; publicada 25/09/2026; desde séptimo ciclo y admite Sistemas; SQL intermedio, Power BI y tableros; tareas de análisis, calidad de datos y automatización; convenio de prácticas. No declara salario ni modalidad en la ficha. | Buena experiencia para una ruta de datos/BI en finanzas, no necesariamente para desarrollo de software. La ficha ofrece postulación, mientras el índice de “estudiantes y recién graduados” mostraba cero vacantes: registrar conflicto de estado y volver a comprobar. |
| MEF convocatoria 55-2026, práctica profesional de Sistemas/Software/Estadística | Índice oficial muestra “vigente”; varias fuentes secundarias reportaron fecha límite 1/10/2026, ya pasada al revisar el 3/10/2026. | Caso de prueba para no aceptar etiqueta de estado aislada. Mantener “vigencia en conflicto / requiere cronograma oficial” hasta resolver; no recomendar postular como activa. |
| Banco de la Nación, ficha de práctica en bolsa universitaria | La bolsa universitaria mostró un anuncio de sistemas bancarios con tecnologías y funciones técnicas; en esta revisión no se confirmó una publicación equivalente vigente en el canal oficial. | Solo candidato de descubrimiento. Estado “fuente secundaria, pendiente de verificación”; no promocionar como vacante oficial comprobada. |
| 42Labs, puestos mobile remoto | Get on Board mostró publicaciones recientes y elegibilidad para Perú, Chile y Colombia; una fuente corporativa separada no fue localizada durante esa revisión. | Útiles como muestra remota internacional, pero registrarlas como verificadas en el canal de postulación, no como corroboradas en portal corporativo independiente. |

La muestra confirma que “buena empresa” no basta. La evaluación debe ser específica para el trabajo y el perfil profesional buscado.

## 5. Prioridad de empresas y sectores

### Prioridad para cobertura inicial

1. **Banca/finanzas y seguros:** bancos grandes y fintech; oportunidades diversas en desarrollo, datos, ciberseguridad, infraestructura y operaciones digitales. Filtrar con rigor los puestos de operaciones que solo acepten la carrera pero no brinden experiencia técnica.
2. **Tecnología y consultoría tecnológica:** software, nube, ciberseguridad, datos y desarrollo de producto. Más probabilidad de encontrar modalidad remota y stacks visibles; revisar con especial atención duración, país elegible y seniority real.
3. **Telecomunicaciones y retail de escala:** sistemas centrales, infraestructura, datos, comercio digital, seguridad y plataformas internas.
4. **Energía y minería:** menos volumen, pero potencial de proyectos complejos y sistemas industriales, infraestructura, datos y ciberseguridad; clasificar ubicación/turnos con cuidado.
5. **Sector público:** bases y condiciones suelen ofrecer evidencia estructurada y remuneración explícita, pero muchas oportunidades son prácticas o contratos de plazo definido. Importante para cobertura y comparación honesta, no indicador automático de estabilidad.

### Cómo hablar de reputación

No construir un ranking “mejor empresa” sin definir fuente, fecha y metodología. Para cada empresa, mostrar atributos verificables —programa de talento, beneficios declarados, formación, movilidad profesional, tecnologías/áreas, política publicada— y, si luego se agrega una valoración externa, indicar su metodología y año. Reputación corporativa nunca debe elevar por sí sola la calidad de una vacante.

## 6. Protocolo de verificación propuesto

1. **Descubrimiento:** guardar URL, fecha de hallazgo, título y plataforma de origen.
2. **Identidad:** enlazar empleador y dominio oficial; comprobar que el portal/formulario pertenece al empleador o a un proveedor ATS identificado por este.
3. **Vacante individual:** revisar título, ubicación/países permitidos, modalidad, requisitos, contrato, remuneración, fecha y texto de postulación.
4. **Vigencia:** intentar abrir la vacante y su formulario; distinguir entre activa, cerrada, vencida, retirada y no comprobable. Si solo el buscador/índice dice “vigente”, dejarlo en conflicto.
5. **Duplicados:** comparar empleador, título normalizado, ubicación, requisición, descripción/tecnologías y URL. Mantener IDs de todas las apariciones y elegir la oficial como registro principal.
6. **Temporalidad y reemplazo:** buscar en anuncio y bases términos como suplencia, reemplazo, necesidad temporal, proyecto, plazo, convenio o fecha de término. Mostrar la frase/evidencia; no inferir permanencia.
7. **Revisión periódica:** inicialmente revisar vacantes destacadas cada 48–72 horas y al momento del clic; después ajustar la frecuencia según tasa de cierres y capacidad operativa. Esta frecuencia es una hipótesis que el piloto debe medir, no una garantía.
8. **Trazabilidad:** guardar fecha/hora, URL consultada, resultado y campos modificados. Si falla el conector, degradar a “última verificación vencida / no comprobable”, no dejar activo indefinidamente.

### Estados que conviene usar

- **Activa verificada en fuente de postulación**
- **Activa verificada en fuente oficial del empleador**
- **En conflicto** (página individual, índice o plazo discrepan)
- **No verificada** (solo agregador o fuente secundaria)
- **Cerrada / vencida**
- **Retirada / ya no encontrada**
- **Verificación atrasada**

Evitar el único estado “activa” porque oculta qué se comprobó.

## 7. MVP recomendado

### Esencial

- Catálogo pequeño y curado, centrado en Sistemas, estudiantes, egresados y junior.
- Filtros por práctica pre/profesional, trainee, junior y puesto profesional; sector; familia técnica; región; elegibilidad remota; presencial/híbrido/remoto; salario publicado; experiencia.
- Ficha con tareas, requisitos, tecnologías, salario y moneda, beneficios, modalidad, lugar/países permitidos, tipo y duración de contrato, fechas y URL de postulación.
- Separación entre **calidad de empresa** y **encaje/calidad del puesto**.
- Señales y riesgos con evidencia y campos desconocidos visibles.
- Estado de verificación, fuente y fecha/hora de última revisión.
- Enlace directo para postular; no crear formulario de candidatura propio.
- Registro interno de procedencia y deduplicación por URL, requisición y similitud.

### Importante, después de validar el piloto

- Filtros guardados y alertas de nuevas vacantes.
- Página de empresas con señales y fuentes fechadas.
- Métricas de frescura, duplicados, datos ausentes y errores de clasificación.
- Conectores de ATS por empresa, después de revisar permisos y comportamiento.

### Fuera del MVP

Perfiles/CV, carga de documentos, recomendaciones personalizadas, aplicación automática, ranking único opaco, scraping masivo de agregadores y rutas profesionales completas.

## 8. Evaluación transparente en lugar de puntaje opaco

Para la primera versión recomiendo **no publicar una nota total de 0–100**. Mostrar evidencia por dimensión:

| Dimensión | Señales observables |
|---|---|
| Compensación | Monto publicado, moneda, periodo, beneficios económicos; si falta, “no indicado”. |
| Encaje técnico | Tareas, tecnologías, profundidad de responsabilidad y vínculo con la ruta seleccionada. |
| Continuidad | Tipo de contrato, duración, fin declarado, renovación condicionada, suplencia/reemplazo y programa formativo. No inferir retención si no hay dato. |
| Desarrollo | Formación, mentoría, rotaciones, movilidad, coaching o progresión descritos por fuente y alcance de esa evidencia. |
| Modalidad | Presencial, híbrida, remota, dirección y países permitidos. Distinguir modalidad fija de “según necesidad”. |
| Confianza del registro | Fuente, fecha de comprobación, coincidencia de empleador, consistencia de páginas y existencia de postulación. |

Una puntuación podría añadirse más adelante solo si usuarios entienden el método, se valida frente a casos reales y se puede explicar qué evidencia mueve cada dimensión.

## 9. Decisiones técnicas previas a programar

1. Empezar con captura curada/manual o automatización limitada a ATS y páginas que autoricen el uso. Mi recomendación: **piloto de 30–50 vacantes con curación manual**, suficiente para probar taxonomía, filtros y utilidad sin construir colectores frágiles.
2. Guardar metadatos mínimos, URLs y evidencia breve; no replicar la descripción completa salvo que las condiciones lo permitan.
3. No almacenar perfiles ni CV en el MVP; reduce exposición de datos personales y evita construir autenticación/permisos antes de que aporten valor.
4. Guardar auditoría de cambios y verificación; una vacante puede cambiar o cerrar después de la captura.
5. Mantener los conectores detrás de una interfaz por fuente para desactivarlos o sustituirlos si cambian términos, estructura o calidad.

## 10. Riesgos y preguntas que permanecen abiertas

- La autorización de reutilización de contenido no queda resuelta solo con documentación técnica pública. Revisar términos y, si hay duda, pedir permiso al proveedor/empleador.
- Algunas fuentes no exponen fecha de cierre o salario; el sistema debe conservar “desconocido”, no rellenarlo.
- Las páginas indexadas pueden retrasarse con respecto al estado real de la candidatura.
- Una empresa puede publicar funciones con valor técnico y, aun así, no tener conversión a empleo posterior; medirlo requerirá datos históricos o declaraciones de la empresa.
- “Remoto” puede estar limitado por país, zona horaria, idioma o relación contractual; registrar todos esos límites cuando estén disponibles.
- Reputación y beneficios promocionados por empleadores son declaraciones de empresa; atribuirlos y no presentarlos como verificación independiente.

## 11. Revisión de alternativas open source existentes

Se revisaron productos ATS y agregadores para evitar rehacer componentes ya resueltos.

| Proyecto | Qué ya hace | Encaje para nosotros | Decisión |
|---|---|---|---|
| [Freehire](https://github.com/strelov1/freehire) | Buscador/aggregador orientado a empleos de tecnología; API pública de lectura; normalización, deduplicación, filtros de país/modalidad/seniority/habilidades/salario y señal de vigencia (`fresh`, `stale`, `likely-evergreen`). El repositorio declara licencia MIT; su guía consultada reporta actividad alta y fuentes que incluyen Get on Board y WhatJobs Perú. | Es el candidato más cercano para **descubrir vacantes tech** y ahorrar trabajo de búsqueda/facetas. No reemplaza nuestra ficha curada: no garantiza que el anuncio continúe abierto, no controla el contenido, puede tener errores de geografía/clasificación y no cubre por sí solo las convocatorias públicas peruanas con bases, renovaciones y suplencias. | Probar como adaptador/fuente de descubrimiento; no como autoridad de vigencia ni como sistema de registro. Antes de guardar o republicar descripciones/datos, aclarar alcance de uso de API y derechos del contenido de terceros. Mostrar URL original y re-verificar cada oportunidad según nuestras reglas. |
| [Ever Jobs](https://github.com/ever-jobs/ever-jobs) | Agregador modular con más de 160 fuentes, APIs REST/GraphQL/CLI, deduplicación y normalización; MIT. | Cobertura amplia, pero documenta extracción por HTML/API/Playwright de fuentes que incluyen LinkedIn, Indeed y otros servicios cuyas condiciones restringen scraping. Un gran número de conectores no equivale a uso autorizado ni a confianza en cada fuente. | No usar como ingestor general. Solo considerar adaptadores cuyo acceso y reutilización se aprueben fuente por fuente. |
| [OpenCATS](https://www.opencats.org/) | ATS para reclutadores, empresas/agencias, candidatos, vacantes y procesos; puede publicar la página de empleos de quien opera el ATS. | Está hecho para que una organización gestione su contratación, no para consolidar y evaluar vacantes ajenas. Además incluiría datos de candidatos que nuestro MVP evita almacenar. | No encaja como base del catálogo. |
| [Frappe HRMS Job Portal](https://docs.frappe.io/hr/job-portal) | Portal de vacantes de una organización para buscar puestos que esta publica y recibir postulaciones. | Resuelve una página de carreras interna, no descubrimiento multifuente, trazabilidad de anuncios externos ni evaluación de riesgo. | No encaja como base del producto. |
| [Job Tailor](https://github.com/stevencrawford/job-tailor) | Agregador personal con IA, CV, recomendaciones y seguimiento, presentado como en desarrollo. | Está orientado al flujo individual y a perfiles/CV; varias capacidades enumeradas constan como en progreso. No es una base madura demostrada para nuestro catálogo institucional. | No adoptar en MVP. |

### Recomendación open source

**Conclusión preliminar, actualizada por la decisión de autonomía de la sección 13:** no construir desde cero el crawler ni depender de Freehire en runtime. Priorizar APIs del ATS y, cuando no existan, una biblioteca crawler autohospedada. Freehire fue estudiado como agregador candidato; su prueba breve solo sirve de referencia sobre cobertura, no lo convierte en proveedor.

La licencia MIT del código Freehire no concede por sí sola derechos sobre anuncios que pertenecen a empleadores o a otras bolsas. Sus términos aclaran que son publicaciones agregadas de terceros y que Freehire no garantiza que sigan abiertas. La prueba debe mantenerlas como **descubiertas / sin verificar**, seguir el enlace original y evitar copiar descripciones completas hasta aclarar derechos y atribución.

También hay una posible brecha de cobertura: la lista de fuentes de Freehire incluye Get on Board y WhatJobs para Perú, pero esta revisión no confirmó cantidad suficiente de prácticas preprofesionales/profesionales peruanas ni cobertura directa de bases del Estado. Esa cobertura se debe medir; no deducirla del volumen global.

## 12. Próxima etapa

La siguiente etapa es seleccionar un grupo pequeño de empleadores y revisar portal ATS, interfaz pública, condiciones de uso, robots y enlaces canónicos. El registro de fuentes está en `collector/sources.json`; los conectores no deben activarse hasta aprobar estas comprobaciones.

### Fuentes principales consultadas

- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [Indeed Terms of Service](https://www.indeed.com/legal?hl=en_US)
- [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html)
- [Lever Postings API](https://github.com/lever/postings-api)
- [Ashby: custom careers page API](https://developers.ashbyhq.com/docs/creating-a-custom-careers-page)
- [Get on Board: empleos seleccionados](https://www.getonbrd.com.pe/)
- [Computrabajo Perú](https://pe.computrabajo.com/)
- [Bumeran Perú](https://www.bumeran.com.pe/)
- [Scotiabank: vacantes para estudiantes y recién graduados](https://jobs.scotiabank.com/go/Empleos-para-estudiantes-y-reci%C3%A9n-graduados-1/2297517/)
- [Scotiabank: Practicante Pre Profesional](https://jobs.scotiabank.com/job/Lima-Practicante-Pre-Profesional-LIM-15047/606461817/)
- [Scotiabank: carreras en Tecnología](https://www.scotiabank.com/careers/es/carreras/tecnologia.html)
- [MEF: procesos de prácticas listados como vigentes](https://www.mef.gob.pe/convocas/procesos_practicas2026.php?estado=VIGENTES)
- [OSITRAN: oportunidades de prácticas](https://oportunidadlaboral.ositran.gob.pe/listadopract)
- [Empléate UPN: práctica de Sistemas Bancarios del Banco de la Nación](https://empleate.upn.edu.pe/trabajar-en-banco-de-la-nacion/trabajos/practicas-pre-profesional-de-ti-sistemas-bancarios/954094) (fuente secundaria; no confirmada como vigente en el portal oficial en esta revisión)
- [Freehire: API de consulta](https://freehire.me/docs/api)
- [Freehire: términos de servicio](https://freehire.me/terms)
- [Freehire: fuentes y cobertura declaradas](https://github.com/strelov1/freehire/blob/main/docs/sources.md)
- [Ever Jobs: repositorio y fuentes documentadas](https://github.com/ever-jobs/ever-jobs)

## 13. Decisión de autonomía tecnológica (3 de octubre de 2026)

### Conclusión

No conviene construir un motor de rastreo propio ni hacer que un agregador externo sea el proveedor permanente. Conviene **integrar primero las APIs públicas de portales ATS del empleador; para páginas permitidas que no expongan datos estructurados, usar Crawlee como librería en nuestro propio colector**. Mantener nuestros adaptadores de fuente, normalización, deduplicación, verificación, evaluación y evidencia como código propio.

El rastreo es un componente técnico reutilizable; la señal de carrera y la procedencia son la diferenciación del producto. No reimplementar colas, reintentos y control de concurrencia de un crawler maduro. Tampoco entregar la función del producto a una API SaaS externa.

| Opción | Licencia / ejecución | Mantenimiento, operación y encaje | Decisión |
|---|---|---|---|
| **Crawlee** | Apache-2.0; Node.js/TypeScript; se ejecuta dentro de nuestro servicio. `CheerioCrawler` hace HTTP/parsing para HTML estático y `PlaywrightCrawler` abre Chromium para páginas que necesiten JavaScript. | Buen equilibrio: colas, deduplicación de URLs, concurrencia y reintentos, sin tener que desplegar una plataforma central aparte. Playwright eleva consumo y complejidad; usarlo por fuente solo si hace falta. | **Elegido para integrar si se autorizan fuentes HTML.** Primero probar HTTP; navegador como excepción. |
| **Firecrawl self-hosted** | AGPL-3.0; API y workers propios. Su Compose actual levanta Playwright, Redis, RabbitMQ, PostgreSQL de cola y más componentes; la guía advierte que el despliegue base no resuelve por sí mismo auth completa, persistencia, copias o recuperación. | Da API uniforme de scrape/crawl/map, útil si varias aplicaciones necesitan el mismo servicio. Para una sola ingestión pequeña aumenta servicios y carga operativa. Las funciones de extracción con LLM no deben ser autoridad de datos fácticos. | **No usar como núcleo del MVP.** Reconsiderar si la organización valida una necesidad de servicio multiaplicación y acepta AGPL/operación. |
| **Crawl4AI** | Apache-2.0 con cláusula de atribución descrita por el proyecto; biblioteca o API propia con Chromium. | Adecuado para convertir páginas a Markdown/HTML orientado a LLM. Más específico que lo necesario para extraer algunos campos de vacantes; introduce énfasis y mantenimiento de extracción IA que no aportan valor frente a adaptadores deterministas. | No elegir como crawler principal; posible apoyo para analizar PDFs/páginas difíciles en una cola humana. |
| **Scrapy** | BSD-3-Clause; Python. | Alternativa madura para colectores HTTP estructurados. La capacidad de navegador/JavaScript exige complementos/servicios aparte y un runtime Python, así que duplica lenguajes respecto de la UI y el prototipo actual. | Elegir si se decide que todo el backend será Python; no ejecutar Scrapy y Crawlee a la vez sin una necesidad concreta. |
| **changedetection.io** | Autohospedado y con detectores HTML/Playwright. | Vigila si páginas específicas cambian; no normaliza vacantes, controla deduplicación ni decide cierre con evidencia estructurada. El repositorio contiene una discusión reciente sobre claridad de licencia para ciertos usos comerciales, por lo que habría que revisar licencia/condiciones exactas antes de adoptarlo. | No como pipeline central. Más adelante se puede evaluar para alertar a operadores sobre cambios en páginas de empleadores. |
| **Freehire / cualquier índice externo** | Servicio tercero; el código libre no licencia automáticamente anuncios del índice o de empleadores. | Útil como pista temporal de descubrimiento, pero añade latencia de proveedor, geografía imperfecta y derechos de republicación sin resolver. | No dependencia de ejecución; conservarlo solo como referencia de investigación. |

### Orden de ingestión por fuente

1. Exportación de un portal público de empleador: Job Board API de Greenhouse o Postings API de Lever cuando se identifique el portal del empleador. Ambas proporcionan datos estructurados para páginas de carreras. Su existencia **no confirma por sí sola** permiso para republicar esos datos fuera del sitio del empleador.
2. RSS/JSON/XML oficial, portal público o convocatoria oficial con metadatos mínimos.
3. Crawlee HTTP + parser específico si el permiso/condiciones se revisaron y la página lo permite.
4. Playwright solo para páginas que no funcionen con HTTP/HTML estático.
5. Revisión manual de PDF y portal público como vía de respaldo; dejar extracción automática para después de medir el volumen/variabilidad.

Las fuentes permanecen deshabilitadas en el registro hasta aprobar condiciones de uso, robots cuando aplique y uso previsto/republicación. No se saltarán login, CAPTCHA, límites, 403/429, controles anti-bot ni restricciones. Al encontrarse con un límite o bloqueo, el colector pausa y deja el caso en revisión.

### Arquitectura propia y portátil

```text
Fuentes ATS/API/feeds y páginas autorizadas
                 ↓
     Adaptador por conector / Crawlee
                 ↓
    cola local de ejecución y registro
                 ↓
   normalización + deduplicación propia
                 ↓
 bandeja de revisión + fuente/evidencia
                 ↓
 disponibilidad verificada + producto web
```

El contrato de adaptador no debe mencionar Firecrawl ni un proveedor concreto. Cada registro tiene endpoint/host, revisión de términos, robots, derechos, presupuesto de solicitudes, intervalo mínimo, límites de profundidad y regla de retención. Los rechazos fallan cerrados. Las APIs de ATS se mantienen separadas de la URL pública de cada anuncio. Persistir URL canónica, clave externa, timestamps y campos necesarios; guardar HTML/descripcion completa solo si está autorizado. Si se cambia de Crawlee, el contrato canónico y los conectores de ATS no cambian.

### Costos y escala

Crawlee es gratuito como software, pero el host, disco, ancho de banda, actualización de Chromium, monitoreo, backups y trabajo curatorial no son gratis. A bajo volumen, un worker único y solicitudes espaciadas cuestan menos y son más fáciles de mantener que un Firecrawl completo. Limitar trabajos por fuente, frecuencia baja, topes de memoria/tiempo, cache y alertas; escalar concurrencia solo cuando cobertura y latencia lo justifiquen. No necesitamos Redis/colas distribuidas antes de medir el piloto.

### Implementación realizada

- Se retiró la consulta de Freehire del frontend después de que la prueba de navegador no pudiera alcanzar la API; no inferimos que el servicio esté caído.
- Se añadió `collector/sources.json` con plantillas ATS y fuente manual deshabilitadas y requisitos de aprobación.
- Se implementó `collector/source-policy.mjs` con control fail-closed de fuentes aprobadas, HTTPS, allowlist exacta, redirects deshabilitados y límites de solicitudes; el normalizador conserva solo metadatos mínimos y deja publicación/verificación desconocidas.
- No se instaló ningún runtime desde Internet. El equipo local no tiene Docker disponible y la fuente legal/robots todavía está pendiente; Firecrawl no se desplegó.

### Siguiente paso

Seleccionar tres empleadores objetivo en sectores diferentes y comprobar para cada uno el tipo de portal, identificador/API, modalidad de vacantes, términos, robots y enlaces canónicos. No activar conectores hasta tener fichas de autorización y al menos un caso reproducible por conector. Después, incorporar Crawlee como dependencia del worker y ejecutar primero ingestión en modo vista previa, sin escritura directa al catálogo público.

### Fuentes primarias

- [Firecrawl: repositorio y licencia AGPL-3.0](https://github.com/firecrawl/firecrawl)
- [Firecrawl: guía oficial de autohospedado y servicios/riesgos operativos](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)
- [Firecrawl: configuración oficial Docker Compose](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)
- [Crawlee: licencia Apache 2.0](https://github.com/apify/crawlee/blob/master/LICENSE.md)
- [Crawlee: PlaywrightCrawler](https://github.com/apify/crawlee/blob/master/packages/playwright-crawler/README.md)
- [Crawlee: guía oficial, recomienda CheerioCrawler para sitios sin JavaScript](https://github.com/apify/crawlee/blob/master/website/versioned_docs/version-3.16/introduction/02-first-crawler.mdx)
- [Crawl4AI: repositorio, autohospedado y licencia/atribución](https://github.com/unclecode/crawl4ai)
- [Scrapy: repositorio BSD-3-Clause](https://github.com/scrapy/scrapy)
- [changedetection.io: repositorio oficial](https://github.com/dgtlmoon/changedetection.io)
- [Greenhouse: API Job Board pública](https://docs.greenhouse.io/job-board.html)
- [Lever: documentación Postings API y sus límites](https://github.com/lever/postings-api)

## 14. Actualización: presupuesto monetario cero (3 de octubre de 2026)

La condición de cero inversión **sustituye** la recomendación previa de Crawlee como herramienta inicial. No desplegar un crawler/servicio adicional hasta demostrar que hace falta. El MVP sirve el catálogo localmente con el runtime existente: Python estándar + SQLite/FTS5 + HTML/CSS/JS locales. Esto evita cuotas, proveedores, claves API y costos recurrentes. La base del producto, sus filtros y evidencia siguen bajo control propio.

| Alternativa | Licencia/costo directo | Carga operativa y control | Decisión |
|---|---|---|---|
| Python estándar + SQLite + FTS5 | Sin nueva instalación ni licencia de pago en el equipo existente. | Muy bajo para demo de solo lectura; el archivo es portable. SQLite no es solución automática para muchos escritores concurrentes o servicio multiusuario exigente. | **Elegido para piloto local.** No es hosting público. |
| Scrapy | Open source BSD-3. | Framework maduro HTTP para Python; aún requiere desplegar y mantener workers, límites y adaptadores. | Primera opción si una fuente HTML autorizada y el volumen lo justifican. |
| Crawlee | Apache 2.0, autohospedable. | Colas/reintentos y navegador, pero introduciría otro runtime antes del caso de uso. | No instalar en este MVP; reevaluar si fuentes lo requieren. |
| Firecrawl | AGPL-3.0, autohospedable. | API completa, varios procesos/servicios y carga de actualizaciones, datos y recuperación. El compose oficial ilustra componentes operativos. | No desplegar con presupuesto y escala actuales; reevaluar licencia y operación solo ante necesidad multiaplicación. |
| Freehire u otro agregador | Servicio separado del costo de su código open source. | Ayuda al descubrimiento, pero añade dependencia de un tercero y la licencia del software no transfiere derechos sobre sus anuncios. | No usar en tiempo de ejecución. Solo fuente de pistas para revisión. |

“Gratis” aquí significa software y cuotas nuevas en cero. La computadora, electricidad, conectividad, mantenimiento y tiempo de curación aún cuestan recursos. Esta versión escucha únicamente en la computadora anfitriona. Para hacerla pública hay que confirmar hardware/conectividad ya disponibles; un plan gratuito con límites o cambios no garantiza continuidad.

### Verificación de oportunidades

El catálogo distingue publicación, fuente y fecha revisada y enlaza el canal externo. La muestra actual es demostrativa. Una API ATS no prueba por sí sola autorización de republicación ni que la postulación seguirá abierta. La futura automatización debe conservar ID/URL canónica y fecha de captura, verificar en fuente oficial o canal vinculado por empleador, deduplicar por ID/URL normalizada, y no deducir cierre únicamente de que un anuncio desaparezca de una API. Si la fuente falla o hay conflicto, mostrar “verificación atrasada/en conflicto” y mandar a revisión. No guardar la descripción completa sin autorización.

### Cambios implementados

- Servidor/API local de solo lectura con búsqueda, filtros y SQLite inicializada desde una muestra versionable.
- Búsqueda FTS5 con alternativa integrada si esa extensión no existe.
- Enlace local protegido: bind loopback, archivos estáticos en allowlist, host check, sin endpoint de escritura, logs de términos o proveedores externos.
- Adaptadores Greenhouse/Lever en biblioteca estándar, apagados por política fail-closed y límites de tiempo, tamaño y host. No se han ejecutado contra Internet.
- Actualización de documentación y exclusión de archivos de base/cachés locales en Git.

### Fuentes técnicas primarias

- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- [SQLite serverless/zero-configuration](https://www.sqlite.org/zeroconf.html)
- [Scrapy y licencia BSD-3](https://github.com/scrapy/scrapy)
- [Crawlee y licencia Apache-2.0](https://github.com/apify/crawlee)
- [Firecrawl y licencia AGPL-3.0](https://github.com/firecrawl/firecrawl)
- [Firecrawl: guía oficial de autohospedado](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)
- [Firecrawl: compose oficial](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)

## 15. Programación de consultas con costo cero

La posibilidad de búsqueda semanal no requiere un servicio nuevo: después de autorizar y validar una fuente, se puede ejecutar un comando local desde el Programador de tareas de Windows. Esto conserva el host y los datos en el equipo existente y evita cuotas, APIs de cron o despliegues cloud. Tiene un límite claro: la tarea no se ejecuta mientras el equipo esté apagado (salvo la opción del Programador de reanudar una tarea pendiente), y no ofrece disponibilidad 24/7.

**Recomendación:** tarea semanal local para una lista de fuentes aprobadas y comando manual de previsualización durante el piloto. Posponer tanto el botón como la tarea hasta que al menos una fuente pase revisión y el conector se haya validado de forma manual. Un botón dentro de la interfaz pública expondría una capacidad de hacer solicitudes externas sin autenticación de operador; si se crea luego, que sea una consola local separada con permisos, CSRF, límites, estado y auditoría. Al no haber cuentas ni autenticación todavía, tampoco se debe añadir un endpoint web de ejecución.

La tarea programada leerá el registro fail-closed, no tomará URLs arbitrarias del usuario, no seguirá redirecciones ni hará crawling profundo, respetará límites de tasa, y guardará un registro local de ejecución. Una ejecución sin fuentes autorizadas debe salir sin realizar red y reportarlo explícitamente. Esta decisión no activa ahora ningún scraping ni crea una tarea OS.

## 16. Recomendación de arquitectura tras revisar el despliegue y cambio a Tailwind

El repo accesible está en `main` y la web está desplegada con GitHub Pages. Esa plataforma publicó bien HTML/CSS/JS, pero no ejecuta el backend Python incluido: la versión anterior llamaba `/api/opportunities` y mostraba que el catálogo no estaba disponible. Para resolverlo sin añadir servicios se cambió a un snapshot estático `data/opportunities.json`, cargado con URL relativa; los filtros se ejecutan en el navegador. `scripts/build_catalog.py` regenera el snapshot desde la semilla, pero no ingiere empleos. Esta corrección arregla la lectura en el despliegue, no la frescura del catálogo.

La tarea cron para Pages debe ser GitHub Actions semanal + ejecución manual, solo después de aprobar fuentes y completar el pipeline. El workflow toma datos de fuentes autorizadas, valida esquema/duplicados/estado, falla cerradamente y despliega un artifact Pages con JSON actualizado. GitHub indica que Actions estándar es gratis en repos públicos; el schedule puede retrasarse y se desactiva en un repositorio público tras 60 días sin actividad. No usar ahora el Programador de tareas de Windows como mecanismo de publicación remota: solo actualiza el equipo donde corre.

Se añadieron clases Tailwind para layout, filtros y tarjetas y se incluyó `@tailwindcss/browser` desde jsDelivr a pedido del usuario. `styles.css` todavía contiene una parte sustancial del diseño, y su migración completa queda pendiente. Tailwind restringe Play CDN a desarrollo; la salida recomendada es pinnear Tailwind CLI en el build de Pages, compilar utilidades y publicar CSS autocontenido. npm no pudo alcanzar su registry desde el entorno, así que no se generó ni verificó el bundle compilado en esta sesión.

La publicación cambiará cuando el usuario haga push de estos archivos; no se modificó GitHub ni se hizo push desde esta sesión.
