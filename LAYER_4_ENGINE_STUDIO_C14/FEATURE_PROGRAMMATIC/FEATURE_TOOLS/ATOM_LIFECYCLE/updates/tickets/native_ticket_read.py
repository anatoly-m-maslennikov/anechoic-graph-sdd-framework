"""Read and revalidate a selected native Ticket."""

from .. import native_update__shared as owner


def _capture_ticket(v):
    selection, path, selected = v["selection"], v["path"], v["selected"]
    companion = path.with_suffix("")
    tree = (
        owner._read_tree(selection.root, companion)
        if v["close_tree"] and companion.is_dir()
        else None
    )
    previous = v["previous_capture"]
    capture = (
        owner.capture_native(selection, domains=v["domains"])
        if previous is None
        else owner.revalidate_native(selection, previous)
    )
    _check_capture(v, capture)
    if v["placement"]:
        owner._branch(
            selection, path, selected["status"], selected, capture.atoms
        )
    owner._check_ticket_tree(
        selection,
        path,
        selected,
        capture,
        tree,
        v["close_tree"],
        v["require_terminal"],
    )
    return tree, capture


def _check_capture(v, capture):
    selected = v["selected"]
    if capture.errors:
        raise owner.SourceChanged("Native carrier capture is incomplete.")
    fresh = [
        row
        for row in capture.atoms
        if row.get("ref") == v["target"]["ref_id"]
        and row.get("status_group") == selected["status_group"]
    ]
    if len(fresh) != 1 or any(
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
        )
    ):
        raise owner.SourceChanged(
            "Current Ticket source changed after selection."
        )


def _read_ticket_bytes(selection, path, digest, selected):
    reader = owner.ReadContext(
        roots=[str(selection.control_root)], limits=dict(owner.CEILINGS)
    )
    raw = reader.read(path)
    bounds = owner.frontmatter_bounds(raw)
    if (
        bounds is None
        or owner.sha256(raw).hexdigest() != digest
        or raw[bounds[2] :] != selected.get("_content_bytes")
    ):
        raise owner.SourceChanged(
            "Current Ticket source changed after selection."
        )
    if owner.parse_carrier(raw, path).metadata != selected.get("header_json"):
        raise owner.SourceChanged(
            "Current Ticket header changed after selection."
        )
    return raw, bounds


def read_ticket(
    selection,
    target,
    selected,
    digest,
    path,
    *,
    close_tree=False,
    placement=False,
    require_terminal=False,
    previous_capture=None,
    domains=None,
):
    try:
        tree, capture = _capture_ticket(locals())
        raw, bounds = _read_ticket_bytes(selection, path, digest, selected)
    except owner.InputError:
        raise
    except owner.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise owner.SourceChanged(
            "Native source is unavailable or changed."
        ) from error
    return raw, bounds, tree, capture
