"""Private, read-only exact Atom source binding for lifecycle workflows."""

from __future__ import annotations


import hashlib as hashlib
import os as os
from pathlib import Path
import re
from typing import Annotated, Any

from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view as carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    ProjectSelection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.units__shared import (
    read_scope_unit_declarations as read_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from ...ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext,
    open_regular as open_regular,
)
from .placement.placement_model import (
    active_placement as active_placement,
    preserve_mapping,
)
from . import source_context_select as _context
from . import source_inventory as _inventory
from . import source_candidates as _candidates
from . import source_select as _select
from .source_binding import (
    ArchiveNotLoadedError as ArchiveNotLoadedError,
    SourceSelectionError,
    bind_query_reader as bind_query_reader,
    query_reader,
)


_Metadata = Annotated[dict[str, Any], WrapValidator(preserve_mapping)]


def query_candidates(selection, **filters):
    """Select indexed carriers without walking Atom directories."""
    reader = query_reader()
    rows = reader.lifecycle_candidates(selection, **filters)
    found = {}
    for atom_id, path in rows:
        path = Path(path)
        if (
            not path.is_absolute()
            or ".." in path.parts
            or not path.is_relative_to(selection.root)
        ):
            raise SourceSelectionError(
                "Indexed Atom path is outside the selected Project"
            )
        found.setdefault(atom_id, set()).add(path)
    return {atom_id: tuple(sorted(paths)) for atom_id, paths in found.items()}


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class SourcePin:
    path: Path
    atom_id: str
    ref_id: str
    version: int
    status: str
    sha256: str
    raw: bytes
    metadata: _Metadata


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class SourceContext:
    path: Path
    atom_id: str
    ref_id: str
    version: int
    status: str
    metadata: _Metadata
    summary: str | None


def _context_candidate(selection, ref_id, atom_id, row):
    return _context._context_candidate(selection, ref_id, atom_id, row)


def select_context(
    selection: ProjectSelection,
    ref_id: str,
    *,
    expected_version: int | None = None,
) -> SourceContext:
    """Select Current Atom context without reading its Carrier."""
    return _context.select_context(
        selection, ref_id, expected_version=expected_version
    )


def _candidate_paths(
    reader: ReadContext,
    selection: ProjectSelection,
    atom_id: str,
    *,
    references: tuple[str, ...] = (),
) -> tuple[Path, ...]:
    """Discover this identity without following links."""
    return _inventory._candidate_paths(
        reader, selection, atom_id, references=references
    )


def _matching_paths(
    reader: ReadContext, selection: ProjectSelection, prefix: re.Pattern[str]
) -> tuple[Path, ...]:
    return _inventory._matching_paths(reader, selection, prefix)


def _inventory_paths(
    reader: ReadContext, selection: ProjectSelection, classify
) -> dict[Any, tuple[Path, ...]]:
    return _inventory._inventory_paths(reader, selection, classify)


def _selector(
    selection: ProjectSelection, ref_id: str, expected_version: int | None
) -> tuple[str, str | None, str | None]:
    return _candidates._selector(selection, ref_id, expected_version)


def _carrier_revision(path: Path, atom_id: str) -> tuple[str | None, bool]:
    return _candidates._carrier_revision(path, atom_id)


def _matches_revision(
    path: Path, atom_id: str, qualified: str | None, draft: str | None
) -> bool:
    return _candidates._matches_revision(path, atom_id, qualified, draft)


def _read_candidate(
    reader: ReadContext,
    path: Path,
    ref_id: str,
    atom_id: str,
    qualified: str | None,
    draft: str | None,
    *,
    retained_history: bool = False,
) -> SourcePin | None:
    return _candidates._read_candidate(
        reader,
        path,
        ref_id,
        atom_id,
        qualified,
        draft,
        retained_history=retained_history,
    )


def _check_currentness(
    reader: ReadContext,
    selection: ProjectSelection,
    atom_id: str,
    candidates: tuple[Path, ...],
) -> None:
    return _candidates._check_currentness(
        reader, selection, atom_id, candidates
    )


def _check_declarations(reader, selection):
    return _candidates._check_declarations(reader, selection)


def _unique_candidate(
    reader, paths, ref_id, atom_id, qualified, draft, *, retained_history=False
):
    return _candidates._unique_candidate(
        reader,
        paths,
        ref_id,
        atom_id,
        qualified,
        draft,
        retained_history=retained_history,
    )


def select_source(
    selection: ProjectSelection,
    ref_id: str,
    *,
    expected_version: int | None = None,
) -> SourcePin:
    """Bind a Current, Archived, or Draft Atom in the Project tree.

    A qualified ID selects Archived, or Draft with the ``-draft`` suffix.
    An optional expected version pins the read.
    """
    return _select.select_source(
        selection, ref_id, expected_version=expected_version
    )


def select_current_sources(
    selection: ProjectSelection, ref_ids: list[str]
) -> dict[str, SourcePin]:
    "Bind Current sources together with one shared inventory and recheck."
    return _select.select_current_sources(selection, ref_ids)


def select_sources(
    selection: ProjectSelection, ref_ids: list[str]
) -> dict[str, SourcePin]:
    "Bind several exact revisions with one source inventory and recheck."
    return _select.select_sources(selection, ref_ids)
