"""Lightweight command setup for Manifest Runtime child processes."""

import os
from pathlib import Path
import subprocess
import sys

_CODE_ROOT = Path(__file__).resolve().parents[3]
_ENGINE = _CODE_ROOT / "LAYER_4_ENGINE_STUDIO_C14"
_PROGRAMMATIC = _ENGINE / "FEATURE_PROGRAMMATIC"
_BUILDER_PACKAGE = (
    "FEATURE_PROGRAMMATIC.FEATURE_MODEL."
    "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1"
)


def _command(module):
    return (sys.executable, "-B", "-P", "-m", module)


def _environment():
    return {**os.environ, "PYTHONPATH": str(_ENGINE)}


def compile_reviewed_model(generation: Path) -> bytes:
    """Compile the reviewed Model in a child and return its attestation."""
    timeout = None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 15
    result = subprocess.run(
        (*_command(f"{_BUILDER_PACKAGE}.image_model_compile"), str(generation), "--attest-model"),
        cwd=_CODE_ROOT, env=_environment(), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, timeout=timeout, check=True,
    )
    return result.stdout
