# R2-A-04 — Revisión Editorial Humana, Auditoría de Evidencia y Preparación de la Decisión de Promoción

**Proyecto:** Ruta Sistemas  
**Fase:** R2 — Flujo editorial real (Puerta de Control Editorial)  
**Fecha de informe:** 2026-11-18  
**Responsables (Roles):** Principal Software Architect, Senior Software Engineer, Technical Product Manager y Responsable de Gobernanza Editorial  
**Resultado de salida:** `RESULTADO B — RECOMENDACIÓN CON LIMITACIONES (PENDING_OWNER_DECISION)`  
**Referencias previas:** [docs/audits/r2-a-02-editorial-review-2026-11-17.md](r2-a-02-editorial-review-2026-11-17.md), [docs/audits/r2-a-03-controlled-capture-2026-11-18.md](r2-a-03-controlled-capture-2026-11-18.md)

---

## 1. Objetivo y Alcance

El bloque **R2-A-04** actúa como una **puerta de control editorial y técnica infranqueable** previa a cualquier consideración de paso a catálogo canónico. Su propósito central es:
1. Auditar con rigor pericial la consistencia temporal, cronológica y documental de la evidencia generada en `R2-A-03`.
2. Verificar nuevamente en tiempo real la publicación oficial de la vacante principal (*CookUnity — Supply Chain Analyst*, ID `8039990003`).
3. Evaluar con total honestidad intelectual si esta vacante representa adecuadamente la visión fundacional de Ruta Sistemas (apoyo a estudiantes y perfiles iniciales de Ingeniería de Sistemas para encontrar prácticas formativas y primeras oportunidades laborales).
4. Preparar un expediente transparente y estructurado para que el propietario del proyecto pueda emitir una decisión formal de aprobación o postergación, sin realizar modificaciones al catálogo canónico (`data/opportunities.seed.json`, `data/opportunities.json`).

---

## 2. Evidencia Documental Consultada

- **Cierre R2-A-02:** Revisión editorial de 8 candidatos y selección de oportunidades pre-cualificadas.
- **Cierre y Auditoría R2-A-03 (`docs/audits/r2-a-03-controlled-capture-2026-11-18.md`):** Recaptura focalizada sobre CookUnity `8039990003`.
- **Roadmap rector (`docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`):** Definición del alcance del MVP y exclusión de promociones automáticas.
- **Seguimiento de fuentes (`docs/sources/seguimiento-autorizacion-fuentes.md`):** Condiciones de uso y estado de fuentes documentadas.
- **Bandeja de staging (`data/candidates/inbox.local.json`):** Registro de candidatos bajo Candidate Schema 2.

---

## 3. Auditoría Pericial de la Evidencia Temporal de R2-A-03

Se investigó a fondo la aparente discrepancia cronológica advertida en el cierre de R2-A-03:

### 3.1. Diagnóstico de Entorno y Zonas Horarias
- **Zona horaria del sistema operativo:** `Hora estándar del Pacífico de Sudamérica` (`UTC-5`, correspondiente a Lima, Perú).
- **Hora local del host al ejecutar R2-A-03:** `2026-11-17T21:24:51-05:00`.
- **Hora UTC equivalente en ese instante:** `2026-11-18T02:24:51+00:00` (`02:24 UTC` del día `18 de noviembre de 2026`).
- **Nomenclatura del archivo de informe:** El nombre del archivo (`docs/audits/r2-a-03-controlled-capture-2026-11-18.md`) fue determinado de forma literal por la especificación de la instrucción recibida en la sección 10 de R2-A-03 (`Crea: docs/audits/r2-a-03-controlled-capture-2026-11-18.md`), la cual adoptó la fecha civil UTC (`2026-11-18`).
- **Marcas temporales del candidato (`capturedAt` y `observedAt`):** Fueron emitidas mediante `datetime.now(timezone(timedelta(hours=-5)))` produciendo exactamente la hora civil local del host (`2026-11-17T21:24:51-05:00`).

### 3.2. Conclusión de Integridad Temporal
No existió inyección manual ni falsificación de fechas futuras. La aparente discrepancia se debió a la coexistencia entre la convención de fecha civil UTC (`2026-11-18`) requerida para el nombre del entregable y la marca horaria local de Lima (`2026-11-17T21:24`) generada por el runtime.

Para despejar toda ambigüedad, en este bloque **R2-A-04** se ejecutó una nueva consulta de verificación en tiempo real a las `2026-11-17T22:28:37-05:00`, renovando las evidencias con estricta trazabilidad local.

---

## 4. Verificación Actual de la Oportunidad (CookUnity `8039990003`)

Se consultaron nuevamente en vivo (2026-11-17T22:28:37-05:00) los endpoints oficiales:
1. **Greenhouse Job Board API (`https://boards-api.greenhouse.io/v1/boards/cookunity/jobs/8039990003`):**
   - Estado: **`HTTP 200 OK`**.
   - Identificador confirmado: `8039990003`.
   - Título confirmado: `Supply Chain Analyst`.
   - Empleador confirmado: `CookUnity`.
   - Fecha de primera publicación: `2026-10-21T13:07:44-04:00`.
   - Fecha límite de postulación: `application_deadline: null` (`DEADLINE_UNKNOWN`).
   - Ubicación: `Lima, Lima Province, Peru` (`offices: [{'id': 4077215003, 'name': 'Lima'}]`).
2. **Página Oficial de Carreras (`https://careers.cookunity.com/jobs/8039990003`):**
   - Estado: **`HTTP 200 OK`** (URL canónica activa).
   - Microdatos Schema.org: `JobPosting` JSON-LD validado con `datePosted: 2026-10-21T13:07:44-04:00`.
   - Canal de postulación: Directo e interactivo, sin bloqueos técnicos.

La vacante continúa **100% activa, vigente y comprobada**.

---

## 5. Evaluación de Pertinencia para Ruta Sistemas

Este es el núcleo de la auditoría editorial. No debemos permitir que una vacante ingrese al catálogo si compromete la identidad del producto:

### 5.1. Público Elegible Real vs Ideal de la Plataforma
- **¿Es para estudiantes universitarios que cursan ciclo regular?** **NO**. El puesto es a tiempo completo (`full-time`). Un estudiante con carga académica diurna no podrá compatibilizarlo salvo horarios nocturnos o encontrarse en fase de tesis.
- **¿Es una práctica preprofesional?** **NO**. No está articulada bajo el convenio de modalidad formativa laboral (Ley 28518) de 30 horas semanales.
- **¿Es para egresados / bachilleres?** **SÍ**. Admite explícitamente *"Bachelor's degree in Business, Supply Chain, Engineering, or other related"*, cubriendo a bachilleres de Ingeniería de Sistemas.
- **¿Es de nivel inicial absoluto (0 experiencia)?** **PARCIALMENTE NO**. Exige *"1+ years of previous experience in a Supply Chain"*, lo que la sitúa como una posición *junior con experiencia previa* (por ejemplo, egresados que ya completaron 1 año de prácticas preprofesionales).

### 5.2. Familia Profesional y Clasificación
- **¿Es un puesto de desarrollo de software?** **ROTUNDAMENTE NO**.
- **Familia profesional exacta:** **`Datos y analítica / Sistemas de información empresarial (ERP/MRP)`**.
- **Herramientas de trabajo:** SQL relacional (extracción, joins, agregaciones y validación de calidad de datos), modelado en Google Sheets avanzado y plataformas ERP/MRP para operaciones de cadena de suministro.
- **Veredicto:** Es pertinente para la rama de Ingeniería de Sistemas orientada a bases de datos, consultoría de sistemas empresariales y analítica de datos, pero **no debe etiquetarse bajo ningún concepto como Ingeniería de Software ni Programación**.

### 5.3. Calidad de las Condiciones Laborales
- **Remuneración:** `NO_INFORMADO`. La fuente pública no transparenta banda salarial.
- **Tipo de contrato:** Tiempo completo (`Full-Time`), relación laboral directa.
- **Modalidad:** `NO_INFORMADO` en los metadatos estructurados. Tiene sede física en Lima; podría ser presencial u operativa híbrida.
- **Requisitos de idioma:** Nivel de inglés profesional obligatorio (reporta a HQ en Nueva York).
- **Potencial formativo:** Alto en el ámbito de datos operacionales y optimización de flujos con inteligencia artificial en operaciones reales.

---

## 6. Riesgo de Desalineación y Comparación con la Visión Original

| Dimensión | Visión Original Ruta Sistemas | Oportunidad CookUnity (`8039990003`) | Oportunidad Canonical en Reserva (`8379825`) |
|---|---|---|---|
| **Público Objetivo** | Estudiantes universitarios y recién egresados de Sistemas | Egresados/bachilleres con 1+ año de experiencia previa | Recién graduados (cohortes 2026/2027) sin experiencia previa |
| **Rol Técnico** | Desarrollo, QA, Datos, Infraestructura, TI | Analista de Operaciones / Datos SQL / ERP | Ingeniero de Software de Código Abierto / Linux Kernel |
| **Dedicación** | Prácticas (formativas) o primer empleo junior | Empleo tiempo completo regular | Empleo tiempo completo formativo con mentoría |
| **Ubicación** | Perú y remoto con elegibilidad explícita | Local físico (`Lima, Perú`) | Remoto mundial con elegibilidad AMER/Perú |
| **Gobernanza de Fuente** | Uso de datos factuales mínimos de APIs públicas | Greenhouse API pública (`READY_WITH_LIMITS`) | Consulta pendiente de términos de uso de Canonical |

### Análisis de Percepción del Usuario:
Si Ruta Sistemas lanza su catálogo presentando como **única primera oportunidad real** un puesto titulado *"Supply Chain Analyst"*, existe el riesgo de que el público estudiantil perciba que la plataforma no se enfoca en desarrollo de software, o que carece de ofertas de prácticas preprofesionales para quienes aún estudian.

Por otro lado, su gran fortaleza es ser una oportunidad **física en Lima, Perú**, en una empresa tecnológica global, con aplicación directa de bases de datos SQL y gestión de sistemas de información.

---

## 7. Decisión Editorial Estructurada

Se dictamina la clasificación:

### **`APPROVE_WITH_LIMITATIONS` (Recomendación con Limitaciones)**

**Fundamento:**
La vacante es legítima, real, vigente, con evidencia de procedencia impecable y apta para bachilleres de Ingeniería de Sistemas con vocación analítica. Sin embargo, no satisface la demanda de estudiantes que buscan prácticas preprofesionales ni de quienes buscan desarrollo de software nativo.

Por tanto, **no se recomienda su promoción directa e incondicional**, sino que se deja la decisión en manos del propietario del proyecto bajo dos opciones estratégicas bien definidas.

---

## 8. Ficha Consolidada para el Propietario del Proyecto

```yaml
Ficha de Decisión Editorial — Ruta Sistemas:
--------------------------------------------
ID Candidato: CAND-greenhouse-public-job-board-template-8039990003
Empleador: CookUnity
Puesto: Supply Chain Analyst
Área / Familia Profesional: Analítica de Datos / Sistemas de Información Empresarial (ERP/MRP)
Nivel Real: Junior con experiencia (1+ años)
Público al que se dirige: Egresados y bachilleres de Ingeniería de Sistemas (no estudiantes activos en ciclo regular)
Ubicación: Lima, Lima Province, Peru (PERU_LOCAL)
Modalidad: Presencial / Híbrida en sede Lima (No declarada explícitamente en API; mode=null)
Tipo de Contrato: Tiempo completo (Full-Time)
Requisitos Académicos: Bachiller o egresado en Ingeniería (Sistemas, Industrial o afines)
Requisitos Técnicos: SQL (consultas, joins, agregaciones, validación), Google Sheets avanzado, ERP/MRP, Inglés fluido
Remuneración: No informada en la publicación pública
Fecha de Publicación Original: 2026-10-21
Fecha Límite: No informada (DEADLINE_UNKNOWN)
Estado de Vigencia: Confirmada activa y abierta (HTTP 200 en API y portal oficial al 2026-11-17T22:28:37-05:00)
URL Oficial: https://careers.cookunity.com/jobs/8039990003
URL Postulación ATS: https://job-boards.greenhouse.io/cookunity/jobs/8039990003
Evidencias Asociadas: 7 evidencias verificadas (ALL_FRESH)
Recomendación Técnica: APPROVE_WITH_LIMITATIONS
```

---

## 9. Pruebas Técnicas Ejecutadas y Resultados

```powershell
# 1. Validación de candidatos Candidate Schema 2 (8 candidatos en staging)
python scripts/validate_candidates.py data/candidates/inbox.local.json
# Resultado: Bandeja local válida (0 errores).

# 2. Análisis de deduplicación determinista
python scripts/editorial_cli.py deduplicate data/candidates/inbox.local.json
# Resultado: 0 colisiones, 0 duplicados.

# 3. Inspección editorial y frescura de evidencias
python scripts/editorial_cli.py inspect data/candidates/inbox.local.json --verify-evidence
# Resultado: 8 ALL_FRESH, 8 pending_review.

# 4. Pruebas unitarias e integración Python (193 tests)
python -m unittest discover -s tests -p "test_*.py"
# Resultado: Ran 193 tests in 2.386s - OK.

# 5. Pruebas E2E Playwright (8 tests en Desktop y Mobile)
npx playwright test
# Resultado: 8 passed (6.6s).

# 6. Verificación de catálogo canónico y snapshot
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
# Resultado: Catálogo válido; snapshot coincide exactamente con la fuente canónica.

# 7. Comprobación de formato Git
git diff --check
# Resultado: Limpio (sin errores).
```

---

## 10. Archivos Modificados e Integridad Canónica

### Modificados dentro del alcance autorizado:
- `data/candidates/inbox.local.json`: Actualizado con la última marca de verificación en vivo (2026-11-17T22:28:37-05:00), manteniendo todas las evidencias `ALL_FRESH` (ignorado por `.gitignore`).
- `docs/audits/r2-a-04-editorial-decision-2026-11-18.md`: Creación del presente informe de decisión editorial.
- `docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`: Actualización del hito R2 en la tabla rectora.
- `docs/sources/seguimiento-autorizacion-fuentes.md`: Actualización del estado de revisión de CookUnity.

### Archivos canónicos estrictamente protegidos (0 modificaciones, hashes intactos):
- `data/opportunities.seed.json`: `772f576e06269b8f41191f34aed32a8ce9894729bc858538ff7bf630eaf9c5d6` (**Inalterado**)
- `data/opportunities.json`: `13f91b9090b2377f0e8b770d7f513ef767ce9904a4b2ebb72d56f868bbf80b05` (**Inalterado**)
- `collector/sources.json`: `ae5ba4d314a450db9118c3ad3a98a6fbe261542a74bd0ec7a623aa7f66b0a124` (**Inalterado**)
- **Dependencias agregadas:** **0** (sin cambios en `package.json` ni en el entorno Python).

---

## 11. Decisión que Corresponde Exclusivamente al Propietario

El asistente ha completado toda la auditoría técnica y editorial. Para proceder con el siguiente paso, se somete a la decisión del propietario del proyecto elegir entre dos alternativas estratégicas:

- **Estrategia A (Aprobar CookUnity con limitaciones):** Autorizar la promoción de *CookUnity — Supply Chain Analyst* a `data/opportunities.seed.json` para convertirse en la primera oportunidad real en producción, catalogándola claramente bajo la familia profesional de **Datos y Sistemas Empresariales**, explicitando que requiere 1+ años de experiencia.
- **Estrategia B (Postergar y buscar rol puro de desarrollo o prácticas):** Mantener a CookUnity en staging en reserva, resolver formalmente la consulta sobre Canonical (*Graduate Software Engineer*) o investigar una fuente local con vacantes de prácticas preprofesionales en desarrollo de software (ej. convenios universitarios o portales oficiales con convenios formativos).

---

## 12. Siguiente Bloque Recomendado

- **Si el propietario aprueba la Estrategia A:** Proceder con **`R2-A-05 — Promoción a Semilla Canónica, Compilación y Publicación`**.
- **Si el propietario elige la Estrategia B:** Proceder con la gestión documental de Canonical o un ciclo focalizado de descubrimiento de convocatorias formativas preprofesionales en Lima.
