"""Render the narrowing tree and its source-backed namespace context."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declarations.views.views__shared \
    import (
        primary_tree,
        read_edges,
        read_nodes,
    )  # fmt: skip


_NAMESPACE = re.compile(
    (
        "^(ANECHOIC_MODEL|ANECHOIC_STRUCTURE|ANECHOIC\\s*<\\+\\s*(?:MODEL|STRU"
        "CTURE))(?:\\s*<\\+\\s*(.+))?$"
    )
)


def _source_ref(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if not isinstance(value, Mapping):
        return None
    atom_id = value.get("atom_id")
    version = value.get("version")
    if atom_id is None:
        return None
    return f"{atom_id}@{version}" if version is not None else str(atom_id)


def _refs(value: object) -> list[str]:
    if isinstance(value, Mapping):
        for key in ("declaration_refs", "source_refs", "source"):
            if key in value:
                return _refs(value[key])
        ref = _source_ref(value)
        return [ref] if ref else []
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        return list(
            dict.fromkeys(ref for item in value for ref in _refs(item))
        )
    ref = _source_ref(value)
    return [ref] if ref else []


def _tree(data: Mapping[str, Any]) -> list[str]:
    graph = data["tree"]
    nodes = read_nodes(graph["nodes"])
    narrowing = [
        edge for edge in graph["edges"] if edge["kind"] == "NARROWER_THAN"
    ]
    children, _, _, _ = read_edges(narrowing, nodes)
    lines, _, _ = primary_tree(nodes, children, set(nodes))
    return lines


def _namespace_path(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, str):
        return None
    match = _NAMESPACE.fullmatch(" ".join(value.strip().split()))
    if not match:
        return None
    tail = (
        []
        if match.group(2) is None
        else [part.strip() for part in re.split(r"\s*<\+\s*", match.group(2))]
    )
    root = tuple(
        part.strip() for part in re.split(r"\s*<\+\s*", match.group(1))
    )
    return (*root, *tail) if all(tail) else None


def _namespace_rows(
    data: Mapping[str, Any],
) -> dict[tuple[str, ...], set[str]]:
    rows: dict[tuple[str, ...], set[str]] = {}

    def add(subject: object, source: object) -> None:
        path = _namespace_path(subject)
        refs = _refs(source)
        if path is not None and refs:
            rows.setdefault(path, set()).update(refs)

    for row in data.get("namespaces", []):
        if isinstance(row, Mapping):
            add(row.get("subject"), row.get("source"))
    for owner in data["tree_provenance"].get("owners", []):
        if isinstance(owner, Mapping):
            subjects = owner.get("subjects", owner.get("subject"))
            if isinstance(subjects, Mapping):
                subjects = subjects.get("active", subjects.get("governs"))
            if isinstance(subjects, Sequence) and not isinstance(
                subjects, (str, bytes, bytearray)
            ):
                for subject in subjects:
                    add(subject, owner.get("source"))
            else:
                add(subjects, owner.get("source"))
    return rows


def _render_namespace(rows: Mapping[tuple[str, ...], set[str]]) -> list[str]:
    if not rows:
        return []
    children: dict[tuple[str, ...], set[str]] = {}
    refs: dict[tuple[str, ...], set[str]] = {}
    for path, source_refs in rows.items():
        for index in range(1, len(path) + 1):
            prefix = path[:index]
            refs.setdefault(prefix, set()).update(source_refs)
            if index > 1:
                children.setdefault(path[: index - 1], set()).add(
                    path[index - 1]
                )

    def walk(prefix: tuple[str, ...], depth: int) -> list[str]:
        lines: list[str] = []
        for child in sorted(children.get(prefix, ())):
            current = prefix + (child,)
            suffix = (
                f" [{', '.join(sorted(refs[current]))}]"
                if refs.get(current)
                else ""
            )
            lines.append("  " * depth + f"<+ {child}{suffix}")
            lines.extend(walk(current, depth + 1))
        return lines

    lines = ["## Namespace context", "", "```text"]
    for root in sorted(path for path in refs if len(path) == 1):
        lines.extend([root[0], *walk(root, 1)])
    return [*lines, "```", ""]
