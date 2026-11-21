"""Exercise native startup with an untouched legacy archive."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
import yaml

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
APP_TESTS = MCP.parents[1] / 'IWE_CONSOLE_C43' / 'APP_WORKBENCH' / 'APP_WORKBENCH__tests'
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(PROGRAMMATIC / 'FEATURE_TOOLS'), str(APP_TESTS.parent.parent), str(APP_TESTS)]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import query_store  # noqa: E402
from direct_gateway import startup_selection  # noqa: E402
from http_paths import MCP_PATH  # noqa: E402
from http_server import create_app  # noqa: E402
from native_project_selection import NativeProjectSelection  # noqa: E402
from smalltest_support import extension_directory, polling_source_watcher  # noqa: E402
import test_native_startup as fixture  # noqa: E402


class NativeProductionStartupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.enterContext(polling_source_watcher())
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        legacy = fixture.RuntimeSelectionTests.legacy(self, '.anechoic_legacy', declared='.anechoic_anechoic')
        fixture.RuntimeSelectionTests.manifest(self, self.root / '.anechoic_anechoic', component='C00')
        asset = self.root / '.anechoic_anechoic/__TKT/ASSETS/AN-T-009-ANALYSIS_REPORT--verify.md'
        asset.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-T-009'},
                  'context': {'container': {'component': 'C00'}, 'template': 'ANALYSIS_REPORT', 'tier': 0},
                  'state': {'version': 2, 'status': 'active', 'updated_at': '2026-11-19T00:00:00Z'}}
        asset.write_text(f'---\n{yaml.safe_dump(header)}---\n\n## Summary\n\nFixture.\n', encoding='utf-8')
        self.old_path = '.anechoic_legacy/02_analysis_and_advisory/CA-P-9--old-asset.md'
        old = self.root / self.old_path
        old.parent.mkdir(parents=True)
        old.write_text('Retained legacy source.\n', encoding='utf-8')
        self.alias_path = self.root / '.anechoic_anechoic/_migration/native-aliases.json'
        self.alias_path.parent.mkdir(parents=True)
        self.alias_path.write_text(json.dumps([['CA-P-9@2', self.old_path, 'AN-T-009@2']]), encoding='utf-8')
        (self.root / 'native-aliases.json').write_text(self.alias_path.read_text(encoding='utf-8'), encoding='utf-8')
        self.legacy = legacy

    def legacy_digests(self):
        return {p.relative_to(self.legacy): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.legacy.rglob('*') if p.is_file()}

    async def test_production_http_uses_native_model_without_alias_map(self):
        self.alias_path.unlink()
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        self.assertIsInstance(selection, NativeProjectSelection)
        self.assertEqual(('AN-S-001@1', self.root / '.anechoic_anechoic'),
                         (selection.manifest_ref, selection.control_root))
        app = create_app(self.root, selection=selection)
        connect = query_store._connect
        cache = extension_directory(MCP.parents[2])

        def connect_with_cache(directory, database, journal_path, journal_disk):
            self.assertIsNone(directory)
            return connect(cache, database, journal_path, journal_disk)

        with patch.object(query_store, '_connect', side_effect=connect_with_cache):
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
                        self.assertFalse(updated.is_error, updated.structured_content)
                        self.assertEqual({'status': 'completed'}, updated.structured_content)
                        visible = await client.call_tool('query_run', {
                            'sql': "SELECT exact_ref FROM native_references WHERE stable_ref = 'AN-T-009'",
                            'result_delivery': 'inline',
                        })
                        self.assertFalse(visible.is_error, visible.structured_content)
                        self.assertEqual([['AN-T-009@2']], visible.structured_content['rows'])
                        capture = app.gateway._native_query._capture
                        ticket, = [row for row in capture.atoms if row['id'] == 'AN-T-009']
                        self.assertIn(b'Updated through MCP.', ticket['_content_bytes'])
        self.assertEqual(before, self.legacy_digests())

    def test_bad_migration_map_is_outside_startup_inputs(self):
        self.alias_path.write_text('{')
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        self.assertIsInstance(create_app(self.root, selection=selection).gateway.selection, NativeProjectSelection)
        self.assertEqual(before, self.legacy_digests())

    def test_http_entrypoint_uses_production_selection(self):
        from http_server import main

        with patch('uvicorn.run') as run:
            self.assertIsNone(main(['--project-root', str(self.root)]))
        self.assertIsInstance(run.call_args.args[0].gateway.selection, NativeProjectSelection)


if __name__ == '__main__':
    unittest.main()
