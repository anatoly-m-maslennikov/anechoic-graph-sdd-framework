"""Measure public queries during candidate Archive work and Ticket ingestion."""

from concurrent.futures import ThreadPoolExecutor
import json
from math import ceil
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic, time_ns
import unittest

from ..FEATURE_MCP__tests__shared import image_timeout, request
from .staged_startup__support import PackagedProbe, carrier, prepare


QUERY_TRIALS = 12
BATCH_START, BATCH_SIZE = 20000, 500
EXTRA_ARCHIVES = 4500
WORKLOAD_SQL = """SELECT reference, "content.summary" FROM mrt_atoms
    WHERE reference IN ('AN-T-2', 'AN-T-3', 'AN-T-4') ORDER BY reference"""
WORKLOAD_ROWS = [[f"AN-T-{number}", f"Current {number}"] for number in (2, 3, 4)]
BATCH_SQL = f"""WITH expected AS (SELECT range AS number FROM range({BATCH_START}, {BATCH_START + BATCH_SIZE}))
    SELECT count(DISTINCT reference) FROM mrt_ticket_atoms
    JOIN expected ON reference = 'AN-T-' || number::VARCHAR
    WHERE "header.state.status" = 'active' AND "content.summary" = 'Batch ' || number::VARCHAR"""
SINGLE_SQL = """SELECT "header.state.status", "content.summary" FROM mrt_ticket_atoms WHERE reference = 'AN-T-1'"""
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
    return {"sample_count": len(times) + len(errors), "success_count": len(times), "error_count": len(errors),
            "p95_ms": round(ordered[ceil(.95 * len(ordered)) - 1], 3) if ordered else None,
            "errors": errors}


def public_query(probe, sql):
    return request(probe.url + "/anechoic/Anechoic/api/run", method="POST",
                   payload={"sql": sql, "result_delivery": "inline"})


def rows(probe, sql):
    status, payload = public_query(probe, sql)
    if status != 200 or not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise AssertionError(f"Public query failed: {status} {payload!r}")
    return payload["rows"]


def public_ready(probe):
    status, payload = request(probe.url + "/anechoic/health")
    return status == 200 and isinstance(payload, dict) and payload.get("state") == "ready"


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
    return sum((jobs.get(lane) or {}).get("worker_alive") is True for lane in ("active", "archive"))


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
    return {"candidate_minus_host_ns_bounds": [min(low), max(high)],
            "write_start_to_watcher_ms_bounds": [(detected - write_start - offset) / 1_000_000
                                                 for offset in (max(high), min(low))],
            "write_end_to_watcher_ms_bounds": [(detected - write_end - offset) / 1_000_000
                                               for offset in (max(high), min(low))]}


class GenerationLoadDockerTests(unittest.TestCase):
    def test_generation_load_and_public_readback(self):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(image, r"\Asha256:[0-9a-f]{64}\Z")
        environment = subprocess.check_output(
            ["docker", "image", "inspect", "--format", "{{json .Config.Env}}", image],
            text=True, timeout=image_timeout(10),
        )
        modes = [value.split("=", 1)[1] for value in json.loads(environment)
                 if value.startswith("ANECHOIC_RUNTIME_STACK=")]
        if not modes or modes[-1] not in ("beta", "beta_next"):
            self.skipTest("Generation load applies to the Beta runtime")
        temporary = self.enterContext(TemporaryDirectory(prefix="anechoic-load-image-"))
        root = Path(temporary).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True, timeout=image_timeout(10))
        directory, archive_count = prepare_load(root)
        probe = PackagedProbe(self, root, image)
        try:
            report = self.exercise(probe, directory, archive_count)
        except BaseException:
            print(probe.docker("logs", probe.container, timeout=30)[-12000:], flush=True)
            raise
        report.update(image=image, runtime=modes[-1], workload_sql=WORKLOAD_SQL, query_concurrency=1,
                      duration_seconds=monotonic() - probe.started,
                      resource_limits={"cpus": 1, "pids": 128, "tmpfs_mib": 256})
        print("ANECHOIC_TEST_METRICS " + json.dumps({"generation_load": report}), flush=True)
        for phase in ("idle", "archive_active", "batch"):
            self.assertEqual(0, report[phase]["queries"]["error_count"], report[phase])
            self.assertEqual(QUERY_TRIALS, report[phase]["queries"]["success_count"], report[phase])

    def exercise(self, probe, directory, archive_count):
        pid = probe.until(probe.stopped, "Archive Worker barrier")
        health, _ = probe.until(probe.ready, "foreground readiness")
        self.assertTrue(health["archive_pending"])
        probe.until(lambda: public_ready(probe), "public readiness")
        self.assertEqual(WORKLOAD_ROWS, rows(probe, WORKLOAD_SQL))
        idle, _, _ = sample_queries(probe)
        resources = {"idle_end": probe.resources()}
        archive = self.archive_queries(probe, pid, archive_count)
        probe.until(probe.complete, "Archive publication")
        resources["archive_publication"] = probe.resources()
        self.assertEqual([[archive_count]], rows(probe, "SELECT count(*) FROM mrt_ticket_atoms WHERE status_group='Archived'"))
        single = self.single_update(probe, directory)
        batch = self.ingest_batch(probe, directory)
        resources["batch_publication"] = probe.resources()
        return {"idle": {"queries": idle, "archive_intentionally_paused": True},
                "archive_active": archive, "single_update": single, "batch": batch, "resources": resources}

    def archive_queries(self, probe, pid, archive_count):
        self.assertIn(probe.exec(ARCHIVE_STATE, pid), {"T", "t"})
        probe.release()
        state_before = probe.exec(ARCHIVE_STATE, pid)
        self.assertTrue(archive_running(state_before), f"Archive Worker was not active: {state_before}")
        queries, _, _ = sample_queries(probe)
        state_after = probe.exec(ARCHIVE_STATE, pid)
        self.assertTrue(archive_running(state_after), f"Archive Worker did not span the query workload: {state_after}")
        return {"queries": queries, "archive_tickets": archive_count, "worker_pid": int(pid),
                "state_before": state_before, "state_after": state_after, "paused_during_queries": False}

    def single_update(self, probe, directory):
        before = probe.jobs()["latest"]["run_id"]
        self.assertEqual([["active", "Current 1"]], rows(probe, SINGLE_SQL))
        clock_before = clock_offset(probe)
        started = monotonic()
        write_start = time_ns()
        (directory / "AN-T-1-TASK--staged.md").write_text(carrier(1, "active", "Measured live edit"))
        write_end = time_ns()
        written = monotonic()
        visible = probe.until(lambda: monotonic() if rows(probe, SINGLE_SQL) == [["active", "Measured live edit"]]
                              else None, "single Ticket edit publication")
        job = probe.until(lambda: self.changed_run(probe, before), "single edit Worker result")
        run_id = job["run_id"]
        self.assertRegex(run_id, r"\A[0-9a-f]{32}\Z")
        flow = probe.until(lambda: self.generation_flow(probe, job), "single edit Flow publication")
        bounds = watcher_detection_bounds(flow["watcher_observed_at"], (clock_before, clock_offset(probe)),
                                          write_start, write_end)
        return {"write_seconds": written - started, "write_start_to_correct_sql_seconds": visible - started,
                "write_end_to_correct_sql_seconds": visible - written,
                "worker_seconds": job["worker_seconds"], "admission_seconds": job["admission_seconds"],
                "run_id": run_id, "generation": job["generation"], "generation_kind": job["kind"],
                "watcher_detection_clock_bounds": bounds, **flow}

    def changed_run(self, probe, before):
        latest = probe.jobs().get("latest") or {}
        if latest.get("run_id") == before:
            return None
        if latest.get("state") in ("failed", "aborted") and not latest.get("retrying"):
            self.fail(f"Single Ticket edit failed: {latest}")
        return latest if latest.get("state") == "succeeded" else None

    def generation_flow(self, probe, job):
        run_id = job["run_id"]
        sql = f"""SELECT sequence, kind, name, "at", CAST(detail AS VARCHAR), outcome, causes FROM src_flow_events
            WHERE component='C68' AND run_id='{run_id}' ORDER BY sequence"""
        events = rows(probe, sql)
        observed = {seq: at for seq, kind, name, at, detail, _, _ in events
                    if kind == "input" and name == "file_change" and json.loads(detail).get("timestamp_source") == "watcher"}
        triggers = [(at, causes) for _, kind, name, at, _, _, causes in events
                    if kind == "trigger" and name == "file_change"]
        outputs = [at for _, kind, name, at, detail, outcome, _ in events
                   if kind == "output" and name == "generation_result" and outcome == "succeeded"
                   and json.loads(detail).get("generation") == job["generation"]]
        if not (triggers and outputs):
            return None
        dispatched, causes = triggers[0]
        watcher = min((observed[seq] for seq in causes if seq in observed), default=None)
        return {"watcher_observed_at": watcher, "flow_dispatch_at": dispatched, "flow_result_at": outputs[-1],
                "watcher_queue_to_dispatch_seconds": dispatched - watcher if watcher is not None and dispatched >= watcher else None,
                "flow_dispatch_to_result_seconds": outputs[-1] - dispatched}

    def ingest_batch(self, probe, directory):
        self.assertEqual([[0]], rows(probe, BATCH_SQL))
        started = monotonic()
        write_ticket(directory, BATCH_START)
        with ThreadPoolExecutor(max_workers=2) as pool:
            writes = pool.submit(write_batch, directory)
            workload = pool.submit(self.batch_queries, probe)
            first, last, worker_peak, queue_peak, observations = self.observe_batch(probe, started, writes)
            written = writes.result()
            queries, queries_started, queries_finished = workload.result()
        self.assertLess(queries_started, last, "Query workload began after all Tickets were visible")
        self.assertGreater(queries_finished, started)
        return {"queries": queries, "tickets_written": BATCH_SIZE, "successful_visible": BATCH_SIZE,
                "write_seconds": written - started,
                "start_to_first_visible_seconds": first - started,
                "start_to_last_visible_seconds": last - started,
                "successful_tickets_per_second": BATCH_SIZE / (last - started),
                "observed_peak_active_workers": worker_peak, "observed_peak_watcher_queue_entries": queue_peak,
                "worker_status_samples": observations,
                "queue_depth_source": "watcher_queue_depth, including wakeups" if queue_peak is not None else "unavailable"}

    def batch_queries(self, probe):
        before = rows(probe, BATCH_SQL)[0][0]
        self.assertLess(before, BATCH_SIZE, "All Tickets were visible before the query workload")
        report, started, finished = sample_queries(probe)
        return report | {"verified_visible_before_queries": before}, started, finished

    def observe_batch(self, probe, started, writes):
        first, last, worker_peak, queue_peak, observations = None, None, 0, None, 0

        def observe():
            nonlocal first, last, worker_peak, queue_peak, observations
            if writes.done():
                writes.result()
            count, = rows(probe, BATCH_SQL)
            visible = monotonic()
            self.assertEqual(1, len(count))
            self.assertIn(count[0], range(BATCH_SIZE + 1))
            if count[0] and first is None:
                first = visible
            jobs = probe.jobs()
            observations += 1
            worker_peak = max(worker_peak, capture_workers(jobs))
            if type(depth := jobs.get("watcher_queue_depth")) is int and depth >= 0:
                queue_peak = max(queue_peak or 0, depth)
            if count[0] == BATCH_SIZE:
                last = visible
            return last

        probe.until(observe, "all 500 exact Ticket rows to become visible")
        self.assertGreaterEqual(first, started)
        self.assertGreaterEqual(last, first)
        return first, last, worker_peak, queue_peak, observations
