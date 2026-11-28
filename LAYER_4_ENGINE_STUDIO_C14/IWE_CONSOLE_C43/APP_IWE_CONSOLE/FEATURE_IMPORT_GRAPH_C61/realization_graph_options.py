"""Validate Python image import options."""

from dataclasses import fields
import json
import keyword
import re
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 \
    .structure.structure__shared import (
    parse_structure,
    realization_component_paths,
)
# fmt: on


def _options(root, config):
    if not isinstance(config, dict) or set(config) - {
        "include",
        "python_roots",
        "python_image_imports",
    }:
        raise ValueError("import_graph must contain only supported options")
    result = []
    for name, default in (("python_roots", None), ("include", [])):
        values = config.get(name, default)
        if name == "python_roots" and name not in config:
            result.append(None)
            continue
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values
        ):
            raise ValueError(
                f"import_graph.{name} must be a list of Project-relative paths"
            )
        for value in values:
            path = Path(value)
            if (
                path.is_absolute()
                or ".." in path.parts
                or not (root / path).resolve().is_relative_to(root)
            ):
                raise ValueError(
                    f"import_graph.{name} paths must be inside the Project"
                )
            if name == "include" and (
                path == Path(".") or (root / path).is_dir()
            ):
                raise ValueError(
                    "import_graph.include paths must name source files"
                )
        result.append(tuple(values))
    return result[0], result[1], _image_imports(root, config)


def _image_imports(root, config):
    images = config.get("python_image_imports", {})
    if not isinstance(images, dict):
        raise ValueError("import_graph.python_image_imports must be a mapping")
    for value, modules in images.items():
        if not isinstance(value, str) or not value:
            raise ValueError(
                "import_graph.python_image_imports"
                " keys must name Python source files"
            )
        path = Path(value)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not (root / path).resolve().is_relative_to(root)
        ):
            raise ValueError(
                "import_graph.python_image_imports"
                " paths must be inside the Project"
            )
        if (
            path.as_posix() != value
            or path.suffix != ".py"
            or (root / path).is_dir()
        ):
            raise ValueError(
                "import_graph.python_image_imports"
                " keys must name Python source files"
            )
        if not isinstance(modules, list) or any(
            not isinstance(module, str)
            or not module
            or any(
                not part.isidentifier() or keyword.iskeyword(part)
                for part in module.split(".")
            )
            for module in modules
        ):
            raise ValueError(
                "import_graph.python_image_imports"
                " values must be lists of dotted "
                "Python module names"
            )
    return {path: tuple(modules) for path, modules in images.items()}


def _structure(request, root, sources):
    components, snapshot, control = None, None, None
    if "structure" in request:
        control = request["control_root"]
        if (
            not isinstance(control, str)
            or not control
            or Path(control).is_absolute()
            or len(Path(control).parts) != 1
            or control in {".", ".."}
            or (root / control).is_symlink()
            or not (root / control).is_dir()
        ):
            raise ValueError(
                "control_root must name a Project control directory"
            )
        snapshot = parse_structure(json.dumps(request["structure"]).encode())
        folders = {Path(path).parent for path in sources}
        components = realization_component_paths(
            root, root / control, snapshot, folders
        )
    return components, snapshot, control


_SAFE_PATH = re.compile(r"[A-Za-z0-9_./-]{1,256}")
_PRIVATE_PATH = re.compile(
    r"\.env\b|\.ssh\b|password|passwd|secret|token|api[_-]?key|"
    r"authorization|bearer",
    re.I,
)


def _first_difference(before, after):
    for path, old in before.items():
        if path not in after:
            return _difference(path, "removed")
        new = after[path]
        if old != new:
            changed = (
                ["stat_signature"]
                if isinstance(old, str)
                else [
                    field.name
                    for field in fields(old)
                    if getattr(old, field.name) != getattr(new, field.name)
                ]
            )
            return _difference(path, "changed", changed)
    return _difference(
        next(path for path in after if path not in before), "added"
    )


def _difference(path, change, changed=()):
    report = {"change": change}
    if (
        _SAFE_PATH.fullmatch(path)
        and not path.startswith("/")
        and ".." not in path.split("/")
        and not _PRIVATE_PATH.search(path)
    ):
        report["path"] = path
    if changed:
        report["fields"] = changed
    return report
