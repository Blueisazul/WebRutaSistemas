# INFORME DE AUDITORÍA Y ACEPTACIÓN TÉCNICA — TASK-R7-02
## Comparador de Trayectorias y Requisitos Técnicos

- **Identificador de Tarea:** `TASK-R7-02`
- **Fase:** R7 — Inteligencia de condiciones laborales y profesionales
- **Proyecto:** Velora
- **Prioridad:** `P3` (Evolución de producto / Valor profesional)
- **Clasificación:** `[REUTILIZACIÓN_INTERNA]` + `[DESARROLLO_PROPIO - Justificado]`
- **Fecha de Certificación:** 2026-11-25
- **Estado Resultante:** `COMPLETED`
- **Dependencias:** `TASK-R7-01` (Satisfecha)

---

## 1. Resumen Ejecutivo

En cumplimiento de la directiva técnica para `TASK-R7-02`, se ha diseñado, implementado y validado el **Comparador de Trayectorias y Requisitos Técnicos** de Velora. La solución extiende el comparador existente (`#compare-dialog`, `compareIds`, `renderComparison()`) para contrastar de manera determinista, comprensible y explicable los requisitos técnicos, competencias y herramientas demandadas entre dos oportunidades laborales o formativas seleccionadas por el usuario.

El desarrollo se adhiere rigurosamente a los principios rectores de Velora:
- **Zero New Dependencies & OSS-First:** Implementado íntegramente con JavaScript vanilla nativo en el cliente y la biblioteca estándar de Python (`re`, `unicodedata`, `typing`) en el backend/collector.
- **Transparencia y Cero Suposiciones:** No inventa requisitos, no infiere competencias no declaradas y señala explícitamente las áreas donde una oportunidad no especifica requerimientos técnicos o formativos.
- **Sin Scoring ni Perfilamiento Arbitrario:** No utiliza modelos de Machine Learning, heurísticas opacas ni algoritmos de "ganador" o "mejor empleo". El usuario mantiene autonomía total de decisión con base en datos contrastables.
- **Trazabilidad Completa:** Cada competencia identificada registra el campo de origen (`skills`, `requirements`, `tasks`, `title`), su fragmento textual exacto de procedencia y su nivel de obligatoriedad.
- **Preservación Canónica:** Se mantuvo la paridad criptográfica SHA-256 inalterada en los catálogos canónicos (`data/opportunities.seed.json` y `data/opportunities.json`).

---

## 2. Diagnóstico del Comparador Previo y Reutilización Interna

### 2.1. Estado Previo
El comparador base (`renderComparison()` en `app.js`) permitía seleccionar hasta 2 oportunidades de la lista y visualizaba una tabla atributiva simple con los campos: `title`, `company`, `location`, `remote`, `modality`, `salary`, `workday` y `source`.
No contrastaba competencias técnicas, no analizaba niveles de exigencia (requisito vs. deseable), ni permitía detectar brechas tecnológicas entre puestos.

### 2.2. Componentes Reutilizados y Extendidos
- **Reutilización:** Estructura de diálogo modal nativo HTML5 (`<dialog id="compare-dialog">`), vector reactivo de selección `compareIds`, disparadores en tarjetas de catálogo y controles de eliminación y limpieza.
- **Extensión:** Incorporación del campo de régimen laboral contractual (`regime`, proveniente de `TASK-R7-01`) en la tabla base, y adición previa de una matriz visual de contraste técnico de 3 columnas (`renderSkillsComparison`) con desglose de competencias coincidentes y exclusivas, niveles de obligatoriedad y panel de advertencias de datos no especificados.

---

## 3. Taxonomía de Competencias y Normalización Determinista

Se implementó un diccionario taxonómico canónico estandarizado que agrupa más de 80 tecnologías clave en las áreas de Ingeniería de Sistemas, Software, Datos, Cloud, DevOps, Seguridad y Redes.

### 3.1. Reglas de Normalización y Protección contra Falsos Positivos
1. **Normalización de Texto:** Remoción determinista de diacríticos y acentos (`normalizeText`), conversión a minúsculas y eliminación de signos de puntuación periféricos sin alterar conectores canónicos (`c++`, `c#`, `.net`).
2. **Protección de Lenguajes Monosilábicos o Ambiguos:**
   - **Lenguaje C:** Regla de exclusión estricta (`\blenguaje c\b`, `\bprogramación en c\b`, `\bc/c++\b`) para evitar que letras aisladas o palabras como "Conocimientos" o "Comunicación" disparen un falso positivo.
   - **C++:** Expresión regular de borde no-palabra (`\bc\+\+(?!\w)`) garantizando su captura precisa sin romper el análisis sintáctico de tokens contiguos.
   - **SQL vs. Variantes Propietarias:** Inclusión de *negative lookbehinds* (`(?<!transact-)(?<!t-)`) y *negative lookaheads* (`(?!\s*(?:server|lite))`) para que menciones a `SQL Server`, `SQLite` o `Transact-SQL` se clasifiquen en sus categorías precisas sin contaminar la competencia genérica de lenguaje SQL.
   - **Redes de Telecomunicaciones vs. Redes Sociales:** Inclusión de *negative lookahead* (`\bredes(?!\s*sociales)`) para prevenir que requisitos de "redes sociales" en puestos multidisciplinarios sean catalogados erróneamente como redes de computadoras (Cisco, TCP/IP).

---

## 4. Criterios de Clasificación de Requisitos

Cada competencia extraída se clasifica bajo cuatro niveles deterministas de prioridad:

| Nivel de Prioridad | Denominación en UI | Definición Operativa | Criterio de Activación |
|---|---|---|---|
| `REQUIRED` | Obligatorio | Requisito indispensable / excluyente para postular. | Extraído de `requirements` o contexto con patrones como *indispensable*, *obligatorio*, *excluyente*, *mínimo*, *experiencia en*, *dominio*. |
| `PREFERRED` | Deseable | Requisito valorado positivamente pero no excluyente. | Patrones como *deseable*, *preferible*, *valorado*, *plus*, *conocimientos básicos*, *interés en*. |
| `MENTIONED` | Mención | Habilidad listada en etiquetas (`skills`) o cuerpo de tareas sin calificador de prioridad. | Presente en el array estructurado `skills` del registro o mencionado en descripción de responsabilidades. |
| `UNSPECIFIED` | No especificado | Ausencia de requisitos técnicos o procedencia formativa explícita en la vacante. | El registro no declara array de `skills` o sus listas de requisitos carecen de especificación técnica. |

### Jerarquía de Prevalencia
Cuando una tecnología aparece simultáneamente en un array de etiquetas genéricas `skills` (por defecto `MENTIONED`) y en el campo detallado `requirements` con un calificador específico (ej. *"Deseable Docker"*), la regla textual de `requirements` prevalece para evitar sobreestimar la exigencia real del empleador.

---

## 5. Manejo Explícito de Incertidumbre y Ausencia de Información

En conformidad con el principio de **Verificabilidad Fail-Closed**:
- Si una oportunidad tiene vacíos sus campos de competencias (`skills` vacío o ausente, y `requirements` sin tecnologías detectables), el comparador **no asume** requisitos de la industria.
- La interfaz despliega un bloque de alerta informativa destacada:
  > *"Requisitos técnicos no declarados: La oportunidad [Título] no lista competencias técnicas estructuradas en sus bases o publicación oficial. Verifique directamente las bases oficiales de la convocatoria."*
- Si ninguna de las dos oportunidades tiene competencias extraíbles, se notifica claramente al usuario que la comparación de habilidades no puede realizarse de forma automatizada y se proveen los enlaces directos a las convocatorias originales.

---

## 6. Arquitectura del Motor de Comparación

### 6.1. Módulo Python (`collector/skills.py`)
- Diseñado para reutilización en auditorías, scripts de validación, pipelines de normalización y testing automatizado.
- Expone:
  - `extract_skills_from_opportunity(job_dict) -> Dict[str, ExtractedSkill]`
  - `compare_opportunity_skills(jobA_dict, jobB_dict) -> SkillComparisonResult`
- Provee trazabilidad completa a través de la tupla nombrada `ExtractedSkill(name, category, priority, source_field, excerpt)`.

### 6.2. Motor Frontend Vanilla (`app.js`)
- Implementación espejo con idéntica lógica algorítmica para ejecución instantánea del lado del cliente.
- Función `renderSkillsComparison(jobA, jobB)`: Genera una matriz visual de tres columnas:
  1. **Competencias Coincidentes:** Ambas oportunidades las solicitan (resaltando si en una es obligatoria y en otra deseable).
  2. **Exclusivas de Oportunidad A:** Demandadas únicamente por el primer empleo.
  3. **Exclusivas de Oportunidad B:** Demandadas únicamente por el segundo empleo.
- Badges semánticos con código de color accesible y tooltips descriptivos con el fragmento original de texto que sustenta la clasificación.

---

## 7. Evidencias Verificables de Pruebas

### 7.1. Suite Unitaria Python (`tests/test_skills.py`)
Se desarrollaron 13 pruebas unitarias exhaustivas cubriendo:
- Normalización canónica de variantes y alias (Postgres -> PostgreSQL, AWS -> Amazon Web Services).
- Protección de falsos positivos en Lenguaje C, SQL Server, Transact-SQL y Redes Sociales.
- Jerarquía de prioridad (`REQUIRED` vs. `PREFERRED` vs. `MENTIONED`).
- Extracción desde múltiples campos (`skills`, `requirements`, `tasks`, `title`).
- Clasificación de competencias coincidentes y exclusivas.
- Detección y reporte de oportunidades con información no especificada.
- Divergencia de prioridades en competencias compartidas.

```text
Ran 13 tests in 0.010s
OK (13/13 passing, 0 errors, 0 failures)
```

### 7.2. Suite Frontend (`tests/catalog_ui.test.cjs`)
Se añadieron validaciones en el entorno VM para certificar:
- Extracción idéntica de competencias en JavaScript.
- Identificación de coincidentes y exclusivas en el comparador.
- Renderizado de badges y avisos de requisitos no especificados en `renderSkillsComparison()`.
- Incorporación del régimen laboral en las filas de comparación atributiva.

```text
node tests/catalog_ui.test.cjs
OK: public catalog filtering scenarios passed.
OK: root/Pages paths and failed-catalog degradation scenarios passed.
Exit code: 0
```

### 7.3. Suite Global de Regresión
Se ejecutó la suite completa del repositorio:
```powershell
python -m unittest discover -s tests
Ran 313 tests in 10.133s
OK (313 passing, 0 regressions)
```

---

## 8. Integridad de Catálogos Canónicos

Se verificó el estado de los archivos canónicos de datos antes y después de la implementación:
- `data/opportunities.seed.json`: `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917` (112 registros, INTACTO)
- `data/opportunities.json`: `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02` (112 registros, INTACTO)
- `git diff --exit-code data/` ejecutado satisfactoriamente (0 diferencias).

---

## 9. Cumplimiento de Criterios de Aceptación

| Criterio de Aceptación | Estado | Evidencia |
|---|---|---|
| Contrastar dos oportunidades lado a lado | `CUMPLIDO` | Modal `#compare-dialog` con matriz de competencias de 3 columnas + tabla atributiva enriquecida. |
| Distinguir competencias compartidas y exclusivas | `CUMPLIDO` | Segmentación determinista en `Coincidentes`, `Exclusivas Oportunidad A` y `Exclusivas Oportunidad B`. |
| Diferenciación de prioridad (`REQUIRED`, `PREFERRED`, etc.) | `CUMPLIDO` | Clasificación léxica de contexto con badges UI diferenciados (`Obligatorio`, `Deseable`, `Mención`). |
| Manejo explícito de información no especificada | `CUMPLIDO` | Alerta contextual fail-closed cuando una vacante no declara requisitos estructurados. |
| Normalización determinista de sinónimos y alias | `CUMPLIDO` | Diccionario taxonómico en `collector/skills.py` y `app.js` con filtros para falsos positivos. |
| Trazabilidad documental de origen | `CUMPLIDO` | Tooltips interactivos y metadatos indicando campo de origen y extracto textual. |
| Zero New Dependencies y preservación canónica | `CUMPLIDO` | 100% standard library / vanilla JS, 0 dependencias añadidas, catálogos intactos. |

---

## 10. Dictamen y Conclusión

La tarea **`TASK-R7-02`** queda certificada con dictamen **`COMPLETED`**. Con esta implementación culmina formalmente la **Fase R7 (Valor Profesional y UX)** de Velora, habiendo dotado a la plataforma de:
1. Taxonomía jurídica de regímenes laborales peruanos (`TASK-R7-01`).
2. Comparador de requisitos técnicos y competencias para análisis objetivo de brechas profesionales (`TASK-R7-02`).
