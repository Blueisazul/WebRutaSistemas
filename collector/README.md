# Ingesta de fuentes — diseño actual

La decisión para un proyecto sin presupuesto es **no instalar un crawler en el MVP**. Las primeras fichas se curan a partir de fuentes oficiales; el catálogo/API local y la interfaz ya funcionan con herramientas incluidas en Python y SQLite.

## Adaptadores existentes

`ats_connectors.py` contiene lectores mínimos para los endpoints públicos de Greenhouse y Lever. `policy.py` impide consultar fuentes desconocidas, apagadas, no aprobadas, fuera de los hosts autorizados o sobre el presupuesto. El registro en `sources.json` mantiene todo apagado por defecto. Los conectores retienen metadatos, no descripciones completas; sus resultados nacen sin confirmación de vigencia.

Antes de usar un conector, hay que identificar el empleador y su tablero, verificar términos/derechos de reutilización y alojar el anuncio original en una URL permitida. La documentación de una API pública facilita acceso técnico; no resuelve por sí sola la licencia de republicar sus anuncios.

## Actualización programada

`.github/workflows/refresh-catalog.yml` despliega cambios de la web al subirlos a `main`; además corre semanalmente (lunes, 10:17 a. m. hora de Perú/Colombia) y permite ejecución manual. `python -m collector.refresh_catalog` consulta solo fuentes `enabled` que pasen la política fail-closed, mezcla los resultados con la muestra curada, y conserva los registros anteriores que ya no aparezcan como “no verificados” para evitar borrarlos en silencio. Si cualquier fuente aprobada falla, la ejecución termina sin tocar/publicar el catálogo. Cuando hay cambios, Actions guarda el JSON en `main` para que la próxima corrida tenga el historial anterior y luego publica el sitio. El flujo no publica nada si todavía no hay fuentes activadas o si no hay cambios.

Las fuentes del registro permanecen apagadas. Antes de activar una, completa sus campos de empleador/tablero y registra una revisión real de términos y derechos; el sistema rechaza los estados `pending`. Un registro encontrado en el ATS confirma presencia en el tablero oficial al momento de consulta, pero no evalúa funciones, requisitos, sueldo, beneficios ni proyección. Esos campos quedan como no especificados o pendientes de revisión; una persona debe completar la evaluación antes de presentar la oportunidad como recomendada.

### Primera cohorte investigada

- **Interbank:** portal oficial de carreras alojado en HiringRoom; sus filtros muestran ubicación y modalidad. La API pública de HiringRoom documentada requiere credenciales de cuenta para integraciones, así que no se debe asumir que ese portal ofrece una API pública de lectura para terceros. Empezar con seguimiento del portal oficial y pedir autorización/API antes de automatizar. [Portal de Interbank](https://interbank.hiringroom.com/jobs), [documentación API de HiringRoom](https://github.com/hiringroom/api-hr-doc).
- **BCP:** la página oficial describe prácticas/Talento Joven, beneficios y enlace al portal de empleos. Es una fuente prioritaria para revisión manual; aún no hay un endpoint público aprobado/configurado en este repositorio. [Trabaja en el BCP](https://www.viabcp.com/unete-al-equipo-bcp), [Talento Joven BCP](https://www.viabcp.com/unete-al-equipo-bcp/talento-joven).
- **Scotiabank:** mantiene página global de carreras y oportunidades de Ingeniería/programas para estudiantes; el sitio por sí solo no acredita un feed reutilizable. Incluirlo en la revisión manual y automatizar solo cuando haya una interfaz oficial autorizada. [Carreras Scotiabank](https://www.scotiabank.com/careers/es/carreras.html), [Ingeniería](https://www.scotiabank.com/careers/es/carreras/ingenieria.html).

Por eso el primer flujo técnico queda preparado para Greenhouse/Lever, pero estos tres bancos no se fuerzan dentro de conectores incompatibles. La cohorte inicial combina seguimiento manual de fuentes bancarias oficiales con cualquier portal ATS que publique un feed accesible y cuyos términos permitan el uso previsto.

Para que Actions publique en GitHub Pages, configura una vez el repositorio en **Settings → Pages → Build and deployment → Source: GitHub Actions**. La publicación incluye solo `index.html`, `app.js`, `styles.css` y el JSON del catálogo. Se puede iniciar manualmente desde **Actions → Refresh jobs catalog → Run workflow**. Mientras no se apruebe y configure al menos una fuente, las corridas programadas serán intencionalmente un no-op: no fabricarán actualizaciones ni consultarán portales. El permiso `contents: write` se usa solo para versionar el JSON cuando sí cambia; el flujo de despliegue no guarda cuentas, perfiles ni datos de postulantes.

## Cuándo reutilizar un crawler

Si aparecen fuentes HTML autorizadas que no exponen una API, **Scrapy** (BSD-3-Clause) es el candidato coherente con el backend Python y se ejecuta bajo nuestra infraestructura. Primero medir si hace falta: no se instala ahora, no se rastrean agregadores masivamente y no se omiten CAPTCHA, inicio de sesión, bloqueos ni límites.

No se propone desplegar Firecrawl: para el catálogo pequeño añade servicios y mantenimiento que no necesitamos, aunque sea open source y autohospedable. Tampoco se justifica mantener simultáneamente Scrapy, Crawlee y Crawl4AI. La interfaz de adaptador, el esquema canónico, la deduplicación, la revisión y la evidencia siguen siendo propios y reemplazables.

## Seguridad operativa

- Mantener `enabled: false` hasta completar revisión individual.
- Un rechazo HTTP, redirección o exceso de límite detiene la captura; no seguir enlaces externos.
- Aplicar pausas respetuosas, límites de respuesta/tiempo y revisión humana.
- Tratar fecha de captura y publicación como distintas; no marcar una oferta “activa” solo porque la API la devuelve.
- No guardar CV, postulaciones, HTML bruto ni el texto completo de la convocatoria en este piloto.
