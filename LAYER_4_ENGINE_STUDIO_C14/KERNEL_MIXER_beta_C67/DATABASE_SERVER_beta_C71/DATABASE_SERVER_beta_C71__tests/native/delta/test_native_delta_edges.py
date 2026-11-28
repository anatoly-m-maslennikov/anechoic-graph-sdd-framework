"""Check native delta rejection and incoming relation retention."""

from copy import deepcopy
import unittest

from ...DATABASE_SERVER_beta_C71__tests__shared import _query, _server
from . import test_native_delta as native_delta

base_generation = native_delta.base_generation
delta = native_delta.delta
edges = native_delta.edges


class NativeDeltaEdgesTest(unittest.TestCase):
    send = native_delta.NativeDeltaTest.send
    assert_graph = native_delta.NativeDeltaTest.assert_graph

    def test_refuses_stale_digest_non_ticket_and_bad_inverse(self):
        with _server() as client:
            data = base_generation()
            response = client.put("/generation", json=data)
            base = response.json()["result"]["generation"]
            atom = deepcopy(data["snapshot"]["atoms"][0])
            key = [atom["relative_path"], atom["filename"]]
            valid = delta(base, [key], [atom], edges("AN-T-1"))
            for payload, status in (
                (valid | {"base_generation": "stale"}, 409),
                (valid | {"snapshot_sha256": "0" * 64}, 400),
                (delta(base, [[".", "not-ticket.md"]], [], []), 400),
                (delta(base, [key], [atom], edges("AN-T-1")[:1]), 409),
            ):
                response = client.put("/generation/native-delta", json=payload)
                self.assertEqual(status, response.status_code, response.text)
                self.assertEqual(
                    base, client.get("/health").json()["result"]["generation"]
                )
            self.assert_graph(client, ["AN-T-1"])

    def test_incoming_relations_and_vertices_survive_owner_delete(self):
        with _server() as client:
            data = base_generation()
            response = client.put("/generation", json=data)
            base = response.json()["result"]["generation"]
            original = data["snapshot"]["atoms"][0]
            other = original | {
                "reference": "AN-T-2",
                "exact_ref": "AN-T-2@1",
                "version": 1,
                "filename": "AN-T-2-TASK.md",
            }
            direct = {
                "source_kind": "Atom",
                "source_ref": "AN-T-2",
                "target_kind": "Atom",
                "target_ref": "AN-T-1",
                "relation_type": "CONTAINED_BY",
                "derived": False,
            }
            inverse = {
                "source_kind": "Atom",
                "source_ref": "AN-T-1",
                "target_kind": "Atom",
                "target_ref": "AN-T-2",
                "relation_type": "CONTAINS",
                "derived": True,
            }
            key = [other["relative_path"], other["filename"]]
            payload = delta(base, [key], [other], [direct, inverse])
            base = self.send(client, payload)
            original_key = [original["relative_path"], original["filename"]]
            self.send(client, delta(base, [original_key], [], []))
            graph = _query(
                client,
                "FROM GRAPH_TABLE (anechoic MATCH "
                "(s:Reference)-[e:CONTAINED_BY]->(t:Reference) "
                "COLUMNS (s.ref AS source, t.ref AS target))",
            )
            rows = graph.json()["result"]["rows"]
            self.assertEqual([["AN-T-2", "AN-T-1"]], rows)
            relations = _query(client, "SELECT count(*) FROM main.relations")
            self.assertEqual([[2]], relations.json()["result"]["rows"])
