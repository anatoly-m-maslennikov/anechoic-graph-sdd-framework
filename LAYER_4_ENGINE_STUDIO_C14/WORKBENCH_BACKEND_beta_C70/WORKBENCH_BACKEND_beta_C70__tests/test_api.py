"""Exercise Backend, Kernel, and Orchestrator through their private processes."""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest

import httpx2

from .WORKBENCH_BACKEND_beta_C70__tests__shared import start_backend, stop_backend, write_project
from .saved_sql_cases import assert_save_failures, assert_saved_writes


CONFIGURED_PAGE = "https://configured.example.test:8443/custom/workbench/"


def _client(path):
    return httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)),
                         base_url="http://private", timeout=10, trust_env=False)


def _ready(client, process, socket):
    until = monotonic() + 90
    while process.poll() is None and monotonic() < until:
        if not socket.is_socket():
            sleep(0.05)
            continue
        try:
            response = client.get("/health")
        except httpx2.TransportError:
            sleep(0.05)
            continue
        response.raise_for_status()
        return response.json()
    raise AssertionError("Backend did not start")


def write_component(control, *, version=1, name="Initial Studio", component_id="C14", prefix="AN"):
    component = control / f"{prefix}-S-2-SPEC-COMPONENT_MANIFEST--declare-studio.md"
    component.write_text(
        f"---\natom_family: SPEC\natom_id: {prefix}-S-2\ncontainer:\n  component: C00\ntier: 4\n"
        f"context:\n  template: component_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: {version}\n"
        f"  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\n{name}\n\n"
        "## Formal Manifest\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ComponentManifest\n"
        "declare_entity(entity_name='Component Manifest', "
        f"instance=ComponentManifest(component_id={component_id!r}, name={name!r}, "
        "layer=3, lens_whitelist=['SPEC']))\n```\n",
        encoding="utf-8",
    )
    return component


class ApiTests(unittest.TestCase):
    def test_query_and_worker_state_are_served_by_separate_processes(self):
        with TemporaryDirectory(prefix="ane-beta-", dir="/tmp") as folder:
            root = Path(folder).resolve()
            manifest = write_project(root)
            control = manifest.parent
            write_component(control)
            manifest = manifest.rename(root / manifest.name)
            saved = root / ".anechoic_runtime/workbench/saved_queries"
            saved.mkdir(parents=True)
            (saved / ("q_" + "a" * 32 + ".sql")).write_text("SELECT 42", encoding="utf-8")
            socket = root / "api.sock"
            digest = sha256(manifest.read_bytes()).hexdigest()
            process = start_backend(root, control, manifest, digest, "--workbench-public-url", CONFIGURED_PAGE)
            try:
                with _client(socket) as api, _client(root / "jobs.sock") as jobs, _client(root / "db.sock") as db:
                    backend = _ready(api, process, socket)
                    orchestrator = jobs.get("/health").json()["result"]
                    self.assertEqual(process.pid, backend["pid"])
                    self.assertEqual(3, len({backend["pid"], backend["kernel_pid"], orchestrator["pid"]}))
                    self.assertEqual(digest, backend["manifest_sha256"])
                    self.assert_query_and_jobs(api)
                    self.assert_worker_abort(api)
                    self.assert_saved_reads(api)
                    assert_save_failures(self, api, control)
                    assert_saved_writes(self, api, root)
                    self.assert_file_delivery(api, root)
                    self.assert_delivery_defaults_and_preview(api, root)
                    self.assert_refresh(api, db, control, digest)
            finally:
                stop_backend(process)
            self.assertEqual(0, process.returncode)
            for pid in (backend["kernel_pid"], orchestrator["pid"]):
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def assert_query_and_jobs(self, api):
        params = {"instance_id": "instance"}
        envelope = {"name": "query_run", "arguments": {"sql": "SELECT reference FROM atoms WHERE reference = 'AN-S-001'"},
                    "instance_id": "instance", "session_id": None, "public_base_url": None,
                    "asserted_project_root": None}
        tools = api.get("/tools", params=params).json()["result"]["tools"]
        self.assertTrue({"query_run", "query_schema", "query_check", "query_page", "workspace_open", "view_get", "view_save"}
                        <= {tool["name"] for tool in tools})
        query = api.post("/tools", json=envelope).json()
        result = query["result"]["value"]
        self.assertEqual([{"name": "reference", "type": "VARCHAR", "has_values": True}], result["columns"])
        self.assertEqual([["AN-S-001"]], result["rows"])
        schema = api.post("/tools", json=envelope | {"name": "query_schema", "arguments": {}}).json()
        tables = schema["result"]["value"]["tables"]
        self.assertEqual([{"name": "reference", "type": "VARCHAR"},
                          {"name": "content.summary", "type": "VARCHAR"}], tables["atoms"][:2])
        self.assertIn("module_imports", tables)
        self.assertIn("native_references", tables)
        status = next(column for column in tables["atoms"] if column["name"] == "header.state.status")
        self.assertEqual(["active"], status["values"])
        invalid_schema = api.post("/tools", json=envelope | {"name": "query_schema", "arguments": {"extra": 1}}).json()
        self.assertEqual("tool_input_invalid", invalid_schema["error"]["code"])
        self.assert_query_check(api, envelope)
        runs = api.get("/jobs/worker-runs", params=params).json()["result"]
        self.assertIsNone(runs["active"])
        self.assertEqual("succeeded", runs["latest"]["state"])
        status = api.post("/tools", json=envelope | {"name": "workbench_status", "arguments": {}}).json()["result"]["value"]
        self.assertEqual((False, None, None), (status["syncing"], status["run_id"], status["worker_alive"]))
        invalid = api.post("/tools", json=envelope | {"name": "workbench_abort", "arguments": {}}).json()
        self.assertEqual("tool_input_invalid", invalid["error"]["code"])
        missing = api.post("/tools", json=envelope | {"name": "workbench_abort", "arguments": {"run_id": "other"}}).json()
        self.assertEqual("run_not_abortable", missing["error"]["code"])
        wrong_binding = api.get("/tools", params={"instance_id": "other"}).json()
        self.assertEqual("value_error", wrong_binding["error"]["code"])

    def assert_worker_abort(self, api):
        envelope = {"instance_id": "instance", "session_id": None, "public_base_url": None,
                    "asserted_project_root": None}
        with ThreadPoolExecutor() as executor:
            rebuild = executor.submit(api.post, "/tools", json=envelope | {
                "name": "query_rebuild", "arguments": {"target": "all"}})
            deadline = monotonic() + 10
            while monotonic() < deadline:
                status = api.post("/tools", json=envelope | {"name": "workbench_status", "arguments": {}}).json()
                value = status["result"]["value"]
                if value["worker_alive"]:
                    break
                if rebuild.done():
                    self.fail("Rebuild completed before its Worker could be observed")
                sleep(0.01)
            else:
                self.fail("Worker did not start")
            self.assertTrue(value["syncing"])
            run_id = value["run_id"]
            self.assertTrue(run_id)
            query = api.post("/tools", json=envelope | {"name": "query_run", "arguments": {
                "sql": "SELECT 42", "result_delivery": "inline", "result_format": "json_matrix"}}).json()
            self.assertEqual([[42]], query["result"]["value"]["rows"])
            response = api.post("/tools", json=envelope | {
                "name": "workbench_abort", "arguments": {"run_id": run_id}}).json()
            self.assertEqual({"run_id": run_id, "state": "aborting"}, response["result"]["value"])
            self.assertEqual("worker_aborted", rebuild.result(timeout=10).json()["error"]["code"])

    def assert_saved_reads(self, api):
        saved_id = "q_" + "a" * 32
        envelope = {"instance_id": "instance", "session_id": None, "public_base_url": "http://example.test",
                    "asserted_project_root": None}
        call = lambda name, args: api.post("/tools", json=envelope | {"name": name, "arguments": args}).json()
        listing = call("query_saved_list", {})["result"]["value"]["items"]
        self.assertEqual(saved_id, listing[0]["saved_query_id"])
        self.assertNotIn("sql", listing[0])
        link = listing[0]["saved_query_url"]
        self.assertEqual(f"http://example.test/anechoic/workbench/Anechoic?query={saved_id}", link)
        self.assertEqual("SELECT 42", call("query_load", {"reference": link})["result"]["value"]["sql"])
        foreign = link.replace("/Anechoic?", "/Another?")
        self.assertEqual("tool_input_invalid", call("query_load", {"reference": foreign})["error"]["code"])
        self.assertEqual("tool_input_invalid", call("query_saved_list", {"limit": True})["error"]["code"])

    def assert_file_delivery(self, api, root):
        envelope = {"instance_id": "instance", "session_id": None, "public_base_url": None,
                    "asserted_project_root": None}
        call = lambda name, args: api.post("/tools", json=envelope | {"name": name, "arguments": args}).json()
        run = call("query_run", {"sql": "SELECT 42 AS answer", "result_delivery": "file", "result_format": "csv"})
        result = run["result"]["value"]
        file = result["result_file"]
        self.assertEqual("csv", file["format"])
        self.assertNotIn("rows", result)
        self.assertIn(b"42", (root / file["path"]).read_bytes())
        saved = call("query_run", {"sql": "SELECT 44", "save": True, "result_delivery": "file"})["result"]["value"]
        self.assertEqual("query", saved["kind"])
        self.assertEqual(f"{CONFIGURED_PAGE}?query={saved['saved_query_id']}", saved["saved_query_url"])
        self.assertEqual("tool_input_invalid", call("query_load", {"reference": saved["saved_query_url"]})["error"]["code"])
        loaded = call("query_load", {"reference": saved["saved_query_id"]})["result"]["value"]
        self.assertEqual(("SELECT 44", saved["saved_query_url"]), (loaded["sql"], loaded["saved_query_url"]))
        self.assertNotIn("sql", saved)
        self.assertIn(b"44", (root / saved["result_file"]["path"]).read_bytes())
        page = call("query_page", {"query_id": result["query_id"], "result_delivery": "file", "result_format": "json_matrix"})
        self.assertIn(b"42", (root / page["result"]["value"]["result_file"]["path"]).read_bytes())
        inline = call("query_page", {"query_id": result["query_id"], "result_delivery": "inline", "result_format": "csv"})
        self.assertIn("42", inline["result"]["value"]["csv"])
        opened = call("workspace_open", {"session_id": "file-delivery"})["result"]["value"]
        view = {"workspace_id": opened["workspace_id"], "view_id": opened["views"][0]["id"]}
        call("view_update", view | {"sql": "SELECT 43 AS answer", "expected_revision": opened["views"][0]["revision"]})
        call("view_run", view)
        fetch = call("view_fetch", view | {"result_delivery": "file", "result_format": "toon"})
        self.assertIn(b"43", (root / fetch["result"]["value"]["result_file"]["path"]).read_bytes())
        for args in ({"sql": "SELECT 1", "result_delivery": "invalid"}, {"sql": "SELECT 1", "result_format": "invalid"}):
            self.assertEqual("tool_input_invalid", call("query_run", args)["error"]["code"])

    def assert_delivery_defaults_and_preview(self, api, root):
        envelope = {"instance_id": "instance", "session_id": None, "public_base_url": None,
                    "asserted_project_root": None}
        call = lambda name, args: api.post("/tools", json=envelope | {"name": name, "arguments": args}).json()
        run = call("query_run", {"sql": "SELECT * FROM range(10)", "preview": 3})["result"]["value"]
        self.assertEqual(3, run["row_count"])
        self.assertEqual(3, len(run["rows"]))
        page = call("query_page", {"query_id": run["query_id"], "preview": 2})["result"]["value"]
        self.assertEqual(2, page["result_file"]["row_count"])
        self.assertTrue((root / page["result_file"]["path"]).is_file())
        for invalid in (-1, True, 1.5):
            self.assertEqual("tool_input_invalid", call("query_run", {"sql": "SELECT 1", "preview": invalid})["error"]["code"])
            self.assertEqual("tool_input_invalid", call("query_page", {"query_id": run["query_id"], "preview": invalid})["error"]["code"])
        opened = call("workspace_open", {"session_id": "default-file"})["result"]["value"]
        view = {"workspace_id": opened["workspace_id"], "view_id": opened["views"][0]["id"]}
        call("view_update", view | {"sql": "SELECT 43", "expected_revision": opened["views"][0]["revision"]})
        call("view_run", view)
        fetch = call("view_fetch", view)["result"]["value"]
        self.assertTrue((root / fetch["result_file"]["path"]).is_file())

    def assert_query_check(self, api, envelope):
        sql = "SELECT '😀' AS label"
        data = envelope | {"name": "query_check", "arguments": {"sql": sql, "cursor_position": 8}}
        result = api.post("/tools", json=data).json()["result"]["value"]
        self.assertEqual({"valid": True, "columns": [{"name": "label", "type": "VARCHAR", "has_values": True}],
                          "sql": sql, "row_count": 1, "column_count": 1}, result)
        data["arguments"]["cursor_position"] = 9
        self.assertEqual("tool_input_invalid", api.post("/tools", json=data).json()["error"]["code"])
        data["arguments"] = {"sql": "DELETE FROM atoms"}
        self.assertEqual("query_error", api.post("/tools", json=data).json()["error"]["code"])

    def generation(self, db, digest):
        params = {"instance_id": "instance"}
        model = db.get("/model", params=params)
        structure = db.get("/structure", params=params)
        self.assertEqual(model.json()["model_sha256"], structure.json()["model_sha256"])
        self.assertEqual(digest, structure.json()["project"]["sha256"])
        self.assertEqual(model.headers["x-anechoic-generation"], structure.headers["x-anechoic-generation"])
        return structure.headers["x-anechoic-generation"], structure.json()["components"]["C14"]["ref"]

    def wait_for_build(self, api, previous, status):
        until = monotonic() + 20
        while monotonic() < until:
            result = api.get("/jobs/worker-runs", params={"instance_id": "instance"}).json()
            latest = result["result"]["latest"]
            if latest and latest != previous and latest["state"] == status:
                return latest
            sleep(0.1)
        self.fail(f"Timed out waiting for build {status}: {latest}")

    def assert_refresh(self, api, db, control, digest):
        initial = self.generation(db, digest)
        self.assertEqual("AN-S-2@1", initial[1])
        previous = api.get("/jobs/worker-runs", params={"instance_id": "instance"}).json()["result"]["latest"]
        write_component(control, version=2, name="Revised Studio")
        success = self.wait_for_build(api, previous, "succeeded")
        revised = self.generation(db, digest)
        self.assertNotEqual(initial[0], revised[0])
        self.assertEqual("AN-S-2@2", revised[1])
        self.assert_summary(api, "Revised Studio")
        write_component(control, version=3, name="Invalid Studio", component_id="invalid")
        failed = self.wait_for_build(api, success, "failed")
        self.assertEqual(revised, self.generation(db, digest))
        self.assert_summary(api, "Revised Studio")
        write_component(control, version=4, name="Recovered Studio")
        self.wait_for_build(api, failed, "succeeded")
        self.assertEqual("AN-S-2@4", self.generation(db, digest)[1])
        self.assert_summary(api, "Recovered Studio")

    def assert_summary(self, api, name):
        result = api.post("/tools", json={
            "name": "query_run",
            "arguments": {"sql": """SELECT "content.summary" FROM atoms WHERE reference = 'AN-S-2'"""},
            "instance_id": "instance", "session_id": None, "public_base_url": None,
            "asserted_project_root": None,
        }).json()
        self.assertEqual([[name]], result["result"]["value"]["rows"])
