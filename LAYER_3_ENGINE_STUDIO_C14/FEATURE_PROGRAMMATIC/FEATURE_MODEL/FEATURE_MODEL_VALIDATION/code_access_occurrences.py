"""Expose each captured Python import for Code Access validation."""

from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from LAYER_3_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import (
    _external, _lookup, _packages, _roots,
)
from LAYER_3_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import Source


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
    root: Path, sources: dict[str, Source], python_roots: tuple[str, ...] = (".",),
) -> tuple[CodeAccessOccurrence, ...]:
    root = Path(root).resolve()
    roots = _roots(root, python_roots)
    packages = _packages(sources, roots)
    nodes = {}
    external = _external(root)
    facts = []
    for path, source in sorted(sources.items()):
        if source.language != "python":
            continue
        file = PurePosixPath(path)
        for site in source.imports:
            written, target, status = _lookup(site, file, roots, sources, packages, external, nodes)
            if site.name is not None:
                written = f"from {written} import {site.name}"
            unit = site.name
            if unit and unit != "*":
                _, bare_target, _ = _lookup(
                    replace(site, name=None), file, roots, sources, packages, external, nodes,
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
    return tuple(facts)
