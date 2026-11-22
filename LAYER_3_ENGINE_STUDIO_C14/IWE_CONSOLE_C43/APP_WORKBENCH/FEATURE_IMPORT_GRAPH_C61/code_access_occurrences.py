"""Expose each captured Python import for Code Access validation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from importlib import metadata
from pathlib import Path, PurePosixPath
import sys

from .resolution import _external, _lookup, _packages, _roots
from .source import Source


@dataclass(frozen=True, slots=True)
class CodeAccessOccurrence:
    source_path: str
    target_path: str | None
    target_kind: str | None
    unit: str | None
    written: str
    line: int
    column: int
    status: str


def code_access_occurrences(
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] | None = (".",),
    *, python_image_imports: dict[str, tuple[str, ...]] | None = None,
) -> tuple[set[str], tuple[CodeAccessOccurrence, ...]]:
    """Return namespace Package paths and resolved import sites from the capture."""

    root = Path(root).resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes = {}
    installed = metadata.packages_distributions() if python_roots is None else None
    external_by_root = {base: _external(root / base.as_posix(), installed, locked=base != PurePosixPath(".")) for base in roots} if python_roots is None else {}
    external = _external(root) if python_roots is not None else set(sys.stdlib_module_names)
    facts = []
    for path, source in sorted(sources.items()):
        if source.language != "python":
            continue
        file = PurePosixPath(path)
        image_modules = (python_image_imports or {}).get(path, ())
        source_roots = [base for base in roots if file.is_relative_to(base)] if python_roots is None else roots
        source_external = external_by_root[source_roots[0]] if source_roots and python_roots is None else external
        for site in source.imports:
            written, target, status = _lookup(site, file, source_roots, sources, packages, source_external, nodes, image_modules)
            if site.name is not None:
                written = f"from {written} import {site.name}"
            unit = site.name
            if unit and unit != "*":
                _, bare_target, _ = _lookup(
                    replace(site, name=None), file, source_roots, sources, packages, source_external, nodes, image_modules,
                )
                if target is not None and target != bare_target:
                    unit = None
            kind, _, key = target.partition(":") if target else (None, None, None)
            target_path = None
            if status == "internal":
                target_path = key.removeprefix("local:") if kind == "package" else key
            facts.append(CodeAccessOccurrence(
                path, target_path, kind,
                unit, written, site.line, site.column, status,
            ))
    return packages, tuple(facts)

