let catalog = [];
let opportunities = [];

const list = document.querySelector('#job-list');
const count = document.querySelector('#result-count');
const empty = document.querySelector('#empty-state');
const dialog = document.querySelector('#job-dialog');
const dialogContent = document.querySelector('#dialog-content');
const filters = {
  query: document.querySelector('#query'),
  mode: document.querySelector('#mode'),
  kind: document.querySelector('#kind'),
  family: document.querySelector('#family'),
  history: document.querySelector('#include-history'),
};
let toastTimer;

function escapeHTML(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function safeHttpsUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : null;
  } catch {
    return null;
  }
}

function initials(name) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0] || '').join('').toUpperCase();
}

function statusTag(job) {
  if (job.status === 'verified') return '<span class="tag verified">✓ Fuente oficial revisada</span>';
  if (job.status === 'secondary') return '<span class="tag unverified">! Fuente secundaria</span>';
  return '<span class="tag closed">Convocatoria cerrada</span>';
}

function modeTag(job) {
  const mode = job.mode || 'No especificado';
  const className = mode.toLowerCase().includes('remoto') ? 'remote' : 'mode';
  return `<span class="tag ${className}">${escapeHTML(mode)}</span>`;
}

function renderCard(job) {
  const id = escapeHTML(job.id);
  const targetClass = job.sector === 'Sector público' ? 'public' : (job.sector === 'Banca y finanzas' ? 'bank' : '');
  const salary = job.salary && job.salary !== 'No publicado' ? escapeHTML(job.salary) : 'No publicado';
  const familyLabel = job.family === 'Desarrollo y QA' ? job.family : job.family;
  const metaDate = `Revisada ${escapeHTML(job.checked || '—')}`;
  const typeLabel = job.history ? 'Histórica' : (job.kind === 'Profesional' ? job.level : job.kind);
  return `<article class="job-card grid grid-cols-1 items-center gap-3 rounded-lg border border-[#e5e9e4] bg-white p-4 transition hover:-translate-y-px hover:border-[#cbd8cb] md:grid-cols-[minmax(0,1fr)_150px_154px]" data-id="${id}">
    <div class="job-main flex min-w-0 items-start gap-3">
      <div class="company-mark ${targetClass}" aria-hidden="true">${escapeHTML(initials(job.employer))}</div>
      <div class="job-copy min-w-0">
        <div class="job-title-row"><h3 class="job-title" role="button" tabindex="0" data-open="${id}">${escapeHTML(job.title)}</h3>${statusTag(job)}</div>
        <p class="company-name">${escapeHTML(job.employer)} <span>·</span> ${escapeHTML(job.sector)}</p>
        <div class="job-tags flex flex-wrap gap-1">${modeTag(job)}<span class="tag">${escapeHTML(familyLabel)}</span><span class="tag ${job.level === 'Senior' ? 'senior' : ''}">${escapeHTML(typeLabel)}</span></div>
        <p class="job-location">⌖ ${escapeHTML(job.location || 'Ubicación no especificada')} <span>·</span> ${escapeHTML(job.eligibility || 'Elegibilidad no confirmada')}</p>
      </div>
    </div>
    <div class="job-fit"><strong>${job.status === 'closed' ? 'Solo referencia histórica' : escapeHTML(job.fitLabel || 'Encaje por revisar')}</strong><span>${escapeHTML(job.growth || '')}</span></div>
    <div class="job-meta flex flex-col items-end gap-2 md:col-auto md:row-auto"> <strong class="salary ${salary === 'No publicado' ? 'missing' : ''}">${salary}</strong><span class="check-date">${metaDate}</span><button class="card-button rounded border border-[#dae4da] bg-white px-3 py-2 text-[#345d44] hover:bg-[#eef4ee]" type="button" data-open="${id}">Ver evidencia <span aria-hidden="true">↗</span></button></div>
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
  const mode = normalized(filters.mode.value);
  const kind = filters.kind.value;
  const family = normalized(filters.family.value);
  return catalog.filter((job) => {
    if (!filters.history.checked && job.history) return false;
    if (mode && !normalized(job.mode).includes(mode)) return false;
    if (kind === 'Junior / profesional' && job.kind !== 'Profesional') return false;
    if (kind && kind !== 'Junior / profesional' && job.kind !== kind) return false;
    if (family && !normalized(job.family).includes(family)) return false;
    const searchable = normalized([
      job.title, job.employer, job.sector, job.family, job.level,
      job.kind, job.mode, job.location, job.eligibility, job.skills,
      job.tasks, job.requirements,
    ].join(' '));
    return tokens.every((token) => searchable.includes(token));
  }).sort((a, b) => {
    const rank = (job) => job.status === 'closed' ? 2 : job.status === 'verified' ? 0 : 1;
    return rank(a) - rank(b) || a.employer.localeCompare(b.employer, 'es') || a.title.localeCompare(b.title, 'es');
  });
}

function updateCatalogView() {
  opportunities = getVisibleJobs();
  empty.querySelector('h3').textContent = 'No encontramos coincidencias';
  empty.querySelector('p').textContent = 'Prueba quitar algún filtro o buscar con otras palabras.';
  document.querySelector('#empty-clear').hidden = false;
  render();
}

function renderDialog(job) {
  const sourceUrl = safeHttpsUrl(job.sourceUrl);
  const applyUrl = safeHttpsUrl(job.applyUrl || job.sourceUrl);
  const risk = job.risk || 'La fuente no especifica esta condición. Confírmala en el anuncio original.';
  const statusText = job.status === 'verified'
    ? `Revisamos la publicación oficial el ${job.checked}. La fecha no garantiza disponibilidad después de esa revisión.`
    : job.status === 'secondary'
      ? `La publicación se encontró en ${job.sourceKind || 'una fuente secundaria'} y aparece disponible allí. No se encontró una confirmación equivalente en el portal corporativo durante esta revisión.`
      : 'La convocatoria está cerrada y se conserva solo como referencia histórica.';
  const applyLabel = job.status === 'closed' ? 'Ver publicación original' : (job.status === 'verified' ? 'Ir a la postulación oficial' : 'Comprobar publicación y postulación');
  const evidenceLink = job.evidenceUrl ? `<a class="detail-evidence-link" href="${escapeHTML(safeHttpsUrl(job.evidenceUrl) || '#')}" target="_blank" rel="noopener noreferrer">Abrir bases/documento de evidencia ↗</a>` : '';
  dialogContent.innerHTML = `<p class="dialog-eyebrow">${escapeHTML(job.requisition || job.id)} · ${escapeHTML(job.sourceKind || 'Fuente de empleo')}</p>
    <h2 class="dialog-title" id="dialog-title">${escapeHTML(job.title)}</h2><p class="dialog-company">${escapeHTML(job.employer)} · ${escapeHTML(job.sector)}</p>
    <div class="dialog-tags">${statusTag(job)}${modeTag(job)}<span class="tag">${escapeHTML(job.level || 'Nivel no especificado')}</span></div>
    <div class="evidence-box ${job.status === 'verified' ? '' : 'warning'}"><b>${job.status === 'verified' ? 'Qué se verificó' : 'Qué falta comprobar'}</b><p>${escapeHTML(statusText)}</p></div>
    <div class="detail-grid">
      <div class="detail-item"><label>Modalidad</label><p>${escapeHTML(job.mode || 'No especificada')}</p></div>
      <div class="detail-item"><label>Elegibilidad / ubicación</label><p>${escapeHTML(job.eligibility || job.location || 'No confirmada')}</p></div>
      <div class="detail-item"><label>Compensación</label><p>${escapeHTML(job.salary || 'No publicado')}${job.salaryNote ? ` · ${escapeHTML(job.salaryNote)}` : ''}</p></div>
      <div class="detail-item"><label>Contrato / plazo</label><p>${escapeHTML(job.duration || 'No especificado')}</p></div>
      <div class="detail-item"><label>Fecha límite</label><p>${escapeHTML(job.deadline || 'No indicada')}</p></div>
      <div class="detail-item"><label>Última revisión</label><p>${escapeHTML(job.checked || 'No revisada')}</p></div>
    </div>
    <section class="detail-section"><h3>Qué harías</h3><p>${escapeHTML(job.tasks || 'La descripción completa se consulta en la fuente original.')}</p></section>
    <section class="detail-section"><h3>Qué experiencia podrías llevar al siguiente paso</h3><p>${escapeHTML(job.growth || 'Encaje y experiencia todavía no analizados.')}</p></section>
    <section class="detail-section"><h3>Requisitos y herramientas</h3><p>${escapeHTML(job.requirements || 'Revisar requisitos en la publicación original.')}${job.skills ? `<br /><br /><b>Tecnologías/señales:</b> ${escapeHTML(job.skills)}` : ''}</p></section>
    <section class="detail-section"><h3>Continuidad y riesgos</h3><p>${escapeHTML(job.continuity || 'No informada.') } ${escapeHTML(risk)}</p></section>
    <section class="detail-section"><h3>Beneficios publicados</h3><p>${escapeHTML(job.benefits || 'No informados; revisar condiciones en la publicación original.')}</p></section>
    ${sourceUrl ? `<p class="external-note">Fuente principal: <a href="${escapeHTML(sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHTML(job.sourceKind || 'publicación original')} ↗</a></p>` : ''}
    ${evidenceLink ? `<p class="external-note">${evidenceLink}</p>` : ''}
    ${applyUrl ? `<a class="apply-link" href="${escapeHTML(applyUrl)}" target="_blank" rel="noopener noreferrer">${escapeHTML(applyLabel)} <span aria-hidden="true">↗</span></a>` : ''}
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
  try {
    const response = await fetch('./data/opportunities.json', { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('El catálogo publicado no respondió.');
    const result = await response.json();
    catalog = Array.isArray(result.opportunities) ? result.opportunities : [];
    const activeJobs = catalog.filter((job) => !job.history);
    document.querySelector('#metric-total').textContent = activeJobs.length;
    document.querySelector('#metric-primary').textContent = activeJobs.filter((job) => job.status === 'verified').length;
    document.querySelector('#metric-secondary').textContent = activeJobs.filter((job) => job.status === 'secondary').length;
    updateCatalogView();
  } catch {
    catalog = [];
    opportunities = [];
    list.innerHTML = '';
    list.hidden = true;
    empty.hidden = false;
    empty.querySelector('h3').textContent = 'No se pudo cargar el catálogo';
    empty.querySelector('p').textContent = 'Inténtalo de nuevo más tarde. Si el problema continúa, avísanos.';
    document.querySelector('#empty-clear').hidden = true;
    count.textContent = 'Catálogo local no disponible';
  }
}

filters.query.addEventListener('input', () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(updateCatalogView, 120);
});
filters.mode.addEventListener('change', updateCatalogView);
filters.kind.addEventListener('change', updateCatalogView);
filters.family.addEventListener('change', updateCatalogView);
filters.history.addEventListener('change', updateCatalogView);
document.querySelector('#filters').addEventListener('submit', (event) => event.preventDefault());
document.querySelector('#filters').addEventListener('reset', () => setTimeout(updateCatalogView, 0));

document.querySelector('#empty-clear').addEventListener('click', () => document.querySelector('#filters').reset());
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
