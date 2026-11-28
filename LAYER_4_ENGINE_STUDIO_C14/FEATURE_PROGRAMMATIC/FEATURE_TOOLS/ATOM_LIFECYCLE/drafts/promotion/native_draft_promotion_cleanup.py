"""Recover publication when its Draft was not removed."""


def _cleanup_published_draft(
    selection,
    target,
    status,
    draft,
    current,
    structure_snapshot,
    current_rows,
    previous_capture,
):
    from . import native_draft_promotion__shared as p

    atom_id, version = target["ref_id"].split("@")[0], target["version"]
    if current.get("status") != status:
        raise p.common.InputError(
            "targetStatus",
            "Published carrier Status differs from the requested Status.",
        )
    root = p._revision_root(
        selection, current, structure_snapshot, current_rows
    )
    paths = _cleanup_paths(selection, target, draft, current, atom_id, root)
    with p._project_write_lock(selection.root):
        _check_companion(paths[0], atom_id)
        p._preflight_cleanup(
            selection,
            target,
            status,
            draft,
            current,
            current_rows,
            previous_capture,
            atom_id,
            version,
            root,
            paths,
        )
        with p.bind_query_reader(None):
            removed = p.effects.remove(
                selection.root, paths[0], draft["_source_sha256"]
            )
        return _cleanup_result(
            selection, paths, atom_id, version, status, removed
        )


def _check_companion(path, atom_id):
    from . import native_draft_promotion__shared as p

    companion = path.with_suffix("")
    if "-T-" in atom_id and (companion.exists() or companion.is_symlink()):
        raise p.common.InputError(
            "target",
            (
                "Recover the interrupted Draft companion before removing its "
                "carrier."
            ),
        )


def _cleanup_result(selection, paths, atom_id, version, status, removed):
    from . import native_draft_promotion__shared as p

    data = (
        {}
        if removed.errors
        else {
            "artifact": p.common.saved(
                selection, paths[1], atom_id, atom_id, version, status
            )
        }
    )
    return p.common.result(
        effects=removed.effects, errors=removed.errors, **data
    )


def _cleanup_paths(selection, target, draft, current, atom_id, root):
    from . import native_draft_promotion__shared as p

    paths = []
    for row, marker, directory in (
        (
            draft,
            target["ref_id"],
            (selection.root / draft["source_path"]).parent,
        ),
        (current, atom_id, (selection.root / current["source_path"]).parent),
    ):
        relative, digest = row.get("source_path"), row.get("_source_sha256")
        if (
            not isinstance(relative, str)
            or not isinstance(digest, str)
            or not p.re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise p.common.SourceChanged(
                "Carrier capture lacks a valid path or digest."
            )
        relative = p.Path(relative)
        path = selection.root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or path.parent != directory
            or (
                row is draft
                and path.parent
                not in {root / p.DRAFT_DIRECTORY, root / "000_draft"}
            )
            or not p.re.fullmatch(p.re.escape(marker) + r"-.+\.md", path.name)
        ):
            raise p.common.SourceChanged("Carrier path is invalid.")
        paths.append(path)
    if paths[0].name[len(target["ref_id"]) :] != paths[1].name[len(atom_id) :]:
        raise p.common.InputError(
            "target", "Published carrier filename differs from the Draft."
        )
    return paths


def _preflight_cleanup(
    selection,
    target,
    status,
    draft,
    current,
    current_rows,
    previous_capture,
    atom_id,
    version,
    root,
    paths,
):
    from . import native_draft_promotion__shared as p

    try:
        capture = p.revalidate_native(selection, previous_capture)
        _check_capture(capture)
        p._check_cleanup_rows(capture, draft, current)
        _read_cleanup(selection, draft, current, paths)
        draft_header, current_header = (
            draft["header_json"],
            current["header_json"],
        )
        p._check_cleanup_task_paths(
            selection,
            draft,
            current_rows,
            capture,
            atom_id,
            version,
            root,
            paths,
            status,
            draft_header,
            current_header,
        )
        _check_equivalence(draft, current, draft_header, current_header)
    except p.common.InputError, p.common.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise p.common.SourceChanged(
            "Native source is unavailable or changed."
        ) from error


def _check_capture(capture):
    from . import native_draft_promotion__shared as p

    if capture.errors:
        raise p.common.SourceChanged("Native carrier capture is incomplete.")


def _check_equivalence(draft, current, draft_header, current_header):
    from . import native_draft_promotion__shared as p

    if (
        p._revision_header(draft_header) != p._revision_header(current_header)
        or draft["_content_bytes"] != current["_content_bytes"]
    ):
        raise p.common.InputError(
            "target", "Published carrier differs from the Draft."
        )


def _read_cleanup(selection, draft, current, paths):
    from . import native_draft_promotion__shared as p

    reader = p.ReadContext(
        roots=[str(selection.control_root)], limits=dict(p.CEILINGS)
    )
    for row, path in zip((draft, current), paths, strict=False):
        raw = reader.read(path)
        bounds = p.frontmatter_bounds(raw)
        if (
            bounds is None
            or p.sha256(raw).hexdigest() != row["_source_sha256"]
            or raw[bounds[2] :] != row.get("_content_bytes")
            or p.parse_carrier(raw, path).metadata != row.get("header_json")
        ):
            raise p.common.SourceChanged(
                "Draft or published carrier changed after selection."
            )
    if reader.currentness()["state"] != "unchanged":
        raise p.common.SourceChanged(
            "Draft or published carrier changed after selection."
        )


def _check_cleanup_task_paths(
    selection,
    draft,
    current_rows,
    capture,
    atom_id,
    version,
    root,
    paths,
    status,
    draft_header,
    current_header,
):
    from . import native_draft_promotion__shared as p

    if "-T-" in atom_id:
        owner = p._check_owner(
            selection,
            p.native_header_view(current_header)["context"].get("container"),
            current_rows,
            capture,
        )
    if "-T-" in atom_id and "atom_family" in current_header:
        body = draft["_content_bytes"].decode("utf-8")
        if paths[0] != p._task_path(
            selection, draft_header, body, "draft", version, owner, root
        ) or paths[1] != p._task_path(
            selection, current_header, body, status, version, owner, root
        ):
            raise p.common.InputError(
                "target",
                "Task paths disagree with their authored Headers and Summary.",
            )


def _check_cleanup_rows(capture, draft, current):
    from . import native_draft_promotion__shared as p

    for row in (draft, current):
        fresh = [
            item
            for item in capture.atoms
            if item.get("_exact_ref") == row.get("_exact_ref")
        ]
        if len(fresh) != 1 or any(
            fresh[0].get(key) != row.get(key)
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
                "_source_sha256",
            )
        ):
            raise p.common.SourceChanged(
                "Draft or published carrier changed after selection."
            )
