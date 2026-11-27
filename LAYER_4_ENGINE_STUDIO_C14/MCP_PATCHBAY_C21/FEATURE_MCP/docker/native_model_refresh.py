("Select staged native Model Claims with Workbench "
 "and compile them for image admission.")  # fmt: skip

import os
from pathlib import Path
import sys
import subprocess
import time


ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
ROOT = Path(__file__).resolve().parents[4]
ENGINE_ROOT = ROOT / ENGINE
PROGRAMMATIC = ENGINE_ROOT / "FEATURE_PROGRAMMATIC"
sys.path.insert(0, str(ENGINE_ROOT))


def _remaining(deadline: float | None) -> float | None:
    if deadline is None:
        return None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("native model refresh", 0)
    return remaining


def verify_project_model(
    project: Path, timeout: float | None, previous: str | None
) -> str:
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
        select_runtime_project,
    )

    deadline = None if timeout is None else time.monotonic() + timeout
    control = select_runtime_project(project).control_root
    module = (
        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
        "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1."
        "image_model_stage"
    )
    remaining = _remaining(deadline)
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        module,
        str(project),
        str(control),
        "none" if remaining is None else str(remaining),
    ]
    if previous is not None:
        command.append(previous)
    environment = dict(os.environ)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONPATH"] = str(ENGINE_ROOT)
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        text=True,
        timeout=_remaining(deadline),
        check=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    unbounded = (
        sys.argv[2] == "none"
        and os.environ.get("ANECHOIC_TEST_IMAGE_DEADLINES") == "0"
    )
    timeout = None if unbounded else float(sys.argv[2])
    print(
        verify_project_model(
            Path(sys.argv[1]),
            timeout,
            sys.argv[3] if len(sys.argv) == 4 else None,
        )
    )
