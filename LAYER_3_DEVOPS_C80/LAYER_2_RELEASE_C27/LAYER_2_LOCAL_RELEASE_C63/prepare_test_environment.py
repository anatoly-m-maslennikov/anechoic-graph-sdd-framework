"""Prepare the selected checkout's pinned Engine test environment."""

import os
from pathlib import Path
import subprocess
import sys

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError, _project_path, _root

from .local_release_gates import _SUITE, _gate_command, _test_environment


_ENGINE = Path("LAYER_4_ENGINE_STUDIO_C14")
_PROJECT = Path("LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine")
_FRONTEND = _ENGINE / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
_CACHE = Path(".anechoic_tmp/workbench")
_EXTENSION_ENV = "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY"
_INSTALL_DUCKPGQ = """import sys
import duckdb

with duckdb.connect(config={"extension_directory": sys.argv[1]}) as connection:
    connection.execute("INSTALL duckpgq FROM community")
"""


def _commands(root):
    for source in (_PROJECT / "pyproject.toml", _PROJECT / "uv.lock", _ENGINE / _SUITE,
                   _FRONTEND / "package.json", _FRONTEND / "package-lock.json"):
        path = _project_path(root, source, label="prepare-environment-input", require_exists=True)
        if not path.is_file():
            raise LocalReleaseError(f"local-release-prepare-environment-input-invalid: {source}")

    engine = root / _ENGINE
    frontend = root / _FRONTEND
    venv = _project_path(root, _ENGINE / ".venv-dev", label="prepare-environment-venv")
    _project_path(root, _FRONTEND / "node_modules", label="prepare-environment-node-modules")
    browsers = _project_path(root, _CACHE / "playwright-browsers", label="prepare-environment-browsers")
    override = os.environ.get(_EXTENSION_ENV)
    if override == "":
        raise LocalReleaseError("local-release-prepare-environment-extension-override-empty")
    extensions = (root / override if override is not None else
                  _project_path(root, _CACHE / "extensions", label="prepare-environment-extensions"))

    env = _test_environment(engine)
    for key in env.keys() & {"UV_WORKING_DIR", "UV_ENV_FILE", "NODE_PATH", _EXTENSION_ENV,
                             "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"}:
        del env[key]
    for key in tuple(env):
        if key.lower() in {"npm_config_prefix", "npm_config_global", "npm_config_workspace", "npm_config_workspaces"}:
            del env[key]
    env.update(PLAYWRIGHT_BROWSERS_PATH=str(browsers), npm_config_global="false")

    commands = [
        ("engine_dependencies", ("uv", "sync", "--project", str(root / _PROJECT), "--locked", "--all-groups",
                                 "--python", "3.14", "--managed-python"), root),
        ("frontend_dependencies", ("npm", "ci", "--include=dev"), frontend),
        ("chromium", ("node", "node_modules/playwright/cli.js", "install", "chromium"), frontend),
    ]
    if override is None:
        commands.append(("duckpgq", (str(venv / "bin/python"), "-I", "-B", "-c",
                                     _INSTALL_DUCKPGQ, str(extensions)), root))
    commands.append(("preflight", _gate_command(root, "preflight", engine, True), root))
    return env, commands, extensions


def prepare_test_environment(root: Path | str) -> dict[str, object]:
    """Prepare prerequisites and run the selected checkout's read-only preflight."""
    completed = []
    result = {"outcome": "failed", "project_root": str(root), "completed_steps": completed,
              "failed_step": "validate_paths"}
    try:
        root = _root(root)
        result["project_root"] = str(root)
        env, commands, extensions = _commands(root)
        for stage, command, cwd in commands:
            result["failed_step"] = stage
            if stage == "duckpgq":
                extensions.mkdir(parents=True, exist_ok=True)
            command_env = env | {_EXTENSION_ENV: str(extensions)} if stage == "preflight" else env
            subprocess.run(command, cwd=cwd, env=command_env, stdin=subprocess.DEVNULL, stdout=sys.stderr,
                           stderr=subprocess.STDOUT, check=True)
            completed.append(stage)
    except (LocalReleaseError, OSError, subprocess.SubprocessError) as error:
        return result | {"error_type": type(error).__name__, "error": str(error)}
    return result | {"outcome": "completed", "failed_step": None}
