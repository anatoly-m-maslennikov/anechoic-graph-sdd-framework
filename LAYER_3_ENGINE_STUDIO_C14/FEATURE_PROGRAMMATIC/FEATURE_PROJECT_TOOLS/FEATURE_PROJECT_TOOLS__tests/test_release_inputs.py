"""Validate the selected Project without changing it."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import discover_native_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_workflow_definition import bind_status_specifications
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__pub import reviewed_native_model


class ReleaseInputsTests(unittest.TestCase):
    def test_selected_project_is_admitted(self):
        selection = discover_native_project(
            Path.cwd(), manifest_validator=lambda: reviewed_native_model().validate_manifest,
        )
        module = (
            "FEATURE_PROGRAMMATIC.FEATURE_MODEL."
            "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler"
        )
        with TemporaryDirectory(prefix="anechoic-release-inputs-") as generation:
            result = subprocess.run(
                [sys.executable, "-B", "-P", "-m", module, str(selection.root),
                 selection.control_relative.as_posix(), selection.manifest_sha256,
                 generation, "--build-model"],
                env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)},
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(0, result.returncode, result.stderr)
        capture = capture_native(selection)
        self.assertFalse(capture.errors, capture.errors)
        bind_status_specifications(selection, current_rows=capture.atoms)()
