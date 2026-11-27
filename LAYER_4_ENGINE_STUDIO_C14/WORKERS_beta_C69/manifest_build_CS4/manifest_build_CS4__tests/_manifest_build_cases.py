"""Manifest build cases collected by test_worker."""

import json
import os
import signal
import subprocess
import tempfile
import time
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from ..manifest_build_CS4__shared import compile_generation
from .manifest_build_CS4__tests__shared import (
    fixture,
    run_worker,
    worker_command,
    worker_env,
)


def _pause_worker_after_staging(process, output):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and process.poll() is None:
        if list(output.parent.glob(".manifest-build-*")):
            try:
                os.kill(process.pid, signal.SIGSTOP)
                return process.pid
            except ProcessLookupError:
                return None
        time.sleep(0.001)
    return None


class ManifestBuildCases:
    def test_ingested_model_diagnostics_use_final_stderr_record(self):
        diagnostics = [{"code": "invalid_model_source"}]
        stderr = (
            "ANECHOIC_STARTUP_TIMING phase=load\n"
            + json.dumps({"model_diagnostics": diagnostics})
            + "\n"
        )
        failure = subprocess.CompletedProcess([], 1, b"", stderr.encode())
        binding = {
            "root": "/project",
            "control_root": "control",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        with patch.object(subprocess, "run", return_value=failure):
            with self.assertRaises(ValueError) as context:
                compile_generation(
                    binding, Path("generation"), model_inputs={}
                )
        self.assertEqual(diagnostics, context.exception.model_diagnostics)
        self.assertEqual(
            "Manifest compiler failed: " + stderr, str(context.exception)
        )

    def test_cli_build_and_verify_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            result = run_worker(binding, output)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(
                binding["manifest_sha256"], receipt["manifest_sha256"]
            )
            self.assertEqual(
                receipt["structure_sha256"],
                sha256((output / "structure.json").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                binding["manifest_sha256"],
                json.loads((output / "structure.json").read_bytes())[
                    "project"
                ]["sha256"],
            )
            descriptor = (output / "model.json").read_bytes()
            self.assertEqual(
                receipt["model_descriptor_sha256"],
                sha256(descriptor).hexdigest(),
            )
            model = json.loads(descriptor)
            self.assertEqual(receipt["model_sha256"], model["model_sha256"])
            for module, digest in model["modules"].items():
                self.assertEqual(
                    digest,
                    sha256(
                        (
                            output / "anechoic_runtime_model" / module
                        ).read_bytes()
                    ).hexdigest(),
                )

    def test_project_root_manifest_uses_project_relative_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            root_manifest = Path(binding["root"]) / manifest.name
            manifest.rename(root_manifest)
            binding["manifest_path"] = root_manifest.name
            result = run_worker(binding, output)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(
                binding["manifest_sha256"], receipt["manifest_sha256"]
            )
            self.assertEqual(
                binding["manifest_sha256"],
                json.loads((output / "structure.json").read_bytes())[
                    "project"
                ]["sha256"],
            )

    def test_changed_pin_leaves_output_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            process = subprocess.Popen(
                worker_command(output),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=worker_env(),
            )
            process.stdin.write(json.dumps(binding))
            process.stdin.close()
            process.stdin = None
            stopped = None
            try:
                stopped = _pause_worker_after_staging(process, output)
                self.assertIsNotNone(
                    stopped, "Compiler process was not observed"
                )
                manifest.write_bytes(manifest.read_bytes() + b"\n")
                os.kill(stopped, signal.SIGCONT)
                stopped = None
                stdout, stderr = process.communicate(timeout=30)
                self.assertNotEqual(0, process.returncode, stdout + stderr)
            finally:
                if stopped:
                    os.kill(stopped, signal.SIGCONT)
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_symlinked_manifest_and_control(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            target = manifest.with_suffix(".target")
            manifest.rename(target)
            manifest.symlink_to(target)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            manifest.unlink()
            target.rename(manifest)
            control = manifest.parent
            moved = control.with_name("moved-control")
            control.rename(moved)
            control.symlink_to(moved, target_is_directory=True)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_nonempty_output(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            (output / "keep").write_text("keep")
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual("keep", (output / "keep").read_text())
