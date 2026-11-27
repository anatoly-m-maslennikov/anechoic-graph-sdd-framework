"""Admitted Project selection arguments at the entrypoint boundary."""

# ruff: noqa: E402
import os
from pathlib import Path
import sys
import json
from http.server import BaseHTTPRequestHandler
from socketserver import UnixStreamServer
import tempfile
import threading
import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    http_main,
    runtime_stack,
    select_runtime_project,
)
from . import test_native_host_launcher as host_fixture


def _backend_handler(selection, requests):
    class Backend(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            body = (
                {
                    "instance_id": selection.instance_id,
                    "manifest_sha256": selection.manifest_sha256,
                    "pid": os.getpid(),
                    "kernel_pid": os.getpid(),
                    "generation": "fixture",
                    "state": "ready",
                }
                if self.path == "/health"
                else {"result": {"tools": [], "blacklist": []}}
            )
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Backend


class ProjectContextTests(unittest.TestCase):
    def setUp(self):
        host_fixture.NativeHostLauncherTests.setUp(self)
        self.selections = [select_runtime_project(self.root)]

    def test_docker_entrypoint_forwards_only_admitted_selection_arguments(
        self,
    ):
        import importlib.util

        path = MCP / "docker/entrypoint.py"
        specification = importlib.util.spec_from_file_location(
            "project_selection_entrypoint", path
        )
        entrypoint = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(entrypoint)
        selection = self.selections[0]
        values = {
            "ANECHOIC_RUNTIME_STACK": "current",
            "ANECHOIC_CONTROL_ROOT": selection.control_relative.as_posix(),
            "ANECHOIC_PROJECT_INSTANCE_ID": selection.instance_id,
            "ANECHOIC_HOST_PROJECT_ROOT": str(selection.host_root),
            "ANECHOIC_MCP_HTTP_SECRET_TOKEN": "private",
        }
        with (
            patch.object(sys, "argv", ["entrypoint", "mcp-http"]),
            patch.dict(os.environ, values),
            patch.object(os, "execve") as execute,
        ):
            entrypoint.main()
        arguments = execute.call_args.args[1]
        self.assertEqual(
            selection.control_relative.as_posix(),
            arguments[arguments.index("--control-root") + 1],
        )
        self.assertEqual(
            selection.instance_id,
            arguments[arguments.index("--instance-id") + 1],
        )
        self.assertNotIn("private", arguments)

    def test_beta_next_http_uses_the_supervised_api_socket(self):
        selection = self.selections[0]
        runtime_stack.cache_clear()
        self.addCleanup(runtime_stack.cache_clear)
        requests = []

        backend_handler = _backend_handler(selection, requests)

        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            socket = str(Path(directory) / "api.sock")
            with UnixStreamServer(socket, backend_handler) as backend:
                thread = threading.Thread(
                    target=backend.serve_forever, daemon=True
                )
                thread.start()
                try:

                    def serve(app, **kwargs):
                        with TestClient(app):
                            pass

                    with (
                        patch.dict(
                            os.environ,
                            {
                                "ANECHOIC_RUNTIME_STACK": "beta_next",
                                "ANECHOIC_BETA_BACKEND_SOCKET": socket,
                            },
                        ),
                        patch("uvicorn.run", side_effect=serve),
                    ):
                        http_main(["--project-root", str(selection.root)])
                finally:
                    backend.shutdown()
                    thread.join(timeout=5)
        self.assertIn("/health", requests)
        self.assertTrue(
            any(path.startswith("/tools?") for path in requests), requests
        )


if __name__ == "__main__":
    unittest.main()
