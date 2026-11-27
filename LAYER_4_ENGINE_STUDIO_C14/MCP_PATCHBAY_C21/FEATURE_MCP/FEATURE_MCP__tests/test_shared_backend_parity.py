"""Shared Workbench transports use one selected native backend lease."""

from __future__ import annotations

import asyncio
from pathlib import Path
import tempfile
import unittest

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    load_host_runtime_config,
)
from mcp import types  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.project_tool_session import (  # noqa: E402
    ToolProtocolError as BackendToolProtocolError,
)
from .test_native_startup import RuntimeSelectionTests  # noqa: E402
from .shared_backend_fixture import backend_gateway  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (  # noqa: E402
    SharedGatewayRefusal,
)


class _Workbench:
    hold: asyncio.Event | None = None
    started: asyncio.Event | None = None

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def call(
        self, name: str, arguments: dict[str, object]
    ) -> dict[str, object]:
        self.calls.append((name, arguments))
        if self.started is not None:
            self.started.set()
        if self.hold is not None:
            await self.hold.wait()
        if arguments.get("sql") == "bad":
            raise BackendToolProtocolError("query_error", "bad query")
        return {"outcome": "completed", "name": name, "arguments": arguments}


class _Gateway:
    blacklists: dict[str, frozenset[str]] = {}
    workbenches: list[_Workbench] = []
    tool_calls = 0

    def __init__(self, root: Path, *, selection: object) -> None:
        self.root = Path(root)
        self.selection = selection
        self.tool_blacklist = self.blacklists.get(str(root), frozenset())
        self.ready = True
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
            FEATURE_IWE_CONSOLE_BACKEND__shared \
            import native_tools  # fmt: skip

        self.tools = [
            tool.model_dump(mode="json", by_alias=True)
            for tool in native_tools()
        ]
        self.workbench = _Workbench()
        self.workbenches.append(self.workbench)

    async def initialize(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def ensure_current(self) -> None:
        return None

    async def call_tool(
        self,
        name,
        arguments,
        *,
        session_id,
        public_base_url,
        asserted_project_root,
    ):
        type(self).tool_calls += 1
        return {
            "value": await self.workbench.call(name, arguments),
            "text": None,
        }


class SharedBackendParityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.projects = self.base / "My_Repos"
        self.roots = [self._project(name) for name in ("alpha", "beta")]
        self.config_path = (
            self.base / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        )
        _Gateway.blacklists = {}
        _Gateway.workbenches = []
        _Gateway.tool_calls = 0
        _Workbench.hold = None
        _Workbench.started = None

    def _project(self, name: str) -> Path:
        root = self.projects / name
        control = root / f".anechoic_{name}"
        RuntimeSelectionTests.manifest(
            self,
            control,
            name=root.name,
            prefix=root.name.upper(),
            component="C00",
        )
        return root

    async def _gateway(self, max_loaded: int = 2):
        self.config_path.write_text(
            "schema_version=1\n[shared_mcp]\n"
            f'projects_root="{self.projects}"\nhttp_port=8092\nmax_loaded_projects={max_loaded}\n'
        )
        return await self.enterAsyncContext(
            backend_gateway(
                load_host_runtime_config(self.config_path), _Gateway
            )
        )

    async def test_mcp_and_native_workbench_return_the_same_result(
        self,
    ) -> None:
        gateway = await self._gateway()
        arguments = {"project_root": str(self.roots[0]), "sql": "SELECT 1"}

        native = (await gateway.call_tool("query_run", arguments))["value"]
        mcp = await gateway.call(
            None,
            types.CallToolRequestParams(name="query_run", arguments=arguments),
        )

        self.assertEqual(native, mcp.structured_content)
        self.assertEqual(2, _Gateway.tool_calls)
        self.assertEqual({"sql": "SELECT 1"}, native["arguments"])
        rows = (await gateway.status())["calls"]
        self.assertEqual(
            ["completed", "completed"], [row["outcome"] for row in rows]
        )

    async def test_cancellation_releases_the_shared_project_lease(
        self,
    ) -> None:
        gateway = await self._gateway(max_loaded=1)
        _Workbench.hold = asyncio.Event()
        _Workbench.started = asyncio.Event()
        pending = asyncio.create_task(
            gateway.call_tool(
                "query_run",
                {"project_root": str(self.roots[0]), "sql": "SELECT 1"},
            )
        )
        await asyncio.wait_for(_Workbench.started.wait(), 10)
        pending.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await pending

        _Workbench.hold = None
        response = await gateway.call_tool(
            "query_run",
            {"project_root": str(self.roots[1]), "sql": "SELECT 2"},
        )
        self.assertEqual("completed", response["value"]["outcome"])

    async def test_native_query_error_keeps_a_returned_error_observation(
        self,
    ) -> None:
        gateway = await self._gateway()

        with self.assertRaisesRegex(ToolProtocolError, "bad query"):
            await gateway.call_tool(
                "query_run", {"project_root": str(self.roots[0]), "sql": "bad"}
            )

        row = (await gateway.status())["calls"][-1]
        self.assertEqual("failed", row["outcome"])
        self.assertEqual("returned-error", row["error_category"])

    async def test_foreign_and_disabled_project_bindings_refuse(self) -> None:
        _Gateway.blacklists = {str(self.roots[0]): frozenset({"query_run"})}
        gateway = await self._gateway()

        with self.assertRaises(SharedGatewayRefusal) as outside:
            await gateway.call_tool(
                "query_run",
                {"project_root": str(self.base), "sql": "SELECT 1"},
            )
        with self.assertRaises(SharedGatewayRefusal) as disabled:
            await gateway.call_tool(
                "query_run",
                {"project_root": str(self.roots[0]), "sql": "SELECT 1"},
            )

        self.assertEqual("outside_project_root", outside.exception.code)
        self.assertEqual(
            "project_tool_frontier_stale", disabled.exception.code
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
