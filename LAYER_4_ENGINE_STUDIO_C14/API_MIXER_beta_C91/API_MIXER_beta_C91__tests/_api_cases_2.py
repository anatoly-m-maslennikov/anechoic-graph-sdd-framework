"""API process test cases."""

import subprocess
import sys
import time

import httpx2

from ._api_test_generation import DIGEST, ENGINE, KERNEL, generation


class ApiCases2:
    def test_query_family_against_real_kernel(self):
        self.servers[0].shutdown()
        self.servers[0].server_close()
        database = self.path / "db.sock"
        database.unlink(missing_ok=True)
        kernel = self.start_kernel(database)
        try:
            deadline = time.monotonic() + 20
            while (
                not database.exists()
                and kernel.poll() is None
                and time.monotonic() < deadline
            ):
                time.sleep(0.05)
            if not database.exists():
                kernel.terminate() if kernel.poll() is None else None
                self.fail(kernel.stderr.read().decode())
            with httpx2.Client(
                transport=httpx2.HTTPTransport(uds=str(database)),
                base_url="http://private",
                trust_env=False,
                timeout=20,
            ) as client:
                response = client.put("/generation", json=generation())
                self.assertEqual(200, response.status_code, response.text)
            self.assert_real_kernel_queries()
        finally:
            if kernel.poll() is None:
                kernel.terminate()
            kernel.wait(timeout=10)
            kernel.stderr.close()

    def start_kernel(self, database):
        env = {
            **self.env,
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(
                ENGINE.parent / ".anechoic_tmp/workbench/extensions"
            ),
        }
        command = [
            sys.executable,
            "-B",
            "-P",
            "-m",
            KERNEL,
            "--socket",
            str(database),
            "--instance-id",
            "instance",
            "--manifest-sha256",
            DIGEST,
            "--project-root",
            str(self.path),
        ]
        kernel = subprocess.Popen(
            command,
            env=env,
            cwd=ENGINE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        return kernel

    def assert_real_kernel_queries(self):
        run = self.call(
            {"sql": "SELECT 42 AS answer", "result_delivery": "inline"}
        )["result"]["value"]
        self.assertEqual([[42]], run["rows"])
        checked = self.call(
            {"sql": "SELECT 42 AS answer"}, name="query_check"
        )["result"]["value"]
        self.assertEqual(
            (True, 1, 1),
            (checked["valid"], checked["row_count"], checked["column_count"]),
        )
        page = self.call(
            {
                "query_id": run["query_id"],
                "result_delivery": "inline",
                "grid": {"sort": [{"column": 0, "direction": "desc"}]},
            },
            name="query_page",
        )
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        exported = self.call({"query_id": run["query_id"]}, name="query_page")[
            "result"
        ]["value"]["result_file"]
        self.assertEqual(1, exported["row_count"])
        self.assertTrue((self.path / exported["path"]).is_file())
        csv = self.call(
            {
                "query_id": run["query_id"],
                "result_delivery": "inline",
                "result_format": "csv",
            },
            name="query_page",
        )["result"]["value"]["csv"]
        self.assertIn("42", csv)
        self.check_real_query_results(run)

    def check_real_query_results(self, run):
        self.assert_public_schema()
        self.assertEqual(
            "query_error",
            self.call(
                {"query_id": run["query_id"], "grid": {"bad": True}},
                name="query_page",
            )["error"]["code"],
        )
        rebuilt = self.call({"target": run["query_id"]}, name="query_rebuild")[
            "result"
        ]["value"]
        new_id = rebuilt["result_ids"][run["query_id"]]
        page = self.call(
            {"query_id": new_id, "result_delivery": "inline"},
            name="query_page",
        )
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        partial = self.call(
            {"sql": "SELECT 99", "save": True, "result_delivery": "inline"}
        )["result"]["value"]
        self.assertEqual("partial", partial["outcome"])
        self.assertTrue(partial["save_error"])
        self.assertEqual([[99]], partial["rows"])
        self.check_partial_saved_view()

    def check_partial_saved_view(self):
        opened = self.call(
            {"session_id": "no-journal"}, name="workspace_open"
        )["result"]["value"]
        view = {
            "workspace_id": opened["workspace_id"],
            "view_id": opened["active_view_id"],
        }
        self.call(
            {**view, "sql": "SELECT 7", "expected_revision": 0},
            name="view_update",
        )
        failed_save = self.call({**view, "save": True}, name="view_run")[
            "result"
        ]["value"]
        self.assertEqual(
            ("success", "partial"),
            (failed_save["status"], failed_save["outcome"]),
        )
        self.assertTrue(failed_save["save_error"])
        self.assertEqual(
            [[7]],
            self.call(
                {**view, "result_delivery": "inline"}, name="view_fetch"
            )["result"]["value"]["rows"],
        )

    def assert_public_schema(self):
        tables = self.call({}, name="query_schema")["result"]["value"][
            "tables"
        ]
        for canonical, alias in (
            ("mrt_atoms", "atoms"),
            ("mrt_atom_references", "native_references"),
            ("mrt_atom_graph_relations", "relations"),
            ("src_flow_events", "flow_events"),
            ("biz_package_coupling", "package_coupling"),
            ("mrt_real_graph_import_occurrences", "module_imports"),
            ("mrt_diag_code_access", "code_access_findings"),
        ):
            self.assertEqual(
                tables[canonical], tables[alias], (canonical, alias)
            )
        self.assertIn(
            "code",
            {column["name"] for column in tables["ops_ingestion_issues"]},
        )
        self.assertNotIn("ops_generation_carrier_hashes", tables)
        self.check_atom_statuses(tables)

    def check_atom_statuses(self, tables):
        for table, rows, values in (
            ("mrt_spec_atoms", [["AN-S-1"]], ["active"]),
            ("mrt_ticket_atoms", [["AN-T-2"]], ["in_queue"]),
            (
                "mrt_project_config_atoms",
                [["AN-C-4@1-draft"], ["AN-P-3"]],
                ["active", "draft"],
            ),
        ):
            with self.subTest(table=table):
                status = next(
                    column
                    for column in tables[table]
                    if column["name"] == "header.state.status"
                )
                self.assertEqual(
                    {
                        "name": "header.state.status",
                        "type": "VARCHAR",
                        "values": values,
                    },
                    status,
                )
                sql = f"SELECT reference FROM main.{table} ORDER BY reference"
                self.assertEqual(
                    rows,
                    self.call({"sql": sql, "result_delivery": "inline"})[
                        "result"
                    ]["value"]["rows"],
                )
