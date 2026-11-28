"""Resolve and validate revision carrier destinations."""

from . import native_draft_revision__shared as origin


def _revision_placement(
    selection,
    target,
    status,
    draft,
    previous,
    current_rows,
    structure_snapshot,
):
    atom_id, version = target["ref_id"].split("@")[0], target["version"]
    root = origin._revision_root(
        selection, previous, structure_snapshot, current_rows
    )
    paths = _revision_carriers(
        selection, target, draft, previous, root, atom_id
    )
    draft_path, previous_path = paths
    suffix = draft_path.name[len(target["ref_id"]) :]
    typed = origin.is_c9_typed_manifest(draft["header_json"])
    if not typed and previous_path.name != atom_id + suffix:
        raise origin.common.InputError(
            "target", "Draft and Current filename must agree."
        )
    previous_suffix = previous_path.name[len(atom_id) :]
    archive_path = (
        root / origin.ARCHIVE_DIRECTORY / f"{atom_id}@{previous['version']}"
        f"{previous_suffix if typed else suffix}"
    )
    destination = (
        root
        / ("" if status in {"active", "in_queue"} else status)
        / (atom_id + suffix)
        if "-T-" in atom_id
        else root / origin.READY_DIRECTORY / (atom_id + suffix)
        if "-S-" in atom_id
        else previous_path
    )

    return (atom_id, version), paths, root, archive_path, destination


def _revision_carriers(selection, target, draft, previous, root, atom_id):
    paths = []
    for row, marker, directory in (
        (
            draft,
            target["ref_id"],
            (selection.root / draft["source_path"]).parent,
        ),
        (previous, atom_id, (selection.root / previous["source_path"]).parent),
    ):
        relative, digest = row.get("source_path"), row.get("_source_sha256")
        if (
            not isinstance(relative, str)
            or not isinstance(digest, str)
            or not origin.re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise origin.common.SourceChanged(
                "Carrier capture lacks a valid path or source digest."
            )
        relative = origin.Path(relative)
        path = selection.root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or path.parent != directory
            or (
                row is draft
                and path.parent
                not in {root / origin.DRAFT_DIRECTORY, root / "000_draft"}
            )
            or not origin.re.fullmatch(
                origin.re.escape(marker) + r"-.+\.md", path.name
            )
        ):
            raise origin.common.InputError(
                "target",
                "Select carriers in their native revision directories.",
            )
        paths.append(path)
    return paths
