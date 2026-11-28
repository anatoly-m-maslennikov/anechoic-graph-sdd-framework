"""Exercise the Import Graph through the native Workbench routes."""

from mcp import types

from ...query.group_1 import test_native_query_stdio as fixture
from .native_import_graph_boundary_cases import _BoundaryCases
from ..group_1.native_import_graph_package_audit_cases import (
    _PackageAuditCases,
)
from ..group_3.native_import_graph_misc_cases import _MiscImportGraphCases


class ImportGraphCases3(
    _PackageAuditCases, _BoundaryCases, _MiscImportGraphCases
):
    async def test_manifest_previous_image_import_is_scoped_to_source(self):
        from ....native_query_test_support import create_native_gateway

        self._source("src/app/client.py", "import old_image.runtime\n")
        self._source("src/app/other.py", "import old_image.runtime\n")
        manifest = self.root / fixture.CONTROL / fixture.MANIFEST
        text = manifest.read_text(encoding="utf-8")
        text = text.replace(
            'ProjectManifest(name="Anechoic", prefix="AN")',
            'ProjectManifest(name="Anechoic", prefix="AN", parameters={"runtime": {"workbench": '
            '{"import_graph": {"python_roots": ["src"], "python_image_imports": '
            '{"src/app/client.py": ["old_image.runtime"]}}}}})',
        )
        manifest.write_text(text, encoding="utf-8")
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)

        response = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={
                    "sql": "SELECT i.source_key, i.resolution_status, i.target_key, n.scan_status "
                    "FROM module_imports i LEFT JOIN import_nodes n ON n.node_key = i.target_key "
                    "WHERE i.written_specifier = 'old_image.runtime' ORDER BY i.source_key",
                    "result_delivery": "inline",
                },
            ),
        )
        self.assertFalse(response.is_error, response.structured_content)
        self.assertEqual(
            [
                [
                    "module:src/app/client.py",
                    "external",
                    "module:external:previous-image:old_image.runtime",
                    "declared_previous_image",
                ],
                ["module:src/app/other.py", "unresolved", None, None],
            ],
            response.structured_content["rows"],
        )
