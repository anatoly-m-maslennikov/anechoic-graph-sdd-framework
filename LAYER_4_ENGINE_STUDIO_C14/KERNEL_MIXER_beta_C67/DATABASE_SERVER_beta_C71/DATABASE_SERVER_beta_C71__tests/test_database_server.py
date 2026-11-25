"""Exercise generation admission and read-only SQL through the real socket."""

from copy import deepcopy
from hashlib import sha256
import json
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


class DatabaseServerTest(unittest.TestCase):
    def test_atomic_generation_and_read_only_query(self):
        with _server() as client:
            self.assertFalse(client.get("/health").json()["result"]["ready"])
            self.assertEqual(_query(client, "SELECT * FROM atoms").status_code, 409)
            self.assertEqual(client.get("/model", params=BINDING).status_code, 409)
            payload = _generation()
            generation = self.admit(client, payload)
            self.assertTrue(client.get("/health").json()["result"]["ready"])
            self.assert_equal_artifacts(client, payload, generation)
            self.assert_rollbacks(client, payload, generation)
            self.assert_read_only_query(client)
            run = _query(client, 'SELECT "content.summary" FROM atoms', page_size=1)
            query_id = run.json()["result"]["query_id"]
            payload["snapshot"]["atoms"][0]["summary"] = "second"
            next_generation = self.admit(client, payload)
            self.assertNotEqual(next_generation, generation)
            self.assert_equal_artifacts(client, payload, next_generation)
            self.assertEqual([["one", "second"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])
            page = client.post("/database", json={**BINDING, "query_id": query_id, "offset": 0, "page_size": 1})
            self.assertEqual([["first"]], page.json()["result"]["rows"])

    def test_graph_admission_rollback_and_refresh(self):
        with _server() as client:
            payload = _generation()
            graph = {"nodes": [["p", "package", "python", "pkg", "ok", None, None],
                               ["test", "package", "python", "tests", "ok", None, "Test Package"],
                               ["m", "module", "python", "pkg/m.py", "ok", "p", None],
                               ["python:external:thirdparty", "external", "python", None, None, None, None]],
                     "occurrences": [["o", "m", "python:external:thirdparty", "thirdparty", 1, 0, "external", False]],
                     "edges": [["m", "python:external:thirdparty", "o", False]],
                     "test_edges": [["test", "p"], ["test", "C00"]], "read_issues": [["bad.py", "unreadable"]]}
            def set_graph(value):
                payload["graph"] = value
                payload["receipt"]["graph_sha256"] = sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            set_graph(graph)
            generation = self.admit(client, payload)
            self.assertEqual([], _query(client, "SELECT * FROM state_effect_findings").json()["result"]["rows"])
            self.assertEqual([["Test Package"]], _query(client, "SELECT package_type FROM import_nodes WHERE node_key = 'test'").json()["result"]["rows"])
            self.assertEqual([["pkg", "python", "thirdparty", 1, 0]], _query(client, "SELECT * FROM package_external_imports").json()["result"]["rows"])
            self.assertEqual([["C00", "test"], ["p", "test"]],
                             _query(client, "SELECT * FROM tested_by_edges ORDER BY source_key").json()["result"]["rows"])
            self.assert_property_graph(client)
            generation = self.assert_state_projection(client, payload, graph, set_graph)
            bad = deepcopy(graph)
            bad["read_issues"].append(["bad.py", "duplicate"])
            set_graph(bad)
            payload["snapshot"]["atoms"][0]["summary"] = "changed"
            self.assertEqual(400, client.put("/generation", json=payload).status_code)
            self.assertEqual([["one", "first"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])
            self.assertEqual([["bad.py", "unreadable"]], _query(client, "SELECT * FROM import_read_issues").json()["result"]["rows"])
            self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
            self.assert_property_graph(client)
            set_graph(None)
            self.assertNotEqual(generation, self.admit(client, payload))
            self.assertEqual(400, _query(client, "SELECT * FROM import_nodes").status_code)
            self.assertEqual(400, _query(client, "SELECT * FROM state_effect_findings").status_code)

    def assert_state_projection(self, client, payload, graph, set_graph):
        graph["state_effect_findings"] = [["m", "pkg/m.py", "python", "run", 1, None,
                                            "unresolved", False, "[]", "[]", "no Lean"]]
        set_graph(graph)
        self.assertEqual(400, client.put("/generation", json=payload).status_code)
        graph["nodes"][2][0] = "module:pkg/m.py"
        graph["occurrences"][0][1] = "module:pkg/m.py"
        graph["edges"][0][0] = "module:pkg/m.py"
        graph["state_effect_findings"][0][0] = "module:pkg/m.py"
        event = {"kind": "write", "target": "ambient", "name": "cache", "line": 2}
        graph["state_effect_findings"].append(["module:pkg/m.py", "pkg/m.py", "python", "write", 2,
                                               "{}", "hasEffects", False, json.dumps([event]),
                                               json.dumps([{"index": 0, **event}]), None])
        set_graph(graph)
        generation = self.admit(client, payload)
        self.assertEqual([["hasEffects", False], ["unresolved", False]], _query(client, "SELECT status, dead_end FROM state_effect_findings ORDER BY status").json()["result"]["rows"])
        invalid_state = deepcopy(graph)
        invalid_state["state_effect_findings"][0][8] = "not JSON"
        set_graph(invalid_state)
        self.assertEqual(400, client.put("/generation", json=payload).status_code)
        self.assertEqual([[2]], _query(client, "SELECT count(*) FROM state_effect_findings").json()["result"]["rows"])
        graph["nodes"].append(["module:pkg/callee.py", "module", "python", "pkg/callee.py", "ok", "p", None])
        propagated = {**event, "sourcePath": "pkg/callee.py"}
        graph["state_effect_findings"][1][8:10] = [json.dumps([propagated]), json.dumps([{"index": 0, **propagated}])]
        set_graph(graph)
        generation = self.admit(client, payload)
        stored = _query(client, "SELECT events, violations FROM state_effect_findings WHERE status = 'hasEffects'").json()["result"]["rows"][0]
        self.assertEqual([propagated], json.loads(stored[0]))
        self.assertEqual([{"index": 0, **propagated}], json.loads(stored[1]))
        for invalid_event, invalid_violation in (
            ({**propagated, "sourcePath": "pkg/missing.py"}, {"index": 0, **propagated, "sourcePath": "pkg/missing.py"}),
            (propagated, {"index": 0, **event}),
            ({**propagated, "sourcePath": ""}, {"index": 0, **propagated, "sourcePath": ""}),
        ):
            invalid_state = deepcopy(graph)
            invalid_state["state_effect_findings"][1][8:10] = [json.dumps([invalid_event]), json.dumps([invalid_violation])]
            set_graph(invalid_state)
            self.assertEqual(400, client.put("/generation", json=payload).status_code)
            self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
        return generation

    def assert_property_graph(self, client):
        for label, target, target_key, expected in (
            ("TESTS", "ImportNode", "node_key", "p"),
            ("TESTS_COMPONENT", "Reference", "ref", "C00"),
        ):
            response = _query(client, f"""
                FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:{label}]->(t:{target})
                    COLUMNS (s.node_key AS source, t.{target_key} AS target))
            """)
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual([["test", expected]], response.json()["result"]["rows"])

    def admit(self, client, payload):
        response = client.put("/generation", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def assert_equal_artifacts(self, client, payload, generation):
        for name in ("model", "structure"):
            response = client.get("/" + name, params=BINDING)
            if name == "structure":
                self.assertEqual(json.loads(payload[name]), response.json())
            else:
                self.assertEqual(payload[name].encode(), response.content)
            self.assertEqual(generation, response.headers["x-anechoic-generation"])

    def assert_rollbacks(self, client, payload, generation):
        duplicate = deepcopy(payload)
        duplicate["snapshot"]["atoms"] *= 2
        changed = deepcopy(payload)
        changed["receipt"]["structure_sha256"] = "c" * 64
        for invalid, status in ((duplicate, 400), (changed, 400), ({**payload, "instance_id": "other"}, 403)):
            self.assertEqual(status, client.put("/generation", json=invalid).status_code)
            self.assert_equal_artifacts(client, payload, generation)
            self.assertEqual([["one", "first"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])

    def assert_read_only_query(self, client):
        for sql in ("DELETE FROM atoms", "SELECT 1; SELECT 2",
                    "SELECT * FROM read_csv('/etc/passwd')", "SELECT * FROM range(1001)"):
            self.assertEqual(400, _query(client, sql).status_code)
        self.assertEqual(403, _query(client, "SELECT 1", instance_id="other").status_code)
        self.assertEqual(400, _query(client, "SELECT 1", extra=True).status_code)


if __name__ == "__main__":
    unittest.main()
