"""Bind and run trusted Workflow definitions within one selected native Project."""
from __future__ import annotations

import base64
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from native_project_selection import NativeProjectSelection
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


@dataclass(frozen=True)
class NativeDefinitionPin:
    ref_id: str
    relative_path: str
    sha256: str


class NativeWorkflowDefinitionError(ValueError):
    """An admitted native definition or its Project binding cannot be verified."""


def _pin_path(selection: NativeProjectSelection, pin: NativeDefinitionPin) -> Path:
    relative = Path(pin.relative_path)
    atom_id = pin.ref_id.partition("@")[0]
    exact = rf"{re.escape(selection.project_prefix)}-P-[0-9]+@[1-9][0-9]*"
    if (re.fullmatch(exact, pin.ref_id) is None
            or relative.as_posix() != pin.relative_path
            or relative.parent != selection.control_relative / "_PMETA"
            or relative.suffix != ".md" or not relative.name.startswith(f"{atom_id}-")):
        raise NativeWorkflowDefinitionError(f"Invalid native PMETA pin: {pin.ref_id}")
    return selection.root / relative


def _pinned_bytes(reader: ReadContext, path: Path, ref_id: str, digest: str) -> bytes:
    try:
        raw = reader.read(path)
    except (OSError, RuntimeError, ValueError) as error:
        raise NativeWorkflowDefinitionError(f"Pinned native source {ref_id} is unavailable") from error
    if reader.fingerprints[str(path)] != digest:
        raise NativeWorkflowDefinitionError(f"Pinned native source {ref_id} changed")
    return raw


def _check_header(path: Path, raw: bytes, kind: str, ref_id: str) -> None:
    try:
        header = parse_carrier(raw, path).metadata
    except ValueError as error:
        raise NativeWorkflowDefinitionError(f"Unreadable native {kind} definition {ref_id}") from error
    identity, context, state = (header.get(key) for key in ("identity", "context", "state"))
    if (not all(isinstance(group, dict) for group in (identity, context, state))
            or type(state.get("version")) is not int
            or f'{identity.get("atom_id")}@{state["version"]}' != ref_id
            or state.get("status") != "active" or context.get("template") != kind):
        raise NativeWorkflowDefinitionError(f"Expected active native {kind} definition {ref_id}")


def bind_native_workflow(
    selection: NativeProjectSelection, *, workflow: NativeDefinitionPin,
    steps: tuple[NativeDefinitionPin, ...], actions: tuple[NativeDefinitionPin, ...],
) -> Callable[[], None]:
    """Verify a trusted binding once and return a check for use before every dispatch."""
    pins = (("workflow", workflow), *(('step', pin) for pin in steps),
            *(('action', pin) for pin in actions))
    sources = tuple((kind, pin, _pin_path(selection, pin)) for kind, pin in pins)
    if len({pin.ref_id.partition("@")[0] for _, pin, _ in sources}) != len(sources):
        raise NativeWorkflowDefinitionError("Duplicate native definition identities in Workflow binding")

    def check(*, validate_headers: bool = False) -> None:
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        _pinned_bytes(reader, selection.manifest_path, selection.manifest_ref, selection.manifest_sha256)
        for kind, pin, path in sources:
            raw = _pinned_bytes(reader, path, pin.ref_id, pin.sha256)
            if validate_headers:
                _check_header(path, raw, kind, pin.ref_id)
        if reader.currentness()["state"] != "unchanged":
            raise NativeWorkflowDefinitionError("Native Workflow sources changed during verification")

    check(validate_headers=True)
    return check


def bind_native_status_workflow(
    selection: NativeProjectSelection, *, migration_refs: Iterable[tuple[str | None, str, str]],
    current_rows: Iterable[Mapping[str, object]],
) -> tuple[Callable[[], None], dict[str, str]]:
    """Bind the installed status Workflow to explicitly migrated Current native carriers."""
    from ATOM_LIFECYCLE import status_workflow_definition as installed
    from ATOM_LIFECYCLE.assets.change_current_status import SOURCE_SHA256, WORKFLOW_BINDING

    expected = {"workflow": "CA-O-10011@4", "step": "CA-O-10010@1", "action": "CA-O-10007@1"}
    if WORKFLOW_BINDING != expected or set(SOURCE_SHA256) != set(expected.values()):
        raise NativeWorkflowDefinitionError("Installed status Workflow binding is invalid")
    try:
        asset_reader = ReadContext(roots=[str(installed._CODE_ROOT)], limits=dict(CEILINGS))
        asset = asset_reader.read(installed.ASSET)
        snapshot = asset_reader.read(installed.SNAPSHOT)
        encoded = json.loads(snapshot)
        if not isinstance(encoded, dict) or set(encoded) != set(expected.values()) or installed._snapshot_bytes(encoded) != snapshot:
            raise ValueError("Invalid snapshot")
        sources = {ref: base64.b64decode(value, validate=True) for ref, value in encoded.items()}
        if any(sha256(sources[ref]).hexdigest() != SOURCE_SHA256[ref] for ref in expected.values()):
            raise ValueError("Snapshot digest differs")
        header = '# Generated from the admitted Workflow Formal Claim.\n\n'
        header += f'WORKFLOW_BINDING = {expected!r}\nSOURCE_SHA256 = {{\n'
        header += ''.join(f'    {ref!r}: {SOURCE_SHA256[ref]!r},\n' for ref in expected.values())
        generated = (header + '}\n\n\n').encode() + installed._claim_code(sources[expected['workflow']], expected)
        if asset != generated or asset_reader.currentness()["state"] != "unchanged":
            raise ValueError("Installed Workflow asset differs")
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        raise NativeWorkflowDefinitionError("Installed status Workflow assets are invalid") from error

    refs, rows = tuple(migration_refs), tuple(current_rows)
    reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
    _pinned_bytes(reader, selection.manifest_path, selection.manifest_ref, selection.manifest_sha256)
    pins, mapping = [], {}
    for kind, atom_id, version, source_path in installed.SOURCES:
        legacy = f"{atom_id}@{version}"
        matches = [(old, path, target) for old, path, target in refs if old == legacy]
        original = (installed.CHECKOUT_MODEL / source_path).as_posix()
        if len(matches) != 1 or matches[0][1] != original:
            raise NativeWorkflowDefinitionError(f"Missing or ambiguous migration for {legacy}")
        native = matches[0][2]
        if not isinstance(native, str) or re.fullmatch(rf"{re.escape(selection.project_prefix)}-P-[0-9]+@[1-9][0-9]*", native) is None:
            raise NativeWorkflowDefinitionError(f"Invalid native migration target for {legacy}")
        selected = [row for row in rows if row.get('_exact_ref') == native and row.get('status_group') == 'Current']
        if len(selected) != 1:
            raise NativeWorkflowDefinitionError(f"Missing or ambiguous native carrier for {legacy}")
        row = selected[0]
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if not isinstance(relative, str) or not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
            raise NativeWorkflowDefinitionError(f"Invalid native carrier for {legacy}")
        full_path = _pin_path(selection, NativeDefinitionPin(native, relative, digest))
        raw = _pinned_bytes(reader, full_path, native, digest)
        _check_header(full_path, raw, kind, native)
        old_body = sources[legacy].partition(b'\n---\n')
        native_body = raw.partition(b'\n---\n')
        if not old_body[1] or not native_body[1] or old_body[2] != native_body[2]:
            raise NativeWorkflowDefinitionError(f"Native source body differs for {legacy}")
        pins.append((full_path, native, digest))
        mapping[legacy] = native
    if len(set(mapping.values())) != len(mapping) or reader.currentness()["state"] != "unchanged":
        raise NativeWorkflowDefinitionError("Native status Workflow sources changed or overlap")

    def check() -> None:
        current = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        _pinned_bytes(current, selection.manifest_path, selection.manifest_ref, selection.manifest_sha256)
        for path, ref, digest in pins:
            _pinned_bytes(current, path, ref, digest)
        if current.currentness()["state"] != "unchanged":
            raise NativeWorkflowDefinitionError("Native status Workflow sources changed during verification")

    return check, mapping


def run_native_status_workflow(selection, params, *, migration_refs, current_rows):
    from ATOM_LIFECYCLE.assets.change_current_status import WORKFLOW_BINDING, change_current_status
    from ATOM_LIFECYCLE.common import InputError
    from ATOM_LIFECYCLE.native_update import _select_ticket, change_ticket_status
    from ATOM_LIFECYCLE.status_cascade import StatusAtom, StatusInvocation, StatusTree

    if set(params) != {'target', 'targetStatus'} or not isinstance(params['targetStatus'], str):
        raise InputError('targetStatus', 'Supply one Current Ticket and target Status.')
    target = params['target']
    selected, _, path = _select_ticket(selection, target, current_rows)
    check, mapping = bind_native_status_workflow(
        selection, migration_refs=migration_refs, current_rows=current_rows,
    )
    atom = StatusAtom(target['ref_id'], selected['status'])
    invocation = StatusInvocation(atom.atom_id, target['version'], params['targetStatus'])

    class LeafStatusRun:
        outcome = None

        def read_status_tree(self):
            is_task = path.is_relative_to(selection.control_root / '__TKT' / 'TASKS')
            return StatusTree(atom, (atom,), is_task, False)

        def preflight(self, *, actions, parent_first, entering_backlog, reopening):
            if actions != [(atom.atom_id, invocation.target_status)]:
                raise ValueError('Native Status Workflow must select the pinned Ticket.')

        def invoke(self, *, step, action, atom_id, target_status):
            if (self.outcome is not None or (step, action) != (WORKFLOW_BINDING['step'], WORKFLOW_BINDING['action'])
                    or (atom_id, target_status) != (atom.atom_id, invocation.target_status)):
                raise ValueError('Native Status Workflow dispatch disagrees with its admitted binding.')
            self.outcome = change_ticket_status(selection, params, current_rows=current_rows, check_definition=check)
            return not self.outcome['errors']

    run = LeafStatusRun()
    change_current_status(invocation=invocation, engine=run)
    if run.outcome is None:
        raise ValueError('Native Status Workflow returned without dispatching its Action.')
    return run.outcome | {'workflow_binding': {kind: mapping[ref] for kind, ref in WORKFLOW_BINDING.items()}}
