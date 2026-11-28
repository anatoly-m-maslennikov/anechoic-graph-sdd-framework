"""Preflight and commit a promotion over a Current revision."""

from hashlib import sha256 as sha256
from pathlib import Path as Path
import re as re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view as native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_carrier_path as native_carrier_path,
    DRAFT_DIRECTORY as DRAFT_DIRECTORY,
    ARCHIVE_DIRECTORY as ARCHIVE_DIRECTORY,
    READY_DIRECTORY as READY_DIRECTORY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native as revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds as frontmatter_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from ....ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext as ReadContext,
)

from ....ADAPTERS_C30.carriers.concern.continuant_concern__pub import (
    CONTINUANT_LENS as CONTINUANT_LENS,
)

from ._revision_placement import _revision_placement
from ._revision_commit import (
    _commit_revision as _commit_revision,
    _rollback_promotion as _rollback_promotion,
)
from ._revision_sources import _read_revision_sources as _read_revision_sources
from ._revision_preflight import _preflight_revision
from ._revision_validation import (
    _check_promotion_destinations as _check_promotion_destinations,
    _check_revision_headers as _check_revision_headers,
)
from ... import common as common, effects as effects
from ...effects import _project_write_lock
from ..native_draft_guards import (
    _check_owner as _check_owner,
    _summary as _summary,
    is_c9_typed_manifest as is_c9_typed_manifest,
    _validate_c9_typed_manifest as _validate_c9_typed_manifest,
    _has_formal_declaration as _has_formal_declaration,
)
from ..sources.native_draft_source__shared import (
    _revision_header as _revision_header,
    _revision_root as _revision_root,
    _state_bytes as _state_bytes,
    _task_path as _task_path,
)
from ...sources.source__shared import bind_query_reader as bind_query_reader
from ...updates.replacement.native_replacement_promotion import (
    _plan_replacements,
    _archive_replacements,
    _check_replacement_activation,
)


def _promote_revision(
    selection,
    target,
    status,
    draft,
    previous,
    current_rows,
    structure_snapshot,
    previous_capture,
    validate_project_spec_model,
):
    identity, paths, root, archive_path, destination = _revision_placement(
        selection,
        target,
        status,
        draft,
        previous,
        current_rows,
        structure_snapshot,
    )
    atom_id, version = identity

    with _project_write_lock(selection.root):
        return _promote_under_lock(
            (selection, status, draft, previous),
            (
                current_rows,
                structure_snapshot,
                previous_capture,
                validate_project_spec_model,
            ),
            (root, paths, archive_path, destination, atom_id, version),
        )


def _promote_under_lock(first, second, third):
    selection, status, draft, previous = first
    (
        current_rows,
        structure_snapshot,
        previous_capture,
        validate_project_spec_model,
    ) = second
    root, paths, archive_path, destination, atom_id, version = third
    archive_path, destination, archive, promoted, capture = (
        _preflight_revision(
            selection,
            status,
            draft,
            previous,
            current_rows,
            previous_capture,
            validate_project_spec_model,
            root,
            paths,
            archive_path,
            destination,
            atom_id,
            version,
        )
    )
    return _commit_under_lock(
        first,
        second,
        third,
        (archive_path, destination, archive, promoted, capture),
    )


def _commit_under_lock(first, second, third, preflight):
    selection, status, draft, previous = first
    (
        current_rows,
        structure_snapshot,
        previous_capture,
        validate_project_spec_model,
    ) = second
    root, paths, original_archive, original_destination, atom_id, version = (
        third
    )
    archive_path, destination, archive, promoted, capture = preflight
    plans = _plan_replacements(
        selection,
        draft,
        current_rows,
        structure_snapshot,
        capture,
        previous=previous,
    )
    if status == "active":
        _check_replacement_activation(
            [draft], capture.atoms, {row["id"] for row, *_ in plans}
        )
    archived = _archive_replacements(selection, plans, draft)
    if archived["outcome"] != "completed":
        return archived
    result = _commit_revision(
        selection,
        status,
        draft,
        previous,
        paths,
        archive_path,
        destination,
        archive,
        promoted,
        atom_id,
        version,
    )
    result["effects"] = archived["effects"] + result["effects"]
    return result
