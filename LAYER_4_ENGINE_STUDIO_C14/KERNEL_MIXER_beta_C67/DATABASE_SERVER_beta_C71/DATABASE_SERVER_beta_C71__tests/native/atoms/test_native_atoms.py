"""Admit a native revision snapshot and its property graph through the server socket."""

import json
import unittest
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _generation,
    _query,
    _server,
)


from .native_atoms_cases import NativeSchemaCases, StagedNativeAtomsCases


def _digest(value):
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


def _native_atom_rows():
    atom = {
        "reference": "AN-T-1",
        "exact_ref": "AN-T-1@2",
        "summary": "second",
        "filename": "AN-T-1-TASK.md",
        "relative_path": "_anechoic_anechoic",
        "status_group": "Current",
        "status": "active",
        "version": 2,
    }
    archived = atom | {
        "reference": "AN-T-1@1",
        "exact_ref": "AN-T-1@1",
        "status_group": "Archived",
        "status": "archived",
        "version": 1,
        "filename": "AN-T-1@1-TASK.md",
        "summary": "first",
    }
    return atom, archived


def _native_generation():
    data = _generation()
    model = json.loads(data["model"])
    model["bindings"]["endpoints"] = {
        "CONTAINED_BY": [{}, False],
        "CONTAINS": [{}, True],
    }
    data["model"] = json.dumps(model)
    data["receipt"]["model_descriptor_sha256"] = sha256(
        data["model"].encode()
    ).hexdigest()
    atom, archived = _native_atom_rows()
    relationship = {
        "source_kind": "Atom",
        "source_ref": "AN-T-1",
        "target_kind": "Component",
        "target_ref": "C00",
        "relation_type": "CONTAINED_BY",
        "derived": False,
    }
    data["snapshot"] = {
        "schema_version": 2,
        "manifest_sha256": PIN,
        "atoms": [atom, archived],
        "relations": [relationship],
        "relation_types": ["CONTAINED_BY", "CONTAINS"],
    }
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    return data


class NativeAtomTest(unittest.TestCase):
    def test_generation_keeps_an_atom_with_an_undeclared_relation_issue(self):
        data = _native_generation()
        issue = {
            "relative_path": "_anechoic_anechoic/AN-T-1-TASK.md",
            "code": "undeclared_relation",
            "message": "Undeclared native relation: UNKNOWN",
            "atom_ref": "AN-T-1@2",
            "related_paths": [],
        }
        with _server() as client:
            for row, status, message in (
                (issue, 200, None),
                (
                    issue | {"atom_ref": "AN-T-1@1"},
                    400,
                    "Undeclared relation issue must match an admitted Atom",
                ),
                (
                    issue | {"code": "invalid_value"},
                    400,
                    "Invalid carrier cannot have an admitted Atom",
                ),
            ):
                with self.subTest(row=row):
                    data["snapshot"]["ingestion_issues"] = [row]
                    data["receipt"]["snapshot_sha256"] = _digest(
                        data["snapshot"]
                    )
                    response = client.put("/generation", json=data)
                    self.assertEqual(
                        status, response.status_code, response.text
                    )
                    if message is not None:
                        self.assertEqual(
                            message, response.json()["error"]["message"]
                        )
            self.assert_native_rows(client)
            rows = client.get("/ingestion/issues", params=BINDING).json()[
                "result"
            ]["rows"]
            self.assertEqual([{"source": "atom", **issue}], rows)

    def test_strict_records_preserve_payload_and_error_order(self):
        original = _native_generation()
        with _server() as client:
            self.assertEqual(
                200, client.put("/generation", json=original).status_code
            )
            for collection, field, value, message in (
                ("atoms", "version", True, "Invalid native Atom fields"),
                ("atoms", "extra", 1, "Invalid native Atom fields"),
                ("relations", "derived", 0, "Invalid native relation"),
                ("relations", "extra", 1, "Invalid native relation"),
            ):
                invalid = deepcopy(original)
                invalid["snapshot"][collection][0][field] = value
                invalid["receipt"]["snapshot_sha256"] = _digest(
                    invalid["snapshot"]
                )
                response = client.put("/generation", json=invalid)
                self.assertEqual(400, response.status_code, response.text)
                self.assertIn(message, response.text)
            for field, value, message in (
                ("schema_version", 2.0, "Invalid native snapshot envelope"),
                ("extra", None, "Invalid native snapshot envelope"),
                ("atoms", {}, "Native snapshot collections must be lists"),
            ):
                invalid = deepcopy(original)
                invalid["snapshot"][field] = value
                invalid["receipt"]["snapshot_sha256"] = _digest(
                    invalid["snapshot"]
                )
                response = client.put("/generation", json=invalid)
                self.assertEqual(400, response.status_code, response.text)
                self.assertIn(message, response.text)
            invalid = deepcopy(original)
            invalid["snapshot"]["atoms"][0]["exact_ref"] = "invalid"
            invalid["snapshot"]["atoms"][1]["version"] = True
            invalid["receipt"]["snapshot_sha256"] = _digest(
                invalid["snapshot"]
            )
            response = client.put("/generation", json=invalid)
            self.assertIn("Invalid native Atom identity", response.text)
            self.assert_native_rows(client)

    def test_upgrade_restart_and_refusal_preserve_generation(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "projection.duckdb"
            with _server(path) as client:
                self.assertEqual(
                    200,
                    client.put("/generation", json=_generation()).status_code,
                )
            with duckdb.connect(str(path)) as connection:
                connection.execute(
                    "CREATE VIEW main.native_references AS SELECT 'legacy' AS reference"
                )
            native = _native_generation()
            with _server(path) as client:
                admitted = client.put("/generation", json=native)
                self.assertEqual(200, admitted.status_code, admitted.text)
                self.assert_native_rows(client)
                malformed = deepcopy(native)
                malformed["snapshot"]["atoms"][0]["summary"] = "tampered"
                refused = client.put("/generation", json=malformed)
                self.assertEqual(400, refused.status_code, refused.text)
                self.assertIn("snapshot digest mismatch", refused.text)
                self.assertEqual(
                    400,
                    client.put("/generation", json=_generation()).status_code,
                )
                self.assert_native_rows(client)
            with _server(path) as client:
                self.assert_native_rows(client)

    def test_generation_with_migrated_current_journal_view(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            legacy = root / ".anechoic_runtime/workbench/projection.duckdb"
            legacy.parent.mkdir(parents=True)
            with duckdb.connect(str(legacy)) as connection:
                connection.execute(
                    "CREATE VIEW main.native_references AS SELECT 'legacy' AS reference"
                )
                connection.execute(
                    "CREATE TABLE work_journal (record_id VARCHAR PRIMARY KEY, "
                    "position BIGINT NOT NULL, author VARCHAR NOT NULL, "
                    "local_date VARCHAR NOT NULL, event JSON NOT NULL)"
                )
                connection.execute(
                    "INSERT INTO work_journal VALUES ('saved', 1, 'operator', '2026-11-22', '{}')"
                )
            projection = root / "beta.duckdb"
            with _server(
                projection,
                "--project-root",
                str(root),
                "--journal-storage",
                "duckdb",
            ) as client:
                for _ in range(2):
                    admitted = client.put(
                        "/generation", json=_native_generation()
                    )
                    self.assertEqual(200, admitted.status_code, admitted.text)
                    self.assert_native_rows(client)
                journal = _query(client, "SELECT record_id FROM work_journal")
                self.assertEqual(200, journal.status_code, journal.text)
                self.assertEqual([["saved"]], journal.json()["result"]["rows"])
            migrated = root / ".anechoic_runtime/db/project.duckdb"
            with duckdb.connect(str(migrated), read_only=True) as connection:
                self.assertEqual(
                    [("legacy",)],
                    connection.execute(
                        "SELECT * FROM native_references"
                    ).fetchall(),
                )

    def assert_native_rows(self, client):
        for table in (
            "mrt_atom_references",
            "mrt_native_references",
            "native_references",
        ):
            revisions = _query(
                client,
                f"SELECT stable_ref, exact_ref FROM {table} ORDER BY exact_ref",
            )
            self.assertEqual(
                [[None, "AN-T-1@1"], ["AN-T-1", "AN-T-1@2"]],
                revisions.json()["result"]["rows"],
            )
        for table in (
            "mrt_atom_graph_relations",
            "mrt_relations",
            "relations",
        ):
            edges = _query(
                client,
                f"SELECT source_ref, target_ref, relation_type FROM {table}",
            )
            self.assertEqual(
                [["AN-T-1", "C00", "CONTAINED_BY"]],
                edges.json()["result"]["rows"],
            )
        graph = _query(
            client,
            """
            FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference)
                COLUMNS (s.ref AS source, t.ref AS target))
        """,
        )
        self.assertEqual(200, graph.status_code, graph.text)
        self.assertEqual([["AN-T-1", "C00"]], graph.json()["result"]["rows"])


class NativeSchemaTest(NativeSchemaCases, unittest.TestCase):
    pass


class StagedNativeAtomsTest(StagedNativeAtomsCases, unittest.TestCase):
    pass
