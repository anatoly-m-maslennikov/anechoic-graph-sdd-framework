"""Shared in-process worker test support."""

import json
import subprocess
import sys
from unittest.mock import patch

from ..WORKERS_beta_C69__tests__shared import command_with_fixture


WORKER = [
    sys.executable,
    "-B",
    "-P",
    "-m",
    "WORKERS_beta_C69.WORKERS_beta_C69__shared",
]


class _WorkerFixture:
    @staticmethod
    def _graph_change(path):
        details = {
            "sources": {
                "change": "changed",
                "path": path,
                "fields": ["status"],
            }
        }
        diagnostic = {
            "code": "realization_graph_inputs_changed",
            "component": "C61",
            "severity": "ERROR",
            "details": details,
        }
        return subprocess.CompletedProcess(
            [], 1, "", "private raw child detail\n" + json.dumps(diagnostic)
        )

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
            response = command_with_fixture(
                WORKER[-1], request, "--generation-dir", str(output)
            )
        return response, invocations, graph_calls
