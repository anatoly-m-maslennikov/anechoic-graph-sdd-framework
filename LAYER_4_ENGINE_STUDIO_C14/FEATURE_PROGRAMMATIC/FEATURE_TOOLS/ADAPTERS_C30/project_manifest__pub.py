"""Read and decode guarded native Project Manifest carriers."""

from datetime import datetime
from pathlib import Path
import re

from .ADAPTERS_C30__pub import ReadContext
from .atom_reference__pub import derive_atom_ref
from .carrier_read__pub import ParsedCarrier, parse_carrier
from .formal_claim__pub import formal_claim
from .native_carrier_header__pub import native_header_model_fields, native_header_view
from .native_model_claim__pub import parse_native_model_claim


class ProjectSelectionError(ValueError):
    """An attributable refusal, without substituting another Project."""

    code = "PROJECT_SELECTION_REFUSED"
    condition = code


def _manifest_paths(reader: ReadContext, control: Path):
    for path in reader.inventory_shallow(control):
        if path.suffix == ".md":
            yield path


def manifest_sources(reader: ReadContext, control: Path, *, root_candidates=False):
    for path in _manifest_paths(reader, control):
        if root_candidates and "-PROJECT_MANIFEST--" not in path.name:
            continue
        try:
            carrier = parse_carrier(reader.read(path), path)
        except ValueError:
            if root_candidates or re.match(r"[A-Z]+-S-", path.name):
                raise
            continue
        if "atom_family" in carrier.metadata or re.match(r"[A-Z]+-S-", path.name):
            yield path, carrier


def active_manifest_carriers(reader: ReadContext, control: Path, *, root_candidates=False):
    for path, carrier in manifest_sources(reader, control, root_candidates=root_candidates):
        context = native_header_view(carrier.metadata).get("context")
        state = carrier.metadata.get("state")
        if (isinstance(context, dict) and context.get("template") == "project_manifest"
                and isinstance(state, dict) and state.get("status") == "active"):
            yield path, carrier



def select_manifest_carriers(reader: ReadContext, root: Path, control: Path):
    """Select root candidates first, retaining the control-root compatibility path."""
    candidates = [path for path in _manifest_paths(reader, root)
                  if "-PROJECT_MANIFEST--" in path.name]
    if candidates:
        return active_manifest_carriers(reader, root, root_candidates=True)
    return active_manifest_carriers(reader, control)


def manifest_inputs(path: Path, carrier: ParsedCarrier) -> tuple[dict[str, object], str]:
    header = native_header_view(carrier.metadata)
    context, state = header["context"], header["state"]
    container, identity = context.get("container"), header.get("identity")
    atom_id = identity.get("atom_id") if isinstance(identity, dict) else None
    version, tier = state.get("version"), context.get("tier")
    if (type(tier) is not int or tier != -1 or type(version) is not int or version < 1
            or not isinstance(container, dict) or set(container) != {"component"}
            or not isinstance(container["component"], str) or not container["component"].strip()
            or not isinstance(atom_id, str) or re.fullmatch(r"[A-Z]+-S-[0-9]+", atom_id) is None
            or ("atom_family" not in carrier.metadata and not path.name.startswith(f"{atom_id}-"))):
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


def manifest_state_fields(carrier: ParsedCarrier, *, include_header=False) -> dict[str, object]:
    state = carrier.metadata["state"]
    updated_at = state.get("updated_at")
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    if not isinstance(updated_at, datetime):
        raise ValueError("Manifest State requires a datetime Updated At")
    fields = {"status": state["status"], "updated_at": updated_at}
    return fields | native_header_model_fields(carrier.metadata) if include_header else fields
