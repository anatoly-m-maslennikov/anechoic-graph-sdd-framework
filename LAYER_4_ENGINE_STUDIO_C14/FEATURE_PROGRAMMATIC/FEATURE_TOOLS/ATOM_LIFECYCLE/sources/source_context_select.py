"""Read and validate native source selection evidence."""

from __future__ import annotations

from . import source__shared as owner


def _context_candidate(selection, ref_id, atom_id, row):
    if not isinstance(row, (list, tuple)) or len(row) != 3:
        raise owner.SourceSelectionError("Indexed Atom context is invalid")
    path, metadata, summary = row
    if (
        not isinstance(path, owner.Path)
        or not isinstance(metadata, dict)
        or not isinstance(summary, (str, type(None)))
    ):
        raise owner.SourceSelectionError("Indexed Atom context is invalid")
    if (
        not path.is_absolute()
        or ".." in path.parts
        or not path.is_relative_to(selection.control_root)
        or path.resolve(strict=False) != path
        or path.suffix != ".md"
    ):
        raise owner.SourceSelectionError(
            "Indexed Atom path is outside the selected Project"
        )
    if not owner._matches_revision(path, atom_id, None, None):
        return None
    view = owner.carrier_read_view(metadata)
    version, status = view.get("version"), view.get("status")
    if (
        "projection" in view
        or view.get("atom_id") != atom_id
        or view.get("ref_id") not in (None, atom_id)
        or type(version) is not int
        or version < 1
        or not isinstance(status, str)
        or not status.strip()
        or status.casefold() in {"draft", "archived"}
    ):
        return None
    return owner.SourceContext(
        path, atom_id, ref_id, version, status, metadata, summary
    )


def _unique_context(selection, ref_id, atom_id, rows):
    candidates = {}
    for row in rows:
        candidate = owner._context_candidate(selection, ref_id, atom_id, row)
        if candidate is not None:
            if (
                candidate.path in candidates
                and candidates[candidate.path] != candidate
            ):
                raise owner.SourceSelectionError(
                    "Atom source context is ambiguous"
                )
            candidates[candidate.path] = candidate
    if len(candidates) != 1:
        raise owner.SourceSelectionError(
            "Atom source context is missing or ambiguous"
        )
    candidate = next(iter(candidates.values()))
    return candidate


def select_context(
    selection: owner.ProjectSelection,
    ref_id: str,
    *,
    expected_version: int | None = None,
) -> owner.SourceContext:
    """Select Current Atom context from the Workbench index."""
    atom_id, qualified, _ = owner._selector(
        selection, ref_id, expected_version
    )
    reader = owner.query_reader()
    if reader is None or qualified is not None:
        raise owner.SourceSelectionError(
            "Current indexed Atom context is required"
        )
    try:
        rows = reader.lifecycle_contexts(selection, ref_id)
        if not isinstance(rows, (list, tuple)):
            raise owner.SourceSelectionError("Indexed Atom context is invalid")
        candidate = _unique_context(selection, ref_id, atom_id, rows)
        if (
            expected_version is not None
            and candidate.version != expected_version
        ):
            raise owner.SourceSelectionError("Expected Version is stale")
        return candidate
    except owner.SourceSelectionError:
        raise
    except (OSError, RuntimeError, KeyError, TypeError, ValueError) as error:
        raise owner.SourceSelectionError(
            "Project Atom context is unavailable or unsafe"
        ) from error
