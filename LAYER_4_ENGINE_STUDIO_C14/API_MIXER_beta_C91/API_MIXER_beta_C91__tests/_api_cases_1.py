"""API process test cases."""

import subprocess
import time

import httpx2

from ._api_test_generation import ENGINE, EXPECTED_TOOLS_1, EXPECTED_TOOLS_2


class ApiCases1:
    def test_catalog_query_validation_and_manifest_gate(self):
        catalog = self.client.get(
            "/tools", params={"instance_id": "instance"}
        ).json()["result"]
        self.assertEqual(
            EXPECTED_TOOLS_1,
            [tool["name"] for tool in catalog["tools"]],
        )
        result = self.call({"sql": "SELECT 42", "result_delivery": "inline"})
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        sent = self.servers[0].received[-1]
        self.assertEqual(100, sent["page_size"])
        self.assertEqual("json_matrix", sent["result_format"])
        self.call({"sql": "SELECT 42"})
        self.assertEqual(1000, self.servers[0].received[-1]["page_size"])
        self.check_invalid_requests_and_gate()

    def check_invalid_requests_and_gate(self):
        for args in (
            {"sql": 42},
            {"sql": "SELECT 1", "page_size": True},
            {"sql": "SELECT 1", "save": 1},
            {"sql": "SELECT 1", "name": "x"},
            {"sql": "SELECT 1", "preview": None},
        ):
            self.assertEqual(
                "tool_input_invalid", self.call(args)["error"]["code"]
            )
        self.assertEqual(
            "tool_unavailable",
            self.call({}, name="not_supported")["error"]["code"],
        )
        self.assertEqual(
            "value_error",
            self.call({"sql": "SELECT 1"}, instance_id="other")["error"][
                "code"
            ],
        )
        self.assertEqual(
            "value_error",
            self.call({"sql": "SELECT 1"}, asserted_project_root="/other")[
                "error"
            ]["code"],
        )
        oversized = self.call({"sql": "x" * 65536})
        self.assertEqual("value_error", oversized["error"]["code"])
        self.gate.write_text("project_manifest_reloading")
        self.assertEqual(
            "project_manifest_reloading",
            self.call({"sql": "SELECT 1"})["error"]["code"],
        )
        self.assertEqual("pending", self.client.get("/health").json()["state"])

    def test_invalid_kernel_reply_is_unavailable(self):
        self.servers[0].invalid = True
        request = {
            "name": "query_run",
            "arguments": {"sql": "SELECT 1"},
            "instance_id": "instance",
            "session_id": None,
            "public_base_url": None,
            "asserted_project_root": None,
        }
        response = self.client.post("/tools", json=request)
        self.assertEqual(503, response.status_code)
        self.assertEqual(
            "workbench_unavailable", response.json()["error"]["code"]
        )

    def test_blacklist_hides_and_rejects_tool(self):
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        self.process = subprocess.Popen(
            self.args + ["--blacklist", "query_run"],
            stdin=subprocess.PIPE,
            env=self.env,
            cwd=ENGINE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (self.path / "api.sock").exists():
                try:
                    catalog = self.client.get(
                        "/tools", params={"instance_id": "instance"}
                    ).json()
                    break
                except httpx2.TransportError:
                    pass
            time.sleep(0.05)
        else:
            self.fail("Blacklisted API did not start")
        self.assertEqual(
            EXPECTED_TOOLS_2,
            [tool["name"] for tool in catalog["result"]["tools"]],
        )
        self.assertEqual(["query_run"], catalog["result"]["blacklist"])
        self.assertEqual(
            "tool_unavailable", self.call({"sql": "SELECT 1"})["error"]["code"]
        )

    def test_query_check_forwards_unpaged_sql_and_validates_cursor(self):
        sql = "SELECT '😀' AS label"
        result = self.call(
            {"sql": sql, "cursor_position": 8}, name="query_check"
        )["result"]["value"]
        self.assertEqual(
            {"instance_id": "instance", "sql": sql},
            self.servers[0].received[-1],
        )
        self.assertEqual(
            {
                "valid": True,
                "columns": [
                    {"name": "answer", "type": "INTEGER", "has_values": True}
                ],
                "sql": sql,
                "row_count": 1,
                "column_count": 1,
            },
            result,
        )
        self.assertEqual(
            "tool_input_invalid",
            self.call({"sql": sql, "cursor_position": 9}, name="query_check")[
                "error"
            ]["code"],
        )
        self.assertEqual(
            "tool_input_invalid",
            self.call({"sql": sql, "page_size": 1}, name="query_check")[
                "error"
            ]["code"],
        )
        self.assertEqual(
            "query_error",
            self.call({"sql": "DELETE FROM atoms"}, name="query_check")[
                "error"
            ]["code"],
        )

    def test_query_page_forwards_defaults_grid_and_rejections(self):
        result = self.call({"query_id": "query"}, name="query_page")["result"][
            "value"
        ]
        self.assertEqual([[42]], result["rows"])
        self.assertEqual(
            {
                "instance_id": "instance",
                "query_id": "query",
                "offset": 0,
                "page_size": 100,
                "result_delivery": "file",
                "result_format": "json_matrix",
            },
            self.servers[0].received[-1],
        )
        grid = {
            "sort": [{"column": 0, "direction": "desc"}],
            "filters": [],
            "group_by": {"column": 0, "direction": "asc"},
        }
        args = {
            "query_id": "query",
            "offset": 2,
            "page_size": 5,
            "preview": 3,
            "grid": grid,
            "result_delivery": "inline",
            "result_format": "csv",
        }
        self.call(args, name="query_page")
        self.assertEqual(
            {"instance_id": "instance", **args}, self.servers[0].received[-1]
        )
        self.check_page_rejections()

    def check_page_rejections(self):
        for invalid in (
            {"query_id": "q", "offset": True},
            {"query_id": "q", "page_size": 0},
            {"query_id": "q", "grid": []},
            {"query_id": "q", "preview": -1},
        ):
            self.assertEqual(
                "tool_input_invalid",
                self.call(invalid, name="query_page")["error"]["code"],
            )
        self.assertEqual(
            "query_error",
            self.call(
                {"query_id": "q", "grid": {"bad": True}}, name="query_page"
            )["error"]["code"],
        )

    def test_query_schema_binding_and_validation(self):
        names = (
            "project_structure",
            "model_entities",
            "model_properties",
            "model_tree",
            "model_primary_entities",
            "diag_model_manifests",
        )
        self.servers[0].schema = {
            "tables": {
                key: [] for name in names for key in (name, f"mrt_{name}")
            }
        }
        self.assertEqual(
            self.servers[0].schema,
            self.call({}, name="query_schema")["result"]["value"],
        )
        self.assertEqual(
            ["/schema?instance_id=instance"], self.servers[0].schema_paths
        )
        self.assertEqual(
            "tool_input_invalid",
            self.call({"extra": 1}, name="query_schema")["error"]["code"],
        )
        self.check_schema_rejections()

    def check_schema_rejections(self):
        invalid = [
            {name: []}
            for name in (
                "mrt_unknown",
                "biz_atoms",
                "ops_generation_carrier_hashes",
            )
        ]
        invalid += [
            {"atoms": [{"name": "", "type": "T"}]},
            {
                "mrt_relations": [
                    {
                        "name": "header.state.status",
                        "type": "VARCHAR",
                        "values": ["active"],
                    }
                ]
            },
        ]
        invalid.append(
            {"atoms": [{"name": "x", "type": "T"}, {"name": "x", "type": "T"}]}
        )
        for tables in invalid:
            with self.subTest(tables=tables):
                self.servers[0].schema = {"tables": tables}
                self.assertEqual(
                    "workbench_unavailable",
                    self.call({}, name="query_schema")["error"]["code"],
                )
