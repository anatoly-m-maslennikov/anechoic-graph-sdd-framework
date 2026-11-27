"""Build graph nodes, candidates and edges for import resolution."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path, PurePosixPath

from .source import Source


def _packages(
    sources: dict[str, Source], roots: list[PurePosixPath]
) -> set[str]:
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
    if (
        any(
            PurePosixPath(path).parent == PurePosixPath(".")
            and source.language in {"javascript", "typescript", "svelte"}
            for path, source in sources.items()
        )
        and not manifest.is_symlink()
        and manifest.is_file()
    ):
        with manifest.open(encoding="utf-8") as handle:
            root_package = bool(json.load(handle).get("name"))
    for path, source in sorted(sources.items()):
        relative = PurePosixPath(path).parent.as_posix()
        owner = None
        if relative != "." or root_package:
            owner = f"package:local:{relative}"
            nodes.setdefault(
                owner,
                (owner, "package", source.language, relative, None, None),
            )
        key = f"module:{path}"
        nodes[key] = (
            key,
            "module",
            source.language,
            path,
            source.status,
            owner,
        )
    return nodes


def _candidates(
    name: str,
    bases: list[PurePosixPath],
    sources: dict[str, Source],
    packages: set[str],
) -> list[str]:
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


def _edges(source_key, target, occurrence_key, nodes):
    edges = []
    if target:
        edges.append((source_key, target, occurrence_key, False))
        source_owner = nodes[source_key][5]
        target_owner = (
            nodes[target][5] if nodes[target][1] == "module" else None
        )
        if target_owner:
            edges.append((source_key, target_owner, occurrence_key, True))
        if source_owner:
            edges.append((source_owner, target, occurrence_key, True))
            if target_owner:
                edges.append(
                    (source_owner, target_owner, occurrence_key, True)
                )
    return edges


def _external_manifest(root: Path) -> tuple[str, set[str]]:
    manifest = root / "pyproject.toml"
    external = set()
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
        for dependency in (
            item for group in groups for item in group if isinstance(item, str)
        ):
            match = re.match(r"\s*([A-Za-z0-9_.-]+)", dependency)
            if match:
                external.add(match.group(1).replace("-", "_").lower())

    return project_name, external


def _lookup_bases(site, file, roots):
    bases = roots
    if site.level:
        parent = file.parent
        for _ in range(site.level - 1):
            parent = parent.parent
        bases = (
            [parent]
            if any(
                file.is_relative_to(base)
                and parent.is_relative_to(base)
                and parent != base
                for base in roots
            )
            else []
        )
    elif roots and file.parent.name == file.parent.parent.name + "__tests":
        bases = [file.parent, *roots]
    return bases


def _record_occurrence(
    site, source_key, written, target, status, seen, nodes, occurrences, edges
):
    dedup = (
        source_key,
        site.line,
        site.column,
        target or (written, site.name),
    )
    if dedup in seen:
        return
    seen.add(dedup)
    identity = (
        source_key,
        site.line,
        site.column,
        site.module,
        site.name,
        site.level,
    )
    occurrence_key = (
        "occurrence:" + hashlib.sha256(repr(identity).encode()).hexdigest()
    )
    occurrences.append(
        (
            occurrence_key,
            source_key,
            target,
            written,
            site.line,
            site.column,
            status,
            site.type_only,
        )
    )
    if target:
        _add_target_edges(source_key, target, occurrence_key, nodes, edges)


def _realization_tests(root, nodes, components):
    packages = {
        row[3]: row[0]
        for row in nodes
        if row[1] == "package" and row[3] is not None
    }
    targets = packages | (components or {})
    for _, kind, _, path, _, owner in nodes:
        if (
            kind == "module"
            and owner
            and PurePosixPath(path).stem != "_bypass__shared"
        ):
            targets[PurePosixPath(path).parent.as_posix()] = owner
    test_edges = []
    test_keys = set()
    for path, key in sorted(packages.items()):
        directory = PurePosixPath(path)
        parent = directory.parent
        if directory.name == (parent.name or root.name) + "__tests":
            test_keys.add(key)
            if target := targets.get(parent.as_posix()):
                test_edges.append((key, target))
    return test_edges, test_keys


def _add_target_edges(source_key, target, occurrence_key, nodes, edges):
    if target not in nodes:
        relative = target.removeprefix("package:local:")
        nodes[target] = (
            target,
            "namespace",
            "python",
            relative,
            None,
            None,
        )
    edges.extend(_edges(source_key, target, occurrence_key, nodes))
