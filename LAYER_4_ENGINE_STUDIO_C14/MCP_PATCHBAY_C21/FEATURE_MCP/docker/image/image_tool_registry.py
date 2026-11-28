"""Compile the MCP tool registry in private image staging."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


TOOL_REGISTRY_COMPILER = (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE"
    "_CONSOLE_BACKEND/generate_tool_registry.py"
)
TOOL_PROVIDERS = (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE"
    "_CONSOLE_BACKEND/tool_providers.json"
)
TOOL_REGISTRY = (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CON"
    "SOLE_BACKEND/tool_registry.json"
)


def _run_compiler(package, timeout):
    staged_compiler = package / TOOL_REGISTRY_COMPILER
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(staged_compiler),
            "--package-root",
            str(package),
        ],
        cwd=package,
        env={"PYTHONPATH": str(package / "LAYER_4_ENGINE_STUDIO_C14")},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )


def compile_tool_registry(
    source_root: Path, *, timeout: float | None, max_output: int
) -> bytes:
    "Generate the registry in private staging, never in the source closure."
    compiler = source_root / TOOL_REGISTRY_COMPILER
    providers = source_root / TOOL_PROVIDERS
    if (
        compiler.is_symlink()
        or not compiler.is_file()
        or providers.is_symlink()
        or not providers.is_file()
    ):
        raise ValueError("tool registry compiler or providers are unavailable")
    with tempfile.TemporaryDirectory(
        prefix="anechoic-tool-registry-"
    ) as stage:
        package = Path(stage) / "package"
        for component in (
            "FEATURE_PROGRAMMATIC",
            "ARCHITECTURE_ANALYSIS_C73",
            "MCP_PATCHBAY_C21",
            "IWE_CONSOLE_C43",
        ):
            relative = Path("LAYER_4_ENGINE_STUDIO_C14") / component
            shutil.copytree(
                source_root / relative, package / relative, symlinks=True
            )
        output = package / TOOL_REGISTRY
        result = _run_compiler(package, timeout)
        if (
            result.returncode != 0
            or output.is_symlink()
            or not output.is_file()
        ):
            raise ValueError("tool registry compilation failed")
        if output.stat().st_size > max_output:
            raise ValueError("tool registry output exceeded its bounded read")
        payload = output.read_bytes()
        try:
            json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("tool registry output is invalid") from error
        return payload
