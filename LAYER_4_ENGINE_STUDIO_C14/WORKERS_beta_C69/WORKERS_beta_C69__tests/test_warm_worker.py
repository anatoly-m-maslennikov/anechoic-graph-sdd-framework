import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from hashlib import sha256
from pathlib import Path


def exchange(address, request):
    with socket.socket(socket.AF_UNIX) as client:
        client.connect(address)
        client.sendall(json.dumps(request).encode() + b"\n")
        with client.makefile("rb") as stream:
            first = json.loads(stream.readline())
            return (first, json.loads(stream.readline())) if first.get("accepted") else (first, None)


class WarmWorkerTest(unittest.TestCase):
    def test_warm_worker(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            self._check_worker(Path(tmp).resolve())

    def _check_worker(self, tmp_path):

        root = tmp_path / "project"
        tickets = root / "_anechoic_test" / "__TKT"
        tickets.mkdir(parents=True)
        manifest = root / "AN-S-1-PROJECT_MANIFEST--test.md"
        manifest.write_text("Pinned bytes")
        ticket = tickets / "AN-T-2--ticket.md"
        ticket.write_text("---\natom_family: TKT\natom_id: AN-T-2\ncontainer: {component: C00}\npriority: 2\ncontext: {template: task}\nstate: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}\n---\n\n## Summary\n\nChanged ticket.\n")
        binding = {"root": str(root), "control_root": "_anechoic_test", "manifest_path": manifest.name,
                   "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(), "project_prefix": "AN"}
        reuse = {"base_generation": "base", "inputs": {}, "graph_config": {},
                 "endpoints": {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}}
        paths = [ticket.relative_to(root).as_posix()]
        runtime = tmp_path / "runtime"
        runtime.mkdir(mode=0o700)
        address = str(runtime / "worker.sock")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        process = subprocess.Popen([sys.executable, "-B", "-m", "WORKERS_beta_C69.warm_worker", "--socket", address], env=env)

        try:
            for _ in range(200):
                if Path(address).exists():
                    break
                assert process.poll() is None
                time.sleep(0.01)
            assert exchange(address, {"kind": "health"})[0] == {"ready": True, "pid": process.pid}
            assert Path(address).stat().st_mode & 0o777 == 0o600
            request = {"kind": "ticket_delta", "start_by": time.monotonic() + 20,
                       "binding": binding, "reuse": reuse, "paths": paths}
            ack, reply = exchange(address, request)
            self.assertTrue(ack["accepted"])
            self.assertNotEqual(process.pid, ack["pid"])
            result = reply["result"]
            self.assertEqual("base", result["base_generation"])
            self.assertEqual(sha256(ticket.read_bytes()).hexdigest(), result["carrier_hashes"][paths[0]])
            self.assertEqual([["_anechoic_test/__TKT", ticket.name]], result["paths"])
            self.assertEqual(["AN-T-2"], [atom["reference"] for atom in result["snapshot"]["atoms"]])
            self.assertEqual(reply, exchange(address, request)[1])
            assert exchange(address, {**request, "start_by": 0}) == ({"accepted": False}, None)
            assert exchange(address, {**request, "paths": []}) == ({"accepted": False}, None)
            ack, reply = exchange(address, {**request, "paths": ["../bad.md"]})
            self.assertTrue(ack["accepted"])
            self.assertEqual({"result": None}, reply)
        finally:
            process.terminate()
            process.wait(timeout=5)
