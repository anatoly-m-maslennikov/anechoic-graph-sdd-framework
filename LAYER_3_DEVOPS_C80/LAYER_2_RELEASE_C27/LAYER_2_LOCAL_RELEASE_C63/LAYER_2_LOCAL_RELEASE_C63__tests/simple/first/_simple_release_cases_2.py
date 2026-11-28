"""Cases for the mocked local release fixture."""

import json
import shutil
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    _GENERATED_ASSETS,
    run_local_release,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)


class SimpleReleaseCases2:
    def test_cache_prune_failure_reports_pending_after_promotion(self):
        self.image.prune_build_cache.side_effect = RuntimeError(
            "prune unavailable"
        )
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="prune-failed", runner=runner
        )
        self.assertEqual("completed_with_cleanup_pending", result["outcome"])
        self.assertIn(
            "Docker build cache cleanup failed.",
            (self.root / result["receipt_path"]).read_text(),
        )

    def test_native_manifest_change_stops_before_product_replacement(self):
        runner, _ = self._runner()

        def change_manifest(argv, cwd):
            if argv[0] == "uv":
                path = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
                path.write_text(
                    path.read_text() + "\nchanged\n", encoding="utf-8"
                )
            return runner(argv, cwd)

        with (
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
                return_value=None,
            ),
        ):
            result = run_local_release(
                self.root, run_id="native-changed", runner=change_manifest
            )
        self.assertEqual(
            ("failed", "validate_project_selection"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())

    def test_native_existing_mode_keeps_the_functional_test_gate(self):
        runner, calls = self._runner()
        with (
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
                self.root,
                run_id="native-existing",
                runner=runner,
                image_mode="existing",
            )
        self.assertEqual("completed", result["outcome"], result)
        gates = [
            call
            for call in calls
            if any(arg.endswith("test_suite__pub.py") for arg in call)
        ]
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [argv[argv.index("--phase") + 1] for argv in gates],
        )
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

        with (
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
                return_value=None,
            ),
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases."
                    "shutil.copy2"
                ),
                side_effect=mutate_after_copy,
            ),
        ):
            result = run_local_release(
                self.root, run_id="native-source-change", runner=runner
            )
        self.assertEqual(
            ("failed", "copy_active_sources"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertEqual("obsolete", (self.product / "old.txt").read_text())
        self.assertIn(
            'version = "0.4.1.1"', (self.root / "version.toml").read_text()
        )

    def test_existing_image_mode_preserves_checkout_assets_without_a_predecessor(
        self,
    ):
        selection = read_release_selection(self.root)
        selection.launcher_state.mkdir(parents=True)
        (selection.launcher_state / "ready.json").write_text(
            "invalid receipt", encoding="utf-8"
        )
        payloads = {
            relative: json.dumps({"existing": relative}).encode()
            for relative in _GENERATED_ASSETS
        }
        for relative, payload in payloads.items():
            (self.root / relative).write_bytes(payload)

        runner, calls = self._runner()
        result = run_local_release(
            self.root,
            run_id="existing-assets",
            runner=runner,
            image_mode="existing",
        )

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("existing", result["image_mode"])
        gates = [
            argv
            for argv in calls
            if any(arg.endswith("test_suite__pub.py") for arg in argv)
        ]
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [argv[argv.index("--phase") + 1] for argv in gates],
        )
        self.assertNotIn("--candidate-image", gates[1])
        self.assertEqual(
            {"use_packaged_assets": True},
            self.image.resolve.call_args_list[0].kwargs,
        )
        runtime_package = self.runtime / "simple_local_release/package"
        for relative, payload in payloads.items():
            self.assertEqual(payload, (self.root / relative).read_bytes())
            self.assertEqual(
                payload, (runtime_package / relative).read_bytes()
            )
