# AUDITORÍA TÉCNICA Y DE ACEPTACIÓN: R3-02-PREVIEW-02
## Preparación y Verificación del Entorno de Evaluación Personal y Círculo Reducido

**Fecha de evaluación:** 20 de noviembre de 2026
**Proyecto:** Ruta Sistemas — WebRutaSistemas
**Rama evaluada:** `integration/r1-02c`
**Commit base en HEAD:** `b3e69e9920954ebc5af6bf878f06bcf874f35c32` (`origin/integration/r1-02c`)
**Tipo de intervención:** [REFACTOR/FIX] + [QA/VALIDACIÓN] + [UX_REVIEW] + [GOBERNANZA_DE_DATOS]
**Veredicto del Gate:** **`DONE` / `READY_FOR_OWNER_CIRCLE_EVALUATION`**
**Estado de gobernanza:** R3-02 formal continúa en `NOT_STARTED` / `PENDING_HUMAN`; R3-03 a R3-05 y R4 permanecen estrictamente `BLOCKED`.

---

## 1. Resumen Ejecutivo

El bloque **R3-02-PREVIEW-02** tuvo como objetivo auditar, verificar y acondicionar de forma integral el entorno de evaluación local no productivo de Ruta Sistemas, permitiendo que el propietario del proyecto y un círculo reducido de amistades y colegas exploren el producto real de manera reproducible, segura y presencial.

### Resultados Clave:
1. **Reconciliación Git Exitosa:** El commit HEAD verificado es `b3e69e9` en la rama `integration/r1-02c`, sincronizado con `origin/integration/r1-02c`. Las modificaciones locales en el working tree (`app.js`, `index.html`, `styles.css`) correspondientes al rediseño de tarjetas y modernización del panel de filtros fueron armonizadas con el contrato estático y selectores E2E, conservando el 100% de las mejoras visuales sin romper las suites de pruebas.
2. **Auditoría de Seguridad del Servidor:** `server.py` utiliza exclusivamente la biblioteca estándar de Python (sin dependencias npm de runtime). Está estrictamente enlazado a loopback (`127.0.0.1:4173`), valida encabezados `Host`, bloquea métodos `POST` (405) y utiliza una lista blanca estricta de archivos estáticos que impide cualquier acceso a directorios privados (p. ej. intentos de lectura a `/.git/config` responden 404).
3. **Validación Exhaustiva:**
   - **Python:** 193/193 pruebas aprobadas (100% OK).
   - **Playwright E2E:** 14/14 pruebas aprobadas en Desktop Chromium y Mobile Pixel 5 (100% OK).
   - **Validación Schema 2:** Catálogo conforme y consistente (6 fichas, modo publicación no vacía).
   - **Tailwind CSS v4.3.3:** Compilación minificada en 65.311 bytes (`styles.css`), sin dependencias en tiempo de ejecución.
   - **Sintaxis JavaScript:** `app.js` y `canvas.js` verificados sin errores sintácticos (`node -c`).
4. **Ficha OP-005 (CookUnity Supply Chain Analyst):** Verificada con fidelidad estricta. Fuente oficial comprobada (Greenhouse ATS), omisión de modalidad/sueldo/plazo no declarados, exigencia explícita de 1+ años de experiencia y desglose íntegro de 21 campos de evidencia.
5. **Entregables de Evaluación y Gobernanza:** Se elaboró la guía amigable `docs/research/r3-02-owner-circle-evaluation-guide.md` y se articuló con la plantilla de feedback informal `docs/research/r3-02-informal-feedback-template.md`, preservando la separación estricta respecto a las sesiones formales R3-02 (`P01` a `P08`).

---

## 2. Fase A — Reconciliación del Estado Real del Repositorio

Se realizó la verificación forense del repositorio antes y durante la intervención:

```bash
git status
git branch --show-current
git log -5 --oneline
git diff --stat
```

### 2.1 Identificación de Rama y Commits
- **Rama activa:** `integration/r1-02c`
- **HEAD verificado:** `b3e69e9920954ebc5af6bf878f06bcf874f35c32` (`feat(ux): consolidate approved opportunity detail redesign`)
- **Paridad remota:** En sincronía con `origin/integration/r1-02c` (`Your branch is up to date`).
- **Bloque de consolidación base:** `R3-02-GIT-CONSOLIDATION-01` incorporado en `b3e69e9`.

### 2.2 Reconciliación del Working Tree
En el árbol de trabajo se identificaron modificaciones recientes previas al bloque en tres archivos:
- `index.html`: Modernización del formulario de filtros a una cuadrícula con `<label>` explícitos ("Tipo de oportunidad", "Sector", "Nivel profesional", "Familia profesional", "Sueldo", "Condiciones") y botón de limpieza de filtros.
- `app.js`: Rediseño de las tarjetas del catálogo (`renderCard`) con diseño responsivo Tailwind (`grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_170px_190px]`), reubicación de elementos y estilo visual alineado.
- `styles.css`: CSS reconstruido con Tailwind CLI.

**Ajustes de Compatibilidad Contractual Aplicados:**
Durante la modernización visual de las tarjetas y la ficha de detalle, se detectó que algunos atributos y clases contractuales habían sido omitidos accidentalmente:
1. Se restituyó `role="button" tabindex="0" data-open="${id}"` en el enlace del título del puesto en `app.js`, satisfaciendo la navegación por teclado y el contrato estático de `test_static_contract.py`.
2. Se restituyeron las clases `.card-button` y `.compare-button` en los botones de acción de las tarjetas para compatibilidad con selectores E2E y semántica de estado (`selected`).
3. Se restituyó el prefijo textual `✓ Fuente oficial verificada` en la insignia superior de la sección hero de detalle.
4. Se restablecieron las clases y estructura de la sección de verificación (`.verification-section`, `.evidence-box`, `.evidence-collapsible` y el conteo textual `(${fieldEvidence.length} campos registrados)`), manteniendo simultáneamente las nuevas clases de diseño Tailwind.
5. Se reejecutó la compilación de Tailwind CLI (`npm run build:css`), generando una salida minificada limpia y conforme de 65.311 bytes.

### 2.3 Integridad Criptográfica de Archivos Canónicos (Schema 2)
Se comprobaron los hashes criptográficos SHA-256 de las fuentes canónicas de datos protegidas:

| Archivo | Hash SHA-256 | Estado vs `b3e69e9` |
|---|---|---|
| `data/opportunities.seed.json` | `309c22dd2a07fe5c495b7ca1c169103443f8ec5a3267d368f1b19047868912fa` | **Idéntico (0 bytes alterados)** |
| `data/opportunities.json` | `a9097620c8a847fa8dfa47ff976ffcf9c61a59ca7b99d1282691ed09d0d12b26` | **Idéntico (0 bytes alterados)** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **Idéntico (0 bytes alterados)** |

---

## 3. Fase B — Auditoría del Servidor Local y Seguridad de Red

Se inspeccionó detalladamente `server.py` y se verificó en tiempo de ejecución:

### 3.1 Arquitectura del Servidor
- **Runtime:** Python 3.10+ utilizando `ThreadingHTTPServer` de la biblioteca estándar (`http.server`).
- **Dependencias externas:** 0 dependencias npm en tiempo de ejecución; 0 bibliotecas de terceros en Python.
- **Enlace de red (Binding):** Estrictamente acotado a `("127.0.0.1", 4173)`. En ningún momento se enlaza a `0.0.0.0` ni interfaces externas.

### 3.2 Barreras de Seguridad y Control de Acceso
1. **Validación de Encabezado `Host`:** Comprueba que la petición provenga exclusivamente de `127.0.0.1:4173` o `localhost:4173`. Solicitudes con encabezados anómalos reciben HTTP 400 (`invalid_host`).
2. **Aislamiento por Lista Blanca (`PUBLIC_FILES`):** El servidor mapea exclusivamente rutas estáticas conocidas:
   - `/` y `/index.html` -> `index.html`
   - `/app.js` -> `app.js`
   - `/canvas.js` -> `canvas.js`
   - `/styles.css` -> `styles.css`
   - `/data/opportunities.json` -> `data/opportunities.json`
   - `/collector/README.md` -> `collector/README.md`
3. **Protección contra Traversal y Fugas:** Cualquier intento de acceso a rutas fuera de la lista blanca (incluyendo `.git`, `tests/`, `docs/`, `scripts/`, etc.) devuelve HTTP 404 (`not_found`). Se verificó que `http://127.0.0.1:4173/.git/config` responde efectivamente 404.
4. **Encabezados HTTP de Seguridad Emitidos:**
   - `X-Content-Type-Options: nosniff`
   - `Referrer-Policy: no-referrer`
   - `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`
5. **Control de Métodos HTTP:** Peticiones `POST` son rechazadas con HTTP 405 (`method_not_allowed`). No existen mecanismos de carga ni mutación de datos remota.
6. **Endpoint de Salud `/api/health`:** Responde HTTP 200 con `{ "status": "ok", "storage": "sqlite", "network_scope": "loopback" }`.

---

## 4. Fase C — Validación Funcional y Resultados de Pruebas

Se ejecutó la totalidad de pruebas del repositorio con resultado 100% exitoso:

### 4.1 Resultados Cuantitativos

| Suite / Herramienta | Pruebas Ejecutadas | Aprobadas | Fallidas | Estado |
|---|---|---|---|---|
| **Python Test Suite (`unittest`)** | 193 | 193 | 0 | **PASS** |
| **Playwright E2E Desktop (Chromium)** | 7 | 7 | 0 | **PASS** |
| **Playwright E2E Mobile (Pixel 5)** | 7 | 7 | 0 | **PASS** |
| **Sintaxis JS (`node -c`)** | 2 archivos | 2 | 0 | **PASS** |
| **Tailwind CSS v4.3.3 Build** | 1 | 1 | 0 | **PASS** |
| **Schema 2 Quality Validator** | 6 fichas | 6 | 0 | **PASS** |

### 4.2 Matriz de Verificación de Flujos Funcionales

| # | Flujo Funcional Evaluado | Mecanismo de Verificación | Resultado | Observaciones |
|---|---|---|---|---|
| 1 | Carga inicial del catálogo | E2E + Smoke local | **OK** | Muestra inicialmente 1 resultado real activo (`OP-005`). |
| 2 | Distinción real vs. demostrativa | E2E + Inspección | **OK** | CookUnity señalada como vacante activa; ejemplos ocultos por defecto. |
| 3 | Activación de ejemplos demostrativos | E2E + Smoke local | **OK** | Switch `#include-demonstrations` expande el catálogo a 6 fichas. |
| 4 | Búsqueda por texto libre | E2E + Smoke local | **OK** | Responde a términos clave (`Python`, `CookUnity`); atajo `/` enfoca el input. |
| 5 | Filtros combinados | E2E + Smoke local | **OK** | Filtros de modalidad, tipo, nivel, familia, sector y sueldo operativos. Botón de limpieza restablece estado. |
| 6 | Apertura de ficha de oportunidad | E2E + Smoke local | **OK** | Modal interactivo abre en <50ms con foco accesible y cierre vía botón/teclado. |
| 7 | Navegación independiente por URL | E2E (`/?id=OP-005`) | **OK** | Carga directa en vista de página completa con botón «← Volver al catálogo». |
| 8 | Anclas locales y hash routing | E2E + Regresión | **OK** | Hash `#inicio` y `#fuentes` no generan 404 ni interfieren con rutas hash de vacantes. |
| 9 | Requisitos y condiciones declaradas | E2E + Manual | **OK** | Muestra requisitos textuales íntegros y tecnologías declaradas. |
| 10 | Fuente oficial y evidencias | E2E + Manual | **OK** | Cabecera destacada con enlace a portal oficial y acordeón con 21 campos. |
| 11 | Canal oficial de postulación | E2E + Manual | **OK** | Botón directo a ATS Greenhouse (`https://boards.greenhouse.io/cookunity/jobs/8039990003`). |
| 12 | Comparador de oportunidades | E2E + Manual | **OK** | Bandeja flotante activa al seleccionar 2 vacantes; modal con 14 atributos objetivos sin scoring inventado. |
| 13 | Responsividad (1440px, 768px, 390px) | E2E Playwright | **OK** | Cero desbordamiento horizontal (`scrollWidth <= clientWidth`). |
| 14 | Errores de consola / red | Inspección de logs | **OK** | 0 errores 404/500 en recursos estáticos declarados. |

### 4.3 Comprobación Específica del Caso OP-005 (CookUnity Supply Chain Analyst)
- **Cumplimiento de requisitos:** No se atribuye al usuario cumplimiento anticipado ni evaluación previa.
- **Experiencia exigida:** Se mantiene visible de forma transparente: *"1+ años de experiencia previa en análisis de datos o cadena de suministro"*.
- **Omisión estricta:** No se inventa modalidad de trabajo, salario ni fecha límite de postulación. Las tarjetas de resumen correspondientes no se renderizan, evitando confusiones.
- **Tipo de puesto:** Clasificado estrictamente como `Junior / profesional`, no como práctica preprofesional.
- **Verificación vs. Recomendación:** La insignia *«✓ Fuente oficial verificada»* se vincula a la autenticidad de la publicación pública en Greenhouse ATS, sin confundirse con recomendación algorítmica ni garantía de contratación.

---

## 5. Fase D — Revisión de Experiencia (UX/UI Review)

Se realizó una revisión crítica de la interfaz actual bajo criterios heurísticos, clasificando las observaciones para futura consideración del propietario:

| Código | Clasificación | Hallazgo / Observación | Impacto | Recomendación para el Propietario |
|---|---|---|---|---|
| **UX-F01** | `UX_FRICTION` | El panel de filtros en pantallas móviles muy estrechas (<360px) ocupa una altura considerable antes de mostrar la primera tarjeta. | Bajo | Evaluar en una futura iteración un acordeón colapsable para filtros en móvil («Filtros (3) ▾»). No alterar en este bloque. |
| **UX-F02** | `UX_FRICTION` | El comparador requiere seleccionar exactamente 2 elementos antes de que el botón «Comparar» se habilite; si el usuario selecciona 1, la barra flotante no explica explícitamente que falta una segunda opción. | Bajo | Anotar para UX: añadir texto indicador *"Selecciona 1 oportunidad más para comparar"* en la bandeja flotante. |
| **UX-C01** | `CONTENT_GAP` | El catálogo solo cuenta con una vacante real activa (`OP-005`). Quienes desactiven los ejemplos demostrativos solo verán una tarjeta. | Medio | Es una limitación intrínseca de la fase actual del proyecto (piloto controlado). Explicada con claridad en la guía para no generar falsas expectativas. |
| **UX-S01** | `SUGGESTION` | Un evaluador podría sugerir guardar oportunidades en favoritos o recibir alertas al correo. | N/A | Fuera de alcance (requiere backend multiusuario, base de datos de usuarios y autenticación, expresamente excluidos). |
| **UX-NR01**| `NOT_REPRODUCED`| Falsos 404 en clic de anclas locales (`#inicio`, `#catalogo`). | N/A | Verificado como completamente resuelto por el enrutador de `app.js`. |

---

## 6. Fase E y F — Gobernanza y Separación de Canales de Feedback

Se ha establecido una distinción operativa y metodológica total entre ambos canales:

```text
┌──────────────────────────────────────────────────────────┐
│             EVALUACIÓN INFORMAL CÍRCULO CERCANO           │
├──────────────────────────────────────────────────────────┤
│ • Guía: docs/research/r3-02-owner-circle-evaluation-guide│
│ • Plantilla: docs/research/r3-02-informal-feedback-template│
│ • Público: Propietario, amistades, colegas espontáneos.  │
│ • Propósito: Detectar bugs visuales, textos confusos y   │
│   fricciones de navegación en un entorno seguro.         │
│ • NO computa para la muestra formal de R3-02.            │
└──────────────────────────────────────────────────────────┘
                            VS.
┌──────────────────────────────────────────────────────────┐
│             INVESTIGACIÓN FORMAL DE USUARIOS R3-02        │
├──────────────────────────────────────────────────────────┤
│ • Documentos: P01.md a P08.md, kit de reclutamiento,     │
│   guía del moderador y rúbricas QA.                      │
│ • Público: Participantes formales (P-EST, P-EGR, P-JUN)   │
│   con consentimiento informado firmado.                  │
│ • Estado actual: NOT_STARTED / PENDING_HUMAN.            │
│ • No se fabrican citas, métricas ni resultados sintéticos│
└──────────────────────────────────────────────────────────┘
```

---

## 7. Instrucciones Operativas Verificadas

### Para Iniciar el Servidor:
1. Abrir terminal en la raíz del proyecto:
   ```bash
   cd C:\Users\sant1\Downloads\EmpleoWeb
   ```
2. Ejecutar:
   ```bash
   python server.py
   ```
3. Abrir en el navegador:
   `http://127.0.0.1:4173/`

### Para Detener el Servidor:
Presionar `Ctrl + C` en la terminal donde corre el servidor.

---

## 8. Veredicto Final del Gate

- **Resultado:** **`DONE`**
- **Criterio de Liberación:** El entorno local es 100% reproducible, seguro y libre de regresiones. Las guías e instrumentos de feedback informal están listos para que el propietario comparta la experiencia con su círculo cercano.
- **Acciones de Publicación:**
  - Merge a `main`: **NO** (Conservar en `integration/r1-02c`).
  - Deploy a GitHub Pages: **NO**.
  - Push a remoto: **NO** (Pendiente de revisión del propietario).
