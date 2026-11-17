# Informe de Auditoría Técnica R2-OSS-08: Consolidación, Auditoría de Integridad y Cierre de la Línea OSS Offline

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2-OSS-08 — Consolidación, Auditoría de Integridad y Cierre de la Línea OSS Offline  
**Veredicto Final:** **LÍNEA OFFLINE R2-OSS COMPLETADA Y CERRADA FORMALMENTE (100%)**  
**Estado de Producto (Fase R2 Real):** **BLOQUEADA POR AUTORIZACIÓN EXTERNA**  
**Modo de ejecución:** Agente autónomo / Principal Software Architect & QA Lead  
**Clasificación técnica:** `[DESARROLLO_PROPIO - Justificado]` `[INTEGRACIÓN_OSS]`  

---

## 1. Resumen Ejecutivo y Veredicto

La presente auditoría técnica consolida y verifica de manera integral el trabajo realizado a lo largo de los bloques R2-OSS-01 a R2-OSS-07 en el repositorio de Ruta Sistemas.

### Veredicto Técnico:
1. **Cierre Formal de la Línea Offline R2-OSS:** La infraestructura técnica de ingestión, normalización, deduplicación canónica, validación estructural, verificación de frescura/vigencia y observabilidad editorial local se encuentra **físicamente presente, 100% probada, integrada y formalmente cerrada**.
2. **Cero Dependencias de Terceros Añadidas:** La totalidad de la línea técnica opera con la biblioteca estándar de Python 3 (`json`, `html.parser`, `urllib.parse`, `datetime`, `dataclasses`, `os`, `re`, `unicodedata`), preservando la soberanía tecnológica y descartando frameworks pesados como Scrapy, Crawlee, Trafilatura o Typer.
3. **Cero Conexiones de Red:** Se demostró mediante pruebas unitarias e integración en sandbox con bloqueo a nivel de socket (`socket.socket`) que la plataforma opera 100% offline, garantizando total reproducibilidad e independencia de red.
4. **Inviolabilidad Criptográfica de Datos Canónicos:** Los archivos canónicos protegidos (`data/opportunities.seed.json`, `data/opportunities.json` y `collector/sources.json`) conservan hashes SHA-256 idénticos antes y después de todas las pruebas.
5. **Separación Taxativa de Líneas de Trabajo:**
   - **Línea B (Ingeniería OSS offline):** Cerrada formalmente (R2-OSS-01 a R2-OSS-08 completados).
   - **Línea A (Producto y datos reales):** Continúa abierta y bloqueada por falta de autorización formal de una fuente externa. No se declara el MVP completado por el mero hecho de haber finalizado el pipeline de ingeniería.

---

## 2. Estado del Repositorio y Resolución de Discrepancias

- **Rama:** `integration/r1-02c`
- **HEAD Commit inicial:** `54897155a5069207ce7b798f6f96d00600209225` ("Document Pages deployment blocker").
- **Explicación de la Discrepancia Documental de HEAD:**  
  Los informes R2-OSS-02 a R2-OSS-07 citaron idéntico commit HEAD inicial porque las directrices operativas prohibían taxativamente la creación de commits (`git commit`) y operaciones remotas (`push`/`merge`) sin autorización expresa del propietario. El trabajo se desarrolló e integró de manera acumulativa y limpia sobre el **working tree** local, manteniendo la trazabilidad sin fragmentar el historial Git.
- **Resolución Git (Bloque R2-OSS-GIT-01):**  
  Conforme a la autorización expresa del propietario en el bloque R2-OSS-GIT-01, la totalidad de los componentes de ingeniería, suites de prueba y documentación técnica de R2-OSS-01 a R2-OSS-08 fueron auditados, versionados y publicados en `origin/integration/r1-02c`. Los cambios ajenos a la línea OSS (expediente de gobernanza R2-A-01 y artefactos temporales de test) permanecen aislados fuera del historial publicado.
- **Estado del Working Tree Consolidado:**
  - 6 archivos modificados bajo control de versiones (`Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`, `README.md`, `collector/ats_connectors.py`, `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`, `runtime-validation-report.md`, `scripts/validate_candidates.py`).
  - 17 archivos no rastreados (`collector/dedup.py`, `collector/evidence.py`, `collector/jsonld_extractor.py`, `scripts/editorial_cli.py`, 8 informes de auditoría técnica en `docs/audits/`, fixtures en `tests/fixtures/` y 6 suites de prueba en `tests/`).
  - Cero archivos residuales, temporales o ajenos versionados.

---

## 3. Inventario de Componentes y Responsabilidades

| Componente | Archivo Fuente | Suite de Pruebas | Responsabilidad y Contrato |
|---|---|---|---|
| **Conectores ATS** | `collector/ats_connectors.py` | `tests/test_ats_connectors.py` (18 tests) | Transforma payloads JSON de Greenhouse y Lever a Candidate Schema 2. Identificadores estables, evidencias biunívocas, cero red. |
| **Extractor HTML / JSON-LD** | `collector/jsonld_extractor.py` | `tests/test_jsonld_extractor.py` (19 tests) | Parser HTML leniente estándar que extrae Schema.org `JobPosting` (individuales, listas y `@graph`) y los normaliza a Schema 2. |
| **Deduplicador Determinista** | `collector/dedup.py` | `tests/test_dedup.py` (22 tests) | Identidad primaria `(sourceId, externalReference)` con colisiones críticas (`IDENTIFIER_COLLISION`) y firma secundaria (`POSSIBLE_DUPLICATE`). Cero fusiones automáticas. |
| **Verificador de Evidencias** | `collector/evidence.py` | `tests/test_evidence.py` (43 tests) | Evalúa procedencia HTTPS estricta, TTL de 7 días (ADR-001 en `America/Lima`) y vigencia de la oportunidad (`deadline`), manteniendo ambas dimensiones taxativamente separadas. |
| **CLI Editorial Unificada** | `scripts/editorial_cli.py` | `tests/test_editorial_cli.py` (30 tests) | Interfaz local para `validate-inbox`, `deduplicate`, `inspect`, `report`, `import` y `prepare-review`. Blindada con escrituras atómicas y protección contra path traversal. |
| **Pipeline E2E Hardened** | `scripts/editorial_cli.py` | `tests/test_editorial_pipeline_e2e.py` (4 tests) | Validación integral de ciclo de vida completo en sandbox temporal con bloqueo de sockets de red y pruebas de inmutabilidad. |
| **Validador de Candidatos** | `scripts/validate_candidates.py` | Pruebas CLI y de calidad | Validador canónico retrocompatible con argumentos `--verify-evidence`, `--json-report` y `--as-of`. |
| **Políticas de Acceso** | `collector/policy.py` | Pruebas de políticas | Política fail-closed: deniega solicitudes si la fuente no está autorizada (`budget: 0`, `pending_review`). |

---

## 4. Diagrama del Flujo Editorial Real

```
                             [ ENTRADA LOCAL ]
                   (Fixtures ATS / HTML institucionales)
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   editorial_cli     │
                          │      import         │
                          └──────────┬──────────┘
                                     │ Normalización a Schema 2
                                     ▼
                          ┌─────────────────────┐
                          │  Bandeja Staging    │ (inbox.local.json /
                          │     Candidatos      │  archivos de lote)
                          └──────────┬──────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  validate-inbox  │       │   deduplicate    │       │     inspect      │
│  (Validación S2  │       │  (Detección de   │       │  (Métricas de    │
│  y Evidencias)   │       │   colisiones)    │       │  estado y TTL)   │
└────────┬─────────┘       └─────────┬────────┘       └─────────┬────────┘
         │                           │                          │
         └───────────────────────────┼──────────────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │     editorial_cli   │
                          │        report       │ (Informe consolidado)
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   prepare-review    │ (Exporta candidatos listos
                          │                     │  para decisión humana)
                          └──────────┬──────────┘
                                     │
                         [ REVISIÓN HUMANA MANUAL ]
                         (Promoción manual conforme a ADR-001;
                          Cero escrituras automáticas a semilla)
```

---

## 5. Resultados de Pruebas y Reproducibilidad

Todas las pruebas fueron ejecutadas y verificadas directamente en el checkout:

1. **Suite Completa de Pruebas Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **193 pruebas aprobadas (0 fallos, 0 errores)** en 2.55s.
2. **Construcción y Verificación de Catálogo:**
   - Comando: `python scripts/build_catalog.py --check`
   - Resultado: `Catálogo válido: 5 registros; snapshot coincide con la fuente canónica.`
3. **Validación Canónica de Catálogo:**
   - Comando: `python scripts/validate_catalog.py`
   - Resultado: `Válido: 5 fichas; modo=publicación no vacía; fecha Lima=2026-11-17.`
4. **Validación de Bandeja de Candidatos:**
   - Comando: `python scripts/validate_candidates.py data/candidates/inbox.example.json`
   - Resultado: `Bandeja local válida: 0 candidatos; no se modificó ni se publicó el catálogo.`
5. **Validación Editorial mediante CLI:**
   - Comando: `python scripts/editorial_cli.py validate-inbox data/candidates/inbox.example.json --verify-evidence`
   - Resultado: `Resultado: VÁLIDO (0 candidatos conformes con Schema 2; inalterado).`
6. **Pruebas End-to-End de Navegador (Playwright):**
   - Comando: `npx playwright test`
   - Resultado: **8 pruebas aprobadas (9.2s)** en Chromium y Mobile WebKit.
7. **Higiene de Formato de Código:**
   - Comando: `git diff --check`
   - Resultado: Salida limpia (cero espacios en blanco sobrantes).

---

## 6. Verificación de Seguridad e Integridad

### Hashes Criptográficos SHA-256 (Verificación Antes y Después):
- `data/opportunities.seed.json`:
  `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` (**Inalterado**)
- `data/opportunities.json`:
  `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` (**Inalterado**)
- `collector/sources.json`:
  `AE5BA4D314A450DB9118C3AD3A98A6FBE261542A74BD0EC7A623AA7F66B0A124` (**Inalterado**)

### Verificación de Políticas Fail-Closed:
- Las fuentes en `collector/sources.json` continúan todas con `enabled: false`.
- Las fuentes de revisión y prueba tienen `budget: 0` o presupuestos acotados (1).
- El estado `decision: pending_review` bloquea de raíz cualquier llamada de red.
- Cero secretos, API keys o credenciales fueron introducidos en el repositorio.

---

## 7. Reconciliación del Roadmap Maestro (R0 a R8)

| Fase / Bloque | Objetivo Principal | Estado Verificado | Dependencias | Bloqueos | Criterio de Salida | Siguiente Acción |
|---|---|---|---|---|---|---|
| **R0** | Cerrar alcance, contrato y criterios | **CERRADA** | Ninguna | Ninguno | Documentación rectora sin contradicciones | Mantener gobernanza |
| **R1** | Estabilizar catálogo y frontend Pages | **COMPLETADA** | R0 | Ninguno | Recursos 200 OK en producción | Mantenimiento operativo |
| **R2 (Línea B: R2-OSS-01..08)** | Pipeline de ingeniería offline | **CERRADA (100%)** | R1 | Ninguno | 193 pruebas aprobadas, CLI y pipeline E2E | Conservar infraestructura |
| **R2 (Línea A: Producto real)** | Obtener 1.ª oportunidad real autorizada | **ABIERTA / BLOQUEADA** | R1 + Autorización | Falta autorización externa documental | 1 ficha real aprobada en catálogo | Enviar borrador de autorización |
| **R3** | Validar utilidad profesional del MVP | **ABIERTA / BLOQUEADA** | R2 real aprobada | Bloqueada por R2 real | Pruebas de comprensión con usuarios reales | Supeditada a R2 real |
| **R4** | Automatizar fuentes autorizadas | **BLOQUEADA** | R2/R3 + Permiso técnico | Sin fuentes aprobadas | Conector automatizado acotado | Supeditada a R2/R3 |
| **R5** | Evaluación profesional explicable | **APLAZADA** | Muestra de datos reales | Falta volumen | Métricas de valor profesional | Planificación futura |
| **R6** | Preferencias, guardados y alertas | **APLAZADA** | R3 validada | Supeditada a R3 | Almacenamiento local privado | Planificación futura |
| **R7** | Trayectorias profesionales | **APLAZADA** | Datos longitudinales | Supeditada a volumen | Orientación profesional auditable | Planificación futura |
| **R8** | Consolidación operativa y salida SaaS | **APLAZADA** | Flujos R1–R7 estables | Fases previas | Autoalojamiento Nginx/Caddy | Planificación futura |

---

## 8. Determinación del Siguiente Paso

### Decisión Técnica:
**Opción A adoptada:** Se cierra formalmente la línea técnica **R2-OSS (R2-OSS-01 a R2-OSS-08)** al haberse cumplido el 100% de los criterios de ingeniería offline, integración, seguridad y pruebas.

### Delimitación de Roles y Responsabilidades:
1. **Acción del Propietario del Proyecto (Externa / Humana):**
   - Iniciar el contacto formal y obtener respuesta escrita de autorización hacia las entidades prioritarias documentadas en [docs/sources/seguimiento-autorizacion-fuentes.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/sources/seguimiento-autorizacion-fuentes.md) (prioritaria: [Canonical Careers](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/sources/canonical-careers-2026-11-11.md) o [SERVIR Talento Perú](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/sources/seguimiento-autorizacion-fuentes.md)).
   - El agente no puede enviar correos ni firmar convenios legales.
2. **Acción del Asistente Técnico / Agente (Interna):**
   - Una vez obtenida y registrada la autorización documental en `sources.json`, ejecutar el conector correspondiente mediante `scripts/editorial_cli.py` para ingresar la primera oportunidad real a staging y preparar su revisión editorial conforme a ADR-001.

---

## 9. Clasificación de Conclusiones

- `[HECHO]` La totalidad de los componentes de R2-OSS-01 a R2-OSS-07 existen físicamente, están integrados sin dependencias externas y pasan 193 pruebas automatizadas de Python y 8 pruebas Playwright E2E.
- `[HECHO]` Los archivos canónicos (`opportunities.seed.json`, `opportunities.json`, `sources.json`) y la bandeja local no sufrieron alteraciones ni escrituras no autorizadas.
- `[INFERENCIA]` La plataforma dispone de toda la infraestructura técnica necesaria para procesar, deduplicar y verificar oportunidades tan pronto como se obtenga una autorización legítima.
- `[BLOQUEO EXTERNO]` La fase R2 a nivel de producto permanece bloqueada porque la autorización de fuentes es un trámite humano y legal del mundo exterior que ningún desarrollo técnico puede sustituir.
- `[PROPUESTA]` Mantener el código en su estado actual, cerrar documentalmente la línea R2-OSS y esperar la respuesta de autorización de fuentes antes de iniciar cualquier captura en producción.
