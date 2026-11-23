# Expediente de Auditoría y Publicación R4-10
## Publicación de Convocatorias Peruanas, Incorporación de Empresas Privadas y Despliegue en Producción
### Hito R4-10-PE-CATALOG-RELEASE-01 | Ruta Sistemas

- **Fecha de ejecución:** 2026-11-23
- **Rama de trabajo:** `integration/r1-02c`
- **Responsables técnicos:** Principal Software Architect, Senior Software Engineer, Technical Product Manager, OSS Integration Specialist, Release Engineer.
- **Repositorio canónico:** `https://github.com/Blueisazul/WebRutaSistemas`
- **Despliegue público:** `https://blueisazul.github.io/WebRutaSistemas/`

---

## 1. Contexto, Identidad y Autorización Expresa

En el bloque R4-09 (`R4-09-PE-SOURCES-01`), Ruta Sistemas incorporó conectores nativos y políticas para fuentes del Estado peruano (OSITRAN y Defensoría del Pueblo) y portales universitarios (UTP HiringRoom Campus), ingresando 10 candidatos peruanos a staging con cero dependencias externas.

Para este bloque **R4-10-PE-CATALOG-RELEASE-01**, el propietario del proyecto emitió autorización expresa para:
1. Revalidar en tiempo real los 10 candidatos peruanos capturados en R4-09 contra las fuentes oficiales.
2. Promover al catálogo público todas las oportunidades que continúen vigentes y cumplan el contrato editorial y las reglas de publicación.
3. Investigar e incorporar empresas privadas de tecnología con operaciones directas en el Perú para asegurar una oferta diversificada, de calidad y continuamente disponible para estudiantes y profesionales de Ingeniería de Sistemas.
4. Ejecutar las pruebas unitarias y de extremo a extremo, consolidar el artefacto de GitHub Pages, realizar el merge a `main` y desplegar a producción sin requerir aprobaciones intermedias adicionales, siempre que se satisfagan al 100% los controles de calidad y el principio *fail-closed*.

---

## 2. Revalidación Exhaustiva de Candidatos Peruanos de R4-09

Se realizó la revalidación en vivo de los 10 candidatos peruanos capturados en R4-09 contra las plataformas oficiales del Estado peruano:

### 2.1 OSITRAN (Organismo Supervisor de la Inversión en Infraestructura de Transporte de Uso Público)
- **CP 029-2026** (*Practicantes Profesionales de Tecnologías de la Información - Sistemas / Software / Informática*): Verificado en portal oficial `oportunidadlaboral.ositran.gob.pe`. Se constató la publicación del "Acta de Resultados Finales y Cuadro de Méritos" de fecha 20 de noviembre de 2026. Proceso concluido.
- **CP 027-2026** (*Practicante Preprofesional de Sistemas e Informática*): Se constató la publicación de resultados finales con postulantes seleccionados. Proceso concluido.
- **CP 026-2026** (*Practicante Profesional de Sistemas e Informática*): Se constató la publicación de resultados de evaluación curricular y entrevista final. Proceso concluido.

### 2.2 Defensoría del Pueblo (Convocatorias CAS)
- **CAS 185-2026-DP**, **CAS 118-2026-DP**, **CAS 116-2026-DP** (*Analistas en Desarrollo de Sistemas*): Verificadas en `defensoria.gob.pe/convocatorias/convocatorias-cas.php` y aplicativo `CasOnline`. Todas cuentan con actas de resultado final publicadas y ganadores suscritos.
- **CAS 117-2026-DP** (*Analista en Redes*): Proceso cerrado con cuadro de mérito final publicado.
- **CAS 21-2026-DP**, **CAS 20-2026-DP** (*Especialistas en Arquitectura de Software e Interoperabilidad*): Procesos concluidos.
- **CAS 17-2026-DP** (*Analista de Datos*): Proceso concluido con resultado final publicado.

### 2.3 Aplicación Estricta de la Salvaguarda Fail-Closed
Bajo la arquitectura de Ruta Sistemas y el contrato de calidad (`catalog_quality.py` y `revalidation.py`), **ninguna oportunidad cuyo proceso de postulación se encuentre concluido o cerrado puede ser publicada en el catálogo activo**. 

En consecuencia:
- Los 10 candidatos de R4-09 fueron actualizados en la bandeja local (`data/candidates/inbox.local.json`) a estado editorial `"rejected"`, con estatus de ciclo de vida `"CLOSED"`, marca de revalidación `2026-11-23T08:35:18-05:00` y nota de auditoría explicable.
- Cero candidatos cerrados del Estado fueron trasladados al catálogo canónico.

---

## 3. Prospección e Integración de Empresa Privada Tecnológica en Perú

Para asegurar oportunidades reales, vigentes y de calidad en el Perú, se auditó el ecosistema empresarial tecnológico:
- **Evaluación de empresas locales:** Culqi, Stefanini, BCP, Interbank, Yape, Encora, SumUp, FeverUp, Cloudbeds, BTG Pactual.
- **Hallazgo clave: Encora Perú (`encora10`):**
  - **Identidad corporativa:** Encora (fusión y evolución de Avantica Technologies en Lima) es una de las mayores firmas globales especializadas en ingeniería de software, arquitectura en la nube, calidad y ciencia de datos, con centro de ingeniería principal en Lima (Torre Prisma, Av. Antonio Miró Quesada 425, Magdalena del Mar).
  - **ATS oficial:** Opera mediante Greenhouse Job Board API oficial pública keyless (`https://boards-api.greenhouse.io/v1/boards/encora10/jobs`).
  - **Métricas de cobertura:** 342 vacantes globales evaluadas, **118 vacantes localizadas en Perú**, de las cuales **90 vacantes corresponden a Ingeniería de Sistemas y Computación** en modalidades presencial, híbrida y remota nacional.
  - **Configuración de política:** Se registró `greenhouse-encora` en `collector/sources.json` con conector nativo `greenhouse-job-board`, `decision: "approved"`, `boardToken: "encora10"`, `allowedHosts: ["boards-api.greenhouse.io", "job-boards.greenhouse.io", "encora.com"]`.

---

## 4. Ingesta a Staging y Promoción Controlada al Catálogo Canónico

### 4.1 Ingesta a Staging
Se ejecutó la adquisición contra el endpoint en vivo de Encora, incorporando los 90 candidatos peruanos a `data/candidates/inbox.local.json` bajo Candidate Schema 2.
El inventario de staging creció de 164 a **254 candidatos**.

### 4.2 Selección y Promoción de 13 Oportunidades Verificadas Activas
Siguiendo las directrices editoriales de Ruta Sistemas (priorización formativa para estudiantes y egresados de Sistemas en Perú), se seleccionaron 13 convocatorias activas para promoción directa al catálogo canónico (`data/opportunities.seed.json`), asignando los identificadores correlativos `OP-099` hasta `OP-111`:

1. **`OP-099` | Encora | Practicante PreProfesional para IT Support/ Helpdesk**
   - Nivel: *Estudiante* | Tipo: *Práctica preprofesional* | Modalidad: *Presencial* (Torre Prisma, Magdalena del Mar, Lima).
   - Jornada: 30 horas semanales según ley de modalidades formativas laborales del Perú.
2. **`OP-100` | Encora | Desarrollador Backend Java Mid**
   - Nivel: *Egresado / bachiller* | Modalidad: *Híbrido* (Lima, asistencia presencial 2-3 días).
3. **`OP-101` | Encora | Desarrollador Backend Java Semisenior**
   - Nivel: *Egresado / bachiller* | Modalidad: *Híbrido* (Lima).
4. **`OP-102` | Encora | Desarrollador iOS Semi Senior**
   - Nivel: *Egresado / bachiller* | Modalidad: *Híbrido* (Lima).
5. **`OP-103` | Encora | Desarrollador Java con Azure Semi Senior**
   - Nivel: *Egresado / bachiller* | Modalidad: *Híbrido* (Lima).
6. **`OP-104` | Encora | Mid Data Engineer**
   - Nivel: *Egresado / bachiller* | Familia: *Analítica y datos* | Modalidad: *Híbrido* (Lima).
7. **`OP-105` | Encora | Mid QA Functional Engineer**
   - Nivel: *Egresado / bachiller* | Familia: *Desarrollo y QA* | Modalidad: *Híbrido* (Lima).
8. **`OP-106` | Encora | Mid React Native Developer**
   - Nivel: *Egresado / bachiller* | Familia: *Desarrollo y QA* | Modalidad: *Híbrido* (Lima).
9. **`OP-107` | Encora | QA Engineer**
   - Nivel: *Egresado / bachiller* | Modalidad: *Remoto* (Remoto nacional en Perú).
10. **`OP-108` | Encora | Mobile Developer (Android & iOS)**
    - Nivel: *Egresado / bachiller* | Modalidad: *Remoto* (Remoto nacional en Perú).
11. **`OP-109` | Encora | Business Analyst (Automatización de Procesos - Power Platform)**
    - Nivel: *Egresado / bachiller* | Familia: *Sistemas empresariales* | Modalidad: *Híbrido* (Lima).
12. **`OP-110` | Encora | Data Governance Analyst**
    - Nivel: *Egresado / bachiller* | Familia: *Analítica y datos* | Modalidad: *Híbrido* (Lima).
13. **`OP-111` | Encora | Mid Java Backend Developer**
    - Nivel: *Egresado / bachiller* | Familia: *Desarrollo y QA* | Modalidad: *Híbrido* (Lima).

Cada ficha cuenta con trazabilidad total en `verificationEvidence`, `editorialDecision` y 14 registros específicos en `fieldEvidence`.

---

## 5. Balance y Métricas del Catálogo y Staging

| Componente | Estado Anterior (R4-09) | Estado Posterior (R4-10) | Variación Neta |
|---|:---:|:---:|:---:|
| **Fichas totales en catálogo** | 99 | 112 | +13 fichas |
| **Oportunidades activas en catálogo** | 94 | 107 | +13 activas (+13.8%) |
| **Oportunidades históricas demostrativas** | 5 | 5 | Inalteradas (0) |
| **Oportunidades peruanas activas en catálogo** | 0 | 13 | +13 (+∞%) |
| **Candidatos en bandeja de staging (`inbox.local.json`)** | 164 | 254 | +90 candidatos (+54.9%) |
| **Candidatos evaluados/cerrados en staging** | 0 | 10 | +10 (`CLOSED` / `rejected`) |
| **Candidatos aprobados para catálogo en staging** | 84 | 97 | +13 (`approved_for_catalog`) |
| **Candidatos en revisión pendiente en staging** | 70 | 147 | +77 (`pending_review`) |
| **Fuentes aprobadas en `sources.json`** | 8 | 9 | +1 (`greenhouse-encora`) |

---

## 6. Aseguramiento de Calidad y Resultados de Validación

1. **Pruebas unitarias de Python:**
   - Comando: `python -m unittest discover -s tests -p "test_*.py"`
   - Resultado: **232 pruebas aprobadas** (0 fallos, 0 errores, 100% éxito).
2. **Pruebas de Extremo a Extremo (Playwright E2E):**
   - Comando: `npx playwright test`
   - Cobertura: 45 pruebas en Chromium, Mobile (Pixel 5) y Narrow viewport (320x568).
   - Accesibilidad: Cero violaciones críticas o serias en axe-core (WCAG 2.1 AA).
   - Resultado: **45 pruebas aprobadas** (100% éxito).
3. **Validación de Esquema y Calidad de Catálogo:**
   - Comando: `python scripts/validate_catalog.py`
   - Resultado: **Válido: 112 fichas; modo=publicación no vacía; fecha Lima=2026-11-23**.
4. **Validación de Candidatos en Staging:**
   - Comando: `python scripts/validate_candidates.py`
   - Resultado: **Bandeja local válida: 254 candidatos; no se modificó ni se publicó el catálogo**.
5. **Artefacto de Producción (GitHub Pages):**
   - Comando: `python scripts/pages_artifact.py`
   - Resultado: **Artefacto Pages preparado y validado: `dist/`** (paridad binaria y cero dependencias remotas no autorizadas).

---

## 7. Dictamen Final y Release

El bloque **R4-10-PE-CATALOG-RELEASE-01** queda formalmente dictaminado como **COMPLETADO SATISFACTORIAMENTE (`DONE`)**.

Ruta Sistemas cuenta ahora con presencia activa y verificada de oportunidades de ingeniería en el mercado peruano, garantizando el cumplimiento irrestricto de las reglas editoriales, rigor criptográfico de datos y la continuidad operativa del producto.
