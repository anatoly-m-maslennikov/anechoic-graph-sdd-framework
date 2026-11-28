from hashlib import sha256 as sha256
import json
import os as os
from pathlib import Path
import signal as signal
import time as time
import subprocess
import sys as sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from ._worker_context import WORKER as WORKER, _WorkerFixture as _WorkerFixture
from ..WORKERS_beta_C69__tests__shared import (
    command_with_fixture as command_with_fixture,
    generation_fixture,
)


class WorkerTests(unittest.TestCase):
    def test_current_snapshot_and_changed_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, _, manifest = generation_fixture(directory)
            control = manifest.parent / binding["control_root"]

            def write(name, atom, status, version, summary):
                path = control / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    f"---\nidentity:\n  atom_id: {atom}\n"
                    "context:\n  container:\n    component: C0\n"
                    f"state:\n  status: {status}\n  version: {version}\n"
                    f"---\n\n## Summary\n\n{summary}\n"
                )
                return path

            write("__TKT/AN-T-1-task.md", "AN-T-1", "active", 2, "Task")
            write(
                "__TKT/AN-T-1@3-draft-task.md", "AN-T-1", "draft", 3, "Draft"
            )

            def run():
                return subprocess.run(
                    WORKER,
                    input=json.dumps(binding),
                    text=True,
                    capture_output=True,
                )

            result = run()
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                {
                    "manifest_sha256": binding["manifest_sha256"],
                    "atoms": [
                        {"reference": "AN-S-1", "summary": "Anechoic"},
                        {"reference": "AN-T-1", "summary": "Task"},
                    ],
                },
                json.loads(result.stdout),
            )
            manifest.write_text(manifest.read_text() + "changed\n")
            result = run()
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("", result.stdout)


class GenerationTests(_WorkerFixture, unittest.TestCase):
    def test_graph_restart_reuses_compilation_and_native_capture(self):
        binding, output, _ = generation_fixture(
            self.enterContext(tempfile.TemporaryDirectory())
        )
        config = {"include": []}
        finish = Mock(return_value=({"atoms": []}, {}))
        success = subprocess.CompletedProcess([], 0, '{"nodes":[]}', "")
        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPT"
                "ERS_C30__shared.prepare_generation_snapshot"
            ),
            return_value=(config, finish),
        ) as prepare:
            response, modules, scans = self._run_graph(
                binding, output, self._graph_change("main.py"), success
            )
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual({"nodes": []}, json.loads(response.stdout)["graph"])
        self.assertEqual(2, len(scans))
        self.assertEqual(scans[0], scans[1])
        self.assertEqual(
            json.loads((output / "structure.json").read_text()),
            scans[0][1]["structure"],
        )
        self.assertEqual(
            1,
            sum(
                name.endswith(".manifest_build_CS4__shared")
                for name in modules
            ),
        )
        prepare.assert_called_once()
        bindings = json.loads((output / "model.json").read_text())["bindings"]
        finish.assert_called_once()
        endpoints, domains = finish.call_args.args
        self.assertFalse(finish.call_args.kwargs)
        self.assertEqual(bindings["endpoints"], endpoints)
        self.assertEqual(set(domains), {"S", "T", "P", "C"})
        self.assertIn('"path":"main.py"', response.stderr)
        self.assertNotIn("private raw child detail", response.stderr)

    def test_unrelated_graph_failure_is_not_restarted(self):
        child = subprocess.CompletedProcess([], 1, "", "unrelated failure")
        for attempts in ([child], [self._graph_change("main.py"), child]):
            with (
                self.subTest(launches=len(attempts)),
                tempfile.TemporaryDirectory() as directory,
            ):
                binding, output, _ = generation_fixture(directory)
                request = {"binding": binding, "reuse": None}
                response, _, scans = self._run_graph(
                    request, output, *attempts
                )
                self.assertEqual(1, response.returncode)
                (issue,) = json.loads(response.stdout)["ingestion_failure"][
                    "issues"
                ]
                self.assertIn(
                    "realization_graph failed: unrelated failure",
                    issue["message"],
                )
                self.assertEqual(len(attempts), len(scans))

    def _managed_foreground_preserves_reuse_witness(
        self,
    ):
        binding, output, _ = generation_fixture(
            self.enterContext(tempfile.TemporaryDirectory())
        )
        archive = (
            Path(binding["root"]) / binding["control_root"] / "09_archived"
        )
        archive.mkdir()
        (archive / "AN-S-19@12--broken.md").write_bytes(b"\xff")
        request = {
            "binding": binding,
            "reuse": None,
            "replay_graph": True,
            "watcher_guarded": True,
            "foreground": True,
        }
        analyzer = (
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61."
            "import_graph__shared.graph_input_signature"
        )
        with patch(
            analyzer, return_value="fixture-graph-signature"
        ) as fingerprint:
            response, _, scans = self._run_graph(
                request,
                output,
                subprocess.CompletedProcess([], 0, '{"nodes":[]}', ""),
            )
        self.assertEqual(0, response.returncode, response.stderr)
        command, _ = scans[0]
        self.assertEqual("--watcher-replay", command[-1])
        self.assertEqual(2, fingerprint.call_count)
        self.assertEqual(
            {"AN-S-19": 12},
            json.loads(response.stdout)["deferred_archive"][
                "archive_versions"
            ],
        )
        witness = json.loads(response.stdout)["reuse"]
        self.assertEqual(
            {"manifest", "graph", "carrier_schema"}, set(witness["inputs"])
        )
        self.assertTrue(all(witness["inputs"].values()))


setattr(
    GenerationTests,
    "test_managed_foreground_passes_replay_to"
    "_analyzer_and_retains_reuse_witness",
    GenerationTests._managed_foreground_preserves_reuse_witness,
)


def _register_split_tests():
    from . import _worker_generation, _worker_refresh

    for cls in (
        _worker_generation.GenerationProcessTests,
        _worker_refresh.GenerationRefreshTests,
    ):
        for name, method in vars(cls).items():
            if name.startswith(("test_", "_check_")) or name in (
                "_runner",
                "_ticket_runner",
            ):
                setattr(GenerationTests, name, method)


_register_split_tests()


if __name__ == "__main__":
    unittest.main()
