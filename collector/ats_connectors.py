"""ATS API adapters producing Schema 2 candidate records; no private candidate data stored."""

from __future__ import annotations

import json
import ssl
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

from .policy import authorize_fetch, public_record_from_posting


MAX_RESPONSE_BYTES = 5 * 1024 * 1024

PROPOSED_FIELDS = (
    "title", "employer", "publisher", "externalReference", "applyUrl",
    "publishedAt", "deadline", "location", "mode", "opportunityType",
    "salary", "benefits", "requirements",
)


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def _fetch_json(url: str) -> dict | list:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), RejectRedirects())
    try:
        with opener.open(request, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "application/json" not in content_type:
                raise ValueError("source_response_not_json")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        if 300 <= error.code < 400:
            raise ValueError("redirect_requires_explicit_source_review") from error
        raise ValueError(f"source_http_{error.code}") from error
    except (TimeoutError, URLError) as error:
        raise ValueError("source_network_error") from error
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("source_response_too_large")
    return json.loads(body.decode("utf-8"))


def _checked_url(source: dict, url: str, request_count: int) -> str:
    decision = authorize_fetch(source, url, request_count)
    if not decision["allowed"]:
        raise ValueError(f"source_policy_{decision['reason']}")
    return decision["url"]


def _current_timestamp() -> str:
    return datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec="seconds")


def _safe_str(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return None


def _is_valid_https_url(url: object) -> tuple[bool, str]:
    if not isinstance(url, str) or not url.strip():
        return False, ""
    try:
        parsed = urlsplit(url.strip())
        if parsed.scheme == "https" and parsed.netloc and not parsed.username and not parsed.password:
            return True, (parsed.hostname or "").lower()
    except ValueError:
        pass
    return False, ""


def _empty_proposed() -> dict[str, str | None]:
    return {field: None for field in PROPOSED_FIELDS}


def _build_candidate_record(
    *,
    candidate_id: str,
    source_id: str,
    source_url: str,
    captured_at: str,
    proposed: dict[str, str | None],
) -> dict:
    field_evidence = []
    apply_url = proposed.get("applyUrl")
    for field, value in proposed.items():
        if value not in (None, ""):
            evidence_url = apply_url if field == "applyUrl" and apply_url else source_url
            field_evidence.append({
                "field": field,
                "url": evidence_url,
                "observedAt": captured_at,
            })

    return {
        "candidateId": candidate_id,
        "sourceId": source_id,
        "sourceUrl": source_url,
        "capturedAt": captured_at,
        "captureMethod": "manual",
        "proposed": proposed,
        "fieldEvidence": field_evidence,
        "editorialReview": {
            "status": "pending_review",
            "reviewer": None,
            "reviewedAt": None,
            "decisionNote": None,
        },
    }


def transform_greenhouse_payload(
    source: dict,
    payload: dict,
    *,
    captured_at: str | None = None,
    source_url: str | None = None,
) -> list[dict]:
    if source.get("connector") != "greenhouse-job-board" or not source.get("boardToken") or not source.get("employer"):
        raise ValueError("greenhouse_source_configuration_incomplete")
    token = str(source["boardToken"])
    if not token.isascii() or not token.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_greenhouse_board_token")

    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("greenhouse_unexpected_response_shape")

    if not source_url:
        source_url = f"https://boards-api.greenhouse.io/v1/boards/{quote(token, safe='')}/jobs"

    is_https, host = _is_valid_https_url(source_url)
    if not is_https or host not in [h.lower() for h in source.get("allowedHosts", [])]:
        raise ValueError("source_url_not_allowlisted")

    captured_at_str = captured_at or _current_timestamp()
    source_id = str(source.get("id", "greenhouse-public-job-board-template"))
    employer = _safe_str(source.get("employer"))
    publisher = _safe_str(source.get("publisher")) or employer
    allowed_posting_hosts = [h.lower() for h in source.get("allowedPostingHosts", source.get("allowedHosts", []))]

    records: list[dict] = []
    seen_ids: set[str] = set()

    for job in payload["jobs"]:
        if not isinstance(job, dict):
            continue
        raw_id = job.get("id")
        if raw_id is None:
            continue
        ext_id = str(raw_id).strip()
        if not ext_id:
            continue

        title = _safe_str(job.get("title"))
        if not title:
            continue

        raw_url = _safe_str(job.get("absolute_url"))
        if not raw_url:
            continue
        url_ok, url_host = _is_valid_https_url(raw_url)
        if not url_ok or url_host not in allowed_posting_hosts:
            continue

        if ext_id in seen_ids:
            continue
        seen_ids.add(ext_id)

        proposed = _empty_proposed()
        proposed["title"] = title
        proposed["employer"] = employer
        proposed["publisher"] = publisher
        proposed["externalReference"] = ext_id
        proposed["applyUrl"] = raw_url

        loc = job.get("location")
        loc_name = _safe_str(loc.get("name")) if isinstance(loc, dict) else None
        if loc_name:
            proposed["location"] = loc_name
            if loc_name.lower() in ("remote", "remoto"):
                proposed["mode"] = "Remoto"

        for date_key in ("first_published_at", "published_at", "created_at"):
            raw_date = job.get(date_key)
            if isinstance(raw_date, str) and raw_date.strip():
                try:
                    dt = datetime.fromisoformat(raw_date.strip().replace("Z", "+00:00"))
                    if 2000 <= dt.year <= 2100:
                        proposed["publishedAt"] = dt.date().isoformat()
                        break
                except (ValueError, OverflowError):
                    pass

        candidate_id = f"CAND-{source_id}-{ext_id}"
        record = _build_candidate_record(
            candidate_id=candidate_id,
            source_id=source_id,
            source_url=source_url,
            captured_at=captured_at_str,
            proposed=proposed,
        )
        records.append(record)

    return records


def transform_lever_payload(
    source: dict,
    payload: list,
    *,
    captured_at: str | None = None,
    source_url: str | None = None,
) -> list[dict]:
    if source.get("connector") != "lever-postings" or not source.get("site") or not source.get("employer"):
        raise ValueError("lever_source_configuration_incomplete")
    site = str(source["site"])
    if not site.isascii() or not site.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_lever_site")

    origin = source.get("apiOrigin", "https://api.lever.co")
    parsed_origin = urlsplit(origin)
    if (parsed_origin.scheme != "https" or parsed_origin.path not in ("", "/") or parsed_origin.username
            or parsed_origin.password or (parsed_origin.hostname or "").lower() not in [h.lower() for h in source.get("allowedHosts", [])]):
        raise ValueError("lever_api_origin_not_allowlisted")

    if not isinstance(payload, list):
        raise ValueError("lever_unexpected_response_shape")

    if not source_url:
        source_url = f"{origin.rstrip('/')}/v0/postings/{quote(site, safe='')}?mode=json"

    is_https, host = _is_valid_https_url(source_url)
    if not is_https or host not in [h.lower() for h in source.get("allowedHosts", [])]:
        raise ValueError("source_url_not_allowlisted")

    captured_at_str = captured_at or _current_timestamp()
    source_id = str(source.get("id", "lever-public-postings-template"))
    employer = _safe_str(source.get("employer"))
    publisher = _safe_str(source.get("publisher")) or employer
    allowed_posting_hosts = [h.lower() for h in source.get("allowedPostingHosts", source.get("allowedHosts", []))]

    records: list[dict] = []
    seen_ids: set[str] = set()

    for posting in payload:
        if not isinstance(posting, dict):
            continue
        raw_id = posting.get("id")
        if raw_id is None:
            continue
        ext_id = str(raw_id).strip()
        if not ext_id:
            continue

        title = _safe_str(posting.get("text"))
        if not title:
            continue

        raw_url = _safe_str(posting.get("applyUrl")) or _safe_str(posting.get("hostedUrl"))
        if not raw_url:
            continue
        url_ok, url_host = _is_valid_https_url(raw_url)
        if not url_ok or url_host not in allowed_posting_hosts:
            continue

        if ext_id in seen_ids:
            continue
        seen_ids.add(ext_id)

        proposed = _empty_proposed()
        proposed["title"] = title
        proposed["employer"] = employer
        proposed["publisher"] = publisher
        proposed["externalReference"] = ext_id
        proposed["applyUrl"] = raw_url

        categories = posting.get("categories") if isinstance(posting.get("categories"), dict) else {}
        loc_name = _safe_str(categories.get("location"))
        if loc_name:
            proposed["location"] = loc_name

        commitment = _safe_str(categories.get("commitment"))
        if commitment:
            proposed["opportunityType"] = commitment

        workplace = _safe_str(posting.get("workplaceType"))
        if workplace:
            w_lower = workplace.lower()
            if w_lower == "remote":
                proposed["mode"] = "Remoto"
            elif w_lower == "hybrid":
                proposed["mode"] = "Híbrido"
            elif w_lower in ("onsite", "on-site"):
                proposed["mode"] = "Presencial"

        created_at_val = posting.get("createdAt")
        if isinstance(created_at_val, (int, float)) and not isinstance(created_at_val, bool) and created_at_val > 0:
            try:
                dt = datetime.fromtimestamp(created_at_val / 1000, tz=timezone.utc)
                if 2000 <= dt.year <= 2100:
                    proposed["publishedAt"] = dt.date().isoformat()
            except (ValueError, OverflowError, OSError):
                pass

        candidate_id = f"CAND-{source_id}-{ext_id}"
        record = _build_candidate_record(
            candidate_id=candidate_id,
            source_id=source_id,
            source_url=source_url,
            captured_at=captured_at_str,
            proposed=proposed,
        )
        records.append(record)

    return records


def fetch_greenhouse_board(
    source: dict,
    *,
    request_count: int,
    captured_at: str | None = None,
) -> list[dict]:
    if source.get("connector") != "greenhouse-job-board" or not source.get("boardToken") or not source.get("employer"):
        raise ValueError("greenhouse_source_configuration_incomplete")
    token = str(source["boardToken"])
    if not token.isascii() or not token.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_greenhouse_board_token")
    url = f"https://boards-api.greenhouse.io/v1/boards/{quote(token, safe='')}/jobs"
    checked_url = _checked_url(source, url, request_count)
    payload = _fetch_json(checked_url)
    return transform_greenhouse_payload(source, payload, captured_at=captured_at, source_url=checked_url)


def fetch_lever_board(
    source: dict,
    *,
    request_count: int,
    captured_at: str | None = None,
) -> list[dict]:
    if source.get("connector") != "lever-postings" or not source.get("site") or not source.get("employer"):
        raise ValueError("lever_source_configuration_incomplete")
    site = str(source["site"])
    if not site.isascii() or not site.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_lever_site")
    origin = source.get("apiOrigin", "https://api.lever.co")
    parsed_origin = urlsplit(origin)
    if (parsed_origin.scheme != "https" or parsed_origin.path not in ("", "/") or parsed_origin.username
            or parsed_origin.password or (parsed_origin.hostname or "").lower() not in [h.lower() for h in source.get("allowedHosts", [])]):
        raise ValueError("lever_api_origin_not_allowlisted")
    url = f"{origin.rstrip('/')}/v0/postings/{quote(site, safe='')}?mode=json"
    checked_url = _checked_url(source, url, request_count)
    payload = _fetch_json(checked_url)
    return transform_lever_payload(source, payload, captured_at=captured_at, source_url=checked_url)
