"""Support cases for native delta tests."""

from hashlib import sha256
import json

import duckdb
from starlette.testclient import TestClient

from ...DATABASE_SERVER_beta_C71__tests__shared import PIN, _query, _server
from ..atoms.test_native_atoms import _digest
from .test_native_delta import base_generation, delta, edges
from ....DATABASE_SERVER_beta_C71__shared import create_app


class DeltaCases1:
    @staticmethod
    def _setup_model_status_domain_rejects_full_and_delta():
        data = base_generation()
        model = json.loads(data["model"])
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
                ("Spec Atom", ["draft", "active", "archived"]),
                ("Ticket Atom", ["draft", "done", "archived"]),
                ("Project Config Atom", ["draft", "active", "archived"]),
            )
        ]
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(
            data["model"].encode()
        ).hexdigest()
        return data

    def test_model_status_domain_rejects_full_and_delta(self):
        data = self._setup_model_status_domain_rejects_full_and_delta()
        with _server() as client:
            refused = client.put("/generation", json=data)
            self.assertEqual(400, refused.status_code, refused.text)
            data["snapshot"]["atoms"][0]["status"] = "done"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            base = admitted.json()["result"]["generation"]
            atom = data["snapshot"]["atoms"][0] | {"status": "active"}
            path = [atom["relative_path"], atom["filename"]]
            refused = client.put(
                "/generation/native-delta",
                json=delta(base, [path], [atom], edges(atom["reference"])),
            )
            self.assertEqual(400, refused.status_code, refused.text)
            rows = _query(
                client,
                (
                    'SELECT "header.state.status" FROM mrt_atom'
                    "s WHERE reference = 'AN-T-1'"
                ),
            )
            self.assertEqual([["done"]], rows.json()["result"]["rows"])

    @staticmethod
    def _add_project_config(data):
        source = data["snapshot"]["atoms"][0]
        data["snapshot"]["atoms"].append(
            source
            | {
                "reference": "AN-C-7",
                "exact_ref": "AN-C-7@1",
                "filename": "AN-C-7.md",
                "version": 1,
                "status": "reviewed",
                "status_group": "Current",
            }
        )

    @staticmethod
    def _setup_canonical_model_project_config_status_domain():
        data = base_generation()
        model = json.loads(data["model"])
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        model["bindings"]["declarations"] = [
            [
                name,
                {
                    "kind": "entity",
                    "arguments": {
                        "entity_name": "Status",
                        "entity_kind": "Property",
                        "relation_name": "IS_PROPERTY_OF",
                        "base_path": root + ".Header.State",
                        "applies_to_entity_classes": [root + "//" + name],
                        "allowed_values": values,
                    },
                },
            ]
            for name, values in (
                ("Specification", ["draft", "active", "archived"]),
                ("Ticket", ["draft", "active", "archived"]),
                (
                    "project_config",
                    ["draft", "active", "reviewed", "archived"],
                ),
            )
        ]
        DeltaCases1._add_project_config(data)
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(
            data["model"].encode()
        ).hexdigest()
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        return data

    def test_canonical_model_project_config_status_domain(self):
        data = self._setup_canonical_model_project_config_status_domain()
        with _server() as client:
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            data["snapshot"]["atoms"][-1]["status"] = "unknown"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = client.put("/generation", json=data)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn(
                "Invalid native Atom Status",
                refused.json()["error"]["message"],
            )

    @staticmethod
    def _setup_partial_and_invalid_family_status_bindings_fail():
        args = {
            "entity_name": "Status",
            "entity_kind": "Property",
            "relation_name": "IS_PROPERTY_OF",
            "base_path": "Node//Artifact//Atom.Header.State",
            "allowed_values": ["active"],
            "applies_to_entity_classes": ["Node//Artifact//Atom//Ticket Atom"],
        }
        data = base_generation()
        model = json.loads(data["model"])

        def submit(client):
            model["bindings"]["declarations"] = [
                ["subject", {"arguments": args}]
            ]
            data["model"] = json.dumps(model)
            data["receipt"]["model_descriptor_sha256"] = sha256(
                data["model"].encode()
            ).hexdigest()
            return client.put("/generation", json=data)

        return args, data, submit

    def test_partial_and_invalid_family_status_bindings_fail(self):
        args, data, submit = (
            self._setup_partial_and_invalid_family_status_bindings_fail()
        )

        with (
            duckdb.connect() as connection,
            TestClient(create_app(connection, "instance", PIN)) as client,
        ):
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Incomplete", refused.json()["error"]["message"])
            args["allowed_values"] = []
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn("Invalid scoped", refused.json()["error"]["message"])
            args["applies_to_entity_classes"] = [
                "Node//Artifact//Atom//Ticket Atom//Task"
            ]
            data["snapshot"]["atoms"].append(data["snapshot"]["atoms"][0])
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn(
                "Duplicate native Atom", refused.json()["error"]["message"]
            )
            data["snapshot"]["atoms"][0]["status"] = "not-a-status"
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            refused = submit(client)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertIn(
                "Invalid native Atom Status",
                refused.json()["error"]["message"],
            )

    @staticmethod
    def _setup_warning_delta():
        path = ["tickets", "AN-T-99--new.md"]
        relative = "/".join(path)
        warning = {
            "relative_path": relative,
            "code": "parse_error",
            "message": "Malformed Atom",
            "atom_ref": None,
            "related_paths": [],
        }
        return path, relative, warning

    def test_warning_only_delta_is_atomic_and_does_not_clear_unrelated_issues(
        self,
    ):
        path, relative, warning = self._setup_warning_delta()
        with _server() as client:
            base = client.put("/generation", json=base_generation()).json()[
                "result"
            ]["generation"]
            payload = delta(base, [path], [], [])
            payload["snapshot"]["ingestion_issues"] = [warning]
            payload["snapshot_sha256"] = _digest(
                {"paths": payload["paths"], "snapshot": payload["snapshot"]}
            )
            refused = client.put(
                "/generation/native-delta",
                json=payload | {"snapshot_sha256": "invalid"},
            )
            self.assertEqual(400, refused.status_code, refused.text)
            issue_sql = "SELECT relative_path, code FROM ops_ingestion_issues"
            self.assertEqual(
                [], _query(client, issue_sql).json()["result"]["rows"]
            )
            admitted = self.send(client, payload)
            self.assertNotEqual(base, admitted)
            unrelated = ["tickets", "AN-T-100--unrelated.md"]
            self.assertEqual(
                admitted,
                self.send(client, delta(admitted, [unrelated], [], [])),
            )
            self.assertEqual(
                [[relative, "parse_error"]],
                _query(client, issue_sql).json()["result"]["rows"],
            )
            self.assertNotEqual(
                admitted, self.send(client, delta(admitted, [path], [], []))
            )
            self.assertEqual(
                [], _query(client, issue_sql).json()["result"]["rows"]
            )
