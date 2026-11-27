"""Bounded process output and known credential-store image negatives."""


from __future__ import annotations

import json
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import NonCallableMock
from unittest.mock import MagicMock, patch


APP = Path(__file__).resolve().parents[1]
import MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared as images  # noqa: E402
import MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared as image_inputs  # noqa: E402


IMAGE_ID = "sha256:" + "a" * 64




class LifecycleImageAssetsTests(unittest.TestCase):
    def assert_source_layer_identity(self, root, manager, before):
        delivery = root / "LAYER_2_META_METHODOLOGY_C58/AN-S-1-source.md"
        delivery.write_text("changed")
        changed = manager.identity(use_packaged_assets=True)
        self.assertNotEqual(before.fingerprint, changed.fingerprint)
        self.assertIn(
            delivery.relative_to(root).as_posix(),
            {entry.path for entry in changed.manifest},
        )
        delivery.write_text("source")
        delivery.unlink()
        delivery.symlink_to(root / "version.toml")
        with self.assertRaises(images.ImageError):
            manager.identity(use_packaged_assets=True)
        delivery.unlink()
        delivery.write_text("source")

    def test_stack_selector_controls_current_source_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for relative in (*image_inputs._REQUIRED, images.TOOL_REGISTRY):
                source = root / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("{}")
            (root / "version.toml").write_text('[framework]\nversion = "0.1.0"\n')
            for layer in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58"):
                path = root / layer / "AN-S-1-source.md"
                path.parent.mkdir(parents=True)
                path.write_text("source")
            docker = MagicMock(side_effect=AssertionError("unexpected Docker command"))
            manager = images.ImageManager(root, project_root=root, executor=docker)
            before = manager.identity(use_packaged_assets=True)
            self.assert_source_layer_identity(root, manager, before)
            component = root / image_inputs.ENGINE_ROOT / "KERNEL_beta_C67"
            component.mkdir()
            (component / "module.py").write_text("pass\n")
            self.assertEqual(before, manager.identity(use_packaged_assets=True))
            selector = root / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
            selector.parent.mkdir(parents=True)
            selector.write_text('stack = "current"\n')
            selected = manager.identity(use_packaged_assets=True)
            self.assertNotEqual(before.fingerprint, selected.fingerprint)
            self.assertIn(
                "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml",
                {entry.path for entry in selected.manifest},
            )
            context = root / "context"
            context.mkdir()
            manager._assemble(context, selected)
            self.assertEqual(
                {entry.path for entry in selected.manifest},
                {
                    path.relative_to(context).as_posix()
                    for path in context.rglob("*")
                    if path.is_file()
                },
            )
            for invalid_selector in (
                'stack = "beta"\n',
                'stack = "beta_next"\n',
                'stack = "current"\nextra = true\n',
            ):
                with self.subTest(selector=invalid_selector):
                    selector.write_text(invalid_selector)
                    with self.assertRaisesRegex(images.ImageError, "must specify"):
                        manager.resolve()
            docker.assert_not_called()

    def test_registry_generator_stages_backend_assets_without_touching_source(
        self,
    ):
        backend = "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND"
        self.assertEqual(
            f"{backend}/generate_tool_registry.py",
            images.TOOL_REGISTRY_COMPILER,
        )
        self.assertEqual(
            f"{backend}/tool_providers.json", images.TOOL_PROVIDERS
        )
        self.assertEqual(f"{backend}/tool_registry.json", images.TOOL_REGISTRY)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for component in (
                "FEATURE_PROGRAMMATIC",
                "ARCHITECTURE_ANALYSIS_C73",
                "MCP_PATCHBAY_C21",
                "IWE_CONSOLE_C43",
            ):
                (root / "LAYER_4_ENGINE_STUDIO_C14" / component).mkdir(
                    parents=True
                )
            feature = root / backend
            feature.mkdir(parents=True)
            (feature / "tool_providers.json").write_text('{"fixture": true}')
            (feature / "generate_tool_registry.py").write_text(
                "from pathlib import Path\n"
                "import sys\n"
                'root = Path(sys.argv[sys.argv.index("--package-root") + 1])\n'
                f'feature = root / "{backend}"\n'
                'assert (feature / "tool_providers.json").is_file()\n'
                '(feature / "tool_registry.json").write_text("{}")\n'
            )
            self.assertEqual(
                b"{}",
                images.compile_tool_registry(root, timeout=5, max_output=100),
            )
            self.assertFalse((feature / "tool_registry.json").exists())

    def test_predecessor_pins_selected_ready_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            project_id = "c" * 64
            state = root / ".anechoic_runtime/runtime/project_mcp" / project_id
            state.mkdir(parents=True)
            control = root / ".anechoic_project"
            selection = NonCallableMock(
                spec_set=['root', 'control_root', 'instance_id', 'launcher_state'],
                root=root, control_root=control, instance_id=project_id, launcher_state=state)
            receipt = {"project_root": str(root), "control_root": str(control), "project_id": project_id,
                       "image_id": IMAGE_ID, "readiness": True}
            path = state / "ready.json"
            path.write_text(json.dumps(receipt))
            with patch("MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared.select_runtime_project", return_value=selection):
                manager = images.ImageManager(root, project_root=root)
                self.assertEqual(IMAGE_ID, manager._build_predecessor())
                path.write_text("{}")
                self.assertEqual(IMAGE_ID, manager._build_predecessor())
                with self.assertRaises(images.ImageError):
                    images.ImageManager(root, project_root=root)._build_predecessor()

    def test_unrelated_or_unsafe_receipt_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            project_id = "d" * 64
            state = root / ".anechoic_runtime/runtime/project_mcp" / project_id
            state.mkdir(parents=True)
            control = root / ".anechoic_project"
            selection = NonCallableMock(
                spec_set=['root', 'control_root', 'instance_id', 'launcher_state'],
                root=root, control_root=control, instance_id=project_id, launcher_state=state)
            path = state / "ready.json"
            receipt = {"project_root": str(root), "control_root": str(control), "project_id": "e" * 64,
                       "image_id": IMAGE_ID, "readiness": True}
            with patch("MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared.select_runtime_project", return_value=selection):
                path.write_text(json.dumps(receipt))
                with self.assertRaises(images.ImageError):
                    images.ImageManager(root, project_root=root)._build_predecessor()
                path.unlink()
                path.symlink_to(root / "missing")
                with self.assertRaises(images.ImageError):
                    images.ImageManager(root, project_root=root)._build_predecessor()
                path.unlink()
                path.write_bytes(b"x" * 65537)
                with self.assertRaises(images.ImageError):
                    images.ImageManager(root, project_root=root)._build_predecessor()

    def test_receipt_read_rejects_symlinked_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            actual = root / "actual"
            actual.mkdir()
            (actual / "ready.json").write_text("{}")
            link = root / "linked"
            link.symlink_to(actual, target_is_directory=True)
            selection = SimpleNamespace(launcher_state=link)
            with self.assertRaises(subprocess.CalledProcessError):
                image_inputs.ready_predecessor(selection)

    def test_first_build_without_state_does_not_resolve_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            resolver = MagicMock(side_effect=AssertionError("unexpected Project read"))
            with patch.dict(sys.modules, {"project_selection": SimpleNamespace(resolve_project=resolver)}):
                manager = images.ImageManager(root, project_root=root)
                self.assertIsNone(manager._build_predecessor())
                self.assertIsNone(manager._build_predecessor())
                resolver.assert_not_called()

    def test_refresh_uses_explicit_predecessor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selector = (
                root / image_inputs.DOCKER_ROOT / "native_model_refresh.py"
            )
            selector.parent.mkdir(parents=True)
            selector.touch()
            manager = images.ImageManager(
                root, project_root=root, previous_image=IMAGE_ID
            )
            process = MagicMock(returncode=0)
            process.communicate.return_value = ("b" * 64 + "\n", None)
            with patch.object(
                images.subprocess, "Popen", return_value=process
            ) as run:
                self.assertEqual("b" * 64, manager._refresh_model(root))
                self.assertEqual(IMAGE_ID, run.call_args.args[0][-1])
                self.assertTrue(run.call_args.kwargs["start_new_session"])
            with self.assertRaises(images.ImageError):
                images.ImageManager(
                    root, project_root=root, previous_image="mutable:tag"
                )

    def test_refresh_timeout_kills_process_group(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selector = (
                root / image_inputs.DOCKER_ROOT / "native_model_refresh.py"
            )
            selector.parent.mkdir(parents=True)
            selector.touch()
            manager = images.ImageManager(root, project_root=root)
            process = MagicMock(pid=123, returncode=-9)
            process.communicate.side_effect = [
                subprocess.TimeoutExpired("refresh", 1),
                ("", None),
            ]
            with (
                patch.object(images.subprocess, "Popen", return_value=process),
                patch.object(images.os, "killpg") as kill,
            ):
                with self.assertRaises(subprocess.TimeoutExpired):
                    manager._refresh_model(root)
                kill.assert_called_once_with(123, signal.SIGKILL)
                self.assertEqual(2, process.communicate.call_count)
