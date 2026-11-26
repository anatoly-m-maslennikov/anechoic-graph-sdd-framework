"""Exercise lifecycle operations through the real API process and HTTP peers."""

import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler

import httpx2


ENGINE = Path(__file__).resolve().parents[2]
DIGEST = "a" * 64
MODULE = "API_MIXER_beta_C82.API_MIXER_beta_C82__shared"
UNKNOWN = {"code": "write_outcome_unknown", "message": "The lifecycle write outcome is unknown."}


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        result = {"instance_id": "instance", "pid": os.getpid()}
        if self.server.kind == "db":
            result.update(manifest_sha256=DIGEST, ready=True, generation="generation")
        else:
            result["startup_replay_pending"] = False
            result["watcher_active"] = True
        self.reply({"result": result})

    def do_POST(self):
        self.server.requests.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
        self.reply(self.server.response)

    def reply(self, value):
        data = value if isinstance(value, bytes) else json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class LifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.temp.name).resolve()
        self.servers = []
        for kind in ("db", "jobs"):
            path = self.root / (kind + ".sock")
            server = Server(str(path), Handler)
            os.chmod(path, 0o600)
            server.kind, server.requests = kind, []
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        self.jobs = self.servers[1]
        self.jobs.response = {"result": {"write_state": "known", "projection": {"state": "ready"},
                                        "lifecycle": {"outcome": "completed", "savedDraft": {"ref_id": "EX-S-1"}}}}
        (self.root / "peers.ready").touch(mode=0o600)
        self.binding = {"root": str(self.root), "control_root": "control", "manifest_path": "manifest",
                        "manifest_sha256": DIGEST, "project_prefix": "AN"}
        args = [sys.executable, "-B", "-P", "-m", MODULE, "--role", "api", "--socket", str(self.root / "api.sock"),
                "--instance-id", "instance", "--project-root", str(self.root), "--control-root", "control",
                "--manifest-path", "manifest", "--manifest-sha256", DIGEST, "--project-prefix", "AN"]
        env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_LOG_LEVEL": "ERROR"}
        env.pop("ANECHOIC_BETA_DIRECT_MANIFEST", None)
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, env=env, cwd=ENGINE, stderr=subprocess.PIPE)
        self.api = httpx2.Client(transport=httpx2.HTTPTransport(uds=str(self.root / "api.sock")),
                                 base_url="http://private", trust_env=False, timeout=10)
        self.wait_ready()

    def wait_ready(self):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(self.process.stderr.read().decode())
            if (self.root / "api.sock").exists():
                try:
                    if self.api.get("/health").json().get("state") == "ready":
                        return
                except httpx2.TransportError:
                    pass
            time.sleep(0.05)
        self.fail("API did not start")

    def tearDown(self):
        self.api.close()
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(self, name, args, **changes):
        envelope = {"name": name, "arguments": args, "instance_id": "instance", "session_id": None,
                    "public_base_url": None, "asserted_project_root": None}
        return self.api.post("/tools", json=envelope | changes).json()

    def test_all_tools_use_project_bound_lifecycle_ipc(self):
        cases = {"atom_lifecycle_create_draft": {"newAtom": {"body": "text", "extra": [1, None]}},
                 "atom_lifecycle_update": {"sourceCurrent": {}},
                 "atom_lifecycle_promote_draft": {"target": {}, "targetStatus": "active"},
                 "atom_lifecycle_change_status": {"target": {}, "targetStatus": "active"},
                 "atom_lifecycle_archive": {"target": {}}, "atom_lifecycle_create_asset": {"newAtom": {}},
                 "atom_lifecycle_direct_update": {"target": {}, "changes": {}}}
        tools = self.api.get("/tools", params={"instance_id": "instance"}).json()["result"]["tools"]
        schema = json.loads((ENGINE / "API_MIXER_beta_C82" / "query_run.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema, next(tool["inputSchema"] for tool in tools if tool["name"] == "query_run"))
        self.assertEqual(set(cases), {item["name"] for item in tools if item["name"].startswith("atom_lifecycle_")})
        for name, args in cases.items():
            value = self.call(name, args)["result"]["value"]
            self.assertEqual("draft_created" if name == "atom_lifecycle_update" else "completed", value["status"])
            request = {**self.binding, "instance_id": "instance", "name": name, "arguments": args}
            self.assertEqual(("/jobs/lifecycle", request), self.jobs.requests[-1])
            if name == "atom_lifecycle_direct_update":
                self.assertEqual({"status": "completed"}, value)

    def test_invalid_inputs_and_project_binding_are_rejected(self):
        for args in ({}, {"target": None}, {"target": {}, "extra": 1}, {"target": {}, "targetStatus": 5}):
            response = self.call("atom_lifecycle_promote_draft", args)
            self.assertEqual("tool_input_invalid", response["error"]["code"])
        response = self.call("atom_lifecycle_archive", {"target": {}}, instance_id="other")
        self.assertEqual("value_error", response["error"]["code"])
        self.assertEqual([], self.jobs.requests)

    def test_status_and_failure_results(self):
        scenarios = [
            ({"write_state": "known", "projection": {"state": "blocked"},
              "lifecycle": {"outcome": "blocked", "errors": [{"code": "write_blocked"}]}},
             "blocked", [{"code": "write_blocked"}]),
            ({"write_state": "known", "projection": {"state": "ready"},
              "lifecycle": {"outcome": "blocked", "warnings": ["wait"]}}, "blocked",
             [{"code": "backend_failure", "message": "Lifecycle operation failed."}]),
            ({"write_state": "known", "projection": {"state": "ready"},
              "lifecycle": {"outcome": "failed", "requested_input": {"target": {"error": "required"}}}},
             "failed", [{"code": "invalid_input", "field": "target", "message": "required"}]),
            ({"write_state": "unknown", "projection": {"state": "ready"}}, "failed", [UNKNOWN]),
            ({"write_state": "known", "projection": {"state": "failed", "error": {"code": "projection_failed"}},
              "lifecycle": {"outcome": "completed"}}, "failed", [{"code": "projection_failed"}]),
        ]
        for outcome, status, errors in scenarios:
            self.jobs.response = {"result": outcome}
            value = self.call("atom_lifecycle_archive", {"target": {}})["result"]["value"]
            self.assertEqual((status, errors), (value["status"], value["errors"]))
        self.jobs.response = {"error": {"code": "lifecycle_active", "message": "busy"}}
        self.assertEqual("lifecycle_active", self.call("atom_lifecycle_archive", {"target": {}})["error"]["code"])
        missing_error = {"write_state": "known", "projection": {"state": "failed"},
                         "lifecycle": {"outcome": "completed"}}
        blocked = {"write_state": "known", "projection": {"state": "blocked"},
                   "lifecycle": {"outcome": "completed"}}
        unknown_blocked = {**blocked, "write_state": "unknown", "lifecycle": {"outcome": "blocked"}}
        for response in ({"result": {"write_state": "known"}}, {"result": missing_error},
                         {"result": blocked}, {"result": unknown_blocked}, b"not JSON"):
            self.jobs.response = response
            value = self.call("atom_lifecycle_archive", {"target": {}})["result"]["value"]
            self.assertEqual([UNKNOWN], value["errors"])

    def test_validated_native_keeps_unknown_fields_and_error_details(self):
        native = {"outcome": "completed", "savedDraft": {"ref_id": "EX-S-2", "extra": {"value": None}},
                  "artifact": {"path": "one.md", "other": [1, True]}}
        self.jobs.response = {"result": {"write_state": "known", "projection": {"state": "ready"}, "lifecycle": native}}
        result = self.call("atom_lifecycle_create_draft", {"newAtom": {}})["result"]["value"]
        self.assertEqual({"status": "completed", "savedDraft": native["savedDraft"], "artifact": native["artifact"]}, result)
        error = {"code": "specific", "details": {"value": None}, "extra": [1, True]}
        native = {"outcome": "failed", "errors": [error], "warnings": [{"message": "keep"}], "effects": []}
        self.jobs.response = {"result": {"write_state": "known", "projection": {"state": "ready"}, "lifecycle": native}}
        result = self.call("atom_lifecycle_archive", {"target": {}})["result"]["value"]
        self.assertEqual(([error], native["warnings"], []), (result["errors"], result["warnings"], result["effects"]))


if __name__ == "__main__":
    unittest.main()
