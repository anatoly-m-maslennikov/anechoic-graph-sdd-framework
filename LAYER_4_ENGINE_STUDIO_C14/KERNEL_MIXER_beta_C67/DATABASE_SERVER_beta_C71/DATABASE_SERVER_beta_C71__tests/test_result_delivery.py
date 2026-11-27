"""Deliver retained query results through the private Kernel socket."""

import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import toon_format

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


def workspace(client, operation, arguments):
    return client.post(
        "/workspace",
        json=BINDING | {"operation": operation, "arguments": arguments},
    )


class ResultDeliveryTest(unittest.TestCase):
    def value(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def test_run_file_exports_full_result_page_and_grid_export_only_requested_rows(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                sql = (
                    "SELECT i AS x, CASE WHEN i=1 THEN NULL ELSE '' END AS x "
                    'FROM range(3) t(i)'
                )
                for fmt in ("json_matrix", "csv", "toon"):
                    result = self.value(_query(client, sql, page_size=1, result_delivery="file", result_format=fmt))
                    self.assertNotIn("rows", result)
                    self.assertNotIn("sql", result)
                    descriptor = result["result_file"]
                    self.assertEqual((3, 0, False), (descriptor["row_count"], descriptor["offset"], descriptor["has_more"]))
                    path = root / descriptor["path"]
                    self.assertTrue(path.is_file())
                    if fmt == "json_matrix":
                        matrix = json.loads(path.read_text())
                    elif fmt == "toon":
                        matrix = toon_format.loads(path.read_text())
                    else:
                        with path.open(newline="") as stream:
                            matrix = list(csv.reader(stream, quoting=csv.QUOTE_NOTNULL))
                        self.assertEqual([["x", "x"], ["0", ""], ["1", None], ["2", ""]], matrix)
                        continue
                    self.assertEqual(
                        {
                            "columns": ["x", "x"],
                            "rows": [[0, ""], [1, None], [2, ""]],
                        },
                        matrix,
                    )
                request = BINDING | {
                    "query_id": result["query_id"],
                    "offset": 1,
                    "page_size": 1,
                    "result_delivery": "file",
                    "grid": {"sort": [{"column": 0, "direction": "desc"}]},
                }
                page = self.value(client.post("/database", json=request))
                file = page["result_file"]
                self.assertEqual((1, 1, True), (file["row_count"], file["offset"], file["has_more"]))
                self.assertEqual([[1, None]], json.loads((root / file["path"]).read_text())["rows"])

    def test_export_failure_keeps_query_and_view_fetch_exports_page(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                tmp = root / ".anechoic_tmp"
                tmp.symlink_to(root, target_is_directory=True)
                failed = self.value(_query(client, "SELECT 7", page_size=1, result_delivery="file"))
                self.assertEqual("partial", failed["outcome"])
                self.assertIn("export_error", failed)
                self.assertNotIn("result_file", failed)
                page = client.post("/database", json=BINDING | {"query_id": failed["query_id"], "offset": 0, "page_size": 1})
                self.assertEqual([[7]], self.value(page)["rows"])
                tmp.unlink()
                opened = self.value(
                    workspace(
                        client, "workspace_open", {"session_id": "delivery"}
                    )
                )
                view = {
                    "workspace_id": opened["workspace_id"],
                    "view_id": opened["active_view_id"],
                }
                self.value(
                    workspace(
                        client,
                        "view_update",
                        view
                        | {
                            "sql": "SELECT i FROM range(3) t(i)",
                            "expected_revision": 0,
                        },
                    )
                )
                self.value(workspace(client, "view_run", view))
                result = self.value(workspace(client, "view_fetch", view | {"offset": 1, "page_size": 1, "result_delivery": "file"}))
                file = result["result_file"]
                self.assertEqual(
                    (1, 1, True),
                    (file["row_count"], file["offset"], file["has_more"]),
                )
                self.assertEqual(
                    [[1]],
                    json.loads((root / file["path"]).read_text())["rows"],
                )

    def test_converted_values_share_inline_and_file_output(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                sql = (
                    'SELECT 9007199254740992::BIGINT, 12.50::DECIMAL(5,2), '
                    "DATE '2026-01-02', BLOB '\\x41', [1,2]"
                )
                inline = self.value(_query(client, sql, page_size=1))["rows"]
                self.assertEqual(
                    [
                        [
                            "9007199254740992",
                            "12.50",
                            "2026-01-02",
                            "base64:QQ==",
                            [1, 2],
                        ]
                    ],
                    inline,
                )
                file = self.value(
                    _query(client, sql, page_size=1, result_delivery="file")
                )["result_file"]
                self.assertEqual(
                    inline,
                    json.loads((root / file["path"]).read_text())["rows"],
                )
                self.assertEqual(
                    400,
                    _query(
                        client, "SELECT 'NaN'::DOUBLE", page_size=1
                    ).status_code,
                )

    def test_grid_sorts_decimal_values_numerically_after_conversion(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.value(client.put("/generation", json=_generation()))
                sql = (
                    'SELECT x::DECIMAL(4,1) AS value FROM (VALUES (10.0), '
                    '(2.0)) t(x)'
                )
                result = self.value(
                    _query(
                        client,
                        sql,
                        page_size=10,
                        grid={"sort": [{"column": 0, "direction": "asc"}]},
                    )
                )
                self.assertEqual([["2.0"], ["10.0"]], result["rows"])
