from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from ..DATABASE_SERVER_beta_C71__shared import create_app, open_database

from .DATABASE_SERVER_beta_C71__tests__shared import _server
from .test_native_atoms import _native_generation


def _stage(directory, frames):
    raw = b"".join(json.dumps(frame, separators=(",", ":")).encode() + b"\n" for frame in frames)
    path = Path(directory).resolve() / "generation-batches.jsonl"
    path.write_bytes(raw)
    return {"path": str(path), "sha256": sha256(raw).hexdigest(), "bytes": len(raw)}


def _frames(data):
    snapshot = dict(data["snapshot"])
    lists = {key: value for key, value in snapshot.items() if isinstance(value, list)}
    snapshot.update({key: [] for key in lists})
    hashes = [[str(Path(atom["relative_path"]) / atom["filename"]), "a" * 64] for atom in data["snapshot"].get("atoms", []) if "filename" in atom]
    return ([{"snapshot": snapshot, "graph": data["graph"], "carrier_hashes": {}}]
            + [["snapshot", key, rows] for key, rows in lists.items()]
            + [["carrier_hashes", "", hashes]])


class BatchGenerationTest(unittest.TestCase):
    def test_reject_tampering_and_bad_frames(self):
        data = _native_generation()
        with tempfile.TemporaryDirectory(prefix="anechoic-generation-") as directory, _server() as client:
            frames = _frames(data)
            descriptor = _stage(directory, frames)
            request = {k: v for k, v in data.items() if k not in {"snapshot", "graph", "carrier_hashes"}}

            def reject(pin):
                reply = client.put("/generation", json=request | {"batch_artifact": pin})
                self.assertEqual(400, reply.status_code, reply.text)

            reject(descriptor | {"sha256": "0" * 64})
            for bad in (["snapshot", "missing", []], ["carrier_hashes", "", [["a", "x"], ["a", "y"]]]):
                reject(_stage(directory, frames + [bad]))
            path = Path(descriptor["path"])
            raw = b'{"snapshot":{},"snapshot":{},"graph":null,"carrier_hashes":{}}\n'
            path.write_bytes(raw)
            reject({"path": str(path), "sha256": sha256(raw).hexdigest(), "bytes": len(raw)})
            path.unlink()
            path.symlink_to("/etc/passwd")
            reject(descriptor)

    def test_admission_is_atomic_and_instance_checked_first(self):
        data = _native_generation()
        with (tempfile.TemporaryDirectory(prefix="anechoic-generation-") as directory,
              open_database() as connection,
              TestClient(create_app(connection, data["instance_id"], data["receipt"]["manifest_sha256"])) as client):
            frames = _frames(data)
            descriptor = _stage(directory, frames)
            request = {k: v for k, v in data.items() if k not in {"snapshot", "graph"}} | {"batch_artifact": descriptor}
            self.assertEqual(client.put('/generation', json=request | {"instance_id": "foreign", "batch_artifact": {}}).status_code, 403)
            admitted = client.put('/generation', json=request)
            self.assertEqual(admitted.status_code, 200, admitted.text)
            generation = admitted.json()['result']['generation']
            descriptor = _stage(directory, frames + [["snapshot", "bad", []]])
            rejected = client.put('/generation', json=request | {"batch_artifact": descriptor})
            self.assertEqual(rejected.status_code, 400, rejected.text)
            self.assertEqual(client.get('/health').json()['result']['generation'], generation)
            invalid_hashes = [frame for frame in frames if isinstance(frame, dict) or frame[0] != 'carrier_hashes'] + [['carrier_hashes', '', []]]
            descriptor = _stage(directory, invalid_hashes)
            rejected = client.put('/generation', json=request | {'batch_artifact': descriptor})
            self.assertEqual(rejected.status_code, 400, rejected.text)
            self.assertEqual(client.get('/health').json()['result']['generation'], generation)
            descriptor = _stage(directory, frames)
            with patch("KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.generation.replace",
                       side_effect=ValueError("late admission failure")):
                rejected = client.put("/generation", json=request | {"batch_artifact": descriptor})
            self.assertEqual(400, rejected.status_code, rejected.text)
            self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
