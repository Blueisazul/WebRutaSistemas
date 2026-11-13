# Evaluación de fuente: Canonical Careers

- **Fecha de consulta:** 2026-11-11
- **ID local propuesto:** `canonical-careers`
- **Empleador:** Canonical Group Limited / Canonical
- **Dominio corporativo:** `canonical.com`
- **Decisión:** `pending_review`
- **Automatización:** deshabilitada; presupuesto de solicitudes `0`

## Evidencia oficial consultada

1. [Canonical Careers](https://canonical.com/careers) identifica el portal corporativo y muestra departamentos de ingeniería, soporte, producto y otros.
2. [Open roles](https://canonical.com/careers/all) muestra el buscador y filtros por departamento y región. La consulta de esta fecha no demostró una vacante concreta elegible para Perú; no se ejecutaron endpoints de búsqueda ni automatización.
3. [Remote work](https://canonical.com/careers/company-culture/remote-work) declara que Canonical es una organización distribuida y describe su política de trabajo remoto. Esto demuestra relevancia potencial para trabajo remoto, no elegibilidad automática desde Perú para cada puesto.
4. [Website terms and conditions](https://canonical.com/legal/terms) indica que el contenido del sitio es de Canonical o de sus proveedores y que la descarga/impresión se permite para uso personal, educativo y no comercial, conservando avisos. Esta cláusula no autoriza a Ruta Sistemas a extraer, conservar o republicar anuncios en un catálogo público; requiere confirmación específica.
5. [Data privacy](https://canonical.com/legal/data-privacy) enlaza una [privacy notice de recruitment](https://canonical.com/legal/data-privacy/recruitment). La política trata datos de postulantes y no concede licencia para reutilizar anuncios ni autoriza a Ruta Sistemas a conservar datos personales. Ruta Sistemas no debe capturar CV, nombres, correos ni formularios.

## Evaluación por dimensión

| Dimensión | Estado | Evidencia / límite |
|---|---|---|
| Consulta manual | Compatible con restricciones | El portal corporativo es públicamente identificable; se debe revisar cada ficha sin asumir disponibilidad futura. |
| Automatización | Pendiente de confirmación | No se identificó un API/feed oficial ni permiso explícito para automatización de terceros. No se consultaron endpoints ATS. |
| Conservación | Pendiente de confirmación | Los términos no definen un conjunto de metadatos de vacantes que Ruta Sistemas pueda almacenar. No conservar contenido completo ni datos personales. |
| Reutilización pública | No demostrada | La autorización de uso personal/educativo/no comercial de la web no equivale a permiso para republicación pública en Ruta Sistemas. |
| Atribución | Pendiente | Como mínimo sería necesario enlazar la ficha corporativa original y mantener avisos; debe confirmarlo Canonical. |
| Canal de postulación | Identificable por ficha, por verificar | La postulación debe permanecer en la URL corporativa original; no se debe sustituir por un formulario de Ruta Sistemas. |
| Cobertura | Potencialmente relevante | Ingeniería y soporte son pertinentes para Sistemas; la elegibilidad territorial debe comprobarse por puesto. |
| Viabilidad operativa | No medida | No se ejecutó scraping, API, prueba de carga ni seguimiento de cambios. |
| Incertidumbre | Alta | Faltan autorización, retención, frecuencia, corrección, retirada y reglas para puestos remotos desde Perú. |

## Propuesta condicionada de incorporación

- **Hosts a evaluar, no autorizados:** `canonical.com` y el host exacto de la ficha corporativa que Canonical confirme. No añadir hosts ATS por conjetura.
- **Mecanismo:** revisión manual inicial. Solo diseñar un adaptador pequeño si Canonical confirma un mecanismo oficial y sus límites.
- **Campos mínimos candidatos:** empleador, publisher, título, ubicación/país elegible, modalidad, fecha observada, URL informativa y URL original de postulación.
- **No almacenar:** descripción completa, requisitos extensos, imágenes, CV, datos de postulantes, cookies, tokens ni contenido sujeto a acceso autenticado.
- **Atribución:** Canonical como empleador, enlace a la ficha original y cualquier texto de atribución que confirme la empresa.
- **Presupuesto inicial:** cero hasta respuesta escrita. Si se autoriza automatización, proponer un límite explícito y reversible antes de activar.
- **Vigencia:** comprobar individualmente que la ficha sigue abierta y que acepta postulantes desde Perú; no inferirlo por la etiqueta “remote”.
- **Retirada:** retirar o marcar histórica ante cierre, solicitud del empleador, redirección no autorizada o evidencia fuera del TTL.

## Consulta humana preparada, no enviada

Canal sugerido: `legal@canonical.com` aparece en los términos del sitio. La consulta debe pedir confirmación separada sobre:

1. consulta manual y uso de enlaces;
2. automatización, API/feed o exportación autorizada;
3. metadatos mínimos que pueden conservarse y plazo;
4. republicación pública en Ruta Sistemas y límites de contenido;
5. atribución obligatoria;
6. frecuencia, identificación y límites técnicos;
7. corrección, retirada y eliminación;
8. URL canónica de postulación y criterio de elegibilidad para Perú;
9. canal responsable de confirmar permisos de cada vacante.

No se envió correo ni formulario en este bloque.

## Decisión

Canonical es la **candidata privada principal para continuar la resolución humana**, porque tiene un portal corporativo oficial, roles técnicos y una política remota explícita. No es una fuente compatible todavía: los términos visibles restringen el uso del contenido y no hay autorización de automatización o republicación. Permanece deshabilitada, sin presupuesto y fuera del flujo de consulta.

## Evaluación R4 y contrato condicionado

La revisión R4 del 2026-11-12 mantiene la decisión `pending_review`. La
existencia del portal, sus filtros o cualquier endpoint técnicamente accesible no
demuestra permiso para consultar automáticamente, conservar metadatos o
republicarlos en Ruta Sistemas. Por esa razón no se consultó ninguna vacante
individual, no se almacenó ninguna respuesta y no se implementó un adaptador
operativo.

Si Canonical autoriza expresamente un piloto, el contrato mínimo propuesto sería:

- **Consulta:** revisión manual de una ficha corporativa; automatización solo
  mediante el mecanismo, host, frecuencia e identificación que la respuesta
  escrita autorice.
- **Campos candidatos:** `employer`, `publisher`, `title`, `location`, `mode`,
  `eligibility`, `publishedAt`, `deadline` cuando aparezcan, `sourceUrl` y
  `applyUrl` canónicas. Los campos ausentes permanecen `null`/ausentes.
- **Evidencia:** cada valor publicado requiere URL HTTPS de la ficha original y
  `observedAt` con zona horaria; el canal debe comprobarse como abierto y
  correspondiente a la convocatoria concreta.
- **Retención y atribución:** solo metadatos mínimos autorizados, enlace a la
  ficha original, atribución indicada por Canonical y procedimiento de
  corrección/retirada.
- **Salida:** candidato local con `captureMethod: manual` o el método realmente
  autorizado y `editorialReview.status: pending_review`. Nunca promoción
  automática a seed, snapshot o Pages.
- **Límites:** máximo inicial de una convocatoria, presupuesto explícito,
  sin descripción completa, CV, datos personales, cookies, tokens ni contenido
  sujeto a autenticación.

La configuración actual conserva `enabled: false`, `decision: pending_review`,
`automatedAccessStatus: pending_review`, `publicReuseStatus: pending_review`,
`maxRequestsPerRun: 0` y `rightsReview: pending`. El bloqueo se considera
resuelto únicamente con autorización escrita suficiente y aprobación humana
separada de la ficha individual.

