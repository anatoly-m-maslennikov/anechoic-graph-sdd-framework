"""Discovery and child process configuration for the test suite."""

import os
from pathlib import Path
import sys

from ..release_image.release_image__shared import (
    IMAGE_DEADLINES,
    image_deadline_mode,
)
from ..static_checks import CODE_ROOTS
from ._suite_runner_parser import _suite_parser as _suite_parser

CHILD = (
    "\nimport json, os, sys, unittest\nsys.path.exte"
    'nd(os.environ.pop("ANECHOIC_TEST_IMPORT_DIRS"'
    ").split(os.pathsep))\nsuite = unittest.default"
    "TestLoader.loadTestsFromName(sys.argv[1])\ncou"
    "nt = suite.countTestCases()\nresult = unittest"
    ".TextTestRunner(verbosity=2).run(suite)\nrequi"
    "red_skips = [(test.id(), reason) for test, re"
    "ason in result.skipped\n                  if l"
    'en(sys.argv) > 2 or "_e2e" in sys.argv[1] or '
    '"_e2e." in test.id()]\nif required_skips:\n    '
    'label = "functional" if len(sys.argv) > 2 els'
    'e "integration"\n    print("Required " + label'
    ' + " tests skipped: " + repr(required_skips),'
    ' file=sys.stderr)\nprint("ANECHOIC_TEST_COUNTS'
    ' " + json.dumps({"tests": result.testsRun, "s'
    'kipped": len(result.skipped)}))\nif not count:'
    '\n    print("No test cases loaded", file=sys.s'
    "tderr)\nsys.exit(0 if count and result.wasSucc"
    "essful() and not required_skips else 1)\n"
)


def discover_test_modules(root: Path) -> list[Path]:
    """Select source test modules and exclude caches and fixture copies."""

    def failed(error: OSError) -> None:
        raise error

    modules = []
    for name in CODE_ROOTS:
        source = root / name
        if source.is_symlink() or not source.is_dir():
            raise OSError(f"source test root is unavailable: {source}")
        for folder, directories, filenames in os.walk(
            source, followlinks=False, onerror=failed
        ):
            directory = Path(folder)
            parts = directory.relative_to(source).parts
            test_package = directory.name == directory.parent.name + "__tests"
            directories[:] = [
                entry
                for entry in directories
                if not entry.startswith(".")
                and entry != "__pycache__"
                and not (test_package and entry == "assets")
                and not (entry == "tests" and "tests" in parts)
            ]
            for entry in directories:
                if (Path(folder) / entry).is_symlink():
                    raise OSError(
                        "source test directory is a symbolic link: "
                        f"{Path(folder) / entry}"
                    )
            for filename in filenames:
                path = Path(folder) / filename
                if not (
                    filename.startswith("test_")
                    and path.suffix == ".py"
                    and path.stem.isidentifier()
                    and not path.stem.endswith(("__pub", "__shared"))
                ):
                    continue
                if path.is_symlink():
                    raise OSError(f"test module is a symbolic link: {path}")
                modules.append(path)
    return sorted(modules)


def _module_environment(child, environment, *, image_module):
    inherited = os.environ if environment is None else environment
    environment = {
        key: value
        for key, value in inherited.items()
        if key not in ("PYTHONHOME", IMAGE_DEADLINES)
    }
    environment.update(
        ANECHOIC_DOCKER_E2E="1",
        ANECHOIC_DOCKER_QUERY_E2E="1",
        PYTHONPATH=str(child),
    )
    if image_module:
        environment[IMAGE_DEADLINES] = image_deadline_mode(inherited)
    return environment


def _uv_command(child, environment):
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("UV_COMPILE_BYTECODE", None)
    environment["UV_PROJECT_ENVIRONMENT"] = str(
        child
        / (
            ".venv-release"
            if child.as_posix().endswith(CODE_ROOTS[1])
            else ".venv-setup"
        )
    )
    command = (
        "uv",
        "run",
        "--no-compile-bytecode",
        "--project",
        str(
            (
                child.parent.parent
                if child.as_posix().endswith(CODE_ROOTS[1])
                else child.parent
            )
            / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72"
            / (
                "release"
                if child.as_posix().endswith(CODE_ROOTS[1])
                else "setup"
            )
        ),
        "--locked",
        "--no-env-file",
        "--python",
        "3.14",
        "--managed-python",
        "python",
        "-B",
    )
    return command


def _module_command(child, module, environment, required):
    name = ".".join(module.relative_to(child).with_suffix("").parts)
    command = (sys.executable, "-B")
    if child.name != CODE_ROOTS[0]:
        command = _uv_command(child, environment)
    return (
        *command,
        "-P",
        "-c",
        CHILD,
        name,
        *(("required",) if required else ()),
    )


def _report_scope(root, phase, test_modules, host_gate, image_suite, modules):
    scope = phase if test_modules is None else "focused"
    if test_modules is not None:
        selection = ", ".join(test_modules)
    elif host_gate or image_suite == "fast":
        selection = ", ".join(
            module.relative_to(root).as_posix() for module in modules
        )
    else:
        selection = (
            "all discovered modules" if phase == "full" else f"{phase} modules"
        )
    print(f"Test scope: {scope}; selected modules: {selection}")
