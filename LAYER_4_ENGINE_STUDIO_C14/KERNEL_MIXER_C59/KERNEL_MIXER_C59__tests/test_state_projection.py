"""Check native state findings publication and rebuild dependencies."""
from unittest.mock import NonCallableMock

from contextlib import redirect_stderr
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

import duckdb
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    NativeQueryRebuild,
    _report,
    prepare_boundaries,
    public_schema,
    remove_boundaries,
    replace_boundaries,
)

from .KERNEL_MIXER_C59__tests__shared import state_finding_row

_BOUNDARY_TABLES = 'KERNEL_MIXER_C59.boundary_tables'


class StateProjectionTests(TestCase):
    def test_publication_rebuild_rollback_and_removal(self):
        connection = duckdb.connect(':memory:')
        self.addCleanup(connection.close)
        row = state_finding_row(
            "src/a.py", "<module>", 1, "unresolved", detail="Lean unavailable"
        )
        connection.execute("BEGIN")
        replace_boundaries(connection, ([], [], [row]))
        connection.execute('COMMIT')
        self.assertEqual([row], connection.execute('SELECT * FROM state_effect_findings').fetchall())
        schema = public_schema(connection, NonCallableMock(
            spec_set=[
                'status_names'
            ],
            status_names=[]))
        self.assertIn('state_effect_findings', schema['tables'])

        rebuild = NativeQueryRebuild()
        rebuild._realization_options = ()
        store = NonCallableMock(
            spec_set=[
                '_projection'
            ],
            _projection=NonCallableMock(
                spec_set=["graph"],
                graph=NonCallableMock(spec_set=["tables"], tables={}),
            ),
        )
        table, scope, dependencies = rebuild._rebuild_scope(
            store, "state_effect_findings"
        )
        self.assertEqual(
            (table, scope), ("state_effect_findings", "realization")
        )
        self.assertIn("state_effect_findings", dependencies)

        connection.execute('BEGIN')
        replace_boundaries(connection, ([], [], []))
        connection.execute('ROLLBACK')
        self.assertEqual([row], connection.execute('SELECT * FROM state_effect_findings').fetchall())
        remove_boundaries(connection)
        self.assertNotIn('state_effect_findings', public_schema(connection, NonCallableMock(
            spec_set=[
                'status_names'
            ],
            status_names=[]))['tables'])

    def test_analysis_receives_same_ownership_as_access_check(self):
        selection = NonCallableMock(
            spec_set=[
                'root', 'control_root'
            ],
            root='root', control_root='control')
        snapshot = NonCallableMock(
            spec_set=["components", "packages"], components={}, packages={}
        )
        sources, ownership, expected = (
            {"a.py": object()},
            object(),
            [("finding",)],
        )
        with (
            patch(
                f"{_BOUNDARY_TABLES}.code_access_occurrences",
                return_value=(set(), []),
            ),
            patch(
                f"{_BOUNDARY_TABLES}.build_code_access_ownership",
                return_value=ownership,
            ) as build,
            patch(
                f"{_BOUNDARY_TABLES}.check_code_access", return_value=[]
            ) as check,
            patch(
                f"{_BOUNDARY_TABLES}.analyze_state", return_value=expected
            ) as analyze,
        ):
            result = prepare_boundaries(
                selection, snapshot, sources, [], None, {}
            )
        self.assertEqual(([], [], expected), result)
        build.assert_called_once()
        check.assert_called_once_with(
            ownership, sources, [], include_entry_bypasses=True
        )
        analyze.assert_called_once_with("root", sources, ownership=ownership)

    def test_analysis_runs_without_structure(self):
        selection = NonCallableMock(spec_set=["root"], root="root")
        sources = {"a.py": object()}
        with patch(
            f"{_BOUNDARY_TABLES}.analyze_state", return_value=[]
        ) as analyze:
            declarations, findings, state = prepare_boundaries(
                selection, None, sources, [], None, {}
            )
        self.assertEqual(([], []), (declarations, state))
        self.assertEqual(
            [
                (
                    "module:a.py",
                    "a.py",
                    None,
                    None,
                    "Package entry",
                    "denied",
                    "Expected one __shared or __public entry in ., found 0",
                )
            ],
            findings,
        )
        analyze.assert_called_once_with("root", sources, ownership=None)

    def test_lint_reports_denied_and_silent_actions(self):
        path = 'src/effects.py'
        rows = [
            state_finding_row(
                path,
                "action",
                1,
                "deadEnd",
                witness="REQUEST_CTX",
                dead_end=True,
            ),
            state_finding_row(
                path,
                "action",
                2,
                "hasEffects",
                violations='[{"line": 2, "kind": "write", "name": "REQUEST_CTX"}]',
            ),
            state_finding_row(path, "declared", 3, "declaredNoOp"),
        ]
        errors = StringIO()
        with redirect_stderr(errors):
            self.assertEqual(1, _report(rows))
        self.assertIn('silent state action action', errors.getvalue())
        self.assertIn('state write denied', errors.getvalue())
        self.assertNotIn('declared', errors.getvalue())


