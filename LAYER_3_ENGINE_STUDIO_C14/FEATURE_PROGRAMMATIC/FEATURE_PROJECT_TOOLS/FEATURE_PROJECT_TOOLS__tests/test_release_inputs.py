"""Validate the selected Project and checked-in registry without changing them."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path.cwd() / "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP"))

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import _NativeModel
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.active_model_sources import (
    read_active_model_sources,
)
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.structure_compile import (
    compile_structure,
)
from native_startup import select_runtime_project
from native_workflow_definition import bind_status_specifications
from tool_registry_runtime import load_active_registry


class ReleaseInputsTests(unittest.TestCase):
    def test_selected_project_is_admitted(self):
        selection = select_runtime_project(Path.cwd())
        records = read_active_model_sources(
            selection.control_root, selection.control_root / "LAYER_1_META_ONTOLOGY_C9"
        )
        model = _NativeModel(records=records)
        compile_structure(selection, model)
        capture = capture_native(selection)
        self.assertFalse(capture.errors, capture.errors)
        bind_status_specifications(selection, current_rows=capture.atoms)()

    def test_checked_in_tool_registry_is_current(self):
        root = Path.cwd()
        feature = root / "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP"
        load_active_registry(feature, root, None)
