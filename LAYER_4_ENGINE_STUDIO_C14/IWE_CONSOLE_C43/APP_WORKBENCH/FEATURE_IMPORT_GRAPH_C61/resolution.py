"""Resolve static imports against inventoried files, without importing project code."""

from __future__ import annotations

import hashlib
from importlib import metadata
import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

from .source import Source
from .web_imports import _WEB, lookup_web


_ENVIRONMENTS = {
    "LAYER_4_ENGINE_STUDIO_C14": "engine",
    "LAYER_5_FRAMEWORK_DELIVERY": "release",
    "LAYER_6_RUNTIME_SETUP": "setup",
}


def _environment_root(root: Path, base: PurePosixPath) -> Path:
    name = _ENVIRONMENTS.get(base.as_posix())
    environment = root / "LAYER_3_ENVIRONMENTS_C72" / name if name else root / base.as_posix()
    if name and not environment.is_symlink() and environment.is_dir():
        return environment
    return root / base.as_posix()


def _roots(root: Path, python_roots: tuple[str, ...] | None) -> list[PurePosixPath]:
    if python_roots is None:
        discovered = []
        for child in sorted(root.iterdir()):
            environment = _environment_root(root, PurePosixPath(child.name))
            manifest, lock = environment / "pyproject.toml", environment / "uv.lock"
            if child.is_symlink() or not child.is_dir() or manifest.is_symlink() or lock.is_symlink():
                continue
            if not manifest.is_file() or not lock.is_file():
                continue
            with manifest.open("rb") as handle:
                if isinstance(tomllib.load(handle).get("project"), dict):
                    discovered.append(child.name)
        python_roots = tuple(discovered) or (".",)
    roots = []
    for value in python_roots:
        path = (root / value).resolve()
        if not path.is_relative_to(root) or not path.is_dir():
            raise ValueError(f"Python root is not a directory inside the workspace: {value}")
        roots.append(PurePosixPath(path.relative_to(root).as_posix()))

    return roots


def _packages(sources: dict[str, Source], roots: list[PurePosixPath]) -> set[str]:
    packages: set[str] = set()
    for path, source in sources.items():
        if source.language != "python":
            continue
        file = PurePosixPath(path)
        for base in roots:
            if file.is_relative_to(base):
                parent = file.parent
                while parent != base and parent != PurePosixPath("."):
                    packages.add(parent.as_posix())
                    parent = parent.parent

    return packages


def _nodes(root: Path, sources: dict[str, Source]) -> dict[str, tuple]:
    nodes: dict[str, tuple] = {}
    manifest = root / "package.json"
    root_package = False
    if (any(PurePosixPath(path).parent == PurePosixPath(".")
            and source.language in {"javascript", "typescript", "svelte"}
            for path, source in sources.items()) and not manifest.is_symlink() and manifest.is_file()):
        with manifest.open(encoding="utf-8") as handle:
            root_package = bool(json.load(handle).get("name"))
    for path, source in sorted(sources.items()):
        relative = PurePosixPath(path).parent.as_posix()
        owner = None
        if relative != "." or root_package:
            owner = f"package:local:{relative}"
            nodes.setdefault(owner, (owner, "package", source.language, relative, None, None))
        key = f"module:{path}"
        nodes[key] = (key, "module", source.language, path, source.status, owner)
    return nodes


def _external(root: Path, installed: dict | None = None, *, locked: bool = False) -> set[str]:
    manifest = root / "pyproject.toml"
    external = set(sys.stdlib_module_names)
    project_name = ""
    if not manifest.is_symlink() and manifest.is_file():
        with manifest.open("rb") as handle:
            manifest_data = tomllib.load(handle)
        project = manifest_data.get("project", {})
        project_name = re.sub(r"[-_.]+", "-", project.get("name", "")).lower()
        groups = [
            project.get("dependencies", []),
            *project.get("optional-dependencies", {}).values(),
            *manifest_data.get("dependency-groups", {}).values(),
        ]
        for dependency in (item for group in groups for item in group if isinstance(item, str)):
            match = re.match(r"\s*([A-Za-z0-9_.-]+)", dependency)
            if match:
                external.add(match.group(1).replace("-", "_").lower())

    lock_names = set()
    if locked:
        with (root / "uv.lock").open("rb") as handle:
            lock_names = {re.sub(r"[-_.]+", "-", package["name"]).lower()
                          for package in tomllib.load(handle).get("package", [])
                          if isinstance(package, dict) and isinstance(package.get("name"), str)}
    for name, distributions in (installed if installed is not None else metadata.packages_distributions()).items():
        normalized = {re.sub(r"[-_.]+", "-", distribution).lower() for distribution in distributions}
        if normalized and project_name not in normalized and (not locked or normalized & lock_names):
            external.add(name)
    return external


def _candidates(name: str, bases: list[PurePosixPath], sources: dict[str, Source], packages: set[str]) -> list[str]:
    parts = name.split(".") if name else []
    for base in bases:
        path = base.joinpath(*parts)
        matches = []
        module = path.as_posix() + ".py"
        if module in sources and sources[module].language == "python":
            matches.append(f"module:{module}")
        if path.as_posix() in packages:
            matches.append(f"package:local:{path.as_posix()}")
        if matches:
            return matches
    return []


def _lookup(site, file, roots, sources, packages, external, nodes, image_modules=()):
    written = "." * site.level + site.module
    bases = roots
    name = site.module
    if site.level:
        parent = file.parent
        for _ in range(site.level - 1):
            parent = parent.parent
        bases = [parent] if any(file.is_relative_to(base) and parent.is_relative_to(base)
                                and parent != base for base in roots) else []
    elif roots and file.parent.name == file.parent.parent.name + "__tests":
        bases = [file.parent, *roots]
    matches = _candidates(name, bases, sources, packages)
    if site.name and site.name != "*":
        child_bases = bases
        if not site.level and bases != roots and _candidates(name, bases[:1], sources, packages):
            child_bases = bases[:1]
        child = _candidates(".".join(filter(None, (name, site.name))), child_bases, sources, packages)
        if child:
            matches = child
    target = matches[0] if len(matches) == 1 else None
    status = "internal" if target else "ambiguous" if matches else "unresolved"
    external_name = name.partition(".")[0]
    if not matches and not site.level and name in image_modules:
        status = "external"
        target = f"module:external:previous-image:{name}"
        nodes[target] = (target, "module", "python", None, "declared_previous_image", None)
    elif not matches and not site.level and external_name in external:
        status = "external"
        kind = "module" if external_name in sys.builtin_module_names else "package"
        target = f"{kind}:external:{external_name}"
        nodes[target] = (target, kind, "python", None, None, None)
    return written, target, status


def _edges(source_key, target, occurrence_key, nodes):
    edges = []
    if target:
        edges.append((source_key, target, occurrence_key, False))
        source_owner = nodes[source_key][5]
        target_owner = nodes[target][5] if nodes[target][1] == "module" else None
        if target_owner:
            edges.append((source_key, target_owner, occurrence_key, True))
        if source_owner:
            edges.append((source_owner, target, occurrence_key, True))
            if target_owner:
                edges.append((source_owner, target_owner, occurrence_key, True))
    return edges


def resolve(
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] | None = (".",),
    *, python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    root = root.resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes = _nodes(root, sources)
    installed = metadata.packages_distributions() if python_roots is None else None
    external_by_root = {base: _external(_environment_root(root, base), installed, locked=base != PurePosixPath(".")) for base in roots} if python_roots is None else {}
    external = _external(root) if python_roots is not None else set(sys.stdlib_module_names)
    occurrences: list[tuple] = []
    edges: list[tuple] = []
    seen = set()
    for path, source in sorted(sources.items()):
        if source.language not in _WEB and source.language != "python":
            continue
        source_key = f"module:{path}"
        file = PurePosixPath(path)
        image_modules = (python_image_imports or {}).get(path, ())
        source_roots = [base for base in roots if file.is_relative_to(base)] if python_roots is None else roots
        source_external = external_by_root[source_roots[0]] if source_roots and python_roots is None else external
        for site in source.imports:
            written, target, status = (lookup_web(root, site, file, sources, nodes)
                                       if source.language in _WEB else
                                       _lookup(site, file, source_roots, sources, packages, source_external, nodes, image_modules))
            dedup = (source_key, site.line, site.column, target or (written, site.name))
            if dedup in seen:
                continue
            seen.add(dedup)
            identity = (source_key, site.line, site.column, site.module, site.name, site.level)
            occurrence_key = "occurrence:" + hashlib.sha256(repr(identity).encode()).hexdigest()
            occurrences.append((occurrence_key, source_key, target, written, site.line, site.column, status, site.type_only))
            if target:
                if target not in nodes:
                    relative = target.removeprefix("package:local:")
                    nodes[target] = (target, "namespace", "python", relative, None, None)
                edges.extend(_edges(source_key, target, occurrence_key, nodes))
    return list(nodes.values()), occurrences, edges


def resolve_realization(
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] | None = (".",),
    *, components: dict[str, str] | None = None,
    python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[tuple], list[tuple], list[tuple], list[tuple], set[str]]:
    """Resolve imports and tests against direct Package paths and declared Components."""
    root = root.resolve()
    nodes, occurrences, edges = resolve(root, sources, python_roots, python_image_imports=python_image_imports)
    packages = {row[3]: row[0] for row in nodes if row[1] == "package" and row[3] is not None}
    targets = (components or {}) | packages
    test_edges = []
    test_keys = set()
    for path, key in sorted(packages.items()):
        directory = PurePosixPath(path)
        parent = directory.parent
        if directory.name == (parent.name or root.name) + "__tests":
            test_keys.add(key)
            if target := targets.get(parent.as_posix()):
                test_edges.append((key, target))
    return nodes, occurrences, edges, test_edges, test_keys
