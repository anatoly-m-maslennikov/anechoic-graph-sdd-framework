"""Archive recovery process test cases."""

from ._archive_sources import API, INSTANCE, OWNER


class ArchiveCases3:
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
