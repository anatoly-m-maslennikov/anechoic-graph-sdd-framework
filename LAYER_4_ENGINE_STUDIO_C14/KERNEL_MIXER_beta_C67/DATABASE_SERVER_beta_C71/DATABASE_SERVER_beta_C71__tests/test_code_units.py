"""Exercise code unit admission, graph traversal, and persistence."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


class CodeUnitsTest(unittest.TestCase):
    def test_admission_replacement_and_reopen(self):
        with TemporaryDirectory(dir='/tmp') as directory:
            path = Path(directory).resolve() / 'projection.duckdb'
            payload = _generation()
            graph = {
                "nodes": [
                    ["p", "package", "python", "pkg", "ok", None, None],
                    ["m", "module", "python", "pkg/m.py", "ok", "p", None],
                ],
                "occurrences": [],
                "edges": [],
                "test_edges": [],
                "read_issues": [],
                "code_units": [
                    ["a", "m", "function", "a", 1, 0],
                    ["b", "m", "method", "C.b", 2, 4],
                    ["c", "m", "class", "C", 2, 0],
                ],
                "code_unit_calls": [["a", "b", 3, 2]],
            }

            def admit(client, value):
                payload['graph'] = value
                payload['receipt']['graph_sha256'] = sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                return client.put('/generation', json=payload)

            with _server(path) as client:
                response = admit(client, graph)
                self.assertEqual(200, response.status_code, response.text)
                schema = client.get('/schema', params=BINDING)
                self.assertEqual(200, schema.status_code, schema.text)
                self.assertIn('code_units', schema.json()['result']['tables'])
                self.assertIn('code_unit_calls', schema.json()['result']['tables'])
                self.assert_graph(client)
                for bad in self.invalid_graphs(graph):
                    self.assertEqual(400, admit(client, bad).status_code)
                self.assert_graph(client)
            with _server(path) as client:
                self.assert_graph(client)
                replacement = deepcopy(graph)
                replacement['code_units'] = []
                replacement['code_unit_calls'] = []
                self.assertEqual(200, admit(client, replacement).status_code)
                self.assertEqual([[0]], _query(client, 'SELECT count(*) FROM code_units').json()['result']['rows'])
                self.assertEqual(200, admit(client, None).status_code)
                self.assertEqual(400, _query(client, 'SELECT * FROM code_units').status_code)

    def invalid_graphs(self, graph):
        for key in ("code_units", "code_unit_calls"):
            yield {name: rows for name, rows in graph.items() if name != key}
        for row in (
            ["a", "m", "function", "a", 1, 0],
            ["d", "p", "function", "d", 1, 0],
            ["d", "m", "function", "d", 0, 0],
            ["d", "m", "function", "d", 1, -1],
        ):
            yield graph | {"code_units": [*graph["code_units"], row]}
        for row in (
            ["a", "c", 1, 0],
            ["a", "missing", 1, 0],
            ["a", "b", 0, 0],
            ["a", "b", 1, -1],
            ["a", "b", 3, 2],
        ):
            yield graph | {"code_unit_calls": [*graph["code_unit_calls"], row]}

    def assert_graph(self, client):
        for pattern, columns, expected in (
            (
                "(m:ImportNode)-[e:ModuleIncludes]->(u:CodeUnit)",
                "m.node_key AS m, u.node_key AS u",
                [["m", "a"], ["m", "b"], ["m", "c"]],
            ),
            (
                "(a:CodeUnit)-[e:Calls]->(b:CodeUnit)",
                "a.node_key AS a, b.node_key AS b",
                [["a", "b"]],
            ),
        ):
            response = _query(
                client,
                (
                    'FROM GRAPH_TABLE (anechoic MATCH '
                    f'{pattern}'
                    ' COLUMNS ('
                    f'{columns}'
                    ')) ORDER BY 1, 2'
                ),
            )
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(expected, response.json()["result"]["rows"])
