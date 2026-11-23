from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import json
import unittest
from pathlib import Path
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    QueryExecutionError,
    WorkbenchUnavailableError,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import public_rows as public_rows_module  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import SCOPE_FIELDS  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.query_store_test_support import QueryStoreFixture


class QueryStoreTest(QueryStoreFixture, unittest.TestCase):
    def test_exact_public_schema_cte_and_direct_replacement(self) -> None:
        self.store.replace([self.atom("A"), self.atom(None)], [self.scope("S")])
        schema = self.store.run(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'main' AND table_name NOT LIKE '__duckpgq_%' "
            "ORDER BY table_name, ordinal_position"
        )["rows"]
        atom_fields = tuple(column for table, column in schema if table == "atoms")
        self.assertTrue({
            "relative_path", "filename", "status_group", "reference", "header.atom_id",
            "header.version", "header.status", "header.relations", "hash",
        } <= set(atom_fields))
        self.assertFalse(any(field.startswith("content.") for field in atom_fields))
        self.assertEqual(
            [[table, field] for table in (
                "atom_declared_carrier_issues", "atom_duplicate_revision_issues", "atom_parse_issues",
                "atom_physical_carrier_issues", "atom_schema_issues",
            ) for field in (
                "reference", "relative_path", "filename", "issue_category", "property", "observed", "expected", "diagnostic",
            )]
            + [["atoms", field] for field in atom_fields]
            + [["change_log", field] for field in ("observed_at", "operation", "old_path", "new_path")]
            + [["live_runs", field] for field in ("run_id", "session_id", "tool", "status")]
            + [["query_log", field] for field in ("log_id", "at", "sql", "outcome", "error", "row_count", "column_count")]
            + [["query_log_records", field] for field in ("log_id", "at", "sql", "outcome", "error", "row_count", "column_count")]
            + [["relations", field] for field in ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")]
            + [["runtime_diagnostics", field] for field in (
                "observed_at", "name", "outcome", "returned_outcome", "error_category", "project_prefix",
                "project_instance_id",
            )]
            + [["scope_units", field] for field in SCOPE_FIELDS],
            schema,
        )
        self.assertEqual(
            [[2]],
            self.store.run("WITH source AS (SELECT * FROM atoms) SELECT count(*) FROM source")["rows"],
        )
        self._assert_empty_replacement()
    def _assert_empty_replacement(self):
        connection = self.store._connection
        self.store.replace([], [])
        self.assertIs(connection, self.store._connection)
        empty_atom_fields = self.store.schema()["tables"]["atoms"]
        self.assertEqual(
            {
                "valid": True,
                "columns": [{"name": column["name"], "type": column["type"], "has_values": True}
                            for column in empty_atom_fields],
                "row_count": 0,
                "column_count": len(empty_atom_fields),
                "sql": "SELECT * FROM atoms",
            },
            self.store.check("SELECT * FROM atoms"),
        )


    def test_check_preserves_duplicate_columns_without_retaining_result(self) -> None:
        before_results = dict(self.store._results)
        before_tables = self.store._connection.sql(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
        ).fetchall()
        checked = self.store.check(
            "SELECT 1::INTEGER AS duplicate, 'x'::VARCHAR AS duplicate WHERE false"
        )
        self.assertEqual(
            {
                "valid": True,
                "columns": [
                    {"name": "duplicate", "type": "INTEGER", "has_values": True},
                    {"name": "duplicate", "type": "VARCHAR", "has_values": True},
                ],
                "row_count": 0,
                "column_count": 2,
                "sql": "SELECT 1::INTEGER AS duplicate, 'x'::VARCHAR AS duplicate WHERE false",
            },
            checked,
        )
        self.assertEqual(before_results, self.store._results)
        self.assertEqual(before_tables, self.store._connection.sql(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
        ).fetchall())

    def test_schema_exposes_actual_status_literals_without_running_a_query(self) -> None:
        done = self.atom("B")
        done["status"] = "Done"
        done["header_json"]["status"] = "Done"
        self.store.replace([self.atom("A"), done], [])

        schema = self.store.schema()["tables"]

        status = next(column for column in schema["atoms"] if column["name"] == "header.status")
        self.assertEqual(["Active", "Done"], status["values"])

    def test_normal_source_edit_uses_delta_not_projection_replacement(self) -> None:
        unchanged = self.atom("B")
        self.store.replace([self.atom("A"), unchanged], [])
        edited = self.atom("A")
        edited["version"] = 2
        edited["header_json"]["version"] = 2

        with patch(
            "KERNEL_MIXER_C59.query_store.insert_rows"
        ) as full_replace:
            changed = self.store.apply([edited, unchanged], [], relation_types=set())

        self.assertTrue(changed)
        full_replace.assert_not_called()
        self.assertEqual([["A", 2], ["B", 1]], self.store.run(
            'SELECT reference, "header.version" FROM atoms ORDER BY reference'
        )["rows"])

    def test_full_replace_projects_once_and_sql_matches_retained_snapshot(self) -> None:
        atoms = [
            self.atom("A", [self.edge("Atom", "A", "Scope Unit", "S")]),
            self.atom("B"),
        ]
        scopes = [self.scope("S")]
        with patch.object(
            public_rows_module, "_atom", wraps=public_rows_module._atom,
        ) as project:
            self.store.replace(atoms, scopes, relation_types={"CONTAINS"})

        self.assertEqual(len(atoms), project.call_count)
        snapshot = self.store._projection
        assert snapshot is not None
        atom_fields = [column[0] for column in self.store._connection.execute(
            "SELECT * FROM atoms LIMIT 0"
        ).description]
        scope_fields = [column[0] for column in self.store._connection.execute(
            "SELECT * FROM scope_units LIMIT 0"
        ).description]
        atom_json = snapshot.header_schema.json_names | {"header.relations"}
        sql_atoms = [
            {
                name: json.loads(value) if name in atom_json and value is not None else value
                for name, value in zip(atom_fields, values, strict=True)
            }
            for values in self.store._connection.execute(
                'SELECT * FROM atoms ORDER BY "relative_path", filename'
            ).fetchall()
        ]
        sql_scopes = [
            {
                name: json.loads(value) if name == "relations" and value is not None else value
                for name, value in zip(scope_fields, values, strict=True)
            }
            for values in self.store._connection.execute("SELECT * FROM scope_units ORDER BY name").fetchall()
        ]
        snapshot_atoms = sorted(
            snapshot.atoms.values(), key=lambda row: (row["relative_path"], row["filename"]),
        )
        snapshot_scopes = sorted(snapshot.scopes.values(), key=lambda row: row["name"])
        self.assertEqual(snapshot_atoms, sql_atoms)
        self.assertEqual(snapshot_scopes, sql_scopes)
        self.assertEqual(
            [row["hash"] for row in snapshot_atoms], [row["hash"] for row in sql_atoms],
        )

    def test_failed_full_replace_keeps_the_published_snapshot(self) -> None:
        self.store.replace([self.atom("A")], [])
        previous_projection = self.store._projection
        previous_header_state = self.store._header_state

        with patch(
            "KERNEL_MIXER_C59.query_store.insert_rows",
            side_effect=RuntimeError("write failed"),
        ), self.assertRaises(WorkbenchUnavailableError):
            self.store.replace([self.atom("B")], [])

        self.assertIs(previous_projection, self.store._projection)
        self.assertIs(previous_header_state, self.store._header_state)

    def test_native_admission_errors_leave_a_valid_connection(self) -> None:
        self.assertEqual([[1]], self.store.run("-- comment ;\nSELECT 1; /* comment ; */")["rows"])
        self.assertEqual(
            [[""]],
            self.store.run("SELECT value FROM duckdb_settings() WHERE name = 'temp_directory'")["rows"],
        )
        with self.assertRaises(ValueError):
            self.store.run("SELECT 1; SELECT 2")
        with self.assertRaises(ValueError):
            self.store.run("INSERT INTO atoms VALUES ('bad')")
        with self.assertRaises(ValueError):
            self.store.run("ATTACH 'outside.duckdb' AS outside")
        with self.assertRaises(RuntimeError):
            self.store.run("WITH attempted AS (DELETE FROM atoms RETURNING filename) SELECT * FROM attempted")
        self.assertEqual([[0]], self.store.run("SELECT count(*) FROM atoms")["rows"])
        with self.assertRaises(RuntimeError):
            self.store.run("SELECT * FROM read_csv_auto('/private/tmp/workbench-does-not-exist.csv')")
        with self.assertRaises(RuntimeError):
            self.store.run("SELECT missing FROM atoms")
        self.assertEqual([[1]], self.store.run("SELECT 1")["rows"])

    def test_public_query_errors_do_not_echo_sql_or_literals(self) -> None:
        cases = (
            ("SELECT missing FROM atoms WHERE 'private_binder_value' = 'x'", "binding"),
            ("SELECT 'private_parser_value' FROM", "syntax"),
            ("SELECT CAST('private_conversion_value' AS INTEGER)", "convert"),
        )
        for sql, reason in cases:
            for operation in (self.store.run, self.store.check):
                with self.subTest(sql=sql, operation=operation.__name__):
                    stderr = StringIO()
                    with redirect_stderr(stderr), self.assertRaises((ValueError, QueryExecutionError)) as caught:
                        operation(sql)
                    message = str(caught.exception)
                    self.assertNotIn("private_", message)
                    self.assertNotIn(sql, message)
                    self.assertNotIn("private_", stderr.getvalue())
                    self.assertIn(reason, message.lower())

    def test_native_ctas_conversion_failure_keeps_the_owner_available(self) -> None:
        with self.assertRaisesRegex(QueryExecutionError, "Could not convert"):
            self.store.run("SELECT CAST('not-an-integer' AS INTEGER)")
        self.assertEqual([[1]], self.store.run("SELECT 1")["rows"])

