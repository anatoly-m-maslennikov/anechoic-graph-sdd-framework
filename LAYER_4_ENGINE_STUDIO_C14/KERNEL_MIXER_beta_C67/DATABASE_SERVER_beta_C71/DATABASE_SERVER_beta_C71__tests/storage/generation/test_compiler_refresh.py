"""Compiler refresh preserves state and admits an optional native delta."""

from copy import deepcopy
from hashlib import sha256
import json
import unittest

from starlette.testclient import TestClient

from ....DATABASE_SERVER_beta_C71__shared import create_app, open_database
from ...DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN
from ...native.atoms.test_native_atoms import _digest
from ...native.delta.test_native_delta import base_generation, delta, edges


def request(base, data):
    compiler = {key: data[key] for key in ("model", "structure")}
    compiler["receipt"] = {
        key: data["receipt"][key]
        for key in (
            "manifest_sha256",
            "model_sha256",
            "model_descriptor_sha256",
            "structure_sha256",
        )
    }
    return BINDING | {
        "base_generation": base,
        "compiler": compiler,
        "reuse": {
            "inputs": {"manifest": "a" * 64, "graph": "b" * 64},
            "graph_config": {},
            "endpoints": json.loads(data["model"])["bindings"]["endpoints"],
        },
    }


class CompilerRefreshTest(unittest.TestCase):
    def assert_invalid_delta_preserves_generation(
        self, client, connection, refresh, generation
    ):
        bad = deepcopy(refresh)
        bad["delta"]["snapshot_sha256"] = "0" * 64
        self.assertEqual(
            400, client.put("/generation/compiler", json=bad).status_code
        )
        query = (
            'SELECT "content.summary" FROM mrt_atoms WHERE reference = '
            "'AN-T-1'"
        )
        self.assertEqual("second", connection.execute(query).fetchone()[0])
        late_failure = deepcopy(refresh)
        late_failure["reuse"]["endpoints"] = {}
        self.assertEqual(
            400,
            client.put("/generation/compiler", json=late_failure).status_code,
        )
        self.assertEqual("second", connection.execute(query).fetchone()[0])
        self.assertEqual(
            generation,
            connection.execute("SELECT id FROM ops_generation").fetchone()[0],
        )

    def test_refresh_delta_and_failures_preserve_last_good(self):
        data = base_generation()
        atom = data["snapshot"]["atoms"][0]
        path = atom["relative_path"] + "/" + atom["filename"]
        archive = data["snapshot"]["atoms"][1]
        archive_path = archive["relative_path"] + "/" + archive["filename"]
        data["carrier_hashes"] = {path: "a" * 64, archive_path: "c" * 64}
        with (
            open_database() as connection,
            TestClient(create_app(connection, "instance", PIN)) as client,
        ):
            response = client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            updated, generation = self.assert_initial_refresh(
                client, connection, data, base, path, archive_path
            )
            refresh = self.prepare_delta_refresh(
                client, connection, atom, generation, updated, path
            )
            response = client.put("/generation/compiler", json=refresh)
            self.assertEqual(200, response.status_code, response.text)
            generation = response.json()["result"]["generation"]
            self.assertEqual(
                "changed",
                connection.execute(
                    (
                        'SELECT "content.summary" FROM mrt_atoms WHERE reference = '
                        "'AN-T-1'"
                    )
                ).fetchone()[0],
            )
            self.assertEqual(
                {path: "b" * 64, archive_path: "c" * 64},
                client.get("/generation/reuse", params=BINDING).json()[
                    "result"
                ]["carrier_hashes"],
            )
            self.assert_changed_columns_rejected(
                client, connection, generation, updated
            )

    def assert_changed_columns_rejected(
        self, client, connection, generation, updated
    ):
        connection.execute(
            "ALTER TABLE mrt_atoms ADD COLUMN unexpected VARCHAR"
        )
        rejected = client.put(
            "/generation/compiler", json=request(generation, updated)
        )
        self.assertEqual(
            (409, "model_columns_changed"),
            (rejected.status_code, rejected.json()["error"]["code"]),
        )
        self.assertEqual(
            generation,
            connection.execute("SELECT id FROM ops_generation").fetchone()[0],
        )

    def prepare_delta_refresh(
        self, client, connection, atom, generation, updated, path
    ):
        changed = atom | {
            "summary": "changed",
            "version": 3,
            "exact_ref": "AN-T-1@3",
        }
        part = delta(
            generation,
            [[atom["relative_path"], atom["filename"]]],
            [changed],
            edges("AN-T-1"),
        )
        part["carrier_hashes"] = {path: "b" * 64}
        part["snapshot_sha256"] = _digest(
            {key: part[key] for key in ("paths", "snapshot", "carrier_hashes")}
        )
        refresh = request(generation, updated) | {
            "delta": {
                key: part[key]
                for key in (
                    "paths",
                    "snapshot",
                    "snapshot_sha256",
                    "carrier_hashes",
                )
            }
        }
        self.assert_invalid_delta_preserves_generation(
            client, connection, refresh, generation
        )
        return refresh

    def assert_initial_refresh(
        self, client, connection, data, base, path, archive_path
    ):
        updated = deepcopy(data)
        descriptor = json.loads(updated["model"])
        descriptor["modules"]["another.py"] = "e" * 64
        updated["model"] = json.dumps(descriptor)
        updated["receipt"]["model_descriptor_sha256"] = sha256(
            updated["model"].encode()
        ).hexdigest()
        payload = request(base, updated)
        response = client.put("/generation/compiler", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        generation = response.json()["result"]["generation"]
        self.assertEqual(
            2,
            connection.execute("SELECT count(*) FROM mrt_atoms").fetchone()[0],
        )
        self.assertEqual(
            {path: "a" * 64, archive_path: "c" * 64},
            client.get("/generation/reuse", params=BINDING).json()["result"][
                "carrier_hashes"
            ],
        )
        self.assertEqual(
            updated["model"],
            connection.execute("SELECT model FROM ops_generation").fetchone()[
                0
            ],
        )
        stale = client.put("/generation/compiler", json=payload)
        self.assertEqual(
            (409, "generation_base_changed"),
            (stale.status_code, stale.json()["error"]["code"]),
        )
        return updated, generation

    def test_rejects_incompatible_relations(self):
        data = base_generation()
        with (
            open_database() as connection,
            TestClient(create_app(connection, "instance", PIN)) as client,
        ):
            base = client.put("/generation", json=data).json()["result"][
                "generation"
            ]
            payload = request(base, data)
            model = json.loads(payload["compiler"]["model"])
            del model["bindings"]["endpoints"]["CONTAINED_BY"][0][
                "inverse_alias"
            ]
            payload["compiler"]["model"] = json.dumps(model)
            payload["compiler"]["receipt"]["model_descriptor_sha256"] = sha256(
                payload["compiler"]["model"].encode()
            ).hexdigest()
            self.assertEqual(
                400,
                client.put("/generation/compiler", json=payload).status_code,
            )
            self.assertEqual(
                base,
                connection.execute("SELECT id FROM ops_generation").fetchone()[
                    0
                ],
            )

    def test_component_change_archive_pending_and_status_rejection(self):
        data = base_generation()
        data["carrier_hashes"] = {
            atom["relative_path"] + "/" + atom["filename"]: "a" * 64
            for atom in data["snapshot"]["atoms"]
        }
        with (
            open_database() as connection,
            TestClient(create_app(connection, "instance", PIN)) as client,
        ):
            initial = client.put("/generation", json=data)
            self.assertEqual(200, initial.status_code, initial.text)
            base = initial.json()["result"]["generation"]
            payload = request(base, data)
            structure = json.loads(payload["compiler"]["structure"])
            structure["components"]["C42"] = {"parent": "C00"}
            payload["compiler"]["structure"] = json.dumps(structure)
            payload["compiler"]["receipt"]["structure_sha256"] = sha256(
                payload["compiler"]["structure"].encode()
            ).hexdigest()
            payload["archive_pending"] = True
            response = client.put("/generation/compiler", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            self.assertTrue(
                client.get("/generation/reuse", params=BINDING).json()[
                    "result"
                ]["archive_pending"]
            )
            self.assertEqual(
                [(1,)],
                connection.execute(
                    (
                        "SELECT count(*) FROM native_graph.int_reference WHERE ref = "
                        "'C42'"
                    )
                ).fetchall(),
            )
            self.assertEqual(
                2,
                connection.execute(
                    "SELECT count(*) FROM mrt_atoms"
                ).fetchone()[0],
            )
            self.assert_status_rejection(client, connection, payload, base)

    def assert_status_rejection(self, client, connection, payload, base):
        payload["base_generation"] = base
        model = json.loads(payload["compiler"]["model"])
        prefix = "Node//Artifact//Atom//"
        model["bindings"]["declarations"] = [
            [
                name,
                {
                    "kind": "entity",
                    "arguments": {
                        "entity_name": "Status",
                        "entity_kind": "Property",
                        "relation_name": "IS_PROPERTY_OF",
                        "base_path": "Node//Artifact//Atom.Header.State",
                        "applies_to_entity_classes": [prefix + name],
                        "allowed_values": values,
                    },
                },
            ]
            for name, values in (
                ("Spec Atom", ["active", "archived"]),
                ("Ticket Atom", ["done", "archived"]),
                ("Project Config Atom", ["active", "archived"]),
            )
        ]
        payload["compiler"]["model"] = json.dumps(model)
        payload["compiler"]["receipt"]["model_descriptor_sha256"] = sha256(
            payload["compiler"]["model"].encode()
        ).hexdigest()
        rejected = client.put("/generation/compiler", json=payload)
        self.assertEqual(400, rejected.status_code, rejected.text)
        self.assertIn("Status", rejected.text)
        self.assertEqual(
            base,
            connection.execute("SELECT id FROM ops_generation").fetchone()[0],
        )
