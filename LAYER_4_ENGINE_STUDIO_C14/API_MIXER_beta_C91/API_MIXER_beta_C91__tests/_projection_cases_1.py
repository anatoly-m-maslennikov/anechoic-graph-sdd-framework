"""Projection control process test cases."""

import threading
from concurrent.futures import ThreadPoolExecutor

from .projection_peer_fixture import INSTANCE


class ProjectionCases1:
    def test_ready_kernel_waits_for_startup_replay(self):
        database, jobs = self.servers[:2]
        database.ready = True
        jobs.runs = {"active": None, "latest": None}
        sql = {"sql": "SELECT 42", "result_delivery": "inline"}
        health = self.clients[0].get("/health")
        self.assertEqual(
            (200, "pending"), (health.status_code, health.json()["state"])
        )
        self.assertEqual(
            "project_build_pending",
            self.call(0, "query_run", sql)["error"]["code"],
        )
        database.unreachable = True
        health = self.clients[0].get("/health")
        self.assertEqual(
            (503, "unavailable"), (health.status_code, health.json()["state"])
        )
        request = {
            "name": "query_run",
            "arguments": sql,
            "instance_id": INSTANCE,
            "session_id": None,
            "public_base_url": None,
            "asserted_project_root": None,
        }
        refused = self.clients[0].post("/tools", json=request)
        self.assertEqual(
            (503, "project_build_unavailable"),
            (refused.status_code, refused.json()["error"]["code"]),
        )
        database.unreachable = False
        self.check_failed_replay(database, jobs, sql)

    def check_failed_replay(self, database, jobs, sql):
        jobs.runs["latest"] = {"state": "failed"}
        health = self.clients[0].get("/health")
        self.assertEqual(
            (200, "degraded"), (health.status_code, health.json()["state"])
        )
        self.assertEqual(
            "project_build_unavailable",
            self.call(0, "query_run", sql)["error"]["code"],
        )
        self.assertFalse(
            any(method == "POST" for method, _, _ in database.requests)
        )
        jobs.startup_replay_pending = False
        self.assertEqual(
            "ready", self.clients[0].get("/health").json()["state"]
        )
        self.assertEqual(
            [[42]], self.call(0, "query_run", sql)["result"]["value"]["rows"]
        )
        self.assertEqual(
            1, sum(method == "POST" for method, _, _ in database.requests)
        )

    def test_watcher_and_orchestrator_gate_direct_health_and_shared_queries(
        self,
    ):
        database, jobs = self.servers[:2]
        database.ready, jobs.startup_replay_pending = True, False
        sql = {"sql": "SELECT 42", "result_delivery": "inline"}
        for index in (0, 1):
            self.assertIn("result", self.call(index, "query_run", sql))
        self.servers[2].cold = False
        jobs.watcher_active = False
        self.assertEqual(
            "degraded", self.clients[0].get("/health").json()["state"]
        )
        for index in (0, 1):
            health = self.call(
                index, "iwe_console_status", {"include_health": True}
            )["result"]["value"]["health"]
            self.assertEqual("degraded", health["state"])
            self.assertIn("watcher is unavailable", health["error"]["message"])
        self.assertEqual(
            "project_build_unavailable",
            self.call(1, "query_run", sql)["error"]["code"],
        )
        jobs.watcher_active, jobs.unreachable = True, True
        self.assertEqual(
            "unavailable", self.clients[0].get("/health").json()["state"]
        )
        self.assertEqual(
            "shared_gateway_failure",
            self.call(1, "query_run", sql)["error"]["code"],
        )

    def test_manifest_gate_blocks_new_calls_but_drains_accepted_call(self):
        database, jobs = self.servers[:2]
        database.ready, jobs.startup_replay_pending = True, False
        database.entered, database.release = (
            threading.Event(),
            threading.Event(),
        )
        sql = {"sql": "SELECT 42", "result_delivery": "inline"}
        with ThreadPoolExecutor(max_workers=1) as pool:
            accepted = pool.submit(self.call, 0, "query_run", sql)
            try:
                self.assertTrue(
                    database.entered.wait(5),
                    "accepted query did not reach Kernel",
                )
                self.check_manifest_refusals(sql)
                self.assertEqual(
                    1,
                    sum(
                        method == "POST" for method, _, _ in database.requests
                    ),
                )
            finally:
                database.release.set()
            self.assertEqual(
                [[42]], accepted.result(timeout=5)["result"]["value"]["rows"]
            )

    def check_manifest_refusals(self, sql):
        for content, state, status, code in (
            (
                b"project_manifest_reloading",
                "pending",
                200,
                "project_manifest_reloading",
            ),
            (
                b"project_manifest_invalid",
                "degraded",
                200,
                "project_manifest_invalid",
            ),
            (
                b"\xff",
                "unavailable",
                503,
                "admission_gate_unavailable",
            ),
        ):
            with self.subTest(code=code):
                self.gate.write_bytes(content)
                health = self.clients[0].get("/health")
                self.assertEqual(
                    (status, state),
                    (health.status_code, health.json()["state"]),
                )
                self.assertEqual(code, health.json()["error"]["code"])
                request = {
                    "name": "query_run",
                    "arguments": sql,
                    "instance_id": INSTANCE,
                    "session_id": None,
                    "public_base_url": None,
                    "asserted_project_root": None,
                }
                refused = self.clients[0].post("/tools", json=request)
                self.assertEqual(
                    (status, code),
                    (
                        refused.status_code,
                        refused.json()["error"]["code"],
                    ),
                )
