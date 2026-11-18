# Repositorio Consolidado y Matriz de Hallazgos R3
**Estructura de Análisis y Priorización Empírica de Usabilidad**

- **Fase del Proyecto:** R3 — Validación del producto
- **Documento rector:** `docs/research/r3-01-findings-template-2026-11-18.md`
- **Uso:** Consolidación de observaciones, incidentes y patrones derivados de las sesiones con usuarios (`P01` a `P08`)

---

## 1. Metodología de Consolidación y Análisis

Para evitar sesgos individuales y no convertir anécdotas aisladas en requerimientos apresurados de desarrollo, los datos de las sesiones de usabilidad se analizan siguiendo un proceso riguroso:

```
[NOTAS DE SESIÓN P01..P08] 
         │
         ▼
[EXTRACCIÓN DE INCIDENTES] ──> Clasificación por Taxonomía (6 categorías)
         │
         ▼
[AGRUPACIÓN EN PATRONES]  ──> Detección de recurrencias (>1 usuario)
         │
         ▼
[CÁLCULO DE SEVERIDAD/PRIORIDAD] ──> Matriz Severidad × Frecuencia × Impacto
         │
         ▼
[HALLAZGO CONSOLIDADO (HAL-R3-XX)] ──> Recomendación técnica acotada
```

---

## 2. Taxonomía de Problemas y Reglas de Decisión

Cada observación debe encasillarse en una y solo una categoría primaria:

| Categoría | Definición | Regla de Decisión | Tratamiento en Ruta Sistemas |
|---|---|---|---|
| `[PROBLEMA_USABILIDAD]` | Falla en interacción, controles, botones, teclado, respuesta visual o navegación. | El usuario sabe qué quiere hacer, pero la interfaz se lo dificulta o impide. | Corrección técnica acotada en frontend (`app.js` / `site.css`). |
| `[PROBLEMA_CONTENIDO]` | Ambigüedad en textos, redacción confusa, tecnicismos o falta de traducción. | El usuario lee el texto, pero no comprende su significado o lo interpreta al revés. | Refactorización de microcopy y etiquetas en la UI. |
| `[PROBLEMA_ARQUITECTURA_INFO]` | Ubicación ilógica de elementos, desorden jerárquico o filtros no encontrados. | La información o control existe, pero el usuario la busca en otro lugar. | Reorganización visual y de agrupación sin añadir funcionalidades. |
| `[PROBLEMA_DATOS_INCOMPLETOS]` | Ausencia de un dato fundamental en la vacante (sueldo, horario, modalidad). | La plataforma refleja fielmente la fuente, pero el dato original no existe. | No inventar datos; mejorar la explicación de *"Lo que falta confirmar"*. |
| `[PROBLEMA_ALCANCE_PRODUCTO]` | Desalineación entre lo que la plataforma ofrece y lo que el usuario espera. | El usuario espera una bolsa masiva tradicional de empleo o empleo garantizado. | Fortalecer la comunicación de la propuesta de valor y límites del MVP. |
| `[SOLICITUD_FUNCIONALIDAD_NUEVA]` | Deseos expresados por el usuario (alertas por correo, guardar en favoritos, CV builder). | El usuario pide algo que no existe en el alcance actual. | Registrar en backlog de R3/R4; **no implementar por impulso**. |

---

## 3. Matriz de Severidad, Frecuencia y Priorización

### 3.1 Escala de Severidad (Impacto en la Tarea)
- **4 - Crítica:** Bloquea la tarea o causa un error de interpretación grave e irreversible (ej. creer que el empleo está garantizado o no poder abrir la postulación).
- **3 - Mayor:** Dificulta severamente la comprensión o causa gran retraso y frustración; requiere orientación para continuar.
- **2 - Menor:** Confusión momentánea o incomodidad superada autónomamente por el usuario.
- **1 - Cosmética:** Detalle visual o tipográfico menor sin impacto en la comprensión.

### 3.2 Frecuencia de Aparición
- **Alta:** Presente en $\ge 50\%$ de los participantes ($\ge 3$ de 5 o $\ge 4$ de 8).
- **Media:** Presente en $25\%$ a $49\%$ de los participantes ($2$ de 5 o $2-3$ de 8).
- **Baja:** Observada en un único participante ($1$ de 5 a 8).

### 3.3 Cuadrante de Priorización de Correcciones
```
                FRECUENCIA ALTA        FRECUENCIA MEDIA       FRECUENCIA BAJA
SEVERIDAD 4      [P0 - URGENTE]        [P0 - URGENTE]         [P1 - IMPORTANTE]
SEVERIDAD 3      [P1 - IMPORTANTE]     [P1 - IMPORTANTE]      [P2 - MODERADA]
SEVERIDAD 2      [P2 - MODERADA]       [P2 - MODERADA]        [P3 - MENOR]
SEVERIDAD 1      [P3 - MENOR]          [P3 - MENOR]           [P4 - DESESTIMAR]
```

---

## 4. Matriz de Síntesis por Pregunta de Investigación

Al finalizar la ronda de pruebas de R3-02, esta tabla resumirá el balance global:

| Pregunta de Investigación | Tarea Asociada | Tasa de Éxito Global (%) | Hallazgos Principales | Veredicto Empírico Preliminar |
|---|---|---|---|---|
| **1. Pertinencia para Sistemas** | Tarea A | `___%` | *(Completar tras sesiones)* | `[ ] Validado / [ ] Fricción / [ ] Bloqueado` |
| **2. Evaluación de Requisitos** | Tarea B | `___%` | *(Completar tras sesiones)* | `[ ] Validado / [ ] Fricción / [ ] Bloqueado` |
| **3. Comprensión de Estados y Vigencia** | Tarea C | `___%` | *(Completar tras sesiones)* | `[ ] Validado / [ ] Fricción / [ ] Bloqueado` |
| **4. Comparación sin Ganador Universal** | Tarea D | `___%` | *(Completar tras sesiones)* | `[ ] Validado / [ ] Fricción / [ ] Bloqueado` |
| **5. Decisión Informada y Canal Oficial** | Tarea E | `___%` | *(Completar tras sesiones)* | `[ ] Validado / [ ] Fricción / [ ] Bloqueado` |

---

## 5. Fichas de Registro de Hallazgos Consolidados (Plantilla Tipo)

*Cada patrón de comportamiento observado que califique como hallazgo debe registrarse con la siguiente estructura:*

---

### `HAL-R3-01`: [Título descriptivo del hallazgo]
- **Categoría:** `[USABILIDAD / CONTENIDO / ARQ_INFO / DATOS / ALCANCE / SOLICITUD]`
- **Severidad:** `[1 - Cosmética / 2 - Menor / 3 - Mayor / 4 - Crítica]`
- **Frecuencia:** `[X de Y participantes] (___%)` · Participantes: `[P01, P03, ...]`
- **Prioridad de Corrección:** `[P0 / P1 / P2 / P3]`
- **Pregunta Rectora Impactada:** `[1. Pertinencia / 2. Requisitos / 3. Estados / 4. Comparación / 5. Decisión]`

#### Descripción del Patrón Observado:
> Explicación detallada y neutral de lo que ocurrió en la interfaz y cómo reaccionaron los usuarios.

#### Evidencia Empírica y Citas Textuales:
- *Comportamiento registrado:* Los usuarios hicieron clic en... esperaban que...
- *Cita de P01:* *"..."*
- *Cita de P04:* *"..."*

#### Causa Raíz Identificada:
- Identificación técnica de por qué ocurre (línea de código, redacción, disposición CSS o diseño conceptual).

#### Recomendación de Acción Acotada (para R3-03 / R3-04):
- Propuesta de solución puntual que **no agregue complejidad innecesaria** ni nuevas dependencias.

---

### `HAL-R3-02`: [Título descriptivo del hallazgo]
- **Categoría:** 
- **Severidad:** 
- **Frecuencia:** 
- **Prioridad:** 
- **Pregunta Rectora Impactada:** 

*(Replicar estructura para cada hallazgo consolidado)*

---

## 6. Registro Crítico de Solicitudes de Funcionalidad Nueva

Los participantes suelen sugerir ideas durante las pruebas. Para proteger la visión minimalista y el principio de no sobre-ingeniería de Ruta Sistemas, cada solicitud debe ser evaluada críticamente antes de considerarse en el roadmap:

| Solicitud Expresada por Usuarios | Frecuencia | ¿Alineada con la Visión del MVP? | Evaluación Técnica y de Gobernanza | Decisión Editorial de R3 |
|---|---|---|---|---|
| *Ejemplo: Alertas por correo de nuevos empleos* | `[X/Y]` | `No` | Requiere backend con base de datos de usuarios, almacenamiento de emails y costos de infraestructura de correo; viola el principio de catálogo estático y privacidad sin registro. | **Desestimada para el MVP** (Ruta Sistemas es un visor neutral, no un servicio de suscripción). |
| *Ejemplo: Filtro específico por tecnologías (tags)* | `[X/Y]` | `Sí` | Puede resolverse aprovechando el campo `skills` ya existente en Schema 2 mediante filtrado en memoria en `app.js`. | **Admitida para análisis en R3-03**. |

---

## 7. Criterio de Cierre y Transferencia a R3-03

Este documento permanecerá abierto como repositorio de trabajo durante la ejecución de las sesiones de **R3-02**.

Se considerará cerrado para la toma de decisiones cuando:
1. Se hayan ejecutado y documentado el 100% de las sesiones planificadas (mínimo 5).
2. Se hayan sintetizado todos los incidentes en hallazgos consolidados.
3. El equipo editorial y de producto priorice las correcciones P0/P1 que habilitarán el bloque **R3-04 (Refactor/Fix UX Justificado)**.
