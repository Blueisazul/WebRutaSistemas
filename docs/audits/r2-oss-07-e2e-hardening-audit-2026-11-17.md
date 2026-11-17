# Informe de Auditoría Técnica R2-OSS-07: Integración End-to-End, Endurecimiento y Verificación del Pipeline Editorial OSS

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2-OSS-07 — Integración End-to-End, Endurecimiento y Verificación del Pipeline Editorial OSS  
**Estado:** COMPLETADA Y VERIFICADA  
**Modo de ejecución:** Agente autónomo / Principal Software Architect & Security Lead  
**Clasificación técnica:** `[DESARROLLO_PROPIO - Justificado]` `[INTEGRACIÓN_OSS]`  

---

## A. Trazabilidad y Resolución de Discrepancias

### 1. Estado Git y Rama
- **Rama:** `integration/r1-02c`
- **HEAD commit:** `54897155a5069207ce7b798f6f96d00600209225` ("Document Pages deployment blocker").
- **Historial de commits reciente:**
  - `5489715`: Document Pages deployment blocker
  - `68d4c52`: Record R1-04 Pages deployment failure
  - `9bb6b39`: Normalize validation report formatting
  - `08683b8`: Document R1-03 validation evidence
  - `2163e88`: Document completed local integration

### 2. Resolución de la Discrepancia Obligatoria de HEAD
- **Pregunta:** ¿Por qué los informes de R2-OSS-02, R2-OSS-03, R2-OSS-04, R2-OSS-05 y R2-OSS-06 declaran exactamente el mismo HEAD `54897155a5069207ce7b798f6f96d00600209225` a pesar de describir implementaciones sucesivas?
- **Evidencia y Dictamen Técnico:**
  `[HECHO]` La rama de trabajo `integration/r1-02c` se fijó en el commit `5489715`.
  `[HECHO]` Todo el trabajo de la línea técnica R2-OSS (R2-OSS-01 a R2-OSS-06) se ejecutó de manera acumulativa y secuencial en el **árbol de trabajo local (working tree)** sin crear nuevos commits de Git, en cumplimiento estricto con las directrices operativas del proyecto que prohíben operaciones no autorizadas de `git commit`, `push` o `merge`.
  `[HECHO]` Los informes de auditoría previos no describían commits separados en el historial, sino el avance progresivo de archivos modificados y sin seguimiento (`untracked`) verificados sobre la base de dicho commit base.
  `[HECHO]` Todos los archivos declarados por los informes existen físicamente en el repositorio y sus pruebas pasan limpiamente.

---

## B. Matriz de Implementación y Estado Real Comprobado

| Bloque | Estado Documental | Estado Comprobado en Código | Pruebas Verificadas | Evidencia de Código |
|---|---|---|---|---|
| **R2-OSS-01** (Auditoría OSS) | Completada | Documentada | N/A | `docs/audits/r2-oss-01-audit-2026-11-17.md` |
| **R2-OSS-02** (Conectores ATS) | Completada | Operativo en código | 18 pruebas unitarias | `collector/ats_connectors.py`, `tests/test_ats_connectors.py` |
| **R2-OSS-03** (Extractor HTML/JSON-LD) | Completada | Operativo en código | 19 pruebas unitarias | `collector/jsonld_extractor.py`, `tests/test_jsonld_extractor.py` |
| **R2-OSS-04** (Deduplicador Canónico) | Completada | Operativo en código | 22 pruebas unitarias | `collector/dedup.py`, `tests/test_dedup.py` |
| **R2-OSS-05** (Verificación Evidencias) | Completada | Operativo en código | 43 pruebas unitarias | `collector/evidence.py`, `tests/test_evidence.py` |
| **R2-OSS-06** (CLI Editorial) | Completada | Operativo en código | 30 pruebas unitarias | `scripts/editorial_cli.py`, `tests/test_editorial_cli.py` |
| **R2-OSS-07** (Endurecimiento y E2E) | Completada | Operativo y endurecido | 4 pruebas E2E pipeline | `scripts/editorial_cli.py`, `tests/test_editorial_pipeline_e2e.py` |

---

## C. Auditoría de Seguridad y Endurecimiento

Durante la auditoría técnica de R2-OSS-07 se identificaron y corrigieron los siguientes aspectos críticos de seguridad e integridad:

### 1. Riesgos Identificados y Mitigados
- **R1: Protección insuficiente de archivos canónicos frente a variaciones de casing en Windows.**
  - *Vulnerabilidad previa:* La comprobación de rutas usaba pertenencia exacta sobre `Path.resolve()`. En Windows, si el archivo objetivo no existe aún o se escribe con diferente mayúscula/minúscula (ej. `data/Opportunities.Seed.json`), la comparación podía no coincidir.
  - *Corrección aplicada:* Normalización mediante `str(target.resolve()).casefold()` contrastada contra un conjunto blindado de rutas protegidas (`PROTECTED_PATHS`).
- **R2: Omisión del registro de fuentes en la lista de exclusión de escritura.**
  - *Vulnerabilidad previa:* `_assert_not_canonical` protegía `opportunities.seed.json` y `opportunities.json`, pero no `collector/sources.json`.
  - *Corrección aplicada:* Se añadió `collector/sources.json` a `PROTECTED_PATHS`, garantizando que ninguna orden de importación, reporte o preparación pueda sobreescribir la configuración de fuentes.
- **R3: Inyección de escritura en el directorio de control de versiones.**
  - *Vulnerabilidad previa:* Un parámetro `--output` malicioso con path traversal hacia `.git/hooks` o `.git/config` no estaba bloqueado explícitamente.
  - *Corrección aplicada:* Detección y bloqueo terminante de cualquier escritura dentro del prefijo canónico `.git`.
- **R4: Colisión destructiva entre archivos de entrada y salida.**
  - *Vulnerabilidad previa:* Comandos como `import` no impedían que el archivo `--output` fuera exactamente el mismo archivo de entrada `--input`.
  - *Corrección aplicada:* Validación de identidad de ruta `output_path.resolve() == input_path.resolve()`, abortando con código de error operativo antes de abrir el descriptor de escritura.
- **R5: Corrupción de archivos por escrituras parciales.**
  - *Vulnerabilidad previa:* El uso de `write_text` directo sobre el archivo destino podía dejar archivos truncados o corruptos ante interrupciones bruscas o fallos de disco.
  - *Corrección aplicada:* Implementación de `_atomic_write_json`, que escribe primero en un archivo temporal oculto `.tmp_{name}_{pid}` en el mismo directorio y realiza un reemplazo atómico mediante `os.replace`. En caso de excepción, el temporal se elimina de inmediato.

---

## D. Integración End-to-End Demostrada

En `tests/test_editorial_pipeline_e2e.py`, se ejecutó y validó el flujo completo en un entorno temporal aislado (`tempfile.TemporaryDirectory`):

1. **Importación Greenhouse:** Fixture `tests/fixtures/ats/greenhouse_complete.json` normalizado a 2 candidatos Schema 2.
2. **Importación Lever:** Fixture `tests/fixtures/ats/lever_complete.json` normalizado a candidatos Schema 2.
3. **Importación HTML/JSON-LD:** Fixture `tests/fixtures/html/jobposting_complete.html` normalizado a Schema 2 con evidencias biunívocas.
4. **Fusión en Staging:** Creación de un inbox temporal consolidado conteniendo los registros normalizados.
5. **Validación Editorial:** `validate-inbox` ejecutado con `--as-of 2026-11-17` y `--verify-evidence`, validando estructura, tipos y TTL.
6. **Deduplicación Canónica:** `deduplicate` ejecutado contra la semilla canónica con `--fail-on-collision`, comprobando ausencia de colisiones.
7. **Inspección de Métricas:** `inspect` extrayendo conteos por fuente, modalidad y estados editoriales.
8. **Informe Consolidado:** `report` guardado en archivo independiente, generando resumen de validación, dedup y acciones humanas.
9. **Preparación de Revisión:** `prepare-review` exportando candidatos para revisión humana con la nota de no publicación.
10. **Aislamiento de Red:** Ejecución bajo `patch("socket.socket", side_effect=RuntimeError)`, certificando cero conexiones de red.
11. **Determinismo:** Dos ejecuciones consecutivas con la misma fecha civil de corte produjeron salidas JSON idénticas.

---

## E. Resultados de Validación y Pruebas

1. **Suite Completa de Pruebas Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **193 pruebas aprobadas (0 fallos, 0 errores)** en 4.35s.
   - Desglose:
     - `tests/test_editorial_pipeline_e2e.py`: 4 pruebas (E2E integral, traversal, colisiones, atomic write).
     - `tests/test_editorial_cli.py`: 30 pruebas unitarias y de comandos.
     - `tests/test_evidence.py`: 43 pruebas unitarias de evidencias y temporalidad.
     - `tests/test_dedup.py`: 22 pruebas unitarias de deduplicación.
     - `tests/test_jsonld_extractor.py`: 19 pruebas unitarias de extracción HTML/JSON-LD.
     - `tests/test_ats_connectors.py`: 18 pruebas unitarias de conectores ATS.
     - `tests/test_catalog_quality.py`: 57 pruebas unitarias de validación de calidad.
2. **Generador y Validador de Catálogo:**
   - `python scripts/build_catalog.py --check`: Catálogo válido, 5 registros; snapshot coincide exactamente con la semilla.
   - `python scripts/validate_catalog.py`: Válido sin errores.
3. **Validador de Candidatos:**
   - `python scripts/validate_candidates.py data/candidates/inbox.example.json --verify-evidence`: Válido (0 candidatos, 0 modificaciones).
4. **Pruebas E2E de Navegador (Playwright):**
   - `npx playwright test`: **8 pruebas aprobadas (Chromium y Mobile WebKit)**.
5. **Higiene de Formato de Código:**
   - `git diff --check`: Limpio (sin errores de espacios en blanco).

---

## F. Integridad de Archivos Canónicos y Fuentes

### Hashes Criptográficos SHA-256 (Antes y Después de la Ejecución):
- `data/opportunities.seed.json`:
  `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` (**Inalterado**)
- `data/opportunities.json`:
  `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` (**Inalterado**)
- `collector/sources.json`:
  `AE5BA4D314A450DB9118C3AD3A98A6FBE261542A74BD0EC7A623AA7F66B0A124` (**Inalterado**)

### Estado de Fuentes:
`[HECHO]` Todas las fuentes en `collector/sources.json` permanecen con `enabled: false`, presupuestos de solicitudes nulos o restringidos a 1/0, y estado `decision: pending_review`. Cero fuentes fueron activadas y cero solicitudes HTTP/DNS fueron ejecutadas.

---

## G. Actualización del Roadmap Maestro

### Línea A — Producto y Datos Reales
- **Estado:** **BLOQUEADA.**
- **Motivo:** No existe autorización documental externa para capturar, almacenar y republicar datos de una fuente real. El producto no cuenta todavía con una vacante real verificada en producción.

### Línea B — Ingeniería OSS Offline
- **Estado:** **COMPLETADA Y VERIFICADA AL 100%.**
- Los 7 bloques técnicos planificados (R2-OSS-01 a R2-OSS-07) han sido completamente implementados, probados, endurecidos y verificados con 193 pruebas automatizadas.
- Se cuenta con conectores ATS, extractor HTML/JSON-LD, deduplicador canónico, verificador de evidencias y temporalidad, y CLI unificada con escrituras atómicas y protecciones de seguridad.

---

## H. Clasificación de Conclusiones

- `[HECHO]` La totalidad de los componentes de R2-OSS-01 a R2-OSS-06 existen en el working tree y funcionan de forma armónica e integrada.
- `[HECHO]` La discrepancia del commit HEAD responde a la restricción deliberada de no realizar commits de Git sin instrucción explícita.
- `[HECHO]` Se fortaleció la seguridad de `scripts/editorial_cli.py` frente a path traversal, colisiones de archivos y fallos de escritura parcial mediante atomic writes.
- `[HECHO]` La prueba E2E demostró que el pipeline completo opera 100% offline, de forma determinista y sin tocar datos canónicos.
- `[INFERENCIA]` La plataforma dispone de la madurez técnica requerida para procesar oportunidades en cuanto se reciba autorización de fuentes, sin necesidad de desarrollo adicional de infraestructura offline.
- `[BLOQUEO]` La fase R2 a nivel de producto continúa pendiente hasta la obtención de autorización documental de una primera fuente viable.
- `[PROPUESTA]` Proceder con el canal de contacto formal hacia las entidades prioritarias ([docs/sources/seguimiento-autorizacion-fuentes.md](docs/sources/seguimiento-autorizacion-fuentes.md)) para autorizar la ingesta de la primera oportunidad real.
