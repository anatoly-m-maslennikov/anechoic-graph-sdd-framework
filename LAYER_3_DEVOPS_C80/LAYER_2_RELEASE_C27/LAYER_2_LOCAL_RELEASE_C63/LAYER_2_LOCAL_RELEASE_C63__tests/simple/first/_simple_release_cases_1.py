"""Cases for the mocked local release fixture."""

import json
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63 import (
    local_release_package_phases as package_phases,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)


class SimpleReleaseCases1:
    def test_root_project_atoms_stay_outside_framework_package(self):
        original = read_release_selection(self.root).manifest_path
        manifest = original.rename(self.root / original.name)
        goal = self.root / "AN-S-2-SPEC-PROJECT_GOAL--goal.md"
        goal.write_text(
            "---\natom_family: SPEC\natom_id: AN-S-2\ncontext: {template: project_goal}\n"
            "state: {status: active, version: 1}\n---\n## Summary\n\nProject goal\n"
        )
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="root-project-atoms", runner=runner
        )
        self.assertEqual("completed", result["outcome"], result)
        package = self.runtime / "simple_local_release/package"
        for source in (manifest, goal):
            self.assertTrue(source.is_file())
            self.assertFalse((package / source.name).exists())

    def test_native_release_runs_full_gates_and_copies_selected_sources(self):
        runner, calls = self._runner()
        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases."
                    "_native_release_sources"
                ),
                wraps=package_phases._native_release_sources,
            ) as select,
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_recovery."
                    "_build_predecessor"
                ),
                return_value=None,
            ),
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "_launcher_image"
                ),
                side_effect=[None, self.image_id],
            ),
        ):
            result = run_local_release(
                self.root, run_id="native-release", runner=runner
            )
        self.assertEqual("completed", result["outcome"], result)
        self.image.mark_production_image.assert_called_once_with(self.image_id)
        self.image.prune_build_cache.assert_called_once_with()
        self.assertGreaterEqual(select.call_count, 2)
        self.assertTrue(
            all(
                call.args[0].manifest_ref == "AN-S-001@1"
                for call in select.call_args_list
            )
        )
        self.assert_native_gates(calls)
        self.assert_native_package(result)

    def assert_native_gates(self, calls):
        gates = [
            call
            for call in calls
            if any(arg.endswith("test_suite__pub.py") for arg in call)
        ]
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [argv[argv.index("--phase") + 1] for argv in gates],
        )
        self.assertNotIn("--candidate-image", gates[0])
        self.assertTrue(all("--required" not in gate for gate in gates[:2]))
        self.assertNotIn("--candidate-image", gates[1])
        image_gate, canary_gate = gates[-2:]
        self.assertEqual(
            ("--candidate-image", self.image_id),
            image_gate[image_gate.index("--phase") + 2 :],
        )
        self.assertEqual(
            self.image_id,
            canary_gate[canary_gate.index("--candidate-image") + 1],
        )
        self.assertIn("--canary-package", canary_gate)
        self.assertEqual(
            "native-release", canary_gate[canary_gate.index("--run-id") + 1]
        )
        self.assert_native_handoff(canary_gate)

    def assert_native_handoff(self, canary_gate):
        selection = read_release_selection(self.root)
        handoff = json.loads(
            canary_gate[canary_gate.index("--canary-selection") + 1]
        )
        self.assertEqual(
            {
                "control_root": selection.control_relative.as_posix(),
                "manifest_path": selection.manifest_path.relative_to(
                    self.root
                ).as_posix(),
                "manifest_ref": selection.manifest_ref,
                "manifest_sha256": selection.manifest_sha256,
                "project_name": selection.project_name,
                "project_prefix": selection.project_prefix,
                "query_enabled": "query_run"
                not in selection.parameters.get("project_mcp", {}).get(
                    "tool_blacklist", ()
                ),
            },
            handoff,
        )

    def assert_native_package(self, result):
        self.assertEqual("refresh", result["image_mode"])
        self.start_container.assert_called_once()
        product_sources = self.root
        for relative, source in self._native_sources().items():
            self.assertEqual(
                source.read_bytes(), (product_sources / relative).read_bytes()
            )
            self.assertEqual(
                source.read_bytes(), (self.installed / relative).read_bytes()
            )
            self.assertEqual(
                source.read_bytes(),
                (
                    self.runtime / "simple_local_release/package" / relative
                ).read_bytes(),
            )
        self.assertEqual(
            (
                self.root
                / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
            ).read_bytes(),
            (
                self.runtime
                / (
                    "simple_local_release/package/LAYER_3_DEVOPS_C80/"
                    "LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
                )
            ).read_bytes(),
        )
        self.assertFalse(
            (
                self.installed / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72"
            ).exists()
        )
        self.assertFalse(
            (
                self.runtime
                / "simple_local_release/package/METHODOLOGY/sources"
            ).exists()
        )
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())

    def test_package_uses_prepared_layer_when_live_layer_changes(self):
        original_prepare = package_phases._prepare_package
        relative = next(iter(self._native_sources()))
        expected = self._native_sources()[relative].read_bytes()

        def mutate_live_layer(root, product, package, **kwargs):
            (root / relative).write_bytes(b"changed after snapshot")
            return original_prepare(root, product, package, **kwargs)

        runner, _ = self._runner()
        with patch(
            (
                "LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases."
                "_prepare_package"
            ),
            side_effect=mutate_live_layer,
        ):
            result = run_local_release(
                self.root, run_id="snapshot-package", runner=runner
            )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(expected, (self.installed / relative).read_bytes())
        self.assertEqual(
            expected,
            (
                self.runtime / "simple_local_release/package" / relative
            ).read_bytes(),
        )

    def test_production_tag_failure_preserves_verified_start_for_resume(self):
        def observe(*args, evidence, **kwargs):
            evidence.update(container_id="e" * 64, readiness="healthy")
            return "http://127.0.0.1:12345/anechoic/mcp"

        self.start_container.side_effect = observe
        self.image.mark_production_image.side_effect = RuntimeError(
            "tag unavailable"
        )
        runner, calls = self._runner()
        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "cleanup_obsolete_images"
                )
            ) as cleanup,
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "prune_temporary_files"
                )
            ) as prune,
        ):
            result = run_local_release(
                self.root, run_id="tag-failed", runner=runner
            )
        cleanup.assert_not_called()
        prune.assert_not_called()
        self.image.prune_build_cache.assert_not_called()
        self.assertEqual(
            ("completed_with_cleanup_pending", None),
            (result["outcome"], result["failed_step"]),
        )
        self.assertEqual("healthy", result["evidence"]["readiness"])
        receipt = (self.root / result["receipt_path"]).read_text()
        self.assertIn(
            "Production image tag failed. Cleanup deferred.", receipt
        )
        self.assertIn(result["endpoint"], receipt)
        self.assertNotIn("tag unavailable", receipt)

        self.assert_resume_after_tag_failure(result, calls, observe, runner)

    def assert_resume_after_tag_failure(self, result, calls, observe, runner):
        self.image.mark_production_image.side_effect = None
        calls.clear()
        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "find_release_container"
                ),
                return_value="e" * 64,
            ),
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "verify_release_container"
                ),
                side_effect=observe,
            ),
        ):
            resumed = run_local_release(
                self.root, run_id="tag-failed", runner=runner, resume=True
            )
        self.assertEqual("completed", resumed["outcome"], resumed)
        self.assertEqual(
            result["evidence"]["container_id"],
            resumed["evidence"]["container_id"],
        )
        self.assertEqual(2, self.image.mark_production_image.call_count)
        self.start_container.assert_called_once()
        self.assertFalse(any("--phase" in argv for argv in calls))
