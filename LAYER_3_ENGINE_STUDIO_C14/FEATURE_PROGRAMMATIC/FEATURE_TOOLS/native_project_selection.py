"""Bind an explicitly selected native Project to its one Active Manifest."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime
import os
from pathlib import Path
import re
from typing import Protocol

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_FORMAL_MODEL_ENGINE.scope_callback_asset import formal_claim
from native_atom_reference import derive_atom_ref
from project_selection import ProjectSelectionError, _instance_id, _project_root
from VALIDATE_ATOMS.validate_atoms_workers.parsing import ParsedCarrier, parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext, protected
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


class ManifestIdentity(Protocol):
    name: str
    prefix: str


@dataclass(frozen=True)
class NativeProjectSelection:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object] = field(default_factory=dict)
    host_root: Path | None = None
    structure_snapshot: Path | None = None

    @property
    def launcher_state(self) -> Path:
        return self.root / ".anechoic_runtime/runtime/project_mcp" / self.instance_id

    @property
    def compose_project(self) -> str:
        return "anechoic-mcp-" + self.instance_id[:24]


def rebind_native_selection(selection: NativeProjectSelection, instance_id: str, *,
                            host_root: str | Path | None = None) -> NativeProjectSelection:
    """Retain the admitted host identity after container path translation."""
    if not isinstance(selection, NativeProjectSelection) or not isinstance(instance_id, str) or not re.fullmatch(r"[0-9a-f]{64}", instance_id):
        raise ProjectSelectionError("Transported Project identity is invalid")
    host = selection.host_root if instance_id == selection.instance_id else None
    if host_root is not None:
        try:
            host = Path(host_root)
        except (TypeError, ValueError) as error:
            raise ProjectSelectionError("Transported host root is invalid") from error
        if (not host.is_absolute() or ".." in host.parts or str(host_root) != host.as_posix()
                or host.as_posix().startswith("//") or protected(host)
                or _instance_id(host, selection.control_relative) != instance_id):
            raise ProjectSelectionError("Transported Project identity contradicts its host binding")
        if os.path.lexists(host):
            _project_root(host)
    return replace(selection, instance_id=instance_id, host_root=host)


def manifest_paths(reader: ReadContext, control: Path):
    for path in reader.inventory_shallow(control):
        if re.match(r"[A-Z]+-S-", path.name):
            yield path


def _manifest_carriers(reader: ReadContext, control: Path):
    for path in manifest_paths(reader, control):
        carrier = parse_carrier(reader.read(path), path)
        context = carrier.metadata.get("context")
        state = carrier.metadata.get("state")
        if (isinstance(context, dict) and context.get("template") == "project_manifest"
                and isinstance(state, dict) and state.get("status") == "active"):
            yield path, carrier


def _manifest_inputs(path: Path, carrier: ParsedCarrier) -> tuple[dict[str, object], str]:
    header = carrier.metadata
    context, state = header["context"], header["state"]
    container, identity = context.get("container"), header.get("identity")
    atom_id = identity.get("atom_id") if isinstance(identity, dict) else None
    version, tier = state.get("version"), context.get("tier")
    if (type(tier) is not int or tier != -1 or type(version) is not int or version < 1
            or not isinstance(container, dict) or set(container) != {"component"}
            or not isinstance(container["component"], str) or not container["component"].strip()
            or not isinstance(atom_id, str) or re.fullmatch(r"[A-Z]+-S-[0-9]+", atom_id) is None
            or not path.name.startswith(f"{atom_id}-")):
        raise ProjectSelectionError("Invalid Active Project Manifest header or filename")
    claim = parse_native_model_claim(formal_claim(carrier.body))
    arguments = claim["arguments"] if claim is not None and claim["kind"] == "entity" else {}
    instance = arguments.get("instance", {})
    fields = instance.get("fields", {})
    if (set(arguments) != {"entity_name", "instance"} or arguments["entity_name"] != "Project Manifest"
            or instance.get("type") != "ProjectManifest" or not {"name", "prefix"} <= fields.keys()
            or fields.keys() - {"name", "prefix", "parameters", "lens_whitelist"}):
        raise ProjectSelectionError("Expected one formal ProjectManifest instance")
    return {"atom_id": atom_id, "ref_id": derive_atom_ref(atom_id, version, state["status"]), "version": version,
            "tier": tier, **fields}, container["component"]


def manifest_state_fields(carrier: ParsedCarrier) -> dict[str, object]:
    state = carrier.metadata["state"]
    updated_at = state.get("updated_at")
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    if not isinstance(updated_at, datetime):
        raise ValueError("Manifest State requires a datetime Updated At")
    return {"status": state["status"], "updated_at": updated_at}


def resolve_native_project(
    project_root: str | Path, control_root: str | Path, *,
    validate_manifest: Callable[[dict[str, object], str], ManifestIdentity],
    require_atom_state: bool = False,
) -> NativeProjectSelection:
    """Validate the Manifest with the caller's compiled model and Project container."""
    root = _project_root(project_root)
    try:
        relative = Path(control_root)
        if (len(relative.parts) != 1 or str(control_root) != relative.as_posix()
                or not relative.name.startswith(".anechoic_") or relative.name == ".anechoic_"):
            raise ProjectSelectionError("Native control root must name one explicit direct Project child")
        control = root / relative
        reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
        sources = _manifest_carriers(reader, control)
        selected = next(sources, None)
        if selected is None or next(sources, None) is not None:
            raise ProjectSelectionError("Expected one Active Tier -1 Project Manifest at Project root")
        path, carrier = selected
        fields, component_id = _manifest_inputs(path, carrier)
        if require_atom_state:
            fields.update(manifest_state_fields(carrier))
        manifest = validate_manifest(fields, component_id)
        parameters = getattr(manifest, "parameters", fields.get("parameters", {}))
        if not isinstance(parameters, dict):
            raise ProjectSelectionError("Validated Project Manifest parameters must be a mapping")
        if relative.name != f".anechoic_{manifest.name.casefold()}":
            raise ProjectSelectionError("Project Manifest name contradicts the native control root")
        if not str(fields["atom_id"]).startswith(f"{manifest.prefix}-S-"):
            raise ProjectSelectionError("Project Manifest prefix contradicts its Atom ID")
        if reader.currentness()["state"] != "unchanged":
            raise ProjectSelectionError("Project carriers changed during selection")
        return NativeProjectSelection(root, control, relative, _instance_id(root, relative),
                                      manifest.name, manifest.prefix, path, str(fields["ref_id"]),
                                      reader.fingerprints[str(path)], deepcopy(parameters))
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectSelectionError("Native Project Manifest is unavailable, invalid, or unsafe") from error
