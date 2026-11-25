"""Select full Model carrier sources from the pinned native capture."""
from pathlib import PurePosixPath
from types import MappingProxyType


def _model_path(selection, path):
    try:
        parts = PurePosixPath(path).relative_to(selection.control_root.relative_to(selection.root).as_posix()).parts
    except (ValueError, TypeError):
        return False
    return ((len(parts) in (2, 3) and parts[0] == "LAYER_1_META_ONTOLOGY_C9"
             and (len(parts) == 2 or parts[1] in {"_SPEC", "_DES"}))
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
    ontology = selection.control_root / "LAYER_1_META_ONTOLOGY_C9"
    return MappingProxyType({"rows": rows, "has_c9": ontology.exists() or ontology.is_symlink(),
                             "issues": tuple(issue for issue in issues if _model_path(selection, issue["relative_path"]))})
