"""Native release source discovery and image build support."""
from __future__ import annotations
import os
import re
from pathlib import Path
import yaml
from .release_assets import LocalReleaseError
from .release_images import ImageManager
from .release_inputs import read_atom_header
from .release_package_files import _project_path, _walk_regular_files, _file_identity, _clear_owned

_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_LAYER_NAMES = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")
_NON_SOURCE_DIRECTORIES = frozenset({"01_draft", "02_ready", "09_archived", "000_draft", "099_archived", "_journal", "_projection"})
_DEFAULT_TIER_ONE_DIRECTORY = "01_TIER_1_ARCHITECTURE"


def _tier_one_directory(parameters):
    project = (parameters or {}).get("project", {})
    if not isinstance(project, dict) or "folder_layout" not in project:
        return _DEFAULT_TIER_ONE_DIRECTORY
    folders = project["folder_layout"]
    tiers = folders.get("active_spec_by_tier") if isinstance(folders, dict) else None
    if (not isinstance(tiers, dict) or tiers.keys() != {"0", "1", "2+"}
            or tiers["0"] != "." or tiers["2+"] != "_{lens}/{sublenses}"):
        raise ValueError("Invalid Active SPEC folders in Project Manifest")
    name = tiers["1"]
    if (not isinstance(name, str) or len(name) > 255 or not re.fullmatch(r"01_[A-Z][A-Z0-9_]*", name)
            or name.casefold() in _NON_SOURCE_DIRECTORIES or re.search(r"_C[0-9]+$", name)):
        raise ValueError("Invalid Tier 1 SPEC folder in Project Manifest")
    return name


def _component_sources(root, control):
    found = {}
    pending = [control]
    while pending:
        parent = pending.pop()
        for child in parent.iterdir():
            match = re.fullmatch(r"(?!__).+_(C[0-9]+)", child.name)
            if not match or not (child.is_dir() or child.is_symlink()):
                continue
            _project_path(root, child.relative_to(root), label="delivery-source", require_exists=True)
            component = match.group(1)
            if component in {"C9", "C58"}:
                if component in found:
                    raise ValueError(f"Multiple delivery source Components for {component}")
                found[component] = child
            else:
                pending.append(child)
    return found


def _release_candidates(root, control, tier_one):
    ontology, methodology = _LAYER_NAMES
    environments = "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72"
    components = _component_sources(root, control)
    ontology_source = components.get("C9", control / ontology)
    scopes = [(ontology_source, ontology, None, ontology_source)]
    for directory, name, component in ((components.get("C58", control / methodology), methodology, None),
                                        (control / environments, environments, "C72")):
        if os.path.lexists(directory):
            scopes.append((directory, methodology if component else name, component, directory))
    project_folders = (tier_one, "__DES", "__DEVOPS", "__QA", "__SWD")
    project_folders += tuple(path.name for path in control.iterdir()
                             if re.fullmatch(r"_[A-Z][A-Z0-9_]*", path.name) and path.name != "_PMETA")
    for name in dict.fromkeys(project_folders):
        directory = control / name
        if os.path.lexists(directory):
            scopes.append((directory, methodology, "C00", control))
    for directory, name, component, base in scopes:
        _project_path(root, directory.relative_to(root), label="delivery-source", require_exists=True)
        if not directory.is_dir():
            raise ValueError("Delivery source is not a directory")
        for path in _walk_regular_files(directory, excluded_directories=_NON_SOURCE_DIRECTORIES):
            yield path, name, component, base
    for path in control.iterdir():
        if path.is_file() or path.is_symlink():
            yield path, methodology, "C00", control


def _release_spec_header(path):
    if path.is_symlink():
        raise ValueError(f"{path}: unsafe Spec source")
    try:
        return read_atom_header(path.read_text(encoding="utf-8"))[0]
    except (UnicodeError, ValueError, yaml.YAMLError) as error:
        raise ValueError(f"{path}: invalid Spec header") from error


def _native_release_sources(selection) -> dict[Path, Path]:
    root, control = selection.root, selection.control_root
    selected, identities = {}, set()
    prefix = f"{selection.project_prefix}-S-"
    try:
        manifest = _project_path(root, selection.manifest_path.relative_to(root), label="manifest", require_exists=True)
        if _file_identity(manifest)[0] != selection.manifest_sha256:
            raise ValueError("Project Manifest changed")
        tier_one = _tier_one_directory(getattr(selection, "parameters", {}))
        for path, layer, component, base in _release_candidates(root, control, tier_one):
            if path.suffix != ".md" or not path.name.startswith(prefix):
                continue
            metadata = _release_spec_header(path)
            context = metadata.get("context", {})
            if component == "C00" and isinstance(context, dict) and context.get("template") in {
                "project_manifest", "project_goal", "component_manifest", "component_seed_manifest", "project_contract"
            }:
                continue
            if metadata.get("atom_family") != "SPEC":
                raise ValueError(f"{path}: invalid Spec family")
            if component is not None:
                container = metadata.get("container", {})
                if not isinstance(container, dict) or container.get("component") != component:
                    continue
            state = metadata.get("state")
            if not isinstance(state, dict) or not isinstance(state.get("status"), str):
                raise ValueError(f"{path}: missing Spec status")
            if state["status"] != "active":
                continue
            atom_id = metadata.get("atom_id")
            if (not isinstance(atom_id, str) or not re.fullmatch(rf"{re.escape(prefix)}[0-9]+", atom_id)
                    or atom_id in identities or not path.name.startswith(atom_id + "-")):
                raise ValueError(f"{path}: duplicate Current identity or mismatched Spec filename")
            identities.add(atom_id)
            selected[Path(layer) / path.relative_to(base)] = path
        if not any(path.parts[0] == _LAYER_NAMES[0] for path in selected):
            raise ValueError("No Active Meta-ontology Specs were selected")
        return selected
    except (OSError, ValueError) as error:
        raise LocalReleaseError(f"local-release-native-sources-invalid: {error}") from error



def _cleanup_staging(root: Path, staging: Path | None) -> str:
    if staging is None:
        return ""
    try:
        _clear_owned(staging, label="temporary-package")
    except (LocalReleaseError, OSError):
        pass
    return f"Retained temporary staging: `{staging.relative_to(root).as_posix()}`.\n" if os.path.lexists(staging) else ""


def _image_manager(source: Path, temporary: Path | None = None, *, project_root: Path,
                   build_provenance: dict[str, str] | None = None, source_provider=None):
    return ImageManager(source, project_root=project_root, build_temp_root=temporary, build_provenance=build_provenance, source_provider=source_provider)
