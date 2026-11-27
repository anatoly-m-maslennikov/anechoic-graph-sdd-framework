"""Exercise the API CLI against private HTTP peers."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from hashlib import sha256
from pathlib import Path

import httpx2

ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE))
from API_MIXER_beta_C91.API_MIXER_beta_C91__tests._package__shared import (
    ApiPeer as Peer,
)
from API_MIXER_beta_C91.API_MIXER_beta_C91__tests._package__shared import Server

DIGEST = "a" * 64
MODULE = "API_MIXER_beta_C91.API_MIXER_beta_C91__shared"
KERNEL = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"


def generation():
    model = json.dumps({"model_sha256": "b" * 64, "binding_schema": 1, "modules": {"__init__.py": "d" * 64},
                        "module_order": [], "class_modules": {}, "bindings": {"endpoints": {}}}, indent=2)
    structure = json.dumps({"model_sha256": "b" * 64, "project": {"ref": "AN-S-1", "sha256": DIGEST},
                            "components": {}}, indent=2)
    atoms = [
        {"reference": ref, "exact_ref": exact, "status": status, "status_group": group, "version": 1,
         "filename": ref + ".md", "relative_path": "control", "summary": "Fixture"}
        for ref, exact, status, group in (
            ("AN-S-1", "AN-S-1@1", "active", "Current"), ("AN-T-2", "AN-T-2@1", "in_queue", "Current"),
            ("AN-P-3", "AN-P-3@1", "active", "Current"), ("AN-C-4@1-draft", "AN-C-4@1-draft", "draft", "Draft"),
        )]
    snapshot = {"schema_version": 2, "manifest_sha256": DIGEST, "atoms": atoms, "relations": [], "relation_types": []}
    graph = {name: [] for name in ("nodes", "occurrences", "edges", "read_issues", "test_edges")}
    return {"instance_id": "instance", "snapshot": snapshot, "model": model, "structure": structure, "graph": graph,
            "carrier_hashes": {"control/" + atom["filename"]: DIGEST for atom in atoms},
            "receipt": {"manifest_sha256": DIGEST, "model_sha256": "b" * 64,
            "snapshot_sha256": sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "graph_sha256": sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "model_descriptor_sha256": sha256(model.encode()).hexdigest(), "structure_sha256": sha256(structure.encode()).hexdigest()}}


class ApiProcessTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir="/tmp")
        self.path = Path(self.directory.name).resolve()
        self.servers = []
        for kind in ("db", "jobs"):
            server = Server(str(self.path / (kind + ".sock")), Peer)
            os.chmod(self.path / (kind + ".sock"), 0o600)
            server.kind, server.received, server.schema_paths = kind, [], []
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        (self.path / "peers.ready").touch(mode=0o600)
        self.manifest = self.path / "manifest"
        self.manifest.write_text("manifest")
        info = self.manifest.lstat()
        version = [info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns]
        self.gate = self.path / "gate"
        env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_BETA_DIRECT_MANIFEST": json.dumps(
            {"path": str(self.manifest), "gate": str(self.gate), "version": version})}
        args = [sys.executable, "-B", "-P", "-m", MODULE, "--role", "api", "--socket", str(self.path / "api.sock"),
                "--instance-id", "instance", "--project-root", str(self.path), "--control-root", "control",
                "--manifest-path", "manifest", "--manifest-sha256", DIGEST, "--project-prefix", "AN", "--project-name", "Project"]
        self.args, self.env = args, env
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, env=env, cwd=ENGINE, stderr=subprocess.PIPE)
        self.client = httpx2.Client(transport=httpx2.HTTPTransport(uds=str(self.path / "api.sock")),
                                    base_url="http://private", trust_env=False, timeout=1)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(self.process.stderr.read().decode())
            if not (self.path / "api.sock").exists():
                time.sleep(0.05)
                continue
            try:
                if self.client.get("/health").json()["state"] == "ready":
                    return
            except httpx2.TransportError:
                time.sleep(0.05)
        self.fail("API did not start")

    def tearDown(self):
        self.client.close()
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.directory.cleanup()

    def call(self, arguments, **updates):
        data = {"name": "query_run", "arguments": arguments, "instance_id": "instance", "session_id": None,
                "public_base_url": None, "asserted_project_root": None}
        return self.client.post("/tools", json=data | updates).json()

    def test_catalog_query_validation_and_manifest_gate(self):
        catalog = self.client.get("/tools", params={"instance_id": "instance"}).json()["result"]
        self.assertEqual(["query_run", "query_check", "query_page", "query_schema",
                          "iwe_console_status", "iwe_console_abort", "workbench_status", "workbench_abort", "query_rebuild",
                          "query_load", "query_saved_list", "view_save", "workspace_open", "workspace_list",
                          "workspace_get", "query_log_list", "query_log_get", "view_create", "view_duplicate", "view_list",
                          "view_get", "view_update", "view_focus", "view_rename", "view_remove", "view_run", "view_check", "view_fetch",
                          "atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive", "atom_lifecycle_create_asset", "atom_lifecycle_direct_update", "iwe_console_atom_document"],
                         [tool["name"] for tool in catalog["tools"]])
        result = self.call({"sql": "SELECT 42", "result_delivery": "inline"})
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        sent = self.servers[0].received[-1]
        self.assertEqual(100, sent["page_size"])
        self.assertEqual("json_matrix", sent["result_format"])
        self.call({"sql": "SELECT 42"})
        self.assertEqual(1000, self.servers[0].received[-1]["page_size"])
        for args in ({"sql": 42}, {"sql": "SELECT 1", "page_size": True},
                     {"sql": "SELECT 1", "save": 1}, {"sql": "SELECT 1", "name": "x"},
                     {"sql": "SELECT 1", "preview": None}):
            self.assertEqual("tool_input_invalid", self.call(args)["error"]["code"])
        self.assertEqual("tool_unavailable", self.call({}, name="not_supported")["error"]["code"])
        self.assertEqual("value_error", self.call({"sql": "SELECT 1"}, instance_id="other")["error"]["code"])
        self.assertEqual("value_error", self.call({"sql": "SELECT 1"}, asserted_project_root="/other")["error"]["code"])
        oversized = self.call({"sql": "x" * 65536})
        self.assertEqual("value_error", oversized["error"]["code"])
        self.gate.write_text("project_manifest_reloading")
        self.assertEqual("project_manifest_reloading", self.call({"sql": "SELECT 1"})["error"]["code"])
        self.assertEqual("pending", self.client.get("/health").json()["state"])

    def test_invalid_kernel_reply_is_unavailable(self):
        self.servers[0].invalid = True
        request = {"name": "query_run", "arguments": {"sql": "SELECT 1"}, "instance_id": "instance",
                   "session_id": None, "public_base_url": None, "asserted_project_root": None}
        response = self.client.post("/tools", json=request)
        self.assertEqual(503, response.status_code)
        self.assertEqual("workbench_unavailable", response.json()["error"]["code"])

    def test_blacklist_hides_and_rejects_tool(self):
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        self.process = subprocess.Popen(self.args + ["--blacklist", "query_run"], stdin=subprocess.PIPE,
                                        env=self.env, cwd=ENGINE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (self.path / "api.sock").exists():
                try:
                    catalog = self.client.get("/tools", params={"instance_id": "instance"}).json()
                    break
                except httpx2.TransportError:
                    pass
            time.sleep(0.05)
        else:
            self.fail("Blacklisted API did not start")
        self.assertEqual(["query_check", "query_page", "query_schema", "iwe_console_status", "iwe_console_abort", "workbench_status", "workbench_abort", "query_rebuild",
                          "query_load", "query_saved_list", "view_save", "workspace_open", "workspace_list",
                          "workspace_get", "query_log_list", "query_log_get", "view_create", "view_duplicate", "view_list",
                          "view_get", "view_update", "view_focus", "view_rename", "view_remove", "view_run", "view_check", "view_fetch",
                          "atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive", "atom_lifecycle_create_asset", "atom_lifecycle_direct_update", "iwe_console_atom_document"],
                         [tool["name"] for tool in catalog["result"]["tools"]])
        self.assertEqual(["query_run"], catalog["result"]["blacklist"])
        self.assertEqual("tool_unavailable", self.call({"sql": "SELECT 1"})["error"]["code"])

    def test_query_check_forwards_unpaged_sql_and_validates_cursor(self):
        sql = "SELECT '😀' AS label"
        result = self.call({"sql": sql, "cursor_position": 8}, name="query_check")["result"]["value"]
        self.assertEqual({"instance_id": "instance", "sql": sql}, self.servers[0].received[-1])
        self.assertEqual({"valid": True, "columns": [{"name": "answer", "type": "INTEGER", "has_values": True}],
                          "sql": sql, "row_count": 1, "column_count": 1}, result)
        self.assertEqual("tool_input_invalid", self.call({"sql": sql, "cursor_position": 9}, name="query_check")["error"]["code"])
        self.assertEqual("tool_input_invalid", self.call({"sql": sql, "page_size": 1}, name="query_check")["error"]["code"])
        self.assertEqual("query_error", self.call({"sql": "DELETE FROM atoms"}, name="query_check")["error"]["code"])

    def test_query_page_forwards_defaults_grid_and_rejections(self):
        result = self.call({"query_id": "query"}, name="query_page")["result"]["value"]
        self.assertEqual([[42]], result["rows"])
        self.assertEqual({"instance_id": "instance", "query_id": "query", "offset": 0, "page_size": 100,
                          "result_delivery": "file", "result_format": "json_matrix"}, self.servers[0].received[-1])
        grid = {"sort": [{"column": 0, "direction": "desc"}], "filters": [],
                "group_by": {"column": 0, "direction": "asc"}}
        args = {"query_id": "query", "offset": 2, "page_size": 5, "preview": 3, "grid": grid,
                "result_delivery": "inline", "result_format": "csv"}
        self.call(args, name="query_page")
        self.assertEqual({"instance_id": "instance", **args}, self.servers[0].received[-1])
        for invalid in ({"query_id": "q", "offset": True}, {"query_id": "q", "page_size": 0},
                        {"query_id": "q", "grid": []}, {"query_id": "q", "preview": -1}):
            self.assertEqual("tool_input_invalid", self.call(invalid, name="query_page")["error"]["code"])
        self.assertEqual("query_error", self.call({"query_id": "q", "grid": {"bad": True}},
                                                   name="query_page")["error"]["code"])

    def test_query_schema_binding_and_validation(self):
        names = ("project_structure", "model_entities", "model_properties", "model_tree",
                 "model_primary_entities", "diag_model_manifests")
        self.servers[0].schema = {"tables": {key: [] for name in names for key in (name, f"mrt_{name}")}}
        self.assertEqual(self.servers[0].schema, self.call({}, name="query_schema")["result"]["value"])
        self.assertEqual(["/schema?instance_id=instance"], self.servers[0].schema_paths)
        self.assertEqual("tool_input_invalid", self.call({"extra": 1}, name="query_schema")["error"]["code"])
        invalid = [{name: []} for name in ("mrt_unknown", "biz_atoms", "ops_generation_carrier_hashes")]
        invalid += [{"atoms": [{"name": "", "type": "T"}]}, {"mrt_relations": [{"name": "header.state.status", "type": "VARCHAR", "values": ["active"]}]}]
        invalid.append({"atoms": [{"name": "x", "type": "T"}, {"name": "x", "type": "T"}]})
        for tables in invalid:
            with self.subTest(tables=tables):
                self.servers[0].schema = {"tables": tables}
                self.assertEqual("workbench_unavailable", self.call({}, name="query_schema")["error"]["code"])

    def test_query_family_against_real_kernel(self):
        self.servers[0].shutdown()
        self.servers[0].server_close()
        database = self.path / "db.sock"
        database.unlink(missing_ok=True)
        env = {**self.env, "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(ENGINE.parent / ".anechoic_tmp/workbench/extensions")}
        command = [sys.executable, "-B", "-P", "-m", KERNEL, "--socket", str(database),
                   "--instance-id", "instance", "--manifest-sha256", DIGEST, "--project-root", str(self.path)]
        kernel = subprocess.Popen(command, env=env, cwd=ENGINE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 20
            while not database.exists() and kernel.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            if not database.exists():
                kernel.terminate() if kernel.poll() is None else None
                self.fail(kernel.stderr.read().decode())
            with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(database)), base_url="http://private",
                               trust_env=False, timeout=20) as client:
                response = client.put("/generation", json=generation())
                self.assertEqual(200, response.status_code, response.text)
            self.assert_real_kernel_queries()
        finally:
            if kernel.poll() is None:
                kernel.terminate()
            kernel.wait(timeout=10)
            kernel.stderr.close()

    def assert_real_kernel_queries(self):
        run = self.call({"sql": "SELECT 42 AS answer", "result_delivery": "inline"})["result"]["value"]
        self.assertEqual([[42]], run["rows"])
        checked = self.call({"sql": "SELECT 42 AS answer"}, name="query_check")["result"]["value"]
        self.assertEqual((True, 1, 1), (checked["valid"], checked["row_count"], checked["column_count"]))
        page = self.call({"query_id": run["query_id"], "result_delivery": "inline",
                          "grid": {"sort": [{"column": 0, "direction": "desc"}]}}, name="query_page")
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        exported = self.call({"query_id": run["query_id"]}, name="query_page")["result"]["value"]["result_file"]
        self.assertEqual(1, exported["row_count"])
        self.assertTrue((self.path / exported["path"]).is_file())
        csv = self.call({"query_id": run["query_id"], "result_delivery": "inline", "result_format": "csv"},
                        name="query_page")["result"]["value"]["csv"]
        self.assertIn("42", csv)
        self.assert_public_schema()
        self.assertEqual("query_error", self.call({"query_id": run["query_id"], "grid": {"bad": True}},
                                                   name="query_page")["error"]["code"])
        rebuilt = self.call({"target": run["query_id"]}, name="query_rebuild")["result"]["value"]
        new_id = rebuilt["result_ids"][run["query_id"]]
        page = self.call({"query_id": new_id, "result_delivery": "inline"}, name="query_page")
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        partial = self.call({"sql": "SELECT 99", "save": True, "result_delivery": "inline"})["result"]["value"]
        self.assertEqual("partial", partial["outcome"])
        self.assertTrue(partial["save_error"])
        self.assertEqual([[99]], partial["rows"])
        opened = self.call({"session_id": "no-journal"}, name="workspace_open")["result"]["value"]
        view = {"workspace_id": opened["workspace_id"], "view_id": opened["active_view_id"]}
        self.call({**view, "sql": "SELECT 7", "expected_revision": 0}, name="view_update")
        failed_save = self.call({**view, "save": True}, name="view_run")["result"]["value"]
        self.assertEqual(("success", "partial"), (failed_save["status"], failed_save["outcome"]))
        self.assertTrue(failed_save["save_error"])
        self.assertEqual([[7]], self.call({**view, "result_delivery": "inline"}, name="view_fetch")["result"]["value"]["rows"])

    def assert_public_schema(self):
        tables = self.call({}, name="query_schema")["result"]["value"]["tables"]
        for canonical, alias in (("mrt_atoms", "atoms"), ("mrt_atom_references", "native_references"), ("mrt_atom_graph_relations", "relations"),
                                 ("src_flow_events", "flow_events"), ("biz_package_coupling", "package_coupling"),
                                 ("mrt_real_graph_import_occurrences", "module_imports"), ("mrt_diag_code_access", "code_access_findings")):
            self.assertEqual(tables[canonical], tables[alias], (canonical, alias))
        self.assertIn("code", {column["name"] for column in tables["ops_ingestion_issues"]})
        self.assertNotIn("ops_generation_carrier_hashes", tables)
        for table, rows, values in (
            ("mrt_spec_atoms", [["AN-S-1"]], ["active"]),
            ("mrt_ticket_atoms", [["AN-T-2"]], ["in_queue"]),
            ("mrt_project_config_atoms", [["AN-C-4@1-draft"], ["AN-P-3"]], ["active", "draft"]),
        ):
            with self.subTest(table=table):
                status = next(column for column in tables[table] if column["name"] == "header.state.status")
                self.assertEqual({"name": "header.state.status", "type": "VARCHAR", "values": values}, status)
                sql = f"SELECT reference FROM main.{table} ORDER BY reference"
                self.assertEqual(rows, self.call({"sql": sql, "result_delivery": "inline"})["result"]["value"]["rows"])


if __name__ == "__main__":
    unittest.main()
