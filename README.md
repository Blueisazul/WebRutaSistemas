# Ruta Sistemas

Catálogo piloto de oportunidades laborales para estudiantes y profesionales de Sistemas, con foco en Perú y puestos remotos elegibles desde Perú. El objetivo es hacer comparables las condiciones y la evidencia que ayudan a decidir una trayectoria; la plataforma no garantiza empleo, continuidad ni ascensos.

## Estado real

La interfaz estática permite buscar y filtrar un catálogo JSON. El conjunto actual conserva cinco fichas **demostrativas** y ninguna está habilitada para postular: una convocatoria vencida, una cerrada/histórica y tres con vigencia desconocida, todas sin verificación vigente. No hay fuentes automáticas aprobadas ni ofertas reales activas actualmente. La fecha de generación del catálogo no significa que las fichas se hayan vuelto a comprobar.

Las fichas demostrativas no aparecen en la búsqueda normal: se muestran solo al activar **“Incluir ejemplos demostrativos”** y están identificadas como ejemplos. Los contadores de oportunidades reales excluyen esas fichas. Cuando no hay oportunidades reales verificadas, la página lo indica y explica que cada publicación se incorpora tras revisar su origen y canal de postulación.

## Fuente de datos y estados

- `data/opportunities.seed.json` es la única fuente editable y versionada. Contiene las fichas, su procedencia, fechas y estados.
- `data/opportunities.json` es un artefacto generado para el frontend. No editarlo directamente: el validador detecta cualquier diferencia con la fuente; para reemplazarlo deliberadamente se usa `--write`.
- Todas las fechas civiles usan `YYYY-MM-DD`; timestamps de evidencia usan ISO 8601 con zona. Fechas civiles se evalúan en `America/Lima` (UTC-05:00). Una fecha incompleta o ausente permanece desconocida.
- `opportunityStatus` describe abierta/cerrada/vencida/desconocida; `verificationStatus` describe verificada/pendiente/atrasada/no verificada; `publicationStatus` determina activa/no confirmada/histórica. No son equivalentes.
- La configuración del TTL piloto está en `verificationTtlDays` de la semilla. El valor inicial es **7 días calendario** por la rotación rápida de vacantes; debe revisarse con evidencia del piloto. Deadline vencido siempre anula publicación activa. Sin deadline, la verificación reciente y la evidencia siguen siendo obligatorias.
- Para publicar una ficha activa se exige revisión manual reciente del canal de postulación confirmado por el empleador y observado abierto, timestamp con zona, evidencia enlazada, enlaces HTTPS en hosts explícitamente permitidos, estatus abierto, fecha límite no vencida si existe y registro no demostrativo. Un ATS que devuelve un anuncio o una ejecución de generación no satisface por sí sola estos requisitos.
- El contrato editorial para nuevas fichas activas separa `employer` (quien contrata) de `publisher` (quien difunde); `sourceUrl` identifica la ficha informativa y `applyUrl` el canal de postulación. `fieldEvidence` registra URL HTTPS y `observedAt` por cada dato publicado, y `editorialDecision` conserva aprobación humana, revisor, fecha y motivo. Cada dato no publicado permanece `null`/ausente; el validador exige evidencia para toda condición que sí se afirme.
- La interfaz identifica empleador, difusor, ficha y canal de postulación por separado; detalla los enlaces de evidencia por campo. Muestras demostrativas se etiquetan como tales, y el enlace de postulación no se habilita por defecto ni se infiere desde la fuente informativa.
- Talento Perú/SERVIR y una alternativa institucional (portal FISI-UNMSM) fueron evaluados el 2026-10-26 y quedaron `pending_review`. El directorio oficial de SERVIR lista una aplicación web pública de consulta, pero no API/feed documentado ni autorización de automatización/reutilización. Ambas fuentes están deshabilitadas con presupuesto de solicitudes cero; no hubo extracción. Los borradores de seguimiento están preparados, no enviados. Los conectores Greenhouse/Lever también continúan desactivados.

## Ejecutar y validar

Requisitos locales: Python 3.12+ recomendado y Node.js solo para comprobar sintaxis JS. El sitio publicado no necesita Node, npm, Tailwind ni peticiones de terceros para cargar estilos.

```powershell
# Comprobar pruebas y fuente/snapshot sin escribir
python -m unittest discover -s tests -v
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
python scripts/validate_candidates.py data/candidates/inbox.example.json
node --check app.js
node tests/catalog_ui.test.cjs

# Después de editar deliberadamente la semilla, regenerar el JSON
python scripts/build_catalog.py --write
python scripts/build_catalog.py --check

# Servidor local de demostración
python server.py
```

La captura editorial manual permanece separada del catálogo: revisa [data/candidates/README.md](data/candidates/README.md). La bandeja real `inbox.local.json` es local e ignorada por Git; no hay importación automática a la semilla.

La generación automática usa hora actual para `generatedAt`, pero ese campo no se usa como evidencia de vigencia. Para una reconstrucción reproducible se puede fijar el timestamp:

```powershell
python scripts/build_catalog.py --write --generated-at 2026-10-26T12:00:00Z
```

El TTL y el `--as-of YYYY-MM-DD` del validador permiten ejecutar la misma regla para una fecha de referencia. El modo de catálogo vacío solo se admite si se pide explícitamente en el validador para una prueba; la publicación no acepta catálogo vacío por defecto.

## Publicación, seguridad y autonomía

El workflow `.github/workflows/refresh-catalog.yml` primero ejecuta pruebas, validación y `node --check`, y solo entonces prepara el artefacto con cuatro archivos. No programa scraping, no escribe commits ni tiene permiso `contents: write`. Un error bloquea la publicación. Cada cambio queda reversible con Git.

**GitHub Pages y GitHub Actions son servicios alojados, no software OSS ni operación autoalojada.** Se conservan en este piloto por simplicidad y costo monetario directo cero bajo las condiciones aplicables a la cuenta/repositorio, no como garantía de disponibilidad ni autonomía plena. El pipeline y catálogo son reproducibles desde el repositorio, sin datos ocultos ni APIs pagadas. Camino de salida: servir el artefacto estático en infraestructura propia con Caddy o Nginx OSS y ejecutar validaciones localmente o con un runner propio. Antes de migrar se debe disponer de máquina/conectividad, dominio/TLS, monitorización, respaldos y procedimiento de restauración; eso implica costos eléctricos y de operación aunque el software sea gratuito.

`server.py` conserva un prototipo local Python/SQLite de lectura, ligado a loopback y no utilizado por Pages. No es backend público ni fuente canónica. No se sincroniza con JSON/semilla. Se reconsiderará solo si aparece una necesidad validada de curación concurrente o historial transaccional.

## Documentos vigentes e históricos

- [ADR-001 — catálogo curado y publicación segura](docs/adr/ADR-001-catalogo-curado-publicacion-segura.md): decisiones vigentes de este bloque.
- [Seguimiento de autorización](docs/sources/seguimiento-autorizacion-fuentes.md): borradores oficiales no enviados y criterios de decisión.
- [Diseño y roadmap](Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md), sección 21: estado vigente y siguiente fase; las secciones anteriores se conservan como historia.
- [Auditoría fechada 2026-10-25](docs/audits/project-state-audit-2026-10-25.md): snapshot previo a este bloque, no descripción del código actual.
- [Investigación de mercado/fuentes](Informe-investigacion-mercado-fuentes-2026-10-03.md): investigación histórica; ninguna fuente queda autorizada por aparecer allí.

Siguiente fase: resolver la revisión pendiente con SERVIR o con la Facultad de Ingeniería de Sistemas e Informática de la UNMSM (mecanismo, uso/reutilización, frecuencia, atribución, retención y retirada). Solo si hay autorización suficiente, ejecutar un piloto acotado de hasta 10 registros en staging separado con revisión humana. Ver [evaluación de fuentes P2](docs/sources/talento-peru-servir-2026-10-26.md). No añadir scoring, IA, rutas profesionales, Firecrawl ni crawling general hasta que la calidad de datos lo justifique.
