"""Seal an explicit source scope in an isolated checkout for Local Release."""

from dataclasses import replace
from hashlib import file_digest
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _owned_directory,
    _project_path,
    _root,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)

from .local_release_package_phases import container_settings, project_port
from ..prepare_local_files import _overlay, _parts
from ..prepare_local_port import _project_port, _rewrite_port
from ..release_support import _read_version
from ..snapshot_inputs import _source_version


_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def _git(root, *args, user_config=False):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env.update(
        GIT_OPTIONAL_LOCKS="0",
        GIT_TERMINAL_PROMPT="0",
        GIT_NO_REPLACE_OBJECTS="1",
    )
    if not user_config:
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    try:
        result = subprocess.run(
            (
                "git",
                "--literal-pathspecs",
                "-c",
                f"core.hooksPath={os.devnull}",
                *args,
            ),
            cwd=root,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise LocalReleaseError(
            f"prepare-local-git-failed: {args[0]}"
        ) from error
    if result.returncode:
        raise LocalReleaseError(f"prepare-local-git-failed: {args[0]}")
    return result.stdout.decode("utf-8").rstrip("\n")


def _validate_base(root, base):
    if _git(root, "rev-parse", "--verify", base + "^{commit}") != base:
        raise LocalReleaseError("prepare-local-base-invalid")
    for entry in _git(root, "ls-tree", "-r", "-z", "--full-tree", base).split(
        "\0"
    ):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        if metadata.split()[0] not in {"100644", "100755"}:
            raise LocalReleaseError("prepare-local-base-entry-unsafe")
        _parts(path, overlay=False)


def _checkout(root, checkout, base, identity):
    _git(
        checkout,
        "init",
        "--quiet",
        "--template=",
        "--object-format=" + ("sha1" if len(base) == 40 else "sha256"),
    )
    _git(
        checkout,
        "fetch",
        "--quiet",
        "--no-tags",
        "--no-recurse-submodules",
        "--",
        str(root),
        base,
    )
    _git(checkout, "checkout", "--quiet", "--detach", base)
    for key, value in zip(("user.name", "user.email"), identity, strict=True):
        _git(checkout, "config", "--local", key, value)


def _pin_port(checkout, source, port):
    selection = read_release_selection(checkout, source.control_relative)
    if port == _project_port(selection) or port == _project_port(source):
        raise LocalReleaseError("prepare-local-port-matches-source")
    _rewrite_port(selection.manifest_path, _project_port(selection), port)
    pinned = read_release_selection(checkout, source.control_relative)
    settings = selection.parameters["project_mcp"] | {"http_port": port}
    expected = replace(
        selection,
        manifest_sha256=pinned.manifest_sha256,
        parameters=selection.parameters | {"project_mcp": settings},
    )
    if pinned != expected:
        raise LocalReleaseError("prepare-local-manifest-changed")
    return pinned


def _seal(checkout, base, copied):
    paths = tuple(path.as_posix() for path in copied)
    _git(checkout, "add", "-A", "--", *paths)
    for relative, digest in copied.items():
        path = checkout / relative
        if digest is None:
            if path.exists() or path.is_symlink():
                raise LocalReleaseError("prepare-local-deletion-changed")
            continue
        with path.open("rb") as source:
            if file_digest(source, "sha256").hexdigest() != digest:
                raise LocalReleaseError("prepare-local-copy-changed")
        raw_blob = _git(
            checkout, "hash-object", "--no-filters", "--", relative.as_posix()
        )
        if (
            _git(checkout, "rev-parse", "--verify", ":" + relative.as_posix())
            != raw_blob
        ):
            raise LocalReleaseError("prepare-local-staged-content-changed")
    _git(
        checkout,
        "commit",
        "--quiet",
        "--no-gpg-sign",
        "-m",
        "chore(release): prepare scoped local checkout",
    )
    revision = _git(checkout, "rev-parse", "--verify", "HEAD")
    changed = _git(
        checkout,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "-z",
        base,
        revision,
    )
    if not set(filter(None, changed.split("\0"))) <= set(paths):
        raise LocalReleaseError("prepare-local-commit-outside-scope")
    if _git(checkout, "status", "--porcelain", "--untracked-files=all"):
        raise LocalReleaseError("prepare-local-checkout-not-clean")
    return revision


def _prepare_version(root, checkout, copied):
    installed = _project_path(
        root,
        Path(".anechoic_runtime/simple_local_release/package/version.toml"),
        label="installed-version",
    )
    installed_version = (
        _source_version(installed.parent) if installed.exists() else ""
    )
    version_path, version = _read_version(
        checkout, installed_version=installed_version
    )
    version_path.write_text(version, encoding="utf-8")
    with version_path.open("rb") as source:
        copied[version_path.relative_to(checkout)] = file_digest(
            source, "sha256"
        ).hexdigest()


def _prepare_checkout(root, stage, base, paths, port, identity, selection):
    checkout = stage / "checkout"
    checkout.mkdir(mode=0o700)
    _checkout(root, checkout, base, identity)
    copied = {path: _overlay(root, checkout, path) for path in paths}
    config = container_settings(root)
    if port is None or config is not None:
        pinned = read_release_selection(checkout, selection.control_relative)
        if port is None:
            _prepare_version(root, checkout, copied)
    else:
        pinned = _pin_port(checkout, selection, port)
        copied[pinned.manifest_path.relative_to(checkout)] = (
            pinned.manifest_sha256
        )
    manifest = pinned.manifest_path.relative_to(checkout)
    revision = _seal(checkout, base, copied)
    if config is not None:
        config = config | {
            "http_port": port if port is not None else config["http_port"]
        }
        container_settings(checkout, config)
    return {
        "outcome": "completed",
        "project_root": str(checkout),
        "revision": revision,
        "base": base,
        "changed_paths": [path.as_posix() for path in paths],
        "manifest_path": manifest.as_posix(),
        "manifest_sha256": pinned.manifest_sha256,
        "instance_id": pinned.instance_id,
        "port": project_port(checkout, pinned),
    }


def _new_stage(stage):
    with _owned_directory(
        stage.parent.parent, Path(stage.parent.name)
    ) as owner:
        info = os.fstat(owner)
        if (
            info.st_uid != os.getuid()
            or info.st_mode & 0o077
            or not os.path.samestat(
                info, stage.parent.stat(follow_symlinks=False)
            )
        ):
            raise LocalReleaseError("prepare-local-scratch-unsafe")
        try:
            os.mkdir(stage.name, mode=0o700, dir_fd=owner)
        except FileExistsError as error:
            raise LocalReleaseError("prepare-local-target-exists") from error


def _prepare(root, stage, base, changed_paths, port):
    if not isinstance(base, str) or not _COMMIT.fullmatch(base):
        raise LocalReleaseError("prepare-local-base-invalid")
    if port is not None and (type(port) is not int or not 1 <= port <= 65535):
        raise LocalReleaseError("prepare-local-port-invalid")
    paths = tuple(_parts(path, overlay=True) for path in changed_paths)
    if not paths or len(set(paths)) != len(paths):
        raise LocalReleaseError("prepare-local-paths-invalid")
    if Path(_git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise LocalReleaseError("prepare-local-source-not-git-root")
    _validate_base(root, base)
    selection = read_release_selection(root)
    config = container_settings(root)
    if port is not None and port == project_port(root, selection):
        raise LocalReleaseError("prepare-local-port-matches-source")
    identity = tuple(
        _git(root, "config", "--get", key, user_config=True)
        for key in ("user.name", "user.email")
    )
    _new_stage(stage)
    try:
        result = _prepare_checkout(
            root, stage, base, paths, port, identity, selection
        )
        if (
            read_release_selection(root) != selection
            or container_settings(root) != config
        ):
            raise LocalReleaseError("prepare-local-source-selection-changed")
        return result
    except BaseException:
        shutil.rmtree(stage)
        raise


def prepare_local(project_root, *, run_id, base, changed_paths, port=None):
    "Prepare one private checkout and report the exact revision to release."
    root = _root(project_root)
    if not isinstance(run_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}", run_id
    ):
        raise LocalReleaseError("prepare-local-run-id-invalid")
    owner = (
        Path.home() / f".anechoic-local-release-{os.getuid()}"
        if port is None
        else Path(tempfile.gettempdir())
        / f"anechoic-local-release-{os.getuid()}"
    )
    stage = owner.parent.resolve(strict=True) / owner.name / run_id
    try:
        if stage.is_relative_to(root):
            raise LocalReleaseError("prepare-local-scratch-inside-source")
        return _prepare(root, stage, base, changed_paths, port) | {
            "run_id": run_id
        }
    except (OSError, ValueError, RuntimeError) as error:
        raise LocalReleaseError(f"{stage / 'checkout'}: {error}") from error
