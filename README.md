# Velora

Plataforma abierta de descubrimiento y evaluación de oportunidades profesionales y trayectorias formativas en tecnología (Ingeniería de Sistemas, Software, Datos y DevOps), con énfasis en Perú y vacantes remotas elegibles desde el país.

El objetivo de Velora es hacer comparables las condiciones laborales, la procedencia y la evidencia verificable de cada convocatoria, permitiendo decisiones de carrera fundamentadas sin depender de la opacidad de las bolsas de empleo convencionales. Velora no es una agencia de colocación ni una simple bolsa de prácticas: es un catálogo técnico estructurado basado en verificación rigurosa de fuentes primarias.

---

## 1. Qué es Velora y qué problema resuelve

En el mercado laboral tecnológico peruano e internacional, los estudiantes y profesionales enfrentan anuncios engañosos, intermediarios no autorizados, requisitos inflados y vacantes fantasma que permanecen abiertas semanas después de haber concluido el proceso.

Velora resuelve esta asimetría mediante:
1. **Evidencia por dato (*Field Evidence*):** Cada condición declarada (remuneración, modalidad, contrato, requisitos, tecnologías) debe contar con una URL HTTPS oficial verificable y una fecha de observación reciente.
2. **Desacople estricto entre Empleador y Difusor:** Se distingue inequívocamente quién contrata (`employer`) de la plataforma o canal que publica la oferta (`publisher`), evitando la confusión entre portales agregadores y vacantes directas.
3. **Canal oficial de postulación:** El enlace de postulación (`applyUrl`) solo se habilita hacia sistemas de seguimiento de postulantes (ATS) o portales corporativos directos y autorizados (`allowedHosts`).
4. **Política *Fail-Closed*:** Si una fuente no es accesible, si la evidencia supera la ventana de frescura o si existen dudas sobre la vigencia, la oportunidad nunca se promociona falsamente como activa y verificada.

---

## 2. Estado Actual del Catálogo y Métricas

A la fecha de corte actual (Noviembre 2026), el catálogo opera bajo **Schema Version 2**:

- **Total de registros en catálogo:** **112 fichas**.
- **Oportunidades reales auditadas:** **107 oportunidades**.
- **Fichas demostrativas:** **5 fichas** (`OP-001` a `OP-004`, `QA-001`), destinadas exclusivamente a calibración visual y pruebas de interfaz, deshabilitadas permanentemente para postulación.
- **Empresas integradas:** Empleadores internacionales y locales con ATS público auditado (Greenhouse, Lever), incluyendo Encora Perú (90 vacantes en staging, 13 convocatorias locales promovidas `OP-099` a `OP-111`), CookUnity (`OP-005`), Canonical (`OP-006` en adelante), Sezzle, entre otros.
- **Fuentes en evaluación/seguimiento:** Sector público (Talento Perú / SERVIR y convocatorias bajo Gob.pe) evaluadas con acceso controlado y bajo estudio institucional.

---

## 3. Modelo de Estados y Desacople de Frescura

Velora implementa un modelo de tres dimensiones ortogonales para garantizar veracidad sin causar "apagones informativos":

### A. Estado de Publicación (`publicationStatus`)
- **`active`:** Oportunidad vigente con evidencia reciente. Se lista en la vista principal con botón de postulación habilitado.
- **`unconfirmed`:** Convocatoria en revisión o cuya evidencia ha superado la ventana de frescura. No aparece en la búsqueda activa por defecto; se preserva íntegra y accesible mediante el filtro de revisión (*“Incluir no confirmadas”*).
- **`historical`:** Convocatoria cerrada, retirada o vencida. Se conserva para análisis histórico de remuneraciones y requisitos de mercado.

### B. Estado de Verificación (`verificationStatus`)
- **`verified`:** Convocatoria revalidada manualmente o mediante conector autorizado dentro de la ventana de frescura.
- **`stale`:** Oportunidad cuya última verificación supera el TTL de frescura.
- **`unverified`:** Oportunidad sin verificación primaria completa.

### C. Antigüedad y Ventana de Frescura (TTL)
- **TTL de verificación:** Configurado en **7 días calendario** (`verificationTtlDays: 7`), evaluado deterministamente en zona horaria `America/Lima` (UTC-05:00).
- **Regla de desacople (R4-11-03):** Superar el TTL degrada la visibilidad a `unconfirmed` / `stale` para proteger al usuario de postulaciones extemporáneas, pero **no destruye el registro ni vacía el catálogo**. El usuario puede consultar la ficha con un distintivo informativo ámbar (*“Pendiente de revalidación”*) y enlace a la publicación original.

---

## 4. Arquitectura del Sistema

Velora está diseñado con arquitectura **OSS-First, 100% estática en el cliente y reproducible**:

```
                                  [ Fuentes Primarias ]
                                (Greenhouse, Lever, Gob.pe)
                                             │
                                             ▼
                             [ collector/acquisition_runner.py ]
                                             │
                                             ▼
                             [ data/candidates/inbox.local.json ] (Staging)
                                             │
                               [ scripts/editorial_cli.py ]
                               (Deduplicación + Validación Schema 2)
                                             │ (Aprobación humana explícita)
                                             ▼
                             [ data/opportunities.seed.json ] (Canónica)
                                             │
                               [ scripts/build_catalog.py ]
                                             │
                                             ▼
                             [ data/opportunities.json ] (Snapshot Frontend)
                                             │
                                             ▼
                        [ GitHub Pages / Vercel Static Hosting ]
                         (index.html + app.js + styles.css)
```

- **Runtime Cero Dependencias:** El frontend funciona exclusivamente con HTML5 semántico, JavaScript ES Modules nativo (`app.js`), canvas WebGL2 opcional (`canvas.js`) y estilos utilitarios compilados (`styles.css`). No se cargan librerías externas, frameworks SPA ni rastreadores en runtime.
- **Proceso de Adquisición Offline-First:** Toda la ingestión y validación de datos se realiza con Python 3.12 utilizando únicamente la biblioteca estándar (`urllib`, `sqlite3`, `unittest`, `hashlib`).

---

## 5. Instalación, Validación y Ejecución Local

### Requisitos previos
- **Python 3.12+**
- **Node.js 22+** (para compilación de CSS y pruebas de Playwright)

### Instalación de herramientas de desarrollo
```bash
# Instalar dependencias fijadas de testing y compilador de CSS
npm ci

# Instalar navegadores para Playwright (solo la primera vez)
npx playwright install --with-deps chromium
```

### Compilación de estilos
```bash
# Compilar hoja de estilos minimizada de producción
npm run build:css

# Modo observador durante desarrollo de plantillas
npm run watch:css
```

### Ejecución de pruebas y validaciones
```bash
# 1. Comprobar sintaxis JavaScript de app.js
node --check app.js

# 2. Ejecutar pruebas unitarias del catálogo y estados (232 pruebas)
python -m unittest discover -s tests -v

# 3. Validar integridad de la semilla canónica y snapshot generado
python scripts/build_catalog.py --check
python scripts/validate_catalog.py

# 4. Validar formato de candidatos de ejemplo
python scripts/validate_candidates.py data/candidates/inbox.example.json

# 5. Ejecutar pruebas de filtrado y subpaths de Pages
node tests/catalog_ui.test.cjs

# 6. Ejecutar suite E2E completa de Playwright (accesibilidad + responsive + flujos)
npm run test:e2e
```

### Servidor local de desarrollo
```bash
python server.py
# Servidor local accesible en: http://127.0.0.1:4173/
```

---

## 6. CLI Editorial y de Observabilidad (`scripts/editorial_cli.py`)

Herramienta de línea de comandos para auditoría y gestión determinista de bandejas de entrada:

```bash
# Validar bandeja con verificación estricta de evidencias y fecha de corte
python scripts/editorial_cli.py validate-inbox data/candidates/inbox.example.json --verify-evidence --as-of 2026-11-24

# Inspeccionar métricas y distribución de estados
python scripts/editorial_cli.py inspect data/candidates/inbox.example.json --verify-evidence

# Análisis de deduplicación de candidatos frente al catálogo canónico
python scripts/editorial_cli.py deduplicate data/candidates/inbox.example.json

# Generar informe JSON integral consolidado
python scripts/editorial_cli.py report data/candidates/inbox.example.json --json-report
```

---

## 7. Limitaciones Actuales y Trabajo Futuro

Para preservar la máxima honestidad técnica con el usuario y el propietario:

1. **Cobertura Estatal en Fase de Diseño (R5):** Los conectores para el sector público peruano (`gobpe-convocatorias` y Talento Perú/SERVIR) están en diseño arquitectónico y no realizan scraping no regulado.
2. **Sin Recomendaciones Predictivas:** Velora no implementa algoritmos de recomendación opacos ni modelos predictivos de contratación; la comparación es tabular, objetiva y asistida por filtros transparentes.
3. **Revisión Humana Obligatoria:** La promoción de candidatos desde la bandeja local a la semilla canónica requiere una decisión editorial explícita (`editorialDecision`) con motivo y fecha auditables.
4. **Despliegues Oficiales:**
   - Producción GitHub Pages: `https://blueisazul.github.io/WebRutaSistemas/`
   - Producción Vercel: `https://velora-six-fawn.vercel.app/`
