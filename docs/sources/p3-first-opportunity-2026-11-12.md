# P3 — Primer caso real: bloqueo por autorización

- **Fecha:** 2026-11-12
- **Estado:** bloqueado por dependencia externa
- **Fuente candidata revisada:** `canonical-careers`
- **Oportunidad real:** no seleccionada
- **Candidato staging:** no creado
- **Catálogo:** sin cambios

## Estado inicial

El checkout es `main` en `eb68ef67cbed45d03c88793750d6d6c59662cfec`, cinco commits
por detrás de `origin/main` (`20d20020d901aba670d8a08ba244994971bf2dfb`). Ya existían
cambios locales de P1/P2 y `canvas.js` sin seguimiento. Se conservaron sin
reconciliar ni sobrescribir.

P0/P1 dejaron vigente el flujo `seed -> snapshot -> Pages`, la bandeja local
offline y la política fail-closed. No existe `data/candidates/inbox.local.json`
en este checkout.

## Fuente y oportunidad

No existe una fuente con autorización documentada suficiente para este caso.
Canonical tiene portal corporativo, roles técnicos y política de trabajo remoto,
pero el expediente [canonical-careers-2026-11-11.md](canonical-careers-2026-11-11.md)
no demuestra derechos para conservar y republicar metadatos de vacantes. Tampoco
hay confirmación de elegibilidad para Perú, retención, atribución, retirada o
canal autorizado para confirmar cada ficha.

No se consultó una vacante individual, no se consultaron endpoints ATS, no se
hizo scraping y no se envió comunicación. En consecuencia, no existe
oportunidad real verificable ni canal de postulación que registrar.

## Flujo editorial ejecutado

- **Captura:** no realizada; crear un candidato real sin autorización habría
  sido una conservación no justificada.
- **Evidencia:** únicamente se conserva la evidencia documental de la evaluación
  de la fuente; no hay evidencia por campo de una oportunidad individual.
- **Validación:** se comprobó que la fuente permanece `pending_review`,
  deshabilitada y con presupuesto cero. La política rechaza su consulta.
- **Revisión:** no se atribuyó revisión humana de una ficha inexistente.
- **Decisión:** bloqueo externo; no `approved_for_catalog`, no rechazo de una
  oportunidad y no promoción.
- **Publicación:** no se modificaron seed, snapshot ni Pages.

## Calidad y métricas

| Métrica | Resultado |
|---|---|
| Campos factuales requeridos | No aplicable: no hubo ficha |
| Campos con evidencia aceptada | 0 |
| Campos no informados | No aplicable |
| Campos pendientes de confirmación | Autorización, retención, atribución, retirada, elegibilidad y canal individual |
| Duplicados detectados | 0 |
| Contradicciones detectadas | 0; no se seleccionó oportunidad |
| Problemas de elegibilidad | 1 bloqueo general: Perú no demostrado |
| Incidencias de postulación | 1 bloqueo general: no se verificó ficha individual |
| Solicitudes de retirada | 0 |
| Tiempo de descubrimiento/captura/revisión | No medido; no se inventan duraciones |

## Validación técnica

Se ejecutaron y aprobaron:

- `npm ci` y `npm run build:css` cuando correspondía al checkout existente;
- suite Python completa: 55 pruebas antes del test de regresión de Canonical;
- prueba adicional de política para Canonical;
- `python scripts/build_catalog.py --check`;
- `python scripts/validate_catalog.py`;
- `python scripts/validate_candidates.py data/candidates/inbox.example.json`;
- `node --check app.js`;
- `node tests/catalog_ui.test.cjs`;
- prueba del artefacto Pages;
- `git diff --check`.

Los negativos existentes cubren expiración, TTL, timestamps, evidencia por
campo, publisher separado, fuentes pendientes, duplicados, hosts no permitidos,
canal de postulación ausente/no verificable y la no promoción automática. No se
añadió un caso ficticio para representar una oportunidad remota.

## Continuidad

P3 no cumple sus criterios de aceptación porque falta autorización externa y una
ficha individual verificable. Para desbloquearlo, una persona responsable debe
obtener confirmación escrita de Canonical sobre:

1. uso público de metadatos mínimos;
2. atribución y enlaces;
3. retención, corrección y retirada;
4. consulta manual y cualquier automatización permitida;
5. URL oficial de postulación;
6. elegibilidad territorial para Perú.

Hasta entonces, el siguiente paso técnico es ninguno: no activar fuentes, no
crear staging real y no modificar el catálogo.

## Ejecución R2 — estado verificable

La ejecución R2 confirma el bloqueo de P3 y no rebaja sus criterios de salida.

### Selección corta de fuentes

| Fuente | Relevancia | Acceso observado | Consulta/retención/republicación | Decisión |
|---|---|---|---|---|
| Talento Perú / SERVIR | Alta para prácticas y empleo público en Perú | Página institucional y aplicación oficial identificadas; la consulta externa recibió 403 | No hay autorización escrita para conservar metadatos, atribuir, retirar o republicar; no hay API/feed autorizado | `pending_review`, bloqueada |
| FISI-UNMSM | Alta para perfiles de Sistemas y prácticas | Portal institucional y sección de oportunidades identificados | No está confirmado si FISI o cada empleador permite conservar y republicar avisos; no hay autorización de automatización | `pending_review`, bloqueada |
| Canonical Careers | Relevante para ingeniería y remoto | Portal corporativo y política remota identificados | Los términos no demuestran permiso de republicación pública; Perú, retención, retirada y canal individual siguen sin confirmar | `pending_review`, bloqueada |
| Greenhouse / Lever | Potencialmente útil para empleadores concretos | Plantillas de API existentes, sin empleador/token seleccionado | No existe autorización del empleador ni decisión de reutilización para un tablero concreto | Deshabilitada, no seleccionable |

La única fuente piloto propuesta para continuar la resolución humana es **Canonical Careers**, por tener portal corporativo y roles técnicos pertinentes; no es una fuente aprobada y no se consultó ninguna vacante individual. SERVIR y FISI conservan sus borradores de consulta en [seguimiento de autorización](seguimiento-autorizacion-fuentes.md). No se enviaron correos ni formularios.

### Matriz de tareas R2

| Tarea | Estado | Evidencia y bloqueo |
|---|---|---|
| RS-R2-01 Seleccionar fuente piloto | **Bloqueada** | Comparación anterior; ninguna fuente tiene autorización suficiente. Canonical queda propuesta, no aprobada. |
| RS-R2-02 Consolidar ficha editorial | **Parcial** | El contrato schema 2 y los campos requeridos están documentados en ADR-001 y `validate_candidates.py`; no se instanció una ficha real. |
| RS-R2-03 Incorporar candidatos | **Bloqueada** | `data/candidates/inbox.example.json` permanece vacío; no se creó `inbox.local.json` ni se conservaron datos sin permiso. |
| RS-R2-04 Validar duplicados | **Parcial** | El validador conserva IDs y referencias como controles; no hubo candidatos ni colisiones reales que comparar. |
| RS-R2-05 Verificar vigencia y postulación | **Bloqueada** | No se consultó una vacante individual; no existe evidencia de `application_open`, empleador confirmado ni elegibilidad desde Perú. |
| RS-R2-06 Aprobar y transferir | **Bloqueada** | No hay aprobación humana registrada; seed y snapshot no fueron modificados. |
| RS-R2-07 Generar y validar catálogo | **Parcial** | El catálogo demostrativo existente sigue validando; no se generó una ficha real ni se presentó como tal. |
| RS-R2-08 Publicar y verificar piloto | **Bloqueada** | No existe una oportunidad real aprobada; no hay URL pública nueva que comprobar. |

### Desbloqueo requerido

Una persona responsable debe enviar y obtener respuesta escrita de la fuente propuesta, confirmando por separado: consulta manual, metadatos mínimos conservables, republicación pública, atribución, retención, corrección, retirada, límites técnicos, URL canónica de postulación y elegibilidad desde Perú. Una respuesta ambigua mantiene `pending_review`; no habilita conectores ni promoción.

Cuando exista esa respuesta, el siguiente paso será revisar manualmente una sola convocatoria vigente, crear un candidato con `captureMethod: manual`, completar evidencia por campo y dejar `editorialReview.status: pending_review`. La promoción a seed seguirá requiriendo aprobación humana explícita.
