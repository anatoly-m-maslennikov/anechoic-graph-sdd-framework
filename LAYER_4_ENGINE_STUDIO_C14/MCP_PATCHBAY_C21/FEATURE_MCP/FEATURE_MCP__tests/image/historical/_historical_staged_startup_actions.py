"""Exercise staged startup and offline reconciliation."""

from . import historical_staged_startup__support as s


class StagedStartupActions:
    def _startup_metrics(self, probe, image, mode):
        metrics = {
            "startup_timing": {
                "image": image,
                "mode": mode,
                "container": probe.container,
                "archive_intentionally_paused": ["cold", "restart"],
                "unchanged_archive": "resume an observed pause or accept completed archive",
                "non_archived_load_ended_meaning": "kernel_admission",
                "scan_metric_note": (
                    "read durations can overlap; foreground_capture scan "
                    "includes parse"
                ),
            },
            "startup_resources": {
                "sample_boundary": "after first public MCP query",
                "scope_note": (
                    "includes one cgroup reader process; the test driver "
                    "runs outside"
                ),
                "candidate_limits": {"cpus": 1, "pids": 128},
            },
            "startup_outcomes": {},
            "public_clock": "host monotonic from the Docker run or start call",
        }
        return metrics

    def _exercise(self, probe, directory, image, mode):
        files = s.paths(directory)
        parent = directory.relative_to(probe.root).as_posix()
        timing_required = mode == "beta_next" and probe.supports_timing()
        metrics = self._startup_metrics(probe, image, mode)
        live, before, disk, generation, live_atoms = self._check_cold(
            probe, parent, files, metrics
        )
        cold = self._record_timing(probe, "cold", metrics, timing_required)
        metrics["cold_ingest_throughput"] = s.cold_throughput(cold, live_atoms)
        if timing_required:
            self.assertIsNotNone(
                metrics["cold_ingest_throughput"]["live_atoms_per_load_second"]
            )
        self._unchanged_cycle(
            probe,
            (parent, files, live, disk, before, generation),
            metrics,
            timing_required,
        )
        probe.stop()
        added, moved, archived = self._offline_changes(files)
        started = probe.restart("restart")
        self._check_restart(
            probe,
            parent,
            files,
            added,
            moved,
            archived,
            live,
            disk,
            before,
            metrics,
            started,
        )
        self._record_timing(
            probe, "restart", metrics, timing_required, changed_paths=5
        )
        print(
            "ANECHOIC_TEST_METRICS "
            + s.json.dumps({"staged_startup": metrics}),
            flush=True,
        )

    def _first_query(self, probe, phase, metrics, started):
        probe.until(lambda: s.public_ready(probe), phase + " public health")
        metrics[phase + "_public_ready_seconds"] = s.monotonic() - started
        if phase == "restored":
            probe.phase("restart_public_ready", url=probe.url)
        s.asyncio.run(self._mcp_query(probe.url))
        metrics[phase + "_first_query_seconds"] = s.monotonic() - started

    def _startup_outcome(
        self, probe, phase, kind, metrics, *, delta_path_count=None
    ):
        result = probe.startup(phase)
        self.assertIsNotNone(
            result,
            f"{phase} startup flow unavailable after successful public query",
        )
        metrics["startup_outcomes"][phase] = result
        self.assertEqual("succeeded", result["outcome"], result)
        self.assertEqual(kind, result["kind"], result)
        self.assertEqual(delta_path_count, result["delta_path_count"], result)
        expected = (
            "generation_reuse_check"
            if kind == "reused"
            else "generation_admission"
        )
        self.assertEqual(
            [("worker_started", "succeeded"), (expected, "succeeded")],
            [(name, state) for name, state, _ in result["reason"]["effects"]],
            result,
        )
        return result

    def _check_cold(self, probe, parent, files, metrics):
        probe.until(probe.stopped, "archive Worker barrier")
        health, _ = probe.until(probe.ready, "foreground readiness")
        metrics["cold_ready_seconds"] = s.monotonic() - probe.started
        self.assertTrue(health["archive_pending"])
        counts = s.status_counts(probe)
        self.assertEqual(0, counts.get("Archived", 0))
        live_atoms = sum(counts.values())
        self.assertGreater(live_atoms, 0)
        self._first_query(probe, "cold", metrics, probe.started)
        metrics["startup_resources"]["cold"] = probe.resources()
        self._startup_outcome(probe, "cold", "full", metrics)["reason"][
            "fixture"
        ] = "no persisted database"
        files[0].write_text(
            files[0].read_text().replace("Current 1", "Live edit 1")
        )
        expected = [[parent, files[0].name, "Live edit 1"]]
        probe.until(
            lambda: probe.rows(s.query("AN-T-1")) == expected,
            "live edit publication",
        )
        self.assertTrue(probe.health()["archive_pending"])
        probe.release()
        complete, _ = probe.until(probe.complete, "archive completion")
        metrics["cold_archive_complete_seconds"] = (
            s.monotonic() - probe.started
        )
        self.assertEqual(expected, probe.rows(s.query("AN-T-1")))
        before = s.status_counts(probe)
        self.assertEqual(1500, before.get("Archived"))
        return (
            expected,
            before,
            probe.disk(),
            complete["generation"],
            live_atoms,
        )

    def _check_unchanged(
        self,
        probe,
        parent,
        files,
        live,
        disk,
        before,
        generation,
        metrics,
        started,
    ):
        health, _ = probe.until(
            probe.ready, "unchanged restart foreground readiness"
        )
        metrics["unchanged_ready_seconds"] = s.monotonic() - started
        self.assertEqual(generation, health["generation"])
        self.assertEqual(disk, probe.disk())
        self._first_query(probe, "unchanged", metrics, started)
        metrics["startup_resources"]["unchanged"] = probe.resources()
        result = self._startup_outcome(probe, "unchanged", "reused", metrics)
        self.assertEqual(generation, result["generation"])
        self.assertEqual(live, probe.rows(s.query("AN-T-1")))
        for number, path in enumerate(files[1:], 2):
            self.assertEqual(
                [[parent, path.name, f"Current {number}"]],
                probe.rows(s.query(f"AN-T-{number}")),
            )
        complete, _ = probe.until(
            probe.complete_unchanged, "unchanged restart archive completion"
        )
        metrics["unchanged_archive_complete_seconds"] = s.monotonic() - started
        self.assertEqual(generation, complete["generation"])
        self.assertEqual(before, s.status_counts(probe))

    def _offline_changes(self, files):
        added = files[3].with_name("AN-T-5-TASK--staged.md")
        added.write_text(s.canonical_carrier(5, "active", "Offline add 5"))
        files[1].write_text(
            files[1].read_text().replace("Current 2", "Offline edit 2")
        )
        moved = files[2].with_name("AN-T-3-TASK--staged-moved.md")
        files[2].rename(moved)
        files[3].unlink()
        archived = (
            added.parent / "09_archived" / "AN-T-15000@1-TASK--history.md"
        )
        archived.write_text(
            s.canonical_carrier(15000, "archived", "Offline archive add")
        )
        return (added, moved, archived)

    async def _mcp_query(self, url):
        async with (
            s.image_mcp_transport(url + "/anechoic/mcp") as streams,
            s.ClientSession(*streams) as client,
        ):
            await client.initialize()
            result = await client.call_tool(
                "query_run",
                {"sql": "SELECT 1 AS ready", "result_delivery": "inline"},
            )
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([[1]], result.structured_content["rows"])

    def _unchanged_cycle(self, probe, state, metrics, timing_required):
        parent, files, live, disk, before, generation = state
        probe.stop()
        started = probe.restart("unchanged")
        self._check_unchanged(
            probe,
            parent,
            files,
            live,
            disk,
            before,
            generation,
            metrics,
            started,
        )
        self._record_timing(
            probe, "unchanged", metrics, timing_required, changed_paths=0
        )
