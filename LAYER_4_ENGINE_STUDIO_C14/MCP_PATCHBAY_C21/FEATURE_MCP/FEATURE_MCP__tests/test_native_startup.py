"""Normal startup selects one validated Project across the migration rename."""
from .native_query_test_support import local_gateway
from .FEATURE_MCP__tests__shared import write_manifest
from .test_launcher_runtime_profiles import DirectSupervisorProbe, runtime_flags


import asyncio
from fcntl import LOCK_EX, LOCK_NB, flock
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from starlette.responses import StreamingResponse
from starlette.routing import Route

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    MCP_PATH, ProjectAdmissionError, ProjectBinding, http_main, project_admission, runtime_stack,
    select_runtime_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations
MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"



def native_fixture_gateway(root, cache, *, selection=None):
    from dataclasses import asdict, replace
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import NativeProjectSelection
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project as startup_selection
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner
    from .native_query_test_support import load_native_inputs

    fields = asdict(selection if selection is not None else startup_selection(root))
    fields.pop("tool_blacklist", None)
    fields.pop("release_workflows_enabled", None)
    selected = NativeProjectSelection(**fields)
    inputs = replace(load_native_inputs(selected), extension_directory=cache)
    return local_gateway(root, native_query=NativeQueryOwner(selected, inputs))


class RuntimeSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admit = cls.enterClassContext(project_admission())

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def legacy(self, name=".anechoic_anechoic", declared=None):
        control = self.root / name
        control.mkdir()
        (control / "anechoic_project_settings.toml").write_text(
            '[project]\nname="Anechoic"\nkey="anechoic"\nrepository_slug="anechoic"\n'
            f'[paths]\ncontrol_root="{declared or name}"\n[artifacts.identity]\nproject_prefix="CA"\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(self.root, control_root=control)
        return control

    manifest = write_manifest

    def select(self, control=None):
        return self.admit(self.root, control)

    def test_staging_then_final_rename(self):
        old = self.legacy()
        staged = self.root / ".anechoic_new"
        self.manifest(staged)
        with self.assertRaises(ProjectAdmissionError):
            self.select()
        old.rename(self.root / ".anechoic_legacy")
        staged.rename(old)
        selected = self.select()
        self.assertIsInstance(selected, ProjectBinding)
        self.assertEqual(old, selected.control_root)
        self.assertEqual("AN-S-001@1", selected.manifest_ref)

    def test_legacy_setting_is_ignored_even_when_explicit_native_project_exists(self):
        legacy = self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native)
        with self.assertRaises(ProjectAdmissionError):
            self.select(legacy.name)
        self.assertEqual(native, self.select(native.name).control_root)
        self.assertEqual(native, self.select().control_root)

    def test_invalid_native_does_not_fall_back_to_legacy(self):
        self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native, component="bad")
        for control in (native.name, None):
            with self.subTest(control=control), self.assertRaises(ProjectAdmissionError):
                self.select(control)

    def test_refuses_legacy_with_manifest_inside_old_spec_directory(self):
        control = self.legacy()
        path = self.manifest(control)
        (control / "SPEC").mkdir()
        path.rename(control / "SPEC" / path.name)
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_missing_and_symlink_control_roots_are_refused(self):
        with self.assertRaises(ProjectAdmissionError):
            self.select(".anechoic_anechoic")
        (self.root / ".anechoic_anechoic").symlink_to(self.root)
        with self.assertRaises(ProjectAdmissionError):
            self.select(".anechoic_anechoic")

    def test_project_settings_do_not_shadow_native_manifest(self):
        control = self.legacy()
        self.manifest(control)
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit):
                self.assertEqual(control, self.select(explicit).control_root)

    def test_reusable_admission_selects_current_pins_without_opening_workbench(self):
        alpha, beta = self.root / "alpha", self.root / "beta"
        first_manifest = self.manifest(alpha / ".anechoic_alpha", name="Alpha", prefix="AL", component="C00")
        self.manifest(beta / ".anechoic_beta", name="Beta", prefix="BE", component="C00",
                      parameters={"project_mcp": {"tool_blacklist": ["query_schema"],
                                                  "release_workflows_enabled": True}})
        with project_admission() as select:
            first = select(alpha)
            other = select(beta)
            self.assertEqual((alpha, beta), (first.root, other.root))
            self.assertNotEqual(first.instance_id, other.instance_id)
            self.assertEqual(("query_schema",), other.tool_blacklist)
            self.assertTrue(other.release_workflows_enabled)
            with self.assertRaises(ProjectAdmissionError):
                select(alpha, instance_id="0" * 64, host_root=alpha)
            first_manifest.write_text(first_manifest.read_text(encoding="utf-8").replace(
                "version: 1", "version: 2", 1), encoding="utf-8")
            revised = select(alpha)
            self.assertEqual("AL-S-001@2", revised.manifest_ref)
            self.assertNotEqual(first.manifest_sha256, revised.manifest_sha256)
            self.assertEqual(other, select(beta))
        for root in (alpha, beta):
            self.assertFalse((root / ".anechoic_runtime/db/project.duckdb").exists())

    def test_family_selection_is_accepted_by_native_gateway(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            select_runtime_project as family_select,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import native_project_gateway

        self.manifest(self.root / ".anechoic_anechoic")
        selected = family_select(self.root)
        gateway = native_project_gateway(self.root, selection=selected)
        self.assertIs(gateway.selection, selected)
        self.assertIsInstance(selected, ProjectBinding)

    def test_default_model_validates_native_selection(self):
        self.manifest(self.root / ".anechoic_anechoic", component="C00")
        selection = select_runtime_project(self.root)
        self.assertEqual("AN-S-001@1", selection.manifest_ref)

    def test_malformed_manifest_does_not_select_legacy_in_same_control(self):
        control = self.legacy()
        self.manifest(control).write_text("---\n[invalid", encoding="utf-8")
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit), self.assertRaises(ProjectAdmissionError):
                self.select(explicit)

    def test_discovery_rejects_excessive_control_roots(self):
        for index in range(65):
            (self.root / f".anechoic_candidate{index}").mkdir()
        with self.assertRaisesRegex(ProjectAdmissionError, "ceiling"):
            self.select()

    def test_visible_control_is_discovered_and_ambiguous_with_hidden_control(self):
        visible = self.root / "_anechoic_anechoic"
        self.manifest(visible)
        self.assertEqual(visible, self.select().control_root)
        self.assertEqual(visible, self.select(visible.name).control_root)
        self.manifest(self.root / ".anechoic_anechoic")
        with self.assertRaisesRegex(ProjectAdmissionError, "unique native Project Manifest"):
            self.select()

    def test_visible_symlink_candidate_is_refused(self):
        (self.root / "_anechoic_anechoic").symlink_to(self.root)
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_staging_is_never_discovered_implicitly(self):
        self.manifest(self.root / ".anechoic_new")
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_refuses_two_native_manifests_and_ignores_retained_legacy(self):
        self.manifest(self.root / ".anechoic_anechoic")
        self.manifest(self.root / ".anechoic_other", name="Other", prefix="OT")
        with self.assertRaisesRegex(ProjectAdmissionError, "unique native Project Manifest"):
            self.select()
        (self.root / ".anechoic_other" / "OT-S-001-PROJECT_MANIFEST--declare.md").unlink()
        self.legacy(".anechoic_legacy", declared=".anechoic_unknown")
        self.assertEqual(self.root / ".anechoic_anechoic", self.select().control_root)


class DirectSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / "_anechoic_anechoic"
        self.manifest = write_manifest(self, self.control)

    def test_direct_manifest_repair_rotates_once_after_transport_and_lifecycle_drain(self):
        previous = self.manifest.read_text()
        probe = DirectSupervisorProbe(self.manifest, repair=lambda: self.manifest.write_text(previous + "\n"),
                                      invalid=True, lifecycle=(0, True, False))
        status, stderr = probe.run(self.root, "beta_next")
        self.assertEqual(0, status)
        self.assertEqual(1, stderr.count("Manifest reload refused"))
        original = (("start", "owner"), ("start", "api"), ("start", "mcp"))
        self.assertEqual([original, original], probe.refusals)
        self.assertEqual(2, len(probe.launched["owner"]))
        self.assertEqual([("stop", "api", None), ("stop", "mcp", None), ("lifecycle",), ("lifecycle",),
                          ("lifecycle",), ("stop", "owner", None), ("start", "owner")], probe.events[3:10])
        [first, repaired] = [runtime_flags(command) for command, _ in probe.launched["owner"]]
        self.assertEqual(first["--instance-id"], repaired["--instance-id"])
        self.assertNotEqual(first["--manifest-sha256"], repaired["--manifest-sha256"])
        self.assertEqual(sha256(self.manifest.read_bytes()).hexdigest(), repaired["--manifest-sha256"])
        binding = json.loads(probe.launched["api"][-1][1]["ANECHOIC_BETA_DIRECT_MANIFEST"])
        info = self.manifest.stat()
        self.assertEqual([info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns],
                         binding["version"])
        self.assertEqual([False, False], probe.ready_gates)

    def test_direct_manifest_reloads_validated_semantic_settings(self):
        parameters = {"runtime": {"workbench": {"storage": "memory", "import_graph": False}}}
        probe = DirectSupervisorProbe(self.manifest, repair=lambda: write_manifest(self, self.control, parameters=parameters))
        self.assertEqual(0, probe.run(self.root, "beta_next")[0])
        for role in ("owner", "api"):
            [(old, _), (new, _)] = probe.launched[role]
            before, after = runtime_flags(old), runtime_flags(new)
            self.assertEqual(before["--instance-id"], after["--instance-id"])
            self.assertNotEqual(before["--manifest-sha256"], after["--manifest-sha256"])
            self.assertEqual(("disk", "memory"), (before["--workbench-storage"], after["--workbench-storage"]))
            self.assertIn("--watch-code", old)
            self.assertNotIn("--watch-code", new)

    def test_beta_next_supervisor_selects_owner_and_api_modules(self):
        probe = DirectSupervisorProbe(self.manifest)
        self.assertEqual(0, probe.run(self.root, "beta_next")[0])
        (owner, _), = probe.launched["owner"]
        (api, env), = probe.launched["api"]
        selected = select_runtime_project(self.root)
        socket = runtime_flags(api)["--socket"]
        args = ["--socket", socket, "--project-root", str(self.root), "--control-root", self.control.name,
                "--instance-id", selected.instance_id, "--manifest-sha256", selected.manifest_sha256,
                "--manifest-path", self.manifest.relative_to(self.root).as_posix(), "--project-prefix", "AN",
                "--project-name", "Anechoic", "--workbench-storage", "disk", "--journal-storage", "files",
                "--watch-code"]
        prefix = [sys.executable, "-B", "-P", "-m"]
        self.assertEqual([*prefix, "ORCHESTRATOR_beta_C68.project_peer_owner", *args], owner)
        self.assertEqual([*prefix, "API_MIXER_beta_C91.API_MIXER_beta_C91__shared", *args, "--role", "api"], api)
        self.assertEqual("beta_next", env["ANECHOIC_RUNTIME_STACK"])


class DirectManifestTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_transport_releases_drain_lock_after_accepted_response_completes(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        write_manifest(self, root / "_anechoic_anechoic")
        gate = root / "api.draining"
        lock = gate.with_suffix(".transport")
        lock.touch()
        admitted, finish = asyncio.Event(), asyncio.Event()

        async def body():
            admitted.set()
            await finish.wait()
            yield b"lifecycle result"

        async def accepted(_request):
            return StreamingResponse(body())

        env = {"ANECHOIC_RUNTIME_STACK": "beta_next", "ANECHOIC_BETA_BACKEND_SOCKET": str(root / "api.sock"),
               "ANECHOIC_BETA_DIRECT_TRANSPORT_GATE": str(gate), "ANECHOIC_BETA_DIRECT_DIAGNOSTICS": "0"}
        runtime_stack.cache_clear()
        self.addCleanup(runtime_stack.cache_clear)
        with patch.dict(os.environ, env), patch("uvicorn.run") as run:
            self.assertIsNone(await asyncio.to_thread(http_main, ["--project-root", str(root)]))
        app = run.call_args.args[0]
        app.starlette_app.router.routes.insert(0, Route(MCP_PATH, accepted, methods=["POST"]))
        transport = httpx2.ASGITransport(app=app)
        client = await self.enterAsyncContext(httpx2.AsyncClient(transport=transport, base_url="http://localhost"))
        request = asyncio.create_task(client.post(MCP_PATH))
        try:
            await asyncio.wait_for(admitted.wait(), 5)
            gate.write_text("project_manifest_invalid")
            blocked = await client.post(MCP_PATH)
            self.assertEqual((409, "project_manifest_invalid"), (blocked.status_code, blocked.json()["error"]))
            with lock.open("rb") as waiter, self.assertRaises(BlockingIOError):
                flock(waiter, LOCK_EX | LOCK_NB)
        finally:
            finish.set()
            completed = await asyncio.wait_for(request, 5)
        self.assertEqual((200, "lifecycle result"), (completed.status_code, completed.text))
        with lock.open("rb") as waiter:
            flock(waiter, LOCK_EX | LOCK_NB)


if __name__ == "__main__":
    unittest.main()
