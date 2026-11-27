"""Check the MCP HTTP request limit through the documented server process."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from uuid import uuid4

import httpx2

from .FEATURE_MCP__tests__shared import project
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import MCP_PATH

ENGINE = Path(__file__).resolve().parents[3]
CURRENT_RELEASE_ENVELOPE_BYTES = 7_266_044
MAX_REQUEST_BODY_SIZE = 16 * 1024 * 1024


class HttpRequestBodyLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("0.0.0.0", 8092))
        root = Path(cls.enterClassContext(tempfile.TemporaryDirectory())).resolve()
        project(root)
        marker = uuid4().hex
        task = root / "_anechoic_anechoic/__TICKETS/TASKS/AN-T-9999999-TASK--probe.md"
        task.parent.mkdir(parents=True, exist_ok=True)
        task.write_text("---\natom_family: TKT\natom_id: AN-T-9999999\ncontainer: {component: C00}\n"
                        "priority: 2\ncontext: {template: task}\nstate: {status: active, version: 1, "
                        "updated_at: '2026-11-22T00:00:00Z'}\n---\n\n## Summary\n\n" + marker + "\n")
        log = cls.enterClassContext(tempfile.TemporaryFile(mode="w+"))
        environment = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_STACK": "beta_next",
                       "PYTHONDONTWRITEBYTECODE": "1", "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                           "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))}
        cls.process = subprocess.Popen(
            [sys.executable, "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server",
             "--project-root", str(root), "--transport", "streamable-http"],
            cwd=ENGINE.parent, env=environment, stdout=log, stderr=log,
        )
        cls.addClassCleanup(cls.stop_process, cls.process)
        cls.client = cls.enterClassContext(httpx2.Client(base_url="http://127.0.0.1:8092", timeout=30, trust_env=False,
                                                         headers={"content-type": "application/json"}))
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if cls.process.poll() is not None:
                break
            try:
                response = cls.client.get("/anechoic/health")
                if response.status_code == 200 and response.json().get("state") == "ready":
                    identity = cls.client.post("/anechoic/Anechoic/api/run", json={
                        "sql": "SELECT \"content.summary\" FROM atoms WHERE reference='AN-T-9999999'",
                        "result_delivery": "inline",
                    })
                    if (identity.status_code == 200 and identity.json().get("rows") == [[marker]]
                            and cls.process.poll() is None):
                        return
            except (httpx2.TransportError, ValueError):
                pass
            time.sleep(.1)
        log.seek(0)
        raise RuntimeError("MCP HTTP process did not become ready: " + log.read()[-8000:])

    @staticmethod
    def stop_process(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("0.0.0.0", 8092))

    @staticmethod
    def current_size_initialize() -> bytes:
        value = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "body-limit-fixture", "version": "1"},
                "_meta": {"padding": ""},
            },
        }
        base = json.dumps(value, separators=(",", ":")).encode()
        value["params"]["_meta"]["padding"] = "x" * (
            CURRENT_RELEASE_ENVELOPE_BYTES - len(base)
        )
        return json.dumps(value, separators=(",", ":")).encode()

    def test_current_release_envelope_size_is_admitted_to_real_mcp_transport(
        self,
    ):
        body = self.current_size_initialize()
        self.assertEqual(len(body), CURRENT_RELEASE_ENVELOPE_BYTES)
        self.assertGreater(len(body), 4 * 1024 * 1024)
        self.assertLess(len(body), MAX_REQUEST_BODY_SIZE)
        response = self.client.post(
            MCP_PATH,
            headers={"accept": "application/json, text/event-stream"},
            content=body,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("mcp-session-id", response.headers)
        self.assertIn("protocolVersion", response.text)
        self.assertNotIn("gate_evidence_refs", response.text)

    def test_over_bound_declared_and_streamed_bodies_are_rejected(self):
        oversized = b"x" * (MAX_REQUEST_BODY_SIZE + 1)
        for body in (
            oversized,
            iter((oversized[: 4 * 1024 * 1024], oversized[4 * 1024 * 1024 :])),
        ):
            with self.subTest(streamed=not isinstance(body, bytes)):
                request = self.client.build_request(
                    "POST", MCP_PATH, content=body
                )
                self.assertEqual(
                    "chunked"
                    if not isinstance(body, bytes)
                    else str(len(body)),
                    request.headers.get(
                        "transfer-encoding"
                        if not isinstance(body, bytes)
                        else "content-length"
                    ),
                )
                response = self.client.send(request)
                self.assertEqual(response.status_code, 413)
                self.assertNotIn("mcp-session-id", response.headers)

    def test_larger_transport_policy_preserves_host_and_origin_admission(self):
        body = self.current_size_initialize()
        for extra, status in (
            ({"host": "attacker.invalid"}, 421),
            ({"origin": "https://attacker.invalid"}, 403),
        ):
            with self.subTest(extra=extra):
                response = self.client.post(
                    MCP_PATH, headers=extra, content=body
                )
                self.assertEqual(response.status_code, status)
                self.assertNotIn("mcp-session-id", response.headers)


if __name__ == "__main__":
    unittest.main()
