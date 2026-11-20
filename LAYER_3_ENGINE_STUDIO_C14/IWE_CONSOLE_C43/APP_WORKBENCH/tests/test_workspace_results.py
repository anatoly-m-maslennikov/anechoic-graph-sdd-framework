from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workspace import WorkspaceStore


class WorkspaceResultsTest(unittest.TestCase):
    def test_native_results_are_transient_and_replaced_together(self):
        with tempfile.TemporaryDirectory() as directory:
            store = WorkspaceStore(Path(directory), transient_results=True)
            opened = store.open("session")
            view_id = opened["active_view_id"]
            store.set_result("session", view_id, {"query_id": "old", "row_count": 1, "column_count": 1})
            self.assertNotIn("result", json.loads(store._path("session").read_text())["views"][0])
            store.replace_result_ids({"old": {"query_id": "new", "row_count": 2, "column_count": 3}})
            self.assertEqual("new", store.get_view("session", view_id)["result"]["query_id"])
            self.assertEqual(2, store.get_view("session", view_id)["result"]["row_count"])
            restarted = WorkspaceStore(Path(directory), transient_results=True)
            self.assertNotIn("result", restarted.get_view("session", view_id))


if __name__ == "__main__":
    unittest.main()
