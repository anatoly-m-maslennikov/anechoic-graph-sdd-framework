"""SPEC status and Draft archive operations."""

from __future__ import annotations

from hashlib import sha256
import sys
import re


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    DRAFT_DIRECTORY as DRAFT_DIRECTORY,
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

from ... import effects as effects
from ...effects import _project_write_lock
from ...common import InputError, SourceChanged, result as result, saved as saved
from ..replacement.native_replacement_promotion import _check_replacement_activation
from ..native_update_selection import _status_bytes
from ...sources.source__shared import bind_query_reader as bind_query_reader
from .native_spec_archive import (
    archive_spec_draft as archive_spec_draft,
    _archive_spec_selected as _archive_spec_selected,
)
from .native_spec_archive_publication import (
    _allocate_archived_spec as _allocate_archived_spec,
    _write_archived_spec as _write_archived_spec,
)


def change_spec_status(
    selection,
    params,
    *,
    current_rows,
    structure_snapshot=None,
    validate_project_spec_model=None,
    previous_capture=None,
):
    """Start implementation of a Ready SPEC or retire an Active SPEC."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.sources.native_draft_source__shared import (
        _revision_root,
    )

    from .native_spec_selection import select_spec_status

    target, status, selected = select_spec_status(
        sys.modules[__name__], selection, params, current_rows
    )
    root = _revision_root(
        selection, selected, structure_snapshot, current_rows
    )
    path = selection.root / selected["source_path"]
    digest = selected.get("_source_sha256")
    if not isinstance(digest, str) or not re.fullmatch(
        r"[0-9a-f]{64}", digest
    ):
        raise SourceChanged("Current SPEC capture lacks a source digest.")
    return _change_spec_selected(
        selection,
        target,
        selected,
        path,
        digest,
        root,
        status,
        validate_project_spec_model,
        previous_capture,
    )


def _selected_spec_bytes(selection, selected, path, digest):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    raw = reader.read(path)
    bounds = frontmatter_bounds(raw)
    if (
        bounds is None
        or sha256(raw).hexdigest() != digest
        or raw[bounds[2] :] != selected["_content_bytes"]
        or parse_carrier(raw, path).metadata != selected["header_json"]
        or sha256(reader.read(selection.manifest_path)).hexdigest()
        != selection.manifest_sha256
        or reader.currentness()["state"] != "unchanged"
    ):
        raise SourceChanged("Current SPEC source changed after selection.")
    return raw, bounds


def _change_spec_selected(
    selection,
    target,
    selected,
    path,
    digest,
    root,
    status,
    validate_project_spec_model,
    previous_capture,
):
    from ..native_update__shared import _move_ticket

    with _project_write_lock(selection.root):
        capture, _ = _revalidate_spec_capture(
            selection,
            previous_capture,
            selected,
            selected.get("_exact_ref"),
            "Current SPEC changed after selection.",
        )
        _check_spec_container(path, selected, capture.atoms)
        raw, bounds, destination, candidate = _plan_spec_status(
            selection,
            selected,
            path,
            digest,
            root,
            status,
            validate_project_spec_model,
            capture.atoms,
        )
        return _move_ticket(
            selection,
            target,
            selected,
            digest,
            path,
            destination,
            status,
            lambda: None,
            locked=True,
            preflight=(raw, bounds, None),
            candidate=candidate,
        )


def _revalidate_spec_capture(
    selection, previous_capture, selected, ref, message
):
    try:
        capture = revalidate_native(selection, previous_capture)
    except (OSError, RuntimeError, ValueError) as error:
        raise SourceChanged("Native carrier capture changed.") from error
    fresh = [row for row in capture.atoms if row.get("_exact_ref") == ref]
    if (
        capture.errors
        or len(fresh) != 1
        or any(
            fresh[0].get(k) != selected.get(k)
            for k in (
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
        raise SourceChanged(message)
    return capture, fresh[0]


def _check_spec_container(path, selected, atoms):
    if (
        path.with_suffix("").exists()
        or path.with_suffix("").is_symlink()
        or any(
            native_header_view(row["header_json"])
            .get("context", {})
            .get("container", {})
            .get("atom")
            == selected["id"]
            for row in atoms
        )
    ):
        raise InputError("target", "SPEC containers cannot change Status.")


def _plan_spec_status(
    selection,
    selected,
    path,
    digest,
    root,
    status,
    validate_project_spec_model,
    atoms,
):
    from ...drafts.native_draft__shared import _validate_project_template

    try:
        raw, bounds = _selected_spec_bytes(selection, selected, path, digest)
        header = selected["header_json"]
        body = raw[bounds[2] :].decode("utf-8")
        candidate = _status_bytes(raw, bounds, path, status)
        projected = parse_carrier(candidate, path).metadata
        if status == "active":
            _check_replacement_activation([selected], atoms)
            _validate_project_template(
                projected, validate_project_spec_model, body
            )
        destination = _spec_status_destination(
            selection,
            root,
            path,
            header,
            projected,
            body,
        )
    except InputError, SourceChanged:
        raise
    except (
        OSError,
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        raise SourceChanged(
            "Current SPEC source is unavailable or changed."
        ) from error
    return raw, bounds, destination, candidate


def _spec_status_destination(selection, root, path, header, projected, body):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        native_carrier_path,
    )
    from ...drafts.native_draft__shared import _summary

    parameters = getattr(selection, "parameters", None)
    expected = native_carrier_path(
        header,
        _summary(body),
        project_root=selection.control_root,
        owner_directory=root,
        parameters=parameters,
    )
    if path != expected and not (
        expected.parent == selection.root
        and path == selection.control_root / expected.name
    ):
        raise InputError(
            "target",
            "SPEC path disagrees with its Header and Summary.",
        )
    destination = native_carrier_path(
        projected,
        _summary(body),
        project_root=selection.control_root,
        owner_directory=root,
        parameters=parameters,
    )
    return destination
