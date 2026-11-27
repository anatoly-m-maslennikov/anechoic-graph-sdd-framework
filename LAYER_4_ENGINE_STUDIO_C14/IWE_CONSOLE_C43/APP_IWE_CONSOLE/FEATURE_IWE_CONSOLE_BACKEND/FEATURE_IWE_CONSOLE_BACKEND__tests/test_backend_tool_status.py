"""Exercise the actual Tool callback across the HTTP boundary."""
from unittest.mock import Mock, NonCallableMock

from pathlib import Path
import unittest
from unittest.mock import patch

import httpx2
from starlette.applications import Starlette
from starlette.routing import Route

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.backend_tool_api import (
    BackendToolAPI,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.project_tool_session import (
    ProjectToolSession, ToolProtocolError as SessionError,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.tool_registry_runtime import (
    ToolInputValidationError, ToolRegistryStaleError,
)


class Registry:
    def __init__(self):
        self.ensure_current = Mock(return_value=None)

    def permits(self, name):
        return name != "missing"

    async def call(self, name, arguments, *, context):
        if name == "invalid":
            raise ToolInputValidationError("bad arguments")
        if name == "stale":
            raise ToolRegistryStaleError("changed")
        if name == "broken":
            raise RuntimeError("secret detail")
        return {"ok": True}


def make_tool_app():
    """Build the production callback with a deterministic local registry."""
    selection = NonCallableMock(
        spec_set=["instance_id", "root", "host_root"],
        instance_id="test",
        root=Path("/test"),
        host_root=None,
    )
    api = BackendToolAPI(
        NonCallableMock(spec_set=["selection"], selection=selection), {}
    )
    api._registry, api._selection, api._blacklist = (
        Registry(),
        selection,
        frozenset(),
    )
    return Starlette(routes=[Route("/", api.invoke, methods=["POST"])])


def envelope(name):
    return {
        "name": name,
        "arguments": {},
        "instance_id": "test",
        "session_id": None,
        "public_base_url": None,
        "asserted_project_root": None,
    }


class ToolStatusTests(unittest.IsolatedAsyncioTestCase):
    def test_status_aliases_dispatch_and_descriptors(self):
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.workbench_operations import (
            WorkbenchOperations,
        )
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.workbench_tools import (
            native_tools,
        )

        operations = WorkbenchOperations(
            query_owner=NonCallableMock(
                spec_set=["status"], status=lambda: {"ready": True}
            )
        )
        for name in ("iwe_console_status", "workbench_status"):
            self.assertIn(name, [tool.name for tool in native_tools()])
            self.assertEqual({"ready": True}, operations.call(name, {}))
            with self.assertRaises(ValueError):
                operations.call(name, {"extra": True})

    def test_status_blacklist_blocks_both_names(self):
        module = (
            'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.backe'
            'nd_tool_api'
        )
        selection = NonCallableMock(
            spec_set=["root", "parameters"], root=Path("/test"), parameters={}
        )
        api = BackendToolAPI(
            NonCallableMock(spec_set=["selection"], selection=selection), {}
        )
        with (
            patch(f"{module}.pinned_project", return_value=selection),
            patch(
                f"{module}.load_active_registry",
                return_value=NonCallableMock(
                    spec_set=["global_blacklist"], global_blacklist=frozenset()
                ),
            ),
            patch(f"{module}.project_tool_policy") as policy,
        ):
            for name in ("workbench_status", "iwe_console_status"):
                policy.return_value = ([name], True)
                self.assertEqual(
                    {"workbench_status", "iwe_console_status"}, api._load()[2]
                )

    async def test_status_and_client_decoding(self):
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=make_tool_app()),
            base_url="http://test",
        ) as client:
            with patch(
                (
                    "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.b"
                    "ackend_tool_api.report_failure"
                ),
                return_value=(None, None),
            ):
                for name, status, code in (
                    ("ok", 200, None),
                    ("invalid", 400, "tool_input_invalid"),
                    ("broken", 500, "internal"),
                    ("stale", 200, "tool_registry_stale"),
                    ("missing", 200, "tool_unavailable"),
                ):
                    with self.subTest(name=name):
                        response = await client.post("/", json=envelope(name))
                        self.assertEqual(response.status_code, status)
                        if code is None:
                            self.assertEqual(
                                response.json()["result"]["value"],
                                {"ok": True},
                            )
                            continue
                        fault = response.json()["error"]
                        self.assertEqual(fault["code"], code)
                        if code == "internal":
                            self.assertNotIn("secret detail", str(fault))
                        with self.assertRaises(SessionError) as caught:
                            ProjectToolSession._response(response)
                        self.assertEqual(caught.exception.code, code)
                        self.assertEqual(
                            caught.exception.tool_result, fault["tool_result"]
                        )
                response = await client.post("/", json={})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "value_error")
                response = await client.post("/", content="{")
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "value_error")
