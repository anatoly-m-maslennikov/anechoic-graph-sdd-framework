"""Keep MCP request metadata across the two gateway boundaries."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"
sys.path[:0] = [str(MCP), str(TOOLS)]

from health_observations import HealthObservations  # noqa: E402
from mcp import types  # noqa: E402
from native_project_selection import NativeProjectSelection  # noqa: E402
from shared_gateway import SharedGateway  # noqa: E402


def _params() -> types.CallToolRequestParams:
    return types.CallToolRequestParams(
        name="echo", arguments={"project_root": "/project", "request": "value"},
        meta={"progressToken": "progress"},
    )


class MetaForwardingTests(unittest.IsolatedAsyncioTestCase):
    async def test_shared_gateway_preserves_meta_when_stripping_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = Path(".anechoic_fixture")
            selection = NativeProjectSelection(
                root, root / control, control, "a" * 64, "Test", "TEST",
                root / control / "manifest.md", "TEST-S-1@1", "b" * 64,
            )
            inner = SimpleNamespace(call=AsyncMock(return_value=types.CallToolResult(content=[])))
            entry = SimpleNamespace(selection=selection, gateway=inner)
            gateway = object.__new__(SharedGateway)
            gateway.frontier = object()
            gateway.pool = SimpleNamespace(
                acquire=AsyncMock(return_value=entry), release=AsyncMock(),
            )
            gateway.health_observations = HealthObservations()
            gateway._arguments = lambda _params: (selection, {"request": "value"})
            gateway._current_config = lambda: None
            gateway._selection = lambda _root: selection
            gateway._current_tool = lambda *_args: None
            gateway._remember_project = lambda *_args: None
            params = _params()
            await gateway.call(None, params)
            forwarded = inner.call.await_args.args[1]
            self.assertEqual(params.meta, forwarded.meta)
            self.assertEqual({"request": "value"}, forwarded.arguments)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
