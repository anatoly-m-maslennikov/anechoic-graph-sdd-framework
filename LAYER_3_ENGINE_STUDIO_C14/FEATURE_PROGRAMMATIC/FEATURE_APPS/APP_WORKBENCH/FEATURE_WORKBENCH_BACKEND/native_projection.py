"""Publish a native capture through the existing Workbench DuckDB store."""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Set
from pathlib import PurePosixPath, PureWindowsPath
import re
from typing import Any

from .native_source_rows import NativeCapture
from .query_store import QueryStore


def _relation_bindings(relation_types, inverses):
    if (any(not isinstance(name, str) or not name for name in relation_types)
            or any(not isinstance(a, str) or not isinstance(b, str) or a == b
                   or a not in relation_types or b not in relation_types for a, b in inverses.items())
            or len(set(inverses.values())) != len(inverses)
            or set(inverses) & set(inverses.values())):
        raise ValueError("Invalid native relation declarations")
    inverse = dict(inverses) | {value: key for key, value in inverses.items()}
    if "CONTAINED_BY" not in inverse:
        raise ValueError("Native containment requires a declared inverse")
    return inverse


def _migration_rows(rows, migration_refs):
    exact_refs = {row["_exact_ref"] for row in rows}
    if len(exact_refs) != len(rows):
        raise ValueError("Duplicate native exact references")
    legacy = []
    paths = {}
    seen = set()
    for old_ref, original_path, target_ref in migration_refs:
        path = PurePosixPath(original_path)
        if (path.is_absolute() or PureWindowsPath(original_path).drive or "\\" in original_path
                or "\x00" in original_path or ".." in path.parts or path.suffix != ".md"
                or original_path != path.as_posix() or target_ref not in exact_refs):
            raise ValueError("Invalid native migration path or exact reference")
        if paths.setdefault(original_path, target_ref) != target_ref:
            raise ValueError(f"Conflicting exact references for native migration path {original_path!r}")
        if old_ref is None:
            continue
        key = old_ref, original_path
        if (not re.fullmatch(r"[A-Z]+-[A-Z]-[0-9]+@[1-9][0-9]*(?:-draft)?", old_ref)
                or key in seen
                or old_ref.rsplit("@", 1)[1].removesuffix("-draft")
                != target_ref.rsplit("@", 1)[1].removesuffix("-draft")):
            raise ValueError("Invalid legacy migration reference")
        seen.add(key)
        legacy.append((old_ref, original_path, target_ref))
    return legacy, list(paths.items())


def _authored_edges(row):
    relations = row["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        raise ValueError("Native relations must be a mapping")
    for name, targets in relations.items():
        if not isinstance(targets, list):
            raise ValueError("Native relation targets must be a list")
        for target in targets:
            if isinstance(target, str) and re.fullmatch(r"C[0-9]+", target):
                kind = "Component"
            elif isinstance(target, str) and re.fullmatch(r"[A-Z]+-[STP]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?", target):
                kind = "Atom"
            else:
                raise ValueError("Invalid native relation target")
            yield {"source_kind": "Atom", "source_ref": row["ref"], "target_kind": kind,
                   "target_ref": target, "relation_type": name, "derived": False}


def _projected_rows(capture, relation_types, inverse):
    rows = [{**row, "relation_edges_json": []} for row in capture.atoms]
    by_ref = {row["ref"]: row for row in rows}
    if len(by_ref) != len(rows) or None in by_ref:
        raise ValueError("Duplicate or missing native references")

    def add(edge: dict[str, Any]) -> None:
        name = edge["relation_type"]
        if name not in relation_types:
            raise ValueError(f"Undeclared native relation: {name}")
        owner = by_ref.get(edge["source_ref"])
        if owner is None or edge["source_kind"] != "Atom":
            raise ValueError("Native relation has no source carrier")
        owner["relation_edges_json"].append(edge)
        if name in inverse:
            owner["relation_edges_json"].append({
                "source_kind": edge["target_kind"], "source_ref": edge["target_ref"],
                "target_kind": edge["source_kind"], "target_ref": edge["source_ref"],
                "relation_type": inverse[name], "derived": True,
            })

    for edge in capture.containment:
        add(dict(edge))
    for row in rows:
        for edge in _authored_edges(row):
            add(edge)
    return rows


def project_native(store: QueryStore, capture: NativeCapture, *,
                   relation_types: Set[str], inverses: Mapping[str, str],
                   migration_refs: Iterable[tuple[str | None, str, str]] = ()) -> None:
    """Replace the disposable projection. Relation declarations must be caller-validated."""
    if capture.errors or not capture.atoms:
        raise ValueError("Cannot project a native capture with invalid carriers")
    inverse = _relation_bindings(relation_types, inverses)
    rows = _projected_rows(capture, relation_types, inverse)
    legacy, paths = _migration_rows(rows, migration_refs)
    with store._lock:
        store.replace(rows, [], relation_types=set(relation_types))
        try:
            store._connection.execute('''CREATE OR REPLACE VIEW main.native_references AS
                SELECT relative_path, filename, status_group, reference,
                       CASE WHEN status_group = 'Current' THEN reference END AS stable_ref,
                       "header.identity.atom_id" || '@' || CAST("header.state.version" AS VARCHAR) ||
                       CASE WHEN status_group = 'Draft' THEN '-draft' ELSE '' END AS exact_ref
                FROM main.atoms''')
            store._connection.execute('''CREATE OR REPLACE TABLE main.native_legacy_references (
                legacy_ref VARCHAR, original_path VARCHAR, exact_ref VARCHAR,
                PRIMARY KEY (legacy_ref, original_path))''')
            if legacy:
                store._connection.executemany(
                    "INSERT INTO main.native_legacy_references VALUES (?, ?, ?)", legacy)
            store._connection.execute('''CREATE OR REPLACE TABLE main.native_migration_paths (
                original_path VARCHAR PRIMARY KEY, exact_ref VARCHAR NOT NULL)''')
            if paths:
                store._connection.executemany("INSERT INTO main.native_migration_paths VALUES (?, ?)", paths)
        except Exception:
            store._available = False
            raise
