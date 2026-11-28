"""Derive exact predecessor archival destinations."""

from . import placement__shared as runtime


def _predecessor_status(source, atom_id, version):
    if not source.is_file():
        raise runtime.PlacementError("Exact predecessor Carrier is missing")
    reader = runtime.query_reader()
    raw = (
        reader.lifecycle_read(source)
        if reader is not None
        else source.read_bytes()
    )
    view = runtime.carrier_read_view(
        runtime.parse_carrier(raw, source).metadata
    )
    old_status = view.get("status")
    if (
        view.get("atom_id") != atom_id
        or type(view.get("version")) is not int
        or view.get("version") != version
        or not isinstance(old_status, str)
        or not runtime.re.fullmatch(r"[A-Za-z]+", old_status)
        or old_status.casefold() in {"draft", "archived"}
    ):
        raise runtime.PlacementError(
            "Predecessor identity, Version or Current Status is invalid"
        )
    return old_status.casefold()


def _archive_destination(
    root, role_root, parent, role, atom_id, version, source_path
):
    if source_path is None:
        raise runtime.PlacementError(
            "Archival requires the exact source Carrier"
        )
    source = runtime._inside(runtime.Path(source_path), role_root)
    old_state = runtime._predecessor_status(source, atom_id, version)
    model = runtime.active_placement()
    if source.parent != runtime._status_directory(
        role_root, role, old_state, parent
    ):
        raise runtime.PlacementError(
            "Predecessor Status does not match its location"
        )
    match = runtime.re.fullmatch(
        r"((?:[1-9][0-9]*-)?)" + runtime.re.escape(atom_id) + r"(?!@)(.*)\.md",
        source.name,
    )
    if not match:
        raise runtime.PlacementError("Unsupported predecessor filename")
    stem = match.group(1) + atom_id + "@" + str(version) + match.group(2)
    archive_base, archive_folder = model.placement(role, "Archived")
    if archive_base != "role":
        raise runtime.PlacementError("Archived placement is not Role-owned")
    return runtime._inside(role_root / archive_folder / (stem + ".md"), root)


def _derive_bound(selection, identity, options):
    atom_id, version, status, role, summary, scope_unit = identity
    tier, parent = options[2], options[4]
    source_path, archived_update = options[5], options[7]
    row, role_root, parent = runtime._scope_binding(
        selection, atom_id, version, role, scope_unit, parent
    )
    if status is not None and (
        not isinstance(status, str)
        or not runtime.re.fullmatch(r"[A-Za-z]+", status)
    ):
        raise runtime.PlacementError("Invalid admitted Status")
    state = status.casefold() if status else None
    if state == "archived" and not archived_update:
        return runtime._archive_destination(
            selection.root,
            role_root,
            parent,
            role,
            atom_id,
            version,
            source_path,
        )
    if archived_update and (
        state != "archived" or parent is not None or source_path is not None
    ):
        raise runtime.PlacementError(
            "Archived update requires a scope-owned Carrier"
        )
    if source_path is not None:
        raise runtime.PlacementError(
            "Source path applies only to exact predecessor archival"
        )
    if tier is not None and (type(tier) is not int or tier < 0):
        raise runtime.PlacementError("Invalid Tier")
    name = _placement_filename(identity, options, row)
    if archived_update:
        name = name.replace(atom_id, f"{atom_id}@{version}", 1)
    directory = runtime._status_directory(role_root, role, status, parent)
    return runtime._inside(directory / name, selection.root)


def _placement_filename(identity, options, row):
    atom_id, version, status, role, summary, _scope_unit = identity
    (
        form,
        label,
        tier,
        target_scope,
        _parent,
        _source,
        work_sequence,
        _archived,
    ) = options
    name = runtime.derive_filename(
        atom_id=atom_id,
        version=version,
        status=status,
        role=role,
        summary=summary,
        row=row,
        form=form,
        label=label,
        tier=tier,
        target_scope=target_scope,
        work_sequence=work_sequence,
    )
    return name
