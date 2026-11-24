const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const pagesBase = 'https://blueisazul.github.io/WebRutaSistemas/';
const rootBase = 'http://127.0.0.1:4173/';
const expectedPaths = {
  'styles.css': '/styles.css',
  'app.js': '/app.js',
  './data/opportunities.json': '/data/opportunities.json',
};
for (const resource of ['styles.css', 'app.js', './data/opportunities.json']) {
  assert.ok(!resource.startsWith('/'), `${resource} must stay relative for project Pages paths`);
  assert.equal(new URL(resource, pagesBase).origin, new URL(pagesBase).origin);
  assert.equal(new URL(resource, rootBase).origin, new URL(rootBase).origin);
  assert.equal(new URL(resource, rootBase).pathname, expectedPaths[resource], `${resource} resolves from the local root`);
  assert.equal(new URL(resource, pagesBase).pathname, `/WebRutaSistemas${expectedPaths[resource]}`, `${resource} resolves beneath the Pages project prefix`);
}
assert.match(html, /href="styles\.css"/, 'stylesheet uses a relative Pages-compatible URL');
assert.match(html, /src="app\.js"/, 'script uses a relative Pages-compatible URL');
const validatorStart = source.indexOf('function isValidCatalogPayload(payload) {');
const statesStart = source.indexOf('\nfunction currentStates(job)', validatorStart);
const safeUrlStart = source.indexOf('function safeHttpsUrl(value) {');
const initialsStart = source.indexOf('\nfunction initials(name)', safeUrlStart);
const stateFunctionStart = source.indexOf('function currentStates(job) {');
const escapeStart = source.indexOf('\nfunction escapeHTML', stateFunctionStart);
assert.ok(validatorStart >= 0 && statesStart > validatorStart && safeUrlStart >= 0 && initialsStart > safeUrlStart, 'catalog payload validator functions must remain identifiable');
assert.ok(stateFunctionStart >= 0 && escapeStart > stateFunctionStart, 'catalog state function must remain identifiable');
const dateStart = source.indexOf('function isCivilDate(value) {');
assert.ok(dateStart >= 0 && validatorStart > dateStart, 'civil date validator must remain identifiable');
const validators = source.slice(dateStart, statesStart) + source.slice(safeUrlStart, initialsStart);
const stateFunction = source.slice(stateFunctionStart, escapeStart);
const evaluationStart = source.indexOf('function knownValue(value) {');
const evaluationEnd = source.indexOf('\nfunction renderSignals(job)', evaluationStart);
assert.ok(evaluationStart >= 0 && evaluationEnd > evaluationStart, 'professional evaluation functions must remain identifiable');
const normalizedStart = source.indexOf('function normalized(value) {');
const viewStart = source.indexOf('function getVisibleJobs() {');
const viewEnd = source.indexOf('\nfunction updateCatalogView()', viewStart);
assert.ok(normalizedStart >= 0 && viewStart > normalizedStart && viewEnd > viewStart, 'catalog filtering functions must remain identifiable');
const functions = source.slice(normalizedStart, viewEnd);

function runView({ examples = false, unconfirmed = false, history = false, query = '', mode = '' } = {}) {
  const catalog = [
    { id: 'REAL-1', recordKind: 'curated', publicationStatus: 'active', employer: 'Banco Ejemplo', title: 'Analista Junior', mode: 'Híbrido' },
    { id: 'DEMO-1', recordKind: 'demonstration', publicationStatus: 'unconfirmed', employer: '42Labs', title: 'Swift Developer', mode: 'Remoto' },
    { id: 'PENDING-1', recordKind: 'curated', publicationStatus: 'unconfirmed', employer: 'Tech Ejemplo', title: 'QA Trainee', mode: 'Presencial' },
    { id: 'OLD-1', recordKind: 'curated', publicationStatus: 'historical', employer: 'Entidad Antigua', title: 'Practicante', mode: 'Presencial' },
  ];
  const filters = {
    query: { value: query }, location: { value: '' }, mode: { value: mode }, kind: { value: '' },
    family: { value: '' }, sector: { value: '' }, level: { value: '' }, salary: { value: '' },
    risk: { value: '' }, history: { checked: history },
  };
  const toggles = {
    '#include-unconfirmed': { checked: unconfirmed },
    '#include-demonstrations': { checked: examples },
  };
  const context = vm.createContext({
    catalog, filters,
    document: { querySelector: (selector) => toggles[selector] },
    result: null,
    currentStates: (job) => ({ opportunityStatus: job.publicationStatus === 'historical' ? 'closed' : 'open', publicationStatus: job.publicationStatus }),
  });
  vm.runInContext(`${functions}\nresult = getVisibleJobs();`, context);
  return Array.from(context.result, (job) => job.id);
}

assert.deepEqual(runView(), ['REAL-1'], 'default results contain only a publishable non-demonstration');
assert.deepEqual(runView({ examples: true }), ['REAL-1', 'DEMO-1'], 'examples appear only after explicit opt-in');
assert.deepEqual(runView({ examples: true, query: 'swift' }), ['DEMO-1'], 'search applies consistently to opt-in examples');
assert.deepEqual(runView({ examples: true, mode: 'Remoto' }), ['DEMO-1'], 'mode filters apply to opt-in examples');
assert.deepEqual(runView({ unconfirmed: true }), ['REAL-1', 'PENDING-1'], 'unconfirmed non-demo entries require their own opt-in');
assert.deepEqual(runView({ history: true }), ['REAL-1', 'OLD-1'], 'historical non-demo entries require the history opt-in');

const metricContext = vm.createContext({
  catalog: [
    { id: 'REAL-1', recordKind: 'curated', publicationStatus: 'active', employer: 'A', title: 'Active' },
    { id: 'DEMO-1', recordKind: 'demonstration', publicationStatus: 'historical', employer: 'B', title: 'Demo' },
    { id: 'PENDING-1', recordKind: 'curated', publicationStatus: 'unconfirmed', employer: 'C', title: 'Pending' },
    { id: 'OLD-1', recordKind: 'curated', publicationStatus: 'historical', employer: 'D', title: 'Historical' },
  ],
  currentStates: (job) => ({ publicationStatus: job.publicationStatus, opportunityStatus: job.publicationStatus === 'historical' ? 'closed' : 'open' }),
  result: null,
});
vm.runInContext(`${functions}\nresult = publicCatalogMetrics(catalog);`, metricContext);
assert.deepEqual(JSON.parse(JSON.stringify(metricContext.result)), { active: 1, expiredOrHistorical: 1, unconfirmed: 1 }, 'metrics exclude examples and do not overlap history with unconfirmed counts');

const stateContext = vm.createContext({ URL, catalogConfig: { verificationTtlDays: 7 }, limaDateString: () => '2026-10-26', result: null });
vm.runInContext(`${source.slice(safeUrlStart, initialsStart)}\n${stateFunction}\nresult = currentStates(job);`, Object.assign(stateContext, {
  job: { id: 'BAD-ACTIVE', recordKind: 'curated', publicationStatus: 'active', opportunityStatus: 'open', verificationStatus: 'verified' },
}));
assert.equal(stateContext.result.publicationStatus, 'unconfirmed', 'incomplete active snapshot is degraded before rendering');

// --- TASK-R4-11-03: Freshness & TTL decoupling tests ---
const baseCurated = JSON.parse(fs.readFileSync(path.join(root, 'data/opportunities.json'), 'utf8')).opportunities.find((o) => o.id === 'OP-005');

function runStateWithDate(job, todayStr) {
  function limaDateString(date) {
    const target = date ? (date instanceof Date ? date : new Date(date)) : new Date(`${todayStr}T12:00:00Z`);
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit',
    }).formatToParts(target);
    const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
    return `${values.year}-${values.month}-${values.day}`;
  }
  const ctx = vm.createContext({
    URL, catalogConfig: { verificationTtlDays: 7 }, limaDateString, isTimestamp: (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(v) && !Number.isNaN(new Date(v).valueOf()),
    result: null, job,
  });
  vm.runInContext(`${source.slice(safeUrlStart, initialsStart)}\n${stateFunction}\nresult = currentStates(job);`, ctx);
  return ctx.result;
}

// 1. Verificación reciente (2 días atrás)
const jobRecent = JSON.parse(JSON.stringify(baseCurated));
jobRecent.lastVerifiedAt = '2026-11-21T10:00:00-05:00';
jobRecent.verificationEvidence.observedAt = '2026-11-21T10:00:00-05:00';
jobRecent.fieldEvidence.forEach((e) => { e.observedAt = '2026-11-21T10:00:00-05:00'; });
const resRecent = runStateWithDate(jobRecent, '2026-11-23');
assert.equal(resRecent.publicationStatus, 'active', 'recent verification keeps active publication');
assert.equal(resRecent.verificationStatus, 'verified', 'recent verification keeps verified status');

// 2. Exactamente 7 días (límite del TTL)
const job7d = JSON.parse(JSON.stringify(baseCurated));
job7d.lastVerifiedAt = '2026-11-16T10:00:00-05:00';
job7d.verificationEvidence.observedAt = '2026-11-16T10:00:00-05:00';
job7d.fieldEvidence.forEach((e) => { e.observedAt = '2026-11-16T10:00:00-05:00'; });
const res7d = runStateWithDate(job7d, '2026-11-23');
assert.equal(res7d.publicationStatus, 'active', 'exact 7-day boundary keeps active publication');
assert.equal(res7d.verificationStatus, 'verified', 'exact 7-day boundary keeps verified status');

// 3. Más de 7 días (8 días) -> deja de aparecer como activo y pasa a revisión (stale / unconfirmed)
const job8d = JSON.parse(JSON.stringify(baseCurated));
job8d.lastVerifiedAt = '2026-11-15T10:00:00-05:00';
job8d.verificationEvidence.observedAt = '2026-11-15T10:00:00-05:00';
job8d.fieldEvidence.forEach((e) => { e.observedAt = '2026-11-15T10:00:00-05:00'; });
const res8d = runStateWithDate(job8d, '2026-11-23');
assert.equal(res8d.publicationStatus, 'unconfirmed', 'stale verification leaves active publication and moves to review');
assert.equal(res8d.verificationStatus, 'stale', 'stale verification is marked as stale requiring revalidation');
assert.equal(res8d.opportunityStatus, 'open', 'stale verification preserves open opportunity status (not closed or expired)');

// 4. Fecha de verificación ausente -> pasa a revisión conservadoramente
const jobNoDate = JSON.parse(JSON.stringify(baseCurated));
delete jobNoDate.lastVerifiedAt;
const resNoDate = runStateWithDate(jobNoDate, '2026-11-23');
assert.equal(resNoDate.publicationStatus, 'unconfirmed', 'missing lastVerifiedAt leaves active publication');
assert.equal(resNoDate.verificationStatus, 'stale', 'missing lastVerifiedAt is not verified');

// 5. Fecha inválida -> pasa a revisión
const jobBadDate = JSON.parse(JSON.stringify(baseCurated));
jobBadDate.lastVerifiedAt = 'not-a-date';
const resBadDate = runStateWithDate(jobBadDate, '2026-11-23');
assert.equal(resBadDate.publicationStatus, 'unconfirmed', 'invalid verification date leaves active publication');
assert.equal(resBadDate.verificationStatus, 'stale', 'invalid verification date is not verified');

// 6. Fecha futura -> pasa a revisión
const jobFuture = JSON.parse(JSON.stringify(baseCurated));
jobFuture.lastVerifiedAt = '2030-01-01T10:00:00-05:00';
const resFuture = runStateWithDate(jobFuture, '2026-11-23');
assert.equal(resFuture.publicationStatus, 'unconfirmed', 'future verification date leaves active publication');
assert.equal(resFuture.verificationStatus, 'stale', 'future verification date is not verified');

// 7. Fecha límite vencida -> clasifica como histórica
const jobExpired = JSON.parse(JSON.stringify(baseCurated));
jobExpired.deadline = '2026-11-20';
const resExpired = runStateWithDate(jobExpired, '2026-11-23');
assert.equal(resExpired.opportunityStatus, 'expired', 'expired deadline sets opportunityStatus to expired');
assert.equal(resExpired.publicationStatus, 'historical', 'expired deadline sets publicationStatus to historical');

// 8. Cierre confirmado -> clasifica como histórica
const jobClosed = JSON.parse(JSON.stringify(baseCurated));
jobClosed.opportunityStatus = 'closed';
const resClosed = runStateWithDate(jobClosed, '2026-11-23');
assert.equal(resClosed.opportunityStatus, 'closed', 'closed status remains closed');
assert.equal(resClosed.publicationStatus, 'historical', 'closed job transitions to historical publication');

// 9. Registro histórico no se reactiva por TTL
const demoHist = JSON.parse(fs.readFileSync(path.join(root, 'data/opportunities.json'), 'utf8')).opportunities.find((o) => o.id === 'OP-001');
const resHist = runStateWithDate(demoHist, '2026-11-23');
assert.equal(resHist.publicationStatus, 'historical', 'historical demonstration is not reactivated by TTL');

// 10. Catálogo completo a +30 días: ninguna activa verificada, todas accesibles en revisión sin apagón ni pérdida
const fullCat = JSON.parse(fs.readFileSync(path.join(root, 'data/opportunities.json'), 'utf8')).opportunities;
let activeCountAt30d = 0;
let staleCountAt30d = 0;
let historicalCountAt30d = 0;
for (const opp of fullCat) {
  if (opp.recordKind === 'demonstration') continue;
  const s = runStateWithDate(opp, '2026-12-30'); // 37 días después de 2026-11-23
  if (s.publicationStatus === 'active') activeCountAt30d++;
  if (s.verificationStatus === 'stale') staleCountAt30d++;
  if (s.publicationStatus === 'historical') historicalCountAt30d++;
}
assert.equal(activeCountAt30d, 0, 'zero stale opportunities remain active in default catalog at +30 days');
assert.equal(staleCountAt30d, 107, 'all 107 opportunities are preserved and marked stale at +30 days');
assert.equal(historicalCountAt30d, 0, 'stale opportunities are not falsely marked historical without proof of closure');

// 11. Mezcla de métricas: distingue activas verificadas de las que requieren revalidación
const mixedMetricsContext = vm.createContext({
  catalog: [
    { id: 'ACT-VER', recordKind: 'curated', publicationStatus: 'active', verificationStatus: 'verified', opportunityStatus: 'open' },
    { id: 'ACT-STALE', recordKind: 'curated', publicationStatus: 'unconfirmed', verificationStatus: 'stale', opportunityStatus: 'open' },
    { id: 'HIST-1', recordKind: 'curated', publicationStatus: 'historical', verificationStatus: 'stale', opportunityStatus: 'expired' },
    { id: 'UNCONF-1', recordKind: 'curated', publicationStatus: 'unconfirmed', verificationStatus: 'unverified', opportunityStatus: 'unknown' },
    { id: 'DEMO-1', recordKind: 'demonstration', publicationStatus: 'historical', verificationStatus: 'stale', opportunityStatus: 'closed' },
  ],
  currentStates: (job) => job,
  result: null,
});
vm.runInContext(`${functions}\nresult = publicCatalogMetrics(catalog);`, mixedMetricsContext);
assert.deepEqual(JSON.parse(JSON.stringify(mixedMetricsContext.result)), {
  active: 1,
  expiredOrHistorical: 1,
  unconfirmed: 2,
}, 'metrics separate verified active from stale requiring revalidation');

// 12. Comparador: no presenta una oportunidad stale como activa verificada
const comparisonContext = vm.createContext({
  currentStates: (job) => job,
  formatDateTime: (d) => String(d || ''),
  escapeHTML: (v) => String(v || ''),
  knownValue: (v) => Boolean(v),
  result: null,
});
const comparisonFunction = source.slice(source.indexOf('function renderComparisonCell('), source.indexOf('\nfunction renderComparison()'));
vm.runInContext(`${comparisonFunction}\nresult = renderComparisonCell({ id: 'STALE-1', recordKind: 'curated', publicationStatus: 'unconfirmed', verificationStatus: 'stale', opportunityStatus: 'open' }, 'status');`, comparisonContext);
assert.match(comparisonContext.result, /Pendiente de revalidación/, 'comparator cell displays pending revalidation');
assert.doesNotMatch(comparisonContext.result, /Activa · Verificada/, 'comparator does not display active verified for stale jobs');

// 13. Detalle: no induce a postulación activa cuando la oportunidad es stale
const statusTagFunction = source.slice(source.indexOf('function statusTag('), source.indexOf('\nfunction modeTag('));
const tagContext = vm.createContext({
  currentStates: (job) => job,
  result: null,
});
vm.runInContext(`${statusTagFunction}\nresult = statusTag({ id: 'STALE-1', recordKind: 'curated', publicationStatus: 'unconfirmed', verificationStatus: 'stale', opportunityStatus: 'open' });`, tagContext);
assert.match(tagContext.result, /Pendiente de revalidación/, 'statusTag for stale opportunity displays Pendiente de revalidación');
assert.doesNotMatch(tagContext.result, /Activa/, 'statusTag for stale opportunity does not say Activa');

const evaluationContext = vm.createContext({
  currentStates: () => ({ opportunityStatus: 'open', verificationStatus: 'verified', publicationStatus: 'active' }),
  result: null,
});
vm.runInContext(`${evaluationStart >= 0 ? source.slice(evaluationStart, evaluationEnd) : ''}\nresult = evaluationSignals(job);`, Object.assign(evaluationContext, {
  job: { salary: 'No publicado', mode: 'Remoto', eligibility: 'Global; confirmar contratación desde Perú' },
}));
const missingSalarySignals = JSON.parse(JSON.stringify(evaluationContext.result));
assert.equal(missingSalarySignals.find((signal) => signal.label === 'Compensación').status, 'Información insuficiente', 'missing salary stays unknown rather than becoming zero');
assert.match(missingSalarySignals.find((signal) => signal.label === 'Modalidad y elegibilidad').limit, /Remoto no demuestra/, 'remote work without explicit Peru eligibility keeps its limitation');
vm.runInContext('result = evaluationSignals({ mode: "Remoto", eligibility: "Presencial únicamente" });', evaluationContext);
assert.equal(JSON.parse(JSON.stringify(evaluationContext.result)).find((signal) => signal.label === 'Modalidad y elegibilidad').status, 'Contradicción documentada', 'contradictory conditions are not treated as favorable');

const payloadContext = vm.createContext({
  payload: {
    schemaVersion: 2, verificationTtlDays: 7, timezone: 'America/Lima', sourceNote: 'Fixture', generatedAt: '2026-10-26T12:00:00Z',
    opportunities: [{
      id: 'JOB-1', employer: 'Empresa fixture', title: 'Puesto fixture', recordKind: 'curated',
      opportunityStatus: 'open', verificationStatus: 'verified', publicationStatus: 'active',
      sourceUrl: 'https://jobs.example.test/1', applyUrl: 'https://jobs.example.test/apply', allowedHosts: ['jobs.example.test'],
    }],
  }, URL, result: null,
});
vm.runInContext(`${validators}\nresult = isValidCatalogPayload(payload);`, payloadContext);
assert.equal(payloadContext.result, true, 'well-formed static catalog is accepted');
payloadContext.payload = JSON.parse(fs.readFileSync(path.join(root, 'data/opportunities.json'), 'utf8'));
vm.runInContext('result = isValidCatalogPayload(payload);', payloadContext);
assert.equal(payloadContext.result, true, 'checked-in snapshot satisfies the browser runtime contract');
for (const corrupt of [
  { ...payloadContext.payload, opportunities: [{ ...payloadContext.payload.opportunities[0], lastVerifiedAt: '2026-10-26T12:00:00' }] },
  { ...payloadContext.payload, opportunities: [{ ...payloadContext.payload.opportunities[0], fieldEvidence: [{ field: 'title', url: 'https://jobs.example.test/1', observedAt: '2026-10-26T12:00:00' }] }] },
  { ...payloadContext.payload, schemaVersion: 1 },
  { ...payloadContext.payload, opportunities: [] },
  { ...payloadContext.payload, opportunities: [null] },
  { ...payloadContext.payload, opportunities: [{ ...payloadContext.payload.opportunities[0], sourceUrl: 'http://jobs.example.test/1' }] },
  { ...payloadContext.payload, opportunities: [{ ...payloadContext.payload.opportunities[0], deadline: '2026-02-31' }] },
  { ...payloadContext.payload, opportunities: [{ ...payloadContext.payload.opportunities[0], fieldEvidence: [null] }] },
]) {
  payloadContext.payload = corrupt;
  vm.runInContext('result = isValidCatalogPayload(payload);', payloadContext);
  assert.equal(payloadContext.result, false, 'malformed or incomplete public snapshot is rejected');
}

const renderStart = source.indexOf('function render() {');
const renderEnd = source.indexOf('\nfunction normalized(', renderStart);
const updateStart = source.indexOf('function updateCatalogView() {');
const updateEnd = source.indexOf('\nfunction setFilterOptions(', updateStart);
const loadStart = source.indexOf('async function loadCatalog() {');
const loadEnd = source.indexOf('\nfilters.query.addEventListener', loadStart);
assert.ok(renderStart >= 0 && renderEnd > renderStart && updateStart >= 0 && updateEnd > updateStart && loadStart >= 0 && loadEnd > loadStart, 'render and catalog loading functions must remain identifiable');

const uiElements = Object.fromEntries([
  '#catalog-refresh', '#metric-total', '#metric-primary', '#metric-secondary',
  '#catalog-generated-at', '#catalog-last-checked', '#catalog-source-note', '#empty-clear',
].map((selector) => [selector, { textContent: '', hidden: false, disabled: false }]));
const heading = { textContent: '' };
const message = { textContent: '' };
const failureUI = {
  catalog: [], opportunities: [], catalogConfig: { verificationTtlDays: 7 }, catalogLoadError: false,
  list: { innerHTML: '', hidden: true }, count: { textContent: '' },
  empty: { hidden: true, querySelector: (selector) => selector === 'h3' ? heading : message },
  filters: { history: { checked: false } },
  document: { querySelector: (selector) => uiElements[selector] || { checked: false } },
  URL,
  fetch: async () => failureUI.responses.shift(),
  responses: [],
  fetchCalls: 0,
  populateFilters: () => {},
  publicCatalogMetrics: () => ({ active: 0, expiredOrHistorical: 0, unconfirmed: 5 }),
  getVisibleJobs: () => failureUI.catalog,
  renderCard: (job) => job.id,
  currentStates: (job) => ({ opportunityStatus: 'open', verificationStatus: 'verified', publicationStatus: job.publicationStatus || 'active' }),
};
vm.createContext(failureUI);
vm.runInContext(`${validators}\n${source.slice(renderStart, renderEnd)}\n${source.slice(updateStart, updateEnd)}\n${source.slice(loadStart, loadEnd)}`, failureUI);
(async () => {
  const validResponse = () => ({ ok: true, json: async () => JSON.parse(fs.readFileSync(path.join(root, 'data/opportunities.json'), 'utf8')) });
  const failures = [
    { ok: false, json: async () => { throw new Error('body must not be read'); } },
    { ok: true, json: async () => { throw new SyntaxError('malformed JSON'); } },
    { ok: true, json: async () => ({ schemaVersion: 1, opportunities: [] }) },
  ];
  for (const failure of failures) {
    failureUI.responses.push(validResponse());
    await failureUI.loadCatalog();
    assert.ok(failureUI.catalog.length > 0 && failureUI.list.innerHTML.length > 0, 'valid response renders before exercising the next failure');
    uiElements['#metric-total'].textContent = '5';
    failureUI.responses.push(failure);
    await failureUI.loadCatalog();
    assert.equal(failureUI.catalog.length, 0, 'failed refresh clears the previously loaded catalog');
    assert.equal(failureUI.opportunities.length, 0, 'failed refresh clears visible opportunities');
    assert.equal(failureUI.list.innerHTML, '', 'failed refresh removes stale cards');
    assert.equal(failureUI.empty.hidden, false, 'failed refresh exposes the error state');
    assert.equal(heading.textContent, 'No se pudo cargar el catálogo');
    assert.equal(uiElements['#metric-total'].textContent, '—', 'failed refresh clears stale metrics');
    assert.equal(failureUI.count.textContent, 'Catálogo local no disponible');
    failureUI.updateCatalogView();
    assert.equal(heading.textContent, 'No se pudo cargar el catálogo', 'filter changes do not replace the persistent load error with an empty-results message');
  }
  console.log('OK: root/Pages paths and failed-catalog degradation scenarios passed.');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
console.log('OK: public catalog filtering scenarios passed.');
