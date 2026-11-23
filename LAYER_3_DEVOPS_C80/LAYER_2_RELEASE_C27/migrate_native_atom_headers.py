#!/usr/bin/env -S python3 -B
"""Run the native Atom header migration with the Engine project."""

import os
from pathlib import Path
import sys


def main():
    engine = Path(__file__).resolve().parents[2] / "LAYER_4_ENGINE_STUDIO_C14"
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = str(engine / ".venv-dev")
    env["PYTHONPATH"] = str(engine)
    command = [
        "uv", "run", "--project", str(engine.parent / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"), "--locked", "--no-env-file",
        "--python", "3.14", "--managed-python", "--group", "dev", "python",
        "-X", f"pycache_prefix={engine.parent}/.anechoic_tmp/python/bytecode", "-P", "-m",
        "FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.migrate_native_atom_headers", *sys.argv[1:],
    ]
    os.execvpe(command[0], command, env)


if __name__ == "__main__":
    main()
