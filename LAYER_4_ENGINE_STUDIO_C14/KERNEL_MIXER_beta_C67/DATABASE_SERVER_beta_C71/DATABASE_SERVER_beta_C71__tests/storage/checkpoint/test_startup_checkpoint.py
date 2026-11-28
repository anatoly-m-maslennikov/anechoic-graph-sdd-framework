"""Exercise persisted startup and Archive checkpoint admission."""

from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import duckdb
from starlette.testclient import TestClient

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint import checkpoint__shared as carrier_checkpoint
from ....DATABASE_SERVER_beta_C71__shared import create_app, open_database
from .startup_checkpoint_cases import StartupCheckpointCases
from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _launch_arguments,
    _query as _query,
    _server,
)
from ...native.atoms.test_native_atoms import _digest
from ...native.refresh.test_native_refresh import graph_payload


def _path(atom):
    return str(PurePosixPath(atom["relative_path"]) / atom["filename"])


def _folder(filename, digest):
    return sha256(
        json.dumps(
            [[filename, digest]], ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def _baseline():
    data = graph_payload()
    current, archived = data["snapshot"]["atoms"]
    archived["relative_path"] += "/09_archived"
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    witness = {
        "inputs": {
            "manifest": "a" * 64,
            "graph": "b" * 64,
            "carrier_schema": "c" * 64,
        },
        "graph_config": {},
        "endpoints": json.loads(data["model"])["bindings"]["endpoints"],
    }
    return data | {
        "reuse": witness,
        "carrier_hashes": {
            _path(current): "a" * 64,
            _path(archived): "b" * 64,
        },
    }


def _delta(base, snapshot, paths, atoms, hashes):
    payload = {
        "paths": paths,
        "carrier_hashes": hashes,
        "snapshot": snapshot | {"atoms": atoms, "relations": []},
    }
    return BINDING | {
        "base_generation": base,
        **payload,
        "snapshot_sha256": _digest(payload),
    }


@contextmanager
def _server_without_lifespan(database):
    _, env = _launch_arguments(database.with_suffix(".sock"))
    with (
        patch.dict("os.environ", env),
        open_database(
            str(database), PIN, BINDING["instance_id"]
        ) as connection,
    ):
        client = TestClient(
            create_app(connection, BINDING["instance_id"], PIN)
        )
        try:
            yield client
        finally:
            client.close()


class StartupCheckpointTests(StartupCheckpointCases, unittest.TestCase):
    def _accepted(self, client, route, payload):
        response = client.put(route, json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def _reuse(self, client):
        return client.get("/generation/reuse", params=BINDING).json()["result"]

    def _assert_disk_checkpoint(self, database, hashes, folders, changes):
        with duckdb.connect(str(database), read_only=True) as connection:
            self.assertEqual(
                hashes,
                dict(
                    connection.execute(
                        (
                            "SELECT path, digest FROM "
                            "ops_generation_carrier_digests"
                        )
                    ).fetchall()
                ),
            )
            self.assertEqual(
                folders,
                dict(
                    connection.execute(
                        "SELECT * FROM ops_generation_folder_hashes"
                    ).fetchall()
                ),
            )
            self.assertEqual(
                changes,
                dict(
                    connection.execute(
                        "SELECT * FROM ops_generation_carrier_changes"
                    ).fetchall()
                ),
            )

    def test_reuse_reports_generation_model_status_domains(self):
        data = _baseline()
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
                ("Ticket", ["draft", "active", "reviewed", "archived"]),
                ("project_config", ["draft", "active", "archived"]),
            )
        ]
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(
            data["model"].encode()
        ).hexdigest()
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        with _server_without_lifespan(
            Path(directory).resolve() / "projection.duckdb"
        ) as client:
            generation = self._accepted(client, "/generation", data)
            result = self._reuse(client)
            self.assertEqual(generation, result["base_generation"])
            self.assertEqual(
                ["active", "archived", "draft", "reviewed"],
                result["status_domains"]["T"],
            )
            self.assertEqual(
                result["status_domains"]["P"], result["status_domains"]["C"]
            )

    def test_control_folder_named_archive_is_foreground(self):
        connection = duckdb.connect(":memory:")
        self.addCleanup(connection.close)
        carrier_checkpoint.initialize_checkpoint(connection)
        carrier_checkpoint._replace_checkpoint(
            connection,
            {
                "09_archived/a.md": "a" * 64,
                "09_archived/09_archived/b.md": "b" * 64,
            },
        )
        self.assertEqual(
            {"09_archived/a.md": "a" * 64},
            carrier_checkpoint.read_checkpoint(connection, "foreground"),
        )
        self.assertEqual(
            {"09_archived/09_archived/b.md": "b" * 64},
            carrier_checkpoint.read_checkpoint(connection, "archive"),
        )

    def test_scoped_checkpoint_reads_include_pending_changes(self):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        database = Path(directory).resolve() / "projection.duckdb"
        data = _baseline()
        current, archived = data["snapshot"]["atoms"]
        with _server(database) as client:
            base = self._accepted(client, "/generation", data)
            for scope, atom, digest in (
                ("foreground", current, "a" * 64),
                ("archive", archived, "b" * 64),
            ):
                result = client.get(
                    "/generation/reuse", params=BINDING | {"scope": scope}
                ).json()["result"]
                self.assertEqual(
                    {_path(atom): digest}, result["carrier_hashes"]
                )
                self.assertEqual(
                    {atom["relative_path"]: _folder(atom["filename"], digest)},
                    result["folder_hashes"],
                )
            base = self._accepted(
                client,
                "/generation/reuse",
                BINDING | {"base_generation": base, "archive_pending": True},
            )
            deleted = _delta(
                base,
                data["snapshot"],
                [[archived["relative_path"], archived["filename"]]],
                [],
                {},
            )
            self._accepted(client, "/generation/archive", deleted)
            self.assert_scoped_after_delete(client, current)

    def assert_scoped_after_delete(self, client, current):
        for scope, expected in (
            ("foreground", {_path(current): "a" * 64}),
            ("archive", {}),
        ):
            result = client.get(
                "/generation/reuse", params=BINDING | {"scope": scope}
            ).json()["result"]
            self.assertEqual(scope, result["checkpoint_scope"])
            self.assertEqual(expected, result["carrier_hashes"])
            self.assertEqual(
                {
                    current["relative_path"]: _folder(
                        current["filename"], "a" * 64
                    )
                }
                if scope == "foreground"
                else {},
                result["folder_hashes"],
            )
        self.assertEqual(
            {_path(current): "a" * 64},
            self._reuse(client)["carrier_hashes"],
        )

    def test_missing_and_empty_checkpoint_remain_distinct(self):
        snapshot = {"schema_version": 2, "atoms": []}
        empty = {"snapshot": snapshot, "carrier_hashes": {}}
        full = _baseline()
        current, _ = full["snapshot"]["atoms"]
        delta = _delta(
            "base",
            full["snapshot"],
            [[current["relative_path"], current["filename"]]],
            [current],
            {_path(current): "d" * 64},
        )
        with duckdb.connect() as connection:
            carrier_checkpoint.update_checkpoint(connection, delta, delta=True)
            self.assertIsNone(carrier_checkpoint.read_checkpoint(connection))
            carrier_checkpoint.update_checkpoint(connection, empty)
            self.assertEqual(
                {}, carrier_checkpoint.read_checkpoint(connection)
            )
            carrier_checkpoint.update_checkpoint(connection, delta, delta=True)
            self.assertEqual(
                delta["carrier_hashes"],
                carrier_checkpoint.read_checkpoint(connection),
            )
            carrier_checkpoint.update_checkpoint(
                connection, {"snapshot": snapshot}, delta=True
            )
            self.assertIsNone(carrier_checkpoint.read_checkpoint(connection))
            self.assertEqual(
                [],
                connection.execute(
                    "SELECT * FROM ops_generation_carrier_changes"
                ).fetchall(),
            )

    def test_reuse_witness_legacy_shape_and_invalid_inputs(self):
        data = _baseline()
        witness = data["reuse"]
        del witness["inputs"]["carrier_schema"]
        witness["inputs"]["graph"] = "disabled"
        witness["graph_config"] = None
        with _server() as client:
            self._accepted(client, "/generation", data)
            proof = self._reuse(client)
            for key, value in witness.items():
                self.assertEqual(value, proof[key])
            self.assertNotIn("folder_hashes", proof)
            invalid = [
                None,
                witness | {"endpoints": {}},
                witness | {"extra": 1},
                witness
                | {"inputs": witness["inputs"] | {"carrier_schema": None}},
                witness | {"inputs": witness["inputs"] | {"graph": "invalid"}},
            ]
            for item in invalid:
                with self.subTest(witness=item):
                    response = client.put(
                        "/generation", json=data | {"reuse": item}
                    )
                    self.assertEqual(400, response.status_code, response.text)
                    self.assertIn("Invalid reuse witness", response.text)
                    self.assertEqual(proof, self._reuse(client))
