"""Exercise foreground readiness and deferred Archived Atoms through real sockets."""

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest

import httpx2

from .test_runtime_roles import _client, _stop, _wait
from .WORKBENCH_BACKEND_beta_C70__tests__shared import process_env, write_project


def _gated_orchestrator():
    from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import GenerationJobs, main

    directory = Path(sys.argv[sys.argv.index("--socket") + 1]).parent
    communicate = GenerationJobs._communicate_worker

    def gated(jobs, workdir, request, *, archive=False):
        if archive:
            (directory / "archive-waiting").touch()
            deadline = monotonic() + 120
            while not (directory / "archive-release").exists():
                if jobs.stopping.is_set() or monotonic() >= deadline:
                    raise RuntimeError("Archive test did not release the Worker")
                sleep(0.02)
        return communicate(jobs, workdir, request, archive=archive)

    GenerationJobs._communicate_worker = gated
    return main()


def _ticket(directory, name, atom_id, status, version):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        f"---\nidentity: {{atom_id: {atom_id}}}\ncontext: {{container: {{component: C00}}}}\n"
        f"state: {{status: {status}, version: {version}}}\n---\n\n## Summary\n\n{status}\n",
        encoding="utf-8",
    )
    return path


class ArchiveStartupEndToEndTests(unittest.TestCase):
    def _start(self, directory, root, manifest):
        socket = directory / "api.sock"
        script = (
            "from WORKBENCH_BACKEND_beta_C70 import runtime\n"
            f"runtime.ORCHESTRATOR = {__name__!r}\n"
            "runtime.main()\n"
        )
        process = subprocess.Popen(
            [sys.executable, "-B", "-P", "-c", script, "--socket", str(socket),
             "--instance-id", "instance", "--project-root", str(root), "--control-root", manifest.parent.name,
             "--manifest-path", manifest.relative_to(root).as_posix(), "--project-prefix", "AN",
             "--manifest-sha256", sha256(manifest.read_bytes()).hexdigest(), "--workbench-storage", "memory"],
            env=process_env(), stdin=subprocess.PIPE,
        )
        self.addCleanup(_stop, process)
        return process, socket

    def _tool(self, client, root, name, arguments):
        return client.post("/tools", json={"name": name, "arguments": arguments, "instance_id": "instance",
                                           "session_id": "archive-startup", "public_base_url": None,
                                           "asserted_project_root": str(root)}).json()

    def _tickets(self, client, root):
        result = self._tool(client, root, "query_run", {
            "sql": 'SELECT reference, status_group, "content.summary" FROM main.atoms '
                   "WHERE reference LIKE 'AN-T-%' ORDER BY reference",
            "result_delivery": "inline",
        })
        self.assertIn("result", result, result)
        return result["result"]["value"]["rows"]

    def test_api_is_ready_while_archive_worker_waits(self):
        directory = Path(self.enterContext(TemporaryDirectory(prefix="ane-beta-arc-", dir="/tmp"))).resolve()
        root = directory / "project"
        root.mkdir()
        manifest = write_project(root)
        tickets = manifest.parent / "__TKT" / "TASKS"
        current = _ticket(tickets, "AN-T-2-TASK--current.md", "AN-T-2", "active", 2)
        _ticket(tickets / "01_draft", "AN-T-2@3-draft-TASK--draft.md", "AN-T-2", "draft", 3)
        _ticket(tickets / "09_archived", "AN-T-99@4-TASK--archived.md", "AN-T-99", "archived", 4)
        process, socket = self._start(directory, root, manifest)
        _wait(process, (directory / "archive-waiting").is_file, 60)
        _wait(process, socket.is_socket, 30)
        client = self.enterContext(_client(socket))

        def ready():
            try:
                return client.get("/health").status_code == 200
            except httpx2.TransportError:
                return False

        _wait(process, ready, 10)
        health = client.get("/health").json()
        self.assertTrue(health["ready"])
        self.assertTrue(health["archive_pending"])
        live = [["AN-T-2", "Current", "active"], ["AN-T-2@3-draft", "Draft", "draft"]]
        self.assertEqual(live, self._tickets(client, root))
        blocked = self._tool(client, root, "atom_lifecycle_create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"}, "summary": "Create another Task",
        }})
        self.assertEqual("archive_pending", blocked["error"]["code"], blocked)

        current.write_text(current.read_text().replace("\nactive\n", "\nUpdated while loading the archive\n"),
                           encoding="utf-8")
        live[0][2] = "Updated while loading the archive"
        _wait(process, lambda: self._tickets(client, root) == live, 30)
        updated = client.get("/health").json()
        self.assertTrue(updated["archive_pending"])
        self.assertNotEqual(health["generation"], updated["generation"])

        (directory / "archive-release").touch()
        _wait(process, lambda: client.get("/health").json().get("archive_pending") is False, 30)
        self.assertNotEqual(updated["generation"], client.get("/health").json()["generation"])
        self.assertEqual(live + [["AN-T-99@4", "Archived", "archived"]], self._tickets(client, root))


if __name__ == "__main__":
    raise SystemExit(_gated_orchestrator())
