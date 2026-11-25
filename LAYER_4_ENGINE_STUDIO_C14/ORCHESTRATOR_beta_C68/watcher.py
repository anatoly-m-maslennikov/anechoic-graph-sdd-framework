"""Poll the selected control tree and root files for source changes."""
from pathlib import Path
from queue import Empty, Queue
import os
import stat
from threading import Lock
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .generation import TICKET_ROOTS
from .retry import COVERAGE_RECOVERED
from .watcher_code import WatcherCode
from .watcher_poll import ArchiveCoverage, PollingProof, polling_observer
from .watcher_receipts import WriteReceipts


MAX_TRACKED_TICKETS = 16384


class SourceWatcher(WatcherCode, FileSystemEventHandler):
    def __init__(self, root, control_root, watch_code=False, *, defer_archives=False):
        super().__init__()
        self.root = Path(root).absolute()
        self.control_root = Path(control_root).absolute()
        if (not self.control_root.is_relative_to(self.root)
                or not self.control_root.resolve().is_relative_to(self.root.resolve())):
            raise ValueError("Workbench sources must be inside the selected repository")
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
        self._archives = ArchiveCoverage(self.root, self.control_root, self._proof, defer_archives)
        self._ticket_lock = Lock()
        self._ticket_versions = {}
        self._ticket_inodes = {}
        self._seeded_tickets = set()
        self._receipts = WriteReceipts(self.root, self._archives, MAX_TRACKED_TICKETS)

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
            observer.schedule(self, str(self.root if self.watch_code else self.control_root), recursive=True)
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
        """Reestablish polling after an emitter stopped, then request reconciliation."""
        observer = self.observer
        if (observer is not None and observer.is_alive() and observer.emitters
                and all(emitter.is_alive() for emitter in observer.emitters)):
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
            except (OSError, RuntimeError):
                self._observer_retry_at = time.monotonic() + 1
                return
            self._queue_recovery()

    def start_ticket_watch(self):
        """Start optional native notifications after the foreground in phased mode."""
        with self._archive_lock:
            if not self._proof.closed and self.ticket_observer is None:
                self.ticket_observer = self._start_ticket_observer()

    def archive_roots(self):
        return self._proof.archive_roots()

    def has_archive_roots(self):
        return bool(self.archive_roots())

    def watch_archives(self):
        """Start the archive baseline on the background lane before it captures."""
        with self._archive_lock:
            if self._proof.closed or not self.defer_archives:
                return False
            if self.archive_observer is not None:
                return self._proof.ready(self.archive_observer, archive=True)
            observer = polling_observer(self._archives.entries, self._archives, archive=True)
            try:
                observer.schedule(self, str(self.control_root), recursive=True)
                observer.start()
            except (OSError, RuntimeError):
                observer.stop()
                if observer.is_alive():
                    observer.join()
                return False
            self.archive_observer = observer
            return self._proof.ready(observer, archive=True)

    def capture_epoch(self, *, archive=False, trace=False, dispatched=False):
        observer = self.archive_observer if archive else self.observer
        return self._proof.epoch(observer, archive=archive, trace=trace, dispatched=dispatched)

    def capture_fence(self, epoch, *, archive=False, timeout=45, run_id=None):
        """Wait for a normal poll that began after capture and dispatched its changes."""
        observer = self.archive_observer if archive else self.observer
        return self._proof.fence(observer, epoch, archive=archive, timeout=timeout, run_id=run_id)

    def replay_fence(self, epoch, *, timeout=45, run_id=None):
        """Wait for post-capture polling to dispatch changes to the foreground queue."""
        return self._proof.fence(self.observer, epoch, archive=False, timeout=timeout,
                                 run_id=run_id, replay=True)

    def foreground_events(self):
        with self._event_lock:
            return self._foreground_events

    def on_poll_complete(self, event):
        self._proof.complete(event, None if event.archive else self._queue_recovery)

    def _queue_recovery(self):
        self.queue.put({"old_path": str(self.control_root), "new_path": None, "event_type": COVERAGE_RECOVERED,
                        "is_directory": True})

    def _start_ticket_observer(self):
        roots = [self.control_root / name for name in TICKET_ROOTS]
        roots = [path for path in roots if path.is_dir() and not path.is_symlink()]
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
        except (OSError, RuntimeError):
            observer.stop()
            if observer.is_alive():
                observer.join()
            return None
        return observer

    def _index_existing_tickets(self, roots):
        for root in roots:
            for directory, folders, files in os.walk(root, followlinks=False):
                if self._proof.closed:
                    return
                if self.defer_archives and "09_archived" in folders:
                    folders.remove("09_archived")
                for name in files:
                    path = Path(directory) / name
                    if self._ticket_path(path) and (version := self._ticket_version(path)) is not None:
                        with self._ticket_lock:
                            if path not in self._ticket_versions:
                                self._remember_ticket(path, version)
                                if self.defer_archives:
                                    self._seeded_tickets.add(path)

    def _visible_entries(self, directory):
        if self._proof.closed:
            return
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                if (not self.watch_code or not entry.is_dir(follow_symlinks=False)
                        or path.is_relative_to(self.control_root) or self.control_root.is_relative_to(path)
                        or self._code_directory(path)):
                    yield entry

    def on_any_event(self, event):
        if event.event_type not in {"created", "deleted", "modified", "moved"}:
            return
        with self._event_lock:
            self._queue_event(event)

    def _queue_event(self, event):
        paths = [Path(value).absolute() for value in
                 (event.src_path, getattr(event, "dest_path", None)) if value]
        foreground = self._archives.source_change(event, paths)
        if event.is_directory and event.event_type == "modified":
            return
        if event.is_directory and all(any(path.is_relative_to(self.control_root / directory)
                                          for directory in TICKET_ROOTS) for path in paths):
            foreground = False
        relevant = foreground
        for path in paths:
            markdown = (not event.is_directory and path.suffix.casefold() == ".md" and
                        (path.is_relative_to(self.control_root) or path.parent == self.root))
            code = False
            if event.is_directory and self.watch_code and path.is_relative_to(self.root):
                code = self._code_directory(path) or any(known.is_relative_to(path) for known in self.known_code)
            elif self.watch_code and not event.is_directory:
                current_code = self._code_path(path) and path.exists()
                code = current_code or path in self.known_code
                if current_code:
                    self.known_code.add(path)
                else:
                    self.known_code.discard(path)
            if code and self._archives.root_for(path) is None:
                foreground = True
            boundary = event.is_directory and (path == self.control_root or path == self._archives.root_for(path))
            relevant |= markdown or code or boundary
        ticket = not event.is_directory and bool(paths) and all(self._ticket_path(path) for path in paths)
        if not relevant:
            return
        changed = self._ticket_change(event.event_type, paths) if ticket else (event.event_type, paths)
        if changed is not None:
            kind, paths = changed
            self.queue.put({"old_path": str(paths[0]), "new_path": str(paths[1]) if len(paths) > 1 else None,
                            "event_type": kind, "is_directory": event.is_directory, "observed_at": time.time()})
            self._foreground_events += foreground

    def _ticket_path(self, path):
        if not path.is_relative_to(self.control_root) or path.suffix != ".md":
            return False
        parts = path.relative_to(self.control_root).parts
        return len(parts) > 1 and parts[0] in TICKET_ROOTS

    def _ticket_change(self, kind, paths):
        with self._ticket_lock:
            try:
                current = {path: self._ticket_version(path) for path in paths}
                if len(paths) == 1 and kind in {"created", "modified"} and (version := current[paths[0]]):
                    previous = self._ticket_inodes.get(version[:2])
                    if previous is not None and previous != paths[0] and self._ticket_version(previous) is None:
                        current[previous] = None
                        paths = [previous, paths[0]]
                        kind = "moved"
            except OSError:
                return kind, paths
            if all(path not in self._seeded_tickets and path in self._ticket_versions
                   and self._ticket_versions[path] == version
                   for path, version in current.items()):
                return None
            for path, version in current.items():
                self._remember_ticket(path, version)
            return kind, paths

    @staticmethod
    def _ticket_version(path):
        try:
            info = path.lstat()
        except FileNotFoundError:
            return None
        return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns

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
        batch.extend(self.queue.get_nowait() for _ in range(self.queue.qsize()))
        return self._receipts.filter(batch, self.capture_epoch(archive=True))

    def close(self):
        self._proof.close()
        with self._archive_lock:
            for name in ("ticket_observer", "archive_observer", "observer"):
                if (observer := getattr(self, name)) is not None:
                    observer.stop()
                    observer.join()
                    setattr(self, name, None)
