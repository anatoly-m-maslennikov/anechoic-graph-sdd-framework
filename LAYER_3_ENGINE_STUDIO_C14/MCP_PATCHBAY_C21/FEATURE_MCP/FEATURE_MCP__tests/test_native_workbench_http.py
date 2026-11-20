"""The existing Workbench HTTP contract uses the native Project store."""

from dataclasses import replace
import unittest
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

import test_native_query_stdio as fixture
from native_query import create_native_gateway
from direct_gateway import startup_selection
from workbench_web import routes


class NativeWorkbenchHttpTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write

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
        self.assertTrue({'workspace_open', 'view_run', 'view_fetch'} <= {tool.name for tool in gateway.tools})
        self.assertIn('workbench_status', {tool.name for tool in gateway.tools})
        status = await gateway.call(None, types.CallToolRequestParams(name='workbench_status', arguments={}))
        self.assertFalse(status.is_error, status.structured_content)
        self.assertEqual({'mode': 'startup_snapshot'}, status.structured_content)
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
            self.assertEqual({'mode': 'startup_snapshot'}, status.json())
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
            self.assertEqual(400, unsupported.status_code)
            self.assertIsNone(gateway.workbench._service)
        self.assertEqual(before, {path: (source / path).read_bytes() for path in before})

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
