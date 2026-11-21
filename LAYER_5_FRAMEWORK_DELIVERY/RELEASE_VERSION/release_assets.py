"""Generate and verify native release inputs."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


class LocalReleaseError(RuntimeError):
    """A pre-effect refusal from the bounded local-release runner."""


_MCP = Path("LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP")


def generate_tool_registry(package: Path) -> Path:
    """Seal the configured MCP providers into the staged runtime package."""
    script = package / _MCP / "generate_tool_registry.py"
    output = script.with_name("tool_registry.json")
    unavailable = "local-release-tool-registry-unavailable"
    if not script.is_file() or script.is_symlink():
        raise LocalReleaseError(unavailable)
    try:
        output.unlink(missing_ok=True)
        result = subprocess.run(
            (sys.executable, "-B", str(script), "--package-root", str(package)),
            cwd=package, text=True, capture_output=True, check=False,
        )
    except OSError as error:
        raise LocalReleaseError(unavailable) from error
    if result.returncode != 0 or not output.is_file() or output.is_symlink():
        raise LocalReleaseError("local-release-tool-registry-generation-failed")
    try:
        json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LocalReleaseError("local-release-tool-registry-generation-failed") from error
    return output


def generate_scope_callback(package: Path, raw: bytes, *, selected_pin, release_sources):
    """Build the explicitly selected callback; no selection preserves legacy release."""
    if selected_pin is None:
        return None
    from FEATURE_FORMAL_MODEL_ENGINE.scope_callback_asset import generated_assets, write_package
    generated = generated_assets(raw, pin=selected_pin, release_sources=release_sources)
    return write_package(package / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/assets", generated)


def verify_native_release_assets(package: Path, project_root: Path, control_relative: Path) -> None:
    """Verify the native Model, Structure, source capture and lifecycle binding."""
    verifier = '''
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
package, root, control = map(Path, sys.argv[1:])
for directory in ("FEATURE_PROGRAMMATIC", "FEATURE_PROGRAMMATIC/FEATURE_TOOLS",
                  "IWE_CONSOLE_C43", "MCP_PATCHBAY_C21/FEATURE_MCP"):
    sys.path.insert(0, str(package / "LAYER_3_ENGINE_STUDIO_C14" / directory))
from native_startup import select_runtime_project
from native_workflow_definition import bind_status_specifications
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.compiler import load_generation_model, write_model
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.structure_compile import compile_structure
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_pkg2.host import verify_model
selection = select_runtime_project(root, control)
with TemporaryDirectory(prefix="anechoic-model-check-") as directory:
    fingerprint = write_model(Path(directory), selection.control_root)
    verify_model(Path(directory), fingerprint)
    sys.path.insert(0, directory)
    model = load_generation_model(Path(directory))
    compile_structure(selection, model)
capture = capture_native(selection)
if capture.errors:
    raise ValueError("native Project capture is incomplete")
bind_status_specifications(selection, current_rows=capture.atoms)()
'''
    try:
        result = subprocess.run(
            (sys.executable, "-B", "-c", verifier, str(package), str(project_root), str(control_relative)),
            cwd=package, env={}, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            timeout=60, check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise LocalReleaseError("local-release-native-assets-verification-failed") from error
    if result.returncode != 0:
        raise LocalReleaseError("local-release-native-assets-verification-failed")
