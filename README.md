# Ruta Sistemas — prototipo local y sin dependencias pagadas

Catálogo de oportunidades para carreras de Sistemas, con foco inicial en Perú. La muestra actual es curada y demostrativa: **no es un listado en tiempo real ni garantiza vigencia**. La aplicación distingue procedencia, disponibilidad y señales de riesgo; no almacena CV ni datos de cuentas.

## Ejecutar en la computadora existente

Para servir localmente requiere Python 3. La página carga Tailwind desde su CDN oficial, así que necesita acceso a ese CDN para procesar las utilidades. No requiere `pip`, `npm`, Docker ni API de pago. Tailwind indica que Play CDN es para desarrollo y no está pensado para producción; compilar y alojar el CSS propio queda como el siguiente ajuste de despliegue.

```powershell
python server.py
```

Abre <http://127.0.0.1:4173>. El servidor solo escucha en la interfaz de loopback de esta computadora; no es un despliegue público. Deténlo con `Ctrl+C`.

GitHub Pages no ejecuta el backend Python. La interfaz pública lee `data/opportunities.json`, que permite que funcionen búsqueda y filtros bajo la URL de proyecto. `python scripts/build_catalog.py` regenera desde la muestra curada y conserva las fichas ATS ya recogidas; no consulta vacantes en vivo. `python -m collector.refresh_catalog` es el colector programable, pero no hará solicitudes mientras no existan fuentes aprobadas y configuradas.

## Datos, privacidad y operación

- `data/opportunities.seed.json` es la muestra curada fuente; `data/opportunities.json` es el catálogo estático que consume la página.
- La aplicación no registra búsquedas ni carga analítica. Tailwind es la única petición a un tercero al abrirla; la API de vacantes no se consulta en vivo.
- El usuario abre el sitio de empleo externo solo al seguir un enlace. La página no consulta empleadores ni APIs automáticamente.
- `collector/sources.json` contiene fuentes modelo apagadas. Greenhouse/Lever no deben activarse hasta revisar y registrar las condiciones, permisos y límites para cada empleador.
- `.github/workflows/refresh-catalog.yml` está preparado para correr semanalmente/manual con GitHub Actions. Sigue sin actualizar ofertas hasta aprobar fuentes ATS; la configuración de Pages también debe permitir publicación mediante Actions.
- Mantén una copia local de `data/opportunities.sqlite3` al hacer cambios curatoriales importantes. No sincronices la base ni futuras cuentas con un servicio externo sin diseñar primero acceso, retención y eliminación.
- El gasto de software puede ser cero usando hardware e internet ya disponibles; electricidad, conectividad, mantenimiento y trabajo de verificación siguen teniendo costo. No se promete alojamiento público gratuito.

## Estructura

- `server.py`: API y SQLite de solo lectura para desarrollo; GitHub Pages no ejecuta este servidor.
- `index.html`, `styles.css`, `app.js`: interfaz, clases utilitarias Tailwind y filtros en el navegador.
- `data/opportunities.seed.json`, `data/opportunities.json`: muestra fuente y catálogo estático publicado.
- `scripts/build_catalog.py`: regenera el archivo público con Python estándar.
- `collector/`: registro fail-closed, adaptadores ATS públicos y actualización del catálogo solo con fuentes aprobadas.
- `.github/workflows/refresh-catalog.yml`: actualización semanal/manual; no consulta nada hasta aprobar y configurar fuentes. GitHub Pages debe usar `GitHub Actions` como origen de publicación.
- `Informe-investigacion-mercado-fuentes-2026-10-03.md`: mercado, fuentes y decisión de tecnologías.
- `Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`: diseño, modelo y alcance del piloto.
