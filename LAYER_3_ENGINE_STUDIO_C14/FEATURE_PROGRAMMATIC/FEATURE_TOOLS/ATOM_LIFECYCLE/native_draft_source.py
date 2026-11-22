"""Resolve native Draft source paths and revision bytes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from types import SimpleNamespace

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import (native_carrier_path, spec_lens_directories,
    DRAFT_DIRECTORY, ARCHIVE_DIRECTORY, READY_DIRECTORY, TICKET_DIRECTORY, PROJECT_CONFIG_DIRECTORY, project_goal_filename)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure_snapshot__pub import read_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS, ReadContext

from . import common
from .native_draft_guards import _check_owner, _summary


def _revision_root(selection, row, structure_snapshot=None, current_rows=None):
    """Validate a Current carrier and return its owning revision directory."""
    relative = row.get("source_path")
    if not isinstance(relative, str):
        raise common.SourceChanged("Current carrier path is invalid.")
    relative = Path(relative)
    path = selection.root / relative
    root_goal = path.parent == selection.root and project_goal_filename(path.name)
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or selection.manifest_path.parent not in {selection.root, selection.control_root}
            or relative.is_absolute() or ".." in relative.parts or (not root_goal and not path.is_relative_to(selection.control_root))
            or path == selection.manifest_path):
        raise common.InputError("sourceCurrent", "Select an admitted Current carrier.")
    atom_id = row.get("id", "")
    header = native_header_view(row.get("header_json"))
    context = header.get("context") if isinstance(header, dict) else None
    if not isinstance(context, dict):
        raise common.InputError("sourceCurrent", "Current carrier context is invalid.")
    status = row.get("status")
    if "-T-" in atom_id:
        return _task_revision_root(selection, row, current_rows, path, atom_id, context, status)
    if status not in {"active", "ready"} or not re.fullmatch(re.escape(atom_id) + r"-.+\.md", path.name):
        raise common.InputError("sourceCurrent", "Select an active native carrier.")
    if root_goal:
        if (status != "active" or context.get("template") != "project_goal" or context.get("lens") != "SPEC"
                or context.get("tier") != -1 or context.get("container") != {"component": "C00"}):
            raise common.InputError("sourceCurrent", "Select an Active Project Goal at the repository root.")
        return selection.control_root
    if "-P-" in atom_id or "-C-" in atom_id:
        root = selection.control_root / ('_PMETA' if '_PMETA' in path.parts else PROJECT_CONFIG_DIRECTORY)
        if path.parent != root:
            raise common.InputError("sourceCurrent", "Select a direct PROJECT_CONFIG carrier.")
        return root
    return _spec_revision_root(selection, structure_snapshot, path, header, context, status)


def _task_revision_root(selection, row, current_rows, path, atom_id, context, status):
    if current_rows is None:
        raise common.SourceChanged('Current owner capture is unavailable.')
    capture = SimpleNamespace(atoms=current_rows)
    owner_directory, _ = _check_owner(selection, context.get("container"), current_rows, capture)
    flat_root = selection.control_root / ("__TKT" if "__TKT" in path.parts else TICKET_DIRECTORY) / "TASKS"
    root = owner_directory or flat_root
    if path.parent == flat_root / ("" if status in {"active", "in_queue"} else str(status)):
        root = flat_root
    directory = () if status in {"active", "in_queue"} else (status,)
    template = context.get("template")
    if (not isinstance(status, str) or status not in {"active", "in_queue", "backlog", "done", "canceled", "resolved"}
            or template not in {"task", "epic"} or not path.is_relative_to(root)
            or path.relative_to(root).parts[:-1] != directory
            or not re.fullmatch(re.escape(atom_id) + (r"-.+--.+\.md" if "atom_family" in row["header_json"]
                                                     else "-" + template.upper() + r"--.+\.md"), path.name)):
        raise common.InputError("sourceCurrent", "Select a native Task or Epic in its Current directory.")
    return root


def _spec_revision_root(selection, structure_snapshot, path, header, context, status):
    lens = context.get("lens")
    container = context.get("container")
    if not isinstance(lens, str) or not isinstance(container, dict) or set(container) != {"component"}:
        raise common.InputError("sourceCurrent", "Select a component-owned SPEC carrier.")
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_manifest__pub import manifest_inputs
    try:
        reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
        raw = reader.read(selection.manifest_path)
        if sha256(raw).hexdigest() != selection.manifest_sha256:
            raise ValueError("Manifest changed")
        _, project_component = manifest_inputs(selection.manifest_path, parse_carrier(raw, selection.manifest_path))
        root = path.parent.parent if status == 'ready' and path.parent.name == READY_DIRECTORY else path.parent
        for directory in reversed(() if status == 'ready' or (header.get('tier', context.get('tier')) in {-1, 0, 1, 2} and not path.parent.name.startswith('__')) else spec_lens_directories(lens)):
            if root.name.upper() != directory:
                raise ValueError("Lens path disagrees")
            root = root.parent
        component = container["component"]
        if (not root.is_relative_to(selection.control_root) or
                (root == selection.control_root and component != project_component) or
                (root != selection.control_root and not root.name.endswith("_" + component))):
            raise ValueError("Component path disagrees")
        if any(part.startswith("_") or not re.search(r"_C[0-9]+$", part)
               for part in root.relative_to(selection.control_root).parts):
            raise ValueError("Nested carrier path")
        snapshot_path = getattr(selection, "structure_snapshot", None)
        if (structure_snapshot is not None or snapshot_path is not None) and root != selection.control_root:
            snapshot = structure_snapshot if structure_snapshot is not None else read_structure(snapshot_path)
            declaration = selection.control_root / snapshot.component(component).source_path
            if declaration.parent != root.parent:
                raise ValueError("Component parent contradicts the current Structure")
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError, KeyError) as error:
        raise common.InputError("sourceCurrent", "SPEC carrier must be in its lens and component root.") from error
    return root


def _revision_header(header):
    result = {key: value for key, value in header.items() if key != 'state'}
    if result.get('atom_family') == 'PMETA':
        result['atom_family'] = 'PROJECT_CONFIG'
    return result


def _state_bytes(raw, bounds, path, version, body, status):
    header = raw[bounds[0]:bounds[1]].decode('utf-8')
    try:
        node = yaml.compose(header, Loader=yaml.SafeLoader)
        states = [value for key, value in node.value if key.value == 'state']
        if len(states) != 1 or not isinstance(states[0], yaml.MappingNode):
            raise ValueError('Invalid state')
        fields = states[0].value
        values = {'status': status, 'version': version}
        if any(key.value == 'updated_at' for key, _ in fields):
            values['updated_at'] = datetime.now(timezone.utc).isoformat()
        edits = []
        family = [value for key, value in node.value if key.value == 'atom_family']
        if len(family) == 1 and isinstance(family[0], yaml.ScalarNode) and family[0].value == 'PMETA':
            edits.append((family[0].start_mark.index, family[0].end_mark.index, 'PROJECT_CONFIG'))
        for name, value in values.items():
            found = [item for key, item in fields if key.value == name]
            if len(found) != 1 or not isinstance(found[0], yaml.ScalarNode):
                raise ValueError('Invalid state field')
            edits.append((found[0].start_mark.index, found[0].end_mark.index, json.dumps(value)))
        for start, end, value in sorted(edits, reverse=True):
            header = header[:start] + value + header[end:]
        candidate = raw[:bounds[0]] + header.encode('utf-8') + raw[bounds[1]:bounds[2]] + body.encode('utf-8')
        before = parse_carrier(raw, path).metadata
        after = parse_carrier(candidate, path).metadata
        expected = dict(before)
        if expected.get('atom_family') == 'PMETA':
            expected['atom_family'] = 'PROJECT_CONFIG'
        expected['state'] = {**before['state'], **values}
        if after != expected:
            raise ValueError('Unexpected header change')
        return candidate
    except (AttributeError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        raise common.InputError('sourceCurrent', 'Task needs valid scalar state fields.') from error


def _task_path(selection, header, body, status, version, owner, root=None):
    projected = {**header, 'state': {**header['state'], 'status': status, 'version': version}}
    try:
        owner_directory, owner_template = owner
        path = native_carrier_path(projected, _summary(body), project_root=selection.control_root,
                                   owner_directory=owner_directory, owner_template=owner_template)
        flat_root = root if root in {selection.control_root / '__TKT' / 'TASKS', selection.control_root / TICKET_DIRECTORY / 'TASKS'} else selection.control_root / TICKET_DIRECTORY / 'TASKS'
        if root == flat_root:
            directory = DRAFT_DIRECTORY if status == 'draft' else ARCHIVE_DIRECTORY if status == 'archived' else '' if status in {'active', 'in_queue'} else status
            return flat_root / directory / path.name
        return path
    except ValueError as error:
        raise common.InputError('summary', 'Task Header or Summary cannot be projected to a path.') from error


