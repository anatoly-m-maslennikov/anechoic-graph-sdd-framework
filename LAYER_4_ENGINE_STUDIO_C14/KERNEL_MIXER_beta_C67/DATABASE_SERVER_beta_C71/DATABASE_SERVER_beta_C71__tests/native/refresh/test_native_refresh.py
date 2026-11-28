"""Conditional native refresh retains the accepted non-native projection."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)
from ..atoms.test_native_atoms import _digest, _native_generation


from .native_refresh_cases_1 import NativeRefreshCases
from .native_refresh_cases_2 import PendingGraphCases


def request(base, snapshot):
    return BINDING | {
        "base_generation": base,
        "snapshot": snapshot,
        "snapshot_sha256": _digest(snapshot),
    }


def graph_payload():
    data = _native_generation()
    graph = {
        "nodes": [
            [
                "module:pkg/a.py",
                "module",
                "python",
                "pkg/a.py",
                "ok",
                None,
                None,
            ]
        ],
        "occurrences": [],
        "edges": [],
        "test_edges": [],
        "read_issues": [],
        "code_access_findings": [
            ["module:pkg/a.py", "pkg/a.py", 1, 0, "pkg.b", "denied", "reason"]
        ],
    }
    data["graph"] = graph
    data["receipt"]["graph_sha256"] = sha256(
        json.dumps(
            graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    return data


class NativeRefreshTest(NativeRefreshCases, unittest.TestCase):
    def test_native_refresh_keeps_artifacts_and_graph_across_restart(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            with _server(database) as client:
                self.assertEqual(
                    409,
                    client.put(
                        "/generation/native", json=request("missing", {})
                    ).status_code,
                )
                data = graph_payload()
                initial = client.put("/generation", json=data)
                self.assertEqual(200, initial.status_code, initial.text)
                base = initial.json()["result"]["generation"]
                artifacts = [
                    client.get(path, params=BINDING).content
                    for path in ("/model", "/structure")
                ]
                snapshot = deepcopy(data["snapshot"])
                snapshot["atoms"][0].update(
                    status="done", version=3, exact_ref="AN-T-1@3"
                )
                updated = client.put(
                    "/generation/native", json=request(base, snapshot)
                )
                self.assertEqual(200, updated.status_code, updated.text)
                generation = updated.json()["result"]["generation"]
                self.assertNotEqual(base, generation)
                self.assertEqual(
                    artifacts,
                    [
                        client.get(path, params=BINDING).content
                        for path in ("/model", "/structure")
                    ],
                )
                self.assert_current(client, generation)
                self.assert_refused(client, base, generation, snapshot)
            self.assert_restart_current(
                database, generation, artifacts, snapshot
            )

    def assert_restart_current(
        self, database, generation, artifacts, snapshot
    ):
        with _server(database) as client:
            self.assert_current(client, generation)
            self.assertEqual(
                artifacts,
                [
                    client.get(path, params=BINDING).content
                    for path in ("/model", "/structure")
                ],
            )
            again = client.put(
                "/generation/native", json=request(generation, snapshot)
            )
            self.assertEqual(200, again.status_code, again.text)

    def assert_current(self, client, generation):
        self.assertEqual(
            generation, client.get("/health").json()["result"]["generation"]
        )
        rows = _query(
            client,
            (
                'SELECT "header.state.status", "header.state.version" FROM '
                "atoms WHERE reference = 'AN-T-1'"
            ),
        )
        self.assertEqual([["done", 3]], rows.json()["result"]["rows"])
        findings = _query(
            client, "SELECT source_key, status FROM code_access_findings"
        )
        self.assertEqual(
            [["module:pkg/a.py", "denied"]], findings.json()["result"]["rows"]
        )
        graph = _query(
            client,
            (
                "FROM GRAPH_TABLE (anechoic MATCH "
                "(s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s."
                "ref AS source, t.ref AS target))"
            ),
        )
        self.assertEqual([["AN-T-1", "C00"]], graph.json()["result"]["rows"])

    def assert_refused(self, client, base, generation, snapshot):
        stale = client.put("/generation/native", json=request(base, snapshot))
        self.assertEqual(
            (409, "generation_base_changed"),
            (stale.status_code, stale.json()["error"]["code"]),
        )
        bad_digest = request(generation, snapshot) | {
            "snapshot_sha256": "0" * 64
        }
        self.assertEqual(
            400, client.put("/generation/native", json=bad_digest).status_code
        )
        bad_types = deepcopy(snapshot)
        bad_types["relation_types"] = ["CONTAINED_BY"]
        self.assertEqual(
            400,
            client.put(
                "/generation/native", json=request(generation, bad_types)
            ).status_code,
        )
        foreign = request(generation, snapshot) | {"instance_id": "foreign"}
        self.assertEqual(
            403, client.put("/generation/native", json=foreign).status_code
        )
        self.assert_current(client, generation)

    def test_native_refresh_replaces_graph_atomically_and_persists(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "projection.duckdb"
            with _server(database) as client:
                data = graph_payload()
                base = client.put("/generation", json=data).json()["result"][
                    "generation"
                ]
                artifacts = [
                    client.get(path, params=BINDING).content
                    for path in ("/model", "/structure")
                ]
                graph = deepcopy(data["graph"])
                graph["code_access_findings"][0][5] = "uncertain"
                payload = request(base, data["snapshot"]) | {
                    "graph": graph,
                    "graph_sha256": _digest(graph),
                }
                self.assert_invalid_graphs(client, payload, base, data, graph)
                updated = client.put("/generation/native", json=payload)
                self.assertEqual(200, updated.status_code, updated.text)
                generation = updated.json()["result"]["generation"]
                self.assertEqual(
                    409,
                    client.put("/generation/native", json=payload).status_code,
                )
                self.assertEqual(
                    artifacts,
                    [
                        client.get(path, params=BINDING).content
                        for path in ("/model", "/structure")
                    ],
                )
                self.assertEqual(
                    [["uncertain"]],
                    _query(
                        client, "SELECT status FROM code_access_findings"
                    ).json()["result"]["rows"],
                )
                self.assert_graph_relation(client)
            self.assert_graph_restart(database, generation, artifacts)

    def assert_graph_relation(self, client):
        self.assertEqual(
            [["AN-T-1", "C00"]],
            _query(
                client,
                (
                    "FROM GRAPH_TABLE (anechoic MATCH "
                    "(s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS "
                    "(s.ref AS source, t.ref AS target))"
                ),
            ).json()["result"]["rows"],
        )

    def assert_graph_restart(self, database, generation, artifacts):
        with _server(database) as client:
            self.assertEqual(
                generation,
                client.get("/health").json()["result"]["generation"],
            )
            self.assertEqual(
                artifacts,
                [
                    client.get(path, params=BINDING).content
                    for path in ("/model", "/structure")
                ],
            )
            self.assertEqual(
                [["uncertain"]],
                _query(
                    client, "SELECT status FROM code_access_findings"
                ).json()["result"]["rows"],
            )

    def assert_invalid_graphs(self, client, payload, base, data, graph):
        self.assertEqual(
            400,
            client.put(
                "/generation/native",
                json=payload | {"graph_sha256": "0" * 64},
            ).status_code,
        )
        self.assertEqual(
            400,
            client.put(
                "/generation/native",
                json=payload | {"graph_sha256": None},
            ).status_code,
        )
        self.assertEqual(
            400,
            client.put(
                "/generation/native",
                json=payload | {"graph": None, "graph_sha256": _digest(None)},
            ).status_code,
        )
        self.assertEqual(
            400,
            client.put(
                "/generation/native",
                json=request(base, data["snapshot"]) | {"graph": graph},
            ).status_code,
        )
        bad_graph = deepcopy(graph)
        bad_graph["test_edges"] = [["missing", "C00"]]
        self.assertEqual(
            400,
            client.put(
                "/generation/native",
                json=payload
                | {
                    "graph": bad_graph,
                    "graph_sha256": _digest(bad_graph),
                },
            ).status_code,
        )

    def test_legacy_base_is_refused_and_absent_graph_stays_absent(self):
        with _server() as client:
            legacy = client.put("/generation", json=_generation())
            base = legacy.json()["result"]["generation"]
            native = _native_generation()
            refused = client.put(
                "/generation/native", json=request(base, native["snapshot"])
            )
            self.assertEqual(
                (409, "generation_base_changed"),
                (refused.status_code, refused.json()["error"]["code"]),
            )
            admitted = client.put("/generation", json=native)
            base = admitted.json()["result"]["generation"]
            updated = client.put(
                "/generation/native", json=request(base, native["snapshot"])
            )
            self.assertEqual(200, updated.status_code, updated.text)
            self.assertEqual(
                400, _query(client, "SELECT * FROM import_nodes").status_code
            )


class PendingGraphTest(PendingGraphCases, unittest.TestCase):
    pass
