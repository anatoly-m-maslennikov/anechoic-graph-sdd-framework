"""Exercise retained query history through the Database Server socket."""

from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


def _legacy_record(name, hours):
    return {"log_id": name, "at": (datetime.now(UTC) - timedelta(hours=hours)).isoformat(),
            "sql": f"SELECT '{name}'", "outcome": "success", "error": None,
            "row_count": 1, "column_count": 1}


class QueryHistoryTest(unittest.TestCase):
    def value(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def call(self, client, name, arguments):
        return client.post("/workspace", json=BINDING | {"operation": name, "arguments": arguments})

    def attempts(self, client, count):
        deadline = monotonic() + 3
        while monotonic() < deadline:
            items = self.value(self.call(client, "query_log_list", {}))["items"]
            if len(items) == count:
                return items
            sleep(0.03)
        self.fail(f"Expected {count} query log records")

    def test_history_is_project_local_and_survives_an_orderly_restart(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            legacy = root / ".anechoic_runtime/workbench/query-log.json"
            legacy.parent.mkdir(parents=True, mode=0o700)
            old_bytes = json.dumps([_legacy_record("retained", 1), _legacy_record("expired", 49)]).encode()
            legacy.write_bytes(old_bytes)
            arguments = (None, "--project-root", str(root))
            with _server(*arguments) as client:
                self.value(client.put("/generation", json=_generation()))
                records = self.run_attempts(client)
                newest = records[0]
                self.assertEqual(newest, self.value(self.call(client, "query_log_get", {"log_id": newest["log_id"]})))
                self.assertEqual([newest], self.value(self.call(client, "query_log_list", {"limit": 1}))["items"])
                sql_rows = self.value(_query(client, 'SELECT sql, outcome, "at" FROM query_log ORDER BY "at" DESC'))["rows"]
                self.assertEqual([(row["sql"], row["outcome"]) for row in records], [tuple(row[:2]) for row in sql_rows])
                self.assertTrue(all(datetime.fromisoformat(row[2]).tzinfo for row in sql_rows))
                foreign = client.post("/workspace", json={"instance_id": "foreign", "operation": "query_log_list", "arguments": {}})
                self.assertEqual(403, foreign.status_code)
            self.assertEqual(old_bytes, legacy.read_bytes())
            with _server(*arguments) as client:
                self.assertEqual(records, self.attempts(client, len(records)))
                self.assertEqual(400, self.call(client, "query_log_get", {"log_id": "expired"}).status_code)

    def run_attempts(self, client):
        self.value(_query(client, "SELECT 33"))  # Check and schema reads do not retain results.
        sql = "SELECT 42\n"
        self.value(_query(client, sql, page_size=1))
        view = self.value(self.call(client, "workspace_open", {"session_id": "query-log-test"}))
        selector = {"workspace_id": view["workspace_id"], "view_id": view["active_view_id"]}
        failed_sql = "SELECT missing"
        self.value(self.call(client, "view_update", selector | {"sql": failed_sql, "expected_revision": 0}))
        failed = self.value(self.call(client, "view_run", selector))
        self.assertEqual("failed", failed["status"])
        records = self.attempts(client, 3)
        self.assertEqual([failed_sql, sql, "SELECT 'retained'"], [row["sql"] for row in records])
        self.assertEqual(set(_legacy_record("shape", 0)), set(records[0]))
        self.assertEqual(("failed", None, None), (records[0]["outcome"], records[0]["row_count"], records[0]["column_count"]))
        self.assertEqual(("success", 1, 1), (records[1]["outcome"], records[1]["row_count"], records[1]["column_count"]))
        return records
