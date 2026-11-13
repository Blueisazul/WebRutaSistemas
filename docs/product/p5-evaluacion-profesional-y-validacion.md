# P5 — Evaluación profesional explicable

## Alcance y estado

P5 construye una capa de lectura y comparación sobre el catálogo schema 2
existente. No crea oportunidades, no modifica la semilla ni el snapshot y no
convierte fichas demostrativas en datos de mercado. La implementación funciona
sin cuenta, backend, almacenamiento persistente ni servicios externos.

El catálogo actual no contiene oportunidades reales activas. Por eso las señales
describen la información observada y sus límites; no recomiendan postular ni
declaran una mejor alternativa universal.

## Modelo de evaluación

Cada dimensión se representa como una señal cualitativa:

- **Dato publicado:** existe un valor explícito en la ficha.
- **Condición que requiere atención:** la ficha declara una temporalidad,
  restricción o dependencia.
- **Limitación documentada:** el propio registro describe un riesgo o condición.
- **Información insuficiente:** el campo está ausente, no publicado o no permite
  concluir.
- **Evidencia atrasada:** la información existe, pero excede el TTL o el estado
  actual no permite usarla como vigencia.
- **No aplicable:** la dimensión no corresponde al tipo de oportunidad.

No existe score, promedio, estrellas, ranking ni ganador universal.

### Oportunidad

| Dimensión | Hecho observado | Interpretación permitida | Límite |
|---|---|---|---|
| Compensación | `salary` y `salaryNote` | Permite saber si hay una cifra publicada | No permite juzgar suficiencia ni comparar si la otra ficha no informa salario |
| Beneficios | `benefits` | Muestra beneficios declarados | No prueba que sean universales o vigentes |
| Continuidad | `duration`, `employmentEndDate`, `continuity` | Hace visible temporalidad, renovación o ausencia de información | No predice contratación, renovación ni estabilidad |
| Valor técnico | `tasks`, `skills`, `family` | Describe exposición técnica potencial basada en la función | Tecnologías mencionadas no prueban práctica real ni mentoría |
| Desarrollo | `growth`, `training`, `requirements`, `level` | Expone aprendizaje o trayectoria declarada | No garantiza ascenso ni movilidad |
| Modalidad | `mode`, `location` | Resume el lugar o modalidad publicada | Remoto no equivale a contratación internacional |
| Elegibilidad | `eligibility` | Indica territorios explícitos | No se infiere Perú por la palabra “remoto” |
| Calidad de convocatoria | estados, fechas, procedencia y evidencia | Señala si la ficha es usable como referencia | Una generación reciente no renueva evidencia |
| Riesgos | `risk` y condiciones contradictorias | Hace visibles restricciones | No convierte una ausencia en riesgo factual |

### Empleador

La identidad, el sector, el publisher y los enlaces de procedencia se presentan
por separado. El frontend muestra “información institucional registrada” cuando
hay datos, pero declara que la evaluación de condiciones laborales del empleador
no está disponible sin evidencia específica. No se derivan reputación, cultura,
trayectoria ni calidad laboral del nombre o del tamaño.

## Hechos, interpretación y evidencia

La vista de detalle separa:

1. **Lo publicado:** valores del registro.
2. **Lectura editorial:** qué podría significar para el siguiente paso.
3. **Lo que falta confirmar:** campos ausentes, TTL vencido, elegibilidad o
   continuidad no documentadas.
4. **Procedencia:** enlaces HTTPS y fecha de observación por campo.

Las señales calculadas son deterministas, locales y reproducibles a partir de
campos existentes. No se guardan como atributos del catálogo.

## Comparador

El comparador permite seleccionar hasta dos fichas visibles y muestra una tabla
lado a lado de compensación, beneficios, modalidad, elegibilidad, continuidad,
tipo, nivel, familia, tareas, herramientas, desarrollo, riesgos y estado de
verificación. Los valores ausentes aparecen como “No informado”; nunca como
cero, favorable o desfavorable. Las fichas demostrativas conservan su etiqueta.

La selección vive solo en memoria de la página. Retirar una ficha elimina su
selección y no transmite preferencias a terceros. La UI no ordena, puntúa ni
declara una ganadora.

## Preferencias futuras y privacidad

Preferencias candidatas: tipo, nivel, familia técnica, modalidad, ubicación,
compensación mínima y prioridad relativa entre compensación, aprendizaje,
continuidad y modalidad. Son preferencias de búsqueda, no un perfil profesional.

En una futura iteración pueden existir como estado efímero local para filtrar o
comparar. No se deben recopilar CV, historial sensible, datos de terceros,
cuentas, seguimiento de postulaciones ni analítica de comportamiento sin
consentimiento, propósito, eliminación y portabilidad definidos.

## Rutas profesionales futuras

Un modelo de rutas requeriría muestras reales longitudinales sobre roles de
entrada, habilidades, tecnologías, niveles, transiciones y requisitos de
progresión. Los campos actuales ayudan a describir una oportunidad, pero no
demuestran transiciones ni causalidad. No se implementa un recomendador ni una
trayectoria automática en P5.

## Protocolo de validación con usuarios

R3 deja preparado un protocolo reproducible, pero no contacta usuarios ni inventa
resultados. La sesión debe usar estudiantes de últimos ciclos, egresados
recientes o profesionales junior de Sistemas y comprobar si pueden:

1. entender condiciones de una ficha;
2. distinguir salario publicado de salario ausente;
3. reconocer temporalidad o suplencia;
4. distinguir modalidad de elegibilidad desde Perú;
5. identificar evidencia insuficiente;
6. comparar dos fichas según sus prioridades;
7. explicar por qué una alternativa les conviene;
8. identificar el dato adicional necesario antes de postular.

Registrar: tiempo de comprensión, tiempo de comparación, interpretación de
estados, errores sobre modalidad/elegibilidad, capacidad de explicar la decisión,
utilidad percibida y dimensiones prioritarias. La aceptación de recomendaciones
de producción requiere usuarios reales y una muestra verificable; esta UI no la
demuestra. Cada sesión debe registrar consentimiento, perfil general no
identificable, fixture utilizado, tarea, resultado esperado, resultado observado,
errores de interpretación, tiempo solo si se mide con reloj, comentario textual y
severidad del problema. Las fichas demostrativas deben presentarse como ejemplos;
los resultados de interacción no validan el valor profesional del catálogo.

### Guion mínimo de sesión R3

1. Sin activar ejemplos, explica qué significa el estado inicial y por qué no
   aparecen oportunidades verificadas.
2. Activa explícitamente los ejemplos y encuentra una ficha remota.
3. Usa modalidad, nivel y ubicación en combinación; después limpia los filtros.
4. Abre una ficha, identifica empleador, publisher, evidencia, última consulta,
   estado y motivo por el que no se puede postular.
5. Selecciona dos fichas, abre la comparación y describe una diferencia
   demostrada, un dato ausente y una prioridad que dependería de la persona.
6. Explica qué dato adicional pediría antes de postular.

El facilitador no debe explicar la respuesta durante la tarea. Los resultados se
clasifican como `completada`, `completada_con_duda`, `no_completada` o
`bloqueada_por_dato_ausente`. La validación de producto permanece pendiente hasta
repetir el guion con al menos una oportunidad real autorizada y publicada.

## Casos que permanecen no evaluables

- salario ausente o no comparable;
- modalidad remota sin elegibilidad territorial explícita;
- beneficios no descritos;
- continuidad o renovación no documentadas;
- tecnologías sin tareas o contexto;
- evidencia atrasada o contradictoria;
- empleador sin evidencia institucional específica;
- cualquier ficha `demonstration` como recomendación real.
