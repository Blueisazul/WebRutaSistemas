# EVALUACIÓN DE ALTERNATIVAS Y DECISIÓN DE INTEGRACIÓN — TASK-R5-04-01
## Modelo de Integración para Radares Secundarios en Velora

- **Fecha:** 24 de noviembre de 2026
- **Fase:** R5 — Cobertura nacional de oportunidades
- **Tarea:** `TASK-R5-04-01`
- **Autor:** Principal Software Architect & Technical Auditor

---

### 1. Comparativa de Alternativas de Integración

Se evaluaron tres modelos posibles para incorporar el valor de descubrimiento de **Practicas.pe** y **Convocatorias de Trabajo** al ecosistema de Velora:

| Criterio de Evaluación | Alternativa A: Radar Automatizado Directo | Alternativa B: Descubrimiento Asistido (Recomendada) | Alternativa C: Sin Integración (Descarte) |
|---|---|---|---|
| **1. Cobertura adicional aportada** | Alta (adquiere masivamente convocatorias de entidades no conectadas). | **Alta y depurada** (detecta entidades abiertas e ingresa a staging con trazabilidad primaria). | Nula (permanece la brecha en entidades estatales no conectadas). |
| **2. Cumplimiento de permisos y gobernanza** | Riesgo Alto (scrapear resúmenes editoriales de IDEADS vulnera sus términos de plataforma). | **Riesgo Bajo / Conforme** (solo extrae identificadores y URLs salientes a fuentes públicas estatales; no copia texto protegido). | Riesgo Cero. |
| **3. Estabilidad técnica** | Frágil (susceptible a roturas de layout o cambios en el CMS PHP de IDEADS). | **Robusta** (el scraper de descubrimiento solo necesita identificar `<a href="...">` a `.gob.pe` y códigos de proceso). | Alta (sin código adicional). |
| **4. Costo de mantenimiento** | Alto (requiere mantener parsers para múltiples variantes de páginas secundarias). | **Bajo** (pipeline ligero centrado en regex de URLs primarias). | Cero. |
| **5. Frecuencia de ejecución requerida** | Diaria masiva (genera volumen excesivo de peticiones a un tercero). | **Semanal o bajo demanda** (orientada a escaneo de novedades en días de postulación estatal). | Nula. |
| **6. Riesgo de publicar datos desactualizados** | Crítico (si el agregador secundario mantiene una vacante caducada, Velora la publicaría erróneamente). | **Cero** (el candidato en staging no se publica sin confirmación oficial de vigencia en la fuente primaria). | Cero. |
| **7. Facilidad de localizar la fuente original** | Directa (el 100% de la muestra estatal contenía enlaces salientes a `.gob.pe` o bases PDF). | **Directa y mandataria**. | No aplica. |
| **8. Tasa de duplicados resultante** | Muy Alta (ambos portales republicitan exactamente los mismos procesos). | **Controlada** (la deduplicación determinista unifica por clave primaria oficial `{entidad}-{proceso}`). | No aplica. |
| **9. Compatibilidad con el motor actual** | Parcial (requeriría adaptar Candidate Schema 2 para admitir agregadores como publisher). | **100% compatible** (el agregador se registra como `discoveryRadar`, el `publisher` es la entidad oficial). | 100% compatible. |
| **10. Dependencia de terceros** | Crítica (Velora dependería de un medio comercial privado no oficial). | **Desacoplada** (el radar avisa; la relación de verdad es con el portal oficial del Estado). | Nula. |

---

### 2. Análisis Detallado del Modelo Recomendado: Descubrimiento Asistido (Modelo B)

#### Flujo Operativo:
```
[ Radar Secundario ] (Practicas.pe / Convocatorias de Trabajo)
        │
        ▼ (Inspección de búsqueda parametrizada: carrera=18)
[ Extracción de Enlaces Salientes Primarios ]
        │  - Identificador de proceso (ej. CAS 016-2026)
        │  - URL oficial (.gob.pe, cdn.www.gob.pe, intranet estatal)
        ▼
[ Candidato en Staging (Candidate Schema 2) ]
        │  - sourceId: "radar-practicas-pe" / "radar-convocatoriasdetrabajo"
        │  - editorialReview.status: "pending_review"
        │  - proposed.externalReference: "{ENTIDAD}-{PROCESO}"
        ▼
[ Validador Oficial de Vigencia ]
        │  - Descarga de bases PDF o consulta de fecha límite oficial
        │  - Deduplicación determinista contra catálogo canónico
        ▼
[ Promoción Editorial Autorizada ] -> Catálogo Canónico Velora
```

#### Reglas de Gobernanza Mandatorias para el Modelo B:
1. **Atribución Estricta:** Velora **nunca** presentará a Practicas.pe ni a Convocatorias de Trabajo como empleador ni como canal oficial de postulación.
2. **Cero Copia de Resúmenes:** Queda estrictamente prohibido ingerir o replicar las descripciones textuales redactadas por IDEADS. Los requisitos y el perfil deben extraerse de las bases oficiales primarias (`.pdf` o publicación legal).
3. **Fail-Closed de Vigencia:** Ningún candidato descubierto a través de un radar secundario podrá recibir estado activo en Velora si su fecha límite no fue comprobada directamente en la documentación de la entidad oficial.

---

### 3. Recomendación Final

Se recomienda **aprobar la adopción conceptual del Modelo B (Descubrimiento Asistido)** y registrar la correspondiente decisión en `docs/audits/VELORA-OPEN-DECISIONS.md`.

No se debe implementar ningún conector de producción en la fase inmediata, sino programar una tarea futura (`TASK-R5-04-02`) condicionada a la aprobación formal del propietario.
