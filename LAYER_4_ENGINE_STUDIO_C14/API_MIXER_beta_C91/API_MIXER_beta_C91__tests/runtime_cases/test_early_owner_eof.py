"""Check owner EOF before the initial Project generation is admitted."""

from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import httpx2

from ..archive_cases.archive_cases__shared import ENGINE, OWNER, write_manifest


def owner_command(runtime, root, manifest, digest):
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        OWNER,
        "--socket",
        str(runtime / "api.sock"),
        "--instance-id",
        "early-eof",
        "--project-root",
        str(root),
        "--control-root",
        manifest.parent.name,
        "--manifest-path",
        manifest.relative_to(root).as_posix(),
        "--manifest-sha256",
        digest,
        "--project-prefix",
        "AN",
        "--workbench-storage",
        "memory",
    ]
    env = {
        **os.environ,
        "PYTHONPATH": str(ENGINE),
        "ANECHOIC_RUNTIME_PROFILE": "test",
        "ANECHOIC_WORKBENCH_STORAGE": "memory",
        "ANECHOIC_JOURNAL_STORAGE": "files",
        "ANECHOIC_ARCHIVES": "load",
        "ANECHOIC_LOG_LEVEL": "ERROR",
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
        ),
    }
    return command, env


class EarlyOwnerEofTest(unittest.TestCase):
    def test_eof_before_initial_admission_cleans_peers(self):
        with tempfile.TemporaryDirectory(
            prefix="ane-early-eof-", dir="/tmp"
        ) as directory:
            runtime = Path(directory).resolve()
            root = runtime / "project"
            root.mkdir()
            manifest = write_manifest(root)
            digest = sha256(manifest.read_bytes()).hexdigest()
            command, env = owner_command(runtime, root, manifest, digest)
            with subprocess.Popen(
                command,
                cwd=ENGINE,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            ) as owner:
                try:
                    kernel = self.wait_for_unadmitted_kernel(runtime, owner)
                    self.assertFalse((runtime / "peers.ready").exists())
                    owner.stdin.close()
                    self.assertEqual(0, owner.wait(timeout=15))
                    for name in (
                        "peers.ready",
                        "api.sock",
                        "db.sock",
                        "jobs.sock",
                    ):
                        self.assertFalse((runtime / name).exists(), name)
                    with self.assertRaises(ProcessLookupError):
                        os.kill(kernel["pid"], 0)
                finally:
                    if not owner.stdin.closed:
                        owner.stdin.close()
                    if owner.poll() is None:
                        owner.kill()
                        owner.wait(timeout=10)

    def wait_for_unadmitted_kernel(self, runtime, owner):
        client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(runtime / "db.sock")),
            base_url="http://private",
            timeout=1,
            trust_env=False,
        )
        try:
            deadline = time.monotonic() + 30
            while owner.poll() is None and time.monotonic() < deadline:
                if not (runtime / "db.sock").is_socket():
                    time.sleep(0.02)
                    continue
                try:
                    health = client.get("/health").json()["result"]
                    if (
                        health["instance_id"] == "early-eof"
                        and not health["ready"]
                        and health["generation"] is None
                    ):
                        return health
                except httpx2.TransportError, KeyError, ValueError:
                    pass
                time.sleep(0.02)
        finally:
            client.close()
        self.fail(
            (
                "Kernel did not report unadmitted state before EOF; owner "
                "exit="
                f"{owner.poll()}"
            )
        )
