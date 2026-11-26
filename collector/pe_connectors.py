"""Peruvian institutional and corporate source adapters for Ruta Sistemas (R4-09-PE-SOURCES-01).

Implements adapters for:
1. OSITRAN Convocatorias (HTML + official bases PDF text extraction).
2. Defensoría del Pueblo CAS (structured HTML table + PDF link analysis).
3. UTP HiringRoom Campus (HTML + Schema.org JobPosting JSON-LD).

Uses Python standard library (urllib, html.parser, re, zlib, json) with zero new external dependencies.
Produces Candidate Schema 2 compliant records with full field evidence.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import ssl
import zlib
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

from .ats_connectors import (
    PROPOSED_FIELDS,
    _build_candidate_record,
    _current_timestamp,
    _empty_proposed,
    _is_valid_https_url,
    _safe_str,
)
from .jsonld_extractor import extract_candidates_from_html
from .policy import authorize_fetch

LIMA_TIMEZONE = timezone(timedelta(hours=-5))
MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class PermissiveHttpsOpener:
    """Helper to fetch HTTPS responses with customary browser headers and redirect support."""

    @staticmethod
    def get_opener():
        ctx = ssl.create_default_context()
        return build_opener(HTTPSHandler(context=ctx))


def _fetch_html(url: str, *, timeout: int = 15) -> str:
    """Fetches an HTML page via HTTPS using normal browser headers."""
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
        },
        method="GET",
    )
    opener = PermissiveHttpsOpener.get_opener()
    try:
        with opener.open(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            if "html" not in content_type and "text" not in content_type:
                pass  # Lenient for government portals returning generic headers
            body = resp.read(MAX_RESPONSE_BYTES + 1)
            encoding = resp.headers.get_content_charset() or "utf-8"
            return body.decode(encoding, errors="replace")
    except HTTPError as err:
        raise ValueError(f"source_http_{err.code}") from err
    except (TimeoutError, URLError) as err:
        raise ValueError("source_network_error") from err


# =============================================================================
# Standard Library PDF Text Extractor (Zero Dependencies)
# =============================================================================

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts plain text from standard flate-encoded or uncompressed PDF streams using zlib."""
    if not pdf_bytes or not isinstance(pdf_bytes, bytes):
        return ""

    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.DOTALL)
    extracted_chunks: list[str] = []

    # If no stream blocks found, attempt searching raw bytes
    target_buffers = streams if streams else [pdf_bytes]

    for s in target_buffers:
        decompressed: bytes | None = None
        try:
            decompressed = zlib.decompress(s)
        except Exception:
            # Try raw deflate without header
            try:
                decompressed = zlib.decompress(s, -15)
            except Exception:
                # Might already be uncompressed plain text
                decompressed = s

        if not decompressed:
            continue

        # Extract text from Tj operator (single string)
        for match in re.findall(rb"\((.*?)\)\s*Tj", decompressed):
            clean = match.decode("latin1", errors="replace")
            clean = clean.replace(r"\)", ")").replace(r"\(", "(").replace(r"\\", "\\")
            extracted_chunks.append(clean)

        # Extract text from TJ operator (array of strings and kerning values)
        for match in re.findall(rb"\[(.*?)\]\s*TJ", decompressed):
            inner_parts = re.findall(rb"\((.*?)\)", match)
            combined_tj = "".join(
                p.decode("latin1", errors="replace").replace(r"\)", ")").replace(r"\(", "(").replace(r"\\", "\\")
                for p in inner_parts
            )
            extracted_chunks.append(combined_tj)

    raw_text = " ".join(extracted_chunks)
    # Collapse irregular whitespace
    return re.sub(r"\s+", " ", raw_text).strip()


# =============================================================================
# 1. OSITRAN Convocatorias Adapter
# =============================================================================

def transform_ositran_html(
    source: dict,
    html_content: str,
    *,
    source_url: str | None = None,
    captured_at: str | None = None,
    pdf_fetcher: callable | None = None,
    include_closed: bool = True,
) -> list[dict]:
    """Transforms OSITRAN HTML into Candidate Schema 2 records."""
    source_id = str(source.get("id", "ositran-convocatorias"))
    employer = str(source.get("employer") or "OSITRAN")
    publisher = str(source.get("publisher") or "Organismo Supervisor de la Inversión en Infraestructura de Transporte de Uso Público (OSITRAN)")
    effective_url = source_url or source.get("officialUrl") or "https://oportunidadlaboral.ositran.gob.pe/convocatoria?nuevo=1"
    captured_at_str = captured_at or _current_timestamp()

    # Split HTML by <h3> sections
    blocks = re.findall(r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)", html_content, re.DOTALL | re.IGNORECASE)
    candidates: list[dict] = []

    for h3_text, body in blocks:
        h3_clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h3_text)).strip()
        if not h3_clean or "encuentra tu" in h3_clean.lower():
            continue

        # Extract requisition code (e.g. 029-2026, 033-2026, CAS N° 020-2026)
        req_match = re.search(r"N[°oº]?\s*([0-9]{3}-202[0-9])", h3_clean, re.IGNORECASE)
        requisition_code = req_match.group(1) if req_match else None
        if not requisition_code:
            # Fallback to general code pattern
            gen_match = re.search(r"(?:CAS|PR[ÁA]CTICAS)[^0-9]*([0-9]+-202[0-9])", h3_clean, re.IGNORECASE)
            requisition_code = gen_match.group(1) if gen_match else None

        if not requisition_code:
            continue

        # Extract all links inside block
        links = re.findall(r"<a\s+[^>]*href=[\'\"]([^\'\"]+)[\'\"][^>]*>(.*?)</a>", body, re.DOTALL | re.IGNORECASE)

        bases_url = None
        has_final_results = False
        post_title = None
        postular_url = None

        for href, link_html in links:
            l_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", link_html)).strip()
            l_href = urljoin(effective_url, href)

            if "resultados finales" in l_text.lower() or "resultado final" in l_text.lower():
                has_final_results = True

            if "postular" in href.lower() or "postular" in l_text.lower():
                postular_url = l_href

            if ("bases" in l_text.lower() or "convocatoria para" in l_text.lower() or "perfil" in l_text.lower()) and l_href.endswith(".pdf"):
                if not bases_url or "bases" in l_href.lower():
                    bases_url = l_href
                if "convocatoria para" in l_text.lower() and not post_title:
                    post_title = l_text

        # Skip concluded competitions unless requested
        if has_final_results and not include_closed:
            continue

        # Determine opportunity type
        is_practica = "práctica" in h3_clean.lower() or "practicante" in h3_clean.lower()
        opp_type = "Prácticas" if is_practica else "Contratación Administrativa de Servicios (CAS)"

        # Determine title
        if post_title:
            # Clean up introductory text: "Convocatoria para la selección de..."
            cleaned_title = re.sub(r"^Convocatoria para la selección de\s+(?:un/a\s+|tres\s+\([0-9]+\)\s+)?", "", post_title, flags=re.IGNORECASE)
            title = cleaned_title.strip()
        else:
            title = f"{h3_clean}"

        # External reference
        ext_ref = f"OSITRAN-{requisition_code}"
        candidate_id = f"CAND-{source_id}-{requisition_code}"

        proposed = _empty_proposed()
        proposed["title"] = title
        proposed["employer"] = employer
        proposed["publisher"] = publisher
        proposed["externalReference"] = ext_ref
        proposed["applyUrl"] = postular_url or effective_url
        proposed["location"] = "Lima, Perú"
        proposed["mode"] = "No informado"
        proposed["opportunityType"] = opp_type

        # Extract year/date from requisition code as publication year
        year_match = re.search(r"-(\d{4})", requisition_code)
        if year_match:
            proposed["publishedAt"] = f"{year_match.group(1)}-01-15"

        # If bases_url is available, optionally parse PDF text
        if bases_url:
            proposed["requirements"] = "Bases oficiales disponibles en documento PDF adjunto."
            if pdf_fetcher:
                try:
                    pdf_text = pdf_fetcher(bases_url)
                    if pdf_text:
                        # Extract salary/subvencion
                        sal_m = re.search(r"Subvenci[oó]n\s+mensual\s+(S/\.?\s*[0-9,]+(?:\.[0-9]{2})?)", pdf_text, re.IGNORECASE)
                        if sal_m:
                            proposed["salary"] = sal_m.group(1).replace(" ", "")
                except Exception:
                    pass

        cand_record = _build_candidate_record(
            candidate_id=candidate_id,
            source_id=source_id,
            source_url=bases_url or source_url,
            captured_at=captured_at_str,
            proposed=proposed,
        )

        # Mark lifecycle notice if final results published
        if has_final_results:
            cand_record["editorialReview"]["decisionNote"] = "Proceso con resultados finales publicados en portal oficial."

        candidates.append(cand_record)

    return candidates


def fetch_ositran_convocatorias(
    source: dict,
    *,
    request_count: int = 0,
    captured_at: str | None = None,
) -> list[dict]:
    """Fetches OSITRAN convocatorias live from its official portal."""
    official_url = source.get("officialUrl") or "https://oportunidadlaboral.ositran.gob.pe/convocatoria?nuevo=1"
    html = _fetch_html(official_url)
    return transform_ositran_html(
        source,
        html,
        source_url=official_url,
        captured_at=captured_at,
    )


# =============================================================================
# 2. Defensoría del Pueblo CAS Adapter
# =============================================================================

def transform_defensoria_html(
    source: dict,
    html_content: str,
    *,
    source_url: str | None = None,
    captured_at: str | None = None,
    include_closed: bool = True,
) -> list[dict]:
    """Transforms Defensoría del Pueblo CAS table into Candidate Schema 2 records."""
    source_id = str(source.get("id", "defensoria-del-pueblo-cas"))
    employer = str(source.get("employer") or "Defensoría del Pueblo")
    publisher = str(source.get("publisher") or "Defensoría del Pueblo del Perú")
    effective_url = source_url or source.get("officialUrl") or "https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php"
    captured_at_str = captured_at or _current_timestamp()

    table_match = re.search(r"<table[^>]*summary=[\"']listado de convocatorias[\"'][^>]*>(.*?)</table>", html_content, re.DOTALL | re.IGNORECASE)
    if not table_match:
        return []

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(1), re.DOTALL | re.IGNORECASE)
    candidates: list[dict] = []

    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.IGNORECASE)
        if len(cells) < 4:
            continue

        clean_cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in cells]
        cas_code = clean_cells[0]
        if not re.match(r"CAS\s*[0-9]+-202[0-9]", cas_code, re.IGNORECASE):
            continue

        objeto = clean_cells[2]
        unidad = clean_cells[3]

        # Extract links
        links = re.findall(r"<a\s+[^>]*href=[\'\"]([^\'\"]+)[\'\"][^>]*>(.*?)</a>", r, re.DOTALL | re.IGNORECASE)
        bases_pdf = None
        has_final_acta = False

        for href, link_html in links:
            l_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", link_html)).strip()
            full_href = urljoin(effective_url, href)
            if href.lower().endswith(".pdf"):
                if not bases_pdf or "convocatoria" in l_text.lower() or "bases" in l_text.lower():
                    bases_pdf = full_href
            if any(act in l_text.lower() or act in href.lower() for act in ("entrevista", "resultado", "final", "comunicado")):
                has_final_acta = True

        # Skip concluded processes unless explicitly requested
        if has_final_acta and not include_closed:
            continue

        # Extract position name from Objeto
        # e.g.: "Contratar a un/a (01) Bachiller... para que preste servicios como Analista en Desarrollo de Sistemas en la Oficina..."
        title_match = re.search(r"para que preste servicios como\s+(.*?)\s+(?:en la |en el |de la |para la )", objeto, re.IGNORECASE)
        if not title_match:
            title_match = re.search(r"CONTRATAR(?: LOS SERVICIOS DE)?\s+(?:A\s+)?(?:UN/A|TRES)?\s*(?:\([0-9]+\))?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s/]+?)(?:\s+EN LA|\s+DE LA|$)", objeto, re.IGNORECASE)

        if title_match:
            job_title = title_match.group(1).strip()
        else:
            job_title = f"{cas_code} - {unidad}"

        # Clean title capitalization
        job_title = re.sub(r"\s+", " ", job_title).strip()

        # Extract requirements snippet from Objeto
        req_match = re.search(r"Contratar\s+(?:por suplencia\s+)?a\s+(?:un/a\s+|tres\s+)?\(?[0-9]*\)?\s*(.*?),\s*para que preste", objeto, re.IGNORECASE)
        requirements = req_match.group(1).strip() if req_match else "Requisitos detallados en las bases oficiales CAS."

        # Format candidate ID
        cas_slug = re.sub(r"[^a-zA-Z0-9]+", "-", cas_code).strip("-")
        candidate_id = f"CAND-{source_id}-{cas_slug}"
        ext_ref = cas_code

        proposed = _empty_proposed()
        proposed["title"] = job_title
        proposed["employer"] = employer
        proposed["publisher"] = publisher
        proposed["externalReference"] = ext_ref
        proposed["applyUrl"] = "https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php"
        proposed["location"] = "Lima, Perú"
        proposed["mode"] = "No informado"
        proposed["opportunityType"] = "Contratación Administrativa de Servicios (CAS)"
        proposed["requirements"] = requirements

        # Year from CAS code
        year_m = re.search(r"-(\d{4})", cas_code)
        if year_m:
            proposed["publishedAt"] = f"{year_m.group(1)}-01-15"

        cand_record = _build_candidate_record(
            candidate_id=candidate_id,
            source_id=source_id,
            source_url=bases_pdf or effective_url,
            captured_at=captured_at_str,
            proposed=proposed,
        )

        if has_final_acta:
            cand_record["editorialReview"]["decisionNote"] = "Proceso CAS con actas o resultados en portal oficial."

        candidates.append(cand_record)

    return candidates


def fetch_defensoria_cas(
    source: dict,
    *,
    request_count: int = 0,
    captured_at: str | None = None,
) -> list[dict]:
    """Fetches Defensoría del Pueblo CAS opportunities live."""
    official_url = source.get("officialUrl") or "https://www.defensoria.gob.pe/convocatorias/convocatorias-cas.php"
    html = _fetch_html(official_url)
    return transform_defensoria_html(
        source,
        html,
        source_url=official_url,
        captured_at=captured_at,
    )


# =============================================================================
# 3. HiringRoom Multi-Tenant Adapter (HTML, OpenGraph & Schema.org JobPosting)
# =============================================================================

def _clean_hiringroom_title(raw_title: str) -> str:
    """Cleans common prefixes and employer suffixes from HiringRoom vacancy titles."""
    t = raw_title.strip()
    t = re.sub(r"^Oportunidad\s+de\s+Empleo:\s*", "", t, flags=re.I)
    t = re.sub(r"^Nuevas\s+oportunidades\s+de\s+empleo:\s*", "", t, flags=re.I)
    t = re.sub(r"\s+en\s+[A-Z0-9\s.,&-]+$", "", t, flags=re.I)
    t = re.sub(r"^[\s🚀🔥*•\-]+", "", t).strip()
    t = re.sub(r"[\s🚀🔥*•\-]+$", "", t).strip()
    return re.sub(r"\s+", " ", t).strip()


def _parse_hiringroom_vacancy_html(
    source: dict,
    html_content: str,
    *,
    detail_url: str,
    captured_at: str | None = None,
) -> dict | None:
    """Parses a HiringRoom vacancy detail page when JSON-LD is absent, extracting OpenGraph and DOM metadata."""
    if not html_content or not isinstance(html_content, str):
        return None

    # Title extraction: og:title -> <title>
    og_title_m = re.search(r'<meta[^>]*property=[\'"]og:title[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html_content, re.I)
    if og_title_m:
        raw_title = html.unescape(og_title_m.group(1))
    else:
        title_tag_m = re.search(r"<title>(.*?)</title>", html_content, re.I | re.DOTALL)
        raw_title = html.unescape(title_tag_m.group(1)) if title_tag_m else ""

    clean_title = _clean_hiringroom_title(raw_title)
    if not clean_title or clean_title.lower() in ("base general", "oportunidad de empleo", "empleo", "n/a"):
        # Not a concrete position
        return None

    source_id = str(source.get("id", "hiringroom-board"))
    employer = str(source.get("employer") or "Empresa Confidencial")
    publisher = str(source.get("publisher") or f"Portal de Empleo {employer} (HiringRoom)")
    captured_at_str = captured_at or _current_timestamp()

    # Description extraction: og:description -> clean text
    desc_m = re.search(r'<meta[^>]*property=[\'"]og:description[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html_content, re.I)
    if desc_m:
        raw_desc = html.unescape(desc_m.group(1))
        clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
        clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
    else:
        clean_desc = ""

    # Location extraction: <span class="hr-Location-pin"></span> or hero container
    loc_m = re.search(r'hr-Location-pin[^>]*></span>\s*([^<\r\n]+)', html_content, re.I)
    if not loc_m:
        loc_m = re.search(r'title=[\'"]([^\'"]*(?:Lima|Peru|Per[úu])[^\'"]*)[\'"]', html_content, re.I)

    raw_loc = loc_m.group(1).strip() if loc_m else ""
    if any(k in raw_loc.lower() for k in ("peru", "perú", "lima")):
        loc_l = raw_loc.lower()
        if "san isidro" in loc_l:
            location = "San Isidro, Lima, Perú"
        elif "surquillo" in loc_l:
            location = "Surquillo, Lima, Perú"
        elif "miraflores" in loc_l:
            location = "Miraflores, Lima, Perú"
        elif "cercado" in loc_l:
            location = "Lima, Perú"
        elif "arequipa" in loc_l:
            location = "Arequipa, Perú"
        elif "trujillo" in loc_l or "libertad" in loc_l:
            location = "La Libertad, Perú"
        else:
            location = "Lima, Perú"
    else:
        location = raw_loc if raw_loc else "Lima, Perú"

    # Modality extraction
    if re.search(r'\b(remoto|remote)\b', clean_title, re.I):
        mode = "Remoto"
    elif re.search(r'\b(h[íi]brido|hybrid)\b', clean_title, re.I):
        mode = "Híbrido"
    elif re.search(r'\b(presencial|on-site|onsite)\b', clean_title, re.I):
        mode = "Presencial"
    elif re.search(r'\b(h[íi]brido|hybrid)\b', html_content, re.I):
        mode = "Híbrido"
    else:
        # Check specific dynamic modality span: <span class="... hr-Remote/hr-Company/hrc-black"></span>[Text]
        mod_span_m = re.search(r'class="[^"]*(?:hr-Remote|hr-Company|hrc-black)[^"]*"[^>]*>\s*</span>\s*([a-zA-ZáéíóúÁÉÍÓÚ]+)', html_content, re.I)
        if mod_span_m:
            span_val = mod_span_m.group(1).strip().lower()
            if "remot" in span_val:
                mode = "Remoto"
            elif "hibrid" in span_val or "híbrid" in span_val:
                mode = "Híbrido"
            elif "presenc" in span_val or "company" in span_val:
                mode = "Presencial"
            else:
                mode = "No informado"
        else:
            # Check class directly in span
            if re.search(r'class="[^"]*\bhr-Remote\b[^"]*"', html_content):
                mode = "Remoto"
            elif re.search(r'class="[^"]*\bhr-Company\b[^"]*"', html_content):
                mode = "Presencial"
            else:
                mode = "No informado"

    # Opportunity type
    lower_comb = f"{clean_title} {clean_desc}".lower()
    if any(k in lower_comb for k in ("prácticas", "practicas", "practicante", "intern")):
        opp_type = "Prácticas"
    else:
        opp_type = "Empleo"

    # Vacancy URL and ID extraction
    og_url_m = re.search(r'<meta[^>]*property=[\'"]og:url[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html_content, re.I)
    effective_detail_url = og_url_m.group(1).strip() if og_url_m else detail_url

    v_match = re.search(r"/jobs/get_vacancy/([a-f0-9]{24})", effective_detail_url)
    if not v_match:
        v_match = re.search(r"/jobs/get_vacancy/([a-f0-9]{24})", html_content)

    if v_match:
        vacancy_id = v_match.group(1)
        if not effective_detail_url or "/jobs/get_vacancy/" not in effective_detail_url:
            effective_detail_url = urljoin(effective_detail_url or "https://hiringroom.com/", f"/jobs/get_vacancy/{vacancy_id}")
    else:
        vacancy_id = hashlib.sha1(effective_detail_url.encode("utf-8")).hexdigest()[:16]

    candidate_id = f"CAND-{source_id}-{vacancy_id}"
    ext_ref = f"{source_id.upper()}-{vacancy_id}"

    proposed = _empty_proposed()
    proposed["title"] = clean_title
    proposed["employer"] = employer
    proposed["publisher"] = publisher
    proposed["externalReference"] = ext_ref
    proposed["applyUrl"] = effective_detail_url
    proposed["location"] = location
    proposed["mode"] = mode
    proposed["opportunityType"] = opp_type
    proposed["requirements"] = clean_desc[:500] if clean_desc else f"Oportunidad laboral en {employer} publicada en HiringRoom."

    cand_record = _build_candidate_record(
        candidate_id=candidate_id,
        source_id=source_id,
        source_url=effective_detail_url,
        captured_at=captured_at_str,
        proposed=proposed,
    )
    cand_record["editorialReview"]["decisionNote"] = f"Vacante publicada en portal HiringRoom de {employer}."
    return cand_record


def transform_hiringroom_html(
    source: dict,
    html_content: str,
    *,
    source_url: str | None = None,
    captured_at: str | None = None,
    detail_fetcher: callable | None = None,
) -> list[dict]:
    """Transforms HiringRoom portal HTML into Candidate Schema 2 records."""
    source_id = str(source.get("id", "hiringroom-board"))
    captured_at_str = captured_at or _current_timestamp()
    effective_url = source_url or source.get("officialUrl") or "https://hiringroom.com/"

    candidates: list[dict] = []

    # 1. If the HTML page itself contains a Schema.org JobPosting, parse directly
    direct_candidates = extract_candidates_from_html(
        source,
        html_content,
        source_url=effective_url,
        captured_at=captured_at_str,
    )
    if direct_candidates:
        candidates.extend(direct_candidates)

    # 2. If no direct candidates from JSON-LD, try parsing as single vacancy detail page
    if not candidates:
        single_cand = _parse_hiringroom_vacancy_html(
            source,
            html_content,
            detail_url=effective_url,
            captured_at=captured_at_str,
        )
        if single_cand:
            candidates.append(single_cand)

    # 3. Find job links on board pages
    v_ids = re.findall(r"/jobs/get_vacancy/([a-f0-9]{24})", html_content)
    raw_hrefs = [f"/jobs/get_vacancy/{vid}" for vid in v_ids]
    if not raw_hrefs:
        raw_hrefs = re.findall(r"href=[\'\"]([^'\"<>]*?/jobs/[a-zA-Z0-9_-]+)[\'\"]", html_content)

    job_urls: list[str] = []
    for h in raw_hrefs:
        full = urljoin(effective_url, h)
        if full not in job_urls and full != effective_url:
            job_urls.append(full)

    # If detail_fetcher is provided, fetch job detail pages
    if detail_fetcher:
        for href in job_urls:
            try:
                detail_html = detail_fetcher(href)
                cands = extract_candidates_from_html(
                    source,
                    detail_html,
                    source_url=href,
                    captured_at=captured_at_str,
                )
                if not cands:
                    cand = _parse_hiringroom_vacancy_html(
                        source,
                        detail_html,
                        detail_url=href,
                        captured_at=captured_at_str,
                    )
                    if cand:
                        cands = [cand]
                candidates.extend(cands)
            except Exception:
                continue

    return candidates


def fetch_hiringroom_board(
    source: dict,
    *,
    request_count: int = 0,
    captured_at: str | None = None,
) -> list[dict]:
    """Fetches HiringRoom board and parses job detail pages."""
    official_url = source.get("officialUrl") or "https://hiringroom.com/"
    html_content = _fetch_html(official_url, timeout=15)
    captured_at_str = captured_at or _current_timestamp()

    max_reqs = int(source.get("maxRequestsPerRun") or 10)

    # Find unique vacancy links
    v_ids = sorted(list(set(re.findall(r"/jobs/get_vacancy/([a-f0-9]{24})", html_content))))
    if v_ids:
        job_urls = [urljoin(official_url, f"/jobs/get_vacancy/{vid}") for vid in v_ids][:max_reqs]
    else:
        raw_hrefs = sorted(list(set(re.findall(r"href=[\'\"]([^'\"<>]*?/jobs/[a-zA-Z0-9_-]+)[\'\"]", html_content))))
        job_urls = [urljoin(official_url, h) for h in raw_hrefs if urljoin(official_url, h) != official_url][:max_reqs]

    candidates: list[dict] = []
    for href in job_urls:
        try:
            detail_html = _fetch_html(href, timeout=10)
            cands = extract_candidates_from_html(
                source,
                detail_html,
                source_url=href,
                captured_at=captured_at_str,
            )
            if not cands:
                cand = _parse_hiringroom_vacancy_html(
                    source,
                    detail_html,
                    detail_url=href,
                    captured_at=captured_at_str,
                )
                if cand:
                    cands = [cand]
            candidates.extend(cands)
        except Exception:
            continue

    return candidates


# =============================================================================
# 4. Gob.pe Convocatorias Adapter (INDECOPI & Peruvian State Entities)
# =============================================================================

def transform_gobpe_indecopi_html(
    source: dict,
    html_content: str,
    *,
    source_url: str | None = None,
    captured_at: str | None = None,
    detail_fetcher: callable | None = None,
    pdf_fetcher: callable | None = None,
    include_closed: bool = True,
    opp_type_override: str | None = None,
) -> list[dict]:
    """Transforms Gob.pe / INDECOPI convocatorias table into Candidate Schema 2 records."""
    source_id = str(source.get("id", "gobpe-indecopi-convocatorias"))
    employer = str(source.get("employer") or "INDECOPI")
    publisher = str(source.get("publisher") or "Instituto Nacional de Defensa de la Competencia y de la Protección de la Propiedad Intelectual (INDECOPI)")
    effective_url = source_url or source.get("officialUrl") or "https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-cas/"
    captured_at_str = captured_at or _current_timestamp()

    # Extract table rows
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html_content, re.DOTALL | re.IGNORECASE)
    candidates: list[dict] = []

    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.IGNORECASE)
        if len(cells) < 6:
            continue

        clean_cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in cells]
        proceso = clean_cells[0]
        if not re.search(r"\d{2,4}-\d{4}", proceso):
            continue

        puesto = clean_cells[1]
        vacantes = clean_cells[2]
        unidad = clean_cells[3]
        gobpe_links = re.findall(r"href=[\'\"]([^\'\"]+)[\'\"]", cells[4], re.IGNORECASE)
        gobpe_pub_url = urljoin(effective_url, gobpe_links[0]) if gobpe_links else effective_url
        estado = clean_cells[5]
        postulacion = clean_cells[6] if len(clean_cells) > 6 else ""

        is_closed = any(k in estado.lower() or k in postulacion.lower() for k in ("finalizada", "concluida", "cancelada", "desierta", "concluidas"))
        if is_closed and not include_closed:
            continue

        # Opportunity type determination
        if opp_type_override:
            opp_type = opp_type_override
        elif any(k in f"{puesto} {effective_url} {proceso}".lower() for k in ("prac", "práctica", "practicante")):
            opp_type = "Prácticas"
        else:
            opp_type = "Contratación Administrativa de Servicios (CAS)"

        # Title formatting: include unidad if informative and not in puesto
        if unidad and unidad.upper() not in puesto.upper():
            title = f"{puesto} ({unidad})"
        else:
            title = puesto
        title = re.sub(r"\s+", " ", title).strip()

        # Location mapping (detect regional offices or default to Lima)
        u_lower = unidad.lower()
        if "arequipa" in u_lower:
            location = "Arequipa, Perú"
        elif "cajamarca" in u_lower:
            location = "Cajamarca, Perú"
        elif "chimbote" in u_lower:
            location = "Chimbote, Perú"
        elif "pasco" in u_lower:
            location = "Pasco, Perú"
        elif "san martin" in u_lower or "tarapoto" in u_lower:
            location = "San Martín, Perú"
        elif "cusco" in u_lower:
            location = "Cusco, Perú"
        elif "piura" in u_lower:
            location = "Piura, Perú"
        elif "lambayeque" in u_lower or "chiclayo" in u_lower:
            location = "Lambayeque, Perú"
        elif "huancayo" in u_lower or "junin" in u_lower or "junín" in u_lower:
            location = "Junín, Perú"
        elif "la libertad" in u_lower or "trujillo" in u_lower:
            location = "La Libertad, Perú"
        else:
            location = "Lima, Perú"

        type_slug = "prac" if opp_type == "Prácticas" else "cas"
        proceso_slug = re.sub(r"[^a-zA-Z0-9]+", "-", proceso).strip("-").lower()
        candidate_id = f"CAND-{source_id}-{type_slug}-{proceso_slug}"
        ext_ref = f"INDECOPI-{type_slug.upper()}-{proceso}"

        proposed = _empty_proposed()
        proposed["title"] = title
        proposed["employer"] = employer
        proposed["publisher"] = publisher
        proposed["externalReference"] = ext_ref
        proposed["applyUrl"] = "https://oportunidadeslaborales.indecopi.gob.pe/"
        proposed["location"] = location
        proposed["mode"] = "No informado"
        proposed["opportunityType"] = opp_type
        proposed["requirements"] = f"Bases oficiales publicadas en Gob.pe para {puesto} en {unidad}."

        # Parse deadline date from postulation string (e.g. "Podrás postular el 4/12/2026")
        d_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", postulacion)
        if d_match:
            d_day, d_month, d_year = d_match.groups()
            proposed["deadline"] = f"{d_year}-{int(d_month):02d}-{int(d_day):02d}"
            proposed["publishedAt"] = f"{d_year}-01-15"
        else:
            y_m = re.search(r"-(\d{4})", proceso)
            if y_m:
                proposed["publishedAt"] = f"{y_m.group(1)}-01-15"

        # Optional detail page / PDF bases inspection
        bases_pdf_url = None
        if detail_fetcher and gobpe_pub_url.startswith("https://www.gob.pe/"):
            try:
                detail_html = detail_fetcher(gobpe_pub_url)
                if detail_html:
                    pdf_links = re.findall(r"href=[\'\"]([^\'\"]+\.pdf[^\'\"]*)[\'\"]", detail_html, re.IGNORECASE)
                    for pl in pdf_links:
                        full_pl = urljoin(gobpe_pub_url, pl)
                        if "cdn.www.gob.pe" in full_pl and ("informacion" in full_pl.lower() or "perfil" in full_pl.lower() or "base" in full_pl.lower()):
                            bases_pdf_url = full_pl
                            break
                        elif not bases_pdf_url and "cdn.www.gob.pe" in full_pl:
                            bases_pdf_url = full_pl
            except Exception:
                pass

        if bases_pdf_url and pdf_fetcher:
            try:
                pdf_text = pdf_fetcher(bases_pdf_url)
                if pdf_text:
                    # Look for salary/subvención
                    sal_m = re.search(r"(?:remuneraci[oó]n|subvenci[oó]n|pago)[^0-9]*?(S/\.?\s*[0-9,]+(?:\.[0-9]{2})?)", pdf_text, re.IGNORECASE)
                    if not sal_m:
                        sal_m = re.search(r"(S/\.?\s*[0-9,]+(?:\.[0-9]{2})?)", pdf_text)
                    if sal_m:
                        proposed["salary"] = re.sub(r"\s+", "", sal_m.group(1))

                    # Look for degree/education
                    acad_m = re.search(r"(?:formaci[oó]n acad[eé]mica|grado acad[eé]mico|perfil)[^:]*?:\s*([^\n\r.]+)", pdf_text, re.IGNORECASE)
                    if acad_m:
                        proposed["requirements"] = acad_m.group(1).strip()
            except Exception:
                pass

        cand_record = _build_candidate_record(
            candidate_id=candidate_id,
            source_id=source_id,
            source_url=bases_pdf_url or gobpe_pub_url,
            captured_at=captured_at_str,
            proposed=proposed,
        )

        note_parts = [f"Proceso {proceso}"]
        if estado:
            note_parts.append(f"estado: {estado}")
        if postulacion:
            note_parts.append(postulacion)
        cand_record["editorialReview"]["decisionNote"] = " | ".join(note_parts)

        candidates.append(cand_record)

    return candidates


def fetch_gobpe_convocatorias(
    source: dict,
    *,
    request_count: int = 0,
    captured_at: str | None = None,
    include_closed: bool = True,
    max_details: int = 5,
) -> list[dict]:
    """Fetches official convocatorias published by INDECOPI on Gob.pe."""
    official_url = source.get("officialUrl") or "https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-cas/"
    practicas_url = source.get("practicasUrl") or "https://oportunidadeslaborales.indecopi.gob.pe/convocatorias-practicantes/"

    candidates: list[dict] = []
    details_fetched = 0

    def detail_fetcher(url: str) -> str:
        nonlocal details_fetched
        if details_fetched >= max_details:
            return ""
        details_fetched += 1
        return _fetch_html(url, timeout=10)

    def pdf_fetcher(url: str) -> str:
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
            opener = PermissiveHttpsOpener.get_opener()
            with opener.open(req, timeout=10) as resp:
                pdf_bytes = resp.read(MAX_RESPONSE_BYTES)
                return extract_text_from_pdf_bytes(pdf_bytes)
        except Exception:
            return ""

    # 1. Fetch CAS page
    try:
        html_cas = _fetch_html(official_url, timeout=15)
        cands_cas = transform_gobpe_indecopi_html(
            source,
            html_cas,
            source_url=official_url,
            captured_at=captured_at,
            detail_fetcher=detail_fetcher,
            pdf_fetcher=pdf_fetcher,
            include_closed=include_closed,
            opp_type_override="Contratación Administrativa de Servicios (CAS)",
        )
        candidates.extend(cands_cas)
    except Exception:
        pass

    # 2. Fetch Prácticas page
    try:
        html_prac = _fetch_html(practicas_url, timeout=15)
        cands_prac = transform_gobpe_indecopi_html(
            source,
            html_prac,
            source_url=practicas_url,
            captured_at=captured_at,
            detail_fetcher=detail_fetcher,
            pdf_fetcher=pdf_fetcher,
            include_closed=include_closed,
            opp_type_override="Prácticas",
        )
        candidates.extend(cands_prac)
    except Exception:
        pass

    return candidates

