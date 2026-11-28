"""Resolve static imports against inventoried files, without importing \
project code."""

from __future__ import annotations

from functools import cache
import hashlib as hashlib
from importlib import metadata
import json as json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

from ._resolution_graph import (
    _candidates as _candidates,
    _edges as _edges,
    _external_manifest,
    _lookup_bases,
    _record_occurrence,
    _realization_tests,
    _nodes as _nodes,
    _packages as _packages,
)
from ..SOURCE_CAPTURE.SOURCE_CAPTURE__shared import Source
from ..SOURCE_CAPTURE.web_imports import _WEB, lookup_web


_ENVIRONMENTS = {
    "LAYER_4_ENGINE_STUDIO_C14": "engine",
    "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27": "release",
    "LAYER_5_USER_SETUP_C65": "setup",
}


def _environment_root(root: Path, base: PurePosixPath) -> Path:
    name = _ENVIRONMENTS.get(base.as_posix())
    environment = (
        root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72" / name
        if name
        else root / base.as_posix()
    )
    if name and not environment.is_symlink() and environment.is_dir():
        return environment
    return root / base.as_posix()


def _roots(
    root: Path, python_roots: tuple[str, ...] | None
) -> tuple[PurePosixPath, ...]:
    if python_roots is None:
        discovered = []
        for child in sorted(
            {*root.iterdir(), *(root / name for name in _ENVIRONMENTS)}
        ):
            relative = child.relative_to(root).as_posix()
            environment = _environment_root(root, PurePosixPath(relative))
            manifest, lock = (
                environment / "pyproject.toml",
                environment / "uv.lock",
            )
            if (
                child.is_symlink()
                or not child.is_dir()
                or manifest.is_symlink()
                or lock.is_symlink()
            ):
                continue
            if not manifest.is_file() or not lock.is_file():
                continue
            with manifest.open("rb") as handle:
                if isinstance(tomllib.load(handle).get("project"), dict):
                    discovered.append(relative)
        python_roots = tuple(discovered) or (".",)
    roots = []
    for value in python_roots:
        path = (root / value).resolve()
        if not path.is_relative_to(root) or not path.is_dir():
            raise ValueError(
                f"Python root is not a directory inside the workspace: {value}"
            )
        roots.append(PurePosixPath(path.relative_to(root).as_posix()))

    return tuple(roots)


def _external(
    root: Path, installed: dict | None = None, *, locked: bool = False
) -> set[str]:
    project_name, dependencies = _external_manifest(root)
    external = set(sys.stdlib_module_names) | dependencies

    lock_names = set()
    if locked:
        with (root / "uv.lock").open("rb") as handle:
            lock_names = {
                re.sub(r"[-_.]+", "-", package["name"]).lower()
                for package in tomllib.load(handle).get("package", [])
                if isinstance(package, dict)
                and isinstance(package.get("name"), str)
            }
    for name, distributions in (
        installed
        if installed is not None
        else metadata.packages_distributions()
    ).items():
        normalized = {
            re.sub(r"[-_.]+", "-", distribution).lower()
            for distribution in distributions
        }
        if (
            normalized
            and project_name not in normalized
            and (not locked or normalized & lock_names)
        ):
            external.add(name)
    return external


def _child_matches(site, name, bases, roots, sources, packages, matches):
    if site.name and site.name != "*":
        child_bases = bases
        if (
            not site.level
            and bases != roots
            and _candidates(name, bases[:1], sources, packages)
        ):
            child_bases = bases[:1]
        child = _candidates(
            ".".join(filter(None, (name, site.name))),
            child_bases,
            sources,
            packages,
        )
        if child:
            matches = child
    return matches


def _lookup(
    site,
    parent,
    roots,
    sources,
    packages,
    external,
    nodes,
    image_modules=(),
    *,
    lookup_bases,
):
    written = "." * site.level + site.module
    name = site.module
    bases = lookup_bases(site.level, parent, roots)
    matches = _candidates(name, bases, sources, packages)
    matches = _child_matches(
        site, name, bases, roots, sources, packages, matches
    )
    target = matches[0] if len(matches) == 1 else None
    status = "internal" if target else "ambiguous" if matches else "unresolved"
    external_name = name.partition(".")[0]
    if (
        not matches
        and not site.level
        and (site.previous_image or name in image_modules)
    ):
        status, target = "external", f"module:external:previous-image:{name}"
        nodes[target] = (
            target,
            "module",
            "python",
            None,
            "declared_previous_image",
            None,
        )
    elif not matches and not site.level and external_name in external:
        kind = (
            "module"
            if external_name in sys.builtin_module_names
            else "package"
        )
        status, target = "external", f"{kind}:external:{external_name}"
        nodes[target] = (target, kind, "python", None, None, None)
    return written, target, status


def _resolve_source(path, source, context, output, lookup_bases):
    (
        root,
        roots,
        python_roots,
        images,
        sources,
        packages,
        external_by_root,
        external,
    ) = context
    nodes, seen, occurrences, edges = output
    if source.language not in _WEB and source.language != "python":
        return
    file = PurePosixPath(path)
    parent = file.parent
    image_modules = (images or {}).get(path, ())
    source_roots = (
        tuple(base for base in roots if file.is_relative_to(base))
        if python_roots is None
        else roots
    )
    source_external = (
        external_by_root[source_roots[0]]
        if source_roots and python_roots is None
        else external
    )
    for site in source.imports:
        if source.language in _WEB:
            result = lookup_web(root, site, file, sources, nodes)
        else:
            result = _lookup(
                site,
                parent,
                source_roots,
                sources,
                packages,
                source_external,
                nodes,
                image_modules,
                lookup_bases=lookup_bases,
            )
        _record_occurrence(
            site, f"module:{path}", *result, seen, nodes, occurrences, edges
        )


def _external_sets(root, roots, python_roots):
    installed = (
        metadata.packages_distributions() if python_roots is None else None
    )
    external_by_root = (
        {
            base: _external(
                _environment_root(root, base),
                installed,
                locked=base != PurePosixPath("."),
            )
            for base in roots
        }
        if python_roots is None
        else {}
    )
    external = (
        _external(root)
        if python_roots is not None
        else set(sys.stdlib_module_names)
    )
    return external_by_root, external


def resolve(
    root: Path,
    sources: dict[str, Source],
    python_roots: tuple[str, ...] | None = (".",),
    *,
    python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    root = root.resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes = _nodes(root, sources)
    external_by_root, external = _external_sets(root, roots, python_roots)
    occurrences: list[tuple] = []
    edges: list[tuple] = []
    seen = set()
    context = (
        root,
        roots,
        python_roots,
        python_image_imports,
        sources,
        packages,
        external_by_root,
        external,
    )
    output = (nodes, seen, occurrences, edges)
    lookup_bases = cache(_lookup_bases)
    for path, source in sorted(sources.items()):
        _resolve_source(path, source, context, output, lookup_bases)
    return list(nodes.values()), occurrences, edges


def resolve_realization(
    root: Path,
    sources: dict[str, Source],
    python_roots: tuple[str, ...] | None = (".",),
    *,
    components: dict[str, str] | None = None,
    python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[tuple], list[tuple], list[tuple], list[tuple], set[str]]:
    """Resolve imports and tests against direct Package paths and declared \
Components."""
    root = root.resolve()
    nodes, occurrences, edges = resolve(
        root, sources, python_roots, python_image_imports=python_image_imports
    )
    test_edges, test_keys = _realization_tests(root, nodes, components)
    return nodes, occurrences, edges, test_edges, test_keys
