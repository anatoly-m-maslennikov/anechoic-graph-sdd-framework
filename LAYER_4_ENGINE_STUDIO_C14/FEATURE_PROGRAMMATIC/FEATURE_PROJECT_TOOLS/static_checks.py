"""Run source gates used by the Test Suite and Local Release."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

from . import python_boundaries, python_bytecode, source_languages, source_line_length, source_sizes


CODE_ROOTS = ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "LAYER_5_USER_SETUP_C65")
FRAMEWORK = Path(__file__).resolve().parents[3]
ENGINE_CONFIG = "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
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


def _run(label, command, root, timeout):
    print(f"Static check: {label}", flush=True)
    try:
        return subprocess.run(command, cwd=root, check=False, timeout=timeout).returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Static check failed: {label}: {error}", file=sys.stderr)
        return 1


def _python_quality(root):
    ruff = (sys.executable, "-B", "-m", "ruff")
    yield _run("Ruff lint", (*ruff, "check", "--config", ENGINE_CONFIG, "--extend-select",
                            "F401,B006", "--no-fix", *CODE_ROOTS), root, 60)
    path = root / ENGINE_CONFIG
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8")).get("tool", {}) if path.is_file() else {}
    except (OSError, ValueError) as error:
        print(f"Static check failed: {ENGINE_CONFIG}: {error}", file=sys.stderr)
        yield 1
        return
    if "ruff" in config:
        yield _run("Ruff format", (*ruff, "format", "--check", "--config", ENGINE_CONFIG, *CODE_ROOTS), root, 60)
    if "mypy" in config:
        yield _run("Mypy", (sys.executable, "-B", "-m", "mypy", "--config-file", ENGINE_CONFIG), root, 120)


def _typed_web(root):
    try:
        for package, command in npm_static_commands(root):
            yield _run(f"npm run {command} in {package.relative_to(root)}",
                       ("npm", "run", command), package, 120)
    except (OSError, ValueError) as error:
        print(f"Static check failed: npm configuration: {error}", file=sys.stderr)
        yield 1


def check(root):
    boundary_scope = ("--import-component", "C14", "--require-state") if (
        root / CODE_ROOTS[0] / "FEATURE_PROGRAMMATIC"
    ).is_dir() else ()
    checks = [
        python_bytecode.check(root), *_python_quality(root), source_sizes.check(root),
        source_line_length.check(root), source_languages.check(root), python_boundaries.check(root),
        *_typed_web(root),
        _run("import ownership", (sys.executable, "-B", "-m", "IWE_CONSOLE_C43.APP_IWE_CONSOLE."
                                  "FEATURE_IMPORT_GRAPH_C61.import_ownership", str(root.resolve())),
             FRAMEWORK / CODE_ROOTS[0], 90),
        _run("Manifest boundaries", (sys.executable, "-B", "-m", "KERNEL_MIXER_C59.state_lint",
                                     str(root.resolve()), *boundary_scope), FRAMEWORK, 120),
    ]
    return int(any(checks))
