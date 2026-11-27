import json
import os
from hashlib import sha256
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from .WORKERS_beta_C69__tests__shared import (
    generation_fixture,
)
from ._worker_context import WORKER, _WorkerFixture


class GenerationProcessTests(_WorkerFixture, unittest.TestCase):
    def test_real_cli_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            result = subprocess.run(
                [*WORKER, "--generation-dir", str(output)],
                input=json.dumps(binding),
                text=True,
                capture_output=True,
                timeout=120,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            response = json.loads(result.stdout)
            self.assertEqual(
                binding["manifest_sha256"],
                response["snapshot"]["manifest_sha256"],
            )
            self.assertEqual(
                binding["manifest_sha256"],
                response["receipt"]["manifest_sha256"],
            )
            for name, key in [
                ("structure.json", "structure_sha256"),
                ("model.json", "model_descriptor_sha256"),
            ]:
                self.assertEqual(
                    response["receipt"][key],
                    sha256((output / name).read_bytes()).hexdigest(),
                )

    def test_rejects_nonempty_generation_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            existing = output / "structure.json"
            existing.write_text("existing generation")
            result = subprocess.run(
                [*WORKER, "--generation-dir", str(output)],
                input=json.dumps(binding),
                text=True,
                capture_output=True,
                timeout=120,
            )
            self.assertEqual(1, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertIn("Traceback (most recent call last)", result.stderr)
            self.assertIn("in build_generation", result.stderr)
            self.assertIn(
                (
                    "Generation directory must be an existing empty "
                    "canonical directory"
                ),
                result.stderr,
            )
            self.assertEqual([existing], list(output.iterdir()))
            self.assertEqual("existing generation", existing.read_text())

    def test_changed_source_does_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = generation_fixture(directory)
            task = (
                manifest.parent
                / binding["control_root"]
                / "__TKT"
                / "AN-T-1-task.md"
            )
            task.parent.mkdir()
            task.write_text(
                (
                    "---\nidentity:\n  atom_id: AN-T-1\ncontext:\n  "
                    "container:\n    component: C0\nstate:\n  status: "
                    "active\n  version: 1\n---\n\n## Summary\n\nTask\n"
                )
            )
            process = subprocess.Popen(
                [*WORKER, "--generation-dir", str(output)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            request = {
                "binding": binding,
                "reuse": None,
                "model_source": {"accepted_model": None},
            }
            process.stdin.write(json.dumps(request))
            process.stdin.close()
            process.stdin = None
            self._check_source_changes(process, output, task)
            self.assertEqual([], list(output.iterdir()))

    def _check_source_changes(self, process, output, task):
        stopped = None
        deadline = time.monotonic() + 10
        try:
            while time.monotonic() < deadline and process.poll() is None:
                if list(output.parent.glob(".beta-job-*")):
                    try:
                        os.kill(process.pid, signal.SIGSTOP)
                        stopped = process.pid
                    except ProcessLookupError:
                        pass
                    break
                time.sleep(0.001)
            self.assertIsNotNone(
                stopped, "Manifest build process was not observed"
            )
            content = task.read_bytes()
            task.write_bytes(content + b"changed\n")
            task.write_bytes(content)
            os.kill(stopped, signal.SIGCONT)
            stopped = None
            stdout, stderr = process.communicate(timeout=30)
            self.assertNotEqual(0, process.returncode, stdout + stderr)
            self.assertIn("Native Project carriers changed", stderr)
            self.assertNotIn("model_diagnostics", json.loads(stdout))
        finally:
            if stopped:
                os.kill(stopped, signal.SIGCONT)
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_graph_restart_exhaustion_reports_last_typed_difference(self):
        details = {
            "sources": {
                "change": "changed",
                "path": "main.py",
                "fields": ["status"],
            }
        }
        binding, output, _ = generation_fixture(
            self.enterContext(tempfile.TemporaryDirectory())
        )
        request = {"binding": binding, "reuse": None}
        response, _, scans = self._run_graph(
            request,
            output,
            self._graph_change("first.py"),
            self._graph_change("main.py"),
        )
        self.assertEqual(1, response.returncode, response.stderr)
        self.assertEqual(2, len(scans))
        reply = json.loads(response.stdout)
        self.assertEqual(details, reply["graph_consistency"])
        (issue,) = reply["ingestion_failure"]["issues"]
        self.assertEqual("realization_scan_failed", issue["code"])
        self.assertIn(
            (
                "Project source or dependency inputs changed during "
                "capture after one Realization Graph restart"
            ),
            issue["message"],
        )
        self.assertIn('"path":"first.py"', response.stderr)
        self.assertNotIn(
            "private raw child detail", response.stdout + response.stderr
        )

    @patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"})
    def test_deferred_core_and_graph_only(self):
        binding, output, _ = generation_fixture(
            self.enterContext(tempfile.TemporaryDirectory())
        )
        fingerprint = (
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61."
            "import_graph__shared.graph_input_signature"
        )
        request = {"binding": binding, "reuse": None, "defer_graph": True}
        with patch(fingerprint, side_effect=AssertionError("graph scanned")):
            response, _, scans = self._run_graph(request, output)
        self.assertEqual(0, response.returncode, response.stderr)
        result = json.loads(response.stdout)
        self.assertIsNone(result["graph"])
        self.assertEqual("pending", result["reuse"]["inputs"]["graph"])
        self.assertEqual([], scans)
        self.assertNotIn("realization_graph_ready", response.stderr)
        reuse = result["reuse"] | {"base_generation": "a" * 64}
        structure = json.loads((output / "structure.json").read_text())
        request = {
            "binding": binding,
            "reuse": reuse,
            "structure": structure,
            "graph_only": True,
            "watcher_guarded": True,
        }
        self._check_graph_only(request, fingerprint, output)

    def _check_force_graph(self, request, fingerprint, output):
        request["force_graph"] = True
        with patch(fingerprint, return_value="signature"):
            response, _, scans = self._run_graph(
                request,
                output,
                subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""),
            )
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual({"nodes": []}, json.loads(response.stdout)["graph"])
        self.assertEqual(1, len(scans))

    def _check_graph_only(self, request, fingerprint, output):
        with patch(fingerprint, return_value="signature"):
            response, _, scans = self._run_graph(
                request,
                output,
                subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""),
            )
            self.assertEqual(0, response.returncode, response.stderr)
            graph = json.loads(response.stdout)
            self.assertEqual({"nodes": []}, graph["graph"])
            self.assertEqual(1, len(scans))
            request["reuse"] = graph["reuse"] | {"base_generation": "a" * 64}
            response, _, scans = self._run_graph(request, output)
        self.assertEqual(
            {"base_generation": "a" * 64, "unchanged": True},
            json.loads(response.stdout),
        )
        self.assertIn(
            '"mode":"reused","phase":"realization_graph_ready"',
            response.stderr,
        )
        self.assertEqual([], scans)
        self._check_force_graph(request, fingerprint, output)


if __name__ == "__main__":
    unittest.main()
