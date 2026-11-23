"""Poll the selected control tree and root files for source changes."""
from pathlib import Path
from queue import Empty, Queue
import os
import stat
from threading import Lock
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserverVFS

from .generation import TICKET_ROOTS


SOURCE_SUFFIXES = frozenset(""".py .sh .js .mjs .cjs .ts .svelte .bash .bat .c .cc .cljs .clj .cpp
.cs .cxx .dart .el .ex .exs .fish .fs .go .hs .java .jl .jsx .kt .kts .lua .m
.mm .ml .php .pl .ps1 .r .rb .rs .scala .swift .tsx .zig .zsh""".split())
RESOLUTION_INPUTS = {".gitignore", "pyproject.toml", "uv.lock", "package.json", "tsconfig.json"}
MAX_TRACKED_TICKETS = 16384
EXCLUDED = set(""".anechoic_archive .anechoic_install .anechoic_legacy .anechoic_runtime
.anechoic_tmp .anechoic_anechoic .cache .git .hg .mypy_cache .nox .pytest_cache
.ruff_cache .runtime .svn .tox .venv __pycache__ archive archives build coverage dist
dist-packages env generated gen history node_modules out migration-evidence site-packages
target temp tmp vendor venv""".split())


class SourceWatcher(FileSystemEventHandler):
    def __init__(self, root, control_root, watch_code=False):
        super().__init__()
        self.root = Path(root).absolute()
        self.control_root = Path(control_root).absolute()
        if (not self.control_root.is_relative_to(self.root)
                or not self.control_root.resolve().is_relative_to(self.root.resolve())):
            raise ValueError("Workbench sources must be inside the selected repository")
        self.watch_code = watch_code
        self.known_code = set()
        self.queue = Queue()
        self.observer = None
        self.ticket_observer = None
        self._ticket_lock = Lock()
        self._ticket_versions = {}
        self._ticket_inodes = {}

    def start(self):
        if self.observer is not None:
            return
        if self.watch_code:
            for directory, folders, files in os.walk(self.root, followlinks=False):
                base = Path(directory)
                folders[:] = [name for name in folders if self._code_directory(base / name)]
                for name in files:
                    path = base / name
                    if self._code_path(path):
                        self.known_code.add(path)
        observer = PollingObserverVFS(os.lstat, self._visible_entries, polling_interval=0.25)
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
        self.ticket_observer = self._start_ticket_observer()

    def _start_ticket_observer(self):
        roots = [self.control_root / name for name in TICKET_ROOTS]
        roots = [path for path in roots if path.is_dir() and not path.is_symlink()]
        if not roots:
            return None
        observer = Observer()
        try:
            self._index_existing_tickets(roots)
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
        with self._ticket_lock:
            for root in roots:
                for directory, _, files in os.walk(root, followlinks=False):
                    for name in files:
                        path = Path(directory) / name
                        if self._ticket_path(path):
                            version = self._ticket_version(path)
                            if version is not None:
                                self._remember_ticket(path, version)

    def _visible_entries(self, directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                if (not self.watch_code or not entry.is_dir(follow_symlinks=False)
                        or path.is_relative_to(self.control_root) or self.control_root.is_relative_to(path)
                        or self._code_directory(path)):
                    yield entry

    def _code_directory(self, path):
        relative = path.relative_to(self.root)
        return (not path.is_symlink() and all(
            not part.startswith((".", "_anechoic_")) and part.casefold() not in EXCLUDED
            for part in relative.parts))

    def _code_path(self, path, directory=False):
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            return False
        parts = relative.parts
        folders = parts if directory else parts[:-1]
        if any(part.startswith((".", "_anechoic_")) for part in folders):
            return False
        if any(part.casefold() in EXCLUDED for part in parts):
            return False
        current = path
        while current != self.root:
            if current.is_symlink():
                return False
            current = current.parent
        if directory:
            return False
        if path.name.casefold() in RESOLUTION_INPUTS or path.suffix.casefold() in SOURCE_SUFFIXES:
            return True
        try:
            with path.open("rb") as stream:
                shebang = stream.read(2) == b"#!"
            return shebang or bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        except OSError:
            return path in self.known_code

    def on_any_event(self, event):
        if event.event_type not in {"created", "deleted", "modified", "moved"}:
            return
        paths = [Path(value).absolute() for value in
                 (event.src_path, getattr(event, "dest_path", None)) if value]
        relevant = False
        for path in paths:
            markdown = (not event.is_directory and path.suffix.casefold() == ".md" and
                        (path.is_relative_to(self.control_root) or path.parent == self.root))
            code = self.watch_code and self._code_path(path, event.is_directory)
            if code and path.exists():
                self.known_code.add(path)
            if event.is_directory and self.watch_code:
                code = any(known.is_relative_to(path) for known in self.known_code)
            relevant |= markdown or code
        ticket = not event.is_directory and bool(paths) and all(self._ticket_path(path) for path in paths)
        if not relevant:
            return
        changed = self._ticket_change(event.event_type, paths) if ticket else (event.event_type, paths)
        if changed is not None:
            kind, paths = changed
            self.queue.put({"old_path": str(paths[0]), "new_path": str(paths[1]) if len(paths) > 1 else None,
                            "event_type": kind, "is_directory": event.is_directory})

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
            if all(path in self._ticket_versions and self._ticket_versions[path] == version
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
        previous = self._ticket_versions.pop(path, None)
        if previous and self._ticket_inodes.get(previous[:2]) == path:
            self._ticket_inodes.pop(previous[:2])
        self._ticket_versions[path] = version
        if version is not None and stat.S_ISREG(version[2]):
            self._ticket_inodes[version[:2]] = path
        if len(self._ticket_versions) > MAX_TRACKED_TICKETS:
            oldest = next(iter(self._ticket_versions))
            previous = self._ticket_versions.pop(oldest)
            if previous and self._ticket_inodes.get(previous[:2]) == oldest:
                self._ticket_inodes.pop(previous[:2])

    def changes(self, timeout):
        try:
            batch = [self.queue.get(timeout=timeout)]
        except Empty:
            return []
        deadline = time.monotonic() + min(timeout, 0.02)
        while True:
            try:
                batch.append(self.queue.get(timeout=max(0, deadline - time.monotonic())))
            except Empty:
                return batch

    def close(self):
        if self.ticket_observer is not None:
            self.ticket_observer.stop()
            self.ticket_observer.join()
            self.ticket_observer = None
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
