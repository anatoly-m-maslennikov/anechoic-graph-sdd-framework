"""Validate the optional code-access projection through the Kernel socket."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    _generation,
    _query,
    _server,
)


def bind_graph(payload, graph):
    payload["graph"] = graph
    encoded = json.dumps(
        graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    payload["receipt"]["graph_sha256"] = sha256(encoded.encode()).hexdigest()


def _graph():
    return {
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
    }


class CodeAccessProjectionTest(unittest.TestCase):
    def test_legacy_graph_findings_rollback_and_graph_disabled(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            db = root / "projection.duckdb"
            graph = _graph()
            payload = _generation()
            bind_graph(payload, graph)
            with _server(db) as client:
                self.assertEqual(
                    200, client.put("/generation", json=payload).status_code
                )
                self.assertEqual(
                    [[0]],
                    _query(
                        client, "SELECT count(*) FROM code_access_findings"
                    ).json()["result"]["rows"],
                )
            with _server(db) as client:
                self.assertEqual(
                    [[0]],
                    _query(
                        client, "SELECT count(*) FROM code_access_findings"
                    ).json()["result"]["rows"],
                )
                self.assert_findings_and_refusal(client, payload, graph)
                bind_graph(payload, None)
                self.assertEqual(
                    200, client.put("/generation", json=payload).status_code
                )
                self.assertEqual(
                    400,
                    _query(
                        client, "SELECT * FROM code_access_findings"
                    ).status_code,
                )
                schema = client.get(
                    "/schema", params={"instance_id": "instance"}
                ).json()["result"]["tables"]
                self.assertNotIn("code_access_findings", schema)

    def assert_findings_and_refusal(self, client, payload, graph):
        statuses = [
            "denied",
            "uncertain",
            "declared_bypass",
            "undeclared_bypass",
        ]
        graph["code_access_findings"] = [
            ["module:pkg/a.py", "pkg/a.py", 1, 0, "pkg.b", status, "reason"]
            for status in statuses
        ]
        bind_graph(payload, graph)
        admitted = client.put("/generation", json=payload)
        self.assertEqual(200, admitted.status_code, admitted.text)
        prior_generation = admitted.json()["result"]["generation"]
        rows = _query(
            client,
            (
                'SELECT source_key, relative_path, line, "column", '
                "written_specifier, status, reason FROM code_access_findings "
                "ORDER BY status"
            ),
        )
        self.assertEqual(200, rows.status_code, rows.text)
        self.assertEqual(
            sorted(statuses), [row[5] for row in rows.json()["result"]["rows"]]
        )
        schema = client.get(
            "/schema", params={"instance_id": "instance"}
        ).json()["result"]["tables"]
        self.assertEqual(
            [
                "source_key",
                "relative_path",
                "line",
                "column",
                "written_specifier",
                "status",
                "reason",
            ],
            [column["name"] for column in schema["code_access_findings"]],
        )
        self.assert_invalid_findings(client, payload, graph, prior_generation)

    def assert_invalid_findings(
        self, client, payload, graph, prior_generation
    ):
        for field, value in (
            (5, "allowed"),
            (0, "module:other.py"),
            (1, "other.py"),
            (2, 0),
            (3, -1),
        ):
            bad = deepcopy(graph)
            bad["code_access_findings"][0][field] = value
            bind_graph(payload, bad)
            self.assertEqual(
                400, client.put("/generation", json=payload).status_code
            )
            self.assertEqual(
                prior_generation,
                client.get("/health").json()["result"]["generation"],
            )
            self.assertEqual(
                [[4]],
                _query(
                    client, "SELECT count(*) FROM code_access_findings"
                ).json()["result"]["rows"],
            )
