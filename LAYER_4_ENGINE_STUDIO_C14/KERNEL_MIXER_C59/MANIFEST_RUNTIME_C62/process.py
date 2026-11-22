"""Lightweight command setup for Manifest Runtime child processes."""

import os
from pathlib import Path
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
