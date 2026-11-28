"""Validate and archive an exact native SPEC Draft."""

from hashlib import sha256
from pathlib import Path
import re

from ...common import InputError, SourceChanged


def archive_spec_draft(
    selection,
    params,
    *,
    current_rows,
    structure_snapshot=None,
    previous_capture=None,
):
    """Archive an exact SPEC Draft without replacing an existing revision."""
    from . import native_update_spec__shared as host

    target, draft = _select_spec_draft(selection, params, current_rows)
    path, digest, owner = _archive_draft_location(
        selection, target, draft, structure_snapshot, current_rows
    )
    return host._archive_spec_selected(
        selection, target, draft, path, digest, owner, previous_capture
    )


def _select_spec_draft(selection, params, current_rows):
    if not isinstance(params, dict) or set(params) != {"target"}:
        raise InputError("target", "Supply one exact SPEC Draft target.")
    target = params["target"]
    if (
        not isinstance(target, dict)
        or set(target) != {"ref_id", "version"}
        or not isinstance(target["ref_id"], str)
        or type(target["version"]) is not int
        or target["version"] < 1
    ):
        raise InputError(
            "target", "Supply an exact SPEC Draft reference and Version."
        )
    match = re.fullmatch(
        re.escape(selection.project_prefix) + r"-S-[0-9]+@([1-9][0-9]*)-draft",
        target["ref_id"],
    )
    if match is None or int(match[1]) != target["version"]:
        raise InputError(
            "target",
            "Supply an exact SPEC Draft reference and matching Version.",
        )
    rows = [
        row
        for row in current_rows
        if row.get("_exact_ref") == target["ref_id"]
        and row.get("status_group") == "Draft"
    ]
    if len(rows) != 1:
        raise SourceChanged("SPEC Draft selection is missing or ambiguous.")
    draft = rows[0]
    return target, draft


def _archive_draft_location(
    selection, target, draft, structure_snapshot, current_rows
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        READY_DIRECTORY,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.sources.native_draft_source__shared import (
        _revision_root,
    )

    from . import native_update_spec__shared as host

    relative, digest = draft.get("source_path"), draft.get("_source_sha256")
    if (
        not isinstance(relative, str)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise SourceChanged("SPEC Draft capture lacks a path or digest.")
    relative = Path(relative)
    path = selection.root / relative
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not path.is_relative_to(selection.control_root)
        or path.parent.name != host.DRAFT_DIRECTORY
    ):
        raise InputError(
            "target", "Select a SPEC in its native Draft directory."
        )
    owner = path.parent.parent
    proposed = {
        **draft,
        "status": "ready",
        "source_path": (
            owner
            / READY_DIRECTORY
            / (draft["id"] + path.name[len(target["ref_id"]) :])
        )
        .relative_to(selection.root)
        .as_posix(),
    }
    if (
        _revision_root(selection, proposed, structure_snapshot, current_rows)
        != owner
    ):
        raise InputError("target", "SPEC Draft owner is invalid.")
    return path, digest, owner


def _archive_spec_selected(
    selection, target, draft, path, digest, owner, previous_capture
):
    from . import native_update_spec__shared as host

    with host._project_write_lock(selection.root):
        capture, source = host._revalidate_spec_capture(
            selection,
            previous_capture,
            draft,
            target["ref_id"],
            "SPEC Draft changed after selection.",
        )
        raw, bounds, body, header, used, version = _preflight_spec_archive(
            selection, target, draft, path, digest, owner, capture, source
        )
        return host._allocate_archived_spec(
            selection,
            target,
            draft,
            path,
            digest,
            owner,
            previous_capture,
            raw,
            bounds,
            body,
            header,
            used,
            version,
        )


def _preflight_spec_archive(
    selection, target, draft, path, digest, owner, capture, source
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        native_carrier_path,
    )
    from ...drafts.native_draft__shared import _summary

    from . import native_update_spec__shared as host

    reader = host.ReadContext(
        roots=[str(selection.root)], limits=dict(host.CEILINGS)
    )
    try:
        raw, bounds = _read_selected_draft(
            host, reader, selection, draft, path, digest
        )
        body = raw[bounds[2] :].decode("utf-8")
        header = draft["header_json"]
        if path != native_carrier_path(
            header,
            _summary(body),
            project_root=selection.control_root,
            owner_directory=owner,
        ):
            raise InputError(
                "target",
                "SPEC Draft path disagrees with its Header and Summary.",
            )
        used, version = _archive_versions(capture, source, draft, target)
    except (
        OSError,
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        raise SourceChanged(
            "SPEC Draft source is unavailable or changed."
        ) from error
    return raw, bounds, body, header, used, version


def _archive_versions(capture, source, draft, target):
    used = {
        row["version"]
        for row in capture.atoms
        if row["id"] == draft["id"] and row is not source
    }
    version = max(
        target["version"],
        getattr(capture, "max_archived_version", 0) + 1,
    )
    return used, version


def _read_selected_draft(host, reader, selection, draft, path, digest):
    raw = reader.read(path)
    bounds = host.frontmatter_bounds(raw)
    if (
        bounds is None
        or sha256(raw).hexdigest() != digest
        or raw[bounds[2] :] != draft["_content_bytes"]
        or host.parse_carrier(raw, path).metadata != draft["header_json"]
        or sha256(reader.read(selection.manifest_path)).hexdigest()
        != selection.manifest_sha256
        or reader.currentness()["state"] != "unchanged"
    ):
        raise SourceChanged("SPEC Draft changed after selection.")
    return raw, bounds
