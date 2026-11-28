"""Run Console View directives through the Current Kernel query entry."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import NonCallableMock

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    NativeQueryInputs,
    NativeQueryOwner,
    QueryExecutionError,
    QueryStore,
)


class ViewDirectiveTests(TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        control = Path("_anechoic_example")
        (root / control).mkdir()
        selection = NonCallableMock(
            spec_set=["root", "control_relative", "parameters"],
            root=root,
            control_relative=control,
            parameters={},
        )
        self.owner = NativeQueryOwner(
            selection, NativeQueryInputs(lambda *_: None, frozenset(), {})
        )
        repository = Path(__file__).resolve().parents[7]
        extensions = Path(
            os.environ.get(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                repository / ".anechoic_tmp/workbench/extensions",
            )
        )
        self.owner._store = QueryStore(
            native=True, extension_directory=extensions
        )
        self.owner._capture = NonCallableMock(spec_set=[])
        self.addCleanup(self.owner.close)

    def test_view_run_executes_sql_and_saves_the_authored_directive(self):
        sql = "SELECT 'π' AS value VIEW /* kind */ DOCUMENT -- authored\n"
        opened = self.owner.interface_call(
            "workspace_open", {"session_id": "view-directive"}
        )
        view = {
            "workspace_id": opened["workspace_id"],
            "view_id": opened["active_view_id"],
        }
        revision = self.owner.interface_call("view_get", view)["revision"]
        self.owner.interface_call(
            "view_update", view | {"sql": sql, "expected_revision": revision}
        )
        self.assertTrue(self.owner.interface_call("view_check", view)["valid"])
        run = self.owner.interface_call("view_run", view | {"save": True})
        self.assertEqual("success", run["status"], run)
        page = self.owner.interface_call(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        self.assertEqual([["π"]], page["rows"])
        self.assertEqual(sql, self.owner.load(run["saved_query_id"])["sql"])

    def test_plain_literal_and_nested_syntax_keep_normal_sql_meaning(self):
        literal = self.owner.run(
            "SELECT 'VIEW GRAPH'", result_delivery="inline"
        )
        self.assertEqual([["VIEW GRAPH"]], literal["rows"])
        with self.assertRaises(QueryExecutionError):
            self.owner.check("SELECT (SELECT 1 VIEW GRAPH)")
