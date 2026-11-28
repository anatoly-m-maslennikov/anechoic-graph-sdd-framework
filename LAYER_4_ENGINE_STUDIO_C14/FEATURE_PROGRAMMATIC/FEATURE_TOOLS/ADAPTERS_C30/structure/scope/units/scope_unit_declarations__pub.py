"""Read current Scope Unit Declaration Atoms; no declaration writing \
lives here."""

from __future__ import annotations

import hashlib
import os as os
from dataclasses import replace
from pathlib import Path
import re
from typing import Any

from ....structure.scope._scope_candidate_discovery import (
    _declaration_candidates as _read_declaration_candidates,
)
from ....settings.settings_carrier__pub import read_settings_carrier
from ....structure.scope.scope_carrier__pub import (
    DELEGATION_ROLE_FOLDERS,
    ScopeDeclarationError,
    has_projection_marker,
    has_scope_declaration_form,
)
from ....structure.scope.scope_declaration_parse__pub import (
    ScopeDelegation,
    ScopeUnitDeclarations,
    assemble_scope_unit_declarations,
    parse_scope_unit_declaration,
)
from ....ADAPTERS_C30__pub import CEILINGS, ReadContext, open_regular


def _control(root: Path, control_root: Path | str) -> Path:
    value = Path(control_root)
    if value.is_absolute():
        control = value
    else:
        control = root / value
    if (
        control.parent != root
        or not control.name.startswith(".anechoic_")
        or control.name == ".anechoic_"
    ):
        raise ScopeDeclarationError(
            "control root must be one direct Project control directory"
        )
    return control


def _digest(pins: dict[str, dict[str, Any]]) -> str:
    payload = "".join(
        f"{path}\0{pin['sha256']}\0{pin['atom_id']}\0{pin['version']}\n"
        for path, pin in sorted(pins.items())
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _declaration_candidates(
    reader: ReadContext, directory: Path, *, root: bool
) -> tuple[tuple[Path, bytes], ...]:
    return _read_declaration_candidates(
        reader,
        directory,
        root=root,
        open_regular=open_regular,
        has_scope_declaration_form=has_scope_declaration_form,
        has_projection_marker=has_projection_marker,
    )


def _child_authority(parent_authority: Path, declaration: Any) -> Path:
    parts = [declaration.scope_unit_id]
    if declaration.label:
        parts.append(declaration.label)
    if declaration.ordered:
        parts.append(str(declaration.local_order))
    parts.append(declaration.name)
    return parent_authority / "_".join(parts)


def _frontier_candidates(reader, frontier, directory, *, root):
    candidates = _declaration_candidates(reader, directory, root=root)
    key = (directory, root)
    expected = tuple(path for path, _ in candidates)
    if key in frontier and frontier[key] != expected:
        raise ScopeDeclarationError(
            "Scope Unit Declaration source frontier changed during discovery"
        )
    frontier[key] = expected
    return candidates


def read_scope_unit_declarations(
    root: Path,
    control_root: Path | str,
    *,
    reader: ReadContext | None = None,
) -> ScopeUnitDeclarations:
    """Read the exact current declaration set below the selected Project \
control root."""
    root = Path(root)
    control = _control(root, control_root)
    reader = (
        reader
        if reader is not None
        else ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    )
    try:
        reader.allowed(root)
        reader.allowed(control)
        rows = []
        pins: dict[str, dict[str, Any]] = {}
        frontier: dict[tuple[Path, bool], tuple[Path, ...]] = {}

        def read_candidates(directory: Path, *, root: bool):
            return _frontier_candidates(reader, frontier, directory, root=root)

        def admit(path: Path, raw: bytes) -> Any:
            return _admit(path, raw, root, pins)

        _discover_tree(control, reader, read_candidates, admit, rows)
        if not rows:
            raise ScopeDeclarationError(
                "no current Scope Unit Declarations found"
            )
        _verify_sources(reader, root, frontier, pins)
        return assemble_scope_unit_declarations(
            rows,
            project_root=root,
            control_root=control,
            source_pins=pins,
            digest=_digest(pins),
        )
    except ScopeDeclarationError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ScopeDeclarationError(
            "Scope Unit Declaration source discovery is unavailable or unsafe"
        ) from error


def _admit(
    path: Path, raw: bytes, root: Path, pins: dict[str, dict[str, Any]]
) -> Any:
    try:
        declaration = parse_scope_unit_declaration(raw, path)
    except ScopeDeclarationError as error:
        if "not an active Requirement Scope Unit Declaration" in str(error):
            raise ScopeDeclarationError(
                f"{path}: declaration Form contradicts its required "
                f"carrier fields"
            ) from error
        raise
    relative = path.relative_to(root).as_posix()
    pins[relative] = {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "atom_id": declaration.atom_id,
        "version": declaration.version,
    }
    return declaration


def _verify_sources(reader, root, frontier, pins) -> None:
    for (directory, is_root), expected in frontier.items():
        if (
            tuple(
                path
                for path, _ in _declaration_candidates(
                    reader, directory, root=is_root
                )
            )
            != expected
        ):
            raise ScopeDeclarationError(
                "Scope Unit Declaration source frontier changed during "
                "discovery"
            )
    for relative, pin in pins.items():
        if (
            hashlib.sha256(
                reader.read(root / relative, remember=False)
            ).hexdigest()
            != pin["sha256"]
        ):
            raise ScopeDeclarationError(
                "Scope Unit Declaration sources changed during discovery"
            )


def _delegation_parent_id(parent, control, reader):
    parent_id = parent.scope_unit_id
    if parent_id is None:
        settings = read_settings_carrier(
            control / "anechoic_project_settings.toml",
            read_bytes=reader.read,
        )
        artifacts = settings.get("artifacts")
        identity = (
            artifacts.get("identity") if isinstance(artifacts, dict) else None
        )
        prefix = (
            identity.get("project_prefix")
            if isinstance(identity, dict)
            else None
        )
        if (
            not isinstance(prefix, str)
            or re.fullmatch(r"[A-Za-z0-9]+", prefix) is None
        ):
            raise ScopeDeclarationError("Project identity prefix is invalid")
        parent_id = f"{prefix.upper()}-SU-00"
    return parent_id


def _classify_candidates(
    candidates, root, parent, parent_path, control, reader
):
    structural: dict[str, list[Any]] = {}
    delegated: dict[str, list[ScopeDelegation]] = {}
    for candidate in candidates:
        if (
            candidate.topic_path is not None
            and root.name.casefold() != "anechoic"
        ):
            raise ScopeDeclarationError(
                f"{candidate.source}: Structure Topic root does not "
                f"identify this Project"
            )
        if candidate.topic_path is not None and candidate.topic_path != (
            *parent_path,
            candidate.name,
        ):
            raise ScopeDeclarationError(
                f"{candidate.source}: Structure Topic path contradicts "
                f"declared containment"
            )
        if isinstance(candidate, ScopeDelegation):
            parent_id = _delegation_parent_id(parent, control, reader)
            if (
                not isinstance(candidate.parent_id, str)
                or not candidate.parent_id
                or candidate.parent_id != parent_id
            ):
                raise ScopeDeclarationError(
                    "Scope Delegation is not in its declared parent authority"
                )
            delegated.setdefault(candidate.name, []).append(candidate)
        else:
            if candidate.is_root or candidate.parent != parent.name:
                raise ScopeDeclarationError(
                    "Scope Unit Declaration is not in its declared parent "
                    "authority"
                )
            structural.setdefault(candidate.name, []).append(candidate)
    return structural, delegated


def _check_delegations(delegated, structural):
    if set(delegated) - set(structural):
        raise ScopeDeclarationError(
            "Scope Delegation has no structural declaration in "
            "its direct parent authority"
        )


def _discover_tree(control, reader, read_candidates, admit, rows) -> None:
    roots = [
        admit(path, raw) for path, raw in read_candidates(control, root=True)
    ]
    if any(
        isinstance(row, ScopeDelegation)
        or not row.is_root
        or row.form != "Scope Unit Declaration"
        for row in roots
    ):
        raise ScopeDeclarationError(
            "Project Scope Unit Declaration must be at the control root"
        )
    rows.extend(roots)
    if len(roots) == 1:
        pending = [(roots[0], control, ())]
        while pending:
            parent, authority, parent_path = pending.pop()
            candidates = _authority_candidates(
                authority, read_candidates, admit
            )
            structural, delegated = _classify_candidates(
                candidates, roots[0], parent, parent_path, control, reader
            )
            _check_delegations(delegated, structural)
            for name, choices in structural.items():
                if len(choices) != 1:
                    raise ScopeDeclarationError(
                        "Scope Unit names and IDs require unique "
                        "structural declarations"
                    )
                declaration = choices[0]
                sources = tuple(delegated.get(name, ()))
                declaration = replace(declaration, delegations=sources)
                rows.append(declaration)
                pending.append(
                    (
                        declaration,
                        _child_authority(authority, declaration),
                        (*parent_path, declaration.name),
                    )
                )


def _authority_candidates(authority, read_candidates, admit) -> list[Any]:
    candidates = []
    for directory, role in zip(
        DELEGATION_ROLE_FOLDERS,
        ("Requirement", "Method", "Evaluation", "Delivery", "Operations"),
    ):
        for path, raw in read_candidates(authority / directory, root=False):
            candidate = admit(path, raw)
            if (
                isinstance(candidate, ScopeDelegation)
                and candidate.role != role
            ) or (
                not isinstance(candidate, ScopeDelegation)
                and role != "Requirement"
            ):
                raise ScopeDeclarationError(
                    f"{path}: Scope carrier Role does not match its "
                    f"authority directory"
                )
            candidates.append(candidate)
    return candidates


__all__ = ["ScopeUnitDeclarations", "read_scope_unit_declarations"]
