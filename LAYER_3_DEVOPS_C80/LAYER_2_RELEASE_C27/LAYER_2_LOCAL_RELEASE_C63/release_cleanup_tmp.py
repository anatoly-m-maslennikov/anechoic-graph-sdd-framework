"""Expire old scratch files after a successful Local Release."""

import errno
import os
from pathlib import Path
import stat
import time

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import INSTALLATION_LOCK_PATH, _owned_directory

from .local_release_state import open_artifacts


_TMP = Path(".anechoic_tmp")
_DAY_NS = 24 * 60 * 60 * 10**9
_KEEP = {
    INSTALLATION_LOCK_PATH.relative_to(_TMP),
    Path("atom_lifecycle/write.lock"),
    Path("cache/uv"),
    Path("rmed-base-revise"),
    Path("workbench/playwright-browsers"),
    Path("workbench/extensions"),
}


def _remove_empty(directory, name, info):
    current = os.stat(name, dir_fd=directory, follow_symlinks=False)
    if not os.path.samestat(info, current):
        return 0
    try:
        os.rmdir(name, dir_fd=directory)
    except OSError as error:
        if error.errno != errno.ENOTEMPTY:
            raise
        return 0
    return 1


def _prune(directory: int, relative: Path, cutoff: int, device: int, blocked: list[str], keep) -> int:
    removed = 0
    for name in os.listdir(directory):
        child = relative / name
        if child in keep:
            continue
        try:
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if info.st_dev != device:
                continue
            report = child.parent == Path("test_reports") and child.suffix == ".json"
            old = info.st_mtime_ns < (cutoff - 5 * _DAY_NS if report else cutoff)
            if stat.S_ISDIR(info.st_mode):
                flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                nested = os.open(name, flags, dir_fd=directory)
                try:
                    if not os.path.samestat(info, os.fstat(nested)):
                        continue
                    removed += _prune(nested, child, cutoff, device, blocked, keep)
                finally:
                    os.close(nested)
                if old:
                    removed += _remove_empty(directory, name, info)
            elif old and (stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)):
                os.unlink(name, dir_fd=directory)
                removed += 1
        except FileNotFoundError:
            continue
        except OSError as error:
            blocked.append(f"{child}: {error.strerror}")
    return removed


def prune_temporary_files(root: Path) -> tuple[int, list[str]]:
    cutoff = time.time_ns() - 2 * _DAY_NS
    blocked: list[str] = []
    keep = _KEEP | _open_paths(root)
    with _owned_directory(root, _TMP) as directory:
        removed = _prune(directory, Path(), cutoff, os.fstat(directory).st_dev, blocked, keep)
    return removed, blocked


def _open_paths(root):
    keep = set()
    for stage, _, logs in open_artifacts(root):
        for value in (stage, *logs):
            if isinstance(value, str):
                path = Path(value)
                if path.parent == _TMP / "simple_local_release":
                    keep.add(path.relative_to(_TMP))
    return keep
