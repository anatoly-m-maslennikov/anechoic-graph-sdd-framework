
from __future__ import annotations

from pathlib import Path
from functools import partial
import re
import tempfile
import unittest
import uuid
from unittest.mock import patch

from starlette.applications import Starlette
from starlette.testclient import TestClient

MCP_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = MCP_ROOT.parents[1] / "IWE_CONSOLE_C43" / "APP_IWE_CONSOLE" / "FEATURE_IWE_CONSOLE_FRONTEND"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import WORKBENCH_PATH  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import workbench_routes as routes  # noqa: E402


PROJECT_NAME = "anechoic"
IWE_CONSOLE_PATH = "/anechoic/iwe-console"
PROJECT_PATH = f"{IWE_CONSOLE_PATH}/{PROJECT_NAME}"
LEGACY_PROJECT_PATH = f"{WORKBENCH_PATH}/{PROJECT_NAME}"
API_PATH = f"/anechoic/{PROJECT_NAME}/api"

from .workbench_web_test_support import FakeGateway  # noqa: E402


class WorkbenchWebTests(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        frontend = Path(self._temporary.name)
        (frontend / "assets").mkdir()
        (frontend / "assets" / "app.js").write_text("// fixture")
        (frontend / "index.html").write_text(
            f'<div id="app"></div><script src="{IWE_CONSOLE_PATH}/assets/app.js"></script>'
        )
        self.routes = partial(routes, frontend=frontend)
        self.addCleanup(self._temporary.cleanup)

    def test_project_named_assets_is_not_shadowed_by_static_files(self):
        gateway = FakeGateway()
        gateway.selection.project_name = "assets"
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            for prefix in (IWE_CONSOLE_PATH, WORKBENCH_PATH):
                self.assertEqual(200, client.get(f"{prefix}/assets").status_code)
                self.assertEqual(200, client.post(f"{prefix}/assets/check", json={"sql": "SELECT 1"}).status_code)
                self.assertEqual(200, client.get(f"{prefix}/assets/app.js").status_code)

    def test_project_api_and_legacy_routes_share_handlers_and_binding(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway, shared=True))
        examples = {
            "run": {"sql": "SELECT 1"}, "check": {"sql": "SELECT 1"},
            "page": {"query_id": "query-1", "offset": 0}, "schema": {}, "status": {},
            "view-save": {"sql": "SELECT 1"}, "load": {"reference": "q_" + "0" * 32},
            "saved-list": {},
            "interface": {"operation": "view_create", "arguments": {"workspace_id": "ws"}},
        }
        with TestClient(app) as client:
            for path, arguments in examples.items():
                body = {**arguments, "project_root": "/project"}
                canonical = client.post(f"{API_PATH}/{path}", json=body)
                self.assertEqual(200, canonical.status_code, path)
                for project_path in (PROJECT_PATH, LEGACY_PROJECT_PATH):
                    response = client.post(f"{project_path}/{path}", json=body)
                    self.assertEqual(canonical.json(), response.json(), path)
                    refused = client.post(f"{project_path}/{path}", json={**body, "project_root": "/invalid"})
                    self.assertEqual(400, refused.status_code)
                self.assertEqual(404, client.post(f"/anechoic/other/api/{path}", json=body).status_code)
                self.assertEqual(400, client.post(f"{API_PATH}/{path}", json={**body, "project_root": "/invalid"}).status_code)

    def test_http_run_defaults_to_file_and_preserves_explicit_inline(self):
        gateway = FakeGateway()
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            self.assertEqual(200, client.post(f"{API_PATH}/run", json={"sql": "SELECT 1"}).status_code)
            self.assertEqual(200, client.post(f"{PROJECT_PATH}/run", json={
                "sql": "SELECT 1", "result_delivery": "inline"}).status_code)
        self.assertEqual("file", gateway.workbench.calls[-2][1]["result_delivery"])
        self.assertEqual("inline", gateway.workbench.calls[-1][1]["result_delivery"])
        with TestClient(Starlette(routes=self.routes(gateway, shared=True))) as client:
            self.assertEqual(200, client.post(f"{API_PATH}/run", json={"project_root": "/project", "sql": "SELECT 1"}).status_code)
        self.assertEqual("file", gateway.workbench.calls[-1][1]["result_delivery"])

    def test_backend_receives_public_url_and_original_root(self):
        gateway = FakeGateway()
        with TestClient(Starlette(routes=self.routes(gateway)), base_url="http://workbench.test") as client:
            response = client.post(f"{API_PATH}/check", json={
                "sql": "SELECT 1", "project_root": str(gateway.root),
            })
        self.assertEqual(200, response.status_code)
        self.assertEqual([("http://workbench.test/", str(gateway.root))], gateway.workbench.contexts)

    def test_diagnostic_failure_preserves_original_error(self):
        gateway = FakeGateway()
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary.logger.warning", side_effect=RuntimeError("secret sink detail")):
            with TestClient(Starlette(routes=self.routes(gateway))) as client:
                response = client.post(f"{API_PATH}/run", json={"sql": "bad"})
        self.assertEqual(400, response.status_code)
        self.assertEqual({"error": "bad query", "diagnostic_error": "technical diagnostic emission failed"}, response.json())
        self.assertNotIn("secret sink detail", response.text)

    def test_http_preserves_validated_tool_refusal(self):
        gateway = FakeGateway()
        fault = {"code": "query_error", "message": "query rejected", "tool_result": {
            "outcome": "rejected", "diagnostics": ["invalid SQL"],
        }}
        with patch.object(gateway, "call_tool", side_effect=ToolProtocolError.from_fault(fault)):
            with TestClient(Starlette(routes=self.routes(gateway))) as client:
                for base in (API_PATH, PROJECT_PATH):
                    response = client.post(f"{base}/run", json={"sql": "bad"})
                    self.assertEqual(400, response.status_code)
                    self.assertEqual({"error": "query rejected", "code": "query_error", "tool_result": fault["tool_result"]}, response.json())

    def _check_paging(self, client):
        large = client.post(f"{PROJECT_PATH}/run", json={"sql": "large"})
        self.assertEqual("application/json", large.headers["content-type"])
        self.assertEqual(
            {
                "query_id": "query-1",
                "columns": [{"name": "item", "type": "VARCHAR"}, {"name": "item", "type": "VARCHAR"}],
                "rows": [[f"λ-{index}", f"value-{index}"] for index in range(100)],
                "row_count": 1024,
                "column_count": 2,
                "offset": 0,
                "page_size": 100,
                "has_more": True,
            },
            large.json(),
        )
        paged = client.post(
            f"{PROJECT_PATH}/page",
            json={"query_id": "query-1", "offset": 100, "page_size": 20},
        )
        self.assertEqual(200, paged.status_code)
        self.assertEqual(100, paged.json()["offset"])
        self.assertEqual(20, paged.json()["page_size"])

    def test_page_and_project_bound_run_check_routes(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway))
        with TestClient(app) as client:
            self.assertEqual(404, client.get(WORKBENCH_PATH).status_code)
            page = client.get(PROJECT_PATH)
            self.assertEqual(200, page.status_code)
            self.assertIn('id="app"', page.text)
            self.assertIn(f"{IWE_CONSOLE_PATH}/assets/", page.text)
            old_page = client.get(f"{LEGACY_PROJECT_PATH}?workspace=session-1")
            self.assertEqual((200, page.text), (old_page.status_code, old_page.text))
            self.assertEqual(1, client.post(f"{PROJECT_PATH}/check", json={"sql": "SELECT 1"}).json()["row_count"])
            result = client.post(f"{PROJECT_PATH}/run", json={"sql": "SELECT 1"})
            self.assertEqual(1, result.json()["row_count"])
            self.assertEqual({"atoms": []}, client.post(f"{PROJECT_PATH}/schema", json={}).json())
            saved_id = "q_" + "0" * 32
            self.assertEqual(saved_id, client.post(f"{PROJECT_PATH}/load", json={"reference": saved_id}).json()["saved_query_id"])
            current_id = str(uuid.uuid7())
            self.assertEqual(current_id, client.post(f"{PROJECT_PATH}/load", json={"reference": current_id}).json()["saved_query_id"])
            self.assertEqual(
                {"error": "saved query reference must be an ID or absolute URL"},
                client.post(f"{PROJECT_PATH}/load", json={"reference": "?query=" + saved_id}).json(),
            )
            self._check_paging(client)
            for operation in ("run", "check"):
                failure = client.post(f"{PROJECT_PATH}/{operation}", json={"sql": "bad"})
                self.assertEqual(400, failure.status_code)
                self.assertEqual({"error": "bad query"}, failure.json())
            failure = client.post(f"{PROJECT_PATH}/run", json={"sql": "crash"})
            self.assertEqual(400, failure.status_code)
            self.assertEqual({"error": "operation failure"}, failure.json())
            failure = client.post(f"{PROJECT_PATH}/check", json={"sql": 1})
            self.assertEqual({"error": "sql must be a string"}, failure.json())
            failure = client.post(f"{PROJECT_PATH}/page", json={"query_id": "query-1", "offset": -1})
            self.assertEqual({"error": "offset must be a non-negative integer"}, failure.json())
            self.assertEqual(404, client.post(f"{WORKBENCH_PATH}/wrong/run", json={"sql": "SELECT 1"}).status_code)

    def test_missing_frontend_does_not_block_query_routes(self):
        missing = Path(self._temporary.name) / "missing"
        app = Starlette(routes=routes(FakeGateway(), frontend=missing))
        with TestClient(app) as client:
            response = client.get(PROJECT_PATH)
            self.assertEqual(503, response.status_code)
            self.assertEqual(
                {"error": "Workbench frontend is unavailable; build required"}, response.json()
            )
            self.assertEqual(
                1,
                client.post(f"{PROJECT_PATH}/check", json={"sql": "SELECT 1"}).json()["row_count"],
            )

    def test_standalone_codex_chat_route_is_disabled(self):
        with TestClient(Starlette(routes=self.routes(FakeGateway()))) as client:
            self.assertEqual(404, client.get(f"{PROJECT_PATH}/codex").status_code)

    def test_workspace_interface_uses_the_shared_native_operation_and_public_url(self):
        with TestClient(Starlette(routes=self.routes(FakeGateway())), base_url="http://workbench.test") as client:
            opened = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "workspace_open", "arguments": {"session_id": "session-1"},
            })
            self.assertEqual(200, opened.status_code)
            self.assertEqual(
                "http://workbench.test/anechoic/iwe-console/anechoic?workspace=session-1",
                opened.json()["workspace_url"],
            )
            self.assertEqual(PROJECT_NAME, opened.json()["project_name"])
            created = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "view_create", "arguments": {"workspace_id": "session-1"},
            })
            self.assertEqual("view-1", created.json()["view_id"])
            invalid = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "unknown", "arguments": {},
            })
            self.assertEqual(400, invalid.status_code)

    def test_interface_rejects_blacklisted_bound_view_save_and_validates_single_root(self):
        gateway = FakeGateway()
        gateway.tool_blacklist = frozenset({"view_save"})
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            blocked = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "view_save", "arguments": {"workspace_id": "session-1", "view_id": "view-1"},
            })
            self.assertEqual(400, blocked.status_code)
            self.assertEqual([], gateway.workbench.calls)

        gateway = FakeGateway()
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            wrong = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "workspace_open", "project_root": "/other",
                "arguments": {"session_id": "session-1"},
            })
            self.assertEqual(400, wrong.status_code)
            self.assertEqual([], gateway.workbench.calls)
            correct = client.post(f"{PROJECT_PATH}/interface", json={
                "operation": "workspace_open", "project_root": str(gateway.root),
                "arguments": {"session_id": "session-1"},
            })
            self.assertEqual(200, correct.status_code)
            self.assertEqual([("workspace_open", {"session_id": "session-1"})], gateway.workbench.calls)

    def test_run_and_save_values_have_request_derived_urls_and_query_errors_do_not(self):
        with TestClient(Starlette(routes=self.routes(FakeGateway())), base_url="http://workbench.test") as client:
            self.assertEqual(404, client.post(f"{PROJECT_PATH}/save", json={"sql": "SELECT 1"}).status_code)
            self.assertEqual(404, client.post(f"{PROJECT_PATH}/worksheet-save", json={"sql": "SELECT 1"}).status_code)
            view = client.post(f"{PROJECT_PATH}/view-save", json={"sql": "SELECT 1", "name": "view"}).json()
            self.assertEqual("view", view["kind"])
            self.assertEqual("view", view["name"])
            saved = client.post(f"{PROJECT_PATH}/run", json={"sql": "SELECT 1", "save": True}).json()
            self.assertEqual(
                "http://workbench.test/anechoic/iwe-console/anechoic?query=q_1", saved["saved_query_url"],
            )
            named = client.post(f"{PROJECT_PATH}/run", json={"sql": "SELECT 1", "save": True, "name": "named"}).json()
            self.assertEqual("named", named["name"])
            unnamed = client.post(f"{PROJECT_PATH}/run", json={"sql": "SELECT 1", "save": True, "name": "   "}).json()
            self.assertNotIn("name", unnamed)
            failed = client.post(f"{PROJECT_PATH}/run", json={"sql": "bad"})
            self.assertEqual(400, failed.status_code)
            self.assertEqual({"error": "bad query"}, failed.json())

    def test_built_assets_follow_the_workbench_route_when_available(self):
        frontend = FRONTEND_ROOT / "dist"
        index = frontend / "index.html"
        if not index.is_file():
            self.skipTest("frontend build is not present")
        app = Starlette(routes=routes(FakeGateway()))
        with TestClient(app) as client:
            self.assertEqual(200, client.get(PROJECT_PATH).status_code)
            assets = re.findall(r'(?:src|href)="([^"?#]+)', index.read_text())
            self.assertTrue(assets)
            for asset in assets:
                self.assertTrue(asset.startswith(f"{IWE_CONSOLE_PATH}/assets/"))
                self.assertNotIn("/assets/assets/", asset)
                self.assertEqual(200, client.get(asset).status_code, asset)

    def test_shared_routes_require_and_forward_the_explicit_project_root(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway, shared=True))
        with TestClient(app) as client:
            self.assertEqual(404, client.get(WORKBENCH_PATH).status_code)
            self.assertEqual(400, client.get(PROJECT_PATH).status_code)
            self.assertEqual(200, client.get(f"{PROJECT_PATH}?project_root=/project").status_code)
            self.assertEqual(404, client.get(f"{WORKBENCH_PATH}/wrong?project_root=/project").status_code)
            self.assertEqual(1, client.post(f"{PROJECT_PATH}/run", json={"project_root": "/project", "sql": "SELECT 1"}).json()["row_count"])
            named = client.post(f"{PROJECT_PATH}/run", json={"project_root": "/project", "sql": "SELECT 1", "save": True, "name": "shared"}).json()
            self.assertEqual("shared", named["name"])
            partial = client.post(f"{PROJECT_PATH}/run", json={"project_root": "/project", "sql": "partial"})
            self.assertEqual(200, partial.status_code)
            self.assertEqual("partial", partial.json()["outcome"])
            self.assertEqual("journal unavailable", partial.json()["save_error"])
            failure = client.post(f"{PROJECT_PATH}/run", json={"project_root": "/project", "sql": "bad"})
            self.assertEqual(400, failure.status_code)
            self.assertEqual({"error": "bad query"}, failure.json())
        self.assertEqual(["/project", "/project", "/project", "/project"], gateway.roots)


if __name__ == "__main__":
    unittest.main()
