"""Discover native carriers and measure the foreground scan when enabled."""

from hashlib import sha256
from pathlib import Path
from threading import Lock
from time import perf_counter_ns
from typing import Literal

from .ADAPTERS_C30__pub import CEILINGS, LimitReached, ReadContext
from .native_carrier_placement__pub import ARCHIVE_DIRECTORY, project_goal_filename
from .startup_timing import mark_startup_timing, startup_timing_enabled


type ScanMode = Literal["foreground_capture", "foreground_hashes"]


class StartupReadContext(ReadContext):
    def __init__(self, root: Path, mode: ScanMode):
        super().__init__(roots=[str(root)], limits=dict(CEILINGS))
        self.mode = mode
        self.census_ns = 0
        self.carrier_count = 0
        self._timings = {"guarded_read_ns": 0, "stream_ns": 0, "sha256_ns": 0}
        self._timing_lock = Lock()

    def _record(self, key, start):
        elapsed = perf_counter_ns() - start
        with self._timing_lock:
            self._timings[key] += elapsed

    def read(self, path, **kwargs):
        start = perf_counter_ns()
        try:
            return super().read(path, **kwargs)
        finally:
            self._record("guarded_read_ns", start)

    def _read_bytes(self, stream, size):
        start = perf_counter_ns()
        try:
            return super()._read_bytes(stream, size)
        finally:
            self._record("stream_ns", start)

    def digest(self, raw):
        start = perf_counter_ns()
        try:
            return sha256(raw).hexdigest()
        finally:
            self._record("sha256_ns", start)

    def emit_scan_metrics(self):
        mark_startup_timing("scan_metrics", mode=self.mode, census_ns=self.census_ns,
                            carrier_count=self.carrier_count, bytes_read=self.bytes_read, **self._timings)


def startup_reader(root: Path, mode: ScanMode | None = None) -> ReadContext:
    if mode is not None and startup_timing_enabled():
        return StartupReadContext(root, mode)
    return ReadContext(roots=[str(root)], limits=dict(CEILINGS))


def root_carriers(reader, selection, *, remember=True):
    return [path for path in reader.inventory_shallow(selection.root, remember=remember)
            if path == selection.manifest_path or project_goal_filename(path.name)]


def _carrier_paths(reader, selection, defer_archives, archive_roots):
    installed = selection.control_root / "000_ANECHOIC_framework"
    if archive_roots is not None:
        paths = set()
        for root in archive_roots:
            paths.update(path for path in reader.inventory(root) if path.suffix == ".md")
            if len(paths) > reader.limits["max_candidates"]:
                raise LimitReached("max_candidates")
        return sorted(paths)

    def prune(path):
        if path == installed:
            return True
        if path.name == ARCHIVE_DIRECTORY:
            defer_archives.add(path)
            return True
        return False

    paths = [path for path in reader.inventory(selection.control_root,
                                               prune=prune if defer_archives is not None else None)
             if path.suffix == ".md" and not path.is_relative_to(installed)]
    return sorted(set(paths + root_carriers(reader, selection)))


def full_carriers(reader, selection, defer_archives=None, archive_roots=None):
    if not isinstance(reader, StartupReadContext):
        return _carrier_paths(reader, selection, defer_archives, archive_roots)
    mark_startup_timing("scan_started", mode=reader.mode)
    start = perf_counter_ns()
    paths = _carrier_paths(reader, selection, defer_archives, archive_roots)
    reader.census_ns = perf_counter_ns() - start
    reader.carrier_count = len(paths)
    if reader.mode == "foreground_capture":
        mark_startup_timing("non_archived_load_started", mode=reader.mode)
    return paths
