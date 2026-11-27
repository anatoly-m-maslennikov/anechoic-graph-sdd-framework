"""Verify staged startup and persisted offline reconciliation in the candidate image."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic
import unittest

from mcp.client.session import ClientSession

from ..FEATURE_MCP__tests__shared import (
    image_mcp_transport,
    image_timeout,
    request,
)
from .staged_startup__support import (
    PackagedProbe, canonical_carrier, cold_throughput, prepare,
)


def query(ref):
    return ('SELECT relative_path, filename, "content.summary" FROM atoms '
            f"WHERE reference='{ref}'")


def status_counts(probe):
    return dict(
        probe.rows("SELECT status_group, count(*) FROM atoms GROUP BY 1")
    )


def public_ready(probe):
    status, payload = request(probe.url + '/anechoic/health')
    return status == 200 and isinstance(payload, dict) and payload.get('state') == 'ready'


def paths(directory):
    return [directory / f'AN-T-{i}-TASK--staged.md' for i in range(1, 5)]


class PackagedStagedStartupTests(unittest.TestCase):
    def test_staged_startup_and_disk_restart(self):
        image = os.environ.get('ANECHOIC_IMAGE', '')
        self.assertRegex(image, r'\Asha256:[0-9a-f]{64}\Z')
        environment = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{json .Config.Env}}', image],
                                              text=True, timeout=image_timeout(10))
        modes = [item.split('=', 1)[1] for item in json.loads(environment)
                 if item.startswith('ANECHOIC_RUNTIME_STACK=')]
        if not modes or modes[-1] not in ('beta', 'beta_next'):
            self.skipTest('Staged startup applies to the Beta runtime')
        temp = self.enterContext(tempfile.TemporaryDirectory(prefix='anechoic-staged-image-'))
        root = Path(temp).resolve()
        subprocess.run(['git', 'init', '--quiet', str(root)], check=True, timeout=image_timeout(10))
        directory = prepare(root, write_carrier=canonical_carrier)
        self.assertFalse((root / '.anechoic_runtime').exists())
        probe = PackagedProbe(self, root, image)
        try:
            self._exercise(probe, directory, image, modes[-1])
        except BaseException:
            logs = probe.docker('logs', probe.container, timeout=30)
            print(logs[-12000:], flush=True)
            raise

    def _exercise(self, probe, directory, image, mode):
        files = paths(directory)
        parent = directory.relative_to(probe.root).as_posix()
        timing_required = mode == 'beta_next' and probe.supports_timing()
        metrics = {
            "startup_timing": {
                "image": image,
                "mode": mode,
                "container": probe.container,
                "archive_intentionally_paused": ["cold", "restart"],
                "unchanged_archive": "resume an observed pause or accept completed archive",
                "non_archived_load_ended_meaning": "kernel_admission",
                "scan_metric_note": "read durations can overlap; foreground_capture scan includes parse",
            },
            "startup_resources": {
                "sample_boundary": "after first public MCP query",
                "scope_note": "includes one cgroup reader process; the test driver runs outside",
                "candidate_limits": {"cpus": 1, "pids": 128},
            },
            "startup_outcomes": {},
            "public_clock": "host monotonic from the Docker run or start call",
        }
        live, before, disk, generation, live_atoms = self._check_cold(
            probe, parent, files, metrics
        )
        cold = self._record_timing(probe, 'cold', metrics, timing_required)
        metrics['cold_ingest_throughput'] = cold_throughput(cold, live_atoms)
        if timing_required:
            self.assertIsNotNone(
                metrics["cold_ingest_throughput"]["live_atoms_per_load_second"]
            )
        probe.stop()
        started = probe.restart('unchanged')
        self._check_unchanged(probe, parent, files, live, disk, before, generation, metrics, started)
        self._record_timing(
            probe, "unchanged", metrics, timing_required, changed_paths=0
        )
        probe.stop()
        added, moved, archived = self._offline_changes(files)
        started = probe.restart('restart')
        self._check_restart(probe, parent, files, added, moved, archived, live, disk, before, metrics, started)
        self._record_timing(
            probe, "restart", metrics, timing_required, changed_paths=5
        )
        print('ANECHOIC_TEST_METRICS ' + json.dumps({'staged_startup': metrics}), flush=True)

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

    def _first_query(self, probe, phase, metrics, started):
        probe.until(lambda: public_ready(probe), phase + ' public health')
        metrics[phase + '_public_ready_seconds'] = monotonic() - started
        if phase == 'restored':
            probe.phase('restart_public_ready', url=probe.url)
        asyncio.run(self._mcp_query(probe.url))
        metrics[phase + '_first_query_seconds'] = monotonic() - started

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
        metrics["cold_ready_seconds"] = monotonic() - probe.started
        self.assertTrue(health["archive_pending"])
        counts = status_counts(probe)
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
            lambda: probe.rows(query("AN-T-1")) == expected,
            "live edit publication",
        )
        self.assertTrue(probe.health()["archive_pending"])
        probe.release()
        complete, _ = probe.until(probe.complete, "archive completion")
        metrics["cold_archive_complete_seconds"] = monotonic() - probe.started
        self.assertEqual(expected, probe.rows(query("AN-T-1")))
        before = status_counts(probe)
        self.assertEqual(1500, before.get("Archived"))
        return (
            expected,
            before,
            probe.disk(),
            complete["generation"],
            live_atoms,
        )

    def _check_unchanged(self, probe, parent, files, live, disk, before, generation, metrics, started):
        health, _ = probe.until(probe.ready, 'unchanged restart foreground readiness')
        metrics['unchanged_ready_seconds'] = monotonic() - started
        self.assertEqual(generation, health['generation'])
        self.assertEqual(disk, probe.disk())
        self._first_query(probe, 'unchanged', metrics, started)
        metrics['startup_resources']['unchanged'] = probe.resources()
        result = self._startup_outcome(probe, 'unchanged', 'reused', metrics)
        self.assertEqual(generation, result['generation'])
        self.assertEqual(live, probe.rows(query('AN-T-1')))
        for number, path in enumerate(files[1:], 2):
            self.assertEqual([[parent, path.name, f'Current {number}']], probe.rows(query(f'AN-T-{number}')))
        complete, _ = probe.until(probe.complete_unchanged, 'unchanged restart archive completion')
        metrics['unchanged_archive_complete_seconds'] = monotonic() - started
        self.assertEqual(generation, complete['generation'])
        self.assertEqual(before, status_counts(probe))

    def _offline_changes(self, files):
        added = files[3].with_name("AN-T-5-TASK--staged.md")
        added.write_text(canonical_carrier(5, "active", "Offline add 5"))
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
            canonical_carrier(15000, "archived", "Offline archive add")
        )
        return added, moved, archived

    def _check_offline_rows(self, probe, parent, files, added, moved):
        self.assertEqual(
            [[parent, files[1].name, "Offline edit 2"]],
            probe.rows(query("AN-T-2")),
        )
        self.assertEqual(
            [[parent, moved.name, "Current 3"]], probe.rows(query("AN-T-3"))
        )
        self.assertEqual([], probe.rows(query("AN-T-4")))
        self.assertEqual(
            [[parent, added.name, "Offline add 5"]],
            probe.rows(query("AN-T-5")),
        )

    def _check_restart(self, probe, parent, files, added, moved, archived, live, disk, before, metrics, restart_started):
        pid = probe.until(probe.stopped, 'restart archive Worker barrier')
        probe.phase('restart_archive_paused', worker_pid=pid)
        health, _ = probe.until(probe.ready, 'restart foreground readiness')
        metrics['restored_ready_seconds'] = monotonic() - restart_started
        self.assertTrue(health['archive_pending'])
        probe.phase(
            "restart_foreground_ready", generation=health["generation"]
        )
        self._check_offline_rows(probe, parent, files, added, moved)
        self.assertEqual([], probe.rows(query('AN-T-15000@1')))
        self.assertEqual(live, probe.rows(query('AN-T-1')))
        self.assertEqual(disk, probe.disk())
        probe.phase('restart_offline_rows_verified')
        self._first_query(probe, 'restored', metrics, restart_started)
        probe.phase('restart_mcp_query_passed')
        metrics['startup_resources']['restart'] = probe.resources()
        result = self._startup_outcome(
            probe, "restart", "native_delta", metrics, delta_path_count=5
        )
        self.assertEqual(health['generation'], result['generation'])
        files[0].write_text(
            files[0].read_text().replace("Live edit 1", "Restart live edit 1")
        )
        probe.phase('restart_live_edit_written')
        restarted = [[parent, files[0].name, 'Restart live edit 1']]
        probe.until(lambda: probe.rows(query('AN-T-1')) == restarted, 'restart live edit')
        probe.phase('restart_live_edit_observed')
        self.assertTrue(probe.health()['archive_pending'])
        probe.release()
        probe.until(probe.complete, 'restart archive completion')
        metrics["restored_archive_complete_seconds"] = (
            monotonic() - restart_started
        )
        self.assertEqual(
            before | {"Archived": before["Archived"] + 1}, status_counts(probe)
        )
        self._check_offline_rows(probe, parent, files, added, moved)
        self.assertEqual([[parent + '/09_archived', archived.name, 'Offline archive add']],
                         probe.rows(query('AN-T-15000@1')))
        self.assertEqual(restarted, probe.rows(query('AN-T-1')))
        self.assertEqual(disk, probe.disk())
        probe.until(lambda: public_ready(probe), 'restart public health')
        asyncio.run(self._mcp_query(probe.url))

    async def _mcp_query(self, url):
        async with (
            image_mcp_transport(url + "/anechoic/mcp") as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            result = await client.call_tool(
                "query_run",
                {"sql": "SELECT 1 AS ready", "result_delivery": "inline"},
            )
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([[1]], result.structured_content["rows"])
