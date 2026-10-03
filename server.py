"""Dependency-free, loopback-only Ruta Sistemas demo server."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "opportunities.sqlite3"
SEED_PATH = DATA_DIR / "opportunities.seed.json"
PORT = 4173
MAX_QUERY_LENGTH = 100
MAX_RESULTS = 500

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    publisher TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    host TEXT NOT NULL,
    terms_review TEXT NOT NULL DEFAULT 'pending',
    rights_review TEXT NOT NULL DEFAULT 'pending',
    robots_review TEXT NOT NULL DEFAULT 'pending',
    UNIQUE (publisher, canonical_url)
);
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    external_id TEXT,
    employer TEXT NOT NULL,
    title TEXT NOT NULL,
    sector TEXT NOT NULL,
    family TEXT NOT NULL,
    level TEXT NOT NULL,
    kind TEXT NOT NULL,
    mode TEXT NOT NULL,
    location TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    salary TEXT NOT NULL,
    salary_note TEXT NOT NULL,
    duration TEXT NOT NULL,
    deadline TEXT NOT NULL,
    published TEXT NOT NULL,
    checked TEXT NOT NULL,
    publication_status TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    requisition TEXT NOT NULL,
    tasks TEXT NOT NULL,
    requirements TEXT NOT NULL,
    skills TEXT NOT NULL,
    growth TEXT NOT NULL,
    risk TEXT NOT NULL,
    continuity TEXT NOT NULL,
    benefits TEXT NOT NULL,
    history INTEGER NOT NULL DEFAULT 0 CHECK (history IN (0, 1)),
    apply_url TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_opportunities_mode ON opportunities(mode);
CREATE INDEX IF NOT EXISTS idx_opportunities_kind ON opportunities(kind);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(publication_status, verification_status);
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id INTEGER PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    evidence_url TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    note TEXT NOT NULL
);
"""


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def source_id_for(record: dict) -> tuple[str, str, str]:
    from urllib.parse import urlsplit as split_url

    source_url = record.get("sourceUrl") or record.get("applyUrl") or ""
    parsed = split_url(source_url)
    host = (parsed.hostname or "unknown").lower()
    kind = record.get("sourceKind") or "Fuente no indicada"
    source_id = hashlib.sha256(f"{kind}|{source_url}".encode("utf-8")).hexdigest()[:20]
    return source_id, host, source_url


def seed_database(connection: sqlite3.Connection) -> None:
    if connection.execute("SELECT 1 FROM opportunities LIMIT 1").fetchone():
        return
    if not SEED_PATH.exists():
        raise RuntimeError(f"No se encuentra la muestra inicial: {SEED_PATH.name}")

    records = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise RuntimeError("El archivo de muestra debe contener una lista JSON.")

    opportunity_columns = (
        "id, source_id, external_id, employer, title, sector, family, level, kind, mode, "
        "location, eligibility, salary, salary_note, duration, deadline, published, checked, "
        "publication_status, verification_status, requisition, tasks, requirements, skills, "
        "growth, risk, continuity, benefits, history, apply_url, payload_json"
    )
    placeholders = ", ".join("?" for _ in opportunity_columns.split(", "))
    insert_opportunity = f"INSERT INTO opportunities ({opportunity_columns}) VALUES ({placeholders})"

    with connection:
        for record in records:
            source_id, host, source_url = source_id_for(record)
            source_kind = record.get("sourceKind") or "Fuente no indicada"
            connection.execute(
                """INSERT OR IGNORE INTO sources
                   (source_id, publisher, source_kind, canonical_url, host)
                   VALUES (?, ?, ?, ?, ?)""",
                (source_id, record.get("employer", "Entidad no indicada"), source_kind, source_url, host),
            )

            old_status = record.get("status", "unverified")
            publication_status = "closed" if old_status == "closed" else "open" if old_status == "verified" else "unknown"
            verification_status = "employer_verified" if old_status in {"verified", "closed"} else "secondary_only"
            payload = dict(record)
            payload["publicationStatus"] = publication_status
            payload["verificationStatus"] = verification_status
            payload["status"] = "closed" if publication_status == "closed" else "verified" if verification_status == "employer_verified" else "secondary"

            values = (
                record["id"], source_id, record.get("requisition", ""), record.get("employer", ""),
                record.get("title", ""), record.get("sector", ""), record.get("family", ""),
                record.get("level", ""), record.get("kind", ""), record.get("mode", ""),
                record.get("location", ""), record.get("eligibility", ""), record.get("salary", ""),
                record.get("salaryNote", ""), record.get("duration", ""), record.get("deadline", ""),
                record.get("published", ""), record.get("checked", ""), publication_status,
                verification_status, record.get("requisition", ""), record.get("tasks", ""),
                record.get("requirements", ""), record.get("skills", ""), record.get("growth", ""),
                record.get("risk", ""), record.get("continuity", ""), record.get("benefits", ""),
                int(bool(record.get("history"))), record.get("applyUrl", source_url),
                json.dumps(payload, ensure_ascii=False),
            )
            connection.execute(insert_opportunity, values)
            connection.execute(
                """INSERT INTO evidence (opportunity_id, field_name, evidence_url, observed_at, note)
                   VALUES (?, 'publication_reference', ?, ?, ?)""",
                (record["id"], source_url, record.get("checked", ""),
                 "Enlace incluido en la muestra curada; no se guardó el texto íntegro de la publicación."),
            )
            if record.get("evidenceUrl"):
                connection.execute(
                    """INSERT INTO evidence (opportunity_id, field_name, evidence_url, observed_at, note)
                       VALUES (?, 'supporting_document', ?, ?, ?)""",
                    (record["id"], record["evidenceUrl"], record.get("checked", ""),
                     "Documento de respaldo enlazado en la muestra curada."),
                )

    try:
        connection.execute("CREATE VIRTUAL TABLE IF NOT EXISTS opportunities_fts USING fts5(opportunity_id UNINDEXED, content)")
        with connection:
            connection.execute("DELETE FROM opportunities_fts")
            for row in connection.execute("SELECT id, title, employer, sector, family, level, kind, location, skills, tasks, requirements FROM opportunities"):
                searchable = " ".join(row[key] or "" for key in row.keys() if key != "id")
                connection.execute("INSERT INTO opportunities_fts (opportunity_id, content) VALUES (?, ?)", (row["id"], searchable))
    except sqlite3.OperationalError:
        # FTS5 is optional in some SQLite builds; bounded LIKE search remains available.
        pass


def query_catalog(params: dict[str, list[str]]) -> dict:
    query = (params.get("q", [""])[0] or "").strip()[:MAX_QUERY_LENGTH]
    mode = (params.get("mode", [""])[0] or "").strip()[:40]
    kind = (params.get("kind", [""])[0] or "").strip()[:60]
    family = (params.get("family", [""])[0] or "").strip()[:60]
    include_history = params.get("history", ["0"])[0] == "1"

    conditions = []
    arguments: list[str] = []
    connection = connect_db()
    try:
        if not include_history:
            conditions.append("o.history = 0")
        if mode:
            if mode.lower() == "remoto":
                conditions.append("lower(o.mode) LIKE '%remoto%'")
            elif mode.lower() == "flexible":
                conditions.append("lower(o.mode) LIKE '%flexible%'")
            else:
                conditions.append("lower(o.mode) = lower(?)")
                arguments.append(mode)
        if kind:
            if kind == "Junior / profesional":
                conditions.append("o.kind = 'Profesional'")
            else:
                conditions.append("o.kind = ?")
                arguments.append(kind)
        if family:
            conditions.append("lower(o.family) LIKE lower(?)")
            arguments.append(f"%{family}%")

        tokens = re.findall(r"[\wÀ-ÿ]+", query, flags=re.UNICODE)
        if tokens:
            fts_query = " AND ".join(f'"{token.replace(chr(34), "")}"*' for token in tokens)
            try:
                connection.execute("SELECT 1 FROM opportunities_fts LIMIT 1")
                conditions.append("o.id IN (SELECT opportunity_id FROM opportunities_fts WHERE opportunities_fts MATCH ?)")
                arguments.append(fts_query)
            except sqlite3.OperationalError:
                for token in tokens:
                    conditions.append("lower(o.title || ' ' || o.employer || ' ' || o.sector || ' ' || o.family || ' ' || o.skills || ' ' || o.tasks || ' ' || o.requirements) LIKE lower(?)")
                    arguments.append(f"%{token}%")

        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = connection.execute(
            "SELECT o.payload_json, o.publication_status, o.verification_status FROM opportunities o"
            + where
            + " ORDER BY CASE o.publication_status WHEN 'closed' THEN 2 ELSE CASE o.verification_status WHEN 'employer_verified' THEN 0 ELSE 1 END END, o.employer, o.title LIMIT ?",
            (*arguments, MAX_RESULTS),
        ).fetchall()
        all_rows = connection.execute(
            "SELECT publication_status, verification_status FROM opportunities WHERE history = 0"
        ).fetchall()
        opportunities = []
        for row in rows:
            record = json.loads(row["payload_json"])
            record["publicationStatus"] = row["publication_status"]
            record["verificationStatus"] = row["verification_status"]
            record["status"] = "closed" if row["publication_status"] == "closed" else "verified" if row["verification_status"] == "employer_verified" else "secondary"
            opportunities.append(record)
        metrics = {
            "total": len(all_rows),
            "primary": sum(row["verification_status"] == "employer_verified" for row in all_rows),
            "secondary": sum(row["verification_status"] == "secondary_only" for row in all_rows),
        }
        return {"opportunities": opportunities, "metrics": metrics}
    finally:
        connection.close()


PUBLIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/collector/README.md": ("collector/README.md", "text/markdown; charset=utf-8"),
}


class LocalHandler(BaseHTTPRequestHandler):
    server_version = "RutaLocal/1"

    def log_message(self, _format: str, *_args: object) -> None:
        # Do not put search terms or request URLs into persistent logs.
        return

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        super().end_headers()

    def _send(self, status: int, body: bytes, content_type: str, cache_control: str = "no-store") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, value: dict) -> None:
        self._send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        expected_hosts = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
        if self.headers.get("Host", "").lower() not in expected_hosts:
            self._json(400, {"error": "invalid_host"})
            return

        parsed = urlsplit(self.path)
        if parsed.path == "/api/health":
            self._json(200, {"status": "ok", "storage": "sqlite", "network_scope": "loopback"})
            return
        if parsed.path == "/api/opportunities":
            try:
                self._json(200, query_catalog(parse_qs(parsed.query)))
            except (sqlite3.Error, ValueError):
                self._json(500, {"error": "catalog_unavailable"})
            return

        public_file = PUBLIC_FILES.get(parsed.path)
        if public_file:
            path = ROOT / public_file[0]
            try:
                self._send(200, path.read_bytes(), public_file[1], "no-cache")
            except OSError:
                self._json(404, {"error": "not_found"})
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        self._json(405, {"error": "method_not_allowed"})


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = connect_db()
    try:
        connection.executescript(SCHEMA)
        seed_database(connection)
    finally:
        connection.close()

    server = ThreadingHTTPServer(("127.0.0.1", PORT), LocalHandler)
    print(f"Ruta Sistemas está disponible solo en esta computadora: http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor local detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
