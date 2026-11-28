"""Additional watcher capture-fence cases."""

from contextlib import redirect_stderr
import errno
from io import StringIO
import json
import os
from threading import Event, Thread
import time
from unittest.mock import patch

from watchdog.observers.api import BaseObserver


class CaptureFenceExtraCases:
    def test_managed_write_skips_poll_without_advancing_proof(self):
        archived = self.control / "09_archived"
        archived.mkdir()
        foreground, background = self.control / "live.md", archived / "old.md"
        for carrier in (foreground, background):
            carrier.write_text("before")
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        with self.watcher.managed_write:
            for carrier, archive in ((foreground, False), (background, True)):
                observer = (
                    self.watcher.archive_observer
                    if archive
                    else self.watcher.observer
                )
                epoch = self.watcher.capture_epoch(archive=archive)
                emitters = [
                    (emitter, emitter._snapshot, emitter._snapshot_started)
                    for emitter in observer.emitters
                ]
                carrier.write_text("after")
                for emitter, snapshot, started in emitters:
                    emitter.queue_events(0)
                    self.assertIs(snapshot, emitter._snapshot)
                    self.assertEqual(started, emitter._snapshot_started)
                self.assertEqual(
                    epoch, self.watcher.capture_epoch(archive=archive)
                )
        paths = set()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and paths != {
            str(foreground),
            str(background),
        }:
            events = self.watcher.changes(0.1)
            self.assertNotIn(
                "coverage_recovered", [event["event_type"] for event in events]
            )
            paths.update(event["old_path"] for event in events)
        self.assertEqual({str(foreground), str(background)}, paths)

    def test_close_cancels_archive_baseline_waiting_for_write(self):
        self.watcher.start()
        entered = Event()
        start = BaseObserver.start
        answers = []

        def baseline(observer):
            entered.set()
            return start(observer)

        with (
            patch.object(BaseObserver, "start", baseline),
            self.watcher.managed_write,
        ):
            archive = Thread(
                target=lambda: answers.append(self.watcher.watch_archives()),
                daemon=True,
            )
            archive.start()
            self.assertTrue(entered.wait(2))
            closing = Thread(target=self.watcher.close, daemon=True)
            closing.start()
            closing.join(2)
            self.assertFalse(closing.is_alive())
            archive.join(2)
        self.assertEqual([False], answers)

    def test_stopped_foreground_observer_restores_baseline_and_queues_reconciliation(
        self,
    ):
        self.watcher.start()
        previous = self.watcher.observer
        emitter = next(iter(previous.emitters))
        emitter.stop()
        emitter.join()
        self.assertIsNone(self.watcher.capture_epoch())
        self.watcher.restore_foreground()
        epoch = self.watcher.capture_epoch()
        self.assertIsNotNone(epoch)
        self.assertIsNot(previous, epoch[0])
        self.assertEqual(
            ["coverage_recovered"],
            [change["event_type"] for change in self.watcher.changes(0)],
        )

    def test_stopped_archive_observer_restores_on_background_capture(self):
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        previous = self.watcher.archive_observer
        emitter = next(iter(previous.emitters))
        emitter.stop()
        emitter.join()
        self.assertIsNone(self.watcher.capture_epoch(archive=True))
        self.assertTrue(self.watcher.watch_archives())
        epoch = self.watcher.capture_epoch(archive=True)
        self.assertIsNotNone(epoch)
        self.assertIsNot(previous, epoch[0])

    def test_fence_refuses_an_incomplete_poll(self):
        carrier = self.control / "atom.md"
        carrier.write_text("present")
        self.watcher.start()
        epoch = self.watcher.capture_epoch(trace=True)
        lstat = os.lstat

        def denied(path, *args, **kwargs):
            if path == str(carrier):
                raise PermissionError(
                    errno.EACCES, "private exception text", path
                )
            return lstat(path, *args, **kwargs)

        diagnostics = StringIO()
        with (
            patch.object(os, "lstat", side_effect=denied),
            redirect_stderr(diagnostics),
        ):
            self.assertIsNone(
                self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32)
            )
        report = json.loads(diagnostics.getvalue())
        self.assertEqual("coverage_lost", report["reason"])
        self.assertEqual(
            {
                "kind": "lstat_failed",
                "path": "control/atom.md",
                "errno": errno.EACCES,
            },
            report["observation"],
        )
        self.assertNotIn("private exception text", diagnostics.getvalue())
        self.assertNotIn(str(self.root), diagnostics.getvalue())
        condition = self.watcher._proof.condition
        with condition:
            self.assertTrue(
                condition.wait_for(
                    lambda: self.watcher.capture_epoch() is not None, timeout=3
                )
            )
        self.assertIn(
            "coverage_recovered",
            [change["event_type"] for change in self.watcher.changes(0)],
        )

    def test_native_ticket_start_defers_archive_index_and_runs_once(self):
        tickets = self.control / "__TKT"
        archive = tickets / "09_archived"
        archive.mkdir(parents=True)
        (archive / "archive.md").touch()
        carrier = tickets / "live.md"
        carrier.touch()
        with patch("ORCHESTRATOR_beta_C68.watching.watcher.Observer") as observer:
            self.watcher.start()
            observer.assert_not_called()
            with patch.object(
                self.watcher,
                "_ticket_version",
                wraps=self.watcher._ticket_version,
            ) as version:
                self.watcher.start_ticket_watch()
                self.watcher.start_ticket_watch()
            observer.assert_called_once()
            version.assert_called_once_with(carrier)
            self.assertEqual(
                ("created", [carrier]),
                self.watcher._ticket_change("created", [carrier]),
            )
            self.assertIsNone(
                self.watcher._ticket_change("created", [carrier])
            )
