"""Preview limits retained results without rewriting the submitted SQL."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


def workspace(client, operation, arguments):
    return client.post("/workspace", json=BINDING | {"operation": operation, "arguments": arguments})


class ResultPreviewTest(unittest.TestCase):
    def value(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def test_run_page_and_rebuild_preserve_preview(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                sql = "WITH source AS (SELECT i FROM range(3000) t(i)) SELECT i FROM source LIMIT 2500"
                self.assertEqual(400, _query(client, sql, page_size=10).status_code)
                result = self.value(_query(client, sql, page_size=10, preview=7))
                self.assertEqual(7, result["row_count"])
                self.assertEqual([[i] for i in range(7)], result["rows"])
                query_id = result["query_id"]
                page = client.post("/database", json=BINDING | {"query_id": query_id, "offset": 2, "page_size": 5, "preview": 2})
                self.assertEqual([[2], [3]], self.value(page)["rows"])
                for target in (query_id, "all"):
                    if target == "all":
                        updated = client.put("/generation", json=_generation() | {"refresh_target": "all"})
                    else:
                        updated = client.post("/results/rebuild", json=BINDING | {"target": target})
                    mapping = self.value(updated)["result_ids"]
                    query_id = mapping[query_id]
                    page = client.post("/database", json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 10})
                    self.assertEqual(7, self.value(page)["row_count"])
                zero = self.value(_query(client, sql, page_size=1, preview=0))
                self.assertEqual((0, []), (zero["row_count"], zero["rows"]))
                self.assertEqual(400, _query(client, sql, page_size=1, preview=True).status_code)
                self.assertEqual(400, client.post("/database", json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 1, "preview": True}).status_code)

    def test_view_run_preview_limits_materialized_result_and_fetch(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                opened = self.value(workspace(client, "workspace_open", {"session_id": "preview"}))
                view = {"workspace_id": opened["workspace_id"], "view_id": opened["active_view_id"]}
                self.value(workspace(client, "view_update", view | {"sql": "SELECT i FROM range(5000) t(i)", "expected_revision": 0}))
                self.assertEqual(400, workspace(client, "view_run", view | {"preview": True}).status_code)
                run = self.value(workspace(client, "view_run", view | {"preview": 4}))
                self.assertEqual(("success", 4), (run["status"], run["row_count"]))
                fetched = self.value(workspace(client, "view_fetch", view | {"offset": 1, "page_size": 3, "preview": 1}))
                self.assertEqual([[1]], fetched["rows"])
                self.assertEqual(4, fetched["row_count"])
