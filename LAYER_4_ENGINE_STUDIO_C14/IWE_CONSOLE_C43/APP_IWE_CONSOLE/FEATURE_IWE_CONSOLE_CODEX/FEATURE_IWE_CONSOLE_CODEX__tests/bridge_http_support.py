"""Real HTTP/SSE coverage for the one-Project Workbench Codex bridge.

The app-server is an external executable fixture on ``PATH``.  The bridge,
HTTP server, JSON-RPC process boundary and runtime files are real.  No
Workbench business service is mocked here.
"""

from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from typing import Any
from urllib.parse import urlsplit


CODEX_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = CODEX_ROOT.parents[3]
FIXTURE = Path(__file__).with_name("fake_codex.py")
ALLOWED_ORIGIN = "http://127.0.0.1:56317"
MCP_URL = f"{ALLOWED_ORIGIN}/anechoic/mcp"
FORBIDDEN_OVERRIDE_KEYS = {
    "model",
    "modelProvider",
    "model_provider",
    "toolConfig",
    "tool_config",
    "allowedTools",
    "allowed_tools",
    "mcpServers",
    "mcp_servers",
    "approvalPolicy",
    "approval_policy",
    "sandbox",
    "auth",
    "credentials",
}


def _bridge_server() -> Path | None:
    configured = os.environ.get("ANECHOIC_CODEX_BRIDGE_SERVER")
    path = Path(configured) if configured else CODEX_ROOT / "bridge_server.py"
    return path if path.is_file() else None


def _write_codex_path_fixture(directory: Path) -> None:
    """Install a real executable named ``codex`` in the test PATH."""
    executable = directory / "codex"
    executable.write_text(
        "#!/bin/sh\n"
        f'exec {shlex.quote(sys.executable)} -B {shlex.quote(str(FIXTURE))} "$@"\n',
        encoding="utf-8",
    )
    executable.chmod(0o755)


class BridgeHTTPFixture(unittest.TestCase):
    """Exercise the public bridge wire, not its private Python classes."""

    @classmethod
    def setUpClass(cls) -> None:
        bridge = _bridge_server()
        if bridge is None:
            raise unittest.SkipTest("bridge_server.py is not available yet")
        temp_parent = REPOSITORY / ".anechoic_tmp/workbench-codex-http"
        temp_parent.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=temp_parent)
        cls.root = Path(cls.temp.name) / "project"
        (cls.root / ".anechoic_anechoic").mkdir(parents=True)
        fake_bin = Path(cls.temp.name) / "bin"
        fake_bin.mkdir()
        _write_codex_path_fixture(fake_bin)
        cls.audit = Path(cls.temp.name) / "fake-codex.jsonl"
        environment = os.environ.copy()
        environment["PATH"] = (
            f"{fake_bin}{os.pathsep}{environment.get('PATH', '')}"
        )
        environment["FAKE_CODEX_AUDIT"] = str(cls.audit)
        cls.process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                str(bridge),
                "--project-root",
                str(cls.root),
                "--mcp-url",
                MCP_URL,
            ],
            cwd=REPOSITORY,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        cls.addClassCleanup(cls._stop_server)
        cls.base_url = cls._wait_for_bridge()

    @classmethod
    def _wait_for_bridge(cls) -> str:
        state = cls.root / ".anechoic_runtime/iwe_console/codex/bridge.json"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if cls.process.poll() is not None:
                stdout = (
                    cls.process.stdout.read() if cls.process.stdout else ""
                )
                stderr = (
                    cls.process.stderr.read() if cls.process.stderr else ""
                )
                raise AssertionError(
                    (
                        "Codex bridge exited\nstdout:\n"
                        f"{stdout}"
                        "\nstderr:\n"
                        f"{stderr}"
                    )
                )
            try:
                value = json.loads(state.read_text(encoding="utf-8"))
                if value.get("ready") is True and isinstance(
                    value.get("url"), str
                ):
                    return value["url"].rstrip("/")
            except OSError, ValueError:
                pass
            time.sleep(0.05)
        raise AssertionError("Codex bridge did not publish ready bridge.json")

    @classmethod
    def _stop_server(cls) -> None:
        process = getattr(cls, "process", None)
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        cls.temp.cleanup()

    @staticmethod
    def _endpoint(base_url: str, path: str) -> tuple[str, int, str]:
        parsed = urlsplit(base_url)
        return parsed.hostname or "127.0.0.1", parsed.port or 80, path

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        origin: str | None = ALLOWED_ORIGIN,
    ) -> tuple[int, dict[str, str], bytes]:
        host, port, request_path = self._endpoint(self.base_url, path)
        connection = http.client.HTTPConnection(host, port, timeout=10)
        body = (
            json.dumps(payload).encode("utf-8")
            if payload is not None
            else None
        )
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if origin is not None:
            headers["Origin"] = origin
        connection.request(method, request_path, body=body, headers=headers)
        response = connection.getresponse()
        result = (
            response.status,
            dict(response.getheaders()),
            response.read(),
        )
        connection.close()
        return result

    def json_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        origin: str | None = ALLOWED_ORIGIN,
    ) -> tuple[int, dict[str, Any]]:
        status, _, body = self.request(method, path, payload, origin=origin)
        return status, json.loads(body or b"{}")

    def open_turn(
        self, message: str
    ) -> tuple[http.client.HTTPConnection, http.client.HTTPResponse]:
        host, port, path = self._endpoint(self.base_url, "/turn")
        connection = http.client.HTTPConnection(host, port, timeout=20)
        connection.request(
            "POST",
            path,
            body=json.dumps({"message": message}).encode("utf-8"),
            headers={
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
                "Origin": ALLOWED_ORIGIN,
            },
        )
        response = connection.getresponse()
        self.assertEqual(200, response.status)
        return connection, response

    @staticmethod
    def read_sse(response: http.client.HTTPResponse) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        data: list[str] = []
        while True:
            raw = response.readline()
            if not raw:
                break
            line = raw.decode("utf-8").rstrip("\r\n")
            if line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line and data:
                events.append(json.loads("\n".join(data)))
                data.clear()
        if data:
            events.append(json.loads("\n".join(data)))
        return events

    def wait_for_pending(self, request_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status, value = self.json_request("GET", "/conversation")
            self.assertEqual(200, status)
            pending = value.get("pending_requests", [])
            if any(
                item == request_id
                or (isinstance(item, dict) and item.get("id") == request_id)
                for item in pending
            ):
                return value
            time.sleep(0.05)
        self.fail(f"native request {request_id!r} did not reach the bridge")

    def collect_turn(
        self,
        connection: http.client.HTTPConnection,
        response: http.client.HTTPResponse,
        output: dict[str, list[dict[str, Any]]],
    ) -> threading.Thread:
        def collect() -> None:
            try:
                output["events"] = self.read_sse(response)
            finally:
                connection.close()

        thread = threading.Thread(target=collect, daemon=True)
        thread.start()
        return thread
