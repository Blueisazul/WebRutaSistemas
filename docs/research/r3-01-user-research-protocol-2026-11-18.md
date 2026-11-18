# Protocolo de Investigación y Pruebas de Usabilidad con Usuarios R3-01
**Evaluación Empírica del MVP de Ruta Sistemas**

- **Fecha de elaboración:** 2026-11-18
- **Fase:** R3 — Validación del producto
- **Clasificación:** `[VALIDACIÓN_CON_USUARIOS]` `[INVESTIGACIÓN_CUALITATIVA]`
- **Tipo de prueba:** Pruebas de usabilidad moderadas basadas en tareas (remotas o presenciales)
- **Tamaño de muestra sugerido:** 5 a 8 participantes

---

## 1. Objetivos y Preguntas de Investigación

### 1.1 Objetivo General
Determinar si estudiantes, egresados y profesionales iniciales de Ingeniería de Sistemas en el Perú pueden emplear Ruta Sistemas de manera autónoma para comprender, evaluar críticamente y comparar oportunidades profesionales reales y demostrativas, identificando requisitos, condiciones contractuales y procedencia para tomar decisiones fundamentadas de postulación.

### 1.2 Preguntas Rectoras de la Validación
1. **Pertinencia:** ¿Los usuarios identifican con claridad si una oportunidad laboral se adecúa a su formación, capacidades e intereses dentro del ecosistema de Sistemas?
2. **Requisitos:** ¿Pueden discernir con precisión entre los requisitos que cumplen, los que no cumplen y aquellos que demandan verificación adicional?
3. **Estados y Vigencia:** ¿Comprenden los conceptos de publicación activa, verificación del empleador, caducidad por TTL y ausencia de garantías de disponibilidad permanente?
4. **Comparación Neutral:** ¿Son capaces de comparar dos oportunidades contrastando condiciones y datos ausentes sin interpretar la interfaz como un ranking, puntaje o recomendación algorítmica universal?
5. **Decisión Informada:** ¿Identifican qué información factual mínima necesitan antes de postular y localizan el canal oficial verificado?

---

## 2. Perfil de Participantes y Criterios de Inclusión

Se define una muestra de **5 a 8 participantes** distribuidos entre tres segmentos clave del público objetivo en el Perú:

| Perfil | Descripción | Criterios de Inclusión | Cuota Piloto |
|---|---|---|---|
| **P-EST (Estudiante)** | Estudiante universitario de Ingeniería de Sistemas, Software o Computación en Perú. | Cursando entre 8vo y 10mo ciclo; en búsqueda activa de prácticas preprofesionales o primer empleo. | 2 - 3 participantes |
| **P-EGR (Egresado / Bachiller)** | Egresado o bachiller reciente (egreso en los últimos 12 meses). | Sin experiencia laboral formal significativa o con solo prácticas preprofesionales previas. | 2 - 3 participantes |
| **P-JUN (Profesional Junior)** | Profesional inicial en tecnología. | Entre 1 y 2 años de experiencia laboral formal en desarrollo, datos, soporte o sistemas. | 1 - 2 participantes |

### 2.1 Criterios de Exclusión
- Personas con más de 3 años de experiencia en la industria tecnológica.
- Integrantes del equipo de desarrollo, auditoría o colaboradores directos de Ruta Sistemas.
- Personas con formación ajena a carreras de tecnologías de la información o sistemas.

### 2.2 Limitaciones Metodológicas de la Muestra
- **Alcance cualitativo formativo:** La muestra de 5 a 8 personas está dimensionada para detectar los principales problemas de usabilidad, fricciones cognitivas y vacíos de contenido (según la curva de Nielsen-Landauer, 5 usuarios descubren el ~80% de los problemas de usabilidad).
- **No representatividad cuantitativa:** Los resultados no deben presentarse como estadísticamente representativos del universo total de estudiantes o profesionales de TI en el Perú.
- **Transparencia en conclusiones:** Las interpretaciones no deben extrapolarse cuantitativamente ni sustentar generalizaciones poblacionales sin estudios cuantitativos posteriores.

---

## 3. Guion de Moderación y Encuadre Neutral

El moderador debe mantener una postura estrictamente neutral, facilitadora y no directiva:
- No enseñar cómo usar la interfaz.
- No responder con afirmaciones sobre si algo está "bien" o "mal".
- No justificar las decisiones de diseño del equipo.
- Emplear la técnica de *Pensamiento en Voz Alta* (*Think Aloud Protocol*).

### 3.1 Guion de Bienvenida e Introducción
> *"Hola [Nombre]. Muchas gracias por participar en esta sesión. Mi nombre es [Moderador] y hoy estamos evaluando un prototipo web llamado Ruta Sistemas, diseñado para que estudiantes y profesionales de Sistemas puedan explorar y analizar ofertas de empleo con información clara.*
>
> *Quiero resaltar algo muy importante: **te estamos evaluando a la plataforma, no a ti**. No hay respuestas correctas ni incorrectas. Si algo te parece confuso, difícil de encontrar o inconsistente, es una falla de diseño de la herramienta y precisamente lo que necesitamos descubrir.*
>
> *Te voy a pedir que durante la sesión intentes pensar en voz alta: cuéntame qué estás mirando, qué intentas hacer, qué dudas te surgen y qué esperas que pase. No te preocupes por herir sentimientos; tus observaciones francas son lo más valioso.*
>
> *La sesión durará aproximadamente 30 a 45 minutos. Tomaremos notas de lo que ocurra en pantalla de manera totalmente anónima. ¿Tienes alguna pregunta antes de comenzar?"*

---

## 4. Consentimiento Informado y Protección de Datos

En estricta observancia del principio de privacidad por diseño:
1. **Sin Datos Sensibles:** No se solicitarán currículums vitae (CV), nombres completos, números de DNI, números de teléfono, credenciales de acceso ni historiales académicos específicos.
2. **Identificación Disociada:** Cada participante será identificado en los registros únicamente mediante un código alfanumérico (`P01`, `P02`, ..., `P08`) asociado a su perfil genérico (`P-EST`, `P-EGR`, `P-JUN`).
3. **Tratamiento Local y Destrucción:** Las notas y registros de observación se mantendrán en archivos locales del repositorio de investigación y no se sincronizarán con servicios de analítica ni bases de datos de terceros.
4. **Grabación Opcional:** Si se realiza grabación de audio/pantalla, requerirá consentimiento expreso y se destruirá una vez extraídos los hallazgos en la plantilla formal.

---

## 5. Diseño de Escenarios y Tareas

Las tareas se formulan como situaciones reales sin indicar qué botones pulsar ni qué filtros seleccionar.

```
+-----------------------------------------------------------------------------------+
| TAREA A: Búsqueda y Pertinencia de la Oportunidad                                 |
+-----------------------------------------------------------------------------------+
| Consigna: "Imagina que estás buscando tu próxima oportunidad laboral acorde a tu |
| perfil en Ingeniería de Sistemas. Ingresa a la página y explora las oportunidades  |
| disponibles. Encuentra un puesto que consideres relevante para alguien de tu     |
| carrera y explícame por qué crees que encaja (o no encaja) con tu formación."      |
+-----------------------------------------------------------------------------------+
```

```
+-----------------------------------------------------------------------------------+
| TAREA B: Evaluación Crítica de Requisitos y Naturaleza del Rol                   |
+-----------------------------------------------------------------------------------+
| Consigna: "Revisa la vacante de 'Supply Chain Analyst' en CookUnity. Analiza en   |
| detalle la información que presenta la plataforma y dime:                         |
| 1. ¿Qué conocimientos técnicos y herramientas se solicitan?                       |
| 2. ¿Qué nivel de experiencia previa exige el puesto?                              |
| 3. De acuerdo a tu criterio, ¿se trata de una práctica o de un empleo formal?     |
| 4. ¿Qué requisitos crees que cumples hoy y cuáles tendrías que comprobar?"        |
+-----------------------------------------------------------------------------------+
```

```
+-----------------------------------------------------------------------------------+
| TAREA C: Interpretación de Estados, Verificación y Modalidad                      |
+-----------------------------------------------------------------------------------+
| Consigna: "Observando la información de la oportunidad de CookUnity:              |
| 1. ¿Qué significa la etiqueta de estado que ves en la tarjeta?                    |
| 2. ¿Qué entiendes por la fecha de última verificación que se muestra?             |
| 3. ¿El hecho de que esté publicada garantiza que puedas postular hoy mismo y que  |
|    el puesto siga abierto?                                                        |
| 4. ¿En qué modalidad de trabajo se desempeñaría este puesto (presencial, remota,  |
|    híbrida) y de dónde obtuviste ese dato?"                                       |
+-----------------------------------------------------------------------------------+
```

```
+-----------------------------------------------------------------------------------+
| TAREA D: Comparación Local de Alternativas sin Ganador Universal                  |
+-----------------------------------------------------------------------------------+
| Consigna: "Para probar la función de comparación, activa la opción de             |
| 'Incluir ejemplos demostrativos' en la parte superior. Selecciona la vacante real |
| y uno de los ejemplos que te llame la atención. Abre la comparación y explícame:  |
| 1. ¿Qué diferencias principales encuentras entre ambas opciones?                  |
| 2. ¿La plataforma te indica cuál de las dos es mejor o te da un puntaje?          |
| 3. ¿Qué significan las celdas que dicen 'No informado' o 'No publicado'?"        |
+-----------------------------------------------------------------------------------+
```

```
+-----------------------------------------------------------------------------------+
| TAREA E: Decisión de Postulación y Verificación de Procedencia                     |
+-----------------------------------------------------------------------------------+
| Consigna: "Imagina que decidiste postular a este puesto de CookUnity.              |
| 1. ¿Dónde encuentras el canal para enviar tu postulación?                         |
| 2. ¿Ruta Sistemas recibe tu currículum o a dónde te dirige?                       |
| 3. ¿Qué información adicional sobre la empresa o el contrato necesitarías antes   |
|    de enviar tu postulación formal?"                                              |
+-----------------------------------------------------------------------------------+
```

---

## 6. Preguntas Posteriores a Cada Tarea (Debriefing)

Tras cada tarea, el moderador formulará preguntas breves de clarificación:
- *Tarea A:* "¿Qué fue lo primero que llamó tu atención al ingresar a la página? ¿Los filtros te ayudaron a encontrar lo que buscabas?"
- *Tarea B:* "¿Te resultó fácil distinguir entre lo que la empresa pide obligatoriamente y lo que es deseable? ¿Por qué?"
- *Tarea C:* "¿Notaste alguna contradicción o mensaje confuso sobre si la vacante está confirmada o vigente?"
- *Tarea D:* "¿Te ayudó la tabla comparativa a notar diferencias? ¿Sentiste que la herramienta intentaba favorecer una vacante sobre otra?"
- *Tarea E:* "¿Sentiste seguridad respecto a quién está recibiendo tus datos y si el enlace es legítimo?"

---

## 7. Métricas y Taxonomía de Evaluación

### 7.1 Métricas de Observación Cuantitativa
Para cada tarea de cada participante se registrará:
1. **Tasa de éxito:**
   - `Éxito sin ayuda` (completó la tarea autónomamente).
   - `Éxito con ayuda` (requirió una pista neutra del moderador tras bloqueo).
   - `Fracaso / Abandono` (no logró el objetivo o se rindió).
2. **Tiempo de ejecución:** Minutos y segundos medidos con cronómetro desde la lectura de la consigna hasta el cierre.
3. **Nivel de confianza subjetiva:** Escala del 1 (muy inseguro) al 5 (completamente seguro) declarada por el usuario.

### 7.2 Métricas Cualitativas y Taxonomía de Problemas
Cada incidente observado se clasificará obligatoriamente según las 6 categorías del proyecto:

```
[PROBLEMA_USABILIDAD]            -> Fallas en controles, botones, teclado, clics, modales, diseño responsivo.
[PROBLEMA_CONTENIDO]             -> Textos confusos, ambigüedades de redacción, términos no explicados, inglés técnico.
[PROBLEMA_ARQUITECTURA_INFO]     -> Jerarquía visual desorientadora, ubicación ilógica de elementos, filtros no hallados.
[PROBLEMA_DATOS_INCOMPLETOS]     -> Ausencia de información crítica en la vacante (sueldo ausente, modalidad no dicha).
[PROBLEMA_ALCANCE_PRODUCTO]      -> Expectativas no cubiertas por el producto (ej. esperar ver bolsa masiva de 500 puestos).
[SOLICITUD_FUNCIONALIDAD_NUEVA]  -> Deseos expresados por el usuario (ej. alertas por correo, guardado en favoritos).
```

### 7.3 Escala de Severidad de Problemas (Nielsen)
- **Crítica (4):** Impide completar la tarea o induce a un error grave de postulación / interpretación de la vacante.
- **Mayor (3):** Causa gran frustración o retraso significativo; el usuario requiere ayuda para superarlo.
- **Menor (2):** Causa confusión momentánea o incomodidad, pero el usuario logra resolverlo por sí mismo.
- **Cosmética (1):** Detalle estético o tipográfico que no afecta la comprensión ni el flujo operativo.

---

## 8. Criterios de Cierre de Sesión y de Fase R3

### 8.1 Cierre de Sesión Individual
Una sesión individual concluye cuando:
1. El participante ha completado o intentado los 5 escenarios.
2. Se ha realizado el cuestionario de cierre y agradecimiento.
3. Se han completado todas las notas en la plantilla de observación.

### 8.2 Cierre del Estudio R3-01
El bloque R3-01 se considera cerrado técnicamente con la entrega de:
- Protocolo aprobado.
- Plantilla individual de sesión lista para usar.
- Matriz de consolidación de hallazgos preparada.
- Auditoría técnica de readiness favorable.

*Nota de gobernanza:* La ejecución material de las entrevistas corresponderá al bloque **R3-02**, asegurando que los hallazgos deriven de interacciones con personas reales y no de suposiciones de ingeniería.
