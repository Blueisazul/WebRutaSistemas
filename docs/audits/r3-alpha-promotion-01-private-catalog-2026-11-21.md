# R3-ALPHA-PROMOTION-01 — Promoción Editorial Controlada de Cinco Oportunidades Canonical a la Alpha Privada

**Proyecto:** Ruta Sistemas  
**Fase:** R3 — Evaluación con Círculo Cercano y Alpha Privada  
**Identificador del bloque:** `R3-ALPHA-PROMOTION-01` (subtareas `01A`, `01B`, `01C`, `01D`)  
**Fecha de ejecución y corte:** 2026-11-21T08:10:00-05:00 (Hora Lima, UTC-5)  
**Responsables (Roles):** Principal Software Engineer, Senior Software Architect, Technical Product Manager y Technical Auditor  
**Estado:** `DONE` (Catálogo de Alpha privada ampliado a 6 vacantes reales y 5 demostrativas; validación técnica 100% aprobada)  
**Rama activa:** `integration/r1-02c`  
**HEAD de referencia:** `b27e418fb80f1e2c9d406fbf135b395ab6c4705d` (en sincronía con `origin/integration/r1-02c`)  
**Documentos rectores:**
- [docs/architecture/r0-decisiones-y-alcance-2026-11-12.md](../architecture/r0-decisiones-y-alcance-2026-11-12.md)
- [docs/architecture/r3-private-alpha-scope-decision-2026-11-20.md](../architecture/r3-private-alpha-scope-decision-2026-11-20.md)
- [docs/audits/r3-alpha-curation-01-second-batch-2026-11-20.md](r3-alpha-curation-01-second-batch-2026-11-20.md)
- [docs/audits/r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md](r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md)

---

## 1. Autorización Expresa y Decisión del Propietario

En cumplimiento de la gobernanza de Ruta Sistemas y tras la entrega del expediente [docs/audits/r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md](r3-alpha-owner-review-01-canonical-editorial-decision-2026-11-20.md), el propietario del proyecto **autorizó expresamente la OPCIÓN A**:

> **Autorización:** Incorporar el lote completo de cinco oportunidades de Canonical Ubuntu a la Alpha privada, destinadas con exclusividad al uso personal del propietario y su círculo cercano no comercial, con el objetivo de resolver el cuello de botella de contenido y evaluar el producto con mayor diversidad disciplinaria (desarrollo, sistemas operativos, kernel, cloud, redes y soporte técnico).

### Delimitación Estricta del Alcance Autorizado:
- **Ámbito:** Local / Alpha privada (servidor loopback `server.py` en `127.0.0.1:4173`).
- **Prohibiciones absolutas respetadas:**
  - Cero publicación en producción externa o GitHub Pages.
  - Cero merge a la rama `main`.
  - Cero commits o pushes no autorizados a repositorios remotos.
  - Cero activación de fuentes en `collector/sources.json` (`canonical-careers` y plantillas ATS permanecen con `enabled: false` y `termsReview: pending`).
  - Cero scraping intrusivo o sincronizaciones automatizadas en segundo plano.

---

## 2. Revalidación Técnica en Tiempo Real Previa a la Promoción

El 21-11-2026 a las 08:03 (UTC-5), se revalidaron las cinco candidatas contra los endpoints públicos del ATS Greenhouse y las páginas oficiales de postulación web:

```
                            [ REVALIDACIÓN EN TIEMPO REAL (2026-11-21) ]
                                                  │
             ┌────────────────────────────────────┼────────────────────────────────────┐
             ▼                                    ▼                                    ▼
       [ OP-006: 8379825 ]                [ OP-007: 6707669 ]                  [ OP-008: 5370815 ]
  Graduate Software Engineer          Junior Ubuntu Software Engineer      Junior Linux Kernel Engineer
  - Cohorte 2026/2027 (16-11-2026)    - Rolling pipeline (act. 08-2026)    - Rolling pipeline (act. 08-2026)
  - HTTP 200 / Formulario Activo      - HTTP 200 / Formulario Activo       - HTTP 200 / Formulario Activo
  - Elegible Perú (AMER UTC-5)        - Elegible Perú (AMER UTC-5)         - Elegible Perú (AMER UTC-5)
             │                                    │                                    │
             └────────────────────────────────────┼────────────────────────────────────┘
                                                  ▼
                               [ OP-009: 3257589 ]        [ OP-010: 6448444 ]
                            Software Engineer Python    Associate Linux Support
                            - Rolling pipeline Americas - Rolling pipeline Sysadmin
                            - HTTP 200 / Form activo    - HTTP 200 / Form activo
                            - Elegible Perú (AMER)      - Elegible Perú (AMER)
```

1. **`8379825` (Canonical Graduate Software Engineer):** Publicada el `2026-11-16T08:39:36-05:00`. Cohorte fresca orientada a graduados 2026 y 2027. Formulario web plenamente activo en `job-boards.greenhouse.io`.
2. **`6707669` (Canonical Junior Ubuntu Software Engineer):** Publicada el `2025-11-07`, actualizada el `2026-08-05`. Requisición continua activa con formulario interactivo.
3. **`5370815` (Canonical Junior Linux Kernel Engineer):** Publicada el `2024-02-25`, actualizada el `2026-08-05`. Pipeline continuo activo para ingeniería de bajo nivel.
4. **`3257589` (Canonical Software Engineer Python Cloud):** Publicada el `2021-06-28`, actualizada el `2026-08-05`. Requisición continua delimitada para la región Américas (coincidente con UTC-5 Lima).
5. **`6448444` (Canonical Associate Linux Support Engineer):** Publicada el `2025-02-10`, actualizada el `2026-08-05`. Pipeline continuo activo para operaciones de TI y soporte en servidores.

---

## 3. Identificadores Canónicos Asignados y Asignación Editorial

Se asignaron los identificadores canónicos consecutivos `OP-006` a `OP-010` respetando la política de identificadores únicos sin colisiones con los registros preexistentes:

| ID Canónico | Requisition ID | Título Oficial | Empleador | Familia Profesional | Nivel | Modalidad | Elegibilidad Territorial | Fecha de Publicación | Estado Catálogo |
|---|---|---|---|---|---|---|---|---|---|
| **`OP-006`** | `8379825` | Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu | Canonical | Desarrollo y QA | Egresado / bachiller | Remoto | Perú (remoto internacional) | 2026-11-16 (Cohorte 2026/2027) | `active` / `curated` |
| **`OP-007`** | `6707669` | Junior Ubuntu Software Engineer | Canonical | Desarrollo y QA | Junior | Remoto | Perú (remoto internacional) | 2025-11-07 (Rolling pipeline) | `active` / `curated` |
| **`OP-008`** | `5370815` | Junior Linux Kernel Engineer - Ubuntu | Canonical | Desarrollo y QA | Junior | Remoto | Perú (remoto internacional) | 2024-02-25 (Rolling pipeline) | `active` / `curated` |
| **`OP-009`** | `3257589` | Software Engineer - Python - Cloud - graduate level | Canonical | Desarrollo y QA | Egresado / bachiller | Remoto | Perú (remoto internacional) | 2021-06-28 (Rolling pipeline) | `active` / `curated` |
| **`OP-010`** | `6448444` | Associate Linux Support Engineer | Canonical | Sistemas empresariales | Egresado / bachiller | Remoto | Perú (remoto internacional) | 2025-02-10 (Rolling pipeline) | `active` / `curated` |

---

## 4. Condiciones Editoriales, Limitaciones y Advertencias Explícitas

En estricta conformidad con los requisitos éticos y de transparencia de Ruta Sistemas, cada ficha promovida incorpora las siguientes advertencias obligatorias:

1. **Jornada de Tiempo Completo (40 horas semanales):**
   - Ninguna de las cinco oportunidades es un convenio de prácticas preprofesionales (ley peruana 28518).
   - Son empleos directos full-time. En el campo `risk` de cada ficha se especifica que no es compatible con estudiantes en ciclo lectivo regular presencial, orientándose a graduandos 2026/2027, egresados y perfiles junior disponibles a tiempo completo.
2. **Requisito de Idioma Inglés:**
   - Todas las descripciones oficiales exigen dominio profesional o fluido de inglés escrito y hablado para interactuar con equipos distribuidos en más de 75 países.
3. **Distinción entre Cohorte Fresca y Requisiciones Continuas:**
   - `OP-006` está expresamente catalogada como convocatoria fresca (publicada el 16-11-2026 para graduados 2026 y 2027).
   - `OP-007`, `OP-008`, `OP-009` y `OP-010` declaran su carácter de *rolling talent pipeline* (requisiciones continuas estratégicas actualizadas semestralmente por Canonical).
4. **Tratamiento del Salario no Publicado:**
   - En cumplimiento estricto del contrato, el campo `salary` se mantiene como `"No publicado"` con `salaryNote: "No informado en la convocatoria pública (incluye USD 2,000/año para desarrollo profesional y sprints internacionales)"`. Cero datos inventados.

---

## 5. Integridad Canónica de Evidencias (`fieldEvidence`)

Cada una de las cinco nuevas fichas cuenta con su desglose exhaustivo de evidencias por dato en `fieldEvidence`, con timestamp Lima reciente (`observedAt: 2026-11-21T08:03:15-05:00`) y URLs oficiales bajo hosts auditados (`canonical.com`, `job-boards.greenhouse.io`, `boards-api.greenhouse.io`):

- **Campos respaldados con evidencia pericial:** `employer`, `publisher`, `title`, `sourceUrl`, `applyUrl`, `publishedAt`, `location`, `mode`, `requirements`, `tasks`, `skills`, `sector`, `family`, `level`, `kind`, `eligibility`, `duration`, `salary`, `benefits`, `growth`, `continuity`, `risk`.
- **Decisión editorial registrada:**
  ```json
  "editorialDecision": {
    "status": "approved",
    "reviewer": "Propietario / Equipo Editorial Ruta Sistemas",
    "reason": "Oportunidad real de tecnología en Canonical Ubuntu, aprobada para la Alpha privada (círculo íntimo) mediante Opción A del expediente R3-ALPHA-OWNER-REVIEW-01.",
    "decidedAt": "2026-11-21T08:00:00-05:00"
  }
  ```

---

## 6. Estado del Catálogo Canónico y Bandeja Staging

### 6.1. Composición del Catálogo Canónico (`opportunities.seed.json` y `opportunities.json`)
El catálogo queda conformado por **11 registros en total**:
- **6 Oportunidades reales activas (`curated` / `active`):**
  1. `OP-005`: CookUnity — Supply Chain Analyst (Lima, Perú)
  2. `OP-006`: Canonical — Graduate Software Engineer, Open Source and Linux (Remoto, cohorte 2026/2027)
  3. `OP-007`: Canonical — Junior Ubuntu Software Engineer (Remoto, rolling)
  4. `OP-008`: Canonical — Junior Linux Kernel Engineer - Ubuntu (Remoto, rolling)
  5. `OP-009`: Canonical — Software Engineer - Python - Cloud - graduate level (Remoto Américas, rolling)
  6. `OP-010`: Canonical — Associate Linux Support Engineer (Remoto, rolling)
- **5 Registros demostrativos (`demonstration`):**
  - `OP-001`: OSITRAN — Practicante profesional de TI (Histórico)
  - `OP-002`: 42Labs — Mobile Developer iOS Swift (Sin confirmar)
  - `OP-003`: 42Labs — Android Developer (Sin confirmar)
  - `OP-004`: Launchpad Technologies — Implementation Consultant (Sin confirmar)
  - `QA-001`: OSITRAN — Practicante preprofesional de Sistemas (Histórico)

### 6.2. Estado de la Bandeja Staging Local (`inbox.local.json`)
- **Total de candidatos en staging:** 12
- **Candidatos promovidos a catálogo:** 6 (CookUnity `8039990003` como `OP-005` y los 5 de Canonical como `OP-006` a `OP-010`), con nota editorial documentando su promoción canónica y preservados para trazabilidad histórica.
- **Candidatos descartados formalmente:** 6 (CookUnity soporte por requerir >4 años exp; 4 Wikimedia por restricciones de país y nivel senior; 1 Deliverect por presencialidad en Países Bajos).
- **Validación de staging:** 0 errores, todas las evidencias en estado `ALL_FRESH`.

---

## 7. Pruebas y Validaciones Técnicas Ejecutadas

Se ejecutó la suite completa de aseguramiento de calidad, verificando la ausencia total de regresiones:

```powershell
# 1. Construcción determinista del catálogo
python scripts/build_catalog.py --write
# Resultado: Catálogo generado explícitamente: 11 registros desde data\opportunities.seed.json.

# 2. Comprobación de sincronía entre semilla y snapshot
python scripts/build_catalog.py --check
# Resultado: Catálogo válido: 11 registros; snapshot coincide con la fuente canónica.

# 3. Validación de calidad del catálogo (Schema 2)
python scripts/validate_catalog.py
# Resultado: Válido: 11 fichas; modo=publicación no vacía; fecha Lima=2026-11-21.

# 4. Validación de la bandeja staging local y evidencias
python scripts/validate_candidates.py data/candidates/inbox.local.json --verify-evidence
# Resultado: Bandeja local válida: 12 candidatos; 0 errores; todas las evidencias ALL_FRESH.

# 5. Deduplicación determinista
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
# Resultado: 0 duplicados exactos, 0 colisiones de ID, 0 duplicados por firma.

# 6. Suite completa de pruebas unitarias Python (193 tests)
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 2.266s - OK (100% aprobadas).

# 7. Suite completa de pruebas E2E Playwright (14 escenarios Desktop y Mobile)
npx playwright test
# Resultado: 14 passed (22.7s) - OK (100% aprobadas).
```

---

## 8. Hashes Criptográficos de Verificación de Integridad

| Archivo | Hash SHA-256 | Estado |
|---|---|---|
| `data/opportunities.seed.json` | `789a5fe4777a596a031089f48885a5d492c401fcf01df1f5ec56b6df490de61c` | **ACTUALIZADO (11 registros)** |
| `data/opportunities.json` | `a6ccb384f232af9a3e05bfce4807691c270b23eba37978e3a69aee06802e9e2c` | **ACTUALIZADO (Snapshot coincidente)** |
| `collector/sources.json` | `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` | **100% INALTERADO (Protegido)** |

---

## 9. Archivos Modificados Durante el Bloque

- `data/opportunities.seed.json`: Incorporación de las 5 oportunidades reales `OP-006` a `OP-010`.
- `data/opportunities.json`: Snapshot de publicación generado por `build_catalog.py --write`.
- `data/candidates/inbox.local.json`: Actualización de notas editoriales registrando la promoción canónica.
- `tests/test_local_server_catalog.py`: Ajuste de aserción de métrica de oportunidades activas (de 1 a 6).
- `tests/e2e/catalog.spec.cjs`: Actualización de expectativas de conteo en pruebas E2E (6 activas, 11 con ejemplos, 8 remotas, selector directo `[data-open="OP-005"]`).
- `docs/audits/r3-alpha-promotion-01-private-catalog-2026-11-21.md`: Creación del presente informe.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Registro del bloque `R3-ALPHA-PROMOTION-01`.

---

## 10. Conclusiones y Estado del Proyecto

1. **Cuello de botella de contenido superado:** La Alpha privada cuenta ahora con **6 oportunidades reales activas y verificadas**, permitiendo evaluar una oferta diversa y representativa de Ingeniería de Sistemas (Desarrollo, Sistemas Operativos, Kernel Linux, Cloud/Python, Soporte TI y Datos/ERP).
2. **Gobernanza y seguridad preservadas:** Cero dependencias externas agregadas, cero alteraciones en `sources.json`, cero despliegues en GitHub Pages y cero commits o pushes no autorizados.
3. **Líneas de investigación formal y fases posteriores:** R3-02 formal permanece `NOT_STARTED / PENDING_HUMAN`, R3-03 a R3-05 y R4 continúan `BLOCKED`, y R5 permanece `APLAZADA`.
