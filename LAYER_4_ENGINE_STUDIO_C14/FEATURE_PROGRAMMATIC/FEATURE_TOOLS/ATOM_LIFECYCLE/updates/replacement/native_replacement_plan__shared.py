"""Validate replacement targets and plan their archival."""

from . import native_replacement_promotion as owner


def _checked_replacement_targets(selection, draft, previous):
    relations = draft["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        raise owner.common.InputError("target", "Draft Relations are invalid.")
    targets = relations.get("IS_REPLACEMENT_FOR", [])
    if not isinstance(targets, list) or any(
        not isinstance(item, str)
        or not owner.re.fullmatch(
            owner.re.escape(selection.project_prefix) + r"-[STPC]-[0-9]+", item
        )
        for item in targets
    ):
        raise owner.common.InputError(
            "target", "Replacement targets must be base Atom IDs."
        )
    if draft["id"] in targets or len(targets) != len(set(targets)):
        raise owner.common.InputError(
            "target",
            "Replacement targets must be unique and different "
            "from the Draft Atom ID.",
        )
    adopted = () if previous is None else owner._replacement_targets(previous)
    if any(atom_id not in targets for atom_id in adopted):
        raise owner.common.InputError(
            "target",
            "A successor revision must retain its adopted replacement links.",
        )
    return targets, adopted


def _validate_replacement_draft(selection, draft, capture):
    if capture.errors or [
        row
        for row in capture.atoms
        if row.get("_exact_ref") == draft["_exact_ref"]
    ] != [draft]:
        raise owner.common.SourceChanged("Draft or native capture changed.")
    draft_path = selection.root / draft["source_path"]
    if (
        draft_path.with_suffix("").exists()
        or draft_path.with_suffix("").is_symlink()
        or any(
            row.get("status_group") == "Current"
            and owner.native_header_view(row["header_json"])
            .get("context", {})
            .get("container", {})
            .get("atom")
            == draft["id"]
            for row in capture.atoms
        )
    ):
        raise owner.common.InputError(
            "target", "A replacement Draft cannot be a container."
        )


def _plan_replacements(
    selection, draft, current_rows, structure_snapshot, capture, previous=None
):
    targets, adopted = _checked_replacement_targets(selection, draft, previous)
    if not targets:
        return []
    _validate_replacement_draft(selection, draft, capture)
    plans = []
    for atom_id in targets:
        plan = owner._plan_replacement(
            selection,
            draft,
            current_rows,
            structure_snapshot,
            capture,
            adopted,
            atom_id,
        )
        if plan is not None:
            plans.append(plan)
    return plans


def _target_location(selection, row, structure_snapshot, capture, atom_id):
    path = selection.root / row["source_path"]
    if (
        path.with_suffix("").exists()
        or path.with_suffix("").is_symlink()
        or any(
            item.get("status_group") == "Current"
            and owner.native_header_view(item["header_json"])
            .get("context", {})
            .get("container", {})
            .get("atom")
            == atom_id
            for item in capture.atoms
        )
    ):
        raise owner.common.InputError(
            "target", "Replacement target is a container."
        )
    header = row["header_json"]
    context = owner.native_header_view(header)["context"]
    custom = (
        header.get("atom_family") == "PROJECT_CONFIG"
        and context.get("container") == {"component": "C00"}
        and context.get("template")
        in {
            "model_manifest",
            "manifest_node",
            "manifest_property",
            "manifest_relation",
        }
    )
    root = (
        selection.control_root
        / owner.PROJECT_CONFIG_DIRECTORY
        / owner.CUSTOM_MODEL_DIRECTORY
        if custom
        else owner._revision_root(
            selection, row, structure_snapshot, capture.atoms
        )
    )
    return path, header, context, custom, root


def _archive_destination(v, body):
    selection, row, path, header, context, root, capture, atom_id = (
        v[key]
        for key in (
            "selection",
            "row",
            "path",
            "header",
            "context",
            "root",
            "capture",
            "atom_id",
        )
    )
    if "-T-" in atom_id and "atom_family" in header:
        ticket_owner = owner._check_owner(
            selection, context.get("container"), capture.atoms, capture
        )
        archive_path = owner._task_path(
            selection,
            header,
            body,
            "archived",
            row["version"],
            ticket_owner,
            root,
        )
    else:
        archive_path = (
            root
            / owner.ARCHIVE_DIRECTORY
            / (f"{atom_id}@{row['version']}" + path.name[len(atom_id) :])
        )
    return archive_path


def _archive_target(v):
    selection, row, path = v["selection"], v["row"], v["path"]
    header, context, custom = v["header"], v["context"], v["custom"]
    root, reader = v["root"], v["reader"]
    raw = reader.read(path)
    bounds = owner.frontmatter_bounds(raw)
    if (
        bounds is None
        or owner.sha256(raw).hexdigest() != row.get("_source_sha256")
        or owner.parse_carrier(raw, path).metadata != header
        or raw[bounds[2] :] != row.get("_content_bytes")
        or reader.currentness()["state"] != "unchanged"
    ):
        raise ValueError("Target changed")
    body = raw[bounds[2] :].decode("utf-8")
    if custom:
        owner._check_custom_path(selection, header, context, body, root, path)
    archive_path = _archive_destination(v, body)
    if (
        archive_path.exists()
        or archive_path.is_symlink()
        or archive_path.parent.is_symlink()
        or (archive_path.parent.exists() and not archive_path.parent.is_dir())
    ):
        raise owner.common.InputError(
            "target",
            "A replacement archive destination already exists or is unsafe.",
        )
    archived = owner._state_bytes(
        raw, bounds, path, row["version"], body, "archived"
    )
    return (row, path, archive_path, archived)


def _plan_replacement(
    selection,
    draft,
    current_rows,
    structure_snapshot,
    capture,
    adopted,
    atom_id,
):
    row = owner._replacement_row(atom_id, capture, current_rows, adopted)
    if row is None:
        return None
    path, header, context, custom, root = _target_location(
        selection, row, structure_snapshot, capture, atom_id
    )
    reader = owner.ReadContext(
        roots=[str(selection.root)], limits=dict(owner.CEILINGS)
    )
    try:
        return _archive_target(locals())
    except owner.common.InputError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise owner.common.SourceChanged(
            "Replacement target is unavailable or changed."
        ) from error
