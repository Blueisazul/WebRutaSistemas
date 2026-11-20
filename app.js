let catalog = [];
let opportunities = [];

const catalogView = document.querySelector('#catalog-view');
const opportunityView = document.querySelector('#opportunity-view');
const list = document.querySelector('#job-list');
const count = document.querySelector('#result-count');
const empty = document.querySelector('#empty-state');
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
  const mode = job.mode || 'No especificada';
  const className = mode.toLowerCase().includes('remoto') ? 'remote' : 'mode';
  return `<span class="tag ${className}">${escapeHTML(mode)}</span>`;
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
    'badge-check': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}" aria-hidden="true"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m16 9-5.5 5.5L8 12"/></svg>`, building: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="' + className + '" aria-hidden="true"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>',
    'triangle-alert': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`,
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

function renderDetailContent(job, { isStandalone = false } = {}) {
  const state = currentStates(job);
  const sourceUrl = safeHttpsUrl(job.sourceUrl);
  const applyUrl = safeHttpsUrl(job.applyUrl);
  const canApply = state.publicationStatus === 'active' && job.recordKind !== 'demonstration';
  const statusText = canApply
    ? `La fuente del empleador se revisó el ${formatDateTime(job.lastVerifiedAt)}; esta comprobación no garantiza disponibilidad posterior.`
    : state.opportunityStatus === 'expired'
      ? 'La fecha límite de postulación ya pasó. Se conserva como referencia y no se habilita el enlace para postular.'
      : state.publicationStatus === 'historical'
        ? 'Registro histórico conservado para referencia. No está disponible para postular.'
        : `${job.recordKind === 'demonstration' ? 'Ficha de demostración. ' : ''}No tiene evidencia vigente suficiente para presentarla como postulable. Última verificación: ${formatDateTime(job.lastVerifiedAt)}; última consulta registrada: ${formatDateTime(job.lastCheckedDate)}. No se afirma que siga publicada.`;
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
    value: escapeHTML(verifiedDateFormatted),
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
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-ice-blue/10 text-crystal-blue border border-ice-blue/30">
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
              ${isVerified ? 'text-crystal-blue' : 'text-crystal-blue'}">
              ${isVerified
      ? lucideIcon('badge-check', 'h-3.5 w-3.5')
      : lucideIcon('triangle-alert', 'h-3.5 w-3.5')}
              ${isVerified ? '✓ Fuente oficial verificada' : 'Fuente de consulta'}
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
      : 'Convocatoria registrada pendiente de comprobación directa'}
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
                    bg-crystalBlue px-3 py-2 text-xs font-semibold mb-2
                    transition-colors duration-150
                    hover:bg-arcticBlue
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
    <section class="summary-section rounded-xl bg-white shadow-xs hover:border-stone-300 transition-colors" aria-label="Resumen de condiciones de la oportunidad">
      <h3 class="text-xs font-bold uppercase tracking-wider text-stone-500 px-5 pt-4">Resumen</h3>
      <div class="summary-grid detail-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        ${summaryCardsHtml}
      </div>
      <div>
        <!-- 3. Tecnologías y herramientas declaradas (inmediatamente debajo del Resumen) -->
        ${skillsHtml}
      </div>
    </section>

    <!-- 4. Tareas y Requisitos del puesto -->
    <section class="bg-white border border-stone-200/80 rounded-xl p-4 shadow-xs">
      <div class="mb-6 mt-6">
        <h3 class="text-[14px] font-bold uppercase tracking-wider text-stone-700 mb-2">Qué harías</h3>
        <p class="text-sm text-stone-700 leading-relaxed ">${escapeHTML(job.tasks || 'La descripción completa se consulta en la fuente original.')}</p>
      </div>

      <div class="detail-section mb-6">
        <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2">Requisitos del puesto</h3>
        <p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(job.requirements || 'Revisar requisitos en la publicación original.')}</p>
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
          <p class="text-sm text-stone-700 leading-relaxed">${escapeHTML(job.benefits)}</p>
        </div>
      ` : ''}
    </section>

    <!-- Verificación y procedencia -->
    <section class="verification-section bg-white border border-stone-200/80 rounded-xl p-4 shadow-xs mt-6">

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
    document.title = `${job.title} · ${job.employer} — Ruta Sistemas`;
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
    document.title = 'Oportunidad no encontrada — Ruta Sistemas';
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
    document.title = 'Ruta Sistemas';
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
    const verStatusMap = { verified: 'Verificada', stale: 'Atrasada', unconfirmed: 'Sin verificar' };
    const pubStatusMap = { active: 'Activa', historical: 'Histórica', unconfirmed: 'Sin verificar' };
    const opp = oppStatusMap[state.opportunityStatus] || state.opportunityStatus;
    const ver = verStatusMap[state.verificationStatus] || state.verificationStatus;
    const pub = pubStatusMap[state.publicationStatus] || state.publicationStatus;
    return `${opp} · ${ver} · ${pub}`;
  }
  if (field === 'salary') return knownValue(job.salary) ? job.salary : 'No publicado';
  return knownValue(job[field]) ? job[field] : 'No informado';
}

function renderComparison() {
  const jobs = compareIds.map((id) => catalog.find((job) => job.id === id)).filter(Boolean);
  if (jobs.length !== 2) return;
  const rows = [
    ['Compensación', 'salary'], ['Beneficios', 'benefits'], ['Modalidad', 'mode'],
    ['Elegibilidad / ubicación', 'eligibility'], ['Duración', 'duration'], ['Tipo', 'kind'],
    ['Nivel', 'level'], ['Familia técnica', 'family'], ['Funciones', 'tasks'],
    ['Tecnologías', 'skills'], ['Desarrollo declarado', 'growth'], ['Continuidad', 'continuity'],
    ['Riesgos', 'risk'], ['Estado de verificación', 'status'],
  ];
  compareContent.innerHTML = `<p class="dialog-eyebrow">COMPARACIÓN LOCAL · SIN PUNTUACIÓN</p>
    <h2 id="compare-dialog-title" class="dialog-title">Dos alternativas, sin ganador universal</h2>
    <p class="dialog-intro">Observa qué está publicado y qué falta confirmar. La comparación no convierte datos ausentes en condiciones desfavorables.</p>
    <div class="comparison-table-wrap"><table class="comparison-table"><thead><tr><th scope="col">Dimensión</th>${jobs.map((job) => `<th scope="col"><span>${escapeHTML(job.recordKind === 'demonstration' ? 'Ficha demostrativa · ' : '')}${escapeHTML(job.title)}</span><small>${escapeHTML(job.employer)}</small></th>`).join('')}</tr></thead>
      <tbody>${rows.map(([label, field]) => `<tr><th scope="row">${escapeHTML(label)}</th>${jobs.map((job) => `<td>${escapeHTML(comparisonValue(job, field))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
    <p class="comparison-note">Los enlaces y fechas de evidencia se conservan en el detalle de cada ficha. No guardamos preferencias ni enviamos datos a terceros.</p>`;
  compareDialog.showModal();
}

function render() {
  const jobs = opportunities;
  list.innerHTML = jobs.map(renderCard).join('');
  list.hidden = jobs.length === 0;
  empty.hidden = jobs.length > 0;
  count.textContent = `${jobs.length} ${jobs.length === 1 ? 'resultado' : 'resultados'}`;
  if (typeof comparePanel !== 'undefined' && comparePanel) updateComparePanel();
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
    empty.querySelector('p').textContent = 'Las oportunidades se incorporan después de revisar la publicación original y el canal de postulación. Puedes activar “Incluir ejemplos demostrativos” para explorar ejemplos que no son vacantes reales.';
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
    console.error('[Ruta Sistemas] No se pudo cargar el catálogo:', error);
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
compareOpen.addEventListener('click', renderComparison);
compareClear.addEventListener('click', () => {
  compareIds = [];
  updateComparePanel();
  render();
});

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
