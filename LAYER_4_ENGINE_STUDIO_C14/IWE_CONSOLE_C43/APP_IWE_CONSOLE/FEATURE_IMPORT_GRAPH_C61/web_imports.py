"Parse web imports with framework-owned parsers and resolve without execution."

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
from typing import TYPE_CHECKING

from .web_imports_capture import apply_web_rows, read_web_items
from .web_imports_local import local_result, local_value

if TYPE_CHECKING:
    from .source import Source

_WEB = frozenset({"javascript", "typescript", "svelte"})
_FRONTEND = (
    Path(__file__).resolve().parent.parent / "FEATURE_IWE_CONSOLE_FRONTEND"
)
_FRONTEND_PROJECT_PATH = _FRONTEND.relative_to(_FRONTEND.parents[3])
_SCANNER = _FRONTEND / "scripts" / "import-graph-scanner.ts"
_EXTENSIONS = (
    "",
    ".ts",
    ".tsx",
    ".cts",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".svelte",
)
_BUILTINS = frozenset(
    (
        "assert buffer child_process crypto events fs http https module "
        "os path process stream string_decoder test timers url util "
        "worker_threads zlib"
    ).split()
)


def scan_web(items):
    "Return scanner rows or None when framework-local tooling is unavailable."
    if not items:
        return {}
    if (
        not shutil.which("node")
        or not _SCANNER.is_file()
        or not all(
            (_FRONTEND / "node_modules" / name / "package.json").is_file()
            for name in ("typescript", "svelte")
        )
    ):
        return None
    try:
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in {"NODE_OPTIONS", "NODE_PATH"}
        }
        timeout = (
            None if env.get("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 60
        )
        result = subprocess.run(
            ["node", str(_SCANNER)],
            input=json.dumps(items),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=True,
            env=env,
        )
        rows = json.loads(result.stdout)
        return rows if isinstance(rows, dict) else None
    except OSError, subprocess.SubprocessError, ValueError:
        return None


def _dependencies(root, file, probe=None):
    current = root / file.parent
    while current.is_relative_to(root):
        manifest = current / "package.json"
        if probe is not None:
            probe(manifest)
        if not manifest.is_symlink() and manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    return set()
                groups = (
                    data.get(field)
                    for field in (
                        "dependencies",
                        "devDependencies",
                        "peerDependencies",
                        "optionalDependencies",
                    )
                )
                return {
                    name
                    for group in groups
                    if isinstance(group, dict)
                    for name in group
                }
            except OSError, ValueError, TypeError:
                return set()
        if current == root:
            break
        current = current.parent
    return set()


def _dependency_file(root, site, file, probe=None):
    dependency_file = file
    if site.name is not None:
        anchor = site.name
        if not anchor.startswith("./") and not anchor.startswith("../"):
            return None
        anchor_path = root / file.parent / anchor
        if probe is not None:
            probe(anchor_path)
        try:
            resolved = anchor_path.resolve(strict=True)
        except OSError:
            return None
        if (
            not resolved.is_relative_to(root)
            or resolved.name != "package.json"
            or not resolved.is_file()
        ):
            return None
        dependency_file = PurePosixPath(resolved.relative_to(root).as_posix())
    return dependency_file


def _lookup_local(
    root,
    spec,
    site,
    file,
    dependency_file,
    sources,
    written,
    probe,
    include_asset_target,
):
    value = local_value(
        root,
        spec,
        site,
        file,
        dependency_file,
        _FRONTEND,
        _FRONTEND_PROJECT_PATH,
    )
    if value is None:
        return written, None, "unresolved"
    return local_result(
        root,
        value,
        sources,
        written,
        _EXTENSIONS,
        _WEB,
        probe,
        include_asset_target,
    )


def _node_modules_package(root, spec, dependency_file, probe):
    parts = PurePosixPath(spec).parts
    if "node_modules" not in parts:
        return None
    index = parts.index("node_modules")
    tail = parts[index + 1 :]
    if not tail or any(part in (".", "..", "node_modules") for part in tail):
        return None
    length = 2 if tail[0].startswith("@") else 1
    if len(tail) < length:
        return None
    package = "/".join(tail[:length])
    directory = root / dependency_file.parent
    for part in parts[:index]:
        directory = directory.parent if part == ".." else directory / part
        if (
            not directory.is_relative_to(root)
            or directory.resolve() != directory
        ):
            return None
    target = directory / "node_modules" / Path(*tail)
    manifest = directory / "package.json"
    if probe is not None:
        probe(manifest)
        probe(target)
    if (
        not directory.is_relative_to(root)
        or directory.resolve() != directory
        or target.resolve() != target
        or manifest.is_symlink()
        or not manifest.is_file()
    ):
        return None
    relative_manifest = PurePosixPath(manifest.relative_to(root).as_posix())
    if package in _dependencies(root, relative_manifest, probe):
        return package
    return None


def lookup_web(
    root, site, file, sources, nodes, *, probe=None, include_asset_target=False
):
    written = site.module
    if written == "<dynamic>" or not written:
        return written, None, "unresolved"
    dependency_file = _dependency_file(root, site, file, probe)
    if dependency_file is None:
        return written, None, "unresolved"
    spec = written.split("?", 1)[0].split("#", 1)[0]
    if spec.startswith(".") and "node_modules" in PurePosixPath(spec).parts:
        package = _node_modules_package(root, spec, dependency_file, probe)
        if package is None:
            return written, None, "unresolved"
        target = f"package:external:{package}"
        nodes[target] = (target, "package", "javascript", None, None, None)
        return written, target, "external"
    if spec.startswith((".", "/")):
        return _lookup_local(
            root,
            spec,
            site,
            file,
            dependency_file,
            sources,
            written,
            probe,
            include_asset_target,
        )
    package = (
        "/".join(spec.split("/")[:2])
        if spec.startswith("@")
        else spec.split("/")[0]
    )
    builtin_name = spec.removeprefix("node:").split("/")[0]
    builtin = builtin_name in _BUILTINS
    if builtin or package in _dependencies(root, dependency_file, probe):
        target = (
            f"package:builtin:{builtin_name}"
            if builtin
            else f"package:external:{package}"
        )
        nodes[target] = (target, "package", "javascript", None, None, None)
        return written, target, "external"
    return written, None, "unresolved"


def capture_web(root: Path, sources: dict[str, Source]) -> None:
    from .source import ImportSite, Source

    items = read_web_items(root, sources, _WEB, Source)
    rows = scan_web(items)
    if rows is None:
        return
    apply_web_rows(
        sources,
        items,
        rows,
        ImportSite,
        Source,
    )
