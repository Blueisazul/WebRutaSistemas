# ADR-001 — Catálogo curado y publicación segura

- **Estado:** Aceptado para el piloto
- **Fecha:** 2026-10-26
- **Alcance:** catálogo de lectura de Ruta Sistemas, no backend multiusuario

## Contexto

El repositorio tenía una semilla JSON, un snapshot JSON y una base SQLite local sin un flujo curatorial integrado. El colector podía generar schema 1 desde ATS y el workflow programado escribía resultados a `main`; en cambio, la UI pública lee el snapshot estático. Ninguna fuente automática está autorizada/activada. El catálogo existente es demostrativo y contiene fechas antiguas.

## Decisiones

1. **Fuente canónica:** `data/opportunities.seed.json`, versionada y editable. `data/opportunities.json` es el artefacto estático schema 2. La generación valida primero, protege IDs ya publicados contra pérdida y solo sobrescribe con el comando explícito `--write`. `--check` nunca escribe y exige igualdad del snapshot con la fuente salvo `generatedAt`.
2. **Estados separados:** `opportunityStatus`, `verificationStatus` y `publicationStatus` tienen vocabularios independientes. `recordKind: demonstration` nunca puede ser activo. Fecha límite vencida impide publicación activa, sin importar fechas de término de contrato.
3. **Frescura:** TTL piloto configurable en la fuente canónica, inicialmente siete días calendario. El plazo es una hipótesis operativa conservadora para un mercado de vacantes de alta rotación y deberá recalibrarse con mediciones. Fechas civiles se interpretan en Perú (UTC−05:00); timestamps requieren offset explícito. Falta de deadline no es prueba de vigencia: el TTL y evidencia siguen siendo necesarios.
4. **Evidencia activa:** revisión manual reciente del canal de postulación confirmado por el empleador y observado abierto (`result: application_open`), fuente y aplicación en hosts allowlisted HTTPS, evidencia enlazada/método/fecha reciente, estado abierto, sin expiración conocida y publicación no demostrativa. Presencia técnica en ATS/API no basta.
5. **Generación vs verificación:** `generatedAt` describe el archivo; `lastVerifiedAt`/`lastCheckedDate` describen consultas por ficha. Ninguno actualiza el otro.
6. **Ingesta:** conectores permanecen apagados y el comando de refresh falla cerrado si una fuente aparece habilitada. Los registros nuevos entran a la fuente canónica después de revisión humana; las fuentes no consultadas no se consideran cerradas.
7. **Despliegue:** CI valida datos, pruebas y sintaxis antes de desplegar; no hay programación, push de datos ni `contents: write`. GitHub Pages/Actions es dependencia alojada por conveniencia, no OSS/autohospedaje. Mantener paquete estático portable como salida.
8. **Frontend:** no se usa Tailwind Browser CDN. Tras el rediseño P15, Tailwind CSS CLI 4.3.3 (MIT, fijado mediante npm lockfile) compila `src/input.css` y `src/site.css` a `styles.css`. Pages sirve solo el CSS estático; no hay runtime externo. El workflow compila de forma reproducible antes de validar y empaquetar.
9. **SQLite local:** permanece como prototipo aislado, no como backend ni fuente canónica. No se implementa sincronización con JSON.
10. **Captura editorial:** las notas manuales se trabajan en `data/candidates/inbox.local.json`, ignorado por Git por defecto; `inbox.example.json` es solo una bandeja vacía validable. `scripts/validate_candidates.py` es de solo lectura y no tiene ruta de promoción/importación. Una persona debe revisar y trasladar explícitamente lo sustentado a la semilla. Las autorizaciones de consulta manual, extracción automatizada y reutilización pública se registran por separado; pendientes no pueden aprobar candidatos para catálogo.
11. **Procedencia y decisión editorial:** nuevas fichas publicables distinguen `employer` de `publisher`, `sourceUrl` de `applyUrl`, y usan `fieldEvidence` para enlazar cada hecho presentado a una fuente y fecha de observación. `editorialDecision` registra aprobación humana, revisor, fecha y motivo. Para mantener una oportunidad activa, la decisión y las evidencias de campos afirmados deben ser recientes según el TTL vigente de siete días; la generación no las renueva. Los registros rechazados permanecen en la bandeja editorial con motivo, no en el catálogo público; los retirados se conservan como históricos con razón.

## Consecuencias

- Al inicio no se muestra ninguna ficha como activa. Se preservan cinco registros de demostración: una vencida, una cerrada/histórica y tres con vigencia desconocida; todas sin verificación vigente. Las fichas se pueden incluir mediante controles explícitos.
- Las ediciones de catálogo requieren modificar semilla, regenerar explícitamente el snapshot y validar. Una diferencia manual del artefacto bloquea CI.
- La estructura es portable y sin servicios de pago, pero Pages y Actions continúan siendo servicios propietarios alojados. Una migración futura necesita infraestructura propia, HTTPS/TLS, disponibilidad, respaldos, monitoreo y responsable operativo.
- El TTL no es una garantía de disponibilidad; es un límite editorial máximo. El estado puede invalidarse por fecha límite aun antes del TTL.

## Aplazado

- Autorizar/seleccionar una fuente real y su política legal/operativa.
- Panel curatorial, autenticación, persistencia multiusuario y migración de SQLite.
- Scoring de oportunidad, perfilado, recomendaciones IA, rutas profesionales.
- Hosting autoalojado; depende de recursos operativos reales.
- Framework de crawling; Scrapy solo si una fuente autorizada supera la capacidad de un adaptador pequeño. Firecrawl y API alojada de Freehire no se incorporan.

## Revisión

Revisar esta decisión después de un piloto de una fuente y mediciones de frescura, completitud, duplicados y costo operativo, o antes si cambian las restricciones de alojamiento/datos. El roadmap vigente se mantiene en la sección 21 del documento de diseño.
