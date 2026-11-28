"""Workbench web route test cases."""

from starlette.applications import Starlette
from starlette.testclient import TestClient
from ..group_2.workbench_web_test_support import FakeGateway
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    WORKBENCH_PATH,
)

PROJECT_NAME = "anechoic"
IWE_CONSOLE_PATH = "/anechoic/iwe-console"
PROJECT_PATH = f"{IWE_CONSOLE_PATH}/{PROJECT_NAME}"
LEGACY_PROJECT_PATH = f"{WORKBENCH_PATH}/{PROJECT_NAME}"
API_PATH = f"/anechoic/{PROJECT_NAME}/api"


class WorkbenchInterfaceCases:
    def test_legacy_interface_dispatches_only_an_admitted_request(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway, shared=True))
        path = f"{LEGACY_PROJECT_PATH}/interface"
        operation = "query_check"
        arguments = {"sql": "SELECT 1"}
        body = {"operation": operation, "arguments": arguments}
        with TestClient(app) as client:
            denied = client.post(path, json={**body, "project_root": "/other"})
            self.assertEqual(400, denied.status_code)
            self.assertEqual([], gateway.workbench.calls)
            admitted = client.post(
                path, json={**body, "project_root": "/project"}
            )
            self.assertEqual(200, admitted.status_code)
            self.assertEqual([(operation, arguments)], gateway.workbench.calls)

    def _case_1(
        self,
    ):
        with TestClient(
            Starlette(routes=self.routes(FakeGateway())),
            base_url="http://workbench.test",
        ) as client:
            opened = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "workspace_open",
                    "arguments": {"session_id": "session-1"},
                },
            )
            self.assertEqual(200, opened.status_code)
            self.assertEqual(
                "http://workbench.test/anechoic/iwe-console/anechoic"
                "?workspace=session-1",
                opened.json()["workspace_url"],
            )
            self.assertEqual(PROJECT_NAME, opened.json()["project_name"])
            created = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "view_create",
                    "arguments": {"workspace_id": "session-1"},
                },
            )
            self.assertEqual("view-1", created.json()["view_id"])
            invalid = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "unknown",
                    "arguments": {},
                },
            )
            self.assertEqual(400, invalid.status_code)
            self.assertEqual("tool_unavailable", invalid.json()["code"])

    def _case_2(
        self,
    ):
        gateway = FakeGateway()
        gateway.tool_blacklist = frozenset({"view_save"})
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            blocked = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "view_save",
                    "arguments": {
                        "workspace_id": "session-1",
                        "view_id": "view-1",
                    },
                },
            )
            self.assertEqual(400, blocked.status_code)
            self.assertEqual("tool_unavailable", blocked.json()["code"])
            self.assertEqual([], gateway.workbench.calls)

        gateway = FakeGateway()
        with TestClient(Starlette(routes=self.routes(gateway))) as client:
            wrong = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "workspace_open",
                    "project_root": "/other",
                    "arguments": {"session_id": "session-1"},
                },
            )
            self.assertEqual(400, wrong.status_code)
            self.assertEqual([], gateway.workbench.calls)
            correct = client.post(
                f"{PROJECT_PATH}/interface",
                json={
                    "operation": "workspace_open",
                    "project_root": str(gateway.root),
                    "arguments": {"session_id": "session-1"},
                },
            )
            self.assertEqual(200, correct.status_code)
            self.assertEqual(
                [("workspace_open", {"session_id": "session-1"})],
                gateway.workbench.calls,
            )

    def test_generic_interface_requires_same_origin_and_bounded_json(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway))
        path = f"{PROJECT_PATH}/interface"
        with TestClient(app, base_url="http://localhost:8092") as client:
            denied = client.post(
                path, json={}, headers={"Origin": "http://localhost:8093"}
            )
            self.assertEqual(403, denied.status_code)
            body = '{"operation":"query_check","arguments":{"sql":"SELECT 1"}}'
            denied = client.post(
                path, content=body, headers={"Content-Type": "text/plain"}
            )
            self.assertEqual(400, denied.status_code)
            refused = client.post(
                path,
                content=body.ljust(65_537),
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(400, refused.status_code)
            self.assertEqual([], gateway.workbench.calls)
            allowed = client.post(
                path,
                content=body,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Origin": "http://localhost:8092",
                },
            )
            self.assertEqual(200, allowed.status_code)
            self.assertEqual(
                [("query_check", {"sql": "SELECT 1"})], gateway.workbench.calls
            )

    def _case_3(self):
        with TestClient(
            Starlette(routes=self.routes(FakeGateway())),
            base_url="http://workbench.test",
        ) as client:
            self.assertEqual(
                404,
                client.post(
                    f"{PROJECT_PATH}/save", json={"sql": "SELECT 1"}
                ).status_code,
            )
            self.assertEqual(
                404,
                client.post(
                    f"{PROJECT_PATH}/worksheet-save", json={"sql": "SELECT 1"}
                ).status_code,
            )
            view = client.post(
                f"{PROJECT_PATH}/view-save",
                json={"sql": "SELECT 1", "name": "view"},
            ).json()
            self.assertEqual("view", view["kind"])
            self.assertEqual("view", view["name"])
            saved = client.post(
                f"{PROJECT_PATH}/run", json={"sql": "SELECT 1", "save": True}
            ).json()
            self.assertEqual(
                "http://workbench.test/anechoic/iwe-console/anechoic"
                "?query=q_1",
                saved["saved_query_url"],
            )
            named = client.post(
                f"{PROJECT_PATH}/run",
                json={"sql": "SELECT 1", "save": True, "name": "named"},
            ).json()
            self.assertEqual("named", named["name"])
            unnamed = client.post(
                f"{PROJECT_PATH}/run",
                json={"sql": "SELECT 1", "save": True, "name": "   "},
            ).json()
            self.assertNotIn("name", unnamed)
            failed = client.post(f"{PROJECT_PATH}/run", json={"sql": "bad"})
            self.assertEqual(400, failed.status_code)
            self.assertEqual({"error": "bad query"}, failed.json())


setattr(
    WorkbenchInterfaceCases,
    "test_workspace_interface_uses_the_shared_native_operation_and_public_url",
    WorkbenchInterfaceCases._case_1,
)

setattr(
    WorkbenchInterfaceCases,
    "test_interface_rejects_blacklisted_bound_view_"
    "save_and_validates_single_root",
    WorkbenchInterfaceCases._case_2,
)

setattr(
    WorkbenchInterfaceCases,
    "test_run_and_save_values_have_request_derived_"
    "urls_and_query_errors_do_not",
    WorkbenchInterfaceCases._case_3,
)
