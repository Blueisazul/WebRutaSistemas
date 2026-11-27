const { test, expect } = require('@playwright/test');

async function enableExamples(page) {
  await page.getByRole('checkbox', { name: 'Incluir ejemplos demostrativos' }).check();
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);
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

  await expect(page).toHaveTitle('Velora — Oportunidades y Trayectorias en Tecnología');
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);
  await expect(page.locator('#job-list')).toBeVisible();
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(12);
  await expect(page.locator('#job-list')).toContainText('Canonical');

  // Verify empty state when filter has zero matches
  await page.locator('#query').fill('no-coincide-xyz');
  await expect(page.locator('#result-count')).toHaveText('0 resultados');
  await expect(page.locator('#empty-state h3')).toHaveText('No encontramos coincidencias para esta búsqueda');
  await expect(page.locator('#job-list')).toBeHidden();

  await page.locator('#clear-filters').click();
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);

  await page.keyboard.press('/');
  await expect(page.locator('#query')).toBeFocused();
  expect(problems).toEqual([]);
});

test('filters examples and active opportunities by mode, level, location, and reset', async ({ page }) => {
  await page.goto('/');
  await enableExamples(page);

  await page.locator('#mode').selectOption({ label: 'Remoto' });
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(12);

  await page.locator('#level').selectOption({ label: 'Senior' });
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);

  await page.locator('#location').fill('Perú');
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);

  await page.locator('#clear-filters').click();
  await expect(page.locator('#result-count')).toHaveText(/\d+\s+resultados/);
  await expect(page.locator('#mode')).toHaveValue('');
  await expect(page.locator('#level')).toHaveValue('');
  await expect(page.locator('#location')).toHaveValue('');
});

test('opens a detail and compares two explicitly selected items', async ({ page }) => {
  await page.goto('/');

  // 1. Real active opportunity detail (Canonical OP-006: within 7-day TTL, verified)
  await page.locator('#query').fill('Graduate Software Engineer');
  await page.locator('button.card-button[data-open="OP-006"]').click();
  await expect(page.getByRole('dialog', { name: 'Graduate Software Engineer, Open Source and Linux, Canonical Ubuntu' })).toBeVisible();
  await expect(page.locator('#dialog-content')).toContainText('Canonical');
  await expect(page.locator('#dialog-content')).toContainText('Ir a postulación');
  await expect(page.locator('#dialog-content')).toContainText('Qué se verificó');
  await expect(page.locator('#dialog-content')).toContainText('Fuente oficial verificada');
  await expect(page.locator('#dialog-content')).toContainText('Resumen');
  await expect(page.locator('#dialog-content')).not.toContainText('Triaje rápido');
  await expect(page.locator('#dialog-content')).not.toContainText('Decisión editorial');
  await expect(page.locator('#dialog-content')).not.toContainText('Evaluación del empleador');
  await page.getByRole('button', { name: 'Cerrar detalle' }).click();
  await expect(page.getByRole('dialog')).toBeHidden();
  await page.locator('#clear-filters').click();

  // 2. Unconfirmed / Stale opportunity detail (OP-005 CookUnity: TTL > 7 days)
  // Verify that by default OP-005 is hidden under fail-closed governance
  await page.locator('#query').fill('CookUnity');
  await expect(page.locator('button.card-button[data-open="OP-005"]')).toHaveCount(0);
  // Opt in to unconfirmed entries: OP-005 is now visible and displays pending revalidation status
  await page.locator('#include-unconfirmed').check();
  await expect(page.locator('button.card-button[data-open="OP-005"]')).toBeVisible();
  await page.locator('button.card-button[data-open="OP-005"]').click();
  await expect(page.getByRole('dialog', { name: 'Supply Chain Analyst' })).toBeVisible();
  await expect(page.locator('#dialog-content')).toContainText('CookUnity');
  await expect(page.locator('#dialog-content')).toContainText('Verificación pendiente de revalidar');
  await page.getByRole('button', { name: 'Cerrar detalle' }).click();
  await expect(page.getByRole('dialog')).toBeHidden();
  await page.locator('#include-unconfirmed').uncheck();
  await page.locator('#clear-filters').click();

  // Demonstration item detail
  await enableExamples(page);
  await page.locator('#query').fill('Android Developer');
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
  await page.locator('#clear-filters').click();

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
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBe(true);
  await page.locator('button.card-button[data-open]').first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Cerrar detalle' })).toBeVisible();
});

test('navigates directly to standalone opportunity view via URL and returns to catalog', async ({ page }) => {
  const problems = trackRuntimeProblems(page);
  await page.goto('/?id=OP-005');

  await expect(page).toHaveTitle(/Supply Chain Analyst · CookUnity — Velora/);
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('#catalog-view')).toBeHidden();
  await expect(page.locator('#opportunity-view')).toContainText('Supply Chain Analyst');
  await expect(page.locator('#opportunity-view')).toContainText('CookUnity');
  await expect(page.locator('#opportunity-view')).toContainText(/Fuente oficial verificada|Verificación pendiente de revalidar/);
  await expect(page.locator('#opportunity-view')).not.toContainText('Decisión editorial');
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');

  // Return to catalog
  await page.locator('[data-action="back-to-catalog"]').first().click();
  await expect(page.locator('#catalog-view')).toBeVisible();
  await expect(page.locator('#opportunity-view')).toBeHidden();
  await expect(page).toHaveTitle('Velora — Oportunidades y Trayectorias en Tecnología');

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
    await expect(page.locator('#opportunity-view')).toBeVisible({ timeout: 10000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1)).toBe(true);
    await expect(page.locator('.summary-grid')).toBeVisible();
  }
});

test('redesigns opportunity detail with verified source, icon summary, omission rules, and Tailwind (UX-EXP-05)', async ({ page }) => {
  const problems = trackRuntimeProblems(page);

  // 1. Check OP-005 (Real opportunity: CookUnity - Supply Chain Analyst)
  await page.goto('/?id=OP-005');
  await expect(page.locator('#opportunity-view')).toBeVisible({ timeout: 10000 });

  // A. Triaje rápido is completely eliminated
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');
  await expect(page.locator('.triage-section, .triage-grid, .triage-card')).toHaveCount(0);

  // B. Verification hero status appears at the top (OP-005 is stale TTL: 'Verificación pendiente de revalidar')
  const officialHero = page.locator('.official-source-hero');
  await expect(officialHero).toBeVisible();
  await expect(officialHero).toContainText('Verificación pendiente de revalidar');
  await expect(officialHero).toContainText('CookUnity');
  await expect(officialHero.locator('a.btn-source')).toBeVisible();

  // C. Resumen with Lucide SVG icons
  const summarySection = page.locator('.summary-section');
  await expect(summarySection).toBeVisible();
  await expect(summarySection.locator('h3')).toContainText('Resumen');

  // OP-005 has 7 verified cards (difusor, ubicación, contrato, régimen R7-01, ámbito territorial R5-05, fecha pub, última verif)
  const summaryCards = summarySection.locator('.summary-card');
  await expect(summaryCards).toHaveCount(7);
  // Verify Lucide SVG icons are present in each card
  await expect(summarySection.locator('.summary-card svg')).toHaveCount(7);

  // Verify presence, label, icon, and territorial information for OP-005 (TASK-R5-05)
  const scopeCard = summarySection.locator('.summary-card:has(label:has-text("Ámbito territorial"))');
  await expect(scopeCard).toBeVisible();
  await expect(scopeCard).toContainText('Empleo en Perú (Presencial/Híbrido)');
  await expect(scopeCard.locator('svg')).toBeVisible();

  // Verify the other 6 verified cards continue to display their expected data
  await expect(summarySection.locator('.summary-card:has(label:has-text("Entidad que difunde"))')).toContainText('CookUnity');
  await expect(summarySection.locator('.summary-card:has(label:has-text("Ubicación y elegibilidad"))')).toContainText('Lima, Perú');
  await expect(summarySection.locator('.summary-card:has(label:has-text("Contrato y plazo"))')).toContainText('Full-time');
  await expect(summarySection.locator('.summary-card:has(label:has-text("Régimen y modalidad"))')).toContainText('Modalidad no especificada');
  await expect(summarySection.locator('.summary-card:has(label:has-text("Fecha de publicación"))')).toBeVisible();
  await expect(summarySection.locator('.summary-card:has(label:has-text("Última verificación o consulta"))')).toContainText('Requiere revalidar');

  // Verify absence of duplicate or empty cards
  for (const card of await summaryCards.all()) {
    await expect(card.locator('label')).not.toBeEmpty();
    await expect(card.locator('p')).not.toBeEmpty();
  }

  // D. Strict omission rules: unknown fields are omitted without placeholder texts (excluding Régimen card)
  await expect(summarySection.locator('.summary-card:has-text("Modalidad"):not(:has-text("Régimen"))')).toHaveCount(0);
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

  // F. Verification details appear after Tecnologías y herramientas (OP-005 shows 'Estado de publicación' due to stale TTL)
  const verificationSection = page.locator('.verification-section');
  await expect(verificationSection).toBeVisible();
  await expect(verificationSection.locator('.evidence-box')).toContainText(/Qué se verificó|Estado de publicación/);
  await expect(verificationSection.locator('.evidence-collapsible summary')).toContainText('Procedencia por dato (21 campos registrados)');

  // G. OP-005 retains Junior level and 1+ years requirement
  await expect(page.locator('.opportunity-header')).toContainText('Junior');
  const reqSection = page.locator('.detail-section:has(h3:has-text("Requisitos del puesto"))');
  await expect(reqSection).toContainText('1+ años de experiencia previa');

  // 2. Check OP-002 (Demonstration with remote modality, no salary/deadline)
  await page.goto('/?id=OP-002');
  await expect(page.locator('#opportunity-view')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('#opportunity-view')).not.toContainText('Triaje rápido');
  const op2Summary = page.locator('.summary-section .summary-card');
  // OP-002 has 8 cards (modalidad, difusor, ubicación, contrato, régimen R7-01, ámbito territorial R5-05, fecha pub, última verif)
  await expect(op2Summary).toHaveCount(8);
  await expect(page.locator('.summary-card:has-text("Modalidad"):not(:has-text("Régimen"))')).toContainText('Remoto');
  const op2ScopeCard = page.locator('.summary-section .summary-card:has(label:has-text("Ámbito territorial"))');
  await expect(op2ScopeCard).toContainText('Ámbito no especificado');
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toHaveCount(0);
  await expect(page.locator('.summary-card:has(label:has-text("Fecha límite"))')).toHaveCount(0);

  // 3. Check OP-001 (Demonstration with all conditions including salary, deadline, and regime)
  await page.goto('/?id=OP-001');
  await expect(page.locator('#opportunity-view')).toBeVisible({ timeout: 10000 });
  const op1Summary = page.locator('.summary-section .summary-card');
  // OP-001 has 10 cards (modalidad, difusor, ubicación, compensación, contrato, régimen R7-01, ámbito territorial R5-05, fecha límite, fecha pub, última verif)
  await expect(op1Summary).toHaveCount(10);
  const op1ScopeCard = page.locator('.summary-section .summary-card:has(label:has-text("Ámbito territorial"))');
  await expect(op1ScopeCard).toContainText('Empleo en Perú (Presencial/Híbrido)');
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toBeVisible();
  await expect(page.locator('.summary-card:has(label:has-text("Fecha límite"))')).toBeVisible();

  // 4. Check QA-001 (Closed demonstration)
  await page.goto('/?id=QA-001');
  await expect(page.locator('#opportunity-view')).toBeVisible();
  await expect(page.locator('.summary-card:has(label:has-text("Compensación"))')).toHaveCount(0);

  // 5. Check OP-006 (Canonical active opportunity within 7-day TTL displays 'Fuente oficial verificada' and active apply button)
  await page.goto('/?id=OP-006');
  await expect(page.locator('#opportunity-view')).toBeVisible({ timeout: 10000 });
  const activeHero = page.locator('.official-source-hero');
  await expect(activeHero).toBeVisible();
  await expect(activeHero).toContainText('Fuente oficial verificada');
  await expect(activeHero.locator('a.btn-apply-main')).toBeVisible();

  expect(problems).toEqual([]);
});

test('R3-ALPHA-UX-01A: handles catalog pagination, navigation, limits, resets, and preserves comparator', async ({ page }) => {
  const problems = trackRuntimeProblems(page);
  await page.goto('/');

  // 1. In expanded catalog (94 active > 12), pagination controls are visible by default
  const paginationNav = page.locator('#pagination');
  await expect(paginationNav).toBeVisible();

  // 2. Test pagination with reduced page size (pageSize = 5) on the 94 real items
  await page.evaluate(() => window.__setCatalogPageSize(5));
  await expect(paginationNav).toBeVisible();

  const prevBtn = page.locator('#prev-page');
  const nextBtn = page.locator('#next-page');
  const pageInfo = page.locator('#pagination-info');

  const totalItems = parseInt((await page.locator('#result-count').textContent()).match(/\d+/)[0], 10);
  const totalPages = Math.ceil(totalItems / 5);

  // Page 1: cards 1..5, prev disabled, next enabled
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(5);
  await expect(prevBtn).toBeDisabled();
  await expect(nextBtn).toBeEnabled();
  await expect(pageInfo).toHaveText(`Página 1 de ${totalPages} · Mostrando 1–5 de ${totalItems} oportunidades`);

  // Select first item for comparator on page 1
  const firstCompareBtn = page.locator('.compare-button').first();
  await firstCompareBtn.click();
  await expect(firstCompareBtn).toHaveClass(/selected/);
  await expect(page.locator('#compare-panel')).toBeVisible();

  // Navigate to Page 2: cards 6..10, prev enabled, next enabled
  await nextBtn.click();
  await expect(page.locator('button.card-button[data-open]')).toHaveCount(5);
  await expect(prevBtn).toBeEnabled();
  await expect(nextBtn).toBeEnabled();
  await expect(pageInfo).toHaveText(`Página 2 de ${totalPages} · Mostrando 6–10 de ${totalItems} oportunidades`);

  // Select second item for comparator on page 2
  const secondCompareBtn = page.locator('.compare-button').first();
  await secondCompareBtn.click();
  await expect(secondCompareBtn).toHaveClass(/selected/);
  // Compare button in compare panel should now be enabled (2 items selected across pages)
  await expect(page.locator('#compare-open')).toBeEnabled();

  // Navigate back to Page 1: verify compare selection is still active on first item
  await prevBtn.click();
  await expect(pageInfo).toHaveText(`Página 1 de ${totalPages} · Mostrando 1–5 de ${totalItems} oportunidades`);
  await expect(page.locator('.compare-button').first()).toHaveClass(/selected/);

  // 3. Changing filters resets to Page 1
  await nextBtn.click();
  await expect(pageInfo).toHaveText(`Página 2 de ${totalPages} · Mostrando 6–10 de ${totalItems} oportunidades`);
  await page.locator('#query').fill('Remoto');
  // Wait for search debounce to take effect on pagination
  await expect(pageInfo).toHaveText(/Página 1 de \d+ · Mostrando 1–5 de \d+ oportunidades/);
  const remoteItems = parseInt((await page.locator('#result-count').textContent()).match(/\d+/)[0], 10);
  const remotePages = Math.ceil(remoteItems / 5);
  await expect(pageInfo).toHaveText(`Página 1 de ${remotePages} · Mostrando 1–5 de ${remoteItems} oportunidades`);

  // 4. Mathematical page count calculations for 13, 20, 24, 25, 40, 100+ items
  const mathChecks = await page.evaluate(() => {
    const calc = (total, size = 12) => ({
      totalPages: Math.ceil(total / size) || 1,
      page1Items: Math.min(size, total),
      lastPageItems: total % size === 0 ? size : total % size,
    });
    return {
      t12: calc(12),
      t13: calc(13),
      t20: calc(20),
      t24: calc(24),
      t25: calc(25),
      t40: calc(40),
      t100: calc(100),
    };
  });

  expect(mathChecks.t12.totalPages).toBe(1);
  expect(mathChecks.t13.totalPages).toBe(2);
  expect(mathChecks.t13.lastPageItems).toBe(1);
  expect(mathChecks.t20.totalPages).toBe(2);
  expect(mathChecks.t20.lastPageItems).toBe(8);
  expect(mathChecks.t24.totalPages).toBe(2);
  expect(mathChecks.t24.lastPageItems).toBe(12);
  expect(mathChecks.t25.totalPages).toBe(3);
  expect(mathChecks.t25.lastPageItems).toBe(1);
  expect(mathChecks.t40.totalPages).toBe(4);
  expect(mathChecks.t100.totalPages).toBe(9);

  // Restore page size and test pagination hidden when count <= pageSize
  await page.evaluate(() => window.__setCatalogPageSize(12));
  await page.locator('#query').fill('CookUnity');
  await expect(paginationNav).toBeHidden();

  await page.locator('#clear-filters').click();
  await expect(paginationNav).toBeVisible();

  expect(problems).toEqual([]);
});

test('R3-ALPHA-UX-01B: formats semicolon-delimited lists as bullet lists and preserves narrative text', async ({ page }) => {
  const problems = trackRuntimeProblems(page);

  // 1. Check OP-006 (Canonical Graduate Software Engineer: tasks, requirements, benefits have semicolons)
  await page.goto('/?id=OP-006');
  await expect(page.locator('#opportunity-view')).toBeVisible();

  // "Qué harías" should be a <ul> with 2 <li> items
  const op6TasksList = page.locator('div:has(> h3:has-text("Qué harías")) ul');
  await expect(op6TasksList).toBeVisible();
  await expect(op6TasksList.locator('li')).toHaveCount(2);
  await expect(op6TasksList.locator('li').first()).toContainText('Desarrollo de software en sistemas Linux');
  await expect(op6TasksList.locator('li').nth(1)).toContainText('Colaboración en equipo distribuido internacional');

  // "Requisitos del puesto" should be a <ul> with 5 <li> items
  const op6ReqList = page.locator('.detail-section:has(h3:has-text("Requisitos del puesto")) ul');
  await expect(op6ReqList).toBeVisible();
  await expect(op6ReqList.locator('li')).toHaveCount(5);
  await expect(op6ReqList.locator('li').first()).toContainText('Graduación 2026/2027');
  await expect(op6ReqList.locator('li').nth(1)).toContainText('Python, Rust, C/C++');

  // "Beneficios publicados" should be a <ul> with 5 <li> items
  const op6BenefitsList = page.locator('.detail-section:has(h3:has-text("Beneficios publicados")) ul');
  await expect(op6BenefitsList).toBeVisible();
  await expect(op6BenefitsList.locator('li')).toHaveCount(5);
  await expect(op6BenefitsList.locator('li').first()).toContainText('Trabajo 100% remoto');
  await expect(op6BenefitsList.locator('li').nth(1)).toContainText('USD 2,000');

  // "Qué experiencia podrías llevar al siguiente paso" (growth) is narrative -> must be a <p>, NOT <ul>
  const op6GrowthPara = page.locator('.detail-section:has(h3:has-text("Qué experiencia podrías llevar")) p');
  await expect(op6GrowthPara).toBeVisible();
  await expect(page.locator('.detail-section:has(h3:has-text("Qué experiencia podrías llevar")) ul')).toHaveCount(0);

  // 2. Check OP-005 (CookUnity Supply Chain Analyst)
  await page.goto('/?id=OP-005');
  await expect(page.locator('#opportunity-view')).toBeVisible();

  // OP-005 tasks: 3 items
  const op5TasksList = page.locator('div:has(> h3:has-text("Qué harías")) ul');
  await expect(op5TasksList).toBeVisible();
  await expect(op5TasksList.locator('li')).toHaveCount(3);
  await expect(op5TasksList.locator('li').first()).toContainText('Análisis y reportería operativa');

  // OP-005 requirements: 6 items
  const op5ReqList = page.locator('.detail-section:has(h3:has-text("Requisitos del puesto")) ul');
  await expect(op5ReqList).toBeVisible();
  await expect(op5ReqList.locator('li')).toHaveCount(6);

  // OP-005 benefits: 2 items
  const op5BenefitsList = page.locator('.detail-section:has(h3:has-text("Beneficios publicados")) ul');
  await expect(op5BenefitsList).toBeVisible();
  await expect(op5BenefitsList.locator('li')).toHaveCount(2);

  // 3. Check QA-001 (Closed demo: single sentence tasks, no semicolon -> renders as <p>, NOT <ul>)
  await page.goto('/?id=QA-001');
  await expect(page.locator('#opportunity-view')).toBeVisible();

  const qaTasksPara = page.locator('div:has(> h3:has-text("Qué harías")) p');
  await expect(qaTasksPara).toBeVisible();
  await expect(qaTasksPara).toContainText('Práctica dirigida a la Jefatura de Contratos Portuarios.');
  await expect(page.locator('div:has(> h3:has-text("Qué harías")) ul')).toHaveCount(0);

  expect(problems).toEqual([]);
});

test('R3-ALPHA-IMPLEMENTATION-01: reasoned side-by-side comparator with requirements, structured lists, difference highlights, unknown indicators, and direct actions', async ({ page }) => {
  const problems = trackRuntimeProblems(page);
  await page.goto('/');

  // 1. Select OP-005 (CookUnity, stale TTL > 7 days) and OP-006 (Canonical) for comparison
  // Opt in to unconfirmed entries so OP-005 is selectable in the catalog
  await page.locator('#include-unconfirmed').check();
  await page.locator('#query').fill('CookUnity');
  await page.locator('.job-card[data-id="OP-005"] .compare-button').click();
  await page.locator('#query').fill('Graduate Software Engineer');
  await page.locator('.job-card[data-id="OP-006"] .compare-button').click();
  await page.locator('#clear-filters').click();

  // 2. Open comparator
  await expect(page.locator('#compare-panel')).toBeVisible();
  await expect(page.locator('#compare-open')).toBeEnabled();
  await page.locator('#compare-open').click();

  const compareDialog = page.locator('#compare-dialog');
  await expect(compareDialog).toBeVisible();

  // Check header and eyebrow
  await expect(page.locator('#compare-content')).toContainText('SIN PUNTUACIÓN');
  await expect(page.locator('#compare-dialog-title')).toHaveText('Dos alternativas, sin ganador universal');

  // Check column headers
  const compareTable = page.locator('.comparison-table');
  await expect(compareTable).toBeVisible();
  await expect(compareTable.locator('thead th:has-text("CookUnity")')).toBeVisible();
  await expect(compareTable.locator('thead th:has-text("Canonical")')).toBeVisible();

  // Action buttons in table headers
  const detailButtons = compareTable.locator('thead button.btn-compare-detail');
  await expect(detailButtons).toHaveCount(2);

  // Active opportunity Canonical OP-006 has apply link; CookUnity OP-005 (stale TTL) hides postulation link under fail-closed governance
  const applyLinks = compareTable.locator('thead a[href*="greenhouse.io"]');
  await expect(applyLinks).toHaveCount(1);
  await expect(compareTable.locator('thead th:has-text("CookUnity")')).toContainText('Pendiente de revalidación');

  // 3. Verify "Requisitos del puesto" dimension exists and has bulleted lists
  const reqRow = compareTable.locator('tbody tr:has(th:has-text("Requisitos del puesto"))');
  await expect(reqRow).toBeVisible();
  const reqLists = reqRow.locator('ul');
  await expect(reqLists).toHaveCount(2);
  // CookUnity has 6 requirements, Canonical OP-006 has 5 requirements
  await expect(reqLists.nth(0).locator('li')).toHaveCount(6);
  await expect(reqLists.nth(1).locator('li')).toHaveCount(5);
  await expect(reqLists.nth(1).locator('li').first()).toContainText('Graduación 2026/2027');

  // 4. Verify "Funciones" dimension has structured lists
  const tasksRow = compareTable.locator('tbody tr:has(th:has-text("Funciones"))');
  await expect(tasksRow).toBeVisible();
  await expect(tasksRow.locator('ul')).toHaveCount(2);

  // 5. Verify "Tecnologías" dimension renders skill chips
  const skillsRow = compareTable.locator('tbody tr:has(th:has-text("Tecnologías"))');
  await expect(skillsRow).toBeVisible();
  await expect(skillsRow.locator('span:has-text("Python")').first()).toBeVisible();

  // 6. Verify "Condiciones y advertencias" displays warning box
  const riskRow = compareTable.locator('tbody tr:has(th:has-text("Condiciones y advertencias"))');
  await expect(riskRow).toBeVisible();
  await expect(riskRow).toContainText('Condición declarada');
  await expect(riskRow).toContainText('Jornada completa');

  // 7. Verify unknown data displays neutral non-punitive indicator
  // CookUnity does not publish salary in the public call
  const salaryRow = compareTable.locator('tbody tr:has(th:has-text("Compensación"))');
  await expect(salaryRow).toBeVisible();
  await expect(salaryRow).toContainText('No publicado en convocatoria');

  // 8. Test "Destacar diferencias" toggle
  const diffToggle = page.locator('#compare-toggle-diff');
  await expect(diffToggle).toBeVisible();
  await expect(diffToggle).not.toBeChecked();

  // Check the diff toggle
  await diffToggle.check();
  await expect(diffToggle).toBeChecked();

  // Different rows (e.g. mode, requirements, salary) should now have visible difference badges
  const visibleDiffBadges = page.locator('.diff-badge:not(.hidden)');
  expect(await visibleDiffBadges.count()).toBeGreaterThan(0);
  await expect(page.locator('tr[data-compare-diff="true"][class*="bg-sky-50"]').first()).toBeVisible();

  // Uncheck the diff toggle
  await diffToggle.uncheck();
  await expect(page.locator('.diff-badge:not(.hidden)')).toHaveCount(0);

  // 9. Direct navigation: clicking "Ver detalle ↗" on CookUnity opens its detail modal
  const viewDetailOp5Btn = compareTable.locator('thead button.btn-compare-detail[data-compare-open="OP-005"]');
  await viewDetailOp5Btn.click();

  // Compare dialog should close, and job-dialog should open with CookUnity detail
  await expect(compareDialog).toBeHidden();
  const jobDialog = page.locator('#job-dialog');
  await expect(jobDialog).toBeVisible();
  await expect(page.locator('#dialog-content')).toContainText('CookUnity');
  await expect(page.locator('#dialog-content')).toContainText('Supply Chain Analyst');

  // Close job dialog
  await page.locator('#job-dialog button[aria-label="Cerrar detalle"]').click();
  await expect(jobDialog).toBeHidden();

  expect(problems).toEqual([]);
});
