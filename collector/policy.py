"""Fail-closed, dependency-free source access policy."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "sources.json"
APPROVED_TERMS = {"approved_public_api", "approved_employer_site"}
APPROVED_RIGHTS = {"metadata_only_approved", "content_reuse_approved"}
FETCH_CONNECTORS = {"greenhouse-job-board", "lever-postings"}


def load_source_registry() -> dict:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if registry.get("schemaVersion") != 1 or not isinstance(registry.get("sources"), list):
        raise ValueError("Unsupported source registry schema.")
    defaults = registry.get("defaultPolicy", {})
    registry["sources"] = [{**defaults, **source} for source in registry["sources"]]
    return registry


def find_source(registry: dict, source_id: str) -> dict | None:
    return next((source for source in registry["sources"] if source["id"] == source_id), None)


def authorize_fetch(source: dict | None, candidate_url: str, request_count: int) -> dict:
    def deny(reason: str) -> dict:
        return {"allowed": False, "reason": reason}

    if source is None:
        return deny("unknown_source")
    if not source.get("enabled"):
        return deny("source_disabled")
    if source.get("connector") not in FETCH_CONNECTORS:
        return deny("connector_not_implemented")
    if source.get("termsReview") not in APPROVED_TERMS:
        return deny("terms_not_approved")
    if source.get("rightsReview") not in APPROVED_RIGHTS:
        return deny("reuse_rights_not_approved")
    if source.get("kind") != "public_ats_api" and source.get("robotsReview") != "reviewed_allowed":
        return deny("robots_not_reviewed_allowed")
    budget = source.get("maxRequestsPerRun")
    if not isinstance(request_count, int) or request_count < 0 or not isinstance(budget, int) or request_count >= budget:
        return deny("source_request_budget_exceeded")

    try:
        parsed = urlsplit(candidate_url)
    except ValueError:
        return deny("invalid_url")
    if parsed.scheme != "https":
        return deny("https_required")
    if parsed.username or parsed.password:
        return deny("embedded_credentials_forbidden")
    if (parsed.hostname or "").lower() not in source.get("allowedHosts", []):
        return deny("host_not_allowlisted")
    return {"allowed": True, "reason": "policy_approved", "url": candidate_url, "minDelayMs": source.get("minDelayMs", 0)}


def authorize_redirect(source: dict | None, redirect_url: str, request_count: int) -> dict:
    if not source or not source.get("allowRedirects"):
        return {"allowed": False, "reason": "redirects_not_enabled"}
    return authorize_fetch(source, redirect_url, request_count)


def public_record_from_posting(source: dict, posting: dict, captured_at: str) -> dict:
    if not source or not posting.get("url") or not posting.get("title") or not posting.get("employer"):
        raise ValueError("Source and posting identity fields are required.")
    parsed = urlsplit(posting["url"])
    allowed_hosts = source.get("allowedPostingHosts", source.get("allowedHosts", []))
    if parsed.scheme != "https" or parsed.username or parsed.password or (parsed.hostname or "").lower() not in allowed_hosts:
        raise ValueError("Canonical posting URL is not permitted by this source.")
    return {
        "sourceId": source["id"],
        "externalId": str(posting.get("externalId") or posting.get("id") or posting["url"]),
        "employer": str(posting["employer"]).strip(),
        "title": str(posting["title"]).strip(),
        "canonicalUrl": posting["url"],
        "capturedAt": captured_at,
        "verificationStatus": "unverified",
        "publicationStatus": "unknown",
        "fullDescription": None,
    }
