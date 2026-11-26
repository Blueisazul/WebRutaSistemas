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
- **Estado de la Decisión:** **APROBADA POR EL PROPIETARIO (Opción A) — IMPLEMENTADA Y CERTIFICADA (25 de noviembre de 2026)**.  
  El propietario autorizó formalmente la Opción A: autopublicación determinista basada en reglas objetivas bajo el principio de *fail-closed*. Se implementó el motor de autopublicación en `collector/autopublish.py`, integrado en `scripts/editorial_cli.py autopublish` y validado exhaustivamente mediante 18 escenarios de prueba automatizados (`tests/test_autopublish.py`). Las 6 reglas obligatorias se evalúan de forma independiente y concurrente; cualquier incumplimiento retiene al candidato en `pending_review` sin alterar el catálogo canónico.

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

---

## Decisión 6: Autorización y Términos de Acceso Automatizado a Portales Institucionales de Gob.pe (INDECOPI y Otras Entidades)

- **Contexto:**  
  En la ejecución de `TASK-R5-01`, el conector `gobpe-convocatorias` interactúa con `oportunidadeslaborales.indecopi.gob.pe`, `www.gob.pe` y `cdn.www.gob.pe`. Si bien las directivas `robots.txt` permiten el rastreo público de publicaciones y documentos, la directiva del proyecto prohíbe interpretar `robots.txt` como una autorización legal o contractual formal de scraping, extracción recurrente o reutilización automatizada.
- **Alternativas:**
  - **Opción A (Recomendada - Consulta Periódica de Bajo Impacto con Atribución Oficial):** Autorizar la extracción automatizada regular con límites estrictos de tasa (máximo 10 peticiones por ejecución, demoras mínimas de 2 segundos, metadatos y enlaces directos a la fuente original de Gob.pe sin republicar el contenido íntegro de las bases), fundamentado en la naturaleza pública y legal de las convocatorias del Estado peruano (Ley de Transparencia y Acceso a la Información Pública).
  - **Opción B (Adquisición Asistida / Semi-Automática):** Mantener el conector únicamente para ejecuciones locales bajo demanda operadas por el equipo editorial, sin programar ejecuciones en pipelines automáticos de CI/CD.
  - **Opción C (Vía Institucional Exclusiva):** Suspender la extracción automatizada de entidades de Gob.pe hasta obtener convenios o pronunciamientos formales de datos abiertos institucionales.
- **Impacto:**  
  Brinda certeza jurídica y operativa a la fase R5 de cobertura nacional de fuentes públicas.

---

## Decisión 7: Modelo de Gobernanza y Uso de Plataformas Secundarias (Practicas.pe y Convocatorias de Trabajo) como Radares de Descubrimiento

- **Contexto:**  
  La investigación técnica de `TASK-R5-04-01` constató que Practicas.pe y Convocatorias de Trabajo (operadas por IDEADS) contienen enlaces directos hacia bases oficiales de decenas de instituciones públicas que Velora no monitorea directamente (SMV, SEDAPAL, UGELs, FONDEPES, JUNTOS, etc.). No obstante, los términos de uso de IDEADS establecen derechos sobre sus portales y eximen responsabilidad, instando a los usuarios a consultar las fuentes primarias.
- **Alternativas:**
  - **Opción A (Modelo B - Descubrimiento Asistido - Recomendada):** Autorizar el uso de estas plataformas **exclusivamente como radares de alerta temprana**. El sistema solo extrae el código del proceso y el hipervínculo a la fuente oficial primaria (`gob.pe`, intranets estatales, bases PDF). Se prohíbe terminantemente copiar descripciones o textos de IDEADS, y ninguna oportunidad se publica en Velora sin haber verificado vigencia y requisitos directamente en la fuente oficial.
  - **Opción B (Modelo A - Radar Automatizado Directo):** Construir conectores de ingesta directa que publiquen oportunidades a partir de los datos sintetizados por IDEADS, asumiendo el riesgo de desactualización y posibles objeciones sobre derechos de autor de sus resúmenes.
  - **Opción C (Modelo C - Descarte Total):** Prohibir cualquier interacción con agregadores secundarios y depender únicamente de conectores punto a punto desarrollados para cada institución estatal o ATS privado.
- **Impacto:**  
  La Opción A multiplica la cobertura nacional de convocatorias públicas del Estado de forma segura y ética, preservando el principio de fail-closed y veracidad absoluta de Velora.

---

## Decisión 8: Adopción del Ecosistema Multitenant HiringRoom para Cobertura Corporativa Privada en Perú

- **Contexto:**  
  La auditoría de canales ATS en el Perú (`TASK-R5-03`) evidenció que las principales consultoras de tecnología, proveedores de infraestructura y firmas de banca TI que contratan en el país (Stefanini IT Solutions Perú, Canvia, MyApps Soluciones, Efitec Corporation) utilizan la plataforma multitenant **HiringRoom** (`*.hiringroom.com`) en lugar de portales globales como Greenhouse o Lever. Asimismo, empresas que utilizan portales SPA reactivos (Belcorp con Rankmi/Pandapé) o intermediarios cerrados (BCP/Yape con Krowdy) no ofrecen endpoints públicos desatendidos sin navegador headless.
- **Alternativas:**
  - **Opción A (Recomendada - Generalización del Conector `hiringroom-board`):** Consolidar el conector nativo `hiringroom-board` en `collector/pe_connectors.py` como la vía estándar de adquisición para el ecosistema corporativo privado peruano. Operar bajo límites estrictos de tasa (`minDelayMs: 1500`, 10 a 15 peticiones por corrida), extraer metadatos factuales indispensables (`metadata_only_approved`) y clasificar fuentes en `pending_review` bajo el principio de *fail-closed* si requieren clientes reactivos complejos.
  - **Opción B (Dependencia Exclusiva de ATS Globales):** Restringir la adquisición privada únicamente a Greenhouse y Lever, limitando severamente la cobertura de oportunidades locales peruanas a empresas multinacionales con presencia en Lima.
  - **Opción C (Desarrollo de Raspadores Específicos por Empresa):** Construir un scraper personalizado para cada portal corporativo privado, incrementando drásticamente el costo de mantenimiento técnico.
- **Impacto:**  
  La Opción A maximiza la captura de oportunidades locales reales con mínimo código adicional, cero librerías externas y pleno respeto de las directivas de acceso ético.
