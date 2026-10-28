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
