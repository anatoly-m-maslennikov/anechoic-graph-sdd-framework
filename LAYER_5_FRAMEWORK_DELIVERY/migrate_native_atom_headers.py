#!/usr/bin/env python3
"""Run the native Atom header migration with the Engine project."""

import os
from pathlib import Path
import sys


def main():
    engine = Path(__file__).resolve().parents[1] / "LAYER_3_ENGINE_STUDIO_C14"
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = ".venv-dev"
    env["PYTHONPATH"] = str(engine)
    command = [
        "uv", "run", "--project", str(engine), "--locked", "--no-env-file",
        "--python", "3.14", "--managed-python", "--group", "dev", "python", "-P", "-m",
        "FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.migrate_native_atom_headers", *sys.argv[1:],
    ]
    os.execvpe(command[0], command, env)


if __name__ == "__main__":
    main()
