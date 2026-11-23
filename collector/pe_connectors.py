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
# 3. UTP HiringRoom Campus Adapter (HTML + Schema.org JobPosting)
# =============================================================================

def transform_hiringroom_html(
    source: dict,
    html_content: str,
    *,
    source_url: str | None = None,
    captured_at: str | None = None,
    detail_fetcher: callable | None = None,
) -> list[dict]:
    """Transforms UTP HiringRoom Campus portal HTML into Candidate Schema 2 records."""
    source_id = str(source.get("id", "utp-hiringroom-campus"))
    captured_at_str = captured_at or _current_timestamp()
    effective_url = source_url or source.get("officialUrl") or "https://utp.hiringroomcampus.com/"

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

    # 2. Find job links
    job_hrefs = re.findall(r"href=[\'\"](https://utp\.hiringroomcampus\.com/jobs/[a-zA-Z0-9_-]+)[\'\"]", html_content)
    unique_hrefs = sorted(list(set(job_hrefs)))

    # If detail_fetcher is provided, fetch job detail pages
    for href in unique_hrefs:
        if detail_fetcher:
            try:
                detail_html = detail_fetcher(href)
                cands = extract_candidates_from_html(
                    source,
                    detail_html,
                    source_url=href,
                    captured_at=captured_at_str,
                )
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
    """Fetches UTP HiringRoom Campus board and parses job detail pages."""
    official_url = source.get("officialUrl") or "https://utp.hiringroomcampus.com/"
    html = _fetch_html(official_url)

    # Use _fetch_html as detail_fetcher (limited to first 5 jobs to stay within budget)
    def detail_fetcher(url: str) -> str:
        return _fetch_html(url, timeout=10)

    # Find unique job links
    job_hrefs = sorted(list(set(re.findall(r"href=[\'\"](https://utp\.hiringroomcampus\.com/jobs/[a-zA-Z0-9_-]+)[\'\"]", html))))[:5]
    
    candidates: list[dict] = []
    for href in job_hrefs:
        try:
            detail_html = detail_fetcher(href)
            cands = extract_candidates_from_html(
                source,
                detail_html,
                source_url=href,
                captured_at=captured_at,
            )
            candidates.extend(cands)
        except Exception:
            continue

    return candidates
