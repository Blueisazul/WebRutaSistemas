# INFORME DE AUDITORÍA Y ENTREGA TÉCNICA: BLOQUE R3-ALPHA-UX-01
## Escalabilidad del Catálogo (Paginación) y Presentación Estructurada de Contenido (Listas)

- **Identificador de Bloque:** `R3-ALPHA-UX-01`
- **Sub-bloques:** `R3-ALPHA-UX-01A` (Paginación escalable) y `R3-ALPHA-UX-01B` (Listas y viñetas)
- **Fecha:** 21 de noviembre de 2026
- **Rama:** `integration/r1-02c`
- **Entorno:** Alpha Privada (Uso Personal y Círculo Cercano)
- **Estado de Ejecución:** `DONE`
- **Auditor / Implementador:** Principal Software Engineer, Senior Frontend Engineer, UX Engineer & Technical Auditor

---

## 1. Contexto y Objetivos del Bloque

Tras la incorporación de las cinco nuevas oportunidades reales de Canonical Ubuntu a la Alpha privada en `R3-ALPHA-PROMOTION-01` (ampliando el catálogo a 11 fichas: 6 reales y 5 demostrativas), el propietario evaluó la aplicación y formuló dos inquietudes concretas sobre la experiencia de uso:

1. **Escalabilidad del catálogo:** ¿Cómo se comportará la interfaz cuando existan 20, 40 o más tarjetas de oportunidades laborales?
2. **Estructura y legibilidad de descripciones:** En los detalles del puesto, varios campos presentaban elementos agrupados en un solo bloque continuo separados por punto y coma (`;`), dificultando su escaneo visual en lugar de mostrarse como listas legibles con viñetas.

El objetivo de `R3-ALPHA-UX-01` es dar respuesta técnica a ambas inquietudes en el frontend sin introducir nuevas dependencias, sin romper contratos existentes y sin modificar en un solo byte los archivos de datos canónicos.

---

## 2. Implementación R3-ALPHA-UX-01A: Paginación Escalable del Catálogo

### 2.1 Reglas de Diseño y Límite por Página
- **Tamaño de página (`PAGE_SIZE`):** Se definió una constante de 12 tarjetas por página (`PAGE_SIZE = 12`).
- **Visibilidad condicional:**
  - Si el total de oportunidades visibles/filtradas es menor o igual a 12 (`totalJobs <= 12`), el contenedor de paginación (`#pagination`) permanece completamente oculto (`hidden = true`).
  - Si el total de oportunidades supera 12 (`totalJobs > 12`), el contenedor se despliega automáticamente mostrando controles de navegación y métricas de página.
- **Controles de navegación:**
  - Botón **Anterior** (`#prev-page`): Habilitado a partir de la página 2; deshabilitado en página 1 (`disabled = currentPage <= 1`).
  - Botón **Siguiente** (`#next-page`): Habilitado mientras queden páginas posteriores; deshabilitado en la última página (`disabled = currentPage >= totalPages`).
  - Indicador informativo (`#pagination-info`): Notificación contextual con formato `Página X de Y · Mostrando A–B de N oportunidades` con `aria-live="polite"`.
- **Navegación fluida:** Al cambiar de página mediante `goToPage(page)`, la vista ejecuta un desplazamiento suave (`scrollIntoView({ behavior: 'smooth', block: 'start' })`) hacia la lista de resultados para evitar que el usuario quede ubicado al pie de página.
- **Reseteo ante cambios de estado:** Todo cambio en los filtros de búsqueda (`#query`, `#location`, `#mode`, `#kind`, `#family`, `#sector`, `#level`, etc.), limpieza de filtros (`#clear-filters`, `#empty-clear`) o conmutación de ejemplos demostrativos (`#include-demonstrations`) o historial (`#include-history`) resetea automáticamente `currentPage = 1`.
- **Preservación del Comparador Local:** Las selecciones para comparación (`compareIds`) se almacenan en el estado desacoplado de la vista y se conservan intactas al navegar entre páginas. Una ficha seleccionada en la página 1 mantiene su estado `selected` y el panel de comparación flotante permanece consistente al pasar a la página 2.

### 2.2 Verificación de Comportamiento Dinámico
El algoritmo matemático implementado calcula dinámicamente las páginas ante cualquier volumen:

| Total Items Filtrados | Total Páginas (`ceil(N/12)`) | Distribución por Página |
|---|:---:|---|
| **6** (Alpha actual sin demos) | 1 | 6 en P1 (Controles ocultos) |
| **11** (Alpha actual con demos) | 1 | 11 en P1 (Controles ocultos) |
| **12** | 1 | 12 en P1 (Controles ocultos) |
| **13** | 2 | P1: 12, P2: 1 |
| **20** | 2 | P1: 12, P2: 8 |
| **24** | 2 | P1: 12, P2: 12 |
| **25** | 3 | P1: 12, P2: 12, P3: 1 |
| **40** | 4 | P1: 12, P2: 12, P3: 12, P4: 4 |
| **100** | 9 | P1–P8: 12 c/u, P9: 4 |

---

## 3. Implementación R3-ALPHA-UX-01B: Presentación Estructurada de Listas

### 3.1 Detección Semántica y Formateo
Se implementó la función auxiliar `formatStructuredList(text, fallbackText)` en `app.js`:

```javascript
function formatBulletItem(item) {
  const clean = item.replace(/\.$/, '').trim();
  if (!clean) return '';
  if (/^[a-z][a-z0-9]/.test(clean) && !/^[a-z][A-Z]/.test(clean)) {
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }
  return clean;
}

function formatStructuredList(text, fallbackText = '') {
  if (!text || typeof text !== 'string' || !text.trim()) {
    return fallbackText ? `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(fallbackText)}</p>` : '';
  }
  const trimmed = text.trim();
  if (!trimmed.includes(';')) {
    return `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(trimmed)}</p>`;
  }
  const items = trimmed.split(';').map((item) => item.trim()).filter(Boolean);
  if (items.length <= 1) {
    return `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(trimmed)}</p>`;
  }
  return `<ul class="list-disc pl-5 space-y-1.5 text-sm text-stone-700 leading-relaxed">${items
    .map((item) => `<li>${escapeHTML(formatBulletItem(item))}</li>`)
    .join('')}</ul>`;
}
```

### 3.2 Campos Transformados
1. **`job.tasks` ("Qué harías"):**
   - Textos con punto y coma (p.ej. OP-001, OP-002, OP-004, OP-005, OP-006 a OP-010) se renderizan como `<ul class="list-disc pl-5 ..."><li>...</li></ul>`.
   - Elementos con viñeta se despojan de puntos finales redundantes y se capitaliza la primera letra para legibilidad profesional.
2. **`job.requirements` ("Requisitos del puesto"):**
   - Convocatorias con requisitos múltiples separados por `;` (p.ej. OP-005 con 6 requisitos, OP-006 con 5, OP-008 con 6) se muestran con viñetas independientes.
3. **`job.benefits` ("Beneficios publicados"):**
   - Convocatorias con beneficios desglosados (p.ej. OP-006 con 5 beneficios: remoto 100%, USD 2,000 capacitación, viajes semestrales, bono, feriados) se muestran en viñetas claras.

### 3.3 Preservación Estricta de Textos Narrativos
- Textos sin punto y coma (p.ej. `QA-001` tasks: *"Práctica dirigida a la Jefatura de Contratos Portuarios."*) se preservan intactos como párrafos `<p>`.
- El campo `growth` ("Qué experiencia podrías llevar al siguiente paso") permanece estrictamente como párrafo narrativo `<p>`, respetando el uso gramatical y analítico del punto y coma editorial sin convertirlo en viñetas.
- Los campos de procedencia y notas analíticas no fueron perturbados.

---

## 4. Evidencia de Verificación y Pruebas Técnicas

### 4.1 Suite Python (193 pruebas)
```text
Ran 193 tests in 2.904s
OK
```
Todas las pruebas de ingesta, deduplicación, validación semántica, contratos offline y servidor local pasaron al 100%.

### 4.2 Validación y Consistencia del Catálogo Canónico
```text
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
Resultado: Catálogo válido: 11 registros; snapshot coincide con la fuente canónica.
```

### 4.3 Suite Playwright E2E (18 pruebas aprobadas)
Se incorporaron dos pruebas completas adicionales en `tests/e2e/catalog.spec.cjs`, elevando la cobertura de 14 a 18 pruebas ejecutadas en Chromium (Desktop) y Mobile (Pixel 5):

```text
Running 18 tests using 1 worker
[1/18]  [chromium] loads the catalog and displays active verified opportunities... PASSED
[2/18]  [chromium] filters examples and active opportunities... PASSED
[3/18]  [chromium] opens a detail and compares two explicitly selected items... PASSED
[4/18]  [chromium] keeps the main flow usable on a narrow viewport... PASSED
[5/18]  [chromium] navigates directly to standalone opportunity view via URL... PASSED
[6/18]  [chromium] renders cleanly without horizontal overflow... PASSED
[7/18]  [chromium] redesigns opportunity detail with verified source... PASSED
[8/18]  [chromium] R3-ALPHA-UX-01A: handles catalog pagination, navigation, limits, resets, and preserves comparator... PASSED
[9/18]  [chromium] R3-ALPHA-UX-01B: formats semicolon-delimited lists as bullet lists and preserves narrative text... PASSED
[10/18] [mobile]   loads the catalog and displays active verified opportunities... PASSED
[11/18] [mobile]   filters examples and active opportunities... PASSED
[12/18] [mobile]   opens a detail and compares two explicitly selected items... PASSED
[13/18] [mobile]   keeps the main flow usable on a narrow viewport... PASSED
[14/18] [mobile]   navigates directly to standalone opportunity view via URL... PASSED
[15/18] [mobile]   renders cleanly without horizontal overflow... PASSED
[16/18] [mobile]   redesigns opportunity detail with verified source... PASSED
[17/18] [mobile]   R3-ALPHA-UX-01A: handles catalog pagination, navigation, limits, resets, and preserves comparator... PASSED
[18/18] [mobile]   R3-ALPHA-UX-01B: formats semicolon-delimited lists as bullet lists and preserves narrative text... PASSED
18 passed (24.9s)
```

---

## 5. Invariabilidad de Archivos Canónicos y Hashes Criptográficos

Durante la ejecución de este bloque de experiencia de usuario, los archivos canónicos de datos permanecieron estrictamente inalterados:

| Archivo | SHA-256 Verificado | Estado |
|---|---|:---:|
| `data/opportunities.seed.json` | `789a5fe4777a596a031089f48885a5d492c401fcf01df1f5ec56b6df490de61c` | **Inalterado** |
| `data/opportunities.json` | `a6ccb384f232af9a3e05bfce4807691c270b23eba37978e3a69aee06802e9e2c` | **Inalterado** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **Inalterado** |

---

## 6. Estado de Gobernanza del Proyecto

1. **R3-02 Investigación Formal:** Permanece en estado `NOT_STARTED` / `PENDING_HUMAN`. Este bloque corresponde exclusivamente a la respuesta sobre inquietudes de uso en la Alpha privada personal.
2. **R3-03 a R3-05 y R4:** Continúan estrictamente bloqueadas (`BLOCKED`).
3. **Control de despliegue:** No se realizó merge a `main`, no se desplegó en GitHub Pages, no se realizaron commits ni pushes no autorizados.
4. **Dependencias:** Cero dependencias npm o pip introducidas; se utilizaron estándares web nativos y Tailwind CSS v4.3.3 preexistente.
