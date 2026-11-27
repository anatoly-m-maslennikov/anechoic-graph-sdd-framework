"""Archive process test cases."""

import os
import signal
import threading

from ._archive_sources import API, INSTANCE, OWNER, write_ticket


class ArchiveCases2:
    def test_live_write_and_archive_publication(self):
        write_ticket(
            self.tickets / "09_archived",
            "AN-T-2@7-TASK--older.md",
            "AN-T-2",
            "archived",
            7,
            "old revision",
        )
        owner = self.start(OWNER)
        self.monitor = threading.Thread(
            target=self.hold_archive, args=(owner,), daemon=True
        )
        self.monitor.start()
        self.wait(
            (self.directory / "peers.ready").is_file,
            owner,
            "peer owner did not become ready",
        )
        api = self.start(API, "--role", "api")
        self.wait(
            (self.directory / "api.sock").is_socket, api, "API did not start"
        )
        client = self.client("api.sock")
        self.wait(
            lambda: self.held is not None,
            owner,
            "Archive Worker was not observed",
        )
        self.wait(
            lambda: client.get("/health").json().get("state") == "ready",
            api,
            "live projection not ready",
        )
        health = client.get("/health").json()
        self.assertTrue(health["archive_pending"])
        status = self.call(client, "workbench_status", {})["result"]["value"]
        self.assertFalse(status["syncing"])
        self.assertEqual(
            ("running", True),
            (status["archive"]["state"], status["archive"]["worker_alive"]),
        )
        live, updated = self.exercise_live_edits(client, api, health)
        self.check_archive_publication(client, api, live, updated)

    def check_archive_publication(self, client, api, live, updated):
        os.kill(self.held, signal.SIGCONT)
        self.held = None
        self.wait(
            lambda: (
                client.get("/health").json().get("archive_pending") is False
            ),
            api,
            "Archive Worker did not publish",
            timeout=60,
        )
        self.assertNotEqual(
            updated["generation"], client.get("/health").json()["generation"]
        )
        archived = [
            ["AN-T-2@7", "Archived", "old revision"],
            ["AN-T-99@4", "Archived", "archived"],
        ]
        self.assertEqual(sorted(live + archived), self.rows(client))
        self.assert_archive_issues(client, api)
        self.monitor.join(timeout=1)

    def exercise_live_edits(self, client, api, health):
        live = [
            ["AN-T-2", "Current", "active"],
            ["AN-T-2@3-draft", "Draft", "draft"],
        ]
        self.assertEqual(live, self.rows(client))
        live = self.create_drafts(client, live)
        self.current.write_text(
            self.current.read_text().replace(
                "\nactive\n", "\nUpdated while loading the archive\n"
            ),
            encoding="utf-8",
        )
        live[1][2] = "Updated while loading the archive"
        self.wait(
            lambda: self.rows(client) == live,
            api,
            "live update was not visible",
            timeout=60,
        )
        updated = client.get("/health").json()
        self.assertTrue(updated["archive_pending"])
        self.assertNotEqual(health["generation"], updated["generation"])
        return live, updated

    def create_drafts(self, client, live):
        created = self.call(
            client,
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nCreate another Task\n",
                }
            },
        )
        self.assertEqual(
            "AN-T-100",
            created["result"]["value"].get("savedDraft", {}).get("atom_id"),
            created,
        )
        revision = self.call(
            client,
            "atom_lifecycle_create_draft",
            {"sourceCurrent": {"ref_id": "AN-T-2", "version": 2}},
        )
        self.assertEqual(
            8,
            revision["result"]["value"].get("savedDraft", {}).get("version"),
            revision,
        )
        live = [
            ["AN-T-100@1-draft", "Draft", "Create another Task"],
            *live,
            ["AN-T-2@8-draft", "Draft", "active"],
        ]
        return live

    def assert_archive_issues(self, client, api):
        def succeeded():
            status = self.call(client, "workbench_status", {})["result"][
                "value"
            ]
            return (
                status if status["archive"]["state"] == "succeeded" else None
            )

        status = self.wait(succeeded, api, "archive did not succeed")
        issues = {
            row["relative_path"]: row
            for row in status["ingestion_issues"]
            if row["source"] == "archive"
        }
        self.assertEqual(
            {
                self.broken.relative_to(self.root).as_posix(),
                self.misplaced.relative_to(self.root).as_posix(),
            },
            set(issues),
        )
        self.assertEqual(
            "parse_error",
            issues[self.broken.relative_to(self.root).as_posix()]["code"],
        )
        misplaced = issues[self.misplaced.relative_to(self.root).as_posix()]
        self.assertEqual(
            (
                "invalid_value",
                "AN-T-97@1",
                "Archive directory contains a non-Archived Atom",
            ),
            (misplaced["code"], misplaced["atom_ref"], misplaced["message"]),
        )
        self.check_post_archive_write(client)

    def check_post_archive_write(self, client):
        allowed = self.call(
            client,
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nCreate a Task after Archive\n",
                }
            },
        )
        self.assertNotEqual(
            "archive_pending", allowed.get("error", {}).get("code"), allowed
        )

    def test_invalid_required_input_reports_and_recovers_under_same_owner(
        self,
    ):
        manifest = next(self.control.glob("*-PROJECT_MANIFEST--*.md"))
        original = manifest.read_bytes()
        manifest.write_bytes(b"Invalid Manifest")
        owner = self.start(OWNER)
        self.wait(
            (self.directory / "peers.ready").is_file,
            owner,
            "peer owner did not become ready",
        )
        api = self.start(API, "--role", "api")
        self.wait(
            (self.directory / "api.sock").is_socket, api, "API did not start"
        )
        client = self.client("api.sock")
        peers = self.peer_ids()

        def build_failed():
            status = self.call(client, "workbench_status", {})["result"][
                "value"
            ]
            return any(
                issue["source"] == "build"
                for issue in status.get("ingestion_issues", [])
            )

        self.wait(
            build_failed, api, "failed build diagnostic was not published"
        )
        self.check_recovery(
            manifest, original, owner, api, client, peers, build_failed
        )

    def check_recovery(
        self, manifest, original, owner, api, client, peers, build_failed
    ):
        health = client.get("/health")
        self.assertEqual(
            (200, "degraded", "project_build_unavailable"),
            (
                health.status_code,
                health.json()["state"],
                health.json()["error"]["code"],
            ),
        )
        response = client.post(
            "/tools",
            json={
                "name": "query_run",
                "arguments": {"sql": "SELECT 42", "result_delivery": "inline"},
                "instance_id": INSTANCE,
                "session_id": None,
                "public_base_url": None,
                "asserted_project_root": None,
            },
        )
        self.assertEqual(
            (200, "project_build_unavailable"),
            (response.status_code, response.json()["error"]["code"]),
        )
        manifest.write_bytes(original)
        self.wait(
            lambda: client.get("/health").json().get("state") == "ready",
            api,
            "repair not admitted",
        )
        self.assertFalse(build_failed())
        result = self.call(
            client,
            "query_run",
            {"sql": "SELECT 42", "result_delivery": "inline"},
        )
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        self.assertIsNone(owner.poll())
        self.assertEqual(peers, self.peer_ids())
