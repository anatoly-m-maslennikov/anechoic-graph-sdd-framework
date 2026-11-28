"""Support the C71 formal console tests."""

import hashlib
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from tempfile import TemporaryDirectory

ROOT = next(
    path
    for path in Path(__file__).resolve().parents
    if (path / "_anechoic_anechoic").is_dir()
)

PIN = "a" * 64
BINDING = {"instance_id": "instance"}


class UnixHTTP(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=5)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class Client:
    def __init__(self, path):
        self.path = path

    def request(self, method, path, payload):
        connection = UnixHTTP(self.path)
        try:
            connection.request(
                method,
                path,
                json.dumps(payload),
                {"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()


def generation():
    model = json.dumps(
        {
            "model_sha256": "b" * 64,
            "binding_schema": 1,
            "modules": {"__init__.py": hashlib.sha256(b"").hexdigest()},
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
    return BINDING | {
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
            "graph_sha256": hashlib.sha256(b"null").hexdigest(),
            "model_descriptor_sha256": hashlib.sha256(
                model.encode()
            ).hexdigest(),
            "structure_sha256": hashlib.sha256(structure.encode()).hexdigest(),
        },
    }


@contextmanager
def _server(_database, *arguments):
    with TemporaryDirectory(
        prefix="ane-formal-server-", dir="/tmp"
    ) as directory:
        path = str(Path(directory).resolve() / "db.sock")
        module = (
            "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71."
            "DATABASE_SERVER_beta_C71__shared"
        )
        env = _server_env()
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                module,
                "--socket",
                path,
                "--instance-id",
                "instance",
                "--manifest-sha256",
                PIN,
                *arguments,
            ],
            env=env,
        )
        try:
            until = time.monotonic() + 10
            while (
                not Path(path).exists()
                and process.poll() is None
                and time.monotonic() < until
            ):
                time.sleep(0.03)
            if not Path(path).exists():
                raise AssertionError("Database server did not start")
            yield Client(path)
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)


def call(client, operation, arguments):
    return client.request(
        "POST",
        "/workspace",
        BINDING | {"operation": operation, "arguments": arguments},
    )


def _server_env():
    env = os.environ | {"PYTHONPATH": str(ROOT / "LAYER_4_ENGINE_STUDIO_C14")}
    extensions = ROOT / ".anechoic_tmp/workbench/extensions"
    if extensions.is_dir():
        env.setdefault("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(extensions))
    return env
