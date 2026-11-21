"""The existing Workbench HTTP contract uses the native Project store."""

import asyncio
from dataclasses import replace
from itertools import product
from pathlib import Path
import shlex
import shutil
import unittest
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

import test_native_query_stdio as fixture
from native_query import NativeQueryOwner, create_native_gateway
from direct_gateway import startup_selection
from native_project_selection import resolve_native_project
from work_journal import PROJECT_DATABASE, append_sealed_events, journal_inbox
from workbench_web import routes


class NativeWorkbenchHttpTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write

    def test_independent_storage_modes_keep_journal_across_rebuild_and_restart(self):
        inputs = fixture._native_inputs()
        for journal, workbench in product(("files", "duckdb"), ("disk", "memory")):
            with self.subTest(journal=journal, workbench=workbench):
                root = self.root / f"{journal}-{workbench}"
                shutil.copytree(self.root / fixture.CONTROL, root / fixture.CONTROL)
                selected = resolve_native_project(root, fixture.CONTROL, validate_manifest=inputs.validate_manifest)
                selected = replace(selected, parameters={"runtime": {
                    "journal": {"storage": journal},
                    "workbench": {"storage": workbench, "import_graph": False},
                }})
                owner = NativeQueryOwner(selected, inputs)
                try:
                    owner.start()
                    append_sealed_events(root, [{"event": "test"}], author="test",
                                         local_date="2026-11-21", timezone="UTC",
                                         journal_root=(selected.control_relative / "_journal").as_posix(),
                                         storage=journal)
                    saved = owner.save_view("SELECT 1")["saved_query_id"]
                    if journal == "duckdb":
                        self.assertEqual([[2]], owner.run("SELECT count(*) FROM work_journal",
                                                          result_delivery="inline")["rows"])
                    owner.rebuild("all")
                    self.assertEqual("SELECT 1", owner.load(saved)["sql"])
                    self.assertEqual(workbench == "disk" or journal == "duckdb", (root / PROJECT_DATABASE).is_file())
                    self.assertEqual(journal == "files", (root / fixture.CONTROL / "_journal").is_dir())
                finally:
                    owner.close()
                owner = NativeQueryOwner(selected, inputs)
                try:
                    owner.start()
                    self.assertEqual("SELECT 1", owner.load(saved)["sql"])
                    if journal == "duckdb":
                        self.assertEqual([[2]], owner.run("SELECT count(*) FROM work_journal",
                                                          result_delivery="inline")["rows"])
                finally:
                    owner.close()
                if (journal, workbench) == ("duckdb", "disk"):
                    database = root / PROJECT_DATABASE
                    before = database.read_bytes()
                    switched = replace(selected, parameters={"runtime": {
                        "workbench": {"storage": "memory", "import_graph": False},
                    }})
                    owner = NativeQueryOwner(switched, inputs)
                    try:
                        owner.start()
                        self.assertEqual("SELECT 1", owner.load(saved)["sql"])
                        self.assertEqual([[2]], owner.run("SELECT count(*) FROM work_journal",
                                                          result_delivery="inline")["rows"])
                        owner.save_view("SELECT 2")
                        self.assertTrue((root / fixture.CONTROL / "_journal").is_dir())
                    finally:
                        owner.close()
                    self.assertEqual(before, database.read_bytes())
                    append_sealed_events(root, [{"event": "pending"}], author="test",
                                         local_date="2026-11-21", timezone="UTC",
                                         journal_root=(selected.control_relative / "_journal").as_posix(),
                                         storage=journal)
                    self.assertTrue(list(journal_inbox(root).glob("*.json")))
                    owner = NativeQueryOwner(switched, inputs)
                    try:
                        owner.start()
                        self.assertEqual([[3]], owner.run("SELECT count(*) FROM work_journal",
                                                          result_delivery="inline")["rows"])
                        self.assertFalse(list(journal_inbox(root).glob("*.json")))
                    finally:
                        owner.close()

    async def test_startup_rebinds_native_identity(self):
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        selection = gateway.selection
        with patch('native_startup.select_runtime_project', return_value=selection):
            self.assertEqual(selection, startup_selection(self.root))
            rebound = startup_selection(self.root, instance_id=selection.instance_id, host_root=self.root)
            self.assertEqual(self.root, rebound.host_root)
            with self.assertRaises(ValueError):
                startup_selection(self.root, host_root=self.root)
            with self.assertRaises(ValueError):
                startup_selection(self.root, instance_id='0' * 64, host_root=self.root)
        await gateway.close()

    async def test_workspace_view_and_bound_root(self):
        source = self.root / fixture.CONTROL
        before = {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()}
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        self.assertIn('module_imports', gateway._native_query.schema()['tables'])
        self.assertTrue({'workspace_open', 'view_run', 'view_fetch'} <= {tool.name for tool in gateway.tools})
        self.assertIn('workbench_status', {tool.name for tool in gateway.tools})
        status = await gateway.call(None, types.CallToolRequestParams(name='workbench_status', arguments={}))
        self.assertFalse(status.is_error, status.structured_content)
        self.assertEqual({'mode': 'live_index'}, status.structured_content)
        mcp_open = await gateway.call(None, types.CallToolRequestParams(
            name='workspace_open', arguments={'session_id': 'mcp-session'},
        ))
        self.assertFalse(mcp_open.is_error, mcp_open.structured_content)
        refused = await gateway.call(None, types.CallToolRequestParams(
            name='workspace_open', arguments={'session_id': 'mcp-session', 'project_root': '/wrong/project'},
        ))
        self.assertTrue(refused.is_error)
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url='http://127.0.0.1:18093') as client:
            path = '/anechoic/Anechoic/api'
            status = await client.post(f'{path}/status', json={})
            self.assertEqual(200, status.status_code, status.text)
            self.assertEqual({'mode': 'live_index'}, status.json())
            wrong_status_root = await client.post(f'{path}/status', json={'project_root': '/wrong/project'})
            self.assertEqual(400, wrong_status_root.status_code)

            async def call(operation, arguments, **envelope):
                return await client.post(f'{path}/interface', json={
                    'operation': operation, 'arguments': arguments, **envelope,
                })

            opened = await call('workspace_open', {'session_id': 'http-session'})
            self.assertEqual(200, opened.status_code, opened.text)
            workspace = opened.json()
            self.assertEqual('Anechoic', workspace['project_name'])
            self.assertIn('/anechoic/workbench/Anechoic?workspace=http-session', workspace['workspace_url'])
            identity = {'workspace_id': workspace['workspace_id'], 'view_id': workspace['active_view_id']}
            sql = "SELECT exact_ref FROM native_references WHERE exact_ref = 'AN-T-009@2'"
            updated = await call('view_update', identity | {'sql': sql, 'expected_revision': 0})
            self.assertEqual(200, updated.status_code, updated.text)
            checked = await call('view_check', identity)
            self.assertTrue(checked.json()['valid'], checked.text)
            result = await call('view_run', identity)
            self.assertEqual('success', result.json()['status'], result.text)
            fetched = await call('view_fetch', identity | {'result_delivery': 'inline'})
            self.assertEqual([['AN-T-009@2']], fetched.json()['rows'])
            saved = await call('view_save', identity)
            self.assertEqual(200, saved.status_code, saved.text)
            saved_url = saved.json()['saved_query_url']
            self.assertIn('/anechoic/workbench/Anechoic?query=', saved_url)
            loaded = await client.post(f'{path}/load', json={'reference': saved_url})
            self.assertEqual(sql, loaded.json()['sql'], loaded.text)
            listed = await client.post(f'{path}/saved-list', json={})
            self.assertEqual(saved.json()['saved_query_id'], listed.json()['items'][0]['saved_query_id'])
            wrong_root = await call('workspace_get', {'workspace_id': workspace['workspace_id']},
                                    project_root='/wrong/project')
            self.assertEqual(400, wrong_root.status_code)
            wrong_query = await client.post(f'{path}/schema', json={'project_root': '/wrong/project'})
            self.assertEqual(400, wrong_query.status_code)
            wrong_page = await client.get('/anechoic/workbench/Anechoic?project_root=/wrong/project')
            self.assertEqual(400, wrong_page.status_code)
            wrong_name = await client.post('/anechoic/wrong/api/interface', json={
                'operation': 'workspace_open', 'arguments': {'session_id': 'wrong'},
            })
            self.assertEqual(404, wrong_name.status_code)
            unsupported = await client.post(f'{path}/archive-load', json={'scopes': []})
            self.assertEqual(404, unsupported.status_code)
        self.assertEqual(before, {path: (source / path).read_bytes() for path in before})

    async def test_external_atom_changes_are_indexed_without_rebuild(self):
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        gateway.selection = gateway._native_query.selection = replace(
            gateway.selection, parameters={'runtime': {'workbench': {'import_graph': False}}},
        )
        with patch.dict('os.environ', {'ANECHOIC_RUNTIME_NAMESPACE': 'docker'}):
            await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        replace_projection = self.enterContext(patch.object(
            gateway._native_query._store, "replace", side_effect=AssertionError("Unexpected full rebuild"),
        ))

        async def wait_for(predicate):
            async with asyncio.timeout(15):
                while True:
                    result = await gateway.call(None, types.CallToolRequestParams(
                        name='query_run', arguments={
                            'sql': "SELECT relative_path, filename, exact_ref FROM native_references "
                                   "WHERE stable_ref = 'AN-T-010'",
                            'result_delivery': 'inline',
                        },
                    ))
                    self.assertFalse(result.is_error, result.structured_content)
                    rows = result.structured_content['rows']
                    if predicate(rows):
                        return rows
                    await asyncio.sleep(0.1)

        original = '__TKT/TASKS/new/nested/AN-T-010-TASK--watch.md'
        moved = '__TKT/TASKS/moved/AN-T-010-TASK--renamed.md'
        self._write(original, 'AN-T-010', 'active', 1, body='## Summary\n\nFirst content.\n')
        first = await wait_for(lambda rows: len(rows) == 1 and rows[0][2] == 'AN-T-010@1')
        self.assertTrue(first[0][0].endswith('__TKT/TASKS/new/nested'))

        self._write(original, 'AN-T-010', 'active', 1, body='## Summary\n\nChanged content.\n')
        await wait_for(lambda _: any(
            atom['id'] == 'AN-T-010' and b'Changed content.' in atom['_content_bytes']
            for atom in gateway._native_query._capture.atoms
        ))
        self._write(original, 'AN-T-010', 'active', 2, body='## Summary\n\nChanged content.\n')
        await wait_for(lambda rows: len(rows) == 1 and rows[0][2] == 'AN-T-010@2')

        source = self.root / fixture.CONTROL / original
        destination = self.root / fixture.CONTROL / moved
        destination.parent.mkdir(parents=True)
        source.rename(destination)
        await wait_for(lambda rows: len(rows) == 1 and rows[0][0].endswith('__TKT/TASKS/moved')
                       and rows[0][1] == destination.name and rows[0][2] == 'AN-T-010@2')
        destination.unlink()
        await wait_for(lambda rows: not rows)

        manifest = gateway.selection.manifest_path
        renamed = manifest.with_name(manifest.name.replace("--declare-", "--define-"))
        renamed.write_text(manifest.read_text().replace("version: 1", "version: 2", 1))
        manifest.unlink()
        self._write(original, 'AN-T-010', 'active', 1)
        await wait_for(lambda rows: bool(rows) and any(
            row['_exact_ref'] == 'AN-S-001@2' for row in gateway._native_query._capture.atoms
        ))
        self.assertEqual('AN-S-001@1', gateway.selection.manifest_ref)
        self.assertEqual('AN-S-001@2', gateway._native_query._projection_selection.manifest_ref)
        replace_projection.assert_not_called()

    async def test_rebuild_contract_over_mcp_and_http(self):
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        response = {'status': 'ready', 'target': 'all', 'result_ids': {'old': 'new'}}
        with patch.object(gateway._native_query, 'rebuild', return_value=response, create=True) as rebuild:
            result = await gateway.call(None, types.CallToolRequestParams(name='query_rebuild', arguments={'target': 'all'}))
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual(response, result.structured_content)
            app = Starlette(routes=routes(gateway))
            async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url='http://127.0.0.1') as client:
                http = await client.post('/anechoic/Anechoic/api/rebuild', json={'target': 'all'})
                self.assertEqual(200, http.status_code, http.text)
                self.assertEqual(response, http.json())
                invalid = await client.post('/anechoic/Anechoic/api/rebuild', json={'target': ''})
                self.assertEqual(400, invalid.status_code)
            self.assertEqual(2, rebuild.call_count)

    async def test_manifest_gates_release_commands(self):
        names = {'local_release_command', 'public_release_command'}
        for flag in ({}, {'release_workflows_enabled': False}, {'release_workflows_enabled': True}):
            with self.subTest(flag=flag):
                gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
                settings = {'project_mcp': flag}
                host_root = Path('/host/Anechoic checkout')
                gateway.selection = gateway._native_query.selection = replace(
                    gateway.selection, host_root=host_root, parameters=settings,
                )
                with patch.dict('os.environ', {'ANECHOIC_RUNTIME_NAMESPACE': 'docker'}):
                    await gateway.initialize()
                try:
                    enabled = flag.get('release_workflows_enabled') is True
                    advertised = {tool.name for tool in gateway.tools}
                    self.assertEqual(names if enabled else set(), advertised & names)
                    for name, operation in (('local_release_command', 'local'),
                                            ('public_release_command', 'public')):
                        response = await gateway.call(None, types.CallToolRequestParams(
                            name=name, arguments={'run_id': 'release-check-1'},
                        ))
                        self.assertEqual(not enabled, response.is_error, response.structured_content)
                        if enabled:
                            args = shlex.split(response.structured_content['command'])
                            self.assertEqual(['uv', 'run'], args[1:3])
                            self.assertEqual([operation, '--project-root', str(host_root), '--run-id',
                                              'release-check-1'], args[-5:])
                            self.assertEqual(str(host_root), response.structured_content['working_directory'])
                finally:
                    await gateway.close()

    async def test_manifest_blacklist_applies_to_mcp_and_http(self):
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        selection = replace(gateway.selection, parameters={
            'project_mcp': {'tool_blacklist': ['query_schema', 'workbench_status']},
        })
        gateway.selection = gateway._native_query.selection = selection
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        self.assertNotIn('query_schema', {tool.name for tool in gateway.tools})
        self.assertNotIn('workbench_status', {tool.name for tool in gateway.tools})
        response = await gateway.call(None, types.CallToolRequestParams(name='query_schema', arguments={}))
        self.assertTrue(response.is_error)
        response = await gateway.call(None, types.CallToolRequestParams(name='workbench_status', arguments={}))
        self.assertTrue(response.is_error)
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=Starlette(routes=routes(gateway))),
                                     base_url='http://127.0.0.1:18093') as client:
            response = await client.post('/anechoic/Anechoic/api/schema', json={})
            self.assertEqual(400, response.status_code)
            response = await client.post('/anechoic/Anechoic/api/status', json={})
            self.assertEqual(400, response.status_code)

        invalid = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        invalid.selection = invalid._native_query.selection = replace(
            invalid.selection, parameters={'project_mcp': {'tool_blacklist': 'query_schema'}},
        )
        with self.assertRaises(ValueError):
            await invalid.initialize()
        await invalid.close()


if __name__ == '__main__':
    unittest.main()
