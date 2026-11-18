# Informe de Revisión y Preparación Operativa del Trabajo de Campo R3-02
**Auditoría de Gobernanza, Instrumentos de Investigación y Verificación de Integridad**

- **Fecha de auditoría:** 2026-11-18
- **Fase del Proyecto:** R3 — Validación del producto (Subfase R3-02)
- **Veredicto de Preparación Operativa:** **`A — PREPARACIÓN OPERATIVA CONFIRMADA`**
- **Estado Empírico del Trabajo de Campo:** **`NOT_STARTED`** *(Cero sesiones ejecutadas; cero participantes ficticios)*
- **Entorno de Producción en Vivo:** [https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/) (commit `28b7a9e`)
- **Rama de Integración Local:** `integration/r1-02c`

---

## 1. Estado Inicial y Mandato del Bloque

Tras el cierre de R3-01 (diseño del protocolo y línea base UX), se abrió el bloque **R3-02** con la misión de habilitar las condiciones objetivas para que el equipo humano ejecute pruebas de usabilidad con 5 a 8 participantes reales en Perú.

Conforme a las directrices de gobernanza de Ruta Sistemas, **ningún agente de IA está autorizado a simular entrevistas, inventar usuarios ni completar plantillas con datos ficticios**. Por ende, la labor de este bloque consistió en auditar la coherencia documental, subsanar vacíos operativos en los materiales de campo, estandarizar la captura de métricas y verificar que los controles éticos y de QA impidan sesgos antes de iniciar las entrevistas humanas.

---

## 2. Documentos Inspeccionados y Alineamiento Metodológico

Se auditaron y cotejaron los siguientes documentos rectores del repositorio:

1. **Documento Rector de Arquitectura:** [`docs/architecture/r0-decisiones-y-alcance-2026-11-12.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/architecture/r0-decisiones-y-alcance-2026-11-12.md).
2. **Línea Base UX de Producción:** [`docs/research/r3-01-ux-baseline-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-ux-baseline-2026-11-18.md).
3. **Protocolo Rector de Investigación:** [`docs/research/r3-01-user-research-protocol-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-user-research-protocol-2026-11-18.md).
4. **Plantilla Maestra de Usabilidad:** [`docs/research/r3-01-usability-test-template-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-usability-test-template-2026-11-18.md).
5. **Matriz de Hallazgos y Priorización:** [`docs/research/r3-01-findings-template-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-01-findings-template-2026-11-18.md).
6. **Auditoría Previa de Preparación:** [`docs/audits/r3-01-research-readiness-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/audits/r3-01-research-readiness-2026-11-18.md).
7. **Cuaderno de Campo y Reclutamiento:** [`docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md).
8. **Repositorio de Sesiones Individuales:** [`docs/research/sessions/README.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/README.md) y plantillas [`P01.md` a `P08.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/).

---

## 3. Inconsistencias Detectadas y Resueltas

Durante la auditoría documental se identificaron tres discrepancias menores de estandarización, las cuales fueron subsanadas sin alterar el alcance aprobado:

| Inconsistencia Detectada | Impacto | Acción Correctiva Implementada |
|---|---|---|
| **Dispersión en clasificación de tareas:** Las plantillas usaban texto libre en español (`Éxito sin ayuda / Éxito con ayuda / Fracaso`) en lugar del estándar formal del protocolo. | Dificultad para agregación automatizada en R3-03. | Se estandarizó el enum oficial: `SUCCESS_WITHOUT_HELP`, `SUCCESS_WITH_HELP`, `ABANDONED`, `NOT_EXECUTED` en la plantilla maestra y en las 8 plantillas de sesión. |
| **Ausencia de registro explícito de intervenciones del moderador:** No había un campo dedicado para registrar pistas neutras brindadas por el facilitador. | Riesgo de sesgo de facilitación no detectado. | Se añadió la fila obligatoria `Intervención del Moderador` en cada tarea para documentar cualquier asistencia y evitar falsos éxitos sin ayuda. |
| **Falta de kit de comunicación estandarizado:** El cuaderno de campo contenía lineamientos generales, pero no los textos exactos de invitación por WhatsApp, correo o LinkedIn. | Riesgo de mensajes desalineados o promesas engañosas durante la convocatoria humana. | Se redactó el kit oficial en [`docs/research/r3-02-recruitment-materials-kit-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-recruitment-materials-kit-2026-11-18.md). |

---

## 4. Materiales Faltantes Preparados y Estandarizados

Para garantizar que el equipo humano cuente con todos los recursos necesarios antes de la primera llamada, se elaboraron dos herramientas operativas complementarias:

### 4.1 Kit de Materiales de Convocatoria (`r3-02-recruitment-materials-kit-2026-11-18.md`)
Contiene:
- Criterios estrictos de inclusión y exclusión por perfil.
- Mensaje breve neutral para WhatsApp / mensajería directa.
- Mensaje formal para correo electrónico y LinkedIn.
- Texto completo de consentimiento informado verbal/escrito.
- Pautas de agendamiento (bloques de 45 min con 15 min de amortiguación).
- Mensajes de confirmación previa y agradecimiento posterior.
- Cláusula expresa: **Prohibición de prometer incentivos económicos o laborales no autorizados.**

### 4.2 Guía de Campo y Moderación Paso a Paso (`r3-02-moderator-field-guide-2026-11-18.md`)
Contiene:
- Cronograma minuto a minuto de la sesión (00:00 a 45:00).
- Guion verbal exacto para las tareas A, B, C, D y E con técnica de *Pensamiento en Voz Alta*.
- Pautas de observación específicas para las **6 fricciones heurísticas previas** (`UX-B01` a `UX-B06`).
- Reglas de oro anti-inducción y preguntas neutrales de rebote (*"¿Dónde esperarías encontrarlo tú?"*).
- Cuestionario de debriefing y protocolo de volcado inmediato.

---

## 5. Verificación de las Plantillas Individuales (`P01.md` a `P08.md`)

Se auditó la totalidad de los 8 archivos de sesión en [`docs/research/sessions/`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/sessions/):
- **Estado unificado:** Todas las plantillas inician en `PENDING_EXECUTION`.
- **Asignación equilibrada de perfiles:**
  - `P01`, `P02`, `P03`: asignadas a `P-EST` (Estudiantes universitarios).
  - `P04`, `P05`, `P06`: asignadas a `P-EGR` (Egresados / Bachilleres).
  - `P07`, `P08`: asignadas a `P-JUN` (Profesionales Junior TI).
- **Estructura completa:** Cada plantilla cuenta con verificación de consentimiento, registro estructurado para las 5 tareas (métrica, tiempo, confianza 1-5, citas, fricciones, intervenciones), cuestionario de cierre y sección de rúbrica QA.
- **Cero datos supuestos:** Ningún campo de observación contiene texto simulado ni respuestas prefabricadas.

---

## 6. Revisión de Privacidad, Anonimización y Ética

Se certifica el cumplimiento de los estándares éticos del proyecto:
1. **Identificadores Únicos Disociados:** Se emplean exclusivamente las claves `P01` a `P08`.
2. **Cero Datos Sensibles:** Los instrumentos prohíben explícitamente almacenar nombres, apellidos, DNI, números de teléfono, correos personales o archivos de CV.
3. **Entorno Aislado:** Todos los registros permanecen como archivos Markdown locales en el repositorio; no se conectan a ninguna base de datos externa ni servicio SaaS de analítica.

---

## 7. Rúbrica de Control de Calidad (QA) de las Sesiones

Para que una sesión sea admitida como válida (`VALID`) y compute hacia la cuota de cierre de R3-02, debe superar la siguiente auditoría:

```
[SESIÓN EJECUTADA]
       │
       ├── 1. ¿Participante real pertenece a P-EST, P-EGR o P-JUN? ───> [NO] ──> INVALID
       │
       ├── 2. ¿Existe confirmación explícita de consentimiento? ──────> [NO] ──> INVALID
       │
       ├── 3. ¿El moderador evitó inducir o soplar respuestas? ────────> [NO] ──> INVALID
       │
       ├── 4. ¿Se ejecutaron las tareas A-E o justificó omisión? ─────> [NO] ──> INCOMPLETE
       │
       ├── 5. ¿Se registraron tiempos, confianza y citas textuales? ──> [NO] ──> INCOMPLETE
       │
       └── Si cumple los 5 criterios ─────────────────────────────────> [SÍ] ──> VALID
```

---

## 8. Estado de Participantes y Sesiones

- **Participantes contactados / agendados:** `0`
- **Sesiones ejecutadas:** `0`
- **Sesiones en estado `PENDING_EXECUTION`:** `8` (`P01` a `P08`)
- **Sesiones en estado `VALID`:** `0`
- **Estado empírico del bloque:** **`NOT_STARTED`**

---

## 9. Inventario de Archivos Creados y Modificados

```
docs/
├── architecture/
│   └── r0-decisiones-y-alcance-2026-11-12.md   (Actualizado: R3-02 operacionalmente listo; trabajo de campo NOT_STARTED)
├── audits/
│   ├── r3-02-user-sessions-2026-11-18.md       (Auditoría previa de estado de sesiones)
│   └── r3-02-fieldwork-readiness-review-2026-11-18.md (Nuevo: Este informe de preparación operativa)
└── research/
    ├── r3-01-usability-test-template-2026-11-18.md (Modificado: Estandarización de enums y rúbrica QA)
    ├── r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md (Cuaderno de campo y seguimiento de embudo)
    ├── r3-02-recruitment-materials-kit-2026-11-18.md (Nuevo: Kit oficial de mensajes de convocatoria y consentimiento)
    ├── r3-02-moderator-field-guide-2026-11-18.md (Nuevo: Guía práctica y guion de moderación paso a paso)
    └── sessions/
        ├── README.md                           (Normas de gobernanza y control)
        └── P01.md a P08.md                     (Modificados: Estandarización de enums y registro de intervenciones)
```

---

## 10. Validación Técnica del Entorno

Se ejecutaron las validaciones automatizadas del repositorio para certificar que ningún cambio documental o de pruebas haya afectado la estabilidad:

```powershell
python scripts/build_catalog.py --check
# -> Catálogo válido: 6 registros; snapshot coincide con la fuente canónica.

python scripts/validate_catalog.py
# -> Válido: 6 fichas; modo=publicación no vacía; fecha Lima=2026-11-18. (0 errores).

python -m unittest discover -s tests -p "test_*.py"
# -> Ran 193 tests in 2.305s - OK. (0 errores, 0 fallos).

node --check app.js
node tests/catalog_ui.test.cjs
# -> OK: public catalog filtering scenarios passed.
# -> OK: root/Pages paths and failed-catalog degradation scenarios passed.

git diff --check
# -> Conforme (sin conflictos de formato ni espacios espurios).
```

---

## 11. Acciones Exclusivas del Equipo Humano de Investigación

El agente de software ha completado el 100% de la instrumentación y auditoría documental autorizada. A partir de este momento, corresponden al equipo humano las siguientes acciones presenciales o remotas:

1. **Difusión:** Enviar las invitaciones a personas reales empleando las plantillas de [`docs/research/r3-02-recruitment-materials-kit-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-recruitment-materials-kit-2026-11-18.md).
2. **Agendamiento:** Confirmar fecha y hora para al menos 5 participantes (distribuidos en `P-EST`, `P-EGR` y `P-JUN`) y registrar las fechas en el cuaderno de campo.
3. **Moderación:** Conducir las sesiones sobre la versión en vivo ([https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/)) siguiendo el guion neutral de [`docs/research/r3-02-moderator-field-guide-2026-11-18.md`](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-moderator-field-guide-2026-11-18.md).
4. **Captura:** Volcar las notas y citas en las plantillas correspondientes (`P01.md` a `P08.md`).
5. **Auditoría QA:** Aplicar la rúbrica para calificar cada sesión como `VALID`.

---

## 12. Veredicto Final

### **`VEREDICTO: A — PREPARACIÓN OPERATIVA CONFIRMADA`**

Los materiales, instrumentos, guías y salvaguardas éticas están completamente listos y verificados. El equipo humano puede iniciar de inmediato la convocatoria y ejecución de las sesiones de prueba. **El estado del trabajo de campo continúa formalmente en `NOT_STARTED` hasta que existan sesiones reales ejecutadas**. Queda prohibido avanzar al análisis en **R3-03** sin evidencia humana comprobable.
