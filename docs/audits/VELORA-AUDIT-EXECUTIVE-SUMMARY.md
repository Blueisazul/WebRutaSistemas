# VELORA-AUDIT-EXECUTIVE-SUMMARY — Resumen Ejecutivo de la Auditoría Integral de Velora

- **Fecha:** 23 de noviembre de 2026
- **Audiencia:** Propietario del Producto, Dirección Técnica y Comité de Entrega
- **Objetivo:** Explicar con honestidad, evidencia empírica y claridad estratégica el estado actual de Velora y la ruta hacia un catálogo nacional confiable.

---

## 1. ¿Qué Tenemos Hoy?
Velora cuenta con una **base de ingeniería de alta calidad**:
- Una aplicación web estática, rápida, accesible (certificada WCAG 2.1 AA) y sin dependencias de frameworks pesados en runtime.
- Un motor de adquisición y gobernanza local escrito en Python estándar (sin librerías externas complejas), con validación de contrato Schema 2, deduplicación determinista y trazabilidad de evidencias por campo.
- Un catálogo canónico publicado con **112 registros totales**, de los cuales **107 son oportunidades reales, activas y verificadas**.
- Una cobertura de pruebas automatizadas impecable: **232 pruebas unitarias de Python** y **45 pruebas de interfaz de usuario de Playwright**, todas pasando al 100%.

---

## 2. ¿Qué Funciona Correctamente?
1. **La Adquisición de ATS Modernos:** Los conectores para **Greenhouse** funcionan de forma determinista y segura para Canonical, Sezzle, CookUnity y recientemente **Encora Perú**, permitiendo poblar el catálogo con datos estructurados y verídicos.
2. **La Experiencia de Usuario:** La búsqueda, los 9 filtros (modalidad, nivel, familia, sector, remuneración, riesgo), la vista comparativa entre dos oportunidades y la paginación funcionan fluidamente en escritorio y dispositivos móviles.
3. **El Principio *Fail-Closed*:** Si una vacante no tiene URL oficial, si el host no está autorizado o si el proceso concluyó, el sistema la bloquea antes de que llegue al usuario.
4. **Despliegue en Vercel:** `https://velora-six-fawn.vercel.app/` está desplegando correctamente el catálogo actualizado de 107 oportunidades activas.

---

## 3. ¿Qué No Funciona o Está Desfasado?
1. **Desincronización de GitHub Pages:** Mientras Vercel muestra 107 oportunidades, GitHub Pages muestra solo 1. Esto se debió a un error en el workflow de CI/CD (falta de Python en el paso de publicación), recién corregido en el repositorio pero pendiente de re-despliegue.
2. **Inconsistencia de Marca (El dilema "Velora" vs "Ruta Sistemas"):** La URL de producción se llama `velora-six-fawn.vercel.app`, pero dentro de la página web, en el código y en la documentación no existe la palabra "Velora"; sigue diciendo "Ruta Sistemas" en todos lados.
3. **Fragilidad del TTL de Frescura en el Navegador:** El código del frontend degrada automáticamente las oportunidades a "no confirmadas" si han pasado más de 7 días desde su última fecha de verificación. Si el equipo no ejecuta una actualización semanal de fechas, el catálogo se "apaga" en la pantalla del usuario mostrando el mensaje: *«No hay oportunidades verificadas disponibles»*.
4. **Cero Oportunidades Activas del Estado:** A pesar de haber desarrollado conectores para el sector público (OSITRAN y Defensoría del Pueblo), el catálogo publicado no tiene ninguna plaza activa del Estado peruano porque los procesos analizados ya habían concluido.

---

## 4. ¿Qué Oportunidades se Están Perdiendo?
- **La gran masa del Sector Público:** Ministerios, INDECOPI, SUNAT, Gobiernos Regionales y Poder Judicial publican cientos de convocatorias mensuales de prácticas y CAS para carreras de Sistemas en Gob.pe y Talento Perú. Actualmente, Velora no las está capturando.
- **Banca y Grandes Empresas Locales:** Entidades como Interbank, BCP, BBVA, Belcorp, Alicorp y las principales consultoras de software en Lima contratan masivamente practicantes y juniors en Sistemas, pero aún no están mapeadas en los conectores de Velora.

---

## 5. ¿Qué Impide Tener Cobertura Nacional Inmediata?
1. **Estructura Técnica Dispar del Estado:** Talento Perú (SERVIR) no ofrece una API REST abierta; opera con una plataforma dinámica en JavaServer Faces que exige estado de sesión y carece de autorización explícita de scraping masivo.
2. **El Cuello de Botella Editorial Humano:** Hasta ahora, el flujo exigía que cada vacante fuese aprobada manualmente por una persona antes de publicarse, lo cual impide escalar a cientos de oportunidades semanales.
3. **Ciclos de Vida Públicos Extremadamente Cortos:** Las convocatorias del Estado suelen abrir postulaciones por 2 a 4 días. Para capturarlas vivas se requiere una frecuencia de sondeo semanal o bisemanal automatizada.

---

## 6. ¿Qué Necesitamos Técnicamente?
1. **Desarrollar el conector `gobpe-convocatorias`:** Extraer las convocatorias oficiales publicadas en Gob.pe aprovechando nuestro parser nativo de HTML y PDF, sin añadir paquetes externos.
2. **Aprobar una Política de Auto-Publicación por Reglas Objetivas:** Si una vacante viene de una fuente aprobada, tiene canal oficial, es afín a Sistemas y tiene fecha futura, debe publicarse automáticamente sin esperar un visto bueno manual.
3. **Corregir el TTL en Frontend:** Hacer que el frontend muestre una advertencia informativa de antigüedad en vez de ocultar la vacante, protegiendo al sitio contra apagones accidentales.
4. **Incorporar 3 a 5 ATS de Empresas en Lima:** Sumar bolsas públicas en Greenhouse/Lever de empresas con centros de tecnología en Perú.

---

## 7. Riesgos Principales y Mitigaciones
- **Riesgo Legal / Bloqueos Anti-Bot:** No raspar portales con protecciones agresivas (Computrabajo/Bumeran). Centrarse en fuentes oficiales transparentes (Gob.pe, ATS oficiales directos).
- **Riesgo de Publicar Vacantes Vencidas:** Mitigado por el conector de revalidación que detecta cuándo una página de postulación devuelve 404 o anuncia resultados finales.
- **Riesgo de Ruptura de Marca:** Resolver formalmente la identidad visual sustituyendo "Ruta Sistemas" por "Velora" en un hito controlado (R4-11).

---

## 8. ¿Qué Ejecutaremos Primero? (Siguiente Acción Concreta)

### Bloque Inmediato R4-11: Estabilización y Marca Velora
1. **Desplegar GitHub Pages:** Sincronizar el pipeline para que ambas plataformas (Vercel y Pages) muestren exactamente las 112 oportunidades.
2. **Aplicar la Marca Velora:** Actualizar el título, cabecera y README a **Velora**.
3. **Ajustar la Regla de TTL:** Proteger el catálogo para que las vacantes sigan visibles con indicación de estado, garantizando continuidad de servicio.
