"""Mocked local release cases."""

import os
from pathlib import Path
import subprocess
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
    write_receipt,
)


class SimpleReleaseTwoCases3:
    def test_receipt_records_verified_deployment_without_extra_evidence(self):
        run_id = "deployment-receipt"
        receipt = (
            self.root
            / ".anechoic_runtime/simple_local_release/reports"
            / f"{run_id}.md"
        )
        receipt.parent.mkdir(parents=True, exist_ok=True)
        endpoint = "http://127.0.0.1:18092/anechoic/mcp"
        evidence = self._receipt_evidence(endpoint)
        result = write_receipt(
            self.root,
            receipt,
            run_id,
            "refresh",
            "static and functional",
            "required",
            None,
            endpoint,
            {"image": "image.log"},
            "retained",
            "",
            evidence=evidence,
        )

        self._assert_receipt_evidence(receipt, result, evidence)

    def _receipt_evidence(self, endpoint):
        evidence = {
            "version": "0.4.1.1",
            "source_sha": "1" * 40,
            "source_root": "/source",
            "accepted_source_sha": "a" * 40,
            "image_build_sha": "1" * 40,
            "verified_phases": {
                "verify candidate image": {
                    "source_sha": "1" * 40,
                    "inputs": {"image": "b" * 64},
                },
                "verify candidate canary": {
                    "source_sha": "a" * 40,
                    "inputs": {"canary": "c" * 64},
                },
            },
            "failed_attempts": [
                {
                    "phase": "verify_candidate_canary",
                    "source_sha": "1" * 40,
                    "logs": {"canary": "failed-canary.log"},
                    "error": "omit retained log text",
                }
            ],
            "project_root": str(self.root),
            "target_manifest_sha256": "0" * 64,
            "target_runtime_settings_sha256": "d" * 64,
            "project_instance": "2" * 64,
            "control_root": self.control.name,
            "port": 18092,
            "package_sha256": "3" * 64,
            "image_id": "sha256:" + "4" * 64,
            "fingerprint": "5" * 64,
            "container_id": "6" * 64,
            "readiness": "healthy",
            "observed_at": "2026-11-24T12:00:00Z",
            "endpoint": endpoint,
            "extra": "ignored",
        }
        return evidence

    def _assert_receipt_evidence(self, receipt, result, evidence):
        self.assertEqual(receipt, self.root / result)
        content = receipt.read_text(encoding="utf-8")
        self.assertNotIn("ignored", content)
        for name, value in evidence.items():
            if name not in {"extra", "verified_phases", "failed_attempts"}:
                self.assertIn(f"`{value}`", content)
        self.assertIn(
            f"Accepted source SHA: `{evidence['accepted_source_sha']}`",
            content,
        )
        self.assertIn(
            f"Image build source SHA: `{evidence['image_build_sha']}`", content
        )
        for phase, proof in evidence["verified_phases"].items():
            self.assertIn(
                f"Verification source SHA for `{phase}`: `{proof['source_sha']}`",
                content,
            )
        failed = evidence["failed_attempts"][0]
        self.assertIn(
            f"Stopped at `{failed['phase']}` on source `{failed['source_sha']}`.",
            content,
        )
        self.assertIn(
            "Complete canary test output: `failed-canary.log`", content
        )
        self.assertNotIn(failed["error"], content)

    def test_start_failure_report_retains_diagnostic_notes(self):
        error = LocalReleaseError("local-release-container-exited")
        note = 'Local Release startup diagnostics: {"loopback_port":18092,"state":{"exit_code":137}}'
        error.add_note(note)
        self.start_container.side_effect = error
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="failed-start", runner=runner
        )

        self.assertEqual(
            ("failed", "start_mcp"), (result["outcome"], result["failed_step"])
        )
        report = self.root / result["report_path"]
        self.assertIn(note, report.read_text(encoding="utf-8"))

    def _logged_gate(self, phases):
        def passed(
            argv, cwd, log, *, env=None, lock_fd=None, check_abort=None
        ):
            phase = argv[argv.index("--phase") + 1]
            if phase == "preflight":
                engine = Path(argv[0]).parents[2]
            else:
                project = Path(argv[argv.index("--project") + 1])
                engine = project.parents[2] / "LAYER_4_ENGINE_STUDIO_C14"
            self.assertEqual(
                str(engine / ".venv-dev"), env["UV_PROJECT_ENVIRONMENT"]
            )
            self.assertEqual(str(engine), env["PYTHONPATH"])
            self.assertEqual(
                str(engine / ".venv-dev/bin"), env["PATH"].split(os.pathsep)[0]
            )
            self.assertNotIn("PYTHONHOME", env)
            self.assertNotIn("VIRTUAL_ENV", env)
            self.assertIn("-P", argv)
            self.assertIn("-B", argv)
            phases.append(phase)
            log.write(f"{phase} evidence\n".encode())
            output = (
                "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n"
                if phase == "canary"
                else ""
            )
            return subprocess.CompletedProcess(argv, 0, output, "")

        return passed

    def test_default_runner_streams_one_log_for_each_gate(self):
        runner, _ = self._runner()
        phases = []

        passed = self._logged_gate(phases)

        with (
            patch.dict(
                os.environ,
                {
                    "PYTHONHOME": "/bad",
                    "VIRTUAL_ENV": "/bad",
                    "PYTHONPATH": "/bad",
                },
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_progress.COMMAND_ROOT",
                self.root,
            ),
            self._patch_host_commands(runner),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_runner.run_logged_test_process",
                side_effect=passed,
            ),
        ):
            result = run_local_release(self.root, run_id="gate-logs")
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            ["preflight", "static", "functional", "image-tests", "canary"],
            phases,
        )
        self.assertEqual(
            {"preflight", "static", "functional", "image", "canary"},
            set(result["test_log_paths"]),
        )
        receipt = (self.root / result["receipt_path"]).read_text()
        for phase in phases:
            name = "image" if phase == "image-tests" else phase
            path = result["test_log_paths"][name]
            self.assertEqual(
                f"{phase} evidence\n", (self.root / path).read_text()
            )
            self.assertIn(f"Complete {name} test output: `{path}`", receipt)
        self.assertEqual(
            result["test_log_paths"]["canary"], result["test_log_path"]
        )
