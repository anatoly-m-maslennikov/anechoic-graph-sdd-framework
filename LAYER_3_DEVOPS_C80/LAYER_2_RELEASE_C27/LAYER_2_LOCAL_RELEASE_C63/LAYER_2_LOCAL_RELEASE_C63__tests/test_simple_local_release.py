"""The concrete Local release flow, without running Docker or installing packages."""


from __future__ import annotations

import subprocess
import json
import shutil
import unittest
from unittest.mock import patch


from LAYER_2_LOCAL_RELEASE_C63 import local_release_package_phases as package_phases  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.local_release_runner import _launcher_image  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import read_release_selection  # noqa: E402
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import _GENERATED_ASSETS  # noqa: E402


from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import SimpleReleaseFixture  # noqa: E402


class SimpleLocalReleaseTests(SimpleReleaseFixture, unittest.TestCase):
    def test_root_project_atoms_stay_outside_framework_package(self):
        original = read_release_selection(self.root).manifest_path
        manifest = original.rename(self.root / original.name)
        goal = self.root / "AN-S-2-SPEC-PROJECT_GOAL--goal.md"
        goal.write_text("---\natom_family: SPEC\natom_id: AN-S-2\ncontext: {template: project_goal}\n"
                        "state: {status: active, version: 1}\n---\n## Summary\n\nProject goal\n")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="root-project-atoms", runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        package = self.runtime / "simple_local_release/package"
        for source in (manifest, goal):
            self.assertTrue(source.is_file())
            self.assertFalse((package / source.name).exists())

    def test_native_release_runs_full_gates_and_copies_selected_sources(self):
        runner, calls = self._runner()
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases._native_release_sources", wraps=package_phases._native_release_sources) as select, \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_recovery._build_predecessor", return_value=None), \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner._launcher_image", side_effect=[None, self.image_id]):
            result = run_local_release(self.root, run_id="native-release", runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        self.image.mark_production_image.assert_called_once_with(self.image_id)
        self.image.prune_build_cache.assert_called_once_with()
        self.assertGreaterEqual(select.call_count, 2)
        self.assertTrue(all(call.args[0].manifest_ref == "AN-S-001@1" for call in select.call_args_list))
        gates = [call for call in calls if any(arg.endswith("test_suite__pub.py") for arg in call)]
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [argv[argv.index("--phase") + 1] for argv in gates],
        )
        self.assertNotIn("--candidate-image", gates[0])
        self.assertTrue(all("--required" not in gate for gate in gates[:2]))
        self.assertNotIn("--candidate-image", gates[1])
        image_gate, canary_gate = gates[-2:]
        self.assertEqual(("--candidate-image", self.image_id), image_gate[image_gate.index("--phase") + 2:])
        self.assertEqual(self.image_id, canary_gate[canary_gate.index("--candidate-image") + 1])
        self.assertIn("--canary-package", canary_gate)
        self.assertEqual("native-release", canary_gate[canary_gate.index("--run-id") + 1])
        selection = read_release_selection(self.root)
        handoff = json.loads(canary_gate[canary_gate.index("--canary-selection") + 1])
        self.assertEqual({
            "control_root": selection.control_relative.as_posix(),
            "manifest_path": selection.manifest_path.relative_to(self.root).as_posix(),
            "manifest_ref": selection.manifest_ref, "manifest_sha256": selection.manifest_sha256,
            "project_name": selection.project_name, "project_prefix": selection.project_prefix,
            "query_enabled": "query_run" not in selection.parameters.get("project_mcp", {}).get("tool_blacklist", ()),
        }, handoff)
        self.assertEqual("refresh", result["image_mode"])
        self.start_container.assert_called_once()
        product_sources = self.root
        for relative, source in self._native_sources().items():
            self.assertEqual(source.read_bytes(), (product_sources / relative).read_bytes())
            self.assertEqual(source.read_bytes(), (self.installed / relative).read_bytes())
            self.assertEqual(source.read_bytes(), (self.runtime / "simple_local_release/package" / relative).read_bytes())
        self.assertEqual((self.root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock").read_bytes(),
                         (self.runtime / "simple_local_release/package/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock").read_bytes())
        self.assertFalse((self.installed / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72").exists())
        self.assertFalse((self.runtime / "simple_local_release/package/METHODOLOGY/sources").exists())
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())


    def test_package_uses_prepared_layer_when_live_layer_changes(self):
        original_prepare = package_phases._prepare_package
        relative = next(iter(self._native_sources()))
        expected = self._native_sources()[relative].read_bytes()

        def mutate_live_layer(root, product, package, **kwargs):
            (root / relative).write_bytes(b"changed after snapshot")
            return original_prepare(root, product, package, **kwargs)

        runner, _ = self._runner()
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases._prepare_package", side_effect=mutate_live_layer):
            result = run_local_release(self.root, run_id="snapshot-package", runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(expected, (self.installed / relative).read_bytes())
        self.assertEqual(expected, (self.runtime / "simple_local_release/package" / relative).read_bytes())


    def test_production_tag_failure_preserves_verified_start_for_resume(self):
        def observe(*args, evidence, **kwargs):
            evidence.update(container_id="e" * 64, readiness="healthy")
            return "http://127.0.0.1:12345/anechoic/mcp"

        self.start_container.side_effect = observe
        self.image.mark_production_image.side_effect = RuntimeError("tag unavailable")
        runner, calls = self._runner()
        with (patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.cleanup_obsolete_images") as cleanup,
              patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.prune_temporary_files") as prune):
            result = run_local_release(self.root, run_id="tag-failed", runner=runner)
        cleanup.assert_not_called()
        prune.assert_not_called()
        self.image.prune_build_cache.assert_not_called()
        self.assertEqual(("completed_with_cleanup_pending", None), (result["outcome"], result["failed_step"]))
        self.assertEqual("healthy", result["evidence"]["readiness"])
        receipt = (self.root / result["receipt_path"]).read_text()
        self.assertIn("Production image tag failed. Cleanup deferred.", receipt)
        self.assertIn(result["endpoint"], receipt)
        self.assertNotIn("tag unavailable", receipt)

        self.image.mark_production_image.side_effect = None
        calls.clear()
        with (patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.find_release_container", return_value="e" * 64),
              patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.verify_release_container", side_effect=observe)):
            resumed = run_local_release(self.root, run_id="tag-failed", runner=runner, resume=True)
        self.assertEqual("completed", resumed["outcome"], resumed)
        self.assertEqual(result["evidence"]["container_id"], resumed["evidence"]["container_id"])
        self.assertEqual(2, self.image.mark_production_image.call_count)
        self.start_container.assert_called_once()
        self.assertFalse(any("--phase" in argv for argv in calls))

    def test_cache_prune_failure_reports_pending_after_promotion(self):
        self.image.prune_build_cache.side_effect = RuntimeError("prune unavailable")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="prune-failed", runner=runner)
        self.assertEqual("completed_with_cleanup_pending", result["outcome"])
        self.assertIn("Docker build cache cleanup failed.", (self.root / result["receipt_path"]).read_text())


    def test_native_manifest_change_stops_before_product_replacement(self):
        runner, _ = self._runner()

        def change_manifest(argv, cwd):
            if argv[0] == "uv":
                path = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
                path.write_text(path.read_text() + "\nchanged\n", encoding="utf-8")
            return runner(argv, cwd)

        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_recovery._build_predecessor", return_value=None), \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner._launcher_image", return_value=None):
            result = run_local_release(self.root, run_id="native-changed", runner=change_manifest)
        self.assertEqual(("failed", "validate_project_selection"), (result["outcome"], result["failed_step"]))
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())


    def test_native_existing_mode_keeps_the_functional_test_gate(self):
        runner, calls = self._runner()
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_recovery._build_predecessor", return_value=None), \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner._launcher_image", side_effect=[None, self.image_id]):
            result = run_local_release(self.root, run_id="native-existing", runner=runner, image_mode="existing")
        self.assertEqual("completed", result["outcome"], result)
        gates = [call for call in calls if any(arg.endswith("test_suite__pub.py") for arg in call)]
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"],
                         [argv[argv.index("--phase") + 1] for argv in gates])
        self.assertNotIn("--candidate-image", gates[1])


    def test_native_source_change_stops_before_product_replacement(self):
        runner, _ = self._runner()
        original_copy = shutil.copy2
        changed = next(iter(self._native_sources().values()))

        def mutate_after_copy(source, destination, *args, **kwargs):
            result = original_copy(source, destination, *args, **kwargs)
            if source == changed:
                changed.write_text("changed", encoding="utf-8")
            return result

        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_recovery._build_predecessor", return_value=None), \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner._launcher_image", return_value=None), \
             patch("LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases.shutil.copy2", side_effect=mutate_after_copy):
            result = run_local_release(self.root, run_id="native-source-change", runner=runner)
        self.assertEqual(("failed", "copy_active_sources"), (result["outcome"], result["failed_step"]))
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())
        self.assertIn('version = "0.4.1.1"', (self.root / "version.toml").read_text())


    def test_existing_image_mode_preserves_checkout_assets_without_a_predecessor(self):
        selection = read_release_selection(self.root)
        selection.launcher_state.mkdir(parents=True)
        (selection.launcher_state / "ready.json").write_text("invalid receipt", encoding="utf-8")
        payloads = {relative: json.dumps({"existing": relative}).encode() for relative in _GENERATED_ASSETS}
        for relative, payload in payloads.items():
            (self.root / relative).write_bytes(payload)

        runner, calls = self._runner()
        result = run_local_release(self.root, run_id="existing-assets", runner=runner, image_mode="existing")

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("existing", result["image_mode"])
        gates = [argv for argv in calls if any(arg.endswith("test_suite__pub.py") for arg in argv)]
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"],
                         [argv[argv.index("--phase") + 1] for argv in gates])
        self.assertNotIn("--candidate-image", gates[1])
        self.assertEqual({"use_packaged_assets": True}, self.image.resolve.call_args_list[0].kwargs)
        runtime_package = self.runtime / "simple_local_release/package"
        for relative, payload in payloads.items():
            self.assertEqual(payload, (self.root / relative).read_bytes())
            self.assertEqual(payload, (runtime_package / relative).read_bytes())


    def test_image_modes_refuse_missing_assets_before_tests(self):
        (self.root / next(iter(_GENERATED_ASSETS))).unlink()
        original_version = (self.root / "version.toml").read_bytes()
        for mode in ("existing", "refresh"):
            with self.subTest(mode=mode):
                runner, calls = self._runner()
                result = run_local_release(self.root, run_id=f"missing-assets-{mode}", runner=runner, image_mode=mode)
                self.assertEqual(("failed", "validate_inputs"), (result["outcome"], result["failed_step"]))
                self.assertEqual(original_version, (self.root / "version.toml").read_bytes())
                self.assertFalse(any(any(item.endswith("test_suite__pub.py") for item in argv) for argv in calls))
        self.image_factory.assert_not_called()


    def test_launcher_image_reads_only_exact_selected_runtime_namespace(self):
        selection = read_release_selection(self.root)
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


    def test_focused_request_runs_and_reports_functional_suite(self):
        modules = (
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_one.py",
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_two.py",
        )
        runner, calls = self._runner()
        result = run_local_release(
            self.root,
            run_id="focused-forwarding",
            runner=runner,
            test_modules=modules,
        )

        self.assertEqual("completed", result["outcome"])
        self.assertEqual("static and functional", result["test_scope"])
        self.assertIsNone(result["test_modules"])
        test_commands = [argv for argv in calls if "--phase" in argv]
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"],
                         [argv[argv.index("--phase") + 1] for argv in test_commands])
        self.assertTrue(all("--test-module" not in argv for argv in test_commands))
        receipt = (self.root / result["receipt_path"]).read_text(encoding="utf-8")
        self.assertIn("Test scope: `static and functional`", receipt)
        self.assertIn("Selected test modules: configured required tests", receipt)


    def test_focused_test_failure_blocks_downstream_release(self):
        modules = ("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_failing.py",)
        base_runner, calls = self._runner()

        def failed_tests(argv, cwd):
            result = base_runner(argv, cwd)
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "static":
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

        self.assertEqual(("failed", "static_tests"), (result["outcome"], result["failed_step"]))
        self.assertEqual("static and functional", result["test_scope"])
        self.assertIsNone(result["test_modules"])
        self.start_container.assert_not_called()
        report = (self.root / result["report_path"]).read_text(encoding="utf-8")
        self.assertIn("Test scope: `static and functional`", report)
        self.assertIn("Selected test modules: configured required tests", report)
        self.assertIn("focused test failure", report)



if __name__ == "__main__":
    unittest.main()
