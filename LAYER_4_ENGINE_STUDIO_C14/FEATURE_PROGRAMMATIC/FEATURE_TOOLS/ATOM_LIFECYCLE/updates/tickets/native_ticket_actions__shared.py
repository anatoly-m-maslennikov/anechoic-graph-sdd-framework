"""Apply a planned sequence of Ticket status actions."""

from .. import native_update__shared as owner


def _selection(v, status, target):
    current, digest, path = owner._select_ticket(
        v["selection"], target, v["current_rows"]
    )
    branch = owner._branch(
        v["selection"], path, current["status"], current, v["current_rows"]
    )
    destination = (
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
    template = (
        owner.native_header_view(current["header_json"])
        .get("context", {})
        .get("template")
    )
    return (
        status,
        target,
        current,
        digest,
        path,
        destination,
        template in ("task", "epic"),
    )


def _unchanged(v, action):
    _, target, current, digest, path, _, tree = action
    if len(v["actions"]) > 1:
        owner._read_ticket(
            v["selection"],
            target,
            current,
            digest,
            path,
            close_tree=tree,
            placement=True,
            require_terminal=v["terminal"],
            domains=v["domains"],
        )
    return owner.result(
        artifact=owner.saved(
            v["selection"],
            path,
            current["id"],
            current["id"],
            target["version"],
            current["status"],
        )
    )


def _move(v, action):
    status, target, current, digest, path, destination, tree = action
    return owner._move_ticket(
        v["selection"],
        target,
        current,
        digest,
        path,
        destination,
        status,
        v["check_definition"],
        close_tree=tree,
        require_terminal=v["terminal"],
        locked=True,
        preflight=(v["raw"], v["bounds"], v["tree"])
        if len(v["actions"]) == 1
        else None,
        domains=v["domains"],
    )


def apply_actions(v):
    recorded = v["recorded"]
    for row in v["actions"]:
        is_parent = row["id"] == v["selected"]["id"]
        status = v["status"] if is_parent else "canceled"
        target = {"ref_id": row["id"], "version": row["version"]}
        try:
            action = _selection(v, status, target)
            outcome = (
                _unchanged(v, action)
                if action[5] == action[4]
                else _move(v, action)
            )
        except (
            owner.InputError,
            owner.SourceChanged,
            OSError,
            ValueError,
            RuntimeError,
            TypeError,
            KeyError,
        ) as error:
            if not recorded:
                raise
            code = (
                "invalid_input"
                if isinstance(error, owner.InputError)
                else "source_changed"
            )
            return owner.result(
                effects=recorded,
                errors=[{"code": code, "message": f"{row['id']}: {error}"}],
            )
        recorded.extend(outcome.get("effects", ()))
        if outcome.get("errors"):
            return owner.result(
                effects=recorded,
                errors=[
                    {**error, "target": row["id"]}
                    for error in outcome["errors"]
                ],
            )
    return owner.result(effects=recorded, artifact=outcome["artifact"])
