"""Fingerprint the source inputs used by Local Release phases."""

import json
import os
import stat
from hashlib import file_digest, sha256
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _LAYER_NAMES,
    LocalReleaseError,
    _walk_regular_files,
)

from .local_release_state import _EXCLUDED, _OWNED, test_environment
from .snapshot_inputs import _COMMIT, _git

_ENGINE = Path("LAYER_4_ENGINE_STUDIO_C14")
_PROJECT_TOOLS = _ENGINE / "FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS"
_CANARY = frozenset(
    {
        _PROJECT_TOOLS / "release_image/_release_canary.py",
        _PROJECT_TOOLS / "FEATURE_PROJECT_TOOLS__tests/release/test_release_canary.py",
        _PROJECT_TOOLS
        / "FEATURE_PROJECT_TOOLS__tests/release/test_release_canary_retry.py",
    }
)
_IMAGE_TESTS = (
    _ENGINE / "MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image"
)
_VERSION = Path("version.toml")
_DOMAINS = ("runtime", "image", "canary", "environment")


def phase_inputs(
    root, runner_root, *, revision=None, external=True, cache=None
):
    """Fingerprint the phase inputs, with an optional cache for one direct release invocation."""
    digests = {domain: sha256() for domain in _DOMAINS}
    for domain, digest in digests.items():
        _add(digest, ("local-release-inputs-v1", domain))
    cache = cache if revision is None else None
    seen = set() if cache is not None else None
    if revision is None:
        rows = _worktree_rows(root, cache, seen, skip_version=True)
        _add_tree(digests, root, "worktree", rows, local=True)
    else:
        _add_tree(
            digests, root, "git-tree", _commit_rows(root, revision), local=True
        )
    if external and runner_root != root:
        rows = _worktree_rows(runner_root, cache, seen)
        _add_tree(digests, runner_root, "runner", rows, local=False)
    if cache is not None:
        for removed in cache.keys() - seen:
            del cache[removed]
    _add(digests["environment"], test_environment())
    return {domain: digest.hexdigest() for domain, digest in digests.items()}


def _add_tree(digests, root, kind, rows, *, local):
    for domain in ("runtime", "image", "canary") if local else ("runtime",):
        _add(digests[domain], (kind, str(root)))
    for relative, identity in rows:
        domain = _domain(relative) if local else "runtime"
        _add(digests[domain], (relative.as_posix(), identity))


def _add(digest, row):
    encoded = json.dumps(row, ensure_ascii=True, separators=(",", ":"))
    digest.update(encoded.encode("ascii") + b"\n")


def _domain(relative):
    if relative in _CANARY:
        return "canary"
    if relative.is_relative_to(_IMAGE_TESTS):
        return "image"
    return "runtime"


def _worktree_rows(root, cache, seen, *, skip_version=False):
    root_layers = frozenset(name.casefold() for name in _LAYER_NAMES)
    for path in _walk_regular_files(
        root,
        excluded_directories=_EXCLUDED,
        excluded_root_directories=root_layers,
    ):
        relative = path.relative_to(root)
        if skip_version and relative == _VERSION:
            continue
        if any(relative.is_relative_to(owned) for owned in _OWNED):
            continue
        if seen is not None:
            seen.add(path)
        yield relative, _worktree_identity(path, cache)


def _witness(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _worktree_identity(path, cache):
    try:
        observed = _witness(path.lstat())
        if not stat.S_ISREG(observed[2]):
            raise LocalReleaseError("local-release-source-changed")
        cached = cache.get(path) if cache is not None else None
        if cached is not None and cached[0] == observed:
            return cached[1]
        identity = _hash_file(path, observed), stat.S_IMODE(observed[2])
    except OSError as error:
        raise LocalReleaseError("local-release-source-changed") from error
    if cache is not None:
        cache[path] = observed, identity
    return identity


def _hash_file(path, observed):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if _witness(os.fstat(fd)) != observed:
            raise LocalReleaseError("local-release-source-changed")
        digest = file_digest(stream, "sha256").hexdigest()
        if (
            _witness(os.fstat(fd)) != observed
            or _witness(path.lstat()) != observed
        ):
            raise LocalReleaseError("local-release-source-changed")
    return digest


def _commit_rows(root, revision):
    if not isinstance(revision, str) or _COMMIT.fullmatch(revision) is None:
        raise LocalReleaseError("local-release-source-revision-invalid")
    tree = _git(root, "ls-tree", "-r", "-z", "--full-tree", revision)
    for row in filter(None, tree.split("\0")):
        metadata, name = row.split("\t", 1)
        mode, entry_type, blob = metadata.split()
        if mode not in {"100644", "100755"} or entry_type != "blob":
            raise LocalReleaseError("local-release-source-entry-unsafe")
        yield Path(name), (mode, blob)
