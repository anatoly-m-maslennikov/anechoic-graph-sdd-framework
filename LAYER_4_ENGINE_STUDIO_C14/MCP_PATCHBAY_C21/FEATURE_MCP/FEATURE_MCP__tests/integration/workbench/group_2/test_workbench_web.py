from __future__ import annotations

from pathlib import Path
from functools import partial
import re
import tempfile
import unittest
import uuid

from starlette.applications import Starlette
from starlette.testclient import TestClient

from .workbench_web_test_support import FakeGateway
from ..group_3.workbench_web_cases import WorkbenchCases
from ..group_3.workbench_interface_cases import WorkbenchInterfaceCases

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


MCP_ROOT = Path(__file__).resolve().parents[4]
FRONTEND_ROOT = (
    MCP_ROOT.parents[1]
    / "IWE_CONSOLE_C43"
    / "APP_IWE_CONSOLE"
    / "FEATURE_IWE_CONSOLE_FRONTEND"
)


PROJECT_NAME = "anechoic"
IWE_CONSOLE_PATH = "/anechoic/iwe-console"
PROJECT_PATH = f"{IWE_CONSOLE_PATH}/{PROJECT_NAME}"
LEGACY_PROJECT_PATH = f"{WORKBENCH_PATH}/{PROJECT_NAME}"
API_PATH = f"/anechoic/{PROJECT_NAME}/api"


class WorkbenchWebTests(
    WorkbenchCases, WorkbenchInterfaceCases, unittest.TestCase
):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        frontend = Path(self._temporary.name)
        (frontend / "assets").mkdir()
        (frontend / "assets" / "app.js").write_text("// fixture")
        (frontend / "index.html").write_text(
            '<!doctype html><html><head></head><body><div id="app"></div>'
            f'<script src="{IWE_CONSOLE_PATH}/assets/app.js"></script>'
            "</body></html>"
        )
        self.routes = partial(routes, frontend=frontend)
        self.addCleanup(self._temporary.cleanup)

    def _check_paging(self, client):
        large = client.post(f"{PROJECT_PATH}/run", json={"sql": "large"})
        self.assertEqual("application/json", large.headers["content-type"])
        self.assertEqual(
            {
                "query_id": "query-1",
                "columns": [
                    {"name": "item", "type": "VARCHAR"},
                    {"name": "item", "type": "VARCHAR"},
                ],
                "rows": [
                    [f"λ-{index}", f"value-{index}"] for index in range(100)
                ],
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

    def check_project_routes(self, client):
        saved_id = "q_" + "0" * 32
        self.assertEqual(
            saved_id,
            client.post(
                f"{PROJECT_PATH}/load", json={"reference": saved_id}
            ).json()["saved_query_id"],
        )
        current_id = str(uuid.uuid7())
        self.assertEqual(
            current_id,
            client.post(
                f"{PROJECT_PATH}/load", json={"reference": current_id}
            ).json()["saved_query_id"],
        )
        self.assertEqual(
            {"error": "saved query reference must be an ID or absolute URL"},
            client.post(
                f"{PROJECT_PATH}/load",
                json={"reference": "?query=" + saved_id},
            ).json(),
        )
        self._check_paging(client)
        self.check_query_errors(client)

    def check_query_errors(self, client):
        for operation in ("run", "check"):
            failure = client.post(
                f"{PROJECT_PATH}/{operation}", json={"sql": "bad"}
            )
            self.assertEqual(400, failure.status_code)
            self.assertEqual({"error": "bad query"}, failure.json())
        failure = client.post(f"{PROJECT_PATH}/run", json={"sql": "crash"})
        self.assertEqual(400, failure.status_code)
        self.assertEqual({"error": "operation failure"}, failure.json())
        failure = client.post(f"{PROJECT_PATH}/check", json={"sql": 1})
        self.assertEqual({"error": "sql must be a string"}, failure.json())
        failure = client.post(
            f"{PROJECT_PATH}/page",
            json={"query_id": "query-1", "offset": -1},
        )
        self.assertEqual(
            {"error": "offset must be a non-negative integer"},
            failure.json(),
        )
        self.assertEqual(
            404,
            client.post(
                f"{WORKBENCH_PATH}/wrong/run", json={"sql": "SELECT 1"}
            ).status_code,
        )

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
            self.assertEqual(
                (200, page.text), (old_page.status_code, old_page.text)
            )
            self.assertEqual(
                1,
                client.post(
                    f"{PROJECT_PATH}/check", json={"sql": "SELECT 1"}
                ).json()["row_count"],
            )
            result = client.post(
                f"{PROJECT_PATH}/run", json={"sql": "SELECT 1"}
            )
            self.assertEqual(1, result.json()["row_count"])
            self.assertEqual(
                {"atoms": []},
                client.post(f"{PROJECT_PATH}/schema", json={}).json(),
            )
            self.check_project_routes(client)

    def test_missing_frontend_does_not_block_query_routes(self):
        missing = Path(self._temporary.name) / "missing"
        app = Starlette(routes=routes(FakeGateway(), frontend=missing))
        with TestClient(app) as client:
            response = client.get(PROJECT_PATH)
            self.assertEqual(503, response.status_code)
            self.assertEqual(
                {"error": "Workbench frontend is unavailable; build required"},
                response.json(),
            )
            self.assertEqual(
                1,
                client.post(
                    f"{PROJECT_PATH}/check", json={"sql": "SELECT 1"}
                ).json()["row_count"],
            )

    def test_standalone_codex_chat_route_is_disabled(self):
        with TestClient(
            Starlette(routes=self.routes(FakeGateway()))
        ) as client:
            self.assertEqual(
                404, client.get(f"{PROJECT_PATH}/codex").status_code
            )

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
                self.assertTrue(
                    asset.startswith(f"{IWE_CONSOLE_PATH}/assets/")
                )
                self.assertNotIn("/assets/assets/", asset)
                self.assertEqual(200, client.get(asset).status_code, asset)

    def check_shared_runs(self, client):
        named = client.post(
            f"{PROJECT_PATH}/run",
            json={
                "project_root": "/project",
                "sql": "SELECT 1",
                "save": True,
                "name": "shared",
            },
        ).json()
        self.assertEqual("shared", named["name"])
        partial = client.post(
            f"{PROJECT_PATH}/run",
            json={"project_root": "/project", "sql": "partial"},
        )
        self.assertEqual(200, partial.status_code)
        self.assertEqual("partial", partial.json()["outcome"])
        self.assertEqual("journal unavailable", partial.json()["save_error"])
        failure = client.post(
            f"{PROJECT_PATH}/run",
            json={"project_root": "/project", "sql": "bad"},
        )
        self.assertEqual(400, failure.status_code)
        self.assertEqual({"error": "bad query"}, failure.json())

    def test_shared_routes_require_and_forward_the_explicit_project_root(self):
        gateway = FakeGateway()
        app = Starlette(routes=self.routes(gateway, shared=True))
        with TestClient(app) as client:
            self.assertEqual(404, client.get(WORKBENCH_PATH).status_code)
            self.assertEqual(400, client.get(PROJECT_PATH).status_code)
            self.assertEqual(
                200,
                client.get(
                    f"{PROJECT_PATH}?project_root=/project"
                ).status_code,
            )
            self.assertEqual(
                404,
                client.get(
                    f"{WORKBENCH_PATH}/wrong?project_root=/project"
                ).status_code,
            )
            self.assertEqual(
                1,
                client.post(
                    f"{PROJECT_PATH}/run",
                    json={"project_root": "/project", "sql": "SELECT 1"},
                ).json()["row_count"],
            )
            self.check_shared_runs(client)
        self.assertEqual(
            ["/project", "/project", "/project", "/project"], gateway.roots
        )


if __name__ == "__main__":
    unittest.main()
