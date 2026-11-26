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

// --- TASK-R7-01: Labor Regime Taxonomy & UI tests ---
assert.match(html, /<select[^>]*id="regime-filter"/, 'regime-filter select element exists in HTML');
for (const regimeKey of [
  'PRE_PROFESSIONAL_INTERNSHIP',
  'PROFESSIONAL_INTERNSHIP',
  'CAS',
  'LABOR_REGIME_728',
  'CIVIL_SERVICES',
  'OTHER',
  'UNSPECIFIED',
]) {
  assert.match(html, new RegExp(`value="${regimeKey}"`), `regime option ${regimeKey} is present in index.html`);
}

function runRegimeView({ regime = '', query = '' } = {}) {
  const catalog = [
    { id: 'JOB-CAS', recordKind: 'curated', publicationStatus: 'active', employer: 'RENIEC', title: 'Especialista en BD CAS', mode: 'Presencial' },
    { id: 'JOB-PRE', recordKind: 'curated', publicationStatus: 'active', employer: 'BCP', title: 'Practicante Preprofesional de Sistemas', mode: 'Híbrido', kind: 'Prácticas' },
    { id: 'JOB-PRO', recordKind: 'curated', publicationStatus: 'active', employer: 'BBVA', title: 'Practicante Profesional de Datos', mode: 'Remoto', kind: 'Prácticas' },
    { id: 'JOB-728', recordKind: 'curated', publicationStatus: 'active', employer: 'Interbank', title: 'Ingeniero Cloud', contractType: 'D. Leg. 728', mode: 'Híbrido' },
    { id: 'JOB-CIVIL', recordKind: 'curated', publicationStatus: 'active', employer: 'Gobierno Regional', title: 'Consultor TI por Locación de Servicios', mode: 'Presencial' },
    { id: 'JOB-OTHER', recordKind: 'curated', publicationStatus: 'active', employer: 'Remote Inc', title: 'Fullstack Contractor B2B', mode: 'Remoto' },
    { id: 'JOB-UNSPEC', recordKind: 'curated', publicationStatus: 'active', employer: 'Startup Inc', title: 'Developer', mode: 'Remoto' },
  ];
  const filters = {
    query: { value: query }, location: { value: '' }, mode: { value: '' }, kind: { value: '' },
    family: { value: '' }, sector: { value: '' }, level: { value: '' }, salary: { value: '' },
    risk: { value: '' }, regime: { value: regime }, history: { checked: false },
  };
  const toggles = {
    '#include-unconfirmed': { checked: false },
    '#include-demonstrations': { checked: false },
  };
  const context = vm.createContext({
    catalog, filters,
    document: { querySelector: (selector) => toggles[selector] },
    result: null,
    currentStates: () => ({ opportunityStatus: 'open', publicationStatus: 'active', verificationStatus: 'verified' }),
  });
  vm.runInContext(`${functions}\nresult = getVisibleJobs();`, context);
  return Array.from(context.result, (job) => job.id);
}

assert.deepEqual(runRegimeView({ regime: 'CAS' }), ['JOB-CAS'], 'regime filter correctly filters CAS opportunities');
assert.deepEqual(runRegimeView({ regime: 'PRE_PROFESSIONAL_INTERNSHIP' }), ['JOB-PRE'], 'regime filter correctly filters Pre-professional internships');
assert.deepEqual(runRegimeView({ regime: 'PROFESSIONAL_INTERNSHIP' }), ['JOB-PRO'], 'regime filter correctly filters Professional internships');
assert.deepEqual(runRegimeView({ regime: 'LABOR_REGIME_728' }), ['JOB-728'], 'regime filter correctly filters 728 opportunities');
assert.deepEqual(runRegimeView({ regime: 'CIVIL_SERVICES' }), ['JOB-CIVIL'], 'regime filter correctly filters civil services opportunities');
assert.deepEqual(runRegimeView({ regime: 'OTHER' }), ['JOB-OTHER'], 'regime filter correctly filters OTHER opportunities');
assert.deepEqual(runRegimeView({ regime: 'UNSPECIFIED' }), ['JOB-UNSPEC'], 'regime filter correctly filters unspecified opportunities');
assert.equal(runRegimeView({ regime: '' }).length, 7, 'all 7 opportunities visible when no regime filter is active');

const regimeTagContext = vm.createContext({
  escapeHTML: (str) => String(str || ''),
  result: null,
});
vm.runInContext(`${functions}\nresult = regimeTag({ id: 'JOB-CAS', requisition: 'CAS N° 045-2026', title: 'Analista de Sistemas' });`, regimeTagContext);
assert.match(regimeTagContext.result, /CAS/, 'regime tag renders CAS short label');
assert.match(regimeTagContext.result, /Decreto Legislativo N° 1057/, 'regime tag includes legal framework tooltip');

vm.runInContext(`result = regimeTag({ id: 'JOB-PRE', kind: 'Prácticas', title: 'Practicante Pre Profesional' });`, regimeTagContext);
assert.match(regimeTagContext.result, /Prácticas Pre/, 'regime tag renders Prácticas Pre');
assert.match(regimeTagContext.result, /Ley N° 28518/, 'regime tag includes Ley 28518 tooltip');

vm.runInContext(`result = regimeTag({ id: 'JOB-728', contractType: 'D. Leg. 728' });`, regimeTagContext);
assert.match(regimeTagContext.result, /Planilla 728/, 'regime tag renders Planilla 728');

const detailContext = vm.createContext({
  safeHttpsUrl: (url) => url,
  escapeHTML: (str) => String(str || ''),
  formatDateTime: (dt) => dt,
  formatLocationEligibility: () => 'Lima, Perú',
  knownValue: (v) => Boolean(v),
  cleanContractDuration: () => 'Full-time',
  formatStructuredList: () => '',
  statusTag: () => '<span>Status</span>',
  currentStates: () => ({ opportunityStatus: 'open', verificationStatus: 'verified', publicationStatus: 'active' }),
  catalogConfig: { verificationTtlDays: 7 },
  lucideIcon: (name) => `<svg>${name}</svg>`,
  isCivilDate: () => true,
  result: null,
});
const detailStart = source.indexOf('function renderDetailContent(job,');
const detailEnd = source.indexOf('\nfunction renderOpportunityPage(', detailStart);
vm.runInContext(`${functions}\n${source.slice(detailStart, detailEnd)}\nresult = renderDetailContent({ id: 'OP-CAS-1', employer: 'SUNAT', title: 'Especialista CAS', requisition: 'CAS 01-2026', sourceUrl: 'https://sunat.gob.pe', applyUrl: 'https://sunat.gob.pe/apply' });`, detailContext);
assert.match(detailContext.result, /Régimen y modalidad/, 'detail renders regime summary card');
assert.match(detailContext.result, /Contratación Administrativa de Servicios \(CAS\)/, 'detail renders full CAS label');
assert.match(detailContext.result, /Régimen Contractual y Marco Normativo/, 'detail renders dedicated legal section');
assert.match(detailContext.result, /Decreto Legislativo N° 1057/, 'detail cites D. Leg. 1057');
assert.match(detailContext.result, /Naturaleza jurídica/, 'detail explains legal nature');
assert.match(detailContext.result, /Jornada y tiempo de trabajo/, 'detail explains working hours');
assert.match(detailContext.result, /Subvención \/ Remuneración/, 'detail explains compensation');
assert.match(detailContext.result, /Garantías y derechos principales/, 'detail explains key rights');
assert.match(detailContext.result, /Cautelas y consideraciones/, 'detail explains cautions');

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
  getJobLaborRegime: (job) => job.laborRegime || 'UNSPECIFIED',
  REGIME_DEFINITIONS: {
    UNSPECIFIED: { label: 'Modalidad no especificada', legalFramework: 'N/A', badgeClass: '' },
    CAS: { label: 'Contratación Administrativa de Servicios (CAS)', legalFramework: 'Decreto Legislativo N° 1057', badgeClass: '' },
  },
  result: null,
});
const comparisonFunction = source.slice(source.indexOf('function renderComparisonCell('), source.indexOf('\nfunction renderComparison()'));
vm.runInContext(`${comparisonFunction}\nresult = renderComparisonCell({ id: 'STALE-1', recordKind: 'curated', publicationStatus: 'unconfirmed', verificationStatus: 'stale', opportunityStatus: 'open' }, 'status');`, comparisonContext);
assert.match(comparisonContext.result, /Pendiente de revalidación/, 'comparator cell displays pending revalidation');
assert.doesNotMatch(comparisonContext.result, /Activa · Verificada/, 'comparator does not display active verified for stale jobs');

vm.runInContext(`result = renderComparisonCell({ id: 'CAS-1', laborRegime: 'CAS' }, 'regime');`, comparisonContext);
assert.match(comparisonContext.result, /Contratación Administrativa de Servicios \(CAS\)/, 'comparator cell renders labor regime');
assert.match(comparisonContext.result, /Decreto Legislativo N° 1057/, 'comparator cell renders regime legal framework');

// --- TASK-R7-02: Skills Extraction & Opportunity Comparison Tests ---
const skillsContext = vm.createContext({
  escapeHTML: (v) => String(v || ''),
  result: null,
});

// Test alias normalization
vm.runInContext(`${functions}\nresult = extractOpportunitySkills({
  title: 'Ingeniero Cloud',
  skills: 'Postgres · Amazon Web Services · Microsoft Azure · TS · K8s · Golang',
});`, skillsContext);
assert.ok(skillsContext.result.PostgreSQL, 'Postgres normalizes to PostgreSQL');
assert.ok(skillsContext.result.AWS, 'Amazon Web Services normalizes to AWS');
assert.ok(skillsContext.result.Azure, 'Microsoft Azure normalizes to Azure');
assert.ok(skillsContext.result.TypeScript, 'TS normalizes to TypeScript');
assert.ok(skillsContext.result.Kubernetes, 'K8s normalizes to Kubernetes');
assert.ok(skillsContext.result.Go, 'Golang normalizes to Go');

// Test false-positive prevention
vm.runInContext(`result = extractOpportunitySkills({
  title: 'Analista de Sistemas',
  requirements: 'Conocimientos generales; comunicación asertiva; capacidad de análisis; administración de redes sociales',
});`, skillsContext);
assert.equal(skillsContext.result.C, undefined, 'Conocimientos/Comunicación does not trigger C language');
assert.equal(skillsContext.result.Redes, undefined, 'Redes sociales does not trigger Redes');

// Test C and C++ detection
vm.runInContext(`result = extractOpportunitySkills({
  title: 'Firmware Dev',
  requirements: 'Programación en C y C++; depuración de controladores',
});`, skillsContext);
assert.ok(skillsContext.result.C, 'C language is detected');
assert.ok(skillsContext.result['C++'], 'C++ is detected');

// Test priority classification
vm.runInContext(`result = extractOpportunitySkills({
  title: 'Backend Dev',
  requirements: 'Experiencia obligatoria en Python; deseable conocimiento en Kubernetes',
  tasks: 'Desplegar servicios en Docker',
});`, skillsContext);
assert.equal(skillsContext.result.Python.priority, 'REQUIRED', 'Python is REQUIRED');
assert.equal(skillsContext.result.Kubernetes.priority, 'PREFERRED', 'Kubernetes is PREFERRED');
assert.equal(skillsContext.result.Docker.priority, 'MENTIONED', 'Docker in tasks is MENTIONED');

// Test comparison between two opportunities
vm.runInContext(`result = compareOpportunitySkills({
  id: 'JOB-A', employer: 'Empresa A', skills: 'Python · AWS · Docker', requirements: 'Python obligatorio; deseable Docker',
}, {
  id: 'JOB-B', employer: 'Empresa B', skills: 'Python · Java · Docker', requirements: 'Java y Python obligatorios',
});`, skillsContext);
assert.equal(skillsContext.result.shared_skills.length, 2, '2 shared skills: Python and Docker');
assert.equal(skillsContext.result.exclusive_a.length, 1, '1 exclusive skill in A: AWS');
assert.equal(skillsContext.result.exclusive_a[0].canonical, 'AWS');
assert.equal(skillsContext.result.exclusive_b.length, 1, '1 exclusive skill in B: Java');
assert.equal(skillsContext.result.exclusive_b[0].canonical, 'Java');

// Test comparison rendering HTML
vm.runInContext(`result = renderSkillsComparison({
  id: 'JOB-A', employer: 'TechCorp', skills: 'Python · Docker',
}, {
  id: 'JOB-B', employer: 'FinCorp',
});`, skillsContext);
assert.match(skillsContext.result, /Contraste de Requisitos Técnicos y Competencias/, 'renders section heading');
assert.match(skillsContext.result, /Coincidentes/, 'renders shared section');
assert.match(skillsContext.result, /Exclusivas: TechCorp/, 'renders exclusive section for A');
assert.match(skillsContext.result, /FinCorp.*no incluye un listado estructurado/, 'renders missing information warning for B');

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
