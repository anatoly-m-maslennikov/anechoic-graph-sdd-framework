"""Native Workbench storage, workspace and watcher test cases."""

import asyncio
from dataclasses import replace
from itertools import product
import shutil
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

from ...query.group_1 import test_native_query_stdio as fixture
from ..group_4 import _native_workbench_http_assertions as http_assertions
from ..group_4 import _native_workbench_watch_assertions as watch_assertions
from ....native_query_test_support import create_native_gateway
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.\
    PROJECT_SELECTION.PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.\
    project.project_database__pub import (
    PROJECT_DATABASE,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.\
    journal.work_journal__pub import (
    append_sealed_events,
    journal_inbox,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


class NativeWorkbenchStateCases:
    def _check_switched_storage(self, root, selected, inputs, saved, journal):
        database = root / PROJECT_DATABASE
        before = database.read_bytes()
        switched = replace(
            selected,
            parameters={
                "runtime": {
                    "workbench": {"storage": "memory", "import_graph": False},
                }
            },
        )
        owner = NativeQueryOwner(switched, inputs)
        try:
            owner.start()
            self.assertEqual("SELECT 1", owner.load(saved)["sql"])
            self.assertEqual(
                [[2]],
                owner.run(
                    "SELECT count(*) FROM work_journal",
                    result_delivery="inline",
                )["rows"],
            )
            owner.save_view("SELECT 2")
            self.assertTrue((root / fixture.CONTROL / "_journal").is_dir())
        finally:
            owner.close()
        self.assertEqual(before, database.read_bytes())
        self._check_switched_pending(root, selected, inputs, journal, switched)

    def _check_switched_pending(
        self, root, selected, inputs, journal, switched
    ):
        append_sealed_events(
            root,
            [{"event": "pending"}],
            author="test",
            local_date="2026-11-21",
            timezone="UTC",
            journal_root=(selected.control_relative / "_journal").as_posix(),
            storage=journal,
        )
        self.assertTrue(list(journal_inbox(root).glob("*.json")))
        owner = NativeQueryOwner(switched, inputs)
        try:
            owner.start()
            self.assertEqual(
                [[3]],
                owner.run(
                    "SELECT count(*) FROM work_journal",
                    result_delivery="inline",
                )["rows"],
            )
            self.assertFalse(list(journal_inbox(root).glob("*.json")))
        finally:
            owner.close()

    def test_independent_storage_modes_keep_journal_across_rebuild_and_restart(
        self,
    ):
        inputs = fixture._native_inputs()
        for journal, workbench in product(
            ("files", "duckdb"), ("disk", "memory")
        ):
            with self.subTest(journal=journal, workbench=workbench):
                self._check_storage_mode(inputs, journal, workbench)

    def _check_storage_mode(self, inputs, journal, workbench):
        root = self.root / f"{journal}-{workbench}"
        shutil.copytree(self.root / fixture.CONTROL, root / fixture.CONTROL)
        selected = resolve_native_project(
            root,
            fixture.CONTROL,
            validate_manifest=inputs.validate_manifest,
        )
        selected = replace(
            selected,
            parameters={
                "runtime": {
                    "journal": {"storage": journal},
                    "workbench": {
                        "storage": workbench,
                        "import_graph": False,
                    },
                }
            },
        )
        saved = self._prepare_storage_owner(
            root, selected, inputs, journal, workbench
        )
        owner = NativeQueryOwner(selected, inputs)
        try:
            owner.start()
            self.assertEqual("SELECT 1", owner.load(saved)["sql"])
            if journal == "duckdb":
                self.assertEqual(
                    [[2]],
                    owner.run(
                        "SELECT count(*) FROM work_journal",
                        result_delivery="inline",
                    )["rows"],
                )
        finally:
            owner.close()
        if (journal, workbench) == ("duckdb", "disk"):
            self._check_switched_storage(
                root, selected, inputs, saved, journal
            )

    def _prepare_storage_owner(
        self, root, selected, inputs, journal, workbench
    ):
        owner = NativeQueryOwner(selected, inputs)
        try:
            owner.start()
            append_sealed_events(
                root,
                [{"event": "test"}],
                author="test",
                local_date="2026-11-21",
                timezone="UTC",
                journal_root=(
                    selected.control_relative / "_journal"
                ).as_posix(),
                storage=journal,
            )
            saved = owner.save_view("SELECT 1")["saved_query_id"]
            if journal == "duckdb":
                self.assertEqual(
                    [[2]],
                    owner.run(
                        "SELECT count(*) FROM work_journal",
                        result_delivery="inline",
                    )["rows"],
                )
            owner.rebuild("all")
            self.assertEqual("SELECT 1", owner.load(saved)["sql"])
            self.assertEqual(
                workbench == "disk" or journal == "duckdb",
                (root / PROJECT_DATABASE).is_file(),
            )
            self.assertEqual(
                journal == "files",
                (root / fixture.CONTROL / "_journal").is_dir(),
            )
        finally:
            owner.close()
        return saved

    async def _check_workspace_refusals(self, client, call, path, workspace):
        wrong_root = await call(
            "workspace_get",
            {"workspace_id": workspace["workspace_id"]},
            project_root="/wrong/project",
        )
        self.assertEqual(400, wrong_root.status_code)
        wrong_query = await client.post(
            f"{path}/schema", json={"project_root": "/wrong/project"}
        )
        self.assertEqual(400, wrong_query.status_code)
        wrong_page = await client.get(
            "/anechoic/workbench/Anechoic?project_root=/wrong/project"
        )
        self.assertEqual(400, wrong_page.status_code)
        wrong_name = await client.post(
            "/anechoic/wrong/api/interface",
            json={
                "operation": "workspace_open",
                "arguments": {"session_id": "wrong"},
            },
        )
        self.assertEqual(404, wrong_name.status_code)
        unsupported = await client.post(
            f"{path}/archive-load", json={"scopes": []}
        )
        self.assertEqual(404, unsupported.status_code)

    async def _check_workspace_http(self, app):
        await http_assertions.check_workspace_http(self, app, httpx2)

    async def test_workspace_view_and_bound_root(self):
        source = self.root / fixture.CONTROL
        before = {
            p.relative_to(source): p.read_bytes()
            for p in source.rglob("*")
            if p.is_file()
        }
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        await self._check_workspace_tools(gateway)
        app = Starlette(routes=routes(gateway))
        await self._check_workspace_http(app)
        self.assertEqual(
            before, {path: (source / path).read_bytes() for path in before}
        )

    async def _check_workspace_tools(self, gateway):
        self.assertIn(
            "module_imports", gateway._native_query.schema()["tables"]
        )
        self.assertTrue(
            {"workspace_open", "view_run", "view_fetch"}
            <= {tool.name for tool in gateway.tools}
        )
        self.assertIn(
            "workbench_status", {tool.name for tool in gateway.tools}
        )
        status = await gateway.call(
            None,
            types.CallToolRequestParams(name="workbench_status", arguments={}),
        )
        self.assertFalse(status.is_error, status.structured_content)
        self.assertEqual({"mode": "live_index"}, status.structured_content)
        mcp_open = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="workspace_open",
                arguments={"session_id": "mcp-session"},
            ),
        )
        self.assertFalse(mcp_open.is_error, mcp_open.structured_content)
        refused = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="workspace_open",
                arguments={
                    "session_id": "mcp-session",
                    "project_root": "/wrong/project",
                },
            ),
        )
        self.assertTrue(refused.is_error)

    async def _wait_for_atom(self, gateway, predicate):
        async with asyncio.timeout(15):
            while True:
                result = await gateway.call(
                    None,
                    types.CallToolRequestParams(
                        name="query_run",
                        arguments={
                            "sql": "SELECT relative_path, filename, exact_ref "
                            "FROM native_references "
                            "WHERE stable_ref = 'AN-T-010'",
                            "result_delivery": "inline",
                        },
                    ),
                )
                self.assertFalse(result.is_error, result.structured_content)
                rows = result.structured_content["rows"]
                if predicate(rows):
                    return rows
                await asyncio.sleep(0.1)

    async def test_external_atom_changes_are_indexed_without_rebuild(self):
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        gateway.selection = gateway._native_query.selection = replace(
            gateway.selection,
            parameters={"runtime": {"workbench": {"import_graph": False}}},
        )
        with patch.dict(
            "os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}
        ):
            await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        replace_projection = self.enterContext(
            patch.object(
                gateway._native_query._store,
                "replace",
                side_effect=AssertionError("Unexpected full rebuild"),
            )
        )

        original = "__TKT/TASKS/new/nested/AN-T-010-TASK--watch.md"
        moved = "__TKT/TASKS/moved/AN-T-010-TASK--renamed.md"
        await watch_assertions.check_atom_changes(self, gateway, original)
        await watch_assertions.check_atom_move(
            self, gateway, original, moved, fixture.CONTROL
        )
        await watch_assertions.check_manifest_change(self, gateway, original)
        replace_projection.assert_not_called()
