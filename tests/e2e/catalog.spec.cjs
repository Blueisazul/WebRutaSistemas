const { test, expect } = require('@playwright/test');

async function enableExamples(page) {
  await page.getByRole('checkbox', { name: 'Incluir ejemplos demostrativos' }).check();
  await expect(page.locator('#result-count')).toHaveText('6 resultados');
}

function trackRuntimeProblems(page) {
  const problems = [];
  page.on('console', (message) => {
    if (message.type() === 'error') problems.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => problems.push(`page: ${error.message}`));
  page.on('requestfailed', (request) => problems.push(`request: ${request.url()} (${request.failure()?.errorText})`));
  return problems;
}

test('loads the catalog and displays active verified opportunities with empty state on zero matches', async ({ page }) => {
  const problems = trackRuntimeProblems(page);
  await page.goto('/');

  await expect(page).toHaveTitle('Ruta Sistemas');
  await expect(page.locator('#result-count')).toHaveText('1 resultado');
  await expect(page.locator('#job-list')).toBeVisible();
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(1);
  await expect(page.locator('#job-list')).toContainText('Supply Chain Analyst');
  await expect(page.locator('#job-list')).toContainText('CookUnity');

  // Verify empty state when filter has zero matches
  await page.locator('#query').fill('no-coincide-xyz');
  await expect(page.locator('#result-count')).toHaveText('0 resultados');
  await expect(page.locator('#empty-state h3')).toHaveText('No encontramos coincidencias para esta búsqueda');
  await expect(page.locator('#job-list')).toBeHidden();

  await page.locator('#clear-filters').click();
  await expect(page.locator('#result-count')).toHaveText('1 resultado');

  await page.keyboard.press('/');
  await expect(page.locator('#query')).toBeFocused();
  expect(problems).toEqual([]);
});

test('filters examples and active opportunities by mode, level, location, and reset', async ({ page }) => {
  await page.goto('/');
  await enableExamples(page);

  await page.locator('#mode').selectOption({ label: 'Remoto' });
  await expect(page.locator('#result-count')).toHaveText('3 resultados');
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(3);

  await page.locator('#level').selectOption({ label: 'Senior' });
  await expect(page.locator('#result-count')).toHaveText('2 resultados');

  await page.locator('#location').fill('Perú');
  await expect(page.locator('#result-count')).toHaveText('2 resultados');

  await page.locator('#clear-filters').click();
  await expect(page.locator('#result-count')).toHaveText('6 resultados');
  await expect(page.locator('#mode')).toHaveValue('');
  await expect(page.locator('#level')).toHaveValue('');
  await expect(page.locator('#location')).toHaveValue('');
});

test('opens a detail and compares two explicitly selected items', async ({ page }) => {
  await page.goto('/');

  // Real active opportunity (OP-005) detail
  await page.locator('button.card-button[data-open]').first().click();
  await expect(page.getByRole('dialog', { name: 'Supply Chain Analyst' })).toBeVisible();
  await expect(page.locator('#dialog-content')).toContainText('CookUnity');
  await expect(page.locator('#dialog-content')).toContainText('Ir a postulación');
  await expect(page.locator('#dialog-content')).toContainText('Qué se verificó');
  await expect(page.locator('#dialog-content')).toContainText('Fuente oficial verificada');
  await expect(page.locator('#dialog-content')).toContainText('Resumen');
  await expect(page.locator('#dialog-content')).toContainText('1+ años de experiencia previa');
  await expect(page.locator('#dialog-content')).not.toContainText('Triaje rápido');
  await expect(page.locator('#dialog-content')).not.toContainText('Decisión editorial');
  await expect(page.locator('#dialog-content')).not.toContainText('Evaluación del empleador');
  await page.getByRole('button', { name: 'Cerrar detalle' }).click();
  await expect(page.getByRole('dialog', { name: 'Supply Chain Analyst' })).toBeHidden();

  // Demonstration item detail
  await enableExamples(page);
  const demoCard = page.locator('button.card-button[data-open="OP-003"]');
  await demoCard.click();
  await expect(page.getByRole('dialog', { name: 'Android Developer' })).toBeVisible();
  await expect(page.locator('#dialog-content')).toContainText('Ficha de demostración');
  await expect(page.locator('#dialog-content')).toContainText('Postulación deshabilitada');
  await expect(page.locator('#dialog-content')).toContainText('Fecha de publicación');
  await expect(page.locator('#dialog-content')).toContainText('Última verificación o consulta');
  await page.getByRole('button', { name: 'Cerrar detalle' }).click();
  await expect(page.getByRole('dialog', { name: 'Android Developer' })).toBeHidden();

  // Keyboard navigation
  await demoCard.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('dialog', { name: 'Android Developer' })).toBeVisible();
  await page.getByRole('button', { name: 'Cerrar detalle' }).click();

  // Compare two items
  await page.locator('[data-compare]').nth(0).click();
  await page.locator('[data-compare]').nth(1).click();
  await expect(page.locator('#compare-panel')).toBeVisible();
  await expect(page.locator('#compare-open')).toBeEnabled();
  await page.getByRole('button', { name: 'Comparar' }).click();
  await expect(page.getByRole('dialog', { name: 'Dos alternativas, sin ganador universal' })).toBeVisible();
  await expect(page.locator('#compare-content')).toContainText('SIN PUNTUACIÓN');
  await page.getByRole('button', { name: 'Cerrar comparación' }).click();

  await page.getByRole('button', { name: 'Quitar selección' }).click();
  await expect(page.locator('#compare-panel')).toBeHidden();
});

test('keeps the main flow usable on a narrow viewport', async ({ page }) => {
  await page.goto('/');
  await enableExamples(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  await page.locator('button.card-button[data-open]').first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Cerrar detalle' })).toBeVisible();
});

test('navigates directly to standalone opportunity view via URL and returns to catalog', async ({ page }) => {
  const problems = trackRuntimeProblems(page);
  await page.goto('/?id=OP-005');

  await expect(page).toHaveTitle(/Supply Chain Analyst · CookUnity — Ruta Sistemas/);
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('#catalog-view')).toBeHidden();
  await expect(page.locator('#opportunity-view')).toContainText('Supply Chain Analyst');
  await expect(page.locator('#opportunity-view')).toContainText('CookUnity');
  await expect(page.locator('#opportunity-view')).toContainText('Fuente oficial verificada');
  await expect(page.locator('#opportunity-view')).not.toContainText('Decisión editorial');
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');

  // Return to catalog
  await page.locator('[data-action="back-to-catalog"]').first().click();
  await expect(page.locator('#catalog-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).toBeHidden();
  await expect(page).toHaveTitle('Ruta Sistemas');

  // Not found scenario
  await page.goto('/?id=OP-999');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).toContainText('Oportunidad no encontrada');
  await page.locator('[data-action="back-to-catalog"]').click();
  await expect(page.locator('#catalog-view')).toBeVisible();

  // Hash routing compatibility: #/oportunidad/OP-005
  await page.goto('/#/oportunidad/OP-005');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).toContainText('CookUnity');
  await page.locator('[data-action="back-to-catalog"]').first().click();
  await expect(page.locator('#catalog-view')).toBeVisible();

  // In-page anchor navigation (e.g. #inicio) should NOT trigger 404
  await page.goto('/#inicio');
  await expect(page.locator('#catalog-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).toBeHidden();

  expect(problems).toEqual([]);
});

test('renders cleanly without horizontal overflow across desktop, tablet, and mobile', async ({ page }) => {
  const viewports = [
    { width: 1440, height: 900, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 390, height: 844, name: 'mobile' },
  ];

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto('/');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBe(true);

    // Check standalone detail view
    await page.goto('/?id=OP-005');
    await expect(page.locator('#opportunity-view')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBe(true);
    await expect(page.locator('.summary-grid')).toBeVisible();
  }
});

test('redesigns opportunity detail with verified source, icon summary, omission rules, and Tailwind (UX-EXP-05)', async ({ page }) => {
  const problems = trackRuntimeProblems(page);

  // 1. Check OP-005 (Real opportunity: CookUnity - Supply Chain Analyst)
  await page.goto('/?id=OP-005');
  await expect(page.locator('#opportunity-view')).toBeVisible();

  // A. Triaje rápido is completely eliminated
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');
  await expect(page.locator('.triage-section, .triage-grid, .triage-card')).toHaveCount(0);

  // B. Fuente oficial verificada appears at the top
  const officialHero = page.locator('.official-source-hero');
  await expect(officialHero).toBeVisible();
  await expect(officialHero).toContainText('✓ Fuente oficial verificada');
  await expect(officialHero).toContainText('CookUnity');
  await expect(officialHero.locator('a.btn-source')).toBeVisible();
  await expect(officialHero.locator('a.btn-apply-main')).toBeVisible();

  // C. Resumen with Lucide SVG icons
  const summarySection = page.locator('.summary-section');
  await expect(summarySection).toBeVisible();
  await expect(summarySection.locator('h3')).toContainText('Resumen');

  // OP-005 has exactly 5 verified cards (difusor, ubicación, contrato, fecha pub, última verif)
  const summaryCards = summarySection.locator('.summary-card');
  await expect(summaryCards).toHaveCount(5);
  // Verify Lucide SVG icons are present in each card
  await expect(summarySection.locator('.summary-card svg')).toHaveCount(5);

  // D. Strict omission rules: unknown fields are omitted without placeholder texts
  await expect(summarySection.locator('.summary-card:has(label:has-text("Modalidad"))')).toHaveCount(0);
  await expect(summarySection.locator('.summary-card:has(label:has-text("Compensación"))')).toHaveCount(0);
  await expect(summarySection.locator('.summary-card:has(label:has-text("Fecha límite"))')).toHaveCount(0);
  await expect(page.locator('#opportunity-view')).not.toContainText('No informado en la convocatoria pública');
  await expect(page.locator('#opportunity-view')).not.toContainText('sujeto a desempeño');
  await expect(page.locator('#opportunity-view')).not.toContainText('evaluación del empleador');

  // E. Tecnologías y herramientas declaradas appears below Resumen as visual tags
  const skillsSection = page.locator('.skills-section');
  await expect(skillsSection).toBeVisible();
  await expect(skillsSection).toContainText('Tecnologías y herramientas declaradas');
  await expect(skillsSection.locator('span:has-text("SQL")')).toBeVisible();
  await expect(skillsSection.locator('span:has-text("Analítica de operaciones")')).toBeVisible();
  await expect(skillsSection.locator('span:has-text("Google Sheets")')).toBeVisible();
  await expect(skillsSection.locator('span:has-text("ERP/MRP")')).toBeVisible();

  // F. Qué se verificó appears after Tecnologías y herramientas
  const verificationSection = page.locator('.verification-section');
  await expect(verificationSection).toBeVisible();
  await expect(verificationSection.locator('.evidence-box')).toContainText('Qué se verificó');
  await expect(verificationSection.locator('.evidence-collapsible summary')).toContainText('Procedencia por dato (21 campos registrados)');

  // G. OP-005 retains Junior level and 1+ years requirement
  await expect(page.locator('.opportunity-header')).toContainText('Junior');
  const reqSection = page.locator('.detail-section:has(h3:has-text("Requisitos del puesto"))');
  await expect(reqSection).toContainText('1+ años de experiencia previa');

  // 2. Check OP-002 (Demonstration with remote modality, no salary/deadline)
  await page.goto('/?id=OP-002');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');
  const op2Summary = page.locator('.summary-section .summary-card');
  // OP-002 has 6 cards (modalidad, difusor, ubicación, contrato, fecha pub, última verif)
  await expect(op2Summary).toHaveCount(6);
  await expect(page.locator('.summary-card:has(label:has-text("Modalidad"))')).toContainText('Remoto');
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toHaveCount(0);
  await expect(page.locator('.summary-card:has(label:has-text("Fecha límite"))')).toHaveCount(0);

  // 3. Check OP-001 (Demonstration with all 8 conditions including salary and deadline)
  await page.goto('/?id=OP-001');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  const op1Summary = page.locator('.summary-section .summary-card');
  await expect(op1Summary).toHaveCount(8);
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toBeVisible();
  await expect(page.locator('.summary-card:has(label:has-text("Fecha límite"))')).toBeVisible();

  // 4. Check QA-001 (Closed demonstration)
  await page.goto('/?id=QA-001');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toHaveCount(0);

  expect(problems).toEqual([]);
});
