# Bandeja editorial local

La bandeja separa una captura manual de la fuente canónica y del JSON público. No tiene interfaz ni servicio: usa un JSON local y un validador Python estándar. No se consulta ninguna fuente por red.

## Flujo

1. Copiar `inbox.example.json` a `inbox.local.json` (este último está ignorado por Git para no subir candidatos ni evidencia antes de revisar las condiciones de almacenamiento/publicación).
2. Comprobar que la fuente permita la consulta manual y el uso público de los metadatos concretos. Son permisos distintos de la extracción automática. No añadas el candidato a un repositorio público si la retención o republicación sigue pendiente.
3. Añadir una ficha a `candidates` con un `candidateId` estable, `sourceId` registrado, URL oficial, `capturedAt` ISO 8601 con zona, `captureMethod: manual`, los campos propuestos y referencias de evidencia por campo. Fechas civiles se anotan `YYYY-MM-DD`; lo desconocido queda `null`.
4. Ejecutar `python scripts/validate_candidates.py`. El comando solo lee y valida; nunca escribe en la bandeja, la semilla, el snapshot ni realiza solicitudes HTTP.
5. La revisión `approved_for_catalog` requiere revisor, fecha, motivo, permiso confirmado para el uso público, evidencia reciente y título/empleador/difusor/canal oficial de postulación. Este estado **no publica** nada. Una persona traslada manualmente los campos sustentados a `data/opportunities.seed.json` y completa `publisher`, `fieldEvidence` y `editorialDecision`; diferencia `sourceUrl` de `applyUrl`. Cada campo de procedencia, incluido el canal de postulación, debe usar HTTPS y hosts revisados explícitamente en `allowedHosts`.
6. Solo registra un campo en `proposed` si la fuente lo respalda; para puestos remotos registra ubicación y elegibilidad desde Perú únicamente si están explícitas. Deja salario, modalidad, plazo, formación, beneficios y requisitos desconocidos como `null` cuando no consten.
7. Confirma manualmente que el canal de postulación está abierto. Registra en `lastVerifiedAt` el momento de esa comprobación (ISO 8601 con zona); no uses `capturedAt` ni la fecha de generación en su lugar. Registra `publishedAt`, `deadline` y duración del empleo como conceptos distintos. Una fecha límite ausente no significa que la oportunidad siga abierta indefinidamente.
8. Para publicar como activa, establece estados separados (`opportunityStatus: open`, `verificationStatus: verified`, `publicationStatus: active`) solo después de la evidencia requerida. Mantén el TTL de siete días desde cada evidencia; regenerar el snapshot no renueva nada. `editorialDecision` incluye estado aprobado, revisor, fecha y razón. Si se rechaza, guarda la nota en la bandeja; si se retira después de publicar, conserva el registro como histórico con la razón.
9. Después de la transferencia manual ejecuta `python scripts/build_catalog.py --write`, `python scripts/build_catalog.py --check`, `python scripts/validate_catalog.py` y las pruebas. Revisa el diff de semilla y snapshot antes de aceptar los cambios. Ningún paso de la bandeja modifica esos archivos automáticamente.

La estructura para añadir dentro de `candidates` (completar solo lo observado) es:

```json
{
  "candidateId": "CAND-<id-estable>",
  "sourceId": "<id-de-collector/sources.json>",
  "sourceUrl": "https://<host-oficial>/<ficha>",
  "capturedAt": "YYYY-MM-DDTHH:mm:ss-05:00",
  "captureMethod": "manual",
  "proposed": {
    "title": null,
    "employer": null,
    "publisher": null,
    "externalReference": null,
    "applyUrl": null,
    "publishedAt": null,
    "deadline": null,
    "location": null,
    "mode": null,
    "opportunityType": null,
    "salary": null,
    "benefits": null,
    "requirements": null
  },
  "fieldEvidence": [],
  "editorialReview": {
    "status": "pending_review",
    "reviewer": null,
    "reviewedAt": null,
    "decisionNote": null
  }
}
```

Por cada campo propuesto que no sea `null`, añadir a `fieldEvidence` una entrada `{ "field": "...", "url": "https://...", "observedAt": "..." }`. Estos son marcadores de formato, no una oportunidad real ni un registro válido hasta ser completados y validados.

`inbox.local.json` es local y no tiene respaldo/versionado; hacer una copia segura manual si se necesita conservarlo. No introducir CV, DNI, emails personales ni copias extensas de convocatorias. El repositorio actual es público: no añadir candidatos ni datos cuya conservación/republicación no esté autorizada.

## Campos

- `sourceId`, `sourceUrl`, `capturedAt`, `captureMethod`: procedencia y captura, nunca prueba de vigencia.
- `proposed`: título, empleador real, entidad que difunde y demás campos tentativos; los valores desconocidos deben ser `null`.
- `fieldEvidence`: una referencia HTTPS y `observedAt` por cada valor no nulo; `note` debe ser una nota breve, no una copia de la descripción.
- `editorialReview`: `pending_review`, `approved_for_catalog` o `rejected`, independiente de oportunidad/verificación/publicación.
- No añadir `opportunityStatus`, `verificationStatus`, `publicationStatus` ni `lastVerifiedAt` al candidato.

## Comandos

```powershell
Copy-Item data/candidates/inbox.example.json data/candidates/inbox.local.json
python scripts/validate_candidates.py
python scripts/validate_candidates.py data/candidates/inbox.example.json
```

La bandeja vacía de ejemplo es válida. No hay importación automática ni comando para mutar el catálogo desde candidatos.
