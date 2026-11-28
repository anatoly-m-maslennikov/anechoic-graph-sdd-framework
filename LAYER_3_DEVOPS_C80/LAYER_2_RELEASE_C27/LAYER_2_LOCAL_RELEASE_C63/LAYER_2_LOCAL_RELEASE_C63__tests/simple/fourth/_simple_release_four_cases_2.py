"""Mocked local release cases."""

import json
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    LocalReleaseRun,
    run_local_release,
)


class SimpleReleaseFourCases2:
    def test_failed_candidate_canary_preserves_the_installed_release(self):
        runner, calls = self._runner()

        def fail_canary(argv, cwd):
            result = runner(argv, cwd)
            if (
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "canary"
            ):
                return subprocess.CompletedProcess(
                    argv, 1, "", "canary failed"
                )
            return result

        result = run_local_release(
            self.root, run_id="canary-failed", runner=fail_canary
        )
        self.assertEqual(
            ("failed", "verify_candidate_canary"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertIsNone(result["canary_endpoint"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.start_container.assert_not_called()
        self.assertFalse(
            any(argv[:3] == ("docker", "image", "rm") for argv in calls)
        )
        self.assertIn(
            "canary failed", (self.root / result["report_path"]).read_text()
        )

    def test_changed_package_stops_canary_and_preserves_installation(self):
        runner, calls = self._runner()

        def mutate_package(argv, cwd):
            result = runner(argv, cwd)
            if (
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "image-tests"
            ):
                package = self.image_factory.call_args.args[0]
                (package / "unverified.txt").write_text("new package input")
            return result

        result = run_local_release(
            self.root, run_id="candidate-changed", runner=mutate_package
        )
        self.assertEqual(
            ("failed", "verify_candidate_canary"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertIn(
            "local-release-package-verification-failed",
            (self.root / result["report_path"]).read_text(),
        )
        self.assertFalse(
            any(
                "--phase" in argv
                and argv[argv.index("--phase") + 1] == "canary"
                for argv in calls
            )
        )
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.start_container.assert_not_called()

    def _release_from_source_suite(self, choices, failed_phase=None):
        source = self.root / "source"
        source.mkdir()
        engine = source / "LAYER_4_ENGINE_STUDIO_C14"
        options = {
            "source_root": source,
            "canary_root": self.root,
            "canary_settings_sha256": "e" * 64,
        }
        runner, _ = self._runner()
        calls, probes = [], []

        def probe(argv, **kwargs):
            self.assertEqual(source, kwargs["cwd"])
            self.assertEqual(str(engine), kwargs["env"]["PYTHONPATH"])
            self.assertEqual(str(engine / ".venv-dev/bin/python"), argv[0])
            self.assertIn("-B", argv)
            probes.append(argv)
            return subprocess.CompletedProcess(
                argv, 0, f"options:\n  --phase {{{choices}}}\n", ""
            )

        def gate(argv, cwd, log, **kwargs):
            self.assertEqual(source, cwd)
            phase = argv[argv.index("--phase") + 1]
            calls.append((phase, argv))
            log.write(f"{phase} verification\n".encode())
            endpoint = (
                "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/"
                "mcp\n"
            )
            if phase == failed_phase:
                return subprocess.CompletedProcess(
                    argv, 1, f"{phase} failed", ""
                )
            return subprocess.CompletedProcess(
                argv, 0, endpoint if phase in {"image", "canary"} else "", ""
            )

        result = self._run_source_suite(options, runner, probe, gate)
        return result, calls, probes

    def _run_source_suite(self, options, runner, probe, gate):
        with (
            patch.object(
                LocalReleaseRun, "_test_gate_options", return_value=options
            ),
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_progress."
                    "COMMAND_ROOT"
                ),
                self.root,
            ),
            self._patch_host_commands(runner, help_probe=probe),
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "run_logged_test_process"
                ),
                side_effect=gate,
            ),
        ):
            result = run_local_release(
                self.root, run_id="source-gate-capabilities"
            )
        return result

    def test_legacy_source_suite_runs_combined_verification_once(self):
        result, calls, probes = self._release_from_source_suite(
            "preflight,static,functional,unit,image"
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            ["preflight", "static", "functional", "image"],
            [phase for phase, _ in calls],
        )
        self.assertEqual(1, len(probes))
        argv = calls[-1][1]
        self.assertEqual(
            self.image_id, argv[argv.index("--candidate-image") + 1]
        )
        self.assertEqual(
            str(self.root), argv[argv.index("--canary-project-root") + 1]
        )
        self.assertIn("--canary-package", argv)
        self.assertEqual(
            "e" * 64,
            json.loads(argv[argv.index("--canary-selection") + 1])[
                "runtime_settings_sha256"
            ],
        )
        self.assertEqual(
            "http://127.0.0.1:49152/anechoic/mcp", result["canary_endpoint"]
        )
        self.assertEqual(
            result["test_log_paths"]["image"],
            result["test_log_paths"]["canary"],
        )

    def test_current_source_suite_canary_failure_does_not_run_combined_verification(
        self,
    ):
        result, calls, probes = self._release_from_source_suite(
            "preflight,static,functional,unit,image,image-tests,canary",
            failed_phase="canary",
        )
        self.assertEqual(
            ("failed", "verify_candidate_canary"),
            (result["outcome"], result["failed_step"]),
            result,
        )
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            [phase for phase, _ in calls],
        )
        self.assertEqual(2, len(probes))
        self.assertNotEqual(
            result["test_log_paths"]["image"],
            result["test_log_paths"]["canary"],
        )
        self.start_container.assert_not_called()

    def test_image_preparation_failure_preserves_previous_installation(self):
        runtime_package = self.runtime / "simple_local_release/package"
        skill = self.root / ".agents/skills/ane"
        for target in (runtime_package, skill):
            target.mkdir(parents=True)
            (target / "old.txt").write_bytes(b"previous payload")
        self.image.resolve.side_effect = RuntimeError("image unavailable")
        runner, calls = self._runner()
        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "cleanup_stopped_containers"
                )
            ) as stopped_cleanup,
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63.local_release_runner."
                    "cleanup_obsolete_images"
                )
            ) as image_cleanup,
        ):
            result = run_local_release(
                self.root, run_id="image-failed", runner=runner
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        stopped_cleanup.assert_not_called()
        image_cleanup.assert_not_called()
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(
            b"previous payload", (runtime_package / "old.txt").read_bytes()
        )
        self.assertEqual(b"previous payload", (skill / "old.txt").read_bytes())
        self.start_container.assert_not_called()

    def test_packaged_fingerprint_mismatch_preserves_previous_installation(
        self,
    ):
        runtime_package = self.runtime / "simple_local_release/package"
        runtime_package.mkdir(parents=True)
        (runtime_package / "old.txt").write_bytes(b"previous payload")
        self.image.identity.side_effect = [
            SimpleNamespace(fingerprint="b" * 64),
            SimpleNamespace(fingerprint="c" * 64),
        ]
        runner, calls = self._runner()
        result = run_local_release(
            self.root, run_id="package-mismatch", runner=runner
        )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("prepare_candidate_image", result["failed_step"])
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(
            b"previous payload", (runtime_package / "old.txt").read_bytes()
        )
        self.start_container.assert_not_called()
