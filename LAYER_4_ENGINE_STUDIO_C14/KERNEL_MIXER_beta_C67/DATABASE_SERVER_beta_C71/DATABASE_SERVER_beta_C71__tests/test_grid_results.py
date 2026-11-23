"""Check grid reads over the shared result cache through the Unix socket."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


class GridResultsTest(unittest.TestCase):
    def test_query_and_view_grid(self):
        with TemporaryDirectory() as root, _server(None, "--project-root", str(Path(root).resolve())) as client:
            self.assertEqual(client.put("/generation", json=_generation()).status_code, 200)
            sql = "SELECT * FROM (VALUES ('a', 2), ('A', 1), ('b', 3), (NULL, 4)) t(k, n)"
            grid = {"filters": [{"column": 0, "operator": "contains", "value": "a"}],
                    "sort": [{"column": 1, "direction": "desc"}],
                    "group_by": {"column": 0, "direction": "asc"}}
            run = _query(client, sql, page_size=1).json()["result"]
            def page(offset):
                return client.post("/database", json={**BINDING, "query_id": run["query_id"],
                                   "offset": offset, "page_size": 1, "grid": grid})
            result = page(0).json()["result"]
            self.assertEqual((result["row_count"], result["source_row_count"]), (2, 4))
            self.assertEqual(result["rows"], [["A", 1]])
            self.assertEqual(result["groups"], [{"value": "A", "count": 1}])
            self.assertEqual(page(1).json()["result"]["rows"], [["a", 2]])
            beyond = page(10).json()["result"]
            self.assertEqual((beyond["rows"], beyond["row_count"], beyond["groups"]), ([], 2, []))
            empty_grid = {**grid, "filters": [{"column": 0, "operator": "contains", "value": "missing"}]}
            empty = client.post("/database", json={**BINDING, "query_id": run["query_id"],
                                "offset": 0, "page_size": 1, "grid": empty_grid}).json()["result"]
            self.assertEqual((empty["rows"], empty["row_count"], empty["groups"]), ([], 0, []))
            self.assertEqual(client.post("/database", json={**BINDING, "query_id": run["query_id"],
                             "offset": 0, "page_size": 1, "grid": {"sort": [{"column": 2, "direction": "asc"}]}}).status_code, 400)
            def call(operation, arguments):
                return client.post("/workspace", json={**BINDING, "operation": operation, "arguments": arguments})
            workspace = call("workspace_open", {"session_id": "grid"}).json()["result"]
            view = {"workspace_id": "grid", "view_id": workspace["active_view_id"]}
            self.assertEqual(call("view_update", view | {"sql": sql, "expected_revision": 0}).status_code, 200)
            self.assertEqual(call("view_run", view).json()["result"]["status"], "success")
            fetched = call("view_fetch", view | {"grid": grid, "page_size": 1}).json()["result"]
            self.assertEqual(fetched["rows"], result["rows"])
            self.assertEqual(fetched["groups"], result["groups"])
