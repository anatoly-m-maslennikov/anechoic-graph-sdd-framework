"""Patch a projection snapshot from changed materialized rows."""

from .projection_types import ProjectionSnapshot
from ...index_delta import MaterializationDelta
from ...header_columns import HeaderSchema
from ...content_schema import ContentSchema
from .public_rows import atom_key, projected_rows


def _same_header_layout(left: HeaderSchema, right: HeaderSchema) -> bool:
    return tuple(
        (column.name, column.format) for column in left.columns
    ) == tuple((column.name, column.format) for column in right.columns)


def _delta_snapshot(
    previous: ProjectionSnapshot,
    delta: MaterializationDelta,
    header_schema: HeaderSchema,
    content_schema: ContentSchema,
) -> ProjectionSnapshot:
    """Patch public maps from materialized changed source rows."""
    if (
        not _same_header_layout(previous.header_schema, header_schema)
        or previous.content_schema.shape != content_schema.shape
    ):
        raise ValueError(
            "projection schema changed; full projection rebuild is required"
        )
    atoms = dict(previous.atoms)
    atom_sources = dict(previous.atom_sources)
    for row in delta.old_atoms.values():
        key = atom_key(row)
        atoms.pop(key, None)
        atom_sources.pop(key, None)
    new_atoms, new_scopes = projected_rows(
        list(delta.new_atoms.values()),
        list(delta.new_scopes.values()),
        header_schema,
        content_schema,
    )
    for public, source in zip(
        new_atoms, delta.new_atoms.values(), strict=True
    ):
        key = (public["relative_path"], public["filename"])
        atoms[key] = public
        atom_sources[key] = source
    scopes = dict(previous.scopes)
    for name in delta.old_scopes:
        scopes.pop(name, None)
    scopes.update({row["name"]: row for row in new_scopes})
    return ProjectionSnapshot(
        atoms,
        scopes,
        previous.graph,
        header_schema,
        content_schema,
        atom_sources,
    )
