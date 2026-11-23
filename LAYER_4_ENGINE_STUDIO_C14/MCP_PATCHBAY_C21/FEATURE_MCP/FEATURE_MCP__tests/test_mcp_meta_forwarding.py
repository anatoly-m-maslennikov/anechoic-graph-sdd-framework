"""Keep request binding and caller context when MCP metadata is present."""

from types import SimpleNamespace
import unittest

from mcp import types
from . import test_shared_gateway as fixture
from .shared_backend_fixture import backend_gateway
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config


class _RecordingSession(fixture._Session):
    calls = []

    async def call_tool(self, name, arguments, *, session_id, public_base_url, asserted_project_root):
        self.calls.append((name, arguments, session_id, public_base_url, asserted_project_root))
        return await super().call_tool(name, arguments, session_id=session_id,
                                       public_base_url=public_base_url,
                                       asserted_project_root=asserted_project_root)


class MetaForwardingTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.SharedGatewayTests.setUp
    _project = fixture.SharedGatewayTests._project
    _config = fixture.SharedGatewayTests._config

    async def test_shared_gateway_binds_caller_and_arguments_with_meta_present(self):
        _RecordingSession.calls = []
        root = str(self.roots[0])
        async with backend_gateway(load_host_runtime_config(self.config_path), _RecordingSession) as gateway:
            result = await gateway.call(
                SimpleNamespace(request=SimpleNamespace(base_url="http://localhost/")),
                types.CallToolRequestParams(
                    name="echo", arguments={"project_root": root, "request": "value",
                                            "caller_context": {"session_id": "caller"}},
                    meta={"progressToken": "progress"},
                ),
            )
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual([("echo", {"request": "value"}, "caller", "http://localhost/", root)],
                         _RecordingSession.calls)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
