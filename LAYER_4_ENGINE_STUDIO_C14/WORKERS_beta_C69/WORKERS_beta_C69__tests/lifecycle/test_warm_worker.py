from contextlib import contextmanager
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
from unittest.mock import patch

from ..WORKERS_beta_C69__tests__shared import generation_fixture


def exchange(address, request):
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(20)
        client.connect(address)
        client.sendall(json.dumps(request).encode() + b"\n")
        with client.makefile("rb") as stream:
            first = json.loads(stream.readline())
            return (
                (first, json.loads(stream.readline()))
                if first.get("accepted")
                else (first, None)
            )


@contextmanager
def broker(address):
    process = subprocess.Popen(
        [
            sys.executable,
            "-B",
            "-m",
            "WORKERS_beta_C69.warm_worker",
            "--socket",
            address,
        ]
    )
    try:
        deadline = time.monotonic() + 20
        while (
            not Path(address).exists()
            and process.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.02)
        assert Path(address).exists(), "Warm Worker did not open its socket"
        yield process
    finally:
        process.terminate()
        process.wait(timeout=5)


class WarmWorkerTest(unittest.TestCase):
    def test_missing_deadline_requires_disabled_test_image_deadlines(self):
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            address = str(root / "worker.sock")
            request, _ = self.ticket_delta(root)
            for setting in (None, "1", "0"):
                with self.subTest(setting=setting), patch.dict(os.environ):
                    if setting is None:
                        os.environ.pop(switch, None)
                    else:
                        os.environ[switch] = setting
                    with broker(address):
                        ack, reply = exchange(
                            address, request | {"start_by": None}
                        )
                        self.assertEqual(setting == "0", ack["accepted"])
                        if setting == "0":
                            self.assertEqual(
                                "base", reply["result"]["base_generation"]
                            )
                        self.assertEqual(
                            ({"accepted": False}, None),
                            exchange(address, request | {"start_by": 0}),
                        )

    def test_warm_worker(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            self._check_worker(Path(tmp).resolve())

    def ticket_delta(self, tmp_path):
        root = tmp_path / "project"
        tickets = root / "_anechoic_test" / "__TKT"
        tickets.mkdir(parents=True)
        manifest = root / "AN-S-1-PROJECT_MANIFEST--test.md"
        manifest.write_text("Pinned bytes")
        ticket = tickets / "AN-T-2--ticket.md"
        ticket.write_text(
            (
                "---\natom_family: TKT\natom_id: AN-T-2\ncontainer: "
                "{component: C00}\npriority: 2\ncontext: {template: "
                "task}\nstate: {status: active, version: 1, updated_at: "
                "'2026-11-22T00:00:00Z'}\n---\n\n## Summary\n\nChanged "
                "ticket.\n"
            )
        )
        binding = {
            "root": str(root),
            "control_root": "_anechoic_test",
            "manifest_path": manifest.name,
            "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
            "project_prefix": "AN",
        }
        reuse = {
            "base_generation": "base",
            "inputs": {},
            "graph_config": {},
            "endpoints": {
                "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                "CONTAINS": [{}, True],
            },
        }
        return {
            "kind": "ticket_delta",
            "binding": binding,
            "reuse": reuse,
            "paths": [ticket.relative_to(root).as_posix()],
        }, ticket

    def _check_worker(self, tmp_path):
        request, ticket = self.ticket_delta(tmp_path)
        paths = request["paths"]
        runtime = tmp_path / "runtime"
        runtime.mkdir(mode=0o700)
        address = str(runtime / "worker.sock")
        with broker(address) as process:
            assert exchange(address, {"kind": "health"})[0] == {
                "ready": True,
                "pid": process.pid,
            }
            assert Path(address).stat().st_mode & 0o777 == 0o600
            request["start_by"] = time.monotonic() + 20
            ack, reply = exchange(address, request)
            self.assertTrue(ack["accepted"])
            self.assertNotEqual(process.pid, ack["pid"])
            result = reply["result"]
            self.assertEqual("base", result["base_generation"])
            self.assertEqual(
                sha256(ticket.read_bytes()).hexdigest(),
                result["carrier_hashes"][paths[0]],
            )
            self.assertEqual(
                [["_anechoic_test/__TKT", ticket.name]], result["paths"]
            )
            self.assertEqual(
                ["AN-T-2"],
                [atom["reference"] for atom in result["snapshot"]["atoms"]],
            )
            self.assertEqual(reply, exchange(address, request)[1])
            reuse = request["reuse"]
            assert exchange(address, {**request, "start_by": 0}) == (
                {"accepted": False},
                None,
            )
            assert exchange(address, {**request, "paths": []}) == (
                {"accepted": False},
                None,
            )
            self._check_rejections(address, request, reply, reuse)
            ack, reply = exchange(address, {**request, "paths": ["../bad.md"]})
            self.assertTrue(ack["accepted"])
            self.assertEqual({"result": None}, reply)
            self._check_indexed(tmp_path, address, process.pid)

    def _check_rejections(self, address, request, reply, reuse):
        for invalid in (
            request | {"extra": True},
            request | {"kind": "other"},
            request | {"binding": request["binding"] | {"root": ""}},
            request | {"paths": ["valid", 1]},
            request | {"paths": ["x"] * 33},
            request | {"start_by": True},
            request | {"reuse": {}},
            request | {"reuse": reuse | {"folder_hashes": {}}},
            request | {"reuse": reuse | {"endpoints": []}},
        ):
            self.assertEqual(
                ({"accepted": False}, None), exchange(address, invalid)
            )
        checkpoint = reuse | {"carrier_hashes": {}, "folder_hashes": {}}
        self.assertEqual(
            reply, exchange(address, request | {"reuse": checkpoint})[1]
        )

    def _check_indexed(self, tmp_path, address, parent_pid):
        project = tmp_path / "indexed"
        project.mkdir()
        binding, _, manifest = generation_fixture(str(project))
        manifest.unlink()
        indexed = {
            "max_number": "100",
            "manifest_ref": "AN-S-1@1",
            "component_ids": ["C00"],
            "ticket_labels": ["Task"],
            "endpoints": {
                "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                "CONTAINS": [{}, True],
            },
        }
        job = {
            "binding": binding,
            "name": "atom_lifecycle_create_draft",
            "base_generation": "base",
            "structure_sha256": "admitted",
            "indexed_task": indexed,
            "arguments": {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nWarm canary.\n",
                }
            },
        }
        envelope = {
            "kind": "indexed_lifecycle",
            "start_by": time.monotonic() + 20,
            "request": job,
        }
        ack, reply = exchange(address, envelope)
        self._check_indexed_reply(
            binding, address, parent_pid, envelope, ack, reply
        )

    def _check_indexed_reply(
        self, binding, address, parent_pid, envelope, ack, reply
    ):
        self.assertTrue(ack["accepted"])
        self.assertNotEqual(parent_pid, ack["pid"])
        result = reply["result"]
        self.assertIsNone(result["projection_error"])
        draft = result["lifecycle"]["savedDraft"]
        self.assertEqual("AN-T-101@1-draft", draft["ref_id"])
        path = Path(binding["root"]) / draft["path"]
        self.assertEqual(
            {draft["path"]: sha256(path.read_bytes()).hexdigest()},
            result["delta"]["carrier_hashes"],
        )
        self.assertEqual(
            {"ready": True, "pid": parent_pid},
            exchange(address, {"kind": "health"})[0],
        )
        self.assertEqual(
            ({"accepted": False}, None),
            exchange(address, {**envelope, "request": {}}),
        )
        self.assertEqual(
            ({"accepted": False}, None),
            exchange(address, envelope | {"extra": True}),
        )
