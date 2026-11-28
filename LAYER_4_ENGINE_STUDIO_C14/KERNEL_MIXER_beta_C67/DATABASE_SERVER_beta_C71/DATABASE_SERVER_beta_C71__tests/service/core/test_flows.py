"""Observed flows and causal snapshots through the private socket."""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


def snapshot():
    return {
        **BINDING,
        "run_id": "a" * 32,
        "component": "C71",
        "action": "serve",
        "events": [
            {
                "kind": "input",
                "name": "request",
                "at": 1,
                "causes": [],
                "target": None,
                "outcome": None,
                "detail": {},
            },
            {
                "kind": "trigger",
                "name": "start",
                "at": 2.5,
                "causes": [0],
                "target": None,
                "outcome": None,
                "detail": {"ok": True},
            },
        ],
    }


class FlowsTest(unittest.TestCase):
    def test_projection_admission_and_restart(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db.duckdb"
            generation = _generation()
            self.assert_initial_projection(path, generation)
            self.assert_updated_projection(path, generation)
            self.assert_retained_projection(path)

    def assert_initial_projection(self, path, generation):
        with _server(path) as client:
            self.assertEqual(
                200,
                client.post("/flow/events", json=snapshot()).status_code,
            )
            self.assertEqual(
                200, client.put("/generation", json=generation).status_code
            )
            old = _query(
                client,
                "SELECT component, action, unit_name FROM component_flows",
            )
            self.assertEqual(
                [["C71", "serve", None]], old.json()["result"]["rows"]
            )

    def assert_updated_projection(self, path, generation):
        with _server(path) as client:
            self.assert_flow_schema(client)
            data = self.assert_invalid_snapshots(client)
            data["run_id"] = "b" * 32
            data["events"][1]["name"] = "resume"
            data["events"][1]["detail"]["unit"] = {
                "path": "server.py",
                "name": "serve",
            }
            data["events"].extend(
                [
                    {
                        "kind": "effect",
                        "name": "write",
                        "at": 3,
                        "causes": [1],
                        "target": "store",
                        "outcome": "ok",
                        "detail": {},
                    },
                    {
                        "kind": "output",
                        "name": "response",
                        "at": 4,
                        "causes": [2],
                        "target": None,
                        "outcome": "ok",
                        "detail": {},
                    },
                ]
            )
            self.assertEqual(
                200, client.post("/flow/events", json=data).status_code
            )
            self.assertEqual(
                200, client.put("/generation", json=generation).status_code
            )
            rows = _query(
                client,
                "SELECT component, action, trigger_names, run_count FROM flow_overlap_candidates",
            ).json()["result"]["rows"]
            self.assertEqual([["C71", "serve", ["resume", "start"], 2]], rows)

    def assert_flow_schema(self, client):
        schema = client.get("/schema", params=BINDING).json()["result"][
            "tables"
        ]
        self.assertTrue(
            {
                "mrt_flow_actions",
                "src_flow_events",
                "mrt_flow_overlap_candidates",
                "mrt_flow_similar_actions",
            }
            <= set(schema)
        )
        self.assertTrue(
            {
                "component_flows",
                "flow_events",
                "flow_overlap_candidates",
                "flow_similar_actions",
            }
            <= set(schema)
        )

    def assert_retained_projection(self, path):
        with _server(path) as client:
            rows = _query(client, "SELECT count(*) FROM flow_events").json()[
                "result"
            ]["rows"]
            self.assertEqual([[6]], rows)
            observed = _query(
                client,
                """SELECT component, action, unit_path, unit_name,
                json_extract_string(inputs, '$[0]'), json_extract_string(triggers, '$.start[0]'),
                json_extract_string(triggers, '$.resume[0]'), json_extract_string(outputs, '$[0]'),
                json_extract_string(effects, '$[0]') FROM mrt_flow_actions""",
            )
            self.assertEqual(200, observed.status_code, observed.text)
            self.assertEqual(
                [
                    [
                        "C71",
                        "serve",
                        "server.py",
                        "serve",
                        "request",
                        "request",
                        "request",
                        "response",
                        "write",
                    ]
                ],
                observed.json()["result"]["rows"],
            )
            self.assertEqual(
                [["C71", "serve"]],
                _query(
                    client,
                    "SELECT component, action FROM mrt_component_flows",
                ).json()["result"]["rows"],
            )

    def assert_invalid_snapshots(self, client):
        data = snapshot()
        self.assertEqual(
            400, client.post("/flow/events", json=data).status_code
        )
        bad = deepcopy(data)
        bad["run_id"] = "b" * 32
        bad["events"][1]["causes"] = [1]
        self.assertEqual(
            400, client.post("/flow/events", json=bad).status_code
        )
        for field, value in [
            ("at", True),
            ("causes", [True]),
            ("detail", []),
            ("kind", "other"),
        ]:
            invalid = deepcopy(data)
            invalid["run_id"] = "c" * 32
            invalid["events"][1][field] = value
            self.assertEqual(
                400, client.post("/flow/events", json=invalid).status_code
            )
        self.assertEqual(
            [[2]],
            _query(client, "SELECT count(*) FROM flow_events").json()[
                "result"
            ]["rows"],
        )
        bad["events"] = bad["events"] * 257
        self.assertEqual(
            400, client.post("/flow/events", json=bad).status_code
        )
        self.assertEqual(
            400,
            client.post(
                "/flow/events", content=b" " * (1024 * 1024 + 1)
            ).status_code,
        )
        return data

    def test_similar_actions_keep_effect_order_and_count(self):
        with _server() as client:
            self.assertEqual(
                200, client.put("/generation", json=_generation()).status_code
            )
            for key, action, kinds in [
                ("a", "first", ["effect", "output"]),
                ("b", "second", ["effect", "output"]),
                ("c", "reordered", ["output", "effect"]),
                ("d", "repeated", ["effect", "effect", "output"]),
                ("e", "truncated", ["effect", "output"]),
            ]:
                events = [
                    {
                        "kind": kind,
                        "name": kind,
                        "at": i,
                        "causes": [i - 1] if i else [],
                        "target": None,
                        "outcome": None,
                        "detail": {"omitted_events": 1}
                        if key == "e" and kind == "output"
                        else {},
                    }
                    for i, kind in enumerate(kinds)
                ]
                response = client.post(
                    "/flow/events",
                    json={
                        **BINDING,
                        "run_id": key * 32,
                        "component": "C71",
                        "action": action,
                        "events": events,
                    },
                )
                self.assertEqual(200, response.status_code, response.text)
            result = _query(
                client,
                "SELECT list_transform(actions, lambda a: a.action) FROM flow_similar_actions",
            )
            self.assertEqual(200, result.status_code, result.text)
            self.assertEqual(
                [[["first", "second"]]], result.json()["result"]["rows"]
            )
