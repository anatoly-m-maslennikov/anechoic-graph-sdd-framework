"""Real MCP transport and standalone hook caller-context checks."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from mcp import types
from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import load_host_runtime_config  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (  # noqa: E402
    RuntimeRequestContext,
    bind_request_context,
    current_request_context,
)
from .shared_backend_fixture import backend_gateway  # noqa: E402
from . import test_shared_gateway as shared_fixture  # noqa: E402


class _ContextGateway(shared_fixture._Session):
    barrier = None

    async def call_tool(self, _name, arguments, *, session_id, public_base_url, asserted_project_root):
        assert asserted_project_root == str(self.root)
        if self.barrier is not None:
            await self.barrier.wait()
        else:
            await asyncio.sleep(0)
        value = {"root": str(self.root), "arguments": arguments, "context_session": session_id}
        return {"value": value, "text": None}


class _CancelledGateway(_ContextGateway):
    async def call_tool(self, _name, arguments, *, session_id, public_base_url, asserted_project_root):
        assert asserted_project_root == str(self.root)
        assert session_id == "cancelled-session"
        raise asyncio.CancelledError


class CallerContextE2ETests(unittest.IsolatedAsyncioTestCase):
    setUp = shared_fixture.SharedGatewayTests.setUp
    _project = shared_fixture.SharedGatewayTests._project
    _config = shared_fixture.SharedGatewayTests._config

    async def _gateway(self, factory=_ContextGateway):
        config = load_host_runtime_config(self.config_path)
        return await self.enterAsyncContext(backend_gateway(config, factory))

    def _event(self, cwd, session, native_session="native-session"):
        return {
            "tool_name": "mcp__anechoic__echo",
            "session_id": session,
            "cwd": str(cwd),
            "tool_input": {"session_id": native_session},
        }

    def _run_hook(self, event):
        hook = PROGRAMMATIC / "FEATURE_CODEX_HOOK" / "codex_hook.py"
        result = subprocess.run(
            [sys.executable, "-B", str(hook)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def _hook_inputs(self):
        inputs = []
        for index, root in enumerate(self.roots):
            (root / ".git").mkdir()
            cwd = root / "nested"
            cwd.mkdir()
            hook = self._run_hook(self._event(cwd, f"codex-{index}"))
            inputs.append(hook["hookSpecificOutput"]["updatedInput"])
        return inputs

    async def test_hook_context_reaches_native_tool_for_two_concurrent_projects(self):
        tool = types.Tool(
            name="echo",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                },
                "required": ["session_id"],
                "additionalProperties": False,
            },
            outputSchema={"type": "object"},
        )
        _ContextGateway.tools_by_root = {str(root): [tool] for root in (*self.roots, self.nested)}
        gateway = await self._gateway()
        self.assertEqual({}, self._run_hook({"tool_name": "unrelated"}))

        async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
            async with ClientSession(*streams) as client:
                await client.initialize()
                listed = (await client.list_tools()).tools[0]
                self.assertIn("caller_context", listed.input_schema["properties"])
                inputs = self._hook_inputs()
                _ContextGateway.barrier = asyncio.Barrier(2)
                first, second = await asyncio.wait_for(
                    asyncio.gather(*(client.call_tool("echo", arguments) for arguments in inputs)),
                    timeout=3,
                )
                _ContextGateway.barrier = None
                for index, response in enumerate((first, second)):
                    self.assertFalse(response.is_error, response.structured_content)
                    self.assertEqual(str(self.roots[index]), response.structured_content["root"])
                    self.assertEqual(
                        {"session_id": "native-session"}, response.structured_content["arguments"]
                    )
                    self.assertEqual(
                        f"codex-{index}", response.structured_content["context_session"]
                    )
                stateless = await client.call_tool(
                    "echo", {"project_root": str(self.roots[0]), "session_id": "native"}
                )
                self.assertIsNone(stateless.structured_content["context_session"])

    async def _call_echo(self, gateway, root, context):
        return await gateway.call(
            None,
            types.CallToolRequestParams(
                name="echo", arguments={"project_root": root, "caller_context": context},
            ),
        )

    async def test_invalid_or_conflicting_context_does_not_invoke_a_tool(self):
        tool = types.Tool(
            name="echo",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        )
        _ContextGateway.tools_by_root = {str(root): [tool] for root in (*self.roots, self.nested)}
        gateway = await self._gateway()
        root = str(self.roots[0])
        with patch.object(_ContextGateway, "call_tool", side_effect=AssertionError("must not invoke")):
            for invalid in (
                None,
                {},
                {"session_id": ""},
                {"session_id": "  "},
                {"session_id": 3},
                {"session_id": "x", "extra": 1},
            ):
                result = await self._call_echo(gateway, root, invalid)
                self.assertTrue(result.is_error, repr(invalid))
            with bind_request_context(RuntimeRequestContext("already-bound")):
                result = await self._call_echo(gateway, root, {"session_id": "different"})
                self.assertTrue(result.is_error)
            result = await self._call_echo(gateway, str(self.base), {"session_id": "session"})
            self.assertTrue(result.is_error)
        self.assertIsNone(current_request_context())

    async def test_context_is_reset_after_cancellation(self):
        tool = types.Tool(
            name="echo",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        )
        _ContextGateway.tools_by_root = {str(root): [tool] for root in (*self.roots, self.nested)}
        gateway = await self._gateway(_CancelledGateway)
        params = types.CallToolRequestParams(
            name="echo",
            arguments={
                "project_root": str(self.roots[0]),
                "caller_context": {"session_id": "cancelled-session"},
            },
        )
        with self.assertRaises(asyncio.CancelledError):
            await gateway.call(None, params)
        self.assertIsNone(current_request_context())
