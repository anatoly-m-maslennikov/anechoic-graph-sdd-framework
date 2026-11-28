"""Cases for the mocked local release fixture."""

import json
import subprocess

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    _GENERATED_ASSETS,
    run_local_release,
)
from LAYER_2_LOCAL_RELEASE_C63.local_release_runner import _launcher_image
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)


class SimpleReleaseCases3:
    def test_image_modes_refuse_missing_assets_before_tests(self):
        (self.root / next(iter(_GENERATED_ASSETS))).unlink()
        original_version = (self.root / "version.toml").read_bytes()
        for mode in ("existing", "refresh"):
            with self.subTest(mode=mode):
                runner, calls = self._runner()
                result = run_local_release(
                    self.root,
                    run_id=f"missing-assets-{mode}",
                    runner=runner,
                    image_mode=mode,
                )
                self.assertEqual(
                    ("failed", "validate_inputs"),
                    (result["outcome"], result["failed_step"]),
                )
                self.assertEqual(
                    original_version, (self.root / "version.toml").read_bytes()
                )
                self.assertFalse(
                    any(
                        any(
                            item.endswith("test_suite__pub.py")
                            for item in argv
                        )
                        for argv in calls
                    )
                )
        self.image_factory.assert_not_called()

    def test_launcher_image_reads_only_exact_selected_runtime_namespace(self):
        selection = read_release_selection(self.root)
        old_image = "sha256:" + "c" * 64
        payload = {
            "project_root": str(self.root),
            "control_root": str(self.control),
            "project_id": selection.instance_id,
            "image_id": old_image,
        }
        legacy = (
            self.root
            / ".anechoic_install/project_mcp"
            / selection.instance_id
            / "last_launch.json"
        )
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps(payload), encoding="utf-8")
        retained = legacy.read_bytes()
        sibling = (
            selection.launcher_state.parent / ("d" * 64) / "last_launch.json"
        )
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
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
                "FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_one."
                "py"
            ),
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
                "FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_two."
                "py"
            ),
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
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [argv[argv.index("--phase") + 1] for argv in test_commands],
        )
        self.assertTrue(
            all("--test-module" not in argv for argv in test_commands)
        )
        receipt = (self.root / result["receipt_path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("Test scope: `static and functional`", receipt)
        self.assertIn(
            "Selected test modules: configured required tests", receipt
        )

    def test_focused_test_failure_blocks_downstream_release(self):
        modules = (
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
                "FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/"
                "test_failing.py"
            ),
        )
        base_runner, calls = self._runner()

        def failed_tests(argv, cwd):
            result = base_runner(argv, cwd)
            if (
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "static"
            ):
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

        self.assertEqual(
            ("failed", "static_tests"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertEqual("static and functional", result["test_scope"])
        self.assertIsNone(result["test_modules"])
        self.start_container.assert_not_called()
        report = (self.root / result["report_path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("Test scope: `static and functional`", report)
        self.assertIn(
            "Selected test modules: configured required tests", report
        )
        self.assertIn("focused test failure", report)
