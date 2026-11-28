"""Read and validate native source selection evidence."""

from __future__ import annotations

from . import source__shared as owner


def _identity_prefix(selection):
    try:
        prefix = selection.settings["artifacts"]["identity"]["project_prefix"]
        if (
            not isinstance(prefix, str)
            or not prefix.strip()
            or prefix != prefix.upper()
        ):
            raise ValueError("Invalid Project identity prefix")
    except (KeyError, TypeError, ValueError) as error:
        raise owner.SourceSelectionError(
            "Selected Project identity prefix is unavailable or invalid"
        ) from error
    return prefix


def _selector(
    selection: owner.ProjectSelection,
    ref_id: str,
    expected_version: int | None,
) -> tuple[str, str | None, str | None]:
    if not isinstance(selection, owner.ProjectSelection) or not isinstance(
        ref_id, str
    ):
        raise owner.SourceSelectionError(
            "Invalid Project selection or Atom reference"
        )
    prefix = _identity_prefix(selection)
    match = owner.re.fullmatch(
        r"("
        + owner.re.escape(prefix)
        + r"-[A-Z]-[0-9]+)(?:@([1-9][0-9]*)(-draft)?)?",
        ref_id,
    )
    if not match or (
        expected_version is not None
        and (type(expected_version) is not int or expected_version < 1)
    ):
        raise owner.SourceSelectionError(
            "Invalid Atom reference or expected Version"
        )
    atom_id, qualified, draft = match.groups()
    if (
        qualified is not None
        and expected_version is not None
        and int(qualified) != expected_version
    ):
        raise owner.SourceSelectionError(
            "Expected Version contradicts Atom reference"
        )
    return atom_id, qualified, draft


def _carrier_revision(
    path: owner.Path, atom_id: str
) -> tuple[str | None, bool]:
    marker = owner.re.match(
        r"(?:[1-9][0-9]*-)?"
        + owner.re.escape(atom_id)
        + r"(?:@([1-9][0-9]*)(-draft)?)?(?=-|\.)",
        path.name,
    )
    if not marker:
        raise owner.SourceSelectionError(
            "Malformed candidate carrier identity"
        )
    candidate_version, candidate_draft = marker.groups()
    if not candidate_version:
        suffix = owner.re.search(r"@([1-9][0-9]*)\.md$", path.name)
        if suffix:
            candidate_version = suffix.group(1)
    return candidate_version, bool(candidate_draft)


def _matches_revision(
    path: owner.Path, atom_id: str, qualified: str | None, draft: str | None
) -> bool:
    return owner._carrier_revision(path, atom_id) == (qualified, bool(draft))


def _candidate_identity(
    view, ref_id, atom_id, qualified, draft, retained_history
):
    if "projection" in view:
        return None
    actual_version, status = view.get("version"), view.get("status")
    actual_id, actual_ref = view.get("atom_id"), view.get("ref_id")
    legacy_archive_id = (
        retained_history
        and qualified is not None
        and not draft
        and actual_id == actual_ref == ref_id
    )
    if (
        (actual_id != atom_id and not legacy_archive_id)
        or type(actual_version) is not int
        or actual_version < 1
        or not isinstance(status, str)
    ):
        raise owner.SourceSelectionError(
            "Candidate identity or Version is invalid"
        )
    status_key = status.casefold()
    if (
        (draft and status_key != "draft")
        or (qualified and not draft and status_key != "archived")
        or (not qualified and status_key in {"draft", "archived"})
    ):
        raise owner.SourceSelectionError(
            "Candidate Status contradicts reference"
        )
    if qualified is not None and actual_version != int(qualified):
        raise owner.SourceSelectionError(
            "Candidate Version contradicts reference"
        )
    if actual_ref is not None and actual_ref not in (
        ref_id,
        atom_id if draft else ref_id,
    ):
        raise owner.SourceSelectionError(
            "Candidate Ref ID contradicts reference"
        )
    return actual_version, status


def _read_candidate(
    reader: owner.ReadContext,
    path: owner.Path,
    ref_id: str,
    atom_id: str,
    qualified: str | None,
    draft: str | None,
    *,
    retained_history: bool = False,
) -> owner.SourcePin | None:
    source_reader = owner.query_reader()
    raw = (
        source_reader.lifecycle_read(path)
        if source_reader is not None
        else reader.read(path)
    )
    parsed = owner.parse_carrier(raw, path)
    view = owner.carrier_read_view(parsed.metadata)
    identity = _candidate_identity(
        view, ref_id, atom_id, qualified, draft, retained_history
    )
    if identity is None:
        return None
    actual_version, status = identity
    return owner.SourcePin(
        path,
        atom_id,
        ref_id,
        actual_version,
        status,
        owner.hashlib.sha256(raw).hexdigest(),
        raw,
        parsed.metadata,
    )


def _check_currentness(
    reader: owner.ReadContext,
    selection: owner.ProjectSelection,
    atom_id: str,
    candidates: tuple[owner.Path, ...],
) -> None:
    if owner.query_reader() is not None:
        return
    if owner._candidate_paths(reader, selection, atom_id) != candidates:
        raise owner.SourceSelectionError(
            "Atom source candidates changed during selection"
        )
    if reader.currentness()["state"] != "unchanged":
        raise owner.SourceSelectionError(
            "Atom source changed during selection"
        )
    selection._revalidate_boundary(reader=reader)
    owner._check_declarations(reader, selection)


def _check_declarations(reader, selection):
    source_reader = owner.query_reader()
    declarations = (
        source_reader.lifecycle_declarations()
        if source_reader is not None
        else owner.read_scope_unit_declarations(
            selection.root, selection.control_relative, reader=reader
        )
    )
    if declarations.digest != selection.declaration_digest:
        raise owner.SourceSelectionError(
            "Retained Project declarations changed"
        )


def _indexed_candidate(
    reader, paths, ref_id, atom_id, qualified, draft, retained_history
):
    matching = {
        path
        for path in paths
        if owner._matches_revision(path, atom_id, qualified, draft)
    }
    if len(matching) != 1:
        raise owner.SourceSelectionError("Atom source is missing or ambiguous")
    pin = owner._read_candidate(
        reader,
        next(iter(matching)),
        ref_id,
        atom_id,
        qualified,
        draft,
        retained_history=retained_history,
    )
    if pin is None:
        raise owner.SourceSelectionError(
            "Atom source has no valid matching carrier"
        )
    return pin


def _unique_candidate(
    reader, paths, ref_id, atom_id, qualified, draft, *, retained_history=False
):
    if owner.query_reader() is not None:
        return _indexed_candidate(
            reader, paths, ref_id, atom_id, qualified, draft, retained_history
        )
    found = [
        pin
        for path in paths
        if owner._matches_revision(path, atom_id, qualified, draft)
        if (
            pin := owner._read_candidate(
                reader,
                path,
                ref_id,
                atom_id,
                qualified,
                draft,
                retained_history=retained_history,
            )
        )
        is not None
    ]
    if len(found) != 1:
        raise owner.SourceSelectionError("Atom source is missing or ambiguous")
    return found[0]
