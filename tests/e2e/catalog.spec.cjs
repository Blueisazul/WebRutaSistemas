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
  await expect(page.locator('#empty-state h3')).toHaveText('No hay oportunidades verificadas disponibles');
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
  await expect(page.locator('#dialog-content')).toContainText('Decisión editorial');
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
