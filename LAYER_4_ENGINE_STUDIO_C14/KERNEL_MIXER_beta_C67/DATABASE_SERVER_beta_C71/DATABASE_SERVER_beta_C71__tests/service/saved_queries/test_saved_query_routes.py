"""Exercise Saved SQL run and snapshot contracts over a real Kernel socket."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import UUID

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


_SQL = " \r\nSELECT 'ქართული;'; -- one query;\r\n\t"


def _workspace(client, operation, args, *, instance=BINDING["instance_id"]):
    return client.post(
        "/workspace",
        json={
            "instance_id": instance,
            "operation": operation,
            "arguments": args,
        },
    )


class SavedQueryRoutesTest(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        self.root = Path(directory).resolve()

    def server(self, *, writable=True):
        args = ["--project-root", str(self.root)]
        if writable:
            args += ["--journal-relative", "control/journal"]
        return self.enterContext(_server(None, *args))

    def result(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def page(self, client, query_id, **options):
        return client.post(
            "/database",
            json=BINDING
            | {
                "query_id": query_id,
                "offset": 0,
                "page_size": 10,
                **options,
            },
        )

    def view(self, client, sql):
        workspace = self.result(
            _workspace(
                client, "workspace_open", {"session_id": "saved-queries"}
            )
        )
        identity = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        self.result(
            _workspace(
                client,
                "view_update",
                identity | {"sql": sql, "expected_revision": 0},
            )
        )
        return identity

    def saved(self, client, result, sql, kind, name):
        saved_id = result["saved_query_id"]
        parsed = UUID(saved_id)
        self.assertEqual((7, saved_id), (parsed.version, str(parsed)))
        loaded = self.result(
            _workspace(client, "query_load", {"reference": saved_id})
        )
        self.assertEqual(
            (saved_id, sql, kind, name),
            (
                loaded["saved_query_id"],
                loaded["sql"],
                loaded["kind"],
                loaded.get("name"),
            ),
        )
        return loaded

    def test_paged_sql_run_saves_exact_original_once(self):
        client = self.server()
        self.assertEqual(
            409, _query(client, _SQL, page_size=1, save=True).status_code
        )
        self.result(client.put("/generation", json=_generation()))
        outcome = self.result(
            _query(client, _SQL, page_size=1, save=True, name="Exact")
        )
        self.assertEqual([["ქართული;"]], outcome["rows"])
        self.saved(client, outcome, _SQL, "query", "Exact")
        self.assertEqual(
            outcome["rows"],
            self.result(self.page(client, outcome["query_id"]))["rows"],
        )
        self.assertEqual(
            400, self.page(client, outcome["query_id"], save=True).status_code
        )
        for request in (
            {"save": True},
            {"page_size": 1, "save": 1},
            {"page_size": 1, "name": "Invalid"},
            {"page_size": 1, "save": False, "name": "Invalid"},
        ):
            self.assertEqual(400, _query(client, _SQL, **request).status_code)
        foreign = _query(
            client, _SQL, page_size=1, save=True, instance_id="another project"
        )
        self.assertEqual(403, foreign.status_code)
        for sql in ("SELECT 1; SELECT 2", "SELECT missing"):
            self.assertEqual(
                400, _query(client, sql, page_size=1, save=True).status_code
            )
        normal = self.result(
            _query(client, "SELECT 1", page_size=1, save=False)
        )
        self.assertNotIn("saved_query_id", normal)
        items = self.result(_workspace(client, "query_saved_list", {}))[
            "items"
        ]
        self.assertEqual(
            [outcome["saved_query_id"]],
            [item["saved_query_id"] for item in items],
        )

    def test_view_run_saves_bookmark_and_view_save_only_snapshots(self):
        client = self.server()
        raw = self.result(
            _workspace(
                client, "view_save", {"sql": "SELECT missing", "name": "Raw"}
            )
        )
        self.saved(client, raw, "SELECT missing", "view", "Raw")
        self.assertEqual(
            [], self.result(_workspace(client, "query_log_list", {}))["items"]
        )
        self.result(client.put("/generation", json=_generation()))
        view = self.view(client, _SQL)
        self.result(
            _workspace(client, "view_rename", view | {"name": "View name"})
        )
        run = self.result(
            _workspace(
                client, "view_run", view | {"save": True, "name": "Bookmark"}
            )
        )
        self.assertEqual("success", run["status"])
        self.assertNotIn("rows", run)
        self.saved(client, run, _SQL, "query", "Bookmark")
        self.assertEqual(
            [["ქართული;"]],
            self.result(_workspace(client, "view_fetch", view))["rows"],
        )
        snapshot = self.result(_workspace(client, "view_save", view))
        self.assertEqual(
            snapshot, self.saved(client, snapshot, _SQL, "view", "View name")
        )
        self.assertEqual(
            1,
            len(
                self.result(_workspace(client, "query_log_list", {}))["items"]
            ),
        )
        self.assert_view_save_rejections(client, view)

    def assert_view_save_rejections(self, client, view):
        for args in (
            view | {"sql": "SELECT 1"},
            view | {"name": "Other"},
            {"sql": ""},
            {"sql": "SELECT 1; SELECT 2"},
            {"sql": "CREATE TABLE t (n INT)"},
        ):
            self.assertEqual(
                400, _workspace(client, "view_save", args).status_code
            )
        self.assertEqual(
            403,
            _workspace(
                client, "view_save", view, instance="foreign"
            ).status_code,
        )
        self.assertEqual(
            400,
            _workspace(
                client, "view_run", view | {"name": "Other"}
            ).status_code,
        )
        self.result(
            _workspace(
                client,
                "view_update",
                view | {"sql": "SELECT missing", "expected_revision": 1},
            )
        )
        failed = self.result(
            _workspace(client, "view_run", view | {"save": True})
        )
        self.assertEqual("failed", failed["status"])
        self.assertNotIn("saved_query_id", failed)
        self.assertEqual(
            3,
            len(
                self.result(_workspace(client, "query_saved_list", {}))[
                    "items"
                ]
            ),
        )

    def assert_partial(self, result):
        self.assertEqual("partial", result["outcome"])
        self.assertTrue(result["save_error"])
        self.assertNotIn("saved_query_id", result)

    def test_unavailable_saved_storage_keeps_completed_runs_pageable(self):
        client = self.server(writable=False)
        self.result(client.put("/generation", json=_generation()))
        run = self.result(_query(client, "SELECT 42", page_size=1, save=True))
        self.assert_partial(run)
        self.assertEqual(
            [[42]], self.result(self.page(client, run["query_id"]))["rows"]
        )
        view = self.view(client, "SELECT 43")
        result = self.result(
            _workspace(client, "view_run", view | {"save": True})
        )
        self.assert_partial(result)
        self.assertEqual("success", result["status"])
        fetch = self.result(_workspace(client, "view_fetch", view))
        self.assertEqual(
            (result["query_id"], [[43]]), (fetch["query_id"], fetch["rows"])
        )
        unavailable = _workspace(client, "view_save", view)
        self.assertEqual(409, unavailable.status_code, unavailable.text)
        self.assertEqual(
            [],
            self.result(_workspace(client, "query_saved_list", {}))["items"],
        )
