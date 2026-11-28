"""Validate current Draft owner paths and captured evidence."""


def _selected_owner(rows, capture, owner_id, allow_draft):
    from . import native_draft_guards as guards

    owner_rows = [row for row in capture.atoms if row.get("id") == owner_id]
    group = (
        "Draft"
        if (
            allow_draft
            and len(owner_rows) == 1
            and owner_rows[0].get("version") == 1
            and owner_rows[0].get("status_group") == "Draft"
        )
        else "Current"
    )
    selected = [
        row
        for row in rows
        if row.get("id") == owner_id and row.get("status_group") == group
    ]
    fresh = [row for row in owner_rows if row.get("status_group") == group]
    if (
        len(selected) != 1
        or len(fresh) != 1
        or any(
            selected[0].get(key) != fresh[0].get(key)
            for key in (
                "source_path",
                "id",
                "_exact_ref",
                "version",
                "status",
                "status_group",
                "header_json",
                "_source_sha256",
            )
        )
    ):
        raise guards.common.SourceChanged(
            "Containing Task or Epic is missing or changed."
        )
    return fresh[0]


def _owner_context(row):
    from . import native_draft_guards as guards

    header = guards.native_header_view(row.get("header_json"))
    context = header.get("context") if isinstance(header, dict) else None
    template = context.get("template") if isinstance(context, dict) else None
    status = row.get("status")
    if template not in {"task", "epic"} or status not in {
        "active",
        "in_queue",
        "backlog",
        "done",
        "canceled",
        "resolved",
        "draft",
    }:
        raise guards.common.InputError(
            "container", "Containing Atom must be a planning Ticket."
        )
    relative = row.get("source_path")
    if not isinstance(relative, str):
        raise guards.common.SourceChanged("Containing Atom path is invalid.")
    relative = guards.Path(relative)
    return context, template, status, relative


def _check_owner(
    selection, container, rows, capture, seen=None, *, allow_draft=False
):
    from . import native_draft_guards as guards

    if isinstance(container, dict) and set(container) == {"component"}:
        return None, None
    if (
        not isinstance(container, dict)
        or set(container) != {"atom"}
        or not isinstance(container["atom"], str)
        or not guards.re.fullmatch(
            guards.re.escape(selection.project_prefix) + r"-T-[0-9]+",
            container["atom"],
        )
    ):
        raise guards.common.InputError(
            "container",
            "Supply C00 or a Current native Task or Epic in this Project.",
        )
    owner_id = container["atom"]
    seen = set() if seen is None else seen
    if owner_id in seen:
        raise guards.common.InputError(
            "container", "Containing Atom cycle is invalid."
        )
    seen.add(owner_id)
    row = _selected_owner(rows, capture, owner_id, allow_draft)
    context, template, status, relative = _owner_context(row)
    parent_directory, _ = guards._check_owner(
        selection,
        context.get("container"),
        rows,
        capture,
        seen,
        allow_draft=allow_draft,
    )
    return guards._checked_owner_path(
        selection, row, relative, parent_directory, owner_id, status, template
    )


def _verify_owner_source(selection, row, path):
    from . import native_draft_guards as guards

    try:
        reader = guards.ReadContext(
            roots=[str(selection.control_root)], limits=dict(guards.CEILINGS)
        )
        raw = reader.read(path)
        if (
            guards.sha256(raw).hexdigest() != row.get("_source_sha256")
            or guards.parse_carrier(raw, path).metadata
            != row.get("header_json")
            or reader.currentness()["state"] != "unchanged"
        ):
            raise ValueError("Owner changed")
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise guards.common.SourceChanged(
            "Containing Task or Epic source changed."
        ) from error


def _owner_root(selection, path, parent_directory, status):
    from . import native_draft_guards as guards

    flat_root = (
        next(
            (
                selection.control_root / name
                for name in (guards.TICKET_DIRECTORY, "001_TICKETS", "__TKT")
                if path.is_relative_to(selection.control_root / name)
            ),
            selection.control_root / guards.TICKET_DIRECTORY,
        )
        / "TASKS"
    )
    root = parent_directory or flat_root
    directory = {
        "active": "",
        "in_queue": "",
        "draft": (
            "000_draft"
            if path.parent.name == "000_draft"
            else guards.DRAFT_DIRECTORY
        ),
    }.get(status, status)
    if path.parent == flat_root / directory:
        root = flat_root
    return root, directory


def _checked_owner_path(
    selection, row, relative, parent_directory, owner_id, status, template
):
    from . import native_draft_guards as guards

    path = selection.root / relative
    root, directory = _owner_root(selection, path, parent_directory, status)
    marker = f"{owner_id}@1-draft" if status == "draft" else owner_id
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not path.is_relative_to(root)
        or path.parent != root / directory
        or not guards.re.fullmatch(
            guards.re.escape(marker)
            + (
                r"-.+\.md"
                if "atom_family" in row["header_json"]
                else "-" + template.upper() + r"--.+\.md"
            ),
            path.name,
        )
    ):
        raise guards.common.InputError(
            "container", "Containing Atom is outside its native Task branch."
        )
    _verify_owner_source(selection, row, path)
    return path.with_suffix(""), template
