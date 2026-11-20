# AUDITORÍA TÉCNICA Y DE ENTREGA GIT: R3-02-PREVIEW-03
## Reconciliación Git y Entrega Controlada de la Versión de Evaluación

**Fecha de evaluación:** 20 de noviembre de 2026
**Proyecto:** Ruta Sistemas — WebRutaSistemas
**Rama objetivo:** `integration/r1-02c`
**Remoto:** `origin` (`https://github.com/Blueisazul/WebRutaSistemas.git`)
**Tipo de intervención:** [AUDITORÍA_GIT] + [COMMIT_CONTROLADO] + [PUSH_CONTROLADO] + [ENTREGA_DE_EVALUACIÓN]
**Veredicto del Gate:** **`DONE`**
**Estado de gobernanza:** R3-02 formal continúa en `NOT_STARTED` / `PENDING_HUMAN`; R3-03 a R3-05 y R4 permanecen estrictamente `BLOCKED`.

---

## 1. Resumen Ejecutivo

El bloque **R3-02-PREVIEW-03** tuvo como misión resolver la discrepancia de sincronización detectada en el informe de `R3-02-PREVIEW-02`, auditar de forma forense el estado del repositorio Git, versionar mediante commits descriptivos y atómicos los cambios validados de interfaz y documentación, y sincronizar la rama de integración `integration/r1-02c` con su repositorio remoto en GitHub mediante un push controlado.

### Resultados Principales:
1. **Resolución de la Discrepancia:** Se aclaró documental y técnicamente por qué el informe anterior reportó simultáneamente `HEAD b3e69e9 en paridad con origin/integration/r1-02c` y `Push a remoto: NO`. El commit base `b3e69e9` efectivamente coincidía entre local y remoto, mientras que las mejoras de interfaz y los nuevos documentos auditados en PREVIEW-02 residían en el working tree sin commit debido a la directriz expresa de dicho bloque (*«No realices commits ni push en este bloque. Primero entrega los resultados para revisión del propietario»*).
2. **Validación Exhaustiva Pre-Sincronización:**
   - **Python:** 193/193 pruebas aprobadas (100% OK).
   - **Playwright E2E:** 14/14 pruebas aprobadas en Desktop Chromium y Mobile Pixel 5 (100% OK).
   - **Catálogo Schema 2:** Catálogo consistente (`build_catalog.py --check` y `validate_catalog.py` conformes con 6 registros).
   - **Compilación CSS:** Tailwind CSS v4.3.3 minificado en 68.717 bytes (`styles.css`), sin dependencias en tiempo de ejecución.
   - **Sintaxis JavaScript:** `app.js` y `canvas.js` verificados sin errores (`node --check`).
   - **Servidor y Seguridad:** `server.py` comprobado con enlace loopback `127.0.0.1:4173`, validación de `Host`, bloqueo 404 a rutas privadas (p. ej. `/.git/config`) y endpoint `/api/health` respondiendo `200 OK`.
3. **Sincronización Git Controlada:** Se crearon commits atómicos y limpios para código UI y paquete documental, ejecutando un push normal a `origin/integration/r1-02c`. Cero uso de `--force`, cero reversiones destructivas y preservación íntegra del historial.
4. **Entrega de Evaluación Documentada:** Se formalizaron las opciones de evaluación presencial (compartiendo pantalla) y de evaluación independiente mediante clonado Git en la rama `integration/r1-02c`.

---

## 2. Análisis y Resolución de la Discrepancia Git

El informe de `R3-02-PREVIEW-02` contenía dos afirmaciones aparentemente contradictorias:
1. *"HEAD `b3e69e9` está en sincronía con `origin/integration/r1-02c`, con cero commits adelantados o atrasados."*
2. *"Sección de publicación: `Push a remoto: NO`."*
3. Enumeraba archivos modificados en `app.js`, `index.html` y `styles.css`.

### Reconstrucción Forense del Estado Real:
- En el commit `b3e69e9` (`feat(ux): consolidate approved opportunity detail redesign`), consolidado el 19 de noviembre de 2026, tanto el HEAD local como el remoto estaban idénticos (`b3e69e9`).
- En la mañana del 20 de noviembre de 2026, se realizaron ediciones locales en el working tree (`app.js`, `index.html`, `styles.css`) modernizando las tarjetas de empleo y el formulario de filtros.
- Durante `R3-02-PREVIEW-02`, estas modificaciones fueron armonizadas con los contratos estáticos y selectores E2E, y se elaboraron los documentos de aceptación y guía de evaluación.
- Sin embargo, las reglas de gobernanza del bloque PREVIEW-02 establecían explícitamente:
  > *"No realices commits ni push en este bloque. Primero entrega los resultados para revisión del propietario."*
- En consecuencia, en ese instante:
  - El puntero Git HEAD seguía siendo `b3e69e9` (idéntico a `origin/integration/r1-02c`).
  - No existían commits locales sin enviar (`ahead 0, behind 0`).
  - Pero el código validado contenía cambios no versionados en el árbol de trabajo (`working tree dirty`).
  - Por ello, se reportó `Push a remoto: NO`.

Una vez revisado y aprobado el resultado por el propietario, el presente bloque **R3-02-PREVIEW-03** asume la responsabilidad de versionar y sincronizar formalmente este estado hacia el repositorio remoto.

---

## 3. Fase A — Auditoría Forense de Git

### 3.1 Estado Inicial del Repositorio
```bash
git status --short --branch
## integration/r1-02c...origin/integration/r1-02c
 M app.js
 M docs/architecture/r0-decisiones-y-alcance-2026-11-12.md
 M index.html
 M styles.css
?? docs/audits/r3-02-preview-02-acceptance-2026-11-20.md
?? docs/research/r3-02-owner-circle-evaluation-guide.md
```

- **Rama activa:** `integration/r1-02c`
- **HEAD local inicial:** `b3e69e9920954ebc5af6bf878f06bcf874f35c32`
- **HEAD remoto inicial (`origin/integration/r1-02c`):** `b3e69e9920954ebc5af6bf878f06bcf874f35c32`
- **Remoto configurado:** `origin -> https://github.com/Blueisazul/WebRutaSistemas.git`
- **Diferencia commit local vs remoto:** `git diff origin/integration/r1-02c...HEAD` = vacío (0 commits).
- **Diferencia working tree vs HEAD:** 4 archivos modificados y 2 archivos nuevos no rastreados.

---

## 4. Fase B — Revisión de Contenido e Inclusiones/Exclusiones

Se auditó que el paquete a sincronizar contiene todos los componentes necesarios para la versión de evaluación:

### Archivos Incluidos y Verificados:
- `server.py`: Servidor nativo loopback en Python estándar.
- `index.html`: Estructura HTML con panel de filtros accesible y contenedor de vista independiente.
- `app.js`: Lógica de renderizado de catálogo, tarjetas Tailwind, acordeón de evidencias, modal y vista standalone.
- `canvas.js`: Fondo visual WebGL2 optimizado con observer y fallback.
- `styles.css`: Hoja de estilos minificada compilada vía Tailwind CLI v4.3.3.
- `data/opportunities.json`: Catálogo de oportunidades Schema 2.
- `data/opportunities.seed.json`: Semilla canónica de oportunidades.
- `collector/sources.json`: Registro de fuentes auditadas.
- `docs/research/r3-02-owner-circle-evaluation-guide.md`: Guía amigable de exploración para el círculo cercano.
- `docs/research/r3-02-informal-feedback-template.md`: Plantilla para recoger impresiones espontáneas.
- `docs/audits/r3-02-preview-02-acceptance-2026-11-20.md`: Auditoría de aceptación técnica de PREVIEW-02.
- `docs/audits/r3-02-preview-03-git-delivery-2026-11-20.md`: Auditoría de entrega y sincronización de PREVIEW-03.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Roadmap maestro actualizado.

### Archivos Excluidos:
- Artefactos temporales de pruebas de Playwright (`test-results/` eliminado y en `.gitignore`).
- Cero archivos de credenciales, secretos, claves API o archivos `.env`.
- Cero datos personales o identificatorios de participantes.

### Invariabilidad Criptográfica de Datos Canónicos (Schema 2):
| Archivo Canónico | Hash SHA-256 Actual | Estado vs `b3e69e9` |
|---|---|---|
| `data/opportunities.seed.json` | `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` | **Idéntico (0 bytes alterados)** |
| `data/opportunities.json` | `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` | **Idéntico (0 bytes alterados)** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **Idéntico (0 bytes alterados)** |

---

## 5. Fase C — Validación Técnica Previa

Antes de preparar los commits, se ejecutó la batería completa de validaciones:

```bash
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
python -m unittest discover -s tests -p "test_*.py"
node --check app.js
node --check canvas.js
npx playwright test
```

### Resultados de Ejecución:
- **`build_catalog.py --check`:** Catálogo válido (6 registros; snapshot coincide exactamente con la fuente canónica).
- **`validate_catalog.py`:** Válido (6 fichas; modo=publicación no vacía; fecha Lima=2026-11-20).
- **Python Unit Tests:** 193 pruebas ejecutadas, 193 aprobadas (0 fallos).
- **Playwright E2E:** 14 escenarios ejecutados en 12.7s:
  - 7 pruebas en Desktop Chromium: 7 aprobadas.
  - 7 pruebas en Mobile Pixel 5: 7 aprobadas.
- **Sintaxis JavaScript:** `node --check app.js` y `node --check canvas.js` exitosos (0 errores).
- **Servidor local y seguridad:**
  - `http://127.0.0.1:4173/api/health` -> `200 OK` (`{"status": "ok", "storage": "sqlite", "network_scope": "loopback"}`).
  - Peticiones con `Host: evil.com` -> `400 Bad Request` (`{"error": "invalid_host"}`).
  - Rutas privadas `http://127.0.0.1:4173/.git/config` -> `404 Not Found`.

---

## 6. Fase D — Commits y Push Controlado

Se organizaron las modificaciones en commits atómicos, verificando `git diff --cached --check` para descartar conflictos de espacio o sintaxis antes de confirmar:

1. **Commit de Código e Interfaz:**
   - Mensaje: `feat(ux): modernize catalog card and filter controls for owner evaluation (R3-02-PREVIEW-02)`
   - Archivos: `app.js`, `index.html`, `styles.css`.
2. **Commit de Documentación y Auditorías:**
   - Mensaje: `docs(r3): document preview-02 acceptance, informal evaluation guide, and git delivery (R3-02-PREVIEW-03)`
   - Archivos: `docs/research/r3-02-owner-circle-evaluation-guide.md`, `docs/audits/r3-02-preview-02-acceptance-2026-11-20.md`, `docs/audits/r3-02-preview-03-git-delivery-2026-11-20.md`, `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`.

### Sincronización Remota:
- Comando: `git push origin integration/r1-02c`
- Método: Push convencional de avance rápido (fast-forward).
- Sin uso de `--force`, `--delete` ni operaciones destructivas.

---

## 7. Procedimiento de Entrega para el Propietario y Amigos

Esta versión es para **evaluación privada y no productiva**. Se proveen dos métodos sencillos para utilizarla:

### Opción A — Evaluación presencial o compartiendo pantalla (Recomendada)
Es el método más ágil y que no requiere configuración técnica por parte de los amigos:
1. El propietario abre su terminal en la carpeta del proyecto y ejecuta:
   ```bash
   python server.py
   ```
2. Abre en su navegador:
   **`http://127.0.0.1:4173/`**
3. Los amigos observan la pantalla (presencialmente o mediante videollamada / Discord / Google Meet) e interactúan guiados por el propietario siguiendo la [guía de exploración](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-owner-circle-evaluation-guide.md).
4. El propietario anota comentarios espontáneos en la [plantilla informal](file:///C:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-informal-feedback-template.md).

### Opción B — Evaluación independiente por amigos técnicos
Si los amigos cuentan con Git y Python 3.10+ en sus equipos y tienen acceso al repositorio:
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Blueisazul/WebRutaSistemas.git
   cd WebRutaSistemas
   ```
2. Cambiar a la rama de integración:
   ```bash
   git switch integration/r1-02c
   ```
3. Iniciar el servidor local:
   ```bash
   python server.py
   ```
4. Abrir en el navegador:
   `http://127.0.0.1:4173/`
5. Seguir el recorrido sugerido en `docs/research/r3-02-owner-circle-evaluation-guide.md`.

> [!WARNING]
> **Limitaciones de Acceso:**
> Si el repositorio en GitHub es privado, los amigos requerirán que el propietario los añada como colaboradores con permiso de lectura para clonarlo. Si no disponen de cuenta de GitHub o acceso, debe utilizarse exclusivamente la **Opción A**.
> **No** se debe hacer público el repositorio ni configurar túneles (ngrok, cloudflare tunnels) ni abrir puertos de red.

---

## 8. Confirmación de Criterios de Publicación

- **Merge a `main`:** **NO**. La rama `main` permanece intacta.
- **Despliegue a producción (GitHub Pages):** **NO**. El sitio en producción continúa en su estado anterior.
- **Ámbito del servidor:** Confinado estrictamente a `127.0.0.1`.

---

## 9. Veredicto Final

- **Resultado:** **`DONE`**
- **Estado de ramas:** Local y remoto `origin/integration/r1-02c` sincronizados en paridad exacta.
- **Siguiente acción:** El propietario puede proceder a realizar las exploraciones con su círculo cercano siguiendo las opciones documentadas.
