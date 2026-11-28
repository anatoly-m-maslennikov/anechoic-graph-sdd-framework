"""Exercise View query behavior through the real Database Server socket."""

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_settings import (
    result_ttl,
)
from .view_results_cases import (
    ViewDirectiveTestCases,
    ResultBudgetTestCases,
    WorkspaceDocumentTestCases,
)
from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _launch_arguments,
    _query,
    _server,
)


def call(client, operation, arguments):
    return client.post(
        "/workspace",
        json=BINDING | {"operation": operation, "arguments": arguments},
    )


class ViewDirectiveTest(ViewDirectiveTestCases, unittest.TestCase):
    pass


class ResultTTLSettingsTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(
            self.enterContext(TemporaryDirectory(dir="/tmp"))
        ).resolve()
        self.settings = (
            self.root / ".anechoic_runtime/anechoic_runtime_settings.toml"
        )
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
                    [*command, "--project-root", str(self.root)],
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=10,
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
        state = self.value(
            call(client, "workspace_open", {"session_id": "view-test"})
        )
        return {
            "workspace_id": state["workspace_id"],
            "view_id": state["active_view_id"],
        }

    def test_view_directive_is_preserved_for_check_run_and_save(self):
        with (
            TemporaryDirectory(dir="/tmp") as directory,
            _server(
                None,
                "--project-root",
                str(Path(directory).resolve()),
                "--journal-relative",
                "control/journal",
            ) as client,
        ):
            view = self.open_view(client)
            sql = "SELECT 42 /* é😀 */ VIEW /* comment */ IMPORTS -- comment\n HORIZONTAL; /* end */"
            self.value(
                call(
                    client,
                    "view_update",
                    view | {"sql": sql, "expected_revision": 0},
                )
            )
            self.assertTrue(
                self.value(call(client, "view_check", view))["valid"]
            )
            run = self.value(call(client, "view_run", view | {"save": True}))
            self.assertEqual("success", run["status"])
            saved_run = self.value(
                call(
                    client, "query_load", {"reference": run["saved_query_id"]}
                )
            )
            self.assertEqual(sql, saved_run["sql"])
            self.assertEqual(
                [[42]], self.value(call(client, "view_fetch", view))["rows"]
            )
            self.assertEqual(
                sql, self.value(call(client, "view_get", view))["sql"]
            )
            self.assert_saved_view(client, view, sql)

    def assert_saved_view(self, client, view, sql):
        snapshot = self.value(call(client, "view_save", view))
        saved = self.value(
            call(
                client,
                "query_load",
                {"reference": snapshot["saved_query_id"]},
            )
        )
        self.assertEqual(sql, saved["sql"])

    def test_pinned_result_survives_expiry_until_view_removal(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            settings = (
                root / ".anechoic_runtime/anechoic_runtime_settings.toml"
            )
            settings.parent.mkdir(mode=0o700)
            settings.write_text(
                "[workbench]\nresult_ttl_seconds = 1\n", encoding="utf-8"
            )
            with _server(None, "--project-root", str(root)) as client:
                settings.write_text(
                    "[workbench]\nresult_ttl_seconds = 3600\n",
                    encoding="utf-8",
                )
                self.assert_pinned_expiry(client)

    def assert_pinned_expiry(self, client):
        view = self.open_view(client)
        self.value(
            call(
                client,
                "view_update",
                view | {"sql": "SELECT 42", "expected_revision": 0},
            )
        )
        run = self.value(call(client, "view_run", view))
        self.assertEqual("success", run["status"])
        self.assertNotIn("rows", run)
        page_request = BINDING | {
            "query_id": run["query_id"],
            "offset": 0,
            "page_size": 1,
        }
        first = self.value(_query(client, "SELECT 11", page_size=1))
        sleep(1.1)
        self.assertEqual(
            [[42]], self.value(call(client, "view_fetch", view))["rows"]
        )
        self.assertEqual(
            [[42]],
            self.value(client.post("/database", json=page_request))["rows"],
        )
        self.assertEqual(
            400,
            client.post(
                "/database",
                json=page_request | {"query_id": first["query_id"]},
            ).status_code,
        )
        self.value(
            call(client, "view_create", {"workspace_id": view["workspace_id"]})
        )
        self.value(call(client, "view_remove", view))
        self.assertEqual(
            400, client.post("/database", json=page_request).status_code
        )

    def test_invalid_input_keeps_result_and_failed_run_removes_it(self):
        with (
            TemporaryDirectory(dir="/tmp") as directory,
            _server(
                None,
                "--project-root",
                str(Path(directory).resolve()),
            ) as client,
        ):
            view = self.open_view(client)
            update = view | {"sql": "SELECT '😀'", "expected_revision": 0}
            self.value(call(client, "view_update", update))
            run = self.value(call(client, "view_run", view))
            self.assertEqual("success", run["status"])
            self.assertEqual(
                400,
                call(
                    client, "view_run", view | {"cursor_position": 9}
                ).status_code,
            )
            checked = self.value(call(client, "view_check", view))
            self.assertTrue(checked["valid"])
            self.assertNotIn("sql", checked)
            fetched = self.value(
                call(
                    client, "view_fetch", view | {"result_delivery": "inline"}
                )
            )
            self.assertEqual(run["query_id"], fetched["query_id"])
            self.assertEqual([["😀"]], fetched["rows"])
            self.assertNotIn("sql", fetched)
            self.assert_failed_run(client, view, update, run)

    def assert_failed_run(self, client, view, update, run):
        self.value(
            call(
                client,
                "view_update",
                update | {"sql": "SELECT missing", "expected_revision": 1},
            )
        )
        self.assertEqual(
            run["query_id"],
            self.value(call(client, "view_fetch", view))["query_id"],
        )
        failed = self.value(call(client, "view_run", view))
        self.assertEqual("failed", failed["status"])
        self.assertIsNone(failed["query_id"])
        self.assertEqual(400, call(client, "view_fetch", view).status_code)
        page = BINDING | {
            "query_id": run["query_id"],
            "offset": 0,
            "page_size": 1,
        }
        self.assertEqual(400, client.post("/database", json=page).status_code)

    def test_restart_preserves_sql_without_result(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            arguments = (
                None,
                "--project-root",
                str(Path(directory).resolve()),
            )
            with _server(*arguments) as client:
                view = self.open_view(client)
                self.value(
                    call(
                        client,
                        "view_update",
                        view | {"sql": "SELECT 7", "expected_revision": 0},
                    )
                )
                first = self.value(call(client, "view_run", view))
                self.assertEqual("success", first["status"])
            with _server(*arguments) as client:
                self.value(client.put("/generation", json=_generation()))
                returned = self.value(call(client, "view_get", view))
                self.assertEqual("SELECT 7", returned["sql"])
                self.assertNotIn("result", returned)
                self.assertEqual(
                    400, call(client, "view_fetch", view).status_code
                )
                second = self.value(call(client, "view_run", view))
                self.assertNotEqual(first["query_id"], second["query_id"])


class ResultBudgetTest(ResultBudgetTestCases, unittest.TestCase):
    pass


class WorkspaceDocumentTest(WorkspaceDocumentTestCases, unittest.TestCase):
    pass
