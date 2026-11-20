# Informe de Preparación de Entorno de Evaluación No Productivo R3-02
**Guía de Ejecución Local, Evaluación Funcional y Compartición para Uso Personal y Círculo Reducido**

- **Fecha de auditoría:** 2026-11-19 (07:05 Lima)
- **Fase del Proyecto:** R3 — Validación del producto (Subfase R3-02: Trabajo de Campo / Evaluación Previa)
- **Resultado del Bloque:** **`DONE`**
- **Rama de Trabajo:** `integration/r1-02c`
- **HEAD Evaluado:** `9d747c5` (`docs(r3): harmonize QA rubrics, fieldwork tracking, and deliver operational audit packet (R3-02)`)
- **Repositorio Remoto:** `https://github.com/Blueisazul/WebRutaSistemas.git`

---

## 1. Commit y Rama Evaluados

- **Rama:** `integration/r1-02c`
- **Commit HEAD:** `9d747c5`
- **Propósito:** Evaluación formativa, funcional y cualitativa en entorno local no productivo por parte del propietario y un grupo reducido de amigos.
- **Alcance:** Exclusivamente no comercial. No se realiza ningún despliegue a producción ni publicación en Internet.

---

## 2. Estado de Sincronización

- La rama local `integration/r1-02c` se encuentra en paridad absoluta con `origin/integration/r1-02c` en el commit `9d747c5`.
- El working tree inicial se encontraba completamente limpio (`nothing to commit, working tree clean`).
- La versión de producción alojada en GitHub Pages ([https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/)) continúa desplegada desde el commit `28b7a9e` (cierre R2-A-05 en la rama `main`). El código de interfaz (`index.html`, `app.js`, `canvas.js`, `styles.css`) y el catálogo publicado (`data/opportunities.json`) son funcionalmente idénticos entre `28b7a9e` y `9d747c5`.

---

## 3. Requisitos de Ejecución Local

Ruta Sistemas fue diseñado bajo una arquitectura de catálogo estático sin dependencias pesadas de runtime:

- **Requisito indispensable:** Python 3.10+ (probado con Python 3.12 en Windows y Linux). Utiliza únicamente la biblioteca estándar (`http.server`, `sqlite3`, `urllib`, `json`, `hashlib`).
- **Navegador Web:** Cualquier navegador moderno (Chrome, Firefox, Edge, Safari) con soporte para JavaScript ES6+ y CSS Grid/Flexbox.
- **Requisitos de desarrollo / pruebas (opcionales):** Node.js 22 (solo necesario para ejecutar tests UI/E2E o recompilar CSS con Tailwind CLI). Para simplemente correr y evaluar la web, **no se requiere instalar nada con npm**.
- **Dependencias externas / SaaS:** Cero (0). No requiere claves de API, cuentas en la nube ni bases de datos remotas.

---

## 4. Procedimiento Local Paso a Paso (Para el Propietario y Amigos)

### 4.1 En el equipo del propietario (Ya clonado)

1. **Abrir la terminal** en la carpeta raíz del proyecto (`EmpleoWeb`).
2. **Verificar rama de evaluación:**
   ```powershell
   git checkout integration/r1-02c
   ```
3. **Iniciar el servidor local de evaluación:**
   ```powershell
   python server.py
   ```
   *Salida esperada:*
   ```text
   Ruta Sistemas está disponible solo en esta computadora: http://127.0.0.1:4173
   ```
4. **Abrir en el navegador:** Acceder a `http://127.0.0.1:4173/` o `http://localhost:4173/`.
5. **Detener el servidor:** Presionar `Ctrl + C` en la terminal.

---

### 4.2 En la computadora de un amigo (Evaluación distribuida por clonación)

Si un amigo desea evaluarlo en su propio equipo de manera autónoma:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Blueisazul/WebRutaSistemas.git
   cd WebRutaSistemas
   git checkout integration/r1-02c
   ```
2. **Ejecutar el servidor estándar:**
   ```bash
   python server.py
   ```
3. **Abrir en el navegador:** `http://127.0.0.1:4173/`.
4. *(Alternativa universal si no se desea usar `server.py`):*
   ```bash
   python -m http.server 4173 --bind 127.0.0.1
   ```

---

### 4.3 Ejecución de la Suite de Pruebas Automatizadas

Para comprobar que el entorno local no presenta regresiones:

```powershell
# 1. Validación de integridad del catálogo
python scripts/build_catalog.py --check
python scripts/validate_catalog.py

# 2. Pruebas unitarias de Python (193 tests)
python -m unittest discover -s tests -p "test_*.py"

# 3. Pruebas de JavaScript en Node
node --check app.js
node tests/catalog_ui.test.cjs

# 4. Pruebas End-to-End con Playwright (requiere npx playwright)
npx playwright test
```

---

## 5. Resultado de las Pruebas

| Componente Evaluado | Herramienta / Script | Resultado | Detalle |
|---|---|:---:|---|
| **Consistencia de Catálogo** | `scripts/build_catalog.py --check` | **PASS** | 6 registros; snapshot coincide exactamente con la semilla canónica. |
| **Gobernanza Schema 2** | `scripts/validate_catalog.py` | **PASS** | 0 errores (evaluado con fecha Lima 2026-11-19). |
| **Sintaxis Frontend** | `node --check app.js` | **PASS** | JavaScript sin errores léxicos ni de sintaxis. |
| **Comportamiento UI Local** | `node tests/catalog_ui.test.cjs` | **PASS** | Filtrado, reseteo y degradación controlada probados. |
| **Suite Unitaria Python** | `python -m unittest discover` | **PASS** | **193/193 tests aprobados** en 3.03s. |
| **Pruebas E2E Playwright** | `npx playwright test` | **PASS** | **8/8 tests aprobados** (Chromium Desktop + Mobile Viewport) en 14.4s. |
| **Disponibilidad HTTP Local** | Diagnóstico en `server.py` | **PASS** | HTTP 200 en `/`, `/styles.css`, `/app.js`, `/data/opportunities.json` y `/api/health`. |

---

## 6. Flujos Funcionales Comprobados

Se verificaron manualmente y mediante tests los 12 flujos esenciales:

1. **Apertura del Catálogo:** Carga rápida instantánea sin parpadeos ni peticiones externas bloqueantes.
2. **Identificación de Oportunidades Reales vs. Demostrativas:** En la carga inicial se muestra únicamente la vacante real `OP-005` (*Supply Chain Analyst* en CookUnity). Los contadores superiores reflejan `1` oportunidad activa verificada.
3. **Activación de Ejemplos Demostrativos:** Al marcar la casilla *"Incluir ejemplos demostrativos"*, se incorporan las 5 fichas históricas claramente marcadas con distintivo *"Ejemplo demostrativo"*.
4. **Búsqueda y Filtros:** El campo de búsqueda (atajo `/`) y los selectores (modalidad, nivel, familia, sector) filtran de forma instantánea.
5. **Apertura de Ficha Individual:** Al hacer clic en una tarjeta se abre el modal accesible con foco atrapado y tecla `Esc` funcional.
6. **Interpretación de Requisitos:** La ficha de CookUnity desglosa claramente conocimientos técnicos (SQL, ERP, modelado de datos), nivel educativo universitario y experiencia requerida (1+ años).
7. **Ubicación y Elegibilidad:** Indica con claridad `Lima, Perú` y elegibilidad local presencial/híbrida.
8. **Comprensión de Estados:** Expone estados separados: oportunidad `open`, verificación `verified` (por empleador con TTL de 7 días) y publicación `active`.
9. **Consulta de Evidencias:** Sección de procedencia con 21 evidencias desglosadas por campo, timestamps en hora peruana y enlaces HTTPS directos a fuentes oficiales.
10. **Canal Oficial de Postulación:** Botón *"Ir a postulación oficial"* habilitado exclusivamente para `OP-005` apuntando a su ATS oficial de Greenhouse, sin intermediación de currículums.
11. **Comparador Local:** Permite seleccionar hasta 2 oportunidades (activando ejemplos) y muestra una tabla comparativa con 14 atributos objetivos sin declarar un "ganador universal".
12. **Diseño Responsivo:** Visualización y navegación cómodas tanto en escritorio como en dispositivos móviles (probado en emulador móvil de Playwright).

---

## 7. Problemas Reproducibles y Fricciones Observadas

No se encontraron errores técnicos de ejecución (crashes de servidor, excepciones de JavaScript o enlaces rotos). Sin embargo, se mantienen bajo observación las **6 fricciones heurísticas conocidas** identificadas en R3-01:

1. **`UX-B01`:** En la tarjeta de `OP-005`, la etiqueta superior indica *"Activa · revisión reciente"*, pero el recuadro central dice *"Vigencia no confirmada"*, lo que puede causar desconcierto inicial.
2. **`UX-B02`:** Si se busca un término que no coincide (ej. "python"), el estado vacío dice *"No hay oportunidades verificadas disponibles"*, pudiendo inducir a pensar que el catálogo general está caído.
3. **`UX-B03`:** En el comparador, la fila de estado de verificación muestra texto técnico en inglés (`open · verified · active`).
4. **`UX-B04`:** En el modal de detalle, se expone un timestamp ISO 8601 crudo (`2026-11-17T22:28:37-05:00`).
5. **`UX-B05`:** El Hero promete áreas como "Fullstack Dev" y "Data & DevOps", pero la única oportunidad real es de analítica logística (*Supply Chain Analyst*).
6. **`UX-B06`:** El switch *"Incluir ejemplos demostrativos"* tiene baja visibilidad al intentar comparar vacantes por primera vez.

> [!NOTE]
> Estas fricciones no deben corregirse de forma prematura: forman parte deliberada de los puntos de observación para la evaluación cualitativa.

---

## 8. Archivos Modificados y Creados en Este Bloque

| Archivo | Tipo de Acción | Justificación |
|---|:---:|---|
| [docs/research/r3-02-informal-feedback-template.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-informal-feedback-template.md) | **Creado** | Plantilla liviana para recoger feedback informal de amigos y círculo cercano protegiendo la privacidad. |
| [docs/audits/r3-02-preview-readiness-2026-11-19.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-02-preview-readiness-2026-11-19.md) | **Creado** | Este informe de preparación de entorno de evaluación no productivo. |

---

## 9. Dependencias Agregadas

- **Dependencias agregadas:** **CERO (0)**.
- Se preserva la arquitectura estática sin dependencias adicionales ni paquetes de terceros en tiempo de ejecución.

---

## 10. Opciones para Compartir la Evaluación con Amigos

| Alternativa | Descripción y Mecánica | Nivel de Exposición | Ventajas | Limitaciones / Requisitos |
|---|---|:---:|---|---|
| **A. Pantalla Compartida (Videollamada)** | El propietario ejecuta `python server.py` y comparte pantalla por Google Meet, Zoom o Discord mientras su amigo comenta. | **Cero exposición de red.** | Cero configuración; máxima seguridad y privacidad. | El amigo no manipula directamente el cursor. |
| **B. Clonación y Ejecución Local por el Amigo** | El amigo clona el repo público, hace `git checkout integration/r1-02c` y corre `python server.py`. | **Cero exposición de red.** | Experiencia 100% interactiva en su propio navegador sin servidores intermedios. | El amigo debe tener Git y Python instalados en su equipo. |
| **C. Red Local Doméstica (Mismo Wi-Fi)** | El propietario ejecuta un servidor local accesible en su LAN (ej. `python -m http.server 4173 --bind 0.0.0.0`) y comparte su IP privada (`http://192.168.1.X:4173`). | **Exposición limitada a la red doméstica privada.** | Permite a un amigo probar la web en su teléfono o laptop mientras esté en la misma casa/oficina. | No funciona para amigos fuera de la misma red local. |
| **D. Preview Remota Alojada en Internet (GitHub Pages / Vercel temporal)** | Desplegar temporalmente la rama en un hosting público o compartir el enlace de GitHub Pages en producción (`https://blueisazul.github.io/WebRutaSistemas/`). | **Pública en Internet.** | Acceso con un solo clic desde cualquier dispositivo sin instalar nada. | **Requiere autorización expresa del propietario.** Expone la web a indexación o visitas no deseadas; rompe el aislamiento no productivo. |

> [!CAUTION]
> **Directriz de No Publicación:** No se han configurado túneles (ngrok, cloudflare tunnels), port forwarding de router ni despliegues automáticos a Internet. Si el propietario desea que amigos remotos accedan mediante enlace web sin clonar el repositorio, la opción recomendada y segura es que utilicen temporalmente el despliegue existente en GitHub Pages ([https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/)), el cual ya contiene exactamente la misma interfaz y catálogo que la rama de integración.

---

## 11. Riesgos y Limitaciones del Entorno No Productivo

1. **Catálogo Reducido:** Actualmente contiene solo 1 oportunidad real (`OP-005`) y 5 demostrativas. Los evaluadores deben comprender que no se trata de una bolsa de empleo activa masiva, sino de un prototipo de validación de modelo editorial.
2. **Limitaciones Específicas de OP-005:** Es un puesto profesional de jornada completa que requiere 1+ años de experiencia previa y conocimiento de SQL/ERP; no es una práctica preprofesional. Su modalidad de trabajo no fue especificada por el empleador en el ATS.
3. **Persistencia Local:** Los filtros, preferencias y selecciones de comparación se mantienen en la memoria del navegador durante la sesión; no se almacenan en servidores remotos ni cookies de terceros.

---

## 12. Separación entre Feedback Informal y Validación Formal R3-02

Para salvaguardar la integridad de la investigación científica:

1. **El feedback informal no computa como cuota:** Las opiniones espontáneas de amistades o familiares se registrarán en [`docs/research/r3-02-informal-feedback-template.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-informal-feedback-template.md) y se considerarán insumos preliminares.
2. **Requisitos para formalizar una sesión:** Una sesión solo podrá trasladarse a las plantillas oficiales `P01`–`P08` si la persona evaluadora:
   - Cumple estrictamente con los criterios de elegibilidad de `P-EST`, `P-EGR` o `P-JUN`.
   - Otorga consentimiento informado formal previo.
   - Es moderada de forma neutral siguiendo el guion de 45 minutos de [`docs/research/r3-02-moderator-field-guide-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-moderator-field-guide-2026-11-18.md).
   - Supera la rúbrica de QA (Sección 6) con veredicto `VALID`.

---

## 13. Siguiente Acción Recomendada

1. **Evaluación Personal del Propietario:** Iniciar el servidor local (`python server.py`) y explorar detenidamente la navegación, filtros y ficha de CookUnity.
2. **Evaluación con Amigos:** Elegir entre la opción de **Pantalla Compartida** (videollamada) o **Clonación Local** para recopilar las primeras impresiones usando la [Plantilla de Feedback Informal](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-informal-feedback-template.md).
3. **Preparación de Campo Formal:** Cuando se decida iniciar el trabajo de campo formal de R3-02, utilizar el [Kit de Reclutamiento](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-recruitment-materials-kit-2026-11-18.md) para convocar a los 5 a 8 participantes de la muestra oficial.
