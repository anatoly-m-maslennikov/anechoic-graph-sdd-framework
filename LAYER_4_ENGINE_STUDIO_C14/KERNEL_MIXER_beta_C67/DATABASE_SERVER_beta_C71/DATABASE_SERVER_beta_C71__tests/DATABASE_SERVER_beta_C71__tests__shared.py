"""CLI fixtures shared by the Database Server tests."""

from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

import httpx2

ENGINE = Path(__file__).resolve().parents[3]
MODULE = (
    "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__"
    "shared"
)
PIN = "a" * 64
BINDING = {"instance_id": "instance"}


def _launch_arguments(socket, database=None, pin=PIN, instance="instance"):
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        MODULE,
        "--socket",
        str(socket),
        "--instance-id",
        instance,
        "--manifest-sha256",
        pin,
    ]
    if database is not None:
        command.extend(("--database-path", str(database)))
    env = {**os.environ, "PYTHONPATH": str(ENGINE)}
    extension_dir = ENGINE.parent / ".anechoic_tmp/workbench/extensions"
    if extension_dir.is_dir():
        env.setdefault(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(extension_dir)
        )
    return command, env


@contextmanager
def _server(database=None, *arguments):
    with TemporaryDirectory(prefix="ane-db-test-", dir="/tmp") as directory:
        socket = Path(directory).resolve() / "db.sock"
        command, env = _launch_arguments(socket, database)
        process = subprocess.Popen([*command, *arguments], env=env)
        try:
            until = monotonic() + 10
            while (
                not socket.exists()
                and process.poll() is None
                and monotonic() < until
            ):
                sleep(0.03)
            if not socket.exists() or os.stat(socket).st_mode & 0o077:
                raise AssertionError(
                    "Database did not start with a private socket"
                )
            with httpx2.Client(
                transport=httpx2.HTTPTransport(uds=str(socket)),
                base_url="http://private",
                timeout=5,
                trust_env=False,
            ) as client:
                yield client
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)


def _generation():
    model = json.dumps(
        {
            "model_sha256": "b" * 64,
            "binding_schema": 1,
            "modules": {"__init__.py": sha256(b"").hexdigest()},
            "module_sources": {"__init__.py": ""},
            "module_order": [],
            "class_modules": {},
            "bindings": {},
        },
        indent=2,
    )
    structure = json.dumps(
        {
            "model_sha256": "b" * 64,
            "project": {"ref": "AN-S-1", "sha256": PIN},
            "components": {},
        },
        indent=2,
    )
    return {
        **BINDING,
        "snapshot": {
            "manifest_sha256": PIN,
            "atoms": [{"reference": "one", "summary": "first"}],
        },
        "model": model,
        "structure": structure,
        "graph": None,
        "receipt": {
            "manifest_sha256": PIN,
            "model_sha256": "b" * 64,
            "graph_sha256": sha256(b"null").hexdigest(),
            "model_descriptor_sha256": sha256(model.encode()).hexdigest(),
            "structure_sha256": sha256(structure.encode()).hexdigest(),
        },
    }


def _query(client, sql, **fields):
    return client.post("/database", json={**BINDING, "sql": sql, **fields})
