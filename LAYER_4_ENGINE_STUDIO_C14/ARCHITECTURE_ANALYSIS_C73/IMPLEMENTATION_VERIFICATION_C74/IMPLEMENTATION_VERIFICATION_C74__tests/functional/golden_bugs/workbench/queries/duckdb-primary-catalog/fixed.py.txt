"""Validate and publish the native Atom snapshot at the database boundary."""
from __future__ import annotations

from pathlib import PurePosixPath
import re

_ATOM = re.compile(r"[A-Z]+-[STPC]-[0-9]+")
_ATOM_REF = re.compile(r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?")
_CURRENT = {
    "S": {"active", "ready"},
    "T": {"active", "in_queue", "backlog", "done", "canceled", "resolved", "complete"},
    "P": {"active"}, "C": {"active"},
}
_ATOM_FIELDS = {"reference", "exact_ref", "status_group", "relative_path", "filename", "summary", "status", "version"}
_EDGE_FIELDS = {"source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived"}


def _string(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def _endpoint(kind, ref):
    return (kind == "Atom" and bool(_ATOM_REF.fullmatch(ref)) or
            kind == "Component" and bool(re.fullmatch(r"C[0-9]+", ref)))


def _atom_references(atoms):
    exacts, references, paths = set(), set(), set()
    for row in atoms:
        if (not isinstance(row, dict) or set(row) != _ATOM_FIELDS
                or any(not _string(row[key]) for key in _ATOM_FIELDS - {"version", "summary"})
                or not isinstance(row["summary"], str) or type(row["version"]) is not int or row["version"] < 1):
            raise ValueError("Invalid native Atom fields")
        exact, group, status = row["exact_ref"], row["status_group"], row["status"]
        identity = exact.split("@", 1)[0]
        if not _ATOM.fullmatch(identity):
            raise ValueError("Invalid native Atom identity")
        family = identity.split("-")[1]
        expected_group = "Current" if status in _CURRENT[family] else status.title() if status in {"draft", "archived"} else None
        expected_exact = f'{identity}@{row["version"]}' + ("-draft" if status == "draft" else "")
        expected_ref = identity if group == "Current" else expected_exact
        if group != expected_group or exact != expected_exact or row["reference"] != expected_ref:
            raise ValueError("Native Atom identity, version or status disagrees")
        path, filename = row["relative_path"], row["filename"]
        parts = PurePosixPath(path).parts
        if (path.startswith("/") or "\\" in path or any(part in {"..", "."} for part in parts)
                or str(PurePosixPath(path)) != path or filename in {".", ".."}
                or "/" in filename or "\\" in filename or not filename.endswith(".md")):
            raise ValueError("Invalid native Atom path")
        location = (path, filename)
        if exact in exacts or row["reference"] in references or location in paths:
            raise ValueError("Duplicate native Atom revision, reference or path")
        exacts.add(exact)
        references.add(row["reference"])
        paths.add(location)
    return references


def validate_native_snapshot(snapshot, manifest_sha256):
    """Reject malformed or inconsistent snapshots before any database mutation."""
    if (not isinstance(snapshot, dict) or set(snapshot) != {"schema_version", "manifest_sha256", "atoms", "relations", "relation_types"}
            or type(snapshot["schema_version"]) is not int or snapshot["schema_version"] != 2
            or not isinstance(manifest_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256)
            or snapshot["manifest_sha256"] != manifest_sha256):
        raise ValueError("Invalid native snapshot envelope or manifest digest")
    atoms, relations, types = (snapshot[key] for key in ("atoms", "relations", "relation_types"))
    if not all(isinstance(value, list) for value in (atoms, relations, types)):
        raise ValueError("Native snapshot collections must be lists")
    if any(not _string(name) for name in types) or len(set(types)) != len(types):
        raise ValueError("Invalid native relation declarations")
    references = _atom_references(atoms)
    for edge in relations:
        if (not isinstance(edge, dict) or set(edge) != _EDGE_FIELDS
                or any(not _string(edge[key]) for key in _EDGE_FIELDS - {"derived"})
                or type(edge["derived"]) is not bool or edge["relation_type"] not in types
                or not _endpoint(edge["source_kind"], edge["source_ref"])
                or not _endpoint(edge["target_kind"], edge["target_ref"])):
            raise ValueError("Invalid native relation")
        if not edge["derived"] and (edge["source_kind"] != "Atom" or edge["source_ref"] not in references):
            raise ValueError("Native relation has no source carrier")
    return snapshot


def replace_native_atoms(connection, snapshot):
    """Replace public tables inside the caller's active transaction."""
    existing = connection.execute("SELECT table_type FROM information_schema.tables WHERE table_catalog = current_database() "
                                  "AND table_schema = 'main' AND table_name = 'native_references'").fetchone()
    if existing and existing[0] == "VIEW":
        connection.execute("DROP VIEW main.native_references")
    connection.execute('''CREATE OR REPLACE TABLE main.atoms (
        reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR, relative_path VARCHAR,
        filename VARCHAR, status_group VARCHAR, "header.state.version" BIGINT,
        "header.state.status" VARCHAR)''')
    rows = snapshot["atoms"]
    if rows:
        connection.executemany('INSERT INTO main.atoms VALUES (?, ?, ?, ?, ?, ?, ?)', [
            (r["reference"], r["summary"], r["relative_path"], r["filename"], r["status_group"], r["version"], r["status"])
            for r in rows])
    connection.execute('''CREATE OR REPLACE TABLE main.native_references (
        relative_path VARCHAR, filename VARCHAR, status_group VARCHAR, reference VARCHAR,
        stable_ref VARCHAR, exact_ref VARCHAR)''')
    if rows:
        connection.executemany('INSERT INTO main.native_references VALUES (?, ?, ?, ?, ?, ?)', [
            (r["relative_path"], r["filename"], r["status_group"], r["reference"],
             r["reference"] if r["status_group"] == "Current" else None, r["exact_ref"]) for r in rows])
    connection.execute('''CREATE OR REPLACE TABLE main.relations (
        source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR, target_ref VARCHAR,
        relation_type VARCHAR, derived BOOLEAN)''')
    if snapshot["relations"]:
        connection.executemany('INSERT INTO main.relations VALUES (?, ?, ?, ?, ?, ?)', [
            tuple(r[key] for key in ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived"))
            for r in snapshot["relations"]])
