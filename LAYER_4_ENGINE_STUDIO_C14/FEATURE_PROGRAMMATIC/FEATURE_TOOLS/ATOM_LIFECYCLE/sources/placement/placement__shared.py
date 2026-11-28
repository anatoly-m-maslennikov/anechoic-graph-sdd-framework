"""Private derivation of a single admitted Atom's Markdown Carrier path.

The caller supplies admitted properties and a verified containing Carrier;
this module does not select a Status, admit containment, or perform effects.
CA-D-651 leaves nonzero numeric Tier tokens to other registered grammar;
this helper implements the ordinary grammar that omits them. External Project
Goal and Scope Unit Declaration grammars are not implemented here (CA-D-651).
"""

from __future__ import annotations


from pathlib import Path
import re

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view as carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    PlacementError,
    admitted_parent,
    derive_filename as derive_filename,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    ProjectSelection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.units__shared import (
    read_scope_unit_declarations,
)

from ._placement_paths import (
    _derive_bound,
    _archive_destination as _archive_destination,
    _predecessor_status as _predecessor_status,
)
from ...common import InputError, logical_container
from ...carriers.carrier__shared import logical_view
from .placement_model import active_placement
from ..source__shared import query_reader, select_context, select_source


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ContainerCarrier:
    path: Path
    status: str

    def __fspath__(self):
        return str(self.path)


def _inside(path: Path, root: Path) -> Path:
    if (
        not path.is_absolute()
        or ".." in path.parts
        or not path.is_relative_to(root)
    ):
        raise PlacementError("Carrier context is outside the selected Project")
    if path.resolve(strict=False) != path:
        raise PlacementError("Carrier context traverses a symlink")
    return path


def resolve_container(
    selection, view, atom_id, seen=frozenset(), *, model=None
):
    if atom_id in seen or len(seen) >= 32:
        raise InputError(
            "container", "Containing Atom chain is cyclic or too deep."
        )
    container = logical_container({}, view)
    if "scope_unit" in container:
        return container["scope_unit"], None
    ref = container["atom"]
    if "@" in ref:
        raise InputError(
            "container", "Containing Atom must use a Current reference."
        )
    parent = (
        select_context(selection, ref)
        if query_reader() is not None
        else select_source(selection, ref)
    )
    parent_view = logical_view(parent.metadata, model)
    role, form = view.get("role"), view.get("form")
    if not admitted_parent(role, form, parent_view, parent.status):
        raise InputError(
            "container", "Containing Atom Role or Form is unsupported."
        )
    scope, grandparent = resolve_container(
        selection, parent_view, parent.atom_id, seen | {atom_id}, model=model
    )
    return scope, _container_directory(
        selection, role, parent, scope, grandparent
    )


def _container_directory(selection, role, parent, scope, grandparent):
    expected = expected_status_directory(
        selection, role, parent.status, scope, grandparent
    )
    if parent.path.parent != expected:
        raise InputError(
            "container",
            "Containing Atom location disagrees with its declaration.",
        )
    directory = parent.path.with_suffix("")
    shared_backlog = (
        role == "Plan"
        and active_placement().placement("Plan", "Backlog")[0] == "role"
    )
    if directory.resolve(strict=False) != directory or (
        not directory.is_dir()
        and not (shared_backlog and not directory.exists())
    ):
        raise InputError(
            "container", "Containing Atom directory is missing or unsafe."
        )
    return (
        ContainerCarrier(directory, parent.status)
        if role == "Plan"
        else directory
    )


def _role_root(selection, role, scope_unit):
    reader = query_reader()
    if reader is None:
        selection._revalidate_boundary()
    declarations = (
        reader.lifecycle_declarations()
        if reader is not None
        else read_scope_unit_declarations(
            selection.root, selection.control_relative
        )
    )
    if declarations.digest != selection.declaration_digest:
        raise PlacementError("Project declarations are stale")
    prefix = selection.settings["artifacts"]["identity"]["project_prefix"]
    rows = [
        row
        for row in selection.structure["scope_units"]
        if scope_unit is not None
        and (
            scope_unit in (row["scope_unit_name"], row["scope_unit_id"])
            or (row["parent"] == "PROJECT" and scope_unit == f"{prefix}-SU-00")
        )
    ]
    if len(rows) != 1:
        raise PlacementError("Scope Unit is missing or ambiguous")
    authority = _inside(
        selection.root / rows[0]["authority_path"], selection.root
    )
    role_root = _inside(
        authority / active_placement().role_folder(role), selection.root
    )
    return rows[0], role_root


def _scope_binding(selection, atom_id, version, role, scope_unit, parent):
    prefix = selection.settings["artifacts"]["identity"]["project_prefix"]
    if not isinstance(atom_id, str) or not re.fullmatch(
        re.escape(prefix) + r"-[A-Z]-[0-9]+", atom_id
    ):
        raise PlacementError("Invalid canonical Atom ID")
    if type(version) is not int or version < 1:
        raise PlacementError("Invalid Version or unsupported Role")
    row, role_root = _role_root(selection, role, scope_unit)
    if parent is not None:
        if role not in ("Plan", "Operations"):
            raise PlacementError("Unsupported containing Carrier")
        parent_path = _inside(Path(parent), role_root)
        shared_backlog = (
            role == "Plan"
            and isinstance(parent, ContainerCarrier)
            and active_placement().placement("Plan", "Backlog")[0] == "role"
        )
        if parent_path == role_root or (
            not parent_path.is_dir()
            and not (shared_backlog and not parent_path.exists())
        ):
            raise PlacementError(
                "Containing Carrier must be an existing directory"
            )
        parent = (
            ContainerCarrier(parent_path, parent.status)
            if isinstance(parent, ContainerCarrier)
            else parent_path
        )
    return row, role_root, parent


def _status_directory(role_root, role, status, parent):
    base, folder = active_placement().placement(role, status)
    if (
        role == "Plan"
        and status.casefold() == "backlog"
        and base == "role"
        and isinstance(parent, ContainerCarrier)
        and parent.status.casefold() == "backlog"
    ):
        return parent.path
    return (
        role_root
        if base == "role"
        else Path(parent)
        if parent is not None
        else role_root
    ) / folder


def shared_plan_backlog_directory(selection, scope):
    _, role_root = _role_root(selection, "Plan", scope)
    base, folder = active_placement().placement("Plan", "Backlog")
    return (
        _inside(role_root / folder, selection.root) if base == "role" else None
    )


def expected_status_directory(selection, role, status, scope, parent):
    _, role_root = _role_root(selection, role, scope)
    if parent is not None:
        _inside(Path(parent), role_root)
    return _inside(
        _status_directory(role_root, role, status, parent), selection.root
    )


def archived_owner(selection, path, role):
    "Locate an exact Archived revision in a declared Scope Unit's Role area."
    placement = active_placement()
    role_dir = placement.role_folder(role)
    base, _ = placement.placement(role, "Archived")
    if base != "role":
        raise InputError("target", "Archived placement is not Role-owned.")
    for row in selection.structure["scope_units"]:
        directory = selection.root / row["authority_path"] / role_dir
        if path.parent in {
            directory / folder for folder in placement.archive_folders(role)
        }:
            return row["scope_unit_name"]
    raise InputError(
        "target", "Archived Atom is outside a shared Role archive."
    )


def derive_destination(
    selection: ProjectSelection,
    *,
    atom_id: str,
    version: int,
    status: str | None,
    role: str,
    summary: str,
    scope_unit: str,
    form: str | None = None,
    label: str | None = None,
    tier: int | None = None,
    target_scope: str | None = None,
    parent: Path | None = None,
    source_path: Path | None = None,
    work_sequence: int | None = None,
    archived_update: bool = False,
) -> Path:
    """Derive a path; parent is an already verified local container.

    source_path is required for archival and preserves the exact predecessor's
    filename components. For Plan, parent identifies the declared immediate
    containing Plan's directory. For Operations, it identifies an admitted
    Workflow/Step grouping directory. Other parent groupings are unsupported.
    """
    if not isinstance(selection, ProjectSelection):
        raise PlacementError("Project selection is required")
    try:
        identity = atom_id, version, status, role, summary, scope_unit
        options = (
            form,
            label,
            tier,
            target_scope,
            parent,
            source_path,
            work_sequence,
            archived_update,
        )
        return _derive_bound(selection, identity, options)
    except PlacementError:
        raise
    except (KeyError, TypeError, ValueError, OSError) as error:
        raise PlacementError(
            "Cannot derive placement from the selected Project"
        ) from error
