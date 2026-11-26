"""Exercise live projection updates while the real Archive Worker is delayed."""

from hashlib import sha256
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

import httpx2


ENGINE = Path(__file__).resolve().parents[2]
INSTANCE = "archive-test"
OWNER = "ORCHESTRATOR_beta_C68.project_peer_owner"
API = "API_MIXER_beta_C91.API_MIXER_beta_C91__shared"


def write_manifest(root):
    control = root / "_anechoic_anechoic"
    control.mkdir()
    manifest = control / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
    manifest.write_text(
        "---\natom_family: SPEC\natom_id: AN-S-001\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 3\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare Anechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
        encoding="utf-8",
    )
    return manifest


def write_ticket(directory, name, atom_id, status, version, summary):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        f"---\natom_family: TKT\natom_id: {atom_id}\ncontainer: {{component: C00}}\n"
        f"priority: 2\ncontext: {{template: task}}\nstate: {{status: {status}, version: {version}, "
        f"updated_at: '2026-11-19T00:00:00Z'}}\n---\n\n## Summary\n\n{summary}\n",
        encoding="utf-8",
    )
    return path


class ArchiveProcessTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="ane-archive-", dir="/tmp"))).resolve()
        self.root = self.directory / "project"
        self.root.mkdir()
        manifest = write_manifest(self.root)
        self.control = manifest.parent
        self.tickets = self.control / "__TICKETS" / "TASKS"
        self.current = write_ticket(self.tickets, "AN-T-2-TASK--active.md", "AN-T-2", "active", 2, "active")
        write_ticket(self.tickets / "01_draft", "AN-T-2@3-draft-TASK--draft.md", "AN-T-2", "draft", 3, "draft")
        write_ticket(self.tickets / "09_archived", "AN-T-99@4-TASK--archived.md", "AN-T-99", "archived", 4, "archived")
        self.misplaced = write_ticket(self.tickets / "09_archived", "AN-T-97-TASK--misplaced.md",
                                      "AN-T-97", "in_queue", 1, "misplaced")
        self.broken = self.tickets / "09_archived" / "AN-T-98@1-TASK--broken.md"
        self.broken.write_text("---\nidentity: [invalid\n", encoding="utf-8")
        self.arguments = ["--socket", str(self.directory / "api.sock"), "--instance-id", INSTANCE,
                          "--project-root", str(self.root), "--control-root", self.control.name,
                          "--manifest-path", manifest.relative_to(self.root).as_posix(),
                          "--manifest-sha256", sha256(manifest.read_bytes()).hexdigest(),
                          "--project-prefix", "AN", "--workbench-storage", "memory"]
        self.env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_PROFILE": "test",
                    "ANECHOIC_WORKBENCH_STORAGE": "memory", "ANECHOIC_JOURNAL_STORAGE": "files",
                    "ANECHOIC_ARCHIVES": "load", "ANECHOIC_LOG_LEVEL": "ERROR",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))}
        self.processes, self.clients = [], []
        self.held = None
        self.monitor = None
        self.monitor_stop = threading.Event()
        self.addCleanup(self.stop_processes)

    def stop_processes(self):
        self.monitor_stop.set()
        if self.monitor is not None:
            self.monitor.join(timeout=10)
        if self.held is not None:
            try:
                os.kill(self.held, signal.SIGCONT)
            except ProcessLookupError:
                pass
            self.held = None
        for process, log in reversed(self.processes):
            if not process.stdin.closed:
                process.stdin.close()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            log.close()
        for client in self.clients:
            client.close()

    def start(self, module, *extra):
        log = (self.directory / (module.rsplit(".", 1)[-1] + ".log")).open("w+")
        process = subprocess.Popen([sys.executable, "-B", "-P", "-m", module, *self.arguments, *extra],
                                   cwd=ENGINE, env=self.env, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=log)
        self.processes.append((process, log))
        return process

    def client(self, name):
        client = httpx2.Client(transport=httpx2.HTTPTransport(uds=str(self.directory / name)),
                               base_url="http://private", trust_env=False, timeout=5)
        self.clients.append(client)
        return client

    def wait(self, predicate, process, message, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and process.poll() is None:
            try:
                if value := predicate():
                    return value
            except (httpx2.TransportError, KeyError, ValueError):
                pass
            time.sleep(0.03)
        self.fail(f"{message}; exit={process.poll()}")

    def hold_archive(self, owner):
        jobs = self.client("jobs.sock")
        deadline = time.monotonic() + 90
        while not self.monitor_stop.is_set() and owner.poll() is None and time.monotonic() < deadline:
            if not (self.directory / "jobs.sock").is_socket():
                time.sleep(0.02)
                continue
            try:
                pid = jobs.get("/health").json()["result"]["pid"]
                rows = subprocess.check_output(["ps", "-eo", "pid=,ppid=,args="], text=True, timeout=2).splitlines()
                for row in rows:
                    parts = row.strip().split(None, 2)
                    if len(parts) == 3 and int(parts[1]) == pid and "anechoic-archive-" in parts[2]:
                        if self.monitor_stop.is_set():
                            return
                        child = int(parts[0])
                        os.kill(child, signal.SIGSTOP)
                        self.held = child
                        return
            except (httpx2.TransportError, KeyError, ValueError, ProcessLookupError, subprocess.TimeoutExpired):
                pass
            time.sleep(0.02)

    def call(self, client, name, arguments):
        return client.post("/tools", json={"name": name, "arguments": arguments, "instance_id": INSTANCE,
                           "session_id": "archive-test", "public_base_url": None, "asserted_project_root": None}).json()

    def rows(self, client):
        query = {"sql": 'SELECT reference, status_group, "content.summary" FROM main.atoms '
                        "WHERE reference LIKE 'AN-T-%' ORDER BY reference", "result_delivery": "inline"}
        result = self.call(client, "query_run", query)
        return result["result"]["value"]["rows"]

    def assert_api_refusal(self, message, *extra):
        command = [sys.executable, "-B", "-P", "-m", API, *self.arguments, "--role", "api", *extra]
        result = subprocess.run(command, cwd=ENGINE, env=self.env, input="", capture_output=True,
                                text=True, timeout=15)
        self.assertNotEqual(0, result.returncode)
        self.assertIn(message, result.stderr)
        self.assertFalse((self.directory / "api.sock").exists())

    def peer_ids(self):
        database = self.client("db.sock").get("/health").json()["result"]
        jobs = self.client("jobs.sock").get("/health").json()["result"]
        return database["pid"], jobs["pid"]

    def ready_api(self):
        process = self.start(API, "--role", "api", "--blacklist", "query_schema")
        self.wait((self.directory / "api.sock").is_socket, process, "API did not start")
        client = self.client("api.sock")
        def ready():
            value = client.get("/health").json()
            return value if value.get("state") == "ready" and not value.get("archive_pending") else None
        health = self.wait(ready, process, "projection did not settle", timeout=90)
        return process, client, health

    def test_api_restarts_against_same_peers_and_retains_query(self):
        self.assert_api_refusal("peers.ready")
        owner = self.start(OWNER)
        ready = self.directory / "peers.ready"
        self.wait(ready.is_file, owner, "peer owner did not become ready", timeout=90)
        self.assertEqual(b"", ready.read_bytes())
        self.assertFalse(ready.stat().st_mode & 0o077)
        self.assert_api_refusal("Beta peer reported a different Project binding", "--manifest-sha256", "0" * 64)

        first, first_client, health = self.ready_api()
        self.assertEqual((first.pid, INSTANCE), (health["pid"], health["instance_id"]))
        self.assertEqual(self.arguments[self.arguments.index("--manifest-sha256") + 1], health["manifest_sha256"])
        peers = self.peer_ids()
        self.assertEqual(peers[0], health["kernel_pid"])
        catalog = first_client.get("/tools", params={"instance_id": INSTANCE}).json()["result"]
        self.assertEqual(["query_schema"], catalog["blacklist"])
        self.assertNotIn("query_schema", [item["name"] for item in catalog["tools"]])
        self.assertEqual("tool_unavailable", self.call(first_client, "query_schema", {})["error"]["code"])
        query = self.call(first_client, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
        self.assertEqual([[42]], query["result"]["value"]["rows"])
        query_id = query["result"]["value"]["query_id"]
        first.kill()
        first.wait(timeout=5)
        first_client.close()
        (self.directory / "api.sock").unlink()
        second, second_client, restarted = self.ready_api()
        self.assertNotEqual(first.pid, second.pid)
        self.assertEqual(second.pid, restarted["pid"])
        self.assertEqual(peers[0], restarted["kernel_pid"])
        self.assertEqual(peers, self.peer_ids())
        page = self.call(second_client, "query_page", {"query_id": query_id, "result_delivery": "inline"})
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        catalog = second_client.get("/tools", params={"instance_id": INSTANCE}).json()["result"]
        self.assertEqual(["query_schema"], catalog["blacklist"])
        self.assertEqual("tool_unavailable", self.call(second_client, "query_schema", {})["error"]["code"])
        second.stdin.close()
        self.assertEqual(0, second.wait(timeout=10))
        self.assertFalse((self.directory / "api.sock").exists())
        self.assertIsNone(owner.poll())
        os.kill(peers[1], signal.SIGKILL)
        self.assertNotEqual(0, owner.wait(timeout=15))
        self.assertFalse(ready.exists())
        for pid in peers:
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_live_write_and_archive_publication(self):
        write_ticket(self.tickets / "09_archived", "AN-T-2@7-TASK--older.md", "AN-T-2", "archived", 7, "old revision")
        owner = self.start(OWNER)
        self.monitor = threading.Thread(target=self.hold_archive, args=(owner,), daemon=True)
        self.monitor.start()
        self.wait((self.directory / "peers.ready").is_file, owner, "peer owner did not become ready")
        api = self.start(API, "--role", "api")
        self.wait((self.directory / "api.sock").is_socket, api, "API did not start")
        client = self.client("api.sock")
        self.wait(lambda: self.held is not None, owner, "Archive Worker was not observed")
        self.wait(lambda: client.get("/health").json().get("state") == "ready", api, "live projection not ready")
        health = client.get("/health").json()
        self.assertTrue(health["archive_pending"])
        status = self.call(client, "workbench_status", {})["result"]["value"]
        self.assertFalse(status["syncing"])
        self.assertEqual(("running", True), (status["archive"]["state"], status["archive"]["worker_alive"]))
        live = [["AN-T-2", "Current", "active"], ["AN-T-2@3-draft", "Draft", "draft"]]
        self.assertEqual(live, self.rows(client))
        created = self.call(client, "atom_lifecycle_create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nCreate another Task\n"}})
        self.assertEqual("AN-T-100", created["result"]["value"].get("savedDraft", {}).get("atom_id"), created)
        revision = self.call(client, "atom_lifecycle_create_draft", {"sourceCurrent": {"ref_id": "AN-T-2", "version": 2}})
        self.assertEqual(8, revision["result"]["value"].get("savedDraft", {}).get("version"), revision)
        live = [["AN-T-100@1-draft", "Draft", "Create another Task"], *live, ["AN-T-2@8-draft", "Draft", "active"]]
        self.current.write_text(self.current.read_text().replace("\nactive\n", "\nUpdated while loading the archive\n"),
                                encoding="utf-8")
        live[1][2] = "Updated while loading the archive"
        self.wait(lambda: self.rows(client) == live, api, "live update was not visible", timeout=60)
        updated = client.get("/health").json()
        self.assertTrue(updated["archive_pending"])
        self.assertNotEqual(health["generation"], updated["generation"])
        os.kill(self.held, signal.SIGCONT)
        self.held = None
        self.wait(lambda: client.get("/health").json().get("archive_pending") is False, api,
                  "Archive Worker did not publish", timeout=60)
        self.assertNotEqual(updated["generation"], client.get("/health").json()["generation"])
        archived = [["AN-T-2@7", "Archived", "old revision"], ["AN-T-99@4", "Archived", "archived"]]
        self.assertEqual(sorted(live + archived), self.rows(client))
        self.assert_archive_issues(client, api)
        self.monitor.join(timeout=1)

    def assert_archive_issues(self, client, api):
        def succeeded():
            status = self.call(client, "workbench_status", {})["result"]["value"]
            return status if status["archive"]["state"] == "succeeded" else None
        status = self.wait(succeeded, api, "archive did not succeed")
        issues = {row["relative_path"]: row for row in status["ingestion_issues"] if row["source"] == "archive"}
        self.assertEqual({self.broken.relative_to(self.root).as_posix(), self.misplaced.relative_to(self.root).as_posix()},
                         set(issues))
        self.assertEqual("parse_error", issues[self.broken.relative_to(self.root).as_posix()]["code"])
        misplaced = issues[self.misplaced.relative_to(self.root).as_posix()]
        self.assertEqual(("invalid_value", "AN-T-97@1", "Archive directory contains a non-Archived Atom"),
                         (misplaced["code"], misplaced["atom_ref"], misplaced["message"]))
        allowed = self.call(client, "atom_lifecycle_create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nCreate a Task after Archive\n"}})
        self.assertNotEqual("archive_pending", allowed.get("error", {}).get("code"), allowed)

    def test_invalid_required_input_reports_and_recovers_under_same_owner(self):
        manifest = next(self.control.glob("*-PROJECT_MANIFEST--*.md"))
        original = manifest.read_bytes()
        manifest.write_bytes(b"Invalid Manifest")
        owner = self.start(OWNER)
        self.wait((self.directory / "peers.ready").is_file, owner, "peer owner did not become ready")
        api = self.start(API, "--role", "api")
        self.wait((self.directory / "api.sock").is_socket, api, "API did not start")
        client = self.client("api.sock")
        peers = self.peer_ids()

        def build_failed():
            status = self.call(client, "workbench_status", {})["result"]["value"]
            return any(issue["source"] == "build" for issue in status.get("ingestion_issues", []))

        self.wait(build_failed, api, "failed build diagnostic was not published")
        health = client.get("/health")
        self.assertEqual((200, "degraded", "project_build_unavailable"),
                         (health.status_code, health.json()["state"], health.json()["error"]["code"]))
        response = client.post("/tools", json={"name": "query_run", "arguments": {
            "sql": "SELECT 42", "result_delivery": "inline"}, "instance_id": INSTANCE,
            "session_id": None, "public_base_url": None, "asserted_project_root": None})
        self.assertEqual((200, "project_build_unavailable"), (response.status_code, response.json()["error"]["code"]))
        manifest.write_bytes(original)
        self.wait(lambda: client.get("/health").json().get("state") == "ready", api, "repair not admitted")
        self.assertFalse(build_failed())
        result = self.call(client, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        self.assertIsNone(owner.poll())
        self.assertEqual(peers, self.peer_ids())
