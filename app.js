let catalog = [];
let opportunities = [];
const PAGE_SIZE = 12;
let pageSize = PAGE_SIZE;
let currentPage = 1;

const catalogView = document.querySelector('#catalog-view');
const opportunityView = document.querySelector('#opportunity-view');
const list = document.querySelector('#job-list');
const count = document.querySelector('#result-count');
const empty = document.querySelector('#empty-state');
const pagination = document.querySelector('#pagination');
const prevPageBtn = document.querySelector('#prev-page');
const nextPageBtn = document.querySelector('#next-page');
const paginationInfo = document.querySelector('#pagination-info');
const dialog = document.querySelector('#job-dialog');
const dialogContent = document.querySelector('#dialog-content');
const compareDialog = document.querySelector('#compare-dialog');
const compareContent = document.querySelector('#compare-content');
const comparePanel = document.querySelector('#compare-panel');
const compareSummary = document.querySelector('#compare-summary');
const compareOpen = document.querySelector('#compare-open');
const compareClear = document.querySelector('#compare-clear');
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
  regime: document.querySelector('#regime-filter'),
  history: document.querySelector('#include-history'),
};
let toastTimer;
let catalogLoadError = false;
let compareIds = [];

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

function isTimestamp(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return false;
  return !Number.isNaN(new Date(value).valueOf());
}

function isValidCatalogPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)
    || payload.schemaVersion !== 2
    || payload.timezone !== 'America/Lima'
    || typeof payload.sourceNote !== 'string'
    || !Number.isInteger(payload.verificationTtlDays)
    || payload.verificationTtlDays < 1 || payload.verificationTtlDays > 30
    || !isTimestamp(payload.generatedAt)
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
    for (const field of ['lastVerifiedAt', 'editorialDecision?.decidedAt']) {
      const value = field === 'lastVerifiedAt' ? job.lastVerifiedAt : job.editorialDecision?.decidedAt;
      if (value !== undefined && value !== null && value !== '' && !isTimestamp(value)) return false;
    }
    if (job.lastCheckedDate !== undefined && job.lastCheckedDate !== null && job.lastCheckedDate !== '' && !isCivilDate(job.lastCheckedDate)) return false;
    if (job.verificationEvidence !== undefined) {
      if (!job.verificationEvidence || typeof job.verificationEvidence !== 'object' || Array.isArray(job.verificationEvidence)) return false;
      if (job.verificationEvidence.observedAt !== undefined && !isTimestamp(job.verificationEvidence.observedAt)) return false;
      if (job.verificationEvidence.url !== undefined
        && (!safeHttpsUrl(job.verificationEvidence.url)
          || !job.allowedHosts.includes(new URL(safeHttpsUrl(job.verificationEvidence.url)).hostname.toLowerCase()))) return false;
    }
    if (job.fieldEvidence !== undefined) {
      const evidenceFields = new Set([
        'employer', 'publisher', 'title', 'sourceUrl', 'applyUrl', 'publishedAt', 'deadline',
        'location', 'mode', 'salary', 'benefits', 'contractType', 'duration', 'requirements',
        'skills', 'training', 'tasks', 'eligibility', 'sector', 'family', 'level', 'kind',
        'growth', 'continuity', 'risk',
      ]);
      if (!Array.isArray(job.fieldEvidence)) return false;
      const seenFields = new Set();
      if (job.fieldEvidence.some((entry) => {
        if (!entry || typeof entry !== 'object' || Array.isArray(entry)
          || !evidenceFields.has(entry.field) || seenFields.has(entry.field)
          || !isTimestamp(entry.observedAt)) return true;
        const evidenceUrl = safeHttpsUrl(entry.url);
        if (!evidenceUrl || !job.allowedHosts.includes(new URL(evidenceUrl).hostname.toLowerCase())) return true;
        seenFields.add(entry.field);
        return false;
      })) return false;
    }
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
  const dayNumber = (isoDate) => Date.parse(`${isoDate}T00:00:00Z`);

  // 1. Tratamiento estricto de cierre y fecha límite vencida
  if (job.deadline && job.deadline < today && !['closed', 'expired'].includes(states.opportunityStatus)) {
    states.opportunityStatus = 'expired';
  }

  // 2. Cálculo determinista de fechas y antigüedad
  const checked = job.lastVerifiedAt && isTimestamp(job.lastVerifiedAt) ? new Date(job.lastVerifiedAt) : null;
  const checkedDate = checked && !Number.isNaN(checked.valueOf()) ? limaDateString(checked) : '';
  const ageDays = checkedDate ? (dayNumber(today) - dayNumber(checkedDate)) / 86400000 : Infinity;

  const evidence = job.verificationEvidence;
  const observed = evidence?.observedAt && isTimestamp(evidence.observedAt) ? new Date(evidence.observedAt) : null;
  const observedDate = observed && !Number.isNaN(observed.valueOf()) ? limaDateString(observed) : '';
  const lowerBound = limaDateString(new Date(dayNumber(today) - ttlDays * 86400000));

  const safeHosts = new Set(job.allowedHosts || []);
  const permitted = (value) => {
    const safeUrl = safeHttpsUrl(value);
    const host = safeUrl ? new URL(safeUrl).hostname.toLowerCase() : '';
    return Boolean(host && safeHosts.has(host));
  };

  const decision = job.editorialDecision;
  const approvedEditorially = decision?.status === 'approved'
    && Boolean(decision.reviewer && decision.reason)
    && decision.decidedAt && !Number.isNaN(new Date(decision.decidedAt).valueOf())
    && limaDateString(new Date(decision.decidedAt)) <= today;

  const fieldEvidence = Array.isArray(job.fieldEvidence) ? job.fieldEvidence : [];
  const evidenceByField = new Map(fieldEvidence.map((entry) => [entry.field, entry]));
  const requiredEvidence = ['employer', 'publisher', 'title', 'sourceUrl', 'applyUrl'];
  const optionalFacts = [
    'publishedAt', 'deadline', 'location', 'mode', 'salary', 'benefits',
    'contractType', 'duration', 'requirements', 'skills', 'training', 'tasks',
    'eligibility', 'sector', 'family', 'level', 'kind', 'growth', 'continuity', 'risk',
  ];
  const claimedFields = [
    ...requiredEvidence,
    ...optionalFacts.filter((field) => job[field] !== null && job[field] !== undefined && job[field] !== ''),
  ];

  // 3. Integridad estructural y de procedencia (requisito invariable de publicación activa)
  const structureValid = Boolean(
    job.recordKind !== 'demonstration'
    && job.employer && String(job.employer).trim()
    && job.publisher && String(job.publisher).trim()
    && job.title && String(job.title).trim()
    && permitted(job.sourceUrl)
    && permitted(job.applyUrl)
    && evidence
    && evidence.publisherRelation === 'employer_confirmed'
    && evidence.method === 'manual'
    && evidence.result === 'application_open'
    && permitted(evidence.url)
    && observedDate && observedDate <= today
    && approvedEditorially
    && claimedFields.every((field) => {
      const entry = evidenceByField.get(field);
      const obs = entry?.observedAt && isTimestamp(entry.observedAt) ? new Date(entry.observedAt) : null;
      const obsDate = obs && !Number.isNaN(obs.valueOf()) ? limaDateString(obs) : '';
      return Boolean(permitted(entry?.url) && obsDate && obsDate <= today);
    })
  );

  // 4. Frescura temporal (dentro del TTL editorial de verificación)
  const withinTtl = ageDays >= 0 && ageDays <= ttlDays
    && observedDate >= lowerBound && observedDate <= today
    && claimedFields.every((field) => {
      const entry = evidenceByField.get(field);
      const obs = entry?.observedAt && isTimestamp(entry.observedAt) ? new Date(entry.observedAt) : null;
      const obsDate = obs && !Number.isNaN(obs.valueOf()) ? limaDateString(obs) : '';
      return Boolean(obsDate && obsDate >= lowerBound && obsDate <= today);
    });

  // 5. Determinación de estados resultantes respetando las dimensiones del modelo
  if (job.recordKind === 'demonstration') {
    states.publicationStatus = 'unconfirmed';
    states.verificationStatus = 'unverified';
    if (job.opportunityStatus === 'closed' || states.opportunityStatus === 'expired') {
      states.publicationStatus = 'historical';
    }
  } else if (states.opportunityStatus === 'expired' || states.opportunityStatus === 'closed' || job.publicationStatus === 'historical') {
    states.publicationStatus = 'historical';
    if (structureValid && withinTtl) {
      states.verificationStatus = 'verified';
    } else if (structureValid && !withinTtl) {
      states.verificationStatus = 'stale';
    }
  } else if (job.publicationStatus === 'active') {
    if (structureValid && withinTtl) {
      states.publicationStatus = 'active';
      states.verificationStatus = 'verified';
    } else if (structureValid && !withinTtl) {
      // Supera el TTL o evidencia no vigente: deja de presentarse como activa y pasa a revisión
      states.publicationStatus = 'unconfirmed';
      states.verificationStatus = 'stale';
    } else {
      // Inconsistencia estructural: tratamiento fail-closed
      states.publicationStatus = 'unconfirmed';
      states.verificationStatus = 'unverified';
    }
  } else {
    if (structureValid) {
      states.verificationStatus = withinTtl ? 'verified' : 'stale';
    } else {
      states.verificationStatus = 'unverified';
    }
  }

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
  if (state.opportunityStatus === 'expired') {
    return '<span class="tag closed inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200">Plazo vencido</span>';
  }
  if (state.publicationStatus === 'historical' || state.opportunityStatus === 'closed') {
    return '<span class="tag closed inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">Referencia histórica</span>';
  }
  if (state.publicationStatus === 'active') {
    if (state.verificationStatus === 'verified') {
      return '<span class="tag verified inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">Activa · revisión reciente</span>';
    }
    return '<span class="tag unverified inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-stone-100 text-stone-600 border border-stone-200">Activa · sin verificar</span>';
  }
  if (state.verificationStatus === 'stale') {
    return '<span class="tag stale inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-800 border border-amber-200">Pendiente de revalidación</span>';
  }
  return `<span class="tag unverified inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-stone-100 text-stone-600 border border-stone-200">${job.recordKind === 'demonstration' ? 'Ficha demostrativa' : 'No confirmada'}</span>`;
}

function modeTag(job) {
  const mode = job.mode || 'No especificada';
  const isRemote = mode.toLowerCase().includes('remoto');
  const className = isRemote ? 'remote' : 'mode';
  const colorClass = isRemote
    ? 'bg-iceBlue/15 text-arcticBlue border border-crystalBlue/20'
    : 'bg-surfaceRaised text-brandDark border border-borderMuted';
  return `<span class="tag ${className} inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${colorClass}">${escapeHTML(mode)}</span>`;
}

function formatLocationEligibility(job) {
  const loc = (job.location || '').trim();
  const elig = (job.eligibility || '').trim();
  if (loc && elig) {
    if (loc.toLowerCase() === elig.toLowerCase()) return loc;
    if (loc.toLowerCase().includes(elig.toLowerCase())) return loc;
    return `${loc} (Elegibilidad: ${elig})`;
  }
  return loc || elig || 'No confirmada';
}

function formatContractDuration(job) {
  const contract = (job.contractType || '').trim();
  const duration = (job.duration || '').trim();
  const continuity = (job.continuity || '').trim();
  const parts = [];
  const ign = /^(?:no especificad[oa]|no informad[oa]|no aplica)/i;
  if (contract && !ign.test(contract)) parts.push(contract);
  if (duration && !ign.test(duration)) parts.push(duration);
  if (continuity && !ign.test(continuity)) {
    if (!parts.some((p) => p.toLowerCase().includes(continuity.toLowerCase()) || continuity.toLowerCase().includes(p.toLowerCase()))) {
      parts.push(continuity);
    }
  }
  return parts.length > 0 ? parts.join(' · ') : 'No especificado';
}

function renderCard(job) {
  const state = currentStates(job);
  const id = escapeHTML(job.id);
  const isCompared = compareIds.includes(job.id);
  const targetClass = job.sector === 'Sector público' ? 'public' : (job.sector === 'Banca y finanzas' ? 'bank' : '');
  const salaryKnown = job.salary && !/no publicado|no especificado/i.test(job.salary);
  const salary = salaryKnown ? escapeHTML(job.salary) : 'No publicado';
  const familyLabel = job.family === 'Desarrollo y QA' ? job.family : job.family;
  const metaDate = `Consulta registrada ${escapeHTML(job.lastCheckedDate || 'No disponible')}`;
  const typeLabel = job.recordKind === 'demonstration' ? 'Ficha de demostración' : (job.kind === 'Profesional' ? job.level : job.kind);
  const fitStatus = state.publicationStatus === 'active'
    ? 'Oportunidad activa · Verificada'
    : state.verificationStatus === 'stale'
      ? 'Pendiente de revalidación'
      : (state.publicationStatus === 'historical' || state.opportunityStatus === 'expired')
        ? 'No disponible para postular'
        : 'Vigencia no confirmada';
  return `<article class="job-card group grid grid-cols-1 gap-4 rounded-xl border border-borderMuted bg-white p-4 transition-colors duration-150 hover:border-crystalBlue/50 sm:p-5 lg:grid-cols-[minmax(0,1fr)_170px_190px] lg:items-center lg:gap-5"
  data-id="${id}" >
    <!-- IZQUIERDA: Información del empleo -->
    <div class="flex min-w-0 items-start gap-3.5">

      <!-- Identidad de empresa -->
      <div
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-md font-bold text-arcticBlue"
        aria-hidden="true"
      >
        ${escapeHTML(initials(job.employer))}
      </div>

      <!-- Información principal -->
      <div class="min-w-0 flex-1">

        <!-- Título y estado -->
        <div class="flex flex-wrap items-center gap-2">
          <h3 class="min-w-0 text-md font-semibold leading-5 text-brandBlack">
            <a href="?id=${id}" role="button" tabindex="0" data-open="${id}" class="rounded-sm no-underline hover:text-arcticBlue hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-crystalBlue">
              ${escapeHTML(job.title)}
            </a>
          </h3>

          ${statusTag(job)}
        </div>

        <!-- Empresa y sector -->
        <p class="mt-1 text-xs text-brandMuted">
          <span class="font-medium text-brandDark">
            ${escapeHTML(job.employer)}
          </span>
          <span aria-hidden="true"> · </span>
          ${escapeHTML(job.sector)}
        </p>

        <!-- Etiquetas -->
        <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
          ${modeTag(job)}
          ${regimeTag(job)}

          <span class="inline-flex items-center rounded-md bg-surfaceRaised px-2 py-1 text-[10px] font-medium text-brandDark">
            ${escapeHTML(familyLabel)}
          </span>

          <span class="inline-flex items-center rounded-md px-2 py-1 text-[10px] font-medium ${job.level === 'Senior'
      ? 'bg-iceBlue/15 text-arcticBlue'
      : 'bg-surfaceRaised text-brandDark'
    }">
            ${escapeHTML(typeLabel)}
          </span>
        </div>

        <!-- Ubicación -->
        <p class="mt-2 flex items-center gap-1.5 text-[11px] text-brandMuted">
          <svg aria-hidden="true" class="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <span class="min-w-0">${escapeHTML(formatLocationEligibility(job))}</span>
        </p>
      </div>
    </div>

    <!-- CENTRO: Compatibilidad -->
    <div class="flex flex-col gap-1 border-t border-borderMuted pt-3 lg:border-l lg:border-t-0 lg:pl-4 lg:pt-0">
      <strong class="text-xs font-semibold text-brandDark">
        ${fitStatus}
      </strong>

      <span class="text-[11px] leading-4 text-brandMuted">
        ${escapeHTML(job.growth || '')}
      </span>
    </div>

    <!-- DERECHA: Información y acciones -->
    <div class="flex flex-wrap items-center justify-between gap-3 border-t border-borderMuted pt-3 sm:flex-nowrap lg:flex-col lg:items-end lg:border-l lg:border-t-0 lg:pl-4 lg:pt-0">

      <!-- Sueldo y fecha -->
      <div class="flex flex-col gap-1 lg:items-end">
        <strong class="text-sm font-semibold ${salary === 'No publicado'
      ? 'text-brandMuted'
      : 'text-brandBlack'
    }">
          ${salary}
        </strong>

        <span class="text-[10px] text-brandMuted">
          ${metaDate}
        </span>
      </div>

      <!-- Acciones -->
      <div class="flex w-full flex-col gap-2">

        <button
          class="card-button inline-flex h-9 w-full items-center justify-center gap-1.5 rounded-lg bg-arcticBlue px-3 text-xs font-semibold text-white transition-colors hover:bg-crystalBlue active:bg-arcticBlue focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-crystalBlue"
          type="button"
          data-open="${id}"
        >
          Ver detalle
          <span aria-hidden="true">↗</span>
        </button>

        <button
          class="compare-button inline-flex h-9 w-full items-center justify-center rounded-lg border border-borderMuted bg-white px-2.5 text-[11px] font-medium text-brandDark transition-colors hover:border-crystalBlue hover:bg-iceBlue/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-crystalBlue ${isCompared
      ? 'selected border-crystalBlue bg-iceBlue/10 text-arcticBlue'
      : ''
    }"
          type="button"
          data-compare="${id}"
          aria-pressed="${isCompared}"
        >
          ${isCompared ? 'Quitar de comparación' : 'Añadir a comparación'}
        </button>

      </div>
    </div>
  </article>`;
}

function formatDateTime(value, { includeTime = false, shortMonth = false } = {}) {
  if (!value) return 'No disponible';
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-');
    return `${day}/${month}/${year}`;
  }
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return String(value);
  const dateOptions = {
    timeZone: 'America/Lima',
    year: 'numeric',
    month: shortMonth ? 'short' : '2-digit',
    day: '2-digit',
  };
  if (includeTime) {
    const formatted = date.toLocaleString('es-PE', {
      ...dateOptions,
      hour: '2-digit',
      minute: '2-digit',
    });
    return `${formatted} (hora Lima)`;
  }
  return date.toLocaleDateString('es-PE', dateOptions);
}

function knownValue(value) {
  return value !== undefined && value !== null && value !== ''
    && !/no publicado|no especificad|no informad|no aplica/i.test(String(value));
}

function hasContradiction(job) {
  const text = [job.mode, job.location, job.eligibility, job.risk].filter(Boolean).join(' ');
  return /contradicci[oó]n|inconsisten/i.test(text)
    || (/remoto/i.test(job.mode || '') && /presencial(?: únicamente| solo)?/i.test(text))
    || (/presencial/i.test(job.mode || '') && /remoto/i.test(job.eligibility || ''));
}

function evaluationSignals(job) {
  const state = currentStates(job);
  const temporary = /suplencia|reemplaz|temporal|plazo fijo|hasta el|por \d+ meses|renovaci[oó]n condicionada|convocatoria cerrada|vencid|por necesidad/i;
  const contradiction = hasContradiction(job);
  const signals = [
    {
      label: 'Compensación',
      status: knownValue(job.salary) ? 'Dato publicado' : 'Información insuficiente',
      tone: knownValue(job.salary) ? 'observed' : 'unknown',
      fact: knownValue(job.salary) ? job.salary : 'La ficha no publica salario o subvención.',
      meaning: knownValue(job.salary) ? 'Permite comparar una condición explícita.' : 'No se puede tratar la ausencia como cero.',
      limit: 'No permite juzgar si la compensación es suficiente.',
    },
    {
      label: 'Beneficios',
      status: knownValue(job.benefits) ? 'Dato publicado' : 'Información insuficiente',
      tone: knownValue(job.benefits) ? 'observed' : 'unknown',
      fact: knownValue(job.benefits) ? job.benefits : 'No hay beneficios descritos en esta ficha.',
      meaning: knownValue(job.benefits) ? 'Hace visibles condiciones declaradas.' : 'La ausencia requiere confirmación en la fuente.',
      limit: 'No prueba que el beneficio aplique a todas las personas.',
    },
    {
      label: 'Continuidad',
      status: temporary.test([job.title, job.duration, job.deadline, job.continuity, job.risk].join(' '))
        ? 'Condición que requiere atención'
        : knownValue(job.duration) || knownValue(job.continuity) ? 'Dato publicado' : 'Información insuficiente',
      tone: temporary.test([job.title, job.duration, job.deadline, job.continuity, job.risk].join(' '))
        ? 'attention' : knownValue(job.duration) || knownValue(job.continuity) ? 'observed' : 'unknown',
      fact: knownValue(job.duration) || knownValue(job.continuity) ? [job.duration, job.continuity].filter(knownValue).join(' · ') : 'La duración o renovación no está informada.',
      meaning: 'La temporalidad visible no equivale a estabilidad ni renovación.',
      limit: 'No predice contratación futura.',
    },
    {
      label: 'Valor técnico',
      status: knownValue(job.tasks) || knownValue(job.skills) ? 'Dato publicado' : 'Información insuficiente',
      tone: knownValue(job.tasks) || knownValue(job.skills) ? 'observed' : 'unknown',
      fact: [job.tasks, job.skills].filter(knownValue).join(' · ') || 'No se describen funciones o herramientas.',
      meaning: knownValue(job.tasks) || knownValue(job.skills) ? 'Describe exposición técnica potencial según la ficha.' : 'No permite interpretar el aprendizaje.',
      limit: 'Las tecnologías mencionadas no prueban práctica real ni mentoría.',
    },
    {
      label: 'Desarrollo profesional',
      status: knownValue(job.growth) || knownValue(job.training) ? 'Interpretación editorial' : 'Información insuficiente',
      tone: knownValue(job.growth) || knownValue(job.training) ? 'interpretation' : 'unknown',
      fact: [job.growth, job.training].filter(knownValue).join(' · ') || 'No hay información suficiente sobre formación o desarrollo.',
      meaning: knownValue(job.growth) || knownValue(job.training) ? 'Puede orientar una siguiente pregunta del usuario.' : 'No se debe inferir una ruta profesional.',
      limit: 'No garantiza ascenso, mentoría ni movilidad.',
    },
    {
      label: 'Modalidad y elegibilidad',
      status: contradiction ? 'Contradicción documentada' : knownValue(job.mode) && knownValue(job.eligibility) ? 'Dato publicado' : 'Información insuficiente',
      tone: contradiction ? 'risk' : knownValue(job.mode) && knownValue(job.eligibility) ? 'observed' : 'unknown',
      fact: [job.mode, job.location, job.eligibility].filter(knownValue).join(' · ') || 'No se informa modalidad o elegibilidad.',
      meaning: 'La elegibilidad territorial debe estar explícita.',
      limit: contradiction ? 'La contradicción impide una lectura favorable automática; debe resolverse en la fuente.' : /remoto/i.test(job.mode || '') && (!/per[uú]/i.test(job.eligibility || '') || /confirmar|verificar/i.test(job.eligibility || '')) ? 'Remoto no demuestra contratación desde Perú.' : 'La ficha puede requerir confirmación posterior.',
    },
    {
      label: 'Calidad de la convocatoria',
      status: state.verificationStatus === 'stale' ? 'Evidencia atrasada'
        : state.opportunityStatus === 'expired' || state.publicationStatus === 'historical' ? 'Condición que requiere atención'
          : state.recordKind === 'demonstration' ? 'Ficha demostrativa' : 'Información disponible',
      tone: state.verificationStatus === 'stale' || state.opportunityStatus === 'expired' || state.publicationStatus === 'historical' ? 'attention' : 'observed',
      fact: `Estado: ${state.opportunityStatus}; verificación: ${state.verificationStatus}; publicación: ${state.publicationStatus}.`,
      meaning: 'La fecha de generación no renueva la evidencia.',
      limit: state.recordKind === 'demonstration' ? 'No es una oportunidad real ni habilita postulación.' : 'La disponibilidad puede cambiar después de la observación.',
    },
  ];
  if (knownValue(job.risk)) {
    signals.push({
      label: 'Riesgos y restricciones',
      status: 'Limitación documentada',
      tone: 'risk',
      fact: job.risk,
      meaning: 'La restricción debe considerarse antes de postular.',
      limit: 'No se agregan riesgos que la fuente no documenta.',
    });
  }
  return signals;
}

function renderSignals(job) {
  return evaluationSignals(job).map((signal) => `<article class="signal-card ${escapeHTML(signal.tone)}">
    <div class="signal-heading"><h4>${escapeHTML(signal.label)}</h4><span class="signal-status">${escapeHTML(signal.status)}</span></div>
    <p><b>Qué se observó:</b> ${escapeHTML(signal.fact)}</p>
    <p><b>Qué puede significar:</b> ${escapeHTML(signal.meaning)}</p>
    <p class="signal-limit"><b>Límite:</b> ${escapeHTML(signal.limit)}</p>
  </article>`).join('');
}

function renderEmployerAssessment(job) {
  const publisher = job.publisher || 'No registrado';
  const source = safeHttpsUrl(job.sourceUrl);
  return `<section class="detail-section employer-assessment">
    <h3>Evaluación del empleador</h3>
    <p><b>Información institucional registrada:</b> ${escapeHTML(job.employer || 'No informada')} · sector ${escapeHTML(job.sector || 'no informado')} · difusor ${escapeHTML(publisher)}.</p>
    <p class="signal-limit"><b>Lo que no se puede concluir:</b> esta ficha no contiene evidencia suficiente para evaluar cultura, reputación, condiciones laborales generales o movilidad interna.</p>
    ${source ? `<p class="external-note">La identidad se atribuye a la <a href="${escapeHTML(source)}" target="_blank" rel="noopener noreferrer">fuente registrada ↗</a>.</p>` : ''}
  </section>`;
}

function lucideIcon(name, className = 'w-5 h-5') {
  const icons = {
    'badge-check': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}" aria-hidden="true"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m16 9-5.5 5.5L8 12"/></svg>`,
    building: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>',
    briefcase: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    'triangle-alert': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`,
    monitor: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>',
    pin: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>',
    wallet: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>',
    file: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    clock: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M21 7.5V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3.5"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/><circle cx="16" cy="16" r="6"/><polyline points="16 14 16 16 18 17"/></svg>',
    calendar: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M8 2v4"/><path d="M16 2v4"/><path d="M21 13V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8"/><path d="M3 10h18"/><path d="M16 19h6"/><path d="M19 16v6"/></svg>',
    shield: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    check: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
    code: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
  };
  return icons[name] || '';
}

function cleanContractDuration(job) {
  const contract = (job.contractType || '').trim();
  const duration = (job.duration || '').trim();
  const cleanParts = [];
  const ign = /^(?:no especificad[oa]|no informad[oa]|no aplica|duraci[oó]n no especificada)[\s.]*$/i;

  if (contract && !ign.test(contract)) {
    cleanParts.push(contract);
  }
  if (duration) {
    if (/full-time|tiempo completo/i.test(duration)) {
      cleanParts.push('Full-time');
    } else if (!ign.test(duration)) {
      const d = duration.replace(/;?\s*duraci[oó]n no especificada/i, '').trim();
      if (d) cleanParts.push(d);
    }
  }
  return cleanParts.length > 0 ? cleanParts.join(' · ') : null;
}

function formatBulletItem(item) {
  const clean = item.replace(/\.$/, '').trim();
  if (!clean) return '';
  if (/^[a-z][a-z0-9]/.test(clean) && !/^[a-z][A-Z]/.test(clean)) {
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }
  return clean;
}

function formatStructuredList(text, fallbackText = '') {
  if (!text || typeof text !== 'string' || !text.trim()) {
    return fallbackText ? `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(fallbackText)}</p>` : '';
  }
  const trimmed = text.trim();
  if (!trimmed.includes(';')) {
    return `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(trimmed)}</p>`;
  }
  const items = trimmed
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean);

  if (items.length <= 1) {
    return `<p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(trimmed)}</p>`;
  }

  return `<ul class="list-disc pl-5 space-y-1.5 text-sm text-stone-700 leading-relaxed">${items
    .map((item) => `<li>${escapeHTML(formatBulletItem(item))}</li>`)
    .join('')}</ul>`;
}

function renderDetailContent(job, { isStandalone = false } = {}) {
  const state = currentStates(job);
  const sourceUrl = safeHttpsUrl(job.sourceUrl);
  const applyUrl = safeHttpsUrl(job.applyUrl);
  const canApply = state.publicationStatus === 'active' && job.recordKind !== 'demonstration' && state.opportunityStatus !== 'expired';
  const isStale = state.verificationStatus === 'stale';
  const statusText = job.recordKind === 'demonstration'
    ? `Ficha de demostración. No tiene evidencia vigente suficiente para presentarla como postulable. Última verificación: ${formatDateTime(job.lastVerifiedAt)}; última consulta registrada: ${formatDateTime(job.lastCheckedDate)}. No se afirma que siga publicada.`
    : canApply
      ? `La fuente del empleador se revisó el ${formatDateTime(job.lastVerifiedAt)}; esta comprobación no garantiza disponibilidad posterior.`
      : state.opportunityStatus === 'expired'
        ? 'La fecha límite de postulación ya pasó. Se conserva como referencia y no se habilita el enlace para postular.'
        : state.publicationStatus === 'historical'
          ? 'Registro histórico conservado para referencia. No está disponible para postular.'
          : isStale
            ? `Convocatoria registrada con verificación previa (${formatDateTime(job.lastVerifiedAt || job.lastCheckedDate)}) que superó el período de frescura de ${catalogConfig.verificationTtlDays || 7} días. Pendiente de revalidar vigencia con la fuente oficial antes de habilitar postulación.`
            : `No tiene evidencia vigente suficiente para presentarla como postulable. Última verificación: ${formatDateTime(job.lastVerifiedAt)}; última consulta registrada: ${formatDateTime(job.lastCheckedDate)}. No se afirma que siga publicada.`;
  const fieldEvidence = Array.isArray(job.fieldEvidence) ? job.fieldEvidence : [];
  const evidenceLabels = { employer: 'Empleador', publisher: 'Difusor', title: 'Puesto', applyUrl: 'Canal de postulación', deadline: 'Fecha límite', salary: 'Remuneración', mode: 'Modalidad', location: 'Ubicación', requirements: 'Requisitos', benefits: 'Beneficios', skills: 'Tecnologías', training: 'Formación', contractType: 'Tipo de contrato', duration: 'Duración', sector: 'Sector', family: 'Familia profesional', level: 'Nivel', kind: 'Tipo de oportunidad', growth: 'Experiencia para el siguiente paso', continuity: 'Continuidad', risk: 'Riesgos' };
  const fieldEvidenceHtml = fieldEvidence.filter((item) => evidenceLabels[item.field] && safeHttpsUrl(item.url)).map((item) => `<li><a href="${escapeHTML(safeHttpsUrl(item.url))}" target="_blank" rel="noopener noreferrer">${escapeHTML(evidenceLabels[item.field])} · evidencia ↗</a> <span>${escapeHTML(formatDateTime(item.observedAt))}</span></li>`).join('');
  const sourcePublisher = job.publisher || job.employer || 'Fuente oficial';
  const evidenceLink = job.evidenceUrl ? `<a class="detail-evidence-link" href="${escapeHTML(safeHttpsUrl(job.evidenceUrl) || '#')}" target="_blank" rel="noopener noreferrer">Abrir bases/documento de evidencia ↗</a>` : '';
  const isVerified = state.verificationStatus === 'verified';
  const verifiedDateFormatted = formatDateTime(job.lastVerifiedAt || job.lastCheckedDate);

  const backNav = isStandalone ? `
    <div class="opportunity-back-nav mb-6">
      <button type="button" class="back-to-catalog flex items-center gap-1.5 text-sm font-semibold text-stone-700 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-3.5 py-2 rounded-lg transition-colors cursor-pointer" data-action="back-to-catalog">
        <span aria-hidden="true">←</span> Volver al catálogo
      </button>
    </div>
  ` : '';

  const bottomBackNav = isStandalone ? `
    <div class="opportunity-bottom-nav mt-8 pt-6 border-t border-stone-200 flex justify-between items-center">
      <button type="button" class="back-to-catalog flex items-center gap-1.5 text-sm font-semibold text-stone-700 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-4 py-2.5 rounded-lg transition-colors cursor-pointer" data-action="back-to-catalog">
        <span aria-hidden="true">←</span> Volver al catálogo
      </button>
      <a href="#inicio" class="text-xs text-stone-500 hover:text-stone-800">Ir arriba ↑</a>
    </div>
  ` : '';

  // Resumen: tarjetas visuales con iconos Lucide y omisión estricta de datos no verificados
  const summaryCards = [];

  if (knownValue(job.mode) && !/no especificad|no informad/i.test(job.mode)) {
    summaryCards.push({
      icon: 'monitor',
      label: 'Modalidad',
      value: escapeHTML(job.mode),
    });
  }

  summaryCards.push({
    icon: 'building',
    label: 'Entidad que difunde',
    value: escapeHTML(sourcePublisher),
  });

  const locElig = formatLocationEligibility(job);
  if (locElig && !/no confirmad|no especificad/i.test(locElig)) {
    summaryCards.push({
      icon: 'pin',
      label: 'Ubicación y elegibilidad',
      value: escapeHTML(locElig),
    });
  }

  if (knownValue(job.salary) && !/no publicado|no especificad|no informad/i.test(job.salary)) {
    summaryCards.push({
      icon: 'wallet',
      label: 'Compensación',
      value: escapeHTML(job.salary) + (job.salaryNote && !/no informad/i.test(job.salaryNote) ? ` · ${escapeHTML(job.salaryNote)}` : ''),
    });
  }

  const contractDuration = cleanContractDuration(job);
  if (contractDuration) {
    summaryCards.push({
      icon: 'file',
      label: 'Contrato y plazo',
      value: escapeHTML(contractDuration),
    });
  }

  const regimeKey = getJobLaborRegime(job);
  const regimeDef = REGIME_DEFINITIONS[regimeKey] || REGIME_DEFINITIONS.UNSPECIFIED;
  summaryCards.push({
    icon: 'briefcase',
    label: 'Régimen y modalidad',
    value: escapeHTML(regimeDef.label) + (job.laborRegimeCertainty === 'EXPLICIT_EVIDENCE' ? ' (Explícito)' : ''),
  });

  if (job.deadline && isCivilDate(job.deadline)) {
    summaryCards.push({
      icon: 'clock',
      label: 'Fecha límite',
      value: escapeHTML(formatDateTime(job.deadline)),
    });
  }

  if (job.publishedAt && isCivilDate(job.publishedAt)) {
    summaryCards.push({
      icon: 'calendar',
      label: 'Fecha de publicación',
      value: escapeHTML(formatDateTime(job.publishedAt)),
    });
  }

  summaryCards.push({
    icon: 'shield',
    label: 'Última verificación o consulta',
    value: escapeHTML(verifiedDateFormatted) + (isStale ? ' · Requiere revalidar' : ''),
  });

  const summaryCardsHtml = summaryCards.map((card) => `
    <div class="summary-card detail-item flex items-start gap-3.5 p-4 ">
      <div class="summary-icon shrink-0 p-2.5 rounded-lg bg-slate-100 text-crystal-blue" aria-hidden="true">
        ${lucideIcon(card.icon, 'w-5 h-5')}
      </div>
      <div class="min-w-0 flex-1">
        <label class="block text-[11px] font-semibold uppercase tracking-wider"> <spam class="text-arctic-blue">${card.label}</spam></label>
        <p class="text-sm font-semibold text-stone-900 mt-1 break-words">${card.value}</p>
      </div>
    </div>
  `).join('');

  // Tecnologías y herramientas como etiquetas visuales
  const skillsList = knownValue(job.skills)
    ? job.skills.split(/\s*·\s*|,\s*/).map((s) => s.trim()).filter(Boolean)
    : [];

  const skillsHtml = skillsList.length > 0 ? `
    <section class="skills-section mb-8 px-5 pb-5" aria-label="Tecnologías y herramientas declaradas">
      <h4 class="text-xs font-semibold text-stone-500 uppercase tracking-wider mb-2">Tecnologías y herramientas declaradas</h4>
      <div class="flex flex-wrap gap-2">
        ${skillsList.map((skill) => `
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-ice-blue/10 text-arcticBlue border border-ice-blue/30">
            ${escapeHTML(skill)}
          </span>
        `).join('')}
      </div>
    </section>
  ` : '';

  return `
    ${backNav}
    <div class="opportunity-header mb-6">
      <p class="dialog-eyebrow text-xs font-mono font-medium text-stone-500 uppercase tracking-wider mb-1">${escapeHTML(job.requisition || job.id)} · ${escapeHTML(job.sourceKind || 'Fuente de empleo')}</p>
      <h2 class="dialog-title text-2xl md:text-3xl font-bold tracking-tight text-stone-900 py-2" id="${isStandalone ? 'opportunity-page-title' : 'dialog-title'}">${escapeHTML(job.title)}</h2>
      <div class="dialog-tags flex flex-wrap gap-2 mb-6">${statusTag(job)}<span class="tag inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-stone-100 text-stone-800 border border-stone-200">${escapeHTML(job.family || 'Tecnología y Sistemas')}</span><span class="tag inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-stone-100 text-stone-800 border border-stone-200">${escapeHTML(job.level || job.kind || 'Oportunidad')}</span></div>
    </div>

    <!-- 1. ✓ Fuente oficial verificada (sección destacada en posición superior) -->
    <section class="official-source-hero mb-5 rounded-xl border border-borderMuted bg-brandBlack p-4">

      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        <!-- Información -->
        <div class="min-w-0 flex-1 text-white">

          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 text-xs font-semibold
              ${isVerified ? 'text-crystal-blue' : (isStale ? 'text-amber-300' : 'text-crystal-blue')}">
              ${isVerified
      ? lucideIcon('badge-check', 'h-3.5 w-3.5')
      : lucideIcon('triangle-alert', 'h-3.5 w-3.5')}
              ${isVerified ? 'Fuente oficial verificada' : (isStale ? 'Verificación pendiente de revalidar' : 'Fuente de consulta')}
            </span>
          </div>

          <h3 class="mt-1.5 break-words text-lg font-semibold text-white">
            ${escapeHTML(sourcePublisher)}
          </h3>

          ${job.employer && job.employer !== sourcePublisher ? `
            <p class="mt-0.5 text-xs text-white">
              Empleador:
              <strong class="font-semibold">${escapeHTML(job.employer)}</strong>
            </p>
          ` : ''}

          <p class="mt-1 text-xs leading-relaxed text-white">
            ${isVerified
      ? 'Publicación oficial verificada directamente en el portal del empleador o difusor'
      : (isStale
        ? 'Convocatoria con verificación previa que superó el período de frescura (requiere comprobar fuente)'
        : 'Convocatoria registrada pendiente de comprobación directa')}
            · Consulta:
            <strong class="font-medium text-white">
              ${escapeHTML(verifiedDateFormatted)}
            </strong>
          </p>

        </div>

        <!-- Acciones alineadas a la derecha -->
        <div class="flex w-full shrink-0 flex-col items-stretch gap-2 sm:w-48 sm:items-stretch">

          ${sourceUrl ? `
            <a
              href="${escapeHTML(sourceUrl)}"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-source inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg
                    border border-borderMuted bg-white px-3 py-2
                    text-xs font-semibold text-brandDark
                    transition-colors duration-150
                    hover:border-iceBlue hover:bg-surfaceRaised hover:text-arcticBlue
                    focus-visible:outline-2 focus-visible:outline-offset-2
                    focus-visible:outline-arcticBlue"
            >
              Ver publicación original
              <span aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-up-right preview-icon"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg></span>
            </a>
          ` : ''}

          ${canApply && applyUrl ? `
            <a
              href="${escapeHTML(applyUrl)}"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-apply-main inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg mt-2
                    bg-arcticBlue hover:bg-[#125091] px-3 py-2 text-xs font-semibold mb-2
                    transition-colors duration-150
                    focus-visible:outline-2 focus-visible:outline-offset-2
                    focus-visible:outline-arcticBlue"
            >
              <span class="text-white">Ir a postulación</span>
              <span class="text-white" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-up-right preview-icon"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg></span>
            </a>
          ` : `
            <span
              class="inline-flex min-h-9 items-center justify-center rounded-lg
                    bg-surfaceRaised px-3 py-2 text-xs text-white"
              aria-disabled="true"
            >
              Postulación deshabilitada
            </span>
          `}

        </div>

      </div>

      <!-- Fuente / Ficha informativa -->
      ${sourceUrl ? `
        <div class="mt-3 border-t border-borderMuted pb-2 pt-4">
          <p class="break-words text-[11px] text-slate-100">
            Ficha informativa:
            <a
              href="${escapeHTML(sourceUrl)}"
              target="_blank"
              rel="noopener noreferrer"
              class="font-medium text-arcticBlue
                    focus-visible:outline-2 focus-visible:outline-offset-2
                    focus-visible:outline-arcticBlue"
            >
              <span class="text-slate-100">${escapeHTML(job.sourceKind || sourcePublisher)} ⌝ </span>
            </a>
          </p>
        </div>
      ` : ''}

    </section>



    <!-- 2. Resumen (cuadrícula visual con iconos Lucide y omisión de datos no verificados) -->
    <section class="summary-section bg-white rounded-xl shadow-xs hover:border-stone-300 transition-colors" aria-label="Resumen de condiciones de la oportunidad">
      <h3 class="text-xs font-bold uppercase tracking-wider text-stone-500 px-5 pt-4">Resumen</h3>
      <div class="summary-grid detail-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-3.5">
        ${summaryCardsHtml}
      </div>
      <div>
        <!-- 3. Tecnologías y herramientas declaradas (inmediatamente debajo del Resumen) -->
        ${skillsHtml}
      </div>
    </section>

    <!-- 4. Tareas y Requisitos del puesto -->
    <section class="bg-white hover:border-stone-300 rounded-xl p-4 shadow-xs">
      <div class="mb-6 mt-6">
        <h3 class="text-[14px] font-bold uppercase tracking-wider text-stone-700 mb-2">Qué harías</h3>
        ${formatStructuredList(job.tasks, 'La descripción completa se consulta en la fuente original.')}
      </div>

      <div class="detail-section mb-6">
        <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2">Requisitos del puesto</h3>
        ${formatStructuredList(job.requirements, 'Revisar requisitos en la publicación original.')}
      </div>

      ${knownValue(job.growth) ? `
        <div class="detail-section mb-6">
          <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2">Qué experiencia podrías llevar al siguiente paso</h3>
          <p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(job.growth)}</p>
        </div>
      ` : ''}

      ${knownValue(job.benefits) ? `
        <div class="detail-section mb-6">
          <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2">Beneficios publicados</h3>
          ${formatStructuredList(job.benefits)}
        </div>
      ` : ''}
    </section>

    <!-- 5. Marco Normativo y Régimen Laboral -->
    <section class="labor-regime-section bg-white hover:border-stone-300 rounded-xl p-4 shadow-xs mt-6" aria-label="Régimen contractual y marco normativo">
      <div class="flex flex-wrap items-center gap-2 mb-3">
        <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border ${regimeDef.badgeClass}">
          ${escapeHTML(regimeDef.label)}
        </span>
        <span class="text-xs text-stone-500 font-medium">· ${escapeHTML(regimeDef.legalFramework)}</span>
      </div>

      <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 mb-3">Régimen Contractual y Marco Normativo</h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-stone-700">
        <div class="rounded-lg bg-stone-50 p-3 border border-stone-200">
          <p class="font-semibold text-stone-900 mb-1">Naturaleza jurídica:</p>
          <p class="leading-relaxed text-stone-600">${escapeHTML(regimeDef.nature)}</p>
        </div>
        <div class="rounded-lg bg-stone-50 p-3 border border-stone-200">
          <p class="font-semibold text-stone-900 mb-1">Jornada y tiempo de trabajo:</p>
          <p class="leading-relaxed text-stone-600">${escapeHTML(regimeDef.maxWorkingHours)}</p>
        </div>
        <div class="rounded-lg bg-stone-50 p-3 border border-stone-200">
          <p class="font-semibold text-stone-900 mb-1">Subvención / Remuneración:</p>
          <p class="leading-relaxed text-stone-600">${escapeHTML(regimeDef.compensation)}</p>
        </div>
        <div class="rounded-lg bg-stone-50 p-3 border border-stone-200">
          <p class="font-semibold text-stone-900 mb-1">Garantías y derechos principales:</p>
          <p class="leading-relaxed text-stone-600">${escapeHTML(regimeDef.keyRights)}</p>
        </div>
      </div>

      <div class="mt-3 rounded-lg bg-amber-50/80 p-3 border border-amber-200 text-xs text-amber-900">
        <p class="font-semibold mb-0.5">Cautelas y consideraciones:</p>
        <p class="leading-relaxed">${escapeHTML(regimeDef.cautions)}</p>
      </div>

      <p class="mt-3 text-[11px] text-stone-500 italic">
        Nota orientativa: Información resumida para orientación profesional y formativa con base en la normativa peruana aplicable. No constituye asesoría legal individual ni sustituye las bases específicas de la convocatoria.
      </p>
    </section>

    <!-- Verificación y procedencia -->
    <section class="verification-section bg-white hover:border-stone-300 rounded-xl p-4 shadow-xs mt-6">

      <!-- Estado de verificación -->
      <div class="evidence-box flex items-start gap-2.5">
        <svg
          aria-hidden="true"
          class="mt-0.5 h-4 w-4 shrink-0 ${canApply ? 'text-arcticBlue' : 'text-amber-600'}"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          ${canApply
      ? '<path d="m5 12 4 4L19 6"/>'
      : '<circle cx="12" cy="12" r="9"/><path d="M12 8v4m0 4h.01"/>'}
        </svg>

        <div class="min-w-0">
          <p class="text-xs font-semibold text-brandBlack">
            ${canApply ? 'Qué se verificó' : 'Estado de publicación'}
          </p>

          <p class="mt-1 text-xs leading-relaxed text-brandMuted">
            ${escapeHTML(statusText)}
          </p>
        </div>
      </div>

      <!-- Procedencia -->
      <details class="evidence-collapsible group mt-3 border-t border-borderMuted pt-3">
        <summary class="flex cursor-pointer list-none items-center justify-between gap-3 text-xs text-brandDark hover:text-arcticBlue focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-crystalBlue">
          <span>
            Procedencia por dato
            <span class="ml-1 text-brandMuted">
              (${fieldEvidence.length} campos registrados)
            </span>
          </span>

          <svg
            aria-hidden="true"
            class="h-4 w-4 shrink-0 text-brandMuted transition-transform duration-150 group-open:rotate-180"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </summary>

        <div class="mt-3">
          ${fieldEvidenceHtml
      ? `<ul class="divide-y divide-borderMuted text-xs">${fieldEvidenceHtml}</ul>`
      : '<p class="text-xs text-brandMuted">No hay evidencia desglosada por campo en esta ficha.</p>'}

          ${evidenceLink
      ? `<div class="mt-3 text-xs text-brandMuted">${evidenceLink}</div>`
      : ''}
        </div>
      </details>

    </section>

    <!-- Nota informativa -->
    <p class="mt-6 text-center text-[11px] text-brandMuted">
      No guardamos tu CV ni enviamos postulaciones desde este prototipo.
    </p>


    ${bottomBackNav}
  `;
}

function renderOpportunityPage(job, updateHistory = true) {
  if (typeof opportunityView === 'undefined' || typeof catalogView === 'undefined' || !opportunityView || !catalogView) return;
  opportunityView.innerHTML = renderDetailContent(job, { isStandalone: true });
  catalogView.classList.add('hidden');
  catalogView.hidden = true;
  opportunityView.classList.remove('hidden');
  opportunityView.hidden = false;
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'instant' });
    document.title = `${job.title} · ${job.employer} — Velora`;
    if (updateHistory && window.history && window.history.pushState) {
      const currentParam = new URLSearchParams(window.location.search).get('id');
      if (currentParam !== job.id) {
        const url = new URL(window.location.href);
        url.searchParams.set('id', job.id);
        window.history.pushState({ id: job.id, standalone: true }, '', url.toString());
      }
    }
  }
}

function renderNotFoundPage(requestedId) {
  if (typeof opportunityView === 'undefined' || typeof catalogView === 'undefined' || !opportunityView || !catalogView) return;
  opportunityView.innerHTML = `
    <div class="opportunity-not-found p-8 text-center max-w-xl mx-auto my-12 bg-white rounded-xl border border-stone-200 shadow-sm">
      <p class="dialog-eyebrow text-xs uppercase font-semibold text-stone-500 mb-2">ERROR 404 · REGISTRO NO ENCONTRADO</p>
      <h2 class="text-xl font-bold text-stone-900 mb-2">Oportunidad no encontrada</h2>
      <p class="text-sm text-stone-600 mb-6">El identificador <code>${escapeHTML(requestedId || '')}</code> no corresponde a ninguna oportunidad disponible en este catálogo.</p>
      <button type="button" class="back-to-catalog inline-flex items-center gap-1.5 text-sm font-semibold text-stone-700 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-4 py-2.5 rounded-lg transition-colors cursor-pointer" data-action="back-to-catalog">
        <span aria-hidden="true">←</span> Volver al catálogo
      </button>
    </div>
  `;
  catalogView.classList.add('hidden');
  catalogView.hidden = true;
  opportunityView.classList.remove('hidden');
  opportunityView.hidden = false;
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'instant' });
    document.title = 'Oportunidad no encontrada — Velora';
  }
}

function closeOpportunityPage(updateHistory = true) {
  if (typeof opportunityView === 'undefined' || typeof catalogView === 'undefined' || !opportunityView || !catalogView) return;
  opportunityView.classList.add('hidden');
  opportunityView.hidden = true;
  opportunityView.innerHTML = '';
  catalogView.classList.remove('hidden');
  catalogView.hidden = false;
  if (typeof document !== 'undefined') {
    document.title = 'Velora — Oportunidades y Trayectorias en Tecnología';
  }
  if (updateHistory && typeof window !== 'undefined' && window.history && window.history.pushState) {
    const params = new URLSearchParams(window.location.search);
    params.delete('id');
    const newSearch = params.toString() ? `?${params.toString()}` : '';
    const newUrl = `${window.location.pathname}${newSearch}${window.location.hash}`;
    window.history.pushState({}, '', newUrl);
  }
}

function getOpportunityIdFromUrl() {
  if (typeof window === 'undefined' || !window.location) return null;
  const params = new URLSearchParams(window.location.search);
  const idParam = params.get('id');
  if (idParam) return idParam;
  const hash = window.location.hash || '';
  const match = hash.match(/^#\/?oportunidad\/([A-Za-z0-9_-]+)$/);
  return match ? match[1] : null;
}

function handleRouting() {
  if (typeof window === 'undefined' || !window.location) return;
  if (typeof opportunityView === 'undefined' || typeof catalogView === 'undefined' || !opportunityView || !catalogView) return;
  const requestedId = getOpportunityIdFromUrl();
  if (!requestedId) {
    if (!opportunityView.hidden) {
      closeOpportunityPage(false);
    }
    if (typeof dialog !== 'undefined' && dialog && dialog.open) {
      dialog.close();
    }
    return;
  }
  const job = catalog.find((item) => item.id === requestedId);
  if (job) {
    renderOpportunityPage(job, false);
  } else if (catalog.length > 0) {
    renderNotFoundPage(requestedId);
  }
}

function updateComparePanel() {
  const selected = compareIds.map((id) => catalog.find((job) => job.id === id)).filter(Boolean);
  compareIds = selected.map((job) => job.id);
  comparePanel.hidden = selected.length === 0;
  compareOpen.disabled = selected.length !== 2;
  compareSummary.textContent = selected.length === 2
    ? `Dos fichas seleccionadas: ${selected.map((job) => job.title).join(' · ')}`
    : `${selected.length} de 2 fichas seleccionadas. La selección solo vive en esta página.`;
}

function toggleCompare(id) {
  if (compareIds.includes(id)) {
    compareIds = compareIds.filter((item) => item !== id);
  } else if (compareIds.length < 2) {
    compareIds = [...compareIds, id];
  } else {
    notify('Compara hasta dos fichas a la vez.');
    return;
  }
  updateComparePanel();
  render();
}

function comparisonValue(job, field) {
  if (field === 'status') {
    const state = currentStates(job);
    const oppStatusMap = { open: 'Abierta', closed: 'Cerrada', expired: 'Expirada' };
    const verStatusMap = { verified: 'Verificada', stale: 'Requiere revalidación', unconfirmed: 'Sin verificar' };
    const pubStatusMap = { active: 'Activa', historical: 'Histórica', unconfirmed: 'Sin verificar' };
    const opp = oppStatusMap[state.opportunityStatus] || state.opportunityStatus;
    const ver = verStatusMap[state.verificationStatus] || state.verificationStatus;
    const pub = pubStatusMap[state.publicationStatus] || state.publicationStatus;
    return `${opp} · ${ver} · ${pub}`;
  }
  if (field === 'salary') return knownValue(job.salary) ? job.salary : 'No publicado';
  return knownValue(job[field]) ? job[field] : 'No informado';
}

function comparisonRawValue(job, field) {
  if (field === 'status') {
    const s = currentStates(job);
    return `${s.opportunityStatus}-${s.verificationStatus}-${s.publicationStatus}-${job.recordKind}`;
  }
  if (field === 'eligibility') {
    return formatLocationEligibility(job);
  }
  if (field === 'regime') {
    return getJobLaborRegime(job);
  }

  if (field === 'salary') {
    return knownValue(job.salary) ? job.salary.trim() : '';
  }
  if (field === 'duration') {
    return cleanContractDuration(job) || '';
  }
  return knownValue(job[field]) ? String(job[field]).trim() : '';
}

function isComparisonRowDifferent(jobA, jobB, field) {
  const valA = normalized(comparisonRawValue(jobA, field));
  const valB = normalized(comparisonRawValue(jobB, field));
  return valA !== valB;
}

function renderComparisonCell(job, field) {
  if (field === 'regime') {
    const regimeKey = getJobLaborRegime(job);
    const defn = REGIME_DEFINITIONS[regimeKey] || REGIME_DEFINITIONS.UNSPECIFIED;
    return `<div>
      <span class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold border ${defn.badgeClass}">${escapeHTML(defn.label)}</span>
      <p class="text-[11px] text-stone-500 mt-1">${escapeHTML(defn.legalFramework)}</p>
    </div>`;
  }

  if (field === 'salary') {
    if (knownValue(job.salary)) {
      return `<div class="font-bold text-stone-900">${escapeHTML(job.salary)}</div>${job.salaryNote ? `<p class="text-[11px] text-stone-500 mt-1 leading-snug">${escapeHTML(job.salaryNote)}</p>` : ''}`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No publicado en convocatoria</span>`;
  }

  if (field === 'requirements') {
    if (knownValue(job.requirements)) {
      return formatStructuredList(job.requirements, 'Revisar en publicación original.');
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>Revisar en publicación oficial</span>`;
  }

  if (field === 'tasks') {
    if (knownValue(job.tasks)) {
      return formatStructuredList(job.tasks, 'Revisar funciones en la publicación original.');
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No especificadas</span>`;
  }

  if (field === 'skills') {
    if (knownValue(job.skills)) {
      const skillList = String(job.skills).split(/[;,·•|]/).map((s) => s.trim()).filter(Boolean);
      if (skillList.length > 1) {
        return `<div class="flex flex-wrap gap-1">${skillList.map((s) => `<span class="inline-block rounded bg-sky-50 border border-sky-200/70 px-2 py-0.5 text-[11px] font-medium text-sky-900">${escapeHTML(s)}</span>`).join('')}</div>`;
      }
      return `<p class="text-xs text-stone-700 leading-relaxed">${escapeHTML(job.skills)}</p>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No declaradas</span>`;
  }

  if (field === 'mode') {
    if (knownValue(job.mode)) {
      const modeColor = job.mode === 'Remoto'
        ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
        : (job.mode === 'Híbrido' ? 'bg-sky-50 text-sky-800 border-sky-200' : 'bg-stone-100 text-stone-800 border-stone-200');
      return `<span class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold border ${modeColor}">${escapeHTML(job.mode)}</span>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No informado</span>`;
  }

  if (field === 'eligibility') {
    return `<p class="text-xs text-stone-700 leading-relaxed">${escapeHTML(formatLocationEligibility(job))}</p>`;
  }

  if (field === 'level') {
    if (knownValue(job.level)) {
      return `<span class="inline-flex items-center rounded-md bg-stone-100 px-2 py-0.5 text-xs font-semibold text-stone-800">${escapeHTML(job.level)}</span>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No informado</span>`;
  }

  if (field === 'duration') {
    const cleaned = cleanContractDuration(job);
    if (cleaned) {
      return `<p class="text-xs text-stone-700">${escapeHTML(cleaned)}</p>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No especificada</span>`;
  }

  if (field === 'family') {
    if (knownValue(job.family)) {
      return `<p class="text-xs font-medium text-stone-700">${escapeHTML(job.family)}</p>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No informada</span>`;
  }

  if (field === 'benefits') {
    if (knownValue(job.benefits)) {
      return formatStructuredList(job.benefits);
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No publicados</span>`;
  }

  if (field === 'risk') {
    if (knownValue(job.risk)) {
      return `<div class="rounded-lg bg-amber-50/80 border border-amber-200/90 p-2.5 text-xs text-amber-900 leading-relaxed">
        <div class="flex items-center gap-1.5 font-semibold text-amber-800 mb-1">
          <svg class="h-3.5 w-3.5 text-amber-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          <span>Condición declarada</span>
        </div>
        ${formatStructuredList(job.risk)}
      </div>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>Sin advertencias señaladas</span>`;
  }

  if (field === 'growth') {
    if (knownValue(job.growth)) {
      return `<p class="text-xs text-stone-700 leading-relaxed">${escapeHTML(job.growth)}</p>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No declarado</span>`;
  }

  if (field === 'continuity') {
    if (knownValue(job.continuity)) {
      return `<p class="text-xs text-stone-700 leading-relaxed">${escapeHTML(job.continuity)}</p>`;
    }
    return `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No informada</span>`;
  }

  if (field === 'status') {
    const state = currentStates(job);
    const isAct = state.publicationStatus === 'active' && job.recordKind !== 'demonstration';
    const isDemo = job.recordKind === 'demonstration';
    const isHist = state.publicationStatus === 'historical' || state.opportunityStatus === 'expired';
    if (isAct) {
      return `<div class="space-y-1">
        <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200/80 px-2 py-0.5 rounded-full">
          ✓ Activa · Verificada
        </span>
        <p class="text-[10px] text-stone-500">Revisión oficial: ${escapeHTML(formatDateTime(job.lastVerifiedAt || job.lastCheckedDate, { shortMonth: true }))}</p>
      </div>`;
    }
    if (state.verificationStatus === 'stale') {
      return `<div class="space-y-1">
        <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200/80 px-2 py-0.5 rounded-full">
          ⏳ Pendiente de revalidación
        </span>
        <p class="text-[10px] text-stone-500">Última revisión: ${escapeHTML(formatDateTime(job.lastVerifiedAt || job.lastCheckedDate, { shortMonth: true }))}</p>
      </div>`;
    }
    if (isDemo) {
      return `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200/80 px-2 py-0.5 rounded-full">
        Ficha de demostración
      </span>`;
    }
    return `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-stone-700 bg-stone-100 border border-stone-200 px-2 py-0.5 rounded-full">
      ${isHist ? 'Cerrada / Histórica' : 'Sin confirmación de vigencia'}
    </span>`;
  }

  return knownValue(job[field])
    ? `<p class="text-xs text-stone-700">${escapeHTML(job[field])}</p>`
    : `<span class="inline-flex items-center gap-1.5 rounded-md bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-600"><span class="h-1.5 w-1.5 rounded-full bg-stone-400" aria-hidden="true"></span>No informado</span>`;
}

function renderComparison() {
  const jobs = compareIds.map((id) => catalog.find((job) => job.id === id)).filter(Boolean);
  if (jobs.length !== 2) return;
  const rows = [
    ['Régimen contractual', 'regime'],
    ['Compensación', 'salary'],
    ['Requisitos del puesto', 'requirements'],
    ['Funciones', 'tasks'],
    ['Tecnologías', 'skills'],
    ['Modalidad', 'mode'],
    ['Elegibilidad / ubicación', 'eligibility'],
    ['Nivel', 'level'],
    ['Tipo y duración', 'duration'],
    ['Familia técnica', 'family'],
    ['Beneficios', 'benefits'],
    ['Condiciones y advertencias', 'risk'],
    ['Desarrollo declarado', 'growth'],
    ['Continuidad', 'continuity'],
    ['Estado de verificación', 'status'],
  ];

  compareContent.innerHTML = `
    <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-stone-200/80 pb-4">
      <div>
        <p class="dialog-eyebrow text-xs uppercase font-semibold text-stone-500 tracking-wider">COMPARACIÓN LOCAL · SIN PUNTUACIÓN</p>
        <h2 id="compare-dialog-title" class="dialog-title text-xl font-bold text-stone-900 tracking-tight mt-0.5">Dos alternativas, sin ganador universal</h2>
        <p class="dialog-intro text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">Observa qué está publicado y qué falta confirmar. La comparación no convierte datos ausentes en condiciones desfavorables ni asigna puntajes automáticos.</p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <label class="inline-flex items-center gap-2 cursor-pointer text-xs font-semibold text-stone-700 select-none bg-stone-100 hover:bg-stone-200/90 px-3 py-2 rounded-lg transition-colors border border-stone-200 shadow-xs">
          <input type="checkbox" id="compare-toggle-diff" class="rounded accent-arcticBlue h-4 w-4" />
          <span>Destacar diferencias</span>
        </label>
      </div>
    </div>

    ${renderSkillsComparison(jobs[0], jobs[1])}

    <div class="comparison-table-wrap overflow-x-auto rounded-xl border border-stone-200 shadow-xs">
      <table class="comparison-table w-full min-w-[680px] border-collapse text-left text-xs">
        <thead>
          <tr>
            <th scope="col" class="w-[170px] p-3.5 bg-stone-100/80 font-bold uppercase tracking-wider text-stone-700 text-[11px] border-b border-stone-200">
              Dimensión
            </th>
            ${jobs.map((job) => {
    const state = currentStates(job);
    const canApply = state.publicationStatus === 'active' && job.recordKind !== 'demonstration';
    const applyUrl = safeHttpsUrl(job.applyUrl);
    const isDemo = job.recordKind === 'demonstration';
    return `
                <th scope="col" class="w-[calc(50%-85px)] p-4 bg-stone-50/90 border-b border-stone-200 align-top">
                  <div class="space-y-2">
                    <div>
                      <span class="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${isDemo ? 'text-amber-800 bg-amber-100/90 border border-amber-200' : (state.verificationStatus === 'stale' ? 'text-amber-800 bg-amber-50 border border-amber-200' : (canApply ? 'text-arcticBlue bg-iceBlue/20 border border-crystalBlue/30' : 'text-stone-700 bg-stone-100 border border-stone-200'))}">
                        ${isDemo ? 'Ficha demostrativa' : (state.verificationStatus === 'stale' ? 'Pendiente de revalidación' : (canApply ? 'Oportunidad verificada' : 'No confirmada'))}
                      </span>
                      <h4 class="text-sm font-bold text-stone-900 mt-1.5 leading-snug">${escapeHTML(job.title)}</h4>
                      <p class="text-xs text-stone-600 font-medium mt-0.5">${escapeHTML(job.employer)}${job.sector ? ` · <span class="text-stone-500 font-normal">${escapeHTML(job.sector)}</span>` : ''}</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 pt-1">
                      <button
                        type="button"
                        class="btn-compare-detail inline-flex items-center gap-1 rounded-lg bg-stone-900 hover:bg-neutral-800 text-white px-3 py-1.5 text-xs font-semibold transition-colors cursor-pointer"
                        data-compare-open="${escapeHTML(job.id)}"
                      >
                        Ver detalle ↗
                      </button>
                      ${canApply && applyUrl ? `
                        <a
                          href="${escapeHTML(applyUrl)}"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="inline-flex items-center gap-1 rounded-lg bg-arcticBlue hover:bg-[#125091] text-white px-3 py-1.5 text-xs font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-arcticBlue"
                        >
                          Ir a postulación ↗
                        </a>
                      ` : ''}
                    </div>
                  </div>
                </th>
              `;
  }).join('')}
          </tr>
        </thead>
        <tbody class="divide-y divide-stone-200">
          ${rows.map(([label, field]) => {
    const isDiff = isComparisonRowDifferent(jobs[0], jobs[1], field);
    return `
              <tr data-compare-diff="${isDiff}" class="compare-row transition-colors">
                <th scope="row" class="w-[170px] p-3.5 align-top font-semibold text-stone-700 bg-stone-50/40 border-r border-stone-200/80">
                  <div class="flex flex-col items-start gap-1">
                    <span>${escapeHTML(label)}</span>
                    <span class="diff-badge hidden inline-block text-[10px] font-bold uppercase tracking-wider text-arcticBlue bg-iceBlue/25 border border-crystalBlue/40 px-1.5 py-0.5 rounded">Diferencia</span>
                  </div>
                </th>
                ${jobs.map((job) => `
                  <td class="p-3.5 align-top text-stone-800 leading-relaxed">
                    ${renderComparisonCell(job, field)}
                  </td>
                `).join('')}
              </tr>
            `;
  }).join('')}
        </tbody>
      </table>
    </div>
    <p class="comparison-note mt-4 text-[11px] text-stone-500 leading-relaxed">Los enlaces oficiales y fechas de verificación se conservan en el detalle de cada ficha. No guardamos preferencias ni enviamos datos a terceros.</p>
  `;

  const toggleDiff = compareContent.querySelector('#compare-toggle-diff');
  if (toggleDiff) {
    toggleDiff.addEventListener('change', () => {
      const diffRows = compareContent.querySelectorAll('tr[data-compare-diff="true"]');
      diffRows.forEach((row) => {
        const badge = row.querySelector('.diff-badge');
        if (toggleDiff.checked) {
          row.classList.add('bg-sky-50/70');
          if (badge) badge.classList.remove('hidden');
        } else {
          row.classList.remove('bg-sky-50/70');
          if (badge) badge.classList.add('hidden');
        }
      });
    });
  }

  compareDialog.showModal();
}

function goToPage(page) {
  const totalPages = Math.ceil(opportunities.length / pageSize) || 1;
  const targetPage = Math.max(1, Math.min(page, totalPages));
  if (targetPage !== currentPage) {
    currentPage = targetPage;
    render();
    if (list) {
      list.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}

if (typeof window !== 'undefined') {
  window.__setCatalogPageSize = (size) => {
    pageSize = size;
    render();
  };
  window.__goToCatalogPage = goToPage;
}

function render() {
  const activePageSize = typeof pageSize !== 'undefined' ? pageSize : 12;
  const activeCurrentPage = typeof currentPage !== 'undefined' ? currentPage : 1;
  const totalJobs = opportunities.length;
  const totalPages = Math.ceil(totalJobs / activePageSize) || 1;
  let pageToRender = activeCurrentPage;
  if (pageToRender > totalPages) {
    pageToRender = totalPages;
  }
  if (pageToRender < 1) {
    pageToRender = 1;
  }
  if (typeof currentPage !== 'undefined') {
    currentPage = pageToRender;
  }

  const startIndex = (pageToRender - 1) * activePageSize;
  const endIndex = Math.min(startIndex + activePageSize, totalJobs);
  const pagedJobs = opportunities.slice(startIndex, endIndex);

  list.innerHTML = pagedJobs.map(renderCard).join('');
  list.hidden = totalJobs === 0;
  empty.hidden = totalJobs > 0;
  count.textContent = `${totalJobs} ${totalJobs === 1 ? 'resultado' : 'resultados'}`;

  if (typeof pagination !== 'undefined' && pagination && typeof prevPageBtn !== 'undefined' && prevPageBtn && typeof nextPageBtn !== 'undefined' && nextPageBtn && typeof paginationInfo !== 'undefined' && paginationInfo) {
    paginationInfo.textContent = `Página ${pageToRender} de ${totalPages} · Mostrando ${totalJobs === 0 ? 0 : startIndex + 1}–${endIndex} de ${totalJobs} oportunidades`;
    if (totalJobs <= activePageSize) {
      pagination.hidden = true;
    } else {
      pagination.hidden = false;
      prevPageBtn.disabled = pageToRender <= 1;
      nextPageBtn.disabled = pageToRender >= totalPages;
    }
  }

  if (typeof comparePanel !== 'undefined' && comparePanel) updateComparePanel();
}

function normalized(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es');
}

const REGIME_DEFINITIONS = {
  PRE_PROFESSIONAL_INTERNSHIP: {
    id: 'PRE_PROFESSIONAL_INTERNSHIP',
    label: 'Prácticas preprofesionales',
    shortLabel: 'Prácticas Pre',
    badgeClass: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    nature: 'Modalidad formativa laboral para estudiantes de educación superior',
    legalFramework: 'Ley N° 28518 (Ley sobre Modalidades Formativas Laborales)',
    maxWorkingHours: 'Máximo 6 horas diarias o 30 horas semanales',
    compensation: 'Subvención económica mensual no menor a 1 RMV (con jornada máxima)',
    keyRights: 'Convenio formativo institucional, seguro médico cubierto al 100% por la empresa, descanso de 15 días subvencionado tras 12 meses, media subvención adicional cada 6 meses.',
    cautions: 'No constituye contrato de trabajo bajo subordinación común. No genera CTS ni gratificaciones de ley.',
  },
  PROFESSIONAL_INTERNSHIP: {
    id: 'PROFESSIONAL_INTERNSHIP',
    label: 'Prácticas profesionales',
    shortLabel: 'Prácticas Pro',
    badgeClass: 'bg-teal-50 text-teal-800 border-teal-200',
    nature: 'Modalidad formativa laboral para egresados o bachilleres',
    legalFramework: 'Ley N° 28518 y Ley N° 31396 (reconocimiento obligatorio como experiencia laboral)',
    maxWorkingHours: 'Máximo 8 horas diarias o 48 horas semanales',
    compensation: 'Subvención mensual no menor a 1 RMV',
    keyRights: 'Reconocimiento legal como experiencia laboral, seguro médico integral, descanso de 15 días tras 12 meses, media subvención adicional cada 6 meses.',
    cautions: 'Modalidad formativa con duración habitual máxima de 12 meses (o según estatuto institucional / Ley 31396).',
  },
  CAS: {
    id: 'CAS',
    label: 'Contratación Administrativa de Servicios (CAS)',
    shortLabel: 'CAS',
    badgeClass: 'bg-amber-50 text-amber-900 border-amber-300',
    nature: 'Régimen especial de contratación laboral privativo del Estado peruano',
    legalFramework: 'Decreto Legislativo N° 1057, Ley N° 29849 y Ley N° 31131 (SERVIR)',
    maxWorkingHours: 'Máximo 8 horas diarias o 48 horas semanales',
    compensation: 'Retribución mensual fijada en las bases del concurso público (mínimo legal RMV)',
    keyRights: '30 días de vacaciones remuneradas, ESSALUD, aguinaldos de Fiestas Patrias y Navidad según Ley de Presupuesto, licencias de ley.',
    cautions: 'Régimen exclusivo del sector público. El acceso formal requiere concurso público de méritos con cronograma estricto.',
  },
  LABOR_REGIME_728: {
    id: 'LABOR_REGIME_728',
    label: 'Régimen Laboral Privado (D. Leg. 728)',
    shortLabel: 'Planilla 728',
    badgeClass: 'bg-blue-50 text-blue-800 border-blue-200',
    nature: 'Contrato de trabajo subordinado del régimen general de la actividad privada',
    legalFramework: 'TUO del D. Leg. N° 728 (D.S. N° 003-97-TR) y Ley N° 27735',
    maxWorkingHours: 'Máximo 8 horas diarias o 48 horas semanales',
    compensation: 'Remuneración mensual pactada en contrato (mínimo legal RMV)',
    keyRights: 'Gratificaciones legales completas (julio y diciembre), Compensación por Tiempo de Servicios (CTS), 30 días de vacaciones, ESSALUD (9%), Seguro de Vida Ley.',
    cautions: 'Sujeto a período de prueba legal. Puede ser a plazo indeterminado o sujeto a modalidad (plazo fijo con causa objetiva).',
  },
  CIVIL_SERVICES: {
    id: 'CIVIL_SERVICES',
    label: 'Locación de Servicios (Honorarios)',
    shortLabel: 'Locación / Honorarios',
    badgeClass: 'bg-purple-50 text-purple-800 border-purple-200',
    nature: 'Contratación de naturaleza civil autónoma sin subordinación',
    legalFramework: 'Código Civil del Perú (artículos 1764 y siguientes)',
    maxWorkingHours: 'Sin jornada laboral obligatoria ni control de asistencia (prestación autónoma por producto/servicio)',
    compensation: 'Retribución civil acordada sujeta a emisión de Recibo por Honorarios (Renta de 4ta Categoría)',
    keyRights: 'Autonomía en la ejecución del servicio y entrega de productos pactados.',
    cautions: 'NO constituye vínculo laboral: no otorga gratificaciones, CTS, vacaciones ni beneficios laborales. La imposición de subordinación u horario desnaturaliza la relación.',
  },
  OTHER: {
    id: 'OTHER',
    label: 'Otras modalidades contractuales',
    shortLabel: 'Otra modalidad',
    badgeClass: 'bg-stone-100 text-stone-800 border-stone-300',
    nature: 'Contratación comercial, internacional (B2B / Contractor) u otro régimen especial',
    legalFramework: 'Acuerdo privado entre las partes / marco contractual aplicable',
    maxWorkingHours: 'Según lo estipulado en el contrato entre partes',
    compensation: 'Tarifa acordada (facturación por servicios o divisa internacional)',
    keyRights: 'Condiciones definidas estrictamente en el acuerdo entre partes.',
    cautions: 'No está amparado por los beneficios del régimen laboral peruano salvo pacto en contrario.',
  },
  UNSPECIFIED: {
    id: 'UNSPECIFIED',
    label: 'Modalidad no especificada',
    shortLabel: 'Por confirmar régimen',
    badgeClass: 'bg-stone-50 text-stone-600 border-stone-200',
    nature: 'Modalidad contractual no detallada expresamente en la publicación',
    legalFramework: 'Sujeto a verificación en las bases del proceso o contrato oficial',
    maxWorkingHours: 'No declarado en la publicación',
    compensation: 'Según oferta o bases del concurso',
    keyRights: 'Verificar en las bases del proceso o documentación formal antes de postular.',
    cautions: 'Velora no presume un régimen laboral sin evidencia documental explícita.',
  },
};

function getJobLaborRegime(job) {
  if (job && job.laborRegime && REGIME_DEFINITIONS[job.laborRegime]) {
    return job.laborRegime;
  }
  const text = normalized([
    job?.contractType,
    job?.requisition,
    job?.title,
    job?.kind,
    job?.level,
    job?.duration,
    job?.tasks,
    job?.requirements,
  ].join(' '));

  if (/\bcas\b|\b1057\b|contratacion administrativa de servicios|contrato administrativo de servicios|convocatoria cas|proceso cas/.test(text)) {
    return 'CAS';
  }
  if (/practica\s+pre\s*profesional|practicas\s+pre\s*profesionales|practicante\s+pre|pre\s*profesional/.test(text)) {
    return 'PRE_PROFESSIONAL_INTERNSHIP';
  }
  if (/practica\s+profesional|practicas\s+profesionales|practicante\s+profesional/.test(text)) {
    return 'PROFESSIONAL_INTERNSHIP';
  }
  if (/practica|practicante|intern\b/.test(text)) {
    if (/estudiante|ciclo/.test(text)) return 'PRE_PROFESSIONAL_INTERNSHIP';
    if (/egresad|bachiller/.test(text)) return 'PROFESSIONAL_INTERNSHIP';
    if (job?.kind === 'Prácticas') return 'PRE_PROFESSIONAL_INTERNSHIP';
  }
  if (/\b728\b|d\.?\s*leg\.?\s*728|actividad privada|planilla completa|cts semestral/.test(text)) {
    return 'LABOR_REGIME_728';
  }
  if (/locacion de servicios|locador|recibo por honorarios|recibos por honorarios|cuarta categoria|orden de servicio|articulo 1764/.test(text)) {
    return 'CIVIL_SERVICES';
  }
  if (/b2b|contractor|contrato mercantil|prestacion independiente internacional|\b276\b|servicio civil|30057/.test(text)) {
    return 'OTHER';
  }
  return 'UNSPECIFIED';
}

function regimeTag(job) {
  const regimeKey = getJobLaborRegime(job);
  const defn = REGIME_DEFINITIONS[regimeKey] || REGIME_DEFINITIONS.UNSPECIFIED;
  return `<span class="inline-flex items-center rounded-md px-2 py-1 text-[10px] font-semibold border ${defn.badgeClass}" title="${escapeHTML(defn.label)} · ${escapeHTML(defn.legalFramework)}">${escapeHTML(defn.shortLabel)}</span>`;
}

// --- TASK-R7-02: Skills & Competencies Taxonomy and Comparison Engine ---
const SKILL_TAXONOMY = {
  Python: { canonical: 'Python', category: 'Lenguajes de programación', patterns: [/\bpython(?:3)?\b/i] },
  Java: { canonical: 'Java', category: 'Lenguajes de programación', patterns: [/\bjava\b(?!\s*script)/i] },
  JavaScript: { canonical: 'JavaScript', category: 'Lenguajes de programación', patterns: [/\bjavascript\b/i, /\bjs\b(?!\s*(?:on|to))/i] },
  TypeScript: { canonical: 'TypeScript', category: 'Lenguajes de programación', patterns: [/\btypescript\b/i, /\bts\b(?!\s*(?:on|to))/i] },
  'C#': { canonical: 'C#', category: 'Lenguajes de programación', patterns: [/\bc#(?!\w)/i, /\bc\s*sharp\b/i] },
  'C++': { canonical: 'C++', category: 'Lenguajes de programación', patterns: [/\bc\+\+(?!\w)/i] },
  C: {
    canonical: 'C',
    category: 'Lenguajes de programación',
    patterns: [
      /\blenguaje\s+c\b/i,
      /\bprogramaci[oó]n\s+en\s+c\b/i,
      /\bc\s*\/c\+\+\b/i,
      /\bc\s*,\s*c\+\+\b/i,
      /\bc\s+y\s+c\+\+\b/i,
      /\bc(?:\s+y\/o|\/)\s*rust\b/i,
      /\blinux\s+kernel\s*·\s*c\b/i,
    ],
  },
  Rust: { canonical: 'Rust', category: 'Lenguajes de programación', patterns: [/\brust\b/i] },
  Go: {
    canonical: 'Go',
    category: 'Lenguajes de programación',
    patterns: [
      /\bgolang\b/i,
      /\blenguaje\s+go\b/i,
      /\bprogramaci[oó]n\s+en\s+go\b/i,
      /(?:^|[\s·•,|/])go(?:[\s·•,|/]|$)/i,
    ],
  },
  PHP: { canonical: 'PHP', category: 'Lenguajes de programación', patterns: [/\bphp\b/i] },
  Kotlin: { canonical: 'Kotlin', category: 'Lenguajes de programación', patterns: [/\bkotlin\b/i] },
  Swift: { canonical: 'Swift', category: 'Lenguajes de programación', patterns: [/\bswift\b/i] },
  Dart: { canonical: 'Dart', category: 'Lenguajes de programación', patterns: [/\bdart\b/i] },
  'Bash / Shell': { canonical: 'Bash / Shell', category: 'Lenguajes de programación', patterns: [/\bbash\b/i, /\bshell\s+script(?:ing)?\b/i] },
  React: { canonical: 'React', category: 'Frameworks y librerías', patterns: [/\breact(?:\.js)?\b/i] },
  Angular: { canonical: 'Angular', category: 'Frameworks y librerías', patterns: [/\bangular\b/i] },
  'Vue.js': { canonical: 'Vue.js', category: 'Frameworks y librerías', patterns: [/\bvue(?:\.js)?\b/i] },
  'Node.js': { canonical: 'Node.js', category: 'Frameworks y librerías', patterns: [/\bnode(?:\.js)?\b/i] },
  'Spring Boot': { canonical: 'Spring Boot', category: 'Frameworks y librerías', patterns: [/\bspring\s*boot\b/i, /\bspring\s+framework\b/i] },
  '.NET': { canonical: '.NET', category: 'Frameworks y librerías', patterns: [/\b\.net\b/i, /\bdotnet\b/i, /\basp\.net\b/i] },
  Django: { canonical: 'Django', category: 'Frameworks y librerías', patterns: [/\bdjango\b/i] },
  FastAPI: { canonical: 'FastAPI', category: 'Frameworks y librerías', patterns: [/\bfastapi\b/i] },
  Flutter: { canonical: 'Flutter', category: 'Frameworks y librerías', patterns: [/\bflutter\b/i] },
  'UIKit / SwiftUI': { canonical: 'UIKit / SwiftUI', category: 'Frameworks y librerías', patterns: [/\buikit\b/i, /\bswiftui\b/i] },
  'Jetpack Compose': { canonical: 'Jetpack Compose', category: 'Frameworks y librerías', patterns: [/\bjetpack\s+compose\b/i] },
  SQL: { canonical: 'SQL', category: 'Bases de datos y analítica', patterns: [/(?<!transact-)(?<!t-)\bsql\b(?!\s*(?:server|lite))/i] },
  PostgreSQL: { canonical: 'PostgreSQL', category: 'Bases de datos y analítica', patterns: [/\bpostgres(?:ql)?\b/i] },
  MySQL: { canonical: 'MySQL', category: 'Bases de datos y analítica', patterns: [/\bmysql\b/i] },
  'SQL Server': { canonical: 'SQL Server', category: 'Bases de datos y analítica', patterns: [/\bsql\s*server\b/i, /\bmssql\b/i] },
  'Oracle DB': { canonical: 'Oracle DB', category: 'Bases de datos y analítica', patterns: [/\boracle\s*(?:db|database|bd)?\b/i] },
  MongoDB: { canonical: 'MongoDB', category: 'Bases de datos y analítica', patterns: [/\bmongodb\b/i, /\bmongo\b/i] },
  Redis: { canonical: 'Redis', category: 'Bases de datos y analítica', patterns: [/\bredis\b/i] },
  'Power BI': { canonical: 'Power BI', category: 'Bases de datos y analítica', patterns: [/\bpower\s*bi\b/i] },
  Excel: { canonical: 'Excel', category: 'Bases de datos y analítica', patterns: [/\bexcel\b(?:\s*avanzado|\s*intermedio)?/i] },
  ETL: { canonical: 'ETL', category: 'Bases de datos y analítica', patterns: [/\betl\b/i] },
  AWS: { canonical: 'AWS', category: 'Cloud, DevOps e Infraestructura', patterns: [/\baws\b/i, /\bamazon\s+web\s+services\b/i] },
  Azure: { canonical: 'Azure', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bazure\b/i, /\bmicrosoft\s+azure\b/i] },
  'Google Cloud': { canonical: 'Google Cloud', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bgcp\b/i, /\bgoogle\s+cloud(?:\s+platform)?\b/i] },
  Docker: { canonical: 'Docker', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bdocker\b/i] },
  Kubernetes: { canonical: 'Kubernetes', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bkubernetes\b/i, /\bk8s\b/i] },
  Linux: { canonical: 'Linux', category: 'Cloud, DevOps e Infraestructura', patterns: [/\blinux\b/i] },
  Ubuntu: { canonical: 'Ubuntu', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bubuntu\b/i] },
  Git: { canonical: 'Git', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bgit\b(?!\s*(?:hub|lab))/i] },
  'CI/CD': { canonical: 'CI/CD', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bci\s*\/\s*cd\b/i, /\bcontinuous\s+integration\b/i, /\bintegraci[oó]n\s+continua\b/i] },
  Terraform: { canonical: 'Terraform', category: 'Cloud, DevOps e Infraestructura', patterns: [/\bterraform\b/i] },
  'APIs REST': { canonical: 'APIs REST', category: 'Arquitectura y Metodologías', patterns: [/\bapis?\s+rest(?:ful)?\b/i, /\bservicios?\s+rest\b/i, /\brest\s*api\b/i] },
  Microservicios: { canonical: 'Microservicios', category: 'Arquitectura y Metodologías', patterns: [/\bmicroservicios\b/i, /\bmicroservices\b/i] },
  'Clean Architecture': { canonical: 'Clean Architecture', category: 'Arquitectura y Metodologías', patterns: [/\bclean\s+architecture\b/i, /\barquitectura\s+limpia\b/i, /\bmvvm\b/i] },
  'ERP / SAP': { canonical: 'ERP / SAP', category: 'Sistemas de gestión', patterns: [/\berp\b/i, /\bsap\b/i, /\bmrp\b/i] },
  Ciberseguridad: { canonical: 'Ciberseguridad', category: 'Seguridad y Redes', patterns: [/\bciberseguridad\b/i, /\bseguridad\s+inform[aá]tica\b/i, /\binformation\s+security\b/i, /\bsecurity\b/i] },
  Redes: { canonical: 'Redes', category: 'Seguridad y Redes', patterns: [/\bredes(?!\s*sociales)(?:\s+de\s+datos|\s+y\s+telecomunicaciones|\s+tcp|\s+cisco)?\b/i] },
};

const PREFERRED_PATTERNS = [
  /\bdeseable\b/i,
  /\bpreferible\b/i,
  /\bpreferente\b/i,
  /\bde\s+preferencia\b/i,
  /\bplus\b/i,
  /\bopcional\b/i,
  /\bvalorar[aá]\b/i,
  /\bse\s+valorar[aá]\b/i,
  /\bno\s+excluyente\b/i,
];

const REQUIRED_PATTERNS = [
  /\bindispensable\b/i,
  /\bexcluyente\b/i,
  /\bobligatorio\b/i,
  /\bm[ií]nimo\b/i,
  /\brequisito\b/i,
  /\bexperiencia\s*(?:m[ií]nima|comprobada|de)\b/i,
  /\bconocimiento\s*(?:s[oó]lido|avanzado|intermedio)\b/i,
  /\bdebe\s+contar\b/i,
  /\bdominio\b/i,
];

function determineSkillPriority(clause, sourceField) {
  const norm = normalized(clause);
  if (PREFERRED_PATTERNS.some((pat) => pat.test(norm))) {
    return 'PREFERRED';
  }
  if (REQUIRED_PATTERNS.some((pat) => pat.test(norm))) {
    return 'REQUIRED';
  }
  if (['requirements', 'skills', 'title'].includes(sourceField)) {
    return 'REQUIRED';
  }
  return 'MENTIONED';
}

function extractOpportunitySkills(job) {
  const extracted = {};

  function inspectBlock(text, sourceField) {
    if (!text || typeof text !== 'string') return;
    const clauses = text.split(/[;.\n\r·•|]/).map((c) => c.trim()).filter(Boolean);
    const items = clauses.length > 0 ? clauses : [text.trim()];

    for (const clause of items) {
      const normClause = normalized(clause);
      for (const [skillKey, defn] of Object.entries(SKILL_TAXONOMY)) {
        for (const pattern of defn.patterns) {
          if (pattern.test(normClause)) {
            const priority = determineSkillPriority(clause, sourceField);
            const priorityRank = { REQUIRED: 3, PREFERRED: 2, MENTIONED: 1 };
            if (extracted[skillKey]) {
              if (extracted[skillKey].source_field === 'requirements' && sourceField === 'skills') {
                // Keep requirements as authoritative
              } else {
                const priorityRank = { REQUIRED: 3, PREFERRED: 2, MENTIONED: 1 };
                if ((priorityRank[priority] || 0) > (priorityRank[extracted[skillKey].priority] || 0)) {
                  extracted[skillKey].priority = priority;
                  extracted[skillKey].source_field = sourceField;
                  extracted[skillKey].context = clause.slice(0, 120);
                }
              }
            } else {
              extracted[skillKey] = {
                canonical: defn.canonical,
                category: defn.category,
                raw: skillKey,
                priority,
                source_field: sourceField,
                context: clause.slice(0, 120),
              };
            }
            break;
          }
        }
      }
    }
  }

  // 1. Requirements field (highest specificity)
  const reqsField = String(job?.requirements || '').trim();
  if (reqsField && !/^no\s/i.test(reqsField)) inspectBlock(reqsField, 'requirements');

  // 2. Direct explicit skills field
  const skillsField = String(job?.skills || '').trim();
  if (skillsField && !/^no\s/i.test(skillsField)) inspectBlock(skillsField, 'skills');

  // 3. Title field
  const titleField = String(job?.title || '').trim();
  if (titleField) inspectBlock(titleField, 'title');

  // 4. Tasks / description field
  const tasksField = String(job?.tasks || '').trim();
  if (tasksField && !/^no\s/i.test(tasksField)) inspectBlock(tasksField, 'tasks');

  return extracted;
}

function compareOpportunitySkills(jobA, jobB) {
  const skillsA = extractOpportunitySkills(jobA);
  const skillsB = extractOpportunitySkills(jobB);

  const keysA = Object.keys(skillsA);
  const keysB = Object.keys(skillsB);

  const sharedKeys = keysA.filter((k) => keysB.includes(k)).sort();
  const exclusiveAKeys = keysA.filter((k) => !keysB.includes(k)).sort();
  const exclusiveBKeys = keysB.filter((k) => !keysA.includes(k)).sort();

  const shared_skills = sharedKeys.map((k) => ({
    canonical: k,
    category: skillsA[k].category,
    priorityA: skillsA[k].priority,
    priorityB: skillsB[k].priority,
    sourceFieldA: skillsA[k].source_field,
    sourceFieldB: skillsB[k].source_field,
    contextA: skillsA[k].context,
    contextB: skillsB[k].context,
  }));

  const exclusive_a = exclusiveAKeys.map((k) => skillsA[k]);
  const exclusive_b = exclusiveBKeys.map((k) => skillsB[k]);

  const required_a = keysA.filter((k) => skillsA[k].priority === 'REQUIRED').sort();
  const required_b = keysB.filter((k) => skillsB[k].priority === 'REQUIRED').sort();

  const preferred_a = keysA.filter((k) => skillsA[k].priority === 'PREFERRED').sort();
  const preferred_b = keysB.filter((k) => skillsB[k].priority === 'PREFERRED').sort();

  return {
    job_a_id: String(jobA?.id || 'A'),
    job_b_id: String(jobB?.id || 'B'),
    shared_skills,
    exclusive_a,
    exclusive_b,
    required_a,
    required_b,
    preferred_a,
    preferred_b,
    is_a_unspecified: keysA.length === 0,
    is_b_unspecified: keysB.length === 0,
  };
}

function renderSkillsComparison(jobA, jobB) {
  const comp = compareOpportunitySkills(jobA, jobB);
  const titleA = escapeHTML(jobA.employer || jobA.title || 'Oportunidad A');
  const titleB = escapeHTML(jobB.employer || jobB.title || 'Oportunidad B');

  const priorityBadge = (priority) => {
    if (priority === 'REQUIRED') {
      return `<span class="inline-block text-[9px] font-semibold text-rose-700 bg-rose-50 border border-rose-200/80 px-1.5 py-0.5 rounded" title="Requisito expresamente obligatorio">Obligatorio</span>`;
    }
    if (priority === 'PREFERRED') {
      return `<span class="inline-block text-[9px] font-semibold text-amber-800 bg-amber-50 border border-amber-200/80 px-1.5 py-0.5 rounded" title="Requisito deseable o preferente">Deseable</span>`;
    }
    return `<span class="inline-block text-[9px] font-semibold text-stone-600 bg-stone-100 border border-stone-200/80 px-1.5 py-0.5 rounded" title="Tecnología mencionada sin prioridad explícita">Mención</span>`;
  };

  const sharedHtml = comp.shared_skills.length > 0
    ? `<div class="flex flex-wrap gap-1.5">
        ${comp.shared_skills.map((s) => `
          <div class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50 border border-emerald-200/90 px-2 py-1 text-xs text-emerald-950" title="Compartida · ${escapeHTML(s.canonical)}&#10;En ${titleA}: ${s.priorityA} (${escapeHTML(s.sourceFieldA)})&#10;En ${titleB}: ${s.priorityB} (${escapeHTML(s.sourceFieldB)})">
            <span class="font-semibold">${escapeHTML(s.canonical)}</span>
            <span class="text-[9px] text-emerald-700 font-mono">(${s.priorityA === s.priorityB ? (s.priorityA === 'REQUIRED' ? 'Oblig.' : (s.priorityA === 'PREFERRED' ? 'Deseab.' : 'Menc.')) : 'Distinta prioridad'})</span>
          </div>
        `).join('')}
      </div>`
    : `<p class="text-xs text-stone-500 italic">No se identificaron tecnologías coincidentes explicitadas en ambas fichas.</p>`;

  const exclusiveAHtml = comp.exclusive_a.length > 0
    ? `<div class="flex flex-wrap gap-1.5">
        ${comp.exclusive_a.map((s) => `
          <div class="inline-flex items-center gap-1.5 rounded-lg bg-sky-50 border border-sky-200/90 px-2 py-1 text-xs text-sky-950" title="Exclusiva de ${titleA}&#10;Prioridad: ${s.priority}&#10;Detectado en: ${escapeHTML(s.source_field)}&#10;Contexto: &quot;${escapeHTML(s.context)}&quot;">
            <span class="font-semibold">${escapeHTML(s.canonical)}</span>
            ${priorityBadge(s.priority)}
          </div>
        `).join('')}
      </div>`
    : `<p class="text-xs text-stone-500 italic">Sin competencias técnicas exclusivas detectadas para esta oportunidad.</p>`;

  const exclusiveBHtml = comp.exclusive_b.length > 0
    ? `<div class="flex flex-wrap gap-1.5">
        ${comp.exclusive_b.map((s) => `
          <div class="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 border border-indigo-200/90 px-2 py-1 text-indigo-950" title="Exclusiva de ${titleB}&#10;Prioridad: ${s.priority}&#10;Detectado en: ${escapeHTML(s.source_field)}&#10;Contexto: &quot;${escapeHTML(s.context)}&quot;">
            <span class="font-semibold">${escapeHTML(s.canonical)}</span>
            ${priorityBadge(s.priority)}
          </div>
        `).join('')}
      </div>`
    : `<p class="text-xs text-stone-500 italic">Sin competencias técnicas exclusivas detectadas para esta oportunidad.</p>`;

  const unstatedWarnings = [];
  if (comp.is_a_unspecified) {
    unstatedWarnings.push(`<b>${titleA}</b> no incluye un listado estructurado de tecnologías o requisitos técnicos en la publicación oficial registrada.`);
  }
  if (comp.is_b_unspecified) {
    unstatedWarnings.push(`<b>${titleB}</b> no incluye un listado estructurado de tecnologías o requisitos técnicos en la publicación oficial registrada.`);
  }

  const warningsHtml = unstatedWarnings.length > 0
    ? `<div class="mt-3 rounded-lg bg-amber-50/80 border border-amber-200/80 p-3 text-xs text-amber-900 leading-relaxed">
        <div class="flex items-center gap-1.5 font-semibold text-amber-800 mb-1">
          <svg class="h-3.5 w-3.5 text-amber-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          <span>Limitación de información registrada:</span>
        </div>
        <ul class="list-disc pl-4 space-y-1">
          ${unstatedWarnings.map((w) => `<li>${w}</li>`).join('')}
        </ul>
        <p class="mt-1.5 text-[11px] text-amber-800 italic">La ausencia de una tecnología en la ficha no certifica que el puesto prescinda de ella; refleja que no fue explícitamente declarada en la convocatoria fuente.</p>
      </div>`
    : '';

  return `
    <section class="skills-comparison-panel mb-5 rounded-xl border border-stone-200 bg-white p-4 sm:p-5 shadow-xs" aria-label="Comparativa de competencias técnicas y requisitos">
      <div class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-stone-200/80 pb-3">
        <div>
          <h3 class="text-sm font-bold uppercase tracking-wider text-stone-800 flex items-center gap-2">
            <span>Contraste de Requisitos Técnicos y Competencias</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-iceBlue/20 text-arcticBlue border border-crystalBlue/30">Análisis determinista</span>
          </h3>
          <p class="text-xs text-stone-600 mt-0.5">Identificación de habilidades coincidentes y diferenciadoras trazables a los datos de cada convocatoria.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        <!-- 1. Coincidentes -->
        <div class="rounded-lg border border-emerald-200 bg-emerald-50/40 p-3.5 flex flex-col">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1.5">
              <svg class="h-3.5 w-3.5 text-emerald-700 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              <span>Coincidentes</span>
            </h4>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">${comp.shared_skills.length}</span>
          </div>
          <div class="flex-1">${sharedHtml}</div>
        </div>

        <!-- 2. Exclusivas A -->
        <div class="rounded-lg border border-sky-200 bg-sky-50/40 p-3.5 flex flex-col">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-sky-900 truncate" title="Exclusivas de ${titleA}">
              <span>Exclusivas: ${titleA}</span>
            </h4>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800 border border-sky-300">${comp.exclusive_a.length}</span>
          </div>
          <div class="flex-1">${exclusiveAHtml}</div>
        </div>

        <!-- 3. Exclusivas B -->
        <div class="rounded-lg border border-indigo-200 bg-indigo-50/40 p-3.5 flex flex-col">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-indigo-900 truncate" title="Exclusivas de ${titleB}">
              <span>Exclusivas: ${titleB}</span>
            </h4>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">${comp.exclusive_b.length}</span>
          </div>
          <div class="flex-1">${exclusiveBHtml}</div>
        </div>
      </div>

      ${warningsHtml}
    </section>
  `;
}

function getVisibleJobs() {
  const tokens = normalized(filters.query.value).split(/\s+/).filter(Boolean);
  const location = normalized(filters.location.value);
  const mode = normalized(filters.mode.value);
  const kind = filters.kind.value;
  const family = normalized(filters.family.value);
  const sector = filters.sector.value;
  const level = filters.level.value;
  const regime = filters.regime?.value || '';
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
    if (regime && getJobLaborRegime(job) !== regime) return false;
    if (filters.salary.value === 'published' && (!job.salary || /no publicado|no especificado/i.test(job.salary))) return false;
    if (filters.risk.value === 'temporary' && !temporarySignal.test([job.title, job.duration, job.deadline, job.continuity, job.risk].join(' '))) return false;
    const jobRegime = getJobLaborRegime(job);
    const regimeDef = REGIME_DEFINITIONS[jobRegime] || REGIME_DEFINITIONS.UNSPECIFIED;
    const searchable = normalized([
      job.title, job.employer, job.sector, job.family, job.level,
      job.kind, job.mode, job.location, job.eligibility, job.skills,
      job.tasks, job.requirements, jobRegime, regimeDef.label, regimeDef.shortLabel,
    ].join(' '));
    return tokens.every((token) => searchable.includes(token));
  }).sort((a, b) => {
    const rank = (job) => {
      const s = currentStates(job);
      if (s.publicationStatus === 'active') {
        return s.verificationStatus === 'verified' ? 0 : 1;
      }
      return s.publicationStatus === 'historical' ? 3 : 2;
    };
    return rank(a) - rank(b) || a.employer.localeCompare(b.employer, 'es') || a.title.localeCompare(b.title, 'es');
  });
}

function publicCatalogMetrics(records) {
  const metrics = { active: 0, expiredOrHistorical: 0, unconfirmed: 0 };
  records.filter((job) => job.recordKind !== 'demonstration').forEach((job) => {
    const state = currentStates(job);
    if (['expired', 'closed'].includes(state.opportunityStatus) || state.publicationStatus === 'historical') {
      metrics.expiredOrHistorical += 1;
    } else if (state.publicationStatus === 'active') {
      if (state.verificationStatus === 'stale') {
        metrics.unconfirmed += 1;
      } else {
        metrics.active += 1;
      }
    } else {
      metrics.unconfirmed += 1;
    }
  });
  return metrics;
}

function updateCatalogView() {
  currentPage = 1;
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
  const isFiltered = Boolean(
    (filters.query && filters.query.value.trim() !== '')
    || (filters.location && filters.location.value.trim() !== '')
    || (filters.mode && filters.mode.value !== '')
    || (filters.kind && filters.kind.value !== '')
    || (filters.family && filters.family.value !== '')
    || (filters.sector && filters.sector.value !== '')
    || (filters.level && filters.level.value !== '')
    || (filters.salary && filters.salary.value !== '')
    || (filters.risk && filters.risk.value !== '')
    || (filters.regime && filters.regime.value !== '')
  );
  const includeExamples = document.querySelector('#include-demonstrations').checked;
  const includeOtherStates = document.querySelector('#include-unconfirmed').checked || filters.history.checked;
  const showNoVerifiedOpportunities = !isFiltered && !includeExamples && !includeOtherStates;

  if (catalog.length === 0) {
    empty.querySelector('h3').textContent = 'No hay oportunidades disponibles';
    empty.querySelector('p').textContent = 'El catálogo no contiene convocatorias actualmente.';
  } else if (opportunities.length === 0 && isFiltered) {
    empty.querySelector('h3').textContent = 'No encontramos coincidencias para esta búsqueda';
    empty.querySelector('p').textContent = 'Prueba quitar algún filtro o modificar los términos de búsqueda.';
  } else if (showNoVerifiedOpportunities) {
    empty.querySelector('h3').textContent = 'No hay oportunidades verificadas disponibles';
    const unconfirmedCount = catalog.filter((j) => j.recordKind !== 'demonstration' && (typeof currentStates === 'function' ? currentStates(j).publicationStatus === 'unconfirmed' : j.publicationStatus === 'unconfirmed')).length;
    empty.querySelector('p').textContent = unconfirmedCount > 0
      ? `Actualmente no hay oportunidades con verificación reciente (últimos ${catalogConfig.verificationTtlDays || 7} días). Hay ${unconfirmedCount} convocatorias en revisión que puedes consultar activando “Incluir no confirmadas”.`
      : 'Las oportunidades se incorporan después de revisar la publicación original y el canal de postulación. Puedes activar “Incluir ejemplos demostrativos” para explorar ejemplos que no son vacantes reales.';
  } else {
    empty.querySelector('h3').textContent = 'No encontramos coincidencias';
    empty.querySelector('p').textContent = 'Prueba quitar algún filtro. Los ejemplos demostrativos nunca representan vacantes reales ni habilitan la postulación.';
  }
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
  dialogContent.innerHTML = renderDetailContent(job, { isStandalone: false });
  dialog.showModal();
  if (typeof window !== 'undefined' && window.history && window.history.pushState) {
    const currentParam = new URLSearchParams(window.location.search).get('id');
    if (currentParam !== job.id) {
      const url = new URL(window.location.href);
      url.searchParams.set('id', job.id);
      window.history.pushState({ id: job.id, modal: true }, '', url.toString());
    }
  }
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
    if (typeof handleRouting === 'function') handleRouting();
  } catch (error) {
    console.error('[Velora] No se pudo cargar el catálogo:', error);
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
if (filters.regime) filters.regime.addEventListener('change', updateCatalogView);
filters.history.addEventListener('change', updateCatalogView);
document.querySelector('#include-unconfirmed').addEventListener('change', updateCatalogView);
document.querySelector('#include-demonstrations').addEventListener('change', updateCatalogView);
document.querySelector('#filters').addEventListener('submit', (event) => event.preventDefault());
document.querySelector('#filters').addEventListener('reset', () => setTimeout(() => {
  filters.family.value = '';
  if (filters.regime) filters.regime.value = '';
  updateCatalogView();
}, 0));

document.querySelector('#empty-clear').addEventListener('click', () => document.querySelector('#filters').reset());
document.querySelector('#catalog-refresh').addEventListener('click', loadCatalog);
compareOpen.addEventListener('click', renderComparison);
compareClear.addEventListener('click', () => {
  compareIds = [];
  updateComparePanel();
  render();
});

if (compareContent) {
  compareContent.addEventListener('click', (event) => {
    const detailBtn = event.target.closest('[data-compare-open]');
    if (detailBtn) {
      const targetId = detailBtn.getAttribute('data-compare-open');
      const targetJob = catalog.find((item) => item.id === targetId);
      if (targetJob) {
        compareDialog.close();
        renderDialog(targetJob);
      }
    }
  });
}

if (prevPageBtn) {
  prevPageBtn.addEventListener('click', () => goToPage(currentPage - 1));
}
if (nextPageBtn) {
  nextPageBtn.addEventListener('click', () => goToPage(currentPage + 1));
}

if (dialog) {
  dialog.addEventListener('close', () => {
    if (typeof window !== 'undefined' && window.history && window.history.pushState) {
      const params = new URLSearchParams(window.location.search);
      if (params.has('id')) {
        params.delete('id');
        const newSearch = params.toString() ? `?${params.toString()}` : '';
        const newUrl = `${window.location.pathname}${newSearch}${window.location.hash}`;
        window.history.pushState({}, '', newUrl);
      }
    }
  });
}

if (opportunityView) {
  opportunityView.addEventListener('click', (event) => {
    const backBtn = event.target.closest('[data-action="back-to-catalog"]');
    if (backBtn) {
      event.preventDefault();
      closeOpportunityPage(true);
    }
  });
}

list.addEventListener('click', (event) => {
  const compareButton = event.target.closest('[data-compare]');
  if (compareButton) {
    toggleCompare(compareButton.dataset.compare);
    return;
  }
  const openLink = event.target.closest('a[data-open]');
  if (openLink) {
    if (!event.ctrlKey && !event.metaKey && !event.shiftKey && event.button === 0) {
      event.preventDefault();
      const job = catalog.find((item) => item.id === openLink.dataset.open);
      if (job) renderOpportunityPage(job, true);
    }
    return;
  }
  const button = event.target.closest('button[data-open]');
  if (!button) return;
  const job = catalog.find((item) => item.id === button.dataset.open);
  if (job) renderDialog(job);
});

list.addEventListener('keydown', (event) => {
  const title = event.target.closest('[data-open][role="button"]');
  if (title && (event.key === 'Enter' || event.key === ' ')) {
    event.preventDefault();
    const job = catalog.find((item) => item.id === title.dataset.open);
    if (job) renderOpportunityPage(job, true);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && (!dialog || !dialog.open) && (!opportunityView || opportunityView.hidden)) {
    event.preventDefault();
    filters.query.focus();
  }
});

window.addEventListener('popstate', handleRouting);
window.addEventListener('hashchange', handleRouting);

loadCatalog();
