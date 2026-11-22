"""Check native state findings publication and rebuild dependencies."""

from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import patch

import duckdb

from KERNEL_MIXER_C59 import boundary_tables
from KERNEL_MIXER_C59.native_query_rebuild import NativeQueryRebuild
from KERNEL_MIXER_C59.query_schema import public_schema


class StateProjectionTests(TestCase):
    def test_publication_rebuild_rollback_and_removal(self):
        connection = duckdb.connect(':memory:')
        self.addCleanup(connection.close)
        row = ('module:src/a.py', 'src/a.py', 'python', '<module>', 1, None,
               'unresolved', False, '[]', '[]', 'Lean unavailable')
        connection.execute('BEGIN')
        boundary_tables.replace_boundaries(connection, ([], [], [row]))
        connection.execute('COMMIT')
        self.assertEqual([row], connection.execute('SELECT * FROM state_effect_findings').fetchall())
        schema = public_schema(connection, SimpleNamespace(status_names=[]))
        self.assertIn('state_effect_findings', schema['tables'])

        rebuild = NativeQueryRebuild()
        rebuild._realization_options = ()
        store = SimpleNamespace(_projection=SimpleNamespace(graph=SimpleNamespace(tables={})))
        table, scope, dependencies = rebuild._rebuild_scope(store, 'state_effect_findings')
        self.assertEqual((table, scope), ('state_effect_findings', 'realization'))
        self.assertIn('state_effect_findings', dependencies)

        connection.execute('BEGIN')
        boundary_tables.replace_boundaries(connection, ([], [], []))
        connection.execute('ROLLBACK')
        self.assertEqual([row], connection.execute('SELECT * FROM state_effect_findings').fetchall())
        boundary_tables.remove_boundaries(connection)
        self.assertNotIn('state_effect_findings', public_schema(connection, SimpleNamespace(status_names=[]))['tables'])

    def test_analysis_receives_same_ownership_as_access_check(self):
        selection = SimpleNamespace(root='root', control_root='control')
        snapshot = SimpleNamespace(components={}, packages={})
        sources, ownership, expected = {'a.py': object()}, object(), [('finding',)]
        with (patch.object(boundary_tables, 'code_access_occurrences', return_value=(set(), [])),
              patch.object(boundary_tables, 'build_code_access_ownership', return_value=ownership) as build,
              patch.object(boundary_tables, 'check_code_access', return_value=[]) as check,
              patch.object(boundary_tables, 'analyze_state', return_value=expected) as analyze):
            result = boundary_tables.prepare_boundaries(selection, snapshot, sources, [], None, {})
        self.assertEqual(([], [], expected), result)
        build.assert_called_once()
        check.assert_called_once_with(ownership, sources, [])
        analyze.assert_called_once_with('root', sources, ownership=ownership)

    def test_analysis_runs_without_structure(self):
        selection = SimpleNamespace(root='root')
        sources = {'a.py': object()}
        with patch.object(boundary_tables, 'analyze_state', return_value=[]) as analyze:
            self.assertEqual(([], [], []), boundary_tables.prepare_boundaries(selection, None, sources, [], None, {}))
        analyze.assert_called_once_with('root', sources, ownership=None)


class StateProjectionWatcherTests(IsolatedAsyncioTestCase):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.test_native_import_graph import NativeImportGraphTests as Fixture

    _write = Fixture._write
    _source = Fixture._source
    _gateway = Fixture._gateway
    setUp = Fixture.setUp
    del Fixture

    async def test_unavailable_lean_is_published(self):
        from mcp import types

        self._source('src/a.py', 'x = 1\n')
        with patch('IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.state_effects__shared.shutil.which',
                   return_value=None):
            gateway = await self._gateway()
            result = await gateway.call(None, types.CallToolRequestParams(name='query_run', arguments={
                'sql': "SELECT source_key, status, detail FROM state_effect_findings WHERE relative_path = 'src/a.py'",
                'result_delivery': 'inline',
            }))
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual([['module:src/a.py', 'unresolved', 'Lean executable unavailable on PATH']],
                         result.structured_content['rows'])

    async def test_source_change_rebuild_and_disabled_projection(self):
        import asyncio
        from mcp import types

        source = self._source('src/a.py', 'x = 1\n')

        def analyze(root, sources, ownership=None):
            return [(f'module:{path}', path, item.language, '<module>', 1, None, 'unresolved', False,
                     '[]', '[]', item.signature) for path, item in sources.items() if path == 'src/a.py']

        with patch.object(boundary_tables, 'analyze_state', side_effect=analyze):
            gateway = await self._gateway()

            async def rows():
                response = await gateway.call(None, types.CallToolRequestParams(name='query_run', arguments={
                    'sql': 'SELECT detail FROM state_effect_findings', 'result_delivery': 'inline',
                }))
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content['rows']

            original = await rows()
            self.assertEqual(1, len(original))
            source.write_text('x = 2\n', encoding='utf-8')
            async with asyncio.timeout(6):
                while await rows() == original:
                    await asyncio.sleep(.03)
            changed = await rows()
            result = await gateway.call(None, types.CallToolRequestParams(
                name='query_rebuild', arguments={'target': 'state_effect_findings'}))
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual(changed, await rows())
            await gateway.close()
            disabled = await self._gateway(enabled=False)
            schema = await disabled.call(None, types.CallToolRequestParams(name='query_schema', arguments={}))
            self.assertNotIn('state_effect_findings', schema.structured_content['tables'])
