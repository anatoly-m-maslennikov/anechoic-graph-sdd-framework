"""Verify staged startup and persisted offline reconciliation in the candidate image."""

import asyncio as asyncio
import json
import os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic as monotonic
import unittest

from mcp.client.session import ClientSession as ClientSession

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    workbench.group_4.workbench_docker_support import (
    image_mcp_transport as image_mcp_transport,
    image_timeout,
    request,
)
from ._historical_staged_startup_actions import StagedStartupActions
from ._historical_staged_restart_actions import StagedRestartActions
from ..staged_startup__support import (
    PackagedProbe,
    canonical_carrier,
    cold_throughput as cold_throughput,
    prepare,
)


def query(ref):
    return (
        'SELECT relative_path, filename, "content.summary" FROM atoms '
        f"WHERE reference='{ref}'"
    )


def status_counts(probe):
    return dict(
        probe.rows("SELECT status_group, count(*) FROM atoms GROUP BY 1")
    )


def public_ready(probe):
    status, payload = request(probe.url + "/anechoic/health")
    return (
        status == 200
        and isinstance(payload, dict)
        and payload.get("state") == "ready"
    )


def paths(directory):
    return [directory / f"AN-T-{i}-TASK--staged.md" for i in range(1, 5)]


class PackagedStagedStartupTests(
    StagedStartupActions, StagedRestartActions, unittest.TestCase
):
    def test_staged_startup_and_disk_restart(self):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(image, r"\Asha256:[0-9a-f]{64}\Z")
        environment = subprocess.check_output(
            [
                "docker",
                "image",
                "inspect",
                "--format",
                "{{json .Config.Env}}",
                image,
            ],
            text=True,
            timeout=image_timeout(10),
        )
        modes = [
            item.split("=", 1)[1]
            for item in json.loads(environment)
            if item.startswith("ANECHOIC_RUNTIME_STACK=")
        ]
        if not modes or modes[-1] not in ("beta", "beta_next"):
            self.skipTest("Staged startup applies to the Beta runtime")
        temp = self.enterContext(
            tempfile.TemporaryDirectory(prefix="anechoic-staged-image-")
        )
        root = Path(temp).resolve()
        subprocess.run(
            ["git", "init", "--quiet", str(root)],
            check=True,
            timeout=image_timeout(10),
        )
        directory = prepare(root, write_carrier=canonical_carrier)
        self.assertFalse((root / ".anechoic_runtime").exists())
        probe = PackagedProbe(self, root, image)
        try:
            self._exercise(probe, directory, image, modes[-1])
        except BaseException:
            logs = probe.docker("logs", probe.container, timeout=30)
            print(logs[-12000:], flush=True)
            raise

    def _record_timing(
        self, probe, phase, metrics, required, *, changed_paths=None
    ):
        if required:
            probe.until(
                lambda: (
                    "realization_graph_ready"
                    not in probe.timing(phase)["unobserved"]
                ),
                phase + " Realization Graph timing",
            )
        timing = (
            probe.assert_timing(phase) if required else probe.timing(phase)
        )
        metrics["startup_timing"][phase] = timing
        observed = [
            event["changed_paths"]
            for event in timing["events"]
            if event["phase"] == "non_archived_load_started"
            and "changed_paths" in event
        ]
        metrics["startup_outcomes"][phase]["scan_reported_changed_paths"] = (
            observed
        )
        if required and changed_paths is not None:
            self.assertEqual([changed_paths], observed)
        prefix = "restored" if phase == "restart" else phase
        probe.phase(
            phase + "_verified",
            docker_started_at=timing["started_at"],
            changed_paths=observed,
            ready_seconds=metrics[prefix + "_ready_seconds"],
            first_query_seconds=metrics[prefix + "_first_query_seconds"],
        )
        return timing
