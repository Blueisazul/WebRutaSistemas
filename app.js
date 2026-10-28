let catalog = [];
let opportunities = [];

const list = document.querySelector('#job-list');
const count = document.querySelector('#result-count');
const empty = document.querySelector('#empty-state');
const dialog = document.querySelector('#job-dialog');
const dialogContent = document.querySelector('#dialog-content');
const filters = {
  query: document.querySelector('#query'),
  location: document.querySelector('#location'),
  mode: document.querySelector('#mode'),
  kind: document.querySelector('#kind'),
  family: document.querySelector('#family'),
  sector: document.querySelector('#sector'),
  level: document.querySelector('#level'),
  salary: document.querySelector('#salary-filter'),
  risk: document.querySelector('#risk-filter'),
  history: document.querySelector('#include-history'),
};
let toastTimer;
let catalogLoadError = false;

function limaDateString(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${values.year}-${values.month}-${values.day}`;
}

let catalogConfig = { verificationTtlDays: 7 };

function isCivilDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

function isValidCatalogPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)
    || payload.schemaVersion !== 2
    || payload.timezone !== 'America/Lima'
    || typeof payload.sourceNote !== 'string'
    || !Number.isInteger(payload.verificationTtlDays)
    || payload.verificationTtlDays < 1 || payload.verificationTtlDays > 30
    || typeof payload.generatedAt !== 'string'
    || !/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(payload.generatedAt)
    || Number.isNaN(new Date(payload.generatedAt).valueOf())
    || !Array.isArray(payload.opportunities) || payload.opportunities.length === 0) return false;
  const kinds = new Set(['demonstration', 'curated', 'imported_unreviewed']);
  const opportunityStates = new Set(['open', 'closed', 'expired', 'unknown']);
  const verificationStates = new Set(['verified', 'pending', 'stale', 'unverified']);
  const publicationStates = new Set(['active', 'unconfirmed', 'historical']);
  const ids = new Set();
  return payload.opportunities.every((job) => {
    if (!job || typeof job !== 'object' || Array.isArray(job)
      || typeof job.id !== 'string' || !job.id.trim() || ids.has(job.id)
      || typeof job.employer !== 'string' || !job.employer.trim()
      || typeof job.title !== 'string' || !job.title.trim()
      || !kinds.has(job.recordKind)
      || !opportunityStates.has(job.opportunityStatus)
      || !verificationStates.has(job.verificationStatus)
      || !publicationStates.has(job.publicationStatus)
      || !Array.isArray(job.allowedHosts) || job.allowedHosts.some((host) => typeof host !== 'string')) return false;
    ids.add(job.id);
    const source = safeHttpsUrl(job.sourceUrl);
    if (!source || !job.allowedHosts.includes(new URL(source).hostname.toLowerCase())) return false;
    if (job.applyUrl) {
      const application = safeHttpsUrl(job.applyUrl);
      if (!application || !job.allowedHosts.includes(new URL(application).hostname.toLowerCase())) return false;
    }
    if (job.deadline !== null && job.deadline !== undefined && !isCivilDate(job.deadline)) return false;
    if (job.fieldEvidence !== undefined
      && (!Array.isArray(job.fieldEvidence) || job.fieldEvidence.some((entry) => !entry || typeof entry !== 'object' || Array.isArray(entry)))) return false;
    return true;
  });
}

function currentStates(job) {
  const states = {
    opportunityStatus: job.opportunityStatus || 'unknown',
    verificationStatus: job.verificationStatus || 'unverified',
    publicationStatus: job.publicationStatus || 'unconfirmed',
  };
  const today = limaDateString();
  const ttlDays = Number.isInteger(catalogConfig.verificationTtlDays) ? catalogConfig.verificationTtlDays : 7;
  if (job.deadline && job.deadline < today && !['closed', 'expired'].includes(states.opportunityStatus)) states.opportunityStatus = 'expired';
  if (states.verificationStatus === 'verified') {
    const checked = job.lastVerifiedAt ? new Date(job.lastVerifiedAt) : null;
    const checkedDate = checked && !Number.isNaN(checked.valueOf()) ? limaDateString(checked) : '';
    const dayNumber = (isoDate) => Date.parse(`${isoDate}T00:00:00Z`);
    const ageDays = checkedDate ? (dayNumber(today) - dayNumber(checkedDate)) / 86400000 : Infinity;
    if (ageDays < 0 || ageDays > ttlDays) states.verificationStatus = 'stale';
  }
  const evidence = job.verificationEvidence;
  const observed = evidence?.observedAt ? new Date(evidence.observedAt) : null;
  const observedDate = observed && !Number.isNaN(observed.valueOf()) ? limaDateString(observed) : '';
  const lowerBound = limaDateString(new Date(Date.now() - ttlDays * 86400000));
  const safeHosts = new Set(job.allowedHosts || []);
  const permitted = (value) => {
    const safeUrl = safeHttpsUrl(value);
    const host = safeUrl ? new URL(safeUrl).hostname.toLowerCase() : '';
    return host && safeHosts.has(host);
  };
  const evidenceComplete = evidence
    && evidence.publisherRelation === 'employer_confirmed'
    && evidence.method === 'manual'
    && evidence.result === 'application_open'
    && observedDate >= lowerBound && observedDate <= today
    && permitted(job.sourceUrl) && permitted(job.applyUrl) && permitted(evidence.url);
  const decision = job.editorialDecision;
  const approvedEditorially = decision?.status === 'approved'
    && Boolean(decision.reviewer && decision.reason)
    && decision.decidedAt && !Number.isNaN(new Date(decision.decidedAt).valueOf())
    && limaDateString(new Date(decision.decidedAt)) <= today;
  const fieldEvidence = Array.isArray(job.fieldEvidence) ? job.fieldEvidence : [];
  const evidenceByField = new Map(fieldEvidence.map((entry) => [entry.field, entry]));
  const requiredEvidence = ['employer', 'publisher', 'title', 'sourceUrl', 'applyUrl'];
  const optionalFacts = ['publishedAt', 'deadline', 'location', 'mode', 'salary', 'benefits', 'contractType', 'duration', 'requirements', 'skills', 'training', 'tasks', 'eligibility', 'sector', 'family', 'level', 'kind', 'growth', 'continuity', 'risk'];
  const claimedFields = [...requiredEvidence, ...optionalFacts.filter((field) => job[field] !== null && job[field] !== undefined && job[field] !== '')];
  const fieldEvidenceComplete = Boolean(job.employer && job.publisher && job.title && job.sourceUrl && job.applyUrl)
    && claimedFields.every((field) => {
      const entry = evidenceByField.get(field);
      const observed = entry?.observedAt ? new Date(entry.observedAt) : null;
      const observedDate = observed && !Number.isNaN(observed.valueOf()) ? limaDateString(observed) : '';
      return permitted(entry?.url) && observedDate >= lowerBound && observedDate <= today;
    });
  const verifiedNow = states.opportunityStatus === 'open'
    && states.verificationStatus === 'verified'
    && job.recordKind !== 'demonstration'
    && evidenceComplete
    && approvedEditorially
    && fieldEvidenceComplete
    && (!job.deadline || job.deadline >= today);
  if (states.publicationStatus === 'active' && !verifiedNow) states.publicationStatus = 'unconfirmed';
  return states;
}

function escapeHTML(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function safeHttpsUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && !url.username && !url.password && (!url.port || url.port === '443') ? url.href : null;
  } catch {
    return null;
  }
}

function initials(name) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0] || '').join('').toUpperCase();
}

function statusTag(job) {
  const state = currentStates(job);
  if (state.publicationStatus === 'active') return '<span class="tag verified">Activa · revisión reciente</span>';
  if (state.opportunityStatus === 'expired') return '<span class="tag closed">Plazo vencido</span>';
  if (state.publicationStatus === 'historical') return '<span class="tag closed">Referencia histórica</span>';
  if (state.verificationStatus === 'stale') return '<span class="tag unverified">Revisión atrasada</span>';
  return `<span class="tag unverified">${job.recordKind === 'demonstration' ? 'Ficha demostrativa' : 'No confirmada'}</span>`;
}

function modeTag(job) {
  const mode = job.mode || 'No especificado';
  const className = mode.toLowerCase().includes('remoto') ? 'remote' : 'mode';
  return `<span class="tag ${className}">${escapeHTML(mode)}</span>`;
}

function renderCard(job) {
  const state = currentStates(job);
  const id = escapeHTML(job.id);
  const targetClass = job.sector === 'Sector público' ? 'public' : (job.sector === 'Banca y finanzas' ? 'bank' : '');
  const salaryKnown = job.salary && !/no publicado|no especificado/i.test(job.salary);
  const salary = salaryKnown ? escapeHTML(job.salary) : 'No publicado';
  const familyLabel = job.family === 'Desarrollo y QA' ? job.family : job.family;
  const metaDate = `Consulta registrada ${escapeHTML(job.lastCheckedDate || 'No disponible')}`;
  const typeLabel = job.recordKind === 'demonstration' ? 'Ficha de demostración' : (job.kind === 'Profesional' ? job.level : job.kind);
  return `<article class="job-card" data-id="${id}">
    <div class="job-main">
      <div class="company-mark ${targetClass}" aria-hidden="true">${escapeHTML(initials(job.employer))}</div>
      <div class="job-copy min-w-0">
        <div class="job-title-row"><h3 class="job-title" role="button" tabindex="0" data-open="${id}">${escapeHTML(job.title)}</h3>${statusTag(job)}</div>
        <p class="company-name">${escapeHTML(job.employer)} <span>·</span> ${escapeHTML(job.sector)}</p>
        <div class="job-tags">${modeTag(job)}<span class="tag">${escapeHTML(familyLabel)}</span><span class="tag ${job.level === 'Senior' ? 'senior' : ''}">${escapeHTML(typeLabel)}</span></div>
        <p class="job-location">⌖ ${escapeHTML(job.location || 'Ubicación no especificada')} <span>·</span> ${escapeHTML(job.eligibility || 'Elegibilidad no confirmada')}</p>
      </div>
    </div>
    <div class="job-fit"><strong>${state.publicationStatus === 'historical' || state.opportunityStatus === 'expired' ? 'No disponible para postular' : 'Vigencia no confirmada'}</strong><span>${escapeHTML(job.growth || '')}</span></div>
    <div class="job-meta"> <strong class="salary ${salary === 'No publicado' ? 'missing' : ''}">${salary}</strong><span class="check-date">${metaDate}</span><button class="card-button" type="button" data-open="${id}">Ver evidencia <span aria-hidden="true">↗</span></button></div>
  </article>`;
}

function render() {
  const jobs = opportunities;
  list.innerHTML = jobs.map(renderCard).join('');
  list.hidden = jobs.length === 0;
  empty.hidden = jobs.length > 0;
  count.textContent = `${jobs.length} ${jobs.length === 1 ? 'resultado' : 'resultados'}`;
}

function normalized(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es');
}

function getVisibleJobs() {
  const tokens = normalized(filters.query.value).split(/\s+/).filter(Boolean);
  const location = normalized(filters.location.value);
  const mode = normalized(filters.mode.value);
  const kind = filters.kind.value;
  const family = normalized(filters.family.value);
  const sector = filters.sector.value;
  const level = filters.level.value;
  const includeUnconfirmed = document.querySelector('#include-unconfirmed').checked;
  const includeDemonstrations = document.querySelector('#include-demonstrations').checked;
  const includeHistory = filters.history.checked;
  const temporarySignal = /suplencia|reemplaz|temporal|plazo fijo|hasta el|por \d+ meses|renovaci[oó]n condicionada|convocatoria cerrada|vencid|por necesidad|campaña/i;
  return catalog.filter((job) => {
    const state = currentStates(job);
    const demonstration = job.recordKind === 'demonstration';
    if (demonstration && !includeDemonstrations) return false;
    if (!demonstration && state.publicationStatus === 'historical' && !includeHistory) return false;
    if (!demonstration && state.publicationStatus !== 'active' && state.publicationStatus !== 'historical' && !includeUnconfirmed) return false;
    if (location && !normalized(job.location + ' ' + job.eligibility).includes(location)) return false;
    if (mode && !normalized(job.mode).includes(mode)) return false;
    if (kind === 'Junior / profesional' && job.kind !== 'Profesional') return false;
    if (kind && kind !== 'Junior / profesional' && job.kind !== kind) return false;
    if (family && !normalized(job.family).includes(family)) return false;
    if (sector && job.sector !== sector) return false;
    if (level && job.level !== level) return false;
    if (filters.salary.value === 'published' && (!job.salary || /no publicado|no especificado/i.test(job.salary))) return false;
    if (filters.risk.value === 'temporary' && !temporarySignal.test([job.title, job.duration, job.deadline, job.continuity, job.risk].join(' '))) return false;
    const searchable = normalized([
      job.title, job.employer, job.sector, job.family, job.level,
      job.kind, job.mode, job.location, job.eligibility, job.skills,
      job.tasks, job.requirements,
    ].join(' '));
    return tokens.every((token) => searchable.includes(token));
  }).sort((a, b) => {
    const rank = (job) => currentStates(job).publicationStatus === 'active' ? 0 : currentStates(job).publicationStatus === 'historical' ? 2 : 1;
    return rank(a) - rank(b) || a.employer.localeCompare(b.employer, 'es') || a.title.localeCompare(b.title, 'es');
  });
}

function publicCatalogMetrics(records) {
  const metrics = { active: 0, expiredOrHistorical: 0, unconfirmed: 0 };
  records.filter((job) => job.recordKind !== 'demonstration').forEach((job) => {
    const state = currentStates(job);
    if (state.publicationStatus === 'active') metrics.active += 1;
    else if (['expired', 'closed'].includes(state.opportunityStatus) || state.publicationStatus === 'historical') metrics.expiredOrHistorical += 1;
    else metrics.unconfirmed += 1;
  });
  return metrics;
}

function updateCatalogView() {
  if (catalogLoadError) {
    catalog = [];
    opportunities = [];
    list.innerHTML = '';
    list.hidden = true;
    empty.hidden = false;
    empty.querySelector('h3').textContent = 'No se pudo cargar el catálogo';
    empty.querySelector('p').textContent = 'Vuelve a intentarlo más tarde.';
    document.querySelector('#empty-clear').hidden = true;
    count.textContent = 'Catálogo local no disponible';
    return;
  }
  opportunities = getVisibleJobs();
  const includeExamples = document.querySelector('#include-demonstrations').checked;
  const includeOtherStates = document.querySelector('#include-unconfirmed').checked || filters.history.checked;
  const showNoVerifiedOpportunities = !includeExamples && !includeOtherStates;
  empty.querySelector('h3').textContent = showNoVerifiedOpportunities ? 'No hay oportunidades verificadas disponibles' : 'No encontramos coincidencias';
  empty.querySelector('p').textContent = showNoVerifiedOpportunities
    ? 'Las oportunidades se incorporan después de revisar la publicación original y el canal de postulación. Puedes activar “Incluir ejemplos demostrativos” para explorar ejemplos que no son vacantes reales.'
    : 'Prueba quitar algún filtro. Los ejemplos demostrativos nunca representan vacantes reales ni habilitan la postulación.';
  document.querySelector('#empty-clear').hidden = false;
  render();
}

function setFilterOptions(select, values, placeholder, selectedValue = '') {
  const options = [...new Set(values.filter((value) => value && value !== 'No especificado' && value !== 'Por clasificar'))]
    .sort((a, b) => a.localeCompare(b, 'es'));
  select.replaceChildren(new Option(placeholder, ''), ...options.map((value) => new Option(value, value)));
  if (options.includes(selectedValue)) select.value = selectedValue;
}

function populateFilters() {
  setFilterOptions(filters.kind, catalog.map((job) => job.kind === 'Profesional' ? 'Junior / profesional' : job.kind), 'Tipo de oportunidad', filters.kind.value);
  setFilterOptions(filters.sector, catalog.map((job) => job.sector), 'Todos los sectores', filters.sector.value);
  setFilterOptions(filters.level, catalog.map((job) => job.level), 'Todos los niveles', filters.level.value);
  setFilterOptions(filters.family, catalog.map((job) => job.family), 'Familia profesional', filters.family.value);
}

function renderDialog(job) {
  const state = currentStates(job);
  const sourceUrl = safeHttpsUrl(job.sourceUrl);
  const applyUrl = safeHttpsUrl(job.applyUrl);
  const canApply = state.publicationStatus === 'active' && job.recordKind !== 'demonstration';
  const risk = job.risk || 'La fuente no especifica esta condición. Confírmala en el anuncio original.';
  const statusText = canApply
    ? `La fuente del empleador se revisó el ${job.lastVerifiedAt}; esta comprobación no garantiza disponibilidad posterior.`
    : state.opportunityStatus === 'expired'
      ? 'La fecha límite de postulación ya pasó. Se conserva como referencia y no se habilita el enlace para postular.'
      : state.publicationStatus === 'historical'
        ? 'Registro histórico conservado para referencia. No está disponible para postular.'
        : `${job.recordKind === 'demonstration' ? 'Ficha de demostración. ' : ''}No tiene evidencia vigente suficiente para presentarla como postulable. Última verificación: ${job.lastVerifiedAt || 'no disponible'}; última consulta registrada: ${job.lastCheckedDate || 'no disponible'}. No se afirma que siga publicada.`;
  const fieldEvidence = Array.isArray(job.fieldEvidence) ? job.fieldEvidence : [];
  const evidenceLabels = { employer: 'Empleador', publisher: 'Difusor', title: 'Puesto', applyUrl: 'Canal de postulación', deadline: 'Fecha límite', salary: 'Remuneración', mode: 'Modalidad', location: 'Ubicación', requirements: 'Requisitos', benefits: 'Beneficios', skills: 'Tecnologías', training: 'Formación', contractType: 'Tipo de contrato', duration: 'Duración', sector: 'Sector', family: 'Familia profesional', level: 'Nivel', kind: 'Tipo de oportunidad', growth: 'Experiencia para el siguiente paso', continuity: 'Continuidad', risk: 'Riesgos' };
  const fieldEvidenceHtml = fieldEvidence.filter((item) => evidenceLabels[item.field] && safeHttpsUrl(item.url)).map((item) => `<li><a href="${escapeHTML(safeHttpsUrl(item.url))}" target="_blank" rel="noopener noreferrer">${escapeHTML(evidenceLabels[item.field])} · evidencia ↗</a> <span>${escapeHTML(item.observedAt || 'fecha no disponible')}</span></li>`).join('');
  const sourcePublisher = job.publisher || 'No identificado en esta ficha';
  const evidenceLink = job.evidenceUrl ? `<a class="detail-evidence-link" href="${escapeHTML(safeHttpsUrl(job.evidenceUrl) || '#')}" target="_blank" rel="noopener noreferrer">Abrir bases/documento de evidencia ↗</a>` : '';
  dialogContent.innerHTML = `<p class="dialog-eyebrow">${escapeHTML(job.requisition || job.id)} · ${escapeHTML(job.sourceKind || 'Fuente de empleo')}</p>
    <h2 class="dialog-title" id="dialog-title">${escapeHTML(job.title)}</h2><p class="dialog-company">Empleador: ${escapeHTML(job.employer || 'No informado')} · ${escapeHTML(job.sector || 'Sector no informado')}</p>
    <div class="dialog-tags">${statusTag(job)}${modeTag(job)}<span class="tag">${escapeHTML(job.level || 'Nivel no especificado')}</span></div>
    <div class="evidence-box ${canApply ? '' : 'warning'}"><b>${canApply ? 'Qué se verificó' : 'Estado de publicación'}</b><p>${escapeHTML(statusText)}</p></div>
    <div class="detail-grid">
      <div class="detail-item"><label>Modalidad</label><p>${escapeHTML(job.mode || 'No especificada')}</p></div>
      <div class="detail-item"><label>Entidad que difunde</label><p>${escapeHTML(sourcePublisher)}</p></div>
      <div class="detail-item"><label>Elegibilidad / ubicación</label><p>${escapeHTML(job.eligibility || job.location || 'No confirmada')}</p></div>
      <div class="detail-item"><label>Compensación</label><p>${escapeHTML(job.salary || 'No publicado')}${job.salaryNote ? ` · ${escapeHTML(job.salaryNote)}` : ''}</p></div>
      <div class="detail-item"><label>Contrato / plazo</label><p>${escapeHTML(job.duration || 'No especificado')}</p></div>
      <div class="detail-item"><label>Fecha límite</label><p>${escapeHTML(job.deadline || 'No indicada')}</p></div>
      <div class="detail-item"><label>Última consulta registrada</label><p>${escapeHTML(job.lastCheckedDate || 'No disponible')}</p></div>
    </div>
    <section class="detail-section"><h3>Qué harías</h3><p>${escapeHTML(job.tasks || 'La descripción completa se consulta en la fuente original.')}</p></section>
    <section class="detail-section"><h3>Qué experiencia podrías llevar al siguiente paso</h3><p>${escapeHTML(job.growth || 'Encaje y experiencia todavía no analizados.')}</p></section>
    <section class="detail-section"><h3>Requisitos y herramientas</h3><p>${escapeHTML(job.requirements || 'Revisar requisitos en la publicación original.')}${job.skills ? `<br /><br /><b>Tecnologías/señales:</b> ${escapeHTML(job.skills)}` : ''}</p></section>
    <section class="detail-section"><h3>Continuidad y riesgos</h3><p>${escapeHTML(job.continuity || 'No informada.') } ${escapeHTML(risk)}</p></section>
    <section class="detail-section"><h3>Beneficios publicados</h3><p>${escapeHTML(job.benefits || 'No informados; revisar condiciones en la publicación original.')}</p></section>
    ${job.editorialDecision?.reason ? `<section class="detail-section"><h3>Decisión editorial</h3><p>${escapeHTML(job.editorialDecision.status || 'Registrada')} · ${escapeHTML(job.editorialDecision.reason)}${job.editorialDecision.decidedAt ? ` (${escapeHTML(job.editorialDecision.decidedAt)})` : ''}</p></section>` : ''}
    ${sourceUrl ? `<p class="external-note">Ficha informativa: <a href="${escapeHTML(sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHTML(job.sourceKind || sourcePublisher)} ↗</a></p>` : ''}
    ${fieldEvidenceHtml ? `<section class="detail-section"><h3>Procedencia por dato</h3><ul class="field-evidence-list">${fieldEvidenceHtml}</ul></section>` : '<section class="detail-section"><h3>Procedencia por dato</h3><p>No hay evidencia desglosada por campo en esta ficha.</p></section>'}
    ${evidenceLink ? `<p class="external-note">${evidenceLink}</p>` : ''}
    ${canApply && applyUrl ? `<a class="apply-link" href="${escapeHTML(applyUrl)}" target="_blank" rel="noopener noreferrer">Ir a postulación <span aria-hidden="true">↗</span></a>` : '<p class="apply-disabled">Postulación deshabilitada hasta contar con una verificación vigente y un canal de postulación comprobado.</p>'}
    <p class="external-note">No guardamos tu CV ni enviamos postulaciones desde este prototipo.</p>`;
  dialog.showModal();
}

function notify(message) {
  const toast = document.querySelector('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

let searchDebounce;

async function loadCatalog() {
  const refreshButton = document.querySelector('#catalog-refresh');
  refreshButton.disabled = true;
  refreshButton.textContent = 'Actualizando…';
  try {
    const response = await fetch('./data/opportunities.json', { headers: { Accept: 'application/json' }, cache: 'no-cache' });
    if (!response.ok) throw new Error('El catálogo publicado no respondió.');
    const result = await response.json();
    if (!isValidCatalogPayload(result)) throw new Error('El catálogo no cumple el esquema de publicación esperado.');
    catalogLoadError = false;
    catalog = result.opportunities;
    catalogConfig = result;
    populateFilters();
    const realJobs = catalog.filter((job) => job.recordKind !== 'demonstration');
    const metrics = publicCatalogMetrics(catalog);
    const checkedDates = realJobs.map((job) => job.lastCheckedDate).filter(Boolean).sort();
    document.querySelector('#metric-total').textContent = metrics.active;
    document.querySelector('#metric-primary').textContent = metrics.expiredOrHistorical;
    document.querySelector('#metric-secondary').textContent = metrics.unconfirmed;
    const generatedAt = result.generatedAt ? new Date(result.generatedAt) : null;
    document.querySelector('#catalog-generated-at').textContent = generatedAt && !Number.isNaN(generatedAt.valueOf())
      ? `Generado ${generatedAt.toLocaleString('es-PE', { timeZone: 'America/Lima', dateStyle: 'medium', timeStyle: 'short' })}`
      : 'Fecha de actualización no disponible';
    document.querySelector('#catalog-last-checked').textContent = checkedDates.length
      ? `Última consulta registrada: ${checkedDates.at(-1)}`
      : 'Sin consultas registradas sobre oportunidades reales';
    document.querySelector('#catalog-source-note').textContent = result.sourceNote || 'Revisa cada publicación en su fuente original.';
    updateCatalogView();
  } catch {
    catalogLoadError = true;
    catalog = [];
    opportunities = [];
    document.querySelector('#metric-total').textContent = '—';
    document.querySelector('#metric-primary').textContent = '—';
    document.querySelector('#metric-secondary').textContent = '—';
    document.querySelector('#catalog-generated-at').textContent = 'Fecha de actualización no disponible';
    document.querySelector('#catalog-last-checked').textContent = 'No se pudo consultar el catálogo.';
    document.querySelector('#catalog-source-note').textContent = 'No se pudo cargar el catálogo. Reintenta en unos momentos.';
    updateCatalogView();
  } finally {
    refreshButton.disabled = false;
    refreshButton.textContent = '↻ Actualizar';
  }
}

filters.query.addEventListener('input', () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(updateCatalogView, 120);
});
filters.location.addEventListener('input', () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(updateCatalogView, 120);
});
filters.mode.addEventListener('change', updateCatalogView);
filters.kind.addEventListener('change', updateCatalogView);
filters.family.addEventListener('change', updateCatalogView);
filters.sector.addEventListener('change', updateCatalogView);
filters.level.addEventListener('change', updateCatalogView);
filters.salary.addEventListener('change', updateCatalogView);
filters.risk.addEventListener('change', updateCatalogView);
filters.history.addEventListener('change', updateCatalogView);
document.querySelector('#include-unconfirmed').addEventListener('change', updateCatalogView);
document.querySelector('#include-demonstrations').addEventListener('change', updateCatalogView);
document.querySelector('#filters').addEventListener('submit', (event) => event.preventDefault());
document.querySelector('#filters').addEventListener('reset', () => setTimeout(() => {
  filters.family.value = '';
  updateCatalogView();
}, 0));

document.querySelector('#empty-clear').addEventListener('click', () => document.querySelector('#filters').reset());
document.querySelector('#catalog-refresh').addEventListener('click', loadCatalog);
list.addEventListener('click', (event) => {
  const button = event.target.closest('[data-open]');
  if (!button) return;
  const job = opportunities.find((item) => item.id === button.dataset.open);
  if (job) renderDialog(job);
});
list.addEventListener('keydown', (event) => {
  const title = event.target.closest('[data-open][role="button"]');
  if (title && (event.key === 'Enter' || event.key === ' ')) {
    event.preventDefault();
    const job = opportunities.find((item) => item.id === title.dataset.open);
    if (job) renderDialog(job);
  }
});
document.addEventListener('keydown', (event) => {
  if (event.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && !dialog.open) {
    event.preventDefault();
    filters.query.focus();
  }
});

loadCatalog();
