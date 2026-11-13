# P4 — Evaluación OSS y diseño condicionado de automatización

- **Fecha:** 2026-11-13
- **Estado:** preparación técnica completada; operación bloqueada
- **Dependencia:** P3 continúa bloqueado por autorización externa
- **Fuentes activas:** ninguna
- **Cambios de catálogo:** ninguno

## Decisión ejecutiva

No se instala ni se integra ninguna herramienta OSS en este bloque. P3 sigue sin
autorización escrita para consulta, automatización, conservación, atribución,
retirada, elegibilidad territorial y republicación de una oportunidad individual.
Por tanto, una herramienta que consulte páginas ahora violaría el criterio
fail-closed aunque sea técnicamente capaz o tenga licencia libre.

La unidad mínima futura, si aparece una fuente autorizada, es un adaptador
acotado que produzca candidatos offline. Debe usar primero la biblioteca estándar
existente y entregar el resultado a la bandeja editorial; no debe escribir la
semilla, el snapshot ni Pages. Scrapy solo se reconsidera si una fuente HTML
autorizada requiere navegación/paginación que el adaptador estándar no pueda
mantener de forma clara. `changedetection.io` no es una dependencia del
catálogo: es un servicio de monitorización separado y no sustituye la revisión
editorial.

## Comprobaciones del checkout

El checkout conserva `main` en `eb68ef67cbed45d03c88793750d6d6c59662cfec`, con
cambios locales P1/P2/P3 y `canvas.js` sin seguimiento. Esta evaluación no
resuelve la divergencia con `origin/main`, no hace commit y no modifica los
archivos de datos.

`package.json` fija `@tailwindcss/cli` y `tailwindcss` en `4.3.3`.
La comprobación ejecutada fue:

```text
npm ci
npm run build:css
SHA256(styles.css) antes: 1C15198F94BD234CD695FC1622A1CD2C0F03D38DF925C3AF3C1198923BFDB7A7
SHA256(styles.css) después: 1C15198F94BD234CD695FC1622A1CD2C0F03D38DF925C3AF3C1198923BFDB7A7
```

La salida fue reproducible y `npm ci` reportó cero vulnerabilidades. Persistió
únicamente el aviso operativo de `@parcel/watcher` sobre sus scripts de
instalación. No se añade ninguna dependencia.

`.github/workflows/refresh-catalog.yml` usa Node 22, Python 3.12, ejecuta
`npm ci`, compila CSS, valida antes de publicar y limita el job de validación a
`contents: read`. El job de publicación solicita solo `pages: write` e
`id-token: write`; no hay `cron`, `contents: write` ni ejecución de colectores.

## Matriz OSS-first

| Alternativa | Problema que resuelve | Licencia / coste operativo | Compatibilidad con el contrato | Decisión |
|---|---|---|---|---|
| **Adaptador Python estándar** | Consultar un API/feed autorizado, normalizar campos y escribir candidatos locales | Sin dependencia nueva; coste operativo bajo; ya existe política y validación local | Mejor ajuste: puede respetar `authorize_fetch()`, límites, HTTPS, evidencia y no promoción | **Preferir primero**, solo después de autorización |
| **Scrapy** | Crawling HTML/API con scheduler, concurrencia, selectores, pipelines y exportación | BSD-3-Clause; requiere dependencias y operación/configuración de crawler; sus capacidades incluyen concurrencia, profundidad, robots y persistencia | Puede producir JSONL, pero añade superficie y facilita sobrepasar el límite de una fuente; no resuelve derechos de republicación | **Descartar por ahora**; reevaluar solo ante complejidad HTML autorizada |
| **changedetection.io** | Detectar cambios en páginas y enviar notificaciones | Apache-2.0; servicio Python autoalojado con almacenamiento, navegador opcional y operación continua; también ofrece SaaS de pago | Detecta cambios, pero no entrega por sí solo el contrato schema 2, evidencia por campo, deduplicación ni revisión humana | **Descartar como dependencia**; podría servir como herramienta externa de observación manual, nunca como publicador |
| **Playwright** | Pruebas E2E y navegación de páginas renderizadas con JS | Apache-2.0; descarga/gestiona navegadores y aumenta el coste de CI/operación | Es apropiado para `tests/catalog_ui.test.cjs` o una prueba autorizada aislada, no para activar un colector | **Mantener fuera de ingesta**; considerar solo para validación UI si aparece una necesidad |
| **pypdf** | Extraer texto/metadatos de convocatorias PDF | BSD-3-Clause; dependencia Python adicional; la extracción puede ser imperfecta y requiere límites de tamaño | Solo sería útil para una fuente PDF autorizada; debe conservar URL, hash/fecha y evidencia, no copiar contenido completo | **No adoptar ahora**; reevaluar ante PDF autorizado real |
| **Freehire** | Descubrimiento normalizado de vacantes mediante API agregada | El código publicado declara MIT; la API permite uso personal/no comercial sin clave y producto con plan API de USD 29/mes; plan Data de USD 99/mes para volumen. Su licencia prohíbe redistribuir el dataset/feed bruto y no concede derechos que las fuentes originales no hayan dado | Reduce crawling propio, pero introduce dependencia externa, coste, contrato y una capa de agregación. El plan no resuelve elegibilidad Perú ni la revisión editorial individual | **Descartar como fuente operativa P4**; conservar solo como referencia documentada |

Fuentes consultadas: [Scrapy overview](https://docs.scrapy.org/en/latest/intro/overview.html),
[Scrapy architecture](https://docs.scrapy.org/en/latest/topics/architecture.html),
[Scrapy license](https://github.com/scrapy/scrapy/raw/master/LICENSE),
[changedetection.io](https://github.com/dgtlmoon/changedetection.io),
[changedetection.io license](https://github.com/dgtlmoon/changedetection.io/raw/master/LICENSE),
[Playwright Python](https://playwright.dev/python/docs/intro),
[Playwright license](https://github.com/microsoft/playwright-python/blob/main/LICENSE),
[pypdf documentation](https://pypdf.readthedocs.io/en/stable/),
[pypdf license](https://github.com/py-pdf/pypdf/blob/main/LICENSE),
[Freehire open catalogue](https://freehire.me/open),
[Freehire API](https://freehire.me/jobs-api) y [Freehire terms](https://freehire.me/terms).

## Diseño condicionado de la unidad mínima

La automatización futura queda condicionada a una fuente con autorización escrita
y a una decisión `approved` registrada en `collector/sources.json`.

```text
fuente autorizada
  -> authorize_fetch() fail-closed
  -> adaptador de una fuente (solo lectura, límites explícitos)
  -> candidato JSON local/offline
  -> validate_candidates.py
  -> revisión humana y evidencia por campo
  -> transferencia manual autorizada a seed
  -> build_catalog.py --write
  -> check + validadores + Pages artifact
```

### Contrato de entrada

- `sourceId` existente y habilitado; `decision: approved`.
- autorización separada para consulta, automatización, retención, atribución,
  retirada y uso público de metadatos;
- host HTTPS exacto permitido, sin redirecciones implícitas;
- presupuesto y demora por ejecución; sin profundidad no justificada;
- respuesta limitada por tamaño, tipo MIME y tiempo de espera;
- para cada registro: URL oficial, timestamp de captura con zona y método;
- para PDF: solo tras autorización explícita, con límite de bytes/páginas y sin
  almacenar el documento completo por defecto.

### Contrato de salida

El adaptador solo puede producir el formato de la bandeja definido en
`data/candidates/README.md`: `candidateId`, `sourceId`, `sourceUrl`,
`capturedAt`, `captureMethod`, valores `proposed` observados y
`fieldEvidence`. Los valores no observados permanecen `null`. No puede emitir
`opportunityStatus`, `verificationStatus`, `publicationStatus` ni
`lastVerifiedAt`, y nunca puede modificar `data/opportunities.seed.json` o
`data/opportunities.json`.

### Controles obligatorios

1. **Autorización:** rechazar antes de red si falta cualquier aprobación o el
   conector no está permitido.
2. **Límites:** máximo de solicitudes, demora, profundidad cero salvo justificación,
   tamaño de respuesta y timeout por host.
3. **Procedencia:** guardar URL, host, fecha de observación y evidencia por cada
   dato; separar `sourceUrl` de `applyUrl`.
4. **Deduplicación:** usar una clave estable basada en fuente y referencia oficial;
   normalizar URL solo para comparar, sin reemplazar la URL canónica observada.
   Las colisiones se conservan como revisión pendiente, no se fusionan
   silenciosamente.
5. **Calidad:** validar esquema, HTTPS, fechas, estados, canal de postulación y
   TTL con los validadores existentes.
6. **Privacidad:** no capturar CV, nombres, correos personales, formularios ni
   descripciones completas salvo autorización específica.
7. **Revisión:** el resultado siempre es staging; no hay promoción automática ni
   publicación directa desde el adaptador.
8. **Desactivación:** poner la fuente en `enabled: false`, presupuesto cero y
   `decision: pending_review` o `revoked`; el siguiente run debe ser un no-op.
   Retirar credenciales y conservar solo la decisión y evidencia mínima necesaria.

## Aceptación futura

P4 no se considera operativo hasta que una fuente concreta cumpla por escrito los
seis puntos del bloqueo P3 y se demuestre, en un staging no publicado:

- el adaptador es rechazado cuando la fuente está pendiente o deshabilitada;
- produce candidatos válidos sin modificar seed/snapshot;
- cada campo no nulo tiene evidencia HTTPS y timestamp;
- duplicados, redirecciones, límites y errores producen resultados explícitos;
- una retirada/desactivación posterior no realiza solicitudes;
- las pruebas existentes, `build_catalog.py --check`,
  `validate_catalog.py`, `validate_candidates.py` y el artefacto Pages pasan;
- la semilla y el snapshot permanecen sin cambios durante el piloto;
- una persona revisa y decide cada candidato antes de cualquier promoción.

## Resultado y siguiente bloque

P4 queda **preparado pero no ejecutado operativamente**. La siguiente acción no
es instalar OSS ni crear un colector: es obtener la autorización escrita para
una fuente concreta y resolver la divergencia entre `main` y `origin/main` sin
sobrescribir trabajo local. Solo después puede aprobarse un piloto de hasta
10 candidatos en staging separado, con revisión humana y presupuesto explícito.
