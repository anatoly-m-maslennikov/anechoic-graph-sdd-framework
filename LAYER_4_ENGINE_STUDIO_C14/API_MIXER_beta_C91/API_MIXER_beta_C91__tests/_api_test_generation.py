"""Generation payload for API process tests."""

import json
from hashlib import sha256
from pathlib import Path


ENGINE = Path(__file__).resolve().parents[2]
DIGEST = "a" * 64
MODULE = "API_MIXER_beta_C91.API_MIXER_beta_C91__shared"
KERNEL = (
    "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71."
    "DATABASE_SERVER_beta_C71__shared"
)


def model_structure():
    model = json.dumps(
        {
            "model_sha256": "b" * 64,
            "binding_schema": 1,
            "modules": {"__init__.py": "d" * 64},
            "module_order": [],
            "class_modules": {},
            "bindings": {"endpoints": {}},
        },
        indent=2,
    )
    structure = json.dumps(
        {
            "model_sha256": "b" * 64,
            "project": {"ref": "AN-S-1", "sha256": DIGEST},
            "components": {},
        },
        indent=2,
    )
    return model, structure


def snapshot_graph():
    atoms = [
        {
            "reference": ref,
            "exact_ref": exact,
            "status": status,
            "status_group": group,
            "version": 1,
            "filename": ref + ".md",
            "relative_path": "control",
            "summary": "Fixture",
        }
        for ref, exact, status, group in (
            ("AN-S-1", "AN-S-1@1", "active", "Current"),
            ("AN-T-2", "AN-T-2@1", "in_queue", "Current"),
            ("AN-P-3", "AN-P-3@1", "active", "Current"),
            ("AN-C-4@1-draft", "AN-C-4@1-draft", "draft", "Draft"),
        )
    ]
    snapshot = {
        "schema_version": 2,
        "manifest_sha256": DIGEST,
        "atoms": atoms,
        "relations": [],
        "relation_types": [],
    }
    graph = {
        name: []
        for name in (
            "nodes",
            "occurrences",
            "edges",
            "read_issues",
            "test_edges",
        )
    }
    return atoms, snapshot, graph


def generation():
    model, structure = model_structure()
    atoms, snapshot, graph = snapshot_graph()
    return {
        "instance_id": "instance",
        "snapshot": snapshot,
        "model": model,
        "structure": structure,
        "graph": graph,
        "carrier_hashes": {
            "control/" + atom["filename"]: DIGEST for atom in atoms
        },
        "receipt": {
            "manifest_sha256": DIGEST,
            "model_sha256": "b" * 64,
            "snapshot_sha256": sha256(
                json.dumps(
                    snapshot, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "graph_sha256": sha256(
                json.dumps(
                    graph, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "model_descriptor_sha256": sha256(model.encode()).hexdigest(),
            "structure_sha256": sha256(structure.encode()).hexdigest(),
        },
    }


EXPECTED_TOOLS_1 = [
    "query_run",
    "query_check",
    "query_page",
    "query_schema",
    "iwe_console_status",
    "iwe_console_abort",
    "workbench_status",
    "workbench_abort",
    "query_rebuild",
    "query_load",
    "query_saved_list",
    "view_save",
    "workspace_open",
    "workspace_list",
    "workspace_get",
    "query_log_list",
    "query_log_get",
    "view_create",
    "view_duplicate",
    "view_list",
    "view_get",
    "view_update",
    "view_focus",
    "view_rename",
    "view_remove",
    "view_run",
    "view_check",
    "view_fetch",
    "atom_lifecycle_create_draft",
    "atom_lifecycle_update",
    "atom_lifecycle_promote_draft",
    "atom_lifecycle_change_status",
    "atom_lifecycle_archive",
    "atom_lifecycle_create_asset",
    "atom_lifecycle_direct_update",
    "iwe_console_atom_document",
]

EXPECTED_TOOLS_2 = [
    "query_check",
    "query_page",
    "query_schema",
    "iwe_console_status",
    "iwe_console_abort",
    "workbench_status",
    "workbench_abort",
    "query_rebuild",
    "query_load",
    "query_saved_list",
    "view_save",
    "workspace_open",
    "workspace_list",
    "workspace_get",
    "query_log_list",
    "query_log_get",
    "view_create",
    "view_duplicate",
    "view_list",
    "view_get",
    "view_update",
    "view_focus",
    "view_rename",
    "view_remove",
    "view_run",
    "view_check",
    "view_fetch",
    "atom_lifecycle_create_draft",
    "atom_lifecycle_update",
    "atom_lifecycle_promote_draft",
    "atom_lifecycle_change_status",
    "atom_lifecycle_archive",
    "atom_lifecycle_create_asset",
    "atom_lifecycle_direct_update",
    "iwe_console_atom_document",
]
