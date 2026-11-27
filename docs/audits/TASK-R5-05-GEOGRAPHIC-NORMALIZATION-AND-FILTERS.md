# TASK-R5-05 — Normalización Geográfica y Segmentación del Ámbito Territorial de las Oportunidades

**Fecha de Ejecución:** 27 de noviembre de 2026  
**Proyecto:** Velora  
**Fase:** R5 — Cobertura nacional y experiencia de descubrimiento  
**Estado:** `COMPLETED_VERIFIED`  
**Prioridad:** P1  
**Clasificación:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]` + `[MEJORA_UX]`  
**Repositorio:** `Blueisazul/WebRutaSistemas`  
**Autorización:** Aprobada expresamente por el propietario bajo el principio OSS-first estricto.

---

## 1. Contexto y Objetivos

La auditoría transversal de Velora identificó dos problemas estructurales en la experiencia de búsqueda territorial:
1. **Problema A (Falta de selector visible de ubicaciones):** El usuario podía escribir texto en el campo libre `#location`, pero carecía de una lista desplegable con las ubicaciones reales disponibles en el catálogo.
2. **Problema B (Confusión entre vacantes locales en Perú e internacionales remotas):** Las oportunidades remotas internacionales (ej. Canonical con 75 vacantes "Home based - Worldwide (Perú elegible)") copaban los resultados de búsqueda geográfica, desdibujando la presencia de oportunidades con sede física y contratación local en el Perú (ej. CookUnity, OSITRAN, Encora).

### Objetivos Ejecutados
- **Etapa A (Taxonomía y Normalización Backend):**
  - Desacoplar tres dimensiones ortogonales e independientes:
    1. **Ámbito Territorial / Elegibilidad para Perú:** `PERU_LOCAL`, `PERU_REMOTE`, `INTERNATIONAL_REMOTE_PERU_ELIGIBLE`, `INTERNATIONAL_REMOTE_UNCONFIRMED`, `NOT_ELIGIBLE_PERU`, `UNSPECIFIED`.
    2. **Modalidad Físico-Espacial:** `ONSITE` (Presencial), `HYBRID` (Híbrido), `REMOTE` (Remoto), `UNSPECIFIED`.
    3. **Ubicación Territorial en Perú:** Departamento (24 departamentos + 1 provincia constitucional), provincia y distrito/sede.
  - Implementar clasificador determinista y *fail-closed* en `collector/geography.py` con cero dependencias externas (sin geocodificadores, servicios de red ni bibliotecas de terceros).
- **Etapa B (Selectores Dinámicos en Frontend):**
  - Actualizar `index.html` incorporando el selector de **Ámbito territorial** (`#scope-filter`) y el selector dinámico de **Ubicación en Perú** (`#department-filter`), refinando el campo `#location` para búsqueda libre complementaria.
  - Actualizar `app.js` poblando dinámicamente `#department-filter` con las ubicaciones peruanas presentes en el catálogo (evitando opciones vacías sin resultados).
  - Integrar etiquetas visuales de ámbito (`geographicScopeTag`) en tarjetas y modal de detalle.
  - Garantizar sincronización completa con reset de filtros y búsqueda reactiva.

---

## 2. Inventario Canónico del Catálogo (112 registros analizados)

El análisis determinista de los 112 registros de `data/opportunities.seed.json` arrojó la siguiente distribución de ámbito territorial:
- `PERU_LOCAL` (14 registros):
  - CookUnity (2 vacantes presenciales/híbridas en Lima: `OP-094`, `OP-095`).
  - OSITRAN (4 vacantes CAS presenciales en Lima: `OP-001`, `OP-002`, `OP-003`, `OP-111`).
  - Encora (8 vacantes presenciales/híbridas en Lima: `OP-101`, `OP-102`, `OP-103`, `OP-104`, `OP-105`, `OP-106`, `OP-109`, `OP-110`).
- `PERU_REMOTE` (2 registros):
  - Encora (`OP-107`, `OP-108` especificando explícitamente "Perú (Remoto nacional)").
- `INTERNATIONAL_REMOTE_PERU_ELIGIBLE` (95 registros):
  - Canonical (75 vacantes "Home based - Worldwide (Perú elegible)").
  - Sezzle (18 vacantes "Latin America (Perú elegible)").
  - 42Labs (2 vacantes demostrativas "Remoto (Chile, Perú o Colombia)").
- `INTERNATIONAL_REMOTE_UNCONFIRMED` (1 registro):
  - Launchpad Technologies (`OP-004`: "Remoto global; confirmar contratación desde Perú").
- `NOT_ELIGIBLE_PERU` (0 registros en catálogo actual).
- **Departamentos peruanos detectados:** Lima (14 oportunidades).

---

## 3. Arquitectura y Componentes Implementados

### 3.1 Módulo Backend (`collector/geography.py`)
- Define constantes canónicas `SCOPE_PERU_LOCAL`, `SCOPE_PERU_REMOTE`, `SCOPE_INTL_ELIGIBLE`, `SCOPE_INTL_UNCONFIRMED`, `SCOPE_NOT_ELIGIBLE`, `SCOPE_UNSPECIFIED`.
- Mapea los 25 departamentos/jurisdicciones administrativas peruanas (24 departamentos + Provincia Constitucional del Callao) con regex optimizadas para evitar falsos positivos.
- Implementa `classify_opportunity_geography(location, eligibility, mode, title, employer)`:
  - Detección *fail-closed* de exclusión extranjera explícita.
  - Detección de remoto nacional peruano (`PERU_REMOTE`).
  - Detección de convocatorias locales en territorio nacional (`PERU_LOCAL`).
  - Detección de señales de confirmación pendiente (`INTERNATIONAL_REMOTE_UNCONFIRMED`).
  - Detección de vacantes internacionales remotas con elegibilidad verificada (`INTERNATIONAL_REMOTE_PERU_ELIGIBLE`).
- Dataclass `GeographicClassification` con método `to_dict()`.

### 3.2 Interfaz de Usuario (`index.html`)
- Sección de filtros geográficos refinada en el bloque de filtros secundarios:
  - `<select id="scope-filter">`: Opciones para todos los ámbitos, Perú local, Remoto nacional, Internacional elegible e Internacional por confirmar.
  - `<select id="department-filter">`: Opciones dinámicas para departamentos con oferta activa.
  - `<input id="location">`: Reorientado como búsqueda textual libre complementaria (ciudad, sede, distrito).

### 3.3 Motor Frontend (`app.js`)
- `GEOGRAPHIC_SCOPES`: Objeto de configuración con badges semánticos, labels y shortLabels accesibles.
- `getJobGeographicScope(job)`: Normalizador determinista homólogo al backend Python.
- `getJobDepartment(job)`: Extractor de departamentos peruanos sobre 25 jurisdicciones.
- `geographicScopeTag(job)`: Componente de renderizado de etiquetas en `renderCard()`.
- `populateFilters()`: Poblado dinámico de `#department-filter` con `Set` de departamentos presentes en `catalog`, ordenados alfabéticamente en español (`es`).
- `getVisibleJobs()`: Filtrado reactivo por `filters.scope.value` y `filters.department.value`, con inclusión de metadatos geográficos en `searchable`.
- `updateCatalogView()`: Inclusión de selectores en el estado `isFiltered` y limpieza integral en el evento `reset`.

---

## 4. Pruebas y Certificación de Calidad

### 4.1 Suite Unitaria Backend (`tests/test_geography.py`)
- 14 pruebas unitarias cubriendo:
  - Presencial y semipresencial en Lima (`PERU_LOCAL`).
  - Remoto nacional circunscrito a Perú (`PERU_REMOTE`).
  - Remoto multinacional con Perú explícito (`INTERNATIONAL_REMOTE_PERU_ELIGIBLE`).
  - Remoto global con contratación por confirmar (`INTERNATIONAL_REMOTE_UNCONFIRMED`).
  - Exclusiones territoriales de Perú (`NOT_ELIGIBLE_PERU`).
  - Extracción de departamentos (Lima, Arequipa, Cusco, Piura, Callao).
  - Normalización de modalidades (`ONSITE`, `HYBRID`, `REMOTE`).
- **Resultado:** 14/14 tests aprobados en 0.003s.

### 4.2 Suite UI / DOM en Node.js (`tests/catalog_ui.test.cjs`)
- Verificación de presencia de elementos `#scope-filter` y `#department-filter`.
- Verificación de opciones canónicas de ámbito en HTML.
- Pruebas de filtrado por cada ámbito territorial individual.
- Pruebas de filtrado por departamento (`Lima`).
- Pruebas de combinación entre ámbito, departamento y búsqueda libre.
- Verificación del renderizado de `geographicScopeTag` y sección en el modal de detalle.
- **Resultado:** 100% de escenarios de filtrado y degradación aprobados.

### 4.3 Suite Global de Regresión
- `python scripts/build_catalog.py --check --as-of 2026-11-23`:
  - Catálogo válido: 112 registros canónicos intactos.
- `python -m unittest discover -s tests -p "test_*.py"`:
  - 329 pruebas unitarias ejecutadas, 0 errores, 0 fallos.
- `node tests/catalog_ui.test.cjs`:
  - Escenarios de filtrado público y degradación aprobados.

---

## 5. Salvaguardas de Gobernanza y No Regresión
- **Zero Hallucination:** No se infieren departamentos sin evidencia léxica explícita.
- **Fail-Closed:** Señales ambiguas o por confirmar se degradan a `INTERNATIONAL_REMOTE_UNCONFIRMED` o `UNSPECIFIED`.
- **Integridad Canónica:** Cero modificaciones no autorizadas en `data/opportunities.seed.json` o `data/opportunities.json`.
- **Preservación del Repositorio:** Cero commits, pushes, tags o despliegues no autorizados. Integridad de remediaciones previas (`TASK-FIX-URL-01`, pilotos de radar) preservada al 100%.
