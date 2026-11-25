"""Lazily bind the reviewed Model once for this process."""

import atexit
from contextlib import ExitStack
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock

from ..MANIFEST_RUNTIME_C62__shared import compile_reviewed_model
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model

_lock = Lock()
_stack = ExitStack()
_model = None
atexit.register(_stack.close)


def reviewed_native_model():
    """Return the process-wide reviewed Model, compiling it in a bounded child."""
    global _model
    with _lock:
        if _model is None:
            with TemporaryDirectory(prefix="anechoic-reviewed-model-") as directory:
                generation = Path(directory).resolve()
                attestation = json.loads(compile_reviewed_model(generation))
                _model = _stack.enter_context(open_admitted_model(
                    generation, attestation["model_sha256"], attestation["descriptor_sha256"]))
        return _model
