import json
import unittest
from copy import deepcopy
from hashlib import sha256

from .DATABASE_SERVER_beta_C71__tests__shared import _query, _server
from .test_native_atoms import _digest, _native_generation


class ImportLabelTest(unittest.TestCase):
    def test_realization_label_skips_empty_native_relation_and_rejects_conflict(self):
        native = _native_generation()
        model = json.loads(native['model'])
        model["bindings"]["endpoints"].update(
            {"IMPORTS": [{}, False], "IMPORTED_BY": [{}, True]}
        )
        native['model'] = json.dumps(model)
        native["receipt"]["model_descriptor_sha256"] = sha256(
            native["model"].encode()
        ).hexdigest()
        native['snapshot']['relation_types'] += ['IMPORTS', 'IMPORTED_BY']
        native['receipt']['snapshot_sha256'] = _digest(native['snapshot'])
        native["graph"] = {
            "nodes": [
                ["a", "module", "python", "a.py", "ok", None, None],
                ["b", "module", "python", "b.py", "ok", None, None],
            ],
            "occurrences": [["o", "a", "b", "b", 1, 0, "resolved", False]],
            "edges": [["a", "b", "o", False]],
            "test_edges": [],
            "read_issues": [],
        }
        native['receipt']['graph_sha256'] = _digest(native['graph'])
        sql = ('FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:Imports]->(t:ImportNode) '
               'COLUMNS (s.node_key AS source, t.node_key AS target))')
        with _server() as client:
            response = client.put("/generation", json=native)
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                [["a", "b"]], _query(client, sql).json()["result"]["rows"]
            )
            conflict = deepcopy(native)
            conflict["snapshot"]["relations"].append(
                conflict["snapshot"]["relations"][0]
                | {"relation_type": "IMPORTS"}
            )
            conflict["receipt"]["snapshot_sha256"] = _digest(
                conflict["snapshot"]
            )
            response = client.put("/generation", json=conflict)
            self.assertEqual(400, response.status_code, response.text)
            self.assertIn("Native IMPORTS relations conflict", response.text)
            self.assertEqual(
                [["a", "b"]], _query(client, sql).json()["result"]["rows"]
            )
