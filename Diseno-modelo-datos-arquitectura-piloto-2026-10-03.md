# Diseño preliminar: modelo de datos y arquitectura del piloto

**Proyecto:** Plataforma de oportunidades y carrera para Sistemas  
**Ámbito:** Perú + remoto elegible desde Perú  
**Estado:** diseño previo a implementación; parte de la investigación de mercado y fuentes del 3 de octubre de 2026.  
**Decisión rectora:** primero confianza y trazabilidad; después automatización y personalización.

## 1. Objetivo de esta etapa

Definir qué datos necesita el producto y cómo pasar de una vacante descubierta a una vacante publicada, verificada y evaluable. La arquitectura debe servir a un catálogo inicial curado de 30–50 oportunidades y permitir incorporar conectores autorizados más adelante, sin recopilar CV ni depender de scraping masivo.

## 2. Decisiones recomendadas

1. **Separar el estado de la convocatoria del estado de la verificación.** “Activa” y “la fuente es oficial” son preguntas distintas.
2. **Guardar evidencia por dato importante**, con URL, fecha y texto mínimo de apoyo; no guardar descripciones completas por defecto.
3. **No calcular una nota total en el MVP.** Mostrar dimensiones y señales explicables.
4. **No tener cuentas, CV ni postulaciones internas al inicio.** El usuario filtra oportunidades y sigue el enlace para postular en el sitio original.
5. **Comenzar con curación manual** sobre un pequeño conjunto de fuentes aprobadas. Probar primero cobertura, vigencia y utilidad antes de construir conectores.
6. **Usar un monolito modular con una base relacional administrada** si el piloto será usado por más personas que el equipo curador. Para una maqueta de validación visual podría generarse un catálogo estático; no convertiría la hoja de cálculo en la base de datos permanente.

## 3. Arquitectura de MVP

```text
FUENTES AUTORIZADAS / REVISIÓN MANUAL
                   │
                   ▼
        CAPTURA Y NORMALIZACIÓN
  validaciones + origen + fecha + evidencia
                   │
                   ▼
          REVISIÓN CURATORIAL
    identidad + duplicados + vigencia + riesgos
                   │
                   ▼
         BASE RELACIONAL ÚNICA
 organización / oportunidad / fuentes / eventos
                   │
             API de lectura
                   │
                   ▼
             WEB PÚBLICA
 buscador + filtros + ficha + enlace para postular
```

### Componentes

| Componente | MVP | Evolución posible |
|---|---|---|
| Interfaz web | Catálogo, filtros y detalle; adaptable a móvil y accesible por teclado. | Alertas, perfiles opcionales y rutas profesionales cuando haya evidencia y justificación. |
| API | Lectura de oportunidades publicables y facetas/filtros. | API interna de administración y conectores por fuente. |
| Curación | Formulario/hoja operativa o panel privado sencillo; publicación requiere revisión humana. | Pipeline por lotes para fuentes aprobadas, con cola de revisión y reintentos. |
| Persistencia | PostgreSQL administrado, con copias de seguridad y migraciones. | Sin necesidad de separar servicios mientras el volumen no lo justifique. |
| Extracción | Manual en el piloto; IA puede sugerir campos desde textos/PDFs, con referencias y aprobación humana. | Procesamiento asistido por lotes y control de calidad por fuente. |
| Observabilidad | Registro de fallos de importación, fecha de última verificación y errores visibles para curadores. | Métricas de frescura y confiabilidad por conector. |

No se recomienda empezar con microservicios, un buscador externo, perfiles personales, almacenamiento de documentos, scraping distribuido ni un recomendador de IA. Ninguno es necesario para validar si el catálogo confiable aporta valor.

## 4. Modelo de datos

### Entidades

```text
Organization 1 ─── * Opportunity
Opportunity 1 ─── * OpportunitySource * ─── 1 Source
Opportunity 1 ─── * VerificationEvent
Opportunity 1 ─── * Evidence
Opportunity * ─── * Skill / RoleFamily / Sector (catálogos)
```

Una oportunidad es la publicación de un proceso/puesto concreto. Una fuente es un portal o sistema de publicación. Una aparición en una bolsa universitaria y otra en la página del empleador apuntan a la misma oportunidad, pero no se sobrescriben: se conservan como procedencias distintas.

### `Organization`

| Campo | Regla |
|---|---|
| `id` | Identificador interno estable. |
| `display_name` | Nombre mostrado. |
| `canonical_domain` | Dominio corporativo cuando se verificó. |
| `sector_id` | Sector normalizado; permitir más de uno si el modelo lo exige. |
| `reputation_evidence` | Señales atribuibles con fecha/fuente, no un adjetivo sin sustento. |
| `created_at`, `updated_at` | Auditoría básica. |

No se necesita puntuar empresas en el primer corte. La reputación es contexto, no calidad automática de cada empleo.

### `Opportunity`

| Campo | Forma recomendada / regla |
|---|---|
| `id` | UUID interno. |
| `organization_id` | Relación con la organización; nullable solo si identidad aún está en revisión. |
| `title_original` | Título como aparece en la fuente principal. |
| `title_normalized` | Versión para deduplicación/búsqueda; no reemplaza el original. |
| `role_family` | Desarrollo, datos/BI, infraestructura/cloud, ciberseguridad, soporte, QA, producto/analítica u otro. |
| `career_level` | Práctica, trainee/graduate, junior, intermedio, senior, otro/no especificado. |
| `opportunity_type` | Práctica preprofesional, práctica profesional, trainee, empleo, contrato por proyecto, convocatoria pública u otro. |
| `work_mode` | Presencial, híbrido, remoto, flexible/según área o no especificado. No inferir de una dirección o del país. |
| `location_text` | Texto humano y ubicación estructurada (ciudad/región/país) si está disponible. |
| `eligible_countries` | Lista explícita para vacantes remotas; vacío significa “no indicado”, no “global”. |
| `salary_min`, `salary_max`, `salary_currency`, `salary_period` | Valores numéricos solo si la fuente los publica; conservar también `salary_raw`. No calcular valor neto ni conversión en la captura. |
| `contract_type`, `duration_text`, `end_date` | Separar plazo del tipo de contrato. Nulos cuando no consten. |
| `deadline_at`, `published_at` | Fechas verificadas y fuente de la fecha. Una fecha inferida de “hace dos días” debe guardar método/precisión. |
| `application_url` | Enlace directo de postulación observado. |
| `publication_status` | `open`, `closed`, `expired`, `withdrawn`, `unknown`. |
| `verification_status` | `employer_verified`, `application_channel_verified`, `secondary_only`, `conflict`, `unverified`, `stale`. |
| `last_checked_at` | Fecha/hora de última comprobación y zona horaria normalizada. |
| `continuity_signals` | Datos explícitos: término, renovación condicionada, suplencia, proyecto, programa trainee. Sin predicción categórica automática. |
| `benefits_text` | Resumen fiel de los beneficios declarados; evidencia asociada. |
| `summary_editorial` | Resumen escrito por el producto, separado del texto original y revisable. |
| `publicly_visible` | Solo publicar cuando los mínimos editoriales y de procedencia se cumplen. |
| `created_at`, `updated_at` | Auditoría. |

### `Source` y `OpportunitySource`

`Source` describe la entidad/plataforma: nombre, dominio, tipo (`employer_site`, `ats`, `government`, `aggregator`, `university`, `other`), condiciones revisadas, vía de acceso aprobada y fecha de revisión de términos.

`OpportunitySource` relaciona una oportunidad con cada URL que la menciona: URL exacta, fuente, tipo de relación (`official_posting`, `application_channel`, `discovery_copy`, `document_pdf`, `results_notice`), fecha de descubrimiento, fecha de última visita y resultado de verificación. Marcar un ATS como “oficial” solo si el empleador lo enlaza o se valida claramente esa relación.

### `Evidence`

| Campo | Uso |
|---|---|
| `id`, `opportunity_id` | Identificación y relación. |
| `field_key` | Campo respaldado: salario, fecha límite, modalidad, duración, tarea, beneficio, etc. |
| `source_url` | URL exacta del dato. |
| `quote_or_locator` | Fragmento mínimo o localizador (página/sección del PDF); limitar copia innecesaria. |
| `observed_at` | Momento de consulta. |
| `capture_method` | Manual, documento oficial, feed/API permitida u otro método autorizado. |
| `reviewer_status` | Pendiente, aprobado, rechazado. |

Campos centrales mostrados como hecho —especialmente pago, fecha, modalidad, contrato, requisitos y estado— requieren evidencia aceptada. Si el anuncio no los dice, mostrarlos como “No indicado”.

### `VerificationEvent`

Historial append-only: oportunidad, hora, URL revisada, método, resultado, cambio de estado, campos que cambiaron, error si lo hubo y responsable/proceso. Esto permite saber si una convocatoria cerró, desapareció o cambió condiciones sin borrar su historial.

### Taxonomías y campos libres

Usar catálogos pequeños y editables para sector, familia técnica, nivel y tipo de oportunidad. Guardar el texto original además del valor normalizado. Evitar vocabularios rígidos que eliminen términos nuevos; una categoría `other` con nota de revisión es preferible a adivinar.

## 5. Reglas de estado y publicación

El estado de vida y la confianza de fuente son dos ejes independientes:

| Estado de publicación | Estado de verificación | Qué mostrar |
|---|---|---|
| `open` | `employer_verified` | “Abierta; comprobada en el portal del empleador”. |
| `open` | `application_channel_verified` | “Abierta; postulación disponible en el canal indicado por el empleador”. |
| `unknown` | `secondary_only` | “No verificada; hallada en [fuente secundaria]”. |
| Cualquiera | `conflict` | “Estado en conflicto; revisar antes de postular”. No promocionar como activa verificada. |
| `expired` o `closed` | Cualquiera | Mostrar como cerrada solo si aporta valor histórico, con aviso claro y sin CTA de postulación activo. |
| `unknown` | `stale` | “Revisión atrasada”; no dejar aparecer en el filtro predeterminado de activas verificadas. |

### Mínimo para publicar como activa verificada

- Empleador identificado.
- Página individual o canal de postulación accesible.
- Elegibilidad para Perú comprobada cuando sea remota.
- Última revisión dentro del intervalo operativo acordado.
- Sin fecha límite ya vencida ni contradicción abierta.
- URL, fecha de revisión y evidencia registradas.

Una oferta que no cumpla lo anterior puede quedar en cola editorial o mostrarse como no verificada si aporta suficiente valor y el usuario entiende la limitación.

## 6. Deduplicación

1. Coincidencia exacta de ID/requisición oficial: alta confianza.
2. URL canónica o URL de postulación común: alta confianza, tras quitar parámetros de seguimiento.
3. Empleador + título normalizado + ubicación + familia/fecha: candidato a coincidencia.
4. Similitud del texto: genera sugerencia para revisión, nunca fusión automática en la primera versión.

Conservar IDs y URLs de apariciones secundarias. Cuando una empresa vuelva a abrir una vacante parecida, no reciclar el registro anterior como si fuera la misma requisición; verificar fechas/ID y crear nueva instancia vinculada si corresponde.

## 7. Extracción asistida por IA

La IA puede proponer título normalizado, habilidades, familia, nivel y resumen, pero el dato sugerido debe enlazar a la evidencia original y quedar marcado como pendiente. Para salario, modalidad, fechas, países habilitados y contrato, exigir pasaje textual/localizador revisable. Si no encuentra evidencia, deja el campo desconocido. La IA no decide por sí sola estado activo, legitimidad del empleador, continuidad ni ranking.

## 8. Interfaz del MVP

### Listado

- Buscador por puesto/empresa/tecnología.
- Filtros por tipo de oportunidad, nivel, familia técnica, sector, ubicación, modalidad y salario publicado.
- Filtro inicial predeterminado de activas con verificación reciente; opción para incluir no verificadas y cerradas.
- Tarjeta de oportunidad: título, empresa, familia, nivel, modalidad/ubicación, salario si publicado, fecha de comprobación y etiquetas de riesgo relevantes.

### Detalle

- Funciones, requisitos y tecnologías.
- Condiciones publicadas: subvención/salario, duración, contrato, beneficios y modalidad.
- “Qué puede aportarte”: lectura breve limitada a tareas/tecnologías declaradas, con nota si la interpretación es editorial.
- Continuidad: plazo, renovación, suplencia o “No indicado”, siempre con evidencia.
- Estado y trazabilidad: dónde y cuándo se verificó; fuente original y cualquier fuente secundaria útil.
- Botón para postular fuera de la plataforma.

### No incluir aún

Cuenta, perfil, carga CV, seguimiento de postulaciones, recomendación personalizada, chat, postulación automatizada, ranking global, rutas profesionales y app móvil.

## 9. Seguridad, privacidad y operación

- Sin cuenta y sin CV en el piloto. Evitar recopilar datos personales del visitante; no añadir analítica de terceros sin necesidad y revisión de privacidad.
- Todo texto importado se trata como no confiable: escapar HTML, no ejecutar contenido embebido, no construir tarjetas con `innerHTML` crudo.
- Limitar enlaces a URLs http/https permitidas; proteger contra redirecciones sospechosas e incluir dominio visible en el enlace externo.
- Si luego se crea un panel curatorial, autenticación restringida, roles mínimos, registro de cambios, variables secretas fuera del repositorio y protección contra CSRF/XSS/SQL injection según la tecnología.
- Copias automáticas de base de datos y prueba documentada de restauración antes de producción.
- No almacenar textos/documentos completos en el MVP si basta con metadatos, enlaces y extractos pequeños de evidencia.
- Si una fuente cae o cambia estructura, poner su flujo en error y marcar los registros afectados como atrasados; nunca conservar “verificada” indefinidamente.

## 10. Roadmap técnico

### Etapa A — cerrar especificación

- Aprobar estados, categorías, requisitos mínimos de publicación y antigüedad admitida.
- Definir quién mantiene el catálogo y con qué frecuencia.
- Validar con 10–15 fichas reales, incluyendo casos vencidos, duplicados, remotos con límite de país, suplencias y PDFs.

### Etapa B — prototipo de datos sin conectores

- Diseñar esquema de base y formulario de captura.
- Cargar una muestra curada de 30–50 oportunidades.
- Revisar falsos activos, salario ausente, modalidad ambigua, clasificación de familia y duplicados.

### Etapa C — web de lectura

- Buscador y filtros.
- Ficha con evidencia, estados separados y enlace externo.
- Accesibilidad, móvil y revisión de errores de navegación.

### Etapa D — operación piloto

- Métricas de frescura, cobertura, conflictos, duplicados y completitud.
- Revisar la frecuencia de comprobación a partir de cierres reales.
- Iniciar uno o dos conectores ATS solo si términos y permisos son aceptables y el piloto manual demuestra utilidad.

### Etapa E — crecimiento

- Alertas sin perfil sensible al principio (por correo opcional y consentimiento explícito).
- Perfiles y seguimiento únicamente si los usuarios lo piden y existe un plan de seguridad/privacidad.
- Rutas profesionales cuando haya suficientes datos longitudinales, no antes.

## 11. Criterios de éxito del piloto

Objetivos propuestos para probar, no garantías de resultado:

- Toda oportunidad publicada como activa tiene URL de fuente, fecha de verificación y fuente identificable.
- Ningún salario, beneficio, modalidad o plazo se presenta sin evidencia, o se etiqueta expresamente como no indicado.
- Las ofertas vencidas conocidas no aparecen en “activas verificadas”.
- Las coincidencias de duplicado se revisan antes de fusionar.
- Se puede distinguir claramente una práctica técnica de datos/BI, soporte o funciones no técnicas.
- Una persona del público objetivo puede filtrar y entender por qué una oportunidad aparece como conveniente, incierta o riesgosa.
- Las métricas de errores y datos ausentes se calculan sobre la muestra y se usan para ajustar fuentes/filtros antes de aumentar cobertura.

## 12. Decisiones que no bloquean la siguiente fase

Pueden quedar configurables hasta validar el piloto: colores de riesgo, orden inicial de filtros, si se incluye sueldo por hora, frecuencia de revisión exacta por fuente y si habrá alertas. Deben cerrarse antes de producción: términos permitidos por fuente, quién verifica, qué significa “activa verificada”, conservación/eliminación de datos y mecanismo de recuperación.

## 13. Recomendación final

Construir después un **monolito modular con PostgreSQL y una interfaz de lectura**, operado primero con registros curados manualmente. Para vacantes tecnológicas, probar Freehire como proveedor open source de descubrimiento mediante su API pública documentada; no reimplementar de entrada el rastreo de cientos de ATS que ya hace. Mantener nuestro propio registro canónico, revisión humana y evidencia: la licencia MIT del código no licencia los anuncios de terceros ni convierte la vigencia estimada en confirmación.

Esta recomendación inicial fue reemplazada por el prototipo estático registrado en la sección 16 y la decisión de autonomía de la sección 17.

## 14. Auditoría de la muestra existente (3 de octubre de 2026)

Al contrastar la hoja `Registro` con este modelo aparecieron ajustes de calidad que deben resolverse antes de tomarla como dato de prueba definitivo:

1. **“URL oficial” no describe el contenido de la columna.** En 42Labs y Launchpad contiene la publicación de Get on Board, no una URL del dominio corporativo. Renombrar a `URL principal / publicación` y guardar por separado URL del empleador, URL de postulación y documentos/evidencias.
2. **Se mezclan disponibilidad y procedencia.** OP-002, OP-003 y OP-004 están marcadas “Activa, verificada”, aunque la propia nota indica que se localizaron en Get on Board y no se encontró una ficha equivalente corporativa. Estado propuesto: disponibilidad observada como abierta en el canal listado, con verificación `secondary_only` mientras no se documente que el empleador enlaza o controla ese canal. No mostrarlas como “oficialmente verificadas”.
3. **La modalidad de OSITRAN no es simplemente “No especificado”.** Las bases señalan presencial y/o teletrabajo parcial o total de acuerdo con las necesidades del área. Codificar `flexible/según área` y explicar que el arreglo concreto no está indicado.
4. **La muestra no debe representar sólo ofertas aún postulables.** QA-001 es una convocatoria cerrada y sirve como caso negativo de prueba; identificarla como dato histórico de validación, fuera del catálogo de activas.
5. **El nombre de ciertos campos oculta incertidumbre.** `Salario publicado` debe aclarar si es subvención/salario, bruto/neto y periodo sólo cuando la fuente lo diga. `Fecha de publicación` puede faltar; no completarla con la fecha de captura.
6. **La evidencia se guarda actualmente en notas o en una columna de fuente secundaria.** Separar en filas/campos de evidencia por atributo, especialmente para plazo, sueldo, modo, tareas y países habilitados.

### Ajuste de nomenclatura recomendado

- `publication_status`: disponibilidad de la convocatoria (`open`, `closed`, `expired`, `withdrawn`, `unknown`).
- `verification_status`: procedencia/calidad de la comprobación (`employer_verified`, `employer_linked_ats`, `application_channel_observed`, `secondary_only`, `conflict`, `stale`, `unverified`).
- `temporary_signals`: plazo, suplencia/reemplazo, duración o renovación condicionada, cada uno con evidencia.

`application_channel_observed` significa que el formulario o botón funciona en el sitio que aloja la vacante; no prueba por sí solo que el empleador haya autorizado el uso de datos por nuestra plataforma. Esa es una comprobación de términos/procedencia separada.

### Resultado de la revisión

La estructura propuesta sí cubre los casos del piloto. En la hoja se corrigieron el encabezado que confundía URL principal con URL corporativa, los estados de las tres ofertas que solo constan en Get on Board y la modalidad flexible de OSITRAN; también se amplió la lista desplegable para esa modalidad. Las ofertas de 42Labs y Launchpad conservan en las notas que el anuncio/canal aparece disponible, pero ya no figuran como verificadas por el empleador.

La hoja piloto aún conserva un solo campo de estado editorial y no es la base final: cuando pasemos al esquema web, separar `publication_status` de `verification_status` y registrar evidencia por campo. La corrección evita los falsos “activa, verificada” actuales; no reemplaza ese trabajo de diseño.

## 15. Alternativa open source identificada: Freehire

La revisión de alternativas encontró [Freehire](https://github.com/strelov1/freehire), un agregador/buscador de vacantes técnicas con licencia MIT en el código, actividad intensa, API pública de consulta y fuentes declaradas para Get on Board y WhatJobs Perú. La API expone país, región, modalidad, nivel, categoría, salario, fuente y una señal de frescura/realidad, con límites de página y consulta documentados.

### Qué conviene integrar

- Consultar vacantes por país/área/modalidad/nivel como **entrada de descubrimiento**.
- Guardar, como mínimo, URL original, fuente que Freehire identifica, su ID/slug, fecha de captura y datos necesarios para revisión.
- Si la oportunidad existe en el canal original y está abierta, pasarla a revisión curatorial; recién entonces generar el registro público local.
- Dejar en nuestra ficha la URL de aplicación original y diferenciar “Freehire la encontró” de “empleador verificado”.

### Qué no sustituye

- Validación individual del empleador y disponibilidad de postulación.
- Evidencia de condiciones del convenio/contrato, suplencia, renovación, modalidad local o salario publicado.
- Cobertura de prácticas y convocatorias peruanas del Estado.
- Nuestra taxonomía profesional y lectura de riesgo de carrera.

### Condición para el prototipo

Freehire declara en sus términos que no controla la exactitud del contenido ni garantiza que la vacante siga abierta; además prohíbe evitar su API documentada o saltarse sus límites. Su documentación de API permite consultas públicas, pero el código MIT no determina las licencias de las publicaciones de empleadores/agregadores. Por ello, Freehire no queda conectado al prototipo ni se usa como proveedor runtime. Su API puede evaluarse como comparación de cobertura si aporta valor, pero cualquier uso mantiene resultados como no verificados y no permite guardar/republicar descripciones completas sin aclarar los derechos.

También se identificaron defectos públicos recientes en el propio proyecto relacionados con geografía/modo remoto, por lo que esos filtros deben revisarse manualmente durante la prueba. La integración debe estar detrás de una interfaz opcional, con degradación si el API falla o si sus términos/cobertura cambian.

El siguiente trabajo técnico vigente queda definido en la sección 17: revisar tres fuentes de empleador y solo después conectar una primera API/feed permitido.

## 16. Prototipo de interfaz — estado al 3 de octubre de 2026

Se implementó una primera interfaz estática de exploración en `index.html`, `styles.css` y `app.js`, con filtros locales, fichas detalladas con evidencia, muestra explícita de datos incompletos/temporales y consulta opcional a Freehire. No hay cuentas, CV, postulaciones, persistencia ni ingesta automática. La muestra es demostrativa y no debe confundirse con una oferta actualizada en producción.

La interfaz no solicita ni almacena datos personales. Eliminamos las fuentes tipográficas remotas para evitar una conexión de terceros al cargar. El botón de Freehire informa qué consulta enviaría y solo consulta tras una acción del visitante. En esta sesión el navegador devolvió `Failed to fetch`; los cuatro registros locales permanecieron disponibles. Esto solo confirma que la consulta desde este entorno falló, no que la API esté caída. Antes de decidir una integración proxy, conviene revisar CORS, disponibilidad desde otra red y límites publicados; si se añade servidor, mantener consulta de bajo volumen, control de errores y no persistir descripciones sin autorización.

La inspección manual del navegador confirmó el render del catálogo y la ficha OSITRAN (plazo, modalidad flexible, remuneración, evidencia, condiciones de renovación y enlaces oficiales). Aún no es el MVP desplegable: faltan cerrar derechos por fuente, política operativa de verificación, esquema persistente canónico y actualización automática.

## 17. Decisión técnica: autonomía y reutilización de open source

Esta sección actualiza la condición de prueba del apartado 15: la búsqueda de Freehire se retiró del frontend, por lo que no hay proveedor externo en tiempo de ejecución. Se conservará en investigación como opción de descubrimiento, no como dependencia.

No construir desde cero un crawler. Usar primero APIs/feed estructurados propios de cada portal y, cuando no existan y su uso esté permitido, integrar **Crawlee como librería dentro de un worker Node.js propio**. Elegir `CheerioCrawler`/HTTP para páginas estáticas y Playwright solo por necesidad de JavaScript. La biblioteca resuelve descarga, cola, reintentos, concurrencia y parsing; el producto mantiene propio el registro canónico, reglas de fuentes, normalización, deduplicación, verificación, evidencia, evaluación y publicación.

No desplegar Firecrawl como núcleo del MVP. Aunque es autohospedable, AGPL-3.0 y requiere operar varios servicios, incluidos navegador, API/workers, Redis, RabbitMQ y PostgreSQL de cola en la configuración documentada. Su guía también indica que el despliegue de partida requiere que el operador diseñe autenticación externa, persistencia, backups y recuperación. Puede ser apropiado si más adelante hay múltiples consumidores y se necesita una API uniforme de scrape/crawl/map; entonces revisar AGPL, seguridad y coste operativo antes de adoptarlo.

Crawl4AI es alternativa si necesitamos extracción HTML/Markdown para un proceso asistido, pero se orienta a flujos LLM y requiere atribución según sus términos Apache 2.0. Scrapy sería razonable si el backend pasa a Python; no mezclar ambos frameworks de rastreo en el MVP. changedetection.io puede vigilar cambios de unas páginas seleccionadas, no sustituye ingestión estructurada ni validación laboral; además, confirmar condiciones comerciales y licencia del commit elegido antes de una adopción productiva.

El registro y guardas iniciales están en `collector/`. Las APIs públicas de Greenhouse y Lever se mantienen como plantillas deshabilitadas: que el ATS publique una API para career sites no implica automáticamente derecho a operar un agregador externo. Requiere identificar cada empleador/portal, revisar términos y licencia/reutilización, respetar robots cuando aplique y delimitar el host. Se prefiere metadata + enlace; el texto completo/HTML no se retiene por defecto.

`authorizeFetch()` falla cerrado si la fuente está apagada, pendiente de términos/derechos, no es HTTPS, queda fuera del host exacto, excedió el presupuesto de consultas o requiere una redirección no autorizada. `publicRecordFromPosting()` no declara una oportunidad activa/verificada. Ningún conector está habilitado en este momento. En el equipo de desarrollo Node 22 está disponible, pero Docker no; no descargamos ni instalamos dependencias hasta elegir y autorizar fuentes.

La prueba CORS fallida con Freehire solo muestra que este entorno no pudo ejecutar esa llamada. No es evidencia de que Freehire esté caído. Aun así, para los objetivos de autonomía no hay necesidad de mantener la API tercera en la página; el prototipo funciona sin ella.

## 18. Revisión por presupuesto cero y primera API local (3 de octubre de 2026)

Esta decisión **reemplaza la propuesta de Crawlee como crawler inicial** de la sección 17. El proyecto no dispone de inversión para servidores ni para operar una plataforma con varios componentes. Por eso la versión ejecutable debe funcionar en el equipo ya disponible, sin paquetes adicionales.

### Elección

- **Servidor/API:** biblioteca estándar de Python. No se necesita framework web para este catálogo pequeño.
- **Persistencia y búsqueda:** SQLite incluido con Python, con FTS5 cuando esté disponible; búsqueda `LIKE` acotada como respaldo. SQLite es embebido/serverless y la biblioteca estándar de Python ofrece `sqlite3` ([documentación](https://docs.python.org/3/library/sqlite3.html)); FTS5 está descrito en [la documentación oficial](https://www.sqlite.org/fts5.html).
- **Interfaz:** HTML, CSS y JavaScript locales, sin CDN, fuentes externas ni llamadas runtime a terceros.
- **Ingesta hoy:** muestra curada y conectores mínimos de Greenhouse/Lever apagados. No se consulta ninguna fuente al abrir la web.
- **Ingesta futura:** APIs/feed autorizados primero; [Scrapy](https://github.com/scrapy/scrapy) (BSD-3) solo si encontramos volumen HTML permitido que lo justifique. Mantener una sola ruta tecnológica Python.

### Por qué no Firecrawl ni un crawler ahora

Firecrawl autohospedado reduce el desarrollo del rastreo, pero aumenta servicios, recursos, actualizaciones y labores operativas. Ese intercambio no compensa para un piloto sin presupuesto, cuyo riesgo principal es la autorización y fiabilidad de fuentes, no la velocidad de descarga. Crawlee es maduro, pero añadir Node.js/Playwright junto al backend Python duplicaría herramientas antes de que una fuente HTML autorizada lo requiera. El código es gratuito; su operación no elimina el costo de máquina, mantenimiento y copias. No instalar ninguna de esas herramientas hoy mantiene el costo y la superficie de riesgo más bajos.

### Implementación

`server.py` levanta la aplicación en `127.0.0.1:4173`, inicializa `data/opportunities.sqlite3` desde `data/opportunities.seed.json` una sola vez y ofrece `/api/health` y `/api/opportunities` con búsqueda/filtros. La base queda fuera de las rutas servidas. El servidor no registra términos, rechaza hosts HTTP inesperados, no tiene endpoints de escritura y devuelve cabeceras de seguridad. `.gitignore` excluye base local y cachés. `collector/policy.py`, `collector/ats_connectors.py` y `collector/sources.json` aportan una base sin activar conexiones: HTTPS, hosts exactos, presupuesto, redirecciones denegadas, tamaño/tiempo límite y estados no verificados.

La aplicación es local; no exponer el puerto a Internet. Publicarla requiere hardware y conectividad ya disponibles, más autenticación, copias, monitoreo, actualizaciones y disponibilidad. No se puede prometer hosting público permanente sin costo sin confirmar infraestructura preexistente. Tampoco se afirma que los metadatos ATS puedan republicarse: registrar aprobación por fuente antes de activar el colector.

### Siguientes acciones

1. Revisar la interfaz servida localmente y confirmar que el catálogo carga y se filtra sin ocultar incertidumbre.
2. Escoger tres empleadores de sectores distintos y confirmar ATS y condiciones. Mantener conectores apagados hasta entonces.
3. Medir con un piloto curado si la actualización manual es manejable; incorporar colector solo cuando haya evidencia y autorización.
4. Hacer y restaurar una copia local antes de cambios curatoriales importantes; no añadir cuentas hasta que existan perfiles o datos personales.

### Fuentes técnicas primarias

- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- [SQLite serverless/zero-configuration](https://www.sqlite.org/zeroconf.html)
- [Scrapy: repositorio y licencia BSD-3-Clause](https://github.com/scrapy/scrapy)
- [Firecrawl: repositorio/licencia](https://github.com/firecrawl/firecrawl)
- [Firecrawl: guía de autohospedado](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)
- [Firecrawl: compose oficial](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)

## 19. Gestión en GitHub y ejecución semanal (3 de octubre de 2026)

El usuario creó [Blueisazul/WebRutaSistemas](https://github.com/Blueisazul/WebRutaSistemas) para alojar y gestionar el proyecto. En esta sesión la carpeta local no tiene commits ni remoto configurado. No pude inspeccionar GitHub: la página no fue accesible en el navegador y `git ls-remote` falló porque el entorno bloqueó la conexión a `github.com:443`. Además, las reglas de esta sesión permiten leer `.git`, pero no escribir dentro de él, así que `git remote add origin ...` no pudo modificar `.git/config`. Los archivos de trabajo siguen presentes localmente; la sincronización remota queda pendiente de que haya acceso de red y escritura del repositorio.

### Recomendación: programador local, no botón público

No añadir ahora un botón web para iniciar colectores: el servidor de catálogo es de solo lectura, no existe autenticación/rol operador y todavía no hay fuentes concretas autorizadas. Un endpoint que dispare rastreos podría ser abusado desde el navegador y ampliaría innecesariamente la superficie de seguridad.

Cuando se apruebe y pruebe al menos una fuente, usar una tarea del **Programador de tareas de Windows** que ejecute el comando local semanalmente. No necesita suscripción, servidor externo ni puerto entrante. La computadora debe estar encendida o configurada para reanudar la tarea; también necesita conectividad para consultar la fuente. Si está apagada, la ejecución se retrasa hasta que vuelva a estar disponible. El botón manual puede añadirse a una herramienta local de operador después, como una acción de vista previa/ejecución con resultados y errores visibles; no a la página pública.

La futura tarea debe leer `collector/sources.json` y consultar **solo** entradas `enabled: true` que hayan aprobado términos, derechos y hosts exactos; mantener presupuesto por fuente y pausa semanal; registrar última ejecución y resultado sin datos personales; y no elevar a activa una oferta solo por recibir una respuesta. Con cero fuentes aprobadas, el comando debe terminar sin hacer conexiones y decir por qué. No crear una tarea programada real ni activar fuentes en esta etapa.

El siguiente paso cuando GitHub sea accesible es comprobar si el remoto está vacío o contiene README/licencia/archivos iniciales, luego sincronizar conservando ambos lados. No inicializar, sobrescribir ni forzar un push antes de esa comprobación.
