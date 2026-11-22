"""Resolve the configured functional test selection."""

import tomllib


def _select_test_modules(
    root: Path, discovered: list[Path], selected: tuple[str, ...]
) -> list[Path]:
    if not isinstance(selected, tuple):
        raise ValueError("test-module selection must be a tuple")
    if not selected:
        raise ValueError("test-module selection is empty")
    if any(not isinstance(module, str) or not module for module in selected):
        raise ValueError("test-module selection contains an invalid path")
    if len(set(selected)) != len(selected):
        raise ValueError("test-module selection contains duplicates")
    available = {module.relative_to(root).as_posix(): module for module in discovered}
    missing = [module for module in selected if module not in available]
    if missing:
        raise ValueError("test-module selection is not discovered: " + ", ".join(missing))
    return [available[module] for module in selected]


def functional_modules(root, discovered, is_docker):
    try:
        with (root / "pyproject.toml").open("rb") as file:
            config = tomllib.load(file)
        selected = config["tool"]["anechoic"]["test_suite"]["functional_test_modules"]
        if not isinstance(selected, list):
            raise ValueError("functional_test_modules must be a list")
        modules = _select_test_modules(root, discovered, tuple(selected))
        if any(is_docker(root, module) for module in modules):
            raise ValueError("functional_test_modules cannot include Docker tests")
        return modules
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"functional_test_modules configuration is invalid: {error}") from error
