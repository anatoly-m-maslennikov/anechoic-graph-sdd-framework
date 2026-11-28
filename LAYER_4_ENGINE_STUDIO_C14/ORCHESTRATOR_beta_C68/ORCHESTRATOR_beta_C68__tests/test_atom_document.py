import json
import socketserver
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import httpx2

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as orchestrator
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.\
    lifecycle.test_lifecycle_queries import database  # fmt: skip


class Kernel(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        request = json.loads(
            self.rfile.read(int(self.headers["Content-Length"]))
        )
        rows = self.server.db.execute(request["sql"]).fetchall()
        payload = json.dumps({"result": {"rows": rows}}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class AtomDocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.db = database()
        self.db.execute(
            'ALTER TABLE atoms ADD COLUMN "content.summary" VARCHAR'
        )
        self.db.execute(
            'UPDATE atoms SET "content.summary"=? WHERE reference=?',
            ["Hello.", "AN-T-1"],
        )
        self.addCleanup(self.db.close)
        kernel_path = str(self.root / "kernel.sock")
        self.kernel = socketserver.UnixStreamServer(kernel_path, Kernel)
        self.kernel.db = self.db
        self.serve(self.kernel)
        self.binding = {
            "root": str(self.root),
            "control_root": str(self.root),
            "manifest_path": "m",
            "manifest_sha256": "h",
            "project_prefix": "AN",
        }
        socket_path = str(self.root / "jobs.sock")
        self.server = orchestrator.Server(
            socket_path, "i", self.binding, kernel_path
        )
        self.server.jobs.live_generation = "g"
        self.serve(self.server)
        self.client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=socket_path), timeout=5
        )
        self.addCleanup(self.client.close)
        self.request = {**self.binding, "instance_id": "i", "ref_id": "AN-T-1"}
        self.write_carrier("AN-T-1.md", 1, "active")
        self.write_carrier("AN-T-1@2-draft.md", 2, "draft")

    def serve(self, server):
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 5)
        self.addCleanup(server.shutdown)

    def call(self, **fields):
        response = self.client.post(
            "http://private/jobs/atom-document",
            json={**self.request, **fields},
        )
        return response.status_code, response.json()

    def write_carrier(self, name, version, status):
        (self.root / name).write_text(
            f"---\natom_family: TKT\natom_id: AN-T-1\ncontainer: {{component: C00}}\n"
            f"priority: 2\ncontext: {{template: task}}\nstate: {{status: {status}, version: {version}, "
            "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\nHello.\n",
            encoding="utf-8",
        )

    def test_current_and_exact_draft(self):
        self.db.execute(
            (
                "INSERT INTO relations VALUES ('Atom', 'AN-T-2', 'Atom', "
                "'AN-T-1', 'CONTAINED_BY', false)"
            )
        )
        status, result = self.call()
        self.assertEqual(status, 200)
        self.assertEqual(result["result"]["exact_ref"], "AN-T-1@1")
        self.assertEqual(result["result"]["filename"], "AN-T-1-TASK--hello.md")
        self.assertIn("Hello.", result["result"]["body"])
        self.assertEqual(
            result["result"]["contained"],
            [{"ref_id": "AN-T-2", "filename": "AN-T-2.md"}],
        )
        self.assertTrue(
            any(
                row["direction"] == "incoming"
                for row in result["result"]["relations"]
            )
        )
        self.assertEqual(
            [row["ref_id"] for row in result["result"]["history"]],
            ["AN-T-1@1", "AN-T-1@2-draft"],
        )
        status, result = self.call(ref_id="AN-T-1@2-draft")
        self.assertEqual(status, 200)
        self.assertEqual(result["result"]["filename"], "AN-T-1@2-draft.md")
        self.assertEqual(
            result["result"]["contained"],
            [{"ref_id": "AN-T-2", "filename": "AN-T-2.md"}],
        )
        self.assertFalse(
            any(
                row["direction"] == "incoming"
                for row in result["result"]["relations"]
            )
        )
        self.assertEqual(self.call(ref_id="AN-T-1@2")[0], 404)

    def test_ticket_status_options_use_only_the_selected_generations_model(
        self,
    ):
        self.server.jobs.generation_reuse = orchestrator.ReuseRecord(
            inputs={},
            graph_config=None,
            endpoints={},
            base_generation="g",
            status_domains={
                "T": [
                    "active",
                    "in_queue",
                    "done",
                    "canceled",
                    "waiting_review",
                ]
            },
        )
        _, current = self.call()
        self.assertEqual(
            ["done", "in_queue", "waiting_review", "canceled"],
            current["result"]["ticket_statuses"],
        )
        _, draft = self.call(ref_id="AN-T-1@2-draft")
        self.assertNotIn("ticket_statuses", draft["result"])
        self.server.jobs.generation_reuse.base_generation = "previous"
        _, current = self.call()
        self.assertEqual(
            ["done", "in_queue", "canceled"],
            current["result"]["ticket_statuses"],
        )

    def _seed_related_revisions(self, archive_ref):
        self.write_carrier(archive_ref + ".md", 3, "archived")
        self.db.execute(
            "INSERT INTO atoms VALUES (?, '.', ?, 'Archived', 3, "
            "'archived', NULL)",
            [archive_ref, archive_ref + ".md"],
        )
        self.db.execute(
            "INSERT INTO native_references VALUES (?, ?)",
            [archive_ref, archive_ref],
        )
        for source, target in [
            ("AN-T-2", "AN-T-1"),
            ("AN-T-3", "AN-T-1@1"),
            ("AN-T-4", "AN-T-1@2-draft"),
            ("AN-T-2", archive_ref),
        ]:
            self.db.execute(
                "INSERT INTO relations VALUES "
                "('Atom', ?, 'Atom', ?, 'RELATES_TO', false)",
                [source, target],
            )
        self.db.execute(
            "INSERT INTO relations VALUES "
            "('Atom', 'AN-T-1@1', 'Atom', 'AN-T-3', 'RELATES_TO', true)"
        )

    def test_incoming_links_follow_selected_revision(self):
        archive_ref = "AN-T-1@3"
        self._seed_related_revisions(archive_ref)
        for ref, expected in [
            ("AN-T-1", {"AN-T-2", "AN-T-3"}),
            ("AN-T-1@1", {"AN-T-2", "AN-T-3"}),
            ("AN-T-1@2-draft", {"AN-T-4"}),
            (archive_ref, {"AN-T-2"}),
        ]:
            with self.subTest(ref=ref):
                status, result = self.call(ref_id=ref)
                self.assertEqual(status, 200)
                self.assertEqual(
                    {
                        row["ref_id"]
                        for row in result["result"]["relations"]
                        if row["direction"] == "incoming"
                    },
                    expected,
                )
                self.assertEqual(
                    {
                        row["ref_id"]
                        for row in result["result"]["relations"]
                        if row["direction"] == "outgoing" and row["derived"]
                    },
                    {"AN-T-3"} if ref in ("AN-T-1", "AN-T-1@1") else set(),
                )

    def test_draft_exposes_only_authored_relations_for_removal(self):
        path = self.root / "AN-T-1@2-draft.md"
        path.write_text(
            path.read_text().replace(
                "state: ", "relations: {BLOCKS: [AN-T-3]}\nstate: "
            )
        )
        self.db.execute(
            (
                "INSERT INTO relations VALUES ('Atom', 'AN-T-1@2-draft', "
                "'Component', 'C00', 'CONTAINED_BY', false)"
            )
        )
        code, result = self.call(ref_id="AN-T-1@2-draft")
        self.assertEqual(code, 200)
        self.assertEqual(
            result["result"]["authored_relations"],
            [{"type": "BLOCKS", "ref_id": "AN-T-3"}],
        )
        self.assertEqual(result["result"]["relations"][0]["ref_id"], "C00")

    def test_rejects_binding_injection_stale_and_symlink(self):
        self.assertEqual(self.call(root="/tmp")[0], 409)
        self.assertEqual(self.call(ref_id="AN-T-1' OR TRUE")[0], 400)
        self.db.execute("UPDATE generation SET id='different'")
        self.assertEqual(self.call()[0], 503)
        self.db.execute("UPDATE generation SET id='g'")
        self.db.execute(
            (
                "UPDATE atoms SET relative_path='../outside' WHERE "
                "reference='AN-T-1'"
            )
        )
        self.assertEqual(self.call()[0], 503)
        self.db.execute(
            "UPDATE atoms SET relative_path='.' WHERE reference='AN-T-1'"
        )
        path = self.root / "AN-T-1.md"
        path.write_text(
            path.read_text().replace("atom_id: AN-T-1", "atom_id: AN-T-9")
        )
        self.assertEqual(self.call()[0], 503)
        path.unlink()
        path.symlink_to(self.root / "AN-T-1@2-draft.md")
        self.assertEqual(self.call()[0], 503)


if __name__ == "__main__":
    unittest.main()
