"""Apply the first publication of native Drafts."""


def _promote_new(
    selection, target, status, draft, current_rows, previous_capture
):
    from . import native_draft_promotion__shared as p

    atom_id = target["ref_id"].split("@")[0]
    path, root, digest = _new_location(selection, target, draft)
    with p._project_write_lock(selection.root):
        capture, destination, promoted = p._preflight_new(
            selection,
            target,
            status,
            draft,
            current_rows,
            previous_capture,
            path,
            root,
            digest,
            atom_id,
        )
        if status in ("active", "in_queue", "backlog"):
            from ...updates.replacement.native_update_promotion import promote_ticket_tree

            return promote_ticket_tree(
                selection,
                draft,
                destination,
                status,
                current_rows,
                capture,
                lambda: None,
            )
        return _write_new(
            selection,
            draft,
            current_rows,
            capture,
            path,
            digest,
            destination,
            promoted,
            atom_id,
            status,
        )


def _new_location(selection, target, draft):
    from . import native_draft_promotion__shared as p

    relative, digest = draft.get("source_path"), draft.get("_source_sha256")
    if (
        not isinstance(relative, str)
        or not isinstance(digest, str)
        or not p.re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise p.common.SourceChanged(
            "Draft capture lacks a valid path or digest."
        )
    relative = p.Path(relative)
    path = selection.root / relative
    root = (
        next(
            (
                selection.control_root / name
                for name in (p.TICKET_DIRECTORY, "001_TICKETS", "__TKT")
                if path.is_relative_to(selection.control_root / name)
            ),
            selection.control_root / p.TICKET_DIRECTORY,
        )
        / "TASKS"
    )
    if (
        not selection.root.is_absolute()
        or not selection.control_root.is_relative_to(selection.root)
        or selection.manifest_path.parent
        not in {selection.root, selection.control_root}
        or relative.is_absolute()
        or ".." in relative.parts
        or not path.is_relative_to(root)
        or path.parent.name not in {p.DRAFT_DIRECTORY, "000_draft"}
        or not p.re.fullmatch(
            p.re.escape(target["ref_id"]) + r"-.+--.+\.md", path.name
        )
    ):
        raise p.common.SourceChanged("Task Draft path is invalid.")
    root = (
        root
        if path.parent in {root / p.DRAFT_DIRECTORY, root / "000_draft"}
        else None
    )
    return path, root, digest


def _write_new(
    selection,
    draft,
    current_rows,
    capture,
    path,
    digest,
    destination,
    promoted,
    atom_id,
    status,
):
    from . import native_draft_promotion__shared as p

    plans = p._plan_replacements(selection, draft, current_rows, None, capture)
    if path.with_suffix("").exists() or path.with_suffix("").is_symlink():
        raise p.common.InputError(
            "targetStatus",
            "Draft trees can only be published to Backlog or In Queue.",
        )
    archived = p._archive_replacements(selection, plans, draft)
    if archived["outcome"] != "completed":
        return archived
    with p.bind_query_reader(None):
        written = p.common.write_destination(
            selection.root, destination, promoted
        )
        recorded = archived["effects"] + list(written.effects)
        if written.errors:
            return p.common.result(effects=recorded, errors=written.errors)
        removed = p.effects.remove(selection.root, path, digest)
        recorded.extend(removed.effects)
    data = (
        {}
        if removed.errors
        else {
            "artifact": p.common.saved(
                selection, destination, atom_id, atom_id, 1, status
            )
        }
    )
    return p.common.result(effects=recorded, errors=removed.errors, **data)


def _publish_first_spec(
    selection,
    draft,
    current_rows,
    structure_snapshot,
    previous_capture,
    validate_project_spec_model,
):
    from . import native_draft_promotion__shared as p
    from ..native_draft__shared import _first_spec_write_lock

    atom_id, ref_id = draft["id"], draft["_exact_ref"]
    path, digest = _spec_location(selection, draft, ref_id)
    with _first_spec_write_lock(selection.root):
        destination, promoted, version, capture = p._preflight_first_spec(
            selection,
            draft,
            structure_snapshot,
            previous_capture,
            validate_project_spec_model,
            atom_id,
            ref_id,
            path,
            digest,
        )
        plans = p._plan_replacements(
            selection, draft, current_rows, structure_snapshot, capture
        )
        archived = p._archive_replacements(selection, plans, draft)
        if archived["outcome"] != "completed":
            return archived
        return _write_spec(
            selection,
            path,
            digest,
            destination,
            promoted,
            version,
            atom_id,
            archived,
        )


def _spec_location(selection, draft, ref_id):
    from . import native_draft_promotion__shared as p

    relative, digest = draft.get("source_path"), draft.get("_source_sha256")
    if (
        not isinstance(relative, str)
        or not isinstance(digest, str)
        or not p.re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise p.common.SourceChanged(
            "Draft capture lacks a valid path or digest."
        )
    relative = p.Path(relative)
    path = selection.root / relative
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not path.is_relative_to(selection.control_root)
        or path.parent.name not in {p.DRAFT_DIRECTORY, "000_draft"}
        or not p.re.fullmatch(p.re.escape(ref_id) + r"-.+\.md", path.name)
    ):
        raise p.common.InputError(
            "target", "Select a Spec in its native Draft directory."
        )
    return path, digest


def _write_spec(
    selection, path, digest, destination, promoted, version, atom_id, archived
):
    from . import native_draft_promotion__shared as p

    with p.bind_query_reader(None):
        written = p.common.write_destination(
            selection.root, destination, promoted
        )
        recorded = archived["effects"] + list(written.effects)
        errors = list(written.errors)
        if not errors:
            removed = p.effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
            errors.extend(removed.errors)
    data = (
        {}
        if errors
        else {
            "artifact": p.common.saved(
                selection, destination, atom_id, atom_id, version, "ready"
            )
        }
    )
    return p.common.result(effects=recorded, errors=errors, **data)
