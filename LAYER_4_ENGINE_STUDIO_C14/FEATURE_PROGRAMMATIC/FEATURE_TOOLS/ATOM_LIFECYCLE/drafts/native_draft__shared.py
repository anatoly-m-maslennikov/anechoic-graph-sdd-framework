"""Create and promote bounded same-ID native Draft revisions."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from hashlib import sha256
import re as re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    DRAFT_DIRECTORY as DRAFT_DIRECTORY,
    native_header_view,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)

from .. import common
from .sources.native_draft_creation_details import (
    _revision_input,
    _write_revision,
    _create_new_draft,
)
from .native_draft_guards import (
    _check_owner,
    _reject_component_contract,
    _summary,
)
from .sources.native_draft_source__shared import (
    _revision_root,
    _state_bytes as _state_bytes,
    _task_path as _task_path,
)
from .native_draft_task import _create_task as _create_task
from .promotion.native_draft_promotion__shared import promote_draft as promote_draft
from ..effects import _project_write_lock
from .sources.native_project_spec import (
    PROJECT_SPEC_TEMPLATES,
    create_project_spec as create_project_spec,
    project_spec_template,
    validate_project_spec,
)
from ..sources.source__shared import bind_query_reader as bind_query_reader


@contextmanager
def _first_spec_write_lock(root):
    with ExitStack() as stack:
        try:
            stack.enter_context(_project_write_lock(root))
        except BlockingIOError as error:
            raise common.SourceChanged(
                "A native Atom write is in progress."
            ) from error
        yield


def _validate_project_template(header, validate, body=None):
    template = native_header_view(header)["context"].get("template")
    _reject_component_contract(template, "target")
    if isinstance(template, str) and (
        template in PROJECT_SPEC_TEMPLATES
        or (
            validate is not None
            and project_spec_template(template, validate) is not None
        )
    ):
        if validate is None:
            raise common.InputError(
                "target",
                (
                    "The compiled Model does not admit this Project SPEC "
                    "Template."
                ),
            )
        validate_project_spec(header, validate, body)


def create_draft(
    selection,
    params,
    *,
    current_rows,
    structure_snapshot=None,
    ticket_labels=(),
    validate_project_spec_model=None,
    previous_capture=None,
    indexed_task=None,
):
    if indexed_task is not None and (
        not isinstance(params, dict)
        or set(params) != {"newAtom"}
        or not isinstance(params["newAtom"], dict)
        or params["newAtom"].get("template") not in ("task", "epic")
        or not isinstance(params["newAtom"].get("container"), dict)
        or set(params["newAtom"]["container"]) != {"component"}
    ):
        raise common.InputError(
            "newAtom", "Indexed creation requires a Component Task or Epic."
        )
    if isinstance(params, dict) and "newAtom" in params:
        return _create_new_draft(
            selection,
            params,
            current_rows,
            structure_snapshot,
            ticket_labels,
            validate_project_spec_model,
            previous_capture,
            indexed_task,
        )
    return _create_revision(
        selection, params, current_rows, structure_snapshot, previous_capture
    )


def _create_revision(
    selection, params, current_rows, structure_snapshot, previous_capture
):
    target, changes, selected, digest, relative = _revision_input(
        selection, params, current_rows
    )
    _reject_component_contract(
        native_header_view(selected["header_json"])["context"].get("template"),
        "sourceCurrent",
    )
    path = selection.root / relative
    root = _revision_root(
        selection, selected, structure_snapshot, current_rows
    )
    with _project_write_lock(selection.root):
        capture, raw, bounds, old_body, owner = _read_revision(
            selection,
            target,
            selected,
            digest,
            path,
            current_rows,
            previous_capture,
        )
        body = changes.get("body", old_body)
        if _summary(body) != _summary(old_body):
            raise common.InputError(
                "summary", "Changing a Summary is not supported."
            )
        return _write_revision(
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
        )


def _read_revision(
    selection, target, selected, digest, path, current_rows, previous_capture
):
    owner = None
    try:
        capture = revalidate_native(selection, previous_capture)
        _check_revision_capture(capture, target, selected)
        raw = ReadContext(
            roots=[str(selection.root)], limits=dict(CEILINGS)
        ).read(path)
        bounds = frontmatter_bounds(raw)
        if (
            bounds is None
            or sha256(raw).hexdigest() != digest
            or raw[bounds[2] :] != selected.get("_content_bytes")
            or parse_carrier(raw, path).metadata != selected.get("header_json")
        ):
            raise common.SourceChanged(
                "Current carrier source changed after selection."
            )
        old_body = raw[bounds[2] :].decode("utf-8")
        if "-T-" in target["ref_id"]:
            owner = _check_owner(
                selection,
                native_header_view(selected["header_json"])["context"].get(
                    "container"
                ),
                current_rows,
                capture,
            )
    except common.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged(
            "Native source is unavailable or changed."
        ) from error
    return capture, raw, bounds, old_body, owner


def _check_revision_capture(capture, target, selected):
    fresh = [
        row
        for row in capture.atoms
        if row.get("id") == target["ref_id"]
        and row.get("status_group") == "Current"
    ]
    if (
        capture.errors
        or len(fresh) != 1
        or any(
            fresh[0].get(key) != selected.get(key)
            for key in (
                "source_path",
                "id",
                "ref",
                "_exact_ref",
                "version",
                "status",
                "status_group",
                "header_json",
                "_content_bytes",
                "_source_sha256",
            )
        )
    ):
        raise common.SourceChanged(
            "Current carrier source changed after selection."
        )


def _revalidate_revision_collision(selection, path, digest, previous_capture):
    try:
        fresh_raw = ReadContext(
            roots=[str(selection.root)], limits=dict(CEILINGS)
        ).read(path)
        if sha256(fresh_raw).hexdigest() != digest:
            raise common.SourceChanged(
                "Current carrier source changed after selection."
            )
        refreshed = revalidate_native(selection, previous_capture)
        if refreshed.errors:
            raise common.SourceChanged("Native carrier capture is incomplete.")
        reader = ReadContext(
            roots=[str(selection.root)], limits=dict(CEILINGS)
        )
        if (
            sha256(reader.read(selection.manifest_path)).hexdigest()
            != selection.manifest_sha256
            or reader.currentness()["state"] != "unchanged"
        ):
            raise common.SourceChanged(
                "Project Manifest changed after selection."
            )
    except (OSError, RuntimeError, ValueError) as error:
        raise common.SourceChanged(
            "Current carrier source changed after selection."
        ) from error
