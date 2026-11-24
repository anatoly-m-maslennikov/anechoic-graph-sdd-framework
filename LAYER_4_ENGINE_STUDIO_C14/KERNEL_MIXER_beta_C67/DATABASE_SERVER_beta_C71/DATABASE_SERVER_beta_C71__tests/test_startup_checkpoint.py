"""Exercise persisted startup and Archive checkpoint admission."""
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _query, _server
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


class StartupCheckpointTests(unittest.TestCase):
    def _accepted(self, client, route, payload):
        response = client.put(route, json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def _reuse(self, client):
        return client.get("/generation/reuse", params=BINDING).json()["result"]

    def test_disk_checkpoint_updates_changed_folders_and_archive_against_latest_base(self):
        directory = self.enterContext(TemporaryDirectory(dir="/tmp"))
        database = Path(directory).resolve() / "projection.duckdb"
        data = _baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        with _server(database) as client:
            first = self._accepted(client, "/generation", data)
        with _server(database) as client:
            proof = self._reuse(client)
            cwd, history = current["relative_path"], archived["relative_path"]
            folder = _folder(archived["filename"], "b" * 64)
            self.assertEqual({cwd: _folder(current["filename"], "a" * 64), history: folder}, proof["folder_hashes"])
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
            rows = _query(client, 'SELECT relative_path, "content.summary" FROM atoms').json()["result"]["rows"]
            self.assertEqual([[moved["relative_path"], "edited"]], rows)

    def test_conditional_archive_reuse_and_replacement_preserve_off_path_archives(self):
        data = _baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        off_path = archived | {"relative_path": current["relative_path"], "reference": "AN-T-1@3",
                               "exact_ref": "AN-T-1@3", "version": 3, "filename": "AN-T-1@3-extra.md"}
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
