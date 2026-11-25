"""Keep pre-prefix Beta databases readable after canonical table migration."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import duckdb

from ..DATABASE_SERVER_beta_C71__shared import open_database
from ..query_results import QueryResults
from .DATABASE_SERVER_beta_C71__tests__shared import PIN


class TableNamesTest(unittest.TestCase):
    def test_open_database_upgrades_previous_prefix_names(self):
        with TemporaryDirectory(prefix="ane-db-names-", dir="/tmp") as directory:
            path = Path(directory).resolve() / "first-prefix.duckdb"
            with open_database(str(path), PIN, "instance") as connection:
                connection.execute("CREATE TABLE mrt_import_read_issues (relative_path VARCHAR, error_message VARCHAR)")
                connection.execute("INSERT INTO mrt_import_read_issues VALUES ('bad.py', 'failed to read')")
                connection.execute("CREATE VIEW import_read_issues AS SELECT * FROM mrt_import_read_issues")
                connection.execute("CREATE TABLE ops_carrier_hashes (carrier_sha256_by_path VARCHAR)")
                connection.execute("INSERT INTO ops_carrier_hashes VALUES (?)", [json.dumps({"a.py": "a" * 64})])
            with open_database(str(path), PIN, "instance") as connection:
                for name in ("mrt_diag_import_read_issues", "mrt_import_read_issues", "import_read_issues"):
                    self.assertEqual([("bad.py", "failed to read")],
                                     connection.execute(f"SELECT * FROM {name}").fetchall())
                kinds = dict(connection.execute(
                    "SELECT table_name, table_type FROM information_schema.tables "
                    "WHERE table_name IN ('mrt_diag_import_read_issues', 'mrt_import_read_issues', 'ops_ingestion_issues')"
                ).fetchall())
                self.assertEqual({"mrt_diag_import_read_issues": "VIEW", "mrt_import_read_issues": "VIEW",
                                  "ops_ingestion_issues": "BASE TABLE"}, kinds)
                self._assert_checkpoint(connection)

    def test_open_database_migrates_legacy_rows_and_reopens_idempotently(self):
        with TemporaryDirectory(prefix="ane-db-names-", dir="/tmp") as directory:
            path = Path(directory).resolve() / "legacy.duckdb"
            self._write_legacy_database(path)
            path.chmod(0o600)

            connection = open_database(str(path), PIN, "instance")
            try:
                self._assert_canonical_rows(connection)
                self._assert_public_compatibility(connection)
                self._assert_selection_accepts_both_names(connection)
            finally:
                connection.close()

            reopened = open_database(str(path), PIN, "instance")
            try:
                self._assert_canonical_rows(reopened)
                self._assert_public_compatibility(reopened)
            finally:
                reopened.close()

    @staticmethod
    def _write_legacy_database(path):
        connection = duckdb.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE project_binding (manifest_sha256 VARCHAR NOT NULL, instance_id VARCHAR NOT NULL)"
            )
            connection.execute("INSERT INTO project_binding VALUES (?, ?)", [PIN, "instance"])
            connection.execute('CREATE TABLE atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)')
            connection.execute("INSERT INTO atoms VALUES ('legacy-atom', 'retained')")
            connection.execute("CREATE TABLE generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
            connection.execute("INSERT INTO generation VALUES (?, ?, ?)", ["legacy-generation", "{}", json.dumps(
                {"project": {"ref": "AN-S-1", "sha256": PIN}, "components": {}})])
            connection.execute("CREATE TABLE generation_carriers (hashes VARCHAR)")
            connection.execute("INSERT INTO generation_carriers VALUES (?)", [json.dumps({"a.py": "a" * 64})])
            connection.execute("CREATE TABLE generation_reuse (witness VARCHAR)")
            connection.execute("INSERT INTO generation_reuse VALUES (?)", [json.dumps({"legacy": True})])
            connection.execute("""CREATE TABLE flow_events (
                run_id VARCHAR NOT NULL, component VARCHAR NOT NULL, action VARCHAR NOT NULL,
                sequence INTEGER NOT NULL, kind VARCHAR NOT NULL, name VARCHAR NOT NULL,
                "at" DOUBLE NOT NULL, causes INTEGER[] NOT NULL, target VARCHAR, outcome VARCHAR,
                detail JSON NOT NULL, PRIMARY KEY (run_id, sequence))""")
            connection.execute(
                "INSERT INTO flow_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ["a" * 32, "C00", "legacy", 0, "trigger", "start", 1.0, [], None, None, "{}"],
            )
        finally:
            connection.close()

    def _assert_canonical_rows(self, connection):
        self.assertEqual(
            [("legacy-atom", "retained")],
            connection.execute('SELECT reference, "content.summary" FROM mrt_atoms').fetchall(),
        )
        self.assertEqual([("legacy-generation",)], connection.execute("SELECT id FROM ops_generation").fetchall())
        self.assertEqual([(PIN, "instance")], connection.execute("SELECT * FROM ops_project_binding").fetchall())
        self._assert_checkpoint(connection)
        self.assertEqual(
            [(json.dumps({"legacy": True}),)],
            connection.execute("SELECT witness FROM ops_generation_reuse").fetchall(),
        )
        self.assertEqual(
            [("a" * 32, "C00", "legacy", 0, "trigger", "start", 1.0, [], None, None, "{}")],
            connection.execute("SELECT * FROM src_flow_events").fetchall(),
        )

    def _assert_checkpoint(self, connection):
        expected = [(json.dumps({"a.py": "a" * 64}),)]
        for table in ("ops_generation_carrier_hashes", "ops_carrier_hashes"):
            self.assertEqual(expected, connection.execute(f"SELECT carrier_sha256_by_path FROM {table}").fetchall())
        self.assertEqual(expected, connection.execute("SELECT hashes FROM generation_carriers").fetchall())

    def _assert_public_compatibility(self, connection):
        self.assertEqual(
            connection.execute('SELECT reference, "content.summary" FROM mrt_atoms').fetchall(),
            connection.execute('SELECT reference, "content.summary" FROM atoms').fetchall(),
        )
        self.assertEqual(
            connection.execute("SELECT * FROM src_flow_events").fetchall(),
            connection.execute("SELECT * FROM flow_events").fetchall(),
        )

    def _assert_selection_accepts_both_names(self, connection):
        for sql in ("SELECT reference FROM atoms", "SELECT reference FROM mrt_atoms"):
            for target in ("atoms", "mrt_atoms"):
                queries = QueryResults()
                query_id = queries.run(connection, sql, 10)["query_id"]
                self.assertEqual({query_id}, set(queries._selection(connection, target)))


if __name__ == "__main__":
    unittest.main()
