"""Select full Model carrier sources from the pinned native capture."""
from pathlib import PurePosixPath
from types import MappingProxyType

from .model_ontology_path__pub import find_ontology_component, is_ontology_model_source


def _model_path(selection, path):
    try:
        parts = PurePosixPath(path).relative_to(selection.control_root.relative_to(selection.root).as_posix()).parts
    except (ValueError, TypeError):
        return False
    return (is_ontology_model_source(PurePosixPath(*parts))
            or (len(parts) == 3 and parts[0] in {"__PROJECT_CONFIG", "002_PROJECT_CONFIG"}
                and parts[1] == "CUSTOM_MODEL")) and parts[-1].endswith(".md")


def model_inputs(selection, capture):
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
    return MappingProxyType({"rows": rows, "has_c9": ontology is not None,
                             "issues": tuple(issue for issue in issues if _model_path(selection, issue["relative_path"]))})
