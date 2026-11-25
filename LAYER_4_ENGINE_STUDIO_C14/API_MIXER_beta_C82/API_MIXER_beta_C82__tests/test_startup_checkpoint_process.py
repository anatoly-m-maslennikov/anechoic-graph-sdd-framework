"""Check persistent startup reuse and offline reconciliation through the API."""

from contextlib import ExitStack, contextmanager
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory, TemporaryFile
from time import monotonic, sleep
import unittest

import httpx2

from .test_archive_process import API, ENGINE, OWNER, write_manifest


INSTANCE = "startup-checkpoint"
STARTUP_RUNS = (
    "SELECT o.run_id, json_extract_string(o.detail, '$.kind') FROM flow_events o "
    "WHERE o.component = 'C68' AND o.name = 'generation_result' AND o.outcome = 'succeeded' "
    "AND EXISTS (SELECT 1 FROM flow_events t WHERE t.run_id = o.run_id "
    "AND t.kind = 'trigger' AND t.name = 'startup') ORDER BY o.at"
)
TICKETS = ('SELECT reference, filename, "content.summary" FROM main.atoms '
           "WHERE reference LIKE 'AN-T-%' ORDER BY reference")


def write_ticket(directory, number, label, *, archived=False):
    directory.mkdir(parents=True, exist_ok=True)
    identity = f"AN-T-{number}"
    path = directory / f"{identity}{'@1' if archived else ''}-TASK--{label}.md"
    status = "archived" if archived else "active"
    path.write_text(
        f"---\natom_family: TKT\natom_id: {identity}\ncontainer: {{component: C00}}\npriority: 2\n"
        f"context: {{template: task}}\nstate: {{status: {status}, version: 1, "
        "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\n"
        f"{label}\n", encoding="utf-8",
    )
    return path


class StartupCheckpointProcessTest(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(TemporaryDirectory(prefix="ane-c82-checkpoint-", dir="/tmp"))
        self.runtime = Path(temp).resolve()
        self.root = self.runtime / "project"
        self.root.mkdir()
        manifest = write_manifest(self.root)
        self.tickets = manifest.parent / "__TKT" / "TASKS"
        self.archive = self.tickets / "09_archived"
        self.arguments = ["--socket", str(self.runtime / "api.sock"), "--instance-id", INSTANCE,
                          "--project-root", str(self.root), "--control-root", manifest.parent.name,
                          "--manifest-path", manifest.relative_to(self.root).as_posix(), "--project-prefix", "AN",
                          "--manifest-sha256", sha256(manifest.read_bytes()).hexdigest(), "--workbench-storage", "disk"]
        extensions = ENGINE.parent / ".anechoic_tmp/workbench/extensions"
        self.env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_PROFILE": "test",
                    "ANECHOIC_WORKBENCH_STORAGE": "disk", "ANECHOIC_JOURNAL_STORAGE": "files",
                    "ANECHOIC_ARCHIVES": "load", "ANECHOIC_LOG_LEVEL": "ERROR",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(extensions))}

    @contextmanager
    def process(self, module, *extra):
        command = [sys.executable, "-B", "-P", "-m", module, *self.arguments, *extra]
        with TemporaryFile(mode="w+") as log:
            process = subprocess.Popen(command, cwd=ENGINE, env=self.env, stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL, stderr=log)
            try:
                yield process, log
            finally:
                process.stdin.close()
                try:
                    code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                    self.fail(f"{module} did not stop on EOF")
            log.seek(0)
            self.assertEqual(0, code, log.read())

    def wait(self, predicate, child, message):
        process, log = child
        deadline = monotonic() + 60
        while monotonic() < deadline and process.poll() is None:
            try:
                if value := predicate():
                    return value
            except httpx2.TransportError:
                pass
            sleep(0.05)
        log.seek(0)
        self.fail(f"{message} (exit={process.poll()})\n{log.read()}")

    def query(self, client, sql):
        response = client.post("/tools", json={"name": "query_run", "instance_id": INSTANCE,
            "session_id": "startup", "public_base_url": None, "asserted_project_root": str(self.root),
            "arguments": {"sql": sql, "result_delivery": "inline"}})
        data = response.json()
        self.assertIn("result", data, data)
        return data["result"]["value"]["rows"]

    def cycle(self, earlier, mode):
        with ExitStack() as stack:
            owner = stack.enter_context(self.process(OWNER))
            self.wait((self.runtime / "peers.ready").is_file, owner, "Peer owner did not become ready")
            api = stack.enter_context(self.process(API, "--role", "api"))
            socket = self.runtime / "api.sock"
            self.wait(socket.is_socket, api, "API socket did not open")
            client = stack.enter_context(httpx2.Client(transport=httpx2.HTTPTransport(uds=str(socket)),
                                                       base_url="http://private", trust_env=False, timeout=5))

            def settled():
                health = client.get("/health").json()
                return health if health.get("state") == "ready" and not health.get("archive_pending") else None

            def startup():
                events = self.query(client, STARTUP_RUNS)
                return events if len(events) > len(earlier) else None

            self.wait(settled, api, "API generation did not settle")
            events = self.wait(startup, api, "Startup result was not published")
            self.assertEqual(earlier, events[:-1])
            self.assertEqual(mode, events[-1][1], events)
            rows = self.query(client, TICKETS)
        for name in ("peers.ready", "api.sock", "db.sock", "jobs.sock"):
            self.assertFalse((self.runtime / name).exists(), name)
        database, = (self.root / ".anechoic_runtime/workbench/beta").glob("*.duckdb")
        stat = database.stat()
        return events, rows, (database, stat.st_dev, stat.st_ino)

    def test_disk_checkpoint_reuses_and_reconciles_offline_changes(self):
        edited = write_ticket(self.tickets, 1, "Initial")
        moved = write_ticket(self.tickets, 2, "Original")
        deleted = write_ticket(self.tickets, 3, "Deleted")
        archived = write_ticket(self.archive, 99, "History", archived=True)
        initial = [["AN-T-1", edited.name, "Initial"], ["AN-T-2", moved.name, "Original"],
                   ["AN-T-3", deleted.name, "Deleted"], ["AN-T-99@1", archived.name, "History"]]
        self.assertFalse((self.root / ".anechoic_runtime").exists())
        events, rows, database = self.cycle([], "full")
        self.assertEqual(initial, rows)
        events, rows, unchanged_database = self.cycle(events, "reused")
        self.assertEqual(initial, rows)
        self.assertEqual(database, unchanged_database)

        stamp = edited.stat()
        edited.write_text(edited.read_text().replace("\nInitial\n", "\nUpdated\n"), encoding="utf-8")
        os.utime(edited, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        destination = moved.rename(moved.with_name("AN-T-2-TASK--moved.md"))
        deleted.unlink()
        added = write_ticket(self.tickets, 4, "Added")
        history = write_ticket(self.archive, 100, "Offline archive", archived=True)

        _, rows, changed_database = self.cycle(events, "native_delta")
        self.assertEqual(database, changed_database)
        self.assertEqual([["AN-T-1", edited.name, "Updated"], ["AN-T-100@1", history.name, "Offline archive"],
                          ["AN-T-2", destination.name, "Original"], ["AN-T-4", added.name, "Added"],
                          ["AN-T-99@1", archived.name, "History"]], rows)
