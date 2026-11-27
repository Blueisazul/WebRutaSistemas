# TASK-FIX-URL-01 — ATS Publication URL Remediation and Quality Enforcement

**Identificador:** `TASK-FIX-URL-01`  
**Fecha:** 2026-11-27  
**Fase:** Corrección transversal de calidad del catálogo  
**Prioridad:** P1 — Crítica  
**Clasificación:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]`  
**Estado:** `COMPLETADO`  
**Repositorio:** `Blueisazul/WebRutaSistemas`  
**Commit base verificado:** `6b754da`  
**Rama:** `main`

---

## 1. Resumen Ejecutivo y Causa Raíz

Durante la auditoría `AUDIT-VELORA-R5-R7-GEO-URL-FUENTES` se identificó que el botón **«Ver publicación original»** en la interfaz de Velora abría endpoints JSON crudos de la API REST de Greenhouse (`https://boards-api.greenhouse.io/v1/boards/{boardToken}/jobs`) en lugar de páginas HTML legibles.

### Causa Raíz
1. **Conector Greenhouse (`collector/ats_connectors.py`):**  
   La función `transform_greenhouse_payload()` asignaba la variable fija `source_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"` como `sourceUrl` del registro canónico y como evidencia de origen. La URL web de la vacante (`job.get("absolute_url")`) se asignaba a `applyUrl`.
2. **Conector Lever (`collector/ats_connectors.py`):**  
   `transform_lever_payload()` asignaba de forma equivalente la URL del endpoint API JSON `https://api.lever.co/v0/postings/{site}?mode=json` a `sourceUrl`.
3. **Catálogo canónico (`data/opportunities.seed.json`):**  
   El mapeo erróneo se persistió históricamente en 97 oportunidades del seed.
4. **Prueba unitaria desalineada (`tests/test_ats_connectors.py`):**  
   La prueba unitaria original afirmaba explícitamente `self.assertEqual(first["sourceUrl"], "https://boards-api.greenhouse.io/v1/boards/empresa-ficticia/jobs")`, validando como correcto el comportamiento defectuoso.

---

## 2. Reconciliación e Inventario Real de Registros

### Aclaración de la Discrepancia Aritmética
La auditoría señalaba 97 registros afectados con Greenhouse API, mencionando cualitativamente 86 de Canonical y 2 de Sezzle. La inspección exacta y reproducible del catálogo canónico reveló la composición completa:

- **Canonical (`greenhouse-canonical`):** 75 registros
- **Sezzle (`greenhouse-sezzle`):** 9 registros
- **Encora (`greenhouse-encora` / `encora10`):** 13 registros (`OP-099` a `OP-111`)
- **Total exacto afectado:** **97 registros**

### Inventario Categórico del Catálogo Canónico (112 registros)
1. **Registros con `sourceUrl` apuntando a `boards-api.greenhouse.io`:** 97 registros (100% remediados).
2. **Registros con `sourceUrl` apuntando a `api.lever.co`:** 0 registros (no había vacantes históricas de Lever en el seed).
3. **Registros con otros endpoints JSON:** 0 registros.
4. **Registros con `sourceUrl` web ya válida:** 15 registros (`OP-001` a `OP-014` y `QA-001`).
5. **Registros sin `sourceUrl`:** 0 registros.
6. **Registros con `applyUrl` ausente:** 0 registros.
7. **Registros con coincidencia `sourceUrl == applyUrl`:**
   - Antes de la remediación: 5 registros (`OP-001`, `OP-002`, `OP-003`, `OP-004`, `QA-001`).
   - Posterior a la remediación: 102 registros (en las vacantes de Greenhouse donde la página oficial de publicación y la postulación directa comparten la misma URL web canónica).

---

## 3. Modificaciones Técnicas Realizadas

### 3.1. Conectores ATS (`collector/ats_connectors.py`)
- **Greenhouse (`transform_greenhouse_payload`):**  
  Se reestructuró la asignación de URLs:
  - `item_source_url`: URL HTML pública navegable del puesto (`job.get("absolute_url")`).
  - `item_apply_url`: URL de postulación oficial correspondiente (`raw_url`).
  - `candidate["sourceUrl"]`: asignado a `item_source_url`.
  - `fieldEvidence`: evidencia de `sourceUrl` apunta a la página web oficial navegable.
- **Lever (`transform_lever_payload`):**  
  Se corrigió la extracción de URLs de Lever:
  - `item_source_url`: `posting.get("hostedUrl") or posting.get("applyUrl")` (página pública del empleo en Lever).
  - `item_apply_url`: `posting.get("applyUrl") or posting.get("hostedUrl")` (formulario de postulación).

### 3.2. Reglas de Calidad Deterministas (`scripts/catalog_quality.py`)
Se incorporó una regla estricta de linteo en `validate_records()`:
```python
source_ok, source_host = valid_https_url(item.get("sourceUrl"))
if not source_ok:
    result.errors.append(f"{prefix}.sourceUrl debe ser HTTPS")
elif source_host in {"boards-api.greenhouse.io", "api.lever.co"}:
    result.errors.append(f"{prefix}.sourceUrl no puede apuntar a endpoints API REST ({source_host}); debe ser una página web navegable")
```

### 3.3. Salvaguarda Defensiva en Frontend (`app.js`)
Se introdujo la función `safeNavigableWebUrl(value)` que valida que la URL sea HTTPS y no corresponda a dominios conocidos de APIs REST crudas (`boards-api.greenhouse.io`, `api.lever.co`).  
Si una vacante tuviera de forma anómala una URL de API, el botón «Ver publicación original» no se renderiza, evitando descargas de payloads JSON en el navegador del usuario.

### 3.4. Validador de Candidatos (`scripts/validate_candidates.py`)
Se unificó la comprobación de hosts autorizados para `candidate.sourceUrl` permitiendo tanto `allowedHosts` como `allowedPostingHosts` declarados en la fuente institucional.

### 3.5. Remediación de Datos y Reconstrucción Canónica
Se remediaron individualmente los 97 registros afectados en `data/opportunities.seed.json`:
- `sourceUrl` actualizado con la URL web verificada proveniente de `applyUrl` / `evidenceUrl`.
- Entrada de `fieldEvidence` para `sourceUrl` actualizada coherentemente.
- Se reconstruyó explícitamente `data/opportunities.json` mediante `python scripts/build_catalog.py --write --as-of 2026-11-23 --generated-at 2026-11-23T13:54:01+00:00`.
- Se verificó la paridad y validación completa con `python scripts/build_catalog.py --check --as-of 2026-11-23`.

---

## 4. Pruebas y Certificación

| Suite de Pruebas | Resultado | Observaciones |
| :--- | :---: | :--- |
| `tests/test_ats_connectors.py` | **18 PASSED** | Valida contratos web para Greenhouse y Lever; rechaza URLs de API. |
| `tests/test_catalog_quality.py` | **24 PASSED** | Valida regla que rechaza endpoints API REST en `sourceUrl`. |
| `tests/test_candidates.py` | **11 PASSED** | Candidate Schema 2 y validaciones locales. |
| `tests/test_revalidation_lifecycle.py`| **10 PASSED** | Ciclo de vida y detección de cambios inalterado. |
| `tests/test_assisted_discovery.py` | **14 PASSED** | Radares asistidos y promoción conforme. |
| **Suite completa Python** | **328 PASSED** (0 fallos, 0 errores) | Suite integral del proyecto pasando al 100%. |
| **Suite de UI Node.js (`catalog_ui.test.cjs`)** | **20 PASSED** (Exit code 0) | Valida que el frontend no abra endpoints REST en el modal ni en tarjetas. |

---

## 5. Gobernanza y Preservación

- **Commits realizados:** 0
- **Push / Merge / Pull Request:** 0
- **Tags creados:** 0
- **Despliegues (GitHub Pages / Vercel):** 0
- Todos los cambios se mantienen en el árbol de trabajo local en estado limpio para revisión del propietario.
