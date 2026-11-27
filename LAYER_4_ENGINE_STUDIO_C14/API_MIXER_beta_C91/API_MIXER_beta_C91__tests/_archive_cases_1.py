"""Archive process test cases."""

import os
import signal

from ._archive_sources import INSTANCE, OWNER


class ArchiveCases1:
    def test_api_restarts_against_same_peers_and_retains_query(self):
        self.assert_api_refusal("peers.ready")
        owner = self.start(OWNER)
        ready = self.directory / "peers.ready"
        self.wait(
            ready.is_file, owner, "peer owner did not become ready", timeout=90
        )
        self.assertEqual(b"", ready.read_bytes())
        self.assertFalse(ready.stat().st_mode & 0o077)
        self.assert_api_refusal(
            "Beta peer reported a different Project binding",
            "--manifest-sha256",
            "0" * 64,
        )

        first, first_client, health = self.ready_api()
        self.assertEqual(
            (first.pid, INSTANCE), (health["pid"], health["instance_id"])
        )
        self.assertEqual(
            self.arguments[self.arguments.index("--manifest-sha256") + 1],
            health["manifest_sha256"],
        )
        peers = self.peer_ids()
        self.assertEqual(peers[0], health["kernel_pid"])
        catalog = first_client.get(
            "/tools", params={"instance_id": INSTANCE}
        ).json()["result"]
        self.assertEqual(["query_schema"], catalog["blacklist"])
        self.assertNotIn(
            "query_schema", [item["name"] for item in catalog["tools"]]
        )
        self.assertEqual(
            "tool_unavailable",
            self.call(first_client, "query_schema", {})["error"]["code"],
        )
        query = self.call(
            first_client,
            "query_run",
            {"sql": "SELECT 42", "result_delivery": "inline"},
        )
        self.assertEqual([[42]], query["result"]["value"]["rows"])
        query_id = query["result"]["value"]["query_id"]
        self.check_restart(owner, ready, peers, first, first_client, query_id)

    def check_restart(
        self, owner, ready, peers, first, first_client, query_id
    ):
        first.kill()
        first.wait(timeout=5)
        first_client.close()
        (self.directory / "api.sock").unlink()
        second, second_client, restarted = self.ready_api()
        self.assertNotEqual(first.pid, second.pid)
        self.assertEqual(second.pid, restarted["pid"])
        self.assertEqual(peers[0], restarted["kernel_pid"])
        self.assertEqual(peers, self.peer_ids())
        page = self.call(
            second_client,
            "query_page",
            {"query_id": query_id, "result_delivery": "inline"},
        )
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        catalog = second_client.get(
            "/tools", params={"instance_id": INSTANCE}
        ).json()["result"]
        self.assertEqual(["query_schema"], catalog["blacklist"])
        self.assertEqual(
            "tool_unavailable",
            self.call(second_client, "query_schema", {})["error"]["code"],
        )
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
