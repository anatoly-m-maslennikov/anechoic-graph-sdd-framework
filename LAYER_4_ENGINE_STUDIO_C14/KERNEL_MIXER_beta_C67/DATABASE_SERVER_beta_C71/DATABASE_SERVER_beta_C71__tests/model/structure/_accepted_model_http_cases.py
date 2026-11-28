"""Private-socket acceptance checks for the retained Model asset."""

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _server,
)


def descriptor(extra=""):
    return json.dumps(
        {
            "binding_schema": 1,
            "model_sha256": "a" * 64,
            "modules": {"__init__.py": sha256(b"").hexdigest()},
            "module_sources": {"__init__.py": ""},
            "module_order": [],
            "class_modules": {},
            "bindings": {},
            "extra": extra,
        }
    )


class AcceptedModelHttpCases:
    def test_bound_server_admission_and_fresh_database_reuse(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            database_path = root / "projection.duckdb"
            data = _generation()
            model = json.loads(descriptor())
            model["model_sha256"] = "b" * 64
            data["model"] = json.dumps(model, indent=2)
            data["receipt"]["model_descriptor_sha256"] = sha256(
                data["model"].encode()
            ).hexdigest()
            asset = root / ".anechoic_runtime/assets/generated_model.json"
            self._check_generation_admission(database_path, root, asset, data)
            self._check_generation_restart(database_path, root, data)

    def _check_generation_restart(self, database_path, root, data):
        with duckdb.connect(str(database_path)) as db:
            self.assertEqual(
                data["receipt"]["model_descriptor_sha256"],
                db.execute("SELECT model FROM ops_generation").fetchone()[0],
            )
            db.execute("DROP TABLE mrt_model_entities")
        with _server(database_path, "--project-root", str(root)) as client:
            self.assertEqual(
                data["model"], client.get("/model", params=BINDING).text
            )
        with duckdb.connect(str(database_path), read_only=True) as db:
            self.assertEqual(
                0,
                db.execute(
                    "SELECT count(*) FROM mrt_model_entities"
                ).fetchone()[0],
            )
        with _server(
            root / "fresh.duckdb", "--project-root", str(root)
        ) as client:
            response = client.get("/model", params=BINDING)
            self.assertEqual(409, response.status_code)
            self.assertIn(
                "no generation receipt",
                response.json()["error"]["message"],
            )

    def _check_generation_admission(self, database_path, root, asset, data):
        with _server(database_path, "--project-root", str(root)) as client:
            response = client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            before = asset.stat().st_mtime_ns
            self.assertEqual(
                200, client.put("/generation", json=data).status_code
            )
            self.assertEqual(before, asset.stat().st_mtime_ns)
            asset.unlink()
            self.assertEqual(
                200, client.put("/generation", json=data).status_code
            )
            self.assertEqual(data["model"], asset.read_text())
            expected = data["model"].encode("utf-8")
            for different in (expected.replace(b"\n", b"\r\n"), b"\xff"):
                asset.write_bytes(different)
                self.assertEqual(
                    200, client.put("/generation", json=data).status_code
                )
                self.assertEqual(expected, asset.read_bytes())
            invalid = dict(
                data, snapshot={"manifest_sha256": "wrong", "atoms": []}
            )
            self.assertEqual(
                400, client.put("/generation", json=invalid).status_code
            )
            self.assertEqual(data["model"], asset.read_text())
            self.assertEqual(
                data["model"], client.get("/model", params=BINDING).text
            )
