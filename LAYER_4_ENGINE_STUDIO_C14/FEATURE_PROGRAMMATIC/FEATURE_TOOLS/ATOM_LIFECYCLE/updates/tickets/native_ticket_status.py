"""Select and execute native Ticket status changes."""

from .. import native_update__shared as owner


def _destination(v):
    path, selected = v["path"], v["selected"]
    branch = owner._branch(
        v["selection"], path, selected["status"], selected, v["current_rows"]
    )
    status = v["status"]
    return (
        branch
        / (
            ""
            if status in {"active", "in_queue"}
            else owner.COMPLETE_DIRECTORY
            if status == "complete"
            else status
        )
        / path.name
    )


def _promote(v, destination):
    try:
        capture = owner.revalidate_native(
            v["selection"], v["previous_capture"]
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise owner.SourceChanged("Native carrier capture changed.") from error
    if capture.errors:
        raise owner.SourceChanged("Native carrier capture is incomplete.")
    return owner.promote_ticket_tree(
        v["selection"],
        v["selected"],
        destination,
        v["status"],
        v["current_rows"],
        capture,
        v["check_definition"],
    )


_DESCENDANT_KEYS = (
    "id",
    "version",
    "status",
    "source_path",
    "_source_sha256",
    "header_json",
)


def _plan(v, capture):
    selected, current_rows, move_tree = (
        v["selected"],
        v["current_rows"],
        v["move_tree"],
    )
    planned = (
        owner._descendants(current_rows, selected["id"]) if move_tree else []
    )
    fresh = (
        owner._descendants(capture.atoms, selected["id"]) if move_tree else []
    )
    if len(planned) != len(fresh) or any(
        any(before.get(key) != after.get(key) for key in _DESCENDANT_KEYS)
        for before, after in zip(planned, fresh, strict=False)
    ):
        raise owner.SourceChanged(
            "Ticket descendants changed after selection."
        )
    if (
        move_tree
        and selected["status"] in ("done", "canceled")
        and not v["terminal"]
        and v["status"] != "in_queue"
        and any(row["status"] != v["status"] for row in planned)
    ):
        raise owner.InputError(
            "target",
            "Reopening requires changing contained Ticket statuses; "
            "this operation is unsupported.",
        )
    actions = [
        row
        for row in planned
        if v["terminal"]
        and row["status"] not in ("done", "canceled", "resolved", "complete")
    ]
    actions.append(selected)
    return actions


def _apply(v):
    raw, bounds, tree, capture = owner._read_ticket(
        v["selection"],
        v["target"],
        v["selected"],
        v["digest"],
        v["path"],
        close_tree=v["move_tree"],
        placement=True,
        previous_capture=v["previous_capture"],
    )
    actions = _plan(v, capture)
    return owner._apply_status_actions(
        v["selection"],
        actions,
        v["selected"],
        v["status"],
        v["current_rows"],
        v["terminal"],
        v["check_definition"],
        raw,
        bounds,
        tree,
        v["recorded"],
        v["domains"],
    )


def _locked(v):
    destination = _destination(v)
    path = v["path"]
    if destination != path and (
        destination.exists()
        or destination.is_symlink()
        or (
            v["move_tree"]
            and (
                destination.with_suffix("").exists()
                or destination.with_suffix("").is_symlink()
            )
        )
    ):
        return owner.result(
            errors=[
                {
                    "code": "destination_exists",
                    "message": "Ticket destination already exists.",
                }
            ]
        )
    if (
        v["move_tree"]
        and v["selected"]["status"] == "backlog"
        and v["status"] == "in_queue"
    ):
        return _promote(v, destination)
    return _apply(v)


def change_status(v):
    params, selection = v["params"], v["selection"]
    if not isinstance(params, dict) or set(params) != {
        "target",
        "targetStatus",
    }:
        raise owner.InputError(
            "target", "Supply one target and target Status."
        )
    domains = getattr(v["previous_capture"], "status_domains", None)
    allowed = owner._ticket_status_domain(domains)
    status = owner._requested_status(params["targetStatus"], allowed)
    target = params["target"]
    selected, digest, path = owner._select_ticket(
        selection, target, v["current_rows"]
    )
    template = owner._ticket_template(
        selected, status, allowed - owner.CURRENT_STATUSES["T"]
    )
    move_tree = template in ("task", "epic")
    terminal = move_tree and status in ("done", "canceled")
    v.update(
        domains=domains,
        status=status,
        target=target,
        selected=selected,
        digest=digest,
        path=path,
        move_tree=move_tree,
        terminal=terminal,
        recorded=[],
    )
    with owner._project_write_lock(selection.root):
        return _locked(v)
