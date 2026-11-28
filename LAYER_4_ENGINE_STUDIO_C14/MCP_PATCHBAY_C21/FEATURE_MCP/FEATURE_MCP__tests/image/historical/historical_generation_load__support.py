"Measure public queries during candidate Archive work and Ticket ingestion."

from concurrent.futures import ThreadPoolExecutor as ThreadPoolExecutor
import json
from math import ceil
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic, time_ns
import unittest

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    workbench.group_4.workbench_docker_support import (
    image_timeout,
    request,
)
from ..staged_startup__support import PackagedProbe, carrier, prepare
from ._historical_generation_load_actions import GenerationLoadActions


QUERY_TRIALS = 12
BATCH_START, BATCH_SIZE = 20000, 500
EXTRA_ARCHIVES = 4500
WORKLOAD_SQL = """SELECT reference, "content.summary" FROM mrt_atoms
    WHERE reference IN ('AN-T-2', 'AN-T-3', 'AN-T-4') ORDER BY reference"""
WORKLOAD_ROWS = [
    [f"AN-T-{number}", f"Current {number}"] for number in (2, 3, 4)
]
BATCH_SQL = f"""WITH expected AS (SELECT range AS number FROM range({BATCH_START}, {BATCH_START + BATCH_SIZE}))
    SELECT count(DISTINCT reference) FROM mrt_ticket_atoms
    JOIN expected ON reference = 'AN-T-' || number::VARCHAR
    WHERE "header.state.status" = 'active' AND "content.summary" = 'Batch ' || number::VARCHAR"""
SINGLE_SQL = (
    'SELECT "header.state.status", "content.summary" FROM mrt_ticket_atoms '
    "WHERE reference = 'AN-T-1'"
)
ARCHIVE_STATE = """
from pathlib import Path
import sys
try:
    status = Path(f'/proc/{int(sys.argv[1])}/status').read_text()
except FileNotFoundError:
    print('gone')
else:
    print(next(line.split()[1] for line in status.splitlines() if line.startswith('State:')))
"""


def summarize_queries(times, errors):
    ordered = sorted(times)
    return {
        "sample_count": len(times) + len(errors),
        "success_count": len(times),
        "error_count": len(errors),
        "p95_ms": round(ordered[ceil(0.95 * len(ordered)) - 1], 3)
        if ordered
        else None,
        "errors": errors,
    }


def public_query(probe, sql):
    return request(
        probe.url + "/anechoic/Anechoic/api/run",
        method="POST",
        payload={"sql": sql, "result_delivery": "inline"},
    )


def rows(probe, sql):
    status, payload = public_query(probe, sql)
    if (
        status != 200
        or not isinstance(payload, dict)
        or not isinstance(payload.get("rows"), list)
    ):
        raise AssertionError(f"Public query failed: {status} {payload!r}")
    return payload["rows"]


def public_ready(probe):
    status, payload = request(probe.url + "/anechoic/health")
    return (
        status == 200
        and isinstance(payload, dict)
        and payload.get("state") == "ready"
    )


def sample_queries(probe):
    samples, errors = [], []
    started = monotonic()
    for _ in range(QUERY_TRIALS):
        beginning = monotonic()
        try:
            answer = rows(probe, WORKLOAD_SQL)
        except (AssertionError, OSError, ValueError) as error:
            errors.append(str(error)[:256])
        else:
            if answer == WORKLOAD_ROWS:
                samples.append((monotonic() - beginning) * 1000)
            else:
                errors.append("The query returned unexpected seed Ticket rows")
    finished = monotonic()
    result = summarize_queries(samples, errors)
    return result | {"duration_seconds": finished - started}, started, finished


def prepare_load(root):
    directory = prepare(root)
    archive = directory / "09_archived"
    for number in range(30000, 30000 + EXTRA_ARCHIVES):
        path = archive / f"AN-T-{number}@1-TASK--load-history.md"
        path.write_text(carrier(number, "archived", "Load history"))
    return directory, len(list(archive.glob("*.md")))


def write_ticket(directory, number):
    path = directory / f"AN-T-{number}-TASK--load.md"
    path.write_text(carrier(number, "active", f"Batch {number}"))


def write_batch(directory):
    for number in range(BATCH_START + 1, BATCH_START + BATCH_SIZE):
        write_ticket(directory, number)
    return monotonic()


def capture_workers(jobs):
    return sum(
        (jobs.get(lane) or {}).get("worker_alive") is True
        for lane in ("active", "archive")
    )


def archive_running(state):
    return state in {"R", "S", "D", "I"}


def clock_offset(probe):
    before = time_ns()
    candidate = int(probe.exec("from time import time_ns; print(time_ns())"))
    return candidate - time_ns(), candidate - before


def watcher_detection_bounds(at, offsets, write_start, write_end):
    low, high = zip(*offsets, strict=True)
    if at is None or write_end < write_start or max(low) > min(high):
        return None
    detected = round(at * 1_000_000_000)
    return {
        "candidate_minus_host_ns_bounds": [min(low), max(high)],
        "write_start_to_watcher_ms_bounds": [
            (detected - write_start - offset) / 1_000_000
            for offset in (max(high), min(low))
        ],
        "write_end_to_watcher_ms_bounds": [
            (detected - write_end - offset) / 1_000_000
            for offset in (max(high), min(low))
        ],
    }


class GenerationLoadDockerTests(GenerationLoadActions, unittest.TestCase):
    def _image_runtime(self):
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
            value.split("=", 1)[1]
            for value in json.loads(environment)
            if value.startswith("ANECHOIC_RUNTIME_STACK=")
        ]
        if not modes or modes[-1] not in ("beta", "beta_next"):
            self.skipTest("Generation load applies to the Beta runtime")
        return image, modes[-1]

    def test_generation_load_and_public_readback(self):
        image, runtime = self._image_runtime()
        temporary = self.enterContext(
            TemporaryDirectory(prefix="anechoic-load-image-")
        )
        root = Path(temporary).resolve()
        subprocess.run(
            ["git", "init", "--quiet", str(root)],
            check=True,
            timeout=image_timeout(10),
        )
        directory, archive_count = prepare_load(root)
        probe = PackagedProbe(self, root, image)
        try:
            report = self.exercise(probe, directory, archive_count)
        except BaseException:
            print(
                probe.docker("logs", probe.container, timeout=30)[-12000:],
                flush=True,
            )
            raise
        report.update(
            image=image,
            runtime=runtime,
            workload_sql=WORKLOAD_SQL,
            query_concurrency=1,
            duration_seconds=monotonic() - probe.started,
            resource_limits={"cpus": 1, "pids": 128, "tmpfs_mib": 256},
        )
        print(
            "ANECHOIC_TEST_METRICS " + json.dumps({"generation_load": report}),
            flush=True,
        )
        for phase in ("idle", "archive_active", "batch"):
            self.assertEqual(
                0, report[phase]["queries"]["error_count"], report[phase]
            )
            self.assertEqual(
                QUERY_TRIALS,
                report[phase]["queries"]["success_count"],
                report[phase],
            )
