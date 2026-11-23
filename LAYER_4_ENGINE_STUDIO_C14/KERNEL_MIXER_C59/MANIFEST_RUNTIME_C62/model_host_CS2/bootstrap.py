"""Lazily bind the reviewed Model once for this process."""

import atexit
from contextlib import ExitStack
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from threading import Lock

from ..process import _BUILDER_PACKAGE, _CODE_ROOT, _command, _environment
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
                timeout = (None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES")
                           == "0" else 15)
                result = subprocess.run(
                    (*_command(f"{_BUILDER_PACKAGE}.image_model_compile"), str(generation), "--attest-model"),
                    cwd=_CODE_ROOT, env=_environment(), stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, timeout=timeout, check=True,
                )
                attestation = json.loads(result.stdout)
                _model = _stack.enter_context(open_admitted_model(
                    generation, attestation["model_sha256"], attestation["descriptor_sha256"]))
        return _model
