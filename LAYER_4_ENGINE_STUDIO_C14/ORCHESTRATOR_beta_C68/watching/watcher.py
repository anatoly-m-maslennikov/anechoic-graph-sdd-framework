"""Poll the selected control tree and root files for source changes."""

from pathlib import Path
from queue import Empty, Queue
import os as os
import stat
from threading import Lock
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ORCHESTRATOR_beta_C68.generation.generation import TICKET_ROOTS
from ORCHESTRATOR_beta_C68.watching.retry import COVERAGE_RECOVERED
from ORCHESTRATOR_beta_C68.watching.watcher_code import WatcherCode
from ORCHESTRATOR_beta_C68.watching.watcher_event_routing import WatcherEventRouting
from ORCHESTRATOR_beta_C68.watching.poll_coverage.poll_coverage__shared import (
    ArchiveCoverage,
    PollingProof,
)
from ORCHESTRATOR_beta_C68.watching.watcher_poll import polling_observer
from ORCHESTRATOR_beta_C68.watching.watcher_receipts import WriteReceipts


MAX_TRACKED_TICKETS = 16384


def _observer_running(observer):
    return (
        observer is not None
        and observer.is_alive()
        and bool(observer.emitters)
        and all(emitter.is_alive() for emitter in observer.emitters)
    )


class SourceWatcher(WatcherEventRouting, WatcherCode, FileSystemEventHandler):
    def __init__(
        self, root, control_root, watch_code=False, *, defer_archives=False
    ):
        super().__init__()
        self.root = Path(root).absolute()
        self.control_root = Path(control_root).absolute()
        if not self.control_root.is_relative_to(
            self.root
        ) or not self.control_root.resolve().is_relative_to(
            self.root.resolve()
        ):
            raise ValueError(
                "Workbench sources must be inside the selected repository"
            )
        self.watch_code = watch_code
        self.defer_archives = defer_archives
        self.known_code = set()
        self.queue = Queue()
        self.observer = None
        self.archive_observer = None
        self.ticket_observer = None
        self._proof = PollingProof(self.root)
        self.managed_write = self._proof.sampling_lock
        self._archive_lock = Lock()
        self._event_lock = Lock()
        self._foreground_events = 0
        self._observer_retry_at = 0
        self._archives = ArchiveCoverage(
            self.root, self.control_root, self._proof, defer_archives
        )
        self._ticket_lock = Lock()
        self._ticket_versions = {}
        self._ticket_inodes = {}
        self._seeded_tickets = set()
        self._receipts = WriteReceipts(
            self.root, self._archives, MAX_TRACKED_TICKETS
        )

    def start(self):
        with self._archive_lock:
            if self._proof.closed or self.observer is not None:
                return
            self._start_foreground()
        if not self.defer_archives:
            self.start_ticket_watch()

    def _start_foreground(self):
        if self.watch_code and not self._seed_known_code():
            return
        observer = polling_observer(self._visible_entries, self._archives)
        try:
            observer.schedule(
                self,
                str(self.root if self.watch_code else self.control_root),
                recursive=True,
            )
            if not self.watch_code and self.control_root != self.root:
                observer.schedule(self, str(self.root), recursive=False)
            observer.start()
        except BaseException:
            observer.stop()
            if observer.is_alive():
                observer.join()
            raise
        self.observer = observer

    def restore_foreground(self):
        "Reestablish polling after an emitter stopped, then request reconciliation."
        observer = self.observer
        if _observer_running(observer):
            return
        if time.monotonic() < self._observer_retry_at:
            return
        with self._archive_lock:
            if self._proof.closed:
                return
            if observer is not None:
                observer.stop()
                observer.join()
                self.observer = None
            try:
                self._start_foreground()
            except OSError, RuntimeError:
                self._observer_retry_at = time.monotonic() + 1
                return
            self._queue_recovery()

    def start_ticket_watch(self):
        "Start optional native notifications after the foreground in phased mode."
        with self._archive_lock:
            if not self._proof.closed and self.ticket_observer is None:
                self.ticket_observer = self._start_ticket_observer()

    def archive_roots(self):
        return self._proof.archive_roots()

    def has_archive_roots(self):
        return bool(self.archive_roots())

    def watch_archives(self):
        "Start the archive baseline on the background lane before it captures."
        with self._archive_lock:
            if self._proof.closed or not self.defer_archives:
                return False
            if _observer_running(self.archive_observer):
                return self._proof.ready(self.archive_observer, archive=True)
            if self.archive_observer is not None:
                self.archive_observer.stop()
                self.archive_observer.join()
                self.archive_observer = None
            observer = polling_observer(
                self._archives.entries, self._archives, archive=True
            )
            try:
                observer.schedule(self, str(self.control_root), recursive=True)
                observer.start()
            except OSError, RuntimeError:
                observer.stop()
                if observer.is_alive():
                    observer.join()
                return False
            self.archive_observer = observer
            return self._proof.ready(observer, archive=True)

    def capture_epoch(self, *, archive=False, trace=False, dispatched=False):
        observer = self.archive_observer if archive else self.observer
        return self._proof.epoch(
            observer, archive=archive, trace=trace, dispatched=dispatched
        )

    def capture_fence(self, epoch, *, archive=False, timeout=45, run_id=None):
        "Wait for a normal poll that began after capture and dispatched its changes."
        observer = self.archive_observer if archive else self.observer
        return self._proof.fence(
            observer, epoch, archive=archive, timeout=timeout, run_id=run_id
        )

    def replay_fence(self, epoch, *, timeout=45, run_id=None):
        "Wait for post-capture polling to dispatch changes to the foreground queue."
        return self._proof.fence(
            self.observer,
            epoch,
            archive=False,
            timeout=timeout,
            run_id=run_id,
            replay=True,
        )

    def foreground_events(self):
        with self._event_lock:
            return self._foreground_events

    def on_poll_complete(self, event):
        self._proof.complete(
            event, None if event.archive else self._queue_recovery
        )

    def _queue_recovery(self):
        self.queue.put(
            {
                "old_path": str(self.control_root),
                "new_path": None,
                "event_type": COVERAGE_RECOVERED,
                "is_directory": True,
            }
        )

    def _start_ticket_observer(self):
        roots = [self.control_root / name for name in TICKET_ROOTS]
        roots = [
            path for path in roots if path.is_dir() and not path.is_symlink()
        ]
        if not roots:
            return None
        observer = Observer()
        try:
            self._index_existing_tickets(roots)
            if self._proof.closed:
                return None
            for root in roots:
                observer.schedule(self, str(root), recursive=True)
            observer.start()
        except OSError, RuntimeError:
            observer.stop()
            if observer.is_alive():
                observer.join()
            return None
        return observer

    def _event_path(self, value):
        return Path(value)

    def _walk(self, *args, **kwargs):
        return os.walk(*args, **kwargs)

    def _scandir(self, directory):
        return os.scandir(directory)

    def on_any_event(self, event):
        if event.event_type not in {"created", "deleted", "modified", "moved"}:
            return
        with self._event_lock:
            self._queue_event(event)

    def _queue_event(self, event):
        paths = [
            Path(value).absolute()
            for value in (event.src_path, getattr(event, "dest_path", None))
            if value
        ]
        foreground = self._archives.source_change(event, paths)
        if event.is_directory and event.event_type == "modified":
            return
        if event.is_directory and all(
            any(
                path.is_relative_to(self.control_root / directory)
                for directory in TICKET_ROOTS
            )
            for path in paths
        ):
            foreground = False
        foreground, relevant = self._event_relevance(event, paths, foreground)
        ticket = (
            not event.is_directory
            and bool(paths)
            and all(self._ticket_path(path) for path in paths)
        )
        if not relevant:
            return
        changed = (
            self._ticket_change(event.event_type, paths)
            if ticket
            else (event.event_type, paths)
        )
        if changed is not None:
            kind, paths = changed
            if event.is_directory and self.control_root in paths:
                kind = COVERAGE_RECOVERED
            self.queue.put(
                {
                    "old_path": str(paths[0]),
                    "new_path": str(paths[1]) if len(paths) > 1 else None,
                    "event_type": kind,
                    "is_directory": event.is_directory,
                    "observed_at": time.time(),
                }
            )
            self._foreground_events += foreground

    def _ticket_path(self, path):
        if not path.is_relative_to(self.control_root) or path.suffix != ".md":
            return False
        parts = path.relative_to(self.control_root).parts
        return len(parts) > 1 and parts[0] in TICKET_ROOTS

    def _remember_ticket(self, path, version):
        self._seeded_tickets.discard(path)
        previous = self._ticket_versions.pop(path, None)
        if previous and self._ticket_inodes.get(previous[:2]) == path:
            self._ticket_inodes.pop(previous[:2])
        self._ticket_versions[path] = version
        if version is not None and stat.S_ISREG(version[2]):
            self._ticket_inodes[version[:2]] = path
        if len(self._ticket_versions) > MAX_TRACKED_TICKETS:
            oldest = next(iter(self._ticket_versions))
            self._seeded_tickets.discard(oldest)
            previous = self._ticket_versions.pop(oldest)
            if previous and self._ticket_inodes.get(previous[:2]) == oldest:
                self._ticket_inodes.pop(previous[:2])

    def acknowledge(self, effects, *, archive_epoch=None):
        self._receipts.acknowledge(effects, archive_epoch)

    def changes(self, timeout):
        """Read a batch through a fixed queue position as its sole consumer."""
        try:
            batch = [self.queue.get(timeout=timeout)]
        except Empty:
            batch = []
        deadline = time.monotonic() + min(timeout, 0.02)
        while batch and (remaining := deadline - time.monotonic()) > 0:
            try:
                batch.append(self.queue.get(timeout=remaining))
            except Empty:
                break
        batch.extend(
            self.queue.get_nowait() for _ in range(self.queue.qsize())
        )
        return self._receipts.filter(batch, self.capture_epoch(archive=True))

    def close(self):
        self._proof.close()
        with self._archive_lock:
            for name in ("ticket_observer", "archive_observer", "observer"):
                if (observer := getattr(self, name)) is not None:
                    observer.stop()
                    observer.join()
                    setattr(self, name, None)
