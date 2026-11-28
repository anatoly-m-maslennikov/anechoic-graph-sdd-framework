"""Find affected projection row keys and references."""

from ...index_delta import MaterializationDelta
from .public_rows import atom_key


def _delta_keys(
    delta: MaterializationDelta,
) -> tuple[set[tuple[str, str]], set[str]]:
    return (
        {
            atom_key(row)
            for row in [*delta.old_atoms.values(), *delta.new_atoms.values()]
        },
        set(delta.old_scopes) | set(delta.new_scopes),
    )


def _changed_reference(previous, current, changed_atoms):
    references = {
        row["reference"]
        for key in changed_atoms
        for row in (previous.atoms.get(key), current.atoms.get(key))
        if row is not None and isinstance(row.get("reference"), str)
    }
    return next(iter(references)) if len(references) == 1 else None
