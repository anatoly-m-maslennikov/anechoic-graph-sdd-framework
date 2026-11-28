"""Capture measured files and exact Realization Graph inventory bindings."""

from pathlib import PurePosixPath

from ..SOURCE_CAPTURE.SOURCE_CAPTURE__shared import (
    _event_path,
    _git_ignored,
    _iter_files,
    _stat_signature,
)
from ..trace_bindings import native_trace_snapshot


def _read_size(path, expected, *, asset=False):
    if _stat_signature(path) != expected:
        raise ValueError(f"Measurement input changed before reading: {path}")
    data = path.read_bytes()
    if _stat_signature(path) != expected:
        raise ValueError(f"Measurement input changed during reading: {path}")
    lines = len(data.splitlines())
    if asset:
        try:
            data.decode("utf-8")
        except UnicodeError:
            lines = None
        if b"\0" in data:
            lines = None
    return len(data), lines


def _test_assets(root, nodes):
    files = {}
    test_packages = sorted(
        (node for node in nodes if node[6] == "Test Package"),
        key=lambda node: len(PurePosixPath(node[3]).parts),
    )
    for key, _, _, relative, _, _, _ in test_packages:
        directory = _event_path(root, relative + "/assets")
        if directory is None or not directory.is_dir():
            continue
        for path in _iter_files(directory):
            files[path.relative_to(root).as_posix()] = (
                key,
                path,
                _stat_signature(path),
            )
    ignored = _git_ignored(root, files)
    return {
        relative: (key, *_read_size(path, signature, asset=True))
        for relative, (key, path, signature) in files.items()
        if relative not in ignored
    }


def _binding_rows(root, nodes, snapshot, ownership):
    package_keys = {n[3]: n[0] for n in nodes if n[1] == "package"}
    module_packages = {n[3]: n[5] for n in nodes if n[1] == "module"}
    rows, _ = native_trace_snapshot(
        root, [node[:6] for node in nodes], strict=True
    )
    bindings = {
        (package, f"{atom}@{version}")
        for owner, _, _, atom, version in rows
        if (package := package_keys.get(owner) or module_packages.get(owner))
    }
    if snapshot is not None:
        for seed, spec in snapshot.packages.items():
            if (entry := ownership.entries.get(seed)) and (
                key := package_keys.get(entry["path"])
            ):
                bindings.add((key, spec.ref))
    return sorted(bindings)


def analysis_inputs(root, nodes, sources, snapshot, ownership):
    assets = _test_assets(root, nodes)
    sizes = {}
    for path, source in sources.items():
        if path in assets or source.status == "read_error":
            continue
        file = _event_path(root, path)
        if file is None:
            raise ValueError(
                f"Measurement source path is outside the Project: {path}"
            )
        sizes[path] = _read_size(file, source.signature)
    return sizes, assets, _binding_rows(root, nodes, snapshot, ownership)
