"""Workbench web route test cases."""

from unittest.mock import patch

from starlette.applications import Starlette
from starlette.testclient import TestClient
from ..group_2.workbench_web_test_support import FakeGateway
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError

PROJECT_NAME = "anechoic"
IWE_CONSOLE_PATH = "/anechoic/iwe-console"
PROJECT_PATH = f"{IWE_CONSOLE_PATH}/{PROJECT_NAME}"
LEGACY_PROJECT_PATH = f"{WORKBENCH_PATH}/{PROJECT_NAME}"
API_PATH = f"/anechoic/{PROJECT_NAME}/api"


class WorkbenchCases:
    def test_project_named_assets_is_not_shadowed_by_static_files(self):
        gateway = FakeGateway()
        gateway.selection.project_name = "assets"
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            for prefix in (IWE_CONSOLE_PATH, WORKBENCH_PATH):
                self.assertEqual(
                    200, client.get(f"{prefix}/assets").status_code
                )
                self.assertEqual(
                    200,
                    client.post(
                        f"{prefix}/assets/check", json={"sql": "SELECT 1"}
                    ).status_code,
                )
                self.assertEqual(
                    200, client.get(f"{prefix}/assets/app.js").status_code
                )

    def test_project_api_and_legacy_routes_share_handlers_and_binding(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway, shared=True))
        examples = {
            "run": {"sql": "SELECT 1"},
            "check": {"sql": "SELECT 1"},
            "page": {"query_id": "query-1", "offset": 0},
            "schema": {},
            "status": {},
            "view-save": {"sql": "SELECT 1"},
            "load": {"reference": "q_" + "0" * 32},
            "saved-list": {},
            "interface": {
                "operation": "view_create",
                "arguments": {"workspace_id": "ws"},
            },
        }
        with TestClient(app) as client:
            for path, arguments in examples.items():
                body = {**arguments, "project_root": "/project"}
                canonical = client.post(f"{API_PATH}/{path}", json=body)
                self.assertEqual(200, canonical.status_code, path)
                for project_path in (PROJECT_PATH, LEGACY_PROJECT_PATH):
                    response = client.post(f"{project_path}/{path}", json=body)
                    self.assertEqual(canonical.json(), response.json(), path)
                    refused = client.post(
                        f"{project_path}/{path}",
                        json={**body, "project_root": "/invalid"},
                    )
                    self.assertEqual(400, refused.status_code)
                self.assertEqual(
                    404,
                    client.post(
                        f"/anechoic/other/api/{path}", json=body
                    ).status_code,
                )
                self.assertEqual(
                    400,
                    client.post(
                        f"{API_PATH}/{path}",
                        json={**body, "project_root": "/invalid"},
                    ).status_code,
                )

    def test_http_run_defaults_to_file_and_preserves_explicit_inline(self):
        gateway = FakeGateway()
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            self.assertEqual(
                200,
                client.post(
                    f"{API_PATH}/run", json={"sql": "SELECT 1"}
                ).status_code,
            )
            self.assertEqual(
                200,
                client.post(
                    f"{PROJECT_PATH}/run",
                    json={"sql": "SELECT 1", "result_delivery": "inline"},
                ).status_code,
            )
        self.assertEqual(
            "file", gateway.workbench.calls[-2][1]["result_delivery"]
        )
        self.assertEqual(
            "inline", gateway.workbench.calls[-1][1]["result_delivery"]
        )
        with TestClient(
            Starlette(routes=self.routes(gateway, shared=True))
        ) as client:
            self.assertEqual(
                200,
                client.post(
                    f"{API_PATH}/run",
                    json={"project_root": "/project", "sql": "SELECT 1"},
                ).status_code,
            )
        self.assertEqual(
            "file", gateway.workbench.calls[-1][1]["result_delivery"]
        )

    def test_backend_receives_public_url_and_original_root(self):
        gateway = FakeGateway()
        with TestClient(
            Starlette(routes=self.routes(gateway)),
            base_url="http://workbench.test",
        ) as client:
            response = client.post(
                f"{API_PATH}/check",
                json={
                    "sql": "SELECT 1",
                    "project_root": str(gateway.root),
                },
            )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [("http://workbench.test/", str(gateway.root))],
            gateway.workbench.contexts,
        )

    def test_diagnostic_failure_preserves_original_error(self):
        gateway = FakeGateway()
        with patch(
            "MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary.logger.warning",
            side_effect=RuntimeError("secret sink detail"),
        ):
            with TestClient(Starlette(routes=self.routes(gateway))) as client:
                response = client.post(f"{API_PATH}/run", json={"sql": "bad"})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {
                "error": "bad query",
                "diagnostic_error": "technical diagnostic emission failed",
            },
            response.json(),
        )
        self.assertNotIn("secret sink detail", response.text)

    def test_http_preserves_validated_tool_refusal(self):
        gateway = FakeGateway()
        fault = {
            "code": "query_error",
            "message": "query rejected",
            "tool_result": {
                "outcome": "rejected",
                "diagnostics": ["invalid SQL"],
            },
        }
        with patch.object(
            gateway,
            "call_tool",
            side_effect=ToolProtocolError.from_fault(fault),
        ):
            with TestClient(Starlette(routes=self.routes(gateway))) as client:
                for base in (API_PATH, PROJECT_PATH):
                    response = client.post(f"{base}/run", json={"sql": "bad"})
                    self.assertEqual(400, response.status_code)
                    self.assertEqual(
                        {
                            "error": "query rejected",
                            "code": "query_error",
                            "tool_result": fault["tool_result"],
                        },
                        response.json(),
                    )
