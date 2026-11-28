"""Run native Atom Lifecycle actions against an admitted Project capture."""

from types import SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    native_workflow_definition import (
    NativeWorkflowDefinitionError,
    STATUS_SPECIFICATIONS,
)


LIFECYCLE_TOOLS = frozenset(
    {
        "atom_lifecycle_direct_update",
        "atom_lifecycle_create_draft",
        "atom_lifecycle_change_status",
        "atom_lifecycle_archive",
        "atom_lifecycle_promote_draft",
        "atom_lifecycle_update",
        "atom_lifecycle_create_asset",
    }
)


def _lifecycle_target(name, arguments):
    from ..ATOM_LIFECYCLE__shared import InputError

    field = (
        "sourceCurrent"
        if name == "atom_lifecycle_create_draft"
        or name == "atom_lifecycle_update"
        and "sourceCurrent" in arguments
        else "target"
    )
    if name == "atom_lifecycle_update" and (
        ("sourceCurrent" in arguments) == ("target" in arguments)
    ):
        raise InputError(
            "target", "Supply exactly one Draft target or Current source."
        )
    target = arguments.get(field)
    ref = target.get("ref_id") if isinstance(target, dict) else None
    if isinstance(ref, str) and any(
        native.partition("@")[0] == ref.partition("@")[0]
        for native, _ in STATUS_SPECIFICATIONS.values()
    ):
        raise InputError(
            field,
            (
                "Installed status definitions can change only with their "
                "runtime binding."
            ),
        )
    return field, ref


def _dispatch_lifecycle(
    selection,
    name,
    arguments,
    rows,
    structure_snapshot,
    *,
    previous_capture,
    ticket_labels,
    validate_project_spec,
    indexed_task=None,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_asset import (
        create_asset,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
        direct_update,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.revision.native_draft_update import (
        update_draft,
    )

    if name == "atom_lifecycle_create_asset":
        return _invoke_simple(
            create_asset, selection, arguments, rows, previous_capture
        )
    field, ref = _lifecycle_target(name, arguments)
    if name == "atom_lifecycle_update" and field == "target":
        action = update_draft
    elif name == "atom_lifecycle_direct_update":
        action = direct_update
    else:
        return _dispatch_remaining(
            selection,
            name,
            arguments,
            rows,
            structure_snapshot,
            field,
            ref,
            previous_capture,
            ticket_labels,
            validate_project_spec,
            indexed_task,
        )
    return _invoke_simple(action, selection, arguments, rows, previous_capture)


def _invoke_simple(action, selection, arguments, rows, previous_capture):
    return action(
        selection,
        arguments,
        current_rows=rows,
        previous_capture=previous_capture,
    )


def _dispatch_remaining(
    selection,
    name,
    arguments,
    rows,
    structure_snapshot,
    field,
    ref,
    previous_capture,
    ticket_labels,
    validate_project_spec,
    indexed_task,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
        create_draft,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
        promote_draft,
    )

    if field == "sourceCurrent":
        return create_draft(
            selection,
            arguments,
            current_rows=rows,
            structure_snapshot=structure_snapshot,
            ticket_labels=ticket_labels,
            validate_project_spec_model=validate_project_spec,
            previous_capture=previous_capture,
            indexed_task=indexed_task,
        )
    if name == "atom_lifecycle_promote_draft":
        return promote_draft(
            selection,
            arguments,
            current_rows=rows,
            structure_snapshot=structure_snapshot,
            previous_capture=previous_capture,
            validate_project_spec_model=validate_project_spec,
        )
    return _dispatch_status(
        (selection, name, arguments, rows, structure_snapshot, ref),
        validate_project_spec,
        previous_capture,
    )


def _dispatch_status(
    target,
    validate_project_spec,
    previous_capture,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
        archive_ticket,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
        change_ticket_status,
    )
    from .native_workflow_definition import bind_status_specifications

    selection, name, arguments, rows, structure_snapshot, ref = target
    if isinstance(ref, str) and ref.startswith(
        f"{selection.project_prefix}-S-"
    ):
        return _change_spec_lifecycle(
            selection,
            name,
            arguments,
            rows,
            structure_snapshot,
            ref,
            validate_project_spec,
            previous_capture,
        )
    if name == "atom_lifecycle_archive":
        return archive_ticket(
            selection,
            arguments,
            current_rows=rows,
            previous_capture=previous_capture,
        )
    definition = bind_status_specifications(selection, current_rows=rows)
    return change_ticket_status(
        selection,
        arguments,
        current_rows=rows,
        check_definition=definition,
        previous_capture=previous_capture,
    )


def _change_spec_lifecycle(
    selection,
    name,
    arguments,
    rows,
    structure_snapshot,
    ref,
    validate_project_spec,
    previous_capture,
):
    from ..ATOM_LIFECYCLE__shared import (
        InputError,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
        archive_spec_draft,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared import (
        change_spec_status,
    )

    if name == "atom_lifecycle_archive":
        if ref.endswith("-draft"):
            return archive_spec_draft(
                selection,
                arguments,
                current_rows=rows,
                structure_snapshot=structure_snapshot,
                previous_capture=previous_capture,
            )
        if set(arguments) != {"target"}:
            raise InputError("target", "Supply one Current SPEC target.")
        arguments = arguments | {"targetStatus": "archived"}
    return change_spec_status(
        selection,
        arguments,
        current_rows=rows,
        structure_snapshot=structure_snapshot,
        validate_project_spec_model=validate_project_spec,
        previous_capture=previous_capture,
    )


def _lifecycle_snapshot(
    selection, read_structure, indexed_task, admitted_structure
):
    from ..ATOM_LIFECYCLE__shared import SourceChanged

    snapshot_path = getattr(selection, "structure_snapshot", None)
    try:
        if admitted_structure is not None:
            snapshot = admitted_structure
        elif indexed_task is not None:
            snapshot = SimpleNamespace(
                components=indexed_task["component_ids"]
            )
        else:
            snapshot = (
                read_structure(snapshot_path)
                if snapshot_path is not None
                else None
            )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise SourceChanged(
            "Structure snapshot is unavailable or invalid."
        ) from error
    return snapshot


def execute_native_lifecycle(
    selection,
    name,
    arguments,
    capture,
    read_structure,
    *,
    previous_capture,
    ticket_labels,
    validate_project_spec,
    indexed_task=None,
    admitted_structure=None,
):
    "Return the native outcome and any file effects for the caller to project."
    from ..ATOM_LIFECYCLE__shared import (
        InputError,
        SourceChanged,
        result,
    )

    if name not in LIFECYCLE_TOOLS:
        raise ValueError("The native Atom Lifecycle Tool is unavailable")
    try:
        snapshot = _lifecycle_snapshot(
            selection, read_structure, indexed_task, admitted_structure
        )
        return _dispatch_lifecycle(
            selection,
            name,
            arguments,
            capture.atoms if capture is not None else [],
            snapshot,
            previous_capture=previous_capture,
            ticket_labels=ticket_labels,
            validate_project_spec=validate_project_spec,
            indexed_task=indexed_task,
        )
    except (InputError, SourceChanged, NativeWorkflowDefinitionError) as error:
        return _lifecycle_error(error, result, InputError, SourceChanged)


def _lifecycle_error(error, result, input_error, source_changed):
    if isinstance(error, input_error):
        return result(
            outcome="needs_input", requested_input=error.requested_input
        )
    if isinstance(error, source_changed):
        return result(
            errors=[{"code": "source_changed", "message": str(error)}]
        )
    return result(
        outcome="blocked",
        errors=[
            {
                "code": "definition_revalidation_required",
                "message": str(error),
            }
        ],
    )
