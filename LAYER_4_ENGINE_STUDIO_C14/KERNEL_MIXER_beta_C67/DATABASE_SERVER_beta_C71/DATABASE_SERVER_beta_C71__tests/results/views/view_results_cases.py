"""Additional View result test cases."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from . import test_view_results as source
from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


class ViewDirectiveTestCases:
    def test_strip_only_top_level_trailing_directives(self):
        with (
            TemporaryDirectory(dir="/tmp") as directory,
            _server(
                None,
                "--project-root",
                str(Path(directory).resolve()),
            ) as client,
        ):
            self.assertEqual(
                200, client.put("/generation", json=_generation()).status_code
            )
            opened = source.call(
                client, "workspace_open", {"session_id": "view-directives"}
            ).json()["result"]
            view = {
                "workspace_id": opened["workspace_id"],
                "view_id": opened["active_view_id"],
            }
            cases = self.directive_cases()
            for revision, (sql, expected) in enumerate(cases):
                with self.subTest(sql=sql):
                    response = source.call(
                        client,
                        "view_update",
                        view | {"sql": sql, "expected_revision": revision},
                    )
                    self.assertEqual(200, response.status_code, response.text)
                    checked = source.call(client, "view_check", view)
                    if expected is None:
                        self.assertNotEqual(
                            200, checked.status_code, checked.text
                        )
                        continue
                    self.assertEqual(200, checked.status_code, checked.text)
                    run = source.call(client, "view_run", view)
                    self.assertEqual(
                        "success", run.json()["result"]["status"], run.text
                    )
                    fetched = source.call(client, "view_fetch", view)
                    self.assertEqual(
                        [[expected]],
                        fetched.json()["result"]["rows"],
                        fetched.text,
                    )

    def directive_cases(self):
        directives = (
            "VIEW TABLE",
            "VIEW DOC",
            "VIEW DOCUMENT",
            "VIEW GRAPH",
            "VIEW GRAPH VERTICAL",
            "VIEW GRAPH HORIZONTAL",
            "VIEW IMPORTS",
            "VIEW IMPORTS VERTICAL",
            "VIEW IMPORTS HORIZONTAL",
            "VIEW STRUCTURE",
        )
        cases = [(f"SELECT 1 {directive}", 1) for directive in directives]
        cases += [
            ("SELECT 'VIEW GRAPH'", "VIEW GRAPH"),
            ("SELECT 1 -- VIEW GRAPH", 1),
            ("SELECT (SELECT 1 VIEW GRAPH)", None),
            ("SELECT 1 /* VIEW GRAPH", None),
            ("SELECT 1 VIEW /* comment */ GRAPH -- end", 1),
            ("SELECT 1 VIEW -- comment\n GRAPH /* end */ ; -- end", 1),
            ("SELECT 'é😀' /* outer /* inner */ end */ VIEW GRAPH", "é😀"),
            (
                "SELECT $tag$VIEW GRAPH ( /*$tag$ VIEW TABLE",
                "VIEW GRAPH ( /*",
            ),
            ('SELECT 1 VIEW "GRAPH"', None),
            ("SELECT 1 VIEW (GRAPH)", None),
            ("SELECT 1 VIEW GRAPH (HORIZONTAL)", None),
            ('SELECT 1 VIEW GRAPH "HORIZONTAL"', None),
            ('SELECT 1 VIEW IMPORTS "HORIZONTAL"', None),
            ("SELECT 1 VIEW GRAPH /*/", None),
            ("SELECT 1 VIEW GRAPH /* outer /* inner */", None),
        ]
        return cases


class ResultBudgetTestCases:
    def page(self, client, query_id):
        return client.post(
            "/database",
            json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 1},
        )

    def test_pinned_and_young_results_remain_pageable(self):
        with (
            TemporaryDirectory(dir="/tmp") as directory,
            _server(
                None, "--project-root", str(Path(directory).resolve())
            ) as client,
        ):
            self.assertEqual(
                200, client.put("/generation", json=_generation()).status_code
            )
            young = _query(client, "SELECT 1", page_size=1).json()["result"][
                "query_id"
            ]
            views = self.create_budget_views(client)
            for _ in range(300):
                direct = _query(client, "SELECT 2", page_size=1)
                self.assertEqual(200, direct.status_code, direct.text)
            self.assertEqual(
                [[1]], self.page(client, young).json()["result"]["rows"]
            )
            for view, query_id in views:
                self.assertEqual(
                    [[42]],
                    self.page(client, query_id).json()["result"]["rows"],
                )
                self.assertEqual(
                    query_id,
                    source.call(client, "view_fetch", view).json()["result"][
                        "query_id"
                    ],
                )

    def create_budget_views(self, client):
        views = []
        for number in range(17):
            opened = source.call(
                client,
                "workspace_open",
                {"session_id": f"budget-{number}"},
            ).json()["result"]
            view = {
                "workspace_id": opened["workspace_id"],
                "view_id": opened["active_view_id"],
            }
            updated = source.call(
                client,
                "view_update",
                view | {"sql": "SELECT 42", "expected_revision": 0},
            )
            self.assertEqual(200, updated.status_code, updated.text)
            run = source.call(client, "view_run", view).json()["result"]
            self.assertEqual("success", run["status"])
            views.append((view, run["query_id"]))
        return views

    def test_budget_refuses_refresh_and_preserves_generation_and_results(self):
        with _server() as client:
            original = client.put("/generation", json=_generation()).json()[
                "result"
            ]["generation"]
            sql = (
                "SELECT repeat('x', length(\"content.summary\") * 100) FROM "
                "atoms, range(1000)"
            )
            ids = []
            for _ in range(17):
                response = _query(client, sql, page_size=1)
                self.assertEqual(200, response.status_code, response.text)
                ids.append(response.json()["result"]["query_id"])
            candidate = _generation()
            candidate["snapshot"]["atoms"][0]["summary"] = "0123456789"
            refused = client.put(
                "/generation", json=candidate | {"refresh_target": "all"}
            )
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("cache is full", refused.text)
            self.assertEqual(
                original, client.get("/health").json()["result"]["generation"]
            )
            self.assertEqual(
                [["first"]],
                _query(
                    client, 'SELECT "content.summary" FROM atoms', page_size=1
                ).json()["result"]["rows"],
            )
            self.assertEqual(
                [["x" * 500]],
                self.page(client, ids[0]).json()["result"]["rows"],
            )
            for _ in range(20):
                response = _query(client, sql, page_size=1)
                if response.status_code != 200:
                    break
            self.assertEqual(400, response.status_code, response.text)
            self.assertIn("cache is full", response.text)
            self.assertEqual(
                [["x" * 500]],
                self.page(client, ids[0]).json()["result"]["rows"],
            )


class WorkspaceDocumentTestCases:
    def test_persisted_shape_and_malformed_documents(self):
        root = Path(
            self.enterContext(TemporaryDirectory(dir="/tmp"))
        ).resolve()
        with _server(None, "--project-root", str(root)) as client:
            self.assertEqual(
                200, client.put("/generation", json=_generation()).status_code
            )
            response = source.call(
                client, "workspace_open", {"session_id": "test"}
            )
            self.assertEqual(200, response.status_code, response.text)
            opened = response.json()["result"]
            view_id = opened["active_view_id"]
            args = {"workspace_id": "test", "view_id": view_id}
            self.assertEqual(
                200,
                source.call(
                    client, "view_rename", args | {"name": "named"}
                ).status_code,
            )
            path = next(
                (root / ".anechoic_runtime/iwe_console/beta/workspaces").glob(
                    "*.json"
                )
            )
            document = json.loads(path.read_text())
            self.assertEqual("named", document["views"][0]["name"])
            self.assertEqual(
                document,
                source.call(
                    client, "workspace_get", {"workspace_id": "test"}
                ).json()["result"],
            )
            self.assertEqual(
                200,
                source.call(
                    client, "view_rename", args | {"name": " "}
                ).status_code,
            )
            self.assertNotIn("name", json.loads(path.read_text())["views"][0])
            self.assert_malformed_views(client, path, document)

    def assert_malformed_views(self, client, path, document):
        for key, value in (
            ("name", None),
            ("revision", True),
            ("sql", "\ud800"),
        ):
            broken = json.loads(path.read_text())
            broken["views"][0][key] = value
            path.write_text(json.dumps(broken))
            with self.subTest(key=key):
                response = source.call(
                    client, "workspace_get", {"workspace_id": "test"}
                )
                self.assertEqual(400, response.status_code, response.text)
                self.assertEqual(
                    "workspace is unavailable",
                    response.json()["error"]["message"],
                )
            path.write_text(json.dumps(document))
