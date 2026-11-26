# VELORA AUDIT REPORT — TASK-R6-01
# Motor Determinista de Autopublicación Basado en Reglas

- **ID de Auditoría:** `AUDIT-R6-01-AUTOPUBLISH`
- **Proyecto:** Velora
- **Fase:** R6 — Automatización operativa
- **Tarea:** `TASK-R6-01 — Implementación del motor de autopublicación basado en reglas`
- **Prioridad:** P1
- **Clasificación:** `[DESARROLLO_PROPIO - Justificado]`
- **Fecha de Certificación:** 25 de noviembre de 2026
- **Responsables:** Principal Software Engineer, Senior Software Architect, Technical Auditor & Software Delivery Architect
- **Autorización Soberana:** Aprobación explícita de la **Opción A de la Decisión 2** (`docs/audits/VELORA-OPEN-DECISIONS.md`).
- **Estado de Tarea:** `COMPLETED`

---

## 1. Resumen Ejecutivo y Dictamen de Auditoría

Se certifica la implementación completa, verificación y aseguramiento de calidad del **Motor de Autopublicación Basado en Reglas Objetivas (`TASK-R6-01`)** para el producto Velora.

El motor resuelve el cuello de botella operativo de revisión manual individual de cada oportunidad capturada, permitiendo promover desatendida y automáticamente al catálogo canónico únicamente a aquellos candidatos de staging que satisfacen de forma simultánea, estricta y demostrable **seis (6) condiciones objetivas de calidad, seguridad y procedencia**, bajo la arquitectura *fail-closed* y con cero dependencias externas (Python estándar puro).

### Métricas de Certificación Técnica
- **Código del motor:** Implementado en `collector/autopublish.py` (970 líneas de código limpio y desacoplado).
- **Interfaz operativa:** Integrado en `scripts/editorial_cli.py` mediante el subcomando `autopublish` con salvaguarda *dry-run* activa por defecto.
- **Suite de pruebas:** Implementados y ejecutados 18 escenarios de prueba exhaustivos en `tests/test_autopublish.py`.
- **Resultado de pruebas globales:** **254 pruebas pasando al 100% en 4.5s** sin errores ni advertencias regresivas.
- **Evaluación en staging real (`inbox.local.json`):** 295 candidatos evaluados; **90 candidatos aprobados** como aptos para publicación y **108 retenidos** en revisión.
- **Integridad canónica:** `data/opportunities.seed.json` y `data/opportunities.json` permanecieron **100% intactos**, con sus sumas de verificación SHA-256 rigurosamente preservadas.

---

## 2. Arquitectura del Motor y Principios de Diseño

```
                                  [ Bandeja de Staging: inbox.local.json ]
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │          EVALUADOR FAIL-CLOSED (collector/autopublish.py)    │
                     └──────────────────────────────┬──────────────────────────────┘
                                                    │
             ┌───────────────────┬──────────────────┼───────────────────┬───────────────────┐
             ▼                   ▼                  ▼                   ▼                   ▼
       [ Regla 1 ]         [ Regla 2 ]        [ Regla 3 ]         [ Regla 4 ]         [ Regla 5 ]         [ Regla 6 ]
     Fuente Aprobada      URL HTTPS en       Taxonomía DIRECT     Elegibilidad       Deduplicación       Vigencia TTL o
     y Acceso Auto.       Lista Blanca       (Sistemas/Comp.)     Explicita Perú      Sin Colisión       Deadline Futuro
             │                   │                  │                   │                   │                   │
             └───────────────────┴──────────────────┼───────────────────┴───────────────────┴───────────────────┘
                                                    │
                                         ¿Cumple 6/6 Reglas?
                                                    │
                                ┌───────────────────┴───────────────────┐
                                │                                       │
                             SÍ (100%)                               NO (<100%)
                                │                                       │
                                ▼                                       ▼
                 ┌─────────────────────────────┐         ┌─────────────────────────────┐
                 │ Promoción a Catálogo        │         │ Retención en Staging        │
                 │ Schema 2 (OP-XXX)           │         │ (pending_review)            │
                 │ - fieldEvidence completo    │         │ - Motivos detallados        │
                 │ - verificationEvidence      │         │ - Explicabilidad auditable  │
                 │ - editorialDecision auto    │         └─────────────────────────────┘
                 │ - Regeneración snapshot     │
                 └─────────────────────────────┘
```

### Principios Fundamentales
1. **Fail-Closed Estricto:** Cualquier duda, error de red/formato, campo faltante, advertencia de taxonomía o ambigüedad territorial retiene inmediatamente al candidato en estado `pending_review`.
2. **Independencia de Reglas:** Ninguna regla compensa a otra. Un candidato con clasificación técnica perfecta (`DIRECT`) pero sin prueba explícita de contratación en Perú (`PERU_REMOTE` o `PERU_LOCAL`) es retenido obligatoriamente.
3. **Aislamiento de Staging:** Los candidatos retenidos jamás son eliminados de forma desatendida ni se altera su procedencia.
4. **Protección Canónica Absoluta:** La modificación de `data/opportunities.seed.json` y `data/opportunities.json` solo ocurre cuando el modo `--apply` es invocado explícitamente y se genera un lote conforme con el validador estricto de `catalog_quality.py`.
5. **Cero Dependencias Externas:** Construido íntegramente sobre la biblioteca estándar de Python (`json`, `dataclasses`, `datetime`, `urllib.parse`, `re`, `pathlib`).

---

## 3. Especificación Detallada de las Seis (6) Reglas Obligatorias

### Regla 1 — Fuente Autorizada (`rule1_authorized_source`)
- **Objetivo:** Garantizar que la procedencia del dato cuente con autorización soberana previa del propietario y habilitación técnica para recolección automatizada.
- **Condición requerida:**
  - `sourceId` registrado en `collector/sources.json`.
  - `source.decision == "approved"`.
  - `source.automatedAccessStatus == "approved"`.
- **Criterio de retención:** Si la fuente está en `pending_review`, `review_needed`, `rejected`, o si `automatedAccessStatus` no es `"approved"` (ej. `manual_only`), el candidato no se autopublica.

### Regla 2 — URL de Postulación Segura (`rule2_secure_apply_url`)
- **Objetivo:** Proteger a los usuarios contra phishing, sitios no verificados, esquemas inseguros o secuestro de enlaces.
- **Condición requerida:**
  - `applyUrl` utiliza exclusivamente el esquema `https://`.
  - El puerto debe ser 443 o predeterminado (sin puertos extraños).
  - Cero credenciales incrustadas (sin usuario ni contraseña en la URL).
  - El hostname de la URL debe pertenecer estrictamente a la lista blanca autorizada de la fuente (`allowedPostingHosts` o `allowedHosts`).
- **Defensa contra ataques de subdominio/subcadena:** Se implementó `is_host_allowlisted()` para impedir ataques de sufijo o similitud (ej. `evil-encora.com` intentando validar contra `encora.com`). Solo se aceptan coincidencias exactas o subdominios legítimos (`.encora.com`).

### Regla 3 — Taxonomía Técnica Inequívoca (`rule3_technical_classification`)
- **Objetivo:** Proteger la propuesta de valor editorial de Velora, publicando exclusivamente roles técnicos genuinos del campo de la computación, software y sistemas.
- **Condición requerida:**
  - Evaluación contra el motor determinista de clasificación (`collector/classification.py`).
  - La relevancia calculada debe ser estrictamente `DIRECT`.
- **Criterio de retención:** Todo rol catalogado como `ADJACENT` (analistas de procesos operativos, mesa de ayuda genérica, contabilidad, compras, cobranza) o `OUT_OF_SCOPE` (administrativos, legales, comerciales puros) queda retenido en `pending_review`.

### Regla 4 — Elegibilidad Explícita para Perú (`rule4_peru_eligibility`)
- **Objetivo:** Garantizar que la vacante sea legal y prácticamente accesible para personas radicadas en territorio peruano.
- **Condición requerida (Independiente y Obligatoria):**
  - La clasificación geográfica debe resolver inequívocamente a `PERU_LOCAL` (ubicación física en territorio peruano: Lima, Miraflores, San Isidro, Surquillo, Arequipa, etc.) o `PERU_REMOTE` (remoto con mención expresa de elegibilidad para Perú o contratación bajo entidad peruana).
- **Criterio de retención:** Términos remotos genéricos o regionales vagos (`LATAM`, `América Latina`, `Worldwide`, `Global Remote`, `Remoto no especificado`) sin mención o comprobación de elegibilidad en Perú son retenidos obligatoriamente.

### Regla 5 — Deduplicación sin Colisiones (`rule5_deduplication`)
- **Objetivo:** Evitar la publicación de ofertas redundantes, identificadores duplicados o colisiones de clave primaria.
- **Condición requerida:**
  - Cero colisiones contra el catálogo canónico publicado (`data/opportunities.seed.json`).
  - Cero colisiones dentro del lote evaluado en la misma corrida.
  - Comprobación en tres niveles:
    1. **Colisión exacta de URL:** URL de postulación idéntica.
    2. **Colisión de clave primaria / Requisición:** Mismo identificador externo de ATS (`requisition`).
    3. **Colisión por firma secundaria:** Mismo empleador normalizado y mismo título normalizado contra una vacante canónica actualmente abierta (`opportunityStatus == "open"`).
- **Criterio de retención:** Si colisiona con una oportunidad canónica abierta, se retiene como duplicado.

### Regla 6 — Vigencia y Trazabilidad Verificables (`rule6_validity_and_traceability`)
- **Objetivo:** Impedir la publicación de convocatorias vencidas, extemporáneas o sin rastro documental auditable.
- **Condición requerida:**
  - **Trazabilidad completa:** Presencia obligatoria de `sourceId`, `sourceUrl` HTTPS, `applyUrl` HTTPS, `capturedAt` ISO válido y lista `fieldEvidence` no vacía.
  - **Ausencia de contradicciones:** Se escanea el título, descripción y notas editoriales descartando palabras clave de cierre (`finalizada`, `concluida`, `cancelada`, `desierta`, `cerrada`, `proceso concluido`).
  - **Vigencia comprobada (Alternativa A o B):**
    - *Alternativa A (Fecha límite):* `deadline >= as_of` (fecha límite válida YYYY-MM-DD igual o posterior a la fecha civil de evaluación).
    - *Alternativa B (Conector directo ATS):* Para fuentes ATS directas (`greenhouse-job-board`, `lever-postings`, `hiringroom-board`, `ositran-portal`, `gobpe-convocatorias`), confirmación de vacante activa capturada dentro de la ventana de frescura TTL (`<= 7` días respecto a `as_of`).
- **Criterio de retención:** Si la fecha límite expiró (`deadline < as_of`) o si la captura de ATS supera los 7 días de TTL sin fecha límite futura, el candidato es retenido.

---

## 4. Transformación Conforme a Opportunity Schema 2

Cuando un candidato cumple satisfactoriamente el 100% de las 6 reglas, la función `convert_candidate_to_opportunity()` construye el objeto canónico de Schema 2 respetando estrictamente el contrato auditado por `scripts/catalog_quality.py`:

1. **Asignación secuencial de identificador:** Calcula el ID canónico incremental (`OP-113`, `OP-114`, etc.) a partir del máximo existente en `opportunities.seed.json`.
2. **Normalización de taxonomía y facetas:** Mapea el sector (`Tecnología`, `Sector Público`, `Finanzas y Banca`), familia técnica (`Desarrollo y QA`, `Analítica y datos`, `Sistemas e Infraestructura`, `Ciberseguridad`, `Sistemas empresariales`), nivel y modalidad.
3. **Evidencia por hecho factual (`fieldEvidence`):** En cumplimiento de la regla de calidad que exige que todo dato factual declarado cuente con su respaldo documental, genera un registro de evidencia para cada atributo (`employer`, `publisher`, `title`, `sourceUrl`, `applyUrl`, `location`, `mode`, `sector`, `family`, `level`, `kind`, `eligibility`, `duration`, `salary`, `deadline`, `publishedAt`), vinculándolo a un host autorizado y dentro de la ventana de frescura.
4. **Metadatos de verificación desatendida (`verificationEvidence`):** Declara método `automated`, relación `employer_confirmed` y resultado `application_open`.
5. **Decisión editorial auditable (`editorialDecision`):** Registra `status: "approved"`, reviewer `Autopublication Engine (TASK-R6-01)`, timestamp ISO y nota explicativa citando la autorización soberana.

---

## 5. Matriz de Resultados de los 18 Escenarios de Aceptación

Los 18 escenarios definidos en los requerimientos fueron codificados en `tests/test_autopublish.py` y pasaron satisfactoriamente al 100%:

| # | Escenario de Prueba | Comportamiento Verificado | Resultado |
|---|---|---|---|
| **1** | Candidato que cumple las 6 reglas simultáneas | Evaluado como `eligible_for_publication`; cero motivos de fallo | `PASS` |
| **2** | Fuente no aprobada (`decision != "approved"`) | Retenido en `pending_review`; fallo en Regla 1 | `PASS` |
| **3** | Acceso automatizado no aprobado (`automatedAccessStatus != "approved"`) | Retenido en `pending_review`; fallo en Regla 1 | `PASS` |
| **4** | URL de postulación no segura (HTTP en vez de HTTPS) | Retenido en `pending_review`; fallo en Regla 2 | `PASS` |
| **5** | Host fuera de lista blanca (intento con `evil-encora.com`) | Retenido en `pending_review`; fallo en Regla 2 | `PASS` |
| **6** | Clasificación técnica ambigua o adyacente (`ADJACENT`) | Retenido en `pending_review`; fallo en Regla 3 | `PASS` |
| **7** | Candidato remoto genérico sin prueba para Perú (`LATAM`) | Retenido en `pending_review`; fallo en Regla 4 | `PASS` |
| **8** | Elegibilidad explícita confirmada (`PERU_LOCAL` y `PERU_REMOTE`) | Aprueba Regla 4 de forma independiente | `PASS` |
| **9** | Duplicado exacto por URL contra el catálogo canónico | Retenido en `pending_review`; fallo en Regla 5 | `PASS` |
| **10** | Posible duplicado por firma secundaria (`employer\|title`) | Retenido en `pending_review`; fallo en Regla 5 | `PASS` |
| **11** | Fecha límite expirada (`deadline < as_of`) | Retenido en `pending_review`; fallo en Regla 6 | `PASS` |
| **12** | Captura ATS desactualizada superando TTL (> 7 días) | Retenido en `pending_review`; fallo en Regla 6 | `PASS` |
| **13** | Evidencia incompleta / campos raíz faltantes | Retenido en `pending_review`; fallo en Regla 6 | `PASS` |
| **14** | Evidencia contradictoria (indicios de vacante cerrada/finalizada) | Retenido en `pending_review`; fallo en Regla 6 | `PASS` |
| **15** | Excepción inesperada durante validación (datos corruptos) | Retenido en `pending_review` bajo *fail-closed* | `PASS` |
| **16** | Idempotencia: segunda ejecución idéntica produce 0 duplicados | Catálogo canónico idéntico en corrida 1 y 2 | `PASS` |
| **17** | Oportunidades canónicas preexistentes conservadas intactas | Preservación exacta campo por campo de registros existentes | `PASS` |
| **18** | Lote mixto: solo candidatos 100% conformes son promovidos | 2 promovidos, 3 retenidos en staging con estados correctos | `PASS` |

---

## 6. Resultados de Evaluación en Seco (*Dry-Run*) sobre la Bandeja Real

Se ejecutó el motor sobre la bandeja real `data/candidates/inbox.local.json` con fecha de corte `2026-11-25`:

```bash
python scripts/editorial_cli.py autopublish --dry-run
```

### Métricas Obtenidas:
- **Total de candidatos evaluados en staging:** 295
- **Candidatos aprobados como aptos para publicación:** 90
- **Candidatos retenidos en revisión manual:** 108
- **Candidatos previamente procesados/aprobados:** 97
- **Oportunidades promovidas al catálogo canónico:** 0 (Modo dry-run activo)

### Análisis de Retenciones Clave:
1. **Fuentes de plantilla y no autorizadas:** Candidatos de `greenhouse-public-job-board-template` retenidos por Regla 1 (fuente de prueba no aprobada) y Regla 5 (colisión con registros canónicos existentes OP-006 a OP-010).
2. **Procesos estatales concluidos (INDECOPI):** Candidatos de `gobpe-indecopi-convocatorias` retenidos por Regla 6 (evidencia explícita de "Convocatoria finalizada" en las bases de Gob.pe).
3. **Candidatos de HiringRoom (Canvia, Stefanini, MyApps, Efitec):** Los 20 candidatos técnicos vigentes incorporados en `TASK-R5-03` resultaron clasificados como **[APTO]**, al cumplir estrictamente:
   - Fuentes aprobadas (`decision: "approved"`, `automatedAccessStatus: "approved"`).
   - Hosts autorizados (`*.hiringroom.com`).
   - Taxonomía directa (`DIRECT` en desarrollo, QA, soporte e infraestructura).
   - Ubicación en Perú (`Lima`, `Miraflores`, `Surquillo`).
   - Cero colisiones con el catálogo.
   - Capturas dentro del TTL de 7 días.

---

## 7. Certificación de Integridad Canónica

Se certifica que ningún archivo de producción ni catálogo canónico fue modificado de forma no controlada.

### Sumas de Verificación SHA-256:
- `data/opportunities.seed.json`: `710D7722856665C42483BABD2202AB851839BB4557AE454692E6D6508B7C1917` (112 registros)
- `data/opportunities.json`: `1D96ECACDB6F07572509484BA1A562E039D2600050A79BB9D09ADDB576A8AF02` (112 registros)

**Estado:** 100% idénticos e inalterados respecto a la línea base certificada al inicio de la tarea.

---

## 8. Siguiente Acción Recomendada

Con `TASK-R6-01` completamente implementada, probada y documentada, el Roadmap Maestro (`docs/roadmap/VELORA-MASTER-ROADMAP.md`) avanza a su siguiente acción operativa única:

- **`TASK-R6-02` — Revalidación Programada en GitHub Actions:**  
  Automatizar la comprobación semanal desatendida mediante cron en GitHub Actions para detectar vacantes que desaparezcan de los ATS y marcarlas como concluidas/históricas, preservando la frescura continua de Velora sin intervención manual.
