"""Run source gates used by the Test Suite and Local Release."""

import json
import os
from pathlib import Path
import subprocess
import sys

from . import python_boundaries, python_bytecode, source_languages, source_sizes


CODE_ROOTS = ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "LAYER_5_USER_SETUP_C65")
FRAMEWORK = Path(__file__).resolve().parents[3]
ESLINT_CONFIGS = ("eslint.config.js", "eslint.config.mjs", "eslint.config.cjs",
                  "eslint.config.ts", "eslint.config.mts", "eslint.config.cts",
                  ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json",
                  ".eslintrc.yaml", ".eslintrc.yml")


def npm_static_commands(root):
    """Find package-owned type checks and configured TypeScript lint commands."""
    for name in CODE_ROOTS:
        for folder, dirs, files in os.walk(root / name, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                             and d.casefold() not in python_boundaries._EXCLUDED
                             and not (Path(folder) / d).is_symlink())
            if "package.json" not in files:
                continue
            package = Path(folder)
            data = json.loads((package / "package.json").read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            if scripts.get("check:types"):
                yield package, "check:types"
            dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            typed = "typescript-eslint" in dependencies or "@typescript-eslint/eslint-plugin" in dependencies
            configured = "eslintConfig" in data or any((package / config).is_file() for config in ESLINT_CONFIGS)
            if typed and "eslint" in dependencies and configured and scripts.get("lint"):
                yield package, "lint"


def check(root):
    if python_bytecode.check(root):
        return 1
    print("Static check: Python imports and mutable defaults", flush=True)
    try:
        status = subprocess.run(
            (sys.executable, "-B", "-m", "ruff", "check", "--config",
             "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml", "--select", "F401,B006", "--no-fix", *CODE_ROOTS),
            cwd=root, check=False, timeout=60,
        ).returncode
        if status or source_sizes.check(root) or source_languages.check(root) or python_boundaries.check(root):
            return 1
        for package, command in npm_static_commands(root):
            print(f"Static check: npm run {command} in {package.relative_to(root)}", flush=True)
            if subprocess.run(("npm", "run", command), cwd=package, check=False, timeout=120).returncode:
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
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Static check failed: {error}", file=sys.stderr)
        return 1
