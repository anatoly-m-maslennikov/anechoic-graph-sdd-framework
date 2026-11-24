"""Conditional native refresh retains the accepted non-native projection."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server
from .test_native_atoms import _digest, _native_generation


def request(base, snapshot):
    return BINDING | {"base_generation": base, "snapshot": snapshot, "snapshot_sha256": _digest(snapshot)}


def graph_payload():
    data = _native_generation()
    graph = {"nodes": [["module:pkg/a.py", "module", "python", "pkg/a.py", "ok", None, None]],
             "occurrences": [], "edges": [], "test_edges": [], "read_issues": [],
             "code_access_findings": [["module:pkg/a.py", "pkg/a.py", 1, 0, "pkg.b", "denied", "reason"]]}
    data["graph"] = graph
    data["receipt"]["graph_sha256"] = sha256(json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data


class NativeRefreshTest(unittest.TestCase):
    def test_native_refresh_keeps_artifacts_and_graph_across_restart(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            with _server(database) as client:
                self.assertEqual(409, client.put("/generation/native", json=request("missing", {})).status_code)
                data = graph_payload()
                initial = client.put("/generation", json=data)
                self.assertEqual(200, initial.status_code, initial.text)
                base = initial.json()["result"]["generation"]
                artifacts = [client.get(path, params=BINDING).content for path in ("/model", "/structure")]
                snapshot = deepcopy(data["snapshot"])
                snapshot["atoms"][0].update(status="done", version=3, exact_ref="AN-T-1@3")
                updated = client.put("/generation/native", json=request(base, snapshot))
                self.assertEqual(200, updated.status_code, updated.text)
                generation = updated.json()["result"]["generation"]
                self.assertNotEqual(base, generation)
                self.assertEqual(artifacts, [client.get(path, params=BINDING).content for path in ("/model", "/structure")])
                self.assert_current(client, generation)
                self.assert_refused(client, base, generation, snapshot)
            with _server(database) as client:
                self.assert_current(client, generation)
                self.assertEqual(artifacts, [client.get(path, params=BINDING).content for path in ("/model", "/structure")])
                again = client.put("/generation/native", json=request(generation, snapshot))
                self.assertEqual(200, again.status_code, again.text)

    def assert_current(self, client, generation):
        self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
        rows = _query(client, 'SELECT "header.state.status", "header.state.version" FROM atoms WHERE reference = \'AN-T-1\'')
        self.assertEqual([["done", 3]], rows.json()["result"]["rows"])
        findings = _query(client, "SELECT source_key, status FROM code_access_findings")
        self.assertEqual([["module:pkg/a.py", "denied"]], findings.json()["result"]["rows"])
        graph = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source, t.ref AS target))")
        self.assertEqual([["AN-T-1", "C00"]], graph.json()["result"]["rows"])

    def assert_refused(self, client, base, generation, snapshot):
        stale = client.put("/generation/native", json=request(base, snapshot))
        self.assertEqual((409, "generation_base_changed"), (stale.status_code, stale.json()["error"]["code"]))
        bad_digest = request(generation, snapshot) | {"snapshot_sha256": "0" * 64}
        self.assertEqual(400, client.put("/generation/native", json=bad_digest).status_code)
        bad_types = deepcopy(snapshot)
        bad_types["relation_types"] = ["CONTAINED_BY"]
        self.assertEqual(400, client.put("/generation/native", json=request(generation, bad_types)).status_code)
        foreign = request(generation, snapshot) | {"instance_id": "foreign"}
        self.assertEqual(403, client.put("/generation/native", json=foreign).status_code)
        self.assert_current(client, generation)

    def test_native_refresh_replaces_graph_atomically_and_persists(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            with _server(database) as client:
                data = graph_payload()
                base = client.put("/generation", json=data).json()["result"]["generation"]
                artifacts = [client.get(path, params=BINDING).content for path in ("/model", "/structure")]
                graph = deepcopy(data["graph"])
                graph["code_access_findings"][0][5] = "uncertain"
                payload = request(base, data["snapshot"]) | {"graph": graph, "graph_sha256": _digest(graph)}
                self.assertEqual(400, client.put("/generation/native", json=payload | {"graph_sha256": "0" * 64}).status_code)
                self.assertEqual(400, client.put("/generation/native", json=payload | {"graph_sha256": None}).status_code)
                self.assertEqual(400, client.put("/generation/native", json=payload | {"graph": None, "graph_sha256": _digest(None)}).status_code)
                self.assertEqual(400, client.put("/generation/native", json=request(base, data["snapshot"]) | {"graph": graph}).status_code)
                bad_graph = deepcopy(graph)
                bad_graph["test_edges"] = [["missing", "C00"]]
                self.assertEqual(400, client.put("/generation/native", json=payload | {"graph": bad_graph, "graph_sha256": _digest(bad_graph)}).status_code)
                updated = client.put("/generation/native", json=payload)
                self.assertEqual(200, updated.status_code, updated.text)
                generation = updated.json()["result"]["generation"]
                self.assertEqual(409, client.put("/generation/native", json=payload).status_code)
                self.assertEqual(artifacts, [client.get(path, params=BINDING).content for path in ("/model", "/structure")])
                self.assertEqual([["uncertain"]], _query(client, "SELECT status FROM code_access_findings").json()["result"]["rows"])
                self.assertEqual([["AN-T-1", "C00"]], _query(client, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source, t.ref AS target))").json()["result"]["rows"])
            with _server(database) as client:
                self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
                self.assertEqual(artifacts, [client.get(path, params=BINDING).content for path in ("/model", "/structure")])
                self.assertEqual([["uncertain"]], _query(client, "SELECT status FROM code_access_findings").json()["result"]["rows"])

    def test_reuse_witness_persists_and_tracks_native_generation(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            data = graph_payload()
            endpoints = json.loads(data["model"])["bindings"]["endpoints"]
            witness = {"inputs": {"manifest": "a" * 64, "graph": "b" * 64},
                       "graph_config": {}, "endpoints": endpoints}
            with _server(database) as client:
                self.assertIsNone(client.get("/generation/reuse", params=BINDING).json()["result"])
                self.assertEqual(403, client.get("/generation/reuse", params={"instance_id": "other"}).status_code)
                accepted = client.put("/generation", json=data | {"reuse": witness})
                self.assertEqual(200, accepted.status_code, accepted.text)
                base = accepted.json()["result"]["generation"]
                bad = deepcopy(witness)
                bad["endpoints"] = {}
                refused = client.put("/generation", json=data | {"reuse": bad})
                self.assertEqual(400, refused.status_code, refused.text)
                self.assertEqual({"base_generation": base, **witness}, client.get("/generation/reuse", params=BINDING).json()["result"])
                ordinary = client.put("/generation/native", json=request(base, data["snapshot"]))
                self.assertEqual(200, ordinary.status_code, ordinary.text)
                base = ordinary.json()["result"]["generation"]
                self.assertEqual({"base_generation": base, **witness}, client.get("/generation/reuse", params=BINDING).json()["result"])
            with _server(database) as client:
                self.assertEqual({"base_generation": base, **witness}, client.get("/generation/reuse", params=BINDING).json()["result"])
                payload = request(base, data["snapshot"]) | {"graph": data["graph"], "graph_sha256": _digest(data["graph"])}
                witness["inputs"]["graph"] = "c" * 64
                updated = client.put("/generation/native", json=payload | {"reuse": witness})
                self.assertEqual(200, updated.status_code, updated.text)
                base = updated.json()["result"]["generation"]
                self.assertEqual({"base_generation": base, **witness}, client.get("/generation/reuse", params=BINDING).json()["result"])
                cleared = client.put("/generation/native", json=payload | {"base_generation": base})
                self.assertEqual(200, cleared.status_code, cleared.text)
                self.assertIsNone(client.get("/generation/reuse", params=BINDING).json()["result"])

    def test_carrier_checkpoint_restart_deletion_and_invalidation(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            data = graph_payload()
            endpoints = json.loads(data["model"])["bindings"]["endpoints"]
            witness = {"inputs": {"manifest": "a" * 64, "graph": "b" * 64},
                       "graph_config": {}, "endpoints": endpoints}
            atoms = data["snapshot"]["atoms"]
            hashes = {f'{a["relative_path"]}/{a["filename"]}': "c" * 64 for a in atoms}
            with _server(database) as client:
                bad = client.put("/generation", json=data | {"reuse": witness, "carrier_hashes": {}})
                self.assertEqual(400, bad.status_code, bad.text)
                admitted = client.put("/generation", json=data | {"reuse": witness, "carrier_hashes": hashes})
                self.assertEqual(200, admitted.status_code, admitted.text)
                base = admitted.json()["result"]["generation"]
            with _server(database) as client:
                self.assertEqual(hashes, client.get("/generation/reuse", params=BINDING).json()["result"]["carrier_hashes"])
                archived = atoms[1]
                paths = [[archived["relative_path"], archived["filename"]]]
                snapshot = data["snapshot"] | {"atoms": [], "relations": []}
                delta = {"paths": paths, "snapshot": snapshot, "carrier_hashes": {}}
                payload = BINDING | {"base_generation": base, **delta, "snapshot_sha256": _digest(delta)}
                refused = client.put("/generation/native-delta", json=payload | {"snapshot_sha256": "0" * 64})
                self.assertEqual(400, refused.status_code, refused.text)
                self.assertEqual(hashes, client.get("/generation/reuse", params=BINDING).json()["result"]["carrier_hashes"])
                deleted = client.put("/generation/native-delta", json=payload)
                self.assertEqual(200, deleted.status_code, deleted.text)
                base = deleted.json()["result"]["generation"]
                del hashes[f'{archived["relative_path"]}/{archived["filename"]}']
                self.assertEqual(hashes, client.get("/generation/reuse", params=BINDING).json()["result"]["carrier_hashes"])
                old = {"paths": paths, "snapshot": snapshot}
                legacy = client.put("/generation/native-delta", json=BINDING | {"base_generation": base, **old, "snapshot_sha256": _digest(old)})
                self.assertEqual(200, legacy.status_code, legacy.text)
                self.assertNotIn("carrier_hashes", client.get("/generation/reuse", params=BINDING).json()["result"])

    def test_reuse_proof_includes_persisted_pending_archive(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            data = graph_payload()
            snapshot = data["snapshot"]
            snapshot["atoms"].pop()
            data["receipt"]["snapshot_sha256"] = _digest(snapshot)
            atom = snapshot["atoms"][0]
            hashes = {f'{atom["relative_path"]}/{atom["filename"]}': "c" * 64}
            witness = {"inputs": {"manifest": "a" * 64, "graph": "b" * 64}, "graph_config": {},
                       "endpoints": json.loads(data["model"])["bindings"]["endpoints"]}
            data.update(reuse=witness, carrier_hashes=hashes)
            with _server(database) as client:
                response = client.put("/generation", json=data | {"archive_pending": True})
                self.assertEqual(200, response.status_code, response.text)
                base = response.json()["result"]["generation"]
            with _server(database) as client:
                proof = client.get("/generation/reuse", params=BINDING).json()["result"]
                self.assertEqual({"base_generation": base, **witness, "carrier_hashes": hashes,
                                  "archive_pending": True}, proof)
                response = client.put("/generation", json=data)
                self.assertEqual(200, response.status_code, response.text)
                proof = client.get("/generation/reuse", params=BINDING).json()["result"]
                self.assertEqual({"base_generation": response.json()["result"]["generation"],
                                  **witness, "carrier_hashes": hashes}, proof)

    def test_legacy_base_is_refused_and_absent_graph_stays_absent(self):
        with _server() as client:
            legacy = client.put("/generation", json=_generation())
            base = legacy.json()["result"]["generation"]
            native = _native_generation()
            refused = client.put("/generation/native", json=request(base, native["snapshot"]))
            self.assertEqual((409, "generation_base_changed"), (refused.status_code, refused.json()["error"]["code"]))
            admitted = client.put("/generation", json=native)
            base = admitted.json()["result"]["generation"]
            updated = client.put("/generation/native", json=request(base, native["snapshot"]))
            self.assertEqual(200, updated.status_code, updated.text)
            self.assertEqual(400, _query(client, "SELECT * FROM import_nodes").status_code)
