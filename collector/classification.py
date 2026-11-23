"""Deterministic classification module for candidate opportunities (R4-06).

Provides explainable, verifiable classification across three required axes:
1. Relevance to systems/computing students & graduates:
   - DIRECT: Software engineering, DevOps/SRE, data, cloud, cybersecurity, systems, QA, tech support.
   - ADJACENT: Operations analyst, BI/reporting, ERP/MRP, fraud/dispute/chargeback analyst, tech product.
   - UNDEMONSTRATED: Ambiguous, generic or unspecified roles lacking concrete technical evidence.
   - NOT_RELEVANT: Culinary/kitchen, retail, warehouse, legal, sales, HR, marketing, accounting.

2. Geographic eligibility for candidates based in Peru:
   - PERU_LOCAL: Physical location explicitly within Peru.
   - PERU_REMOTE: Remote with explicit Peru eligibility.
   - LATAM: Remote across Latin America / Americas region.
   - GLOBAL_REMOTE: Remote worldwide / home-based globally.
   - NOT_ELIGIBLE: Restricted to specific non-Peru countries/cities with no remote option.
   - UNKNOWN: Location unspecified or ambiguous.

3. Experience tier / Seniority:
   - ENTRY_OR_JUNIOR: Intern, trainee, graduate, apprentice, junior, entry level, associate, 0-2 yrs.
   - MID: Standard professional role without senior/lead qualifiers.
   - SENIOR_OR_LEAD: Senior, lead, principal, staff, director, head of, vp, architect.
   - UNKNOWN: Unstated or indeterminate.

Principle: Zero hallucination, zero assuming affirmative presence from missing data.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
    cleaned = re.sub(r"[^\w\s]", " ", ascii_only.lower())
    return " ".join(cleaned.split())


# Keywords for Relevance Classification
DIRECT_RELEVANCE_PATTERNS = [
    r"\bsoftware\b",
    r"\bdeveloper\b",
    r"\bdesarrollador\b",
    r"\bdesarrolladora\b",
    r"\bengineer\b",
    r"\bingeniero\b",
    r"\bingeniera\b",
    r"\bprogramador\b",
    r"\bbackend\b",
    r"\bfrontend\b",
    r"\bfullstack\b",
    r"\bfull stack\b",
    r"\bdevops\b",
    r"\bsre\b",
    r"\bsite reliability\b",
    r"\bcloud\b",
    r"\bnube\b",
    r"\blinux\b",
    r"\bubuntu\b",
    r"\bsystems?\b",
    r"\bsistemas\b",
    r"\bqa\b",
    r"\bquality assurance\b",
    r"\bsdet\b",
    r"\btesting\b",
    r"\bsecurity\b",
    r"\bseguridad\b",
    r"\bcybersecurity\b",
    r"\bciberseguridad\b",
    r"\bdata\b",
    r"\bdatos\b",
    r"\bmachine learning\b",
    r"\bartificial intelligence\b",
    r"\bia\b",
    r"\btech support\b",
    r"\btechnical support\b",
    r"\bsoporte tecnico\b",
    r"\btechnical specialist\b",
    r"\bit support\b",
    r"\binfrastructure\b",
    r"\binfraestructura\b",
    r"\bdatabase\b",
    r"\bbase de datos\b",
    r"\bdba\b",
    r"\bkernel\b",
    r"\bdistributed systems\b",
    r"\bnetwork\b",
    r"\bredes(?!\s*sociales)\b",
    r"\barchitect\b",
    r"\barquitecto\b",
]

ADJACENT_RELEVANCE_PATTERNS = [
    r"\boperations? analyst\b",
    r"\banalista de operaciones\b",
    r"\bsupply chain analyst\b",
    r"\banalista de cadena de suministro\b",
    r"\bprocess automation\b",
    r"\bautomatizacion de procesos\b",
    r"\bbusiness intelligence\b",
    r"\bbi analyst\b",
    r"\banalista bi\b",
    r"\berp\b",
    r"\bmrp\b",
    r"\bsap\b",
    r"\bfraud\b",
    r"\bfraude\b",
    r"\bdisputes?\b",
    r"\bdisputas\b",
    r"\bchargebacks?\b",
    r"\btechnical product\b",
    r"\bproduct operations\b",
    r"\bit audit\b",
    r"\bauditoria de sistemas\b",
    r"\brisk analyst\b",
    r"\banalista de riesgo\b",
    r"\bcompliance analyst\b",
    r"\banalista de cumplimiento\b",
    r"\bafiliaciones y traspasos\b",
    r"\bcobranza\b",
]

NON_RELEVANT_PATTERNS = [
    r"\bchef\b",
    r"\bcook\b",
    r"\bcocina\b",
    r"\bculinary\b",
    r"\bkitchen\b",
    r"\bbaker\b",
    r"\bfood safety\b",
    r"\bwarehouse\b",
    r"\balmacen\b",
    r"\bdriver\b",
    r"\bchofer\b",
    r"\bretail\b",
    r"\bventas\b",
    r"\bsales\b",
    r"\baccount executive\b",
    r"\bbusiness development\b",
    r"\blegal\b",
    r"\babogad[oa]\b",
    r"\battorney\b",
    r"\bcounsel\b",
    r"\bmarketing\b",
    r"\bmercadeo\b",
    r"\bgrowth marketing\b",
    r"\bsocial media\b",
    r"\bredes sociales\b",
    r"\brecruiter\b",
    r"\breclutador\b",
    r"\btalent acquisition\b",
    r"\bhuman resources\b",
    r"\brrhh\b",
    r"\bhr generalist\b",
    r"\baccounting\b",
    r"\baccountant\b",
    r"\bcontad[oa]r\b",
    r"\btax\b",
    r"\bimpuestos\b",
    r"\bgraphic design\b",
    r"\bdiseno grafico\b",
    r"\bcopywriter\b",
    r"\bpublic relations\b",
    r"\bpr specialist\b",
    r"\bconstruction\b",
    r"\bmaintenance technician\b",
]

# Experience Tier Patterns
ENTRY_JUNIOR_PATTERNS = [
    r"\bintern\b",
    r"\binternship\b",
    r"\bpracticante\b",
    r"\bpracticas\b",
    r"\btrainee\b",
    r"\bgraduate\b",
    r"\begresad[oa]\b",
    r"\bgraduad[oa]\b",
    r"\bapprentice\b",
    r"\baprendiz\b",
    r"\bjunior\b",
    r"\bjr\b",
    r"\bentry\b",
    r"\bentry level\b",
    r"\bassociate\b",
    r"\basociad[oa]\b",
    r"\bentry[- ]level\b",
]

SENIOR_LEAD_PATTERNS = [
    r"\bsenior\b",
    r"\bsr\.?\b",
    r"\blead\b",
    r"\blider\b",
    r"\bprincipal\b",
    r"\bstaff\b",
    r"\bdirector\b",
    r"\bdirectora\b",
    r"\bhead of\b",
    r"\bjefe de\b",
    r"\bvp\b",
    r"\bvice president\b",
    r"\bvicepresidente\b",
    r"\bdistinguished\b",
    r"\bexpert\b",
]

# Geographic Patterns
PERU_LOCAL_PATTERNS = [
    r"\bperu\b",
    r"\blima\b",
    r"\barequipa\b",
    r"\btrujillo\b",
    r"\bcusco\b",
]

LATAM_PATTERNS = [
    r"\blatam\b",
    r"\blatin america\b",
    r"\bamerica latina\b",
    r"\bamericas\b",
    r"\bsouth america\b",
    r"\bsuramerica\b",
]

GLOBAL_REMOTE_PATTERNS = [
    r"\bworldwide\b",
    r"\bglobal\b",
    r"\banywhere\b",
    r"\bhome based - worldwide\b",
]


@dataclass
class ClassificationResult:
    relevance: str  # DIRECT, ADJACENT, UNDEMONSTRATED, NOT_RELEVANT
    geographic_eligibility: str  # PERU_LOCAL, PERU_REMOTE, LATAM, GLOBAL_REMOTE, NOT_ELIGIBLE, UNKNOWN
    experience_tier: str  # ENTRY_OR_JUNIOR, MID, SENIOR_OR_LEAD, UNKNOWN
    relevance_reason: str
    geography_reason: str
    experience_reason: str
    is_staging_eligible: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "relevance": self.relevance,
            "geographicEligibility": self.geographic_eligibility,
            "experienceTier": self.experience_tier,
            "relevanceReason": self.relevance_reason,
            "geographyReason": self.geography_reason,
            "experienceReason": self.experience_reason,
            "isStagingEligible": self.is_staging_eligible,
        }


def classify_candidate(
    *,
    title: str | None,
    location: str | None,
    mode: str | None,
    employer: str | None = None,
    description: str | None = None,
) -> ClassificationResult:
    norm_title = _normalize(title)
    norm_loc = _normalize(location)
    norm_mode = _normalize(mode)
    full_loc_text = f"{norm_loc} {norm_mode}".strip()

    # --- 1. CLASSIFY RELEVANCE ---
    relevance = "UNDEMONSTRATED"
    relevance_reason = "No se identificaron patrones técnicos ni de funciones afines en el título."

    # Check non-relevant first (exclusion override)
    matched_non_relevant = [p for p in NON_RELEVANT_PATTERNS if re.search(p, norm_title)]
    matched_direct = [p for p in DIRECT_RELEVANCE_PATTERNS if re.search(p, norm_title)]
    matched_adjacent = [p for p in ADJACENT_RELEVANCE_PATTERNS if re.search(p, norm_title)]

    # If title has explicit non-technical business domain words without technical role
    if matched_non_relevant and not matched_direct:
        relevance = "NOT_RELEVANT"
        relevance_reason = f"Rol perteneciente a área no técnica/administrativa/operativa general (coincidencia: {matched_non_relevant[0]})."
    elif matched_direct:
        relevance = "DIRECT"
        relevance_reason = f"Convocatoria directamente vinculada a desarrollo, ingeniería o computación (patrón: {matched_direct[0]})."
    elif matched_adjacent:
        relevance = "ADJACENT"
        relevance_reason = f"Rol de analista, soporte o automatización operativa afín a sistemas (patrón: {matched_adjacent[0]})."
    elif not norm_title:
        relevance = "UNDEMONSTRATED"
        relevance_reason = "Título no informado o vacío."

    # Special handling: if non-relevant keyword appears alongside direct (e.g., 'Engineering Recruiter')
    if matched_direct and any(re.search(p, norm_title) for p in [r"\brecruiter\b", r"\breclutador\b", r"\btalent acquisition\b", r"\bsales\b", r"\bmarketing\b", r"\bchef\b", r"\bredes sociales\b", r"\bsocial media\b"]):
        # Unless it's explicitly 'Sales Engineer' or similar, recruiter/sales takes precedence
        if "sales engineer" in norm_title or "solutions engineer" in norm_title:
            relevance = "DIRECT"
            relevance_reason = "Rol técnico de preventa / arquitectura de soluciones."
        else:
            relevance = "NOT_RELEVANT"
            relevance_reason = "Rol de reclutamiento, ventas o marketing en redes sociales, no posición técnica de sistemas."

    # --- 2. CLASSIFY GEOGRAPHIC ELIGIBILITY ---
    geo = "UNKNOWN"
    geo_reason = "Ubicación no especificada o indeterminada."

    is_remote = any(k in full_loc_text for k in ("remoto", "remote", "home based", "virtual"))

    if any(re.search(p, full_loc_text) for p in PERU_LOCAL_PATTERNS):
        if is_remote or "remote" in norm_loc:
            geo = "PERU_REMOTE"
            geo_reason = "Ubicación explícitamente remota con sede o elegibilidad en Perú."
        else:
            geo = "PERU_LOCAL"
            geo_reason = "Sede u oficina presencial o híbrida situada en Perú."
    elif any(re.search(p, full_loc_text) for p in GLOBAL_REMOTE_PATTERNS):
        geo = "GLOBAL_REMOTE"
        geo_reason = "Modalidad remota a nivel mundial / global (elegible para Perú)."
    elif any(re.search(p, full_loc_text) for p in LATAM_PATTERNS):
        geo = "LATAM"
        geo_reason = "Modalidad remota a nivel regional (América Latina / Américas), elegible desde Perú."
    elif full_loc_text:
        # Non-Peru location check (e.g. United States, Minneapolis, Poland, China, Germany, Chile onsite, Mexico onsite)
        foreign_countries = [
            "united states", "usa", "us", "canada", "france", "germany", "poland", "india",
            "netherlands", "serbia", "turkiye", "turkey", "spain", "china", "taiwan",
            "shenzhen", "beijing", "taipei", "london", "uk", "toronto", "atlanta",
            "austin", "chicago", "hyattsville", "savage", "seattle", "new york", "miami",
            "chile", "mexico", "santiago", "sao paulo", "brasil", "brazil", "bogota", "colombia", "argentina"
        ]
        has_foreign = any(fc in full_loc_text for fc in foreign_countries)
        if has_foreign and not is_remote:
            geo = "NOT_ELIGIBLE"
            geo_reason = f"Convocatoria presencial/híbrida restringida a sede extranjera ({location})."
        elif has_foreign and is_remote:
            # Foreign country with remote (e.g. 'Argentina, Remote', 'Poland, Remote')
            geo = "NOT_ELIGIBLE"
            geo_reason = f"Posición remota restringida por país a jurisdicción distinta de Perú ({location})."
        else:
            geo = "UNKNOWN"
            geo_reason = f"Ubicación no concluyente para determinar elegibilidad en Perú ({location})."

    # --- 3. CLASSIFY EXPERIENCE TIER ---
    exp_tier = "UNKNOWN"
    exp_reason = "No se especificó nivel de experiencia en el título."

    matched_entry = [p for p in ENTRY_JUNIOR_PATTERNS if re.search(p, norm_title)]
    matched_senior = [p for p in SENIOR_LEAD_PATTERNS if re.search(p, norm_title)]

    if matched_entry and not matched_senior:
        exp_tier = "ENTRY_OR_JUNIOR"
        exp_reason = f"Título contiene identificador de nivel formativo o inicial (patrón: {matched_entry[0]})."
    elif matched_senior and not matched_entry:
        exp_tier = "SENIOR_OR_LEAD"
        exp_reason = f"Título contiene identificador de nivel senior o de liderazgo (patrón: {matched_senior[0]})."
    elif matched_entry and matched_senior:
        # E.g. "Lead Intern Coordinator" or ambiguous
        exp_tier = "UNKNOWN"
        exp_reason = "Título contiene términos contradictorios de nivel formativo y liderazgo."
    elif relevance in ("DIRECT", "ADJACENT"):
        exp_tier = "MID"
        exp_reason = "Puesto profesional estándar sin prefijos restrictivos de nivel senior ni junior."

    # --- 4. OVERALL STAGING ELIGIBILITY ---
    # To be staged into inbox, an opportunity must be DIRECT or ADJACENT,
    # and its geography must be potentially eligible (PERU_LOCAL, PERU_REMOTE, LATAM, GLOBAL_REMOTE).
    # Senior positions are recorded and staged with their explicit tier so the owner can review them.
    # NOT_RELEVANT roles (cooks, kitchen, sales, drivers) or NOT_ELIGIBLE geographics (Beijing office, Poland remote)
    # are filtered out with explicit reasons.
    is_eligible = (
        relevance in ("DIRECT", "ADJACENT")
        and geo in ("PERU_LOCAL", "PERU_REMOTE", "LATAM", "GLOBAL_REMOTE")
    )

    return ClassificationResult(
        relevance=relevance,
        geographic_eligibility=geo,
        experience_tier=exp_tier,
        relevance_reason=relevance_reason,
        geography_reason=geo_reason,
        experience_reason=exp_reason,
        is_staging_eligible=is_eligible,
    )
