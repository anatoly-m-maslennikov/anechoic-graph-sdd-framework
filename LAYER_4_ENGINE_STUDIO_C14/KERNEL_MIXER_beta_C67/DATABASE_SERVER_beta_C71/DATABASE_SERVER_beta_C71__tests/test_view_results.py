"""Exercise View query behavior through the real Database Server socket."""

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from ..DATABASE_SERVER_beta_C71__shared import result_ttl
from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _launch_arguments, _query, _server


def call(client, operation, arguments):
    return client.post("/workspace", json=BINDING | {"operation": operation, "arguments": arguments})


class ResultTTLSettingsTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory(dir="/tmp"))).resolve()
        self.settings = self.root / ".anechoic_runtime/anechoic_runtime_settings.toml"
        self.settings.parent.mkdir()

    def test_missing_file_or_setting_uses_default_ttl(self):
        self.assertEqual(3600, result_ttl(self.root, None))
        self.settings.write_text("[workbench]\n", encoding="utf-8")
        self.assertEqual(3600, result_ttl(self.root, None))

    def test_startup_refuses_invalid_settings_before_listening(self):
        socket = self.root / "db.sock"
        command, environment = _launch_arguments(socket)
        for content, error in (
            ("[workbench]\nresult_ttl_seconds = 0\n", "positive integer"),
            ("[workbench\n", "TOMLDecodeError"),
        ):
            with self.subTest(content=content):
                self.settings.write_text(content, encoding="utf-8")
                result = subprocess.run(
                    [*command, "--project-root", str(self.root)], env=environment,
                    capture_output=True, text=True, timeout=10,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn(error, result.stderr)
                self.assertFalse(socket.exists())


class ViewResultsTest(unittest.TestCase):
    def value(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def open_view(self, client):
        self.value(client.put("/generation", json=_generation()))
        state = self.value(call(client, "workspace_open", {"session_id": "view-test"}))
        return {"workspace_id": state["workspace_id"], "view_id": state["active_view_id"]}

    def test_pinned_result_survives_expiry_until_view_removal(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            settings = root / ".anechoic_runtime/anechoic_runtime_settings.toml"
            settings.parent.mkdir(mode=0o700)
            settings.write_text("[workbench]\nresult_ttl_seconds = 1\n", encoding="utf-8")
            with _server(None, "--project-root", str(root)) as client:
                settings.write_text("[workbench]\nresult_ttl_seconds = 3600\n", encoding="utf-8")
                self.assert_pinned_expiry(client)

    def assert_pinned_expiry(self, client):
        view = self.open_view(client)
        self.value(call(client, "view_update", view | {"sql": "SELECT 42", "expected_revision": 0}))
        run = self.value(call(client, "view_run", view))
        self.assertEqual("success", run["status"])
        self.assertNotIn("rows", run)
        page_request = BINDING | {"query_id": run["query_id"], "offset": 0, "page_size": 1}
        first = self.value(_query(client, "SELECT 11", page_size=1))
        sleep(1.1)
        self.assertEqual([[42]], self.value(call(client, "view_fetch", view))["rows"])
        self.assertEqual([[42]], self.value(client.post("/database", json=page_request))["rows"])
        self.assertEqual(400, client.post("/database", json=page_request | {"query_id": first["query_id"]}).status_code)
        self.value(call(client, "view_create", {"workspace_id": view["workspace_id"]}))
        self.value(call(client, "view_remove", view))
        self.assertEqual(400, client.post("/database", json=page_request).status_code)

    def test_invalid_input_keeps_result_and_failed_run_removes_it(self):
        with TemporaryDirectory(dir="/tmp") as directory, _server(
            None, "--project-root", str(Path(directory).resolve()),
        ) as client:
            view = self.open_view(client)
            update = view | {"sql": "SELECT '😀'", "expected_revision": 0}
            self.value(call(client, "view_update", update))
            run = self.value(call(client, "view_run", view))
            self.assertEqual("success", run["status"])
            self.assertEqual(400, call(client, "view_run", view | {"cursor_position": 9}).status_code)
            checked = self.value(call(client, "view_check", view))
            self.assertTrue(checked["valid"])
            self.assertNotIn("sql", checked)
            fetched = self.value(call(client, "view_fetch", view | {"result_delivery": "inline"}))
            self.assertEqual(run["query_id"], fetched["query_id"])
            self.assertEqual([["😀"]], fetched["rows"])
            self.assertNotIn("sql", fetched)
            self.value(call(client, "view_update", update | {"sql": "SELECT missing", "expected_revision": 1}))
            self.assertEqual(run["query_id"], self.value(call(client, "view_fetch", view))["query_id"])
            failed = self.value(call(client, "view_run", view))
            self.assertEqual("failed", failed["status"])
            self.assertIsNone(failed["query_id"])
            self.assertEqual(400, call(client, "view_fetch", view).status_code)
            page = BINDING | {"query_id": run["query_id"], "offset": 0, "page_size": 1}
            self.assertEqual(400, client.post("/database", json=page).status_code)

    def test_restart_preserves_sql_without_result(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            arguments = (None, "--project-root", str(Path(directory).resolve()))
            with _server(*arguments) as client:
                view = self.open_view(client)
                self.value(call(client, "view_update", view | {"sql": "SELECT 7", "expected_revision": 0}))
                first = self.value(call(client, "view_run", view))
                self.assertEqual("success", first["status"])
            with _server(*arguments) as client:
                self.value(client.put("/generation", json=_generation()))
                returned = self.value(call(client, "view_get", view))
                self.assertEqual("SELECT 7", returned["sql"])
                self.assertNotIn("result", returned)
                self.assertEqual(400, call(client, "view_fetch", view).status_code)
                second = self.value(call(client, "view_run", view))
                self.assertNotEqual(first["query_id"], second["query_id"])


class ResultBudgetTest(unittest.TestCase):
    def page(self, client, query_id):
        return client.post("/database", json=BINDING | {"query_id": query_id, "offset": 0, "page_size": 1})

    def test_pinned_and_young_results_remain_pageable(self):
        with TemporaryDirectory(dir="/tmp") as directory, _server(None, "--project-root", str(Path(directory).resolve())) as client:
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            young = _query(client, "SELECT 1", page_size=1).json()["result"]["query_id"]
            views = []
            for number in range(17):
                opened = call(client, "workspace_open", {"session_id": f"budget-{number}"}).json()["result"]
                view = {"workspace_id": opened["workspace_id"], "view_id": opened["active_view_id"]}
                updated = call(client, "view_update", view | {"sql": "SELECT 42", "expected_revision": 0})
                self.assertEqual(200, updated.status_code, updated.text)
                run = call(client, "view_run", view).json()["result"]
                self.assertEqual("success", run["status"])
                views.append((view, run["query_id"]))
            for _ in range(300):
                direct = _query(client, "SELECT 2", page_size=1)
                self.assertEqual(200, direct.status_code, direct.text)
            self.assertEqual([[1]], self.page(client, young).json()["result"]["rows"])
            for view, query_id in views:
                self.assertEqual([[42]], self.page(client, query_id).json()["result"]["rows"])
                self.assertEqual(query_id, call(client, "view_fetch", view).json()["result"]["query_id"])

    def test_budget_refuses_refresh_and_preserves_generation_and_results(self):
        with _server() as client:
            original = client.put("/generation", json=_generation()).json()["result"]["generation"]
            sql = "SELECT repeat('x', length(\"content.summary\") * 100) FROM atoms, range(1000)"
            ids = []
            for _ in range(17):
                response = _query(client, sql, page_size=1)
                self.assertEqual(200, response.status_code, response.text)
                ids.append(response.json()["result"]["query_id"])
            candidate = _generation()
            candidate["snapshot"]["atoms"][0]["summary"] = "0123456789"
            refused = client.put("/generation", json=candidate | {"refresh_target": "all"})
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("cache is full", refused.text)
            self.assertEqual(original, client.get("/health").json()["result"]["generation"])
            self.assertEqual([["first"]], _query(client, 'SELECT "content.summary" FROM atoms', page_size=1).json()["result"]["rows"])
            self.assertEqual([["x" * 500]], self.page(client, ids[0]).json()["result"]["rows"])
            for _ in range(20):
                response = _query(client, sql, page_size=1)
                if response.status_code != 200:
                    break
            self.assertEqual(400, response.status_code, response.text)
            self.assertIn("cache is full", response.text)
            self.assertEqual([["x" * 500]], self.page(client, ids[0]).json()["result"]["rows"])


class WorkspaceDocumentTest(unittest.TestCase):
    def test_persisted_shape_and_malformed_documents(self):
        root = Path(self.enterContext(TemporaryDirectory(dir="/tmp"))).resolve()
        with _server(None, "--project-root", str(root)) as client:
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            response = call(client, "workspace_open", {"session_id": "test"})
            self.assertEqual(200, response.status_code, response.text)
            opened = response.json()["result"]
            view_id = opened["active_view_id"]
            args = {"workspace_id": "test", "view_id": view_id}
            self.assertEqual(200, call(client, "view_rename", args | {"name": "named"}).status_code)
            path = next((root / ".anechoic_runtime/workbench/beta/workspaces").glob("*.json"))
            document = json.loads(path.read_text())
            self.assertEqual("named", document["views"][0]["name"])
            self.assertEqual(document, call(client, "workspace_get", {"workspace_id": "test"}).json()["result"])
            self.assertEqual(200, call(client, "view_rename", args | {"name": " "}).status_code)
            self.assertNotIn("name", json.loads(path.read_text())["views"][0])
            for key, value in (("name", None), ("revision", True), ("sql", "\ud800")):
                broken = json.loads(path.read_text())
                broken["views"][0][key] = value
                path.write_text(json.dumps(broken))
                with self.subTest(key=key):
                    response = call(client, "workspace_get", {"workspace_id": "test"})
                    self.assertEqual(400, response.status_code, response.text)
                    self.assertEqual("workspace is unavailable", response.json()["error"]["message"])
                path.write_text(json.dumps(document))
