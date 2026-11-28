"""Check restored data and archive reconciliation."""

from . import historical_staged_startup__support as s


class StagedRestartActions:
    def _check_offline_rows(self, probe, parent, files, added, moved):
        self.assertEqual(
            [[parent, files[1].name, "Offline edit 2"]],
            probe.rows(s.query("AN-T-2")),
        )
        self.assertEqual(
            [[parent, moved.name, "Current 3"]], probe.rows(s.query("AN-T-3"))
        )
        self.assertEqual([], probe.rows(s.query("AN-T-4")))
        self.assertEqual(
            [[parent, added.name, "Offline add 5"]],
            probe.rows(s.query("AN-T-5")),
        )

    def _check_restart(
        self,
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
        restart_started,
    ):
        pid = probe.until(probe.stopped, "restart archive Worker barrier")
        probe.phase("restart_archive_paused", worker_pid=pid)
        health, _ = probe.until(probe.ready, "restart foreground readiness")
        metrics["restored_ready_seconds"] = s.monotonic() - restart_started
        self.assertTrue(health["archive_pending"])
        probe.phase(
            "restart_foreground_ready", generation=health["generation"]
        )
        self._check_offline_rows(probe, parent, files, added, moved)
        self.assertEqual([], probe.rows(s.query("AN-T-15000@1")))
        self.assertEqual(live, probe.rows(s.query("AN-T-1")))
        self.assertEqual(disk, probe.disk())
        probe.phase("restart_offline_rows_verified")
        self._first_query(probe, "restored", metrics, restart_started)
        probe.phase("restart_mcp_query_passed")
        metrics["startup_resources"]["restart"] = probe.resources()
        result = self._startup_outcome(
            probe, "restart", "native_delta", metrics, delta_path_count=5
        )
        self.assertEqual(health["generation"], result["generation"])
        restarted = self._restart_live_edit(probe, parent, files)
        self._release_archive(probe)
        self._check_restart_archive(
            probe,
            (parent, files, added, moved, archived),
            disk,
            before,
            metrics,
            restart_started,
            restarted,
        )

    def _check_restart_archive(
        self, probe, paths, disk, before, metrics, restart_started, restarted
    ):
        parent, files, added, moved, archived = paths
        probe.until(probe.complete, "restart archive completion")
        metrics["restored_archive_complete_seconds"] = (
            s.monotonic() - restart_started
        )
        self.assertEqual(
            before | {"Archived": before["Archived"] + 1},
            s.status_counts(probe),
        )
        self._check_offline_rows(probe, parent, files, added, moved)
        self.assertEqual(
            [[parent + "/09_archived", archived.name, "Offline archive add"]],
            probe.rows(s.query("AN-T-15000@1")),
        )
        self.assertEqual(restarted, probe.rows(s.query("AN-T-1")))
        self.assertEqual(disk, probe.disk())
        probe.until(lambda: s.public_ready(probe), "restart public health")
        s.asyncio.run(self._mcp_query(probe.url))

    def _restart_live_edit(self, probe, parent, files):
        files[0].write_text(
            files[0].read_text().replace("Live edit 1", "Restart live edit 1")
        )
        probe.phase("restart_live_edit_written")
        restarted = [[parent, files[0].name, "Restart live edit 1"]]
        probe.until(
            lambda: probe.rows(s.query("AN-T-1")) == restarted,
            "restart live edit",
        )
        probe.phase("restart_live_edit_observed")
        return restarted

    def _release_archive(self, probe):
        self.assertTrue(probe.health()["archive_pending"])
        probe.release()
