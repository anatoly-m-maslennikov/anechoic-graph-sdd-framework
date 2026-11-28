"""Exercise the image generation workload."""

from . import historical_generation_load__support as s


class GenerationLoadActions:
    def exercise(self, probe, directory, archive_count):
        pid = probe.until(probe.stopped, "Archive Worker barrier")
        health, _ = probe.until(probe.ready, "foreground readiness")
        self.assertTrue(health["archive_pending"])
        probe.until(lambda: s.public_ready(probe), "public readiness")
        self.assertEqual(s.WORKLOAD_ROWS, s.rows(probe, s.WORKLOAD_SQL))
        idle, _, _ = s.sample_queries(probe)
        resources = {"idle_end": probe.resources()}
        archive = self.archive_queries(probe, pid, archive_count)
        probe.until(probe.complete, "Archive publication")
        resources["archive_publication"] = probe.resources()
        self.assertEqual(
            [[archive_count]],
            s.rows(
                probe,
                (
                    "SELECT count(*) FROM mrt_ticket_atoms WHERE "
                    "status_group='Archived'"
                ),
            ),
        )
        single = self.single_update(probe, directory)
        batch = self.ingest_batch(probe, directory)
        resources["batch_publication"] = probe.resources()
        return {
            "idle": {"queries": idle, "archive_intentionally_paused": True},
            "archive_active": archive,
            "single_update": single,
            "batch": batch,
            "resources": resources,
        }

    def archive_queries(self, probe, pid, archive_count):
        self.assertIn(probe.exec(s.ARCHIVE_STATE, pid), {"T", "t"})
        probe.release()
        state_before = probe.exec(s.ARCHIVE_STATE, pid)
        self.assertTrue(
            s.archive_running(state_before),
            f"Archive Worker was not active: {state_before}",
        )
        queries, _, _ = s.sample_queries(probe)
        state_after = probe.exec(s.ARCHIVE_STATE, pid)
        self.assertTrue(
            s.archive_running(state_after),
            f"Archive Worker did not span the query workload: {state_after}",
        )
        return {
            "queries": queries,
            "archive_tickets": archive_count,
            "worker_pid": int(pid),
            "state_before": state_before,
            "state_after": state_after,
            "paused_during_queries": False,
        }

    def _write_single(self, probe, directory):
        clock_before = s.clock_offset(probe)
        started = s.monotonic()
        write_start = s.time_ns()
        (directory / "AN-T-1-TASK--staged.md").write_text(
            s.carrier(1, "active", "Measured live edit")
        )
        write_end = s.time_ns()
        written = s.monotonic()
        return clock_before, started, write_start, write_end, written

    def single_update(self, probe, directory):
        before = probe.jobs()["latest"]["run_id"]
        self.assertEqual(
            [["active", "Current 1"]], s.rows(probe, s.SINGLE_SQL)
        )
        clock_before, started, write_start, write_end, written = (
            self._write_single(probe, directory)
        )
        visible = probe.until(
            lambda: (
                s.monotonic()
                if s.rows(probe, s.SINGLE_SQL)
                == [["active", "Measured live edit"]]
                else None
            ),
            "single Ticket edit publication",
        )
        job = probe.until(
            lambda: self.changed_run(probe, before),
            "single edit Worker result",
        )
        run_id = job["run_id"]
        self.assertRegex(run_id, "\\A[0-9a-f]{32}\\Z")
        flow = probe.until(
            lambda: self.generation_flow(probe, job),
            "single edit Flow publication",
        )
        bounds = s.watcher_detection_bounds(
            flow["watcher_observed_at"],
            (clock_before, s.clock_offset(probe)),
            write_start,
            write_end,
        )
        return {
            "write_seconds": written - started,
            "write_start_to_correct_sql_seconds": visible - started,
            "write_end_to_correct_sql_seconds": visible - written,
            "worker_seconds": job["worker_seconds"],
            "admission_seconds": job["admission_seconds"],
            "run_id": run_id,
            "generation": job["generation"],
            "generation_kind": job["kind"],
            "watcher_detection_clock_bounds": bounds,
            **flow,
        }

    def changed_run(self, probe, before):
        latest = probe.jobs().get("latest") or {}
        if latest.get("run_id") == before:
            return None
        if latest.get("state") in ("failed", "aborted") and (
            not latest.get("retrying")
        ):
            self.fail(f"Single Ticket edit failed: {latest}")
        return latest if latest.get("state") == "succeeded" else None

    def generation_flow(self, probe, job):
        run_id = job["run_id"]
        sql = (
            'SELECT sequence, kind, name, "at", CAST(detail AS VARCHAR), '
            "outcome, causes FROM src_flow_events\n            WHERE "
            "component='C68' AND run_id='"
            f"{run_id}"
            "' ORDER BY sequence"
        )
        events = s.rows(probe, sql)
        observed = {
            seq: at
            for seq, kind, name, at, detail, _, _ in events
            if kind == "input"
            and name == "file_change"
            and (s.json.loads(detail).get("timestamp_source") == "watcher")
        }
        triggers = [
            (at, causes)
            for _, kind, name, at, _, _, causes in events
            if kind == "trigger" and name == "file_change"
        ]
        outputs = [
            at
            for _, kind, name, at, detail, outcome, _ in events
            if kind == "output"
            and name == "generation_result"
            and (outcome == "succeeded")
            and (s.json.loads(detail).get("generation") == job["generation"])
        ]
        if not (triggers and outputs):
            return None
        dispatched, causes = triggers[0]
        watcher = min(
            (observed[seq] for seq in causes if seq in observed), default=None
        )
        return {
            "watcher_observed_at": watcher,
            "flow_dispatch_at": dispatched,
            "flow_result_at": outputs[-1],
            "watcher_queue_to_dispatch_seconds": dispatched - watcher
            if watcher is not None and dispatched >= watcher
            else None,
            "flow_dispatch_to_result_seconds": outputs[-1] - dispatched,
        }

    def ingest_batch(self, probe, directory):
        self.assertEqual([[0]], s.rows(probe, s.BATCH_SQL))
        started = s.monotonic()
        s.write_ticket(directory, s.BATCH_START)
        with s.ThreadPoolExecutor(max_workers=2) as pool:
            writes = pool.submit(s.write_batch, directory)
            workload = pool.submit(self.batch_queries, probe)
            first, last, worker_peak, queue_peak, observations = (
                self.observe_batch(probe, started, writes)
            )
            written = writes.result()
            queries, queries_started, queries_finished = workload.result()
        self.assertLess(
            queries_started,
            last,
            "Query workload began after all Tickets were visible",
        )
        self.assertGreater(queries_finished, started)
        return {
            "queries": queries,
            "tickets_written": s.BATCH_SIZE,
            "successful_visible": s.BATCH_SIZE,
            "write_seconds": written - started,
            "start_to_first_visible_seconds": first - started,
            "start_to_last_visible_seconds": last - started,
            "successful_tickets_per_second": s.BATCH_SIZE / (last - started),
            "observed_peak_active_workers": worker_peak,
            "observed_peak_watcher_queue_entries": queue_peak,
            "worker_status_samples": observations,
            "queue_depth_source": "watcher_queue_depth, including wakeups"
            if queue_peak is not None
            else "unavailable",
        }

    def batch_queries(self, probe):
        before = s.rows(probe, s.BATCH_SQL)[0][0]
        self.assertLess(
            before,
            s.BATCH_SIZE,
            "All Tickets were visible before the query workload",
        )
        report, started, finished = s.sample_queries(probe)
        return (
            report | {"verified_visible_before_queries": before},
            started,
            finished,
        )

    def observe_batch(self, probe, started, writes):
        first, last, worker_peak, queue_peak, observations = (
            None,
            None,
            0,
            None,
            0,
        )

        def observe():
            nonlocal first, last, worker_peak, queue_peak, observations
            if writes.done():
                writes.result()
            (count,) = s.rows(probe, s.BATCH_SQL)
            visible = s.monotonic()
            self.assertEqual(1, len(count))
            self.assertIn(count[0], range(s.BATCH_SIZE + 1))
            if count[0] and first is None:
                first = visible
            jobs = probe.jobs()
            observations += 1
            worker_peak = max(worker_peak, s.capture_workers(jobs))
            if (
                type((depth := jobs.get("watcher_queue_depth"))) is int
                and depth >= 0
            ):
                queue_peak = max(queue_peak or 0, depth)
            if count[0] == s.BATCH_SIZE:
                last = visible
            return last

        probe.until(observe, "all 500 exact Ticket rows to become visible")
        self.assertGreaterEqual(first, started)
        self.assertGreaterEqual(last, first)
        return (first, last, worker_peak, queue_peak, observations)
