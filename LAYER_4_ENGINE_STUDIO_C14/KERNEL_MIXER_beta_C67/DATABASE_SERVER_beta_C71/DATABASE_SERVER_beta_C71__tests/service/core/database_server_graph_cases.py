"""Graph admission and rollback cases for database server tests."""

from copy import deepcopy
from hashlib import sha256
import json

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    _generation,
    _query,
    _server,
)


def _initial_findings():
    return [
        [
            "m",
            "pkg/m.py",
            "python",
            "run",
            1,
            None,
            "unresolved",
            False,
            "[]",
            "[]",
            "no Lean",
        ]
    ]


def _graph_fixture():
    return {
        "nodes": [
            ["p", "package", "python", "pkg", "ok", None, None],
            [
                "test",
                "package",
                "python",
                "tests",
                "ok",
                None,
                "Test Package",
            ],
            ["m", "module", "python", "pkg/m.py", "ok", "p", None],
            [
                "python:external:thirdparty",
                "external",
                "python",
                None,
                None,
                None,
                None,
            ],
        ],
        "occurrences": [
            [
                "o",
                "m",
                "python:external:thirdparty",
                "thirdparty",
                1,
                0,
                "external",
                False,
            ]
        ],
        "edges": [["m", "python:external:thirdparty", "o", False]],
        "test_edges": [["test", "p"], ["test", "C00"]],
        "read_issues": [["bad.py", "unreadable"]],
    }


class DatabaseServerGraphCases:
    def test_graph_admission_rollback_and_refresh(self):
        with _server() as client:
            payload = _generation()
            graph = _graph_fixture()

            def set_graph(value):
                payload["graph"] = value
                payload["receipt"]["graph_sha256"] = sha256(
                    json.dumps(
                        value,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                ).hexdigest()

            set_graph(graph)
            generation = self.admit(client, payload)
            self._assert_initial_graph(client)
            generation = self.assert_state_projection(
                client, payload, graph, set_graph
            )
            self._assert_graph_rollback(
                client, payload, graph, set_graph, generation
            )

    def _assert_graph_rollback(
        self, client, payload, graph, set_graph, generation
    ):
        bad = deepcopy(graph)
        bad["read_issues"].append(["bad.py", "duplicate"])
        set_graph(bad)
        payload["snapshot"]["atoms"][0]["summary"] = "changed"
        self.assertEqual(
            400, client.put("/generation", json=payload).status_code
        )
        self.assertEqual(
            [["one", "first"]],
            _query(client, "SELECT * FROM atoms").json()["result"]["rows"],
        )
        self.assertEqual(
            [["bad.py", "unreadable"]],
            _query(client, "SELECT * FROM import_read_issues").json()[
                "result"
            ]["rows"],
        )
        self.assertEqual(
            generation,
            client.get("/health").json()["result"]["generation"],
        )
        self.assert_property_graph(client)
        set_graph(None)
        self.assertNotEqual(generation, self.admit(client, payload))
        self.assertEqual(
            400, _query(client, "SELECT * FROM import_nodes").status_code
        )
        self.assertEqual(
            400,
            _query(client, "SELECT * FROM state_effect_findings").status_code,
        )

    def _assert_initial_graph(self, client):
        self.assertEqual(
            [],
            _query(client, "SELECT * FROM state_effect_findings").json()[
                "result"
            ]["rows"],
        )
        self.assertEqual(
            [["Test Package"]],
            _query(
                client,
                (
                    "SELECT package_type FROM import_nodes WHERE node_key = "
                    "'test'"
                ),
            ).json()["result"]["rows"],
        )
        self.assertEqual(
            [["pkg", "python", "thirdparty", 1, 0]],
            _query(client, "SELECT * FROM package_external_imports").json()[
                "result"
            ]["rows"],
        )
        self.assertEqual(
            [["C00", "test"], ["p", "test"]],
            _query(
                client, "SELECT * FROM tested_by_edges ORDER BY source_key"
            ).json()["result"]["rows"],
        )
        self.assert_property_graph(client)

    def _prepare_findings(self, client, payload, graph, set_graph):
        graph["state_effect_findings"] = _initial_findings()
        set_graph(graph)
        self.assertEqual(
            400, client.put("/generation", json=payload).status_code
        )
        graph["nodes"][2][0] = "module:pkg/m.py"
        graph["occurrences"][0][1] = "module:pkg/m.py"
        graph["edges"][0][0] = "module:pkg/m.py"
        graph["state_effect_findings"][0][0] = "module:pkg/m.py"
        event = {
            "kind": "write",
            "target": "ambient",
            "name": "cache",
            "line": 2,
        }
        graph["state_effect_findings"].append(
            [
                "module:pkg/m.py",
                "pkg/m.py",
                "python",
                "write",
                2,
                "{}",
                "hasEffects",
                False,
                json.dumps([event]),
                json.dumps([{"index": 0, **event}]),
                None,
            ]
        )
        return event

    def assert_state_projection(self, client, payload, graph, set_graph):
        event = self._prepare_findings(client, payload, graph, set_graph)
        set_graph(graph)
        self.admit(client, payload)
        self.assertEqual(
            [["hasEffects", False], ["unresolved", False]],
            _query(
                client,
                (
                    "SELECT status, dead_end FROM state_effect_findings "
                    "ORDER BY status"
                ),
            ).json()["result"]["rows"],
        )
        invalid_state = deepcopy(graph)
        invalid_state["state_effect_findings"][0][8] = "not JSON"
        set_graph(invalid_state)
        self.assertEqual(
            400, client.put("/generation", json=payload).status_code
        )
        self.assertEqual(
            [[2]],
            _query(
                client, "SELECT count(*) FROM state_effect_findings"
            ).json()["result"]["rows"],
        )
        return self._assert_propagation(
            client, payload, graph, set_graph, event
        )

    def _assert_propagation(self, client, payload, graph, set_graph, event):
        graph["nodes"].append(
            [
                "module:pkg/callee.py",
                "module",
                "python",
                "pkg/callee.py",
                "ok",
                "p",
                None,
            ]
        )
        propagated = {**event, "sourcePath": "pkg/callee.py"}
        graph["state_effect_findings"][1][8:10] = [
            json.dumps([propagated]),
            json.dumps([{"index": 0, **propagated}]),
        ]
        set_graph(graph)
        generation = self.admit(client, payload)
        stored = _query(
            client,
            (
                "SELECT events, violations FROM state_effect_findings WHERE "
                "status = 'hasEffects'"
            ),
        ).json()["result"]["rows"][0]
        self.assertEqual([propagated], json.loads(stored[0]))
        self.assertEqual([{"index": 0, **propagated}], json.loads(stored[1]))
        self._assert_invalid_propagation(
            client, payload, graph, set_graph, event, propagated, generation
        )
        return generation

    def _assert_invalid_propagation(
        self, client, payload, graph, set_graph, event, propagated, generation
    ):
        for invalid_event, invalid_violation in (
            (
                {**propagated, "sourcePath": "pkg/missing.py"},
                {"index": 0, **propagated, "sourcePath": "pkg/missing.py"},
            ),
            (propagated, {"index": 0, **event}),
            (
                {**propagated, "sourcePath": ""},
                {"index": 0, **propagated, "sourcePath": ""},
            ),
        ):
            invalid_state = deepcopy(graph)
            invalid_state["state_effect_findings"][1][8:10] = [
                json.dumps([invalid_event]),
                json.dumps([invalid_violation]),
            ]
            set_graph(invalid_state)
            self.assertEqual(
                400, client.put("/generation", json=payload).status_code
            )
            self.assertEqual(
                generation,
                client.get("/health").json()["result"]["generation"],
            )

    def assert_property_graph(self, client):
        for label, target, target_key, expected in (
            ("TESTS", "ImportNode", "node_key", "p"),
            ("TESTS_COMPONENT", "Reference", "ref", "C00"),
        ):
            response = _query(
                client,
                f"""
                FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:{label}]->(t:{target})
                    COLUMNS (s.node_key AS source, t.{target_key} AS target))
            """,
            )
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                [["test", expected]], response.json()["result"]["rows"]
            )
