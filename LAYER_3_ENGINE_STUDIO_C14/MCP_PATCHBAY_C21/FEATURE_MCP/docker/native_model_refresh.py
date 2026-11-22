"""Select staged native Model Claims with Workbench and compile them for image admission."""

import os
from pathlib import Path
import sys
import subprocess
import time


ENGINE = "LAYER_3_ENGINE_STUDIO_C14"
ROOT = Path(__file__).resolve().parents[4]
ENGINE_ROOT = ROOT / ENGINE
PROGRAMMATIC = ENGINE_ROOT / "FEATURE_PROGRAMMATIC"
sys.path.insert(0, str(ENGINE_ROOT))


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("native model refresh", 0)
    return remaining


def verify_project_model(project: Path, timeout: float, previous: str | None) -> str:
    from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project

    deadline = time.monotonic() + timeout
    control = select_runtime_project(project).control_root
    module = ("FEATURE_PROGRAMMATIC.FEATURE_MODEL."
              "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage")
    command = [sys.executable, "-B", "-P", "-m", module, str(project), str(control),
               str(_remaining(deadline))]
    if previous is not None:
        command.append(previous)
    environment = dict(os.environ)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONPATH"] = str(ENGINE_ROOT)
    result = subprocess.run(command, cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, text=True, timeout=_remaining(deadline), check=True)
    return result.stdout.strip()


if __name__ == "__main__":
    print(verify_project_model(Path(sys.argv[1]), float(sys.argv[2]),
                               sys.argv[3] if len(sys.argv) == 4 else None))
