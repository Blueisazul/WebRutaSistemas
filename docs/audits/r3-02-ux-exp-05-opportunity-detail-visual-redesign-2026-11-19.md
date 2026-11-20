# AUDITORÍA TÉCNICA Y DE DISEÑO: R3-02-UX-EXP-05
## Rediseño Visual de la Ficha de Oportunidad, Adopción Efectiva de Tailwind CSS v4 y Política Estricta de Omisión

**Fecha:** 19 de noviembre de 2026
**Proyecto:** Ruta Sistemas — WebRutaSistemas
**Rama de trabajo:** `integration/r1-02c`
**Commit base:** `9d747c5`
**Tipo de intervención:** [REFACTOR/UX-UI] Rediseño de componentes de detalle, resolución de tokens Tailwind CSS v4 y verificación E2E
**Estado de gobernanza:** Entorno exploratorio personal / círculo reducido. R3-02 formal permanece `NOT_STARTED` / `PENDING_HUMAN`; R3-03 permanece `BLOCKED`.

---

## 1. Contexto y Objetivos del Bloque

Tras las iteraciones exploratorias R3-02-UX-EXP-01 a UX-EXP-04, la evaluación del propietario y su círculo reducido identificó que la ficha de oportunidad aún presentaba una densidad cognitiva innecesaria debida a la sección de «Triaje rápido», la cual generaba fricción al intentar interpretar heurísticas sintéticas en lugar de mostrar de forma directa la información contrastada.

Asimismo, se observó que la interfaz no estaba reflejando visualmente el poder expresivo de Tailwind CSS, viéndose como una página predominantemente en escala de grises con fallas en la aplicación de colores de marca.

El objetivo de este bloque fue:
1. **Eliminar completamente el «Triaje rápido»**: Suprimir las tarjetas de evaluación y sus heurísticas.
2. **Priorizar «✓ Fuente oficial verificada»**: Posicionar la sección en la cabecera del detalle, destacando el difusor, empleador, estado de verificación, fecha de comprobación y enlace directo a la postulación oficial.
3. **Introducir «Resumen» con iconos SVG Lucide**: Sustituir etiquetas textuales frías por una cuadrícula de tarjetas con iconos Lucide inlined (`monitor`, `building`, `pin`, `wallet`, `file`, `clock`, `calendar`, `shield`).
4. **Aplicar una política estricta de omisión visual**: Si un dato no fue declarado o verificado en la convocatoria pública, no renderizar tarjetas vacías, textos redundantes como «No informado» ni frases especulativas (p. ej. «sujeto a desempeño y evaluación del empleador»).
5. **Reubicar «Tecnologías y herramientas declaradas»**: Situarlas inmediatamente debajo de Resumen como etiquetas visuales destacadas.
6. **Reubicar «Qué se verificó»**: Desplazarla debajo de tecnologías, preservando intactos los 21 campos de evidencia desglosada de OP-005.
7. **Diagnosticar y resolver la integración de Tailwind CSS v4**: Identificar la causa raíz de la falta de estilos Tailwind y configurar correctamente `@theme` en la cadena de compilación.

---

## 2. Diagnóstico y Corrección de Tailwind CSS v4

### 2.1 Causa Raíz Identificada
Al inspeccionar el archivo `src/input.css` y compararlo con el historial del repositorio, se descubrió que durante la migración desde Tailwind CSS v3 (vía CDN con objeto `tailwind.config`) hacia la CLI moderna de **Tailwind CSS v4** (`@tailwindcss/cli` v4.3.3):
- La configuración JS previa (`tailwind.config = { theme: { extend: { colors: { ... } } } }`) fue descartada por la arquitectura v4.
- En Tailwind v4, las extensiones de tema deben declararse explícitamente dentro de `@theme { ... }` en el archivo CSS de entrada (`src/input.css`).
- Al estar ausentes en `src/input.css`, clases ampliamente utilizadas en `index.html` (como `text-brandBlack`, `border-borderMuted`, `text-crystalBlue`, `bg-arcticBlue`, etc.) fueron silenciosamente ignoradas por el compilador, generando un CSS que omitía las propiedades de color de identidad y fallbackeaba a estilos genéricos no deseados.
- Un script de comprobación detectó 162 ocurrencias en `index.html` de clases de utilidad sin generar.

### 2.2 Solución Implementada en `src/input.css`
Se incorporaron los tokens oficiales en `@theme`:
```css
@theme {
  --color-ice-blue: #65C7F2;
  --color-crystal-blue: #299EDC;
  --color-arctic-blue: #1765B5;
  --color-brand-black: #202120;
  --color-brand-dark: #505050;
  --color-brand-muted: #757575;
  --color-surface-raised: #f9f9f9;
  --color-border-muted: #efefef;

  /* Alias camelCase para compatibilidad retroactiva con clases existentes */
  --color-iceBlue: #65C7F2;
  --color-crystalBlue: #299EDC;
  --color-arcticBlue: #1765B5;
  --color-brandBlack: #202120;
  --color-brandDark: #505050;
  --color-brandMuted: #757575;
  --color-surfaceRaised: #f9f9f9;
  --color-borderMuted: #efefef;
}
```
Tras ejecutar `npm run build:css`, el archivo `styles.css` (45 KB minificado) generó inmediatamente todas las utilidades correspondientes, restaurando la coherencia cromática y visual de la aplicación.

---

## 3. Rediseño Estructural de la Ficha de Oportunidad (`app.js`)

Se reescribió `renderDetailContent(job)` y sus componentes de soporte:

### 3.1 Retiro Completo del Triaje Rápido
Se eliminaron de `app.js`:
- La función constructora de señales de triaje.
- La función `renderQuickTriage(job)`.
- Toda mención o bloque de triaje sintético en el DOM y en las vistas de diálogo y standalone.

### 3.2 Sección Destacada «✓ Fuente oficial verificada»
Posicionada en la cima del contenido (debajo del título y tags de cabecera):
- Contenedor con borde suavizado y gradiente sutil (`bg-gradient-to-br from-emerald-50/70 via-white to-stone-50 border-emerald-200/90` para verificadas; gris para fichas demostrativas).
- Badge de verificación con icono Lucide `check` (para verificadas) o `shield`.
- Rótulo claro del difusor (`CookUnity`) y empleador contratante si difiere.
- Subtítulo explicativo: *«Publicación oficial verificada directamente en el portal del empleador o difusor · Consulta: [fecha]»*.
- Acciones claras: botón «Ver publicación original ↗» y botón «Ir a postulación ↗» (o `Postulación deshabilitada` si no cumple condiciones de postulación activa).
- Enlace discreto a la ficha informativa de origen.

### 3.3 Cuadrícula de «Resumen» con Iconos SVG Lucide Inlined
Se implementó la función estática `lucideIcon(name, className)` con 10 iconos SVG vectoriales sin dependencias externas:
1. `monitor`: Modalidad de trabajo.
2. `building`: Entidad que difunde.
3. `pin`: Ubicación y elegibilidad territorial.
4. `wallet`: Compensación económica.
5. `file`: Contrato y plazo.
6. `clock`: Fecha límite de postulación.
7. `calendar`: Fecha de publicación original.
8. `shield`: Última verificación o consulta técnica.

Cada tarjeta en `summary-grid` presenta un contenedor accesible (`summary-card flex items-start gap-3.5 p-4 rounded-xl border border-stone-200/90 bg-white shadow-xs`), con un contenedor de icono (`summary-icon shrink-0 p-2.5 rounded-lg bg-stone-100 text-stone-700`) y etiqueta superior en tipografía reducida uppercase (`text-[11px] uppercase tracking-wider text-stone-500`).

### 3.4 Política Estricta de Omisión de Datos No Declarados
En observancia estricta del contrato de rigor editorial:
- Si un campo no está publicado en la fuente o contiene indicadores de ausencia («No especificada», «No informado», «No publicado»), **la tarjeta se omite por completo de la interfaz**.
- En la oportunidad real `OP-005` (CookUnity):
  - No declara modalidad formal en el encabezado -> **Se omite la tarjeta Modalidad**.
  - No publica salario -> **Se omite la tarjeta Compensación**.
  - No establece fecha límite formal -> **Se omite la tarjeta Fecha límite**.
  - Resultado: `OP-005` renderiza exactamente 5 tarjetas verídicas comprobadas: `Entidad que difunde`, `Ubicación y elegibilidad`, `Contrato y plazo`, `Fecha de publicación`, y `Última verificación o consulta`.
- **Limpieza de frases especulativas:** Se implementó `cleanContractDuration(job)` para depurar textos superfluos o condicionales como *«sujeto a desempeño y evaluación del empleador»*, mostrando únicamente los hechos comprobados (*«Indefinido · Full-time»*).

### 3.5 Tecnologías y Herramientas Declaradas
- Posicionada inmediatamente debajo de la cuadrícula de Resumen.
- Contenedor con encabezado distintivo y el icono Lucide `code`.
- Desglose de tecnologías como etiquetas individuales (`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-900 border border-emerald-200/80`).

### 3.6 Reubicación de «Qué se verificó»
- Ubicada a continuación de Tecnologías y herramientas.
- Mantiene la advertencia de comprobación (`evidence-box`).
- Preserva el acordeón interactivo de evidencias (`details.evidence-collapsible`) con los **21 campos de evidencia desglosada** de `OP-005` exigidos por Schema 2.

---

## 4. Preservación del Esquema y Contratos Estáticos

1. **Schema 2 inalterado:** `data/opportunities.seed.json` y `data/opportunities.json` se mantuvieron 100% intactos. No se modificó ningún esquema JSON.
2. **Contrato estático protegido:** `tests/test_static_contract.py` valida 9 aserciones críticas (presencia de difusor, ficha informativa, procedencia por dato, sanitización de URLs seguras `safeHttpsUrl`, y mensaje seguro en ausencia de evidencia). Las 9 pruebas pasaron con éxito.
3. **Cero dependencias npm nuevas:** Los iconos Lucide son componentes SVG en línea sin introducir paquetes ni llamadas de red externas.

---

## 5. Resultados de Pruebas y Validación

| Suite / Verificación | Comando ejecutado | Resultado | Detalle |
|---|---|---|---|
| **Sintaxis JS** | `node --check app.js` `node --check canvas.js` | **PASS** | 0 errores sintácticos. |
| **Pruebas de Catálogo UI** | `node tests/catalog_ui.test.cjs` | **PASS** | 2/2 escenarios pasaron (filtrado y degradación). |
| **Contrato Estático Python** | `python -m unittest tests/test_static_contract.py` | **PASS** | 9/9 pruebas pasaron (0.005s). |
| **Validación de Catálogo** | `python scripts/validate_catalog.py` | **PASS** | 6 fichas validadas; snapshot coincide con canónica. |
| **Build de Catálogo** | `python scripts/build_catalog.py --check` | **PASS** | Catálogo verificado sin desajustes. |
| **Suite Completa Python** | `python -m unittest discover -s tests -p "test_*.py"` | **PASS** | 193/193 pruebas pasaron (2.78s). |
| **Pruebas E2E Playwright** | `npx playwright test` | **PASS** | 14/14 pruebas pasaron en Chromium y Mobile Pixel 5 (14.1s). |
| **Compilación CSS** | `npm run build:css` | **PASS** | Generado `styles.css` minificado (126ms). |
| **Chequeo Git Diff** | `git diff --check` | **PASS** | Sin espacios en blanco erróneos ni conflictos. |

---

## 6. Estado de Gobernanza y Próximos Pasos

- **Ámbito:** La presente iteración R3-02-UX-EXP-05 optimiza la claridad, estética moderna y utilidad del producto para el propietario y su grupo reducido de amigos.
- **Estado de R3-02:** Continúa formalmente en `NOT_STARTED` / `PENDING_HUMAN`. No se han simulado entrevistas ni participantes empíricos ficticios.
- **Estado de R3-03 a R3-05:** Continúan estrictamente `BLOCKED` hasta que el equipo humano ejecute las sesiones de campo reales.
- **Acción Git:** Los cambios se mantienen en el árbol de trabajo local; no se han realizado `git commit`, `push`, `merge` ni despliegues no autorizados.
