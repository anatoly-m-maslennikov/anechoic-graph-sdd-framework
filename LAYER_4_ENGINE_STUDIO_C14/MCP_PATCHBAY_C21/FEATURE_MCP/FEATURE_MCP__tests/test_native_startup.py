"""Normal startup selects one validated Project across the migration rename."""
from .native_query_test_support import local_gateway


import asyncio
from contextlib import redirect_stderr
from fcntl import LOCK_EX, LOCK_NB, flock
from io import StringIO
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock, patch

import httpx2
import yaml

from MCP_PATCHBAY_C21.FEATURE_MCP.docker import shared_supervisor as supervisor
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import _guard_direct_transport
MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    ProjectAdmissionError, ProjectBinding, project_admission, select_runtime_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations


def native_fixture_gateway(root, cache, *, selection=None):
    from dataclasses import asdict, replace
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import NativeProjectSelection
    from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import startup_selection
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

    def manifest(self, control, *, name="Anechoic", prefix="AN", component="C00", parameters=None):
        path = control / f"{prefix}-S-001-PROJECT_MANIFEST--declare.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": f"{prefix}-S-001"},
                  "context": {"container": {"component": component}, "tier": -1,
                              "template": "project_manifest"},
                  "state": {"status": "active", "version": 1}}
        runtime = f", parameters={parameters!r}" if parameters is not None else ""
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n## Claim\n\n### Formal Claim\n\n```python\n"
                        "from anechoic.formal_claims import declare_entity\n"
                        "from anechoic.model import ProjectManifest\n"
                        f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, "
                        f"prefix={prefix!r}{runtime}))\n```\n", encoding="utf-8")
        return path

    def select(self, control=None):
        return self.admit(self.root, control)

    def test_direct_manifest_repair_rotates_once_after_transport_and_lifecycle_drain(self):
        control = self.root / ".anechoic_anechoic"
        manifest = self.manifest(control)
        directory = self.root / "sockets"
        directory.mkdir()
        arguments = lambda selection, _socket: ([selection.manifest_sha256], [selection.project_name])
        reload = supervisor.ManifestReload(self.select, arguments, directory)
        owner, backend = reload.children({})
        calls = Mock()
        owner.stop, owner.ensure, backend.stop = calls.owner_stop, calls.owner_start, calls.backend_stop
        mcp = Mock(stop=calls.mcp_stop)
        initial = reload.selection
        original = manifest.read_text()
        stopping = Event()
        self.assertTrue(reload.refresh(owner, backend, mcp, stopping))
        manifest.write_text("Invalid Manifest")
        failure = StringIO()
        with redirect_stderr(failure):
            self.assertFalse(reload.refresh(owner, backend, mcp, stopping))
            self.assertFalse(reload.refresh(owner, backend, mcp, stopping))
        self.assertEqual(1, failure.getvalue().count("Manifest reload refused"))
        self.assertEqual("project_manifest_invalid", reload.gate.read_text())
        self.assertEqual([], calls.mock_calls)
        manifest.write_text(original + "\n")
        calls.idle.side_effect = [False, False, True]
        with patch.object(supervisor, "_lifecycle_idle", calls.idle), patch.object(supervisor, "sleep"):
            self.assertTrue(reload.refresh(owner, backend, mcp, stopping))
            self.assertTrue(reload.refresh(owner, backend, mcp, stopping))
        self.assertEqual(["backend_stop", "mcp_stop", "idle", "idle", "idle", "owner_stop", "owner_start"],
                         [call[0] for call in calls.mock_calls])
        calls.backend_stop.assert_called_once_with(graceful=True)
        calls.mcp_stop.assert_called_once_with(graceful=True)
        calls.owner_stop.assert_called_once_with(graceful=True)
        self.assertEqual(initial.instance_id, reload.selection.instance_id)
        self.assertNotEqual(initial.manifest_sha256, reload.selection.manifest_sha256)
        self.assertEqual([reload.selection.manifest_sha256], owner.command)
        self.assertEqual(list(reload.version),
                         json.loads(backend.environment["ANECHOIC_BETA_DIRECT_MANIFEST"])["version"])
        self.assertFalse(reload.gate.exists())

    def test_direct_manifest_reloads_validated_semantic_settings(self):
        control = self.root / ".anechoic_anechoic"
        self.manifest(control)
        directory = self.root / "sockets"
        directory.mkdir()
        reload = supervisor.ManifestReload(self.select, supervisor._direct_arguments, directory)
        owner, backend = reload.children({})
        mcp = Mock()
        old = reload.selection
        for child in (owner, backend):
            self.assertEqual("disk", child.command[child.command.index("--workbench-storage") + 1])
        parameters = {"runtime": {"workbench": {"storage": "memory", "import_graph": False}}}
        self.manifest(control, parameters=parameters)
        with patch.object(owner, "ensure") as restart:
            self.assertTrue(reload.refresh(owner, backend, mcp, Event()))
            restart.assert_called_once()
        self.assertEqual(old.instance_id, reload.selection.instance_id)
        self.assertNotEqual(old.manifest_sha256, reload.selection.manifest_sha256)
        for child in (owner, backend):
            self.assertEqual("memory", child.command[child.command.index("--workbench-storage") + 1])
            self.assertNotIn("--watch-code", child.command)

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
        from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import native_project_gateway

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


class DirectManifestTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_transport_releases_drain_lock_after_accepted_response_completes(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        gate = root / "api.draining"
        lock = gate.with_suffix(".transport")
        lock.touch()
        admitted, finish = asyncio.Event(), asyncio.Event()

        async def app(_scope, _receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            admitted.set()
            await finish.wait()
            await send({"type": "http.response.body", "body": b"lifecycle result"})

        transport = httpx2.ASGITransport(app=_guard_direct_transport(app, gate))
        client = await self.enterAsyncContext(httpx2.AsyncClient(transport=transport, base_url="http://localhost"))
        request = asyncio.create_task(client.post("/mcp"))
        try:
            await asyncio.wait_for(admitted.wait(), 5)
            gate.write_text("project_manifest_invalid")
            blocked = await client.post("/mcp")
            self.assertEqual((503, "project_manifest_invalid"), (blocked.status_code, blocked.json()["error"]))
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
