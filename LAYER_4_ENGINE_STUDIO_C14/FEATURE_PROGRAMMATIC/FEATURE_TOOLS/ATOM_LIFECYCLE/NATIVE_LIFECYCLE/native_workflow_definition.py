"Check workflow and status specification pins in the selected native Project."

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from ...ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    PROJECT_CONFIG_DIRECTORY,
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    formal_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier,
)
from ...ADAPTERS_C30.model.model_ontology_path__pub import component_path
from ._native_release_claim import _parse_release_claim
from ...PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared import NativeProjectSelection


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class NativeDefinitionPin:
    ref_id: str
    relative_path: str
    sha256: str


class NativeWorkflowDefinitionError(ValueError):
    "An admitted native definition or its Project binding cannot be verified."


def _pin_path(
    selection: NativeProjectSelection, pin: NativeDefinitionPin
) -> Path:
    relative = Path(pin.relative_path)
    atom_id = pin.ref_id.partition("@")[0]
    exact = rf"{re.escape(selection.project_prefix)}-[PC]-[0-9]+@[1-9][0-9]*"
    if (
        re.fullmatch(exact, pin.ref_id) is None
        or relative.as_posix() != pin.relative_path
        or relative.parent
        not in {
            selection.control_relative / PROJECT_CONFIG_DIRECTORY,
            selection.control_relative / "_PMETA",
        }
        or relative.suffix != ".md"
        or not relative.name.startswith(f"{atom_id}-")
    ):
        raise NativeWorkflowDefinitionError(
            f"Invalid native PROJECT_CONFIG pin: {pin.ref_id}"
        )
    return selection.root / relative


def _pinned_bytes(
    reader: ReadContext,
    path: Path,
    ref_id: str,
    digest: str,
    *,
    metadata_guard=False,
) -> bytes:
    try:
        raw = reader.read(path, metadata_guard=metadata_guard)
    except (OSError, RuntimeError, ValueError) as error:
        raise NativeWorkflowDefinitionError(
            f"Pinned native source {ref_id} is unavailable"
        ) from error
    if sha256(raw).hexdigest() != digest:
        raise NativeWorkflowDefinitionError(
            f"Pinned native source {ref_id} changed"
        )
    return raw


def _check_header(path: Path, raw: bytes, kind: str, ref_id: str) -> dict:
    try:
        header = native_header_view(parse_carrier(raw, path).metadata)
    except ValueError as error:
        raise NativeWorkflowDefinitionError(
            f"Unreadable native {kind} definition {ref_id}"
        ) from error
    identity, context, state = (
        header.get(key) for key in ("identity", "context", "state")
    )
    if (
        not all(
            isinstance(group, dict) for group in (identity, context, state)
        )
        or type(state.get("version")) is not int
        or f"{identity.get('atom_id')}@{state['version']}" != ref_id
        or state.get("status") != "active"
        or context.get("template") != kind
    ):
        raise NativeWorkflowDefinitionError(
            f"Expected active native {kind} definition {ref_id}"
        )
    return context


def bind_native_workflow(
    selection: NativeProjectSelection,
    *,
    workflow: NativeDefinitionPin,
    steps: tuple[NativeDefinitionPin, ...],
    actions: tuple[NativeDefinitionPin, ...],
) -> Callable[[], None]:
    "Verify a trusted binding once and return a check for use before every dispatch."
    pins = (
        ("workflow", workflow),
        *(("step", pin) for pin in steps),
        *(("action", pin) for pin in actions),
    )
    sources = tuple(
        (kind, pin, _pin_path(selection, pin)) for kind, pin in pins
    )
    if len({pin.ref_id.partition("@")[0] for _, pin, _ in sources}) != len(
        sources
    ):
        raise NativeWorkflowDefinitionError(
            "Duplicate native definition identities in Workflow binding"
        )

    def check(*, validate_headers: bool = False) -> None:
        reader = ReadContext(
            roots=[str(selection.control_root), str(selection.manifest_path)],
            limits=dict(CEILINGS),
        )
        _pinned_bytes(
            reader,
            selection.manifest_path,
            selection.manifest_ref,
            selection.manifest_sha256,
        )
        for kind, pin, path in sources:
            raw = _pinned_bytes(reader, path, pin.ref_id, pin.sha256)
            if validate_headers:
                _check_header(path, raw, kind, pin.ref_id)
        if reader.currentness()["state"] != "unchanged":
            raise NativeWorkflowDefinitionError(
                "Native Workflow sources changed during verification"
            )

    check(validate_headers=True)
    return check


STATUS_SPECIFICATIONS = {
    "workflow": (
        "AN-S-1928@5",
        "5baee5afaf1cc2577bb7e85fce2b2d78db4229d97033d40a4ef36674426b0fcb",
    ),
    "step": (
        "AN-S-1834@1",
        "cf13a7f20adf79c318e0ea52dfb4466ef1bcec6f0eae4246935a31880c7ab9e2",
    ),
    "action": (
        "AN-S-1831@2",
        "f2d16c77d8b2d9062c7c8221adbbb6eeb011dc5c2d6ec84da33eb6ae2fd1f81a",
    ),
}


def _status_spec_path(selection, row, ref):
    relative, digest = row.get("source_path"), row.get("_source_sha256")
    if not isinstance(relative, str) or not isinstance(digest, str):
        raise NativeWorkflowDefinitionError(
            f"Invalid native status specification {ref}"
        )
    path = Path(relative)
    atom_id = ref.partition("@")[0]
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != relative
        or not path.is_relative_to(selection.control_relative)
        or component_path(path.relative_to(selection.control_relative), "C58")
        is None
        or path.suffix != ".md"
        or not path.name.startswith(atom_id + "-")
    ):
        raise NativeWorkflowDefinitionError(
            f"Invalid native status specification path {ref}"
        )
    return selection.root / path, digest


def _pin_status_specification(
    reader, selection, rows, kind, ref, expected_body
):
    selected = [
        row
        for row in rows
        if row.get("_exact_ref") == ref
        and row.get("status_group") == "Current"
    ]
    if len(selected) != 1:
        raise NativeWorkflowDefinitionError(
            f"Missing or ambiguous native status specification {ref}"
        )
    path, digest = _status_spec_path(selection, selected[0], ref)
    raw = _pinned_bytes(reader, path, ref, digest, metadata_guard=True)
    if _check_header(path, raw, kind, ref).get("lens") != "DOM/MTD":
        raise NativeWorkflowDefinitionError(
            f"Expected DOM/MTD Lens for native status specification {ref}"
        )
    _, delimiter, body = raw.partition(b"\n---\n")
    if not delimiter or sha256(body).hexdigest() != expected_body:
        raise NativeWorkflowDefinitionError(
            f"Native status specification body differs for {ref}"
        )
    return path


def bind_status_specifications(
    selection: NativeProjectSelection,
    *,
    current_rows: Iterable[Mapping[str, object]],
) -> Callable[[], None]:
    "Bind the installed status operation to its exact native SPEC carriers."
    rows = tuple(current_rows)
    roots = [str(selection.control_root), str(selection.manifest_path)]
    reader = ReadContext(roots=roots, limits=dict(CEILINGS))
    _pinned_bytes(
        reader,
        selection.manifest_path,
        selection.manifest_ref,
        selection.manifest_sha256,
        metadata_guard=True,
    )
    refs = {str(selection.manifest_path): selection.manifest_ref}
    for kind, (ref, expected_body) in STATUS_SPECIFICATIONS.items():
        path = _pin_status_specification(
            reader, selection, rows, kind, ref, expected_body
        )
        refs[str(path)] = ref

    def check() -> None:
        changed = {
            item["path"] for item in reader.currentness()["affected_inputs"]
        }
        if changed:
            ref = next(ref for path, ref in refs.items() if path in changed)
            raise NativeWorkflowDefinitionError(
                f"Pinned native source {ref} changed"
            )

    check()
    return check


def declared_release_entrypoint(selection, operation):
    reader = ReadContext(
        roots=[str(selection.control_root)], limits=dict(CEILINGS)
    )
    entrypoints = []
    for path in reader.inventory_shallow(
        selection.control_root / PROJECT_CONFIG_DIRECTORY
    ):
        carrier = parse_carrier(reader.read(path), path)
        header = native_header_view(carrier.metadata)
        atom_id = header.get("identity", {}).get("atom_id", "")
        if (
            not re.fullmatch(
                rf"{re.escape(selection.project_prefix)}-[PC]-[0-9]+", atom_id
            )
            or header.get("context", {}).get("template") != "workflow"
            or header.get("state", {}).get("status") != "active"
        ):
            continue
        source = formal_claim(carrier.body, required=False)
        if source is not None and re.search(r"\brelease_command\s*\(", source):
            declared_operation, entrypoint = _parse_release_claim(source)
            if declared_operation == operation:
                entrypoints.append(entrypoint)
    if len(entrypoints) != 1:
        raise ValueError(
            f"Expected one Active Project Config claim for {operation} release"
        )
    entrypoint = entrypoints[0]
    script = selection.root / entrypoint
    if not script.is_file() or script.resolve() != script:
        raise ValueError("Declared release entrypoint is unavailable")
    return entrypoint
