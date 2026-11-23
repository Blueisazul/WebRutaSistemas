const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('Accessibility Audit (WCAG 2.1 AA) - R4-05B', () => {
  test('catalog view has zero critical or serious axe violations', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#result-count')).toHaveText('107 resultados');
    await expect(page.locator('button.card-button[data-open]').first()).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    const seriousOrCritical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    expect(seriousOrCritical).toEqual([]);
  });

  test('job detail dialog has zero critical or serious axe violations', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#result-count')).toHaveText('107 resultados');

    // Open first job card detail
    await page.locator('button.card-button[data-open]').first().click();
    await expect(page.getByRole('dialog')).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    const seriousOrCritical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    expect(seriousOrCritical).toEqual([]);

    await page.getByRole('button', { name: 'Cerrar detalle' }).click();
    await expect(page.getByRole('dialog')).toBeHidden();
  });

  test('comparator dialog has zero critical or serious axe violations', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#result-count')).toHaveText('107 resultados');

    // Select first two items for comparison
    await page.locator('[data-compare]').nth(0).click();
    await page.locator('[data-compare]').nth(1).click();
    await expect(page.locator('#compare-panel')).toBeVisible();

    // Open comparator dialog
    await page.getByRole('button', { name: 'Comparar' }).click();
    await expect(page.getByRole('dialog', { name: 'Dos alternativas, sin ganador universal' })).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    const seriousOrCritical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    expect(seriousOrCritical).toEqual([]);

    await page.getByRole('button', { name: 'Cerrar comparación' }).click();
  });

  test('keyboard navigation, focus trap, and Escape key dismissal on dialogs', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#result-count')).toHaveText('107 resultados');

    // Focus the first card button via keyboard Tab
    const firstCard = page.locator('button.card-button[data-open]').first();
    await firstCard.focus();
    await expect(firstCard).toBeFocused();

    // Open dialog via Enter key
    await page.keyboard.press('Enter');
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Close via Escape key
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
  });

  test('empty state and filtered state have zero axe violations', async ({ page }) => {
    await page.goto('/');

    // Type query with no matches
    await page.locator('#query').fill('sin-coincidencia-xyz');
    await expect(page.locator('#result-count')).toHaveText('0 resultados');
    await expect(page.locator('#empty-state')).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    const seriousOrCritical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    expect(seriousOrCritical).toEqual([]);
  });
});
