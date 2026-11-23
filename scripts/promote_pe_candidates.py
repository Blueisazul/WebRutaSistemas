"""Promotion script for R4-10 Peruvian opportunities."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "opportunities.seed.json"
INBOX_PATH = ROOT / "data" / "candidates" / "inbox.local.json"

LIMA_TZ = timezone(timedelta(hours=-5), "America/Lima")
OBSERVED_AT = "2026-11-23T08:46:38-05:00"
LAST_CHECKED = "2026-11-23"

PROMOTIONS = [
    {
        "req": "5297208007",
        "title": "Practicante PreProfesional para IT Support/ Helpdesk",
        "level": "Estudiante",
        "kind": "Práctica preprofesional",
        "sector": "Tecnología",
        "family": "Sistemas empresariales",
        "mode": "Presencial",
        "location": "Lima (Torre Prisma, Magdalena del Mar)",
        "eligibility": "Estudiantes universitarios en Perú (presencial Lima)",
        "duration": "Convenio de prácticas preprofesionales (30h/semana)",
        "salary": "No publicado",
        "salaryNote": "Subvención económica mensual acorde a ley de modalidades formativas (no informada en el portal público)",
    },
    {
        "req": "5251861007",
        "title": "Desarrollador Backend Java Mid",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia a oficina 2-3 días)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5263221007",
        "title": "Desarrollador Backend Java Semisenior",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia presencial 2-3 días)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5259646007",
        "title": "Desarrollador iOS Semi Senior",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia presencial 2-3 días)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5259645007",
        "title": "Desarrollador Java con Azure Semi Senior",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia presencial 2-3 días)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5248126007",
        "title": "Mid Data Engineer",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Analítica y datos",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia a oficina 2-3 días)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5286089007",
        "title": "Mid QA Functional Engineer",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5301871007",
        "title": "Mid React Native Developer",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5300899007",
        "title": "QA Engineer",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Remoto",
        "location": "Perú (Remoto nacional)",
        "eligibility": "Perú (trabajo remoto en territorio peruano)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5298868007",
        "title": "Mobile Developer (Android & iOS)",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Remoto",
        "location": "Perú (Remoto nacional)",
        "eligibility": "Perú (trabajo remoto en territorio peruano)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5283233007",
        "title": "Business Analyst (Automatización de Procesos - Power Platform)",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Sistemas empresariales",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia 2-3 veces por semana)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5259734007",
        "title": "Data Governance Analyst",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Analítica y datos",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida con asistencia a oficina 2-3 veces por semana)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
    {
        "req": "5286088007",
        "title": "Mid Java Backend Developer",
        "level": "Egresado / bachiller",
        "kind": "Profesional",
        "sector": "Tecnología",
        "family": "Desarrollo y QA",
        "mode": "Híbrido",
        "location": "Lima, Perú",
        "eligibility": "Perú (modalidad híbrida)",
        "duration": "Tiempo completo (40h/semana); contrato a plazo indeterminado",
        "salary": "No publicado",
        "salaryNote": "No informado en la convocatoria pública",
    },
]

ALLOWED_HOSTS = [
    "encora.com",
    "job-boards.greenhouse.io",
    "boards-api.greenhouse.io",
]

def make_opportunity(idx: int, p: dict) -> dict:
    op_id = f"OP-{idx:03d}"
    req = p["req"]
    apply_url = f"https://job-boards.greenhouse.io/encora10/jobs/{req}"
    source_url = "https://boards-api.greenhouse.io/v1/boards/encora10/jobs"
    evidence_url = apply_url

    # Fields that require fieldEvidence:
    # employer, publisher, title, sourceUrl, applyUrl, location, mode, sector, family, level, kind, eligibility, duration, salary
    field_evidence = [
        {"field": "employer", "url": f"https://boards-api.greenhouse.io/v1/boards/encora10/jobs/{req}", "observedAt": OBSERVED_AT},
        {"field": "publisher", "url": f"https://boards-api.greenhouse.io/v1/boards/encora10/jobs/{req}", "observedAt": OBSERVED_AT},
        {"field": "title", "url": f"https://boards-api.greenhouse.io/v1/boards/encora10/jobs/{req}", "observedAt": OBSERVED_AT},
        {"field": "sourceUrl", "url": source_url, "observedAt": OBSERVED_AT},
        {"field": "applyUrl", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "location", "url": f"https://boards-api.greenhouse.io/v1/boards/encora10/jobs/{req}", "observedAt": OBSERVED_AT},
        {"field": "mode", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "sector", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "family", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "level", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "kind", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "eligibility", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "duration", "url": apply_url, "observedAt": OBSERVED_AT},
        {"field": "salary", "url": apply_url, "observedAt": OBSERVED_AT},
    ]

    return {
        "id": op_id,
        "employer": "Encora",
        "publisher": "Portal público oficial (ATS Greenhouse)",
        "title": p["title"],
        "sector": p["sector"],
        "family": p["family"],
        "level": p["level"],
        "kind": p["kind"],
        "mode": p["mode"],
        "location": p["location"],
        "eligibility": p["eligibility"],
        "salary": p["salary"],
        "salaryNote": p["salaryNote"],
        "duration": p["duration"],
        "deadline": None,
        "sourceKind": "Portal público oficial (ATS Greenhouse)",
        "sourceUrl": source_url,
        "applyUrl": apply_url,
        "evidenceUrl": evidence_url,
        "requisition": req,
        "recordKind": "curated",
        "opportunityStatus": "open",
        "verificationStatus": "verified",
        "publicationStatus": "active",
        "lastCheckedDate": LAST_CHECKED,
        "lastVerifiedAt": OBSERVED_AT,
        "publishedAt": None,
        "employmentEndDate": None,
        "allowedHosts": ALLOWED_HOSTS,
        "verificationEvidence": {
            "publisherRelation": "employer_confirmed",
            "method": "manual",
            "result": "application_open",
            "url": evidence_url,
            "observedAt": OBSERVED_AT,
        },
        "editorialDecision": {
            "status": "approved",
            "reviewer": "Auditor Editorial R4-10 / Ruta Sistemas",
            "reason": f"Convocatoria oficial verificada activa de Encora en Perú ({p['title']}), aprobada formalmente para el catálogo público mediante R4-10-PE-CATALOG-RELEASE-01.",
            "decidedAt": OBSERVED_AT,
        },
        "fieldEvidence": field_evidence,
    }

def main():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)
    with open(INBOX_PATH, "r", encoding="utf-8") as f:
        inbox = json.load(f)

    existing_ops = seed["opportunities"]
    start_idx = len(existing_ops)
    print(f"Existing opportunities in seed: {start_idx}")

    new_ops = []
    promoted_reqs = set()
    for offset, p in enumerate(PROMOTIONS):
        op = make_opportunity(start_idx + offset, p)
        new_ops.append(op)
        promoted_reqs.add(p["req"])

    print(f"Generated {len(new_ops)} new opportunities (from OP-{start_idx:03d} to OP-{start_idx + len(new_ops) - 1:03d})")

    seed["opportunities"].extend(new_ops)

    # Update candidate review status in inbox
    candidates_updated = 0
    for cand in inbox.get("candidates", []):
        ext_ref = cand.get("proposed", {}).get("externalReference")
        if ext_ref in promoted_reqs and cand.get("sourceId") == "greenhouse-encora":
            cand["editorialReview"] = {
                "status": "approved_for_catalog",
                "reviewer": "Auditor Editorial R4-10 / Ruta Sistemas",
                "reviewedAt": OBSERVED_AT,
                "decisionNote": f"Promovido al catálogo canónico como OP-XXX mediante R4-10-PE-CATALOG-RELEASE-01",
            }
            candidates_updated += 1

    print(f"Updated {candidates_updated} candidates in staging inbox to 'approved_for_catalog'.")

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(INBOX_PATH, "w", encoding="utf-8") as f:
        json.dump(inbox, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Successfully wrote updated seed and inbox!")

if __name__ == "__main__":
    main()
