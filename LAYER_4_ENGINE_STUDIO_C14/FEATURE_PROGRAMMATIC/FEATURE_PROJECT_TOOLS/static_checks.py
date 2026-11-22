"""Run source gates used by the Test Suite and Local Release."""

from pathlib import Path
import subprocess
import sys

from . import python_boundaries, python_bytecode, source_sizes


CODE_ROOTS = ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_5_FRAMEWORK_DELIVERY", "LAYER_6_RUNTIME_SETUP")
FRAMEWORK = Path(__file__).resolve().parents[3]


def check(root):
    if python_bytecode.check(root):
        return 1
    print("Static check: unused Python imports", flush=True)
    try:
        status = subprocess.run(
            (sys.executable, "-B", "-m", "ruff", "check", "--config",
             "LAYER_3_ENVIRONMENTS_C72/engine/pyproject.toml", "--select", "F401", "--no-fix", *CODE_ROOTS),
            cwd=root, check=False, timeout=60,
        ).returncode
        if status or source_sizes.check(root) or python_boundaries.check(root):
            return 1
        print("Static check: import ownership", flush=True)
        ownership = subprocess.run(
            (sys.executable, "-B", "-m", "LAYER_4_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH."
             "FEATURE_IMPORT_GRAPH_C61.import_ownership", str(root.resolve())),
            cwd=FRAMEWORK, check=False, timeout=90,
        ).returncode
        if ownership:
            return ownership
        print("Static check: state boundaries", flush=True)
        return subprocess.run(
            (sys.executable, "-B", "-m", "KERNEL_MIXER_C59.state_lint", str(root.resolve())),
            cwd=FRAMEWORK, check=False, timeout=120,
        ).returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Static check failed: {error}", file=sys.stderr)
        return 1
