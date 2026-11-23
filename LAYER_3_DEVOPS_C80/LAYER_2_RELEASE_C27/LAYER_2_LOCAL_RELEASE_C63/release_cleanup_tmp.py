"""Expire old scratch files after a successful Local Release."""

import errno
import os
from pathlib import Path
import stat
import time

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import INSTALLATION_LOCK_PATH, _owned_directory


_TMP = Path(".anechoic_tmp")
_KEEP = {
    INSTALLATION_LOCK_PATH.relative_to(_TMP),
    Path("atom_lifecycle/write.lock"),
    Path("cache/uv"),
    Path("rmed-base-revise"),
    Path("workbench/playwright-browsers"),
}


def _prune(directory: int, relative: Path, cutoff: int, device: int, blocked: list[str]) -> int:
    removed = 0
    for name in os.listdir(directory):
        child = relative / name
        if child in _KEEP:
            continue
        try:
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if info.st_dev != device:
                continue
            old = info.st_mtime_ns < cutoff
            if stat.S_ISDIR(info.st_mode):
                flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                nested = os.open(name, flags, dir_fd=directory)
                try:
                    if not os.path.samestat(info, os.fstat(nested)):
                        continue
                    removed += _prune(nested, child, cutoff, device, blocked)
                finally:
                    os.close(nested)
                if old and os.path.samestat(info, os.stat(name, dir_fd=directory, follow_symlinks=False)):
                    try:
                        os.rmdir(name, dir_fd=directory)
                        removed += 1
                    except OSError as error:
                        if error.errno != errno.ENOTEMPTY:
                            raise
            elif old and (stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)):
                os.unlink(name, dir_fd=directory)
                removed += 1
        except FileNotFoundError:
            continue
        except OSError as error:
            blocked.append(f"{child}: {error.strerror}")
    return removed


def prune_temporary_files(root: Path) -> tuple[int, list[str]]:
    cutoff = time.time_ns() - 48 * 60 * 60 * 10**9
    blocked: list[str] = []
    with _owned_directory(root, _TMP) as directory:
        removed = _prune(directory, Path(), cutoff, os.fstat(directory).st_dev, blocked)
    return removed, blocked
