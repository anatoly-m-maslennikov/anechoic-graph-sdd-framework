"""Focused shared-MCP routing checks; native behavior remains a fixture."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND \
    .FEATURE_IWE_CONSOLE_BACKEND__shared \
    import load_host_runtime_config  # fmt: skip

# fmt: off
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND \
    import shared_backend_process as backend_process
# fmt: on
from mcp import types  # noqa: E402
from ....runtime.launch.group_1.test_native_startup import (
    RuntimeSelectionTests,
)
from .shared_backend_fixture import backend_gateway


from ....runtime.http.group_2.gateway_test_fixtures import _Gateway
from ....runtime.http.group_2.gateway_test_fixtures import _Session
from ....runtime.http.group_2.gateway_test_fixtures import _tool
from ....runtime.http.group_1.gateway_test_cases import GatewayCases

MCP = Path(__file__).resolve().parents[4]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"


class SharedGatewayTests(GatewayCases, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.projects = self.base / "My_Repos"
        self.projects.mkdir()
        self.roots = [self._project(name) for name in ("alpha", "beta")]
        self.nested = self._project("nested/project")
        self.config_path = (
            self.base / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        )
        self._config(max_loaded=2)
        _Gateway.tools_by_root = {
            str(root): [_tool()] for root in (*self.roots, self.nested)
        }
        _Gateway.blacklist_by_root, _Gateway.hold = {}, None

    def _project(self, name):
        root = self.projects / name
        control = root / (".anechoic_" + root.name)
        RuntimeSelectionTests.manifest(
            self,
            control,
            name=root.name,
            prefix=root.name.upper(),
            component="C00",
        )
        return root

    def _config(self, max_loaded):
        self.config_path.write_text(
            "schema_version=1\n[shared_mcp]\n"
            f'projects_root="{self.projects}"\n'
            f"http_port=8092\nmax_loaded_projects={max_loaded}\n"
        )

    async def _gateway(self):
        return await self.enterAsyncContext(
            backend_gateway(
                load_host_runtime_config(self.config_path), _Session
            )
        )

    async def test_single_project_catalog_and_routing_include_lifecycle(self):
        root = self.roots[0]
        self.config_path.write_text(
            (
                'schema_version=1\n[shared_mcp]\nproject_root="'
                f"{root}"
                '"\nhttp_port=8092\n'
            )
        )
        name = "atom_lifecycle_archive"
        _Gateway.tools_by_root[str(root)] = [_tool(), _tool(name)]
        gateway = await self._gateway()
        self.assertEqual({"echo", name}, {tool.name for tool in gateway.tools})
        for tool in ("echo", name):
            for selected, expected_error in (
                (root, False),
                (self.roots[1], True),
            ):
                result = await gateway.call(
                    None,
                    types.CallToolRequestParams(
                        name=tool,
                        arguments={
                            "project_root": str(selected),
                            "request": "x",
                        },
                    ),
                )
                self.assertEqual(expected_error, bool(result.is_error))
                if expected_error:
                    self.assertEqual(
                        ["outside_project_root"],
                        result.structured_content["diagnostics"],
                    )

    async def test_project_error_codes_do_not_depend_on_message_wording(self):
        backend = backend_process

        coordinator = backend.SharedBackend(
            load_host_runtime_config(self.config_path), _Session
        )
        for error, expected in (
            (
                backend.OutsideProjectRootError("a different explanation"),
                "outside_project_root",
            ),
            (
                backend.HostRuntimeConfigError("outside is mentioned here"),
                "invalid_project_root",
            ),
        ):
            with (
                self.subTest(error=error),
                patch.object(
                    backend, "resolve_host_project", side_effect=error
                ),
            ):
                with self.assertRaises(backend.SharedProjectRefusal) as caught:
                    coordinator.select(str(self.roots[0]))
                self.assertEqual(expected, str(caught.exception))

    async def test_omitted_call_arguments_report_missing_project_root(self):
        gateway = await self._gateway()
        result = await gateway.call(
            None, types.CallToolRequestParams(name="echo")
        )
        self.assertTrue(result.is_error)
        self.assertEqual(
            ["missing_project_root"], result.structured_content["diagnostics"]
        )

    async def test_current_backend_refuses_foreign_project_before_tool_call(
        self,
    ):
        gateway = await self._gateway()
        root = str(self.roots[0])
        foreign = await gateway.select_project(str(self.roots[1]))
        with patch.object(_Session, "call_tool") as call:
            status, envelope = await gateway.tool_rest(
                "POST",
                headers={
                    "X-Anechoic-Project-Instance": foreign["instance_id"]
                },
                json={
                    "name": "echo",
                    "arguments": {"project_root": root, "request": "x"},
                    "session_id": None,
                    "public_base_url": None,
                },
            )
        self.assertEqual(200, status)
        self.assertIsNone(envelope["project"])
        self.assertEqual(
            "project_declarations_stale", envelope["error"]["code"]
        )
        call.assert_not_called()

    async def test_lifecycle_reuses_selected_project_and_rejects_replaced_root(
        self,
    ):
        name = "atom_lifecycle_archive"
        _Gateway.tools_by_root = {
            str(root): [_tool(name)] for root in (*self.roots, self.nested)
        }
        gateway = await self._gateway()

        async def call(root):
            return await gateway.call(
                None,
                types.CallToolRequestParams(
                    name=name,
                    arguments={"project_root": str(root), "request": "x"},
                ),
            )

        first = await call(self.roots[0])
        second = await call(self.roots[0])
        other = await call(self.roots[1])
        self.assertFalse(first.is_error)
        self.assertFalse(second.is_error)
        self.assertFalse(other.is_error)
        self.assertEqual(str(self.roots[1]), other.structured_content["root"])
        outside = await call(self.base)
        self.assertTrue(outside.is_error)
        self.assertEqual(
            ["outside_project_root"], outside.structured_content["diagnostics"]
        )
        original = self.roots[0].with_name("alpha-original")
        self.roots[0].rename(original)
        self.roots[0].mkdir()
        replaced = await call(self.roots[0])
        self.assertTrue(replaced.is_error)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
