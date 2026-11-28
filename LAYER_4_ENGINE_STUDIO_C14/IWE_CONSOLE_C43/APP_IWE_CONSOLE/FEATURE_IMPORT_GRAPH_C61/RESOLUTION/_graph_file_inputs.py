"""Capture Git and filesystem identity for Realization Graph reuse."""

from hashlib import file_digest
import os
from pathlib import Path
import stat

from dulwich.errors import NotGitRepository
from dulwich.ignore import default_user_ignore_filter_path
from dulwich.repo import Repo

from ..SOURCE_CAPTURE.SOURCE_CAPTURE__shared import _stat_signature


def _git_input_paths(root):
    try:
        repo = Repo.discover(root, across_filesystem=False)
    except NotGitRepository:
        return [], None
    with repo:
        base = Path(repo.path).resolve()
        common = Path(repo.commondir())
        config = repo.get_config_stack()
        paths = [
            Path(repo.index_path()),
            common / "config",
            common / "info/exclude",
            Path(repo.controldir()) / "config.worktree",
            Path(default_user_ignore_filter_path(config)).expanduser(),
        ]
        directory = root
        while directory.is_relative_to(base):
            paths.append(directory / ".gitignore")
            directory = directory.parent
        return paths, config


def _content_identity(path):
    try:
        mode = path.stat().st_mode
    except FileNotFoundError, NotADirectoryError:
        return "missing"
    if stat.S_ISDIR(mode):
        return ("directory", mode)
    if not stat.S_ISREG(mode):
        raise ValueError("Unwitnessed non-regular graph input")
    signature = _stat_signature(path)
    with path.open("rb") as file:
        digest = file_digest(file, "sha256").hexdigest()
    if signature != _stat_signature(path):
        raise ValueError("Graph input changed while reading")
    return ("file", mode, digest)


def _git_inputs(root):
    paths, _ = _git_input_paths(root)
    return [
        (str(path), _content_identity(path), _content_identity(path.parent))
        for path in paths
    ]


def _git_selection_witness(root):
    paths, config = _git_input_paths(root)
    ignore_case = (
        config.get_boolean((b"core",), b"ignorecase", False)
        if config is not None
        else False
    )
    return ignore_case, [(str(path), _stat_signature(path)) for path in paths]


def _library_witness(root):
    prefix = os.fspath(root) + os.sep
    pending, files = [os.fspath(root)], []
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(entry.path)
                elif not stat.S_ISREG(info.st_mode):
                    raise ValueError("Unwitnessed entry in Lean libraries")
                files.append(
                    (
                        entry.path.removeprefix(prefix),
                        info.st_dev,
                        info.st_ino,
                        info.st_mode,
                        info.st_size,
                        info.st_mtime_ns,
                        info.st_ctime_ns,
                    )
                )
    return sorted(files)
