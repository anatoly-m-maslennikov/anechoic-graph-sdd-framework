"""Check archive consistency during foreground graph refresh."""

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ..WORKERS_beta_C69__tests__shared import command_with_fixture, generation_fixture
from .test_incremental_startup import WORKER, carrier


class ForegroundReplayGraphTest(unittest.TestCase):
    def _graph_fixture(self):
        directory = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding, output, _ = generation_fixture(directory)
        root = Path(binding["root"])
        archived = (
            root
            / binding["control_root"]
            / "__TICKETS"
            / "09_archived"
            / "AN-T-8@1-task.md"
        )
        archived.parent.mkdir(parents=True)
        archived.write_text(carrier(8, "archived"))
        full = command_with_fixture(
            WORKER,
            {"binding": binding, "reuse": None},
            "--generation-dir",
            str(output),
        )
        self.assertEqual(0, full.returncode, full.stderr)
        reuse = json.loads(full.stdout)["reuse"] | {
            "base_generation": "admitted"
        }
        structure = json.loads((output / "structure.json").read_text())
        (root / "source.py").write_text("VALUE = 1\n")
        output = directory / "refresh"
        output.mkdir()
        return binding, output, archived, reuse, structure

    def test_graph_refresh_checks_archives_outside_foreground_watcher(self):
        binding, output, archived, reuse, structure = self._graph_fixture()
        original = subprocess.run

        def graph_with_archive_edit(command, *args, **options):
            if "WORKERS_beta_C69.realization_graph" in command:
                archived.write_text(
                    carrier(8, "archived").replace(
                        "Ticket 8.", "Edited archive."
                    )
                )
            return original(command, *args, **options)

        request = {
            "binding": binding,
            "reuse": reuse,
            "foreground": True,
            "incremental": True,
            "watcher_guarded": True,
            "structure": structure,
        }
        with patch.object(
            subprocess, "run", side_effect=graph_with_archive_edit
        ):
            result = command_with_fixture(
                WORKER, request, "--generation-dir", str(output)
            )
        self.assertEqual(1, result.returncode, result.stdout)
        (issue,) = json.loads(result.stdout)["ingestion_failure"]["issues"]
        self.assertIn(
            "Native Project carriers changed during generation",
            issue["message"],
        )
        self.assertFalse(any(output.iterdir()))
