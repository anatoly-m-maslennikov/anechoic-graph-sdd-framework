"""Exercise migrated Project startup with the reviewed Model and alias map."""

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
APP_TESTS = MCP.parents[1] / 'IWE_CONSOLE_C43' / 'APP_WORKBENCH' / 'tests'
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(PROGRAMMATIC / 'FEATURE_TOOLS'), str(APP_TESTS.parent.parent), str(APP_TESTS)]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import query_store  # noqa: E402
from direct_gateway import startup_selection  # noqa: E402
from http_paths import MCP_PATH  # noqa: E402
from http_server import create_app  # noqa: E402
from native_project_selection import NativeProjectSelection  # noqa: E402
from project_selection import ProjectSelectionError  # noqa: E402
from smalltest_support import extension_directory  # noqa: E402
import test_native_startup as fixture  # noqa: E402


class NativeProductionStartupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        legacy = fixture.RuntimeSelectionTests.legacy(self, '.anechoic_legacy', declared='.anechoic_anechoic')
        fixture.RuntimeSelectionTests.manifest(self, self.root / '.anechoic_anechoic', component='C00')
        task = self.root / '.anechoic_anechoic/__TKT/TASKS/AN-T-009-TASK--verify.md'
        task.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-T-009'},
                  'context': {'container': {'component': 'C00'}, 'template': 'task', 'tier': 0},
                  'state': {'version': 2, 'status': 'active', 'updated_at': '2026-11-19T00:00:00Z'}}
        task.write_text(f'---\n{yaml.safe_dump(header)}---\n\n## Summary\n\nFixture.\n', encoding='utf-8')
        self.old_path = '.anechoic_legacy/03_plan/CA-P-9--old-task.md'
        old = self.root / self.old_path
        old.parent.mkdir(parents=True)
        old.write_text('Retained legacy source.\n', encoding='utf-8')
        self.alias_path = self.root / 'native-aliases.json'
        self.alias_path.write_text(json.dumps([['CA-P-9@2', self.old_path, 'AN-T-009@2']]), encoding='utf-8')
        self.legacy = legacy

    def legacy_digests(self):
        return {p.relative_to(self.legacy): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.legacy.rglob('*') if p.is_file()}

    async def test_production_http_queries_reviewed_model_and_alias(self):
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        self.assertIsInstance(selection, NativeProjectSelection)
        self.assertEqual(('AN-S-001@1', self.root / '.anechoic_anechoic'),
                         (selection.manifest_ref, selection.control_root))
        app = create_app(self.root, selection=selection)
        connect = query_store._connect
        cache = extension_directory(MCP.parents[2])

        def connect_with_cache(directory, database):
            self.assertIsNone(directory)
            return connect(cache, database)

        with patch.object(query_store, '_connect', side_effect=connect_with_cache):
            async with app.starlette_app.router.lifespan_context(app.starlette_app):
                async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                               base_url='http://127.0.0.1:18093') as http:
                    async with streamable_http_client('http://127.0.0.1:18093' + MCP_PATH,
                                                      http_client=http) as streams, ClientSession(*streams) as client:
                        await client.initialize()
                        self.assertIn('query_run', {tool.name for tool in (await client.list_tools()).tools})
                        result = await client.call_tool('query_run', {
                            'sql': 'SELECT legacy_ref, original_path, exact_ref FROM native_legacy_references',
                            'result_delivery': 'inline',
                        })
                        self.assertFalse(result.is_error, result.structured_content)
                        self.assertEqual([['CA-P-9@2', self.old_path, 'AN-T-009@2']],
                                         result.structured_content['rows'])
        self.assertEqual(before, self.legacy_digests())

    def test_missing_or_malformed_alias_map_refuses_startup(self):
        before = self.legacy_digests()
        selection = startup_selection(self.root)
        for contents in (None, '{', '{}', '[["CA-P-9@2", "path.md"]]', '[[1, "path.md", "AN-T-009@2"]]'):
            with self.subTest(contents=contents):
                if contents is None:
                    self.alias_path.unlink(missing_ok=True)
                else:
                    self.alias_path.write_text(contents, encoding='utf-8')
                with self.assertRaises(ProjectSelectionError):
                    create_app(self.root, selection=selection)
        self.assertEqual(before, self.legacy_digests())

    def test_http_entrypoint_uses_production_selection(self):
        from http_server import main

        with patch('uvicorn.run') as run:
            self.assertIsNone(main(['--project-root', str(self.root)]))
        self.assertIsInstance(run.call_args.args[0].gateway.selection, NativeProjectSelection)


if __name__ == '__main__':
    unittest.main()
