"""Poll the selected control tree and root files for source changes."""
from pathlib import Path
from queue import Empty, Queue
import os
import stat
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserverVFS


SOURCE_SUFFIXES = frozenset(""".py .sh .js .mjs .ts .svelte .bash .bat .c .cc .cljs .clj .cpp
.cs .cxx .dart .el .ex .exs .fish .fs .go .hs .java .jl .jsx .kt .kts .lua .m
.mm .ml .php .pl .ps1 .r .rb .rs .scala .swift .tsx .zig .zsh""".split())
RESOLUTION_INPUTS = {".gitignore", "pyproject.toml", "uv.lock", "package.json"}
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
        if relevant:
            self.queue.put({"old_path": event.src_path, "new_path": getattr(event, "dest_path", None)})

    def changes(self, timeout):
        try:
            batch = [self.queue.get(timeout=timeout)]
        except Empty:
            return []
        deadline = time.monotonic() + timeout
        while True:
            try:
                batch.append(self.queue.get(timeout=max(0, deadline - time.monotonic())))
            except Empty:
                return batch

    def close(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
