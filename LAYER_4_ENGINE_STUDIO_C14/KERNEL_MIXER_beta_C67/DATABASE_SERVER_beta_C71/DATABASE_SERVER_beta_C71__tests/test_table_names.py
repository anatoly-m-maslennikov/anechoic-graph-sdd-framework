"""Keep pre-prefix Beta databases readable after canonical table migration."""

import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import duckdb

from .. import persistence
from ..carrier_checkpoint import read_checkpoint
from ..table_names import main_objects
from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _query,
    _server,
)


class TableNamesTest(unittest.TestCase):
    def test_open_database_upgrades_previous_prefix_names(self):
        with TemporaryDirectory(prefix="ane-db-names-", dir="/tmp") as directory:
            path = Path(directory).resolve() / "first-prefix.duckdb"
            with _server(path):
                pass
            with duckdb.connect(str(path)) as connection:
                connection.execute("CREATE TABLE mrt_import_read_issues (relative_path VARCHAR, error_message VARCHAR)")
                connection.execute("INSERT INTO mrt_import_read_issues VALUES ('bad.py', 'failed to read')")
                connection.execute("CREATE VIEW import_read_issues AS SELECT * FROM mrt_import_read_issues")
                connection.execute("DROP VIEW ops_carrier_hashes")
                connection.execute(
                    "CREATE TABLE ops_carrier_hashes (carrier_sha256_by_path VARCHAR)"
                )
                connection.execute(
                    "INSERT INTO ops_carrier_hashes VALUES (?)",
                    [json.dumps({"a.py": "a" * 64})],
                )
            with _server(path):
                pass
            with duckdb.connect(str(path), read_only=True) as connection:
                for name in (
                    "mrt_diag_import_read_issues",
                    "mrt_import_read_issues",
                    "import_read_issues",
                ):
                    self.assertEqual(
                        [("bad.py", "failed to read")],
                        connection.execute(f"SELECT * FROM {name}").fetchall(),
                    )
                kinds = dict(
                    connection.execute(
                        "SELECT table_name, table_type FROM information_schema.tables "
                        "WHERE table_name IN ('mrt_diag_import_read_issues', 'mrt_import_read_issues', 'ops_ingestion_issues')"
                    ).fetchall()
                )
                self.assertEqual(
                    {
                        "mrt_diag_import_read_issues": "VIEW",
                        "mrt_import_read_issues": "VIEW",
                        "ops_ingestion_issues": "BASE TABLE",
                    },
                    kinds,
                )
                self._assert_checkpoint(connection)

    def test_open_database_migrates_legacy_rows_and_reopens_idempotently(self):
        with TemporaryDirectory(
            prefix="ane-db-names-", dir="/tmp"
        ) as directory:
            path = Path(directory).resolve() / "legacy.duckdb"
            self._write_legacy_database(path)
            path.chmod(0o600)

            with _server(path) as client:
                self._assert_selection_accepts_both_names(client)
            with duckdb.connect(str(path), read_only=True) as connection:
                self._assert_canonical_rows(connection)
                self._assert_public_compatibility(connection)
            with _server(path):
                pass
            with duckdb.connect(str(path), read_only=True) as connection:
                self._assert_canonical_rows(connection)
                self._assert_public_compatibility(connection)

    def test_open_database_migrates_canonical_checkpoint_and_preserves_empty_state(
        self,
    ):
        for hashes in (
            {"control/é.md": "b" * 64, "root.md": "c" * 64},
            {},
            None,
        ):
            with self.subTest(hashes=hashes):
                directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
                path = Path(directory).resolve() / "old.duckdb"
                self._write_canonical_checkpoint(path, hashes)
                expected = [] if hashes is None else [hashes]
                rows = [
                    (name, PurePosixPath(name).parent.as_posix(), digest)
                    for name, digest in (hashes or {}).items()
                ]
                for _ in range(2):
                    with patch.object(persistence, "connect", duckdb.connect):
                        with persistence.open_bound_database(
                            str(path), PIN, "instance"
                        ) as connection:
                            self.assertEqual(
                                hashes, read_checkpoint(connection)
                            )
                            self._assert_checkpoint_views(connection, expected)
                            self.assertEqual(
                                sorted(rows),
                                connection.execute(
                                    "SELECT * FROM ops_generation_carrier_digests ORDER BY path"
                                ).fetchall(),
                            )

    def test_open_database_restores_canonical_checkpoint_after_migration_failure(
        self,
    ):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        path = Path(directory).resolve() / "old.duckdb"
        hashes = {"root.md": "b" * 64}
        self._write_canonical_checkpoint(path, hashes)
        with patch.object(persistence, "connect", duckdb.connect):
            with patch.object(
                persistence,
                "ensure_structure_table",
                side_effect=ValueError("late failure"),
            ):
                with self.assertRaisesRegex(ValueError, "late failure"):
                    persistence.open_bound_database(str(path), PIN, "instance")
            with duckdb.connect(str(path), read_only=True) as connection:
                objects = main_objects(connection)
                self.assertEqual(
                    "BASE TABLE", objects["ops_generation_carrier_hashes"]
                )
                self.assertNotIn("ops_generation_carrier_digests", objects)
                self.assertEqual(
                    [(json.dumps(hashes),)],
                    connection.execute(
                        "SELECT * FROM generation_carriers"
                    ).fetchall(),
                )
            with persistence.open_bound_database(
                str(path), PIN, "instance"
            ) as connection:
                self.assertEqual(hashes, read_checkpoint(connection))

    @staticmethod
    def _write_canonical_checkpoint(path, hashes):
        with duckdb.connect(str(path)) as connection:
            connection.execute(
                "CREATE TABLE ops_project_binding (manifest_sha256 VARCHAR, instance_id VARCHAR)"
            )
            connection.execute(
                "INSERT INTO ops_project_binding VALUES (?, ?)",
                [PIN, "instance"],
            )
            connection.execute(
                "CREATE TABLE ops_generation_carrier_hashes (carrier_sha256_by_path VARCHAR)"
            )
            if hashes is not None:
                connection.execute(
                    "INSERT INTO ops_generation_carrier_hashes VALUES (?)",
                    [json.dumps(hashes)],
                )
            connection.execute(
                "CREATE VIEW ops_carrier_hashes AS SELECT * FROM ops_generation_carrier_hashes"
            )
            connection.execute(
                "CREATE VIEW generation_carriers AS SELECT carrier_sha256_by_path AS hashes "
                "FROM ops_generation_carrier_hashes"
            )
        path.chmod(0o600)

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
            connection.execute("INSERT INTO generation VALUES ('legacy-generation', '{}', ?)",
                               [json.dumps({"components": {}, "project": {"ref": "AN-S-1", "sha256": PIN}})])
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
            connection.execute(
                'SELECT reference, "content.summary" FROM mrt_atoms'
            ).fetchall(),
        )
        self.assertEqual(
            [("legacy-generation",)],
            connection.execute("SELECT id FROM ops_generation").fetchall(),
        )
        self.assertEqual(
            [(PIN, "instance")],
            connection.execute("SELECT * FROM ops_project_binding").fetchall(),
        )
        self._assert_checkpoint(connection)
        self.assertEqual(
            [(json.dumps({"legacy": True}),)],
            connection.execute(
                "SELECT witness FROM ops_generation_reuse"
            ).fetchall(),
        )
        self.assertEqual(
            [
                (
                    "a" * 32,
                    "C00",
                    "legacy",
                    0,
                    "trigger",
                    "start",
                    1.0,
                    [],
                    None,
                    None,
                    "{}",
                )
            ],
            connection.execute("SELECT * FROM src_flow_events").fetchall(),
        )

    def _assert_checkpoint(self, connection):
        self._assert_checkpoint_views(connection, [{"a.py": "a" * 64}])
        self.assertEqual(
            [("a.py", ".", "a" * 64)],
            connection.execute(
                "SELECT * FROM ops_generation_carrier_digests"
            ).fetchall(),
        )

    def _assert_checkpoint_views(self, connection, expected):
        objects = main_objects(connection)
        self.assertEqual(
            "BASE TABLE", objects["ops_generation_carrier_digests"]
        )
        for table, column in (
            ("ops_generation_carrier_hashes", "carrier_sha256_by_path"),
            ("ops_carrier_hashes", "carrier_sha256_by_path"),
            ("generation_carriers", "hashes"),
        ):
            self.assertEqual("VIEW", objects[table])
            self.assertEqual(
                expected,
                [
                    json.loads(raw)
                    for (raw,) in connection.execute(
                        f"SELECT {column} FROM {table}"
                    ).fetchall()
                ],
            )

    def _assert_public_compatibility(self, connection):
        self.assertEqual(
            connection.execute(
                'SELECT reference, "content.summary" FROM mrt_atoms'
            ).fetchall(),
            connection.execute(
                'SELECT reference, "content.summary" FROM atoms'
            ).fetchall(),
        )
        self.assertEqual(
            connection.execute("SELECT * FROM src_flow_events").fetchall(),
            connection.execute("SELECT * FROM flow_events").fetchall(),
        )

    def _assert_selection_accepts_both_names(self, client):
        for sql in (
            "SELECT reference FROM atoms",
            "SELECT reference FROM mrt_atoms",
        ):
            for target in ("atoms", "mrt_atoms"):
                response = _query(client, sql, page_size=10)
                self.assertEqual(200, response.status_code, response.text)
                query_id = response.json()["result"]["query_id"]
                rebuilt = client.post(
                    "/results/rebuild", json={**BINDING, "target": target}
                )
                self.assertEqual(200, rebuilt.status_code, rebuilt.text)
                self.assertIn(query_id, rebuilt.json()["result"]["result_ids"])


if __name__ == "__main__":
    unittest.main()
