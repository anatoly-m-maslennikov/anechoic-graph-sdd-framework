"""Resolve native Draft source paths and revision bytes."""

from datetime import datetime as datetime, timezone as timezone
from hashlib import sha256 as sha256
import json as json
from pathlib import Path
import re
from types import SimpleNamespace as SimpleNamespace

import yaml as yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    active_spec_directories,
    native_carrier_path,
    spec_lens_directories,
    project_goal_filename,
    DRAFT_DIRECTORY,
    ARCHIVE_DIRECTORY,
    READY_DIRECTORY as READY_DIRECTORY,
    TICKET_DIRECTORY,
    PROJECT_CONFIG_DIRECTORY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    read_structure as read_structure,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext as ReadContext,
)

from ... import common
from .native_draft_source_details import (
    _task_revision_root,
    _spec_revision_root,
    _state_bytes as _state_bytes,
)
from ..native_draft_guards import _check_owner as _check_owner
from ..native_draft_guards import _summary


def _admitted_current(selection, row):
    relative = row.get("source_path")
    if not isinstance(relative, str):
        raise common.SourceChanged("Current carrier path is invalid.")
    relative = Path(relative)
    path = selection.root / relative
    root_goal = path.parent == selection.root and project_goal_filename(
        path.name
    )
    if (
        not selection.root.is_absolute()
        or not selection.control_root.is_relative_to(selection.root)
        or selection.manifest_path.parent
        not in {selection.root, selection.control_root}
        or relative.is_absolute()
        or ".." in relative.parts
        or (not root_goal and not path.is_relative_to(selection.control_root))
        or path == selection.manifest_path
    ):
        raise common.InputError(
            "sourceCurrent", "Select an admitted Current carrier."
        )
    atom_id = row.get("id", "")
    header = native_header_view(row.get("header_json"))
    context = header.get("context") if isinstance(header, dict) else None
    if not isinstance(context, dict):
        raise common.InputError(
            "sourceCurrent", "Current carrier context is invalid."
        )
    status = row.get("status")
    return path, root_goal, atom_id, header, context, status


def _revision_root(selection, row, structure_snapshot=None, current_rows=None):
    """Validate a Current carrier and return its owning revision directory."""
    path, root_goal, atom_id, header, context, status = _admitted_current(
        selection, row
    )
    if "-T-" in atom_id:
        return _task_revision_root(
            selection, row, current_rows, path, atom_id, context, status
        )
    if status not in {"active", "ready"} or not re.fullmatch(
        re.escape(atom_id) + r"-.+\.md", path.name
    ):
        raise common.InputError(
            "sourceCurrent", "Select an active native carrier."
        )
    if root_goal:
        if (
            status != "active"
            or context.get("template") != "project_goal"
            or context.get("lens") != "SPEC"
            or context.get("tier") != -1
            or context.get("container") != {"component": "C00"}
        ):
            raise common.InputError(
                "sourceCurrent",
                "Select an Active Project Goal at the repository root.",
            )
        return selection.control_root
    if "-P-" in atom_id or "-C-" in atom_id:
        return _project_config_root(selection, path)
    return _spec_revision_root(
        selection, structure_snapshot, path, header, context, status
    )


def _project_config_root(selection, path):
    root = next(
        (
            selection.control_root / name
            for name in (
                PROJECT_CONFIG_DIRECTORY,
                "002_PROJECT_CONFIG",
                "_PMETA",
            )
            if path.is_relative_to(selection.control_root / name)
        ),
        selection.control_root / PROJECT_CONFIG_DIRECTORY,
    )
    if path.parent != root:
        raise common.InputError(
            "sourceCurrent", "Select a direct PROJECT_CONFIG carrier."
        )
    return root


def _spec_lens_owner(root, tier, lens, status, parameters):
    directories = (
        ()
        if status == "ready"
        else active_spec_directories(
            tier, spec_lens_directories(lens), parameters=parameters
        )
    )
    candidates = [directories]
    if status != "ready":
        candidates.append(
            ()
            if lens.upper() == "SPEC"
            else tuple("__" + part.upper() for part in lens.split("/"))
        )
        if tier in {-1, 0, 1, 2}:
            candidates.append(())
    for candidate in candidates:
        if not candidate:
            return root
        if (
            len(root.parts) >= len(candidate)
            and tuple(part.upper() for part in root.parts[-len(candidate) :])
            == candidate
        ):
            return root.parents[len(candidate) - 1]
    raise ValueError("Lens path disagrees")


def _revision_header(header):
    result = {key: value for key, value in header.items() if key != "state"}
    if result.get("atom_family") == "PMETA":
        result["atom_family"] = "PROJECT_CONFIG"
    return result


def _task_path(selection, header, body, status, version, owner, root=None):
    projected = {
        **header,
        "state": {**header["state"], "status": status, "version": version},
    }
    try:
        owner_directory, owner_template = owner
        path = native_carrier_path(
            projected,
            _summary(body),
            project_root=selection.control_root,
            owner_directory=owner_directory,
            owner_template=owner_template,
        )
        flat_root = (
            root
            if root
            in {
                selection.control_root / name / "TASKS"
                for name in ("__TKT", "001_TICKETS", TICKET_DIRECTORY)
            }
            else selection.control_root / TICKET_DIRECTORY / "TASKS"
        )
        if root == flat_root:
            directory = (
                DRAFT_DIRECTORY
                if status == "draft"
                else ARCHIVE_DIRECTORY
                if status == "archived"
                else ""
                if status in {"active", "in_queue"}
                else status
            )
            return flat_root / directory / path.name
        return path
    except ValueError as error:
        raise common.InputError(
            "summary", "Task Header or Summary cannot be projected to a path."
        ) from error
