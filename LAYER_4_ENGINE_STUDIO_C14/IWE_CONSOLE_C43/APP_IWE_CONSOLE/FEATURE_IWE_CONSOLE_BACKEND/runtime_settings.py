"""Read the legacy Workbench Header schema mode."""

from __future__ import annotations

from pathlib import Path
import tomllib

DEFAULT_SCHEMA_MODE = 2


def schema_mode(root: Path) -> int:
    "Return the selected cold-start schema mode without a public query option."
    path = Path(root) / ".anechoic_runtime" / "anechoic_runtime_settings.toml"
    if not path.exists():
        return DEFAULT_SCHEMA_MODE

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
        import read_settings_carrier  # fmt: skip

    try:
        document = read_settings_carrier(path)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError("invalid Workbench runtime settings") from error
    workbench = document.get("workbench", {})
    if not isinstance(workbench, dict):
        raise ValueError("invalid Workbench runtime settings")
    value = workbench.get("schema_mode", DEFAULT_SCHEMA_MODE)
    if type(value) is not int or value not in {1, 2}:
        raise ValueError("workbench.schema_mode must be 1 or 2")
    return value
