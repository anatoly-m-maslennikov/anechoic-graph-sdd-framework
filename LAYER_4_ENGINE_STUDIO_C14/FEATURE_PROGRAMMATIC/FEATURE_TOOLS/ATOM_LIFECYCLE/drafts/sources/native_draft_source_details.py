"""Validate Draft source locations and construct state revisions."""


def _task_root(selection, current_rows, path, context, status):
    from . import native_draft_source__shared as src

    if current_rows is None:
        raise src.common.SourceChanged("Current owner capture is unavailable.")
    capture = src.SimpleNamespace(atoms=current_rows)
    owner_directory, _ = src._check_owner(
        selection, context.get("container"), current_rows, capture
    )
    flat_root = (
        next(
            (
                selection.control_root / name
                for name in (src.TICKET_DIRECTORY, "001_TICKETS", "__TKT")
                if path.is_relative_to(selection.control_root / name)
            ),
            selection.control_root / src.TICKET_DIRECTORY,
        )
        / "TASKS"
    )
    root = owner_directory or flat_root
    if path.parent == flat_root / (
        "" if status in {"active", "in_queue"} else str(status)
    ):
        root = flat_root
    return root


def _task_revision_root(
    selection, row, current_rows, path, atom_id, context, status
):
    from . import native_draft_source__shared as src

    root = _task_root(selection, current_rows, path, context, status)
    directory = () if status in {"active", "in_queue"} else (status,)
    template = context.get("template")
    if (
        not isinstance(status, str)
        or status
        not in {
            "active",
            "in_queue",
            "backlog",
            "done",
            "canceled",
            "resolved",
        }
        or template not in {"task", "epic"}
        or not path.is_relative_to(root)
        or path.relative_to(root).parts[:-1] != directory
        or not src.re.fullmatch(
            src.re.escape(atom_id)
            + (
                r"-.+--.+\.md"
                if "atom_family" in row["header_json"]
                else "-" + template.upper() + r"--.+\.md"
            ),
            path.name,
        )
    ):
        raise src.common.InputError(
            "sourceCurrent",
            "Select a native Task or Epic in its Current directory.",
        )
    return root


def _check_spec_parent(
    selection,
    structure_snapshot,
    root,
    component,
    fields,
    component_manifest_parent,
):
    from . import native_draft_source__shared as src

    snapshot_path = getattr(selection, "structure_snapshot", None)
    if (
        structure_snapshot is not None or snapshot_path is not None
    ) and root != selection.control_root:
        snapshot = (
            structure_snapshot
            if structure_snapshot is not None
            else src.read_structure(snapshot_path)
        )
        declaration = src.Path(snapshot.component(component).source_path)
        parent = component_manifest_parent(
            declaration, fields.get("parameters")
        )
        if selection.control_root / parent != root.parent:
            raise ValueError(
                "Component parent contradicts the current Structure"
            )


def _check_spec_location(selection, root, component, project_component):
    from . import native_draft_source__shared as src

    if (
        not root.is_relative_to(selection.control_root)
        or (root == selection.control_root and component != project_component)
        or (
            root != selection.control_root
            and not root.name.endswith("_" + component)
        )
    ):
        raise ValueError("Component path disagrees")
    if any(
        part.startswith("_") or not src.re.search(r"_C[0-9]+$", part)
        for part in root.relative_to(selection.control_root).parts
    ):
        raise ValueError("Nested carrier path")


def _resolve_spec_root(
    selection,
    structure_snapshot,
    path,
    header,
    context,
    status,
    lens,
    container,
    manifest_inputs,
    component_manifest_parent,
):
    from . import native_draft_source__shared as src

    reader = src.ReadContext(
        roots=[str(selection.root)], limits=dict(src.CEILINGS)
    )
    raw = reader.read(selection.manifest_path)
    if src.sha256(raw).hexdigest() != selection.manifest_sha256:
        raise ValueError("Manifest changed")
    fields, project_component = manifest_inputs(
        selection.manifest_path,
        src.parse_carrier(raw, selection.manifest_path),
    )
    root = (
        path.parent.parent
        if status == "ready" and path.parent.name == src.READY_DIRECTORY
        else path.parent
    )
    tier = header.get("tier", context.get("tier"))
    root = src._spec_lens_owner(
        root, tier, lens, status, getattr(selection, "parameters", None)
    )
    component = container["component"]
    _check_spec_location(selection, root, component, project_component)
    _check_spec_parent(
        selection,
        structure_snapshot,
        root,
        component,
        fields,
        component_manifest_parent,
    )
    return root


def _spec_revision_root(
    selection, structure_snapshot, path, header, context, status
):
    from . import native_draft_source__shared as src

    lens = context.get("lens")
    container = context.get("container")
    if (
        not isinstance(lens, str)
        or not isinstance(container, dict)
        or set(container) != {"component"}
    ):
        raise src.common.InputError(
            "sourceCurrent", "Select a component-owned SPEC carrier."
        )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        component_manifest_parent,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
        manifest_inputs,
    )

    try:
        return _resolve_spec_root(
            selection,
            structure_snapshot,
            path,
            header,
            context,
            status,
            lens,
            container,
            manifest_inputs,
            component_manifest_parent,
        )
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        AttributeError,
        KeyError,
    ) as error:
        raise src.common.InputError(
            "sourceCurrent",
            "SPEC carrier must be in its lens and component root.",
        ) from error


def _state_edits(node, fields, values):
    from . import native_draft_source__shared as src

    edits = []
    family = [value for key, value in node.value if key.value == "atom_family"]
    if (
        len(family) == 1
        and isinstance(family[0], src.yaml.ScalarNode)
        and family[0].value == "PMETA"
    ):
        edits.append(
            (
                family[0].start_mark.index,
                family[0].end_mark.index,
                "PROJECT_CONFIG",
            )
        )
    for name, value in values.items():
        found = [item for key, item in fields if key.value == name]
        if len(found) != 1 or not isinstance(found[0], src.yaml.ScalarNode):
            raise ValueError("Invalid state field")
        edits.append(
            (
                found[0].start_mark.index,
                found[0].end_mark.index,
                src.json.dumps(value),
            )
        )
    return edits


def _state_bytes(
    raw, bounds, path, version, body, status, *, update_timestamp=False
):
    from . import native_draft_source__shared as src

    header = raw[bounds[0] : bounds[1]].decode("utf-8")
    try:
        node = src.yaml.compose(header, Loader=src.yaml.SafeLoader)
        states = [value for key, value in node.value if key.value == "state"]
        if len(states) != 1 or not isinstance(states[0], src.yaml.MappingNode):
            raise ValueError("Invalid state")
        fields = states[0].value
        values = {"status": status, "version": version}
        if update_timestamp and any(
            key.value == "updated_at" for key, _ in fields
        ):
            values["updated_at"] = src.datetime.now(
                src.timezone.utc
            ).isoformat()
        edits = _state_edits(node, fields, values)
        for start, end, value in sorted(edits, reverse=True):
            header = header[:start] + value + header[end:]
        candidate = (
            raw[: bounds[0]]
            + header.encode("utf-8")
            + raw[bounds[1] : bounds[2]]
            + body.encode("utf-8")
        )
        before = src.parse_carrier(raw, path).metadata
        after = src.parse_carrier(candidate, path).metadata
        expected = dict(before)
        if expected.get("atom_family") == "PMETA":
            expected["atom_family"] = "PROJECT_CONFIG"
        expected["state"] = {**before["state"], **values}
        if after != expected:
            raise ValueError("Unexpected header change")
        return candidate
    except (
        AttributeError,
        KeyError,
        TypeError,
        ValueError,
        src.yaml.YAMLError,
    ) as error:
        message = "Task needs valid scalar state fields."
        raise src.common.InputError("sourceCurrent", message) from error
