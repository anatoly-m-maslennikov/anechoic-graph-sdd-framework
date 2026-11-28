"""Read and validate native source selection evidence."""

from __future__ import annotations

from typing import Any

from . import source__shared as owner


def _candidate_paths(
    reader: owner.ReadContext,
    selection: owner.ProjectSelection,
    atom_id: str,
    *,
    references: tuple[str, ...] = (),
) -> tuple[owner.Path, ...]:
    """Discover this identity in authoring roots without following links."""
    prefix = owner.re.compile(
        r"^(?:[1-9][0-9]*-)?" + owner.re.escape(atom_id) + r"(?=@|-|\.)"
    )
    if owner.query_reader() is not None:
        return tuple(
            path
            for path in owner.query_candidates(
                selection, atom_ids=(atom_id,), references=references
            ).get(atom_id, ())
            if prefix.match(path.name)
        )
    return owner._matching_paths(reader, selection, prefix)


def _matching_paths(
    reader: owner.ReadContext,
    selection: owner.ProjectSelection,
    prefix: owner.re.Pattern[str],
) -> tuple[owner.Path, ...]:
    return owner._inventory_paths(
        reader, selection, lambda name: True if prefix.match(name) else None
    ).get(True, ())


def _inventory_roots(selection):
    recursive = {
        selection.root / unit["authority_path"] / role
        for unit in selection.structure["scope_units"]
        for role in owner.active_placement().role_folders.values()
    }
    direct = {selection.control_root}
    pending = [(directory, True) for directory in recursive] + [
        (directory, False) for directory in direct
    ]
    return pending


def _inventory_paths(
    reader: owner.ReadContext, selection: owner.ProjectSelection, classify
) -> dict[Any, tuple[owner.Path, ...]]:
    pending = _inventory_roots(selection)
    found: dict[Any, set[owner.Path]] = {}
    while pending:
        directory, descend = pending.pop()
        reader.checkpoint()
        try:
            reader.allowed(directory)
            descriptor = owner.open_regular(directory, directory=True)
        except FileNotFoundError:
            continue
        try:
            with owner.os.scandir(descriptor) as entries:
                for entry in entries:
                    reader.checkpoint()
                    path = directory / entry.name
                    identity = classify(entry.name)
                    _inventory_entry(
                        entry, path, identity, descend, pending, found, reader
                    )
        finally:
            owner.os.close(descriptor)
    return {
        identity: tuple(sorted(paths)) for identity, paths in found.items()
    }


def _inventory_entry(entry, path, identity, descend, pending, found, reader):
    if entry.is_symlink():
        if identity is not None or descend:
            raise owner.SourceSelectionError(
                "Symlink in Atom source boundary"
            )
    elif descend and entry.is_dir(follow_symlinks=False):
        pending.append((path, True))
    elif entry.name.endswith(".md") and identity is not None:
        candidates = found.setdefault(identity, set())
        candidates.add(path)
        if len(candidates) > reader.limits["max_candidates"]:
            raise owner.SourceSelectionError(
                "Atom source candidate limit exceeded"
            )
