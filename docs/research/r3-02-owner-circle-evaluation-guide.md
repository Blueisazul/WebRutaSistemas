# Guía de Exploración para el Propietario y Círculo Reducido
## Evaluación No Productiva de Ruta Sistemas

> [!NOTE]
> **Propósito de esta guía:**
> Este documento está pensado para el propietario de Ruta Sistemas y un grupo pequeño de amistades o colegas cercanos que quieran probar la aplicación de forma presencial o directa.
> **No es un examen ni una prueba formal de usabilidad.** El objetivo es que explores con total libertad, veas lo que hace la herramienta en su estado real de desarrollo y nos digas con sinceridad qué se entiende, qué no se entiende, qué resulta útil y qué falla o sobra.

---

## 1. ¿Qué es Ruta Sistemas hoy?

Ruta Sistemas es un explorador de oportunidades laborales y prácticas para estudiantes y profesionales de ingeniería de sistemas y tecnologías de la información en el Perú.

En esta versión de evaluación:
- **No es una bolsa de trabajo tradicional:** No guardamos tu currículum ni gestionamos postulaciones directamente.
- **Transparencia y evidencia:** Cada dato (requisitos, modalidad, sueldo, tecnologías) proviene de una fuente pública verificada o se señala como no publicado.
- **Oportunidad real activa:** Incluye la vacante real de **CookUnity (Supply Chain Analyst)** en Lima, verificada en su portal oficial (ATS Greenhouse).
- **Ejemplos demostrativos:** Contiene ejemplos con fines de diseño y prueba de filtros que puedes activar o desactivar libremente.

---

## 2. Cómo iniciar el servidor local

Para abrir la aplicación en tu computadora:

1. Abre tu terminal (PowerShell, Command Prompt o terminal de tu preferencia) en la carpeta del proyecto:
   ```bash
   cd C:\Users\sant1\Downloads\EmpleoWeb
   ```
2. Ejecuta el servidor local:
   ```bash
   python server.py
   ```
3. Verás un mensaje como este:
   ```text
   Ruta Sistemas está disponible solo en esta computadora: http://127.0.0.1:4173
   ```
4. Abre tu navegador web (Chrome, Edge, Firefox, Safari) y entra a:
   **`http://127.0.0.1:4173/`**

> [!IMPORTANT]
> **Seguridad y privacidad:**
> El servidor funciona exclusivamente dentro de tu propia computadora (`127.0.0.1`). No está abierto a Internet ni comparte datos fuera de tu máquina.

---

## 3. Recorrido sugerido (Paso a paso)

Te recomendamos seguir estos pasos para conocer las funciones principales, aunque puedes explorar en el orden que prefieras:

```text
1. Vistazo inicial  ──>  2. Búsqueda y filtros  ──>  3. Oportunidad real  ──>  4. Ficha detallada  ──>  5. Comparador
```

### Paso 1: Vistazo inicial
- Entra a la página de inicio.
- Observa la cabecera, la presentación y el catálogo inicial.
- **Pregunta para reflexionar:** ¿Queda claro de inmediato para qué sirve este sitio?

### Paso 2: La vacante real activa
- En el catálogo verás inicialmente la vacante real verificada: **Supply Chain Analyst** en **CookUnity**.
- Haz clic en **«Ver detalle ↗»** o en el título del puesto.
- Observa la ficha que se abre:
  - **Cabecera destacada:** Fuente oficial verificada (Greenhouse ATS) con fecha de revisión.
  - **Resumen:** Ubicación (Lima, Perú), nivel profesional (Junior). Nota cómo **no inventamos** modalidad ni salario si la empresa no los publicó.
  - **Requisitos reales:** Exige 1+ años de experiencia previa (no es práctica preprofesional ni sin experiencia).
  - **Qué se verificó y Procedencia:** Despliega el acordeón de «Procedencia por dato (21 campos registrados)» para ver el origen exacto de cada dato.
  - **Canal de postulación:** Observa el botón «Ir a postulación ↗» que dirige al portal oficial del empleador.

### Paso 3: Explorar con ejemplos demostrativos
- Cierra la ficha con el botón **«Cerrar»** (o tecla `Esc`).
- En el panel de filtros, activa la casilla **«Incluir ejemplos demostrativos»**.
- Verás que el catálogo se amplía con otros registros de prueba (Frontend, Data Engineer, etc.).
- Prueba a:
  - Escribir en la barra de búsqueda (ej. `Python`, `SQL`, `Lima`). (Atajo: presiona la tecla `/` para enfocar la búsqueda).
  - Cambiar los filtros de **Modalidad** (Remoto, Híbrido, Presencial), **Sector**, **Nivel** o **Familia profesional**.
  - Usar el botón **«Limpiar filtros»** para reiniciar la búsqueda.

### Paso 4: Probar el comparador
- Con los ejemplos demostrativos activados, busca dos puestos que te interesen.
- En la primera tarjeta, haz clic en **«Añadir a comparación»**.
- En la segunda tarjeta, haz clic en **«Añadir a comparación»**.
- En la parte inferior aparecerá una barra flotante indicando que tienes 2 opciones seleccionadas.
- Haz clic en **«Comparar»**.
- Se abrirá una tabla comparativa lado a lado que evalúa 14 atributos objetivos sin poner calificaciones subjetivas inventadas.
- Cierra la comparación con **«Cerrar»** y desmarca la selección con **«Quitar selección»**.

### Paso 5: Vista directa por enlace (URL)
- Si deseas ver una ficha como página completa independiente, abre en una pestaña nueva:
  `http://127.0.0.1:4173/?id=OP-005`
- Nota que puedes navegar directamente y volver al catálogo con el botón **«← Volver al catálogo»**.

---

## 4. Limitaciones conocidas de esta versión

Para que tengas expectativas claras:
1. **Pocas ofertas reales:** Actualmente solo hay 1 vacante real publicada (`OP-005`). Los demás registros son demostrativos para evaluar la interfaz.
2. **Sin cuenta de usuario:** No hay registro, inicio de sesión, favoritos guardados en la nube ni alertas por correo.
3. **No se postula desde aquí:** La postulación siempre se realiza en el portal del empleador; aquí solo se informa y verifica.
4. **Solo en tu equipo:** El enlace no funcionará si se lo envías por WhatsApp a un amigo a su teléfono, a menos que esté mirando tu pantalla o use tu equipo.

---

## 5. Cómo comunicar observaciones, dudas o errores

No necesitas llenar un formulario técnico complejo. Nos interesa tu opinión espontánea y honesta:
- **¿Qué no entendiste?** (Textos confusos, siglas raras, botones difíciles de encontrar).
- **¿Qué te pareció innecesario o recargado?** (Demasiada información, secciones que no leerías).
- **¿Qué echaste en falta?** (Datos importantes que esperarías ver de inmediato).
- **¿Algo falló visual o técnicamente?** (Botones que no responden, textos que se cortan en tu pantalla).

### Dónde anotarlo
El propietario tiene disponible la plantilla:
`docs/research/r3-02-informal-feedback-template.md`

Simplemente pídele que tome nota de tus comentarios o dile lo que piensas directamente mientras exploras la pantalla.

> [!TIP]
> **Si eres amigo del propietario:** Di la verdad sin compromiso. Los comentarios críticos ("esto no se entiende nada", "este botón no hace lo que pensé", "la tabla es muy larga") son mucho más valiosos que decir "se ve bonito" por cortesía.

---

## 6. Cómo detener el servidor

Cuando termines la sesión de exploración:
1. Ve a la ventana de la terminal donde ejecutaste `python server.py`.
2. Presiona las teclas **`Ctrl + C`**.
3. Verás el mensaje:
   ```text
   Servidor local detenido.
   ```
4. Ya puedes cerrar la terminal y el navegador.

---

## 7. Gobernanza: Feedback informal vs. Investigación formal

- **Esta evaluación informal:** Es libre, espontánea y sirve para pulir detalles de diseño y estabilidad antes de contactar a personas externas.
- **Investigación formal R3-02:** El proyecto cuenta con un protocolo formal (`P01` a `P08`) con rúbricas de control de calidad y consentimiento informado. Los comentarios recogidos aquí **no** se mezclarán con los datos de las sesiones formales.
