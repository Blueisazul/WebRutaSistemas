# Ruta Sistemas — prototipo local y sin dependencias pagadas

Catálogo de oportunidades para carreras de Sistemas, con foco inicial en Perú. La muestra actual es curada y demostrativa: **no es un listado en tiempo real ni garantiza vigencia**. La aplicación distingue procedencia, disponibilidad y señales de riesgo; no almacena CV ni datos de cuentas.

## Ejecutar en la computadora existente

Requiere Python 3 con su módulo SQLite. Si el SQLite instalado incluye FTS5, la búsqueda lo usa; si no, usa la búsqueda alternativa incorporada. No requiere `pip`, `npm`, Docker, nube, API de pago ni servicios externos.

```powershell
python server.py
```

Abre <http://127.0.0.1:4173>. El servidor solo escucha en la interfaz de loopback de esta computadora; no es un despliegue público. Deténlo con `Ctrl+C`.

## Datos, privacidad y operación

- `data/opportunities.seed.json` es la muestra curada inicial. La base SQLite local se crea en `data/opportunities.sqlite3` al primer inicio.
- La aplicación solo sirve rutas explícitas; la base de datos no se expone por HTTP. No registra las búsquedas ni carga analítica, fuentes, tipografías o scripts de terceros.
- El usuario abre el sitio de empleo externo solo al seguir un enlace. La página no consulta empleadores ni APIs automáticamente.
- `collector/sources.json` contiene fuentes modelo apagadas. Greenhouse/Lever no deben activarse hasta revisar y registrar las condiciones, permisos y límites para cada empleador.
- La búsqueda programada semanal queda pendiente hasta aprobar una fuente concreta y validar su conector. La recomendación es usar el Programador de tareas de Windows en este equipo, no un botón público ni un servicio cloud.
- Mantén una copia local de `data/opportunities.sqlite3` al hacer cambios curatoriales importantes. No sincronices la base ni futuras cuentas con un servicio externo sin diseñar primero acceso, retención y eliminación.
- El gasto de software puede ser cero usando hardware e internet ya disponibles; electricidad, conectividad, mantenimiento y trabajo de verificación siguen teniendo costo. No se promete alojamiento público gratuito.

## Estructura

- `server.py`: servidor/API local en la biblioteca estándar de Python; SQLite y búsqueda FTS5.
- `index.html`, `styles.css`, `app.js`: interfaz y filtros conectados al catálogo local.
- `data/opportunities.seed.json`: datos de muestra sin extracción de descripciones completas.
- `collector/`: registro fail-closed y adaptadores mínimos desactivados para APIs públicas de ATS.
- `Informe-investigacion-mercado-fuentes-2026-10-03.md`: mercado, fuentes y decisión de tecnologías.
- `Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`: diseño, modelo y alcance del piloto.
