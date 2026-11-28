"""Source fixtures for image asset tests."""

from unittest.mock import NonCallableMock

import MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared as images


def prepare_image_root(root):
    for relative in (*images._REQUIRED, images.TOOL_REGISTRY):
        source = root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("{}")
    (root / "version.toml").write_text('[framework]\nversion = "0.1.0"\n')
    for layer in (
        "LAYER_1_META_ONTOLOGY_C9",
        "LAYER_2_META_METHODOLOGY_C58",
    ):
        path = root / layer / "AN-S-1-source.md"
        path.parent.mkdir(parents=True)
        path.write_text("source")


def unsafe_receipt_fixture(root, image_id):
    project_id = "d" * 64
    state = root / ".anechoic_runtime/runtime/project_mcp" / project_id
    state.mkdir(parents=True)
    control = root / ".anechoic_project"
    selection = NonCallableMock(
        spec_set=[
            "root",
            "control_root",
            "instance_id",
            "launcher_state",
        ],
        root=root,
        control_root=control,
        instance_id=project_id,
        launcher_state=state,
    )
    path = state / "ready.json"
    receipt = {
        "project_root": str(root),
        "control_root": str(control),
        "project_id": "e" * 64,
        "image_id": image_id,
        "readiness": True,
    }
    return selection, path, receipt
