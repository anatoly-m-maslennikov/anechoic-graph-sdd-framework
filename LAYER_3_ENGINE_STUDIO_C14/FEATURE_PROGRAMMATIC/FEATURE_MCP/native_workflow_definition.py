"""Check trusted Workflow definition pins within one selected native Project."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
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
