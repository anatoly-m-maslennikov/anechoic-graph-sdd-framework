"""Create native Task and Epic Draft carriers."""

from datetime import datetime, timezone

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    canonical_native_header,
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_ticket_label,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native,
)

from .. import common
from ..effects import _project_write_lock
from .native_draft_guards import _check_owner, _native_slug
from .sources.native_draft_source__shared import _task_path
from ..sources.source__shared import bind_query_reader


def _create_task(
    selection,
    values,
    current_rows,
    structure_snapshot,
    ticket_labels,
    previous_capture=None,
    indexed_task=None,
):
    body, body_bytes = _task_body(values)
    if (
        not selection.root.is_absolute()
        or not selection.control_root.is_relative_to(selection.root)
        or selection.manifest_path.parent
        not in {selection.root, selection.control_root}
    ):
        raise common.SourceChanged("Selected Project path is invalid.")
    with _project_write_lock(selection.root):
        try:
            prepared = _prepare_task(
                selection,
                values,
                current_rows,
                structure_snapshot,
                ticket_labels,
                previous_capture,
                indexed_task,
                body,
                body_bytes,
            )
        except common.InputError, common.SourceChanged:
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged(
                "Native Project source is unavailable or changed."
            ) from error
        return _publish_task(selection, *prepared)


def _task_body(values):
    if (
        not isinstance(values, dict)
        or set(values) - {"label"} != {"template", "container", "body"}
        or values["template"] not in ("task", "epic")
        or not isinstance(values["body"], str)
    ):
        raise common.InputError(
            "newAtom",
            (
                "Supply the Task template, container, Markdown body, and "
                "optional Label."
            ),
        )
    if "label" in values and not isinstance(values["label"], str):
        raise common.InputError("label", "Supply a text navigation Label.")
    body = values["body"]
    try:
        _native_slug(body)
        body_bytes = body.encode("utf-8")
    except (ValueError, UnicodeError) as error:
        if isinstance(error, common.InputError):
            raise
        raise common.InputError(
            "summary", "Summary cannot be used in a Task filename."
        ) from error
    return body, body_bytes


def _prepare_task(
    selection,
    values,
    current_rows,
    structure_snapshot,
    ticket_labels,
    previous_capture,
    indexed_task,
    body,
    body_bytes,
):
    capture, number = _task_allocation(
        selection, previous_capture, indexed_task
    )
    owner, label = _task_owner_and_label(
        selection,
        values,
        current_rows,
        structure_snapshot,
        ticket_labels,
        capture,
    )
    atom_id = f"{selection.project_prefix}-T-{number}"
    ref = f"{atom_id}@1-draft"
    header = _task_header(atom_id, values["container"], label)
    path = _task_path(selection, header, body, "draft", 1, owner)
    raw = (
        b"---\n"
        + yaml.safe_dump(header, sort_keys=False).encode()
        + b"---\n"
        + body_bytes
    )
    return path, raw, atom_id, ref, header


def _publish_task(selection, path, raw, atom_id, ref, header):
    with bind_query_reader(None):
        outcome = common.write_destination(selection.root, path, raw)
    data = (
        {}
        if outcome.errors
        else {
            "savedDraft": common.saved(
                selection, path, atom_id, ref, 1, "Draft"
            )
        }
    )
    if data:
        data["savedDraft"]["updated_at"] = header["state"]["updated_at"]
    return common.result(
        effects=outcome.effects, errors=outcome.errors, **data
    )


def _task_allocation(selection, previous_capture, indexed_task):
    if indexed_task is not None:
        return None, int(indexed_task["max_number"]) + 1
    capture = revalidate_native(selection, previous_capture)
    if capture.errors:
        raise common.SourceChanged("Native carrier capture is incomplete.")
    return capture, common.next_native_number(selection, capture, "T")


def _task_owner_and_label(
    selection, values, current_rows, structure_snapshot, ticket_labels, capture
):
    _check_task_container(values["container"], structure_snapshot)
    owner = _check_owner(
        selection, values["container"], current_rows, capture, allow_draft=True
    )
    owner_directory, owner_template = owner
    owner_label = _owner_label(selection, owner_directory, capture)
    try:
        label = native_ticket_label(
            values["template"],
            owner_template,
            owner_label,
            label=values.get("label"),
        )
    except ValueError as error:
        raise common.InputError(
            "label", "Supply a filename-safe navigation Label."
        ) from error
    if ticket_labels:
        label = next(
            (
                value
                for value in ticket_labels
                if value.casefold() == label.casefold()
            ),
            None,
        )
        if label is None:
            raise common.InputError(
                "label",
                "Supply a declared navigation Label.",
                allowed_values=ticket_labels,
            )
    return owner, label


def _owner_label(selection, owner_directory, capture):
    if owner_directory is None:
        return None
    owner_path = (
        owner_directory.with_name(owner_directory.name + ".md")
        .relative_to(selection.root)
        .as_posix()
    )
    owner_row = next(
        row for row in capture.atoms if row.get("source_path") == owner_path
    )
    return native_header_view(owner_row["header_json"])["context"].get("label")


def _task_header(atom_id, container, label):
    context = {
        "container": container,
        "priority": 2,
        "template": "task",
        "label": label,
    }
    return canonical_native_header(
        {
            "identity": {"atom_id": atom_id},
            "context": context,
            "state": {
                "status": "draft",
                "version": 1,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        }
    )


def _check_task_container(container, structure_snapshot):
    if isinstance(container, dict) and set(container) == {"component"}:
        component = container["component"]
        if component != "C00" and (
            not isinstance(component, str)
            or structure_snapshot is None
            or component not in structure_snapshot.components
        ):
            raise common.InputError(
                "container", "Supply a Component in this Project."
            )
    elif not isinstance(container, dict) or set(container) != {"atom"}:
        raise common.InputError(
            "container",
            "Supply a Project Component or a Current Task or Epic.",
        )
