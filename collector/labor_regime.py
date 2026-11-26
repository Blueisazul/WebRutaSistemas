"""Peruvian Labor and Contractual Regimes Taxonomy and Normalization (TASK-R7-01).

Provides:
- Canonical taxonomy of Peruvian labor and contractual regimes:
  * PRE_PROFESSIONAL_INTERNSHIP (Prácticas preprofesionales - Ley 28518)
  * PROFESSIONAL_INTERNSHIP (Prácticas profesionales - Ley 28518 / Ley 31396)
  * CAS (Contratación Administrativa de Servicios - D. Leg. 1057 / Ley 29849 / Ley 31131)
  * LABOR_REGIME_728 (Régimen laboral de la actividad privada - D. Leg. 728 / D.S. 003-97-TR)
  * CIVIL_SERVICES (Locación de servicios / honorarios civiles - Código Civil art. 1764)
  * OTHER (Otras modalidades: B2B internacional, regímenes especiales D. Leg. 276, etc.)
  * UNSPECIFIED (Modalidad no especificada o pendiente de clasificación)
- Deterministic, fail-closed classification from opportunity fields.
- Rigorous legal framework backing from official Peruvian sources (MTPE, SERVIR, El Peruano).
- Level of certainty tracking (EXPLICIT_EVIDENCE, DERIVED_BASES, UNSPECIFIED).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

# Canonical regime identifiers
REGIME_PRE_PROFESSIONAL = "PRE_PROFESSIONAL_INTERNSHIP"
REGIME_PROFESSIONAL = "PROFESSIONAL_INTERNSHIP"
REGIME_CAS = "CAS"
REGIME_728 = "LABOR_REGIME_728"
REGIME_CIVIL = "CIVIL_SERVICES"
REGIME_OTHER = "OTHER"
REGIME_UNSPECIFIED = "UNSPECIFIED"

ALL_REGIMES = (
    REGIME_PRE_PROFESSIONAL,
    REGIME_PROFESSIONAL,
    REGIME_CAS,
    REGIME_728,
    REGIME_CIVIL,
    REGIME_OTHER,
    REGIME_UNSPECIFIED,
)

# Certainty levels
CERTAINTY_EXPLICIT = "EXPLICIT_EVIDENCE"
CERTAINTY_DERIVED = "DERIVED_BASES"
CERTAINTY_UNSPECIFIED = "UNSPECIFIED"

ALL_CERTAINTIES = (
    CERTAINTY_EXPLICIT,
    CERTAINTY_DERIVED,
    CERTAINTY_UNSPECIFIED,
)

# Detailed normative regime definitions backed by official Peruvian sources
REGIME_DEFINITIONS: dict[str, dict[str, Any]] = {
    REGIME_PRE_PROFESSIONAL: {
        "id": REGIME_PRE_PROFESSIONAL,
        "label": "Prácticas preprofesionales",
        "shortLabel": "Prácticas pre",
        "badgeColor": "violet",
        "category": "FORMATIVE",
        "legalFramework": "Ley N° 28518 (arts. 12-14) y D.S. N° 007-2005-TR (MTPE)",
        "officialSourceUrl": "https://www.gob.pe/institucion/mtpe/normativas/200466-28518",
        "nature": "Modalidad formativa especial para estudiantes de educación superior universitaria o técnica. Se formaliza mediante Convenio de Aprendizaje suscrito entre el estudiante, el centro de formación y la empresa o entidad.",
        "maxWorkingHours": "6 horas diarias o 30 horas semanales",
        "compensation": "Subvención económica mensual no menor a una Remuneración Mínima Vital (RMV, S/ 1,025) cuando se cumple la jornada máxima permitida.",
        "keyRights": [
            "Convenio tripartito (estudiante, centro de estudios, empresa/entidad).",
            "Jornada máxima de 6 horas diarias (30 semanales).",
            "Subvención mensual no menor a 1 RMV (para jornada máxima).",
            "Media subvención económica adicional cada 6 meses continuos.",
            "Descanso semanal obligatorio de 24 horas consecutivas.",
            "Cobertura de salud mediante ESSALUD o seguro privado (cobertura médica al 100%).",
            "Certificado de prácticas preprofesionales emitido por la entidad.",
        ],
        "cautions": "No constituye relación laboral de subordinación; no genera CTS, gratificaciones legales de julio/diciembre ni asignación familiar.",
    },
    REGIME_PROFESSIONAL: {
        "id": REGIME_PROFESSIONAL,
        "label": "Prácticas profesionales",
        "shortLabel": "Prácticas pro",
        "badgeColor": "cyan",
        "category": "FORMATIVE",
        "legalFramework": "Ley N° 28518 (arts. 15-18), Ley N° 31396 y D.S. N° 007-2005-TR (MTPE)",
        "officialSourceUrl": "https://www.gob.pe/institucion/mtpe/normativas/200466-28518",
        "nature": "Modalidad formativa para egresados o bachilleres antes de la obtención del título profesional. Duración máxima legal de 12 meses (o hasta 24 meses si lo establece el plan curricular). Se reconoce como experiencia laboral en el sector público y privado (Ley N° 31396).",
        "maxWorkingHours": "8 horas diarias o 48 horas semanales",
        "compensation": "Subvención económica mensual no menor a una Remuneración Mínima Vital (RMV, S/ 1,025) para jornada completa.",
        "keyRights": [
            "Convenio bipartito o tripartito para egresados y bachilleres.",
            "Reconocimiento legal obligatorio como experiencia laboral (Ley N° 31396).",
            "Jornada máxima de 8 horas diarias (48 semanales).",
            "Subvención mensual no menor a 1 RMV.",
            "Media subvención económica adicional por cada 6 meses continuos de prácticas.",
            "15 días calendario de descanso subvencionado tras 12 meses de duración continua.",
            "Cobertura de salud ESSALUD o seguro médico privado.",
            "Certificado formal de prácticas profesionales emitido al culminar.",
        ],
        "cautions": "Modalidad de aprendizaje formativo; no genera CTS ni gratificaciones legales del régimen laboral común.",
    },
    REGIME_CAS: {
        "id": REGIME_CAS,
        "label": "Contratación Administrativa de Servicios (CAS)",
        "shortLabel": "CAS (D.L. 1057)",
        "badgeColor": "indigo",
        "category": "LABOR_PUBLIC",
        "legalFramework": "Decreto Legislativo N° 1057, D.S. N° 075-2008-PCM, Ley N° 29849 y Ley N° 31131 (SERVIR)",
        "officialSourceUrl": "https://www.gob.pe/institucion/servir/normativas/1085023-decreto-legislativo-n-1057",
        "nature": "Régimen especial de contratación laboral privativo del Estado peruano. Se formaliza mediante contrato administrativo de servicios por concurso público de méritos, sujeto a disponibilidad presupuestal institucional.",
        "maxWorkingHours": "8 horas diarias o 48 horas semanales",
        "compensation": "Remuneración convenida no menor a la RMV, fijada en las bases del concurso público.",
        "keyRights": [
            "Contrato laboral estatal bajo el régimen especial del D. Leg. N° 1057.",
            "Jornada máxima legal de 8 horas diarias o 48 semanales.",
            "Remuneración mensual no menor a una RMV.",
            "30 días calendario de vacaciones remuneradas al año.",
            "Afiliación obligatoria a la seguridad social en salud (ESSALUD).",
            "Afiliación previsional (ONP o AFP según elección del trabajador).",
            "Aguinaldo por Fiestas Patrias y Navidad según monto fijado en la Ley de Presupuesto del Sector Público.",
            "Licencias por maternidad, paternidad y enfermedad conforme a ley.",
        ],
        "cautions": "Régimen especial público que no genera CTS ni las gratificaciones completas de julio y diciembre de la actividad privada (percibe aguinaldo estatal fijado anualmente por Ley de Presupuesto).",
    },
    REGIME_728: {
        "id": REGIME_728,
        "label": "Régimen laboral privado (D. Leg. 728)",
        "shortLabel": "Régimen 728",
        "badgeColor": "emerald",
        "category": "LABOR_PRIVATE",
        "legalFramework": "TUO del D. Leg. N° 728 (D.S. N° 003-97-TR), Ley N° 27735 (Gratificaciones) y Ley N° 25129",
        "officialSourceUrl": "https://www.gob.pe/institucion/mtpe/normativas/200453-003-97-tr",
        "nature": "Contrato de trabajo subordinado de la actividad privada (aplicable en empresas privadas y en empresas del Estado o entidades públicas bajo régimen 728). Puede ser a plazo indeterminado o sujeto a modalidad (plazo fijo).",
        "maxWorkingHours": "8 horas diarias o 48 horas semanales",
        "compensation": "Remuneración pactada en contrato, no menor a la RMV.",
        "keyRights": [
            "Contrato de trabajo con relación de dependencia y subordinación (planilla).",
            "Jornada máxima de 8 horas diarias o 48 semanales.",
            "Compensación por Tiempo de Servicios (CTS) depositada semestralmente (mayo y noviembre).",
            "Dos gratificaciones legales completas al año (julio y diciembre) equivalentes a un sueldo mensual cada una más bonificación extraordinaria (Ley N° 27735).",
            "Asignación familiar del 10% de la RMV para trabajadores con hijos dependientes (Ley N° 25129).",
            "30 días de vacaciones pagadas anuales.",
            "Aportes de salud a cargo del empleador (ESSALUD 9%).",
            "Seguro de Vida Ley desde el inicio de la relación laboral.",
        ],
        "cautions": "Si el contrato es sujeto a modalidad (plazo fijo), debe cumplir con la causa objetiva de contratación prevista en la ley para evitar desnaturalización.",
    },
    REGIME_CIVIL: {
        "id": REGIME_CIVIL,
        "label": "Locación de servicios / Honorarios",
        "shortLabel": "Locación de servicios",
        "badgeColor": "amber",
        "category": "CIVIL",
        "legalFramework": "Código Civil del Perú (artículos 1764 a 1770)",
        "officialSourceUrl": "https://www.gob.pe/institucion/minjus/normativas/238965-codigo-civil",
        "nature": "Contratación civil autónoma entre partes independientes para la prestación de servicios materiales o intelectuales a cambio de una retribución. Se emiten Recibos por Honorarios (Rentas de Cuarta Categoría).",
        "maxWorkingHours": "No sujeta a jornada laboral ni control de asistencia (prestación autónoma)",
        "compensation": "Retribución por honorarios según entregables y términos contractuales acordados.",
        "keyRights": [
            "Autonomía técnica y operativa en la ejecución del servicio.",
            "Ausencia de jornada obligatoria o subordinación laboral.",
            "Retribución económica pactada contractualmente por producto o servicio.",
            "Emisión de Recibo por Honorarios electrónico (RUC / 4ta categoría SUNAT).",
        ],
        "cautions": "Contrato civil sin vínculo laboral. No genera derecho a remuneración mínima, CTS, gratificaciones, vacaciones, asignación familiar ni seguro médico a cargo del contratante. La imposición de horario y subordinación constituye desnaturalización contractual.",
    },
    REGIME_OTHER: {
        "id": REGIME_OTHER,
        "label": "Otra modalidad contractual",
        "shortLabel": "Otra modalidad",
        "badgeColor": "slate",
        "category": "OTHER",
        "legalFramework": "Normativa contractual específica según jurisdicción o régimen especial aplicable",
        "officialSourceUrl": "https://www.gob.pe",
        "nature": "Modalidades contractuales no comprendidas en los regímenes principales peruanos (ej. contrato internacional mercantil B2B para teletrabajo transfronterizo, contratos del régimen de carrera administrativa D. Leg. 276 o convenios específicos).",
        "maxWorkingHours": "Según términos acordados en la convocatoria o contrato",
        "compensation": "Según oferta publicada o contrato suscrito.",
        "keyRights": [
            "Términos y condiciones pactados formalmente entre las partes.",
        ],
        "cautions": "Revisar detalladamente las bases o términos de contratación para conocer la ley aplicable y jurisdicción.",
    },
    REGIME_UNSPECIFIED: {
        "id": REGIME_UNSPECIFIED,
        "label": "Modalidad no especificada",
        "shortLabel": "No especificada",
        "badgeColor": "slate",
        "category": "UNSPECIFIED",
        "legalFramework": "Pendiente de especificación por la entidad convocante",
        "officialSourceUrl": "https://www.gob.pe",
        "nature": "Oportunidades donde la publicación oficial del empleador no declara explícitamente el régimen contractual o este se encuentra en proceso de revisión.",
        "maxWorkingHours": "No especificada en el aviso público",
        "compensation": "Consultar bases o publicación original.",
        "keyRights": [
            "La modalidad aplicable debe verificarse directamente en las bases o contrato formal del empleador.",
        ],
        "cautions": "No asumir condiciones ni derechos laborales anticipados hasta revisar el contrato formal o las bases completas del puesto.",
    },
}


def _strip_accents(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


@dataclass(frozen=True)
class LaborRegimeClassification:
    """Immutable classification result for an opportunity's labor regime."""

    regime_id: str
    label: str
    short_label: str
    certainty: str
    legal_framework: str
    explanation: str
    matched_term: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_labor_regime(record: dict[str, Any]) -> LaborRegimeClassification:
    """Determines the labor and contractual regime of an opportunity deterministically.

    Inspects available structured and unstructured fields with conservative fail-closed logic:
    1. Direct explicit indicators (contractType, opportunityType, requisition prefixes).
    2. Modality/kind declarations (Prácticas preprofesionales, Prácticas profesionales).
    3. Contextual title/duration/bases declarations.
    4. Conservative fallback to UNSPECIFIED (no blind assumptions).
    """
    contract_type = str(record.get("contractType") or "").strip()
    opp_type = str(record.get("opportunityType") or "").strip()
    kind = str(record.get("kind") or "").strip()
    level = str(record.get("level") or "").strip()
    title = str(record.get("title") or "").strip()
    requisition = str(record.get("requisition") or record.get("externalReference") or "").strip()
    duration = str(record.get("duration") or "").strip()
    tasks = str(record.get("tasks") or "").strip()
    requirements = str(record.get("requirements") or "").strip()
    benefits = str(record.get("benefits") or "").strip()
    employer = str(record.get("employer") or "").strip()
    sector = str(record.get("sector") or "").strip()

    # Pre-normalize search texts
    norm_ct = _strip_accents(contract_type)
    norm_ot = _strip_accents(opp_type)
    norm_kind = _strip_accents(kind)
    norm_title = _strip_accents(title)
    norm_req = _strip_accents(requisition)
    norm_dur = _strip_accents(duration)
    norm_emp = _strip_accents(employer)
    norm_tasks = _strip_accents(tasks)
    norm_reqs = _strip_accents(requirements)
    norm_bene = _strip_accents(benefits)

    combined_explicit = f"{norm_ct} | {norm_ot} | {norm_req}"
    combined_all = f"{norm_ct} | {norm_ot} | {norm_kind} | {norm_title} | {norm_req} | {norm_dur} | {norm_tasks} | {norm_reqs} | {norm_bene}"

    # -------------------------------------------------------------------------
    # 1. CAS: Contratación Administrativa de Servicios (D. Leg. 1057)
    # -------------------------------------------------------------------------
    cas_explicit_patterns = [
        r"\bcas\b",
        r"\bd\.?\s*leg\.?\s*(?:n[°oº]?\s*)?1057\b",
        r"\bdecreto\s+legislativo\s*(?:n[°oº]?\s*)?1057\b",
        r"\bcontratacion\s+administrativa\s+de\s+servicios\b",
        r"\bcontrato\s+administrativo\s+de\s+servicios\b",
        r"\bconvocatoria\s+cas\b",
        r"\bproceso\s+cas\b",
    ]
    for pat in cas_explicit_patterns:
        if re.search(pat, combined_explicit):
            defn = REGIME_DEFINITIONS[REGIME_CAS]
            return LaborRegimeClassification(
                regime_id=REGIME_CAS,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=CERTAINTY_EXPLICIT,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como CAS por mención explícita del régimen, código CAS o D. Leg. 1057 en la convocatoria.",
                matched_term=pat,
            )

    # Contextual CAS in title/duration/bases
    for pat in cas_explicit_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_CAS]
            return LaborRegimeClassification(
                regime_id=REGIME_CAS,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=CERTAINTY_DERIVED,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como CAS por referencia normativa al D. Leg. 1057 en el título o descripción de la oportunidad.",
                matched_term=pat,
            )

    # -------------------------------------------------------------------------
    # 2. PRÁCTICAS PREPROFESIONALES (Ley 28518)
    # -------------------------------------------------------------------------
    pre_pro_patterns = [
        r"\bpractica\s+pre\s*profesional\b",
        r"\bpracticas\s+pre\s*profesionales\b",
        r"\bpracticante\s+pre\s*profesional\b",
        r"\bpracticante\s+pre\b",
        r"\bpre\s*profesional\b",
        r"\bconvenio\s+de\s+aprendizaje\s+pre\b",
    ]
    for pat in pre_pro_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_PRE_PROFESSIONAL]
            cert = CERTAINTY_EXPLICIT if any(re.search(p, combined_explicit) for p in pre_pro_patterns) or "preprofesional" in norm_kind else CERTAINTY_DERIVED
            return LaborRegimeClassification(
                regime_id=REGIME_PRE_PROFESSIONAL,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=cert,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Práctica Preprofesional bajo el marco de la Ley N° 28518 para estudiantes de educación superior.",
                matched_term=pat,
            )

    # -------------------------------------------------------------------------
    # 3. PRÁCTICAS PROFESIONALES (Ley 28518 / Ley 31396)
    # -------------------------------------------------------------------------
    pro_patterns = [
        r"\bpractica\s+profesional\b",
        r"\bpracticas\s+profesionales\b",
        r"\bpracticante\s+profesional\b",
        r"\bconvenio\s+de\s+practica\s+profesional\b",
    ]
    for pat in pro_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_PROFESSIONAL]
            cert = CERTAINTY_EXPLICIT if any(re.search(p, combined_explicit) for p in pro_patterns) or "profesional" in norm_kind else CERTAINTY_DERIVED
            return LaborRegimeClassification(
                regime_id=REGIME_PROFESSIONAL,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=cert,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Práctica Profesional bajo el marco de la Ley N° 28518 y Ley N° 31396 para egresados o bachilleres.",
                matched_term=pat,
            )

    # Generic "Prácticas" without pre/pro qualifier:
    # If level is 'Estudiante', derive PRE_PROFESSIONAL; if 'Egresado', derive PROFESSIONAL; else UNSPECIFIED formative
    if "practica" in norm_kind or "practicas" in norm_kind or "practicante" in norm_title or "intern" in norm_title:
        norm_level = _strip_accents(level)
        if "estudiante" in norm_level:
            defn = REGIME_DEFINITIONS[REGIME_PRE_PROFESSIONAL]
            return LaborRegimeClassification(
                regime_id=REGIME_PRE_PROFESSIONAL,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=CERTAINTY_DERIVED,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Práctica Preprofesional por convocatoria de prácticas orientada a condición formativa de estudiante.",
                matched_term="practica + estudiante",
            )
        if "egresado" in norm_level or "bachiller" in norm_level:
            defn = REGIME_DEFINITIONS[REGIME_PROFESSIONAL]
            return LaborRegimeClassification(
                regime_id=REGIME_PROFESSIONAL,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=CERTAINTY_DERIVED,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Práctica Profesional por convocatoria de prácticas orientada a egresado o bachiller.",
                matched_term="practica + egresado",
            )

    # -------------------------------------------------------------------------
    # 4. RÉGIMEN LABORAL DE LA ACTIVIDAD PRIVADA (D. Leg. 728)
    # -------------------------------------------------------------------------
    regime_728_patterns = [
        r"\bd\.?\s*leg\.?\s*(?:n[°oº]?\s*)?728\b",
        r"\bdecreto\s+legislativo\s*(?:n[°oº]?\s*)?728\b",
        r"\blegislativo\s*728\b",
        r"\bregimen\s*728\b",
        r"\bactividad\s+privada\b",
        r"\bplanilla\s+completa\b",
        r"\bcts\s*(?:y\s*gratificaciones|semestral)\b",
        r"\bgratificaciones\s+de\s+julio\s+y\s+diciembre\b",
    ]
    for pat in regime_728_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_728]
            cert = CERTAINTY_EXPLICIT if any(re.search(p, combined_explicit) for p in regime_728_patterns) else CERTAINTY_DERIVED
            return LaborRegimeClassification(
                regime_id=REGIME_728,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=cert,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Régimen Laboral de la Actividad Privada (D. Leg. 728) por mención explícita o beneficios propios del régimen común.",
                matched_term=pat,
            )

    # -------------------------------------------------------------------------
    # 5. LOCACIÓN DE SERVICIOS / HONORARIOS (Código Civil art. 1764)
    # -------------------------------------------------------------------------
    civil_patterns = [
        r"\blocaci[oó]n\s+de\s+servicios\b",
        r"\blocador\b",
        r"\brecibos?\s+por\s+honorarios\b",
        r"\bcuarta\s+categor[ií]a\b",
        r"\bhonorarios\s+profesionales\b",
        r"\borden\s+de\s+servicio\b",
        r"\bart[ií]culo\s*1764\b",
    ]
    for pat in civil_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_CIVIL]
            cert = CERTAINTY_EXPLICIT if any(re.search(p, combined_explicit) for p in civil_patterns) else CERTAINTY_DERIVED
            return LaborRegimeClassification(
                regime_id=REGIME_CIVIL,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=cert,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como Locación de Servicios bajo el Código Civil (art. 1764) por retribución mediante honorarios independientes.",
                matched_term=pat,
            )

    # -------------------------------------------------------------------------
    # 6. OTRAS MODALIDADES IDENTIFICADAS (Contratos B2B internacional, etc.)
    # -------------------------------------------------------------------------
    other_patterns = [
        r"\bb2b\s+contract\b",
        r"\bcontractor\b",
        r"\bcontrato\s+mercantil\b",
        r"\bprestacion\s+independiente\s+internacional\b",
        r"\bd\.?\s*leg\.?\s*276\b",
        r"\bley\s*(?:del\s*servicio\s*civil|30057)\b",
    ]
    for pat in other_patterns:
        if re.search(pat, combined_all):
            defn = REGIME_DEFINITIONS[REGIME_OTHER]
            return LaborRegimeClassification(
                regime_id=REGIME_OTHER,
                label=defn["label"],
                short_label=defn["shortLabel"],
                certainty=CERTAINTY_DERIVED,
                legal_framework=defn["legalFramework"],
                explanation="Clasificado como otra modalidad contractual por características de contratación internacional o régimen público no común.",
                matched_term=pat,
            )

    # -------------------------------------------------------------------------
    # 7. CONSERVATIVE FALLBACK: UNSPECIFIED
    # Fail-closed: Never assume a public agency is CAS or a private company is 728
    # without explicit or derived text backing.
    # -------------------------------------------------------------------------
    defn = REGIME_DEFINITIONS[REGIME_UNSPECIFIED]
    return LaborRegimeClassification(
        regime_id=REGIME_UNSPECIFIED,
        label=defn["label"],
        short_label=defn["shortLabel"],
        certainty=CERTAINTY_UNSPECIFIED,
        legal_framework=defn["legalFramework"],
        explanation="Modalidad de contratación no precisada en la convocatoria oficial; requiere consultar bases o contrato.",
        matched_term=None,
    )


def normalize_regime_id(val: str | None) -> str:
    """Normalizes any regime identifier or label to its canonical ID."""
    if not val:
        return REGIME_UNSPECIFIED
    clean = _strip_accents(str(val)).strip()
    if clean in (REGIME_PRE_PROFESSIONAL.lower(), "practicas preprofesionales", "practica preprofesional", "preprofesional", "pre"):
        return REGIME_PRE_PROFESSIONAL
    if clean in (REGIME_PROFESSIONAL.lower(), "practicas profesionales", "practica profesional", "profesional", "pro"):
        return REGIME_PROFESSIONAL
    if clean in (REGIME_CAS.lower(), "contratacion administrativa de servicios", "cas"):
        return REGIME_CAS
    if clean in (REGIME_728.lower(), "728", "regimen 728", "d.leg 728", "regimen laboral privado"):
        return REGIME_728
    if clean in (REGIME_CIVIL.lower(), "locacion de servicios", "honorarios", "locacion"):
        return REGIME_CIVIL
    if clean in (REGIME_OTHER.lower(), "otra modalidad", "otro", "other"):
        return REGIME_OTHER
    if clean in (REGIME_UNSPECIFIED.lower(), "no especificada", "sin especificar", "unspecified"):
        return REGIME_UNSPECIFIED
    return REGIME_UNSPECIFIED


def get_regime_metadata(regime_id: str) -> dict[str, Any]:
    """Retrieves authoritative metadata and legal backing for a regime identifier."""
    norm_id = normalize_regime_id(regime_id)
    return REGIME_DEFINITIONS.get(norm_id, REGIME_DEFINITIONS[REGIME_UNSPECIFIED])
