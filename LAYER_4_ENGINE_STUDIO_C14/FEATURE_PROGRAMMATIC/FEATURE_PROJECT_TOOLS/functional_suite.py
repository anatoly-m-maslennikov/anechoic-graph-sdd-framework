"""Resolve Test Suite phase and module selections."""

from pathlib import Path
import re
import tomllib

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_config import load_suite_config

from .full_suite_docker import APP

WORKBENCH = Path("LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH")
WORKBENCH_TESTS = WORKBENCH / (WORKBENCH.name + "__tests")
MCP_TESTS = APP / (APP.name + "__tests")


def _test_phase(root: Path, module: Path) -> str:
    """Classify explicit phase folders beneath a canonical Component test package."""
    parts = module.relative_to(root).parts
    for index in range(1, len(parts) - 1):
        if parts[index] == parts[index - 1] + "__tests" and index + 1 < len(parts) - 1:
            if parts[index + 1] in ("static", "unit", "image"):
                return parts[index + 1]
    if module.parent in (root / MCP_TESTS, root / WORKBENCH_TESTS) and (
        module.stem.endswith("_docker_e2e") or module.stem == "test_selected_query_mcp_e2e"
    ):
        return "image"
    return "unit"


def valid_test_request(phase, candidate_image, test_modules, required):
    return (phase in ("full", "static", "unit", "functional", "e2e", "image")
            and (phase in ("e2e", "image")) == (candidate_image is not None)
            and (candidate_image is None or isinstance(candidate_image, str)
                 and re.fullmatch(r"sha256:[0-9a-f]{64}", candidate_image) is not None)
            and (test_modules is None or phase in ("full", "unit"))
            and (not required or phase == "unit" and test_modules is None))


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


def _required_unit_modules(root, discovered):
    try:
        config = load_suite_config(root)
        selected = config["tool"]["anechoic"]["test_suite"]["functional_test_modules"]
        if not isinstance(selected, list):
            raise ValueError("functional_test_modules must be a list")
        modules = _select_test_modules(root, discovered, tuple(selected))
        phases = {_test_phase(root, module) for module in modules}
        if "image" in phases:
            raise ValueError("functional_test_modules cannot include Docker tests")
        if phases != {"unit"}:
            raise ValueError("functional_test_modules must select unit tests")
        return modules
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"functional_test_modules configuration is invalid: {error}") from error


def select_phase_modules(root, discovered, phase, focused, required):
    if required:
        return _required_unit_modules(root, discovered)
    if phase != "full":
        phase = "image" if phase == "e2e" else phase
        discovered = [module for module in discovered if _test_phase(root, module) == phase]
    return _select_test_modules(root, discovered, focused) if focused is not None else discovered
