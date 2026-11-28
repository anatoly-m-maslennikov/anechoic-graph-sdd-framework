"""Validate and publish the native Atom snapshot at the database boundary."""

from __future__ import annotations

from pathlib import PurePosixPath
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import validate_carrier_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native_atom_records import DuplicateNativeAtom as DuplicateNativeAtom, NativeAtom as NativeAtom, NativeRelation as NativeRelation, _atom_references, _string, _validate_relation_records
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    status_domains as _status_domains,
)

NATIVE_PROJECTION_COLUMNS = {
    "mrt_atoms": (
        ("reference", "VARCHAR"),
        ("content.summary", "VARCHAR"),
        ("relative_path", "VARCHAR"),
        ("filename", "VARCHAR"),
        ("status_group", "VARCHAR"),
        ("header.state.version", "BIGINT"),
        ("header.state.status", "VARCHAR"),
        ("header.container.component", "VARCHAR"),
        ("header.tier", "BIGINT"),
        ("header.context.template", "VARCHAR"),
    ),
    "mrt_atom_references": tuple(
        (name, "VARCHAR")
        for name in (
            "relative_path",
            "filename",
            "status_group",
            "reference",
            "stable_ref",
            "exact_ref",
        )
    ),
    "mrt_atom_graph_relations": tuple(
        (name, "VARCHAR")
        for name in (
            "source_kind",
            "source_ref",
            "target_kind",
            "target_ref",
            "relation_type",
        )
    )
    + (("derived", "BOOLEAN"),),
}


class _NativeSnapshot(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    schema_version: int
    manifest_sha256: str
    atoms: object
    relations: object
    relation_types: object
    spec_sizes: object = Field(default_factory=list)
    lifecycle_lenses: object = Field(default_factory=list)
    ingestion_issues: object = Field(default_factory=list)


def _validate_lenses(atoms, lenses):
    current_specs = {
        atom.reference
        for atom in atoms
        if atom.status_group == "Current" and "-S-" in atom.reference
    }
    if (
        not isinstance(lenses, list)
        or any(
            not isinstance(row, list)
            or len(row) != 2
            or not _string(row[0])
            or row[0] not in current_specs
            or not _string(row[1])
            for row in lenses
        )
        or len({row[0] for row in lenses}) != len(lenses)
    ):
        raise ValueError("Invalid native lifecycle Lens rows")


def _snapshot_record(snapshot, manifest_sha256):
    message = "Invalid native snapshot envelope or manifest digest"
    if not isinstance(snapshot, dict):
        raise ValueError(message)
    try:
        record = _NativeSnapshot.model_validate(snapshot)
    except ValidationError as error:
        raise ValueError(message) from error
    if (
        record.schema_version != 2
        or record.manifest_sha256 != manifest_sha256
        or not re.fullmatch(r"[0-9a-f]{64}", record.manifest_sha256)
    ):
        raise ValueError(message)
    return record


def validate_native_snapshot(snapshot, manifest_sha256, bindings=None):
    "Reject malformed or inconsistent snapshots before any database mutation."
    record = _snapshot_record(snapshot, manifest_sha256)
    atoms, relations, types = (
        record.atoms,
        record.relations,
        record.relation_types,
    )
    if not all(isinstance(value, list) for value in (atoms, relations, types)):
        raise ValueError("Native snapshot collections must be lists")
    if any(not _string(name) for name in types) or len(set(types)) != len(
        types
    ):
        raise ValueError("Invalid native relation declarations")
    references, atoms = _atom_references(
        atoms, _status_domains(bindings or {})
    )
    validate_carrier_issues(
        record.ingestion_issues,
        {
            str(PurePosixPath(row.relative_path) / row.filename): row.exact_ref
            for row in atoms
        },
    )
    _validate_spec_sizes(record, atoms)
    _validate_lenses(atoms, record.lifecycle_lenses)
    return atoms, _validate_relation_records(relations, types, references)


def _validate_spec_sizes(record, atoms):
    measured = {
        atom.exact_ref
        for atom in atoms
        if atom.status_group == "Current"
        and re.fullmatch(
            r"[A-Z][A-Z0-9]*-S-[0-9]+@[1-9][0-9]*", atom.exact_ref
        )
    }
    sizes = record.spec_sizes
    if (
        not isinstance(sizes, list)
        or any(
            not isinstance(row, list)
            or len(row) != 5
            or not _string(row[0])
            or row[0] not in measured
            or any(type(value) is not int or value < 0 for value in row[1:])
            or row[3] > row[1]
            or row[4] > row[2]
            for row in sizes
        )
        or (
            "spec_sizes" in record.model_fields_set
            and {row[0] for row in sizes} != measured
        )
    ):
        raise ValueError("Invalid native Spec size rows")


def stage_atom_rows(connection, rows):
    """Stage validated Atom rows once for both public tables."""
    connection.execute(
        """CREATE OR REPLACE TEMP TABLE int_admission_atoms AS
        SELECT atom.reference AS reference, atom.summary AS "content.summary",
            atom.relative_path AS relative_path, atom.filename AS filename,
            atom.status_group AS status_group, atom.version AS "header.state.version",
            atom.status AS "header.state.status", atom.exact_ref AS exact_ref,
            atom.container_component AS "header.container.component", atom.tier AS "header.tier",
            atom.template AS "header.context.template"
        FROM UNNEST(?::STRUCT(reference VARCHAR, summary VARCHAR, relative_path VARCHAR,
            filename VARCHAR, status_group VARCHAR, version BIGINT, status VARCHAR, exact_ref VARCHAR,
            container_component VARCHAR, tier BIGINT, template VARCHAR)[]) AS t(atom)""",
        [rows],
    )


def write_staged_atoms(connection):
    """Insert the staged rows into both public Atom tables."""
    connection.execute("""INSERT INTO main.mrt_atoms
        SELECT reference, "content.summary", relative_path, filename, status_group,
            "header.state.version", "header.state.status", "header.container.component",
            "header.tier", "header.context.template" FROM int_admission_atoms""")
    connection.execute("""INSERT INTO main.mrt_atom_references
        SELECT relative_path, filename, status_group, reference,
            CASE WHEN status_group = 'Current' THEN reference ELSE NULL END, exact_ref
        FROM int_admission_atoms""")


def replace_native_atoms(connection, snapshot):
    """Replace public tables inside the caller's active transaction."""
    existing = connection.execute(
        "SELECT table_type FROM information_schema.tables WHERE table_catalog = current_database() "
        "AND table_schema = 'main' AND table_name = 'mrt_atom_references'"
    ).fetchone()
    if existing and existing[0] == "VIEW":
        connection.execute("DROP VIEW main.mrt_atom_references")
    for table, columns in NATIVE_PROJECTION_COLUMNS.items():
        definitions = ", ".join(f'"{name}" {kind}' for name, kind in columns)
        key = ", PRIMARY KEY (reference)" if table == "mrt_atoms" else ""
        connection.execute(
            f"CREATE OR REPLACE TABLE main.{table} ({definitions}{key})"
        )
    stage_atom_rows(connection, snapshot["atoms"])
    write_staged_atoms(connection)
    connection.execute("DROP TABLE int_admission_atoms")
    connection.execute(
        """INSERT INTO main.mrt_atom_graph_relations
        SELECT edge.source_kind, edge.source_ref, edge.target_kind, edge.target_ref, edge.relation_type, edge.derived
        FROM UNNEST(?::STRUCT(source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR,
            target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)[]) AS t(edge)""",
        [snapshot["relations"]],
    )

    connection.execute("DROP TABLE IF EXISTS main.int_lifecycle_lenses")
    if "lifecycle_lenses" in snapshot:
        connection.execute(
            (
                "CREATE TABLE main.int_lifecycle_lenses (reference VARCHAR "
                "PRIMARY KEY, lens VARCHAR NOT NULL)"
            )
        )
        if snapshot["lifecycle_lenses"]:
            connection.executemany(
                "INSERT INTO main.int_lifecycle_lenses VALUES (?, ?)",
                snapshot["lifecycle_lenses"],
            )
