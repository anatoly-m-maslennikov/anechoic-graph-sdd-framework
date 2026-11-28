"""Prepare and write same-ID Draft revisions."""


def _write_revision(
    selection,
    target,
    selected,
    path,
    root,
    raw,
    bounds,
    body,
    old_body,
    capture,
    previous_capture,
    digest,
    owner,
):
    version = _initial_revision(
        selection, target, selected, path, root, old_body, capture, owner
    )
    destination, candidate, outcome, version = _write_candidate_revision(
        selection,
        target,
        selected,
        path,
        root,
        raw,
        bounds,
        body,
        version,
        owner,
        digest,
        previous_capture,
    )
    return _revision_result(
        selection, target, destination, candidate, outcome, version
    )


def _revision_result(
    selection, target, destination, candidate, outcome, version
):
    from .. import native_draft__shared as draft

    data = (
        {}
        if outcome.errors
        else {
            "savedDraft": draft.common.saved(
                selection,
                destination,
                target["ref_id"],
                f"{target['ref_id']}@{version}-draft",
                version,
                "Draft",
            )
        }
    )
    if data:
        timestamp = (
            draft.parse_carrier(candidate, destination)
            .metadata.get("state", {})
            .get("updated_at")
        )
        if timestamp is not None:
            data["savedDraft"]["updated_at"] = str(timestamp)
    return draft.common.result(
        effects=outcome.effects, errors=outcome.errors, **data
    )


def _write_candidate_revision(
    selection,
    target,
    selected,
    path,
    root,
    raw,
    bounds,
    body,
    version,
    owner,
    digest,
    previous_capture,
):
    from .. import native_draft__shared as draft

    while version <= 2**63 - 1:
        destination = _draft_destination(
            selection, target, selected, path, root, body, version, owner
        )
        candidate = draft._state_bytes(
            raw, bounds, path, version, body, "draft", update_timestamp=True
        )
        with draft.bind_query_reader(None):
            outcome = draft.common.write_destination(
                selection.root, destination, candidate
            )
        if not draft.common.destination_collision(
            {"effects": outcome.effects, "errors": outcome.errors}
        ):
            break
        draft._revalidate_revision_collision(
            selection, path, digest, previous_capture
        )
        version += 1
    else:
        raise draft.common.SourceChanged(
            "No representable revision Version remains."
        )
    return destination, candidate, outcome, version


def _draft_destination(
    selection, target, selected, path, root, body, version, owner
):
    from .. import native_draft__shared as draft

    if "-T-" in target["ref_id"] and "atom_family" in selected["header_json"]:
        return draft._task_path(
            selection,
            selected["header_json"],
            body,
            "draft",
            version,
            owner,
            root,
        )
    else:
        return (
            root
            / draft.DRAFT_DIRECTORY
            / path.name.replace(
                target["ref_id"] + "-",
                f"{target['ref_id']}@{version}-draft-",
                1,
            )
        )


def _initial_revision(
    selection, target, selected, path, root, old_body, capture, owner
):
    from .. import native_draft__shared as draft

    version = (
        max(
            getattr(capture, "max_archived_version", 0),
            max(
                row["version"]
                for row in capture.atoms
                if row.get("id") == target["ref_id"]
            ),
        )
        + 1
    )
    if "-T-" in target["ref_id"] and "atom_family" in selected["header_json"]:
        if (
            draft._task_path(
                selection,
                selected["header_json"],
                old_body,
                selected["status"],
                target["version"],
                owner,
                root,
            )
            != path
        ):
            raise draft.common.InputError(
                "sourceCurrent",
                "Task path disagrees with its authored Header and Summary.",
            )
    return version


def _revision_input(selection, params, current_rows):
    from .. import native_draft__shared as draft

    if (
        not isinstance(params, dict)
        or set(params) - {"sourceCurrent", "changes"}
        or "sourceCurrent" not in params
    ):
        raise draft.common.InputError(
            "sourceCurrent",
            "Supply one Current carrier and optional body change.",
        )
    target, changes = _revision_parameters(selection, params)
    matches = [
        row
        for row in current_rows
        if row.get("id") == target["ref_id"]
        and row.get("status_group") == "Current"
    ]
    if len(matches) != 1 or matches[0].get("version") != target["version"]:
        raise draft.common.SourceChanged(
            "Current carrier selection is missing, ambiguous, or stale."
        )
    selected = matches[0]
    digest, relative = (
        selected.get("_source_sha256"),
        selected.get("source_path"),
    )
    if (
        not isinstance(digest, str)
        or not draft.re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(relative, str)
    ):
        raise draft.common.SourceChanged(
            "Current carrier capture lacks a valid path or source digest."
        )
    return target, changes, selected, digest, relative


def _revision_parameters(selection, params):
    from .. import native_draft__shared as draft

    target = params["sourceCurrent"]
    if (
        not isinstance(target, dict)
        or set(target) != {"ref_id", "version"}
        or not isinstance(target["ref_id"], str)
        or not draft.re.fullmatch(
            draft.re.escape(selection.project_prefix) + r"-[STPC]-[0-9]+",
            target["ref_id"],
        )
        or type(target["version"]) is not int
        or target["version"] < 1
    ):
        raise draft.common.InputError(
            "sourceCurrent",
            "Supply a Current carrier reference and positive Version.",
        )
    changes = params.get("changes", {})
    if (
        not isinstance(changes, dict)
        or set(changes) - {"body"}
        or ("body" in changes and not isinstance(changes["body"], str))
    ):
        raise draft.common.InputError(
            "changes", "Supply only a Markdown body change."
        )
    return target, changes


def _is_project_spec(template, values):
    from .. import native_draft__shared as draft

    return (
        isinstance(template, str)
        and template not in ("task", "epic")
        and (
            template in draft.PROJECT_SPEC_TEMPLATES
            or isinstance(values, dict)
            and "lens" in values
        )
    )


def _create_new_spec(
    selection, values, validate_project_spec_model, previous_capture
):
    from .. import native_draft__shared as draft

    if validate_project_spec_model is None:
        raise draft.common.InputError(
            "newAtom",
            "The compiled Model does not admit this Project SPEC Template.",
        )
    return draft.create_project_spec(
        selection,
        values,
        validate_project_spec_model,
        previous_capture,
    )


def _create_new_draft(
    selection,
    params,
    current_rows,
    structure_snapshot,
    ticket_labels,
    validate_project_spec_model,
    previous_capture,
    indexed_task,
):
    from .. import native_draft__shared as draft

    if set(params) != {"newAtom"}:
        raise draft.common.InputError(
            "newAtom", "Supply only new Task or Epic properties."
        )
    values = params["newAtom"]
    template = values.get("template") if isinstance(values, dict) else None
    draft._reject_component_contract(template, "newAtom")
    if _is_project_spec(template, values):
        return _create_new_spec(
            selection, values, validate_project_spec_model, previous_capture
        )
    return draft._create_task(
        selection,
        params["newAtom"],
        current_rows,
        structure_snapshot,
        ticket_labels,
        previous_capture,
        indexed_task,
    )
