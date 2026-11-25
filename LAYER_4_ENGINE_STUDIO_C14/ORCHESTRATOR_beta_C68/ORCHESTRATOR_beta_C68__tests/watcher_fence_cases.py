"""Exercise watcher triggers and the Orchestrator's Kernel admission paths."""

from contextlib import redirect_stderr
import errno
from io import StringIO
import json
import tempfile
import time
import unittest
import os
from pathlib import Path
from threading import Event, Thread
from unittest.mock import patch

from watchdog.events import DirCreatedEvent, DirDeletedEvent

from ORCHESTRATOR_beta_C68.watcher import SourceWatcher
from ORCHESTRATOR_beta_C68.watcher_poll import PollComplete



class CaptureFenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / "control"
        self.control.mkdir()
        self.watcher = SourceWatcher(self.root, self.control, defer_archives=True)
        self.addCleanup(self.watcher.close)

    def test_fence_detects_restored_mtime_and_leaves_event_queued(self):
        carrier = self.control / "atom.md"
        carrier.write_text("before")
        self.watcher.start()
        epoch = self.watcher.capture_epoch(trace=True)
        self.assertIsNotNone(epoch)
        diagnostics = StringIO()
        with redirect_stderr(diagnostics):
            self.assertTrue(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32))
        self.assertEqual("", diagnostics.getvalue())
        before = carrier.stat()
        carrier.write_text("edited")
        os.utime(carrier, ns=(before.st_atime_ns, before.st_mtime_ns))
        with redirect_stderr(diagnostics):
            self.assertIs(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32), False)
        report = json.loads(diagnostics.getvalue())
        self.assertEqual(("watcher_fence_failed", "foreground", "source_changed", "WARNING", "a" * 32),
                         (report["code"], report["phase"], report["reason"], report["severity"], report["run_id"]))
        self.assertEqual({"kind": "modified", "path": "control/atom.md", "stat_fields": ["ctime_ns"]},
                         report["observation"])
        self.assertGreaterEqual(report["wait_ms"], 0)
        with patch.dict(os.environ, ANECHOIC_LOG_LEVEL="ERROR"), redirect_stderr(StringIO()) as filtered:
            self.assertIs(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32), False)
        self.assertEqual("", filtered.getvalue())
        self.assertIn(str(carrier), [change["old_path"] for change in self.watcher.changes(1)])

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
        with patch("ORCHESTRATOR_beta_C68.watcher_poll.os.lstat", side_effect=denied), redirect_stderr(diagnostics):
            self.assertIsNone(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32))
        report = json.loads(diagnostics.getvalue())
        self.assertEqual("coverage_lost", report["reason"])
        self.assertEqual({"kind": "lstat_failed", "path": "control/atom.md", "errno": errno.EACCES}, report["observation"])
        self.assertNotIn("private exception text", diagnostics.getvalue())
        self.assertNotIn(str(self.root), diagnostics.getvalue())

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
