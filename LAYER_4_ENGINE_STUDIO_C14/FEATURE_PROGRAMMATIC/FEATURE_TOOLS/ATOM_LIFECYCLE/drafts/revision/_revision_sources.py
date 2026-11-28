"""Revalidate and read the two revision sources."""

from . import native_draft_revision__shared as origin


def _read_revision_sources(
    selection, draft, previous, previous_capture, paths, atom_id, version
):
    capture = origin.revalidate_native(selection, previous_capture)
    if capture.errors:
        raise origin.common.SourceChanged(
            "Native carrier capture is incomplete."
        )
    _validate_revision_capture(capture, draft, previous, atom_id, version)
    reader = origin.ReadContext(
        roots=[str(selection.root)], limits=dict(origin.CEILINGS)
    )
    raw_draft, raw_previous = (reader.read(path) for path in paths)
    _validate_revision_bytes(draft, previous, paths, raw_draft, raw_previous)
    draft_bounds, previous_bounds = (
        origin.frontmatter_bounds(raw_draft),
        origin.frontmatter_bounds(raw_previous),
    )
    draft_body, previous_body = (
        raw_draft[draft_bounds[2] :].decode(),
        raw_previous[previous_bounds[2] :].decode(),
    )
    return (
        capture,
        raw_draft,
        raw_previous,
        draft_bounds,
        previous_bounds,
        draft_body,
        previous_body,
    )


def _validate_revision_capture(capture, draft, previous, atom_id, version):
    for row in (draft, previous):
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
            raise origin.common.SourceChanged(
                "Draft or Current predecessor changed after selection."
            )
    if any(
        row.get("id") == atom_id
        and row.get("version") == version
        and row.get("status_group") != "Draft"
        for row in capture.atoms
    ):
        raise origin.common.InputError(
            "target", "The Draft Version already has a non-Draft revision."
        )


def _validate_revision_bytes(draft, previous, paths, raw_draft, raw_previous):
    for row, path, raw in zip(
        (draft, previous), paths, (raw_draft, raw_previous), strict=False
    ):
        bounds = origin.frontmatter_bounds(raw)
        if (
            bounds is None
            or origin.sha256(raw).hexdigest() != row["_source_sha256"]
            or raw[bounds[2] :] != row.get("_content_bytes")
            or origin.parse_carrier(raw, path).metadata
            != row.get("header_json")
        ):
            raise origin.common.SourceChanged(
                "Draft or Current predecessor changed after selection."
            )
