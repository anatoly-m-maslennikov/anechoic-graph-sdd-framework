"""Admit one Project per JSON-lines request using the reviewed Model."""

from contextlib import ExitStack
from dataclasses import asdict
import atexit
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Lock

from .model_generation__pub import open_admitted_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    discover_native_project,
    mcp_tool_blacklist,
    rebind_native_selection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import ProjectSelectionError  # fmt: skip

_ENGINE = Path(__file__).resolve().parents[4]
_ROOT = _ENGINE.parent
_COMPILER = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR."
    "manifest_compiler_CS1.image_model_compile"
)
_lock = Lock()
_stack = ExitStack()
_model = None
atexit.register(_stack.close)


def reviewed_model():
    """Compile and hold an attested reviewed Model for this process."""
    global _model
    with _lock:
        if _model is None:
            with TemporaryDirectory(
                prefix="anechoic-beta-reviewed-model-"
            ) as directory:
                generation = Path(directory).resolve()
                timeout = (
                    None
                    if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0"
                    else 15
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-P",
                        "-m",
                        _COMPILER,
                        str(generation),
                        "--attest-model",
                    ],
                    cwd=_ROOT,
                    env={**os.environ, "PYTHONPATH": str(_ENGINE)},
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    timeout=timeout,
                    check=True,
                )
                attestation = json.loads(result.stdout)
                _model = _stack.enter_context(
                    open_admitted_model(
                        generation,
                        attestation["model_sha256"],
                        attestation["descriptor_sha256"],
                    )
                )
        return _model


def select_runtime_project(
    project_root, control_root=None, *, instance_id=None, host_root=None
):
    selection = discover_native_project(
        project_root,
        control_root,
        manifest_validator=lambda: reviewed_model().validate_manifest,
    )
    if host_root is not None and instance_id is None:
        raise ProjectSelectionError(
            "Host Project binding requires an explicit instance identity"
        )
    if instance_id is not None:
        selection = rebind_native_selection(
            selection, instance_id, host_root=host_root
        )
    return selection


def _selection(encoded):
    value = json.loads(encoded)
    if (
        not isinstance(value, dict)
        or set(value)
        != {"project_root", "control_root", "instance_id", "host_root"}
        or not isinstance(value["project_root"], str)
        or any(
            value[key] is not None and not isinstance(value[key], str)
            for key in ("control_root", "instance_id", "host_root")
        )
    ):
        raise ProjectSelectionError("Invalid Project admission request")
    selection = asdict(select_runtime_project(**value))
    del selection["structure_snapshot"]
    selection["tool_blacklist"] = sorted(
        mcp_tool_blacklist(selection["parameters"])
    )
    selection["release_workflows_enabled"] = (
        selection["parameters"]
        .get("project_mcp", {})
        .get("release_workflows_enabled")
        is True
    )
    for key in (
        "root",
        "control_root",
        "control_relative",
        "manifest_path",
        "host_root",
    ):
        if selection[key] is not None:
            selection[key] = str(selection[key])
    return selection


def main():
    for line in sys.stdin.buffer:
        try:
            response = {"result": _selection(line)}
        except ProjectSelectionError as error:
            response = {
                "error": {
                    "code": "project_selection_error",
                    "message": str(error),
                }
            }
        except ValueError:
            response = {
                "error": {
                    "code": "project_selection_error",
                    "message": "Invalid Project admission request",
                }
            }
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
