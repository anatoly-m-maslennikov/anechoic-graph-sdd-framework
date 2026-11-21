"""Check workflow and status specification pins in the selected native Project."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from native_carrier_header import native_header_view
from native_carrier_placement import PROJECT_CONFIG_DIRECTORY
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
            or relative.parent not in {selection.control_relative / PROJECT_CONFIG_DIRECTORY,
                                       selection.control_relative / "_PMETA"}
            or relative.suffix != ".md" or not relative.name.startswith(f"{atom_id}-")):
        raise NativeWorkflowDefinitionError(f"Invalid native PROJECT_CONFIG pin: {pin.ref_id}")
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
        header = native_header_view(parse_carrier(raw, path).metadata)
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


STATUS_SPECIFICATIONS = {
    'workflow': ('AN-S-1928@4',
        'aa687f42ead0f4f6fe800880b31ad36167a5c40ae9d03db444a1990aea0c057d'),
    'step': ('AN-S-1834@1',
        'cf13a7f20adf79c318e0ea52dfb4466ef1bcec6f0eae4246935a31880c7ab9e2'),
    'action': ('AN-S-1831@1',
        'ff28938b3a725b2aee728e8cad99bb14f202446c0183e5ab9428d5f26c6b7448'),
}


def bind_status_specifications(
    selection: NativeProjectSelection, *, current_rows: Iterable[Mapping[str, object]],
) -> Callable[[], None]:
    """Bind the installed status operation to its exact native SPEC carriers."""
    rows = tuple(current_rows)
    reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
    _pinned_bytes(reader, selection.manifest_path, selection.manifest_ref, selection.manifest_sha256)
    pins = []
    for kind, (ref, expected_body) in STATUS_SPECIFICATIONS.items():
        atom_id = ref.partition("@")[0]
        selected = [row for row in rows if row.get("_exact_ref") == ref and row.get("status_group") == "Current"]
        if len(selected) != 1:
            raise NativeWorkflowDefinitionError(f"Missing or ambiguous native status specification {ref}")
        row = selected[0]
        relative, digest = row.get("source_path"), row.get("_source_sha256")
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise NativeWorkflowDefinitionError(f"Invalid native status specification {ref}")
        path = Path(relative)
        if (path.is_absolute() or ".." in path.parts or path.as_posix() != relative
                or not path.is_relative_to(selection.control_relative / "LAYER_1_META_ONTOLOGY_C9")
                or path.suffix != ".md" or not path.name.startswith(atom_id + "-")):
            raise NativeWorkflowDefinitionError(f"Invalid native status specification path {ref}")
        full_path = selection.root / path
        raw = _pinned_bytes(reader, full_path, ref, digest)
        _check_header(full_path, raw, kind, ref)
        _, delimiter, body = raw.partition(b"\n---\n")
        if not delimiter or sha256(body).hexdigest() != expected_body:
            raise NativeWorkflowDefinitionError(f"Native status specification body differs for {ref}")
        pins.append((full_path, ref, digest))
    if reader.currentness()["state"] != "unchanged":
        raise NativeWorkflowDefinitionError("Native status Workflow sources changed during verification")

    def check() -> None:
        current = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        _pinned_bytes(current, selection.manifest_path, selection.manifest_ref, selection.manifest_sha256)
        for path, ref, digest in pins:
            _pinned_bytes(current, path, ref, digest)
        if current.currentness()["state"] != "unchanged":
            raise NativeWorkflowDefinitionError("Native status Workflow sources changed during verification")

    return check
