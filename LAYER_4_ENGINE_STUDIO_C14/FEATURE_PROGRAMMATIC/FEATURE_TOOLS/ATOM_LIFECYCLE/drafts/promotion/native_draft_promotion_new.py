"""Preflight the first publication of a native Ticket Draft."""


def _preflight_new(
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
):
    from . import native_draft_promotion__shared as p

    try:
        capture = p.revalidate_native(selection, previous_capture)
        _check_history(capture, draft, atom_id)
        header = draft.get("header_json")
        context = p.native_header_view(header).get("context")
        if not isinstance(context, dict) or context.get("template") not in (
            "task",
            "epic",
        ):
            raise p.common.InputError(
                "target", "Select a native Task or Epic Draft."
            )
        owner = p._check_owner(
            selection, context.get("container"), current_rows, capture
        )
        raw, bounds, body = _read_draft(selection, draft, path, digest, header)
        destination = _destination(
            selection, target, status, path, root, atom_id, header, body, owner
        )
        promoted = p._state_bytes(raw, bounds, path, 1, body, status)
    except p.common.InputError, p.common.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise p.common.SourceChanged(
            "Native source is unavailable or changed."
        ) from error
    return capture, destination, promoted


def _check_history(capture, draft, atom_id):
    from . import native_draft_promotion__shared as p

    rows = [row for row in capture.atoms if row.get("id") == atom_id]
    if (
        capture.errors
        or len(rows) != 1
        or any(
            rows[0].get(key) != draft.get(key)
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
        raise p.common.SourceChanged(
            "Task Draft changed or its identity already has history."
        )


def _read_draft(selection, draft, path, digest, header):
    from . import native_draft_promotion__shared as p

    reader = p.ReadContext(
        roots=[str(selection.control_root)], limits=dict(p.CEILINGS)
    )
    raw = reader.read(path)
    bounds = p.frontmatter_bounds(raw)
    if (
        bounds is None
        or p.sha256(raw).hexdigest() != digest
        or raw[bounds[2] :] != draft.get("_content_bytes")
        or p.parse_carrier(raw, path).metadata != header
        or reader.currentness()["state"] != "unchanged"
    ):
        raise p.common.SourceChanged(
            "Task Draft source changed after selection."
        )
    body = raw[bounds[2] :].decode("utf-8")
    return raw, bounds, body


def _destination(
    selection, target, status, path, root, atom_id, header, body, owner
):
    from . import native_draft_promotion__shared as p

    slug = p._native_slug(body)
    if path != (
        p._task_path(selection, header, body, "draft", 1, owner, root)
        if "atom_family" in header
        else root / p.DRAFT_DIRECTORY / f"{target['ref_id']}-TASK--{slug}.md"
    ):
        raise p.common.InputError(
            "target", "Task Draft filename disagrees with its Summary."
        )
    destination = (
        p._task_path(selection, header, body, status, 1, owner, root)
        if "atom_family" in header
        else root
        / ("" if status in {"active", "in_queue"} else status)
        / f"{atom_id}-TASK--{slug}.md"
    )
    _check_destination(destination)
    return destination


def _check_destination(destination):
    from . import native_draft_promotion__shared as p

    if destination.exists() or destination.is_symlink():
        raise p.common.InputError(
            "target", "The promotion destination already exists."
        )
    if destination.parent.is_symlink() or (
        destination.parent.exists() and not destination.parent.is_dir()
    ):
        raise p.common.InputError(
            "target", "The promotion destination directory is unsafe."
        )
