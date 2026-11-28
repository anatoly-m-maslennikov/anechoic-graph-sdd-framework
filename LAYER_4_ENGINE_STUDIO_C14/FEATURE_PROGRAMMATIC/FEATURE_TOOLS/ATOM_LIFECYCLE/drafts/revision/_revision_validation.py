"""Validate revision compatibility and promotion destinations."""

from . import native_draft_revision__shared as origin


def _check_revision_headers(
    draft_header, previous_header, draft_body, previous_body, typed
):
    draft_revision, previous_revision = (
        origin._revision_header(draft_header),
        origin._revision_header(previous_header),
    )
    draft_revision, previous_revision = _normalize_typed_headers(
        draft_revision,
        previous_revision,
        previous_header,
        previous_body,
        typed,
    )
    _strip_replacement_relations(
        draft_header, previous_header, draft_revision, previous_revision
    )
    draft_relations = draft_revision.pop("relations", {})
    previous_relations = previous_revision.pop("relations", {})
    if (
        not isinstance(draft_relations, dict)
        or not isinstance(previous_relations, dict)
        or any(
            not isinstance(values, list)
            or not isinstance(previous_relations.get(key), list)
            or any(
                values.count(value) > previous_relations[key].count(value)
                for value in values
            )
            for key, values in draft_relations.items()
        )
    ):
        raise origin.common.InputError(
            "target", "A Draft may only remove existing authored relations."
        )
    if draft_revision != previous_revision or origin._summary(
        draft_body
    ) != origin._summary(previous_body):
        raise origin.common.InputError(
            "target",
            "Only a body revision with unchanged Summary is supported.",
        )


def _strip_replacement_relations(
    draft_header, previous_header, draft_revision, previous_revision
):
    if any(
        "IS_REPLACEMENT_FOR" in header.get("relations", {})
        for header in (draft_header, previous_header)
    ):
        for revision in (draft_revision, previous_revision):
            if isinstance(revision.get("relations"), dict):
                revision["relations"] = {
                    k: v
                    for k, v in revision["relations"].items()
                    if k != "IS_REPLACEMENT_FOR"
                }
                if not revision["relations"]:
                    revision.pop("relations")


def _normalize_typed_headers(
    draft_revision, previous_revision, previous_header, previous_body, typed
):
    if (
        typed
        and previous_header.get("atom_family") == "SPEC"
        and (
            previous_revision.get("context", {}).get("template")
            == draft_revision["context"]["template"]
            or (
                previous_revision.get("context", {}).get("template") is None
                and origin._has_formal_declaration(previous_body)
            )
        )
    ):
        draft_revision = {
            **draft_revision,
            "context": {
                k: v
                for k, v in draft_revision["context"].items()
                if k != "template"
            },
        }
        previous_revision = {
            **previous_revision,
            "context": {
                k: v
                for k, v in previous_revision["context"].items()
                if k != "template"
            },
        }
        if draft_revision["context"].get(
            "lens"
        ) == origin.CONTINUANT_LENS and previous_revision["context"].get(
            "lens"
        ) in {
            "SPEC",
            "DES",
        }:
            draft_revision["context"].pop("lens")
            previous_revision["context"].pop("lens")
            draft_revision.pop("concern", None)
            previous_revision.pop("concern", None)
    return draft_revision, previous_revision


def _check_promotion_destinations(
    archive_path, destination, previous_path, capture, atom_id
):
    if (
        archive_path.exists()
        or archive_path.is_symlink()
        or (
            destination != previous_path
            and (destination.exists() or destination.is_symlink())
        )
    ):
        raise origin.common.InputError(
            "target", "A promotion destination already exists."
        )
    if destination != previous_path and (
        previous_path.with_suffix("").exists()
        or previous_path.with_suffix("").is_symlink()
        or any(
            row.get("status_group") == "Current"
            and origin.native_header_view(row["header_json"])
            .get("context", {})
            .get("container", {})
            .get("atom")
            == atom_id
            for row in capture.atoms
        )
    ):
        raise origin.common.InputError(
            "target", "A container cannot change status during promotion."
        )
    for parent in (archive_path.parent, destination.parent):
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise origin.common.InputError(
                "target", "A promotion destination directory is unsafe."
            )
