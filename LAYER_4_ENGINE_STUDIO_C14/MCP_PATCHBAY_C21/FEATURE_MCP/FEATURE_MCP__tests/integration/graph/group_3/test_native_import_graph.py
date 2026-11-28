"""Exercise the Import Graph through the native Workbench routes."""

from dataclasses import replace
import subprocess
import unittest
from unittest.mock import patch

from watchdog.observers.polling import PollingObserver

from ...query.group_1 import test_native_query_stdio as fixture
from ....native_query_test_support import create_native_gateway
from ..group_2.native_import_graph_cases_1 import ImportGraphCases1
from ..group_2.native_import_graph_cases_2 import ImportGraphCases2
from ..group_2.native_import_graph_cases_3 import ImportGraphCases3
from ..group_1.native_import_graph_cases_4 import ImportGraphCases4
from ..group_1.native_import_graph_rebuild_cases import ImportGraphRebuildCases


class NativeImportGraphTests(
    ImportGraphCases1,
    ImportGraphCases2,
    ImportGraphCases3,
    ImportGraphCases4,
    ImportGraphRebuildCases,
    unittest.IsolatedAsyncioTestCase,
):
    _write = fixture.NativeQueryStdioTests._write

    def setUp(self):
        fixture.NativeQueryStdioTests.setUp(self)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def _source(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    async def _gateway(self, *, enabled=True, structure_snapshot=None):
        inputs = fixture._native_inputs()

        def validate(fields, component):
            manifest = inputs.validate_manifest(fields, component)
            workbench = {
                "import_graph": {"python_roots": ["src"]} if enabled else False
            }
            return replace(
                manifest, parameters={"runtime": {"workbench": workbench}}
            )

        gateway = create_native_gateway(
            self.root,
            fixture.CONTROL,
            replace(inputs, validate_manifest=validate),
        )
        if structure_snapshot is not None:
            selected = replace(
                gateway.selection, structure_snapshot=structure_snapshot
            )
            gateway.selection = gateway._native_query.selection = selected
        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_watche"
                "r__pub.NativeObserver"
            ),
            lambda: PollingObserver(timeout=0.05),
        ):
            await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        return gateway
