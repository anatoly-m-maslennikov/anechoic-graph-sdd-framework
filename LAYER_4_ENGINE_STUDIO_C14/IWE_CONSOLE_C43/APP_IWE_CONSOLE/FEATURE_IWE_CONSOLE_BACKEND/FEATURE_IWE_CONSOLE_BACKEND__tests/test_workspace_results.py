from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from KERNEL_MIXER_C59.workspace import WorkspaceStore


class WorkspaceResultsTest(unittest.TestCase):
    def test_created_and_duplicated_views_keep_persisted_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            store = WorkspaceStore(Path(directory))
            first = store.open("session")["active_view_id"]
            created = store.create("session", "last", "Named")["view_id"]
            store.set_result("session", created, {"query_id": "query"})
            path = store._path("session")
            document = json.loads(path.read_text())
            document["views"][0]["historic"] = {"kept": True}
            path.write_text(json.dumps(document))
            duplicate = store.duplicate("session", created)["view_id"]
            views = json.loads(path.read_text())["views"]
            self.assertEqual(
                ["id", "sql", "cursor_position", "revision"],
                list(views[0])[:4],
            )
            self.assertEqual({"kept": True}, views[0]["historic"])
            self.assertNotIn("name", views[0])
            self.assertEqual(
                [first, created, duplicate], [view["id"] for view in views]
            )
            self.assertEqual(
                ["id", "sql", "cursor_position", "revision", "name"],
                list(views[2]),
            )
            self.assertEqual("Named(1)", views[2]["name"])
            self.assertNotIn("result", views[2])
            self.assertEqual(
                1, store.update("session", first, "SELECT 1", 0, 8)["revision"]
            )
            self.assertNotIn("name", store.rename("session", created, ""))
            value, query_id = store.clear_result("session", created)
            self.assertEqual("query", query_id)
            self.assertNotIn("result", value)
            self.assertEqual(
                {"kept": True},
                json.loads(path.read_text())["views"][0]["historic"],
            )

    def test_invalid_persisted_view_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            store = WorkspaceStore(Path(directory))
            store.open("session")
            path = store._path("session")
            document = json.loads(path.read_text())
            document["views"][0]["revision"] = "0"
            corrupt = json.dumps(document)
            path.write_text(corrupt)
            with self.assertRaisesRegex(
                ValueError, "^workspace is unavailable$"
            ):
                store.open("session")
            self.assertEqual(corrupt, path.read_text())

    def test_native_results_are_transient_and_replaced_together(self):
        with tempfile.TemporaryDirectory() as directory:
            store = WorkspaceStore(Path(directory), transient_results=True)
            opened = store.open("session")
            view_id = opened["active_view_id"]
            store.set_result(
                "session",
                view_id,
                {"query_id": "old", "row_count": 1, "column_count": 1},
            )
            self.assertNotIn(
                "result",
                json.loads(store._path("session").read_text())["views"][0],
            )
            store.replace_result_ids(
                {"old": {"query_id": "new", "row_count": 2, "column_count": 3}}
            )
            self.assertEqual(
                "new", store.get_view("session", view_id)["result"]["query_id"]
            )
            self.assertEqual(
                2, store.get_view("session", view_id)["result"]["row_count"]
            )
            restarted = WorkspaceStore(Path(directory), transient_results=True)
            self.assertNotIn("result", restarted.get_view("session", view_id))


if __name__ == "__main__":
    unittest.main()
