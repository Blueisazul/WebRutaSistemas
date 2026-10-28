from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


class LocalServerCatalogTests(unittest.TestCase):
    def test_legacy_local_api_never_relabels_sample_rows_as_active(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.executescript(server.SCHEMA)
        server.seed_database(connection)
        with patch("server.connect_db", return_value=connection):
            result = server.query_catalog({})
        self.assertEqual(result["metrics"]["total"], 0)
        self.assertTrue(result["opportunities"])
        self.assertTrue(all(item["publicationStatus"] != "active" for item in result["opportunities"]))
        self.assertTrue(all("status" not in item and "history" not in item for item in result["opportunities"]))


if __name__ == "__main__":
    unittest.main()
