from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import time
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from .WORKERS_beta_C69__tests__shared import command_with_fixture, generation_fixture

WORKER = [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared"]


class WorkerTests(unittest.TestCase):
    def test_current_snapshot_and_changed_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, _, manifest = generation_fixture(directory)
            control = manifest.parent / binding["control_root"]
            def write(name, atom, status, version, summary):
                path = control / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"---\nidentity:\n  atom_id: {atom}\ncontext:\n  container:\n    component: C0\nstate:\n  status: {status}\n  version: {version}\n---\n\n## Summary\n\n{summary}\n")
                return path
            write("__TKT/AN-T-1-task.md", "AN-T-1", "active", 2, "Task")
            write("__TKT/AN-T-1@3-draft-task.md", "AN-T-1", "draft", 3, "Draft")
            def run():
                return subprocess.run(WORKER, input=json.dumps(binding),
                                      text=True, capture_output=True)
            result = run()
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual({"manifest_sha256": binding["manifest_sha256"], "atoms": [
                {"reference": "AN-S-1", "summary": "Anechoic"},
                {"reference": "AN-T-1", "summary": "Task"}]}, json.loads(result.stdout))
            manifest.write_text(manifest.read_text() + "changed\n")
            result = run()
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("", result.stdout)

class GenerationTests(unittest.TestCase):
    @staticmethod
    def _graph_change(path):
        details = {"sources": {"change": "changed", "path": path, "fields": ["status"]}}
        diagnostic = {"code": "realization_graph_inputs_changed", "component": "C61",
                      "severity": "ERROR", "details": details}
        return subprocess.CompletedProcess([], 1, "", "private raw child detail\n" + json.dumps(diagnostic))

    def _run_graph(self, request, output, *replies):
        original_run = subprocess.run
        invocations, graph_calls = [], []
        replies = iter(replies)

        def launch(command, *args, **options):
            if "-m" in command:
                module = command[command.index("-m") + 1]
                invocations.append(module)
                if module == "WORKERS_beta_C69.realization_graph":
                    graph_calls.append((command, json.loads(options["input"])))
                    return next(replies)
            return original_run(command, *args, **options)

        with patch.object(subprocess, "run", side_effect=launch):
            response = command_with_fixture(WORKER[-1], request, "--generation-dir", str(output))
        return response, invocations, graph_calls

    def test_graph_restart_reuses_compilation_and_native_capture(self):
        binding, output, _ = generation_fixture(self.enterContext(tempfile.TemporaryDirectory()))
        config = {"include": []}
        finish = Mock(return_value=({"atoms": []}, {}))
        success = subprocess.CompletedProcess([], 0, '{"nodes":[]}', "")
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.prepare_generation_snapshot",
                   return_value=(config, finish)) as prepare:
            response, modules, scans = self._run_graph(binding, output, self._graph_change("main.py"), success)
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual({"nodes": []}, json.loads(response.stdout)["graph"])
        self.assertEqual(2, len(scans))
        self.assertEqual(scans[0], scans[1])
        self.assertEqual(json.loads((output / "structure.json").read_text()), scans[0][1]["structure"])
        self.assertEqual(1, sum(name.endswith(".manifest_build_CS4__shared") for name in modules))
        prepare.assert_called_once()
        finish.assert_called_once_with(json.loads((output / "model.json").read_text())["bindings"]["endpoints"])
        self.assertIn('"path":"main.py"', response.stderr)
        self.assertNotIn("private raw child detail", response.stderr)

    def test_unrelated_graph_failure_is_not_restarted(self):
        child = subprocess.CompletedProcess([], 1, "", "unrelated failure")
        for attempts in ([child], [self._graph_change("main.py"), child]):
            with self.subTest(launches=len(attempts)), tempfile.TemporaryDirectory() as directory:
                binding, output, _ = generation_fixture(directory)
                request = {"binding": binding, "reuse": None}
                response, _, scans = self._run_graph(request, output, *attempts)
                self.assertEqual(1, response.returncode)
                issue, = json.loads(response.stdout)["ingestion_failure"]["issues"]
                self.assertIn("realization_graph failed: unrelated failure", issue["message"])
                self.assertEqual(len(attempts), len(scans))

    def test_managed_foreground_passes_replay_to_analyzer_and_retains_reuse_witness(self):
        binding, output, _ = generation_fixture(self.enterContext(tempfile.TemporaryDirectory()))
        archive = Path(binding["root"]) / binding["control_root"] / "09_archived"
        archive.mkdir()
        (archive / "AN-S-19@12--broken.md").write_bytes(b"\xff")
        request = {"binding": binding, "reuse": None, "replay_graph": True,
                   "watcher_guarded": True, "foreground": True}
        analyzer = "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared.graph_input_signature"
        with patch(analyzer, return_value="fixture-graph-signature") as fingerprint:
            response, _, scans = self._run_graph(request, output, subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""))
        self.assertEqual(0, response.returncode, response.stderr)
        command, _ = scans[0]
        self.assertEqual("--watcher-replay", command[-1])
        self.assertEqual(2, fingerprint.call_count)
        self.assertEqual({"AN-S-19": 12}, json.loads(response.stdout)["deferred_archive"]["archive_versions"])
        witness = json.loads(response.stdout)["reuse"]
        self.assertEqual({"manifest", "graph", "carrier_schema"}, set(witness["inputs"]))
        self.assertTrue(all(witness["inputs"].values()))

    @patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"})
    def test_deferred_core_and_graph_only(self):
        binding, output, _ = generation_fixture(self.enterContext(tempfile.TemporaryDirectory()))
        fingerprint = "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared.graph_input_signature"
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
        request = {"binding": binding, "reuse": reuse, "structure": structure, "graph_only": True, "watcher_guarded": True}
        with patch(fingerprint, return_value="signature"):
            response, _, scans = self._run_graph(request, output, subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""))
            self.assertEqual(0, response.returncode, response.stderr)
            graph = json.loads(response.stdout)
            self.assertEqual({"nodes": []}, graph["graph"])
            self.assertEqual(1, len(scans))
            request["reuse"] = graph["reuse"] | {"base_generation": "a" * 64}
            response, _, scans = self._run_graph(request, output)
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, json.loads(response.stdout))
        self.assertIn('"mode":"reused","phase":"realization_graph_ready"', response.stderr)
        self.assertEqual([], scans)
        request["force_graph"] = True
        with patch(fingerprint, return_value="signature"):
            response, _, scans = self._run_graph(request, output, subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""))
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual({"nodes": []}, json.loads(response.stdout)["graph"])
        self.assertEqual(1, len(scans))

    def test_graph_restart_exhaustion_reports_last_typed_difference(self):
        details = {"sources": {"change": "changed", "path": "main.py", "fields": ["status"]}}
        binding, output, _ = generation_fixture(self.enterContext(tempfile.TemporaryDirectory()))
        request = {"binding": binding, "reuse": None}
        response, _, scans = self._run_graph(request, output, self._graph_change("first.py"), self._graph_change("main.py"))
        self.assertEqual(1, response.returncode, response.stderr)
        self.assertEqual(2, len(scans))
        reply = json.loads(response.stdout)
        self.assertEqual(details, reply["graph_consistency"])
        issue, = reply["ingestion_failure"]["issues"]
        self.assertEqual("realization_scan_failed", issue["code"])
        self.assertIn("Project source or dependency inputs changed during capture after one Realization Graph restart",
                      issue["message"])
        self.assertIn('"path":"first.py"', response.stderr)
        self.assertNotIn("private raw child detail", response.stdout + response.stderr)

    def test_managed_refresh_reuses_artifacts_until_graph_inputs_change(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            root = Path(binding["root"])
            tickets = root / binding["control_root"] / "__TICKETS"
            tickets.mkdir()
            def run(folder, reuse, structure=None, **options):
                request = {"binding": binding, "reuse": reuse, **options}
                if structure is not None:
                    request["structure"] = structure
                result = subprocess.run([*WORKER, "--generation-dir", str(folder)], capture_output=True,
                                        text=True, timeout=120, input=json.dumps(request))
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            full = run(output, None)
            self.assertIsInstance(full["reuse"], dict)
            previous = {**full["reuse"], "base_generation": "a" * 64}
            (tickets / "AN-T-1-task.md").write_text(
                "---\nidentity: {atom_id: AN-T-1}\ncontext: {container: {component: C00}}\n"
                "state: {status: active, version: 1}\n---\n\n## Summary\n\nNew Ticket.\n",
                encoding="utf-8",
            )
            refreshed = output.with_name("refreshed")
            refreshed.mkdir()
            native = run(refreshed, previous)
            self.assertEqual({"base_generation", "snapshot", "snapshot_sha256", "carrier_hashes"}, set(native))
            self.assertEqual("a" * 64, native["base_generation"])
            self.assertNotEqual(full["snapshot"], native["snapshot"])
            self.assertEqual([], list(refreshed.iterdir()))
            (root / "new_module.py").write_text("value = 1\n", encoding="utf-8")
            structure = json.loads((output / "structure.json").read_text())
            graph_refresh = run(refreshed, previous, structure)
            self.assertEqual({"base_generation", "snapshot", "snapshot_sha256", "graph", "graph_sha256", "reuse", "carrier_hashes"}, set(graph_refresh))
            self.assertIsNotNone(graph_refresh["graph"])
            self.assertEqual(previous["inputs"]["manifest"], graph_refresh["reuse"]["inputs"]["manifest"])
            self.assertNotEqual(previous["inputs"]["graph"], graph_refresh["reuse"]["inputs"]["graph"])
            self.assertEqual({"inputs", "graph_config", "endpoints"}, set(graph_refresh["reuse"]))
            self.assertEqual(graph_refresh, run(refreshed, previous, structure, foreground=True, incremental=True,
                                                watcher_guarded=True, replay_graph=True))
            self.assertEqual([], list(refreshed.iterdir()))
            rebuilt = run(refreshed, previous)
            self.assertIn("receipt", rebuilt)
            self.assertIn("graph", rebuilt)
            self.assertNotEqual(full["reuse"]["inputs"], rebuilt["reuse"]["inputs"])
            self.assertTrue((refreshed / "structure.json").is_file())

    def test_startup_hash_checkpoint_detects_ticket_edits_and_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            root = Path(binding["root"])
            ticket = root / binding["control_root"] / "__TKT" / "AN-T-1-task.md"
            ticket.parent.mkdir()
            ticket.write_text("---\nidentity: {atom_id: AN-T-1}\ncontext: {container: {component: C00}}\n"
                              "state: {status: active, version: 1}\n---\n\n## Summary\n\nFirst.\n")
            def run(folder, reuse):
                result = subprocess.run([*WORKER, "--generation-dir", str(folder)], capture_output=True,
                                        text=True, timeout=120, input=json.dumps({"binding": binding, "reuse": reuse}))
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            full = run(output, None)
            previous = {**full["reuse"], "base_generation": "a" * 64, "carrier_hashes": full["carrier_hashes"]}
            refreshed = output.with_name("refreshed")
            refreshed.mkdir()
            self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, run(refreshed, previous))
            unknown = {**previous, "carrier_hashes": {**previous["carrier_hashes"], "outside.md": "0" * 64}}
            self.assertIn("snapshot", run(refreshed, unknown))
            stat = ticket.stat()
            ticket.write_text(ticket.read_text().replace("First.", "Other."))
            os.utime(ticket, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            delta = run(refreshed, previous)
            relative = ticket.relative_to(root).as_posix()
            self.assertEqual([[ticket.parent.relative_to(root).as_posix(), ticket.name]], delta["paths"])
            self.assertEqual(sha256(ticket.read_bytes()).hexdigest(), delta["carrier_hashes"][relative])
            ticket.unlink()
            deleted = run(refreshed, previous)
            self.assertEqual(delta["paths"], deleted["paths"])
            self.assertNotIn(relative, deleted["carrier_hashes"])
            self.assertEqual([], list(refreshed.iterdir()))

    def test_real_cli_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            result = subprocess.run([*WORKER, '--generation-dir', str(output)],
                                    input=json.dumps(binding), text=True, capture_output=True, timeout=120)
            self.assertEqual(0, result.returncode, result.stderr)
            response = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], response['snapshot']['manifest_sha256'])
            self.assertEqual(binding['manifest_sha256'], response['receipt']['manifest_sha256'])
            for name, key in [('structure.json', 'structure_sha256'), ('model.json', 'model_descriptor_sha256')]:
                self.assertEqual(response['receipt'][key], sha256((output / name).read_bytes()).hexdigest())

    def test_rejects_nonempty_generation_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            existing = output / 'structure.json'
            existing.write_text('existing generation')
            result = subprocess.run([*WORKER, '--generation-dir', str(output)],
                                    input=json.dumps(binding), text=True, capture_output=True, timeout=120)
            self.assertEqual(1, result.returncode)
            self.assertEqual('', result.stdout)
            self.assertIn('Traceback (most recent call last)', result.stderr)
            self.assertIn('in build_generation', result.stderr)
            self.assertIn('Generation directory must be an existing empty canonical directory', result.stderr)
            self.assertEqual([existing], list(output.iterdir()))
            self.assertEqual('existing generation', existing.read_text())

    def test_changed_source_does_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = generation_fixture(directory)
            task = manifest.parent / binding['control_root'] / '__TKT' / 'AN-T-1-task.md'
            task.parent.mkdir()
            task.write_text('---\nidentity:\n  atom_id: AN-T-1\ncontext:\n  container:\n    component: C0\nstate:\n  status: active\n  version: 1\n---\n\n## Summary\n\nTask\n')
            process = subprocess.Popen([*WORKER, '--generation-dir', str(output)],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            request = {"binding": binding, "reuse": None, "model_source": {"accepted_model": None}}
            process.stdin.write(json.dumps(request))
            process.stdin.close()
            process.stdin = None
            stopped = None
            deadline = time.monotonic() + 10
            try:
                while time.monotonic() < deadline and process.poll() is None:
                    if list(output.parent.glob('.beta-job-*')):
                        try:
                            os.kill(process.pid, signal.SIGSTOP)
                            stopped = process.pid
                        except ProcessLookupError:
                            pass
                        break
                    time.sleep(0.001)
                self.assertIsNotNone(stopped, 'Manifest build process was not observed')
                content = task.read_bytes()
                task.write_bytes(content + b'changed\n')
                task.write_bytes(content)
                os.kill(stopped, signal.SIGCONT)
                stopped = None
                stdout, stderr = process.communicate(timeout=30)
                self.assertNotEqual(0, process.returncode, stdout + stderr)
                self.assertIn('Native Project carriers changed', stderr)
                self.assertNotIn("model_diagnostics", json.loads(stdout))
            finally:
                if stopped:
                    os.kill(stopped, signal.SIGCONT)
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual([], list(output.iterdir()))


if __name__ == "__main__":
    unittest.main()
