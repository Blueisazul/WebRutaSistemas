# AUDITORÍA TÉCNICA Y DE REMEDIACIÓN: TASK-FIX-E2E-R5-05
## Corrección de Pruebas E2E tras la Integración de Normalización Geográfica

- **Identificador de Tarea:** `TASK-FIX-E2E-R5-05`
- **Proyecto:** Velora (`WebRutaSistemas`)
- **Fase:** R5 — Cobertura nacional de oportunidades
- **Prioridad:** P0 (Bloqueante de CI y despliegue a GitHub Pages)
- **Clasificación:** `[REFACTOR/FIX]` + `[REUTILIZACIÓN_INTERNA]`
- **Fecha de Ejecución:** 27 de noviembre de 2026
- **Estado de Tarea:** `COMPLETED_LOCALLY` (Verificado localmente en suite E2E completa de 45 pruebas Playwright en Chromium, Mobile y Narrow; pendiente de commit y push)

---

## 1. Causa Raíz

En la consolidación técnica `TASK-FIX-URL-01` + `TASK-R5-05` (commit `f861e06899604bd08dcd8f05c6a4244c6621c308`), se implementó la normalización geográfica tridimensional. Como parte de la experiencia de usuario de `TASK-R5-05`, el modal y vista de detalle de la oportunidad (`app.js`, líneas 780-786) incorporaron una nueva tarjeta de resumen visual:

```javascript
  const scopeKey = getJobGeographicScope(job);
  const scopeDef = GEOGRAPHIC_SCOPES[scopeKey] || GEOGRAPHIC_SCOPES.UNSPECIFIED;
  summaryCards.push({
    icon: 'pin',
    label: 'Ámbito territorial',
    value: escapeHTML(scopeDef.label),
  });
```

Esta incorporación elevó el número de tarjetas de resumen en la sección `.summary-section` de 6 a 7 para la vacante de prueba `OP-005` (CookUnity).

La suite de pruebas E2E en `tests/e2e/catalog.spec.cjs:227` mantenía una aserción fija estricta heredada de la fase anterior R7:
```javascript
  const summaryCards = summarySection.locator('.summary-card');
  await expect(summaryCards).toHaveCount(6);
  await expect(summarySection.locator('.summary-card svg')).toHaveCount(6);
```

Al ejecutarse el pipeline de GitHub Actions (`refresh-catalog.yml`, Run ID `46055123843`), el paso `Exercise browser flows` (`npm run test:e2e`) falló con:
`Error: expect(locator).toHaveCount(expected) failed: Expected 6, Received 7`.

Dado que el job `validate` falló, el job dependiente `publish` fue omitido (`skipped`), impidiendo que GitHub Pages se desplegara con la nueva versión del catálogo y los filtros territoriales.

---

## 2. Expectativa Anterior vs. Comportamiento Real de la Interfaz

| Aspecto | Expectativa Anterior (R7) | Comportamiento Real Aprobado (R5-05) |
|---|---|---|
| **Número de tarjetas en `OP-005`** | 6 tarjetas | **7 tarjetas** (incorporación de tarjeta de Ámbito territorial) |
| **Iconos SVG en `OP-005`** | 6 iconos SVG Lucide | **7 iconos SVG Lucide** (icono `pin` para ámbito territorial) |
| **Tarjeta de Ámbito territorial** | No existía / No testeada | Presente: `<label>Ámbito territorial</label><p>Empleo en Perú (Presencial/Híbrido)</p>` |
| **Número de tarjetas en `OP-002`** | 7 tarjetas | **8 tarjetas** (incorporación de tarjeta de Ámbito territorial) |
| **Número de tarjetas en `OP-001`** | 9 tarjetas | **10 tarjetas** (incorporación de tarjeta de Ámbito territorial) |

---

## 3. Cambios Concretos Realizados

En `tests/e2e/catalog.spec.cjs`:

1. **Actualización de conteos para `OP-005`:**
   - Actualizado `toHaveCount(6)` a `toHaveCount(7)` tanto para `.summary-card` como para `.summary-card svg`.
2. **Aserción funcional explícita del Ámbito Territorial (`TASK-R5-05`):**
   ```javascript
   const scopeCard = summarySection.locator('.summary-card:has(label:has-text("Ámbito territorial"))');
   await expect(scopeCard).toBeVisible();
   await expect(scopeCard).toContainText('Empleo en Perú (Presencial/Híbrido)');
   await expect(scopeCard.locator('svg')).toBeVisible();
   ```
3. **Validación individual de las otras 6 tarjetas para prevenir regresiones:**
   - `Entidad que difunde`: contiene `'CookUnity'`.
   - `Ubicación y elegibilidad`: contiene `'Lima, Perú'`.
   - `Contrato y plazo`: contiene `'Full-time'`.
   - `Régimen y modalidad`: contiene `'Modalidad no especificada'`.
   - `Fecha de publicación`: visible.
   - `Última verificación o consulta`: contiene `'Requiere revalidar'`.
4. **Validación de integridad visual (sin tarjetas vacías ni duplicadas):**
   - Bucle `for (const card of await summaryCards.all())` verificando que cada tarjeta tenga etiqueta y párrafo de valor no vacíos.
5. **Actualización de conteos y verificación de ámbito para `OP-002` y `OP-001`:**
   - `OP-002`: actualizado conteo a 8 tarjetas y verificado que Ámbito territorial muestre `'Ámbito no especificado'` (clasificación fail-closed para demostración).
   - `OP-001`: actualizado conteo a 10 tarjetas y verificado que Ámbito territorial muestre `'Empleo en Perú (Presencial/Híbrido)'`.

---

## 4. Archivos Modificados

- `tests/e2e/catalog.spec.cjs`: Actualización de aserciones de tarjetas de resumen y adición de verificaciones semánticas de ámbito territorial.
- `docs/audits/TASK-FIX-E2E-R5-05.md`: Informe técnico de auditoría y remediación (este documento).
- `docs/roadmap/VELORA-MASTER-ROADMAP.md`: Registro de la tarea de remediación `TASK-FIX-E2E-R5-05` vinculada a R5-05.

---

## 5. Pruebas Ejecutadas y Resultados Verificables

1. **Prueba específica en Chromium:**
   - `npx playwright test tests/e2e/catalog.spec.cjs -g "redesigns opportunity detail" --project=chromium`
   - Resultado: **PASÓ** (1 passed en 20.4s).
2. **Prueba específica en los tres proyectos de Playwright:**
   - `npx playwright test tests/e2e/catalog.spec.cjs -g "redesigns opportunity detail"`
   - Proyectos: `chromium`, `mobile`, `narrow`.
   - Resultado: **PASÓ** (3 passed en 59.5s).
3. **Suite completa E2E:**
   - `npm run test:e2e` (45 pruebas en 3 viewports).
   - Resultado: Verificado al 100%.
4. **Validaciones de Regresión:**
   - `node --check app.js`: **0 errores de sintaxis**.
   - `node tests/catalog_ui.test.cjs`: **PASÓ** (escenarios de filtrado de catálogo, rutas Pages y degradación).
   - `python -m unittest discover -s tests -v`: **PASÓ** (342 pruebas pasando al 100%).
   - `python scripts/build_catalog.py --check --as-of 2026-11-23`: **PASÓ** (112 registros válidos, snapshot coincide bit a bit con fuente canónica).

---

## 6. Distinción de Entornos y Estado de Despliegue

| Entorno / Instancia | Commit en Ejecución | Estado de TASK-FIX-URL-01 / R5-05 | Estado de Pruebas E2E |
|---|---|---|---|
| **Local (Árbol de trabajo)** | `f861e06` + fix local | Implementado y remediado | **100% pasando (45/45 E2E, 342 Python)** |
| **Remoto (`origin/main`)** | `f861e06` | Integrado en Git | Fallo en CI (Run `46055123843`) pendiente de fix |
| **Vercel Production** | `f861e06` | **Desplegado y 100% operativo** | Operativo (despliegue desatendido directo) |
| **GitHub Pages Production** | `6b754da` (`v0.7.0`) | **Desfasado (no desplegado)** | Bloqueado por fallo en job `validate` |

---

## 7. Limitaciones

- La confirmación definitiva de la resolución de GitHub Pages depende de que este cambio sea comprometido y enviado a `origin/main` para que el workflow `refresh-catalog.yml` ejecute exitosamente los jobs `validate` y `publish`.
- En esta sesión no se ejecutó commit ni push, respetando la directiva de autonomía del usuario.

---

## 8. Próximo Paso Recomendado

1. Someter a revisión del propietario este informe y la modificación en `tests/e2e/catalog.spec.cjs`.
2. Con la autorización expresa del propietario:
   - Crear un commit atómico: `fix(tests): update summary card count and assert territorial scope card in E2E suite (TASK-FIX-E2E-R5-05)`.
   - Ejecutar `git push origin main`.
   - Verificar la ejecución exitosa de `refresh-catalog.yml` (jobs `validate` y `publish`).
   - Confirmar en vivo que GitHub Pages alcance la paridad con Vercel.
