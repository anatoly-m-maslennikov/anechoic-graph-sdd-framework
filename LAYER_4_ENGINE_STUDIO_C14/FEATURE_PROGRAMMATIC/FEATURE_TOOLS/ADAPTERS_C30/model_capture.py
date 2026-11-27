"""Select full Model carrier sources from the pinned native capture."""
from pathlib import PurePosixPath
import re
from types import MappingProxyType
from types import SimpleNamespace

from .atom_reference__pub import COMPONENT_MANIFEST_FILENAME
from .model_ontology_path__pub import find_ontology_component, is_ontology_model_source
from .native_carrier_placement__pub import component_manifest_parent, spec_folder_layout
from .project_manifest__pub import manifest_inputs


def _model_path(selection, path):
    try:
        parts = PurePosixPath(path).relative_to(selection.control_root.relative_to(selection.root).as_posix()).parts
    except (ValueError, TypeError):
        return False
    return (is_ontology_model_source(PurePosixPath(*parts))
            or (len(parts) == 3 and parts[0] in {"__PROJECT_CONFIG", "002_PROJECT_CONFIG"}
                and parts[1] == "CUSTOM_MODEL")) and parts[-1].endswith(".md")


def _structure_candidate(selection, path, parameters):
    try:
        relative = PurePosixPath(path).relative_to(selection.control_root.relative_to(selection.root).as_posix())
    except ValueError:
        return False
    if not re.match(r'[A-Z]+-S-', relative.name):
        return False
    owner = component_manifest_parent(relative, parameters)
    if any(not re.fullmatch(r'(?!__).+_C[0-9]+', part) for part in owner.parts):
        return False
    if relative.parent not in {owner, owner / '_SPEC', owner / spec_folder_layout(parameters)['1']}:
        return False
    return relative


def model_inputs(selection, capture, *, include_spec_rows=False):
    root = selection.control_root.relative_to(selection.root).as_posix()
    rows = tuple({"source_path": PurePosixPath(row["source_path"]).relative_to(root).as_posix(),
                  "exact_ref": row["_exact_ref"], "metadata": row["header_json"],
                  "body": row["_content_bytes"].decode("utf-8")}
                 for row in capture.atoms
                 if row["status_group"] == "Current" and _model_path(selection, row["source_path"]))
    issues = list(capture.ingestion_issues)
    covered = {issue["relative_path"] for issue in issues}
    issues.extend({"relative_path": path, "code": "invalid_value", "message": message,
                   "atom_ref": None, "related_paths": []}
                  for path, message in sorted(capture.errors.items()) if path not in covered)
    ontology = find_ontology_component(selection.control_root)
    result = {"rows": rows, "has_c9": ontology is not None,
              "issues": tuple(issue for issue in issues if _model_path(selection, issue["relative_path"]))}
    if include_spec_rows:
        result.update(_spec_inputs(selection, capture, issues))
    return MappingProxyType(result)


def _spec_inputs(selection, capture, issues):
    result = {}
    manifest = selection.manifest_path.relative_to(selection.root).as_posix()
    result["manifest_path"] = manifest
    manifest_row = next((row for row in capture.atoms if row['source_path'] == manifest), None)
    parameters = None
    if manifest_row is not None:
        carrier = SimpleNamespace(metadata=manifest_row['header_json'],
                                  body=manifest_row['_content_bytes'].decode('utf-8'))
        parameters = manifest_inputs(selection.manifest_path, carrier)[0].get('parameters')
    structural, aliases = [], []
    templates = getattr(capture, 'classified_templates', {})
    for issue in issues:
        path = issue['relative_path']
        relative = _structure_candidate(selection, path, parameters)
        if not relative:
            continue
        match = COMPONENT_MANIFEST_FILENAME.fullmatch(relative.name)
        template = match[1].lower() if match else templates.get(path)
        if not template or (template == 'component_seed_manifest'
                            and relative.parent.name == spec_folder_layout(parameters)['1']):
            continue
        if match:
            structural.append(issue)
        else:
            aliases.append({'relative_path': path, 'template': template})
    result['structure_issues'] = tuple(structural)
    result['structure_alias_issues'] = tuple(aliases)
    result["spec_rows"] = [
        {"source_path": row["source_path"], "exact_ref": row["_exact_ref"],
         "metadata": row["header_json"], "body": row["_content_bytes"].decode("utf-8"),
         "sha256": capture.carrier_hashes[row["source_path"]]}
        for row in capture.atoms
        if row["status_group"] != "Archived" and (
            row["source_path"] == manifest
            or row["id"].startswith(selection.project_prefix + "-S-")
            or (row["status_group"] == "Current" and _model_path(selection, row["source_path"])))
    ]
    return result
