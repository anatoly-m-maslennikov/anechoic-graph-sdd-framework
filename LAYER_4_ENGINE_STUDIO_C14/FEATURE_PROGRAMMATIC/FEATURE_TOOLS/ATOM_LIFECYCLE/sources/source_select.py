"""Read and validate native source selection evidence."""

from __future__ import annotations

from . import source__shared as owner


def select_source(
    selection: owner.ProjectSelection,
    ref_id: str,
    *,
    expected_version: int | None = None,
) -> owner.SourcePin:
    """Bind one logical ID in the retained Project tree without mutation.

    An unqualified ID selects Current. A qualified ID selects Archived or Draft
    with the ``-draft`` suffix. An optional expected version pins any read.
    """
    atom_id, qualified, draft = owner._selector(
        selection, ref_id, expected_version
    )
    reader = owner.ReadContext(
        roots=[str(selection.root)], limits=dict(owner.CEILINGS)
    )
    try:
        if owner.query_reader() is None:
            selection._revalidate_boundary(reader=reader)
        candidates = owner._candidate_paths(
            reader, selection, atom_id, references=(ref_id,)
        )
        selected = owner._unique_candidate(
            reader,
            candidates,
            ref_id,
            atom_id,
            qualified,
            draft,
            retained_history=bool(qualified and not draft),
        )
        if (
            expected_version is not None
            and selected.version != expected_version
        ):
            raise owner.SourceSelectionError("Expected Version is stale")
        owner._check_currentness(reader, selection, atom_id, candidates)
        return selected
    except owner.SourceSelectionError:
        raise
    except (OSError, RuntimeError, KeyError, TypeError, ValueError) as error:
        raise owner.SourceSelectionError(
            "Project source selection is unavailable or unsafe"
        ) from error


def select_current_sources(
    selection: owner.ProjectSelection, ref_ids: list[str]
) -> dict[str, owner.SourcePin]:
    """Bind Current sources together with one shared inventory and recheck."""
    selectors = [
        owner._selector(selection, ref_id, None) for ref_id in ref_ids
    ]
    if any(qualified is not None for _, qualified, _ in selectors):
        raise owner.SourceSelectionError(
            "Invalid Atom reference or expected Version"
        )
    return owner.select_sources(selection, ref_ids)


def _select_indexed(selection, ref_ids, selectors, ids, reader):
    if len(ids) == len(selectors):
        indexed = owner.query_candidates(
            selection,
            atom_ids=tuple(sorted(ids)),
            references=tuple(ref_ids),
        )
        return {
            ref_id: owner._unique_candidate(
                reader,
                indexed.get(atom_id, ()),
                ref_id,
                atom_id,
                qualified,
                draft,
                retained_history=bool(qualified and not draft),
            )
            for ref_id, atom_id, qualified, draft in selectors
        }
    return {
        ref_id: owner._unique_candidate(
            reader,
            owner.query_candidates(
                selection, atom_ids=(atom_id,), references=(ref_id,)
            ).get(atom_id, ()),
            ref_id,
            atom_id,
            qualified,
            draft,
            retained_history=bool(qualified and not draft),
        )
        for ref_id, atom_id, qualified, draft in selectors
    }


def _select_unindexed(selection, selectors, reader, classify):
    selection._revalidate_boundary(reader=reader)
    candidates = owner._inventory_paths(reader, selection, classify)
    selected = {
        ref_id: owner._unique_candidate(
            reader,
            candidates.get(atom_id, ()),
            ref_id,
            atom_id,
            qualified,
            draft,
            retained_history=bool(qualified and not draft),
        )
        for ref_id, atom_id, qualified, draft in selectors
    }
    if owner._inventory_paths(reader, selection, classify) != candidates:
        raise owner.SourceSelectionError(
            "Atom source candidates changed during selection"
        )
    if reader.currentness()["state"] != "unchanged":
        raise owner.SourceSelectionError(
            "Atom source changed during selection"
        )
    selection._revalidate_boundary(reader=reader)
    owner._check_declarations(reader, selection)
    return selected


def select_sources(
    selection: owner.ProjectSelection, ref_ids: list[str]
) -> dict[str, owner.SourcePin]:
    """Bind several exact revisions with one source inventory and recheck."""
    selectors = [
        (ref_id, *owner._selector(selection, ref_id, None))
        for ref_id in ref_ids
    ]
    ids = {atom_id for _, atom_id, _, _ in selectors}
    if not ids:
        return {}
    prefix = selection.settings["artifacts"]["identity"]["project_prefix"]
    marker = owner.re.compile(
        r"^(?:[1-9][0-9]*-)?("
        + owner.re.escape(prefix)
        + r"-[A-Z]-[0-9]+)(?=@|-|\.)"
    )

    def classify(name: str) -> str | None:
        match = marker.match(name)
        return match.group(1) if match and match.group(1) in ids else None

    reader = owner.ReadContext(
        roots=[str(selection.root)], limits=dict(owner.CEILINGS)
    )
    try:
        if owner.query_reader() is not None:
            return _select_indexed(selection, ref_ids, selectors, ids, reader)
        return _select_unindexed(selection, selectors, reader, classify)
    except owner.SourceSelectionError:
        raise
    except (OSError, RuntimeError, KeyError, TypeError, ValueError) as error:
        raise owner.SourceSelectionError(
            "Project source selection is unavailable or unsafe"
        ) from error
