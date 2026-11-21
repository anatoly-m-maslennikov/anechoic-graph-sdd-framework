"""Result delivery through the Workbench service and cached DuckDB result."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "APP_WORKBENCH__tests"))
from test_incremental_indexing import IncrementalIndexingTests


class ResultDeliveryTests(IncrementalIndexingTests):
    def test_auto_delivery_uses_utf8_size_and_keeps_the_full_result(self):
        inline = self.service.run("select repeat('a', 1000)", result_delivery="auto")
        self.assertEqual([["a" * 1000]], inline["rows"])
        self.assertNotIn("result_file", inline)
        exported = self.service.run("select repeat('文', 1500)", result_delivery="auto")
        self.assertNotIn("rows", exported)
        data = json.loads((self.root / exported["result_file"]["path"]).read_text())
        self.assertEqual([["文" * 1500]], data["rows"])
        paged = self.service.run("select i from range(2) as t(i)", page_size=1, result_delivery="auto")
        data = json.loads((self.root / paged["result_file"]["path"]).read_text())
        self.assertEqual([[0], [1]], data["rows"])

    def test_auto_csv_measures_the_encoded_table(self):
        inline = self.service.run("select repeat('a', 4087) as x", result_delivery="auto", result_format="csv")
        self.assertEqual(4096, len(inline["csv"].encode("utf-8")))
        self.assertNotIn("rows", inline)
        exported = self.service.run("select repeat('文', 1363) as x", result_delivery="auto", result_format="csv")
        self.assertNotIn("csv", exported)
        self.assertEqual("csv", exported["result_file"]["format"])
        data = (self.root / exported["result_file"]["path"]).read_bytes()
        self.assertEqual(4098, len(data))

    def test_full_file_and_page_and_check(self):
        result = self.service.run("select i from range(250) t(i)", page_size=10)
        self.assertNotIn("sql", result)
        self.assertNotIn("rows", result)
        data = json.loads((self.root / result["result_file"]["path"]).read_text())
        self.assertEqual(250, len(data["rows"]))
        page = self.service.page(result["query_id"], 100, page_size=10)
        data = json.loads((self.root / page["result_file"]["path"]).read_text())
        self.assertEqual([[i] for i in range(100, 110)], data["rows"])
        inline = self.service.page(result["query_id"], 0, page_size=2, result_delivery="inline")
        self.assertEqual([[0], [1]], inline["rows"])
        self.assertNotIn("sql", inline)
        self.assertNotIn("sql", self.service.check("select 1"))

    def test_export_failure_leaves_cached_result_available(self):
        with patch("APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery.write_result_file", side_effect=OSError("disk unavailable")):
            result = self.service.run("select 42")
        self.assertEqual("partial", result["outcome"])
        self.assertNotIn("result_file", result)
        page = self.service.page(result["query_id"], 0, result_delivery="inline")
        self.assertEqual([[42]], page["rows"])


if __name__ == "__main__":
    import unittest
    unittest.main()
