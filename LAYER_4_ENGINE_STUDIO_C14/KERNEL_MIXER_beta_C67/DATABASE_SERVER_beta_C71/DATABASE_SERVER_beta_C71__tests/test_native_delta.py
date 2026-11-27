"""Apply bounded native Ticket deltas without rebuilding the property graph."""

import asyncio
from copy import deepcopy
from hashlib import sha256
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb
import httpx2
from starlette.testclient import TestClient

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _query, _server
from .test_native_atoms import _digest, _native_generation
from ..DATABASE_SERVER_beta_C71__shared import create_app


def base_generation():
    data = _native_generation()
    model = json.loads(data["model"])
    model["bindings"]["endpoints"]["CONTAINED_BY"] = [{"inverse_alias": "CONTAINS"}, False]
    data["model"] = json.dumps(model)
    data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
    data["snapshot"]["relations"].append({"source_kind": "Component", "source_ref": "C00", "target_kind": "Atom",
                                          "target_ref": "AN-T-1", "relation_type": "CONTAINS", "derived": True})
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    return data


def delta(base, paths, atoms, relations):
    snapshot = {"schema_version": 2, "manifest_sha256": PIN, "atoms": atoms, "relations": relations,
                "relation_types": ["CONTAINED_BY", "CONTAINS"]}
    return BINDING | {"base_generation": base, "paths": paths, "snapshot": snapshot,
                      "snapshot_sha256": _digest({"paths": paths, "snapshot": snapshot})}


def edges(reference, target="C00"):
    return [{"source_kind": "Atom", "source_ref": reference, "target_kind": "Component", "target_ref": target,
             "relation_type": "CONTAINED_BY", "derived": False},
            {"source_kind": "Component", "source_ref": target, "target_kind": "Atom", "target_ref": reference,
             "relation_type": "CONTAINS", "derived": True}]


class NativeDeltaTest(unittest.TestCase):
    def send(self, client, payload):
        response = client.put("/generation/native-delta", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def test_model_status_domain_rejects_full_and_delta(self):
        data = base_generation()
        model = json.loads(data["model"])
        prefix = "Node//Artifact//Atom//"
        model["bindings"]["declarations"] = [
            [name, {"kind": "entity", "arguments": {"entity_name": "Status", "entity_kind": "Property", "relation_name": "IS_PROPERTY_OF",
                                  "base_path": "Node//Artifact//Atom.Header.State",
                                  "applies_to_entity_classes": [prefix + name], "allowed_values": values}}]
            for name, values in (("Spec Atom", ["draft", "active", "archived"]),
                                 ("Ticket Atom", ["draft", "done", "archived"]),
                                 ("Project Config Atom", ["draft", "active", "archived"]))
        ]
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
        with _server() as client:
            refused = client.put("/generation", json=data)
            self.assertEqual(400, refused.status_code, refused.text)
            data["snapshot"]["atoms"][0]["status"] = "done"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            base = admitted.json()["result"]["generation"]
            atom = data["snapshot"]["atoms"][0] | {"status": "active"}
            path = [atom["relative_path"], atom["filename"]]
            refused = client.put("/generation/native-delta", json=delta(base, [path], [atom], edges(atom["reference"])))
            self.assertEqual(400, refused.status_code, refused.text)
            rows = _query(client, "SELECT \"header.state.status\" FROM mrt_atoms WHERE reference = 'AN-T-1'")
            self.assertEqual([["done"]], rows.json()["result"]["rows"])

    def test_canonical_model_project_config_status_domain(self):
        data = base_generation()
        model = json.loads(data["model"])
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        model["bindings"]["declarations"] = [
            [name, {"kind": "entity", "arguments": {"entity_name": "Status", "entity_kind": "Property",
              "relation_name": "IS_PROPERTY_OF", "base_path": root + ".Header.State",
              "applies_to_entity_classes": [root + "//" + name], "allowed_values": values}}]
            for name, values in (("Specification", ["draft", "active", "archived"]),
                                 ("Ticket", ["draft", "active", "archived"]),
                                 ("project_config", ["draft", "active", "reviewed", "archived"]))
        ]
        source = data["snapshot"]["atoms"][0]
        data["snapshot"]["atoms"].append(source | {
            "reference": "AN-C-7", "exact_ref": "AN-C-7@1", "filename": "AN-C-7.md",
            "version": 1, "status": "reviewed", "status_group": "Current"})
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        with _server() as client:
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            data["snapshot"]["atoms"][-1]["status"] = "unknown"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = client.put("/generation", json=data)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Invalid native Atom Status", refused.json()["error"]["message"])

    def test_partial_and_invalid_family_status_bindings_fail(self):
        args = {"entity_name": "Status", "entity_kind": "Property", "relation_name": "IS_PROPERTY_OF",
                "base_path": "Node//Artifact//Atom.Header.State", "allowed_values": ["active"],
                "applies_to_entity_classes": ["Node//Artifact//Atom//Ticket Atom"]}
        data = base_generation()
        model = json.loads(data["model"])

        def submit(client):
            model["bindings"]["declarations"] = [["subject", {"arguments": args}]]
            data["model"] = json.dumps(model)
            data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
            return client.put("/generation", json=data)

        with duckdb.connect() as connection, TestClient(create_app(connection, "instance", PIN)) as client:
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Incomplete", refused.json()["error"]["message"])
            args["allowed_values"] = []
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Invalid scoped", refused.json()["error"]["message"])
            args["applies_to_entity_classes"] = ["Node//Artifact//Atom//Ticket Atom//Task"]
            data["snapshot"]["atoms"].append(data["snapshot"]["atoms"][0])
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Duplicate native Atom", refused.json()["error"]["message"])
            data["snapshot"]["atoms"][0]["status"] = "not-a-status"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Invalid native Atom Status", refused.json()["error"]["message"])

    def test_warning_only_delta_is_atomic_and_does_not_clear_unrelated_issues(self):
        path = ["tickets", "AN-T-99--new.md"]
        relative = "/".join(path)
        warning = {"relative_path": relative, "code": "parse_error", "message": "Malformed Atom",
                   "atom_ref": None, "related_paths": []}
        with _server() as client:
            base = client.put("/generation", json=base_generation()).json()["result"]["generation"]
            payload = delta(base, [path], [], [])
            payload["snapshot"]["ingestion_issues"] = [warning]
            payload["snapshot_sha256"] = _digest({"paths": payload["paths"], "snapshot": payload["snapshot"]})
            refused = client.put("/generation/native-delta", json=payload | {"snapshot_sha256": "invalid"})
            self.assertEqual(400, refused.status_code, refused.text)
            issue_sql = "SELECT relative_path, code FROM ops_ingestion_issues"
            self.assertEqual([], _query(client, issue_sql).json()["result"]["rows"])
            admitted = self.send(client, payload)
            self.assertNotEqual(base, admitted)
            unrelated = ["tickets", "AN-T-100--unrelated.md"]
            self.assertEqual(admitted, self.send(client, delta(admitted, [unrelated], [], [])))
            self.assertEqual([[relative, "parse_error"]], _query(client, issue_sql).json()["result"]["rows"])
            self.assertNotEqual(admitted, self.send(client, delta(admitted, [path], [], [])))
            self.assertEqual([], _query(client, issue_sql).json()["result"]["rows"])

    def test_create_edit_rename_delete_and_duplicate_collision(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            created = original | {"reference": "AN-T-2", "exact_ref": "AN-T-2@1", "version": 1,
                                  "filename": "AN-T-2-TASK.md", "summary": "created"}
            key = [created["relative_path"], created["filename"]]
            base = self.send(client, delta(base, [key], [created], edges("AN-T-2") * 2))
            self.assertEqual([[2]], _query(client, "SELECT count(*) FROM main.relations WHERE source_ref='AN-T-2'").json()["result"]["rows"])
            self.assert_graph(client, ["AN-T-1", "AN-T-2"])
            edited = created | {"status": "done", "version": 2, "exact_ref": "AN-T-2@2", "summary": "edited"}
            base = self.send(client, delta(base, [key], [edited], edges("AN-T-2")))
            self.assertEqual([["done", 2]], _query(client, 'SELECT "header.state.status", "header.state.version" FROM atoms WHERE reference=\'AN-T-2\'').json()["result"]["rows"])
            other = edited | {"relative_path": "moved"}
            new_key = ["moved", edited["filename"]]
            collision = client.put("/generation/native-delta", json=delta(base, [new_key], [other], edges("AN-T-2")))
            self.assertEqual(409, collision.status_code, collision.text)
            self.assertEqual("delta_full_reconciliation", collision.json()["error"]["code"])
            self.assertEqual(base, client.get("/health").json()["result"]["generation"])
            base = self.send(client, delta(base, [key, new_key], [other], edges("AN-T-2")))
            self.assertEqual(base, self.send(client, delta(base, [key], [], [])))
            self.assertEqual([["moved"]], _query(client, "SELECT relative_path FROM atoms WHERE reference='AN-T-2'").json()["result"]["rows"])
            base = self.send(client, delta(base, [new_key], [], []))
            self.assertEqual([[0]], _query(client, "SELECT count(*) FROM atoms WHERE reference='AN-T-2'").json()["result"]["rows"])
            self.assert_graph(client, ["AN-T-1"])
            self.assertEqual(base, client.get("/health").json()["result"]["generation"])

    def test_lifecycle_lenses_follow_delta_and_legacy_availability(self):
        with _server() as client:
            data = base_generation()
            spec = data["snapshot"]["atoms"][0] | {
                "reference": "AN-S-2", "exact_ref": "AN-S-2@1", "version": 1,
                "filename": "AN-S-2-DES.md"}
            data["snapshot"]["atoms"].append(spec)
            data["snapshot"]["lifecycle_lenses"] = [["AN-S-2", "SPEC/TEST"]]
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            base = client.put("/generation", json=data).json()["result"]["generation"]
            key = [spec["relative_path"], spec["filename"]]
            payload = delta(base, [key], [spec], [])
            payload["snapshot"]["lifecycle_lenses"] = [["AN-S-2", "SPEC/NEW"]]
            payload["snapshot_sha256"] = _digest({"paths": payload["paths"], "snapshot": payload["snapshot"]})
            bad = deepcopy(payload)
            bad["snapshot"]["lifecycle_lenses"] = [["AN-T-1", "SPEC"]]
            bad["snapshot_sha256"] = _digest({"paths": bad["paths"], "snapshot": bad["snapshot"]})
            self.assertEqual(400, client.put("/generation/native-delta", json=bad).status_code)
            self.assertEqual([["AN-S-2", "SPEC/TEST"]], _query(client, "SELECT * FROM lifecycle_lenses").json()["result"]["rows"])
            base = self.send(client, payload)
            self.assertEqual([["AN-S-2", "SPEC/NEW"]], _query(client, "SELECT * FROM lifecycle_lenses").json()["result"]["rows"])
            base = self.send(client, delta(base, [key], [], []))
            tables = _query(client, "SELECT count(*) FROM information_schema.tables WHERE table_name='lifecycle_lenses'")
            self.assertEqual([[0]], tables.json()["result"]["rows"])

    def test_path_limit(self):
        with _server() as client:
            base = client.put("/generation", json=base_generation()).json()["result"]["generation"]
            paths = [[".", f"AN-T-{i}-TASK.md"] for i in range(1, 1026)]
            self.assertEqual(base, self.send(client, delta(base, paths[:1024], [], [])))
            response = client.put("/generation/native-delta", json=delta(base, paths, [], []))
            self.assertEqual(400, response.status_code, response.text)
            self.assertEqual(base, client.get("/health").json()["result"]["generation"])

    def test_bulk_500_rows_and_stale_base(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            atoms = [original | {"reference": f"AN-T-{i}", "exact_ref": f"AN-T-{i}@1", "version": 1,
                                 "filename": f"AN-T-{i}-TASK.md", "summary": f"ticket {i}"}
                     for i in range(2, 502)]
            paths = [[a["relative_path"], a["filename"]] for a in atoms]
            relations = [edge for atom in atoms for edge in edges(atom["reference"])]
            payload = delta(base, paths, atoms, relations)
            new_base = self.send(client, payload)
            self.assertEqual(409, client.put("/generation/native-delta", json=payload).status_code)
            self.assertEqual([[1002]], _query(client, "SELECT count(*) FROM main.relations").json()["result"]["rows"])
            sql = _query(client, "SELECT count(*), count(DISTINCT reference) FROM atoms")
            self.assertEqual([[502, 502]], sql.json()["result"]["rows"])
            graph = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source)) SELECT count(*)")
            self.assertEqual([[501]], graph.json()["result"]["rows"])
            self.send(client, delta(new_base, paths, [], []))
            self.assertEqual([[2]], _query(client, "SELECT count(*) FROM atoms").json()["result"]["rows"])
            self.assert_graph(client, ["AN-T-1"])

    def test_failed_write_rolls_back(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db.duckdb"
            data = base_generation()
            with _server(path) as client:
                base = client.put("/generation", json=data).json()["result"]["generation"]
            atom = data["snapshot"]["atoms"][0]
            key = [atom["relative_path"], atom["filename"]]
            with duckdb.connect(str(path)) as connection:
                app = create_app(connection, BINDING["instance_id"], PIN)
                route = next(r for r in app.routes if r.path == "/generation/native-delta")
                async def exercise():
                    async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://test") as client:
                        with patch.dict(route.endpoint.__globals__, {"_write_graph": unittest.mock.Mock(side_effect=duckdb.Error("injected failure"))}):
                            response = await client.put("/generation/native-delta", json=delta(base, [key], [], []))
                        self.assertEqual(400, response.status_code, response.text)
                        self.assertEqual(base, connection.execute("SELECT id FROM generation").fetchone()[0])
                        self.assertEqual(2, connection.execute("SELECT count(*) FROM atoms").fetchone()[0])
                        self.assertEqual(2, connection.execute("SELECT count(*) FROM relations").fetchone()[0])
                        response = await client.put("/generation/native-delta", json=delta(base, [key], [atom], edges("AN-T-1")))
                        self.assertEqual(200, response.status_code, response.text)
                asyncio.run(exercise())

    def test_native_carrier_families_add_update_remove(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            for family in "SPC":
                ref = f"AN-{family}-2"
                atom = original | {"reference": ref, "exact_ref": f"{ref}@1", "version": 1,
                                   "filename": f"{ref}-DES.md", "status": "active"}
                key = [atom["relative_path"], atom["filename"]]
                base = self.send(client, delta(base, [key], [atom], edges(ref)))
                edited = atom | {"version": 2, "exact_ref": f"{ref}@2", "summary": "edited"}
                base = self.send(client, delta(base, [key], [edited], edges(ref)))
                rows = _query(client, f"SELECT \"header.state.version\" FROM atoms WHERE reference='{ref}'")
                self.assertEqual([[2]], rows.json()["result"]["rows"])
                base = self.send(client, delta(base, [key], [], []))
                rows = _query(client, f"SELECT count(*) FROM atoms WHERE reference='{ref}'")
                self.assertEqual([[0]], rows.json()["result"]["rows"])
            self.assert_graph(client, ["AN-T-1"])

    def test_native_path_rejects_mismatched_identity_and_revision(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            for filename in ("AN-P-3-DES.md", "AN-S-2@2-DES.md", "AN-X-2-DES.md"):
                atom = original | {"reference": "AN-S-2", "exact_ref": "AN-S-2@1", "version": 1,
                                   "filename": filename, "status": "active"}
                key = [atom["relative_path"], filename]
                response = client.put("/generation/native-delta", json=delta(base, [key], [atom], []))
                self.assertEqual(400, response.status_code, response.text)
                self.assertEqual(base, client.get("/health").json()["result"]["generation"])

    def assert_graph(self, client, expected):
        result = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source)) ORDER BY source")
        self.assertEqual(200, result.status_code, result.text)
        self.assertEqual([[value] for value in expected], result.json()["result"]["rows"])
