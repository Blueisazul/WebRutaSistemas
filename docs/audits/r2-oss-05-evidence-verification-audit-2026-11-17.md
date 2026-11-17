# Informe de Auditoría Técnica R2-OSS-05: Verificación de Procedencia, Vigencia y Frescura de Evidencias

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2-OSS-05 — Verificación de procedencia, vigencia y frescura de evidencias  
**Estado:** COMPLETADA Y VERIFICADA  
**Modo de ejecución:** Agente autónomo / Ingeniero de Integridad de Datos  
**Clasificación técnica:** `[DESARROLLO_PROPIO - Justificado]` `[INTEGRACIÓN_OSS]`  

---

## 1. Resumen Ejecutivo

En el marco de la arquitectura editorial Schema 2 de Ruta Sistemas, donde ninguna oportunidad puede publicarse sin evidencia trazable, se implementó el módulo canónico `collector/evidence.py` y su integración en `scripts/validate_candidates.py`.

El módulo opera bajo una política de **cero dependencias externas** y **ejecución 100% offline y determinista**, empleando exclusivamente la biblioteca estándar de Python (`datetime`, `urllib.parse`, `dataclasses`, `re`).

### Logros Principales:
1. **Verificación de Procedencia y Estructura URL:** Validación estricta de esquemas HTTPS, rechazo de credenciales embebidas (RFC 3986), restricción de puertos a 443 o implícito, y contraste con listas blancas de hosts autorizados (`allowedHosts`, `allowedPostingHosts`) por fuente.
2. **Evaluación de Frescura Editorial (TTL):** Implementación de la política ADR-001 (TTL de 7 días naturales calculados sobre el huso horario civil de Lima `America/Lima` `UTC-05:00`). Clasificación exacta en `FRESH`, `STALE`, `FUTURE`, `INVALID` y `UNKNOWN`.
3. **Evaluación de Vigencia de la Oportunidad:** Análisis de `proposed.deadline` contra la fecha de corte civil (`as_of`), determinando estados `DEADLINE_FUTURE`, `DEADLINE_REACHED`, `DEADLINE_EXPIRED`, `DEADLINE_UNKNOWN` y `DEADLINE_INVALID`.
4. **Separación Taxativa de Dimensiones:** Aislamiento formal entre la frescura de la evidencia y la vigencia de la vacante. Una evidencia reciente no revalida una oportunidad expirada, y una fecha límite lejana no excusa evidencia caduca.
5. **Integración Retrocompatible:** Incorporación de las banderas `--verify-evidence` y `--json-report` en `scripts/validate_candidates.py` sin alterar el comportamiento base de validación ni los hashes de catálogo.
6. **Batería de Pruebas Rigurosa:** Creación de 30 escenarios sintéticos en `tests/fixtures/evidence/evidence_cases.json` y 43 pruebas unitarias en `tests/test_evidence.py`, elevando la suite Python a 159 pruebas con 0 fallos.

---

## 2. Decisiones Técnicas y Justificación

### D1: Cero solicitudes de red y validación puramente estructural
- **Decisión:** La procedencia se valida sintácticamente contra las políticas de fuentes registradas en `collector/sources.json`. No se realizan comprobaciones HTTP/HEAD ni resoluciones DNS.
- **Justificación:** Previene fugas de información, ataques SSRF, dependencia de conectividad, bloqueos por rate limiting y no determinismo en pipelines de CI/CD. El campo `remoteAvailability` se fija explícitamente como `REMOTE_AVAILABILITY_NOT_CHECKED`.

### D2: Huso horario de referencia `America/Lima` (UTC-05:00)
- **Decisión:** Todo cálculo de edad en días y comparación con fechas de vencimiento se normaliza al huso horario oficial de Perú (`America/Lima`), convirtiendo marcas ISO 8601 con zona horaria a fechas civiles locales antes de la sustracción.
- **Justificación:** Cumplimiento con ADR-001. Evita desfasajes de ±1 día originados por la conversión ingenua de marcas de tiempo nocturnas (ej. 23:30 Lima = 04:30 UTC del día siguiente).

### D3: Inmutabilidad de candidatos y política "Fail-Closed"
- **Decisión:** La función `verify_candidate_evidence` trata el diccionario del candidato como de solo lectura. Ante cualquier ambigüedad, falta de datos requeridos o error de análisis, el estado resultante es de rechazo (`STRUCTURAL_INVALID`, `ALL_STALE` o `DEADLINE_INVALID`).
- **Justificación:** Garantiza la pureza editorial y evita corrupciones silenciosas del staging de candidatos.

---

## 3. Matriz de Cobertura de Escenarios (30 Casos)

| # | Dimensión | Escenario | Entrada clave | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|
| 01 | Procedencia | HTTPS institucional en lista blanca | `https://jobs.bcp.com.pe/opp-01` | `STRUCTURAL_VALID`, `PROVENANCE_VALID` | Conforme |
| 02 | Procedencia | URL HTTP no segura | `http://jobs.bcp.com.pe/opp-02` | `STRUCTURAL_INVALID`, `PROVENANCE_INVALID` | Conforme |
| 03 | Procedencia | URL sin host o malformada | `https:///no-host` | `STRUCTURAL_INVALID`, `PROVENANCE_INVALID` | Conforme |
| 04 | Procedencia | Credenciales embebidas | `https://admin:pass123@host/opp-04` | `STRUCTURAL_INVALID`, `PROVENANCE_INVALID` | Conforme |
| 05 | Procedencia | Puerto no estándar (8080) | `https://jobs.bcp.com.pe:8080/opp-05` | `STRUCTURAL_INVALID`, `PROVENANCE_INVALID` | Conforme |
| 06 | Procedencia | Host no listado en la fuente | `https://unauthorized-domain.com/` | `STRUCTURAL_INVALID`, `PROVENANCE_INVALID` | Conforme |
| 07 | Procedencia | URL de evidencia ausente/null | `url: null` | `STRUCTURAL_INVALID`, error URL | Conforme |
| 08 | Procedencia | Evidencia con host inconsistente con `sourceUrl` | `sourceUrl`: empresa.com, ev: otro.org | `STRUCTURAL_INVALID`, advertencia/error | Conforme |
| 09 | Procedencia | Evidencia huérfana (campo no en proposed) | `salary` evidenciado pero null en proposed | `STRUCTURAL_VALID`, advertencia huérfana | Conforme |
| 10 | Procedencia | Campo propuesto no nulo sin evidencia | `employer` presente sin fieldEvidence | `STRUCTURAL_INVALID`, error falta evidencia | Conforme |
| 11 | Frescura | Observada hoy (edad = 0 días) | `2026-11-17T09:00:00-05:00` | `FRESH`, `age_days: 0`, `ALL_FRESH` | Conforme |
| 12 | Frescura | Observada dentro de TTL (3 días) | `2026-11-14T10:00:00-05:00` | `FRESH`, `age_days: 3`, `ALL_FRESH` | Conforme |
| 13 | Frescura | Límite exacto de TTL (7 días) | `2026-11-10T00:00:00-05:00` | `FRESH`, `age_days: 7`, `ALL_FRESH` | Conforme |
| 14 | Frescura | Fuera de TTL por 1 día (8 días) | `2026-11-09T23:59:00-05:00` | `STALE`, `age_days: 8`, `ALL_STALE` | Conforme |
| 15 | Frescura | Profundamente vencida (60 días) | `2026-09-18T10:00:00-05:00` | `STALE`, `age_days: 60`, `ALL_STALE` | Conforme |
| 16 | Frescura | observedAt ausente o nulo | `observedAt: null` | `STRUCTURAL_INVALID`, `ALL_STALE` | Conforme |
| 17 | Frescura | observedAt malformado (no ISO) | `17-11-2026 10:00 AM` | `STRUCTURAL_INVALID`, `INVALID_TEMPORALITY`| Conforme |
| 18 | Frescura | observedAt en el futuro | `2026-11-18T10:00:00-05:00` | `STRUCTURAL_INVALID`, `INVALID_TEMPORALITY`| Conforme |
| 19 | Vigencia | Deadline en el futuro | `deadline: "2026-11-30"` | `DEADLINE_FUTURE` | Conforme |
| 20 | Vigencia | Deadline alcanzada hoy | `deadline: "2026-11-17"` | `DEADLINE_REACHED` | Conforme |
| 21 | Vigencia | Deadline vencida en el pasado | `deadline: "2026-11-10"` | `DEADLINE_EXPIRED`, advertencia | Conforme |
| 22 | Vigencia | Deadline ausente o null | `deadline: null` | `DEADLINE_UNKNOWN` | Conforme |
| 23 | Vigencia | Formato de deadline inválido | `deadline: "30-11-2026"` | `DEADLINE_INVALID`, `STRUCTURAL_INVALID` | Conforme |
| 24 | Vigencia | Control huso horario nocturno | `observedAt: 23:30 -05:00` | `ALL_FRESH`, `age_days: 0`, sin desfase | Conforme |
| 25 | Vigencia | Evidencia fresca + deadline vencida | `ev: FRESH`, `deadline: 2026-11-10` | `ALL_FRESH` + `DEADLINE_EXPIRED` | Conforme |
| 26 | Vigencia | Deadline futura + evidencia vencida | `ev: STALE`, `deadline: 2026-12-31` | `ALL_STALE` + `DEADLINE_FUTURE` | Conforme |
| 27 | Integridad | proposed vacío sin campos | `proposed: {}`, `fieldEvidence: []` | `STRUCTURAL_VALID`, `NO_EVIDENCE` | Conforme |
| 28 | Integridad | Múltiples evidencias por campo | 2 evidencias para `title` | `STRUCTURAL_VALID`, advertencia múltiplo | Conforme |
| 29 | Integridad | Campos opcionales null sin evidencia | `salary: null`, `benefits: null` | `STRUCTURAL_VALID`, sin error | Conforme |
| 30 | Integridad | Estructura JSON malformada | `proposed: "string"`, `ev: "string"` | `STRUCTURAL_INVALID`, error controlado | Conforme |

---

## 4. Resultados de Validación y Verificación

1. **Pruebas Unitarias Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **159 pruebas aprobadas, 0 fallos, 0 errores** (tiempo: 3.25s).
   - Componentes cubiertos: `test_evidence.py` (43), `test_dedup.py` (22), `test_jsonld_extractor.py` (19), `test_ats_connectors.py` (18), `test_catalog_quality.py` (57).
2. **Generación e Integridad de Catálogo:**
   - Comando: `python scripts/build_catalog.py --check`
   - Resultado: `Catálogo válido: 5 registros; snapshot coincide con la fuente canónica.`
   - Comando: `python scripts/validate_catalog.py`
   - Resultado: Catálogo canónico y snapshot validados exitosamente.
3. **Validador de Candidatos y CLI:**
   - Comando: `python scripts/validate_candidates.py data/candidates/inbox.example.json --verify-evidence`
   - Resultado: Ejecución exitosa, reporte de evidencias emitido, 0 modificaciones a datos.
4. **Pruebas de Integración E2E (Playwright):**
   - Comando: `npx playwright test`
   - Resultado: **8 pruebas pasadas (Chromium y Mobile WebKit)**.
5. **Verificación de Inmutabilidad de Fuentes Canónicas:**
   - `data/opportunities.seed.json`: `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` (Inalterado)
   - `data/opportunities.json`: `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` (Inalterado)
6. **Higiene de Formato de Código:**
   - Comando: `git diff --check`
   - Resultado: Limpio (cero espacios en blanco sobrantes).

---

## 5. Seguridad de la Cadena de Suministro

- **Dependencias agregadas:** 0.
- **Riesgo CVE introducido:** 0.
- **Licenciamiento:** Exclusivamente código propio bajo la licencia MIT del repositorio y biblioteca estándar de Python.
- **Protección contra inyección:** Expresiones regulares acotadas y análisis seguro vía `urllib.parse` con validación estricta de esquemas, puertos y credenciales.

---

## 6. Siguiente Paso Técnico Justificado: R2-OSS-06

Con los bloques R2-OSS-01 (Auditoría OSS), R2-OSS-02 (Conectores ATS), R2-OSS-03 (Extractor HTML/JSON-LD), R2-OSS-04 (Deduplicador Determinista) y R2-OSS-05 (Verificación de Evidencias) concluidos e integrados, el siguiente paso técnico natural y obligatorio es:

### `R2-OSS-06` — CLI unificado de gestión de bandeja editorial y observabilidad local
- **Objetivo:** Construir una interfaz unificada en línea de comandos (`scripts/editorial_cli.py` o módulo equivalente) que integre secuencialmente extracción, normalización, deduplicación y verificación de evidencias, permitiendo a los revisores humanos inspeccionar el staging editorial, auditar alertas y preparar promociones al catálogo sin tocar la semilla canónica manualmente.
