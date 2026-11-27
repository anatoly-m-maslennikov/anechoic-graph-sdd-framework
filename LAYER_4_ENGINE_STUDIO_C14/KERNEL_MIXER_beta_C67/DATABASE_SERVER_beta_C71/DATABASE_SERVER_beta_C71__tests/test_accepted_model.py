"""Test the private accepted Model asset and receipt."""

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import duckdb

from ..accepted_model import initialize, managed, prepare, publish


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


def database():
    connection = duckdb.connect()
    connection.execute((
        'CREATE TABLE ops_generation (id VARCHAR, model VARCHAR, structure '
        'VARCHAR)'
    ))
    return connection


class AcceptedModelTests(unittest.TestCase):
    def test_lifecycle_generation_resolves_only_the_accepted_receipt(self):
        with TemporaryDirectory() as directory, database() as db:
            db.execute(
                "CREATE VIEW generation AS SELECT * FROM ops_generation"
            )
            initialize(db, Path(directory).resolve())
            model = json.dumps(
                {**json.loads(descriptor()), "ticket_labels": ["Task"]}
            )
            receipt, pending = prepare(db, model)
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["g", receipt, "{}"],
            )
            publish(db, model, pending)
            self.assertEqual(
                (receipt,),
                db.execute("SELECT model FROM ops_generation").fetchone(),
            )
            self.assertEqual(
                (receipt,),
                db.execute("SELECT model FROM main.generation").fetchone(),
            )
            self.assertEqual(
                ("g", '["Task"]'),
                db.execute(
                    (
                        "SELECT id, json_extract(model, '$.ticket_labels') "
                        'FROM main.int_lifecycle_generation'
                    )
                ).fetchone(),
            )
            db.execute("UPDATE ops_generation SET model = ?", ["b" * 64])
            self.assertIsNone(
                db.execute(
                    "SELECT id, model FROM main.int_lifecycle_generation"
                ).fetchone()
            )

    def test_publish_restart_unchanged_and_rejected(self):
        with TemporaryDirectory() as directory, database() as db:
            root = Path(directory).resolve()
            initialize(db, root)
            model = descriptor()
            receipt, pending = prepare(db, model)
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["generation", receipt, "{}"],
            )
            publish(db, model, pending)
            asset = root / ".anechoic_runtime/assets/generated_model.json"
            self.assertEqual(model, asset.read_text())
            with patch(
                "os.replace",
                side_effect=AssertionError("unchanged file was replaced"),
            ):
                self.assertEqual((receipt, None), prepare(db, model))
                publish(db, model, None)
            _, pending = prepare(db, model)
            self.assertIsNone(pending)
            asset.unlink()
            publish(db, model, pending)
            self.assertEqual(model.encode("utf-8"), asset.read_bytes())
            asset.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "unavailable or unsafe"):
                prepare(db, model)
            asset.chmod(0o600)
            bad = json.loads(model)
            bad["module_sources"]["__init__.py"] = "bad"
            with self.assertRaises(ValueError):
                prepare(db, json.dumps(bad))
            self.assertEqual(model, asset.read_text())
            with database() as fresh:
                initialize(fresh, root)
                self.assertIsNone(managed(fresh)[1])
            db.execute("UPDATE ops_generation SET model = ?", ["b" * 64])
            db.execute("DROP TABLE accepted_model_state")
            initialize(db, root)
            self.assertIsNone(managed(db)[1])
            self.assertIsNone(
                db.execute("SELECT id FROM ops_generation").fetchone()
            )
            self.assertEqual(model, asset.read_text())

    def test_rejects_unusable_assets_with_reason(self):
        for content, receipt, reason in (
            (None, "a" * 64, "missing"),
            ("invalid", "a" * 64, "invalid or unsafe"),
            (descriptor(), "a" * 64, "does not match"),
            (descriptor(), None, "no generation receipt"),
        ):
            with (
                self.subTest(reason=reason),
                TemporaryDirectory() as directory,
                database() as db,
            ):
                root = Path(directory).resolve()
                if content is not None:
                    asset = (
                        root / ".anechoic_runtime/assets/generated_model.json"
                    )
                    asset.parent.mkdir(parents=True)
                    asset.write_text(content)
                    asset.chmod(0o600)
                if receipt is not None:
                    db.execute(
                        "INSERT INTO ops_generation VALUES (?, ?, ?)",
                        ["one", receipt, "{}"],
                    )
                initialize(db, root)
                self.assertIsNone(managed(db)[1])
                self.assertIn(reason, managed(db)[2])
                self.assertIsNone(
                    db.execute("SELECT id FROM ops_generation").fetchone()
                )

    def test_unusable_asset_can_be_replaced_after_bootstrap_refusal(self):
        with TemporaryDirectory() as directory, database() as db:
            root = Path(directory).resolve()
            target = root / "untouched"
            target.write_text("keep")
            asset = root / ".anechoic_runtime/assets/generated_model.json"
            asset.parent.mkdir(parents=True)
            asset.symlink_to(target)
            initialize(db, root)
            self.assertIn("invalid or unsafe", managed(db)[2])
            model = descriptor()
            receipt, pending = prepare(db, model)
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["one", receipt, "{}"],
            )
            publish(db, model, pending)
            self.assertFalse(asset.is_symlink())
            self.assertEqual("keep", target.read_text())
            self.assertEqual(model, asset.read_text())

    def test_migrates_legacy_model_row(self):
        with TemporaryDirectory() as directory, database() as db:
            root = Path(directory).resolve()
            model = descriptor()
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["one", model, "{}"],
            )
            initialize(db, root)
            self.assertEqual(
                model,
                (
                    root / ".anechoic_runtime/assets/generated_model.json"
                ).read_text(),
            )
            self.assertEqual(
                sha256(model.encode()).hexdigest(),
                db.execute("SELECT model FROM ops_generation").fetchone()[0],
            )

    def test_failed_publication_keeps_file_and_forces_reconciliation(self):
        with TemporaryDirectory() as directory, database() as db:
            root = Path(directory).resolve()
            initialize(db, root)
            first, pending = prepare(db, descriptor())
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["one", first, "{}"],
            )
            publish(db, descriptor(), pending)
            second = descriptor("changed")
            receipt, pending = prepare(db, second)
            db.execute(
                "UPDATE ops_generation SET id = ?, model = ?", ["two", receipt]
            )
            with patch("os.replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    publish(db, second, pending)
            self.assertEqual(
                descriptor(),
                (
                    root / ".anechoic_runtime/assets/generated_model.json"
                ).read_text(),
            )
            self.assertIsNone(
                db.execute("SELECT id FROM ops_generation").fetchone()
            )
            self.assertEqual(descriptor(), managed(db)[1])

    def test_cache_failure_preserves_the_previous_file(self):
        with TemporaryDirectory() as directory, database() as db:
            root = Path(directory).resolve()
            initialize(db, root)
            first = descriptor()
            _, pending = prepare(db, first)
            publish(db, first, pending)
            second = descriptor("changed")
            receipt, pending = prepare(db, second)
            db.execute(
                "INSERT INTO ops_generation VALUES (?, ?, ?)",
                ["new", receipt, "{}"],
            )

            def execute(sql, *arguments):
                if sql.startswith("UPDATE accepted_model_state"):
                    raise duckdb.OutOfMemoryException("cache write failed")
                return db.execute(sql, *arguments)

            connection = Mock(wraps=db)
            connection.execute.side_effect = execute
            with self.assertRaisesRegex(
                duckdb.OutOfMemoryException, "cache write failed"
            ):
                publish(connection, second, pending)
            asset = root / ".anechoic_runtime/assets/generated_model.json"
            self.assertEqual(first, asset.read_text())
            self.assertEqual(
                [asset.name], [path.name for path in asset.parent.iterdir()]
            )
            self.assertIsNone(
                db.execute("SELECT id FROM ops_generation").fetchone()
            )
            self.assertEqual(first, managed(db)[1])

    def test_bound_server_admission_and_fresh_database_reuse(self):
        from .DATABASE_SERVER_beta_C71__tests__shared import (
            BINDING,
            _generation,
            _server,
        )

        with TemporaryDirectory(dir='/tmp') as directory:
            root = Path(directory).resolve()
            database_path = root / 'projection.duckdb'
            data = _generation()
            model = json.loads(descriptor())
            model['model_sha256'] = 'b' * 64
            data['model'] = json.dumps(model, indent=2)
            data['receipt']['model_descriptor_sha256'] = sha256(data['model'].encode()).hexdigest()
            asset = root / '.anechoic_runtime/assets/generated_model.json'
            with _server(database_path, '--project-root', str(root)) as client:
                response = client.put('/generation', json=data)
                self.assertEqual(200, response.status_code, response.text)
                before = asset.stat().st_mtime_ns
                self.assertEqual(200, client.put('/generation', json=data).status_code)
                self.assertEqual(before, asset.stat().st_mtime_ns)
                asset.unlink()
                self.assertEqual(200, client.put('/generation', json=data).status_code)
                self.assertEqual(data['model'], asset.read_text())
                expected = data['model'].encode('utf-8')
                for different in (expected.replace(b'\n', b'\r\n'), b'\xff'):
                    asset.write_bytes(different)
                    self.assertEqual(200, client.put('/generation', json=data).status_code)
                    self.assertEqual(expected, asset.read_bytes())
                invalid = dict(data, snapshot={'manifest_sha256': 'wrong', 'atoms': []})
                self.assertEqual(400, client.put('/generation', json=invalid).status_code)
                self.assertEqual(data['model'], asset.read_text())
                self.assertEqual(data['model'], client.get('/model', params=BINDING).text)
            with duckdb.connect(str(database_path)) as db:
                self.assertEqual(data['receipt']['model_descriptor_sha256'],
                                 db.execute('SELECT model FROM ops_generation').fetchone()[0])
                db.execute('DROP TABLE mrt_model_entities')
            with _server(database_path, '--project-root', str(root)) as client:
                self.assertEqual(data['model'], client.get('/model', params=BINDING).text)
            with duckdb.connect(str(database_path), read_only=True) as db:
                self.assertEqual(0, db.execute('SELECT count(*) FROM mrt_model_entities').fetchone()[0])
            with _server(root / 'fresh.duckdb', '--project-root', str(root)) as client:
                response = client.get('/model', params=BINDING)
                self.assertEqual(409, response.status_code)
                self.assertIn('no generation receipt', response.json()['error']['message'])
