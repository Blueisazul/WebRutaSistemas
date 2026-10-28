# Diseño preliminar: modelo de datos y arquitectura del piloto

**Proyecto:** Plataforma de oportunidades y carrera para Sistemas  
**Ámbito:** Perú + remoto elegible desde Perú  
**Estado:** diseño previo a implementación; parte de la investigación de mercado y fuentes del 3 de octubre de 2026.  
**Decisión rectora:** primero confianza y trazabilidad; después automatización y personalización.

> **Vigencia:** este documento conserva decisiones y recomendaciones históricas. Para el estado implementado, seguir [ADR-001](docs/adr/ADR-001-catalogo-curado-publicacion-segura.md) y la sección 21; esas decisiones sustituyen las recomendaciones anteriores de hosting, colector, Tailwind y publicación.

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

## 20. GitHub Pages y catálogo JSON estático

Se volvió a inspeccionar el repositorio sincronizado y la URL pública de Pages. El HTML cargaba, pero los números quedaban en “—” y el catálogo entraba en estado de error: GitHub Pages no ejecuta `server.py`, mientras la interfaz llamaba `/api/opportunities`. Se cambió la vista a descargar `data/opportunities.json` con URL relativa, que funciona bajo el subpath `/WebRutaSistemas/`; búsqueda, modalidad, tipo, familia y convocatorias históricas ahora se filtran en el navegador. `scripts/build_catalog.py` genera el archivo público desde la semilla curada; no es un colector y no agrega publicaciones nuevas. `server.py`/SQLite quedan disponibles solo para desarrollo local.

No se habilitó cron, porque las fuentes siguen pendientes de aprobación y los lectores ATS aún no conforman una canalización de persistencia y verificación. Cuando ese trabajo exista, usar GitHub Actions semanal/manual para regenerar y publicar el JSON es lo más sencillo. Programador de Windows sirve para alimentar un equipo local, pero no actualiza por sí solo la web de GitHub Pages.

Se incorporaron utilidades Tailwind en áreas principales, formularios y tarjetas. `styles.css` conserva aún estilos de marca, arte, modal y detalle, por lo que no se considera una traducción total terminada. Se usa temporalmente el Play CDN permitido por el usuario; Tailwind advierte que esta opción se limita a desarrollo. Antes de consolidar producción, compilar el CSS localmente/en CI y servir el bundle propio. No se pudo probar esa compilación local porque npm no alcanzó el registro desde este entorno.

Referencias: [GitHub Pages con Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site?source=post_page---------------------------), [GitHub Actions gratis en repos públicos](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [cron Actions puede retrasarse o apagarse tras 60 días sin actividad](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows?ref=fabians-dev-blog), [Tailwind Play CDN (desarrollo)](https://tailwindcss.com/docs/installation/play-cdn).

## 21. Estado vigente y roadmap (decisión 2026-10-26)

> Este apartado y [ADR-001](docs/adr/ADR-001-catalogo-curado-publicacion-segura.md) reemplazan las recomendaciones operativas anteriores de este documento. Las secciones 1–20 se conservan como registro histórico, no como instrucciones actuales.

### Arquitectura vigente

- Fuente editable canónica única: `data/opportunities.seed.json` (schema 2).
- Artefacto estático generado: `data/opportunities.json`. `python scripts/build_catalog.py --check` compara toda la semilla con el snapshot excepto `generatedAt`; `--write` reemplaza explícitamente el artefacto. La generación impide perder IDs existentes que no estén en la fuente canónica.
- TTL inicial configurable: 7 días calendario, evaluado con fecha civil de Perú UTC−05:00. Es hipótesis de piloto y se revisará midiendo cierres; no promete disponibilidad.
- El catálogo auditado conserva cinco fichas demostrativas y ninguna activa. Vencimiento, evidencia faltante o verificación atrasada impiden enlazar a postulación.
- GitHub Pages/Actions continúa como hosting/ejecutor alojado, no como OSS ni independencia plena. El flujo estático es portable. SQLite es prototipo local separado; no sincroniza ni decide el catálogo público.
- Browser CDN de Tailwind eliminado; la hoja CSS local existente se encarga de la presentación.
- Colectores apagados. Si alguna fuente se activa en configuración, `python -m collector.refresh_catalog` se detiene sin solicitud de red hasta definir e implementar el proceso de revisión schema 2.

### Estado de tareas y siguiente fase

| Trabajo | Estado | Evidencia/criterio |
|---|---|---|
| Estados separados, TTL y bloqueo de deadline vencida | Implementado | `scripts/catalog_quality.py`; pruebas sin red |
| Catálogo canónico y generación sin pérdida silenciosa | Implementado | semilla como fuente única; `--check` y `--write` explícito |
| Pruebas de límites, URL, frescura y fallos de red | Implementado | `tests/test_catalog_quality.py` |
| Validación previa al despliegue y permisos separados | Implementado localmente | `.github/workflows/refresh-catalog.yml`; ejecución remota aún no verificada |
| Tailwind CDN runtime | Eliminado | `index.html`; CSP local endurecida en `server.py` |
| Una fuente real autorizada | Pendiente de autorización/revisión | no activar Greenhouse/Lever ni automatizar antes del permiso y medición |
| Hosting totalmente autoalojado | Aplazado | requiere máquina disponible, TLS, monitoreo, respaldo y persona operadora |

**Siguiente bloque exacto:** seleccionar una fuente de un empleador concreto y completar revisión documentada de acceso/uso, atribución, frecuencia, datos conservables y retirada. Si está permitida, capturar una muestra pequeña bajo revisión humana; medir frescura, campos ausentes, falsos activos, duplicados y tiempo manual. No publicar automáticamente las fichas de prueba. No construir scoring, recomendaciones, IA, rutas profesionales ni crawler general en ese bloque.

## 22. Evaluación P2: Talento Perú/SERVIR (2026-10-26)

Esta sección actualiza el siguiente paso del roadmap 21 para la evaluación P2. **No reemplaza las decisiones técnicas del ADR-001.**

- Estado local verificado: rama `main`, HEAD `19cf942e2829833ee95ae3af177f4a44aea3566a`, cambios P0/P1 locales sin commit. No fue posible consultar el remoto por error de red/DNS; no se afirma sincronización.
- Talento Perú es una fuente oficial de descubrimiento según SERVIR. La documentación indica que cada postulante continúa en la web de la entidad convocante.
- Se identificó en el directorio oficial de SERVIR la aplicación pública de consulta de Talento Perú. No se identificó API/feed ni condiciones que autoricen automatización, reutilización, retención o republicación. La herramienta devolvió HTTP 403 al abrir la consulta; no se infiere de ello una prohibición ni caída.
- Como única alternativa, se evaluó la web de oportunidades/noticias de la Facultad de Ingeniería de Sistemas e Informática de UNMSM (FISI). El índice consultado muestra avisos laborales y de prácticas; una ficha identifica un anuncio de GM Ingenieros difundido por la facultad. No se encontró API/feed o términos de uso para automatización/reutilización; la apertura directa de la ficha falló HTTP 502 y `robots.txt` no fue accesible. No se infiere permiso, prohibición ni caída.
- Ambas decisiones son `pending_review`; las dos fuentes están registradas apagadas y con presupuesto de solicitudes cero. No hubo adaptación ni piloto de extracción; volumen, completitud y otras métricas no se midieron.
- Evidencia y preguntas pendientes: [evaluación P2 de Talento Perú y alternativa FISI-UNMSM](docs/sources/talento-peru-servir-2026-10-26.md). Pruebas automáticas aseguran que ambas entradas no se puedan consultar.

**Siguiente bloque exacto:** solicitar y registrar respuesta de SERVIR o de FISI-UNMSM sobre acceso automatizado, reutilización de metadatos, atribución, frecuencia, retención/corrección/retirada y canal canónico de postulación. Mientras falte esa confirmación, mantener ambas fuentes deshabilitadas y no ejecutar piloto automatizado. Si una confirma condiciones compatibles, implementar una captura de hasta 10 candidatos en staging, revisar a mano y medir; no habilitar cron ni publicar candidatos automáticamente. Si ambas lo descartan, el siguiente camino es captura manual reproducible a partir de enlaces oficiales, previa revisión editorial individual.

## 23. Bloque P3: solicitudes institucionales y flujo editorial local (2026-10-26)

- **Contactos confirmados:** SERVIR publica `talentoperu@servir.gob.pe` para Talento Perú y anexos de consulta; el directorio oficial FISI lista `decanato.fisi@unmsm.edu.pe`. Los borradores para ambas instituciones están en [seguimiento de autorización](docs/sources/seguimiento-autorizacion-fuentes.md); no fueron enviados.
- **Mecanismo SERVIR mejorado:** su directorio oficial lista la aplicación pública de consulta. Esto resuelve quién ofrece consulta humana, pero no derechos de automatización/reutilización ni estabilidad técnica; el navegador de investigación recibió 403. SERVIR y FISI siguen con decisión `pending_review`, extracción y presupuesto cero.
- **Brecha editorial cerrada localmente:** existían campos de evidencia para publicar una oportunidad, pero no un staging para un candidato sin modificar la semilla. Se añadió `data/candidates/inbox.local.json` (ignorado por Git), ejemplo vacío, documentación de proceso y `scripts/validate_candidates.py`, de solo lectura. Una decisión editorial nunca crea por sí sola un registro activo; la transferencia a la semilla sigue siendo manual y luego pasa los controles actuales.
- **Pruebas:** las pruebas del validador cubren bandeja vacía, datos desconocidos, URL/fechas, duplicados, fuente pendiente, bloqueo de estados de publicación y no modificación de la semilla. El workflow valida el ejemplo vacío; no consulta fuentes ni ejecuta scraping.
- **Pendiente externo:** recibir respuestas institucionales que diferencien consulta humana, automatización y reutilización pública; revisar API/feed, límites, atribución, retención/retirada y postulación. Ningún borrador se envió y no hay oportunidades reales nuevas.

**Siguiente bloque exacto:** una persona autorizada revisa y, si lo decide, envía los dos borradores. Registrar respuestas y adjuntar evidencia oficial a `collector/sources.json`. Aprobar por separado uso manual, automatización y reutilización pública. Solo si la fuente autoriza el uso público y existe mecanismo estable, ejecutar piloto de hasta 10 candidatos en bandeja local; si no, mantener la curación manual limitada al uso confirmado. No habilitar programación mientras no haya muestra longitudinal que justifique frecuencia y mantenimiento.

## 24. Bloque P3: contrato de evidencia y presentación editorial (2026-10-26)

- **Brecha comprobada:** el catálogo exigía evidencia agregada de vigencia, pero no exigía procedencia por cada dato factual; tampoco había campo explícito para diferenciar empleador de difusor. La ficha modal llamaba “Fuente principal” al origen y usaba `applyUrl || sourceUrl` para el enlace informativo, lo que podía presentar la ficha como canal de postulación.
- **Implementado:** `scripts/catalog_quality.py` ahora exige para fichas activas editor aprobador, revisor, fecha/motivo, empleador/difusor explícitos y evidencia reciente por campo para identidad, enlace de postulación y toda condición no vacía (salario, modalidad, fechas, requisitos, beneficios, herramientas, etc.). Evidencia externa requiere HTTPS, host permitido y timestamp válido. La lógica del frontend degrada también un snapshot inconsistente y nunca deriva postulación desde el enlace informativo.
- **Interfaz:** detalle diferencia empleador, entidad difusora, ficha informativa y canal de postulación; muestra enlaces de procedencia por dato, fecha de última verificación y datos no informados. Las fichas demostrativas continúan etiquetadas como tales. No se añade puntuación ni promesa de continuidad.
- **Sin migración de datos:** este bloque no modificó `data/opportunities.seed.json` ni `data/opportunities.json`. En el estado local actual siguen cinco fichas demostrativas, ninguna activa; cambios P1 previos en esos archivos ya estaban presentes al inicio y se preservan. No se elevan las muestras a datos reales.
- **Flujo editorial:** la bandeja manual ahora representa también `publisher` (difusor) por separado de `employer`; valores ausentes siguen `null`. La aprobación candidata requiere identificar al difusor junto al empleador y canal de postulación.
- **Validación:** 39 pruebas `unittest` pasan, incluidas pruebas de evidencia por campo, revisor/aprobación, salario sin evidencia, rechazo/retiro sin motivo, hosts y estados en UI. Se ejecuta además el validador y generador en comprobación de solo lectura. No se revisó despliegue remoto.
- **Pendiente:** SERVIR y FISI-UNMSM continúan `pending_review`, deshabilitadas y con presupuesto cero; el bloqueo externo es obtener aclaración/autorización y no se ha ejecutado ingesta real.

**Siguiente bloque exacto:** mantener fichas demostrativas ocultas por defecto y, cuando una persona autorizada resuelva los derechos de reutilización de una fuente, incorporar manualmente una primera oportunidad comprobada que incluya evidencia por campo. Antes de ampliar a otras fuentes, medir con esa ficha real el esfuerzo editorial, la claridad de la procedencia y el funcionamiento de los estados. Los borradores institucionales siguen sin enviarse.

## 25. Bloque P4: catálogo público honesto (2026-10-26)

- **Comportamiento público:** las cinco fichas con `recordKind: demonstration` quedan fuera de resultados y contadores por defecto. Se pueden consultar con la casilla explícita “Incluir ejemplos demostrativos”; los estados, búsqueda y filtros de cada ejemplo se mantienen y nunca se habilita postulación.
- **Catálogo sin ofertas reales:** la vista predeterminada muestra un mensaje de “No hay oportunidades verificadas disponibles” y explica la revisión humana de publicación y canal de postulación. Los contadores y fecha de última consulta excluyen demostraciones para no aparentar cobertura o actividad real.
- **Procedimiento manual:** la guía de la bandeja editorial especifica autorización pública, evidencia por dato, empleador/difusor, enlace de anuncio/postulación, elegibilidad remota, fechas separadas, verificación, decisión humana y promoción manual más los comandos reproducibles. `approved_for_catalog` no escribe la semilla ni el snapshot.
- **Pruebas:** añadidas comprobaciones para la opción explícita, exclusión de demostraciones de métricas, CTA deshabilitado y separación entre origen y postulación; se amplió la prueba de bandeja para preservar semilla y snapshot, y de catálogo para rechazar demostraciones activas/evidencia caducada. La validación integrada de 43 pruebas, el generador, los validadores y sintaxis JavaScript se ejecutaron localmente. No se pudo abrir el servidor loopback en el navegador integrado por timeout de conexión, así que no se declara inspección visual.
- **Bloqueo sin cambio:** las fuentes institucionales siguen pendientes y deshabilitadas; no se consultaron. El catálogo conserva cinco demostraciones, ninguna oportunidad real activa; no se creó una oferta ni se modificó la semilla/snapshot en este bloque.

**Siguiente paso:** esperar decisión humana sobre autorización de uso de una fuente; cuando exista, incorporar manualmente una única oportunidad real con evidencia completa, revisar el diff y medir el esfuerzo editorial. Mantener la demostración optativa y no activar ingesta programada.

## 26. Bloque P5: validación funcional integrada (2026-10-26)

- **Defecto reproducible corregido:** el frontend aceptaba un objeto con `opportunities` como catálogo sin comprobar versión, estados, IDs, URL de origen, hosts ni registros nulos. Ahora valida el contrato mínimo schema 2 antes de sustituir el estado visible y presenta un error claro si falla la primera carga. La comprobación de URLs del navegador coincide con los controles básicos HTTPS del validador.
- **Contadores corregidos:** se calculan solo sobre registros no demostrativos y separan activas, vencidas/históricas y no confirmadas sin solapamientos. La etiqueta de orden ahora describe el criterio real (estado y empresa), y el error de carga ya no promete un canal de contacto inexistente.
- **Pruebas integradas:** Node.js estándar ejecuta `tests/catalog_ui.test.cjs` en CI sin paquetes nuevos. Evalúa con VM las funciones reales de filtrado, métricas y estados; incluye ejemplos optativos, búsqueda, modalidad, historia, payloads inválidos y degradación de una ficha activa incompleta. Python comprueba que un candidato aprobado no se promueve solo y que `--check` no escribe; semilla y snapshot se comparan antes/después.
- **Pipeline local:** el workflow declara `contents: read`, ejecuta pruebas de Python, validadores de catálogo/candidatos, `node --check` y el test de interfaz antes del job de Pages. No hay schedule ni llamada al colector; Pages requiere permisos de publicación propios del job. No se ejecutó GitHub Actions remoto.
- **Validación visual:** no completada. Se intentó abrir `127.0.0.1:4173` en el navegador integrado y agotó el tiempo de conexión; el entorno restringió el acceso al socket local. Las pruebas de Node y las comprobaciones estáticas pasan, pero no se afirma inspección visual ni compatibilidad móvil observada en pantalla.
- **Datos y fuentes:** este bloque no modificó semilla, snapshot ni bandeja de ejemplo. Los cinco registros siguen demostrativos, ninguno activo. SERVIR/FISI siguen `pending_review`, apagadas y con presupuesto cero; no hubo consultas ni piloto.

**Siguiente paso operativo:** una persona autorizada debe revisar y, si lo decide, enviar los borradores institucionales y registrar sus respuestas. Solo con autorización de reutilización pública, incorporar manualmente una única oportunidad real y ejecutar el proceso editorial. No hay tarea de ingesta automatizada pendiente de ejecución ni despliegue confirmado.

## 27. Bloque P6: preparación del primer piloto curado y publicación estática (2026-10-27)

- **Decisión del piloto:** no se incorporó una oportunidad real. `collector/sources.json` mantiene SERVIR y FISI-UNMSM en `pending_review`, `enabled: false` y `maxRequestsPerRun: 0`; la guía de autorización confirma que los borradores no se enviaron. No hubo consultas ni existe evidencia nueva de autorización para conservar y republicar metadatos.
- **Expediente:** los contactos, enlaces institucionales, borradores de consulta, preguntas y criterios para separar acceso manual, extracción automatizada y reutilización pública ya constan en `docs/sources/seguimiento-autorizacion-fuentes.md`. No se duplicó ese material ni se contactó a las instituciones. La referencia Rentry no estuvo accesible desde la herramienta durante esta ejecución; se contrastó el estado con el checkout y su documentación.
- **Flujo editorial:** se ejecutaron las pruebas existentes de candidatos y fuentes. La bandeja `inbox.example.json` valida como vacía, el validador no publica y el comando `python -m collector.refresh_catalog` confirma que no hay fuentes activadas y no realiza consultas. `inbox.local.json` no existe en este entorno; no se creó ni se inventó una oportunidad para reemplazarlo.
- **Publicación estática local:** `build_catalog.py --check` confirmó que el snapshot coincide con la semilla; el generador mantiene `--write` como acción explícita. Se ensambló temporalmente el artefacto con los cuatro archivos declarados en el workflow (HTML, JS, CSS y JSON), y la URL relativa del catálogo resolvió a `/WebRutaSistemas/data/opportunities.json`. El workflow local valida antes de publicar, sin cron, scraping ni permisos `contents: write`. No se ejecutó Actions remoto ni se desplegó Pages.
- **Validación:** 47 pruebas Python aprobadas; validadores de catálogo y candidatos, `node --check`, `node --test tests/catalog_ui.test.cjs` y `git diff --check` finalizaron correctamente. El validador informa advertencias esperadas por las fichas de demostración/no activas. La comprobación visual sigue pendiente: el entorno anterior no permitió abrir el servidor loopback y no se confirmó una sesión visual en este bloque.
- **Datos:** no se modificaron semilla, snapshot ni bandeja de ejemplo durante P6. Los cambios preexistentes en semilla/snapshot ya estaban en el árbol inicial y se conservaron. No hay métricas reales de captura editorial; en el primer caso autorizado se medirán duración, campos factuales respaldados, datos desconocidos, dificultades de vigencia/postulación, conflictos, cambios editoriales y defectos de publicación.

**Siguiente paso concreto:** una persona autorizada revisa y, si lo decide, envía los borradores institucionales y registra las respuestas/evidencias. Mantener cada fuente deshabilitada hasta confirmar por separado consulta manual, extracción, conservación, atribución y publicación pública. Cuando exista autorización pública suficiente, incorporar una sola oportunidad real mediante la bandeja y medir el esfuerzo editorial; no activar scraping ni programación en este bloque.

## 28. Bloque P7: publicación Pages y degradación segura (2026-10-27)

- **Estado del checkout:** `main`, base `19cf942e2829833ee95ae3af177f4a44aea3566a`; los cambios P1–P6 ya estaban sin commit y se preservaron. La referencia Rentry no fue accesible desde las herramientas; se usó el código local como fuente de verdad y se observó Pages en modo de solo lectura.
- **Divergencia crítica confirmada en Pages:** el sitio público cargó bajo `/WebRutaSistemas/`, pero el JSON público sigue en schema 1 y declara `generatedAt: 2026-10-03`. La interfaz muestra cuatro registros y no tiene el control de demostraciones optativas del checkout actual. El snapshot público contiene `OP-001` con fecha límite `2026-10-13`, `status: verified`, `history: false`; a la fecha de esta comprobación, 2026-10-27, ese plazo ya pasó. Los otros tres anuncios visibles también registran su consulta el 03/10. Esto demuestra que el despliegue observado no incorpora los cambios locales P4–P6 y aún presenta datos antiguos como resultados. No se cambió el sitio remoto.
- **Checkout local:** semilla y snapshot schema 2 coinciden y contienen cinco registros, todos `recordKind: demonstration`, con estados stale, históricos o no confirmados; no hay oportunidades reales activas. SERVIR y FISI continúan deshabilitadas y con cero solicitudes.
- **Corrección local:** `app.js` ahora elimina tarjetas, resultados y métricas anteriores cuando una recarga falla, deja visible el error también tras interactuar con filtros y restablece los indicadores de fecha. El contenedor de estado vacío/error anuncia cambios con `role=status`. `tests/catalog_ui.test.cjs` cubre raíz y subpath, además de secuencias válidas seguidas de error HTTP, JSON malformado o schema incompatible. Se añadió `tests/__init__.py` porque `python -m unittest` ejecutaba cero casos sin el paquete de pruebas.
- **Publicación local:** se revisó que HTML, CSS, JS y JSON usan rutas compatibles con el subpath; las pruebas comprueban las rutas exactas de los tres recursos en raíz y bajo `/WebRutaSistemas/`. Se reensambló el artefacto actual en staging temporal y se verificó que contiene solo los cuatro archivos esperados. El workflow local ejecuta validación antes del job `publish`, no contiene schedule ni scraper y limita `contents` a lectura, con permisos de Pages solo en el job de despliegue.
- **Validación visual:** parcialmente verificada. El navegador inspeccionó captura visual y DOM del sitio Pages público, confirmando su carga y la divergencia indicada. El servidor local no pudo abrirse en el navegador integrado (timeout de loopback), así que no se inspeccionó visualmente el checkout corregido ni su diseño móvil. El despliegue remoto/Actions no se ejecutó ni se validó.
- **Validaciones locales:** `python -m unittest` y `python -m unittest discover -s tests` (47 aprobadas); `python scripts/build_catalog.py --check`; `python scripts/validate_catalog.py` (válido con advertencias esperadas); `python scripts/validate_candidates.py data/candidates/inbox.example.json`; `python -m collector.refresh_catalog` (no-op sin solicitudes); `node --check app.js`; `node --test tests/catalog_ui.test.cjs`; `git diff --check` (éxito; avisos informativos LF/CRLF).
- **Datos:** no se modificaron la semilla, el snapshot ni la bandeja. Sus modificaciones previas ya estaban presentes al inicio. No se habilitó ninguna fuente, no se incorporó una oportunidad y no hubo scraping.

**Siguiente prioridad de entrega:** revisión humana del diff local acumulado y, cuando el usuario autorice, integrar y publicar los cambios P1–P7 para que Pages deje de servir schema 1 y el registro vencido. Después de publicar, volver a comprobar visualmente la URL real, el estado vacío, los ejemplos optativos y los errores de carga. No hacer push ni despliegue sin autorización explícita. La autorización de fuentes sigue siendo una dependencia humana separada y ninguna oportunidad real debe añadirse mientras siga pendiente.

## 29. Bloque P8: candidato local de versión y divergencia remota (2026-10-27)

- **Clasificación Git:** `main` en `19cf942e2829833ee95ae3af177f4a44aea3566a`; 16 archivos rastreados modificados y archivos nuevos en docs, scripts, pruebas y el ejemplo de bandeja ya estaban sin commit. Git no permite atribuirlos por separado a P7 porque todo el conjunto está pendiente desde P1–P7; se conservaron sin stage, restauración ni limpieza. `data/candidates/inbox.local.json` no existe en este checkout y sigue ignorado por diseño. No aparecieron temporales en el árbol del repositorio.
- **Candidato:** coherente para revisión local. ADR-001 y el código mantienen la semilla editable como fuente, snapshot schema 2 generado, comprobación de solo lectura, protección de IDs y edición humana. La interfaz valida schema 2, usa rutas relativas, oculta demostraciones por defecto y desactiva postulación demostrativa. Semilla y snapshot contienen los mismos cinco registros demostrativos; cero están activos. No se agregaron oportunidades reales.
- **Artefacto/CI:** el workflow valida antes de publicar (`publish.needs: validate`), prepara únicamente `index.html`, `app.js`, `styles.css` y `data/opportunities.json`, exige exactamente esos cuatro archivos y concede escritura Pages/OIDC únicamente al job de publicación; el alcance global del repositorio es lectura. No hay trigger programado, scraping ni escritura de datos a `main`. Se comprobó un staging local actual con esos cuatro archivos byte por byte iguales al checkout. La UI carga recursos bajo el prefijo `/WebRutaSistemas/`; las pruebas deterministas comprueban recursos desde raíz y subpath.
- **Riesgo remoto reconfirmado en modo de solo lectura:** Pages sigue sirviendo schema 1 generado el 03/10/2026, muestra cuatro resultados y `OP-001` figura como `verified` con fecha límite `13/10/2026`. No es el candidato local y representa riesgo de información vencida. La configuración remota de Pages, una ejecución remota de Actions y los cambios locales aún no publicados no se confirmaron por API; no se hizo publicación.
- **Pruebas y datos:** `python -m unittest` y `python -m unittest discover -s tests -v` pasaron (47); generador en `--check`, validadores de catálogo y bandeja de ejemplo, sintaxis JS, test UI Node y `git diff --check` pasaron. Las advertencias del catálogo son por fichas de demostración/no activas; Git informa solo avisos LF/CRLF. Hashes SHA-256 de seed y snapshot se mantuvieron iguales durante la validación. SERVIR y FISI continúan `pending_review`, deshabilitadas y con cero solicitudes.
- **Límite del candidato:** es un lote local amplio, no preparado ni aprobado para integración automática. Antes de cualquier release, una persona debe revisar el diff completo y seleccionar conscientemente los archivos P1–P7; ejecutar validaciones sobre ese conjunto; autorizar un commit/push a `main` (que activa el workflow actual); comprobar la ejecución de Actions; y validar en navegador la página y el JSON públicos. Ninguno de esos pasos remotos se ejecutó aquí. La publicación del sitio y la autorización de fuentes son decisiones separadas.

**Decisión P8:** candidato local listo para revisión de publicación, no publicado. Mientras el sitio público siga con schema 1 y la oferta vencida, no tratar Pages como representación del checkout actual. El siguiente paso es revisión e integración autorizadas del conjunto coherente, seguida de validación remota; no se requiere más desarrollo de rutas o generación para habilitar esa revisión. La curación de oportunidades reales permanece bloqueada por autorización humana de fuente y revisión individual.

## 30. Bloque P9: unidad de integración controlada (2026-10-27)

- **Estado inspeccionado:** rama `main`, `HEAD` `19cf942e2829833ee95ae3af177f4a44aea3566a`; cero cambios staged y el mismo lote P1–P8 sigue modificado/no rastreado. El diff acumulado comprende frontend/datos, validación/generador, colector deshabilitado, prototipo SQLite local, pruebas y documentos. Al no haber commits por etapas, Git no permite atribuir cada archivo a una sesión/autora; no se descartó ni se separó trabajo. No existe `data/candidates/inbox.local.json` en el checkout. El staging temporal se creó fuera del repo.
- **Unidad fuente propuesta para revisión:** (a) aplicación/catálogo: `index.html`, `app.js`, `styles.css`, `data/opportunities.seed.json`, `data/opportunities.json`; (b) contrato y control de datos: `scripts/build_catalog.py`, `scripts/catalog_quality.py`, `scripts/validate_catalog.py`, `scripts/validate_candidates.py`, `data/candidates/README.md`, `data/candidates/inbox.example.json`, `.gitignore`; (c) fuentes y política: `collector/sources.json`, `collector/policy.py`, `collector/refresh_catalog.py`, `collector/README.md`; (d) CI y regresión: `.github/workflows/refresh-catalog.yml`, `tests/__init__.py`, `tests/catalog_ui.test.cjs`, `tests/test_candidates.py`, `tests/test_catalog_quality.py`, `tests/test_local_server_catalog.py`, `tests/test_source_evaluation.py`, `tests/test_static_contract.py`; (e) continuidad: `README.md`, `Informe-investigacion-mercado-fuentes-2026-10-03.md`, este roadmap, `docs/adr/ADR-001-catalogo-curado-publicacion-segura.md`, `docs/audits/project-state-audit-2026-10-25.md`, `docs/sources/seguimiento-autorizacion-fuentes.md` y `docs/sources/talento-peru-servir-2026-10-26.md`; (f) `server.py` con `tests/test_local_server_catalog.py` se conserva como pareja del prototipo local schema 2, no como backend público.
- **Dependencias del release:** la semilla, generador, snapshot, contrato del frontend y validadores tienen que viajar en el mismo commit para que `--check` y CI validen el artefacto que se publicará. El workflow toma el checkout de ese mismo evento, requiere el job `validate` y copia exclusivamente cuatro archivos a Pages: `index.html`, `app.js`, `styles.css`, `data/opportunities.json`. ADR, scripts, collector, seed, tests, README y bandeja sirven al repo/CI; no entran en el artefacto Pages. `docs/audits/project-state-audit-2026-10-25.md` es una referencia histórica y tampoco entra al artefacto. `inbox.local.json`, SQLite y staging temporal quedan fuera.
- **Compatibilidad/seguridad:** 47 pruebas Python, generador en `--check`, validadores, sintaxis JS, prueba Node de UI y `git diff --check` pasaron. Los hashes del seed/snapshot no cambiaron; schema 2, cinco demos y cero activos; fuentes SERVIR/FISI continúan pendientes, deshabilitadas y a cero solicitudes. Las rutas y los fallos de catálogo están cubiertos por las pruebas de raíz y `/WebRutaSistemas/`.
- **Producción/remoto:** una inspección de solo lectura el 2026-10-27 confirmó que Pages sigue con UI de cuatro resultados y snapshot schema 1 de `2026-10-03`, incluyendo `OP-001` `verified` con deadline `2026-10-13`. `git ls-remote origin HEAD refs/heads/main` falló por `getaddrinfo`; el valor local de `origin/main` coincide con `HEAD`, pero no prueba el HEAD remoto. No se verificó configuración remota de Pages ni una ejecución remota de Actions.
- **Decisión:** unidad fuente lista para revisión de integración, no integrada ni publicada. La procedencia exacta de cambios no puede recuperarse del diff agregado; revisar el lote antes de seleccionarlo para un commit. Ningún archivo local se añadió al staging en P9.

**Secuencia mínima para una publicación autorizada posterior:** revisar y seleccionar conscientemente la unidad fuente anterior; confirmar con `git diff --cached` que seed, snapshot, validadores, pruebas y workflow corresponden al mismo candidato y excluir cualquier archivo ajeno; ejecutar la suite y revisar que `build_catalog.py --check` pase; autorizar el commit/push a `main` sabiendo que el workflow dispara Pages; esperar el resultado observable de Actions; y comprobar en navegador que el sitio ya sirve schema 2, cero vacantes reales activas y demostraciones optativas, y que el JSON remoto coincide con el candidato. No se hizo ninguno de esos pasos de integración/publicación. La autorización de fuentes sigue siendo una decisión humana independiente.

## 31. Bloque P10: integridad del artefacto de GitHub Pages (2026-10-27)

- **Estado inicial:** rama `main`, `HEAD` `19cf942e2829833ee95ae3af177f4a44aea3566a`; el lote acumulado de P1–P9 seguía con cambios staged/unstaged/no rastreados previos. No se descartó ni reescribió ese trabajo. Este bloque añadió únicamente el preparador/validador de artefacto, sus pruebas, el enlace del workflow y esta nota.
- **Brecha cerrada:** las validaciones previas cubrían fuentes por separado y el workflow copiaba cuatro archivos con comandos de shell, pero no comprobaba el directorio final de publicación frente al snapshot ni rechazaba recursos extra. `scripts/pages_artifact.py` ahora centraliza la única lista de archivos públicos, crea `dist` y valida ese mismo directorio antes de que se cargue a Pages.
- **Contrato del artefacto:** se requieren exactamente `index.html`, `app.js`, `styles.css` y `data/opportunities.json`; faltantes y extras fallan. Se comprueban referencias locales de CSS/JS, la resolución bajo `/WebRutaSistemas/`, el uso por el frontend de la ruta relativa del catálogo y schema 2, la ausencia del endpoint local `/api/opportunities` y de imports/URLs remotos en CSS. El JSON de `dist` debe coincidir byte por byte con el snapshot validado y pasar el validador de catálogo. No se modifica semilla ni snapshot.
- **CI:** `publish` invoca `python scripts/pages_artifact.py --output dist` antes de configurar Pages, cargar el artefacto o desplegarlo. `publish.needs: validate` conserva el bloqueo tras las pruebas/validadores; `path: dist` consume el directorio que acaba de verificarse. No se añadieron dependencias, cron, scraping ni permisos de escritura al repositorio. La ejecución remota de Actions no se comprobó.
- **Cobertura nueva:** fixtures aislados comprueban éxito con los cuatro archivos exactos y rechazo ante recurso faltante, JSON malformado, schema distinto, ruta raíz incompatible con el subpath, divergencia del snapshot y archivo adicional. La prueba de contrato comprueba que el workflow valida antes de cargar/desplegar.
- **Resultado local:** `python -m unittest discover -s tests -v` pasó con 54 pruebas; `build_catalog.py --check`, validadores de catálogo/candidatos, `node --check app.js`, `node --test tests/catalog_ui.test.cjs`, y `git diff --check` pasaron. La prueba específica pasó un caso positivo y seis casos negativos. `python scripts/pages_artifact.py --output <temporal>` ensambló y validó localmente los cuatro archivos, y el temporal se retiró. SHA-256 del seed y snapshot antes y después: `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` y `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05`, respectivamente; no cambiaron. La prueba usa herramientas estándar de Python, sin paquetes nuevos. La inspección visual del sitio local no se realizó en este bloque y el estado remoto de Actions/Pages no se deduce de estas comprobaciones.
- **Integridad editorial:** las cinco fichas siguen siendo demostrativas, no hay vacantes reales activas y las fuentes SERVIR/FISI permanecen pendientes, deshabilitadas y con presupuesto cero. No hubo consultas ni incorporación de datos.

**Siguiente paso:** revisar e integrar el lote local acumulado de forma autorizada y comprobar la ejecución real de Actions; después de una publicación autorizada, inspeccionar la página y el JSON públicos. La autorización de fuentes y reutilización pública sigue siendo una decisión humana independiente.

## 32. Paquete de revisión para release (2026-10-27)

### Estado comprobado

- Checkout en `main`, `HEAD` `19cf942e2829833ee95ae3af177f4a44aea3566a`; cero archivos staged, 16 archivos rastreados modificados y 18 archivos no rastreados. Los cambios ya estaban acumulados; el historial no permite atribuirlos a P1–P10 ni a una persona/fase con certeza. No se hizo staging.
- `origin` apunta al repositorio GitHub esperado; la referencia local `origin/main` coincide con `HEAD`, pero no es una lectura remota reciente. `git ls-remote origin HEAD refs/heads/main` falló con `getaddrinfo() thread failed to start`. Rentry y las URLs de Pages no fueron accesibles a la herramienta en esta revisión. La página del repositorio sí devolvió un snapshot del rastreador web marcado como rastreado dos días antes; no expuso un SHA actual y mostraba un README antiguo, así que no se usa como prueba del remoto vigente. El resultado P9 —Pages schema 1 y una ficha vencida— es la última observación documentada, no una confirmación nueva del estado actual.
- `data/opportunities.seed.json` y `data/opportunities.json` ya estaban modificados respecto a la base; validación local previa a esta nota confirmó schema 2 y sincronización, cinco demos y cero oportunidades reales activas. No se cambiaron datos en esta revisión.
- Elementos locales ignorados observados: `data/opportunities.sqlite3`, `node_modules/` y cachés `__pycache__/`. No forman parte de la unidad pública. `data/candidates/inbox.local.json` no existe en este checkout. Un escaneo acotado no encontró el correo personal dado al agente ni patrones comunes de tokens GitHub en los archivos revisados; no sustituye un escáner de secretos especializado.

### Clasificación de la unidad candidata

| Grupo | Archivos observados | Dependencia / riesgo si se separa | Pages |
| --- | --- | --- | --- |
| Aplicación pública | `index.html`, `app.js`, `styles.css`, `data/opportunities.json` | Deben viajar juntos: el frontend exige schema 2; el JSON es el snapshot que consume. El workflow limita el artefacto a este conjunto y `scripts/pages_artifact.py` comprueba su contenido exacto. | Sí: solo estos cuatro archivos |
| Datos y contrato editorial | `data/opportunities.seed.json`, `scripts/build_catalog.py`, `scripts/catalog_quality.py`, `scripts/validate_catalog.py`, `scripts/validate_candidates.py`, `data/candidates/README.md`, `data/candidates/inbox.example.json`, `.gitignore` | Semilla → generador → snapshot y validadores forman una cadena; omitirlos deja sin fuente reproducible o rompe las verificaciones. La bandeja local no se versiona. | No |
| Fuentes y control de ingesta | `collector/README.md`, `collector/policy.py`, `collector/refresh_catalog.py`, `collector/sources.json` | Van con pruebas de fuentes: config y policy mantienen el cierre seguro. No habilitar conectores. `collector/ats_connectors.py` no está modificado y no hace falta añadirlo a la unidad. | No |
| CI y pruebas | `.github/workflows/refresh-catalog.yml`, `tests/__init__.py`, `tests/catalog_ui.test.cjs`, `tests/test_candidates.py`, `tests/test_catalog_quality.py`, `tests/test_local_server_catalog.py`, `tests/test_pages_artifact.py`, `tests/test_source_evaluation.py`, `tests/test_static_contract.py`, `scripts/pages_artifact.py` | Deben integrarse juntos: workflow ejecuta pruebas, y prepara/valida el mismo `dist` que carga. El contrato de integración necesita estos controles; una prueba aislada sin workflow no bloquearía Pages. | No; validan el artefacto |
| Soporte local | `server.py` y `tests/test_local_server_catalog.py` | No participa en Pages. Como la suite lo prueba, integrarlos como pareja evita una suite rota; decidir expresamente si se conserva el prototipo local. SQLite ignorado queda fuera. | No |
| Documentación/continuidad | `README.md`, `Informe-investigacion-mercado-fuentes-2026-10-03.md`, este documento, `docs/adr/ADR-001-catalogo-curado-publicacion-segura.md`, `docs/audits/project-state-audit-2026-10-25.md`, `docs/sources/seguimiento-autorizacion-fuentes.md`, `docs/sources/talento-peru-servir-2026-10-26.md` | README y ADR deben acompañar las decisiones implementadas; reportes/auditoría son contexto, no dependencias de ejecución. Revisar que las notas históricas no se interpreten como estado actual. | No |

La tabla clasifica el lote por función, no por autoría. El número de archivos exacto debe confirmarse con `git status` antes de una integración futura porque ese árbol puede cambiar. La base de revisión no contiene commits intermedios para separar P1–P10; no hacer una selección parcial por fecha o nombre. No se detectó un defecto funcional nuevo que justifique cambiar código en este bloque. El workflow usa acciones oficiales mediante tags de versión mayor (`@vN`), no SHA inmutables: revisar ese riesgo de cadena de suministro antes de adoptar una política de pinning, sin actualizar dependencias a ciegas en este lote.

### Validaciones de este candidato

- Ejecutadas en la revisión P10 inmediatamente anterior, sin cambios de código posteriores: `python -m unittest discover -s tests -v` (54 pruebas), `python scripts/build_catalog.py --check`, `python scripts/validate_catalog.py` (válido, advertencias esperadas de demostraciones/no activas), `python scripts/validate_candidates.py data/candidates/inbox.example.json`, `node --check app.js`, `node --test tests/catalog_ui.test.cjs`, `git diff --check` y preparación/validación local de `dist` con `python scripts/pages_artifact.py`. Todo terminó correctamente; `git diff --check` mostró solo avisos de conversión LF/CRLF de Windows.
- El artefacto generado contiene exactamente `index.html`, `app.js`, `styles.css` y `data/opportunities.json`. Pruebas positivas/negativas validan ausencia de archivo, JSON malformado, schema incompatible, ruta absoluta que rompe el subpath, divergencia byte a byte del snapshot y archivo extra. `publish` depende de `validate`; en su job, un error del script detiene la ejecución antes de subir/desplegar `dist`.
- Las pruebas de publicación comprueban las rutas raíz y `/WebRutaSistemas/`, demostraciones opt-in y degradación segura. No se afirmó una comprobación visual nueva ni una ejecución remota de Actions.

En el cierre integrado P10 del 2026-10-27 se ejecutaron `python -m unittest` (54 aprobadas), `python scripts/build_catalog.py --check`, `python scripts/validate_catalog.py`, `python scripts/validate_candidates.py data/candidates/inbox.example.json`, `node --check app.js`, `node --test tests/catalog_ui.test.cjs`, `git diff --check` y `python scripts/pages_artifact.py` con staging temporal; pasaron. El staging contenía exactamente los cuatro archivos permitidos. Los SHA-256 antes/después fueron iguales para semilla (`772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6`), snapshot (`13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05`) y SQLite local ignorado (`B5A14B99F598281892D00FD14C41EC991AD589A67C658E8F8D30DD0ACDAF5A37`); las pruebas no alteraron esos archivos. El intento de servir el artefacto por HTTP loopback no pudo abrir socket (`WinError 10013`, acceso no permitido), por lo que HTTP real, navegador y vista móvil no se verificaron. En las comprobaciones de solo lectura de este cierre, `git ls-remote` volvió a fallar con `getaddrinfo() thread failed to start`, Pages y Rentry no fueron accesibles y Actions respondió `Cache miss`; no hay verificación remota actual.

### Decisión y revisión humana antes de release

**Candidato técnicamente coherente para revisión, no autorizado ni publicado.** El lote amplio incluye cambios de soporte local y documentación además de los necesarios para Pages; no existe base histórica suficiente para presumir que cada cambio ambiguo debe integrarse. La persona responsable debe revisar el diff completo, confirmar qué pares/grupos conserva (en especial `server.py` con su prueba), excluir base de datos, cachés, `node_modules`, bandeja local y temporales, y decidir si el lote completo es propio y deseado. El workflow solo publica cuatro archivos; no copiar seed, documentos, scripts, base SQLite ni pruebas al artefacto.

Secuencia posterior, solo tras autorización expresa de integración/publicación: (1) actualizar/verificar referencias remotas y revisar cambios entrantes; (2) confirmar propiedad y alcance del diff, sin `reset`/limpieza; (3) seleccionar conscientemente los archivos coherentes y revisar el staged diff; (4) ejecutar suite, validadores, `--check` y prueba del artefacto sobre ese mismo candidato; (5) aprobar commit/push a `main`, sabiendo que activa Pages; (6) inspeccionar el resultado real de Actions y comprobar en navegador el HTML y JSON publicados. Si hay divergencia remota, resolverla antes de integrar sin forzar sobrescritura.

La publicación del sitio y la autorización para reutilizar datos de una fuente son decisiones separadas. SERVIR/FISI continúan pendientes y deshabilitadas; no se incorporaron vacantes reales. No hubo staging, commit, push, despliegue ni cambio remoto en esta revisión.

## 33. Cierre P11: release local y preparación editorial (2026-10-27)

- **Revisión del checkout:** se mantiene `main` en `19cf942e2829833ee95ae3af177f4a44aea3566a`; 16 rastreados modificados, 18 sin seguimiento y cero staged. No se detectaron cambios nuevos de código desde la validación P10. Se preservó el lote completo; la procedencia por fase/autor no puede inferirse del historial local.
- **Unidad técnica:** seed → generador/validadores → snapshot schema 2 → frontend → pruebas/workflow siguen coherentes. La prueba de artefacto prepara el mismo `dist` que consume Pages y comprueba su lista exacta de cuatro archivos. La suite ejecutada en el cierre inmediatamente anterior aprobó 54 pruebas; generador, validadores, Node y diff check también pasaron. No se cambió código ni catálogo durante P11.
- **Integridad:** la semilla y snapshot siguen sincronizados; cinco fichas demostrativas, cero oportunidades reales activas. SERVIR y FISI-UNMSM permanecen `pending_review`, apagadas y con cero solicitudes. El buzón local no existe en este checkout; el ejemplo vacío valida. SQLite ignorado se mantuvo sin cambios. El procedimiento manual ya está documentado en `data/candidates/README.md`: candidato no publica, validación solo lectura y traslado humano explícito a la semilla.
- **Piloto real:** no hay una oportunidad elegible comprobada ni autorización confirmada para reutilización pública de fuentes. No se hicieron consultas, scraping ni contactos. El flujo editorial es suficiente técnicamente; su uso con datos reales queda bloqueado por evidencia y decisión humana, no por falta de CMS o backend.
- **Estado remoto:** las URLs de Rentry y Pages no fueron accesibles en esta nueva comprobación. `git ls-remote` continuó fallando con `getaddrinfo() thread failed to start`, y la consulta de Actions devolvió `Cache miss`. La divergencia de producción no queda resuelta ni confirmada de nuevo; la última observación verificable sigue siendo la de P9.
- **Prueba local de red:** se intentó servir el artefacto mediante el módulo HTTP estándar, pero Windows impidió abrir el socket con `WinError 10013`. Por ello no se afirma verificación HTTP ni visual/móvil; permanecen válidas solo las pruebas deterministas de rutas y contrato.
- **Etapas:** (1) consolidación/validación local, completada para este lote; (2) revisión y autorización de integración, pendiente; (3) publicación y verificación remota, pendiente por autorización y acceso; (4) autorización de fuente, pendiente; (5) primera oportunidad real y piloto manual, bloqueados por 4 y por revisión individual; (6) medición de utilidad, posterior al piloto.

**Siguiente acción de mayor impacto:** revisión humana del diff acumulado y decisión explícita de autorizar o no la integración/publicación. Tras una publicación autorizada, verificar Actions y Pages. En paralelo, una persona responsable debe decidir si envía las consultas institucionales; solo una respuesta documentada sobre acceso, conservación, atribución y reutilización pública permitirá seleccionar una oportunidad real y ejecutar el piloto editorial. Ninguna etapa remota o de ingesta se considera completada por esta preparación local.

## 34. Cierre P12: validación del release y preparación del piloto (2026-10-27)

- **Estado Git:** rama `main`, `HEAD` `19cf942e2829833ee95ae3af177f4a44aea3566a`; lote acumulado sin staging: 16 archivos rastreados modificados y 18 no rastreados. No se atribuyó el lote a autorías/fases que el historial no registra, ni se descartó ningún cambio. No hubo commit, push o despliegue.
- **Resultado técnico:** sin defectos reproducibles nuevos en la cadena seed → generador/validadores → snapshot → frontend → workflow. Por eso no se modificó código. `scripts/pages_artifact.py` preparó en temporal un artefacto validado con exactamente los cuatro archivos públicos; el workflow valida antes de cargarlo/desplegarlo. No se incluyeron documentos, buzones, SQLite ni temporales.
- **Validaciones P12:** `python -m unittest` (54 aprobadas), `python scripts/build_catalog.py --check`, `python scripts/validate_catalog.py` (válido con advertencias esperadas para demos/no activas), `python scripts/validate_candidates.py data/candidates/inbox.example.json`, `node --check app.js`, `node --test tests/catalog_ui.test.cjs`, `git diff --check` y preparación de artefacto; pasaron. `git diff --check` solo emitió advertencias de conversión LF/CRLF. Los hashes del seed, snapshot y SQLite local permanecieron en `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6`, `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` y `B5A14B99F598281892D00FD14C41EC991AD589A67C658E8F8D30DD0ACDAF5A37`; no se modificaron. `inbox.local.json` no existe en este checkout.
- **Contrato editorial:** la guía existente requiere fuente y autorización de uso público, `sourceUrl` separado de `applyUrl`, evidencia por campo, fecha de comprobación, revisión humana con responsable/fecha/motivo y traslado manual tras validar. El validador es de solo lectura y `approved_for_catalog` no publica. No hace falta CMS ni backend para una primera incorporación manual. La guía se verificó con la bandeja de ejemplo, no con una oferta real.
- **Datos y fuentes:** catálogo schema 2, cinco registros `demonstration`, cero oportunidades reales activas. SERVIR y FISI siguen `pending_review`, deshabilitadas y con cero solicitudes. No hay autorización documentada ni oportunidad real evaluada; no se ejecutó ingesta ni se inventaron métricas de piloto.
- **Remoto y visual:** durante las comprobaciones más recientes Rentry y Pages no fueron accesibles; `git ls-remote` falló con `getaddrinfo() thread failed to start`, Actions respondió `Cache miss`. El último estado público comprobable continúa siendo el documentado en P9, no una observación actual. La prueba HTTP loopback está bloqueada por `WinError 10013`; la inspección visual/móvil y la ejecución remota no están verificadas.
- **Etapas:** (1) consolidación local, validada; (2) revisión/autorización de integración, pendiente; (3) publicación y comprobación remota, pendiente; (4) autorización de fuente, pendiente; (5) primera oportunidad y piloto manual, bloqueados por evidencia/autorización; (6) medición del valor, posterior al piloto.

**Siguiente acción única:** una persona responsable revisa el diff acumulado y decide explícitamente si autoriza la integración/publicación. Después de una publicación autorizada se verifica Actions y Pages. El piloto real sigue dependiendo, por separado, de una respuesta documentada sobre permisos de uso público y de una oportunidad cuya vigencia y canal de postulación se comprueben individualmente.

## 35. Cierre P13: verificación local y camino al piloto (2026-10-27)

- **Estado local comprobado:** `main` en `19cf942e2829833ee95ae3af177f4a44aea3566a`; 16 archivos rastreados modificados, 18 sin seguimiento, ninguno staged. No hubo cambios de código respecto a P12 ni se atribuyó autoría/fase al lote acumulado. La única modificación de este bloque es esta actualización de roadmap.
- **Validación ejecutada:** `python -m unittest` (54 aprobadas), `python scripts/build_catalog.py --check`, `python scripts/validate_catalog.py` (válido con advertencias por fichas demostrativas/no activas), `python scripts/validate_candidates.py data/candidates/inbox.example.json`, `node --check app.js`, `node --test tests/catalog_ui.test.cjs`, `git diff --check` y `python scripts/pages_artifact.py --output <temporal>`; todos pasaron. El temporal validado contenía solo `index.html`, `app.js`, `styles.css` y `data/opportunities.json`, y se eliminó al terminar.
- **No mutación:** SHA-256 antes/después: seed `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6`, snapshot `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` y SQLite local ignorado `B5A14B99F598281892D00FD14C41EC991AD589A67C658E8F8D30DD0ACDAF5A37`; iguales. La bandeja local no existe. El catálogo mantiene schema 2, cinco demostraciones y cero oportunidades reales activas.
- **Flujo editorial:** se considera listo para un caso manual, no probado con una oportunidad real. La guía exige procedencia autorizada, evidencia por campo, empleador/publicador diferenciados, enlace de postulación independiente, verificación humana reciente, decisión registrada y transferencia explícita después de validar. El candidato y el validador no modifican el seed ni el snapshot.
- **Fuentes:** SERVIR y FISI continúan `pending_review`, deshabilitadas y con presupuesto de solicitudes cero. No hay autorización de reutilización pública ni una oportunidad real verificada; no hubo extracción ni contacto externo.
- **Remoto:** el intento de `git ls-remote origin HEAD refs/heads/main` falló con `getaddrinfo() thread failed to start`. Las comprobaciones previas recientes encontraron Rentry/Pages inaccesibles y Actions con `Cache miss`; no hay evidencia nueva de publicación. La divergencia solo puede cerrarse tras una integración autorizada y una comprobación observable del HTML/JSON públicos y del workflow real.
- **Visual/HTTP:** no se volvió a intentar el servidor local; el último intento falló con `WinError 10013`, así que HTTP loopback, inspección visual y vista móvil siguen no verificables. Las pruebas deterministas sí cubren resolución de rutas en raíz y `/WebRutaSistemas/` y errores de carga.
- **Fases:** consolidación local validada; revisión/autorización de integración pendiente; publicación/confirmación remota pendiente; autorización de fuente pendiente; piloto con oportunidad real pendiente; medición de utilidad aún no iniciada.

**Siguiente acción:** revisión humana del diff acumulado y decisión expresa sobre integrar/publicar. Si se autoriza, validar ese conjunto, publicarlo por el workflow existente y confirmar Actions, HTML y JSON públicos. En paralelo, la primera oportunidad requiere permiso documentado de reutilización y revisión editorial individual; esta dependencia no habilita automatización.

## 36. P14: integración local autorizada y publicación pendiente

- **Base verificada:** `main` en `19cf942e2829833ee95ae3af177f4a44aea3566a`, 16 archivos rastreados modificados y 18 nuevos antes del staging; no había cambios staged iniciales. Se preservó el lote. El paquete seleccionado comprende 34 archivos de aplicación/datos, validación, fuentes apagadas, workflow/pruebas, prototipo local con su prueba y documentación enlazada; se excluyeron SQLite, `node_modules`, cachés, buzón local (no existe) y temporales.
- **Pruebas antes de commit:** `python -m unittest` (54 aprobadas), generador `--check`, validadores de catálogo/candidatos, `node --check`, test UI Node, `git diff --check` y generación/validación del artefacto; pasaron. El catálogo da las advertencias esperadas por fichas de demostración/no activas. El artefacto temporal contiene exactamente los cuatro archivos públicos. Seed, snapshot y SQLite conservaron sus hashes. El staging explícito se revisó; `git diff --cached --check` pasó después de normalizar finales de línea/documentación nuevos. No se detectaron los patrones acotados de correo personal conocido ni tokens GitHub.
- **Datos y fuentes:** schema 2, cinco demostraciones y cero oportunidades reales activas. SERVIR/FISI continúan `pending_review`, `enabled: false`, `maxRequestsPerRun: 0`. No hubo consulta ni se incorporaron ofertas.
- **Remote/push:** una consulta de lectura `git ls-remote origin HEAD refs/heads/main` falló con `getaddrinfo() thread failed to start`; Pages y Actions tampoco fueron accesibles desde las herramientas de lectura (Actions devolvió `Cache miss`). Al no poder confirmar el HEAD remoto no se ejecutó push para evitar sobrescribir una posible divergencia. El commit local autorizado puede conservarse, pero no equivale a integración remota ni resuelve la divergencia de producción.
- **Inspección visual:** no verificada; la última prueba de servidor HTTP local falló al abrir loopback (`WinError 10013`).
- **Estado:** validación y staging local completados; commit local pendiente de la confirmación final del staging, push pendiente por lectura remota bloqueada; Actions/Pages y piloto real pendientes. La fuente externa requiere autorización documental independiente.

**Siguiente paso:** con el commit local ya creado, reintentar lectura de `origin/main`; solo si la actualización es fast-forward segura, hacer push autorizado y verificar el workflow, HTML/JSON y vista pública. La primera oportunidad requiere además autorización de reutilización de una fuente y validación editorial individual.

## 37. P14: publicación y verificación de producción (2026-10-28)

- **Integración:** el commit `0b1569a795d4c5d56a39b49b03e1421423e5bf37` (`Integrate validated static catalog release`) se publicó en `main` mediante fast-forward desde `19cf942e2829833ee95ae3af177f4a44aea3566a`. `git ls-remote` confirmó que `refs/heads/main` apunta al mismo SHA. No se usó force push.
- **CI:** el run de GitHub Actions `40697857260`, disparado por push al SHA esperado, terminó `success`; los jobs `validate` y `publish` terminaron correctamente. El run expuso el artefacto `github-pages` (18,435 bytes). No se ejecutaron fuentes ni recolección.
- **Pages:** respuestas HTTP 200 para la página, `app.js`, `styles.css` y `data/opportunities.json` en `/WebRutaSistemas/`. El JSON público es schema 2 y contiene cinco registros, todos `recordKind: demonstration`; no hay oportunidad real activa. Los registros están históricos, no confirmados o con verificación stale. El HTML/DOM expone el estado vacío predeterminado (0 activas verificadas) y la casilla explícita para incluir demostraciones. Con esa casilla activada aparecen cinco ejemplos con etiqueta de demostración; su detalle mantiene deshabilitada la postulación y diferencia la ficha informativa. El JavaScript público no contiene la ruta `/api/opportunities`.
- **Interfaz:** comprobación visual real de escritorio y lectura del árbol accesible en Pages. Se verificaron estado vacío, contador cero, activación de ejemplos y detalle demostrativo sin CTA de postulación. No se hizo validación móvil con viewport reducido ni prueba visual de estados HTTP de error.
- **Validación local tras integrar:** `python -m unittest` (54 aprobadas); `python scripts/build_catalog.py --check` (paridad correcta); `python scripts/validate_catalog.py` (válido, con advertencias esperadas para datos demostrativos/no activos); `python scripts/validate_candidates.py data/candidates/inbox.example.json` (válida, cero candidatos); `node --check app.js`; `node --test tests/catalog_ui.test.cjs` (1 suite aprobada, incluye rutas raíz/subpath y degradación); `git diff --check`. No se modificaron seed ni snapshot en esta verificación.
- **Etapas:** integración y commit completados; push, Actions y publicación verificados para el SHA indicado. Inspección móvil pendiente. SERVIR y FISI continúan pendientes de autorización y deshabilitadas; no existe primera oportunidad real ni piloto editorial medido.

**Siguiente hito:** obtener y registrar autorización documentada para reutilización pública de una fuente concreta; después, curar manualmente una oportunidad real con evidencia vigente y medir tiempo, completitud y conflictos antes de ampliar cobertura. La autorización de fuentes es independiente del release técnico ya publicado.

## 38. P15: rediseño UX/UI y build estático con Tailwind (2026-10-28)

- **Estado inicial:** `main` limpio en `e6633e0a803ff6018f308432cd8d339b27705bc2`; P14 ya estaba publicado y verificado. No existía `package.json`, Tailwind ni un build CSS. El frontend cargaba `styles.css` propio. ADR-001 registraba la decisión anterior de evitar CLI hasta justificarlo; P15 aporta ese uso concreto para compilar la nueva interfaz.
- **Dirección de producto:** se tomó de Sequence únicamente la jerarquía clara, el ritmo/espaciado y la composición de producto sobria; no se copiaron marca, textos ni secciones. La interfaz prioriza explorar/evaluar oportunidades, no vender un SaaS. Se mantiene paleta verde bosque y neutros, escala tipográfica legible, estados de confianza expresados con texto, filtros y tarjetas escaneables, detalle editorial y responsividad. Se evita cargar fuentes remotas.
- **Tailwind:** integración OSS MIT `tailwindcss` y `@tailwindcss/cli` fijados ambos en 4.3.3 mediante `package-lock.json`. `src/input.css` importa Tailwind, declara tokens y escanea HTML/JS; `src/site.css` es la fuente de componentes. `npm ci && npm run build:css` produce el `styles.css` estático versionado; `npm run watch:css` sirve para desarrollo. Pages no descarga Tailwind ni depende de runtime externo. El workflow instala Node 22 y compila antes de pruebas, y vuelve a compilar en `publish` antes del empaquetado; el path filter incluye lockfile y fuentes.
- **Cambios:** renovados `index.html` y estilos para navegación, introducción, métricas, filtros, lista/detalle, confianza y estado vacío; utilidades Tailwind y CSS compilado permanecen compatibles con rutas relativas de Pages. Se ajustó una aserción de contrato para comprobar el breakpoint móvil compilado, y se añadió una prueba estática que exige versiones fijadas y compilación del workflow. README y ADR-001 documentan los comandos y la decisión.
- **Validaciones:** `npm ci` (33 paquetes, cero vulnerabilidades reportadas); `npm run build:css`; `python -m unittest` (55 aprobadas); `python scripts/build_catalog.py --check`; `python scripts/catalog_quality.py`; `python scripts/validate_catalog.py` (válido, advertencias esperadas por las demostraciones); `python scripts/validate_candidates.py data/candidates/inbox.example.json`; `node --check app.js`; `node --test tests/catalog_ui.test.cjs`; 7 pruebas de `tests.test_pages_artifact`; `git diff --check`. El artefacto temporal se comprobó con exactamente `index.html`, `app.js`, `styles.css` y `data/opportunities.json`, y se eliminó. La primera prueba detectó una aserción ligada al formato anterior de CSS; fue actualizada al breakpoint presente y la suite pasó después.
- **Datos y seguridad:** semilla y snapshot no cambiaron; se mantienen cinco demostraciones y cero oportunidades reales activas. No se tocó la bandeja local ni se activaron fuentes. No se añadieron dependencias de producción.
- **Inspección visual:** el intento de abrir servidor local falló porque Windows denegó el socket de loopback (`WinError 10013`); el navegador también bloqueó la URL `file:` por política. La validación visual del checkout local y de móvil queda pendiente; no se presenta como completada. Pruebas automatizadas verifican el contrato y breakpoints, no el aspecto real en móvil.
- **Publicación:** estos cambios aún requieren commit/push y una ejecución de CI para afirmar que Pages los sirve. El sitio público previo no representa este rediseño hasta confirmar el nuevo CSS/HTML. GitHub Actions compilará los mismos fuentes con lockfile y debe completar validación antes de publicación.

**Siguiente hito:** integrar este rediseño solo tras revisión final del diff y fast-forward seguro; confirmar Actions, recursos públicos y la UI en escritorio/móvil. La primera oportunidad real permanece separada y condicionada a autorización de fuente y revisión editorial individual.

## 39. P15: verificación de producción del rediseño (2026-10-28)

- **Release:** `dd40e73f8482eb3f25051c97ec05ee6cc2e1900c` (`Redesign catalog experience with compiled Tailwind CSS`) está en `main`; push fast-forward confirmado y checkout limpio al comprobarlo. Actions run `40703125923` del SHA exacto terminó `success`; `validate` y `publish` completaron correctamente.
- **Pages:** HTTP 200 en `/WebRutaSistemas/`, `app.js`, `styles.css` y `data/opportunities.json`. HTML contiene el nuevo mensaje introductorio; CSS publicado incluye el build Tailwind 4.3.3. El JSON conserva schema 2 y cinco demostraciones, con cero reales activas. No hay API runtime; el estado vacío, filtros y ejemplos optativos aparecieron en el DOM.
- **Inspección visual:** se revisó el sitio publicado en escritorio: jerarquía de portada, panel de principios, resumen, filtros, estado vacío y tarjetas tras activar demostraciones. El detalle y la prueba de postulación deshabilitada permanecen cubiertos por pruebas previas/DOM; los ejemplos se muestran como demostrativos. La vista móvil con viewport reducido no fue ejecutada. El servidor local continuó bloqueado por permisos de socket, por lo que la revisión visual fue en Pages tras el despliegue, no local.
- **Integridad:** seed y snapshot no se modificaron; workflow produjo la versión bajo prefijo Pages. Fuentes SERVIR/FISI siguen deshabilitadas y pendientes de autorización.
- **Continuidad:** el rediseño y su publicación técnica están verificados. La comprobación móvil queda como brecha visual pequeña; no bloquea la arquitectura ni la cadena de release. La primera oportunidad real continúa pendiente de permiso de reutilización pública y revisión editorial individual.

**Siguiente hito:** validar visualmente los flujos de búsqueda/filtros a viewport móvil y, en paralelo solo cuando se obtenga autorización humana de fuente, curar una oportunidad real. No añadir más fuentes o automatización antes de medir ese primer caso.
