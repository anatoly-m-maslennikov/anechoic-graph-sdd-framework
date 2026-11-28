"""Select the native Draft publication path."""


def promote_draft(
    selection,
    params,
    *,
    current_rows,
    structure_snapshot=None,
    previous_capture=None,
    validate_project_spec_model=None,
):
    """Publish a native Draft."""
    from . import native_draft_promotion__shared as p

    target, status, match = p._promotion_input(selection, params)
    atom_id, version = match[1], target["version"]
    draft, previous = _select_draft(target, status, atom_id, current_rows)
    if previous is None:
        return _publish_initial(
            selection,
            target,
            status,
            draft,
            current_rows,
            structure_snapshot,
            previous_capture,
            validate_project_spec_model,
            atom_id,
            version,
        )
    return _publish_revision(
        selection,
        target,
        status,
        draft,
        previous,
        current_rows,
        structure_snapshot,
        previous_capture,
        validate_project_spec_model,
        version,
    )


def _select_draft(target, status, atom_id, current_rows):
    from . import native_draft_promotion__shared as p

    chosen = [
        row
        for row in current_rows
        if row.get("_exact_ref") == target["ref_id"]
        and row.get("status_group") == "Draft"
    ]
    predecessors = [
        row
        for row in current_rows
        if row.get("id") == atom_id and row.get("status_group") == "Current"
    ]
    if len(chosen) != 1 or len(predecessors) > 1:
        raise p.common.SourceChanged(
            "Draft or Current predecessor is missing or ambiguous."
        )
    p._reject_component_contract(
        p.native_header_view(chosen[0]["header_json"])["context"].get(
            "template"
        ),
        "target",
    )
    if (
        "-T-" in atom_id
        and status != "backlog"
        and "atom_family" in chosen[0]["header_json"]
    ):
        raise p.common.InputError(
            "targetStatus",
            "A native Ticket Draft must be published to Backlog.",
        )
    return chosen[0], predecessors[0] if predecessors else None


def _publish_initial(
    selection,
    target,
    status,
    draft,
    current_rows,
    structure_snapshot,
    previous_capture,
    validate_project_spec_model,
    atom_id,
    version,
):
    from . import native_draft_promotion__shared as p

    if version == 1 and p._is_custom_replacement(draft["header_json"]):
        return p._publish_custom_replacement(
            selection, draft, current_rows, previous_capture
        )
    if "-S-" in atom_id:
        return p._publish_first_spec(
            selection,
            draft,
            current_rows,
            structure_snapshot,
            previous_capture,
            validate_project_spec_model,
        )
    if version == 1 and "-T-" in atom_id:
        return p._promote_new(
            selection, target, status, draft, current_rows, previous_capture
        )
    raise p.common.SourceChanged("Current predecessor is missing.")


def _publish_revision(
    selection,
    target,
    status,
    draft,
    previous,
    current_rows,
    structure_snapshot,
    previous_capture,
    validate_project_spec_model,
    version,
):
    from . import native_draft_promotion__shared as p

    if previous.get("version") == version:
        return p._cleanup_published_draft(
            selection,
            target,
            status,
            draft,
            previous,
            structure_snapshot,
            current_rows,
            previous_capture,
        )
    if (
        type(previous.get("version")) is not int
        or previous["version"] >= version
    ):
        raise p.common.InputError(
            "target",
            "Draft Version must be newer than its Current predecessor.",
        )
    return p._promote_revision(
        selection,
        target,
        status,
        draft,
        previous,
        current_rows,
        structure_snapshot,
        previous_capture,
        validate_project_spec_model,
    )
