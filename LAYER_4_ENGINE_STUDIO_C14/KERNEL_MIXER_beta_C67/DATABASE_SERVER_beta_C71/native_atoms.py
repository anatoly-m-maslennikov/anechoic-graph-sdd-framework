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


def _validate_lenses(atoms, lenses):
    current_specs = {atom["reference"] for atom in atoms if atom["status_group"] == "Current"
                     and "-S-" in atom["reference"]}
    if (not isinstance(lenses, list) or any(
        not isinstance(row, list) or len(row) != 2 or not _string(row[0]) or row[0] not in current_specs
        or not _string(row[1]) for row in lenses
    ) or len({row[0] for row in lenses}) != len(lenses)):
        raise ValueError("Invalid native lifecycle Lens rows")


def validate_native_snapshot(snapshot, manifest_sha256):
    """Reject malformed or inconsistent snapshots before any database mutation."""
    if (not isinstance(snapshot, dict) or set(snapshot) - {"spec_sizes", "lifecycle_lenses"} != {"schema_version", "manifest_sha256", "atoms", "relations", "relation_types"}
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
    measured = {atom["exact_ref"] for atom in atoms if atom["status_group"] == "Current"
                and re.fullmatch(r"[A-Z][A-Z0-9]*-S-[0-9]+@[1-9][0-9]*", atom["exact_ref"])}
    sizes = snapshot.get("spec_sizes", [])
    if (not isinstance(sizes, list) or any(
        not isinstance(row, list) or len(row) != 5 or not _string(row[0]) or row[0] not in measured
        or any(type(value) is not int or value < 0 for value in row[1:])
        or row[3] > row[1] or row[4] > row[2] for row in sizes
    ) or ("spec_sizes" in snapshot and {row[0] for row in sizes} != measured)):
        raise ValueError("Invalid native Spec size rows")
    _validate_lenses(atoms, snapshot.get("lifecycle_lenses", []))
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


def stage_atom_rows(connection, atoms):
    """Stage validated Atom rows once for both public tables."""
    keys = ("reference", "summary", "relative_path", "filename", "status_group", "version", "status", "exact_ref")
    rows = [{key: row[key] for key in keys} for row in atoms]
    connection.execute('''CREATE OR REPLACE TEMP TABLE int_admission_atoms AS
        SELECT atom.reference AS reference, atom.summary AS "content.summary",
            atom.relative_path AS relative_path, atom.filename AS filename,
            atom.status_group AS status_group, atom.version AS "header.state.version",
            atom.status AS "header.state.status", atom.exact_ref AS exact_ref
        FROM UNNEST(?::STRUCT(reference VARCHAR, summary VARCHAR, relative_path VARCHAR,
            filename VARCHAR, status_group VARCHAR, version BIGINT, status VARCHAR, exact_ref VARCHAR)[]) AS t(atom)''', [rows])


def write_staged_atoms(connection):
    """Insert the staged rows into both public Atom tables."""
    connection.execute('''INSERT INTO main.mrt_atoms
        SELECT reference, "content.summary", relative_path, filename, status_group,
            "header.state.version", "header.state.status" FROM int_admission_atoms''')
    connection.execute('''INSERT INTO main.mrt_atom_references
        SELECT relative_path, filename, status_group, reference,
            CASE WHEN status_group = 'Current' THEN reference ELSE NULL END, exact_ref
        FROM int_admission_atoms''')


def replace_native_atoms(connection, snapshot):
    """Replace public tables inside the caller's active transaction."""
    existing = connection.execute("SELECT table_type FROM information_schema.tables WHERE table_catalog = current_database() "
                                  "AND table_schema = 'main' AND table_name = 'mrt_atom_references'").fetchone()
    if existing and existing[0] == "VIEW":
        connection.execute("DROP VIEW main.mrt_atom_references")
    connection.execute('''CREATE OR REPLACE TABLE main.mrt_atoms (
        reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR, relative_path VARCHAR,
        filename VARCHAR, status_group VARCHAR, "header.state.version" BIGINT,
        "header.state.status" VARCHAR)''')
    connection.execute('''CREATE OR REPLACE TABLE main.mrt_atom_references (
        relative_path VARCHAR, filename VARCHAR, status_group VARCHAR, reference VARCHAR,
        stable_ref VARCHAR, exact_ref VARCHAR)''')
    stage_atom_rows(connection, snapshot["atoms"])
    write_staged_atoms(connection)
    connection.execute("DROP TABLE int_admission_atoms")
    connection.execute('''CREATE OR REPLACE TABLE main.mrt_atom_graph_relations (
        source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR, target_ref VARCHAR,
        relation_type VARCHAR, derived BOOLEAN)''')
    relation_keys = ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")
    relations = [{key: row[key] for key in relation_keys} for row in snapshot["relations"]]
    connection.execute('''INSERT INTO main.mrt_atom_graph_relations
        SELECT edge.source_kind, edge.source_ref, edge.target_kind, edge.target_ref, edge.relation_type, edge.derived
        FROM UNNEST(?::STRUCT(source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR,
            target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)[]) AS t(edge)''', [relations])

    connection.execute("DROP TABLE IF EXISTS main.int_lifecycle_lenses")
    if "lifecycle_lenses" in snapshot:
        connection.execute("CREATE TABLE main.int_lifecycle_lenses (reference VARCHAR PRIMARY KEY, lens VARCHAR NOT NULL)")
        if snapshot["lifecycle_lenses"]:
            connection.executemany("INSERT INTO main.int_lifecycle_lenses VALUES (?, ?)", snapshot["lifecycle_lenses"])
