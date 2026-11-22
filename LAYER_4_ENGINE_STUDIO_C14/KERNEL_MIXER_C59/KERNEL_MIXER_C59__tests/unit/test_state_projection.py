"""Check native state findings publication and rebuild dependencies."""

from types import SimpleNamespace
from unittest import TestCase
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
        check.assert_called_once_with(ownership, sources, [], include_entry_bypasses=True)
        analyze.assert_called_once_with('root', sources, ownership=ownership)

    def test_analysis_runs_without_structure(self):
        selection = SimpleNamespace(root='root')
        sources = {'a.py': object()}
        with patch.object(boundary_tables, 'analyze_state', return_value=[]) as analyze:
            self.assertEqual(([], [], []), boundary_tables.prepare_boundaries(selection, None, sources, [], None, {}))
        analyze.assert_called_once_with('root', sources, ownership=None)

    def test_lint_reports_denied_and_silent_actions(self):
        from contextlib import redirect_stderr
        from io import StringIO
        from KERNEL_MIXER_C59.state_lint import _report

        rows = [
            ('module:src/effects.py', 'src/effects.py', 'python', 'action', 1, 'REQUEST_CTX',
             'deadEnd', True, '[]', '[]', ''),
            ('module:src/effects.py', 'src/effects.py', 'python', 'action', 2, None,
             'hasEffects', False, '[]', '[{"line": 2, "kind": "write", "name": "REQUEST_CTX"}]', ''),
            ('module:src/effects.py', 'src/effects.py', 'python', 'declared', 3, None,
             'declaredNoOp', False, '[]', '[]', ''),
        ]
        errors = StringIO()
        with redirect_stderr(errors):
            self.assertEqual(1, _report(rows))
        self.assertIn('silent state action action', errors.getvalue())
        self.assertIn('state write denied', errors.getvalue())
        self.assertNotIn('declared', errors.getvalue())


