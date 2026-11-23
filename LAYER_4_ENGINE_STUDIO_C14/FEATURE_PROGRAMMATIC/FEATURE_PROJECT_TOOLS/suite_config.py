"""Read the project test suite configuration."""

from pathlib import Path
import tomllib


def load_suite_config(root: Path) -> dict:
    engine = root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
    try:
        with engine.open("rb") as file:
            config = tomllib.load(file)
    except FileNotFoundError:
        config = {}
    tool = config.get("tool", {})
    anechoic = tool.get("anechoic", {}) if isinstance(tool, dict) else {}
    if isinstance(anechoic, dict) and "test_suite" in anechoic:
        return config
    with (root / "pyproject.toml").open("rb") as file:
        return tomllib.load(file)
