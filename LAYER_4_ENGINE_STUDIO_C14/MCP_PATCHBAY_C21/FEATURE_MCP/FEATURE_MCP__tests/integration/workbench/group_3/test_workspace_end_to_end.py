"""Real MCP and HTTP boundary proof for Workspace Views."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from watchdog.observers.polling import PollingObserver


from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    MCP_PATH,
    WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    create_http_app as create_app,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared import (
    extension_directory,
)


from ....runtime.launch.group_1.test_native_startup import (
    RuntimeSelectionTests,
)
from ....runtime.launch.group_1.test_native_startup import (
    native_fixture_gateway,
)

from ..group_1._workspace_steps_a import WorkspaceStepsA
from ._workspace_steps_b import WorkspaceStepsB
from ..group_4._workspace_steps_c import WorkspaceStepsC


REPOSITORY = Path(__file__).resolve().parents[7]
PROGRAMMATIC = (
    REPOSITORY / "LAYER_4_ENGINE_STUDIO_C14" / "FEATURE_PROGRAMMATIC"
)
MCP = REPOSITORY / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP"
APP = REPOSITORY / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE"


class WorkspaceEndToEndTests(
    WorkspaceStepsA,
    WorkspaceStepsB,
    WorkspaceStepsC,
    unittest.IsolatedAsyncioTestCase,
):
    def setUp(self) -> None:
        observer = patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "source_watcher__pub.NativeObserver"
            ),
            PollingObserver,
        )
        observer.start()
        self.addCleanup(observer.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = (Path(self.temporary.name) / "project").resolve()
        self.root.mkdir()
        control = self.root / ".anechoic_fixture"
        RuntimeSelectionTests.manifest(
            self, control, name="fixture", component="C00"
        )
        spec = control / "AN-S-684-DES--fixture.md"
        spec.write_text(
            "---\natom_family: SPEC\natom_id: AN-S-684\n"
            "structure: {container: {component: C00}}\ncontext: {lens: DES}\n"
            "state: {status: active, version: 1, updated_at: '2026-11-21T00:00:00Z'}\n"
            "---\n## Summary\n\nFixture\n"
        )
        gateway = native_fixture_gateway(
            self.root, extension_directory(REPOSITORY)
        )
        self.app = create_app(self.root, runtime_gateway=gateway)
        self.interface = f"{WORKBENCH_PATH}/fixture/interface"

    @asynccontextmanager
    async def session(self):
        async with self.app.starlette_app.router.lifespan_context(
            self.app.starlette_app
        ):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=self.app),
                base_url="http://127.0.0.1:18093",
            ) as client:
                transport = streamable_http_client(
                    "http://127.0.0.1:18093" + MCP_PATH,
                    http_client=client,
                )
                streams = await transport.__aenter__()
                session = ClientSession(*streams)
                await session.__aenter__()
                try:
                    await session.initialize()
                    yield session, client
                finally:
                    await session.__aexit__(None, None, None)
                    await transport.__aexit__(None, None, None)

    async def tool(
        self, session: ClientSession, name: str, arguments: dict
    ) -> dict:
        response = await session.call_tool(name, arguments)
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content

    async def interface_call(
        self, client: httpx2.AsyncClient, operation: str, arguments: dict
    ):
        return await client.post(
            self.interface,
            json={"operation": operation, "arguments": arguments},
        )

    async def test_native_mcp_workspace_flow_matches_http_state(self) -> None:
        async with self.session() as (session, client):
            (
                created,
                first,
                opened,
                view,
            ) = await self._open_workspace_and_create_view(client, session)
            fetched = await self._run_and_fetch_view(opened, session, view)
            await self._check_workspace_state(
                client, created, fetched, first, opened, session
            )

    def _check_workspace_persistence(self):
        workspace_files = list(
            (self.root / ".anechoic_runtime/iwe_console/workspaces").glob(
                "*.json"
            )
        )
        self.assertEqual(1, len(workspace_files))
        self.assertNotIn(
            "project_name", workspace_files[0].read_text(encoding="utf-8")
        )

    async def test_view_duplicate_has_strict_mcp_http_parity_without_execution(
        self,
    ) -> None:
        async with self.session() as (session, client):
            source_id, workspace_id = await self._prepare_duplicate_workspace(
                session
            )
            (
                duplicate,
                duplicate_id,
                logs_before,
            ) = await self._duplicate_view_and_read_log(
                session, source_id, workspace_id
            )
            await self._check_duplicate_and_http(
                client,
                duplicate,
                duplicate_id,
                logs_before,
                session,
                source_id,
                workspace_id,
            )

    async def _check_duplicate_http_parity(
        self, session, client, workspace_id, source_id
    ):
        http_state = await self._check_http_duplicate(
            client, session, source_id, workspace_id
        )
        await self._check_invalid_duplicate(
            client, http_state, session, source_id, workspace_id
        )

    async def test_workspaces_are_isolated_and_guarded_by_ids_and_revisions(
        self,
    ) -> None:
        async with self.session() as (session, client):
            one_view, two_view = await self._prepare_isolated_workspaces(
                session
            )
            await self._check_workspace_guards(one_view, session, two_view)
            await self._check_workspace_http_error(client, session, two_view)

    async def test_runs_log_success_and_failure_and_saved_views_stay_loadable(
        self,
    ) -> None:
        async with self.session() as (session, _client):
            view = await self._save_successful_query(session)
            logs = await self._run_failure_and_read_logs(session, view)
            preview = await self._check_logs_and_preview(logs, session)
            await self._check_preview_not_saved(preview)

    async def test_view_run_preserves_workbench_unavailable_boundary(
        self,
    ) -> None:
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
            WorkbenchUnavailableError,
        )

        async with self.session() as (session, client):
            opened = await self.tool(
                session, "workspace_open", {"session_id": "invalid-settings"}
            )
            identity = {
                "workspace_id": opened["workspace_id"],
                "view_id": opened["active_view_id"],
            }
            await self.tool(
                session,
                "view_update",
                identity | {"sql": "SELECT 1", "expected_revision": 0},
            )
            with patch.object(
                self.app.gateway._native_query,
                "_run_store",
                side_effect=WorkbenchUnavailableError("unavailable"),
            ):
                failed = await session.call_tool("view_run", identity)
                self.assertTrue(failed.is_error)
                self.assertIn(
                    "workbench_unavailable", str(failed.structured_content)
                )
                response = await self.interface_call(
                    client, "view_run", identity
                )
                self.assertEqual(400, response.status_code)
                self.assertIn(
                    "Workbench unavailable", response.json()["error"]
                )

    async def test_grid_page_contract_matches_http_and_rejects_invalid_indices(
        self,
    ) -> None:
        async with self.session() as (session, client):
            args, grid, identity, native = await self._run_grid_query(session)
            response = await self._check_grid_results(
                args, client, grid, identity, native, session
            )
            await self._check_invalid_grid(
                args, client, identity, native, response, session
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
