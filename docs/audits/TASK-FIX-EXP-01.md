# INFORME DE AUDITORÍA Y REVISIÓN PRE-RELEASE — TASK-FIX-EXP-01
## Corrección prioritaria de expiración de convocatorias y retirada definitiva de Greenhouse

- **Identificador de tarea:** `TASK-FIX-EXP-01`
- **Proyecto:** Velora (anteriormente Ruta Sistemas / WebRutaSistemas)
- **Repositorio:** `Blueisazul/WebRutaSistemas`
- **Rama activa:** `main`
- **Commit HEAD:** `dca999d92d1b9ee1831e6d19a4c0865e584c8474`
- **Prioridad:** `P0` (Confiabilidad y veracidad de catálogo)
- **Clasificación:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]`
- **Fecha de auditoría:** 27 de noviembre de 2026
- **Estado de implementación local:** `COMPLETED_VERIFIED`
- **Estado de integración Git:** `PENDING_OWNER_AUTHORIZATION` (0 commits, 0 pushes ejecutados)
- **Estado de despliegue en producción:** `NOT_DEPLOYED` (Producción en GitHub Pages y Vercel se mantiene en commit `dca999d`)
- **Dictamen pre-release:** `READY_FOR_CONSOLIDATION`

---

## 1. OBJETIVO DEL BLOQUE

Verificar y certificar técnica y documentalmente que:
1. Las convocatorias vencidas o con plazo expirado (`deadline < today` en `America/Lima` o timestamp vencido) no aparezcan como activas en el catálogo web y que sus llamadas a la acción de postulación estén deshabilitadas (`aria-disabled="true"`, sin enlace interactivo).
2. La plataforma internacional Greenhouse ha sido retirada definitivamente de las fuentes activas y de la bandeja de evaluación staging (`inbox.local.json`), preservando al mismo tiempo la trazabilidad histórica de lo ya registrado en el catálogo canónico.
3. Se conservan intactas las salvaguardas de no mutación no autorizada de datos canónicos y cero exposición de PII.
4. Las suites completas de pruebas (Python, Node VM y Playwright E2E) aprueban al 100%.

---

## 2. AUDITORÍA DEL ESTADO DE GIT Y SALVAGUARDAS

- **Rama:** `main` sincronizada con `origin/main` en `dca999d`.
- **Commits locales creados:** **0**.
- **Pushes ejecutados:** **0**.
- **`git diff --check`:** Aprobado sin errores de espacio en blanco ni conflictos.
- **Catálogo Canónico:**
  - `data/opportunities.seed.json`: **100% intacto**.
  - `data/opportunities.json`: **100% intacto**.
  - `scripts/build_catalog.py --check --as-of 2026-11-23`: Paridad criptográfica absoluta certificada.

---

## 3. VERIFICACIÓN FUNCIONAL DE EXPIRACIÓN Y VIGENCIA (DECISIÓN B / DECISIÓN 9 / DECISIÓN 11)

### 3.1 Reglas Temporales Implementadas
1. **Fecha civil (`YYYY-MM-DD`):** Una oportunidad con fecha límite correspondiente al día civil actual en Lima (`America/Lima`) se considera vigente hasta el final del día (`deadline == today` es válida). Expira a partir del día siguiente (`deadline < today`).
2. **Timestamp con hora (ISO 8601):** Evaluado contra el instante temporal exacto en `America/Lima`. Si el instante ya transcurrió, expira inmediatamente.
3. **Fecha ausente (`null` o vacía):** No se asume vencida por inferencia arbitraria.
4. **Desacoplamiento semántico:** La fecha límite de postulación (`deadline`) es independiente de:
   - `employmentEndDate` (fecha de culminación del contrato de trabajo).
   - `lastVerifiedAt` (antigüedad de verificación técnica).
   - TTL de 7 días (frescura de evidencia).
5. **Transición forzosa a histórico:** Oportunidades en estado `expired`, `closed` o `withdrawn` transicionan automáticamente a `publicationStatus: "historical"`.
6. **Desactivación de botones de postulación:**
   - En tarjetas de catálogo (`renderCard`): Botón desactivado con etiqueta textual *"Convocatoria concluida"* o *"Propuesta retirada"*.
   - En modal de detalle (`renderDetailContent`): Enlaces `#btn-apply-main` y `#btn-apply-footer` sin `href`, clase desactivada y atributo `aria-disabled="true"`.
   - En comparador (`renderComparison`): Enlace en cabecera de columna neutralizado.
7. **Segregación de métricas:**
   - `#metric-total` refleja exclusivamente vacantes activas vigentes dentro del TTL.
   - `#metric-secondary` agrupa convocatorias en revisión / históricas sin solapamientos.

---

## 4. VERIFICACIÓN DE RETIRADA DE GREENHOUSE (DECISIÓN A / DECISIÓN 10)

1. **Fuentes retiradas en `collector/sources.json`:**
   - `greenhouse-canonical`: `enabled: false`, `decision: "withdrawn"`, `automatedAccessStatus: "withdrawn"`.
   - `greenhouse-sezzle`: `enabled: false`, `decision: "withdrawn"`, `automatedAccessStatus: "withdrawn"`.
   - `greenhouse-cookunity`: `enabled: false`, `decision: "withdrawn"`, `automatedAccessStatus: "withdrawn"`.
   - `greenhouse-encora`: `enabled: false`, `decision: "withdrawn"`, `automatedAccessStatus: "withdrawn"`.
   - `greenhouse-public-job-board-template`: `enabled: false`, `decision: "withdrawn"`.
   - `canonical-careers`: `enabled: false`, `decision: "withdrawn"`, `automatedAccessStatus: "withdrawn"`.
2. **Depuración de bandeja staging (`data/candidates/inbox.local.json`):**
   - Total de candidatos en bandeja: 297.
   - Candidatos procedentes de Greenhouse: Exactamente 236.
   - Estado de candidatos Greenhouse: 236 rechazados (`editorialReview.status: "rejected"`).
   - Candidatos Greenhouse en `pending_review`: **Exactamente 0**.
   - Candidatos Greenhouse en `approved_for_catalog`: **Exactamente 0**.
3. **Preservación técnica:**
   - Conectores y funciones de parseo en `collector/ats_connectors.py` preservados intactos para garantizar trazabilidad histórica y compatibilidad.

---

## 5. RESULTADOS DE LA SUITE DE PRUEBAS

| Comando ejecutado | Alcance | Código de salida | Total pruebas | Aprobadas | Fallidas | Tiempo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `python scripts/validate_catalog.py` | Esquema 2 y coherencia del catálogo canónico | `0` | 112 fichas | 112 | 0 | 0.4s |
| `python scripts/build_catalog.py --check --as-of 2026-11-23` | Paridad determinista entre seed y snapshot | `0` | 112 registros | 112 | 0 | 0.3s |
| `node --check app.js` | Sintaxis y compilación JavaScript | `0` | — | — | 0 | 0.1s |
| `python -m unittest tests/test_lifecycle_expiration.py -v` | Nueva suite unitaria dedicada de expiración | `0` | 11 | 11 | 0 | 0.01s |
| `node tests/catalog_ui.test.cjs` | Pruebas de degradación, filtros, UI y métricas | `0` | 16 escenarios | 16 | 0 | 0.2s |
| `python -m unittest discover -s tests` | Suite completa Python de regresión | `0` | 356 | 356 | 0 | 4.78s |
| `npx playwright test tests/e2e/catalog.spec.cjs` | Pruebas E2E completas (Desktop, Mobile, Narrow) | `0` | 30 | 30 | 0 | 3.7m |

---

## 6. INVENTARIO DE CAMBIOS Y SEGREGACIÓN DE TAREAS

### 6.1 Archivos pertenecientes a `TASK-FIX-EXP-01`
- `app.js`: Lógica de expiración `isDeadlineExpired`, reglas de desactivación de postulación y estado `withdrawn`.
- `collector/evidence.py`: Soporte de timestamps ISO 8601 con zona horaria en evaluación de vigencia.
- `collector/revalidation.py`: Detección de vencimiento de fecha límite y bypass offline con `fixtures_dir`.
- `scripts/catalog_quality.py`: Admisión de `withdrawn`, soporte de ISO 8601 en `parse_date` y validación de expiración.
- `collector/sources.json`: 6 fuentes Greenhouse marcadas como `withdrawn` y `enabled: false`.
- `data/candidates/inbox.local.json`: 236 candidatos Greenhouse transicionados a `rejected`.
- `tests/test_lifecycle_expiration.py`: Nueva suite unitaria dedicada.
- `tests/catalog_ui.test.cjs`: Pruebas de contrato de interfaz para `isDeadlineExpired` y métricas.
- `tests/test_acquisition_pilot.py`: Aserción de fuentes activas Lever y retirada de Greenhouse.
- `tests/test_autopublish.py`: Fixtures adaptadas a fuente aprobada `lever-kavak`.
- `tests/test_classification_and_coverage.py`: Ajuste de recuento a 10 fuentes aprobadas.
- `tests/test_periodic_acquisition_ops.py`: Ajuste de métricas a 10 fuentes evaluadas.
- `tests/test_source_evaluation.py`: Verificación de `canonical-careers` como retirada.
- `tests/e2e/catalog.spec.cjs`: Timeout defensivo en `#QA-001`.
- `docs/audits/VELORA-OPEN-DECISIONS.md`: Formalización de Decisiones 10 y 11.
- `docs/roadmap/VELORA-MASTER-ROADMAP.md`: Actualización de estado de la tarea.

### 6.2 Modificaciones no pertenecientes a TASK-FIX-EXP-01 (Pendientes en Working Tree)
- `collector/pe_connectors.py` y `tests/test_pe_connectors.py`: Pertenecen a `TASK-R5-03` (Conector HiringRoom formalizado bajo Decisión 8).
- `scripts/editorial_cli.py`, `collector/assisted_discovery.py`, `tests/test_assisted_discovery.py` y reportes en `docs/audits/R5-04-*`: Pertenecen a `TASK-R5-04-02` / `TASK-R5-04-03` (Descubrimiento Asistido de convocatorias estatales).
- `docs/audits/TASK-FIX-E2E-R5-05.md` y `docs/audits/VELORA-PRE-RELEASE-URL-GEOGRAPHY-CONSOLIDATION.md`: Documentos de auditoría de integración previa.

---

## 7. DICTAMEN FINAL Y RECOMENDACIÓN

- **Dictamen:** `READY_FOR_CONSOLIDATION`
- **Condición:** Los cambios de `TASK-FIX-EXP-01` se encuentran completamente implementados, probados y verificados en el entorno local. No están desplegados en producción.
- **Acción requerida del propietario:** Autorizar expresamente si desea consolidar únicamente `TASK-FIX-EXP-01` de manera aislada (staging selectivo de archivos de esta tarea) o consolidar de forma conjunta las tareas complementarias (`TASK-R5-03` HiringRoom + `TASK-FIX-EXP-01`).
