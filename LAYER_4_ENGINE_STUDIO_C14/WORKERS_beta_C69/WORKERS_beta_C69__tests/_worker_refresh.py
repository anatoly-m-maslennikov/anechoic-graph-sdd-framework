import json
import os
from hashlib import sha256
from pathlib import Path
import subprocess
import tempfile
import unittest

from .WORKERS_beta_C69__tests__shared import (
    generation_fixture,
)
from ._worker_context import WORKER, _WorkerFixture


class GenerationRefreshTests(_WorkerFixture, unittest.TestCase):
    def test_managed_refresh_reuses_artifacts_until_graph_inputs_change(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            root = Path(binding["root"])
            tickets = root / binding["control_root"] / "__TICKETS"
            tickets.mkdir()

            run = self._runner(binding)

            full = run(output, None)
            self.assertIsInstance(full["reuse"], dict)
            previous = {**full["reuse"], "base_generation": "a" * 64}
            (tickets / "AN-T-1-task.md").write_text(
                (
                    "---\nidentity: {atom_id: AN-T-1}\ncontext: "
                    "{container: {component: C00}}\nstate: {status: "
                    "active, version: 1}\n---\n\n## Summary\n\nNew "
                    "Ticket.\n"
                ),
                encoding="utf-8",
            )
            refreshed = output.with_name("refreshed")
            refreshed.mkdir()
            native = run(refreshed, previous)
            self.assertEqual(
                {
                    "base_generation",
                    "snapshot",
                    "snapshot_sha256",
                    "carrier_hashes",
                },
                set(native),
            )
            self.assertEqual("a" * 64, native["base_generation"])
            self.assertNotEqual(full["snapshot"], native["snapshot"])
            self.assertEqual([], list(refreshed.iterdir()))
            (root / "new_module.py").write_text(
                "value = 1\n", encoding="utf-8"
            )
            self._check_graph_refresh(run, output, refreshed, previous)
            self._check_rebuilt(run, refreshed, previous, full)

    def _check_graph_refresh(self, run, output, refreshed, previous):
        structure = json.loads((output / "structure.json").read_text())
        graph_refresh = run(refreshed, previous, structure)
        self.assertEqual(
            {
                "base_generation",
                "snapshot",
                "snapshot_sha256",
                "graph",
                "graph_sha256",
                "reuse",
                "carrier_hashes",
            },
            set(graph_refresh),
        )
        self.assertIsNotNone(graph_refresh["graph"])
        self.assertEqual(
            previous["inputs"]["manifest"],
            graph_refresh["reuse"]["inputs"]["manifest"],
        )
        self.assertNotEqual(
            previous["inputs"]["graph"],
            graph_refresh["reuse"]["inputs"]["graph"],
        )
        self.assertEqual(
            {"inputs", "graph_config", "endpoints"},
            set(graph_refresh["reuse"]),
        )
        self.assertEqual(
            graph_refresh,
            run(
                refreshed,
                previous,
                structure,
                foreground=True,
                incremental=True,
                watcher_guarded=True,
                replay_graph=True,
            ),
        )
        self.assertEqual([], list(refreshed.iterdir()))

    def _check_rebuilt(self, run, refreshed, previous, full):
        rebuilt = run(refreshed, previous)
        self.assertIn("receipt", rebuilt)
        self.assertIn("graph", rebuilt)
        self.assertNotEqual(
            full["reuse"]["inputs"], rebuilt["reuse"]["inputs"]
        )
        self.assertTrue((refreshed / "structure.json").is_file())

    def test_startup_hash_checkpoint_detects_ticket_edits_and_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            root = Path(binding["root"])
            ticket = (
                root / binding["control_root"] / "__TKT" / "AN-T-1-task.md"
            )
            ticket.parent.mkdir()
            ticket.write_text(
                (
                    "---\nidentity: {atom_id: AN-T-1}\ncontext: "
                    "{container: {component: C00}}\nstate: {status: "
                    "active, version: 1}\n---\n\n## Summary\n\nFirst.\n"
                )
            )

            run = self._ticket_runner(binding)

            full = run(output, None)
            previous = {
                **full["reuse"],
                "base_generation": "a" * 64,
                "carrier_hashes": full["carrier_hashes"],
            }
            refreshed = output.with_name("refreshed")
            refreshed.mkdir()
            self.assertEqual(
                {"base_generation": "a" * 64, "unchanged": True},
                run(refreshed, previous),
            )
            unknown = {
                **previous,
                "carrier_hashes": {
                    **previous["carrier_hashes"],
                    "outside.md": "0" * 64,
                },
            }
            self.assertIn("snapshot", run(refreshed, unknown))
            self._check_ticket_updates(ticket, root, refreshed, previous, run)

    def _check_ticket_updates(self, ticket, root, refreshed, previous, run):
        stat = ticket.stat()
        ticket.write_text(ticket.read_text().replace("First.", "Other."))
        os.utime(ticket, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        delta = run(refreshed, previous)
        relative = ticket.relative_to(root).as_posix()
        self.assertEqual(
            [[ticket.parent.relative_to(root).as_posix(), ticket.name]],
            delta["paths"],
        )
        self.assertEqual(
            sha256(ticket.read_bytes()).hexdigest(),
            delta["carrier_hashes"][relative],
        )
        ticket.unlink()
        deleted = run(refreshed, previous)
        self.assertEqual(delta["paths"], deleted["paths"])
        self.assertNotIn(relative, deleted["carrier_hashes"])
        self.assertEqual([], list(refreshed.iterdir()))

    def _runner(self, binding):
        def run(folder, reuse, structure=None, **options):
            request = {"binding": binding, "reuse": reuse, **options}
            if structure is not None:
                request["structure"] = structure
            result = subprocess.run(
                [*WORKER, "--generation-dir", str(folder)],
                capture_output=True,
                text=True,
                timeout=120,
                input=json.dumps(request),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return json.loads(result.stdout)

        return run

    def _ticket_runner(self, binding):
        def run(folder, reuse):
            result = subprocess.run(
                [*WORKER, "--generation-dir", str(folder)],
                capture_output=True,
                text=True,
                timeout=120,
                input=json.dumps({"binding": binding, "reuse": reuse}),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return json.loads(result.stdout)

        return run


if __name__ == "__main__":
    unittest.main()
