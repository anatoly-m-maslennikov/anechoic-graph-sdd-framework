"""Plan and archive explicit replacement targets under the promotion lock."""

from hashlib import sha256
import re as re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    ARCHIVE_DIRECTORY as ARCHIVE_DIRECTORY,
    CUSTOM_MODEL_DIRECTORY as CUSTOM_MODEL_DIRECTORY,
    PROJECT_CONFIG_DIRECTORY,
    native_carrier_path,
    native_header_view as native_header_view,
)
from ....ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds as frontmatter_bounds,
    parse_carrier as parse_carrier,
)
from ... import common, effects
from . import native_replacement_plan__shared as _plan
from ...drafts.native_draft_guards import _check_owner as _check_owner, _summary
from ...drafts.sources.native_draft_source__shared import (
    _revision_root as _revision_root,
    _state_bytes as _state_bytes,
    _task_path as _task_path,
)
from ...sources.source__shared import bind_query_reader


def _replacement_targets(row):
    relations = row["header_json"].get("relations", {})
    return (
        relations.get("IS_REPLACEMENT_FOR", ())
        if isinstance(relations, dict)
        else ()
    )


def _check_replacement_activation(activating, rows, archived=()):
    activating_ids = {row["id"] for row in activating}
    active = [
        row
        for row in rows
        if row["status_group"] == "Current"
        and row["status"] == "active"
        and row["id"] not in activating_ids
        and row["id"] not in archived
    ]
    active.extend(activating)
    active_ids = {row["id"] for row in active}
    for row in active:
        targets = _replacement_targets(row)
        if isinstance(targets, list):
            for target in targets:
                if (
                    isinstance(target, str)
                    and target != row["id"]
                    and target in active_ids
                    and (
                        row["id"] in activating_ids or target in activating_ids
                    )
                ):
                    raise common.InputError(
                        "targetStatus",
                        f"Replacement-linked Atoms {row['id']} and "
                        f"{target} cannot both be Active.",
                    )


def _plan_replacements(
    selection, draft, current_rows, structure_snapshot, capture, previous=None
):
    return _plan._plan_replacements(
        selection, draft, current_rows, structure_snapshot, capture, previous
    )


def _plan_replacement(
    selection,
    draft,
    current_rows,
    structure_snapshot,
    capture,
    adopted,
    atom_id,
):
    return _plan._plan_replacement(
        selection,
        draft,
        current_rows,
        structure_snapshot,
        capture,
        adopted,
        atom_id,
    )


def _check_custom_path(selection, header, context, body, root, path):
    projected = native_carrier_path(
        header,
        _summary(body),
        project_root=selection.control_root,
        owner_directory=None,
    )
    if context.get("template") != "model_manifest":
        config_root = selection.control_root / PROJECT_CONFIG_DIRECTORY
        projected = root / projected.relative_to(config_root)
    if path != projected:
        raise ValueError("Custom Model path disagrees")


def _replacement_row(atom_id, capture, current_rows, adopted):
    rows = [row for row in capture.atoms if row.get("id") == atom_id]
    selected = [
        row
        for row in current_rows
        if row.get("id") == atom_id
        and row.get("status_group") in {"Current", "Archived"}
    ]
    if [
        row
        for row in rows
        if row.get("status_group") in {"Current", "Archived"}
    ] != selected:
        raise common.SourceChanged(
            "Replacement target changed after selection."
        )
    current = [row for row in rows if row.get("status_group") == "Current"]
    if (
        len(current) > 1
        or not current
        and not any(row.get("status_group") == "Archived" for row in rows)
    ):
        raise common.SourceChanged(
            "Replacement target is missing or ambiguous."
        )
    if not current and atom_id in adopted:
        return None
    if not current or current[0].get("status") not in {"ready", "active"}:
        raise common.InputError(
            "target",
            f"Replacement predecessor {atom_id} must be "
            "Current Ready or Active.",
        )
    return current[0]


def _archive_replacements(selection, plans, draft):
    recorded = []
    with bind_query_reader(None):
        for row, path, archive_path, archived in plans:
            try:
                reader = ReadContext(
                    roots=[str(selection.root)], limits=dict(CEILINGS)
                )
                draft_path = selection.root / draft["source_path"]
                if (
                    sha256(reader.read(draft_path)).hexdigest()
                    != draft["_source_sha256"]
                    or sha256(reader.read(selection.manifest_path)).hexdigest()
                    != selection.manifest_sha256
                    or sha256(reader.read(path)).hexdigest()
                    != row["_source_sha256"]
                    or reader.currentness()["state"] != "unchanged"
                ):
                    raise ValueError("Source changed")
            except OSError, RuntimeError, ValueError:
                return common.result(
                    effects=recorded,
                    errors=[
                        {
                            "code": "source_changed",
                            "message": (
                                "Draft, Manifest or replacement "
                                "target changed."
                            ),
                        }
                    ],
                )
            written = common.write_destination(
                selection.root, archive_path, archived
            )
            recorded.extend(written.effects)
            if written.errors:
                return common.result(effects=recorded, errors=written.errors)
            removed = effects.remove(
                selection.root, path, row["_source_sha256"]
            )
            recorded.extend(removed.effects)
            if removed.errors:
                return common.result(effects=recorded, errors=removed.errors)
    return common.result(effects=recorded)
