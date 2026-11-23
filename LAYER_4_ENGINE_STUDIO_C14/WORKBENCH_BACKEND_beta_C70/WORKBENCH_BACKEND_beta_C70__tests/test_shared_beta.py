"""Exercise the real shared Beta Backend with independently owned Project peers."""

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs, urlsplit

import httpx2

from .WORKBENCH_BACKEND_beta_C70__tests__shared import write_project, process_env


def _project(projects, name):
    root = projects / name
    root.mkdir()
    manifest = write_project(root)
    manifest.write_text(manifest.read_text().replace("Declare Anechoic", name))
    return root, manifest


def _settings(directory, projects):
    path = directory / "runtime.toml"
    path.write_text(
        f'schema_version=1\n[shared_mcp]\nprojects_root="{projects}"\n'
        'http_port=8092\nmax_loaded_projects=2\n',
    )
    return path


async def _wait_ready(http, process, path):
    async with asyncio.timeout(20):
        while process.returncode is None:
            if path.exists():
                health = (await http.get("/health")).json()["result"]
                if health["initialized"] and health["pid"] == process.pid:
                    return
            await asyncio.sleep(0.05)
    raise AssertionError("Shared Beta Backend did not start")


async def _stop(process):
    process.stdin.close()
    try:
        await asyncio.wait_for(process.wait(), 20)
    except TimeoutError:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), 10)
        except TimeoutError:
            process.kill()
            await process.wait()


@asynccontextmanager
async def _backend(directory, settings):
    path = directory / "api.sock"
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-B", "-P", "-m", "WORKBENCH_BACKEND_beta_C70.shared_runtime",
        "--socket", str(path), "--host-settings", str(settings),
        env=process_env(), stdin=asyncio.subprocess.PIPE,
    )
    try:
        async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=str(path)),
                                      base_url="http://private", timeout=30, trust_env=False) as http:
            await _wait_ready(http, process, path)
            yield http, process.pid
    finally:
        await _stop(process)
    if process.returncode:
        raise AssertionError(f"Unexpected Backend exit {process.returncode}")


async def _invoke(http, root, name="query_run", arguments=None, *, base=None):
    if arguments is None:
        arguments = {"sql": 'SELECT "content.summary" FROM atoms', "result_delivery": "inline",
                     "cursor_position": 0, "page_size": 100}
    request = {"name": name, "arguments": {"project_root": str(root), **arguments},
               "session_id": None, "public_base_url": base}
    return (await http.post("/tools", json=request)).json()


async def _status(http):
    return (await http.get("/health")).json()["result"]


class SharedBetaTests(unittest.IsolatedAsyncioTestCase):
    async def test_workspace_persists_and_isolates_projects(self):
        with TemporaryDirectory(prefix="ane-beta-workspace-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            alpha, manifest = _project(projects, "alpha")
            manifest.write_text(manifest.read_text().replace("prefix='AN'", "prefix='AN', parameters={'runtime': {'workbench': {'public_url': 'https://configured.test/saved'}}}"))
            beta, _ = _project(projects, "beta")
            settings = _settings(root, projects)
            async with _backend(root, settings) as (http, _):
                session = {"session_id": "shared-session"}
                opened = await _invoke(http, alpha, "workspace_open", session)
                view = opened["result"]["value"]
                self.assertEqual("Anechoic", view["project_name"])
                view_ref = {"workspace_id": view["workspace_id"], "view_id": view["active_view_id"]}
                updated = await _invoke(http, alpha, "view_update", view_ref | {
                    "sql": "SELECT 42", "expected_revision": 0, "cursor_position": 9,
                })
                self.assertEqual(1, updated["result"]["value"]["revision"])
                base = "http://example.test"
                saved = (await _invoke(http, alpha, "view_save", view_ref, base=base))["result"]["value"]
                link = saved["saved_query_url"]
                self.assertEqual([str(alpha)], parse_qs(urlsplit(link).query)["project_root"])
                stale = await _invoke(http, alpha, "view_update", view_ref | {"sql": "", "expected_revision": 0})
                self.assertIn("error", stale)
                foreign = await _invoke(http, beta, "workspace_open", session)
                self.assertNotEqual(view_ref["view_id"], foreign["result"]["value"]["active_view_id"])
                foreign_save = await _invoke(http, beta, "query_load", {"reference": saved["saved_query_id"]})
                self.assertIn("error", foreign_save)
            async with _backend(root, settings) as (http, _):
                reopened = await _invoke(http, alpha, "view_get", view_ref)
                self.assertEqual("SELECT 42", reopened["result"]["value"]["sql"])
                self.assertEqual(1, reopened["result"]["value"]["revision"])
                loaded = await _invoke(http, alpha, "query_load", {"reference": link}, base=base)
                self.assertEqual("SELECT 42", loaded["result"]["value"]["sql"])
                configured = await _invoke(http, alpha, "query_load", {"reference": saved["saved_query_id"]})
                self.assertTrue(configured["result"]["value"]["saved_query_url"].startswith("https://configured.test/saved?query="))

    async def test_disk_generation_survives_restart_and_failed_rebuild(self):
        with TemporaryDirectory(prefix="ane-beta-disk-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            project, manifest = _project(projects, "accepted")
            settings = _settings(root, projects)
            ticket = manifest.parent / "__TKT" / "AN-T-1--task.md"
            ticket.parent.mkdir()
            async with _backend(root, settings) as (http, first_pid):
                instance = await self.query(http, project, "accepted")
                ticket.write_text("---\nidentity: [invalid\n")
                failed = await _invoke(http, project, "query_rebuild", {"target": "all"})
                self.assertIn("error", failed)
                self.assertEqual(instance, await self.query(http, project, "accepted"))
            databases = list(project.glob(".anechoic_runtime/workbench/beta/*.duckdb"))
            self.assertEqual(1, len(databases))
            async with _backend(root, settings) as (http, restarted_pid):
                self.assertNotEqual(first_pid, restarted_pid)
                refused = await _invoke(http, project)
                self.assertEqual(instance, refused["project"]["instance_id"])
                self.assertEqual("shared_gateway_failure", refused["error"]["code"])
            self.assertTrue(databases[0].is_file())
            ticket.write_text(
                "---\nidentity: {atom_id: AN-T-1}\ncontext: {container: {component: C00}}\n"
                "state: {status: active, version: 1}\n---\n\n## Summary\n\nRepaired Ticket.\n"
            )
            async with _backend(root, settings) as (http, _):
                caught_up = await _invoke(http, project)
                self.assertEqual(instance, caught_up["project"]["instance_id"])
                self.assertIn("result", caught_up, caught_up)
                self.assertEqual({("accepted",), ("Repaired Ticket.",)},
                                 {tuple(row) for row in caught_up["result"]["value"]["rows"]})
            self.assertEqual([databases[0]], list(project.glob(".anechoic_runtime/workbench/beta/*.duckdb")))

    async def test_storage_default_override_and_guarded_location(self):
        with TemporaryDirectory(prefix="ane-beta-storage-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            memory, _ = _project(projects, "memory")
            disk, manifest = _project(projects, "disk")
            manifest.write_text(manifest.read_text().replace(
                "prefix='AN'", "prefix='AN', parameters={'runtime': {'workbench': {'storage': 'disk'}}}",
            ))
            settings = _settings(root, projects)
            with settings.open("a") as configuration:
                configuration.write('[project_defaults]\nworkbench_storage="memory"\n')
            async with _backend(root, settings) as (http, _):
                await self.query(http, memory, "memory")
                self.assertFalse(list(memory.glob(".anechoic_runtime/workbench/beta/*.duckdb")))
                (disk / ".anechoic_runtime").symlink_to(memory, target_is_directory=True)
                self.assertIn("error", await _invoke(http, disk))
                (disk / ".anechoic_runtime").unlink()
                await self.query(http, disk, "disk")
                self.assertEqual(1, len(list(disk.glob(".anechoic_runtime/workbench/beta/*.duckdb"))))

    async def test_selection_rechecks_project_manifest(self):
        with TemporaryDirectory(prefix="ane-beta-admit-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            project, manifest = _project(projects, "selection")
            async with _backend(root, _settings(root, projects)) as (http, _):
                async def select():
                    return (await http.post("/selection", json={"project_root": str(project)})).json()

                ready = await select()
                self.assertEqual("AN", ready["result"]["project_prefix"])
                self.assertEqual(ready, await select())
                original = manifest.read_bytes()
                manifest.unlink()
                self.assertEqual("invalid_project_root", (await select())["error"]["code"])
                manifest.write_bytes(original)
                self.assertEqual(ready, await select())

    async def test_direct_update_returns_current_public_response(self):
        with TemporaryDirectory(prefix="ane-beta-asset-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            project, manifest = _project(projects, "asset")
            asset = manifest.parent / "__TICKETS/ASSETS/AN-T-9-ANALYSIS_REPORT--canary.md"
            asset.parent.mkdir(parents=True)
            header = ("---\natom_family: TKT\natom_id: AN-T-9\ncontainer:\n  component: C00\n"
                      "priority: 2\ncontext:\n  template: Analysis Report\nstate:\n"
                      "  status: in_queue\n  version: 1\n  updated_at: '2026-11-19T00:00:00Z'\n---\n")
            before = "\n## Summary\n\nCanary.\n"
            asset.write_text(header + before, encoding="utf-8")
            after = before + "\n## Work\n\nUpdated.\n"
            async with _backend(root, _settings(root, projects)) as (http, _):
                result = await _invoke(http, project, "atom_lifecycle_direct_update", {
                    "target": {"ref_id": "AN-T-9", "version": 1}, "changes": {"body": after},
                })
                self.assertEqual({"value": {"status": "completed"}, "text": None}, result.get("result"), result)
            self.assertEqual((header + after).encode(), asset.read_bytes())

    async def test_reuse_isolation_eviction_and_shutdown(self):
        with TemporaryDirectory(prefix="ane-beta-shared-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            alpha, manifest = _project(projects, "alpha")
            beta, _ = _project(projects, "beta")
            gamma, _ = _project(projects, "gamma")
            settings = _settings(root, projects)
            async with _backend(root, settings) as (http, backend_pid):
                catalog = (await http.get("/tools")).json()["result"]["tools"]
                self.assertEqual({
                    "query_run", "query_schema", "query_check", "query_page", "workspace_open", "workspace_list",
                    "workspace_get", "view_create", "view_duplicate", "view_list", "view_get", "view_update",
                    "view_focus", "view_rename", "view_remove", "view_run", "view_check", "view_fetch", "view_save",
                    "query_rebuild", "workbench_status", "workbench_abort", "query_log_list", "query_log_get",
                    "atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft",
                    "atom_lifecycle_change_status", "atom_lifecycle_archive", "atom_lifecycle_direct_update",
                    "query_load", "query_saved_list",
                }, {tool["name"] for tool in catalog})
                self.assertIn("project_root", catalog[0]["inputSchema"]["required"])
                cold = await _invoke(http, alpha, "workbench_status", {})
                self.assertEqual("unavailable", cold["result"]["value"]["mode"])
                self.assertEqual({}, self.loaded(await _status(http)))
                first, evicted = await self.assert_isolation(http, backend_pid, alpha, beta, gamma)
                live = await self.assert_rebind(http, alpha, manifest, first)
                await self.assert_admission_refusals(http, projects, alpha, settings)
            self.assert_stopped(evicted | live | first)

    async def assert_isolation(self, http, backend_pid, alpha, beta, gamma):
        first = await self.query(http, alpha, "alpha")
        second = await self.query(http, beta, "beta")
        await self.assert_result_isolation(http, alpha, beta)
        self.assertNotEqual(first, second)
        loaded = self.loaded(await _status(http))
        self.assertEqual({first, second}, set(loaded))
        peers = loaded[first] | loaded[second]
        self.assertEqual(4, len(peers))
        self.assertNotIn(backend_pid, peers)
        self.assertEqual(first, await self.query(http, alpha, "alpha"))
        self.assertEqual(loaded, self.loaded(await _status(http)))
        third = await self.query(http, gamma, "gamma")
        after = self.loaded(await _status(http))
        self.assertEqual({first, third}, set(after))
        self.assertEqual(loaded[first], after[first])
        self.assert_stopped(loaded[second])
        return loaded[first], loaded[second]

    async def assert_result_isolation(self, http, alpha, beta):
        result = await _invoke(http, alpha)
        query_id = result["result"]["value"]["query_id"]
        params = {"query_id": query_id, "offset": 0, "page_size": 100, "result_delivery": "inline"}
        page = await _invoke(http, alpha, "query_page", params)
        self.assertEqual([["alpha"]], page["result"]["value"]["rows"])
        foreign = await _invoke(http, beta, "query_page", params)
        self.assertEqual("query_error", foreign["error"]["code"])
        rebuilt = await _invoke(http, alpha, "query_rebuild", {"target": "all"})
        new_id = rebuilt["result"]["value"]["result_ids"][query_id]
        self.assertNotEqual(query_id, new_id)
        params["query_id"] = new_id
        page = await _invoke(http, alpha, "query_page", params)
        self.assertEqual([["alpha"]], page["result"]["value"]["rows"])
        foreign = await _invoke(http, beta, "query_page", params)
        self.assertEqual("query_error", foreign["error"]["code"])

    async def assert_rebind(self, http, root, manifest, prior):
        manifest.write_text(manifest.read_text().replace("\nalpha\n", "\nupdated alpha\n"))
        identity = await self.query(http, root, "updated alpha")
        loaded = self.loaded(await _status(http))
        self.assertEqual(2, len(loaded))
        self.assertTrue(prior.isdisjoint(loaded[identity]))
        self.assert_stopped(prior)
        return set().union(*loaded.values())

    async def assert_admission_refusals(self, http, projects, alpha, settings):
        link = projects / "link"
        link.symlink_to(alpha, target_is_directory=True)
        for path, code in ((projects.parent, "outside_project_root"), (link, "invalid_project_root")):
            result = await http.post("/selection", json={"project_root": str(path)})
            self.assertEqual(code, result.json()["error"]["code"])
        blocked, manifest = _project(projects, "blocked")
        manifest.write_text(manifest.read_text().replace(
            "prefix='AN'", "prefix='AN', parameters={'project_mcp': {'tool_blacklist': ['query_run']}}",
        ))
        self.assertEqual("tool_unavailable", (await _invoke(http, blocked))["error"]["code"])
        settings.write_text(settings.read_text().replace("8092", "8093"))
        result = await http.post("/selection", json={"project_root": str(alpha)})
        self.assertEqual("host_configuration_stale", result.json()["error"]["code"])

    async def query(self, http, root, expected):
        reply = await _invoke(http, root)
        self.assertIn("result", reply, reply)
        self.assertEqual([[expected]], reply["result"]["value"]["rows"])
        return reply["project"]["instance_id"]

    def loaded(self, report):
        self.assertEqual(report["loaded_project_count"], len(report["loaded_project_processes"]))
        self.assertLessEqual(report["loaded_project_count"], report["max_loaded_projects"])
        return {entry["instance_id"]: {entry["kernel_pid"], entry["orchestrator_pid"]}
                for entry in report["loaded_project_processes"]}

    def assert_stopped(self, pids):
        for pid in pids:
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)


if __name__ == "__main__":
    unittest.main()
