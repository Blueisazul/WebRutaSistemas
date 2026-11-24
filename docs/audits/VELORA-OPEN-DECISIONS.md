# VELORA-OPEN-DECISIONS — Registro de Decisiones Requeridas del Propietario

- **Fecha de emisión:** 23 de noviembre de 2026
- **Propósito:** Someter a decisión exclusiva del propietario del proyecto los dilemas estratégicos, legales y de producto que no deben ser resueltos unilateralmente por la vía técnica.

---

## Decisión 1: Formalización de Marca e Identidad Visual (Velora frente a Ruta Sistemas)

- **Contexto:**  
  El proyecto se concibió históricamente como "Ruta Sistemas" (repositorio `WebRutaSistemas`). No obstante, en la URL pública de Vercel (`velora-six-fawn.vercel.app`) y en la estrategia de producto se utiliza el nombre **Velora**. En el código actual, interfaz de usuario (`<title>`, encabezado, textos), metadatos y documentación técnica, la palabra "Velora" no aparece en ninguna parte.
- **Alternativas:**
  - **Opción A (Recomendada):** Adoptar plenamente la marca **Velora** en la interfaz de usuario, cabecera, metadatos y documentación pública, conservando "Ruta Sistemas" únicamente como subtítulo formativo o nombre histórico del repositorio.
  - **Opción B:** Mantener "Ruta Sistemas" como marca oficial y configurar un dominio personalizado acorde en Vercel, retirando la denominación "Velora".
- **Impacto Técnico:**  
  La Opción A requiere actualizar `index.html`, `README.md` y selectores de aserción en los tests E2E de Playwright.
- **Estado de la Decisión:** **APROBADA POR EL PROPIETARIO (24 de noviembre de 2026)**.  
  El propietario autorizó expresamente la ejecución de `TASK-R4-11-02` adoptando **Velora** como marca oficial única del producto. Se preserva `WebRutaSistemas` como identificador del repositorio y subpath de Pages para continuidad de despliegue.

---

## Decisión 2: Política de Publicación Automatizada sin Revisión Manual Individual

- **Contexto:**  
  El propietario cuestionó la necesidad de que cada oportunidad individual requiera una aprobación humana explícita antes de publicarse, argumentando que si una vacante es legítima y verificable, debe estar visible para que el usuario tome su propia decisión.
- **Alternativas:**
  - **Opción A (Recomendada - Reglas Objetivas):** Autorizar que toda vacante capturada desde fuentes pre-aprobadas (ej. Greenhouse de Encora, Canonical, Sezzle o bases oficiales de Gob.pe) que cumpla estrictamente con:
    1. Host permitido y URL HTTPS segura.
    2. Taxonomía técnica afín a Sistemas/Software/Tecnología.
    3. Elegibilidad verificada en Perú.
    4. Cero colisiones en deduplicación.
    5. Fecha límite futura o estado abierto confirmado.  
    se publique **automáticamente** en el catálogo activo, reservando la revisión humana únicamente para excepciones, conflictos de deduplicación o fuentes nuevas.
  - **Opción B (Flujo Editorial Estricto):** Mantener la aprobación humana manual mediante `editorialDecision` para cada vacante antes de su promoción a producción.
- **Impacto:**  
  La Opción A escala el catálogo nacional a cientos de vacantes sin cuellos de botella humanos, manteniendo el principio *fail-closed*.

---

## Decisión 3: Estrategia de Acceso para Talento Perú / SERVIR

- **Contexto:**  
  Talento Perú (`app.servir.gob.pe`) es el portal con mayor volumen de convocatorias del Estado peruano, pero utiliza formularios dinámicos JavaServer Faces (JSF) sin API REST pública y con términos que no contemplan scraping masivo.
- **Alternativas:**
  - **Opción A (Vía Institucional):** Remitir una carta o solicitud formal de acceso a datos abiertos o colaboración institucional a SERVIR (`talentoperu@servir.gob.pe`).
  - **Opción B (Scraping de Bajo Impacto):** Implementar un conector técnico defensivo que consulte periódicamente (1 vez al día, con demoras de 10 segundos) únicamente los metadatos de ofertas afines a Sistemas, asumiendo el riesgo de bloqueo de IP o cambios de interfaz JSF.
  - **Opción C (Descubrimiento Asistido):** Utilizar Gob.pe y portales de reguladores como fuentes directas, dejando Talento Perú como canal de consulta manual externa referenciada.
- **Impacto:**  
  Define la legitimidad y estabilidad del flujo de datos del sector público.

---

## Decisión 4: Dominio Canónico y Plataforma Definitiva de Despliegue

- **Contexto:**  
  Actualmente existen dos despliegues públicos: Vercel (`velora-six-fawn.vercel.app`) y GitHub Pages (`blueisazul.github.io/WebRutaSistemas/`), los cuales estuvieron desfasados debido a un fallo en el CI de Pages.
- **Alternativas:**
  - **Opción A (Vercel como Canónico):** Declarar a Vercel como la plataforma principal de producción, asociarle un dominio propio (ej. `velora.pe` o `velora.app`) y mantener GitHub Pages únicamente como réplica pasiva de respaldo.
  - **Opción B (GitHub Pages como Canónico):** Mantener GitHub Pages como plataforma principal aprovechando el workflow de empaquetado exacto de 5 archivos (`pages_artifact.py`).
- **Impacto:**  
  Claridad de cara al usuario final, SEO y centralización del tráfico.

---

## Decisión 5: Política Editorial sobre Procesos del Estado Concluidos

- **Contexto:**  
  En el sector público peruano (CAS y Prácticas), los concursos suelen tener una ventana de postulación de solo 2 a 5 días hábiles. Cuando el proceso termina, las bases y actas siguen siendo valiosas para que un estudiante conozca qué perfiles, conocimientos y remuneraciones exige el Estado.
- **Alternativas:**
  - **Opción A:** Permitir que las convocatorias públicas concluidas se mantengan en el catálogo bajo la etiqueta clara de `"Convocatoria concluida / Histórica"` (sin CTA de postulación), para fines de comparación y entendimiento del mercado estatal.
  - **Opción B:** Ocultarlas inmediatamente del catálogo una vez concluida la postulación, mostrándolas solo si el usuario activa un filtro explícito de histórico.
- **Impacto:**  
  Enriquece la utilidad informativa del catálogo para el estudiante sin inducir a postulaciones extemporáneas.
