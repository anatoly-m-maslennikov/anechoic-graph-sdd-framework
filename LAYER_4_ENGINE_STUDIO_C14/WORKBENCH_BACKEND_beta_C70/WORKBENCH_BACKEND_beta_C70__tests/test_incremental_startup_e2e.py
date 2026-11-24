"""Exercise disk checkpoint reuse and offline reconciliation across real peers."""

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest

import httpx2

from .test_runtime_roles import _client, _wait
from .WORKBENCH_BACKEND_beta_C70__tests__shared import process_env, write_project


def _ticket(directory, name, atom_id, status, version):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        f"---\natom_family: TKT\natom_id: {atom_id}\ncontainer: {{component: C00}}\npriority: 2\n"
        f"context: {{template: task}}\nstate: {{status: {status}, version: {version}, "
        "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\n"
        f"{status}\n", encoding="utf-8",
    )
    return path


class IncrementalStartupTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(TemporaryDirectory(prefix="ane-beta-disk-", dir="/tmp"))).resolve()
        self.root = self.directory / "project"
        self.root.mkdir()
        self.manifest = write_project(self.root)
        self.tickets = self.manifest.parent / "__TKT" / "TASKS"
        self.current = [_ticket(self.tickets, f"AN-T-{n}-TASK--current.md", f"AN-T-{n}", "active", 1)
                        for n in range(1, 5)]
        self.archive = self.tickets / "09_archived"
        _ticket(self.archive, "AN-T-99@1-TASK--archived.md", "AN-T-99", "archived", 1)
        self.process = None
        self.addCleanup(self.stop)

    def start(self):
        for name in ("archive-waiting", "archive-release"):
            (self.directory / name).unlink(missing_ok=True)
        socket = self.directory / "api.sock"
        script = ("from WORKBENCH_BACKEND_beta_C70 import runtime\n"
                  "runtime.ORCHESTRATOR = 'WORKBENCH_BACKEND_beta_C70.WORKBENCH_BACKEND_beta_C70__tests.test_archive_startup_e2e'\n"
                  "runtime.main()\n")
        started = monotonic()
        self.process = subprocess.Popen(
            [sys.executable, "-B", "-P", "-c", script, "--socket", str(socket),
             "--instance-id", "instance", "--project-root", str(self.root), "--control-root", self.manifest.parent.name,
             "--manifest-path", self.manifest.relative_to(self.root).as_posix(), "--project-prefix", "AN",
             "--manifest-sha256", sha256(self.manifest.read_bytes()).hexdigest(), "--workbench-storage", "disk"],
            env=process_env(), stdin=subprocess.PIPE,
        )
        _wait(self.process, socket.is_socket, 90)
        client = _client(socket)
        self.addCleanup(client.close)
        _wait(self.process, lambda: self.healthy(client), 30)
        return client, monotonic() - started

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process.stdin.close()
            self.process = None

    def healthy(self, client):
        try:
            return client.get("/health").status_code == 200
        except httpx2.TransportError:
            return False

    def rows(self, client, sql):
        result = client.post("/tools", json={"name": "query_run", "arguments": {"sql": sql, "result_delivery": "inline"},
            "instance_id": "instance", "session_id": "startup", "public_base_url": None,
            "asserted_project_root": str(self.root)}).json()
        self.assertIn("result", result, result)
        return result["result"]["value"]["rows"]

    def startup_flows(self, client):
        return self.rows(client, "SELECT o.run_id, json_extract_string(o.detail, '$.kind') "
            "FROM flow_events o WHERE o.component = 'C68' AND o.name = 'generation_result' "
            "AND o.outcome = 'succeeded' AND EXISTS (SELECT 1 FROM flow_events t "
            "WHERE t.run_id = o.run_id AND t.kind = 'trigger' AND t.name = 'startup') ORDER BY o.at")

    def wait_flow(self, client, previous, expected):
        _wait(self.process, lambda: len(self.startup_flows(client)) > previous, 30)
        flows = self.startup_flows(client)
        self.assertEqual(expected, flows[-1][1], flows)
        return len(flows)

    def wait_archive(self, client):
        _wait(self.process, (self.directory / "archive-waiting").is_file, 60)
        self.assertTrue(client.get("/health").json()["archive_pending"])

    def release_archive(self, client):
        (self.directory / "archive-release").touch()
        _wait(self.process, lambda: client.get("/health").json().get("archive_pending") is False, 60)

    def ticket_rows(self, client):
        return self.rows(client, 'SELECT reference, filename, "content.summary" FROM atoms '
            "WHERE reference LIKE 'AN-T-%' ORDER BY reference")

    def database_identity(self):
        database, = (self.root / ".anechoic_runtime/workbench/beta").glob("*.duckdb")
        info = database.stat()
        return info.st_dev, info.st_ino

    def offline_changes(self):
        self.current[0].write_text(self.current[0].read_text().replace("\nactive\n", "\nOffline edit\n"))
        self.current[1].rename(self.current[1].with_name("AN-T-2-TASK--moved.md"))
        self.current[2].unlink()
        _ticket(self.tickets, "AN-T-5-TASK--added.md", "AN-T-5", "active", 1)
        _ticket(self.archive, "AN-T-100@1-TASK--archived.md", "AN-T-100", "archived", 1)

    def test_missing_database_reuse_and_offline_delta_with_archive_catchup(self):
        client, cold = self.start()
        self.wait_archive(client)
        count = self.wait_flow(client, 0, "full")
        self.assertNotIn("AN-T-99@1", [row[0] for row in self.ticket_rows(client)])
        self.release_archive(client)
        self.assertIn("AN-T-99@1", [row[0] for row in self.ticket_rows(client)])
        identity = self.database_identity()
        self.stop()
        client, unchanged = self.start()
        count = self.wait_flow(client, count, "reused")
        self.assertEqual(identity, self.database_identity())
        self.assertIn("AN-T-99@1", [row[0] for row in self.ticket_rows(client)])
        self.stop()
        self.offline_changes()
        client, changed = self.start()
        self.wait_archive(client)
        self.wait_flow(client, count, "native_delta")
        self.assertEqual(identity, self.database_identity())
        rows = self.ticket_rows(client)
        self.assertIn(["AN-T-1", "AN-T-1-TASK--current.md", "Offline edit"], rows)
        self.assertIn(["AN-T-2", "AN-T-2-TASK--moved.md", "active"], rows)
        self.assertNotIn("AN-T-3", [row[0] for row in rows])
        self.assertIn("AN-T-5", [row[0] for row in rows])
        self.assertIn("AN-T-99@1", [row[0] for row in rows])
        self.assertNotIn("AN-T-100@1", [row[0] for row in rows])
        self.release_archive(client)
        self.assertIn("AN-T-100@1", [row[0] for row in self.ticket_rows(client)])
        print(f"startup seconds: cold={cold:.3f} unchanged={unchanged:.3f} offline={changed:.3f}", flush=True)
