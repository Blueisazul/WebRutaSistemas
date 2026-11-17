"""Deterministic canonical deduplicator and collision detector for Ruta Sistemas.

No probabilistic ML, no external dependencies, no destructive merges.
Outputs reproducible and explainable collision reports.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED_PATH = ROOT / "data" / "opportunities.seed.json"
DEFAULT_INBOX_PATH = ROOT / "data" / "candidates" / "inbox.local.json"

EXACT_DUPLICATE = "EXACT_DUPLICATE"
IDENTIFIER_COLLISION = "IDENTIFIER_COLLISION"
POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
NO_MATCH = "NO_MATCH"

SET_BATCH = "batch"
SET_INBOX = "inbox"
SET_SEED = "seed"


def normalize_text(text: object) -> str:
    """Normalizes Unicode, strips accents, removes punctuation, collapses whitespace and casefolds."""
    if text is None:
        return ""
    s = str(text).strip()
    if not s:
        return ""
    decomposed = unicodedata.normalize("NFKD", s)
    without_accents = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    clean = re.sub(r"[^\w\s]", " ", without_accents)
    return " ".join(clean.split()).casefold()


def normalize_identifier(identifier: object) -> str:
    """Normalizes external reference without removing leading zeros."""
    if identifier is None:
        return ""
    s = str(identifier).strip()
    if not s:
        return ""
    normalized = unicodedata.normalize("NFKC", s)
    return " ".join(normalized.split()).casefold()


def make_primary_key(source_id: object, external_ref: object) -> str | None:
    s_id = str(source_id).strip().casefold() if source_id else ""
    e_ref = normalize_identifier(external_ref)
    if not s_id or not e_ref:
        return None
    return f"{s_id}:{e_ref}"


def make_secondary_signature(
    *,
    employer: object,
    title: object,
    location: object = None,
    mode: object = None,
    opportunity_type: object = None,
) -> str | None:
    emp = normalize_text(employer)
    tit = normalize_text(title)
    if not emp or not tit:
        return None
    loc = normalize_text(location) or "none"
    mod = normalize_text(mode) or "none"
    opp = normalize_text(opportunity_type) or "none"
    return f"{emp}|{tit}|{loc}|{mod}|{opp}"


@dataclass(frozen=True)
class CollisionRecord:
    record_id: str
    matched_id: str
    matched_set: str
    match_type: str
    match_key: str
    matching_fields: tuple[str, ...]
    discrepant_fields: tuple[str, ...]
    explanation: str
    recommended_action: str

    def to_dict(self) -> dict:
        return {
            "recordId": self.record_id,
            "matchedId": self.matched_id,
            "matchedSet": self.matched_set,
            "matchType": self.match_type,
            "matchKey": self.match_key,
            "matchingFields": list(self.matching_fields),
            "discrepantFields": list(self.discrepant_fields),
            "explanation": self.explanation,
            "recommendedAction": self.recommended_action,
        }


@dataclass
class DeduplicationReport:
    total_evaluated: int
    collisions: list[CollisionRecord]
    summary_by_type: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "totalEvaluated": self.total_evaluated,
            "summaryByType": dict(self.summary_by_type),
            "collisions": [c.to_dict() for c in self.collisions],
        }


def extract_fields(record: dict, *, is_seed: bool = False) -> dict:
    if is_seed:
        return {
            "id": str(record.get("id") or "unknown"),
            "sourceId": str(record.get("sourceKind") or record.get("sourceUrl") or "seed"),
            "title": record.get("title"),
            "employer": record.get("employer"),
            "publisher": record.get("sourceKind") or record.get("employer"),
            "externalReference": record.get("requisition"),
            "applyUrl": record.get("applyUrl"),
            "location": record.get("location"),
            "mode": record.get("mode"),
            "opportunityType": record.get("kind"),
            "salary": record.get("salary"),
            "publishedAt": record.get("publishedAt"),
            "deadline": record.get("deadline"),
        }
    proposed = record.get("proposed") if isinstance(record.get("proposed"), dict) else {}
    return {
        "id": str(record.get("candidateId") or "unknown"),
        "sourceId": str(record.get("sourceId") or ""),
        "title": proposed.get("title"),
        "employer": proposed.get("employer"),
        "publisher": proposed.get("publisher"),
        "externalReference": proposed.get("externalReference"),
        "applyUrl": proposed.get("applyUrl"),
        "location": proposed.get("location"),
        "mode": proposed.get("mode"),
        "opportunityType": proposed.get("opportunityType"),
        "salary": proposed.get("salary"),
        "publishedAt": proposed.get("publishedAt"),
        "deadline": proposed.get("deadline"),
    }


def compare_records(
    rec1_fields: dict,
    rec2_fields: dict,
    *,
    matched_set: str,
) -> CollisionRecord | None:
    rec1_id = rec1_fields["id"]
    rec2_id = rec2_fields["id"]
    if rec1_id == rec2_id:
        return None

    all_fields = (
        "title", "employer", "publisher", "externalReference", "applyUrl",
        "location", "mode", "opportunityType", "salary", "publishedAt", "deadline",
    )
    matching_fields = []
    discrepant_fields = []
    for f in all_fields:
        v1 = rec1_fields.get(f)
        v2 = rec2_fields.get(f)
        if v1 is None and v2 is None:
            continue
        if v1 is not None and v2 is not None:
            n1 = normalize_text(v1) if f in ("title", "employer", "publisher", "location", "mode", "opportunityType") else str(v1).strip().casefold()
            n2 = normalize_text(v2) if f in ("title", "employer", "publisher", "location", "mode", "opportunityType") else str(v2).strip().casefold()
            if n1 == n2:
                matching_fields.append(f)
            else:
                discrepant_fields.append(f)
        else:
            discrepant_fields.append(f)

    # 1. Primary match evaluation
    pk1 = make_primary_key(rec1_fields.get("sourceId"), rec1_fields.get("externalReference"))
    pk2 = make_primary_key(rec2_fields.get("sourceId"), rec2_fields.get("externalReference"))

    if pk1 and pk2 and pk1 == pk2:
        norm_tit1 = normalize_text(rec1_fields.get("title"))
        norm_tit2 = normalize_text(rec2_fields.get("title"))
        norm_emp1 = normalize_text(rec1_fields.get("employer"))
        norm_emp2 = normalize_text(rec2_fields.get("employer"))

        contradictions = []
        if norm_tit1 and norm_tit2 and norm_tit1 != norm_tit2:
            contradictions.append(f"título ('{rec1_fields.get('title')}' vs '{rec2_fields.get('title')}')")
        if norm_emp1 and norm_emp2 and norm_emp1 != norm_emp2:
            contradictions.append(f"empleador ('{rec1_fields.get('employer')}' vs '{rec2_fields.get('employer')}')")

        if contradictions:
            return CollisionRecord(
                record_id=rec1_id,
                matched_id=rec2_id,
                matched_set=matched_set,
                match_type=IDENTIFIER_COLLISION,
                match_key=pk1,
                matching_fields=tuple(matching_fields),
                discrepant_fields=tuple(discrepant_fields),
                explanation=f"Misma identidad primaria ({pk1}) pero datos contradictorios en: {', '.join(contradictions)}.",
                recommended_action="Revisar manualmente: conflicto crítico de identificador externo; no fusionar.",
            )
        else:
            return CollisionRecord(
                record_id=rec1_id,
                matched_id=rec2_id,
                matched_set=matched_set,
                match_type=EXACT_DUPLICATE,
                match_key=pk1,
                matching_fields=tuple(matching_fields),
                discrepant_fields=tuple(discrepant_fields),
                explanation=f"Identidad primaria coincidente ({pk1}) con datos consistentes.",
                recommended_action="Conservar registro existente y revisar si el nuevo lote aporta evidencia más reciente.",
            )

    # 2. Secondary match evaluation
    sec1 = make_secondary_signature(
        employer=rec1_fields.get("employer"),
        title=rec1_fields.get("title"),
        location=rec1_fields.get("location"),
        mode=rec1_fields.get("mode"),
        opportunity_type=rec1_fields.get("opportunityType"),
    )
    sec2 = make_secondary_signature(
        employer=rec2_fields.get("employer"),
        title=rec2_fields.get("title"),
        location=rec2_fields.get("location"),
        mode=rec2_fields.get("mode"),
        opportunity_type=rec2_fields.get("opportunityType"),
    )

    if sec1 and sec2 and sec1 == sec2:
        return CollisionRecord(
            record_id=rec1_id,
            matched_id=rec2_id,
            matched_set=matched_set,
            match_type=POSSIBLE_DUPLICATE,
            match_key=sec1,
            matching_fields=tuple(matching_fields),
            discrepant_fields=tuple(discrepant_fields),
            explanation="Firma secundaria coincidente: mismo empleador, título, ubicación, modalidad y tipo.",
            recommended_action="Revisar manualmente: posible duplicado cross-fuente; no fusionar automáticamente.",
        )

    return None


def deduplicate_candidates(
    candidates: list[dict],
    *,
    inbox_candidates: list[dict] | None = None,
    seed_opportunities: list[dict] | None = None,
) -> DeduplicationReport:
    """Evaluates candidates against the current batch, an existing inbox, and/or canonical seed opportunities."""
    collisions: list[CollisionRecord] = []
    seen_pair_keys: set[tuple[str, str, str]] = set()

    evaluated_fields: list[dict] = []
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        c_fields = extract_fields(cand, is_seed=False)
        c_id = c_fields["id"]

        # 1. Compare against previous candidates in same batch
        for prev_fields in evaluated_fields:
            col = compare_records(c_fields, prev_fields, matched_set=SET_BATCH)
            if col:
                pair_key = (c_id, prev_fields["id"], col.match_type)
                if pair_key not in seen_pair_keys:
                    seen_pair_keys.add(pair_key)
                    collisions.append(col)

        # 2. Compare against inbox candidates if provided
        if inbox_candidates:
            for in_cand in inbox_candidates:
                if not isinstance(in_cand, dict):
                    continue
                in_fields = extract_fields(in_cand, is_seed=False)
                col = compare_records(c_fields, in_fields, matched_set=SET_INBOX)
                if col:
                    pair_key = (c_id, in_fields["id"], col.match_type)
                    if pair_key not in seen_pair_keys:
                        seen_pair_keys.add(pair_key)
                        collisions.append(col)

        # 3. Compare against seed opportunities if provided
        if seed_opportunities:
            for seed_opp in seed_opportunities:
                if not isinstance(seed_opp, dict):
                    continue
                seed_fields = extract_fields(seed_opp, is_seed=True)
                col = compare_records(c_fields, seed_fields, matched_set=SET_SEED)
                if col:
                    pair_key = (c_id, seed_fields["id"], col.match_type)
                    if pair_key not in seen_pair_keys:
                        seen_pair_keys.add(pair_key)
                        collisions.append(col)

        evaluated_fields.append(c_fields)

    collisions.sort(key=lambda c: (c.record_id, c.matched_set, c.matched_id, c.match_type))

    summary: dict[str, int] = {
        EXACT_DUPLICATE: sum(1 for c in collisions if c.match_type == EXACT_DUPLICATE),
        IDENTIFIER_COLLISION: sum(1 for c in collisions if c.match_type == IDENTIFIER_COLLISION),
        POSSIBLE_DUPLICATE: sum(1 for c in collisions if c.match_type == POSSIBLE_DUPLICATE),
    }

    return DeduplicationReport(
        total_evaluated=len(evaluated_fields),
        collisions=collisions,
        summary_by_type=summary,
    )


def load_seed_opportunities(path: Path | str | None = None) -> list[dict]:
    p = Path(path) if path else DEFAULT_SEED_PATH
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("opportunities"), list):
            return data["opportunities"]
    except Exception:
        pass
    return []


def load_inbox_candidates(path: Path | str | None = None) -> list[dict]:
    p = Path(path) if path else DEFAULT_INBOX_PATH
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("candidates"), list):
            return data["candidates"]
    except Exception:
        pass
    return []
