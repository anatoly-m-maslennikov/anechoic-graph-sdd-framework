"""Check bounded native edge updates against a full graph rebuild."""

import unittest
from copy import deepcopy

from .DATABASE_SERVER_beta_C71__tests__shared import _query, _server
from .test_native_atoms import _digest
from .test_native_delta import base_generation, delta, edges


class NativeDeltaParityTest(unittest.TestCase):
    def test_duplicate_edge_counts_match_full_rebuild(self):
        data = base_generation()
        atom = data["snapshot"]["atoms"][0]
        other = atom | {"reference": "AN-T-2", "exact_ref": "AN-T-2@1", "version": 1,
                        "filename": "AN-T-2-TASK.md"}
        incoming = [
            {"source_kind": "Atom", "source_ref": "AN-T-2", "target_kind": "Atom", "target_ref": "AN-T-1",
             "relation_type": "CONTAINED_BY", "derived": False},
            {"source_kind": "Atom", "source_ref": "AN-T-1", "target_kind": "Atom", "target_ref": "AN-T-2",
             "relation_type": "CONTAINS", "derived": True},
        ]
        data["snapshot"]["atoms"].append(other)
        data["snapshot"]["relations"] = edges("AN-T-1") * 2 + incoming
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        key = [atom["relative_path"], atom["filename"]]

        with _server() as incremental, _server() as rebuilt:
            response = incremental.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            for count in (2, 1, 0):
                if count != 2:
                    response = incremental.put("/generation/native-delta", json=delta(base, [key], [atom], edges("AN-T-1") * count))
                    self.assertEqual(200, response.status_code, response.text)
                    base = response.json()["result"]["generation"]
                full = deepcopy(data)
                full["snapshot"]["relations"] = edges("AN-T-1") * count + incoming
                full["receipt"]["snapshot_sha256"] = _digest(full["snapshot"])
                response = rebuilt.put("/generation", json=full)
                self.assertEqual(200, response.status_code, response.text)
                for sql in (
                    "SELECT * FROM main.relations ORDER BY ALL",
                    "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) "
                    "COLUMNS (s.kind AS sk, s.ref AS sr, t.kind AS tk, t.ref AS tr)) ORDER BY ALL",
                    "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINS]->(t:Reference) "
                    "COLUMNS (s.kind AS sk, s.ref AS sr, t.kind AS tk, t.ref AS tr)) ORDER BY ALL",
                ):
                    actual, expected = _query(incremental, sql), _query(rebuilt, sql)
                    self.assertEqual(200, actual.status_code, actual.text)
                    self.assertEqual(200, expected.status_code, expected.text)
                    self.assertEqual(expected.json()["result"]["rows"], actual.json()["result"]["rows"])
                graph = _query(incremental, "FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref AS source, t.ref AS target)) ORDER BY ALL")
                self.assertEqual([["AN-T-1", "C00"], ["AN-T-2", "AN-T-1"]] if count else
                                 [["AN-T-2", "AN-T-1"]], graph.json()["result"]["rows"])
