# Ingesta de fuentes — diseño actual

La decisión para un proyecto sin presupuesto es **no instalar un crawler en el MVP**. Las primeras fichas se curan a partir de fuentes oficiales; el catálogo/API local y la interfaz ya funcionan con herramientas incluidas en Python y SQLite.

## Adaptadores existentes

`ats_connectors.py` contiene lectores mínimos para los endpoints públicos de Greenhouse y Lever. `policy.py` impide consultar fuentes desconocidas, apagadas, no aprobadas, fuera de los hosts autorizados o sobre el presupuesto. El registro en `sources.json` mantiene todo apagado por defecto. Los conectores retienen metadatos, no descripciones completas; sus resultados nacen sin confirmación de vigencia.

Antes de usar un conector, hay que identificar el empleador y su tablero, verificar términos/derechos de reutilización y alojar el anuncio original en una URL permitida. La documentación de una API pública facilita acceso técnico; no resuelve por sí sola la licencia de republicar sus anuncios.

## Cuándo reutilizar un crawler

Si aparecen fuentes HTML autorizadas que no exponen una API, **Scrapy** (BSD-3-Clause) es el candidato coherente con el backend Python y se ejecuta bajo nuestra infraestructura. Primero medir si hace falta: no se instala ahora, no se rastrean agregadores masivamente y no se omiten CAPTCHA, inicio de sesión, bloqueos ni límites.

No se propone desplegar Firecrawl: para el catálogo pequeño añade servicios y mantenimiento que no necesitamos, aunque sea open source y autohospedable. Tampoco se justifica mantener simultáneamente Scrapy, Crawlee y Crawl4AI. La interfaz de adaptador, el esquema canónico, la deduplicación, la revisión y la evidencia siguen siendo propios y reemplazables.

## Seguridad operativa

- Mantener `enabled: false` hasta completar revisión individual.
- Un rechazo HTTP, redirección o exceso de límite detiene la captura; no seguir enlaces externos.
- Aplicar pausas respetuosas, límites de respuesta/tiempo y revisión humana.
- Tratar fecha de captura y publicación como distintas; no marcar una oferta “activa” solo porque la API la devuelve.
- No guardar CV, postulaciones, HTML bruto ni el texto completo de la convocatoria en este piloto.
