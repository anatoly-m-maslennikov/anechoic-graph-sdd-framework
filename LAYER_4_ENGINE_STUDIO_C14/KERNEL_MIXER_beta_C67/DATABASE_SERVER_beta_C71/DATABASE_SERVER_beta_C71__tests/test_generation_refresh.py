"""Generation and cached result refresh commit as one operation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


def workspace(client, operation, arguments):
    return client.post("/workspace", json=BINDING | {"operation": operation, "arguments": arguments})


class GenerationRefreshTest(unittest.TestCase):
    def test_failed_refresh_preserves_generation_cache_and_view_then_success_rekeys(self):
        with TemporaryDirectory(dir="/tmp") as directory, _server(None, "--project-root", str(Path(directory).resolve())) as client:
            original = client.put("/generation", json=_generation()).json()["result"]["generation"]
            first = _query(client, "SELECT reference FROM atoms ORDER BY reference", page_size=2).json()["result"]
            opened = workspace(client, "workspace_open", {"session_id": "refresh-test"}).json()["result"]
            view = {"workspace_id": opened["workspace_id"], "view_id": opened["active_view_id"]}
            updated = workspace(client, "view_update", view | {"sql": "SELECT reference FROM atoms", "expected_revision": 0})
            self.assertEqual(200, updated.status_code, updated.text)
            run = workspace(client, "view_run", view).json()["result"]
            for invalid in (first["query_id"], "workbench_results", "missing_table", 3):
                rejected = client.put("/generation", json=_generation() | {"refresh_target": invalid})
                self.assertEqual(400, rejected.status_code, rejected.text)
            candidate = _generation()
            candidate["snapshot"]["atoms"] = [{"reference": str(i), "summary": "s"} for i in range(1001)]
            failed = client.put("/generation", json=candidate | {"refresh_target": "all"})
            self.assertEqual(400, failed.status_code, failed.text)
            self.assertIn("1000 rows", failed.text)
            self.assertEqual(original, client.get("/health").json()["result"]["generation"])
            self.assertEqual([["one"]], _query(client, "SELECT reference FROM atoms").json()["result"]["rows"])
            for query_id in (first["query_id"], run["query_id"]):
                page = client.post("/database", json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 2})
                self.assertEqual(200, page.status_code, page.text)
            self.assertEqual(run["query_id"], workspace(client, "view_fetch", view).json()["result"]["query_id"])
            candidate["snapshot"]["atoms"] = [{"reference": "new", "summary": "s"}]
            success = client.put("/generation", json=candidate | {"refresh_target": "atoms"})
            self.assertEqual(200, success.status_code, success.text)
            result = success.json()["result"]
            self.assertNotEqual(original, result["generation"])
            self.assertEqual({first["query_id"], run["query_id"]}, set(result["result_ids"]))
            self.assertEqual(result["result_ids"][run["query_id"]], workspace(client, "view_fetch", view).json()["result"]["query_id"])
            for query_id in (first["query_id"], run["query_id"]):
                old = client.post("/database", json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 2})
                self.assertEqual(400, old.status_code, old.text)
                new = client.post("/database", json=BINDING | {"query_id": result["result_ids"][query_id], "offset": 0, "page_size": 2})
                self.assertEqual([["new"]], new.json()["result"]["rows"])
