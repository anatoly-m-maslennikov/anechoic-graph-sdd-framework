
"""Resource-registry checks for the native Workbench MCP App."""

from __future__ import annotations

import asyncio
from pathlib import Path
import unittest
from unittest.mock import patch

from mcp import MCPError, types


EXTENSION = Path(__file__).resolve().parents[1]
APPS = EXTENSION.parents[1]

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_CODEX_EXTENSION import FEATURE_CODEX_EXTENSION__shared as shared  # noqa: E402


class MCPAppProbeTests(unittest.TestCase):
    def test_registry_lists_probe_and_workbench_resources(self) -> None:
        resources = asyncio.run(shared.list_resources(None, None)).resources

        self.assertEqual(["ui://anechoic/workbench-compatibility-v2.html", "ui://anechoic/workbench.html"],
                         [resource.uri for resource in resources])
        self.assertTrue(all(resource.mime_type == "text/html;profile=mcp-app" for resource in resources))

    def test_read_workbench_uses_built_resource(self) -> None:
        with patch.object(Path, "read_text", return_value="<html>built workbench</html>"):
            result = asyncio.run(shared.read_resource(
                None, types.ReadResourceRequestParams(uri="ui://anechoic/workbench.html"),
            ))

        self.assertEqual("ui://anechoic/workbench.html", result.contents[0].uri)
        self.assertEqual("text/html;profile=mcp-app", result.contents[0].mime_type)
        self.assertEqual("<html>built workbench</html>", result.contents[0].text)

    def test_missing_workbench_resource_is_an_mcp_error(self) -> None:
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            with self.assertRaises(MCPError):
                asyncio.run(shared.read_resource(
                    None, types.ReadResourceRequestParams(uri="ui://anechoic/workbench.html"),
                ))

    def test_probe_contract_is_retained(self) -> None:
        self.assertEqual(("workbench_ui_probe", "workbench_ui_ping"), tuple(tool.name for tool in shared.tools()))
        self.assertEqual({"message": "ANECHOIC MCP App resource loaded"},
                         shared.call("workbench_ui_probe"))
        self.assertEqual({"message": "Tool bridge passed"}, shared.call("workbench_ui_ping"))

    def test_shared_interface_refuses_unknown_resource_and_tool(self) -> None:
        with self.assertRaises(MCPError) as raised:
            asyncio.run(shared.read_resource(
                None, types.ReadResourceRequestParams(uri="ui://anechoic/unknown.html"),
            ))
        self.assertEqual(-32002, raised.exception.error.code)
        self.assertEqual("Unknown UI resource", raised.exception.error.message)

        with self.assertRaisesRegex(ValueError, "Unknown UI probe tool"):
            shared.call("unknown_tool")


if __name__ == "__main__":
    unittest.main()
