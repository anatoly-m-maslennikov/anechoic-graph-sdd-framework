"""Exercise preflight and evidence capture through the Local Release API."""
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared import (
    SimpleReleaseFixture,
)


class LocalReleaseEvidenceTests(SimpleReleaseFixture, unittest.TestCase):
    def test_fast_policy_runs_both_fast_gates_and_remains_bound_on_resume(self):
        runner, calls = self._runner()
        options = {"run_id": "fast-evidence", "runner": runner}
        result = run_local_release(self.root, functional_suite="fast", **options)
        self.assertEqual("completed", result["outcome"], result)
        self.assertTrue(result["evidence"]["fast_limit_met"])
        for phase, option in (("functional", "--functional-suite"), ("image-tests", "--image-suite"),
                              ("canary", "--image-suite")):
            command, = [argv for argv in calls if "--phase" in argv and argv[argv.index("--phase") + 1] == phase]
            self.assertEqual("fast", command[command.index(option) + 1])
        refused = run_local_release(self.root, resume=True, functional_suite="full", **options)
        self.assertEqual("local-release-functional-suite-invalid", refused["error"])

    def test_fast_overrun_is_reported_after_successful_continuation(self):
        runner, calls = self._runner()
        clock = "LAYER_2_LOCAL_RELEASE_C63.local_release_recovery.time"

        def fail_functional(argv, cwd):
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "functional":
                return subprocess.CompletedProcess(argv, 1, "", "test failed")
            return runner(argv, cwd)

        with patch(clock, return_value=1000):
            first = run_local_release(self.root, run_id="fast-overrun", runner=fail_functional, functional_suite="fast")
        self.assertEqual(("failed", "functional_tests"), (first["outcome"], first["failed_step"]))

        with patch(clock, return_value=1901):
            result = run_local_release(self.root, run_id="fast-overrun", resume=True, runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        evidence = result["evidence"]
        self.assertEqual(901.0, evidence["ready_seconds"])
        self.assertFalse(evidence["fast_target_met"])
        self.assertFalse(evidence["fast_limit_met"])
        phases = [argv[argv.index("--phase") + 1] for argv in calls if "--phase" in argv]
        self.assertEqual(["preflight", "static", "functional", "image-tests", "canary"], phases)
        receipt = (self.root / result["receipt_path"]).read_text()
        self.assertIn("ideal 10-minute target: `False`", receipt)
        self.assertIn("mandatory 15-minute limit: `False`", receipt)
        self.start_container.assert_called_once()

    def test_missing_dependencies_are_prepared_before_preflight(self):
        runner, _ = self._runner()
        failure = {"outcome": "failed", "failed_step": "chromium", "error": "download failed"}
        with (
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT", self.root),
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.subprocess.run",
                  side_effect=lambda argv, **options: runner(argv, options["cwd"])),
            patch("LAYER_2_LOCAL_RELEASE_C63.prepare_test_environment.missing_test_environment",
                  side_effect=[True, False]),
            patch("LAYER_2_LOCAL_RELEASE_C63.prepare_test_environment.prepare_test_environment",
                  side_effect=[failure, failure | {"failed_step": "duckpgq"}]) as prepare,
        ):
            result = run_local_release(self.root, run_id="prepare-missing")
            resumed = run_local_release(self.root, run_id="prepare-missing", resume=True)
        self.assertEqual(2, prepare.call_count)
        prepare.assert_called_with(self.root, verify=False)
        self.assertEqual("preflight_tests", result["failed_step"], result)
        self.assertIn("chromium: download failed", result["error"])
        self.assertIn("duckpgq: download failed", resumed["error"])
        self.assertIn('version = "0.4.1"', (self.root / "version.toml").read_text())
        self.start_container.assert_not_called()

    def test_abort_during_gate_preserves_evidence_for_continuation(self):
        runner, _ = self._runner()
        options = {"run_id": "abort-during-gate"}

        def abort_gate(argv, cwd, log, *, check_abort, **_):
            phase = argv[argv.index("--phase") + 1]
            if phase == "static":
                log.write(b"partial static output\n")
                log.flush()
                requested = run_local_release(self.root, mode="abort", **options)
                self.assertTrue(requested["abort_requested"])
                check_abort()
            return subprocess.CompletedProcess(argv, 0, "", "")

        with (
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT", self.root),
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.subprocess.run",
                  side_effect=lambda argv, **options: runner(argv, options["cwd"])),
            patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.run_logged_test_process", side_effect=abort_gate),
        ):
            failed = run_local_release(self.root, **options)
        self.assertEqual("local-release-aborted", failed["error"])
        self.assertEqual("partial static output\n", (self.root / failed["test_log_path"]).read_text())
        self.start_container.assert_not_called()
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT", self.root):
            resumed = run_local_release(self.root, resume=True, runner=runner, **options)
        self.assertEqual("completed", resumed["outcome"], resumed)
        self.assertFalse(run_local_release(self.root, mode="status", **options)["abort_requested"])

    def test_failed_preflight_refuses_before_version_or_long_gates(self):
        runner, calls = self._runner()

        def fail_preflight(argv, cwd):
            result = runner(argv, cwd)
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "preflight":
                return subprocess.CompletedProcess(argv, 1, "Pinned Chromium not installed", "")
            return result

        result = run_local_release(self.root, run_id="no-browser", runner=fail_preflight)
        self.assertEqual(("failed", "preflight_tests"), (result["outcome"], result["failed_step"]))
        version = self.root / "version.toml"
        self.assertIn('version = "0.4.1"', version.read_text())
        gate, = [argv for argv in calls if "--phase" in argv]
        self.assertEqual("LAYER_4_ENGINE_STUDIO_C14/.venv-dev/bin/python", "/".join(Path(gate[0]).parts[-4:]))
        self.assertIn("Pinned Chromium", result["error"])
        self.start_container.assert_not_called()

    def test_missing_engine_preflight_leaves_environment_uncreated(self):
        runner, _ = self._runner()
        interpreter = self.root / "LAYER_4_ENGINE_STUDIO_C14/.venv-dev/bin/python"
        with patch("LAYER_2_LOCAL_RELEASE_C63.local_release_gates._ROOT", self.root), \
                patch("LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT", self.root), \
                patch("LAYER_2_LOCAL_RELEASE_C63.local_release_runner.subprocess.run",
                      side_effect=lambda argv, **options: runner(argv, options["cwd"])):
            result = run_local_release(self.root, run_id="missing-preflight-engine")

        self.assertEqual(("failed", "preflight_tests"), (result["outcome"], result["failed_step"]), result)
        self.assertIn(str(interpreter), result["error"])
        self.assertIn("release.py local --prepare-environment", result["error"])
        self.assertFalse(interpreter.parents[1].exists())
        self.start_container.assert_not_called()

    def test_readiness_evidence_survives_completed_resume(self):
        runner, _ = self._runner()

        def start(root, selection, image, fingerprint, port, observer, **options):
            evidence = options["evidence"]
            endpoint = "http://127.0.0.1:12345/anechoic/mcp"
            evidence.update(container_id="e" * 64, project_instance=selection.instance_id,
                            project_root=str(root), control_root=selection.control_relative.as_posix(),
                            port=port, endpoint=endpoint, readiness="healthy")
            return endpoint

        self.start_container.side_effect = start
        options = {"run_id": "evidence", "runner": runner}
        result = run_local_release(self.root, **options)
        self.assertEqual("completed", result["outcome"], result)
        evidence = result["evidence"]
        self.assertEqual(("d" * 40, self.image_id, "b" * 64, "0.4.1.1"),
                         (evidence["source_sha"], evidence["image_id"], evidence["fingerprint"], evidence["version"]))
        self.assertEqual((12345, "healthy", "e" * 64),
                         (evidence["port"], evidence["readiness"], evidence["container_id"]))
        receipt = (self.root / result["receipt_path"]).read_text()
        self.assertIn(evidence["container_id"], receipt)
        self.assertIn(evidence["observed_at"], receipt)
        self.assertEqual(result, run_local_release(self.root, resume=True, **options))
        self.start_container.assert_called_once()

    def test_start_failure_preserves_observed_effects_and_diagnostics(self):
        runner, _ = self._runner()
        failure = RuntimeError("candidate port in use")
        note = 'Local Release startup diagnostics: {"port":12345}'
        failure.add_note(note)
        self.start_container.side_effect = failure

        result = run_local_release(self.root, run_id="port-in-use", runner=runner)

        self.assertEqual(("failed", "start_mcp", 12345),
                         (result["outcome"], result["failed_step"], result["port"]))
        phases = {entry["phase"] for entry in result["effects"]}
        self.assertIn("install project runtime", phases)
        self.assertNotIn("start mcp", phases)
        self.assertEqual([note], result["diagnostics"])
