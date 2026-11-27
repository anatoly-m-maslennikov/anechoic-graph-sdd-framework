"""Admit a native revision snapshot and its property graph through the server socket."""

import json
import unittest
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _generation, _query, _server


def _digest(value):
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


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
    archived = atom | {"reference": "AN-T-1@1", "exact_ref": "AN-T-1@1", "status_group": "Archived",
                      "status": "archived", "version": 1, "filename": "AN-T-1@1-TASK.md", "summary": "first"}
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
        issue = {"relative_path": "_anechoic_anechoic/AN-T-1-TASK.md", "code": "undeclared_relation",
                 "message": "Undeclared native relation: UNKNOWN", "atom_ref": "AN-T-1@2", "related_paths": []}
        with _server() as client:
            for row, status, message in (
                (issue, 200, None),
                (issue | {"atom_ref": "AN-T-1@1"}, 400, "Undeclared relation issue must match an admitted Atom"),
                (issue | {"code": "invalid_value"}, 400, "Invalid carrier cannot have an admitted Atom"),
            ):
                with self.subTest(row=row):
                    data["snapshot"]["ingestion_issues"] = [row]
                    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
                    response = client.put("/generation", json=data)
                    self.assertEqual(status, response.status_code, response.text)
                    if message is not None:
                        self.assertEqual(message, response.json()["error"]["message"])
            self.assert_native_rows(client)
            rows = client.get("/ingestion/issues", params=BINDING).json()["result"]["rows"]
            self.assertEqual([{"source": "atom", **issue}], rows)

    def test_strict_records_preserve_payload_and_error_order(self):
        original = _native_generation()
        with _server() as client:
            self.assertEqual(200, client.put("/generation", json=original).status_code)
            for collection, field, value, message in (
                ("atoms", "version", True, "Invalid native Atom fields"),
                ("atoms", "extra", 1, "Invalid native Atom fields"),
                ("relations", "derived", 0, "Invalid native relation"),
                ("relations", "extra", 1, "Invalid native relation"),
            ):
                invalid = deepcopy(original)
                invalid["snapshot"][collection][0][field] = value
                invalid["receipt"]["snapshot_sha256"] = _digest(invalid["snapshot"])
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
                invalid["receipt"]["snapshot_sha256"] = _digest(invalid["snapshot"])
                response = client.put("/generation", json=invalid)
                self.assertEqual(400, response.status_code, response.text)
                self.assertIn(message, response.text)
            invalid = deepcopy(original)
            invalid["snapshot"]["atoms"][0]["exact_ref"] = "invalid"
            invalid["snapshot"]["atoms"][1]["version"] = True
            invalid["receipt"]["snapshot_sha256"] = _digest(invalid["snapshot"])
            response = client.put("/generation", json=invalid)
            self.assertIn("Invalid native Atom identity", response.text)
            self.assert_native_rows(client)

    def test_upgrade_restart_and_refusal_preserve_generation(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "projection.duckdb"
            with _server(path) as client:
                self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            with duckdb.connect(str(path)) as connection:
                connection.execute("CREATE VIEW main.native_references AS SELECT 'legacy' AS reference")
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
                self.assertEqual(400, client.put("/generation", json=_generation()).status_code)
                self.assert_native_rows(client)
            with _server(path) as client:
                self.assert_native_rows(client)

    def test_generation_with_migrated_current_journal_view(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            legacy = root / ".anechoic_runtime/workbench/projection.duckdb"
            legacy.parent.mkdir(parents=True)
            with duckdb.connect(str(legacy)) as connection:
                connection.execute("CREATE VIEW main.native_references AS SELECT 'legacy' AS reference")
                connection.execute("CREATE TABLE work_journal (record_id VARCHAR PRIMARY KEY, "
                                   "position BIGINT NOT NULL, author VARCHAR NOT NULL, "
                                   "local_date VARCHAR NOT NULL, event JSON NOT NULL)")
                connection.execute("INSERT INTO work_journal VALUES ('saved', 1, 'operator', '2026-11-22', '{}')")
            projection = root / "beta.duckdb"
            with _server(projection, "--project-root", str(root), "--journal-storage", "duckdb") as client:
                for _ in range(2):
                    admitted = client.put("/generation", json=_native_generation())
                    self.assertEqual(200, admitted.status_code, admitted.text)
                    self.assert_native_rows(client)
                journal = _query(client, "SELECT record_id FROM work_journal")
                self.assertEqual(200, journal.status_code, journal.text)
                self.assertEqual([["saved"]], journal.json()["result"]["rows"])
            migrated = root / ".anechoic_runtime/db/project.duckdb"
            with duckdb.connect(str(migrated), read_only=True) as connection:
                self.assertEqual([("legacy",)], connection.execute("SELECT * FROM native_references").fetchall())

    def assert_native_rows(self, client):
        for table in ("mrt_atom_references", "mrt_native_references", "native_references"):
            revisions = _query(client, f"SELECT stable_ref, exact_ref FROM {table} ORDER BY exact_ref")
            self.assertEqual([[None, "AN-T-1@1"], ["AN-T-1", "AN-T-1@2"]], revisions.json()["result"]["rows"])
        for table in ("mrt_atom_graph_relations", "mrt_relations", "relations"):
            edges = _query(client, f"SELECT source_ref, target_ref, relation_type FROM {table}")
            self.assertEqual([["AN-T-1", "C00", "CONTAINED_BY"]], edges.json()["result"]["rows"])
        graph = _query(client, """
            FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference)
                COLUMNS (s.ref AS source, t.ref AS target))
        """)
        self.assertEqual(200, graph.status_code, graph.text)
        self.assertEqual([["AN-T-1", "C00"]], graph.json()["result"]["rows"])


class NativeSchemaTest(unittest.TestCase):
    def test_atom_family_views_publish_each_family_and_its_statuses(self):
        native = _native_generation()
        source = native["snapshot"]["atoms"][0]
        for reference, status, group in (("AN-S-2", "active", "Current"), ("AN-P-3", "active", "Current"),
                                         ("AN-C-4@1-draft", "draft", "Draft")):
            atom_id = reference.split("@")[0]
            native["snapshot"]["atoms"].append(source | {
                "reference": reference, "exact_ref": reference if group == "Draft" else f"{atom_id}@1",
                "version": 1, "status_group": group, "status": status, "filename": f"{atom_id}.md",
            })
        native["receipt"]["snapshot_sha256"] = _digest(native["snapshot"])
        expected = {
            "mrt_spec_atoms": ([["AN-S-2"]], ["active"]),
            "mrt_ticket_atoms": (
                [["AN-T-1"], ["AN-T-1@1"]],
                ["active", "archived"],
            ),
            "mrt_project_config_atoms": (
                [["AN-C-4@1-draft"], ["AN-P-3"]],
                ["active", "draft"],
            ),
        }
        with _server() as client:
            response = client.put("/generation", json=native)
            self.assertEqual(200, response.status_code, response.text)
            tables = client.get(
                "/schema", params={"instance_id": "instance"}
            ).json()["result"]["tables"]
            for table, (rows, values) in expected.items():
                with self.subTest(table=table):
                    self.assertEqual(rows, _query(client, f"SELECT reference FROM {table} ORDER BY 1").json()["result"]["rows"])
                    status = next(column for column in tables[table] if column["name"] == "header.state.status")
                    self.assertEqual(values, status["values"])

    def test_schema_hints_follow_admitted_generation_without_query_history(
        self,
    ):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with _server(None, "--project-root", str(root)) as client:
                self.assertEqual(
                    409,
                    client.get(
                        "/schema", params={"instance_id": "instance"}
                    ).status_code,
                )
                self.assertEqual(
                    403,
                    client.get(
                        "/schema", params={"instance_id": "other"}
                    ).status_code,
                )
                native = _native_generation()
                self.assertEqual(
                    200, client.put("/generation", json=native).status_code
                )
                self.assert_values(client, ["active", "archived"])
                native["snapshot"]["atoms"][0]["status"] = "done"
                native["receipt"]["snapshot_sha256"] = _digest(
                    native["snapshot"]
                )
                self.assertEqual(
                    200, client.put("/generation", json=native).status_code
                )
                self.assert_values(client, ["archived", "done"])
                history = client.post(
                    "/workspace",
                    json={
                        "instance_id": "instance",
                        "operation": "query_log_list",
                        "arguments": {},
                    },
                )
                self.assertEqual(200, history.status_code, history.text)
                self.assertEqual([], history.json()["result"]["items"])

    def assert_values(self, client, expected):
        result = client.get("/schema", params={"instance_id": "instance"})
        self.assertEqual(200, result.status_code, result.text)
        tables = result.json()["result"]["tables"]
        self.assertIn("native_references", tables)
        self.assertNotIn("generation", tables)
        status = next(
            column
            for column in tables["atoms"]
            if column["name"] == "header.state.status"
        )
        self.assertEqual(expected, status["values"])

class StagedNativeAtomsTest(unittest.TestCase):
    def test_mixed_order_empty_revisions_and_atomic_refusal(self):
        data = _native_generation()
        current, archived = data["snapshot"]["atoms"]
        draft = archived | {
            "reference": "AN-T-2@1-draft",
            "exact_ref": "AN-T-2@1-draft",
            "status_group": "Draft",
            "status": "draft",
            "filename": "draft.md",
        }
        data["snapshot"]["atoms"] = [
            current,
            dict(reversed(list(draft.items()))),
            archived,
        ]
        data["snapshot"]["relations"] = []
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        sql = "SELECT stable_ref, exact_ref FROM mrt_atom_references ORDER BY reference"
        expected = [
            ["AN-T-1", "AN-T-1@2"],
            [None, "AN-T-1@1"],
            [None, "AN-T-2@1-draft"],
        ]
        with _server() as client:
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertEqual(
                expected, _query(client, sql).json()["result"]["rows"]
            )
            invalid = deepcopy(data)
            invalid["snapshot"]["atoms"].append(current)
            invalid["receipt"]["snapshot_sha256"] = _digest(
                invalid["snapshot"]
            )
            self.assertEqual(
                400, client.put("/generation", json=invalid).status_code
            )
            self.assertEqual(
                expected, _query(client, sql).json()["result"]["rows"]
            )
            data["snapshot"]["atoms"] = []
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            empty = client.put("/generation", json=data)
            self.assertEqual(200, empty.status_code, empty.text)
            self.assertEqual([], _query(client, sql).json()["result"]["rows"])
