"""Persist Archive version facts across incomplete generations and deltas."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import duckdb

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _server
from .test_archive_generation import _partial
from .test_native_atoms import _digest
from .test_startup_checkpoint import _baseline, _delta, _path


def versions(database):
    with duckdb.connect(str(database), read_only=True) as connection:
        exists = connection.execute(
            (
                "SELECT count(*) FROM information_schema.tables WHERE "
                "table_schema='main' AND table_name='ops_archive_versions'"
            )
        ).fetchone()[0]
        return (
            connection.execute(
                "SELECT * FROM main.ops_archive_versions ORDER BY atom_id"
            ).fetchall()
            if exists
            else None
        )


class ArchiveVersionsTests(unittest.TestCase):
    def test_first_partial_and_complete_snapshot(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "test.duckdb"
            data, archive, hashes = _partial()
            with _server(database) as client:
                base = client.put("/generation", json=data).json()["result"][
                    "generation"
                ]
            self.assertIsNone(versions(database))
            with _server(database) as client:
                request = BINDING | {
                    "base_generation": base,
                    "snapshot": archive,
                    "snapshot_sha256": _digest(archive),
                    "carrier_hashes": hashes,
                }
                self.assertEqual(
                    200,
                    client.put(
                        "/generation/archive", json=request
                    ).status_code,
                )
            self.assertEqual([("AN-T-1", 1)], versions(database))

    def test_empty_complete_snapshot_has_a_cache(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "test.duckdb"
            data = _baseline()
            current, archived = data["snapshot"]["atoms"]
            data["snapshot"]["atoms"] = [current]
            data["snapshot"]["relations"] = [
                r
                for r in data["snapshot"]["relations"]
                if r["source_ref"] != archived["reference"]
            ]
            del data["carrier_hashes"][_path(archived)]
            data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
            with _server(database) as client:
                response = client.put("/generation", json=data)
                self.assertEqual(200, response.status_code, response.text)
            self.assertEqual([], versions(database))

    def test_warm_pending_delta_and_failed_transaction(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            database = Path(directory).resolve() / "test.duckdb"
            data = _baseline()
            current, archived = data["snapshot"]["atoms"]
            with _server(database) as client:
                response = client.put("/generation", json=data)
                self.assertEqual(200, response.status_code, response.text)
                base = response.json()["result"]["generation"]
            self.assertEqual([("AN-T-1", 1)], versions(database))
            with _server(database) as client:
                pending = BINDING | {
                    "base_generation": base,
                    "archive_pending": True,
                }
                self.assertEqual(
                    200,
                    client.put("/generation/reuse", json=pending).status_code,
                )
                higher = archived | {
                    "reference": "AN-T-1@3",
                    "exact_ref": "AN-T-1@3",
                    "version": 3,
                    "filename": "AN-T-1@3-extra.md",
                }
                delta = _delta(
                    base,
                    data["snapshot"],
                    [[higher["relative_path"], higher["filename"]]],
                    [higher],
                    {_path(higher): "d" * 64},
                )
                response = client.put("/generation/native-delta", json=delta)
                self.assertEqual(200, response.status_code, response.text)
                failed = client.put("/generation/native-delta", json=delta)
                self.assertEqual(409, failed.status_code, failed.text)
            self.assertEqual([("AN-T-1", 3)], versions(database))
