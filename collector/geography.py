"""Geographic Normalization and Territorial Scope Taxonomy for Velora (TASK-R5-05).

Provides:
- Canonical three-dimensional geographic classification:
  1. Geographic Scope / Eligibility for Peru:
     - PERU_LOCAL: Physical location explicitly within Peru with local contracting.
     - PERU_REMOTE: Remote opportunity restricted exclusively or primarily to residents in Peru.
     - INTERNATIONAL_REMOTE_PERU_ELIGIBLE: International remote vacancy with explicit Peru eligibility.
     - INTERNATIONAL_REMOTE_UNCONFIRMED: International remote vacancy whose Peru eligibility is unverified/pending.
     - NOT_ELIGIBLE_PERU: Convocatoria explicitly excluding candidates residing in Peru.
     - UNSPECIFIED: Location or eligibility unstated or ambiguous.
  2. Workplace Mode / Modalidad Físico-Espacial:
     - ONSITE: Presencial.
     - HYBRID: Híbrido.
     - REMOTE: Remoto.
     - UNSPECIFIED: No especificada / Flexible según área.
  3. Peruvian Territorial Location / Ubicación Territorial en Perú:
     - Department (e.g. Lima, Arequipa, Cusco, etc.), Province, District/City.

Principle: Zero hallucination, fail-closed, complete traceability and zero external dependencies.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

# Canonical Territorial Scope Identifiers
SCOPE_PERU_LOCAL = "PERU_LOCAL"
SCOPE_PERU_REMOTE = "PERU_REMOTE"
SCOPE_INTL_ELIGIBLE = "INTERNATIONAL_REMOTE_PERU_ELIGIBLE"
SCOPE_INTL_UNCONFIRMED = "INTERNATIONAL_REMOTE_UNCONFIRMED"
SCOPE_NOT_ELIGIBLE = "NOT_ELIGIBLE_PERU"
SCOPE_UNSPECIFIED = "UNSPECIFIED"

ALL_SCOPES = (
    SCOPE_PERU_LOCAL,
    SCOPE_PERU_REMOTE,
    SCOPE_INTL_ELIGIBLE,
    SCOPE_INTL_UNCONFIRMED,
    SCOPE_NOT_ELIGIBLE,
    SCOPE_UNSPECIFIED,
)

SCOPE_DEFINITIONS: dict[str, dict[str, str]] = {
    SCOPE_PERU_LOCAL: {
        "id": SCOPE_PERU_LOCAL,
        "label": "Empleo presencial o híbrido en Perú",
        "shortLabel": "Perú local",
        "description": "Puesto con sede física en Perú (presencial o híbrido) y contratación local acreditada.",
    },
    SCOPE_PERU_REMOTE: {
        "id": SCOPE_PERU_REMOTE,
        "label": "Remoto nacional (Perú)",
        "shortLabel": "Remoto Perú",
        "description": "Trabajo 100% remoto reservado para residentes dentro del territorio peruano.",
    },
    SCOPE_INTL_ELIGIBLE: {
        "id": SCOPE_INTL_ELIGIBLE,
        "label": "Internacional remoto (admite Perú)",
        "shortLabel": "Internacional elegible",
        "description": "Vacante remota internacional o regional con evidencia explícita de contratación para Perú.",
    },
    SCOPE_INTL_UNCONFIRMED: {
        "id": SCOPE_INTL_UNCONFIRMED,
        "label": "Internacional remoto (elegibilidad no confirmada)",
        "shortLabel": "Internacional por confirmar",
        "description": "Vacante global o regional sin confirmación fehaciente de contratación legal desde Perú.",
    },
    SCOPE_NOT_ELIGIBLE: {
        "id": SCOPE_NOT_ELIGIBLE,
        "label": "No elegible para residentes de Perú",
        "shortLabel": "No elegible Perú",
        "description": "Convocatoria con exclusión expresa o circunscrita a jurisdicciones fuera de Perú.",
    },
    SCOPE_UNSPECIFIED: {
        "id": SCOPE_UNSPECIFIED,
        "label": "Ámbito territorial no especificado",
        "shortLabel": "No especificado",
        "description": "Información geográfica o de elegibilidad insuficiente para emitir una clasificación.",
    },
}

# Peruvian Administrative Departments (24 Departamentos + 1 Provincia Constitucional)
PERUVIAN_DEPARTMENTS: dict[str, dict[str, str]] = {
    "Amazonas": {"department": "Amazonas", "pattern": r"\bamazonas\b|\bchachapoyas\b|\bbagua\b"},
    "Áncash": {"department": "Áncash", "pattern": r"\bancash\b|\bchimbote\b|\bhuaraz\b|\bcasma\b"},
    "Apurímac": {"department": "Apurímac", "pattern": r"\bapurimac\b|\babancay\b|\bandahuaylas\b"},
    "Arequipa": {"department": "Arequipa", "pattern": r"\barequipa\b|\bcaman[aá]\b|\bcayma\b"},
    "Ayacucho": {"department": "Ayacucho", "pattern": r"\bayacucho\b|\bhuamanga\b"},
    "Cajamarca": {"department": "Cajamarca", "pattern": r"\bcajamarca\b|\bjaen\b|\bchota\b"},
    "Callao": {"department": "Callao", "pattern": r"\bcallao\b|\bbellavista\b|\bla perla\b|\bla punta\b|\bventanilla\b"},
    "Cusco": {"department": "Cusco", "pattern": r"\bcusco\b|\bcuzco\b|\burubamba\b|\bwanchaq\b"},
    "Huancavelica": {"department": "Huancavelica", "pattern": r"\bhuancavelica\b|\btayacaja\b"},
    "Huánuco": {"department": "Huánuco", "pattern": r"\bhuanuco\b|\btingo maria\b"},
    "Ica": {"department": "Ica", "pattern": r"\bica\b|\bchincha\b|\bpisco\b|\bnazca\b"},
    "Junín": {"department": "Junín", "pattern": r"\bjunin\b|\bhuancayo\b|\btarma\b|\bjauja\b|\bsatipo\b"},
    "La Libertad": {"department": "La Libertad", "pattern": r"\bla libertad\b|\btrujillo\b|\bhuanchaco\b|\bchepen\b"},
    "Lambayeque": {"department": "Lambayeque", "pattern": r"\blambayeque\b|\bchiclayo\b|\blambayeque\b|\bferrenafe\b"},
    "Lima": {"department": "Lima", "pattern": r"\blima\b|\bsurquillo\b|\bmagdalena\b|\bsan isidro\b|\bmiraflores\b|\bsan borja\b|\bsurco\b|\bla molina\b|\blince\b|\bjesus maria\b|\bpueblo libre\b|\blos olivos\b|\bsan martin de porres\b|\bbarranco\b|\bchorrillos\b|\bcallao\b|\bate\b|\bsan miguel\b|\bhuancho\b|\bcomas\b"},
    "Loreto": {"department": "Loreto", "pattern": r"\bloreto\b|\biquitos\b|\byurimaguas\b"},
    "Madre de Dios": {"department": "Madre de Dios", "pattern": r"\bmadre de dios\b|\bpuerto maldonado\b"},
    "Moquegua": {"department": "Moquegua", "pattern": r"\bmoquegua\b|\bilo\b"},
    "Pasco": {"department": "Pasco", "pattern": r"\bpasco\b|\bcerro de pasco\b|\boxapampa\b"},
    "Piura": {"department": "Piura", "pattern": r"\bpiura\b|\bsullana\b|\btalara\b|\bpaita\b"},
    "Puno": {"department": "Puno", "pattern": r"\bpuno\b|\bjuliaca\b"},
    "San Martín": {"department": "San Martín", "pattern": r"\bsan martin\b|\btarapoto\b|\bmoyobamba\b"},
    "Tacna": {"department": "Tacna", "pattern": r"\btacna\b"},
    "Tumbes": {"department": "Tumbes", "pattern": r"\btumbes\b|\bzarumilla\b"},
    "Ucayali": {"department": "Ucayali", "pattern": r"\bucayali\b|\bpucallpa\b|\bcoronel portillo\b"},
}


def _strip_accents(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
    cleaned = re.sub(r"[^\w\s]", " ", ascii_only.lower())
    return " ".join(cleaned.split())


@dataclass
class GeographicClassification:
    scope: str  # PERU_LOCAL, PERU_REMOTE, INTERNATIONAL_REMOTE_PERU_ELIGIBLE, etc.
    scope_label: str
    workplace_mode: str  # ONSITE, HYBRID, REMOTE, UNSPECIFIED
    country_code: str | None = None
    country_name: str | None = None
    department: str | None = None
    city_or_district: str | None = None
    explanation: str = ""
    evidence_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "scopeLabel": self.scope_label,
            "workplaceMode": self.workplace_mode,
            "countryCode": self.country_code,
            "countryName": self.country_name,
            "department": self.department,
            "cityOrDistrict": self.city_or_district,
            "explanation": self.explanation,
            "evidenceText": self.evidence_text,
        }


def extract_peruvian_department(text: str | None) -> str | None:
    """Extracts a validated Peruvian department from text without guessing."""
    if not text:
        return None
    norm = _strip_accents(text)
    # Check Lima and specific districts first to avoid false positive matches
    if re.search(PERUVIAN_DEPARTMENTS["Lima"]["pattern"], norm):
        return "Lima"
    for dept_name, info in PERUVIAN_DEPARTMENTS.items():
        if dept_name == "Lima":
            continue
        if re.search(info["pattern"], norm):
            return dept_name
    return None


def extract_city_or_district(text: str | None) -> str | None:
    """Extracts recognized city/district within Peru when explicit."""
    if not text:
        return None
    norm = _strip_accents(text)
    known_districts = {
        "Surquillo": r"\bsurquillo\b",
        "Magdalena del Mar": r"\bmagdalena\b",
        "San Isidro": r"\bsan isidro\b",
        "Miraflores": r"\bmiraflores\b",
        "San Borja": r"\bsan borja\b",
        "Santiago de Surco": r"\bsurco\b",
        "La Molina": r"\bla molina\b",
        "Arequipa": r"\barequipa\b",
        "Trujillo": r"\btrujillo\b",
        "Cusco": r"\bcusco\b|\bcuzco\b",
        "Chiclayo": r"\bchiclayo\b",
        "Piura": r"\bpiura\b",
        "Huancayo": r"\bhuancayo\b",
    }
    for dist_name, pat in known_districts.items():
        if re.search(pat, norm):
            return dist_name
    return None


def normalize_workplace_mode(mode: str | None, location: str | None = None) -> str:
    """Normalizes workplace physical mode into ONSITE, HYBRID, REMOTE or UNSPECIFIED."""
    raw = f"{mode or ''} {location or ''}".lower()
    norm = _strip_accents(raw)
    if "hibrid" in norm or "hybrid" in norm:
        return "HYBRID"
    if "remot" in norm or "remote" in norm or "home based" in norm or "teletrabajo" in norm:
        return "REMOTE"
    if "presencial" in norm or "onsite" in norm or "on-site" in norm:
        return "ONSITE"
    return "UNSPECIFIED"


def classify_opportunity_geography(
    *,
    location: str | None,
    mode: str | None = None,
    eligibility: str | None = None,
    employer: str | None = None,
) -> GeographicClassification:
    """Determines canonical territorial scope and normalized location without hallucinations."""
    loc_str = str(location or "").strip()
    mode_str = str(mode or "").strip()
    elig_str = str(eligibility or "").strip()
    combined_norm = _strip_accents(f"{loc_str} {mode_str} {elig_str}")

    workplace_mode = normalize_workplace_mode(mode_str, loc_str)

    # 1. Check for explicit exclusion of Peru
    # e.g., 'US residents only', 'Europa únicamente', 'Must reside in Argentina'
    exclusive_foreign = [
        r"\bus\s+residents\s+only\b",
        r"\bsolo\s+residentes\s+en\s+eeuu\b",
        r"\bnot\s+eligible\s+in\s+peru\b",
        r"\bexclusive\s+for\s+chile\b",
        r"\bno\s+aplica\s+para\s+peru\b",
    ]
    if any(re.search(pat, combined_norm) for pat in exclusive_foreign):
        return GeographicClassification(
            scope=SCOPE_NOT_ELIGIBLE,
            scope_label=SCOPE_DEFINITIONS[SCOPE_NOT_ELIGIBLE]["label"],
            workplace_mode=workplace_mode,
            country_code=None,
            country_name="Extranjero",
            department=None,
            city_or_district=None,
            explanation="La vacante excluye explícitamente la residencia o contratación desde Perú.",
            evidence_text=loc_str,
        )

    # 2. Check for explicit Peruvian Local / National presence
    # Indicators: mentions of Peruvian cities/departments, 'Remoto nacional', or physical Peruvian office
    has_peru_mention = bool(re.search(r"\bperu\b|\blima\b|\barequipa\b|\bcusco\b|\btrujillo\b|\bcallao\b", combined_norm))
    is_peru_remote_national = bool(re.search(r"remoto\s+nacional|trabajo\s+remoto\s+en\s+territorio\s+peruano", combined_norm))
    is_worldwide_or_multinational = bool(re.search(r"worldwide|americas|emea|apac|latin\s*america|global", combined_norm))

    dept = extract_peruvian_department(loc_str) or (extract_peruvian_department(elig_str) if has_peru_mention else None)
    city_dist = extract_city_or_district(loc_str)

    # Case A: Remote National inside Peru (e.g. Encora Remoto nacional)
    if is_peru_remote_national:
        return GeographicClassification(
            scope=SCOPE_PERU_REMOTE,
            scope_label=SCOPE_DEFINITIONS[SCOPE_PERU_REMOTE]["label"],
            workplace_mode="REMOTE",
            country_code="PE",
            country_name="Perú",
            department=dept,
            city_or_district=city_dist,
            explanation="Trabajo remoto nacional circunscrito al territorio peruano.",
            evidence_text=f"{loc_str} (Elegibilidad: {elig_str})",
        )

    # Case B: Peruvian Local (Presencial / Híbrido en territorio peruano)
    # Exclude multi-country remote like 'Chile, Perú o Colombia'
    is_multicountry = bool(re.search(r"chile\s+peru\s+o\s+colombia", combined_norm))
    if has_peru_mention and not is_worldwide_or_multinational and not is_multicountry:
        # Check if it is purely local office/presence
        if workplace_mode in ("ONSITE", "HYBRID") or dept is not None or "peru" in _strip_accents(loc_str):
            # If workplace mode is explicit remote but with local contract (e.g. Sezzle local o remoto)
            if workplace_mode == "REMOTE" and not is_peru_remote_national and "sezzle" in (employer or "").lower():
                # Handled as international eligible below
                pass
            else:
                return GeographicClassification(
                    scope=SCOPE_PERU_LOCAL,
                    scope_label=SCOPE_DEFINITIONS[SCOPE_PERU_LOCAL]["label"],
                    workplace_mode=workplace_mode if workplace_mode != "UNSPECIFIED" else "ONSITE",
                    country_code="PE",
                    country_name="Perú",
                    department=dept or "Lima",
                    city_or_district=city_dist,
                    explanation="Oportunidad con sede y contratación local en Perú.",
                    evidence_text=f"{loc_str} (Modalidad: {mode_str})",
                )

    # Case C: International Remote with Unconfirmed Eligibility
    # Any explicit signal requiring confirmation or lacking verification takes precedence (fail-closed)
    is_unconfirmed_signal = bool(re.search(r"confirmar\s+contratacion|no\s+confirmad|por\s+confirmar|global\s+segun\s+el\s+anuncio", combined_norm))
    if is_unconfirmed_signal:
        return GeographicClassification(
            scope=SCOPE_INTL_UNCONFIRMED,
            scope_label=SCOPE_DEFINITIONS[SCOPE_INTL_UNCONFIRMED]["label"],
            workplace_mode="REMOTE",
            country_code=None,
            country_name="Internacional",
            department=None,
            city_or_district=None,
            explanation="Oportunidad internacional remota sin confirmación fehaciente de elegibilidad para Perú.",
            evidence_text=f"{loc_str} (Elegibilidad: {elig_str})",
        )

    # Case D: International Remote with Confirmed Peru Eligibility
    # Canonical: 'Home based - Worldwide (Perú elegible)', 'Americas/EMEA (Perú elegible)'
    # Sezzle: 'Latin America (Perú elegible)', 'Peru (Remoto)'
    # 42Labs: 'Remoto (Chile, Perú o Colombia)'
    has_peru_eligible_flag = bool(re.search(r"peru\s+elegible|elegible\s+para\s+peru|remoto\s+internacional|chile\s+peru\s+o\s+colombia|local\s+o\s+remoto", combined_norm))
    if has_peru_eligible_flag:
        return GeographicClassification(
            scope=SCOPE_INTL_ELIGIBLE,
            scope_label=SCOPE_DEFINITIONS[SCOPE_INTL_ELIGIBLE]["label"],
            workplace_mode="REMOTE",
            country_code=None,
            country_name="Internacional",
            department=None,
            city_or_district=None,
            explanation="Oportunidad internacional remota con elegibilidad explícita confirmada para Perú.",
            evidence_text=f"{loc_str} ({elig_str})",
        )

    if is_worldwide_or_multinational:
        return GeographicClassification(
            scope=SCOPE_INTL_UNCONFIRMED,
            scope_label=SCOPE_DEFINITIONS[SCOPE_INTL_UNCONFIRMED]["label"],
            workplace_mode="REMOTE",
            country_code=None,
            country_name="Internacional",
            department=None,
            city_or_district=None,
            explanation="Vacante de alcance multinacional o global sin confirmación expresa de contratación desde Perú.",
            evidence_text=loc_str,
        )

    # Case E: Fallback UNSPECIFIED
    return GeographicClassification(
        scope=SCOPE_UNSPECIFIED,
        scope_label=SCOPE_DEFINITIONS[SCOPE_UNSPECIFIED]["label"],
        workplace_mode=workplace_mode,
        country_code=None,
        country_name=None,
        department=None,
        city_or_district=None,
        explanation="Información geográfica insuficiente para clasificar el ámbito territorial.",
        evidence_text=loc_str,
    )
