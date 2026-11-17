# Informe de Auditoría Técnica R2-OSS-06: CLI Unificado de Gestión Editorial y Observabilidad Local

**Proyecto:** Ruta Sistemas  
**Fecha:** 2026-11-17  
**Fase:** R2-OSS-06 — CLI unificado de gestión de bandeja editorial y observabilidad local  
**Estado:** COMPLETADA Y VERIFICADA  
**Modo de ejecución:** Agente autónomo / Principal Software Architect & QA Lead  
**Clasificación técnica:** `[DESARROLLO_PROPIO - Justificado]`  

---

## 1. Resumen Ejecutivo

En el marco de la arquitectura editorial Schema 2 de Ruta Sistemas, se implementó la herramienta central de línea de comandos `scripts/editorial_cli.py`.

La CLI proporciona al revisor humano un punto de acceso unificado, reproducible y estrictamente offline para operar sobre la bandeja de candidatos, normalizar fixtures locales, evaluar deduplicaciones y colisiones, validar el cumplimiento de Schema 2, inspeccionar la frescura de evidencias y preparar candidatos seleccionados para revisión formal.

### Logros Principales:
1. **Orquestación de Componentes Reales:** La CLI integra y delega secuencialmente en `collector/ats_connectors.py`, `collector/jsonld_extractor.py`, `collector/dedup.py`, `collector/evidence.py`, `collector/policy.py` y `scripts/validate_candidates.py` sin duplicar lógica interna.
2. **Cero Dependencias Externas:** Construida enteramente sobre la biblioteca estándar de Python (`argparse`, `json`, `pathlib`, `datetime`). Se rechazó el uso de frameworks externos como Click, Typer o Rich para evitar riesgos en la cadena de suministro.
3. **Seguridad e Inviolabilidad de Catálogo:** Mecanismo estricto de guardián (`_assert_not_canonical`) que bloquea a nivel de código cualquier intento de escritura sobre `data/opportunities.seed.json` o `data/opportunities.json`. La promoción continúa siendo un acto editorial humano independiente.
4. **Protección de Datos Locales:** Las operaciones de análisis (`validate-inbox`, `deduplicate`, `inspect`, `report`) son estrictamente de solo lectura sobre los archivos de entrada. La exportación requiere rutas destino explícitas y confirmación para sobrescritura.
5. **Observabilidad Estructurada:** Generación de informes tanto en formato legible en consola como en JSON estructurado para auditorías automatizadas o integración futura.
6. **Batería de Pruebas Automatizadas:** 30 pruebas unitarias y de integración dedicadas en `tests/test_editorial_cli.py`, elevando la suite completa de pruebas unitarias Python a **189 pruebas aprobadas (0 fallos)**.

---

## 2. Diagrama del Flujo Integrado

```
                              [ ENTRADA LOCAL ]
                    (Fixtures ATS / JSON-LD HTML locales)
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

## 3. Subcomandos Implementados

| Subcomando | Propósito | Entradas Principales | Salidas / Efectos | Código Éxito / Error |
|---|---|---|---|---|
| `validate-inbox` | Valida cumplimiento de Schema 2 y opcionalmente vigencia y procedencia de evidencias. | `[path]`, `--as-of`, `--verify-evidence`, `--json-report` | Salida en consola o JSON estructurado. Solo lectura. | 0: Válido<br>1: Error datos<br>2: Error operativo |
| `deduplicate` | Compara un lote contra sí mismo, contra la bandeja y contra el catálogo canónico. | `[path]`, `--inbox`, `--seed`, `--fail-on-collision`, `--json-report` | Reporte determinista de duplicados exactos, colisiones y posibles duplicados. Solo lectura. | 0: Sin colisiones<br>1: Colisión detectada<br>2: Error operativo |
| `inspect` | Inspecciona el volumen, fuentes, estados editoriales y resumen de frescura TTL. | `[path]`, `--as-of`, `--verify-evidence`, `--json-report` | Desglose cuantitativo en consola o JSON. Solo lectura. | 0: Éxito<br>2: Error operativo |
| `report` | Genera un informe integral consolidado de validación, duplicados y evidencias. | `[path]`, `--seed`, `--as-of`, `--output`, `--json-report` | Reporte consolidado en pantalla o guardado en archivo independiente. Solo lectura de entrada. | 0: Válido<br>1: Error datos/colisión<br>2: Error operativo |
| `import` | Normaliza datos locales en formatos ATS (Greenhouse, Lever) o HTML/JSON-LD a Schema 2. | `--format`, `--source-id`, `--input`, `--output`, `--source-url`, `--force-write` | Genera contenedor Schema 2 de candidatos en archivo destino. Cero llamadas HTTP. | 0: Éxito<br>2: Error operativo |
| `prepare-review` | Filtra y exporta candidatos listos para revisión y auditoría humana. | `--inbox`, `--output`, `--status`, `--force-write` | Genera archivo de exportación con advertencia de no publicación. Prohíbe escribir a semilla. | 0: Éxito<br>2: Error operativo |

---

## 4. Pruebas y Resultados de Validación

1. **Suite de Pruebas Unitarias de la CLI (`tests/test_editorial_cli.py`):**
   - 30 pruebas unitarias aprobadas (tiempo: 0.14s).
   - Cobertura: ayuda general y de cada subcomando, validación de inbox, deduplicación y colisiones, inspección de métricas, generación de reportes JSON y en archivo, importación ATS (Greenhouse y Lever), importación HTML/JSON-LD, preparación de revisión con filtros, rechazo estricto de escritura a archivos canónicos, soporte de rutas con espacios y verificación de determinismo.
2. **Suite Global de Pruebas Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **189 pruebas aprobadas, 0 fallos, 0 errores** en 2.73s.
3. **Verificación de Catálogo y Snapshot:**
   - `python scripts/build_catalog.py --check`: Catálogo válido, snapshot consistente.
   - `python scripts/validate_catalog.py`: Validador canónico conforme.
4. **Pruebas E2E de Navegador:**
   - `npx playwright test`: **8 pruebas aprobadas (Chromium y Mobile WebKit)**.
5. **Inviolabilidad de Archivos Canónicos:**
   - `data/opportunities.seed.json`: `772F576E06269B8F41191F34AED32A8CE9894729BC858538FF7BF630EAF9C5D6` (Inalterado)
   - `data/opportunities.json`: `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` (Inalterado)
   - `collector/sources.json`: `AE5BA4D314A450DB9118C3AD3A98A6FBE261542A74BD0EC7A623AA7F66B0A124` (Inalterado)
6. **Higiene de Formato de Código:**
   - `git diff --check`: Salida limpia (sin espacios en blanco residuales).

---

## 5. Trazabilidad de Decisiones y Documentos Actualizados

- `Diseno-modelo-datos-arquitectura-piloto-2026-10-03.md`: Sección 51 actualizada con el cierre formal de R2-OSS-06 y la consolidación de 189 pruebas unitarias.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Sección 7 actualizada con la culminación de la línea offline R2-OSS (R2-OSS-01 a R2-OSS-06).
- `README.md`: Sección operativa añadida documentando la ejecución de `scripts/editorial_cli.py`.
- `docs/audits/r2-oss-06-editorial-cli-audit-2026-11-17.md`: Este informe de auditoría técnica.

---

## 6. Estado Final y Siguiente Acción

- **Línea Offline R2-OSS (R2-OSS-01 a R2-OSS-06):** **100% COMPLETADA Y CERRADA.** Toda la infraestructura de normalización, deduplicación, validación, verificación y observabilidad está operativa y probada.
- **Bloqueo Material del MVP (Fase R2):** **VIGENTE.** El proyecto no tiene fuentes externas autorizadas para capturar vacantes reales. Ningún scraper ni conector se ejecutará contra servidores externos mientras no se cuente con la confirmación documental requerida.
- **Siguiente acción recomendada:** Gestionar y registrar la autorización formal de una fuente real (e.g. Canonical Careers o SERVIR Talento Perú) conforme al protocolo de [seguimiento de autorización](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/sources/seguimiento-autorizacion-fuentes.md) para permitir el ingreso de la primera oportunidad real al staging editorial.
