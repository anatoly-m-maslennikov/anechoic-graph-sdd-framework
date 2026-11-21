"""The concrete Local release flow, without running Docker or installing packages."""

# CA-E-573@19

from __future__ import annotations

import subprocess
import io
import json
import os
import shutil
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "RELEASE_VERSION"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"))
import local_release  # noqa: E402
from local_release import run_local_release, _launcher_image  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project  # noqa: E402
from release_support import _GENERATED_ASSETS, _file_identity, _publish_image_assets  # noqa: E402
from release_registry_test_fixture import write_tool_registry_generator  # noqa: E402


class SimpleLocalReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.control = self.root / ".anechoic_anechoic"
        self.control.mkdir()
        ontology = self.control / "LAYER_1_META_ONTOLOGY_C9"
        ontology.mkdir()
        self.native_sources = (
            ontology / "AN-S-10-SPEC--model.md",
            ontology / "AN-S-11-SPEC--related-spec.md",
        )
        for path in self.native_sources:
            path.write_text("## Claim\nNative source\n", encoding="utf-8")
        (self.root / ".gitignore").write_text(".anechoic_tmp/\n", encoding="utf-8")
        self.product = self.root / "LAYER_1_FRAMEWORK_METHODOLOGY"
        self.installed = self.control / "000_ANECHOIC_framework"
        self.runtime = self.root / ".anechoic_runtime"
        delivery = self.root / "LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE"
        delivery.mkdir(parents=True)
        (delivery / "public_release.py").write_text("# release source\n", encoding="utf-8")
        (delivery / "PUBLIC_RELEASE__tests").mkdir()
        (delivery / "PUBLIC_RELEASE__tests/test_private.py").write_text("# excluded test\n", encoding="utf-8")
        for destination in (self.product, self.installed, self.runtime):
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("obsolete", encoding="utf-8")
            (destination / "config.toml").write_text("keep = true\n", encoding="utf-8")
        skill = self.root / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("ane skill", encoding="utf-8")
        (skill / "references").mkdir()
        (skill / "references/details.md").write_text("skill reference", encoding="utf-8")
        (self.root / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
        (self.root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        (self.root / "version.toml").write_text('[framework]\nversion = "0.4.1"\n', encoding="utf-8")
        tools = self.root / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
        tools.mkdir(parents=True)
        bootstrap_helper = (
            Path(__file__).resolve().parents[2]
            / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/project_mcp_bootstrap.py"
        )
        (tools / "project_mcp_bootstrap.py").write_bytes(bootstrap_helper.read_bytes())
        (tools / "project_mcp_bootstrap.py").chmod(0o644)
        (tools / "tests").mkdir()
        (tools / "tests/test_retired.py").write_text("# package-excluded test\n", encoding="utf-8")
        (tools / "fixtures").mkdir()
        (tools / "fixtures/input.json").write_text("{}\n", encoding="utf-8")
        (tools / "README.md").write_text("package-excluded prose\n", encoding="utf-8")
        (tools / "scope_declaration_test_support.py").write_text("# package-excluded test helper\n", encoding="utf-8")
        (tools / "scope_declaration_render.py").write_text("# package-excluded test renderer\n", encoding="utf-8")
        skill = tools / "retained/SKILL.md"
        skill.parent.mkdir()
        skill.write_text("retained implementation skill\n", encoding="utf-8")
        subject_builder = tools / "GENERATE_ENTITY_GRAPH/render_entity_tree.py"
        subject_builder.parent.mkdir()
        subject_builder.write_text("# retained subject builder\n", encoding="utf-8")
        prompt = self.root / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/retired.py"
        prompt.parent.mkdir(parents=True)
        prompt.write_text("# source-only prompt\n", encoding="utf-8")
        self.engine_bootstrap = (
            self.root / "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/"
            "docker/start_mcp.py"
        )
        self.engine_bootstrap.parent.mkdir(parents=True)
        self.engine_bootstrap.write_bytes(b"#!/usr/bin/env python3\n# package bootstrap fixture\n")
        self.engine_bootstrap.chmod(0o755)
        (self.engine_bootstrap.parent / "runtime.py").write_text("# runtime entrypoint fixture\n", encoding="utf-8")
        mcp = self.engine_bootstrap.parent.parent
        (mcp / "tool_providers.json").write_text(
            '{"mcp_blacklist":[],"providers":[]}\n', encoding="utf-8")
        write_tool_registry_generator(mcp)
        self.image_id = "sha256:" + "a" * 64
        self.image = SimpleNamespace(resolve=Mock(return_value=self.image_id),
                                     identity=Mock(return_value=SimpleNamespace(fingerprint="b" * 64)))
        original_launcher_image = local_release._launcher_image

        def scoped_launcher_image(selection):
            observed = original_launcher_image(selection)
            if observed is not None:
                return observed
            package = self.runtime / "simple_local_release/package"
            return self.image_id if package.is_dir() else None

        launcher = patch("local_release._launcher_image", side_effect=scoped_launcher_image)
        launcher.start()
        self.addCleanup(launcher.stop)
        image_factory = patch("local_release._image_manager", return_value=self.image)
        self.image_factory = image_factory.start()
        self.addCleanup(image_factory.stop)
        canary = patch("local_release.verify_candidate_image", return_value="http://127.0.0.1:49152/anechoic/mcp")
        self.canary = canary.start()
        self.addCleanup(canary.stop)
        provenance = patch("local_release.release_image_provenance", return_value={
            "project_id": "c" * 64, "project_root": str(self.root),
            "control_root": ".anechoic_anechoic", "project_name": "Fixture",
            "head_commit": "d" * 40,
        })
        self.provenance = provenance.start()
        self.addCleanup(provenance.stop)

        self._native_project()
        self.enterContext(patch("release_support._native_release_sources", side_effect=lambda _selection: self._native_sources()))

    def _runner(self):
        calls = []

        def run(argv, cwd):
            self.assertEqual(self.root, cwd)
            calls.append(argv)
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, 1, "", "")
            if self._is_mcp_bootstrap(argv):
                return self._mcp_bootstrap_success(argv)
            return subprocess.CompletedProcess(argv, 0, "", "")

        return run, calls

    def _is_mcp_bootstrap(self, argv: tuple[str, ...]) -> bool:
        return (
            len(argv) > 1
            and argv[0] == sys.executable
            and argv[1] == str(self.runtime / "start_mcp.py")
        )

    def _mcp_bootstrap_success(self, argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        launcher_python = self.runtime / "launcher-venv/bin/python"
        launcher_python.parent.mkdir(parents=True, exist_ok=True)
        launcher_python.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        launcher_python.chmod(0o755)
        return subprocess.CompletedProcess(argv, 0, "http://localhost:12345/mcp\n", "")

    def _native_project(self):
        manifest = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
        manifest.parent.mkdir(exist_ok=True)
        manifest.write_text(
            "---\nidentity:\n  atom_id: AN-S-001\ncontext:\n  container:\n    component: C00\n"
            "  tier: -1\n  template: project_manifest\nstate:\n  status: active\n  version: 1\n---\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            "declare_entity(entity_name='Project Manifest', "
            "instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n", encoding="utf-8",
        )

        for relative in _GENERATED_ASSETS:
            (self.root / relative).write_text('{"sealed": true}\n', encoding="utf-8")
        self.native_assets = self.enterContext(patch("release_support.verify_native_release_assets"))

    def _native_sources(self):
        return {source.relative_to(self.control): source for source in self.native_sources if source.is_file()}

    def test_native_release_runs_full_gates_and_copies_selected_sources(self):
        runner, calls = self._runner()
        with patch("release_support._native_release_sources", return_value=self._native_sources(), create=True) as select, \
             patch("local_release._build_predecessor", return_value=None), \
             patch("local_release._launcher_image", side_effect=[None, self.image_id]):
            result = run_local_release(self.root, run_id="native-release", runner=runner)
        self.native_assets.assert_called_once()
        self.assertEqual("completed", result["outcome"], result)
        self.assertTrue(all(call.args[0].manifest_ref == "AN-S-001@1" for call in select.call_args_list))
        test_argv = next(call for call in calls if any(arg.endswith("run_full_test_suite.py") for arg in call))
        self.assertEqual(("--image-mode", "existing"), test_argv[-2:])
        self.assertEqual("refresh", result["image_mode"])
        self.assertTrue(any(self._is_mcp_bootstrap(call) for call in calls))
        product_sources = self.product / "SUPERLAYER_1_METHODOLOGY_SOURCES"
        for relative, source in self._native_sources().items():
            self.assertEqual(source.read_bytes(), (product_sources / relative).read_bytes())

    def test_native_manifest_change_stops_before_product_replacement(self):
        runner, _ = self._runner()

        def change_manifest(argv, cwd):
            if argv[0] == "uv":
                path = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
                path.write_text(path.read_text() + "\nchanged\n", encoding="utf-8")
            return runner(argv, cwd)

        with patch("release_support._native_release_sources", return_value=self._native_sources(), create=True), \
             patch("local_release._build_predecessor", return_value=None), \
             patch("local_release._launcher_image", return_value=None):
            result = run_local_release(self.root, run_id="native-changed", runner=change_manifest)
        self.assertEqual(("failed", "validate_project_selection"), (result["outcome"], result["failed_step"]))
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())

    def test_native_existing_mode_keeps_the_full_test_gate(self):
        runner, calls = self._runner()
        with patch("release_support._native_release_sources", return_value=self._native_sources(), create=True), \
             patch("local_release._build_predecessor", return_value=None), \
             patch("local_release._launcher_image", side_effect=[None, self.image_id]):
            result = run_local_release(self.root, run_id="native-existing", runner=runner, image_mode="existing")
        self.native_assets.assert_called_once()
        self.assertEqual("completed", result["outcome"], result)
        test_argv = next(call for call in calls if any(arg.endswith("run_full_test_suite.py") for arg in call))
        self.assertEqual(("--image-mode", "existing"), test_argv[-2:])

    def test_native_source_change_stops_before_product_replacement(self):
        runner, _ = self._runner()
        original_copy = shutil.copy2
        changed = next(iter(self._native_sources().values()))

        def mutate_after_copy(source, destination, *args, **kwargs):
            result = original_copy(source, destination, *args, **kwargs)
            if source == changed:
                changed.write_text("changed", encoding="utf-8")
            return result

        with patch("release_support._native_release_sources", return_value=self._native_sources(), create=True), \
             patch("local_release._build_predecessor", return_value=None), \
             patch("local_release._launcher_image", return_value=None), \
             patch("local_release.shutil.copy2", side_effect=mutate_after_copy):
            result = run_local_release(self.root, run_id="native-source-change", runner=runner)
        self.assertEqual(("failed", "copy_active_sources"), (result["outcome"], result["failed_step"]))
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())
        self.assertIn('version = "0.4.1"', (self.root / "version.toml").read_text())

    def test_existing_image_mode_preserves_checkout_assets_without_a_predecessor(self):
        selection = select_runtime_project(self.root)
        selection.launcher_state.mkdir(parents=True)
        (selection.launcher_state / "ready.json").write_text("invalid receipt", encoding="utf-8")
        payloads = {relative: json.dumps({"existing": relative}).encode() for relative in _GENERATED_ASSETS}
        for relative, payload in payloads.items():
            (self.root / relative).write_bytes(payload)

        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="existing-assets", runner=runner, image_mode="existing")

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("existing", result["image_mode"])
        test_argv = next(argv for argv in calls if any(arg.endswith("run_full_test_suite.py") for arg in argv))
        self.assertEqual(("--image-mode", "existing"), test_argv[-2:])
        self.assertEqual({"use_packaged_assets": True}, self.image.resolve.call_args_list[0].kwargs)
        runtime_package = self.runtime / "simple_local_release/package"
        for relative, payload in payloads.items():
            self.assertEqual(payload, (self.root / relative).read_bytes())
            self.assertEqual(payload, (runtime_package / relative).read_bytes())

    def test_failed_asset_publication_restores_checkout(self):
        relative, = _GENERATED_ASSETS
        target = self.root / relative
        target.write_bytes(b"known-good\n")
        previous = {relative: _file_identity(target)}
        package = self.root / ".anechoic_tmp/package"
        staged = package / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(b"replacement\n")
        expected = {relative: _file_identity(staged)}

        with patch("release_support.os.replace", side_effect=OSError("asset cannot be replaced")):
            with self.assertRaisesRegex(OSError, "asset cannot be replaced"):
                _publish_image_assets(self.root, package, previous, expected)
        self.assertEqual(previous[relative], _file_identity(target))

    def test_existing_image_mode_refuses_missing_assets_before_tests(self):
        runner, calls = self._runner()
        (self.root / next(iter(_GENERATED_ASSETS))).unlink()
        original_version = (self.root / "version.toml").read_bytes()
        result = run_local_release(self.root, run_id="missing-assets", runner=runner, image_mode="existing")
        self.assertEqual(("failed", "validate_inputs"), (result["outcome"], result["failed_step"]))
        self.assertEqual(original_version, (self.root / "version.toml").read_bytes())
        self.assertFalse(any(any(item.endswith("run_full_test_suite.py") for item in argv) for argv in calls))
        self.image_factory.assert_not_called()

    def test_launcher_image_reads_only_exact_selected_runtime_namespace(self):
        selection = select_runtime_project(self.root)
        old_image = "sha256:" + "c" * 64
        payload = {"project_root": str(self.root), "control_root": str(self.control),
                   "project_id": selection.instance_id, "image_id": old_image}
        legacy = self.root / ".anechoic_install/project_mcp" / selection.instance_id / "last_launch.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps(payload), encoding="utf-8")
        retained = legacy.read_bytes()
        sibling = selection.launcher_state.parent / ("d" * 64) / "last_launch.json"
        sibling.parent.mkdir(parents=True)
        sibling.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(_launcher_image(selection))
        current = selection.launcher_state / "last_launch.json"
        current.parent.mkdir(parents=True)
        current.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(old_image, _launcher_image(selection))
        payload["project_id"] = "d" * 64
        current.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(_launcher_image(selection))
        current.unlink()
        current.symlink_to(legacy)
        self.assertIsNone(_launcher_image(selection))
        self.assertEqual(retained, legacy.read_bytes())

    def test_focused_request_runs_and_reports_full_suite(self):
        modules = (
            "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_one.py",
            "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_two.py",
        )
        runner, calls = self._runner()
        result = run_local_release(
            self.root,
            run_id="focused-forwarding",
            runner=runner,
            test_modules=modules,
        )

        self.assertEqual("completed", result["outcome"])
        self.assertEqual("full", result["test_scope"])
        self.assertIsNone(result["test_modules"])
        test_command = next(argv for argv in calls if any(
            item.endswith("run_full_test_suite.py") for item in argv
        ))
        self.assertNotIn("--test-module", test_command)
        receipt = (self.root / result["receipt_path"]).read_text(encoding="utf-8")
        self.assertIn("Test scope: `full`", receipt)
        self.assertIn("Selected test modules: all discovered modules", receipt)

    def test_focused_test_failure_blocks_downstream_release(self):
        modules = ("LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_failing.py",)
        base_runner, calls = self._runner()

        def failed_tests(argv, cwd):
            result = base_runner(argv, cwd)
            if any(item.endswith("run_full_test_suite.py") for item in argv):
                return subprocess.CompletedProcess(
                    argv, 1, "focused tests ran\n", "focused test failure\n"
                )
            return result

        result = run_local_release(
            self.root,
            run_id="focused-failed",
            runner=failed_tests,
            test_modules=modules,
        )

        self.assertEqual(("failed", "tests"), (result["outcome"], result["failed_step"]))
        self.assertEqual("full", result["test_scope"])
        self.assertIsNone(result["test_modules"])
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))
        report = (self.root / result["report_path"]).read_text(encoding="utf-8")
        self.assertIn("Test scope: `full`", report)
        self.assertIn("Selected test modules: all discovered modules", report)
        self.assertIn("focused test failure", report)

    def _assert_input_refused(self, run_id):
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id=run_id, runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("validate_inputs", result["failed_step"])
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.assertFalse(any(any(item.endswith("run_full_test_suite.py") for item in argv) for argv in calls))
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))
        self.image_factory.assert_not_called()

    def test_unsafe_product_descendant_refuses_before_any_clear(self):
        (self.product / "linked.txt").symlink_to(self.installed / "old.txt")
        self._assert_input_refused("unsafe-product")

    def test_invalid_version_refuses_before_tests_or_replacement(self):
        version = self.root / "version.toml"
        version.write_text('[framework]\nversion = "invalid"\n')
        self._assert_input_refused("invalid-version")
        self.assertIn('version = "invalid"', version.read_text())

    def test_installer_refreshes_bootstrap_without_touching_runtime_config_or_state(self):
        runner, calls = self._runner()
        first = run_local_release(self.root, run_id="bootstrap-one", runner=runner)
        self.assertEqual("completed", first["outcome"])
        state = self.runtime / "project_mcp_state.json"
        state.write_text("retain this runtime state\n", encoding="utf-8")
        self.engine_bootstrap.write_bytes(b"#!/usr/bin/env python3\n# refreshed package bootstrap\n")
        self.engine_bootstrap.chmod(0o755)

        second = run_local_release(self.root, run_id="bootstrap-two", runner=runner)

        self.assertEqual("completed", second["outcome"])
        bootstrap = self.runtime / "start_mcp.py"
        self.assertEqual(self.engine_bootstrap.read_bytes(), bootstrap.read_bytes())
        self.assertEqual(0o755, stat.S_IMODE(bootstrap.stat().st_mode))
        self.assertEqual("keep = true\n", (self.runtime / "config.toml").read_text())
        self.assertEqual("retain this runtime state\n", state.read_text())
        self.assertEqual(2, sum(self._is_mcp_bootstrap(argv) for argv in calls))

    def test_four_component_local_version_increments_without_rollover(self):
        (self.root / "version.toml").write_text('[framework]\nversion = "0.4.1.9"\n', encoding="utf-8")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="version", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertIn('version = "0.4.1.10"', (self.root / "version.toml").read_text())

    def test_workbench_node_dependencies_are_not_packaged(self):
        frontend = self.root / "LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
        dependencies = frontend / "node_modules/.bin"
        dependencies.mkdir(parents=True)
        (frontend / "package.json").write_text('{"name":"workbench"}')
        (dependencies / "vite").symlink_to("../vite/bin/vite.js")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="frontend-dependencies", runner=runner)
        self.assertEqual("completed", result["outcome"])
        packaged = self.runtime / "simple_local_release/package" / frontend.relative_to(self.root)
        self.assertTrue((packaged / "package.json").is_file())
        self.assertFalse((packaged / "node_modules").exists())

    def test_preserved_ds_store_directories_do_not_block_replacement(self):
        kept, removed = (path.relative_to(self.control) for path in self.native_sources)
        self.native_sources[1].unlink()
        retained = (
            self.product / "SUPERLAYER_1_METHODOLOGY_SOURCES",
            self.product / "SUPERLAYER_1_METHODOLOGY_SOURCES" / kept.parent,
            self.installed / "obsolete",
            self.runtime / "simple_local_release/package/LAYER_3_ENGINE_STUDIO_C14",
        )
        for directory in retained:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / ".DS_Store").write_bytes(b"ignored")
            (directory / "obsolete.txt").write_text("old", encoding="utf-8")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="ds-store", runner=runner)
        self.assertEqual("completed", result["outcome"])
        for directory in retained:
            self.assertEqual(b"ignored", (directory / ".DS_Store").read_bytes())
            self.assertFalse((directory / "obsolete.txt").exists())
        self.assertTrue((self.product / "SUPERLAYER_1_METHODOLOGY_SOURCES" / kept).is_file())
        for target in (self.product, self.installed):
            self.assertFalse((target / "SUPERLAYER_1_METHODOLOGY_SOURCES" / removed).exists())

    def test_test_failure_leaves_both_methodology_destinations_untouched(self):
        calls = []
        stdout = "early stdout evidence\n" + "output tail\n" * 500
        stderr = "early failure traceback\n" + "error tail\n" * 500

        def runner(argv, cwd):
            calls.append(argv)
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, 1, "", "")
            if any(item.endswith("run_full_test_suite.py") for item in argv):
                self.assertIn("--all-groups", argv)
                self.assertIn("--managed-python", argv)
                self.assertIn("3.14", argv)
                self.assertEqual(str(self.root), argv[argv.index("--project-root") + 1])
                for target in (self.product, self.installed):
                    self.assertEqual("obsolete", (target / "old.txt").read_text())
            failed = any(item.endswith("run_full_test_suite.py") for item in argv)
            return subprocess.CompletedProcess(argv, 2 if failed else 0, stdout if failed else "", stderr if failed else "")

        with (
            patch("local_release.cleanup_stopped_containers") as stopped_cleanup,
            patch("local_release.cleanup_obsolete_images") as image_cleanup,
        ):
            result = run_local_release(self.root, run_id="tests-failed", runner=runner)
        self.assertEqual("tests", result["failed_step"])
        self.assertEqual("failed", result["outcome"])
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.assertEqual(1, sum(any(item.endswith("run_full_test_suite.py") for item in argv) for argv in calls))
        self.assertEqual(2, sum(argv[:2] == ("git", "commit") for argv in calls))
        report = (self.root / result["report_path"]).read_text()
        logs = list((self.root / ".anechoic_tmp/simple_local_release").glob("tests-failed-tests-*.log"))
        self.assertEqual(1, len(logs))
        self.assertIn(f"Complete test output: `{logs[0].relative_to(self.root).as_posix()}`", report)
        self.assertEqual(f"stdout:\n{stdout}\nstderr:\n{stderr}", logs[0].read_text())
        self.assertNotIn("early failure traceback", report)
        with patch("local_release.tempfile.NamedTemporaryFile", side_effect=OSError("unavailable")):
            unsaved = run_local_release(self.root, run_id="tests-log-unavailable", runner=runner)
        self.assertEqual(("failed", "tests"), (unsaved["outcome"], unsaved["failed_step"]))
        self.assertIn("Complete test output could not be saved (OSError)",
                      (self.root / unsaved["report_path"]).read_text())

    def test_default_tests_log_is_retained_on_interrupt_with_actual_failed_step(self):
        runner, calls = self._runner()

        def interrupted(argv, cwd, log):
            self.assertIn("-u", argv)
            self.assertEqual(self.root, cwd)
            log.write(b"partial test evidence\n")
            log.flush()
            raise KeyboardInterrupt

        output = io.StringIO()
        with patch("local_release.subprocess.run", side_effect=lambda argv, **kwargs: runner(argv, kwargs["cwd"])), \
                patch("local_release.run_logged_test_process", side_effect=interrupted), \
                patch("local_release.sys.stderr", output):
            result = run_local_release(self.root, run_id="interrupted")

        self.assertEqual(("failed", "tests", "KeyboardInterrupt"),
                         (result["outcome"], result["failed_step"], result["error_type"]))
        self.assertEqual("partial test evidence\n", (self.root / result["test_log_path"]).read_text())
        report = (self.root / result["report_path"]).read_text()
        self.assertIn("Stopped at: `tests`", report)
        self.assertIn("Error class: `KeyboardInterrupt`", report)
        self.assertIn(result["test_log_path"], report)
        self.assertIn("Local release phase START: tests", output.getvalue())
        self.assertIn(result["test_log_path"], output.getvalue())
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))

    def test_default_test_log_survives_later_failure_without_whole_output_capture(self):
        runner, _ = self._runner()

        def passed(argv, cwd, log):
            log.write(b"complete test evidence\n")
            return subprocess.CompletedProcess(argv, 0, "bounded tail", "")

        with patch("local_release.subprocess.run", side_effect=lambda argv, **kwargs: runner(argv, kwargs["cwd"])), \
                patch("local_release.run_logged_test_process", side_effect=passed), \
                patch("local_release._prepare_package", side_effect=RuntimeError("package failed")):
            result = run_local_release(self.root, run_id="later-failed")

        self.assertEqual(("failed", "build_package"), (result["outcome"], result["failed_step"]))
        self.assertEqual("complete test evidence\n", (self.root / result["test_log_path"]).read_text())
        self.assertIn(result["test_log_path"], (self.root / result["report_path"]).read_text())

    def test_interrupt_before_tests_reports_actual_git_step_without_claiming_log(self):
        def interrupted(argv, cwd):
            raise KeyboardInterrupt

        result = run_local_release(self.root, run_id="git-interrupted", runner=interrupted)
        self.assertEqual(("failed", "git_before_validate_inputs", "KeyboardInterrupt"),
                         (result["outcome"], result["failed_step"], result["error_type"]))
        self.assertIsNone(result["test_log_path"])
        self.assertIn("git_before_validate_inputs", (self.root / result["report_path"]).read_text())

    def test_git_stages_everything_and_commits_before_steps_and_at_end(self):
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="git-order", runner=runner)
        self.assertEqual("completed", result["outcome"])
        adds = [index for index, argv in enumerate(calls) if argv[:3] == ("git", "add", "-A")]
        commits = [index for index, argv in enumerate(calls) if argv[:2] == ("git", "commit")]
        self.assertGreaterEqual(len(commits), 7)
        self.assertEqual(len(adds), len(commits))
        for add, commit in zip(adds, commits):
            self.assertEqual(add + 2, commit)
        self.assertEqual(len(calls) - 2, commits[-1])
        self.assertEqual([
            "validate inputs", "tests", "copy active sources", "build package", "prepare candidate image",
            "copy product to installed framework", "install project runtime", "start mcp", "final",
        ], [calls[index][-1].removeprefix("chore(release): simple local ") for index in commits])

    def test_checkpoints_commit_actual_temporary_git_changes_including_final(self):
        def git(*args):
            return subprocess.run(("git", *args), cwd=self.root, capture_output=True, text=True, check=True)

        git("init", "--quiet")
        git("config", "user.name", "Release fixture")
        git("config", "user.email", "release-fixture@example.invalid")

        def runner(argv, cwd):
            self.assertEqual(self.root, cwd)
            if argv[0] == "git":
                return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
            if self._is_mcp_bootstrap(argv):
                return self._mcp_bootstrap_success(argv)
            if argv[0] == "docker":
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 0, "http://localhost:12345/mcp", "")

        result = run_local_release(self.root, run_id="real-git", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual("", git("status", "--porcelain").stdout)
        self.assertEqual("chore(release): simple local final", git("log", "-1", "--format=%s").stdout.strip())
        receipt = ".anechoic_runtime/simple_local_release/reports/real-git.md"
        self.assertIn("http://localhost:12345/mcp", git("show", f"HEAD:{receipt}").stdout)
        self.assertEqual(6, int(git("rev-list", "--count", "HEAD").stdout))
        for relative in _GENERATED_ASSETS:
            self.assertEqual((self.root / relative).read_text(), git("show", f"HEAD:{relative}").stdout)

    def test_package_inputs_fail_before_any_installed_replacement(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_text("prior payload", encoding="utf-8")
            (target / "old.txt").chmod(0o640)
        def inventory(target):
            return {path.relative_to(target).as_posix(): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
                    for path in target.rglob("*") if path.is_file()}
        before = {target: inventory(target) for target in (self.installed, runtime_package, skill)}
        for relative in ("uv.lock", "LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md",
                         "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/runtime.py"):
            with self.subTest(relative=relative):
                missing = self.root / relative
                payload = missing.read_bytes()
                mode = stat.S_IMODE(missing.stat().st_mode)
                missing.unlink()
                runner, calls = self._runner()
                result = run_local_release(self.root, run_id="missing-input", runner=runner)
                missing.write_bytes(payload)
                missing.chmod(mode)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual("build_package", result["failed_step"])
                self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))
                for target, snapshot in before.items():
                    self.assertEqual(snapshot, inventory(target))
                self.assertEqual([], list((self.root / ".anechoic_tmp/simple_local_release").iterdir()))

    def test_installed_copies_are_checked_for_corruption(self):
        copy_tree = local_release._copy_tree
        for destination, step in ((self.installed, "copy_product_to_installed_framework"),
                                  (self.root / ".agents/skills/ane", "install_project_runtime")):
            with self.subTest(destination=destination):
                def corrupt(source, target, **kwargs):
                    copy_tree(source, target, **kwargs)
                    if target == destination:
                        next(path for path in target.rglob("*") if path.is_file() and path.name != "config.toml").write_text("corrupt")
                runner, _ = self._runner()
                with patch.object(local_release, "_copy_tree", corrupt):
                    result = run_local_release(self.root, run_id="corrupt-copy", runner=runner)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual(step, result["failed_step"])

    def test_installation_lock_refuses_contention_before_replacement(self):
        runner, calls = self._runner()
        version = (self.root / "version.toml").read_bytes()
        product = {p.relative_to(self.product): p.read_bytes() for p in self.product.rglob("*") if p.is_file()}
        stderr = io.StringIO()
        with local_release._installation_lock(self.root, select_runtime_project(self.root)), patch("sys.stderr", stderr):
            result = run_local_release(self.root, run_id="locked-install", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("installation_lock", result["failed_step"])
        self.assertIn("local-release-installation-lock-busy", stderr.getvalue())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(version, (self.root / "version.toml").read_bytes())
        self.assertEqual(product, {p.relative_to(self.product): p.read_bytes() for p in self.product.rglob("*") if p.is_file()})
        self.assertFalse(any(argv[0] == "git" for argv in calls))
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))
        with local_release._installation_lock(self.root, select_runtime_project(self.root)):
            pass

    def test_installation_lock_covers_copy_and_mcp_handoff(self):
        runner, _ = self._runner()
        copy_tree = local_release._copy_tree
        checked = []
        def check_locked():
            with self.assertRaisesRegex(local_release.LocalReleaseError, "installation-lock-busy"):
                with local_release._installation_lock(self.root, select_runtime_project(self.root)):
                    pass
            checked.append(True)
        def copy(source, target, **kwargs):
            if target in (self.installed, self.runtime / "simple_local_release/package", self.root / ".agents/skills/ane"):
                check_locked()
            return copy_tree(source, target, **kwargs)
        def run(argv, cwd):
            if self._is_mcp_bootstrap(argv):
                check_locked()
            return runner(argv, cwd)
        with patch.object(local_release, "_copy_tree", copy):
            result = run_local_release(self.root, run_id="lock-coverage", runner=run)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(4, len(checked))

    def test_package_byte_or_mode_drift_refuses_before_installed_clear(self):
        import local_release
        prepare = local_release._prepare_package
        for field in ("bytes", "mode"):
            with self.subTest(field=field):
                def tamper(*args, **kwargs):
                    expected = prepare(*args, **kwargs)
                    path = args[2] / "uv.lock"
                    if field == "bytes":
                        path.write_bytes(path.read_bytes() + b"drift")
                    else:
                        path.chmod(0o600 if stat.S_IMODE(path.stat().st_mode) != 0o600 else 0o644)
                    return expected
                runner, _ = self._runner()
                with patch.object(local_release, "_prepare_package", tamper):
                    result = run_local_release(self.root, run_id="tampered-package", runner=runner)
                self.assertEqual("failed", result["outcome"])
                self.assertEqual("prepare_candidate_image", result["failed_step"])
                self.image_factory.assert_not_called()
                self.assertEqual("obsolete", (self.installed / "old.txt").read_text())

    def test_unverified_native_status_specifications_stop_package_build(self):
        self.native_assets.side_effect = local_release.LocalReleaseError("unverified native status Workflow")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="unverified-workflow", runner=runner)
        self.assertEqual(("failed", "build_package"), (result["outcome"], result["failed_step"]))
        self.image_factory.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())

    def test_unreadable_package_subtree_refuses_before_replacement(self):
        blocked = self.root / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/blocked"
        blocked.mkdir()
        (blocked / "required.py").write_bytes(b"required payload")
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_bytes(b"previous payload")
        runner, calls = self._runner()
        blocked.chmod(0)
        try:
            result = run_local_release(self.root, run_id="unreadable-package", runner=runner)
        finally:
            blocked.chmod(0o700)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("build_package", result["failed_step"])
        self.image_factory.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        for target in (runtime_package, skill):
            self.assertEqual(b"previous payload", (target / "old.txt").read_bytes())
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))

    def test_staging_is_run_private_and_verified_before_replacement(self):
        import local_release
        prepare = local_release._prepare_package
        stages = []
        def capture(root, product, package, **kwargs):
            self.assertTrue(package.is_relative_to(root / ".anechoic_tmp/simple_local_release"))
            self.assertTrue(package.parent.name.startswith("private-"))
            self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
            stages.append(package)
            return prepare(root, product, package, **kwargs)
        runner, _ = self._runner()
        with patch.object(local_release, "_prepare_package", capture):
            result = run_local_release(self.root, run_id="private", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(1, len(stages))
        self.assertFalse(stages[0].exists())
        self.assertFalse((self.root / ".anechoic_install").exists())

    def test_image_is_verified_before_replacement_and_installed_launch_cannot_build(self):
        events = []

        def resolve(**kwargs):
            if kwargs == {"use_packaged_assets": True}:
                events.append("candidate-resolve")
                self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
                self.assertFalse((self.runtime / "simple_local_release/package").exists())
                self.assertFalse((self.root / ".agents/skills/ane").exists())
            else:
                events.append("installed-resolve")
                self.assertEqual({"explicit_id": self.image_id, "build_if_missing": False}, kwargs)
            return self.image_id
        self.image.resolve.side_effect = resolve
        runner, calls = self._runner()

        def verify_canary(root, selection, package, staging, image, *, run_id):
            events.append("candidate-canary")
            self.assertEqual(self.root, root)
            self.assertEqual(self.image_id, image)
            self.assertEqual("image-order", run_id)
            self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
            self.assertEqual(staging, package.parent)
            return "http://127.0.0.1:49152/anechoic/mcp"

        self.canary.side_effect = verify_canary

        def record(argv, cwd):
            result = runner(argv, cwd)
            if any(item.endswith("run_full_test_suite.py") for item in argv):
                events.append("full-suite-green")
            elif self._is_mcp_bootstrap(argv):
                events.append("launch")
            elif argv[:3] == ("docker", "image", "ls"):
                events.append("post-smoke-image-cleanup")
            return result

        result = run_local_release(self.root, run_id="image-order", runner=record)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(2, self.image_factory.call_count)
        self.assertEqual([unittest.mock.call(use_packaged_assets=True)] * 3, self.image.identity.call_args_list)
        source, temporary = self.image_factory.call_args_list[0].args
        self.assertTrue(source.is_relative_to(self.root / ".anechoic_tmp/simple_local_release"))
        self.assertEqual(source.parent / "image_builds", temporary)
        self.assertEqual(self.runtime / "simple_local_release/package", self.image_factory.call_args_list[1].args[0])
        launch = next(argv for argv in calls if self._is_mcp_bootstrap(argv))
        self.assertEqual((sys.executable, str(self.runtime / "start_mcp.py")), launch[:2])
        self.assertEqual(str(self.runtime / "simple_local_release/package"), launch[launch.index("--source-root") + 1])
        self.assertNotIn("--image", launch)
        self.assertIn("--no-build", launch)
        self.assertLess(events.index("full-suite-green"), events.index("candidate-resolve"))
        self.assertLess(events.index("candidate-resolve"), events.index("candidate-canary"))
        self.assertLess(events.index("candidate-canary"), events.index("installed-resolve"))
        self.assertLess(events.index("installed-resolve"), events.index("launch"))
        self.assertLess(events.index("launch"), events.index("post-smoke-image-cleanup"))
        self.assertEqual("http://127.0.0.1:49152/anechoic/mcp", result["canary_endpoint"])

    def test_failed_candidate_canary_preserves_the_installed_release(self):
        self.canary.side_effect = local_release.LocalReleaseError("local-release-canary-probe-failed")
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="canary-failed", runner=runner)
        self.assertEqual("verify_candidate_image", result["failed_step"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))
        self.assertFalse(any(argv[:3] == ("docker", "image", "rm") for argv in calls))

    def test_image_preparation_failure_preserves_previous_installation(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_bytes(b"previous payload")
        self.image.resolve.side_effect = RuntimeError("image unavailable")
        runner, calls = self._runner()
        with (
            patch("local_release.cleanup_stopped_containers") as stopped_cleanup,
            patch("local_release.cleanup_obsolete_images") as image_cleanup,
        ):
            result = run_local_release(self.root, run_id="image-failed", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(b"previous payload", (runtime_package / "old.txt").read_bytes())
        self.assertEqual(b"previous payload", (skill / "old.txt").read_bytes())
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))

    def test_packaged_fingerprint_mismatch_preserves_previous_installation(self):
        runtime_package = self.runtime / "simple_local_release/package"
        runtime_package.mkdir(parents=True)
        (runtime_package / "old.txt").write_bytes(b"previous payload")
        self.image.identity.side_effect = [SimpleNamespace(fingerprint="b" * 64),
                                           SimpleNamespace(fingerprint="c" * 64)]
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="package-mismatch", runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(b"previous payload", (runtime_package / "old.txt").read_bytes())
        self.assertFalse(any(self._is_mcp_bootstrap(argv) for argv in calls))


if __name__ == "__main__":
    unittest.main()
