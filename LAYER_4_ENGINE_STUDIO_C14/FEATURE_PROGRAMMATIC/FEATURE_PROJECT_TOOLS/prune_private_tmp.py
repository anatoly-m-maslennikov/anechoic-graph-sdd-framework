"""Expire explicitly marked disposable Project directories under /private/tmp."""

import argparse
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

PRIVATE_TMP = Path("/private/tmp")
MARKER = ".anechoic-disposable"
RETENTION_SECONDS = 3 * 24 * 60 * 60


def private_directory(path, root):
    if path.parent != root:
        return None
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        return None
    return None if path.is_mount() else info


def mark(path, root, project):
    if private_directory(path, root) is None:
        raise ValueError("Use a private directory directly under /private/tmp")
    with (path / MARKER).open("x", encoding="utf-8") as marker:
        marker.write(f"{project}\n")


def expired_directories(root, project, now):
    for path in root.iterdir():
        try:
            directory = private_directory(path, root)
            if directory is None or now - directory.st_mtime <= RETENTION_SECONDS:
                continue
            marker = path / MARKER
            info = marker.lstat()
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_size > 4096
                    or now - info.st_mtime <= RETENTION_SECONDS):
                continue
            if marker.read_text(encoding="utf-8", errors="replace") == f"{project}\n":
                yield path, directory
        except (FileNotFoundError, PermissionError):
            continue


def capture(command, project):
    return subprocess.check_output(command, cwd=project, text=True, timeout=20)


def protected_paths(project):
    worktrees = capture(["git", "worktree", "list", "--porcelain", "-z"], project)
    roots = [Path(row.removeprefix("worktree ")).resolve()
             for row in worktrees.split("\0") if row.startswith("worktree ")]
    containers = capture(["docker", "ps", "-aq"], project).splitlines()
    if containers:
        mounts = capture(["docker", "inspect", "--format",
                          "{{range .Mounts}}{{println .Source}}{{end}}", *containers], project)
        roots.extend(Path(path).resolve() for path in mounts.splitlines() if path.startswith("/"))
    open_files = capture(["/usr/sbin/lsof", "-w", "-nP", "-Fn"], project)
    opened = [Path(row[1:]) for row in open_files.splitlines() if row.startswith("n/")]
    mounts = capture(["/sbin/mount"], project)
    for row in mounts.splitlines():
        mount = row.partition(" on ")[2].rpartition(" (")[0]
        if mount.startswith("/"):
            opened.append(Path(mount))
    opened.extend(Path("/private") / str(path).lstrip("/") for path in tuple(opened)
                  if path.is_relative_to("/tmp"))
    return roots, opened


def prune(root, project, now):
    candidates = list(expired_directories(root, project, now))
    if not candidates:
        return
    if not shutil.rmtree.avoids_symlink_attacks:
        raise RuntimeError("Safe directory removal is unavailable")
    roots, opened = protected_paths(project)
    for path, expected in candidates:
        if any(other.is_relative_to(path) or path.is_relative_to(other) for other in roots):
            continue
        if any(other.is_relative_to(path) for other in opened):
            continue
        current = private_directory(path, root)
        if current is None or (current.st_dev, current.st_ino, current.st_mtime_ns) != (
            expected.st_dev, expected.st_ino, expected.st_mtime_ns,
        ):
            continue
        shutil.rmtree(path)
        print(f"Removed {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mark", type=Path, help="Mark a completed run's private scratch directory")
    args = parser.parse_args()
    try:
        project = Path(capture(["git", "rev-parse", "--show-toplevel"], Path.cwd()).strip()).resolve()
        if args.mark is not None:
            mark(args.mark.absolute(), PRIVATE_TMP, project)
        else:
            prune(PRIVATE_TMP, project, time.time())
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f"Project temp cleanup failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
