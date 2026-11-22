"""The concrete Local release flow, without running Docker or installing packages."""


from __future__ import annotations

import subprocess
import os
from pathlib import Path
import io
import stat
import unittest
from unittest.mock import patch


from RELEASE_VERSION.local_release import run_local_release  # noqa: E402


from RELEASE_VERSION.RELEASE_VERSION__tests.RELEASE_VERSION__tests__shared import SimpleReleaseFixture  # noqa: E402


class SimpleLocalReleaseTests(SimpleReleaseFixture, unittest.TestCase):
    def test_unsafe_product_descendant_refuses_before_any_clear(self):
        (self.product / "linked.txt").symlink_to(self.installed / "old.txt")
        self._assert_input_refused("unsafe-product")


    def test_invalid_version_refuses_before_tests_or_replacement(self):
        version = self.root / "version.toml"
        version.write_text('[framework]\nversion = "invalid"\n')
        self._assert_input_refused("invalid-version", "bump_candidate_version")
        self.assertIn('version = "invalid"', version.read_text())


    def test_release_preserves_launcher_and_runtime_config(self):
        launcher = self.runtime / "start_mcp.py"
        launcher.write_bytes(b"existing launcher\n")
        state = self.runtime / "project_mcp_state.json"
        state.write_text("retain this runtime state\n", encoding="utf-8")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="launcher-state", runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(self.engine_bootstrap.read_bytes(), launcher.read_bytes())
        self.assertEqual(0o755, stat.S_IMODE(launcher.stat().st_mode))
        self.assertEqual("keep = true\n", (self.runtime / "config.toml").read_text())
        self.assertEqual("retain this runtime state\n", state.read_text())
        self.start_container.assert_called_once()


    def test_four_component_local_version_increments_without_rollover(self):
        (self.root / "version.toml").write_text('[framework]\nversion = "0.4.1.9"\n', encoding="utf-8")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="version", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertIn('version = "0.4.1.10"', (self.root / "version.toml").read_text())


    def test_workbench_node_dependencies_are_not_packaged(self):
        frontend = self.root / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
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
            self.root / kept.parts[0],
            self.root / kept.parent,
            self.installed / "obsolete",
            self.runtime / "simple_local_release/package/LAYER_4_ENGINE_STUDIO_C14",
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
        self.assertTrue((self.root / kept).is_file())
        for target in (self.root, self.installed):
            self.assertFalse((target / removed).exists())


    def _failing_gate_runner(self, calls, stdout, stderr):
        staged = False

        def runner(argv, cwd):
            nonlocal staged
            calls.append(argv)
            if argv[:2] == ("git", "add"):
                staged = True
            elif argv[:2] == ("git", "commit"):
                staged = False
            if argv[:2] == ("git", "rev-parse"):
                return subprocess.CompletedProcess(argv, 0, "d" * 40 + "\n", "")
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, int(staged), "", "")
            if any(item.endswith("test_suite__pub.py") for item in argv):
                self.assertIn("--all-groups", argv)
                self.assertIn("--managed-python", argv)
                self.assertEqual("LAYER_3_ENVIRONMENTS_C72/engine", Path(argv[argv.index("--project") + 1]).relative_to(Path(__file__).resolve().parents[3]).as_posix())
                self.assertIn("3.14", argv)
                self.assertEqual(str(self.root), argv[argv.index("--project-root") + 1])
                for target in (self.product, self.installed):
                    self.assertEqual("obsolete", (target / "old.txt").read_text())
            failed = any(item.endswith("test_suite__pub.py") for item in argv)
            return subprocess.CompletedProcess(argv, 2 if failed else 0, stdout if failed else "", stderr if failed else "")

        return runner

    def test_test_failure_leaves_both_methodology_destinations_untouched(self):
        calls = []
        stdout = "early stdout evidence\n" + "output tail\n" * 500
        stderr = "early failure traceback\n" + "error tail\n" * 500

        runner = self._failing_gate_runner(calls, stdout, stderr)

        with (
            patch("RELEASE_VERSION.local_release_runner.cleanup_stopped_containers") as stopped_cleanup,
            patch("RELEASE_VERSION.local_release_runner.cleanup_obsolete_images") as image_cleanup,
        ):
            result = run_local_release(self.root, run_id="tests-failed", runner=runner)
        self.assertEqual("static_tests", result["failed_step"])
        self.assertEqual("failed", result["outcome"])
        self.image_factory.assert_not_called()
        self.start_container.assert_not_called()
        self.image.mark_production_image.assert_not_called()
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.assertEqual(1, sum(any(item.endswith("test_suite__pub.py") for item in argv) for argv in calls))
        gate = next(argv for argv in calls if any(item.endswith("test_suite__pub.py") for item in argv))
        self.assertEqual("static", gate[gate.index("--phase") + 1])
        self.assertNotIn("--candidate-image", gate)
        self.assertEqual(2, sum(argv[:2] == ("git", "commit") for argv in calls))
        report = (self.root / result["report_path"]).read_text()
        logs = list((self.root / ".anechoic_tmp/simple_local_release").glob("tests-failed-tests-*.log"))
        self.assertEqual(1, len(logs))
        self.assertIn(f"Complete test output: `{logs[0].relative_to(self.root).as_posix()}`", report)
        self.assertEqual(f"stdout:\n{stdout}\nstderr:\n{stderr}", logs[0].read_text())
        self.assertNotIn("early failure traceback", report)
        with patch("RELEASE_VERSION.local_release_runner.tempfile.NamedTemporaryFile", side_effect=OSError("unavailable")):
            unsaved = run_local_release(self.root, run_id="tests-log-unavailable", runner=runner)
        self.assertEqual(("failed", "static_tests"), (unsaved["outcome"], unsaved["failed_step"]))
        self.assertIn("Complete test output could not be saved (OSError)",
                      (self.root / unsaved["report_path"]).read_text())


    def test_default_tests_log_is_retained_on_interrupt_with_actual_failed_step(self):
        runner, calls = self._runner()

        def interrupted(argv, cwd, log, *, env=None):
            self.assertIn("-u", argv)
            self.assertEqual(self.root, cwd)
            log.write(b"partial test evidence\n")
            log.flush()
            raise KeyboardInterrupt

        output = io.StringIO()
        with patch("RELEASE_VERSION.local_release_runner.subprocess.run", side_effect=lambda argv, **kwargs: runner(argv, kwargs["cwd"])), \
                patch("RELEASE_VERSION.local_release_runner.run_logged_test_process", side_effect=interrupted), \
                patch("RELEASE_VERSION.local_release_runner.sys.stderr", output):
            result = run_local_release(self.root, run_id="interrupted")

        self.assertEqual(("failed", "static_tests", "KeyboardInterrupt"),
                         (result["outcome"], result["failed_step"], result["error_type"]))
        self.assertEqual("partial test evidence\n", (self.root / result["test_log_path"]).read_text())
        report = (self.root / result["report_path"]).read_text()
        self.assertIn("Stopped at: `static_tests`", report)
        self.assertIn("Error class: `KeyboardInterrupt`", report)
        self.assertIn(result["test_log_path"], report)
        self.assertIn("Local release phase START: static tests", output.getvalue())
        self.assertIn(result["test_log_path"], output.getvalue())
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.start_container.assert_not_called()


    def test_default_test_log_survives_later_failure_without_whole_output_capture(self):
        runner, _ = self._runner()

        def passed(argv, cwd, log, *, env=None):
            log.write(b"complete test evidence\n")
            return subprocess.CompletedProcess(argv, 0, "bounded tail", "")

        with patch("RELEASE_VERSION.local_release_runner.subprocess.run", side_effect=lambda argv, **kwargs: runner(argv, kwargs["cwd"])), \
                patch("RELEASE_VERSION.local_release_runner.run_logged_test_process", side_effect=passed), \
                patch("RELEASE_VERSION.local_release_package_phases._prepare_package", side_effect=RuntimeError("package failed")):
            result = run_local_release(self.root, run_id="later-failed")

        self.assertEqual(("failed", "build_package"), (result["outcome"], result["failed_step"]))
        self.assertEqual("complete test evidence\n", (self.root / result["test_log_path"]).read_text())
        self.assertIn(result["test_log_path"], (self.root / result["report_path"]).read_text())


    def test_default_runner_streams_one_log_for_each_gate(self):
        runner, _ = self._runner()
        phases = []

        def passed(argv, cwd, log, *, env=None):
            project = Path(argv[argv.index("--project") + 1])
            engine = project.parents[1] / "LAYER_4_ENGINE_STUDIO_C14"
            self.assertEqual(str(engine / ".venv-dev"), env["UV_PROJECT_ENVIRONMENT"])
            self.assertEqual(str(engine), env["PYTHONPATH"])
            self.assertNotIn("PYTHONHOME", env)
            self.assertNotIn("VIRTUAL_ENV", env)
            self.assertIn("-P", argv)
            phase = argv[argv.index("--phase") + 1]
            phases.append(phase)
            log.write(f"{phase} evidence\n".encode())
            output = "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n" if phase == "image" else ""
            return subprocess.CompletedProcess(argv, 0, output, "")

        original_run = subprocess.run
        def run(argv, **kwargs):
            if argv[0] in ("git", "docker"):
                return runner(argv, self.root)
            return original_run(argv, **kwargs)

        with patch.dict(os.environ, {"PYTHONHOME": "/bad", "VIRTUAL_ENV": "/bad", "PYTHONPATH": "/bad"}), \
                patch("RELEASE_VERSION.local_release_runner.subprocess.run", side_effect=run), \
                patch("RELEASE_VERSION.local_release_runner.run_logged_test_process", side_effect=passed):
            result = run_local_release(self.root, run_id="two-logs")
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(["static", "unit", "image"], phases)
        for phase in phases:
            path = self.root / result["test_log_paths"][phase]
            self.assertEqual(f"{phase} evidence\n", path.read_text())
        self.assertEqual(result["test_log_paths"]["image"], result["test_log_path"])



if __name__ == "__main__":
    unittest.main()
