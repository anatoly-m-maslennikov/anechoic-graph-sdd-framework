"""Verify foreground and Archive polling proofs."""

from contextlib import redirect_stderr
import errno
import gc
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
from threading import Event, Thread
import time
import unittest
from unittest.mock import patch
import weakref

from pydantic import ValidationError
from watchdog.events import DirCreatedEvent, DirDeletedEvent, FileSystemEventHandler
from watchdog.observers.api import BaseObserver, EventQueue, ObservedWatch

from ..ORCHESTRATOR_beta_C68__shared import PollComplete
from .ORCHESTRATOR_beta_C68__tests__shared import project_jobs


class PollCompleteTests(unittest.TestCase):
    def test_watchdog_queue_dispatch_and_mutation(self):
        event = PollComplete("/project", started=7, clean=True, roots=(("archive", 1, 2),))
        equal = PollComplete("/project", started=7, clean=True, roots=(("archive", 1, 2),))
        self.assertEqual(event, equal)
        self.assertEqual(hash(event), hash(equal))
        queue = EventQueue()
        watch = ObservedWatch("/project", recursive=True)
        queue.put((event, watch))
        queue.put((equal, watch))
        self.assertEqual(1, queue.qsize())
        received, _ = queue.get_nowait()
        seen = []

        class Handler(FileSystemEventHandler):
            def on_poll_complete(self, value):
                seen.append(value)

        Handler().dispatch(received)
        self.assertEqual([event], seen)
        event.clean = False
        event.probe = "mutable"
        self.assertEqual((False, "mutable"), (event.clean, event.probe))
        self.assertNotEqual(event, equal)

    def test_poll_data_is_strict(self):
        for kwargs in ({"started": "7"}, {"clean": 1}, {"roots": [["archive", 1, 2]]}, {"other": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                PollComplete("/project", **kwargs)


class CaptureFenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.control = self.root / "control"
        self.control.mkdir()
        jobs = project_jobs(self.root)
        self.watcher = jobs.watcher
        self.addCleanup(jobs.close)

    def test_discarded_snapshot_is_released_without_cyclic_collection(self):
        self.watcher.start()
        emitter = next(iter(self.watcher.observer.emitters))
        with self.watcher._proof.sampling_lock:
            if gc.isenabled():
                self.addCleanup(gc.enable)
            gc.disable()
            snapshot = emitter._take_snapshot()
            discarded = weakref.ref(snapshot)
            del snapshot
            self.assertIsNone(discarded())

    def test_fence_detects_restored_mtime_and_leaves_event_queued(self):
        carrier = self.control / "atom.md"
        carrier.write_text("before")
        self.watcher.start()
        epoch = self.watcher.capture_epoch(trace=True)
        self.assertIsNotNone(epoch)
        diagnostics = StringIO()
        with redirect_stderr(diagnostics):
            self.assertTrue(
                self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32)
            )
        self.assertEqual("", diagnostics.getvalue())
        before = carrier.stat()
        carrier.write_text("edited")
        os.utime(carrier, ns=(before.st_atime_ns, before.st_mtime_ns))
        with redirect_stderr(diagnostics):
            self.assertIs(
                self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32),
                False,
            )
        report = json.loads(diagnostics.getvalue())
        self.assertEqual(("watcher_fence_failed", "foreground", "source_changed", "WARNING", "a" * 32),
                         (report["code"], report["phase"], report["reason"], report["severity"], report["run_id"]))
        self.assertEqual({"kind": "modified", "path": "control/atom.md", "stat_fields": ["ctime_ns"]},
                         report["observation"])
        self.assertGreaterEqual(report["wait_ms"], 0)
        with patch.dict(os.environ, ANECHOIC_LOG_LEVEL="ERROR"), redirect_stderr(StringIO()) as filtered:
            self.assertIs(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32), False)
        self.assertEqual("", filtered.getvalue())
        self.assertIn(
            str(carrier),
            [change["old_path"] for change in self.watcher.changes(1)],
        )

    def test_archive_baselines_are_separate_and_skip_installed_sources(self):
        archive = self.control / "09_archived"
        archive.mkdir()
        carrier = archive / "old.md"
        carrier.write_text("before")
        (self.control / "000_ANECHOIC_framework/09_archived").mkdir(parents=True)
        self.watcher.start()
        self.assertEqual(("control/09_archived",), self.watcher.archive_roots())
        self.assertIsNone(self.watcher.capture_epoch(archive=True))
        self.assertTrue(self.watcher.watch_archives())
        self.assertEqual([], self.watcher.changes(0.05))
        foreground = self.watcher.capture_epoch()
        background = self.watcher.capture_epoch(archive=True)
        carrier.unlink()
        self.assertIs(self.watcher.capture_fence(background, archive=True, timeout=3), False)
        self.assertTrue(self.watcher.capture_fence(foreground, timeout=3))
        self.assertIn(str(carrier), [change["old_path"] for change in self.watcher.changes(1)])
        new_root = self.control / "component" / "09_archived"
        new_root.mkdir(parents=True)
        self.assertIs(self.watcher.capture_fence(foreground, timeout=3), False)
        deadline = time.monotonic() + 3
        while "control/component/09_archived" not in self.watcher.archive_roots() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertIn("control/component/09_archived", self.watcher.archive_roots())

    def test_replay_fence_dispatches_covered_code_and_carrier_changes(self):
        self.watcher.watch_code = True
        script = self.root / "entry"
        script.write_text("#!/bin/sh\n")
        yaml = self.control / "layout.yaml"
        yaml.touch()
        self.watcher.start()
        epoch = self.watcher.capture_epoch()
        script.write_text("no interpreter\n")
        yaml.write_text("new value\n")
        asset = self.root / "style.css"
        asset.touch()
        package = self.root / "typed"
        package.mkdir()
        self.assertIs(self.watcher.replay_fence(epoch, timeout=3), True)
        self.assertEqual(
            {str(path) for path in (script, yaml, asset, package)},
            {change["old_path"] for change in self.watcher.changes(0)},
        )

    def test_same_path_replacement_keeps_root_and_invalidates_intermediate_epoch(self):
        archive = self.control / "09_archived"
        archive.mkdir()
        replacement = self.root / "replacement"
        replacement.mkdir()
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        roots = ("control/09_archived",)
        with self.watcher._proof.condition:
            archive.rename(self.root / "old")
            replacement.rename(archive)
            self.watcher.dispatch(DirDeletedEvent(str(archive)))
            self.watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual(roots, self.watcher.archive_roots())
            epoch = self.watcher.capture_epoch(archive=True)
            self.assertIsNotNone(epoch)
            info = archive.stat()
            self.watcher.on_poll_complete(PollComplete(str(self.control), started=time.monotonic_ns(), clean=True,
                                                       archive=True, roots=((roots[0], info.st_ino, info.st_dev),)))
            self.assertIs(self.watcher.capture_fence(epoch, archive=True, timeout=0), False)
            self.assertEqual(roots, self.watcher.archive_roots())

    def test_completed_archive_scope_replaces_roots_when_parent_moves(self):
        component = self.control / "component"
        (component / "09_archived").mkdir(parents=True)
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        epoch = self.watcher.capture_epoch(archive=True)
        component.rename(self.control / "moved")
        self.assertIsNot(self.watcher.capture_fence(epoch, archive=True, timeout=3), True)
        condition = self.watcher._proof.condition
        with condition:
            self.assertTrue(condition.wait_for(
                lambda: self.watcher.archive_roots() == ("control/moved/09_archived",), timeout=3))

    def test_close_releases_waiting_fence(self):
        self.watcher.start()
        epoch = self.watcher.capture_epoch()
        started, finished = Event(), Event()
        results = []

        def fence():
            started.set()
            results.append(self.watcher.capture_fence(epoch, timeout=3))
            finished.set()

        thread = Thread(target=fence)
        thread.start()
        self.assertTrue(started.wait(1))
        self.watcher.close()
        self.assertTrue(finished.wait(1))
        thread.join()
        self.assertEqual([None], results)

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
                observer = self.watcher.archive_observer if archive else self.watcher.observer
                epoch = self.watcher.capture_epoch(archive=archive)
                emitters = [(emitter, emitter._snapshot, emitter._snapshot_started) for emitter in observer.emitters]
                carrier.write_text("after")
                for emitter, snapshot, started in emitters:
                    emitter.queue_events(0)
                    self.assertIs(snapshot, emitter._snapshot)
                    self.assertEqual(started, emitter._snapshot_started)
                self.assertEqual(epoch, self.watcher.capture_epoch(archive=archive))
        paths = set()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and paths != {str(foreground), str(background)}:
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

        with patch.object(BaseObserver, "start", baseline), self.watcher.managed_write:
            archive = Thread(target=lambda: answers.append(self.watcher.watch_archives()), daemon=True)
            archive.start()
            self.assertTrue(entered.wait(2))
            closing = Thread(target=self.watcher.close, daemon=True)
            closing.start()
            closing.join(2)
            self.assertFalse(closing.is_alive())
            archive.join(2)
        self.assertEqual([False], answers)

    def test_stopped_foreground_observer_restores_baseline_and_queues_reconciliation(self):
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
        self.assertEqual(["coverage_recovered"], [change["event_type"] for change in self.watcher.changes(0)])

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
                raise PermissionError(errno.EACCES, "private exception text", path)
            return lstat(path, *args, **kwargs)

        diagnostics = StringIO()
        with patch.object(os, "lstat", side_effect=denied), redirect_stderr(diagnostics):
            self.assertIsNone(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32))
        report = json.loads(diagnostics.getvalue())
        self.assertEqual("coverage_lost", report["reason"])
        self.assertEqual({"kind": "lstat_failed", "path": "control/atom.md", "errno": errno.EACCES}, report["observation"])
        self.assertNotIn("private exception text", diagnostics.getvalue())
        self.assertNotIn(str(self.root), diagnostics.getvalue())
        condition = self.watcher._proof.condition
        with condition:
            self.assertTrue(condition.wait_for(lambda: self.watcher.capture_epoch() is not None, timeout=3))
        self.assertIn("coverage_recovered", [change["event_type"] for change in self.watcher.changes(0)])

    def test_native_ticket_start_defers_archive_index_and_runs_once(self):
        tickets = self.control / "__TKT"
        archive = tickets / "09_archived"
        archive.mkdir(parents=True)
        (archive / "archive.md").touch()
        carrier = tickets / "live.md"
        carrier.touch()
        with patch("ORCHESTRATOR_beta_C68.watcher.Observer") as observer:
            self.watcher.start()
            observer.assert_not_called()
            with patch.object(self.watcher, "_ticket_version", wraps=self.watcher._ticket_version) as version:
                self.watcher.start_ticket_watch()
                self.watcher.start_ticket_watch()
            observer.assert_called_once()
            version.assert_called_once_with(carrier)
            self.assertEqual(("created", [carrier]), self.watcher._ticket_change("created", [carrier]))
            self.assertIsNone(self.watcher._ticket_change("created", [carrier]))
