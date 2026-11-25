"""Read the Git and runtime inputs for a split Local Release."""

from hashlib import sha256
import os
from pathlib import Path
import re
import stat
import subprocess
import tomllib

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError, _project_path

_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_GATE_ROOTS = (
    "LAYER_4_ENGINE_STUDIO_C14",
    "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27",
    "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72",
    "LAYER_5_USER_SETUP_C65",
)
_GATE_INPUTS = (
    Path("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py"),
    *(
        Path(_GATE_ROOTS[2]) / environment / name
        for environment in ("engine", "release", "setup")
        for name in ("pyproject.toml", "uv.lock")
    ),
)
_GATE_CACHE_DIRS = frozenset({
    ".anechoic_tmp", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache",
    ".venv", ".venv-dev", ".venv-prod", ".venv-release", ".venv-setup",
    "node_modules", "__pycache__", "dist",
})


def _git(root, *args, optional=False):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    try:
        result = subprocess.run(
            ("git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.ignorestat=false",
             "-c", "core.fileMode=true", *args),
            cwd=root, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=120, check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise LocalReleaseError(f"local-release-git-read-failed: {args[0]}") from error
    if result.returncode:
        if optional and result.stderr.startswith(b"fatal: not a git repository"):
            return None
        raise LocalReleaseError(f"local-release-git-read-failed: {args[0]}")
    return os.fsdecode(result.stdout).rstrip("\n")


def _assert_source_clean(root, revision):
    if _git(root, "rev-parse", "--verify", "HEAD") != revision:
        raise LocalReleaseError("local-release-source-revision-mismatch")
    flags = _git(root, "ls-files", "-v", "-z").split("\0")
    if any(row and (row[0] == "S" or row[0].islower()) for row in flags):
        raise LocalReleaseError("local-release-source-index-flags-unsafe")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none", "-z"):
        raise LocalReleaseError("local-release-source-worktree-not-clean")
    ignored = _git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z",
                   "--", *_GATE_ROOTS)
    for name in filter(None, ignored.split("\0")):
        path = Path(name)
        if path.name == ".DS_Store" or not _GATE_CACHE_DIRS.isdisjoint(path.parts):
            continue
        directory = root / path
        if name.endswith("/") and not directory.is_symlink() and all(
            child.name == ".DS_Store" for child in directory.iterdir()
        ):
            continue
        raise LocalReleaseError("local-release-untracked-gate-input")


def _source_tree(root, revision):
    if not isinstance(revision, str) or _COMMIT.fullmatch(revision) is None:
        raise LocalReleaseError("local-release-source-revision-invalid")
    if Path(_git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise LocalReleaseError("local-release-source-not-git-root")
    _assert_source_clean(root, revision)
    tracked = set()
    for row in filter(None, _git(root, "ls-tree", "-r", "-z", "--full-tree", revision).split("\0")):
        metadata, name = row.split("\t", 1)
        if metadata.split()[0] not in {"100644", "100755"}:
            raise LocalReleaseError("local-release-source-entry-unsafe")
        tracked.add(Path(name))
    if not {*_GATE_INPUTS, Path("version.toml")}.issubset(tracked):
        raise LocalReleaseError("local-release-source-gate-input-unavailable")
    return frozenset(tracked)


def _source_version(root):
    path = _project_path(root, Path("version.toml"), label="version-path", require_exists=True)
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))["framework"]["version"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise LocalReleaseError("local-release-version-invalid") from error
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2,3}", value):
        raise LocalReleaseError("local-release-version-invalid")
    return value


def _target_git(root, targets):
    top = _git(root, "rev-parse", "--show-toplevel", optional=True)
    if top is None:
        return set(), {}
    top = Path(top).resolve(strict=True)
    scopes = [f":(literal){path.relative_to(top).as_posix()}" for path in targets]
    exclusions = [f":(exclude,literal){(path / name).relative_to(top).as_posix()}"
                  for path, (_, preserve) in targets.items() for name in preserve or ()]
    pathspec = (*scopes, *exclusions)
    tracked = _git(top, "ls-files", "-v", "-z", "--", *pathspec)
    status = _git(top, "status", "--porcelain=v1", "--no-renames", "-z", "--untracked-files=no",
                  "--", *pathspec)
    return ({top / row[2:] for row in tracked.split("\0") if row.startswith("H ")},
            {top / row[3:]: row[:2] for row in filter(None, status.split("\0"))})


def target_runtime_digest(root):
    relative = Path(".anechoic_runtime/anechoic_runtime_settings.toml")
    path = _project_path(root, relative, label="runtime-settings")
    maximum = 65_536
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise LocalReleaseError("local-release-target-runtime-settings-invalid") from error
    with os.fdopen(fd, "rb") as stream:
        observed = os.fstat(stream.fileno())
        if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1:
            raise LocalReleaseError("local-release-target-runtime-settings-invalid")
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise LocalReleaseError("local-release-target-runtime-settings-invalid")
    return sha256(data).hexdigest()
