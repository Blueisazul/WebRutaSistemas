"""Technical skills and competencies extraction and comparison engine.

TASK-R7-02: Comparador de Trayectorias y Requisitos Técnicos.
Features:
- Deterministic extraction and normalization of technical skills and competencies.
- Priority classification: REQUIRED, PREFERRED, MENTIONED, UNSPECIFIED.
- Contrast between two opportunities: shared skills, exclusive skills, requirement differences.
- Traceability to source fields (skills, requirements, tasks, title) with excerpt quotes.
- Conservative fail-closed behavior: no hallucinated requirements or scoring.
- Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

# Priority levels
PRIORITY_REQUIRED = "REQUIRED"
PRIORITY_PREFERRED = "PREFERRED"
PRIORITY_MENTIONED = "MENTIONED"
PRIORITY_UNSPECIFIED = "UNSPECIFIED"

ALL_PRIORITIES = (
    PRIORITY_REQUIRED,
    PRIORITY_PREFERRED,
    PRIORITY_MENTIONED,
    PRIORITY_UNSPECIFIED,
)

# Canonical skill taxonomy with strict boundary regexes to avoid false positives
# e.g., C should not match within 'Conocimientos' or 'Comunicación'
SKILL_TAXONOMY: dict[str, dict[str, Any]] = {
    "Python": {
        "canonical": "Python",
        "category": "Lenguajes de programación",
        "patterns": [r"\bpython(?:3)?\b"],
    },
    "Java": {
        "canonical": "Java",
        "category": "Lenguajes de programación",
        "patterns": [r"\bjava\b(?!\s*script)"],
    },
    "JavaScript": {
        "canonical": "JavaScript",
        "category": "Lenguajes de programación",
        "patterns": [r"\bjavascript\b", r"\bjs\b(?!\s*(?:on|to))"],
    },
    "TypeScript": {
        "canonical": "TypeScript",
        "category": "Lenguajes de programación",
        "patterns": [r"\btypescript\b", r"\bts\b(?!\s*(?:on|to))"],
    },
    "C#": {
        "canonical": "C#",
        "category": "Lenguajes de programación",
        "patterns": [r"\bc#(?!\w)", r"\bc\s*sharp\b"],
    },
    "C++": {
        "canonical": "C++",
        "category": "Lenguajes de programación",
        "patterns": [r"\bc\+\+(?!\w)"],
    },
    "C": {
        "canonical": "C",
        "category": "Lenguajes de programación",
        "patterns": [
            r"\blenguaje\s+c\b",
            r"\bprogramaci[oó]n\s+en\s+c\b",
            r"\bc\s*\/c\+\+\b",
            r"\bc\s*,\s*c\+\+\b",
            r"\bc\s+y\s+c\+\+\b",
            r"\bc(?:\s+y\/o|\/)\s*rust\b",
            r"\blinux\s+kernel\s*·\s*c\b",
        ],
    },
    "Rust": {
        "canonical": "Rust",
        "category": "Lenguajes de programación",
        "patterns": [r"\brust\b"],
    },
    "Go": {
        "canonical": "Go",
        "category": "Lenguajes de programación",
        "patterns": [
            r"\bgolang\b",
            r"\blenguaje\s+go\b",
            r"\bprogramaci[oó]n\s+en\s+go\b",
            r"(?:^|[\s·•,|/])go(?:[\s·•,|/]|$)",
        ],
    },
    "PHP": {
        "canonical": "PHP",
        "category": "Lenguajes de programación",
        "patterns": [r"\bphp\b"],
    },
    "Kotlin": {
        "canonical": "Kotlin",
        "category": "Lenguajes de programación",
        "patterns": [r"\bkotlin\b"],
    },
    "Swift": {
        "canonical": "Swift",
        "category": "Lenguajes de programación",
        "patterns": [r"\bswift\b"],
    },
    "Dart": {
        "canonical": "Dart",
        "category": "Lenguajes de programación",
        "patterns": [r"\bdart\b"],
    },
    "Bash / Shell": {
        "canonical": "Bash / Shell",
        "category": "Lenguajes de programación",
        "patterns": [r"\bbash\b", r"\bshell\s+script(?:ing)?\b"],
    },
    # Frameworks & Libraries
    "React": {
        "canonical": "React",
        "category": "Frameworks y librerías",
        "patterns": [r"\breact(?:\.js)?\b"],
    },
    "Angular": {
        "canonical": "Angular",
        "category": "Frameworks y librerías",
        "patterns": [r"\bangular\b"],
    },
    "Vue.js": {
        "canonical": "Vue.js",
        "category": "Frameworks y librerías",
        "patterns": [r"\bvue(?:\.js)?\b"],
    },
    "Node.js": {
        "canonical": "Node.js",
        "category": "Frameworks y librerías",
        "patterns": [r"\bnode(?:\.js)?\b"],
    },
    "Spring Boot": {
        "canonical": "Spring Boot",
        "category": "Frameworks y librerías",
        "patterns": [r"\bspring\s*boot\b", r"\bspring\s+framework\b"],
    },
    ".NET": {
        "canonical": ".NET",
        "category": "Frameworks y librerías",
        "patterns": [r"\b\.net\b", r"\bdotnet\b", r"\basp\.net\b"],
    },
    "Django": {
        "canonical": "Django",
        "category": "Frameworks y librerías",
        "patterns": [r"\bdjango\b"],
    },
    "FastAPI": {
        "canonical": "FastAPI",
        "category": "Frameworks y librerías",
        "patterns": [r"\bfastapi\b"],
    },
    "Flutter": {
        "canonical": "Flutter",
        "category": "Frameworks y librerías",
        "patterns": [r"\bflutter\b"],
    },
    "UIKit / SwiftUI": {
        "canonical": "UIKit / SwiftUI",
        "category": "Frameworks y librerías",
        "patterns": [r"\buikit\b", r"\bswiftui\b"],
    },
    "Jetpack Compose": {
        "canonical": "Jetpack Compose",
        "category": "Frameworks y librerías",
        "patterns": [r"\bjetpack\s+compose\b"],
    },
    # Databases & Data Analytics
    "SQL": {
        "canonical": "SQL",
        "category": "Bases de datos y analítica",
        "patterns": [r"(?<!transact-)(?<!t-)\bsql\b(?!\s*(?:server|lite))"],
    },
    "PostgreSQL": {
        "canonical": "PostgreSQL",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bpostgres(?:ql)?\b"],
    },
    "MySQL": {
        "canonical": "MySQL",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bmysql\b"],
    },
    "SQL Server": {
        "canonical": "SQL Server",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bsql\s*server\b", r"\bmssql\b"],
    },
    "Oracle DB": {
        "canonical": "Oracle DB",
        "category": "Bases de datos y analítica",
        "patterns": [r"\boracle\s*(?:db|database|bd)?\b"],
    },
    "MongoDB": {
        "canonical": "MongoDB",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bmongodb\b", r"\bmongo\b"],
    },
    "Redis": {
        "canonical": "Redis",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bredis\b"],
    },
    "Power BI": {
        "canonical": "Power BI",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bpower\s*bi\b"],
    },
    "Excel": {
        "canonical": "Excel",
        "category": "Bases de datos y analítica",
        "patterns": [r"\bexcel\b(?:\s*avanzado|\s*intermedio)?"],
    },
    "ETL": {
        "canonical": "ETL",
        "category": "Bases de datos y analítica",
        "patterns": [r"\betl\b"],
    },
    # Cloud, DevOps & Infrastructure
    "AWS": {
        "canonical": "AWS",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\baws\b", r"\bamazon\s+web\s+services\b"],
    },
    "Azure": {
        "canonical": "Azure",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bazure\b", r"\bmicrosoft\s+azure\b"],
    },
    "Google Cloud": {
        "canonical": "Google Cloud",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bgcp\b", r"\bgoogle\s+cloud(?:\s+platform)?\b"],
    },
    "Docker": {
        "canonical": "Docker",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bdocker\b"],
    },
    "Kubernetes": {
        "canonical": "Kubernetes",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bkubernetes\b", r"\bk8s\b"],
    },
    "Linux": {
        "canonical": "Linux",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\blinux\b"],
    },
    "Ubuntu": {
        "canonical": "Ubuntu",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bubuntu\b"],
    },
    "Git": {
        "canonical": "Git",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bgit\b(?!\s*(?:hub|lab))"],
    },
    "CI/CD": {
        "canonical": "CI/CD",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [
            r"\bci\s*\/\s*cd\b",
            r"\bcontinuous\s+integration\b",
            r"\bintegraci[oó]n\s+continua\b",
        ],
    },
    "Terraform": {
        "canonical": "Terraform",
        "category": "Cloud, DevOps e Infraestructura",
        "patterns": [r"\bterraform\b"],
    },
    # Architecture & Practices
    "APIs REST": {
        "canonical": "APIs REST",
        "category": "Arquitectura y Metodologías",
        "patterns": [r"\bapis?\s+rest(?:ful)?\b", r"\bservicios?\s+rest\b", r"\brest\s*api\b"],
    },
    "Microservicios": {
        "canonical": "Microservicios",
        "category": "Arquitectura y Metodologías",
        "patterns": [r"\bmicroservicios\b", r"\bmicroservices\b"],
    },
    "Clean Architecture": {
        "canonical": "Clean Architecture",
        "category": "Arquitectura y Metodologías",
        "patterns": [r"\bclean\s+architecture\b", r"\barquitectura\s+limpia\b", r"\bmvvm\b"],
    },
    "ERP / SAP": {
        "canonical": "ERP / SAP",
        "category": "Sistemas de gestión",
        "patterns": [r"\berp\b", r"\bsap\b", r"\bmrp\b"],
    },
    "Ciberseguridad": {
        "canonical": "Ciberseguridad",
        "category": "Seguridad y Redes",
        "patterns": [
            r"\bciberseguridad\b",
            r"\bseguridad\s+inform[aá]tica\b",
            r"\binformation\s+security\b",
            r"\bsecurity\b",
        ],
    },
    "Redes": {
        "canonical": "Redes",
        "category": "Seguridad y Redes",
        "patterns": [r"\bredes(?!\s*sociales)(?:\s+de\s+datos|\s+y\s+telecomunicaciones|\s+tcp|\s+cisco)?\b"],
    },
}

PREFERRED_PATTERNS = [
    r"\bdeseable\b",
    r"\bpreferible\b",
    r"\bpreferente\b",
    r"\bde\s+preferencia\b",
    r"\bplus\b",
    r"\bopcional\b",
    r"\bvalorar[aá]\b",
    r"\bse\s+valorar[aá]\b",
    r"\bno\s+excluyente\b",
]

REQUIRED_PATTERNS = [
    r"\bindispensable\b",
    r"\bexcluyente\b",
    r"\bobligatorio\b",
    r"\bm[ií]nimo\b",
    r"\brequisito\b",
    r"\bexperiencia\s*(?:m[ií]nima|comprobada|de)\b",
    r"\bconocimiento\s*(?:s[oó]lido|avanzado|intermedio)\b",
    r"\bdebe\s+contar\b",
    r"\bdominio\b",
]


def _strip_accents(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


@dataclass
class ExtractedSkill:
    canonical: str
    category: str
    raw: str
    priority: str  # REQUIRED, PREFERRED, MENTIONED
    source_field: str  # skills, requirements, tasks, title
    context: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillComparisonResult:
    job_a_id: str
    job_b_id: str
    shared_skills: list[dict[str, Any]]
    exclusive_a: list[dict[str, Any]]
    exclusive_b: list[dict[str, Any]]
    required_a: list[str]
    required_b: list[str]
    preferred_a: list[str]
    preferred_b: list[str]
    is_a_unspecified: bool
    is_b_unspecified: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _determine_priority(item_text: str, source_field: str) -> str:
    """Determines priority based on surrounding context and field origin."""
    norm = _strip_accents(item_text.lower())
    if any(re.search(pat, norm) for pat in PREFERRED_PATTERNS):
        return PRIORITY_PREFERRED
    if any(re.search(pat, norm) for pat in REQUIRED_PATTERNS):
        return PRIORITY_REQUIRED
    if source_field in ("requirements", "skills", "title"):
        return PRIORITY_REQUIRED
    return PRIORITY_MENTIONED


def extract_skills_from_opportunity(job: dict[str, Any]) -> dict[str, ExtractedSkill]:
    """Extracts, normalizes, and classifies technical skills from an opportunity record."""
    extracted: dict[str, ExtractedSkill] = {}

    def inspect_text_block(text: str, field_name: str) -> None:
        if not text:
            return
        # Split on sentence/bullet boundaries
        clauses = [c.strip() for c in re.split(r"[;.\n\r·•|]", text) if c.strip()]
        if not clauses:
            clauses = [text.strip()]

        for clause in clauses:
            clause_norm = _strip_accents(clause.lower())
            for skill_key, defn in SKILL_TAXONOMY.items():
                for pat in defn["patterns"]:
                    # Match on normalized text with pattern
                    m = re.search(pat, clause_norm, re.IGNORECASE)
                    if m:
                        priority = _determine_priority(clause, field_name)
                        # If already found with lower priority, upgrade
                        existing = extracted.get(skill_key)
                        if existing:
                            if existing.source_field == "requirements" and field_name == "skills":
                                pass
                            else:
                                priority_rank = {PRIORITY_REQUIRED: 3, PRIORITY_PREFERRED: 2, PRIORITY_MENTIONED: 1}
                                if priority_rank.get(priority, 0) > priority_rank.get(existing.priority, 0):
                                    existing.priority = priority
                                    existing.source_field = field_name
                                    existing.context = clause
                        else:
                            raw_term = clause[m.start():m.end()] if m.start() < len(clause) else defn["canonical"]
                            extracted[skill_key] = ExtractedSkill(
                                canonical=defn["canonical"],
                                category=defn["category"],
                                raw=raw_term or defn["canonical"],
                                priority=priority,
                                source_field=field_name,
                                context=clause[:120],
                            )
                        break

    # 1. Requirements field (highest specificity for required vs preferred)
    reqs_field = str(job.get("requirements") or "").strip()
    if reqs_field and not reqs_field.lower().startswith("no "):
        inspect_text_block(reqs_field, "requirements")

    # 2. Direct explicit skills field
    skills_field = str(job.get("skills") or "").strip()
    if skills_field and not skills_field.lower().startswith("no "):
        inspect_text_block(skills_field, "skills")

    # 3. Title field
    title_field = str(job.get("title") or "").strip()
    if title_field:
        inspect_text_block(title_field, "title")

    # 4. Tasks / description field
    tasks_field = str(job.get("tasks") or "").strip()
    if tasks_field and not tasks_field.lower().startswith("no "):
        inspect_text_block(tasks_field, "tasks")

    return extracted


def compare_opportunity_skills(job_a: dict[str, Any], job_b: dict[str, Any]) -> SkillComparisonResult:
    """Compares technical skills and requirements between two opportunities."""
    skills_a = extract_skills_from_opportunity(job_a)
    skills_b = extract_skills_from_opportunity(job_b)

    keys_a = set(skills_a.keys())
    keys_b = set(skills_b.keys())

    shared_keys = sorted(keys_a.intersection(keys_b))
    exclusive_a_keys = sorted(keys_a - keys_b)
    exclusive_b_keys = sorted(keys_b - keys_a)

    shared_skills = [
        {
            "canonical": k,
            "category": skills_a[k].category,
            "priorityA": skills_a[k].priority,
            "priorityB": skills_b[k].priority,
            "sourceFieldA": skills_a[k].source_field,
            "sourceFieldB": skills_b[k].source_field,
            "contextA": skills_a[k].context,
            "contextB": skills_b[k].context,
        }
        for k in shared_keys
    ]

    exclusive_a = [skills_a[k].to_dict() for k in exclusive_a_keys]
    exclusive_b = [skills_b[k].to_dict() for k in exclusive_b_keys]

    required_a = sorted([k for k, s in skills_a.items() if s.priority == PRIORITY_REQUIRED])
    required_b = sorted([k for k, s in skills_b.items() if s.priority == PRIORITY_REQUIRED])

    preferred_a = sorted([k for k, s in skills_a.items() if s.priority == PRIORITY_PREFERRED])
    preferred_b = sorted([k for k, s in skills_b.items() if s.priority == PRIORITY_PREFERRED])

    is_a_unspecified = len(skills_a) == 0
    is_b_unspecified = len(skills_b) == 0

    return SkillComparisonResult(
        job_a_id=str(job_a.get("id") or "A"),
        job_b_id=str(job_b.get("id") or "B"),
        shared_skills=shared_skills,
        exclusive_a=exclusive_a,
        exclusive_b=exclusive_b,
        required_a=required_a,
        required_b=required_b,
        preferred_a=preferred_a,
        preferred_b=preferred_b,
        is_a_unspecified=is_a_unspecified,
        is_b_unspecified=is_b_unspecified,
    )
