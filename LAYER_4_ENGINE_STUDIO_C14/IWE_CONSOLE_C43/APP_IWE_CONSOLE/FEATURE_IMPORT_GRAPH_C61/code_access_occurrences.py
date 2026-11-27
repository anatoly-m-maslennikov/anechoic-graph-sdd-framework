"""Expose each captured Python import for Code Access validation."""

from __future__ import annotations

from dataclasses import replace
from functools import cache, partial
from importlib import metadata
from pathlib import Path, PurePosixPath
import sys

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ._resolution_graph import _lookup_bases
from .resolution import (
    _environment_root,
    _external,
    _lookup,
    _packages,
    _roots,
)
from .source import Source
from .web_imports import _WEB, lookup_web


@dataclass(
    frozen=True, slots=True, config=ConfigDict(strict=True, extra="forbid")
)
class CodeAccessOccurrence:
    source_path: str
    target_path: str | None
    target_kind: str | None
    unit: str | None
    written: str
    line: int
    column: int
    status: str


def _external_imports(root, roots, python_roots):
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


def _occurrence(path, site, lookup, *, python):
    written, target, status = lookup(site)
    if python and site.name is not None:
        written = f"from {written} import {site.name}"
    unit = site.name if python else None
    if unit and unit != "*":
        _, bare_target, _ = lookup(replace(site, name=None))
        if target is not None and target != bare_target:
            unit = None
    kind, _, key = target.partition(":") if target else (None, None, None)
    target_path = None
    if status in {"internal", "asset"}:
        target_path = key.removeprefix("local:") if kind == "package" else key
    return CodeAccessOccurrence(
        path,
        target_path,
        kind,
        unit,
        written,
        site.line,
        site.column,
        status,
    )


def _site_lookup(
    python,
    root,
    file,
    sources,
    source_roots,
    source_external,
    packages,
    nodes,
    image_modules,
    lookup_bases,
):
    if python:
        return partial(
            _lookup,
            parent=file.parent,
            roots=source_roots,
            sources=sources,
            packages=packages,
            external=source_external,
            nodes=nodes,
            image_modules=image_modules,
            lookup_bases=lookup_bases,
        )
    else:
        return partial(
            lookup_web,
            root,
            file=file,
            sources=sources,
            nodes=nodes,
            include_asset_target=True,
        )


def code_access_occurrences(
    root: Path,
    sources: dict[str, Source],
    python_roots: tuple[str, ...] | None = (".",),
    *,
    python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[set[str], tuple[CodeAccessOccurrence, ...]]:
    """Return namespace Package paths and resolved import sites."""

    root = Path(root).resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes, facts = {}, []
    external_by_root, external = _external_imports(root, roots, python_roots)
    lookup_bases = cache(_lookup_bases)
    for path, source in sorted(sources.items()):
        if source.language not in _WEB and source.language != "python":
            continue
        file = PurePosixPath(path)
        image_modules = (python_image_imports or {}).get(path, ())
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
        python = source.language == "python"
        lookup = _site_lookup(
            python,
            root,
            file,
            sources,
            source_roots,
            source_external,
            packages,
            nodes,
            image_modules,
            lookup_bases,
        )
        facts.extend(
            _occurrence(path, site, lookup, python=python)
            for site in source.imports
        )
    return packages, tuple(facts)
