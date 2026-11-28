"""Complete polling cycles in the same event queue as their changes."""

from dataclasses import field
from functools import partial
import os
from pathlib import Path as Path
import stat
from threading import Condition as Condition
from threading import Lock as Lock
from time import monotonic as monotonic
from time import monotonic_ns

from pydantic import ConfigDict, dataclasses
from watchdog.events import (
    DirModifiedEvent,
    FileModifiedEvent,
    FileSystemEvent,
)
from watchdog.observers.api import BaseObserver
from watchdog.observers.polling import PollingEmitter
from watchdog.utils.dirsnapshot import DirectorySnapshot

from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import (
    FenceDiagnostics as FenceDiagnostics,
    report_fence_failure as report_fence_failure,
)
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_poll_coverage import ArchiveCoverage as ArchiveCoverage
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_poll_coverage import PollingProof as PollingProof


@dataclasses.dataclass(
    unsafe_hash=True, config=ConfigDict(strict=True, extra="forbid")
)
class PollComplete(FileSystemEvent):
    event_type: str = field(default="poll_complete", init=False)
    started: int = 0
    clean: bool = False
    archive: bool = False
    roots: tuple[tuple[str, int, int], ...] | None = None
    issue: tuple[str, str, int | None, tuple[str, ...]] | None = None


def _version(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _stat_fields(before, after):
    return tuple(
        name
        for name in ("dev", "ino", "mode", "size", "mtime_ns", "ctime_ns")
        if getattr(before, "st_" + name) != getattr(after, "st_" + name)
    )


class _Snapshot(DirectorySnapshot):
    def mtime(self, path):
        return self.stat_info(path).st_mtime_ns

    def _lost(self, kind, path, errno=None, stat_fields=()):
        self.clean = False
        if self.issue is None:
            self.issue = kind, path, errno, stat_fields

    def walk(self, root):
        if self.skip_directory(root):
            return
        try:
            before = self.stat(root)
        except OSError:
            return
        if not stat.S_ISDIR(before.st_mode):
            self._lost("directory_type_changed", root, stat_fields=("mode",))
            return
        first = self.stat_info(root)
        if _version(before) != _version(first):
            self._lost(
                "directory_before_scan_changed",
                root,
                stat_fields=_stat_fields(first, before),
            )
        yield from super().walk(root)
        try:
            after = self.stat(root)
            if _version(before) != _version(after):
                self._lost(
                    "directory_during_scan_changed",
                    root,
                    stat_fields=_stat_fields(before, after),
                )
        except OSError:
            pass

    def __init__(self, path, recursive, entries, skip_directory):
        self.clean, self.issue = True, None
        self.skip_directory = skip_directory

        def observe(path):
            try:
                return os.lstat(path)
            except OSError as error:
                self._lost("lstat_failed", path, error.errno)
                raise

        def listdir(path):
            try:
                yield from entries(path)
            except OSError as error:
                self._lost("scandir_failed", path, error.errno)
                raise

        super().__init__(
            path, recursive=recursive, stat=observe, listdir=listdir
        )
        self.stat, self.listdir = os.lstat, entries


class _ProofEmitter(PollingEmitter):
    """Extend snapshot and dispatch order in the pinned Watchdog emitter."""

    def __init__(self, *args, entries, coverage, archive, **kwargs):
        super().__init__(*args, **kwargs)
        self._entries = entries
        self._coverage = coverage
        self._archive = archive
        self._take_snapshot = self._take_guarded_snapshot

    def _take_guarded_snapshot(self):
        self._snapshot_started = monotonic_ns()
        skip = (
            self._coverage.skip_installed
            if self._archive
            else self._coverage.skip_foreground_directory
        )
        try:
            return _Snapshot(
                self.watch.path, self.watch.is_recursive, self._entries, skip
            )
        except OSError as error:
            self._coverage.proof.observer_issue(
                self._archive, error.filename or self.watch.path, error.errno
            )
            raise

    def on_thread_start(self):
        proof = self._coverage.proof
        while not proof.closed:
            if proof.sampling_lock.acquire(timeout=0.1):
                try:
                    if not proof.closed:
                        super().on_thread_start()
                        self.baseline_clean = self._snapshot.clean
                        proof.complete(self._completed())
                        return
                finally:
                    proof.sampling_lock.release()
        raise OSError("Watcher stopped before polling baseline")

    def queue_events(self, timeout):
        lock = self._coverage.proof.sampling_lock
        if self.stopped_event.wait(timeout) or not lock.acquire(
            blocking=False
        ):
            return
        try:
            previous = self._snapshot
            super().queue_events(0)
            if self._snapshot is not previous:
                self._queue_version_changes(previous, self._snapshot)
                self.queue_event(self._completed())
        finally:
            lock.release()

    def _completed(self):
        clean = self._snapshot.clean
        roots = (
            self._coverage.snapshot_roots(self._snapshot)
            if clean and self.watch.is_recursive
            else None
        )
        if self._archive and clean:
            self._coverage.proof.remember_archive_sample(
                self.watch.path, self._snapshot_started, self._snapshot
            )
        return PollComplete(
            self.watch.path,
            started=self._snapshot_started,
            clean=clean,
            archive=self._archive,
            roots=roots,
            issue=self._snapshot.issue,
        )

    def _queue_version_changes(self, previous, current):
        """Queue restored-mtime edits at stable paths and preserve moves."""
        for path in previous.paths & current.paths:
            old, new = previous.stat_info(path), current.stat_info(path)
            if (old.st_dev, old.st_ino, old.st_size, old.st_mtime_ns) == (
                new.st_dev,
                new.st_ino,
                new.st_size,
                new.st_mtime_ns,
            ) and (old.st_ctime_ns, old.st_mode) != (
                new.st_ctime_ns,
                new.st_mode,
            ):
                event = (
                    DirModifiedEvent(path)
                    if stat.S_ISDIR(new.st_mode)
                    else FileModifiedEvent(path)
                )
                event.stat_fields = _stat_fields(old, new)
                self.queue_event(event)


def polling_observer(entries, coverage, *, archive=False):
    emitter = partial(
        _ProofEmitter, entries=entries, coverage=coverage, archive=archive
    )
    return BaseObserver(emitter, timeout=0.25)
