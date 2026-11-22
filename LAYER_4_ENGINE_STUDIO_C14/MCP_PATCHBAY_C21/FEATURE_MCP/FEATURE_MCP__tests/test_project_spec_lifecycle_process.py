"""Project SPEC lifecycle against the real MCP Backend and active Model."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mcp import types
import yaml

from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import native_runtime_gateway
from .FEATURE_MCP__tests__shared import CONTROL, ROOT, project

BODY = '\n## Summary\n\nExample\n\n## Guarantee\n\nThe output is available.\n'


class ProjectSpecLifecycleProcessTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.enterContext(patch.dict(os.environ, {'ANECHOIC_RUNTIME_NAMESPACE': 'docker',
            'ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY': str(ROOT / '.anechoic_tmp/workbench/extensions')}))
        self.gateway = self.enterContext(native_runtime_gateway(project(self.root)))
        await self.gateway.initialize()
        self.addAsyncCleanup(self.gateway.close)

    async def call(self, name, arguments, expected='completed'):
        response = await self.gateway.call(None, types.CallToolRequestParams(
            name='atom_lifecycle_' + name, arguments=arguments))
        value = response.structured_content
        self.assertEqual(expected, value['status'], value)
        return value

    async def draft(self, template, **extra):
        values = {'template': template, 'container': {'component': 'C00'}, 'lens': 'SPEC',
                  'body': '\n## Summary\n\nExample\n', **extra}
        return await self.call('create_draft', {'newAtom': values})

    async def reject(self, template, **extra):
        values = {'template': template, 'container': {'component': 'C00'}, 'lens': 'SPEC',
                  'body': '\n## Summary\n\nExample\n', **extra}
        result = await self.gateway.call(None, types.CallToolRequestParams(
            name='atom_lifecycle_create_draft', arguments={'newAtom': values}))
        self.assertNotEqual('completed', result.structured_content['status'], result.structured_content)

    async def test_axiom_zero_and_negative_tier(self):
        await self.reject('axiom', tier=-1)
        draft = (await self.draft('axiom'))['savedDraft']
        target = {'ref_id': draft['ref_id'], 'version': 1}
        ready = (await self.call('promote_draft', {'target': target, 'targetStatus': 'ready'}))['artifact']
        active = (await self.call('change_status', {'target': {'ref_id': ready['ref_id'], 'version': 1},
                                                   'targetStatus': 'active'}))['artifact']
        path = self.root / active['path']
        self.assertEqual(0, yaml.safe_load(path.read_text().split('---', 2)[1])['tier'])
        self.assertEqual(self.root / CONTROL, path.parent)

    async def test_applicable_principle_tiers(self):
        for tier in (1, 2):
            with self.subTest(tier=tier):
                draft = (await self.draft('applicable_principle', tier=tier))['savedDraft']
                header = yaml.safe_load((self.root / draft['path']).read_text().split('---', 2)[1])
                self.assertEqual(tier, header['tier'])
        for tier in (0, 3):
            with self.subTest(tier=tier):
                await self.reject('applicable_principle', tier=tier)

    async def test_project_contract_guarantee(self):
        for body in ('\n## Summary\n\nExample\n', BODY.replace('The output is available.', '   '),
                     BODY + '\n## Guarantee\n\nDuplicate\n'):
            with self.subTest(body=body):
                await self.reject('project_contract', body=body)
        await self.reject('project_contract', body=BODY, tier=1)
        await self.reject('project_contract', body=BODY, container={'component': 'C9'})
        draft = (await self.draft('project_contract', body=BODY))['savedDraft']
        target = {'ref_id': draft['ref_id'], 'version': 1}
        await self.check_invalid_then_restore(draft, 'promote_draft', target, 'ready')
        ready = (await self.call('promote_draft', {'target': target, 'targetStatus': 'ready'}))['artifact']
        target = {'ref_id': ready['ref_id'], 'version': 1}
        await self.check_invalid_then_restore(ready, 'change_status', target, 'active')
        result = await self.call('change_status', {'target': target, 'targetStatus': 'active'})
        self.assertEqual('active', result['artifact']['status'])

    async def check_invalid_then_restore(self, artifact, operation, target, status):
        path = self.root / artifact['path']
        original = path.read_text()
        path.write_text(original.replace('The output is available.', ' '))
        result = await self.gateway.call(None, types.CallToolRequestParams(
            name='atom_lifecycle_' + operation, arguments={'target': target, 'targetStatus': status}))
        self.assertNotEqual('completed', result.structured_content['status'], result.structured_content)
        path.write_text(original)
