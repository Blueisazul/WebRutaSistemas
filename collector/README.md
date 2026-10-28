# Ingesta de fuentes — estado y límites

## Estado vigente

No se ejecuta ingesta automática. Talento Perú/SERVIR y la alternativa institucional FISI-UNMSM se evaluaron el 2026-10-26; ambas están en `pending_review`, deshabilitadas y con presupuesto de consultas cero. No hay evidencia consultada suficiente de un mecanismo/licencia para automatización y reutilización; la página FISI tampoco pudo abrirse directamente en la revisión. Consulta el [registro de evaluación](../docs/sources/talento-peru-servir-2026-10-26.md). `python -m collector.refresh_catalog` solo confirma el no-op. Si una entrada se habilita, el comando termina antes de realizar solicitudes o modificar datos: el adaptador histórico aún no está migrado al schema 2 ni al flujo curatorial vigente.

SERVIR sí incluye en su directorio institucional una [aplicación pública de consulta](https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml). Es un mecanismo de consulta oficial; no se encontró API/feed documentado ni permiso para automatizar o reutilizar. La solicitud de aclaración está preparada, no enviada. Para gestionar información manualmente sin tocar el catálogo, usa la [bandeja editorial local](../data/candidates/README.md) y sus borradores de autorización en [seguimiento de fuentes](../docs/sources/seguimiento-autorizacion-fuentes.md).

La política de `authorize_fetch()` ahora requiere explícitamente `decision: approved`, `automatedAccessStatus: approved`, términos y derechos aprobados, fuente habilitada, conector implementado y host permitido. La falta de cualquier campo de decisión también deniega el acceso.

No activar Talento Perú, FISI-UNMSM, Greenhouse, Lever, OSITRAN ni agregadores sin una revisión específica de acceso técnico, términos, uso permitido, atribución, frecuencia, retención y evidencia. Una API pública facilita la lectura técnica, pero no constituye licencia de republicación ni confirma que una vacante siga abierta.

## Próxima evolución

La fuente canónica editable es `data/opportunities.seed.json`; los datos que se deseen proponer desde un futuro conector deberán revisarse y copiarse/aceptarse explícitamente ahí antes de generar `data/opportunities.json`. El resultado automático nunca debe declarar vigencia por la sola presencia de un anuncio. La fase de piloto debe capturar una muestra acotada para medir completitud y exactitud, sin publicar directamente.

Los conectores HTTP existentes en `ats_connectors.py` y políticas en `policy.py` son material de referencia, no un pipeline actualmente operativo. Mantienen límites de respuesta y rechazan redirecciones. No se sigue un redirect automáticamente: debe revisarse el nuevo host y permitirse de forma explícita. No se usa Scrapy hasta que la complejidad de fuentes HTML autorizadas lo justifique; no se incorpora Firecrawl ni API alojada de Freehire. Talento Perú no tiene condiciones suficientes documentadas; FISI-UNMSM fue evaluada como única alternativa, pero sus condiciones de uso tampoco se aclararon y la ficha no pudo consultarse directamente. Ambas fuentes siguen apagadas; no hubo piloto ni scraping.

`data/candidates/inbox.local.json` es una bandeja de notas que no se versiona ni se sirve en Pages; copiar desde `data/candidates/inbox.example.json` y validar con `python scripts/validate_candidates.py`. El validador es offline y de solo lectura. No equivale a autorización de conservar/publicar contenido y no promociona candidatos: una decisión editorial aprobada requiere que la fuente tenga autorización manual y de reutilización pública; luego el revisor debe transferir los datos manualmente a la semilla y superar el validador del catálogo.

## Comandos

```powershell
python -m collector.refresh_catalog
python -m unittest discover -s tests -v
python scripts/validate_catalog.py
```

El workflow de publicación no tiene cron, no llama a colectores y no escribe commits en `main`. GitHub Actions/Pages siguen siendo servicios alojados; ver la decisión vigente en `docs/adr/ADR-001-catalogo-curado-publicacion-segura.md` y el roadmap en la sección 21 de `Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`.
