"""Exercise preflight and evidence capture through the Local Release API."""

import unittest
from importlib import import_module
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)

SimpleReleaseFixture = import_module(
    "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests."
    "LAYER_2_LOCAL_RELEASE_C63__tests__shared"
).SimpleReleaseFixture


class LocalReleaseEvidenceTests(SimpleReleaseFixture, unittest.TestCase):
    def test_missing_engine_preflight_leaves_environment_uncreated(self):
        runner, _ = self._runner()
        interpreter = (
            self.root / "LAYER_4_ENGINE_STUDIO_C14/.venv-dev/bin/python"
        )
        with (
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_gates._ROOT",
                self.root,
            ),
            patch(
                "LAYER_2_LOCAL_RELEASE_C63.local_release_progress."
                "COMMAND_ROOT",
                self.root,
            ),
            self._patch_host_commands(runner),
        ):
            result = run_local_release(
                self.root, run_id="missing-preflight-engine"
            )

        self.assertEqual(
            ("failed", "preflight_tests"),
            (result["outcome"], result["failed_step"]),
            result,
        )
        self.assertIn(str(interpreter), result["error"])
        self.assertIn(
            "release.py local --prepare-environment", result["error"]
        )
        self.assertFalse(interpreter.parents[1].exists())
        self.start_container.assert_not_called()

    def _readiness_start(
        self, root, selection, image, fingerprint, port, observer, **options
    ):
        evidence = options["evidence"]
        endpoint = "http://127.0.0.1:12345/anechoic/mcp"
        evidence.update(
            container_id="e" * 64,
            project_instance=selection.instance_id,
            project_root=str(root),
            control_root=selection.control_relative.as_posix(),
            port=port,
            endpoint=endpoint,
            readiness="healthy",
        )
        return endpoint

    def test_readiness_evidence_survives_completed_resume(self):
        runner, _ = self._runner()

        self.start_container.side_effect = self._readiness_start
        options = {"run_id": "evidence", "runner": runner}
        result = run_local_release(self.root, **options)
        self.assertEqual("completed", result["outcome"], result)
        evidence = result["evidence"]
        self.assertEqual(
            ("d" * 40, self.image_id, "b" * 64, "0.4.1.1"),
            (
                evidence["source_sha"],
                evidence["image_id"],
                evidence["fingerprint"],
                evidence["version"],
            ),
        )
        self.assertEqual(
            (12345, "healthy", "e" * 64),
            (
                evidence["port"],
                evidence["readiness"],
                evidence["container_id"],
            ),
        )
        receipt = (self.root / result["receipt_path"]).read_text()
        self.assertIn(evidence["container_id"], receipt)
        self.assertIn(evidence["observed_at"], receipt)
        self.assertEqual(
            result, run_local_release(self.root, resume=True, **options)
        )
        self.start_container.assert_called_once()

    def test_start_failure_preserves_observed_effects_and_diagnostics(self):
        runner, _ = self._runner()
        failure = RuntimeError("candidate port in use")
        note = 'Local Release startup diagnostics: {"port":12345}'
        failure.add_note(note)
        self.start_container.side_effect = failure

        result = run_local_release(
            self.root, run_id="port-in-use", runner=runner
        )

        self.assertEqual(
            ("failed", "start_mcp", 12345),
            (result["outcome"], result["failed_step"], result["port"]),
        )
        phases = {entry["phase"] for entry in result["effects"]}
        self.assertIn("install project runtime", phases)
        self.assertNotIn("start mcp", phases)
        self.assertEqual([note], result["diagnostics"])
