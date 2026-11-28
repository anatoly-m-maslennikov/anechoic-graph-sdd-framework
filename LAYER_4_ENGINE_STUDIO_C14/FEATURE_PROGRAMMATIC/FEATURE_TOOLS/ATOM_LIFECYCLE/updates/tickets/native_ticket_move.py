"""Move a checked Ticket under its project write lock."""

from .. import native_update__shared as owner


def prepare_directory(
    selection, destination, recorded, recorded_errors, check
):
    if not destination.parent.exists():
        if not check():
            return owner.result(effects=recorded, errors=recorded_errors)
        try:
            owner._create_parents(selection.root, destination.parent, recorded)
        except OSError, ValueError:
            return owner.result(
                effects=recorded,
                errors=[
                    {
                        "code": "backend_failure",
                        "message": (
                            "Cannot create the Ticket status directory."
                        ),
                    }
                ],
            )
    return None


def source_intact(selection, path, digest, close_tree, tree, companion):
    try:
        reader = owner.ReadContext(
            roots=[str(selection.control_root)], limits=dict(owner.CEILINGS)
        )
        return owner.sha256(reader.read(path)).hexdigest() == digest and not (
            close_tree
            and tree is None
            and (companion.exists() or companion.is_symlink())
        )
    except OSError, RuntimeError, ValueError:
        return False


def definition_intact(check_definition, errors):
    try:
        check_definition()
        return True
    except Exception as error:
        errors.append(
            {"code": "definition_revalidation_required", "message": str(error)}
        )
        return False


def _preflight(v):
    if v["preflight"] is not None:
        return v["preflight"]
    raw, bounds, tree, _ = owner._read_ticket(
        v["selection"],
        v["target"],
        v["selected"],
        v["digest"],
        v["path"],
        close_tree=v["close_tree"],
        placement=True,
        require_terminal=v["require_terminal"],
        previous_capture=v["previous_capture"],
        domains=v["domains"],
    )
    return raw, bounds, tree


def _finish_move(v, recorded, recorded_errors):
    selected, target, status = v["selected"], v["target"], v["status"]
    ref = (
        f"{selected['id']}@{target['version']}"
        if status == "archived"
        else selected["id"]
    )
    data = (
        {}
        if recorded_errors
        else {
            "artifact": owner.saved(
                v["selection"],
                v["destination"],
                selected["id"],
                ref,
                target["version"],
                status,
            )
        }
    )
    return owner.result(effects=recorded, errors=recorded_errors, **data)


def _publish_move(
    v, tree, candidate, check, source_intact, recorded, recorded_errors
):
    selection, destination = v["selection"], v["destination"]

    def rollback():
        if source_intact():
            undone = owner.effects.remove(
                selection.root,
                destination,
                owner.sha256(candidate).hexdigest(),
            )
            recorded.extend(undone.effects)
            recorded_errors.extend(undone.errors)

    failure = owner._prepare_ticket_directory(
        selection, destination, recorded, recorded_errors, check
    )
    if failure is not None:
        return failure
    if not check():
        return owner.result(effects=recorded, errors=recorded_errors)
    if not source_intact():
        return owner.result(
            effects=recorded,
            errors=[
                {
                    "code": "source_changed",
                    "message": (
                        "Current Ticket source changed before publication."
                    ),
                }
            ],
        )
    return _perform_publication(
        v,
        tree,
        candidate,
        check,
        source_intact,
        recorded,
        recorded_errors,
        rollback,
    )


def _perform_publication(
    v,
    tree,
    candidate,
    check,
    source_intact,
    recorded,
    recorded_errors,
    rollback,
):
    selection, path, destination = v["selection"], v["path"], v["destination"]
    outcome = owner._publish_ticket(
        selection,
        path,
        destination,
        v["digest"],
        candidate,
        tree,
        v["companion"],
        v["target_companion"],
        recorded,
        recorded_errors,
        check,
        source_intact,
        rollback,
        owner.move_directory,
    )
    return (
        outcome
        if outcome is not None
        else _finish_move(v, recorded, recorded_errors)
    )


def _move_locked(v):
    destination, path = v["destination"], v["path"]
    v["companion"] = path.with_suffix("")
    target_companion = v["target_companion"] = destination.with_suffix("")
    if (
        destination.exists()
        or destination.is_symlink()
        or (
            v["close_tree"]
            and (target_companion.exists() or target_companion.is_symlink())
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
    raw, bounds, tree = _preflight(v)
    candidate = v["candidate"]
    if candidate is None:
        candidate = owner._status_bytes(raw, bounds, path, v["status"])
    recorded, recorded_errors = [], []
    check = owner.partial(
        owner._ticket_definition_intact, v["check_definition"], recorded_errors
    )
    source_intact = owner.partial(
        owner._ticket_source_intact,
        v["selection"],
        path,
        v["digest"],
        v["close_tree"],
        tree,
        v["companion"],
    )
    return _publish_move(
        v, tree, candidate, check, source_intact, recorded, recorded_errors
    )


def move_ticket(
    selection,
    target,
    selected,
    digest,
    path,
    destination,
    status,
    check_definition,
    *,
    close_tree=False,
    require_terminal=False,
    locked=False,
    preflight=None,
    previous_capture=None,
    domains=None,
    candidate=None,
):
    with (
        owner.nullcontext()
        if locked
        else owner._project_write_lock(selection.root)
    ):
        return _move_locked(locals())
