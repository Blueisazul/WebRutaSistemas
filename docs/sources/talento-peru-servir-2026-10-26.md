# Evaluación de fuente: Talento Perú / SERVIR

- **Fecha de revisión:** 2026-10-26
- **ID local:** `talento-peru-servir`
- **Entidad:** Autoridad Nacional del Servicio Civil (SERVIR)
- **Decisión:** `pending_review`
- **Automatización:** deshabilitada (`enabled: false`, presupuesto de solicitudes `0`)

## Evidencia oficial consultada

1. La [página de Talento Perú en gob.pe](https://www.gob.pe/institucion/servir/campañas/4782-talento-peru) identifica a SERVIR como responsable y describe el portal como medio de difusión de ofertas laborales y prácticas de entidades públicas. Indica que las convocatorias se publican simultáneamente en Talento Perú y en la web institucional, y enlaza al portal y a material de usuario. La página no documenta una API pública, feed, licencia de reutilización de fichas, ni autorización para extracción automatizada por terceros.
2. Las [preguntas frecuentes oficiales de SERVIR (PDF)](https://cdn.www.gob.pe/uploads/document/file/3291482/Preguntas%20frecuentes%20sobre%20Talento%20Per%C3%BA.pdf) explican que las personas consultan la convocatoria en Talento Perú y luego postulan en la web de la entidad. Esto hace que Talento Perú sea una vía de descubrimiento; no prueba que la ficha del portal sea la autoridad del canal de postulación ni confirma su vigencia actual.
3. En la consulta de esta evaluación, la herramienta de navegación no pudo acceder al portal `talentoperu.servir.gob.pe` ni a su `robots.txt`. Esto es una limitación observable del entorno, no evidencia de que el portal esté caído o de que prohíba acceso. No se obtuvo respuesta técnica del servicio ni se ejecutó scraping.
4. El [directorio oficial de canales de consulta de SERVIR](https://www.gob.pe/institucion/servir/informes-publicaciones/6182394-directorio-de-plataformas-para-canales-de-atencion-de-consultas) lista “Búsqueda de empleos y prácticas en el Estado — Talento Perú” y enlaza la [aplicación de consulta pública](https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml). Esto confirma un mecanismo oficial de consulta humana, no una API ni permiso de automatización/reutilización. La herramienta de navegación recibió HTTP 403 al abrir esa aplicación; no se infiere que el servidor origine el 403 ni que el uso humano esté denegado.
5. SERVIR publica `talentoperu@servir.gob.pe` y el teléfono (01) 206-3370, anexos 2519 (empleos) y 2616 (prácticas). Su [nota institucional sobre Talento Perú](https://www.servir.gob.pe/servir-lanza-unico-portal-de-ofertas-de-empleos-y-practicas-en-el-estado-talento-peru/) también publica el correo para consultas sobre el portal.

## Calificación para el uso propuesto

| Aspecto | Resultado |
|---|---|
| Fuente oficial / responsable | Confirmado por SERVIR en gob.pe |
| Mecanismo consultable | Directorio SERVIR enlaza una aplicación pública de consulta; API/feed oficial no identificado. Interacción automática y estabilidad no comprobadas |
| Condiciones de acceso y reutilización | No localizadas; no se interpreta el acceso público como autorización |
| Robots / límites | No comprobados; el recurso no fue accesible desde el mecanismo de consulta |
| Campos | La página oficial describe el propósito del portal, pero no se comprobó el esquema/cobertura de fichas. No se conserva contenido de convocatorias |
| Postulación | SERVIR indica que se continúa en la página de cada entidad; la URL del empleador tendría que ser identificada y verificada individualmente |
| Frecuencia | Ninguna autorizada. Presupuesto configurado en cero mientras la decisión esté pendiente |
| Atribución / retención / retirada | Pendientes de confirmar con SERVIR. Por ahora conservar solo URLs de referencia de documentación oficial en el registro de evaluación |
| Correcciones y bajas | Pendiente. Una respuesta HTTP o presencia en el portal no determinaría por sí sola estado abierto |
| Contacto institucional | `talentoperu@servir.gob.pe`, publicado por SERVIR; borrador de consulta preparado, no enviado |

## Decisión y siguiente condición

La fuente **no queda aprobada ni rechazada**: `pending_review` porque las páginas oficiales consultadas no resuelven el permiso de automatización, almacenamiento y reutilización necesario para el piloto. No se selecciona otra institución de manera implícita. Tampoco se construye conector ni se consulta el portal en automático.

Para reconsiderar la decisión, solicitar a SERVIR confirmación escrita sobre: (1) API/feed o mecanismo permitido de consulta automatizada; (2) reutilización de metadatos mínimos y atribución; (3) frecuencia y límites; (4) retención, corrección y retirada; (5) enlace canónico y relación entre la ficha de Talento Perú y el canal vigente de postulación de cada entidad. Si la respuesta habilita un piloto, iniciar con una muestra manual de hasta 10 registros y mantenerla en staging separado del catálogo canónico.

## Métricas del piloto

No se ejecutó piloto de extracción, pues faltan condiciones de uso y mecanismo autorizados. Registros encontrados / parseados: **no medidos**; completitud, duplicados, fechas/enlaces ambiguos y errores de extracción: **no medidos**. Mantenimiento observado: **no medido**. No deben interpretarse como cero ni como fallo del portal.

## Alternativa institucional evaluada: FISI-UNMSM

Talento Perú no tiene evidencia suficiente para habilitar la ingesta, así que se revisó una sola alternativa: la Facultad de Ingeniería de Sistemas e Informática de la UNMSM, `https://sistemas.unmsm.edu.pe/`.

- La [web oficial de FISI](https://sistemas.unmsm.edu.pe/) muestra secciones de “Oportunidad Laboral” y títulos de convocatorias, incluidas prácticas y puestos técnicos. La [publicación de prácticas de GM Ingenieros](https://sistemas.unmsm.edu.pe/site/noticias/35-importante/1844-convocatoria-para-practicas-preprofesionales-gm-ingenieros-y-consultores-s-a-c) ilustra que el portal puede difundir anuncios de terceros, por lo que no se debe tratar a la facultad como empleador ni asumir que controla el cierre/postulación.
- La página de portada consultada mediante índice de búsqueda confirma que el mecanismo es una web de noticias, pero no se encontró API/feed ni términos explícitos de automatización, reutilización o retención. La apertura directa de una publicación falló con HTTP 502 desde el navegador de investigación y `robots.txt` no estuvo accesible. Esto no demuestra una caída o prohibición.
- **Decisión:** `pending_review` para extracción automatizada. Queda como siguiente alternativa identificada, pero no autorizada. Solo pueden utilizarse enlaces para revisión manual interna una vez que se pueda consultar directamente cada publicación; no se importaron ni copiaron fichas a los datos del proyecto.
- **Frecuencia y conservación:** automatización cero, sin retener HTML ni descripción. Antes de reconsiderar, solicitar a la facultad confirmación sobre consulta automatizada, reutilización de metadatos mínimos, atribución, frecuencia, corrección/retirada y fuente real de postulación.
- **Muestra/métricas:** no se ejecutó piloto. La búsqueda permitió observar encabezados de oportunidades, pero no una muestra reproducible validable; registros parseados, completitud, fechas ambiguas y duplicados quedan **sin medir**.

La alternativa está registrada en `collector/sources.json` como `unmsm-fisi-employment-board`, deshabilitada con presupuesto de solicitudes cero. No se crea adaptador hasta resolver la autorización y poder consultar páginas directamente.
