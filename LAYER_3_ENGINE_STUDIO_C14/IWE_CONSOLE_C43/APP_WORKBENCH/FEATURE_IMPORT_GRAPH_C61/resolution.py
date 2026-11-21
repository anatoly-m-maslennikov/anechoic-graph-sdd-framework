"""Resolve static imports against inventoried files, without importing project code."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

from .source import Source


def _roots(root: Path, python_roots: tuple[str, ...]) -> list[PurePosixPath]:
    roots = []
    for value in python_roots:
        path = (root / value).resolve()
        if not path.is_relative_to(root) or not path.is_dir():
            raise ValueError(f"Python root is not a directory inside the workspace: {value}")
        roots.append(PurePosixPath(path.relative_to(root).as_posix()))

    return roots


def _packages(sources: dict[str, Source], roots: list[PurePosixPath]) -> set[str]:
    # Index only inventoried files; directories containing them provide namespace evidence.
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


def _external(root: Path) -> set[str]:
    manifest = root / "pyproject.toml"
    external = set(sys.stdlib_module_names)
    if not manifest.is_symlink() and manifest.is_file():
        with manifest.open("rb") as handle:
            manifest_data = tomllib.load(handle)
        project = manifest_data.get("project", {})
        groups = [
            project.get("dependencies", []),
            *project.get("optional-dependencies", {}).values(),
            *manifest_data.get("dependency-groups", {}).values(),
        ]
        for dependency in (item for group in groups for item in group if isinstance(item, str)):
            match = re.match(r"\s*([A-Za-z0-9_.-]+)", dependency)
            if match:
                external.add(match.group(1).replace("-", "_").lower())

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


def _lookup(site, file, roots, sources, packages, external, nodes):
    written = "." * site.level + site.module
    bases = roots
    name = site.module
    if site.level:
        containing = next((base for base in roots if file.is_relative_to(base)), None)
        if containing is None:
            bases = []
        else:
            parent = file.parent
            for _ in range(site.level - 1):
                parent = parent.parent
            bases = [parent] if parent.is_relative_to(containing) and parent != containing else []
    matches = _candidates(name, bases, sources, packages)
    if site.name and site.name != "*":
        child = _candidates(".".join(filter(None, (name, site.name))), bases, sources, packages)
        if child:
            matches = child
    target = matches[0] if len(matches) == 1 else None
    status = "internal" if target else "ambiguous" if matches else "unresolved"
    if not matches and not site.level and name.split(".")[0].lower() in external:
        status = "external"
        external_name = name.split(".")[0]
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
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] = (".",)
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    root = root.resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes = _nodes(root, sources)
    external = _external(root)
    occurrences: list[tuple] = []
    edges: list[tuple] = []
    seen = set()
    for path, source in sorted(sources.items()):
        if source.language != "python":
            continue
        source_key = f"module:{path}"
        file = PurePosixPath(path)
        for site in source.imports:
            written, target, status = _lookup(site, file, roots, sources, packages, external, nodes)
            dedup = (source_key, site.line, site.column, target or (written, site.name))
            if dedup in seen:
                continue
            seen.add(dedup)
            identity = (source_key, site.line, site.column, site.module, site.name, site.level)
            occurrence_key = "occurrence:" + hashlib.sha256(repr(identity).encode()).hexdigest()
            occurrences.append((occurrence_key, source_key, target, written, site.line, site.column, status, False))
            if target:
                if target not in nodes:
                    relative = target.removeprefix("package:local:")
                    nodes[target] = (target, "namespace", "python", relative, None, None)
                edges.extend(_edges(source_key, target, occurrence_key, nodes))
    return list(nodes.values()), occurrences, edges


def resolve_realization(
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] = (".",),
    *, components: dict[str, str] | None = None,
) -> tuple[list[tuple], list[tuple], list[tuple], list[tuple], set[str]]:
    """Resolve imports and tests against direct Package paths and declared Components."""
    root = root.resolve()
    nodes, occurrences, edges = resolve(root, sources, python_roots)
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
