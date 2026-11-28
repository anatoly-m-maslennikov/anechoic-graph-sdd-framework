"""Preflight a native revision before writing any carriers."""

from . import native_draft_revision__shared as origin


def _preflight_revision(
    selection,
    status,
    draft,
    previous,
    current_rows,
    previous_capture,
    validate_project_spec_model,
    root,
    paths,
    archive_path,
    destination,
    atom_id,
    version,
):
    from ..native_draft__shared import _validate_project_template

    draft_path, previous_path = paths
    try:
        return _compute_preflight(
            (selection, status, draft, previous),
            (current_rows, previous_capture, validate_project_spec_model),
            (root, paths, archive_path, destination, atom_id, version),
            _validate_project_template,
        )
    except origin.common.InputError, origin.common.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise origin.common.SourceChanged(
            "Native sources are unavailable or changed."
        ) from error


def _compute_preflight(first, second, third, validate_project_template):
    selection, status, draft, previous = first
    current_rows, previous_capture, validate_project_spec_model = second
    root, paths, archive_path, destination, atom_id, version = third
    draft_path, previous_path = paths
    (
        capture,
        raw_draft,
        raw_previous,
        draft_bounds,
        previous_bounds,
        draft_body,
        previous_body,
    ) = origin._read_revision_sources(
        selection,
        draft,
        previous,
        previous_capture,
        paths,
        atom_id,
        version,
    )
    archive_path, destination, typed, headers = _revision_paths(
        first, second, third, capture, (draft_body, previous_body)
    )
    archive, promoted = _revision_bytes(
        first,
        second,
        (paths, archive_path, destination, atom_id, version),
        (
            capture,
            raw_draft,
            raw_previous,
            draft_bounds,
            previous_bounds,
            draft_body,
            previous_body,
            typed,
            headers,
        ),
        validate_project_template,
    )
    return archive_path, destination, archive, promoted, capture


def _revision_paths(first, second, third, capture, bodies):
    selection, status, draft, previous = first
    current_rows, previous_capture, validate_project_spec_model = second
    root, paths, archive_path, destination, atom_id, version = third
    draft_path, previous_path = paths
    draft_body, previous_body = bodies
    draft_header, previous_header = (
        draft["header_json"],
        previous["header_json"],
    )
    typed = origin.is_c9_typed_manifest(draft_header)
    if typed:
        _validate_typed_draft(
            selection, draft_path, draft_header, draft_body, root
        )
    if "-T-" in atom_id:
        owner = origin._check_owner(
            selection,
            origin.native_header_view(previous_header)["context"].get(
                "container"
            ),
            current_rows,
            capture,
        )
    if "-T-" in atom_id and "atom_family" in previous_header:
        archive_path, destination = _task_revision_paths(
            selection,
            status,
            draft,
            previous,
            owner,
            root,
            paths,
            (draft_body, previous_body),
            version,
        )
    return archive_path, destination, typed, (draft_header, previous_header)


def _revision_bytes(first, second, locations, data, validate_project_template):
    selection, status, draft, previous = first
    current_rows, previous_capture, validate_project_spec_model = second
    paths, archive_path, destination, atom_id, version = locations
    (
        capture,
        raw_draft,
        raw_previous,
        draft_bounds,
        previous_bounds,
        draft_body,
        previous_body,
        typed,
        headers,
    ) = data
    draft_path, previous_path = paths
    draft_header, previous_header = headers
    origin._check_revision_headers(
        draft_header, previous_header, draft_body, previous_body, typed
    )
    origin._check_promotion_destinations(
        archive_path, destination, previous_path, capture, previous["id"]
    )
    archive = origin._state_bytes(
        raw_previous,
        previous_bounds,
        previous_path,
        previous["version"],
        previous_body,
        "archived",
    )
    promoted = origin._state_bytes(
        raw_draft, draft_bounds, draft_path, version, draft_body, status
    )
    if "-S-" in atom_id:
        validate_project_template(
            origin.parse_carrier(promoted, destination).metadata,
            validate_project_spec_model,
            draft_body,
        )
    return archive, promoted


def _task_revision_paths(
    selection, status, draft, previous, owner, root, paths, bodies, version
):
    draft_path, previous_path = paths
    draft_body, previous_body = bodies
    draft_header, previous_header = (
        draft["header_json"],
        previous["header_json"],
    )
    _validate_task_paths(
        selection, draft, previous, owner, root, paths, bodies, version
    )
    archive_path = origin._task_path(
        selection,
        previous_header,
        previous_body,
        "archived",
        previous["version"],
        owner,
        root,
    )
    destination = origin._task_path(
        selection,
        draft_header,
        draft_body,
        status,
        version,
        owner,
        root,
    )
    return archive_path, destination


def _validate_task_paths(
    selection, draft, previous, owner, root, paths, bodies, version
):
    draft_path, previous_path = paths
    draft_body, previous_body = bodies
    draft_header, previous_header = (
        draft["header_json"],
        previous["header_json"],
    )
    if draft_path != origin._task_path(
        selection,
        draft_header,
        draft_body,
        "draft",
        version,
        owner,
        root,
    ) or previous_path != origin._task_path(
        selection,
        previous_header,
        previous_body,
        previous["status"],
        previous["version"],
        owner,
        root,
    ):
        raise origin.common.InputError(
            "target",
            "Task paths disagree with their authored Headers and Summaries.",
        )


def _validate_typed_draft(
    selection, draft_path, draft_header, draft_body, root
):
    origin._validate_c9_typed_manifest(draft_header, draft_body)
    parameters = getattr(selection, "parameters", None)
    if draft_path != origin.native_carrier_path(
        draft_header,
        origin._summary(draft_body),
        project_root=selection.control_root,
        owner_directory=root,
        parameters=parameters,
    ):
        raise origin.common.InputError(
            "target",
            "Draft path disagrees with its Header and Summary.",
        )
