"""Minimal public ATS API adapters; no descriptions or candidate data are stored."""

from __future__ import annotations

import json
import ssl
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

from .policy import authorize_fetch, public_record_from_posting


MAX_RESPONSE_BYTES = 5 * 1024 * 1024


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


def fetch_greenhouse_board(source: dict, *, request_count: int) -> list[dict]:
    if source.get("connector") != "greenhouse-job-board" or not source.get("boardToken") or not source.get("employer"):
        raise ValueError("greenhouse_source_configuration_incomplete")
    token = str(source["boardToken"])
    if not token.isascii() or not token.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_greenhouse_board_token")
    url = f"https://boards-api.greenhouse.io/v1/boards/{quote(token, safe='')}/jobs"
    payload = _fetch_json(_checked_url(source, url, request_count))
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("greenhouse_unexpected_response_shape")

    captured_at = datetime.now(timezone.utc).isoformat()
    records = []
    for job in payload["jobs"]:
        if not job.get("absolute_url") or not job.get("title") or job.get("id") is None:
            continue
        record = public_record_from_posting(source, {
            "externalId": job["id"], "employer": source["employer"],
            "title": job["title"], "url": job["absolute_url"],
        }, captured_at)
        record["location"] = (job.get("location") or {}).get("name")
        record["departments"] = [item["name"] for item in job.get("departments", []) if item.get("name")]
        record["offices"] = [item["name"] for item in job.get("offices", []) if item.get("name")]
        records.append(record)
    return records


def fetch_lever_board(source: dict, *, request_count: int) -> list[dict]:
    if source.get("connector") != "lever-postings" or not source.get("site") or not source.get("employer"):
        raise ValueError("lever_source_configuration_incomplete")
    site = str(source["site"])
    if not site.isascii() or not site.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_lever_site")
    origin = source.get("apiOrigin", "https://api.lever.co")
    parsed_origin = urlsplit(origin)
    if (parsed_origin.scheme != "https" or parsed_origin.path not in ("", "/") or parsed_origin.username
            or parsed_origin.password or (parsed_origin.hostname or "").lower() not in source.get("allowedHosts", [])):
        raise ValueError("lever_api_origin_not_allowlisted")
    url = f"{origin.rstrip('/')}/v0/postings/{quote(site, safe='')}?mode=json"
    payload = _fetch_json(_checked_url(source, url, request_count))
    if not isinstance(payload, list):
        raise ValueError("lever_unexpected_response_shape")

    captured_at = datetime.now(timezone.utc).isoformat()
    records = []
    for posting in payload:
        if not posting.get("hostedUrl") or not posting.get("text") or not posting.get("id"):
            continue
        record = public_record_from_posting(source, {
            "externalId": posting["id"], "employer": source["employer"],
            "title": posting["text"], "url": posting["hostedUrl"],
        }, captured_at)
        categories = posting.get("categories") or {}
        record["location"] = categories.get("location")
        record["department"] = categories.get("team")
        record["employmentType"] = categories.get("commitment")
        record["workplaceType"] = posting.get("workplaceType")
        records.append(record)
    return records
