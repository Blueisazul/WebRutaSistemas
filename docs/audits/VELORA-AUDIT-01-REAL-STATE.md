# VELORA-AUDIT-01 — Auditoría Técnica y Operativa del Estado Real de Velora

- **Fecha de auditoría pericial:** 23 de noviembre de 2026
- **Commit auditado:** `43a0cad8466fff33da410020013a6e171b71448f` (HEAD de `integration/r1-02c`, alineado con `main` y `origin/main`)
- **Repositorio canónico:** `https://github.com/Blueisazul/WebRutaSistemas`
- **Despliegues evaluados:**
  - Vercel (Producción viva): `https://velora-six-fawn.vercel.app/`
  - GitHub Pages (Despliegue secundario/histórico): `https://blueisazul.github.io/WebRutaSistemas/`
- **Roles periciales:** Principal Software Architect, Engineering Lead, Technical Auditor, DevOps Architect, Data Engineer.

---

## 1. Resumen Ejecutivo

Esta auditoría integral fue ejecutada de forma exhaustiva, contrastando directamente el repositorio de código fuente, los entornos de ejecución local, los resultados de pruebas automatizadas y los despliegues públicos en vivo frente a la documentación histórica del proyecto.

### Conclusiones Principales:
1. **Identidad y Marca (Discrepancia Crítica):**  
   Aunque el proyecto es comercializado y referenciado externamente como **Velora** (reflejado en el subdominio de Vercel `velora-six-fawn.vercel.app`), el repositorio, la aplicación web, el código HTML/JavaScript, los encabezados, títulos y documentación continúan denominándose íntegramente **Ruta Sistemas**. No existe mención técnica de "Velora" en el código fuente.
2. **Estado del Catálogo en Vivo (112 Oportunidades Reales):**  
   El catálogo canónico (`data/opportunities.seed.json` y `data/opportunities.json`) contiene **112 registros totales**:
   - **107 oportunidades reales activas y verificadas** (todas pertenecientes al sector privado de tecnología, con elegibilidad confirmada para Perú).
   - **5 fichas demostrativas** (3 de tecnología/consultoría y 2 del sector público - OSITRAN, catalogadas como históricas/cerradas).
   - **Brecha del Sector Público:** Existen **0 oportunidades activas del sector público peruano** en el catálogo publicado. Los conectores estatales desarrollados en R4-09 (OSITRAN y Defensoría del Pueblo) extrajeron convocatorias que, al revalidarse en R4-10, ya habían publicado actas de resultados finales o cerrado su etapa de postulación, siendo correctamente bloqueadas por el principio *fail-closed*.
3. **Desincronización de Despliegues (Vercel vs GitHub Pages):**  
   - **Vercel** se encuentra al día, desplegando el commit de R4-10 con **107 oportunidades activas** (12 por página en el catálogo paginado).
   - **GitHub Pages** está desactualizado desde el 18 de noviembre de 2026, mostrando únicamente **1 oportunidad activa** (CookUnity `OP-005`). Esto ocurrió porque el trabajo `publish` del workflow de GitHub Actions fallaba por la ausencia del paso de configuración de Python (`actions/setup-python`), anomalía recién corregida en el commit `43a0cad`.
4. **Causa Raíz del "Problema Conocido de Vercel":**  
   El incidente reportado donde Vercel mostraba `"No hay oportunidades verificadas disponibles"` y contadores en `"——"` no fue una falla de infraestructura ni de rutas HTTP. Se debió al mecanismo de expiración por frescura (TTL de verificación de 7 días fijado en `verificationTtlDays`) ejecutado en el cliente (`app.js`): al transcurrir más de 7 días sin una revalidación que refrescase `lastVerifiedAt` y `fieldEvidence`, el algoritmo degrada dinámicamente las oportunidades activas a `"unconfirmed"`, ocultándolas de la vista predeterminada. En R4-10 se regeneraron los timestamps con fecha 23 de noviembre de 2026, restableciendo la visibilidad.
5. **Solidez Técnica y Cero Deuda en Pruebas:**  
   El repositorio cuenta con una cobertura y rigor excepcionales: 232 pruebas unitarias en `pytest` aprobadas (100%), pruebas de validación de contrato de esquema aprobadas, verificaciones sintácticas de JavaScript aprobadas y 45 pruebas E2E con Playwright (incluyendo auditoría de accesibilidad WCAG 2.1 AA con `axe-core`) aprobadas.

---

## 2. Estado Real del Repositorio y Git

### 2.1 Configuración de Ramas y Commits
- **Rama activa local:** `integration/r1-02c`
- **Sincronización remota:** La rama local está sincronizada y al día con `origin/integration/r1-02c`, `origin/main` y `main`.
- **Últimos commits auditados:**
  - `43a0cad` (HEAD, 2026-11-23 09:31:02): *ci: add Python setup to publish job in refresh-catalog workflow*
  - `53ac014` (2026-11-23 09:22:37): *ci: include playwright config and server in workflow trigger paths*
  - `aef97a0` (2026-11-23 09:18:14): *ci(playwright): configure explicit chromium device for narrow project and increase timeouts for CI*
  - `c448025` (2026-11-23 09:12:00): *fix(tests): handle gitignored staging inbox gracefully in CI environments*
  - `14c44bb` (2026-11-23 09:04:42): *feat(catalog): release verified Peruvian tech opportunities and integrate Encora (R4-10)*
- **Estado del Working Tree:** Limpio. No existen modificaciones pendientes de lógica ni archivos sin seguimiento que comprometan la reproducibilidad.

---

## 3. Inventario Arquitectónico y Modular

Velora opera bajo un diseño arquitectónico **estático y desacoplado (Backend-less / Jamstack nativo)** combinado con un **motor de adquisición y gobernanza local en Python puro**:

```
WebRutaSistemas/ (Velora)
├── index.html                   # Shell SPA accesible y semántica
├── app.js                       # Controlador frontend (búsqueda, filtros, detalle, comparador)
├── styles.css                   # CSS compilado de Tailwind CLI v4.3.3
├── canvas.js                    # Fondo dinámico WebGL2 interactivo
├── collector/                   # Motor de Adquisición y Gobernanza de Datos (Python stdlib)
│   ├── sources.json             # Registro declarativo de fuentes, políticas y cuotas
│   ├── policy.py                # Control de acceso fail-closed y permisos de consulta
│   ├── ats_connectors.py        # Adaptadores Greenhouse y Lever API
│   ├── pe_connectors.py         # Conectores nacionales (OSITRAN, Defensoría, UTP HiringRoom) y extractor PDF
│   ├── jsonld_extractor.py      # Parser Schema.org JobPosting nativo
│   ├── classification.py        # Taxonomía técnica y geográfica
│   ├── dedup.py                 # Algoritmo de colisiones y huella determinista
│   ├── evidence.py              # Validación de frescura y evidencias por campo
│   ├── revalidation.py          # Ciclo de vida, detección de cambios y desaparición
│   └── acquisition_runner.py    # Orquestador local por lotes
├── data/
│   ├── opportunities.seed.json  # Fuente canónica de verdad versionada (112 fichas)
│   ├── opportunities.json       # Snapshot plano para distribución pública (112 fichas)
│   └── candidates/              # Staging local de adquisición
│       ├── inbox.local.json     # Bandeja local de 254 candidatos (gitignored)
│       └── inbox.example.json   # Esquema sintético de prueba
├── scripts/
│   ├── editorial_cli.py         # Interfaz unificada de línea de comandos para auditoría
│   ├── build_catalog.py         # Generador determinista del catálogo
│   ├── validate_catalog.py      # Verificador de contrato y reglas Schema 2
│   ├── validate_candidates.py   # Verificador de candidatos en staging
│   └── pages_artifact.py        # Empaquetador estricto para GitHub Pages (5 archivos)
└── tests/                       # Suite integral de pruebas unitarias, integración y E2E
```

---

## 4. Auditoría del Catálogo y Calidad de Datos

### 4.1 Métricas Totales del Catálogo Publicado (`data/opportunities.json`)

| Métrica / Dimensión | Valor Real Calculado | Observaciones de Auditoría |
|---|---|---|
| **Total de Registros** | **112** | Coincide con la publicación del hito R4-10. |
| **Oportunidades Reales Activas** | **107** | Estado `publicationStatus: "active"`, `verificationStatus: "verified"`. |
| **Fichas Demostrativas** | **5** | Ocultas por defecto; requieren activar toggle explícito. |
| **Oportunidades Cerradas / Históricas** | **2** | `OP-001` y `QA-001` (OSITRAN, demostrativas). |
| **Oportunidades No Confirmadas** | **3** | `OP-002`, `OP-003`, `OP-004` (42Labs y Launchpad, demostrativas). |
| **Sector Público Activo** | **0** | Brecha estructural pendiente de resolver. |
| **Sector Privado Activo** | **107** | 100% de las oportunidades activas pertenecen al sector privado. |
| **Modalidad Remota** | **95** | Dominante debido a vacantes internacionales de Canonical y Sezzle. |
| **Modalidad Híbrida** | **10** | Con asistencia presencial en Lima (Encora). |
| **Modalidad Presencial** | **1** | Práctica preprofesional IT Helpdesk en Lima (Encora). |
| **Modalidad Sin Especificar / Abierta** | **1** | CookUnity Supply Chain Analyst (`OP-005`). |
| **Elegibilidad Perú Confirmada** | **107 (100%)** | Cada ficha cuenta con evidencia específica de contratación para Perú. |
| **Remuneración Publicada** | **4 (3.7%)** | Solo 4 vacantes de Sezzle informan rango salarial explícito en USD. |
| **Fechas Límite (Deadlines) Presentes** | **0 (0%)** | Ninguna vacante activa tiene deadline fijo (requisiciones ATS continuas). |

### 4.2 Desglose por Empleador Real

| Empleador | País Matriz | Tipo de Presencia | Fichas Activas | Canal de Postulación |
|---|---|---|---|---|
| **Canonical** | Reino Unido / Global | Remoto internacional | **80** | Greenhouse ATS oficial |
| **Encora** | EE.UU. / Perú | Oficinas en Lima (Magdalena) | **13** | Greenhouse ATS (`encora10`) |
| **Sezzle** | EE.UU. | Remoto internacional / LatAm | **13** | Greenhouse ATS oficial |
| **CookUnity** | EE.UU. / Argentina | Operaciones en Lima | **1** | Greenhouse ATS (`OP-005`) |
| **Total Activas** | | | **107** | |

### 4.3 Clasificación por Nivel Profesional

- **Egresado / Bachiller / Junior Avanzado:** 93 posiciones (86.9%)
- **Junior / Entry:** 6 posiciones (5.6%)
- **Estudiantes (Prácticas preprofesionales):** 4 posiciones (3.7%)
- **Prácticas profesionales formativas:** 4 posiciones (3.7%)

---

## 5. Auditoría de Despliegues: Vercel frente a GitHub Pages

Se realizó una inspección HTTP y una auditoría en navegador headless (Playwright Chromium) de ambos despliegues en producción:

| Parámetro / Componente | Vercel (`velora-six-fawn.vercel.app`) | GitHub Pages (`blueisazul.github.io/WebRutaSistemas/`) | Estado de Paridad |
|---|---|---|---|
| **Estado HTTP** | 200 OK | 200 OK | Paridad técnica básica |
| **Título (`<title>`)** | `Ruta Sistemas` | `Ruta Sistemas` | Paridad (Marca Velora ausente) |
| **Branding en Header** | `/ Ruta Sistemas` | `/ Ruta Sistemas` | Paridad (Marca Velora ausente) |
| **Tamaño de `opportunities.json`** | 537,807 bytes | 16,954 bytes | **DESINCRONIZADO** |
| **Fecha de Generación del JSON** | 2026-11-23T13:54:01Z | 2026-11-18T03:53:25Z | **DESINCRONIZADO (5 días de desfase)** |
| **Total Fichas Servidas** | 112 | 6 | **DESINCRONIZADO** |
| **Oportunidades Activas Mostradas** | **107 resultados** | **1 resultado** | **DESINCRONIZADO** |
| **Paginación Funcional** | Sí (12 tarjetas/página, 9 páginas) | No requerida (1 tarjeta) | Divergente |
| **Errores en Consola del Navegador** | 0 errores JS (solo warnings WebGL) | 0 errores JS | Conforme |

### 5.1 Causa Raíz de la Desincronización de GitHub Pages
El workflow `.github/workflows/refresh-catalog.yml` tiene dos trabajos: `validate` y `publish`.
En el trabajo `publish`, se ejecuta `python scripts/pages_artifact.py --output dist`. Hasta el commit `43a0cad` de hoy, este trabajo carecía del step `actions/setup-python@v5`. En entornos limpios de GitHub Actions (`ubuntu-latest`), la invocación a `python` fallaba inmediatamente antes del despliegue de Pages. Por tanto, GitHub Pages conservó el último despliegue exitoso (R2/R3, 18 de noviembre). Vercel, al compilar directamente del árbol del repositorio en cada push a `main`, sirvió el JSON actualizado de inmediato.

---

## 6. Auditoría del Mecanismo de Frescura (TTL) en Cliente

El contrato de datos establece:
```javascript
const ttlDays = Number.isInteger(catalogConfig.verificationTtlDays) ? catalogConfig.verificationTtlDays : 7;
if (ageDays < 0 || ageDays > ttlDays) states.verificationStatus = 'stale';
...
if (states.publicationStatus === 'active' && !verifiedNow) states.publicationStatus = 'unconfirmed';
```

### Impacto en la Experiencia de Usuario:
1. Si pasan más de 7 días naturales sin que el equipo ejecute una revalidación que actualice el campo `lastVerifiedAt` en la semilla, el frontend marca **todas** las vacantes como `stale` y degrada su estado a `unconfirmed`.
2. Dado que el filtro predeterminado oculta los estados no confirmados, el usuario recibe el mensaje:  
   *«No hay oportunidades verificadas disponibles»* y el contador de resultados cae a cero.
3. Este diseño es excesivamente frágil para la operación continua: transfiere una regla de auditoría interna al renderizado en el navegador del usuario final, provocando "apagones" visuales del catálogo si no hay actividad editorial semanal.

---

## 7. Contradicciones Documentales Identificadas

1. **README.md desactualizado:**
   - Afirma que el catálogo cuenta con **1 oportunidad real activa** (`OP-005`: CookUnity) y 5 demostrativas, cuando en realidad cuenta con **112 fichas** (107 activas).
   - Declara que los conectores Greenhouse y Lever continúan totalmente desactivados, cuando en `collector/sources.json` y en producción están activos para Canonical, Sezzle, CookUnity y Encora.
   - Sostiene que la promoción es exclusivamente manual, cuando existen scripts de migración y promoción (`promote_pe_candidates.py`).
2. **Nombre de Marca:**
   - El proyecto se llama comercialmente **Velora** en comunicaciones y URLs de Vercel, pero el código fuente, HTML, workflows y documentación interna lo llaman **Ruta Sistemas** / `web-ruta-sistemas`.
3. **Estado de Fuentes Estatales:**
   - Se menciona reiteradamente a Talento Perú / SERVIR en hojas de ruta pasadas, pero permanece bloqueado y deshabilitado con cero solicitudes ejecutadas.

---

## 8. Verificación de Suites de Pruebas

Se ejecutaron localmente las suites oficiales del repositorio con los siguientes resultados certificados:

```powershell
# 1. Pruebas Unitarias de Python (Collector, Políticas, Conectores, Dedup, Evidencia)
python -m pytest -v
-> Resultado: 232 passed, 43 subtests passed en 8.78s (100% de éxito).

# 2. Validación de Contrato de Catálogo y Snapshot
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
-> Resultado: Catálogo válido: 112 registros; snapshot coincide exactamente con la fuente canónica.

# 3. Comprobación Sintáctica de JavaScript
node --check app.js
-> Resultado: Sin errores sintácticos.

# 4. Pruebas de Interfaz de Filtrado
node tests/catalog_ui.test.cjs
-> Resultado: Escenarios de filtrado y degradación aprobados (OK).

# 5. Pruebas E2E de Playwright (Accesibilidad WCAG 2.1 AA y Flujos de Usuario)
npm run test:e2e
-> Resultado: 45 pruebas aprobadas en Chromium (100% de éxito).
```

---

## 9. Conclusión del Estado Real

Velora cuenta con una base de código excepcionalmente sólida, modular y con pruebas de clase mundial. Su motor de adquisición y políticas *fail-closed* garantizan que nunca se publique una vacante cerrada o fraudulenta. 

Sin embargo, el producto sufre de **tres brechas críticas para su objetivo nacional**:
1. **Desalineación de marca:** La identidad visual y técnica sigue siendo "Ruta Sistemas".
2. **Ausencia del sector público:** 0 vacantes del Estado peruano en el catálogo activo.
3. **Dependencia de revalidación manual de TTL:** Riesgo recurrente de que el catálogo se "apague" en el frontend cada 7 días.
