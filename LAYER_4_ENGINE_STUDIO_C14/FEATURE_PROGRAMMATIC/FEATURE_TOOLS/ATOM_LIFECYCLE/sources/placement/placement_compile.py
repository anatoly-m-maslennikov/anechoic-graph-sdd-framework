"""Compile declared Role and Status placement bindings."""

from . import placement_model as owner


def _role_statuses(role, entry, rules, required_statuses):
    statuses = {
        status
        for selected_role, status in rules
        if selected_role in (None, role)
    }
    expected = (
        {owner._name(status) for status in required_statuses.get(role, ())}
        if required_statuses is not None
        else set()
    )
    if (None, "*") in rules and rules[(None, "*")][1] == "<status folder>":
        if not expected:
            raise ValueError(
                f"{entry['role']}: Current Status domain is missing"
            )
        statuses.remove("*")
        statuses.update(expected - {"draft", "archived"})
    if (
        required_statuses is not None
        and "*" not in statuses
        and (not expected or not expected.issubset(statuses))
    ):
        raise ValueError(
            f"{entry['role']}: incomplete Status placement declarations"
        )
    return statuses


def _role_records(
    role, entry, statuses, rules, sources, by_id, status_folders
):
    records = []
    for status in sorted(statuses):
        binding = rules.get((role, status), rules.get((None, status)))
        if binding is None and status not in {"draft", "archived"}:
            binding = rules.get((None, "*"))
        if binding is None:
            raise ValueError(f"{entry['role']}: Status placement is missing")
        base, folder, source = binding
        if folder == "<status folder>":
            if status not in status_folders:
                raise ValueError(
                    f"{entry['role']}: Status order is missing for {status}"
                )
            folder, order_source = status_folders[status]
            sources[order_source] = by_id[order_source]
        records.append(
            {
                "role": entry["role"],
                "status": status,
                "base": base,
                "folder": folder,
                "source": source,
            }
        )
    return records


def _compile_placement_records(
    folders,
    rules,
    sources,
    requirement_rows,
    required_statuses,
    status_folders,
):
    records = []
    by_id = {row["id"]: row for row in requirement_rows}
    for role, entry in folders.items():
        statuses = _role_statuses(role, entry, rules, required_statuses)
        records.extend(
            _role_records(
                role, entry, statuses, rules, sources, by_id, status_folders
            )
        )
    return records


def _read_declarations(rows, rules, sources):
    generic_source = None
    for row in rows:
        body = row["_content_bytes"].decode("utf-8")
        for rule in owner.parse_placement_claim(body) or ():
            source = row["id"]
            if rule["kind"] == "role_root":
                if generic_source is not None:
                    raise ValueError(
                        "Duplicate generic Role placement template"
                    )
                generic_source = source
                sources[source] = row
                continue
            role = None if rule["role"] is None else owner._name(rule["role"])
            status = (
                "*" if rule["status"] == "*" else owner._name(rule["status"])
            )
            if (role, status) in rules:
                raise ValueError(f"{source}: duplicate placement binding")
            rules[(role, status)] = (rule["base"], rule["folder"], source)
            sources[source] = row
    return generic_source


def _bind_role_folders(
    generic_source,
    role_folders,
    declared_roles,
    requirement_rows,
    folders,
    sources,
):
    if generic_source is not None:
        if not role_folders or (
            declared_roles is not None
            and {owner._name(role) for role in role_folders}
            != {owner._name(role) for role in declared_roles}
        ):
            raise ValueError("Role order declarations are incomplete")
        by_id = {row["id"]: row for row in requirement_rows}
        for role, (folder, source) in role_folders.items():
            folders[owner._name(role)] = {
                "role": role,
                "folder": folder,
                "source": source,
            }
            sources[source] = by_id[source]
    elif role_folders:
        raise ValueError("Generic Role placement template is missing")


def compile_placement(
    rows, requirement_rows=(), declared_roles=None, required_statuses=None
):
    """Compile native Delivery and model placement Declarations."""
    folders, rules, sources = {}, {}, {}
    role_folders, status_folders = owner._declared_orders(requirement_rows)
    generic_source = _read_declarations(rows, rules, sources)
    _bind_role_folders(
        generic_source,
        role_folders,
        declared_roles,
        requirement_rows,
        folders,
        sources,
    )
    if not sources:
        return None
    if not folders:
        raise ValueError("Placement Role folder declarations are missing")
    records = owner._compile_placement_records(
        folders,
        rules,
        sources,
        requirement_rows,
        required_statuses,
        status_folders,
    )
    payload = {
        "sources": [
            {
                "atom_id": row["id"],
                "version": row["version"],
                "sha256": row["_sha256"],
                "source_path": row["source_path"],
            }
            for row in sources.values()
        ],
        "role_folders": list(folders.values()),
        "placements": records,
        "archive_aliases": [],
    }
    owner.load_placement(payload)
    return payload
