"""Exercise the default startup checkpoint and deferred Archive protocol."""

from contextlib import redirect_stderr
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest.mock import patch

from .... import ORCHESTRATOR_beta_C68__shared as orchestrator
from ...ORCHESTRATOR_beta_C68__tests__shared import RunFixture, kernel_server


TIMING_PREFIX = "ANECHOIC_STARTUP_TIMING "


def timing_records(buffer):
    return [
        json.loads(line.removeprefix(TIMING_PREFIX))
        for line in buffer.getvalue().splitlines()
        if line.startswith(TIMING_PREFIX)
    ]


class ReplayCapture:
    def __init__(self, jobs):
        self.jobs = jobs
        self.started = [Event() for _ in range(3)]
        self.release = [Event() for _ in range(2)]
        self.final_admission = Event()
        self.calls = []
        self.admissions = []

    def capture(self, directory, reuse, paths, **options):
        step = len(self.calls)
        self.calls.append((paths, self.jobs.status()["latest"]))
        self.started[step].set()
        if step < len(self.release) and not self.release[step].wait(5):
            raise RuntimeError("Test capture was not released")
        witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
        result = {"snapshot": {"atoms": []}, "reuse": witness}
        return result | ({"paths": paths} if paths else {})

    def admit(self, *args):
        generation = str(len(self.admissions) + 1)
        self.admissions.append(generation)
        if generation == "3":
            self.final_admission.set()
        return {"generation": generation}


class StartupCheckpointObservations:
    def test_live_timing_follows_successful_startup_admission_only(self):
        root = Path(self.jobs.binding["root"])
        for field in ("model", "structure"):
            (root / (field + ".json")).write_text("{}")
        cases = (
            ("full", "disabled", {}),
            ("native_delta", "none", {"paths": []}),
            (
                "reused",
                "deferred",
                {"unchanged": True, "archive_pending": True},
            ),
        )
        with (
            kernel_server(root) as kernel,
            patch.dict(os.environ, ANECHOIC_STARTUP_TIMING="1"),
        ):
            self.jobs.database_socket = str(root / "kernel.sock")
            for mode, archive, result in cases:
                self._check_timing_after_admission(
                    root, kernel, mode, archive, result
                )

    def _check_timing_after_admission(
        self, root, kernel, mode, archive, result
    ):
        with (
            self.subTest(mode=mode),
            redirect_stderr(StringIO()) as stderr,
        ):
            self.jobs.startup_capture = True
            self.jobs.skip_archives = archive == "disabled"
            kernel.reject = True
            with self.assertRaisesRegex(
                RuntimeError, "Kernel rejected generation"
            ):
                self.jobs._admit_live_result(str(root), result, None, None)
            self.assertFalse(timing_records(stderr))
            kernel.reject = False
            self.assertEqual(
                mode,
                self.jobs._admit_live_result(str(root), result, None, None)[
                    "kind"
                ],
            )
            self.jobs.startup_capture = False
            self.jobs._admit_live_result(str(root), result, None, None)
            (record,) = timing_records(stderr)
            self.assertGreater(record.pop("timestamp_ns"), 0)
            self.assertEqual(
                {
                    "phase": "non_archived_load_ended",
                    "mode": mode,
                    "archive": archive,
                },
                record,
            )

    def test_unchanged_live_reconciles_previously_known_archive_after_all_roots_removed(
        self,
    ):
        unchanged = {"base_generation": "old", "unchanged": True}
        with (
            patch.object(
                self.jobs, "_run_worker", return_value=unchanged
            ) as worker,
            patch.object(
                orchestrator,
                "confirm_reuse",
                return_value={"generation": "old", "kind": "reused"},
            ) as admit,
        ):
            outcome = self.jobs._attempt_generation(None, self.reuse)
        self.assertEqual("reused", outcome["kind"])
        self.assertEqual(
            {
                "incremental": True,
                "foreground": True,
                "watcher_guarded": True,
                "force_model": False,
            },
            worker.call_args.kwargs,
        )
        self.assertTrue(admit.call_args.args[-1]["archive_pending"])
        deferred = self.jobs.deferred_archive
        self.assertEqual([], deferred["roots"])
        self.assertEqual(
            {"control/09_archived/a.md": "c" * 64},
            deferred["checkpoint"]["carrier_hashes"],
        )
        self.assertEqual(
            {"control/09_archived": "e" * 64},
            deferred["checkpoint"]["folder_hashes"],
        )
        self.assertNotIn("folder_hashes", self.jobs.generation_reuse)

    def test_compiler_refresh_uses_updated_archive_witness(self):
        foreground = self.reuse | {
            "checkpoint_scope": "foreground",
            "carrier_hashes": {},
            "folder_hashes": {},
        }
        witness = {
            "inputs": self.reuse["inputs"] | {"manifest": "d" * 64},
            "graph_config": None,
            "endpoints": {"new": "endpoint"},
        }
        self.jobs.deferred_archive = self.jobs._restart_archive(
            foreground, {"compiler": {}, "reuse": witness}
        )
        self.jobs.watcher.watch_archives.return_value = True
        record = orchestrator.ReuseRecord.model_validate(
            self.reuse | witness | {"checkpoint_scope": "archive"}
        )
        with (
            patch(
                "ORCHESTRATOR_beta_C68.archive_operations.archive_jobs.read_reuse",
                return_value=record,
            ),
            patch.object(
                self.jobs,
                "_archive_snapshot",
                return_value=({}, {"unchanged": True}),
            ) as capture,
        ):
            self.jobs._capture_archive(self.jobs.deferred_archive)
        self.assertEqual(
            witness["endpoints"], capture.call_args.args[1]["endpoints"]
        )
        self.assertEqual(
            {"control/09_archived/a.md": "c" * 64},
            capture.call_args.args[1]["carrier_hashes"],
        )

    def test_scoped_unchanged_startup_confirms_without_another_checkpoint_read(
        self,
    ):
        foreground = self.reuse | {
            "checkpoint_scope": "foreground",
            "carrier_hashes": {},
            "folder_hashes": {},
        }
        result = {"base_generation": "old", "unchanged": True}
        with (
            patch.object(self.jobs, "_run_worker", return_value=result),
            patch.object(self.jobs, "_record_ingestion_issues"),
            patch("ORCHESTRATOR_beta_C68.generation.generation.read_reuse") as read,
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.admit_generation",
                return_value={"generation": "old", "kind": "reused"},
            ) as admit,
        ):
            self.jobs._attempt_generation(None, foreground)
        read.assert_not_called()
        self.assertTrue(admit.call_args.args[3]["archive_pending"])

    def test_failed_foreground_fence_keeps_legacy_error_and_passes_run_id(
        self,
    ):
        self.jobs.active = RunFixture(
            state="running", started_at=0, run_id="a" * 32
        )
        for fence in (False, None):
            with (
                self.subTest(fence=fence),
                patch.object(self.jobs, "_run_worker", return_value={}),
            ):
                self.jobs.watcher.capture_fence.return_value = fence
                with self.assertRaisesRegex(
                    ValueError,
                    "Native Project carriers changed during generation",
                ):
                    self.jobs._attempt_generation(None, None)
                self.assertEqual(
                    "a" * 32,
                    self.jobs.watcher.capture_fence.call_args.kwargs["run_id"],
                )
        self.jobs.watcher.capture_epoch.assert_called_with(trace=True)

    def test_run_snapshot_preserves_result_ids_and_replay_state(self):
        outcome = {
            "state": "succeeded",
            "generation": "g",
            "result_ids": {"old": "new"},
        }
        with patch.object(
            self.jobs, "_attempt_with_recovery", return_value=outcome
        ):
            self.jobs._generate()
        self.jobs.startup_replay = True
        latest = self.jobs.status()["latest"]
        self.assertEqual("running", latest["state"])
        latest["result_ids"]["old"] = "changed"
        self.jobs.startup_replay = False
        latest = self.jobs.status()["latest"]
        self.assertEqual(
            ("succeeded", {"old": "new"}),
            (latest["state"], latest["result_ids"]),
        )
        self.assertNotIn("retrying", latest)

    def test_startup_replays_a_finite_batch_before_reporting_ready(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        control = root / "_anechoic_replay"
        tickets = control / "__TKT"
        tickets.mkdir(parents=True)
        binding = self.jobs.binding | {
            "root": str(root),
            "control_root": control.name,
        }
        jobs = orchestrator.GenerationJobs("test", binding, "socket")
        self.addCleanup(jobs.close)
        replay = ReplayCapture(jobs)
        for event in replay.release:
            self.addCleanup(event.set)
        self._run_startup_replay(jobs, replay, tickets, binding)
        self.assertEqual(
            [
                [
                    f"{control.name}/__TKT/AN-T-{index}--task.md"
                    for index in indices
                ]
                for indices in ((1, 2), (3,))
            ],
            [call[0] for call in replay.calls[1:]],
        )
        follow_up_status = replay.calls[2][1]
        self.assertEqual(
            ("succeeded", "2"),
            (follow_up_status["state"], follow_up_status["generation"]),
        )

    def _run_startup_replay(self, jobs, replay, tickets, binding):
        with (
            patch.object(orchestrator, "read_reuse", return_value=None),
            patch.object(jobs, "_run_worker", side_effect=replay.capture),
            patch.object(jobs, "_admit_live_result", side_effect=replay.admit),
            patch.object(jobs, "_run_archive"),
        ):
            jobs.start()
            self.assertTrue(replay.started[0].wait(3))
            for count in (1, 2):
                (tickets / f"AN-T-{count}--task.md").touch()
            replay.release[0].set()
            self.assertTrue(replay.started[1].wait(5))
            self.assertEqual(["1"], replay.admissions)
            self.assertEqual("running", jobs.status()["latest"]["state"])
            self.assertTrue(jobs.health()["startup_replay_pending"])
            request = binding | {
                "instance_id": "test",
                "name": "atom_lifecycle_update",
                "arguments": {},
            }
            self.assertEqual(
                "startup_replay_pending",
                jobs.lifecycle(request)[1]["error"]["code"],
            )
            (tickets / "AN-T-3--task.md").touch()
            replay.release[1].set()
            self.assertTrue(replay.started[2].wait(5))
            self.assertTrue(replay.final_admission.wait(5))
            self.assertFalse(jobs.health()["startup_replay_pending"])
            jobs.close()
