"""Projection control process test cases."""

from .projection_peer_fixture import INSTANCE, QUERY_ID


class ProjectionCases2:
    def test_direct_unready_status_abort_and_rebuild(self):
        refused = self.call(0, "query_run", {"sql": "SELECT 1"})
        self.assertEqual("project_build_pending", refused["error"]["code"])
        refused = self.call(
            0, "atom_lifecycle_archive", {"target": {"ref": "AN-S-1"}}
        )
        self.assertEqual("project_build_pending", refused["error"]["code"])
        self.assertEqual(
            self.call(0, "workbench_status", {}),
            self.call(0, "iwe_console_status", {}),
        )
        self.assertEqual(
            "aborting",
            self.call(0, "iwe_console_abort", {"run_id": "run-1"})["result"][
                "value"
            ]["state"],
        )
        value = self.call(0, "workbench_status", {})["result"]["value"]
        self.assertEqual(
            (True, "run-1", True),
            (value["syncing"], value["run_id"], value["worker_alive"]),
        )
        self.assertEqual([{"code": "warning"}], value["ingestion_issues"])
        self.assertEqual(
            "aborting",
            self.call(0, "workbench_abort", {"run_id": "run-1"})["result"][
                "value"
            ]["state"],
        )
        self.check_rebuilds()

    def check_rebuilds(self):
        result = self.call(0, "query_rebuild", {"target": "main.mrt_atoms"})[
            "result"
        ]["value"]
        self.assertEqual(
            {
                "status": "ready",
                "target": "main.mrt_atoms",
                "result_ids": {QUERY_ID: "d" * 32},
            },
            result,
        )
        self.assertEqual(
            (
                "POST",
                "/jobs/build",
                {
                    **self.worker_binding,
                    "instance_id": INSTANCE,
                    "refresh_target": "atoms",
                },
            ),
            self.servers[1].requests[-1],
        )
        self.call(0, "query_rebuild", {"target": "query_" + QUERY_ID})
        self.assertEqual(
            (
                "POST",
                "/results/rebuild",
                {"instance_id": INSTANCE, "target": QUERY_ID},
            ),
            self.servers[0].requests[-1],
        )
        count = len(self.servers[1].requests) + len(self.servers[0].requests)
        self.assertEqual(
            "tool_input_invalid",
            self.call(0, "query_rebuild", {"target": "unknown"})["error"][
                "code"
            ],
        )
        self.assertEqual(
            count,
            len(self.servers[1].requests) + len(self.servers[0].requests),
        )

    def test_graph_rebuild_routes_to_worker(self):
        result = self.call(
            0, "query_rebuild", {"target": "realization_graph"}
        )["result"]["value"]
        self.assertEqual("realization_graph", result["target"])
        self.assertEqual(
            (
                "POST",
                "/jobs/build",
                {
                    **self.worker_binding,
                    "instance_id": INSTANCE,
                    "refresh_target": "realization_graph",
                },
            ),
            self.servers[1].requests[-1],
        )

    def test_model_projection_rebuild_targets(self):
        for name in ("model_tree", "model_primary_entities"):
            for target in (name, "mrt_" + name, "main.mrt_" + name):
                with self.subTest(target=target):
                    result = self.call(0, "query_rebuild", {"target": target})[
                        "result"
                    ]["value"]
                    self.assertEqual(target, result["target"])
                    self.assertEqual(
                        (
                            "POST",
                            "/jobs/build",
                            {
                                **self.worker_binding,
                                "instance_id": INSTANCE,
                                "refresh_target": name,
                            },
                        ),
                        self.servers[1].requests[-1],
                    )

    def test_shared_cold_status_abort_do_not_start_project(self):
        status = self.call(1, "workbench_status", {})["result"]["value"]
        self.assertEqual(
            {"mode": "unavailable", "syncing": False, "last_synced_at": None},
            status,
        )
        abort = self.call(1, "workbench_abort", {"run_id": "run-1"})
        self.assertEqual("run_not_abortable", abort["error"]["code"])
        leases = [
            item
            for item in self.servers[2].requests
            if item["operation"] == "lease"
        ]
        self.assertEqual([False, False], [item["start"] for item in leases])
        self.assertEqual([b"R", b"R"], self.servers[2].releases)
        rebuilt = self.call(1, "query_rebuild", {"target": "all"})["result"][
            "value"
        ]
        self.assertEqual("ready", rebuilt["status"])
        leases = [
            item
            for item in self.servers[2].requests
            if item["operation"] == "lease"
        ]
        self.assertTrue(leases[-1]["start"])
        self.assertEqual(
            "all", self.servers[1].requests[-1][2]["refresh_target"]
        )

    def test_direct_worker_runs_binding(self):
        response = self.clients[0].get(
            "/jobs/worker-runs", params={"instance_id": INSTANCE}
        )
        self.assertEqual(
            "run-1", response.json()["result"]["active"]["run_id"]
        )
        count = len(self.servers[1].requests)
        for params in (
            {},
            {"instance_id": "other"},
            {"instance_id": INSTANCE, "extra": "x"},
        ):
            result = (
                self.clients[0].get("/jobs/worker-runs", params=params).json()
            )
            self.assertEqual("value_error", result["error"]["code"])
        self.assertEqual(count, len(self.servers[1].requests))

    def test_shared_warm_status_and_abort_use_no_start_lease(self):
        self.servers[2].cold = False
        status = self.call(1, "workbench_status", {})["result"]["value"]
        self.assertEqual(
            ("run-1", True), (status["run_id"], status["worker_alive"])
        )
        result = self.call(1, "workbench_abort", {"run_id": "run-1"})[
            "result"
        ]["value"]
        self.assertEqual({"run_id": "run-1", "state": "aborting"}, result)
        leases = [
            item
            for item in self.servers[2].requests
            if item["operation"] == "lease"
        ]
        self.assertEqual([False, False], [item["start"] for item in leases])
        self.assertNotIn(
            "/jobs/build", [item[1] for item in self.servers[1].requests]
        )

    def test_archive_pending_keeps_live_health_and_queries_ready(self):
        database, jobs = self.servers[:2]
        database.ready, jobs.startup_replay_pending = True, False
        for pending in (True, False, None):
            with self.subTest(pending=pending):
                database.archive_pending = pending
                response = self.clients[0].get("/health")
                self.assertEqual(200, response.status_code)
                self.assertEqual("ready", response.json()["state"])
                self.assertIs(
                    pending is True, response.json()["archive_pending"]
                )
                query = self.call(
                    0,
                    "query_run",
                    {"sql": "SELECT 42", "result_delivery": "inline"},
                )
                self.assertEqual([[42]], query["result"]["value"]["rows"])
        self.assertNotIn("/jobs/build", [item[1] for item in jobs.requests])

    def test_archive_status_is_not_live_sync_for_direct_and_shared(self):
        archive = {"state": "running", "started_at": 100, "worker_alive": True}
        self.servers[1].runs = {
            "active": None,
            "latest": {"state": "succeeded", "finished_at": 50.0},
            "archive": archive,
        }
        self.servers[2].cold = False
        for index in (0, 1):
            with self.subTest(index=index):
                status = self.call(index, "workbench_status", {})["result"][
                    "value"
                ]
                self.assertFalse(status["syncing"])
                self.assertEqual(archive, status["archive"])
                self.assertEqual(
                    [{"code": "warning"}], status["ingestion_issues"]
                )
        self.assertNotIn(
            "/jobs/build", [item[1] for item in self.servers[1].requests]
        )
