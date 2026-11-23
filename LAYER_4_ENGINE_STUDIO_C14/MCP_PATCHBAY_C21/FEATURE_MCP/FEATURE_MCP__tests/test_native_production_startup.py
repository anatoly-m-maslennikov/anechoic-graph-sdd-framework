"""Exercise native startup with an untouched legacy archive."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
import yaml

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"

from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import startup_selection  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import MCP_PATH, ProjectBinding  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import extension_directory  # noqa: E402
from . import test_native_startup as fixture  # noqa: E402


class NativeProductionStartupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        legacy = fixture.RuntimeSelectionTests.legacy(self, '.anechoic_legacy', declared='.anechoic_anechoic')
        fixture.RuntimeSelectionTests.manifest(self, self.root / '.anechoic_anechoic', component='C00')
        self.asset = self.root / '.anechoic_anechoic/__TKT/ASSETS/AN-T-009-ANALYSIS_REPORT--verify.md'
        self.asset.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-T-009'},
                  'context': {'container': {'component': 'C00'}, 'template': 'ANALYSIS_REPORT', 'tier': 0},
                  'state': {'version': 2, 'status': 'active', 'updated_at': '2026-11-19T00:00:00Z'}}
        self.asset.write_text(f'---\n{yaml.safe_dump(header)}---\n\n## Summary\n\nFixture.\n', encoding='utf-8')
        self._add_untyped_asset()
        self.old_path = '.anechoic_legacy/02_analysis_and_advisory/CA-P-9--old-asset.md'
        old = self.root / self.old_path
        old.parent.mkdir(parents=True)
        old.write_text('Retained legacy source.\n', encoding='utf-8')
        self.alias_path = self.root / '.anechoic_anechoic/_migration/native-aliases.json'
        self.alias_path.parent.mkdir(parents=True)
        self.alias_path.write_text(json.dumps([['CA-P-9@2', self.old_path, 'AN-T-009@2']]), encoding='utf-8')
        (self.root / 'native-aliases.json').write_text(self.alias_path.read_text(encoding='utf-8'), encoding='utf-8')
        self.legacy = legacy

    def _add_untyped_asset(self):
        self.untyped_asset = self.root / '.anechoic_anechoic/001_TICKETS/ASSETS/AN-T-010-ASSET--legacy.md'
        self.untyped_asset.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-T-010'}, 'context': {'container': {'component': 'C00'}},
                  'state': {'version': 1, 'status': 'active', 'updated_at': '2026-11-19T00:00:00Z'}}
        self.untyped_asset.write_text(f'---\n{yaml.safe_dump(header)}---\n\n## Summary\n\nFixture.\n', encoding='utf-8')

    def legacy_digests(self):
        return {p.relative_to(self.legacy): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.legacy.rglob('*') if p.is_file()}

    async def test_production_http_uses_native_model_without_alias_map(self):
        self.alias_path.unlink()
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        self.assertIsInstance(selection, ProjectBinding)
        self.assertEqual(('AN-S-001@1', self.root / '.anechoic_anechoic'),
                         (selection.manifest_ref, selection.control_root))
        cache = extension_directory(MCP.parents[2])

        with patch.dict(os.environ, {'ANECHOIC_RUNTIME_NAMESPACE': 'docker',
                                     'ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY': str(cache)}):
            app = create_app(self.root, selection=selection)
            async with app.starlette_app.router.lifespan_context(app.starlette_app):
                async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                               base_url='http://127.0.0.1:18093') as http:
                    async with streamable_http_client('http://127.0.0.1:18093' + MCP_PATH,
                                                      http_client=http) as streams, ClientSession(*streams) as client:
                        await client.initialize()
                        tools = {tool.name for tool in (await client.list_tools()).tools}
                        self.assertTrue({'query_run', 'atom_lifecycle_update', 'atom_lifecycle_direct_update'} <= tools)
                        schema = await client.call_tool('query_schema', {})
                        self.assertNotIn('native_legacy_references', schema.structured_content['tables'])
                        self.assertNotIn('native_migration_paths', schema.structured_content['tables'])
                        updated = await client.call_tool('atom_lifecycle_direct_update', {
                            'target': {'ref_id': 'AN-T-009', 'version': 2},
                            'changes': {'body': '## Summary\n\nFixture.\n\n## Work\n\nUpdated through MCP.\n'},
                        })
                        await self._update_untyped_asset(client)
                        self.assertFalse(updated.is_error, updated.structured_content)
                        self.assertEqual({'status': 'completed'}, updated.structured_content)
                        visible = await client.call_tool('query_run', {
                            'sql': "SELECT exact_ref FROM native_references WHERE stable_ref = 'AN-T-009'",
                            'result_delivery': 'inline',
                        })
                        self.assertFalse(visible.is_error, visible.structured_content)
                        self.assertEqual([['AN-T-009@2']], visible.structured_content['rows'])
                        self.assertIn('Updated through MCP.', self.asset.read_text(encoding='utf-8'))
        self.assertEqual(before, self.legacy_digests())

    async def _update_untyped_asset(self, client):
        before = self.untyped_asset.read_bytes().split(b'---\n', 2)[1]
        updated = await client.call_tool('atom_lifecycle_direct_update', {
            'target': {'ref_id': 'AN-T-010', 'version': 1},
            'changes': {'body': '## Summary\n\nFixture.\n\n## Work\n\nUpdated through MCP.\n'},
        })
        self.assertFalse(updated.is_error, updated.structured_content)
        self.assertEqual({'status': 'completed'}, updated.structured_content)
        self.assertEqual(before, self.untyped_asset.read_bytes().split(b'---\n', 2)[1])
        self.assertIn(b'Updated through MCP.', self.untyped_asset.read_bytes())

    def test_bad_migration_map_is_outside_startup_inputs(self):
        self.alias_path.write_text('{')
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        self.assertIsInstance(create_app(self.root, selection=selection).gateway.selection, ProjectBinding)
        self.assertEqual(before, self.legacy_digests())

    def test_http_entrypoint_uses_production_selection(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import main

        with patch('uvicorn.run') as run:
            self.assertIsNone(main(['--project-root', str(self.root)]))
        self.assertIsInstance(run.call_args.args[0].gateway.selection, ProjectBinding)


if __name__ == '__main__':
    unittest.main()
