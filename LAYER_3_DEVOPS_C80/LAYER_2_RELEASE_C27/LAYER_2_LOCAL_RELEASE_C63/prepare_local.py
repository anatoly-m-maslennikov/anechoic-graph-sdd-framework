"""Seal an explicit source scope in an isolated checkout for Local Release."""

import ast
import json
from contextlib import ExitStack
from dataclasses import asdict, replace
from hashlib import file_digest
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

from markdown_it import MarkdownIt

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _owned_directory,
    _project_path,
    _root,
    read_release_selection,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.container_settings__pub import (
    CONTAINER_SETTINGS_FILENAME, parse_container_settings, read_container_settings,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings_carrier__pub import (
    write_settings_carrier,
)

from .local_release_package_phases import project_port
from .release_support import _read_version
from .snapshot_inputs import _source_version


_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
_PROTECTED = {".git", ".ssh", ".aws", ".gnupg"}
_RUNTIME = {".anechoic_tmp", ".anechoic_runtime", ".anechoic_install"}


def _git(root, *args, user_config=False):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    if not user_config:
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    try:
        result = subprocess.run(
            ("git", "--literal-pathspecs", "-c", f"core.hooksPath={os.devnull}", *args),
            cwd=root, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise LocalReleaseError(f"prepare-local-git-failed: {args[0]}") from error
    if result.returncode:
        raise LocalReleaseError(f"prepare-local-git-failed: {args[0]}")
    return result.stdout.decode("utf-8").rstrip("\n")


def _parts(value, *, overlay):
    if not isinstance(value, str):
        raise LocalReleaseError("prepare-local-path-unsafe")
    path = Path(value)
    if (path.is_absolute() or not path.parts or path.as_posix() != value or "\\" in value
            or any(ord(char) < 32 or ord(char) == 127 for char in value)
            or any(part == ".." or part.casefold() in _PROTECTED or part.casefold().startswith(".env")
                   or part.casefold().endswith(".env") for part in path.parts)
            or (overlay and any(part.casefold() in _RUNTIME for part in path.parts))):
        raise LocalReleaseError("prepare-local-path-unsafe")
    return path


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


def _checkout(root, checkout, base, identity, *, full_history):
    _git(checkout, "init", "--quiet", "--template=", "--object-format=" + ("sha1" if len(base) == 40 else "sha256"))
    depth = () if full_history else ("--depth=1",)
    _git(checkout, "fetch", "--quiet", *depth, "--no-tags", "--no-recurse-submodules", "--", str(root), base)
    _git(checkout, "checkout", "--quiet", "--detach", base)
    for key, value in zip(("user.name", "user.email"), identity, strict=True):
        _git(checkout, "config", "--local", key, value)


def _open_source(root, relative):
    flags = os.O_RDONLY | os.O_NOFOLLOW
    with ExitStack() as directories:
        parent = os.open(root, flags | os.O_DIRECTORY)
        directories.callback(os.close, parent)
        for part in relative.parts[:-1]:
            parent = os.open(part, flags | os.O_DIRECTORY, dir_fd=parent)
            directories.callback(os.close, parent)
        return os.open(relative.name, flags | os.O_NONBLOCK, dir_fd=parent)


def _version(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _overlay(root, checkout, relative):
    destination = _project_path(
        checkout, relative, label="prepare-local-destination"
    )
    try:
        descriptor = _open_source(root, relative)
    except FileNotFoundError:
        if not destination.is_file():
            raise LocalReleaseError(
                "prepare-local-deletion-missing-from-base"
            ) from None
        destination.unlink()
        return None
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise LocalReleaseError("prepare-local-source-entry-unsafe")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as output:
            shutil.copyfileobj(source, output)
        destination.chmod(0o755 if before.st_mode & stat.S_IXUSR else 0o644)
        source.seek(0)
        digest = file_digest(source, "sha256").hexdigest()
        if _version(before) != _version(os.fstat(source.fileno())):
            raise LocalReleaseError("prepare-local-source-changed")
        return digest


def _mapping_value(mapping, key):
    if isinstance(mapping, ast.Dict):
        return next((value for index, value in zip(mapping.keys, mapping.values, strict=True)
                     if isinstance(index, ast.Constant) and index.value == key), None)
    return None


def _port_nodes(code, manifest_type):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == manifest_type:
            parameters = next((arg.value for arg in node.keywords if arg.arg == "parameters"), None)
            port = _mapping_value(_mapping_value(parameters, "project_mcp"), "http_port")
            if isinstance(port, ast.Constant) and type(port.value) is int:
                yield port


def _formal_claim_fences(text):
    tokens = MarkdownIt("commonmark").parse(text)
    headings = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append(
                (level, tokens[index + 1].content.strip().casefold())
            )
        elif token.type == "fence":
            section = tuple(name for _, name in headings)
            info = token.info.strip().casefold()
            if section == ("claim", "formal claim") and info == "python":
                yield token, "ProjectManifest"
            elif section == ("formal manifest",) and info in {"python", "python anechoic-edsl"}:
                yield token, "ComponentManifest"


def _rewrite_port(path, old_port, port):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = raw.splitlines(keepends=True)
    slots = []
    for token, manifest_type in _formal_claim_fences(text):
        for node in _port_nodes(token.content, manifest_type):
            if node.value == old_port:
                slots.append((token, node))
    if len(slots) != 1:
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    token, node = slots[0]
    index = token.map[0] + node.lineno
    code_line = token.content.splitlines()[node.lineno - 1].encode("utf-8")
    original_line = lines[index].rstrip(b"\r\n")
    if not original_line.endswith(code_line):
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    offset = len(original_line) - len(code_line)
    first, last = offset + node.col_offset, offset + node.end_col_offset
    lines[index] = (
        lines[index][:first] + str(port).encode("ascii") + lines[index][last:]
    )
    path.write_bytes(b"".join(lines))


def _project_port(selection):
    settings = selection.parameters.get("project_mcp")
    port = settings.get("http_port") if isinstance(settings, dict) else None
    if type(port) is not int or not 1 <= port <= 65535:
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    return port


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
        raw_blob = _git(checkout, "hash-object", "--no-filters", "--", relative.as_posix())
        if _git(checkout, "rev-parse", "--verify", ":" + relative.as_posix()) != raw_blob:
            raise LocalReleaseError("prepare-local-staged-content-changed")
    _git(checkout, "commit", "--quiet", "--no-gpg-sign", "-m", "chore(release): prepare scoped local checkout")
    revision = _git(checkout, "rev-parse", "--verify", "HEAD")
    changed = _git(checkout, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", base, revision)
    if not set(filter(None, changed.split("\0"))) <= set(paths):
        raise LocalReleaseError("prepare-local-commit-outside-scope")
    if _git(checkout, "status", "--porcelain", "--untracked-files=all"):
        raise LocalReleaseError("prepare-local-checkout-not-clean")
    return revision


def _prepare_checkout(root, stage, base, paths, port, identity, selection):
    checkout = stage / "checkout"
    checkout.mkdir(mode=0o700)
    _checkout(root, checkout, base, identity, full_history=port is None)
    copied = {path: _overlay(root, checkout, path) for path in paths}
    config = read_container_settings(root)
    if port is None or config is not None:
        pinned = read_release_selection(checkout, selection.control_relative)
        installed = _project_path(root, Path(".anechoic_runtime/simple_local_release/package/version.toml"),
                                  label="installed-version")
        installed_version = _source_version(installed.parent) if installed.exists() else ""
        if port is None:
            version_path, version = _read_version(checkout, installed_version=installed_version)
            version_path.write_text(version, encoding="utf-8")
            with version_path.open("rb") as source:
                copied[version_path.relative_to(checkout)] = file_digest(source, "sha256").hexdigest()
    else:
        pinned = _pin_port(checkout, selection, port)
        copied[pinned.manifest_path.relative_to(checkout)] = pinned.manifest_sha256
    manifest = pinned.manifest_path.relative_to(checkout)
    revision = _seal(checkout, base, copied)
    if config is not None:
        config = replace(config, http_port=port if port is not None else config.http_port)
        content = "schema_version = 1\n\n[container]\n" + "".join(
            f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
            for key, value in asdict(config).items() if value is not None
        )
        write_settings_carrier(checkout / CONTAINER_SETTINGS_FILENAME, content,
                               validate=parse_container_settings, replace_existing=False)
    return {"outcome": "completed", "project_root": str(checkout), "revision": revision, "base": base,
            "changed_paths": [path.as_posix() for path in paths], "manifest_path": manifest.as_posix(),
            "manifest_sha256": pinned.manifest_sha256, "instance_id": pinned.instance_id, "port": project_port(checkout, pinned)}


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
    config = read_container_settings(root)
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
        if (read_release_selection(root) != selection or
                read_container_settings(root) != config):
            raise LocalReleaseError("prepare-local-source-selection-changed")
        return result
    except BaseException:
        shutil.rmtree(stage)
        raise


def prepare_local(project_root, *, run_id, base, changed_paths, port=None):
    (
        'Prepare one private checkout and report the exact revision to '
        'release.'
    )
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
