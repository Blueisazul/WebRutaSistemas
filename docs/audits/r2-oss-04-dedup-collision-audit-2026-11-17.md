# R2-OSS-04 — Informe de Implementación: Deduplicador Determinista Canónico y Detección de Colisiones
**Proyecto:** Ruta Sistemas  
**Fecha de ejecución:** 2026-11-17  
**Rama:** `integration/r1-02c`  
**Commit base:** `54897155a5069207ce7b798f6f96d00600209225`  
**Roles del auditor e ingeniero:** Principal Software Architect, Senior Python Engineer, Data Pipeline Engineer, OSS Integration Specialist, Data Quality Engineer, Software Quality Engineer, Technical Auditor, Engineering Lead.

---

## 1. Resumen Ejecutivo

- **[HECHO] Implementación completa del deduplicador canónico:** Se desarrolló el módulo [collector/dedup.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/dedup.py), un motor determinista, no probabilístico y no destructivo para la detección de duplicados y colisiones de identidad en Ruta Sistemas.
- **[HECHO] Coincidencia en dos niveles explicables:**
  1. *Coincidencia primaria (`EXACT_DUPLICATE` e `IDENTIFIER_COLLISION`):* Clave conceptual `sourceId:externalReference` (con normalización Unicode, casefold y preservación estricta de ceros a la izquierda). Si la clave primaria coincide pero los datos fundamentales (título o empleador) son contradictorios, se clasifica como `IDENTIFIER_COLLISION` para revisión urgente.
  2. *Coincidencia secundaria (`POSSIBLE_DUPLICATE`):* Firma compuesta normalizada (`employer|title|location|mode|opportunityType`) con eliminación de puntuación, descompresión de espacios y plegado de mayúsculas. No convierte campos nulos en cadenas vacías que provoquen falsos positivos.
- **[HECHO] Comparación multi-conjunto en solo lectura:** Permite comparar lotes entrantes (`batch`) contra sí mismos, contra la bandeja de entrada local (`inbox`) y contra la semilla canónica ([data/opportunities.seed.json](file:///c:/Users/sant1/Downloads/EmpleoWeb/data/opportunities.seed.json)) sin consultar el snapshot generado (evitando duplicar el catálogo) y sin escribir en disco.
- **[HECHO] No destructividad garantizada:** No fusiona, no sobrescribe, no borra y no promueve registros automáticamente. Emite un informe estructurado `DeduplicationReport` con ordenación determinista y acciones recomendadas para revisión humana.
- **[HECHO] Cobertura y regresión al 100%:** Se implementaron 22 pruebas dedicadas en [tests/test_dedup.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/test_dedup.py) junto a fixtures sintéticos en `tests/fixtures/dedup/`. La suite completa de Python pasó de 94 a **116 pruebas unitarias aprobadas** (`Ran 116 tests in 3.413s: OK`), y la suite Playwright E2E aprobó **8/8 pruebas**.
- **[HECHO] Integridad y hashes verificados:** Cero peticiones de red realizadas. Semilla canónica (`772F576E...`) y snapshot público (`13F91B90...`) conservaron exactamente sus hashes SHA-256 originales.

---

## 2. Estado Inicial (Fase 0 — Inspección)

- **Rama:** `integration/r1-02c`
- **Commit HEAD:** `54897155a5069207ce7b798f6f96d00600209225`
- **Working Tree:** Modificaciones previas limitadas a documentación, conectores adaptados (`collector/ats_connectors.py`) y micro-extractor (`collector/jsonld_extractor.py`).
- **Estado de bloques R2-OSS previos:**
  - `R2-OSS-01`: Auditoría de reutilización completada (decisión de micro-bibliotecas y descarte de ML/dedupe probabilístico).
  - `R2-OSS-02`: Adaptadores ATS funcionales y probados (18 tests).
  - `R2-OSS-03`: Micro-extractor HTML/JSON-LD funcional y probado (19 tests).
- **Documentos rectores revisados:** [Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md) (Sección 51) y [docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/architecture/r0-decisiones-y-alcance-2026-11-12.md) (Sección 7).

---

## 3. Diseño de Identidad y Reglas de Deduplicación (Fase 1)

### 3.1. Coincidencia primaria: identidad externa
- **Clave conceptual:** `sourceId + ":" + externalReference`.
- **Reglas:**
  - Ambos campos deben ser no vacíos; la ausencia de identificador se trata como ausencia de clave, nunca como coincidencia.
  - Normalización Unicode (NFKC) y `casefold()`.
  - **Preservación estricta de ceros iniciales:** `"00123"` no es equivalente a `"123"`.
  - Independencia de espacios de nombres: el mismo identificador en fuentes distintas (`fuente-a:123` vs `fuente-b:123`) **no** produce coincidencia primaria.

### 3.2. Coincidencia secundaria: identidad probable
- **Firma normalizada:** `employer|title|location|mode|opportunityType`.
- **Reglas:**
  - Limpieza de puntuación repetida (`/`, `-`, `·`, paréntesis) y colapso de espacios.
  - Descomposición y eliminación de diacríticos para títulos (`normalize_text()`), garantizando que "Ingeniería" coincida con "Ingenieria".
  - **Sensibilidad de contexto:** Si dos registros comparten empleador y título, pero difieren en ubicación (ej. Lima vs Arequipa), modalidad (Remoto vs Presencial) o tipo de oportunidad (Práctica preprofesional vs Práctica profesional), **no** coinciden como posibles duplicados (se reconocen como convocatorias legítimamente distintas).
  - Valores nulos se representan explícitamente (`"none"`), evitando que la ausencia de campos coincida erróneamente con valores confirmados.

### 3.3. Clasificación y resolución de conflictos
- **`IDENTIFIER_COLLISION` (Máxima precedencia):** Misma clave primaria (`sourceId:externalReference`) pero títulos o empleadores contradictorios. Alerta crítica que exige revisión humana inmediata.
- **`EXACT_DUPLICATE`:** Misma clave primaria con datos de título y empleador consistentes.
- **`POSSIBLE_DUPLICATE`:** Claves primarias distintas o ausentes, pero firma secundaria coincidente en todos los campos discriminantes.
- **`NO_MATCH`:** Sin coincidencias detectadas.

---

## 4. Implementación Técnica (Fases 2, 3 y 4)

Se implementó [collector/dedup.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/collector/dedup.py) con las siguientes responsabilidades:

1. **Normalización determinista:**
   - `normalize_text(text)`: normalización NFKD, eliminación de acentos, remoción de puntuación y `casefold()`.
   - `normalize_identifier(id)`: normalización NFKC y `casefold()` conservando ceros iniciales intactos.
   - `make_primary_key(source_id, external_ref)`: generación de clave primaria canónica.
   - `make_secondary_signature(employer, title, location, mode, opportunity_type)`: generación de firma secundaria multi-dimensional.
2. **Extracción y comparación:**
   - `extract_fields(record, is_seed)`: adaptador universal para extraer campos normalizados desde fichas de candidatos (`proposed`) o desde la semilla canónica (`opportunities.seed.json`).
   - `compare_records(rec1, rec2, matched_set)`: evaluador pairwise que detecta campos idénticos y discrepantes, aplicando la precedencia entre `IDENTIFIER_COLLISION`, `EXACT_DUPLICATE` y `POSSIBLE_DUPLICATE`.
3. **Orquestación multi-conjunto:**
   - `deduplicate_candidates(candidates, *, inbox_candidates, seed_opportunities)`: analiza el lote entrante contra sí mismo (`batch`), contra la bandeja local (`inbox`) y contra la semilla canónica (`seed`).
   - `DeduplicationReport`: contenedor inmutable con métricas de resumen y lista de colisiones ordenada determinísticamente por `(recordId, matchedSet, matchedId, matchType)`.
4. **Carga en solo lectura:**
   - `load_seed_opportunities()`: carga determinista de la semilla sin tocar el snapshot público.
   - `load_inbox_candidates()`: carga de la bandeja local sin mutaciones.

---

## 5. Fixtures Sintéticos y Pruebas (Fases 5 y 6)

Se creó el archivo de fixtures sintéticos en [tests/fixtures/dedup/dedup_cases.json](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/fixtures/dedup/dedup_cases.json) y la suite [tests/test_dedup.py](file:///c:/Users/sant1/Downloads/EmpleoWeb/tests/test_dedup.py) cubriendo los 20 escenarios requeridos:

| Caso de prueba | Propósito / Escenario | Resultado verificado |
| :--- | :--- | :--- |
| `test_exact_duplicate_same_source_same_ref` | Misma fuente y mismo identificador | Clasificado como `EXACT_DUPLICATE` (`batch`) |
| `test_different_source_same_ref_no_primary_match` | Mismo identificador en fuentes distintas | Clasificado como `NO_MATCH` en clave primaria |
| `test_different_location_no_secondary_match` | Mismo título/empleador, distinta ciudad | No coincide; preserva convocatorias separadas |
| `test_different_mode_no_secondary_match` | Mismo título/empleador, distinta modalidad | No coincide; preserva modalidades separadas |
| `test_different_opportunity_type_no_secondary_match` | Mismo título/empleador, distinto nivel de práctica | No coincide; preserva tipos separados |
| `test_different_title_same_employer_no_match` | Mismo empleador con cargos distintos | No coincide |
| `test_leading_zeros_preservation` | `"00123"` vs `"00123"` y `"00123"` vs `"123"` | `"00123"` coincide exacto; `"123"` no colisiona primario |
| `test_missing_identifiers_do_not_produce_primary_match` | Ausencia de `externalReference` | No genera clave primaria falsa |
| `test_employer_case_and_whitespace_normalization` | `"  EMPRESA FICTICIA  "` vs `"Empresa Ficticia"` | Normaliza y detecta coincidencia |
| `test_title_accents_and_unicode_normalization` | `"Ingeniería"` vs `"Ingenieria"` | Normaliza diacríticos y detecta coincidencia |
| `test_title_punctuation_normalization` | `"TI / Sistemas"` vs `"TI - Sistemas"` | Normaliza separadores y detecta coincidencia |
| `test_null_values_handled_gracefully` | Campos completamente nulos | Manejado sin excepciones ni falsos positivos |
| `test_different_dates_flagged_in_discrepant_fields` | Fechas de publicación distintas | Detectado en `discrepant_fields: ["publishedAt"]` |
| `test_batch_duplicates_detected` | Duplicados dentro del mismo lote | Reportado con `matched_set: "batch"` |
| `test_inter_batch_duplicates_detected` | Duplicados entre lotes distintos | Reportado con `matched_set: "inbox"` |
| `test_inbox_matches_detected` | Coincidencia con candidatos en bandeja | Reportado con `matched_set: "inbox"` |
| `test_seed_matches_detected` | Coincidencia contra `OP-001` de la semilla | Reportado con `matched_set: "seed"` sin tocar datos |
| `test_identifier_collision_contradictory_data` | Mismo ID externo con cargo contradictorio | Clasificado como `IDENTIFIER_COLLISION` con alerta |
| `test_similar_titles_different_fields_no_match` | Sistemas vs Finanzas en el mismo ministerio | No coincide (`NO_MATCH`) |
| `test_empty_input_returns_zero_collisions` | Lote vacío | `total_evaluated: 0, collisions: []` |
| `test_immutability_of_inputs_and_seed` | Entradas y semilla en disco | Objetos y bytes en disco 100% inalterados |
| `test_deterministic_order_of_report` | Ejecuciones repetidas | Salida JSON idéntica y orden estable |

---

## 6. Validación y Resultados de Ejecución

```
Validaciones ejecutadas:
----------------------------------------------------------------------
1. Suite unitaria completa Python:
   python -m unittest discover -s tests -p "test_*.py"
   Ran 116 tests in 3.413s: OK (0 fallos, 0 errores)

2. Chequeo de catálogo demostrativo:
   python scripts/build_catalog.py --check
   Catálogo válido: 5 registros; snapshot coincide con la fuente canónica.

3. Validación de catálogo:
   python scripts/validate_catalog.py
   Válido: 5 fichas; modo=publicación no vacía; fecha Lima=2026-11-17.

4. Validación de bandeja de candidatos de ejemplo:
   python scripts/validate_candidates.py data/candidates/inbox.example.json
   Bandeja local válida: 0 candidatos; no se modificó ni se publicó el catálogo.

5. Suite Playwright E2E:
   npx playwright test
   8 passed (7.7s)

6. Formato de código y diff:
   git diff --check
   (Salida limpia: sin conflictos ni espacios sobrantes)
```

---

## 7. Verificación de Seguridad e Integridad

- **[HECHO] Hashes SHA-256 de archivos canónicos:**
  - `data/opportunities.seed.json`: `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` (Inalterado).
  - `data/opportunities.json`: `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` (Inalterado).
- **[HECHO] Ausencia total de solicitudes de red:** La ejecución fue 100% local y offline.
- **[HECHO] Ausencia de fusiones destructivas o eliminaciones:** El deduplicador es puramente observacional y genera reportes; no borra fichas ni altera `candidateId`.
- **[HECHO] Cero dependencias añadidas:** No se añadieron paquetes a `package.json` ni dependencias externas en Python.

---

## 8. Actualización del Roadmap y Trazabilidad (Fase 14)

Se actualizaron los documentos rectores del proyecto respetando las reglas de trazabilidad y formato:

1. **[Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md):**  
   Se actualizó la **Sección 51** incorporando el estado de R2-OSS-04:
   - `R2-OSS-01 [INTEGRACIÓN_OSS]`: Completada.
   - `R2-OSS-02 [ADAPTACIÓN_OSS] [REFACTOR/FIX]`: Completada.
   - `R2-OSS-03 [DESARROLLO_PROPIO - Justificado] [INTEGRACIÓN_OSS]`: Completada.
   - `R2-OSS-04 [DESARROLLO_PROPIO - Justificado] [REFACTOR/FIX] [INTEGRACIÓN_OSS]`: **Completada y verificada (116 tests unitarios, 8 E2E).**
   - Tareas pendientes: `R2-OSS-05` (verificación de procedencia y vigencia) y `R2-OSS-06` (CLI unificado).
2. **[docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/architecture/r0-decisiones-y-alcance-2026-11-12.md):**  
   Se actualizó la tabla de la Sección 7 reflejando la completitud de R2-OSS-01 a R2-OSS-04 y la vigencia del bloqueo externo sobre fuentes reales.

---

## 9. Estado Final y Criterios de Aceptación

| Criterio | Estado | Evidencia |
| :--- | :--- | :--- |
| Estado real del repositorio inspeccionado | **CUMPLIDO** | Commit 5489715 verificado |
| Implementación de R2-OSS-02 y R2-OSS-03 comprobada | **CUMPLIDO** | Conectores ATS y extractor JSON-LD operativos |
| Reglas de identidad primaria documentadas y probadas | **CUMPLIDO** | `sourceId:externalReference` con ceros iniciales |
| Coincidencia secundaria conservadora y explicable | **CUMPLIDO** | `POSSIBLE_DUPLICATE` sensible a ciudad, modalidad y tipo |
| Colisiones contradictorias identificadas | **CUMPLIDO** | `IDENTIFIER_COLLISION` con alerta explícita |
| Resultado determinista y orden estable | **CUMPLIDO** | Ordenación por clave cuádruple; test de reproducibilidad aprobado |
| Comparación multi-conjunto en modo lectura | **CUMPLIDO** | Comparación contra `batch`, `inbox` y `seed` |
| No utilización del snapshot como duplicado | **CUMPLIDO** | Solo consulta `data/opportunities.seed.json` |
| Sin fusiones ni eliminaciones de registros | **CUMPLIDO** | Objetos de entrada inalterados; salida en reporte separado |
| Sin modificación de Schema 2 | **CUMPLIDO** | Contrato de candidatos Schema 2 respetado |
| Regresiones y conectores intactos | **CUMPLIDO** | 116 tests unitarios y 8 E2E aprobados |
| Cero dependencias añadidas | **CUMPLIDO** | Uso exclusivo de biblioteca estándar de Python |
| Semilla, snapshot e inbox intactos | **CUMPLIDO** | Hashes SHA-256 idénticos antes y después |

---

## 10. Evaluación del Siguiente Bloque: R2-OSS-05

El bloque **R2-OSS-04** se declara formalmente completado y verificado.

**Evaluación técnica para R2-OSS-05 `[DESARROLLO_PROPIO - Justificado]` (Módulo de verificación de procedencia, vigencia y frescura de evidencias):**
1. **Factibilidad:** La base de candidatos Schema 2 normalizada por los conectores ATS (R2-OSS-02) y por el extractor JSON-LD (R2-OSS-03), sumada a la detección de colisiones (R2-OSS-04), proporciona la información estructurada necesaria (`observedAt`, `validThrough`, `fieldEvidence`).
2. **Alcance:** R2-OSS-05 deberá implementar la verificación del Time-To-Live (TTL de 7 días según ADR-001), expiración frente a fechas límite civiles (`deadline`), consistencia horaria en zona `America/Lima` (-05:00) y validación de vigencia de enlaces de evidencia HTTPS sin realizar solicitudes activas de red mientras no existan fuentes autorizadas.
3. **Riesgos y dependencias:** No requiere librerías externas; se puede resolver íntegramente con `datetime` y utilidades del proyecto. No existen bloqueos técnicos internos para comenzar R2-OSS-05.
