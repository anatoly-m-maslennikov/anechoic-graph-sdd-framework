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

from .. import carrier_checkpoint
from ..DATABASE_SERVER_beta_C71__shared import create_app, open_database
from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _launch_arguments, _query, _server
from .test_native_atoms import _digest
from .test_native_refresh import graph_payload


def _path(atom):
    return str(PurePosixPath(atom["relative_path"]) / atom["filename"])


def _folder(filename, digest):
    return sha256(json.dumps([[filename, digest]], ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _baseline():
    data = graph_payload()
    current, archived = data["snapshot"]["atoms"]
    archived["relative_path"] += "/09_archived"
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    witness = {"inputs": {"manifest": "a" * 64, "graph": "b" * 64, "carrier_schema": "c" * 64},
               "graph_config": {}, "endpoints": json.loads(data["model"])["bindings"]["endpoints"]}
    return data | {"reuse": witness, "carrier_hashes": {_path(current): "a" * 64, _path(archived): "b" * 64}}


def _delta(base, snapshot, paths, atoms, hashes):
    payload = {"paths": paths, "carrier_hashes": hashes,
               "snapshot": snapshot | {"atoms": atoms, "relations": []}}
    return BINDING | {"base_generation": base, **payload, "snapshot_sha256": _digest(payload)}


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


class StartupCheckpointTests(unittest.TestCase):
    def _accepted(self, client, route, payload):
        response = client.put(route, json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def _reuse(self, client):
        return client.get("/generation/reuse", params=BINDING).json()["result"]

    def _assert_disk_checkpoint(self, database, hashes, folders, changes):
        with duckdb.connect(str(database), read_only=True) as connection:
            self.assertEqual(hashes, dict(connection.execute(
                "SELECT path, digest FROM ops_generation_carrier_digests"
            ).fetchall()))
            self.assertEqual(folders, dict(connection.execute("SELECT * FROM ops_generation_folder_hashes").fetchall()))
            self.assertEqual(changes, dict(connection.execute("SELECT * FROM ops_generation_carrier_changes").fetchall()))

    def test_reuse_reports_generation_model_status_domains(self):
        data = _baseline()
        model = json.loads(data["model"])
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        model["bindings"]["declarations"] = [
            [name, {"kind": "entity", "arguments": {"entity_name": "Status", "entity_kind": "Property",
             "relation_name": "IS_PROPERTY_OF", "base_path": root + ".Header.State",
             "applies_to_entity_classes": [root + "//" + name], "allowed_values": values}}]
            for name, values in (("Specification", ["draft", "active", "archived"]),
                                 ("Ticket", ["draft", "active", "reviewed", "archived"]),
                                 ("project_config", ["draft", "active", "archived"]))
        ]
        data["model"] = json.dumps(model)
        data["receipt"]["model_descriptor_sha256"] = sha256(data["model"].encode()).hexdigest()
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        with _server_without_lifespan(Path(directory).resolve() / "projection.duckdb") as client:
            generation = self._accepted(client, "/generation", data)
            result = self._reuse(client)
            self.assertEqual(generation, result["base_generation"])
            self.assertEqual(["active", "archived", "draft", "reviewed"], result["status_domains"]["T"])
            self.assertEqual(result["status_domains"]["P"], result["status_domains"]["C"])

    def test_control_folder_named_archive_is_foreground(self):
        connection = duckdb.connect(":memory:")
        self.addCleanup(connection.close)
        carrier_checkpoint.initialize_checkpoint(connection)
        carrier_checkpoint._replace_checkpoint(connection, {"09_archived/a.md": "a" * 64,
                                                            "09_archived/09_archived/b.md": "b" * 64})
        self.assertEqual({"09_archived/a.md": "a" * 64}, carrier_checkpoint.read_checkpoint(connection, "foreground"))
        self.assertEqual({"09_archived/09_archived/b.md": "b" * 64}, carrier_checkpoint.read_checkpoint(connection, "archive"))

    def test_scoped_checkpoint_reads_include_pending_changes(self):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        database = Path(directory).resolve() / "projection.duckdb"
        data = _baseline()
        current, archived = data["snapshot"]["atoms"]
        with _server(database) as client:
            base = self._accepted(client, "/generation", data)
            for scope, atom, digest in (("foreground", current, "a" * 64), ("archive", archived, "b" * 64)):
                result = client.get("/generation/reuse", params=BINDING | {"scope": scope}).json()["result"]
                self.assertEqual({_path(atom): digest}, result["carrier_hashes"])
                self.assertEqual({atom["relative_path"]: _folder(atom["filename"], digest)}, result["folder_hashes"])
            base = self._accepted(client, "/generation/reuse", BINDING | {"base_generation": base, "archive_pending": True})
            deleted = _delta(base, data["snapshot"], [[archived["relative_path"], archived["filename"]]], [], {})
            self._accepted(client, "/generation/archive", deleted)
            for scope, expected in (("foreground", {_path(current): "a" * 64}), ("archive", {})):
                result = client.get("/generation/reuse", params=BINDING | {"scope": scope}).json()["result"]
                self.assertEqual(scope, result["checkpoint_scope"])
                self.assertEqual(expected, result["carrier_hashes"])
                self.assertEqual({current["relative_path"]: _folder(current["filename"], "a" * 64)}
                                 if scope == "foreground" else {}, result["folder_hashes"])
            self.assertEqual({_path(current): "a" * 64}, self._reuse(client)["carrier_hashes"])

    def test_disk_checkpoint_updates_changed_folders_and_archive_against_latest_base(self):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        database = Path(directory).resolve() / "projection.duckdb"
        data = _baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        with _server(database) as client:
            first = self._accepted(client, "/generation", data)
        with _server_without_lifespan(database) as client:
            proof = self._reuse(client)
            cwd, history = current["relative_path"], archived["relative_path"]
            folder = _folder(archived["filename"], "b" * 64)
            initial_folders = {cwd: _folder(current["filename"], "a" * 64), history: folder}
            self.assertEqual(initial_folders, proof["folder_hashes"])
            moved = current | {"relative_path": f"{cwd}/new", "summary": "edited"}
            paths = [[row["relative_path"], row["filename"]] for row in (current, moved)]
            delta = _delta(first, snapshot, paths, [moved], {_path(moved): "d" * 64})
            current_base = self._accepted(client, "/generation/native-delta", delta | {"archive_pending": True})
            proof = self._reuse(client)
            self.assertTrue(proof["archive_pending"])
            self.assertEqual({moved["relative_path"]: _folder(moved["filename"], "d" * 64), history: folder},
                             proof["folder_hashes"])
            delete = _delta(first, snapshot, [[history, archived["filename"]]], [], {})
            stale = client.put("/generation/archive", json=delete)
            self.assertEqual(409, stale.status_code, stale.text)
            bad = _delta(current_base, snapshot, [paths[-1]], [], {})
            self.assertEqual(400, client.put("/generation/archive", json=bad).status_code)
            self.assertEqual(proof, self._reuse(client))
            self._accepted(client, "/generation/archive", delete | {"base_generation": current_base})
            proof = self._reuse(client)
            self.assertNotIn("archive_pending", proof)
            self.assertEqual({_path(moved): "d" * 64}, proof["carrier_hashes"])
            rows = _query(
                client, 'SELECT relative_path, "content.summary" FROM atoms'
            ).json()["result"]["rows"]
            self.assertEqual([[moved["relative_path"], "edited"]], rows)
        self._assert_disk_checkpoint(database, data["carrier_hashes"], initial_folders,
                                     {_path(current): None, _path(moved): "d" * 64, _path(archived): None})
        with _server(database) as client:
            self.assertEqual(proof, self._reuse(client))
        self._assert_disk_checkpoint(
            database, proof["carrier_hashes"], proof["folder_hashes"], {}
        )

    def test_latest_live_digest_is_retained_across_offline_reversion(self):
        directory = Path(
            self.enterContext(TemporaryDirectory(dir="/tmp"))
        ).resolve()
        database = directory / "projection.duckdb"
        data = _baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        path = _path(current)
        carrier = directory / "carrier.md"
        carrier.write_bytes(b"original")
        original = sha256(carrier.read_bytes()).hexdigest()
        data["carrier_hashes"][path] = original
        with _server_without_lifespan(database) as client:
            base = self._accepted(client, "/generation", data)
            paths = [[current["relative_path"], current["filename"]]]
            for content in (b"first edit", b"latest admitted bytes"):
                carrier.write_bytes(content)
                updated = sha256(carrier.read_bytes()).hexdigest()
                delta = _delta(
                    base, snapshot, paths, [current], {path: updated}
                )
                base = self._accepted(
                    client, "/generation/native-delta", delta
                )
        carrier.write_bytes(b"original")
        initial_folders = {
            current["relative_path"]: _folder(current["filename"], original),
            archived["relative_path"]: _folder(archived["filename"], "b" * 64),
        }
        self._assert_disk_checkpoint(
            database, data["carrier_hashes"], initial_folders, {path: updated}
        )
        with _server(database) as client:
            proof = self._reuse(client)
            self.assertEqual(base, proof["base_generation"])
            self.assertEqual(updated, proof["carrier_hashes"][path])
            self.assertNotEqual(sha256(carrier.read_bytes()).hexdigest(), proof["carrier_hashes"][path])
            self.assertEqual(_folder(current["filename"], updated), proof["folder_hashes"][current["relative_path"]])
        self._assert_disk_checkpoint(
            database, proof["carrier_hashes"], proof["folder_hashes"], {}
        )

    def test_live_checkpoint_skips_folder_rebuild_and_changes_roll_back(self):
        data = _baseline()
        current, _ = data["snapshot"]["atoms"]
        path = _path(current)
        paths = [[current["relative_path"], current["filename"]]]
        with duckdb.connect() as connection:
            carrier_checkpoint.update_checkpoint(connection, data)
            delta = _delta("base", data["snapshot"], paths, [current], {path: "c" * 64})
            with patch.object(carrier_checkpoint, "_folder_hashes") as folder_hashes:
                connection.begin()
                carrier_checkpoint.update_checkpoint(connection, delta, delta=True)
                connection.commit()
                connection.begin()
                carrier_checkpoint.update_checkpoint(connection, delta | {"carrier_hashes": {path: "d" * 64}}, delta=True)
                connection.rollback()
                folder_hashes.assert_not_called()
            self.assertEqual(data["carrier_hashes"] | {path: "c" * 64}, carrier_checkpoint.read_checkpoint(connection))
            connection.begin()
            carrier_checkpoint.fold_checkpoint(connection)
            connection.rollback()
            self.assertEqual([(path, "c" * 64)],
                             connection.execute("SELECT * FROM ops_generation_carrier_changes").fetchall())
            self.assertEqual(data["carrier_hashes"], dict(connection.execute(
                "SELECT path, digest FROM ops_generation_carrier_digests"
            ).fetchall()))

    def test_missing_and_empty_checkpoint_remain_distinct(self):
        snapshot = {"schema_version": 2, "atoms": []}
        empty = {"snapshot": snapshot, "carrier_hashes": {}}
        full = _baseline()
        current, _ = full["snapshot"]["atoms"]
        delta = _delta("base", full["snapshot"], [[current["relative_path"], current["filename"]]],
                       [current], {_path(current): "d" * 64})
        with duckdb.connect() as connection:
            carrier_checkpoint.update_checkpoint(connection, delta, delta=True)
            self.assertIsNone(carrier_checkpoint.read_checkpoint(connection))
            carrier_checkpoint.update_checkpoint(connection, empty)
            self.assertEqual({}, carrier_checkpoint.read_checkpoint(connection))
            carrier_checkpoint.update_checkpoint(connection, delta, delta=True)
            self.assertEqual(delta["carrier_hashes"], carrier_checkpoint.read_checkpoint(connection))
            carrier_checkpoint.update_checkpoint(connection, {"snapshot": snapshot}, delta=True)
            self.assertIsNone(carrier_checkpoint.read_checkpoint(connection))
            self.assertEqual([], connection.execute("SELECT * FROM ops_generation_carrier_changes").fetchall())

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

    def test_conditional_archive_reuse_and_replacement_preserve_off_path_archives(self):
        data = _baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        off_path = archived | {
            "relative_path": current["relative_path"],
            "reference": "AN-T-1@3",
            "exact_ref": "AN-T-1@3",
            "version": 3,
            "filename": "AN-T-1@3-extra.md",
        }
        snapshot["atoms"].append(off_path)
        data["carrier_hashes"][_path(off_path)] = "d" * 64
        data["receipt"]["snapshot_sha256"] = _digest(snapshot)
        with _server() as client:
            base = self._accepted(client, "/generation", data)
            pending = BINDING | {"base_generation": base, "archive_pending": True}
            stale = client.put("/generation/reuse", json=pending | {"base_generation": "stale"})
            self.assertEqual(409, stale.status_code, stale.text)
            self._accepted(client, "/generation/reuse", pending)
            self.assertTrue(self._reuse(client)["archive_pending"])
            complete = BINDING | {"base_generation": base, "unchanged": True}
            self.assertEqual(base, self._accepted(client, "/generation/archive", complete))
            self.assertNotIn("archive_pending", self._reuse(client))
            self._accepted(client, "/generation/reuse", pending)
            empty = snapshot | {"atoms": [], "relations": []}
            replacement = BINDING | {"base_generation": base, "snapshot": empty, "snapshot_sha256": _digest(empty),
                                     "carrier_hashes": {}, "replace": True}
            self._accepted(client, "/generation/archive", replacement)
            proof = self._reuse(client)
            self.assertNotIn("archive_pending", proof)
            self.assertEqual({_path(current): "a" * 64, _path(off_path): "d" * 64}, proof["carrier_hashes"])
            self.assertEqual([[off_path["exact_ref"]]], _query(client,
                "SELECT exact_ref FROM native_references WHERE status_group = 'Archived'").json()["result"]["rows"])
