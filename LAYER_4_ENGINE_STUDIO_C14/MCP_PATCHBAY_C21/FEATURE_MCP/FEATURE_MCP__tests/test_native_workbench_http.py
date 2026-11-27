"""The existing Workbench HTTP contract uses the native Project store."""

import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path
import shlex
import unittest
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

from . import test_native_query_stdio as fixture
from .native_workbench_http_cases import NativeWorkbenchStateCases
from .native_query_test_support import create_native_gateway
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project as startup_selection,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    workbench_routes as routes,
)


class NativeWorkbenchHttpTests(NativeWorkbenchStateCases, unittest.IsolatedAsyncioTestCase):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write



    async def test_startup_rebinds_native_identity(self):
        manifest = self.root / fixture.CONTROL / fixture.MANIFEST
        manifest.write_text(manifest.read_text().replace("component: C0\n", "component: C00\n", 1))
        selection = await asyncio.to_thread(startup_selection, self.root)
        rebound = await asyncio.to_thread(startup_selection, self.root, instance_id=selection.instance_id,
                                          host_root=self.root)
        self.assertEqual(replace(selection, host_root=self.root), rebound)
        with self.assertRaises(ValueError):
            await asyncio.to_thread(startup_selection, self.root, host_root=self.root)
        with self.assertRaises(ValueError):
            await asyncio.to_thread(startup_selection, self.root, instance_id="0" * 64, host_root=self.root)







    async def test_manifest_change_blocks_lifecycle_until_gateway_restarts(self):
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        manifest = gateway.selection.manifest_path
        renamed = manifest.with_name(
            manifest.name.replace("--declare-", "--define-")
        )
        renamed.write_text(manifest.read_text().replace("version: 1", "version: 2", 1))
        manifest.unlink()

        async with asyncio.timeout(15):
            while True:
                query = await gateway.call(None, types.CallToolRequestParams(
                    name='query_run', arguments={'sql': 'SELECT 1', 'result_delivery': 'inline'},
                ))
                self.assertFalse(query.is_error, query.structured_content)
                if gateway._native_query._projection_selection.manifest_ref == 'AN-S-001@2':
                    break
                await asyncio.sleep(0.1)

        arguments = {'newAtom': {
            'template': 'task', 'label': 'Task', 'container': {'component': 'C00'},
            'body': '## Summary\n\nManifest reload regression.\n',
        }}
        source = self.root / fixture.CONTROL
        before = {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()}
        result = await gateway.call(None, types.CallToolRequestParams(
            name='atom_lifecycle_create_draft', arguments=arguments,
        ))
        self.assertEqual('blocked', result.structured_content['status'], result.structured_content)
        self.assertEqual('project_manifest_reload_required', result.structured_content['errors'][0]['code'])
        self.assertIn('restart', result.structured_content['errors'][0]['message'].lower())
        self.assertEqual(before, {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()})

        await gateway.close()
        fresh = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        await fresh.initialize()
        self.addAsyncCleanup(fresh.close)
        self.assertEqual('AN-S-001@2', fresh.selection.manifest_ref)
        result = await fresh.call(None, types.CallToolRequestParams(
            name='atom_lifecycle_create_draft', arguments=arguments,
        ))
        self.assertEqual('completed', result.structured_content['status'], result.structured_content)
        self.assertTrue(result.structured_content['savedDraft'])

    async def test_lifecycle_catalog_and_saved_references(self):
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        tools = {tool.name: tool for tool in gateway.tools}
        lifecycle = {
            name for name in tools if name.startswith("atom_lifecycle_")
        }
        self.assertEqual({
            'atom_lifecycle_archive', 'atom_lifecycle_change_status', 'atom_lifecycle_create_asset',
            'atom_lifecycle_create_draft', 'atom_lifecycle_direct_update',
            'atom_lifecycle_promote_draft', 'atom_lifecycle_update',
        }, lifecycle)
        self.assertEqual({'sourceCurrent', 'changes', 'newAtom'},
                         set(tools['atom_lifecycle_create_draft'].input_schema['properties']))

        async def call(name, arguments, status, field):
            response = await gateway.call(None, types.CallToolRequestParams(name=name, arguments=arguments))
            self.assertFalse(response.is_error, response.structured_content)
            value = response.structured_content
            self.assertEqual(status, value['status'], value)
            saved = value[field]
            self.assertTrue((self.root / saved['path']).is_file(), saved)
            self.assertTrue(Path(saved['path']).name.startswith(saved['ref_id'] + '-'), saved)
            return saved

        await call('atom_lifecycle_create_asset', {'newAtom': {
            'template': 'spec_proposal', 'body': '## Summary\n\nExample proposal.\n',
        }}, 'completed', 'artifact')
        draft = await call('atom_lifecycle_create_draft', {'newAtom': {
            'template': 'task', 'label': 'Task', 'container': {'component': 'C00'},
            'body': '## Summary\n\nLifecycle catalog check.\n',
        }}, 'completed', 'savedDraft')
        current = await call('atom_lifecycle_promote_draft', {
            'target': {'ref_id': draft['ref_id'], 'version': draft['version']}, 'targetStatus': 'backlog',
        }, 'completed', 'artifact')
        self.assertEqual(draft['atom_id'], current['ref_id'])
        revision = await call('atom_lifecycle_update', {
            'sourceCurrent': {'ref_id': current['ref_id'], 'version': current['version']},
            'changes': {'body': '## Summary\n\nLifecycle catalog check.\n\nRevised.\n'},
        }, 'draft_created', 'savedDraft')
        self.assertEqual(draft['atom_id'], revision['atom_id'])
        self.assertEqual(current['version'] + 1, revision['version'])
        self.assertEqual(f"{revision['atom_id']}@{revision['version']}-draft", revision['ref_id'])

    async def test_generated_lifecycle_catalog_is_public(self):
        mcp = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(mcp / 'docker'))
        self.addCleanup(sys.path.remove, str(mcp / 'docker'))
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import compile_tool_registry

        registry = json.loads(await asyncio.to_thread(
            compile_tool_registry, mcp.parents[2], timeout=60, max_output=2_000_000,
        ))
        provider = next(item for item in registry['providers'] if item['provider_id'] == 'lifecycle')
        self.assertEqual('tool_descriptors', provider['descriptor_factory'])
        expected = {
            'atom_lifecycle_archive', 'atom_lifecycle_change_status', 'atom_lifecycle_create_asset',
            'atom_lifecycle_create_draft', 'atom_lifecycle_direct_update',
            'atom_lifecycle_promote_draft', 'atom_lifecycle_update',
        }
        self.assertEqual(expected, {tool['name'] for tool in provider['tools']})
        self.assertTrue(expected <= set(registry['public_tools']))
        self.assertFalse(expected & set(registry['mcp_blacklist']))
        create = next(tool for tool in provider['tools'] if tool['name'] == 'atom_lifecycle_create_draft')
        self.assertEqual({'sourceCurrent', 'changes', 'newAtom'}, set(create['inputSchema']['properties']))

    async def test_rebuild_contract_over_mcp_and_http(self):
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        query = await gateway.call(None, types.CallToolRequestParams(
            name='query_run', arguments={'sql': 'SELECT reference FROM atoms ORDER BY reference',
                                         'result_delivery': 'inline'},
        ))
        self.assertFalse(query.is_error, query.structured_content)
        first = query.structured_content['query_id']
        result = await gateway.call(None, types.CallToolRequestParams(name='query_rebuild', arguments={'target': 'all'}))
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual(('ready', 'all'), (result.structured_content['status'], result.structured_content['target']))
        second = result.structured_content['result_ids'][first]
        self.assertNotEqual(first, second)
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            base_url="http://127.0.0.1",
        ) as client:
            http = await client.post(
                "/anechoic/Anechoic/api/rebuild", json={"target": "all"}
            )
            self.assertEqual(200, http.status_code, http.text)
            response = http.json()
            self.assertEqual(
                ("ready", "all"), (response["status"], response["target"])
            )
            self.assertNotEqual(second, response["result_ids"][second])
            invalid = await client.post(
                "/anechoic/Anechoic/api/rebuild", json={"target": ""}
            )
            self.assertEqual(400, invalid.status_code)

    def _release_claim(self, operation, *, status='active', entrypoint=None, atom_id=None, body=None):
        atom_id = atom_id or ('AN-P-058' if operation == 'local' else 'AN-P-049')
        entrypoint = entrypoint or f'release scripts/{operation}.py'
        if body is None:
            body = (f'## Claim\n\n### Formal Claim\n\n```python\n'
                    f'release_command(operation={operation!r}, entrypoint={entrypoint!r})\n```\n')
        self._write(f'__PROJECT_CONFIG/{atom_id}-WORKFLOW--{operation}.md', atom_id, status, 1,
                    template='workflow', body=body)
        script = self.root / entrypoint
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text('# fixture\n', encoding='utf-8')
        return self.root / fixture.CONTROL / f'__PROJECT_CONFIG/{atom_id}-WORKFLOW--{operation}.md'

    async def test_manifest_gates_release_commands(self):
        names = {'local_release_command', 'public_release_command'}
        for operation in ('local', 'public'):
            self._release_claim(operation)
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
                            name=name, arguments={'run_id': 'release-check-1', **(
                                {'content_draft': '/host/review draft.json'} if operation == 'public' else {})},
                        ))
                        self.assertEqual(not enabled, response.is_error, response.structured_content)
                        if enabled:
                            args = shlex.split(response.structured_content['command'])
                            self.assertEqual(['uv', 'run'], args[1:3])
                            script = str(host_root / f'release scripts/{operation}.py')
                            self.assertIn(script, args)
                            expected = [operation, '--project-root', str(host_root), '--run-id', 'release-check-1']
                            if operation == 'public':
                                expected += ['--content-draft', '/host/review draft.json']
                            self.assertEqual(expected, args[args.index(script) + 1:])
                            self.assertEqual(response.structured_content['command'], response.content[0].text)
                            self.assertEqual(str(host_root), response.structured_content['working_directory'])
                finally:
                    await gateway.close()

    async def test_release_claim_errors_and_recovery(self):
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        gateway.selection = gateway._native_query.selection = replace(
            gateway.selection,
            parameters={"project_mcp": {"release_workflows_enabled": True}},
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)

        async def call():
            return await gateway.call(None, types.CallToolRequestParams(
                name='local_release_command', arguments={'run_id': 'release-check-1'},
            ))

        self.assertTrue((await call()).is_error)
        path = self._release_claim('local', status='draft')
        self.assertTrue((await call()).is_error)
        self._release_claim('local')
        self.assertFalse((await call()).is_error)
        duplicate = self._release_claim('local', atom_id='AN-P-059')
        self.assertTrue((await call()).is_error)
        duplicate.unlink()
        self._release_claim('local', body='## Claim\n\n### Formal Claim\n\n```python\n'
                            'release_command(operation="local", entrypoint="../escape.py")\n```\n')
        self.assertTrue((await call()).is_error)
        self._release_claim('local')
        self.assertFalse((await call()).is_error)
        path.unlink()
        self.assertTrue((await call()).is_error)

    async def test_manifest_blacklist_applies_to_mcp_and_http(self):
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        selection = replace(gateway.selection, parameters={
            'project_mcp': {'tool_blacklist': ['query_schema', 'workbench_status']},
        })
        gateway.selection = gateway._native_query.selection = selection
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        self.assertNotIn('query_schema', {tool.name for tool in gateway.tools})
        self.assertNotIn(
            "workbench_status", {tool.name for tool in gateway.tools}
        )
        response = await gateway.call(None, types.CallToolRequestParams(name='query_schema', arguments={}))
        self.assertTrue(response.is_error)
        response = await gateway.call(None, types.CallToolRequestParams(name='workbench_status', arguments={}))
        self.assertTrue(response.is_error)
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(
                app=Starlette(routes=routes(gateway))
            ),
            base_url="http://127.0.0.1:18093",
        ) as client:
            response = await client.post(
                "/anechoic/Anechoic/api/schema", json={}
            )
            self.assertEqual(400, response.status_code)
            response = await client.post(
                "/anechoic/Anechoic/api/status", json={}
            )
            self.assertEqual(400, response.status_code)

        await gateway.close()
        invalid = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        invalid.selection = invalid._native_query.selection = replace(
            invalid.selection,
            parameters={"project_mcp": {"tool_blacklist": "query_schema"}},
        )
        with self.assertRaises(ValueError):
            await invalid.initialize()
        await invalid.close()


if __name__ == '__main__':
    unittest.main()
