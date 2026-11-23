"""Git checkpoints and secured local Release staging and locks."""

from __future__ import annotations

import fcntl
import os
import re
import stat
from collections.abc import Callable
from contextlib import ExitStack, contextmanager
from pathlib import Path
from secrets import token_urlsafe

from .release_assets import LocalReleaseError

INSTALLATION_LOCK_PATH = Path(".anechoic_tmp/local_release_installation/installation.lock")


def _git_head(root: Path, runner: Callable) -> str:
    result = runner(("git", "rev-parse", "--verify", "HEAD"), root)
    head = getattr(result, "stdout", "")
    if (getattr(result, "returncode", 1) != 0 or not isinstance(head, str)
            or re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", head.strip()) is None):
        raise LocalReleaseError("local-release-head-commit-unavailable")
    return head.strip()


def _git_checkpoint(root: Path, runner: Callable, phase: str, paths: tuple[str, ...], head: str | None) -> str:
    if head is not None and _git_head(root, runner) != head:
        raise LocalReleaseError("local-release-head-commit-changed")
    sensitive = runner((
        "git", "diff", "--cached", "--name-only", "--", ":(glob)**/.env*", ":(glob)**/*.env",
    ), root)
    if (getattr(sensitive, "returncode", 1) != 0 or not isinstance(getattr(sensitive, "stdout", None), str)
            or sensitive.stdout.strip()):
        raise LocalReleaseError("local-release-staged-environment-file-or-check-unavailable")
    if head is not None and runner(("git", "diff", "--cached", "--quiet"), root).returncode != 0:
        raise LocalReleaseError("local-release-index-changed")
    committed = False
    if paths:
        result = runner((
            "git", "add", "-A", "--", *paths, ":(exclude,glob)**/.env*", ":(exclude,glob)**/*.env",
        ), root)
        if result.returncode != 0:
            raise LocalReleaseError("local-release-git-failed")
        staged = runner(("git", "diff", "--cached", "--quiet"), root)
        if staged.returncode == 1:
            result = runner(("git", "commit", "-m", f"chore(release): simple local {phase}"), root)
            if result.returncode != 0:
                raise LocalReleaseError("local-release-git-failed")
            committed = True
        elif staged.returncode != 0:
            raise LocalReleaseError("local-release-git-failed")
    result = runner(("git", "status", "--porcelain", "--untracked-files=all"), root)
    if (result.returncode != 0 or not isinstance(getattr(result, "stdout", None), str) or result.stdout.strip()):
        raise LocalReleaseError("local-release-worktree-not-clean")
    current = _git_head(root, runner)
    if head is not None and not committed and current != head:
        raise LocalReleaseError("local-release-head-commit-changed")
    return current


@contextmanager
def _owned_directory(root: Path, relative: Path):
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    with ExitStack() as descriptors:
        try:
            directory = os.open(root.anchor, flags)
            descriptors.callback(os.close, directory)
            for name in root.parts[1:]:
                directory = os.open(name, flags, dir_fd=directory)
                descriptors.callback(os.close, directory)
            for name in relative.parts:
                try:
                    os.mkdir(name, mode=0o700, dir_fd=directory)
                except FileExistsError:
                    pass
                directory = os.open(name, flags, dir_fd=directory)
                descriptors.callback(os.close, directory)
        except OSError as error:
            raise LocalReleaseError("local-release-temporary-directory-unsafe") from error
        yield directory


def _new_staging_directory(root: Path, prefix: str) -> Path:
    owner = root / ".anechoic_tmp/simple_local_release"
    name = prefix + token_urlsafe(6)
    with _owned_directory(root, owner.relative_to(root)) as descriptor:
        os.mkdir(name, mode=0o700, dir_fd=descriptor)
        try:
            if not os.path.samestat(os.fstat(descriptor), owner.stat(follow_symlinks=False)):
                raise LocalReleaseError("local-release-temporary-directory-changed")
        except (OSError, LocalReleaseError):
            os.rmdir(name, dir_fd=descriptor)
            raise
    return owner / name


@contextmanager
def _installation_lock(root: Path, selection):
    if selection.root != root:
        raise LocalReleaseError("local-release-temporary-project-mismatch")
    with _release_lock(root, INSTALLATION_LOCK_PATH, "installation"):
        yield


@contextmanager
def _release_lock(root: Path, relative: Path, label: str):
    with _owned_directory(root, relative.parent) as directory:
        descriptor = os.open(relative.name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                             mode=0o600, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise LocalReleaseError(f"local-release-{label}-lock-invalid")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise LocalReleaseError(f"local-release-{label}-lock-busy") from error
            yield
        finally:
            os.close(descriptor)


