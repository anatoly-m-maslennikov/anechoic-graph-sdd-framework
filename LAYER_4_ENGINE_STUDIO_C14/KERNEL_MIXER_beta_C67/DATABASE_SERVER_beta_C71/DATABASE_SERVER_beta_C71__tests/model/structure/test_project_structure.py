"""Structure projection follows admitted generations and retained databases."""

import json
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _generation,
    _query,
    _server,
)


def _structure_fixture():
    payload = _generation()
    structure = json.loads(payload["structure"])
    structure["project"]["purpose"] = "Provide the Project runtime."
    structure["packages"] = {
        "CS1": {
            "component": "C1",
            "ref": "AN-S-2",
            "fields": {"purpose": "Build", "solution": "Do"},
        }
    }
    structure["components"] = {
        "C1": {
            "parent": "C00",
            "source_path": "a",
            "ref": "r",
            "sha256": "h",
            "fields": {"name": "first"},
            "purpose": "Provide a Component service.",
        }
    }
    return payload, structure


class ProjectStructureTest(unittest.TestCase):
    def test_projection_replaces_atomically_and_preserves_structure(self):
        payload, structure = _structure_fixture()
        with _server() as client:
            for components, expected in (
                (structure["components"], [["C00", None], ["C1", "a"]]),
                (
                    {"C2": {"parent": "C00", "source_path": "b"}},
                    [["C00", None], ["C2", "b"]],
                ),
            ):
                structure["components"] = components
                payload["structure"] = json.dumps(structure, indent=2)
                payload["receipt"]["structure_sha256"] = sha256(
                    payload["structure"].encode()
                ).hexdigest()
                response = client.put("/generation", json=payload)
                self.assertEqual(200, response.status_code, response.text)
                self.assertEqual(
                    [["CS1", "C1", "AN-S-2", "Build"]],
                    _query(
                        client,
                        "SELECT seed_id, parent, ref, json_extract_string(fields, '$.purpose') FROM mrt_component_seeds",
                    ).json()["result"]["rows"],
                )
                self.assertEqual(
                    payload["structure"],
                    client.get("/structure", params=BINDING).text,
                )
                self.assertEqual(
                    expected,
                    _query(
                        client,
                        "SELECT component_id, source_path FROM mrt_project_structure ORDER BY component_id",
                    ).json()["result"]["rows"],
                )
            self.assert_rejection_preserves_structure(
                client, payload, expected
            )

    def assert_rejection_preserves_structure(self, client, payload, expected):
        payload["receipt"]["structure_sha256"] = "0" * 64
        self.assertEqual(
            400, client.put("/generation", json=payload).status_code
        )
        self.assertEqual(
            expected,
            _query(
                client,
                "SELECT component_id, source_path FROM mrt_project_structure ORDER BY component_id",
            ).json()["result"]["rows"],
        )

    def test_existing_projection_backfills_seeds(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db"
            payload = _generation()
            structure = json.loads(payload["structure"])
            structure["packages"] = {
                "CS1": {
                    "component": "C1",
                    "ref": "AN-S-2",
                    "fields": {"purpose": "Build"},
                }
            }
            payload["structure"] = json.dumps(structure)
            payload["receipt"]["structure_sha256"] = sha256(
                payload["structure"].encode()
            ).hexdigest()
            with _server(path) as client:
                response = client.put("/generation", json=payload)
                self.assertEqual(200, response.status_code, response.text)
            with duckdb.connect(str(path)) as db:
                db.execute("DROP TABLE mrt_component_seeds")
            query = "SELECT seed_id, parent, ref FROM mrt_component_seeds"
            for _ in range(2):
                with _server(path) as client:
                    self.assertEqual(
                        [["CS1", "C1", "AN-S-2"]],
                        _query(client, query).json()["result"]["rows"],
                    )

    def test_existing_generation_migrates_in_place(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db"
            doc = {
                "model_sha256": "m",
                "project": {"ref": "p", "sha256": "s"},
                "components": {"C1": {"parent": "C00", "source_path": "src"}},
            }
            with duckdb.connect(str(path)) as db:
                db.execute(
                    "CREATE TABLE ops_project_binding (manifest_sha256 VARCHAR, instance_id VARCHAR)"
                )
                db.execute(
                    "INSERT INTO ops_project_binding VALUES (?, 'instance')",
                    [PIN],
                )
                db.execute(
                    "CREATE TABLE ops_generation (id VARCHAR, model VARCHAR, structure VARCHAR)"
                )
                db.execute(
                    "INSERT INTO ops_generation VALUES (?, ?, ?)",
                    ["id", "{}", json.dumps(doc, indent=2)],
                )
                db.execute(
                    "CREATE VIEW generation AS SELECT * FROM ops_generation"
                )
            path.chmod(0o600)
            with _server(path) as client:
                self.assertEqual(
                    json.dumps(doc, indent=2),
                    client.get("/structure", params=BINDING).text,
                )
                self.assertEqual(
                    [["C00"], ["C1"]],
                    _query(
                        client,
                        "SELECT component_id FROM mrt_project_structure ORDER BY component_id",
                    ).json()["result"]["rows"],
                )


class ModelDiagnosticsAdmissionTest(unittest.TestCase):
    def test_diagnostics_are_validated_and_admitted_atomically(self):
        from ...DATABASE_SERVER_beta_C71__tests__shared import (
            _generation,
            _query,
            _server,
        )

        payload = _generation()
        payload["model_diagnostics"] = [
            {
                "attempt_id": "attempt",
                "accepted_generation": None,
                "severity": "error",
                "code": "invalid",
                "message": "bad source",
                "atom_ref": None,
                "source_path": None,
                "subject": None,
            }
        ]
        with _server() as client:
            response = client.put("/generation", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            query = "SELECT accepted_generation, code FROM mrt_diag_model_manifests"
            self.assertEqual(
                [["b" * 64, "invalid"]],
                _query(client, query).json()["result"]["rows"],
            )
            payload["model_diagnostics"][0]["message"] = 42
            self.assertEqual(
                400, client.put("/generation", json=payload).status_code
            )
            self.assertEqual(
                [["b" * 64, "invalid"]],
                _query(client, query).json()["result"]["rows"],
            )
            payload["model_diagnostics"] = []
            self.assertEqual(
                200, client.put("/generation", json=payload).status_code
            )
            self.assertEqual(
                [], _query(client, query).json()["result"]["rows"]
            )
