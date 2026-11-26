# INFORME DE AUDITORÍA Y ACEPTACIÓN TÉCNICA — TASK-R7-01
## Taxonomía de Regímenes Laborales Peruanos (CAS, 728, Formativo, Civil, Otros)

- **Identificador de Tarea:** `TASK-R7-01`
- **Fase:** R7 — Valor profesional y UX
- **Proyecto:** Velora
- **Prioridad:** `P2` (Valor funcional Perú)
- **Clasificación:** `[DESARROLLO_PROPIO - Justificado]`
- **Fecha de Certificación:** 2026-11-25
- **Estado Resultante:** `COMPLETED`
- **Dependencias:** `TASK-R5-01`, `TASK-R6-01`, `TASK-R6-02` (Satisfechas)

---

## 1. Resumen Ejecutivo

En cumplimiento de la directiva de producto y arquitectura para Velora, se ha diseñado, implementado y verificado la **Taxonomía Integral de Regímenes Laborales Peruanos**. Esta funcionalidad permite clasificar de forma determinista, comprensible y con estricta rigurosidad legal las oportunidades laborales y formativas dirigidas a estudiantes y profesionales de Ingeniería de Sistemas y TI en el Perú.

La implementación satisface plenamente el principio de arquitectura **OSS-First / Zero New Dependencies**, retrocompatibilidad estricta con Schema 2, principio fail-closed ante ambigüedad, y preservación inalterada de la paridad criptográfica de los catálogos canónicos publicados.

---

## 2. Taxonomía Canónica Implementada

Se establecieron siete categorías normalizadas inmutables, acompañadas de sus niveles de certeza y citas normativas peruanas oficiales:

| ID Canónico | Denominación Oficial | Etiqueta UI | Marco Normativo Principal | Naturaleza Jurídica |
|---|---|---|---|---|
| `PRE_PROFESSIONAL_INTERNSHIP` | Prácticas preprofesionales | Prácticas Pre | Ley N° 28518 | Modalidad formativa laboral para estudiantes de educación superior |
| `PROFESSIONAL_INTERNSHIP` | Prácticas profesionales | Prácticas Pro | Ley N° 28518 / Ley N° 31396 | Modalidad formativa laboral para egresados o bachilleres (reconocida como experiencia) |
| `CAS` | Contratación Administrativa de Servicios | CAS | D. Leg. N° 1057 / Ley N° 29849 / Ley N° 31131 | Régimen especial público privativo del Estado por concurso público |
| `LABOR_REGIME_728` | Régimen Laboral Privado (D. Leg. 728) | Planilla 728 | TUO D. Leg. N° 728 (D.S. 003-97-TR) / Ley 27735 | Contrato de trabajo subordinado con CTS, gratificaciones de ley y vacaciones |
| `CIVIL_SERVICES` | Locación de Servicios / Honorarios | Locación / Honorarios | Código Civil del Perú (Art. 1764 y ss.) | Contratación civil autónoma por honorarios (4ta categoría) sin subordinación |
| `OTHER` | Otras modalidades contractuales | Otra modalidad | Contratos internacionales / Acuerdos privados | Contratación B2B internacional, contractor, D. Leg. 276, Ley 30057 |
| `UNSPECIFIED` | Modalidad no especificada | Por confirmar régimen | Sujeto a verificación en bases | Fail-closed: publicación sin suficiente evidencia contractual explícita |

### Niveles de Certeza (`Certainty`)
1. `EXPLICIT_EVIDENCE`: Evidencia documental o textual explícita en `contractType`, `opportunityType`, `requisition` o bases del concurso.
2. `DERIVED_BASES`: Derivación lógica determinista a partir de combinación contextual (ej. convocatoria de prácticas dirigida a nivel estudiante, o presencia de CTS/gratificaciones completas).
3. `UNSPECIFIED`: Política fail-closed. Velora jamás asume un régimen (ej. asumir 728 para empresas privadas o CAS para entidades públicas) sin respaldo textual demostrable.

---

## 3. Arquitectura y Componentes Desarrollados

### 3.1. Módulo Central Normalizador (`collector/labor_regime.py`)
- Declaración de constantes canónicas `ALL_REGIMES` y `ALL_CERTAINTIES`.
- Diccionario maestro `REGIME_DEFINITIONS` con metadata jurídica completa: naturaleza, jornada máxima, compensación mínima legal, garantías esenciales y cautelas/riesgos específicos.
- Clasificador determinista `classify_labor_regime(record) -> LaborRegimeClassification`.
- Normalizador universal de texto `normalize_regime_id(val)`.

### 3.2. Integración en Flujo de Adquisición y Autopublicación
- `collector/classification.py`: Incorporación de `labor_regime`, `labor_regime_certainty` y `labor_regime_explanation` en `ClassificationResult`.
- `collector/autopublish.py`: Función `convert_candidate_to_opportunity()` enriquece automáticamente las nuevas oportunidades promovidas con `laborRegime` y `laborRegimeCertainty`.
- `scripts/validate_candidates.py`: Registro de `contractType`, `laborRegime` y `laborRegimeCertainty` en campos reconocidos de candidatos.

### 3.3. Contrato de Calidad y Esquema 2 (`scripts/catalog_quality.py`)
- Definición de conjuntos `LABOR_REGIMES` y `LABOR_REGIME_CERTAINTIES`.
- Validación estricta en `validate_records()`: si los campos existen, deben pertenecer a los conjuntos canónicos autorizados; su omisión mantiene 100% de validez retrocompatible.

### 3.4. Interfaz de Usuario y Experiencia Jamstack (`index.html` y `app.js`)
- **Filtro de Régimen:** `<select id="regime-filter">` integrado armónicamente en el grid responsivo de 8 filtros de `index.html`.
- **Badges visuales en tarjetas:** Función `regimeTag(job)` que renderiza en cada tarjeta una etiqueta con color temático según régimen y tooltip explicativo.
- **Resumen en Ficha de Oportunidad:** Tarjeta visual con icono Lucide `briefcase` en la cuadrícula de resumen superior.
- **Sección Normativa Detallada:** Bloque dedicado `Régimen Contractual y Marco Normativo` que desglosa naturaleza jurídica, límites de jornada, compensación mínima, derechos garantizados, cautelas legales y descargo de responsabilidad orientativo.
- **Búsqueda reactiva:** Filtrado dinámico por régimen en `getVisibleJobs()`, persistencia al resetear filtros y soporte para búsqueda textual por nombre de régimen.

---

## 4. Evidencias Verificables de Pruebas

### 4.1. Pruebas Unitarias de Clasificación (`tests/test_labor_regime.py`)
- **23 pruebas ejecutadas, 23 aprobadas (100% OK):**
  - Validación de los 7 regímenes canónicos y sus marcos normativos.
  - Normalización de variaciones ortográficas y abreviaturas comunes.
  - Comportamiento fail-closed ante convocatorias genéricas sin contrato especificado.
  - Derivación formativa diferenciando estudiante (pre) de egresado (pro).
  - Detección de beneficios 728 (CTS + gratificaciones) y honorarios civiles (Código Civil 1764).
  - Validación de integración con autopublicación y calidad Schema 2.

### 4.2. Pruebas de Interfaz de Usuario (`tests/catalog_ui.test.cjs`)
- **Aprobado con exit code 0:**
  - Verificación de presencia de `<select id="regime-filter">` y las 7 opciones canónicas en `index.html`.
  - Pruebas en sandbox VM de filtrado por régimen para las 7 categorías y estado sin filtro.
  - Renderizado de etiquetas con badges temáticos y tooltips normativos.
  - Renderizado de tarjeta de resumen y sección detallada de marco normativo en `renderDetailContent()`.

### 4.3. Suite Global de Regresión
- Comando: `python -m unittest discover -s tests; node tests/catalog_ui.test.cjs`
- Resultado: **300 pruebas unitarias y de integración de Python pasando al 100%** + pruebas completas de frontend pasando sin regresión.

### 4.4. Integridad Criptográfica de Catálogos Canónicos
- `data/opportunities.seed.json`: SHA-256 `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917` (112 registros, INTACTO).
- `data/opportunities.json`: SHA-256 `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02` (112 registros, INTACTO).
- `git diff --exit-code data/` ejecutado satisfactoriamente (cero modificaciones).

---

## 5. Dictamen y Conclusión

La tarea `TASK-R7-01 — Taxonomía de Regímenes Laborales Peruanos (CAS, 728, Formativo)` se certifica como **COMPLETED**. Cumple todos los requisitos funcionales, arquitectónicos, de calidad de datos y de salvaguardas operativas.

Queda habilitada como siguiente acción única del Roadmap Maestro la tarea `TASK-R7-02 — Comparador de Trayectorias y Requisitos Técnicos`.
