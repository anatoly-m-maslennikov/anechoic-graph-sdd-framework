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

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _query, _server
from .test_native_atoms import _digest, _native_generation
from ..DATABASE_SERVER_beta_C71__shared import create_app


def base_generation():
    data = _native_generation()
    model = json.loads(data["model"])
    model["bindings"]["endpoints"]["IS_CONTAINED_BY"] = [{"inverse_alias": "CONTAINS"}, False]
    data["model"] = json.dumps(model)
    data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
    data["snapshot"]["relations"].append({"source_kind": "Component", "source_ref": "C00", "target_kind": "Atom",
                                          "target_ref": "AN-T-1", "relation_type": "CONTAINS", "derived": True})
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    return data


def delta(base, paths, atoms, relations):
    snapshot = {"schema_version": 2, "manifest_sha256": PIN, "atoms": atoms, "relations": relations,
                "relation_types": ["IS_CONTAINED_BY", "CONTAINS"]}
    return BINDING | {"base_generation": base, "paths": paths, "snapshot": snapshot,
                      "snapshot_sha256": _digest({"paths": paths, "snapshot": snapshot})}


def edges(reference, target="C00"):
    return [{"source_kind": "Atom", "source_ref": reference, "target_kind": "Component", "target_ref": target,
             "relation_type": "IS_CONTAINED_BY", "derived": False},
            {"source_kind": "Component", "source_ref": target, "target_kind": "Atom", "target_ref": reference,
             "relation_type": "CONTAINS", "derived": True}]


class NativeDeltaTest(unittest.TestCase):
    def send(self, client, payload):
        response = client.put("/generation/native-delta", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

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
            graph = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:IS_CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source)) SELECT count(*)")
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
        result = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:IS_CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source)) ORDER BY source")
        self.assertEqual(200, result.status_code, result.text)
        self.assertEqual([[value] for value in expected], result.json()["result"]["rows"])

    def test_refuses_stale_digest_non_ticket_and_bad_inverse(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            atom = deepcopy(data["snapshot"]["atoms"][0])
            key = [atom["relative_path"], atom["filename"]]
            valid = delta(base, [key], [atom], edges("AN-T-1"))
            for payload, status in ((valid | {"base_generation": "stale"}, 409),
                                    (valid | {"snapshot_sha256": "0" * 64}, 400),
                                    (delta(base, [[".", "not-ticket.md"]], [], []), 400),
                                    (delta(base, [key], [atom], edges("AN-T-1")[:1]), 409)):
                response = client.put("/generation/native-delta", json=payload)
                self.assertEqual(status, response.status_code, response.text)
                self.assertEqual(base, client.get("/health").json()["result"]["generation"])
            self.assert_graph(client, ["AN-T-1"])

    def test_incoming_relations_and_vertices_survive_owner_delete(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            other = original | {"reference": "AN-T-2", "exact_ref": "AN-T-2@1", "version": 1,
                                "filename": "AN-T-2-TASK.md"}
            direct = {"source_kind": "Atom", "source_ref": "AN-T-2", "target_kind": "Atom", "target_ref": "AN-T-1",
                      "relation_type": "IS_CONTAINED_BY", "derived": False}
            inverse = {"source_kind": "Atom", "source_ref": "AN-T-1", "target_kind": "Atom", "target_ref": "AN-T-2",
                       "relation_type": "CONTAINS", "derived": True}
            key = [other["relative_path"], other["filename"]]
            base = self.send(client, delta(base, [key], [other], [direct, inverse]))
            original_key = [original["relative_path"], original["filename"]]
            self.send(client, delta(base, [original_key], [], []))
            graph = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:IS_CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source, t.ref AS target))")
            self.assertEqual([["AN-T-2", "AN-T-1"]], graph.json()["result"]["rows"])
            self.assertEqual([[2]], _query(client, "SELECT count(*) FROM main.relations").json()["result"]["rows"])
