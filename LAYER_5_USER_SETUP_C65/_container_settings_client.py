"""Access the isolated mounted container settings command."""

import json
from pathlib import Path
import subprocess
import sys

CONTAINER_SETTINGS_FILENAME = ".anechoic_runtime_config.toml"
_CONTAINER_CLI = (
    Path(__file__).resolve().parents[1]
    / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
    / "ADAPTERS_C30/container_settings_cli.py"
)


def _container_cli(action: str, root: Path, values: dict | None = None):
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(_CONTAINER_CLI), action, str(root)],
        input=json.dumps(values) if values is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 3:
        raise FileExistsError(root / CONTAINER_SETTINGS_FILENAME)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Invalid container settings")
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("Invalid container settings response") from error
    if document is not None and not isinstance(document, dict):
        raise ValueError("Invalid container settings response")
    if action == "create" and document is None:
        raise ValueError("Invalid container settings response")
    return document
