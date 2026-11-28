"""Mocked local release cases."""

import io
from pathlib import Path
import subprocess
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class SimpleReleaseTwoCases2:
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
                return subprocess.CompletedProcess(
                    argv, 0, "d" * 40 + "\n", ""
                )
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, int(staged), "", "")
            if any(item.endswith("test_suite__pub.py") for item in argv):
                if argv[argv.index("--phase") + 1] != "preflight":
                    self.assertIn("--all-groups", argv)
                    self.assertIn("--managed-python", argv)
                    self.assertEqual(
                        "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine",
                        Path(argv[argv.index("--project") + 1])
                        .relative_to(Path(__file__).resolve().parents[6])
                        .as_posix(),
                    )
                    self.assertIn("3.14", argv)
                self.assertEqual(
                    str(self.root), argv[argv.index("--project-root") + 1]
                )
                for target in (self.product, self.installed):
                    self.assertEqual(
                        "obsolete", (target / "old.txt").read_text()
                    )
            failed = (
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "static"
            )
            return subprocess.CompletedProcess(
                argv,
                2 if failed else 0,
                stdout if failed else "",
                stderr if failed else "",
            )

        return runner

    def test_test_failure_leaves_both_methodology_destinations_untouched(self):
        calls = []
        stdout = "early stdout evidence\n" + "output tail\n" * 500
        stderr = "early failure traceback\n" + "error tail\n" * 500

        runner = self._failing_gate_runner(calls, stdout, stderr)

        with (
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.cleanup_stopped_containers"
            ) as stopped_cleanup,
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.cleanup_obsolete_images"
            ) as image_cleanup,
        ):
            result = run_local_release(
                self.root, run_id="tests-failed", runner=runner
            )
        self.assertEqual("static_tests", result["failed_step"])
        self.assertEqual("failed", result["outcome"])
        self.image_factory.assert_not_called()
        self.start_container.assert_not_called()
        self.image.mark_production_image.assert_not_called()
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        gates = [argv for argv in calls if "--phase" in argv]
        self.assertEqual(
            ["preflight", "static"],
            [argv[argv.index("--phase") + 1] for argv in gates],
        )
        gate = gates[-1]
        self.assertEqual("static", gate[gate.index("--phase") + 1])
        self.assertNotIn("--candidate-image", gate)
        self.assertEqual(
            2, sum(argv[:2] == ("git", "commit") for argv in calls)
        )
        self._assert_failed_test_logs(result, stdout, stderr, runner)

    def _assert_failed_test_logs(self, result, stdout, stderr, runner):
        report = (self.root / result["report_path"]).read_text()
        logs = list(
            (self.root / ".anechoic_tmp/simple_local_release").glob(
                "tests-failed-tests-*.log"
            )
        )
        self.assertEqual(1, len(logs))
        self.assertIn(
            f"Complete test output: `{logs[0].relative_to(self.root).as_posix()}`",
            report,
        )
        self.assertEqual(
            f"stdout:\n{stdout}\nstderr:\n{stderr}", logs[0].read_text()
        )
        self.assertNotIn("early failure traceback", report)
        with patch(
            "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.tempfile.NamedTemporaryFile",
            side_effect=OSError("unavailable"),
        ):
            unsaved = run_local_release(
                self.root, run_id="tests-log-unavailable", runner=runner
            )
        self.assertEqual(
            ("failed", "static_tests"),
            (unsaved["outcome"], unsaved["failed_step"]),
        )
        self.assertIn(
            "Complete test output could not be saved (OSError)",
            (self.root / unsaved["report_path"]).read_text(),
        )

    def test_default_tests_log_is_retained_on_interrupt_with_actual_failed_step(
        self,
    ):
        runner, calls = self._runner()

        def interrupted(
            argv, cwd, log, *, env=None, lock_fd=None, check_abort=None
        ):
            self.assertIn("-u", argv)
            self.assertEqual(self.root, cwd)
            if argv[argv.index("--phase") + 1] == "preflight":
                return subprocess.CompletedProcess(argv, 0, "", "")
            log.write(b"partial test evidence\n")
            log.flush()
            raise KeyboardInterrupt

        output = io.StringIO()
        with (
            self._patch_host_commands(runner),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT",
                self.root,
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.run_logged_test_process",
                side_effect=interrupted,
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.sys.stderr",
                output,
            ),
        ):
            result = run_local_release(self.root, run_id="interrupted")

        self.assertEqual(
            ("failed", "static_tests", "KeyboardInterrupt"),
            (result["outcome"], result["failed_step"], result["error_type"]),
        )
        self.assertEqual(
            "partial test evidence\n",
            (self.root / result["test_log_path"]).read_text(),
        )
        self._assert_interrupted_report(result, output)

    def _assert_interrupted_report(self, result, output):
        report = (self.root / result["report_path"]).read_text()
        self.assertIn("Stopped at: `static_tests`", report)
        self.assertIn("Error class: `KeyboardInterrupt`", report)
        self.assertIn(result["test_log_path"], report)
        self.assertIn(
            "Local release phase START: static tests", output.getvalue()
        )
        self.assertIn(result["test_log_path"], output.getvalue())
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.start_container.assert_not_called()

    def test_default_test_log_survives_later_failure_without_whole_output_capture(
        self,
    ):
        runner, _ = self._runner()

        def passed(
            argv, cwd, log, *, env=None, lock_fd=None, check_abort=None
        ):
            phase = argv[argv.index("--phase") + 1]
            status = run_local_release(
                self.root, run_id="later-failed", mode="status"
            )
            self.assertEqual(
                status["test_log_paths"][phase],
                Path(log.name).relative_to(self.root).as_posix(),
            )
            log.write(b"complete test evidence\n")
            return subprocess.CompletedProcess(argv, 0, "bounded tail", "")

        with (
            self._patch_host_commands(runner),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT",
                self.root,
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.run_logged_test_process",
                side_effect=passed,
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_package_phases._prepare_package",
                side_effect=RuntimeError("package failed"),
            ),
        ):
            result = run_local_release(self.root, run_id="later-failed")

        self.assertEqual(
            ("failed", "build_package"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertEqual(
            "complete test evidence\n",
            (self.root / result["test_log_path"]).read_text(),
        )
        self.assertIn(
            result["test_log_path"],
            (self.root / result["report_path"]).read_text(),
        )

    def test_rejected_repeat_preserves_completed_receipt(self):
        runner, _ = self._runner()
        run_id = "retained-receipt"
        completed = run_local_release(self.root, run_id=run_id, runner=runner)
        self.assertEqual("completed", completed["outcome"], completed)
        receipt = self.root / completed["receipt_path"]
        original = receipt.read_bytes()

        rejected = run_local_release(self.root, run_id=run_id, runner=runner)
        self.assertEqual("failed", rejected["outcome"], rejected)
        report = self.root / rejected["report_path"]
        self.assertNotEqual(receipt, report)
        self.assertIn(
            "Simple local release failed", report.read_text(encoding="utf-8")
        )
        self.assertEqual(original, receipt.read_bytes())
        status = run_local_release(self.root, run_id=run_id, mode="status")
        self.assertEqual(
            ("completed", completed["receipt_path"]),
            (status["release_outcome"], status["report_path"]),
        )
        self.assertEqual(
            completed,
            run_local_release(
                self.root, run_id=run_id, runner=runner, resume=True
            ),
        )
