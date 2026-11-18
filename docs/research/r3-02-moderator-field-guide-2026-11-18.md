# Guía de Campo y Moderación para Pruebas de Usabilidad R3-02
**Protocolo de Ejecución Paso a Paso para el Moderador Humano**

- **Fase:** R3 — Validación del producto (Subfase R3-02)
- **Fecha:** 2026-11-18
- **URL de prueba:** [https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/)
- **Duración estimada:** 35 a 45 minutos por sesión
- **Público objetivo:** Estudiantes de últimos ciclos (`P-EST`), egresados recientes (`P-EGR`) y profesionales junior de TI (`P-JUN`) en Perú.

---

## 1. Reglas de Oro de la Moderación Neutral (Anti-Inducción)

> [!WARNING]
> **El rol del moderador es observar, escuchar y registrar, nunca enseñar ni defender la web.**

1. **Nunca muestres cómo usar la interfaz:** Si el usuario pregunta "¿Dónde hago clic?" o "¿Esto está bien?", responde con preguntas neutrales de rebote: *"¿Dónde esperarías encontrarlo tú?"* o *"¿Qué te hace pensar eso?"*.
2. **No justifiques el diseño:** Evita frases como *"Lo pusimos ahí porque..."* o *"Es que todavía estamos en piloto"*. El usuario debe interactuar con el producto real tal como está.
3. **No corrijas interpretaciones erróneas durante la tarea:** Si el usuario confunde un empleo profesional con una práctica, o cree que una fecha es de expiración cuando es de consulta, **no lo corrijas**. Anota la confusión: ese es el dato empírico más valioso.
4. **Distinción obligatoria de asistencia:**
   - Si el participante completa la tarea por sí mismo: `SUCCESS_WITHOUT_HELP`.
   - Si el participante se bloquea por más de 60 segundos y se le da una pista neutra para continuar: `SUCCESS_WITH_HELP` (documentando la ayuda en la plantilla).
   - Si se rinde o pasa de tarea sin lograrla: `ABANDONED`.
   - Si el tiempo se agota antes de abordarla: `NOT_EXECUTED`.

---

## 2. Preparación Previa a la Sesión (5 minutos antes)

- [ ] Abrir [https://blueisazul.github.io/WebRutaSistemas/](https://blueisazul.github.io/WebRutaSistemas/) en una ventana de incógnito del navegador para asegurar que no haya cookies ni estados en caché.
- [ ] Abrir el archivo correspondiente en el editor local: `docs/research/sessions/P[01..08].md`.
- [ ] Tener cronómetro a mano (en el teléfono o reloj).
- [ ] Verificar audio y asegurarse de que el participante pueda compartir pantalla con visibilidad clara del cursor.

---

## 3. Estructura de la Sesión y Tiempos Sugeridos

```
[00:00 - 05:00]  Encuadre, bienvenida y consentimiento informado
[05:00 - 12:00]  Tarea A: Búsqueda y pertinencia de la oportunidad
[12:00 - 19:00]  Tarea B: Evaluación crítica de requisitos (CookUnity)
[19:00 - 26:00]  Tarea C: Interpretación de estados, vigencia y modalidad
[26:00 - 33:00]  Tarea D: Comparación de alternativas sin ganador universal
[33:00 - 39:00]  Tarea E: Decisión de postulación y canal oficial
[39:00 - 45:00]  Debriefing, preguntas de cierre y agradecimiento
```

---

## 4. Guion de Moderación Paso a Paso

### 4.1 Bienvenida y Consentimiento (00:00 - 05:00)

**Acción del moderador:** Leer con tono cordial y pausado:

> *"Hola [Nombre], bienvenido/a. Muchas gracias por tu tiempo hoy. Mi nombre es [Tu Nombre] y estamos evaluando un prototipo web llamado **Ruta Sistemas**, pensado para personas de carreras de Sistemas e Informática en Perú.*
>
> *Quiero reiterar algo fundamental: **estamos probando la plataforma, no tus capacidades**. No hay respuestas correctas ni incorrectas. Si te trabas o algo no se entiende, es un defecto de la interfaz y justo lo que necesitamos documentar para corregirlo.*
>
> *Te pediré que pienses en voz alta: cuéntame qué miras, qué intentas hacer, qué dudas te saltan y qué esperas que ocurra. Toda la información es 100% anónima; no te pediremos CV ni datos personales.*
>
> *¿Estás de acuerdo con participar bajo estas condiciones?"*

*(Registrar confirmación de consentimiento en la plantilla).*

---

### 4.2 TAREA A — Búsqueda y Pertinencia (05:00 - 12:00)

**Consigna verbal:**
> *"Imagina que estás buscando tu próxima oportunidad laboral acorde a tu formación en Sistemas. Ingresa a la página y explora libremente las opciones. Encuentra un puesto que consideres relevante para tu carrera y explícame por qué crees que encaja (o no encaja) con lo que buscas."*

- **Qué observar:**
  - ¿Qué lee primero? ¿El Hero, las métricas o las tarjetas?
  - ¿Utiliza la barra de búsqueda? ¿Qué términos escribe?
  - ¿Descubre los selectores de modalidad o familia profesional?
  - ¿Detecta la vacante real de CookUnity (*Supply Chain Analyst*)?
- **Focos heurísticos específicos de observación:**
  - `UX-B05`: ¿Observa los términos "Fullstack Dev" y "Data & DevOps" del Hero? ¿Muestra extrañeza si solo ve un puesto de analítica de supply chain?
  - `UX-B02`: Si el participante busca una palabra que no coincide (ejemplo: "python"), ¿qué mensaje lee? ¿Concluye que la web está vacía de empleos o entiende que su filtro no arrojó resultados?
- **Al terminar:** Pedir nivel de confianza (1 a 5) y anotar tiempo.

---

### 4.3 TAREA B — Evaluación de Requisitos (12:00 - 19:00)

**Consigna verbal:**
> *"Por favor, abre la oportunidad de 'Supply Chain Analyst' de la empresa CookUnity. Revisa la información que presenta la plataforma y dime:*
> *1. ¿Qué conocimientos técnicos y herramientas se solicitan?*
> *2. ¿Qué nivel de experiencia previa se exige?*
> *3. De acuerdo a lo que ves, ¿se trata de un empleo regular o de una práctica preprofesional?*
> *4. ¿Qué requisitos crees que cumples hoy y cuáles tendrías que confirmar?"*

- **Qué observar:**
  - ¿Cómo abre el detalle? ¿Hace clic en el título, en *"Ver evaluación ↗"* o en otra zona?
  - ¿Identifica claramente SQL, ERP/MRP y modelado de datos?
  - ¿Nota que exige mínimo 1 año de experiencia previa?
  - ¿Distingue que es un rol profesional y no una práctica?
- **Intervención permitida:** Si no encuentra cómo abrir la ficha tras 45 segundos explorando la tarjeta: *"Puedes interactuar con los botones de la tarjeta para ver más detalles"*. (Registrar como `SUCCESS_WITH_HELP`).
- **Al terminar:** Pedir nivel de confianza (1 a 5) y anotar tiempo.

---

### 4.4 TAREA C — Estados y Vigencia (19:00 - 26:00)

**Consigna verbal:**
> *"Observando la información y etiquetas de este puesto de CookUnity:*
> *1. ¿Qué entiendes por la etiqueta de estado que tiene la vacante?*
> *2. ¿Qué significa la fecha de última verificación que se muestra en el cuadro verde?*
> *3. ¿El hecho de que esté publicada te garantiza que el puesto siga abierto hoy?*
> *4. ¿En qué modalidad de trabajo se desempeñará (remoto, presencial, híbrido) y de dónde obtienes ese dato?"*

- **Qué observar:**
  - ¿Comprende que *"Verificada"* significa que el equipo revisó la fuente, pero no es garantía futura?
  - ¿Entiende que el TTL de verificación dura 7 días?
  - ¿Identifica que la modalidad figura como *"No especificado"* o *"No informada"*?
- **Focos heurísticos específicos de observación:**
  - `UX-B01`: ¿Nota alguna contradicción entre la etiqueta superior *"Activa · revisión reciente"* y el texto en negrita *"Vigencia no confirmada"* del bloque central de la tarjeta?
  - `UX-B04`: En el cuadro de verificación, ¿cómo reacciona al leer el formato del timestamp (ej. `2026-11-17T22:28:37-05:00`)? ¿Le resulta natural o parece código técnico?
- **Al terminar:** Pedir nivel de confianza (1 a 5) y anotar tiempo.

---

### 4.5 TAREA D — Comparación sin Ganador Universal (26:00 - 33:00)

**Consigna verbal:**
> *"Para probar la herramienta de comparación, activa en la parte superior la opción 'Incluir ejemplos demostrativos'. Selecciona la vacante de CookUnity y uno de los ejemplos que te interese. Abre el comparador y dime:*
> *1. ¿Qué diferencias principales notas entre ambas alternativas?*
> *2. ¿La plataforma te dice cuál es mejor o te da un puntaje?*
> *3. ¿Qué significan las celdas que dicen 'No informado' o 'No publicado'?"*

- **Qué observar:**
  - ¿Encuentra fácilmente el switch de ejemplos?
  - ¿Comprende cómo añadir fichas a la barra inferior de comparación?
  - ¿Percibe que la plataforma es neutral o busca un score/ranking?
  - ¿Interpreta que *"No informado"* significa ausencia de dato y no necesariamente una condición mala?
- **Focos heurísticos específicos de observación:**
  - `UX-B06`: ¿Detecta el toggle *"Incluir ejemplos demostrativos"* de forma autónoma o requiere que el moderador le indique dónde está ubicado?
  - `UX-B03`: En la fila *"Estado de verificación"* de la tabla, ¿qué opina al ver `open · verified · active` o `unknown · unverified · unconfirmed` en inglés?
- **Al terminar:** Pedir nivel de confianza (1 a 5) y anotar tiempo.

---

### 4.6 TAREA E — Decisión de Postulación (33:00 - 39:00)

**Consigna verbal:**
> *"Imagina que tras analizarlo decides postular al puesto de CookUnity:*
> *1. ¿Dónde encuentras el enlace para enviar tu postulación?*
> *2. Si pulsas en postular, ¿Ruta Sistemas recibe tu currículum o qué sucede?*
> *3. ¿Qué información adicional sobre la vacante o la empresa necesitarías conocer antes de decidirte a enviar tus datos?"*

- **Qué observar:**
  - ¿Encuentra el botón verde *"Ir a postulación ↗"* al pie del modal de detalle?
  - ¿Reconoce que la postulación es externa y directa con el empleador (Greenhouse)?
  - ¿Verifica la sección de *"Procedencia por dato"* con los enlaces de evidencia?
  - ¿Qué datos echa en falta? (Sueldo exacto, horario, ubicación exacta, beneficios de ley).
- **Al terminar:** Pedir nivel de confianza (1 a 5) y anotar tiempo.

---

### 4.7 Debriefing y Cierre (39:00 - 45:00)

1. *"En una escala del 1 al 5, ¿qué tan clara y confiable sentiste la información de las ofertas?"*
2. *"¿Qué te pareció más útil en comparación con portales tradicionales como LinkedIn o Computrabajo?"*
3. *"¿Hubo algo que te generó dudas, desconfianza o frustración durante la sesión?"*
4. Agradecer y despedir cordialmente.

---

## 5. Protocolo Post-Sesión para el Moderador (Inmediatamente después)

1. **Limpieza y volcado:** Abrir `docs/research/sessions/P[XX].md` y completar todos los campos vacíos con las notas tomadas y citas textuales exactas.
2. **Clasificación estandarizada:**
   - Asignar para cada tarea uno de los 4 estados: `SUCCESS_WITHOUT_HELP`, `SUCCESS_WITH_HELP`, `ABANDONED`, `NOT_EXECUTED`.
3. **Control de Calidad:**
   - Verificar que no se filtró ningún nombre real, DNI ni dato de contacto.
   - Declarar el estado de la sesión: `VALID` (si se completó con calidad), `INCOMPLETE` (si faltaron tareas) o `INVALID` (si hubo inducción grave).
4. **Actualizar el cuaderno de campo:**
   - Registrar la sesión como completada en [docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md](file:///c:/Users/sant1/Downloads/EmpleoWeb/docs/research/r3-02-fieldwork-and-recruitment-tracker-2026-11-18.md).
