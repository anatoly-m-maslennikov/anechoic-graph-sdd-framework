"""Complete polling cycles in the same event queue as their changes."""

from dataclasses import field
from functools import partial
import os
from pathlib import Path
import stat
from threading import Condition, Lock
from time import monotonic, monotonic_ns

from pydantic import ConfigDict, dataclasses
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEvent
from watchdog.observers.api import BaseObserver
from watchdog.observers.polling import PollingEmitter
from watchdog.utils.dirsnapshot import DirectorySnapshot

from .watcher_diagnostics import FenceDiagnostics, report_fence_failure


@dataclasses.dataclass(unsafe_hash=True, config=ConfigDict(strict=True, extra="forbid"))
class PollComplete(FileSystemEvent):
    event_type: str = field(default="poll_complete", init=False)
    started: int = 0
    clean: bool = False
    archive: bool = False
    roots: tuple[tuple[str, int, int], ...] | None = None
    issue: tuple[str, str, int | None, tuple[str, ...]] | None = None


def _version(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _stat_fields(before, after):
    return tuple(name for name in ("dev", "ino", "mode", "size", "mtime_ns", "ctime_ns")
                 if getattr(before, "st_" + name) != getattr(after, "st_" + name))


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
            self._lost("directory_before_scan_changed", root, stat_fields=_stat_fields(first, before))
        yield from super().walk(root)
        try:
            after = self.stat(root)
            if _version(before) != _version(after):
                self._lost("directory_during_scan_changed", root, stat_fields=_stat_fields(before, after))
        except OSError:
            pass

    def __init__(self, path, recursive, entries, skip_directory):
        self.clean = True
        self.issue = None
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

        super().__init__(path, recursive=recursive, stat=observe, listdir=listdir)


class _ProofEmitter(PollingEmitter):
    """Extend the snapshot and dispatch order of the pinned Watchdog emitter."""

    def __init__(self, *args, entries, coverage, archive, **kwargs):
        super().__init__(*args, **kwargs)
        self._entries = entries
        self._coverage = coverage
        self._archive = archive
        self._take_snapshot = self._take_guarded_snapshot

    def _take_guarded_snapshot(self):
        self._snapshot_started = monotonic_ns()
        skip = self._coverage.skip_installed if self._archive else self._coverage.skip_foreground_directory
        try:
            return _Snapshot(self.watch.path, self.watch.is_recursive, self._entries, skip)
        except OSError as error:
            self._coverage.proof.observer_issue(self._archive, error.filename or self.watch.path, error.errno)
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
        if self.stopped_event.wait(timeout) or not lock.acquire(blocking=False):
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
        roots = self._coverage.snapshot_roots(self._snapshot) if clean and self.watch.is_recursive else None
        if self._archive and clean:
            self._coverage.proof.remember_archive_sample(self.watch.path, self._snapshot_started, self._snapshot)
        return PollComplete(self.watch.path, started=self._snapshot_started, clean=clean,
                            archive=self._archive, roots=roots, issue=self._snapshot.issue)

    def _queue_version_changes(self, previous, current):
        """Queue edits with restored mtime at stable paths and preserve move events."""
        for path in previous.paths & current.paths:
            old, new = previous.stat_info(path), current.stat_info(path)
            if ((old.st_dev, old.st_ino, old.st_size, old.st_mtime_ns)
                    == (new.st_dev, new.st_ino, new.st_size, new.st_mtime_ns)
                    and (old.st_ctime_ns, old.st_mode) != (new.st_ctime_ns, new.st_mode)):
                event = DirModifiedEvent(path) if stat.S_ISDIR(new.st_mode) else FileModifiedEvent(path)
                event.stat_fields = _stat_fields(old, new)
                self.queue_event(event)


def polling_observer(entries, coverage, *, archive=False):
    emitter = partial(_ProofEmitter, entries=entries, coverage=coverage, archive=archive)
    return BaseObserver(emitter, timeout=0.25)


class PollingProof:
    def __init__(self, root=None):
        self.condition = Condition()
        self.sampling_lock = Lock()
        self.closed = False
        self._revisions = [0, 0]
        self._losses = [0, 0]
        self._polls = ({}, {})
        self._archive_roots = [None, None]
        self._archive_sample = None
        self._diagnostics = FenceDiagnostics(root)

    def archive_roots(self):
        with self.condition:
            roots = self._archive_roots[1]
            if roots is None:
                roots = self._archive_roots[0]
            return tuple(path for path, _, _ in roots or ())

    def ready(self, observer, *, archive):
        return (not self.closed and observer is not None and observer.is_alive() and bool(observer.emitters)
                and all(emitter.is_alive() and self._polls[archive].get(emitter.watch.path, emitter.baseline_clean)
                        for emitter in observer.emitters))

    def epoch(self, observer, *, archive, trace=False, dispatched=False):
        with self.condition:
            if self.ready(observer, archive=archive):
                if dispatched and any(self._polls[archive].get(emitter.watch.path) != emitter._snapshot_started
                                      for emitter in observer.emitters):
                    return None
                if trace:
                    self._diagnostics.start(archive)
                return observer, self._revisions[archive], self._losses[archive]
        return None

    def fence(self, observer, epoch, *, archive, timeout, run_id=None, replay=False):
        started = monotonic_ns()
        deadline = None if timeout is None else monotonic() + timeout
        with self.condition:
            stable, reason = self._wait_fence(observer, epoch, archive, started, deadline, replay)
            record = None if stable is True else self._diagnostics.failure(
                archive, run_id, reason, started, epoch, self._revisions[archive], self._losses[archive])
        report_fence_failure(record)
        return stable

    def _wait_fence(self, observer, epoch, archive, started, deadline, replay):
        if epoch is None or observer is not epoch[0]:
            return None, "baseline_unavailable" if epoch is None else "observer_replaced"
        _, revision, losses = epoch
        while self.ready(observer, archive=archive) and losses == self._losses[archive]:
            if not replay and self._revisions[archive] != revision:
                return False, "source_changed"
            if all(self._polls[archive].get(emitter.watch.path, 0) >= started for emitter in observer.emitters):
                return True, None
            remaining = 0.25 if deadline is None else deadline - monotonic()
            if remaining <= 0:
                return None, "poll_timeout"
            self.condition.wait(min(remaining, 0.25))
        if losses != self._losses[archive]:
            return None, "coverage_lost"
        if self.closed or observer is None or not observer.is_alive():
            return None, "observer_stopped"
        return None, "emitter_unavailable"

    def complete(self, event, on_recovery=None):
        with self.condition:
            previous = self._polls[event.archive].get(event.src_path)
            self._polls[event.archive][event.src_path] = event.started if event.clean else 0
            if not event.clean:
                self._losses[event.archive] += 1
                if event.issue is not None:
                    kind, path, errno, fields = event.issue
                    self._diagnostics.observe(event.archive, "loss", kind, path, errno=errno, stat_fields=fields)
            elif event.roots is not None and self._archive_roots[event.archive] != event.roots:
                self._archive_roots[event.archive] = event.roots
                self._revisions[event.archive] += 1
                self._diagnostics.observe(event.archive, "change", "archive_roots_changed", event.src_path)
            if previous == 0 and event.clean and on_recovery is not None:
                on_recovery()
            self.condition.notify_all()

    def observer_issue(self, archive, path, errno):
        with self.condition:
            self._diagnostics.observe(archive, "loss", "snapshot_failed", path, errno=errno)

    def remember_archive_sample(self, source, started, snapshot):
        with self.condition:
            if not self.closed:
                self._archive_sample = (source, started, snapshot)

    def sampled_archive_carriers(self, since, carriers):
        with self.condition:
            if self._archive_sample is None:
                return None
            source, started, snapshot = self._archive_sample
            if started < since or self._polls[True].get(source, 0) < started:
                return None
            try:
                return all(stat.S_ISREG(snapshot.stat_info(path).st_mode) for path in carriers)
            except KeyError:
                return False

    def change(self, foreground, archive, event, paths):
        with self.condition:
            self._revisions[0] += foreground
            self._revisions[1] += archive
            for lane, changed in enumerate((foreground, archive)):
                if changed:
                    self._diagnostics.observe(lane, "change", event.event_type, paths[0],
                                              destination=paths[1] if len(paths) > 1 else None,
                                              stat_fields=getattr(event, "stat_fields", ()))
            self.condition.notify_all()

    def close(self):
        with self.condition:
            self.closed = True
            self._archive_sample = None
            self.condition.notify_all()


class ArchiveCoverage:
    def __init__(self, root, control_root, proof, deferred):
        self.root = root
        self.control = control_root
        self.installed = self.control / "000_ANECHOIC_framework"
        self.proof = proof
        self.deferred = deferred

    def snapshot_roots(self, snapshot):
        if not self.deferred:
            return None
        roots = []
        for name in snapshot.paths:
            if os.path.basename(name) != "09_archived" or not snapshot.isdir(name):
                continue
            path = Path(name)
            if path == self.root_for(path):
                roots.append((path.relative_to(self.root).as_posix(), *snapshot.inode(name)))
        return tuple(sorted(roots))

    def root_for(self, path):
        if not path.is_relative_to(self.control):
            return None
        parts = path.relative_to(self.control).parts
        if "09_archived" in parts and not path.is_relative_to(self.installed):
            return self.control.joinpath(*parts[:parts.index("09_archived") + 1])
        return None

    def skip_foreground_directory(self, directory):
        if not self.deferred:
            return False
        path = Path(directory)
        return path == self.root_for(path) or path == self.installed

    def skip_installed(self, directory):
        return Path(directory) == self.installed

    def entries(self, directory):
        path = Path(directory)
        if self.proof.closed or path.is_relative_to(self.installed):
            return
        archived = self.root_for(path)
        with os.scandir(directory) as entries:
            for entry in entries:
                if archived is not None or entry.is_dir(follow_symlinks=False):
                    yield entry

    def source_change(self, event, paths):
        foreground = archive = False
        tree_change = event.is_directory and event.event_type != "modified"
        for path in paths:
            if self.deferred and path.is_relative_to(self.installed):
                continue
            archived = self.root_for(path)
            if self.deferred and archived is not None:
                archive = True
                foreground |= archived == path and (tree_change or not event.is_directory)
            elif path.is_relative_to(self.control):
                foreground = True
                archive |= tree_change
            elif path.parent == self.root and path.suffix.casefold() == ".md":
                foreground = True
            elif path == self.root and tree_change:
                foreground = archive = True
        if foreground or archive:
            self.proof.change(foreground, archive, event, paths)
        return foreground
