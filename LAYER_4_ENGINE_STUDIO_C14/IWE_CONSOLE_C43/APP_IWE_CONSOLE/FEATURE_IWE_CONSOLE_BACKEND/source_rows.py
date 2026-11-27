
"""Map parsed Atom and Scope Unit sources to raw Workbench rows."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub import canonical_row



def scope(item: Any, root: Path) -> dict[str, Any]:
    return {
        "name": item.name,
        "scope_unit_id": item.scope_unit_id,
        "parent_name": item.parent,
        "declared_label": item.label,
        "ordered": item.ordered,
        "order_number": item.local_order,
        "declaration_source_path": item.source.relative_to(root).as_posix(),
        "declaration_version": item.version,
        "relation_edges_json": [],
        "hash": None,
    }


def _same_types(before: Any, after: Any) -> bool:
    if type(before) is not type(after):
        return False
    if isinstance(before, dict):
        return before.keys() == after.keys() and all(_same_types(value, after[key]) for key, value in before.items())
    if isinstance(before, (list, tuple)):
        return len(before) == len(after) and all(_same_types(left, right) for left, right in zip(before, after))
    return True


def same_row(
    before: tuple[tuple[int, ...], dict[str, Any]] | None,
    after: tuple[tuple[int, ...], dict[str, Any]] | None,
) -> bool:
    if before is None or after is None:
        return before is after
    if before[1] is after[1]:
        return True
    return (
        _same_types(before[1], after[1])
        and before[1].get("_content_bytes") == after[1].get("_content_bytes")
        and canonical_row(before[1]) == canonical_row(after[1])
    )


class ReferenceIndex:
    """Track one selected carrier per reference and retain later copies for audits."""

    def __init__(self) -> None:
        self.paths: dict[str, set[Path]] = {}
        self.accepted: set[Path] = set()

    def paths_for(self, reference: str) -> set[Path]:
        return self.paths.get(reference, set())

    def paths_by_reference(self, references: set[str]) -> dict[str, set[Path]]:
        return {reference: self.paths.get(reference, set()) for reference in references}

    def accepted_paths(self, paths: set[Path] | None = None) -> set[Path]:
        return set(self.accepted) if paths is None else self.accepted & paths

    def rebuild(self, rows: Mapping[Path, Mapping[str, Any]]) -> None:
        self.paths = {}
        for path, row in rows.items():
            if (reference := _reference(row)) is not None:
                self.paths.setdefault(reference, set()).add(path)
        self.accepted = {
            path for path, row in rows.items()
            if (reference := _reference(row)) is None or path == min(self.paths[reference], key=_path_rank)
        }

    def update(
        self, before: Mapping[Path, Mapping[str, Any] | None],
        after: Callable[[Path], Mapping[str, Any] | None], affected: set[Path],
    ) -> set[Path]:
        impacted = set(affected)
        references = {
            reference
            for lookup in (before.get, after) for path in affected
            if (row := lookup(path)) is not None and (reference := _reference(row)) is not None
        }
        for reference in references:
            old = set(self.paths.get(reference, ()))
            for path in affected:
                if _reference(before.get(path)) == reference:
                    self.paths[reference].discard(path)
                if _reference(after(path)) == reference:
                    self.paths.setdefault(reference, set()).add(path)
            current = self.paths.get(reference, set())
            if not current:
                self.paths.pop(reference, None)
            impacted.update(old | current)
        for path in impacted:
            row = after(path)
            reference = _reference(row)
            if row is not None and (reference is None or path == min(self.paths[reference], key=_path_rank)):
                self.accepted.add(path)
            else:
                self.accepted.discard(path)
        return impacted


def _reference(row: Mapping[str, Any] | None) -> str | None:
    value = row.get("ref") if row is not None else None
    return value if isinstance(value, str) else None


def _path_rank(path: Path) -> tuple[bool, Path]:
    return "_projection" in path.parts, path


def file_signature(path: Path) -> tuple[int, ...] | None:
    try:
        item = path.stat()
        return item.st_mode, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns
    except OSError:
        return None
