"""Structure rows remain authoritative across admission and database migration."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import duckdb

from ..persistence import open_bound_database
from ..project_structure import (
    ensure_structure_table,
    replace_structure,
    structure_bytes,
)


class ProjectStructureTest(unittest.TestCase):
    def test_rows_reconstruct_and_replace(self):
        db = duckdb.connect(":memory:")
        ensure_structure_table(db)
        doc = {"model_sha256": "m", "project": {"ref": "p", "sha256": "s"}, "packages": {},
               "components": {"C1": {"parent": "C00", "source_path": "a", "ref": "r", "sha256": "h",
                                      "fields": {"name": "first"}}}}
        facts = replace_structure(db, doc)
        self.assertEqual(doc, json.loads(structure_bytes(db, facts)))
        self.assertEqual([("C00", None), ("C1", "a")], db.execute(
            "SELECT component_id, source_path FROM mrt_project_structure ORDER BY component_id").fetchall())
        doc["components"]["C1"].update({"parent": "C2", "source_path": "moved", "ref": "edited"})
        doc["components"]["C2"] = {"parent": "C00", "source_path": "b"}
        facts = replace_structure(db, doc)
        self.assertEqual(doc, json.loads(structure_bytes(db, facts)))
        self.assertEqual([("C2", "moved", "edited")], db.execute(
            "SELECT parent, source_path, ref FROM mrt_project_structure WHERE component_id = 'C1'").fetchall())
        db.execute("BEGIN")
        doc["components"] = {"C2": {"parent": "C00", "source_path": "b"}}
        replace_structure(db, doc)
        db.execute("ROLLBACK")
        self.assertEqual([("C00",), ("C1",), ("C2",)], db.execute(
            "SELECT component_id FROM mrt_project_structure ORDER BY component_id").fetchall())
        facts = replace_structure(db, doc)
        self.assertEqual(doc, json.loads(structure_bytes(db, facts)))
        self.assertEqual([("C00",), ("C2",)], db.execute(
            "SELECT component_id FROM mrt_project_structure ORDER BY component_id").fetchall())
        db.close()

    def test_existing_generation_migrates_in_place(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db"
            db = duckdb.connect(str(path))
            db.execute("CREATE TABLE ops_project_binding (manifest_sha256 VARCHAR, instance_id VARCHAR)")
            db.execute("INSERT INTO ops_project_binding VALUES ('pin', 'instance')")
            db.execute("CREATE TABLE ops_generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
            doc = {"model_sha256": "m", "project": {"ref": "p", "sha256": "s"},
                   "components": {"C1": {"parent": "C00", "source_path": "src"}}}
            db.execute("INSERT INTO ops_generation VALUES (?, ?, ?)", ["id", "{}", json.dumps(doc, indent=2)])
            db.execute("CREATE VIEW generation AS SELECT * FROM ops_generation")
            db.close()
            path.chmod(0o600)
            with patch("KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.persistence.connect", duckdb.connect):
                db = open_bound_database(str(path), "pin", "instance")
            self.assertNotIn("structure", [row[1] for row in db.execute("PRAGMA table_info('ops_generation')").fetchall()])
            generation, facts = db.execute("SELECT id, structure_facts FROM ops_generation").fetchone()
            self.assertEqual("id", generation)
            self.assertEqual(doc, json.loads(structure_bytes(db, facts)))
            db.close()


class ModelDiagnosticsAdmissionTest(unittest.TestCase):
    def test_diagnostics_are_validated_and_admitted_atomically(self):
        from .DATABASE_SERVER_beta_C71__tests__shared import (
            _generation,
            _query,
            _server,
        )

        payload = _generation()
        payload["model_diagnostics"] = [{"attempt_id": "attempt", "accepted_generation": None,
            "severity": "error", "code": "invalid", "message": "bad source", "atom_ref": None,
            "source_path": None, "subject": None}]
        with _server() as client:
            response = client.put("/generation", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            query = "SELECT accepted_generation, code FROM mrt_diag_model_manifests"
            self.assertEqual([["b" * 64, "invalid"]], _query(client, query).json()["result"]["rows"])
            payload["model_diagnostics"][0]["message"] = 42
            self.assertEqual(400, client.put("/generation", json=payload).status_code)
            self.assertEqual([["b" * 64, "invalid"]], _query(client, query).json()["result"]["rows"])
            payload["model_diagnostics"] = []
            self.assertEqual(200, client.put("/generation", json=payload).status_code)
            self.assertEqual([], _query(client, query).json()["result"]["rows"])
