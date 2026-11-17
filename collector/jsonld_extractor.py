"""Institutional HTML and Schema.org JSON-LD micro-extractor producing Schema 2 candidates.

Uses Python standard library (html.parser, json, urllib, datetime) with zero external dependencies.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit

from .ats_connectors import (
    PROPOSED_FIELDS,
    _build_candidate_record,
    _current_timestamp,
    _empty_proposed,
    _is_valid_https_url,
    _safe_str,
)


class JsonLdScriptParser(HTMLParser):
    """Lenient HTML parser that extracts raw content from <script type="application/ld+json"> tags."""

    def __init__(self) -> None:
        super().__init__()
        self.in_jsonld: bool = False
        self.current_chunks: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            for attr_name, attr_value in attrs:
                if attr_name.lower() == "type" and attr_value and attr_value.strip().lower() == "application/ld+json":
                    self.in_jsonld = True
                    self.current_chunks = []
                    break

    def handle_data(self, data: str) -> None:
        if self.in_jsonld:
            self.current_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_jsonld:
            full_text = "".join(self.current_chunks).strip()
            if full_text:
                self.scripts.append(full_text)
            self.in_jsonld = False
            self.current_chunks = []


def extract_jsonld_scripts(html_content: str) -> list[str]:
    """Extracts raw JSON-LD text content from all application/ld+json script tags."""
    if not html_content or not isinstance(html_content, str):
        return []
    parser = JsonLdScriptParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass
    return parser.scripts


def parse_jsonld_payloads(raw_scripts: list[str]) -> list[dict | list]:
    """Parses raw script texts into JSON structures, safely ignoring syntax errors."""
    payloads: list[dict | list] = []
    for script_text in raw_scripts:
        try:
            parsed = json.loads(script_text)
            if isinstance(parsed, (dict, list)):
                payloads.append(parsed)
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    return payloads


def _is_job_posting_type(type_val: object) -> bool:
    """Checks whether an @type property represents a Schema.org JobPosting."""
    if isinstance(type_val, str):
        t = type_val.strip()
        return t == "JobPosting" or t.endswith("/JobPosting") or t.endswith(":JobPosting")
    if isinstance(type_val, list):
        return any(_is_job_posting_type(item) for item in type_val)
    return False


def find_job_postings(data: object) -> list[dict]:
    """Recursively traverses a JSON structure to find all JobPosting dictionaries."""
    results: list[dict] = []

    if isinstance(data, dict):
        if _is_job_posting_type(data.get("@type")):
            results.append(data)
        graph = data.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                results.extend(find_job_postings(item))
        for key, val in data.items():
            if key not in ("@graph",) and isinstance(val, (dict, list)):
                results.extend(find_job_postings(val))
    elif isinstance(data, list):
        for item in data:
            results.extend(find_job_postings(item))

    return results


def _extract_employer(org_data: object) -> str | None:
    if isinstance(org_data, dict):
        return _safe_str(org_data.get("name"))
    if isinstance(org_data, str):
        return _safe_str(org_data)
    return None


def _extract_external_ref(identifier: object) -> str | None:
    if isinstance(identifier, (str, int)) and not isinstance(identifier, bool):
        return _safe_str(str(identifier))
    if isinstance(identifier, dict):
        val = identifier.get("value")
        if isinstance(val, (str, int)) and not isinstance(val, bool):
            return _safe_str(str(val))
    return None


def _extract_date(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    val_str = value.strip()
    if not val_str:
        return None
    try:
        dt = datetime.fromisoformat(val_str.replace("Z", "+00:00"))
        if 2000 <= dt.year <= 2100:
            return dt.date().isoformat()
    except (ValueError, OverflowError):
        pass
    return None


def _extract_location(value: object) -> str | None:
    if isinstance(value, str):
        return _safe_str(value)
    if isinstance(value, dict):
        addr = value.get("address")
        if isinstance(addr, str):
            return _safe_str(addr)
        if isinstance(addr, dict):
            parts = []
            for k in ("streetAddress", "addressLocality", "addressRegion", "addressCountry"):
                v = addr.get(k)
                if isinstance(v, dict):
                    v = v.get("name")
                v_str = _safe_str(v)
                if v_str:
                    parts.append(v_str)
            if parts:
                return ", ".join(parts)
        name = value.get("name")
        if isinstance(name, str):
            return _safe_str(name)
    return None


def _extract_mode(job: dict, location_str: str | None) -> str | None:
    loc_type = job.get("jobLocationType")
    if isinstance(loc_type, str) and loc_type.strip().upper() == "TELECOMMUTE":
        return "Remoto"
    if location_str and location_str.lower() in ("remote", "remoto"):
        return "Remoto"
    return None


def _extract_opportunity_type(emp_type: object) -> str | None:
    if isinstance(emp_type, str):
        t = emp_type.strip().upper()
        if t in ("INTERN", "INTERNSHIP"):
            return "Prácticas"
        if t == "FULL_TIME":
            return "Tiempo completo"
        if t == "PART_TIME":
            return "Medio tiempo"
        return _safe_str(emp_type)
    if isinstance(emp_type, list):
        for item in emp_type:
            res = _extract_opportunity_type(item)
            if res:
                return res
    return None


def _extract_salary(value: object) -> str | None:
    if isinstance(value, dict):
        currency = _safe_str(value.get("currency"))
        amount = value.get("value")
        if isinstance(amount, dict):
            val_num = amount.get("value") or amount.get("minValue")
        elif isinstance(amount, (int, float, str)) and not isinstance(amount, bool):
            val_num = amount
        else:
            val_num = None

        if currency and val_num is not None:
            clean_num = str(val_num).strip()
            if clean_num:
                return f"{currency} {clean_num}"
    elif isinstance(value, str):
        val_str = value.strip()
        if any(curr in val_str.upper() for curr in ("S/", "PEN", "USD", "$")):
            return val_str
    return None


def normalize_job_posting(
    source: dict,
    job: dict,
    *,
    source_url: str,
    captured_at: str | None = None,
) -> dict | None:
    """Normalizes a single Schema.org JobPosting dictionary into a Schema 2 candidate record."""
    if not isinstance(job, dict):
        return None

    title = _safe_str(job.get("title"))
    if not title:
        return None

    source_id = str(source.get("id", "institutional-source"))
    employer = _extract_employer(job.get("hiringOrganization")) or _safe_str(source.get("employer")) or _safe_str(source.get("entity"))
    publisher = _safe_str(source.get("publisher")) or employer
    external_ref = _extract_external_ref(job.get("identifier"))
    captured_at_str = captured_at or _current_timestamp()

    proposed = _empty_proposed()
    proposed["title"] = title
    proposed["employer"] = employer
    proposed["publisher"] = publisher
    proposed["externalReference"] = external_ref

    raw_apply_url = _safe_str(job.get("url"))
    if raw_apply_url:
        is_ok, _ = _is_valid_https_url(raw_apply_url)
        if is_ok:
            proposed["applyUrl"] = raw_apply_url

    proposed["publishedAt"] = _extract_date(job.get("datePosted"))
    proposed["deadline"] = _extract_date(job.get("validThrough"))

    location = _extract_location(job.get("jobLocation"))
    if location:
        proposed["location"] = location

    mode = _extract_mode(job, location)
    if mode:
        proposed["mode"] = mode

    opp_type = _extract_opportunity_type(job.get("employmentType"))
    if opp_type:
        proposed["opportunityType"] = opp_type

    salary = _extract_salary(job.get("baseSalary"))
    if salary:
        proposed["salary"] = salary

    if external_ref:
        candidate_id = f"CAND-{source_id}-{external_ref}"
    else:
        sig = f"{source_url}:{title}"
        stable_hash = hashlib.sha256(sig.encode("utf-8")).hexdigest()[:8]
        candidate_id = f"CAND-{source_id}-HASH-{stable_hash}"

    return _build_candidate_record(
        candidate_id=candidate_id,
        source_id=source_id,
        source_url=source_url,
        captured_at=captured_at_str,
        proposed=proposed,
    )


def extract_candidates_from_html(
    source: dict,
    html_content: str,
    *,
    source_url: str,
    captured_at: str | None = None,
) -> list[dict]:
    """Extracts, filters, and normalizes Schema.org JobPosting records from an HTML document."""
    is_https, host = _is_valid_https_url(source_url)
    if not is_https or host not in [h.lower() for h in source.get("allowedHosts", [])]:
        raise ValueError("source_url_not_allowlisted")

    scripts = extract_jsonld_scripts(html_content)
    if not scripts:
        return []

    payloads = parse_jsonld_payloads(scripts)
    if not payloads:
        return []

    raw_jobs: list[dict] = []
    for item in payloads:
        raw_jobs.extend(find_job_postings(item))

    records: list[dict] = []
    seen_ids: set[str] = set()

    for job in raw_jobs:
        record = normalize_job_posting(source, job, source_url=source_url, captured_at=captured_at)
        if record is None:
            continue
        cand_id = record["candidateId"]
        if cand_id in seen_ids:
            continue
        seen_ids.add(cand_id)
        records.append(record)

    return records
