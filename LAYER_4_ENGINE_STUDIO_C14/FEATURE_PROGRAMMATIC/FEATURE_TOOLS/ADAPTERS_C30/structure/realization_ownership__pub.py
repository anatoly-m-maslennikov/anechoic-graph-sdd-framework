"""Map admitted Structure owners to inventoried Python paths."""

from dataclasses import replace
from pathlib import Path, PurePosixPath

from pydantic import ConfigDict, field_validator
from pydantic.dataclasses import dataclass

from ..carriers.header.native_carrier_placement__pub import component_manifest_parent
from ..structure.structure_snapshot__pub import _preserve_mapping


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class CodeAccessOwnership:
    entries: dict
    by_path: dict

    _validate_indexes = field_validator("entries", "by_path", mode="wrap")(
        _preserve_mapping
    )

    def owner(self, path, kind="module"):
        path = PurePosixPath(path)
        if kind == "module":
            path = path.parent
        while True:
            owner = self.by_path.get(path.as_posix())
            if owner is not None:
                return self.entries[owner]
            if path == path.parent:
                return None
            path = path.parent


def _component_path(control, cid, component, parent, paths, parameters):
    candidates = {
        path
        for path in paths
        if path != parent
        and path.is_relative_to(parent)
        and path.name.endswith("_" + cid)
    }
    source_parent = component_manifest_parent(
        PurePosixPath(component.source_path), parameters
    )
    native_parent = control / source_parent
    native = [
        p.name
        for p in native_parent.iterdir()
        if not p.is_symlink() and p.is_dir() and p.name.endswith("_" + cid)
    ]
    if len(native) > 1:
        raise ValueError(f"Ambiguous native Component path: {cid}")
    if native:
        alias = native[0].removesuffix("_" + cid)
        candidates.update(
            path
            for path in paths
            if path != parent
            and path.is_relative_to(parent)
            and path.name == alias
        )
    if len(candidates) > 1:
        raise ValueError(f"Ambiguous Component path: {cid}")
    return next(iter(candidates), None)


def _add_component_paths(control, snapshot, paths, entries, add):
    parameters = snapshot.project.get("parameters")
    remaining = dict(snapshot.components)
    while remaining:
        ready = [
            (cid, component)
            for cid, component in remaining.items()
            if component.parent == "C00" or component.parent not in remaining
        ]
        if not ready:
            raise ValueError("Component parent cycle")
        for cid, component in ready:
            del remaining[cid]
            if component.parent not in entries:
                continue
            parent_path = PurePosixPath(entries[component.parent]["path"])
            path = _component_path(
                control, cid, component, parent_path, paths, parameters
            )
            if path is not None:
                add(cid, component.parent, path, "component", component.fields)


def build_code_access_ownership(
    root, control_root, snapshot, package_paths, *, allow_unrealized=False
):  # noqa: C901
    """Return owners for resolved paths; never infer a \
declared ID from a name."""
    root, control = Path(root), Path(control_root)
    paths = {PurePosixPath(path) for path in package_paths}
    if any(path.is_absolute() or ".." in path.parts for path in paths):
        raise ValueError("Python package paths must be project-relative")
    entries = {
        "C00": {
            "id": "C00",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": snapshot.project,
        }
    }
    by_path = {".": "C00"}

    def add(identity, parent, path, kind, fields):
        path = path.as_posix()
        if identity in entries or path in by_path:
            raise ValueError(
                f"Duplicate owner identity or path: {identity} {path}"
            )
        entries[identity] = {
            "id": identity,
            "parent": parent,
            "path": path,
            "kind": kind,
            "fields": fields,
        }
        by_path[path] = identity

    _add_component_paths(control, snapshot, paths, entries, add)

    _add_packages(root, snapshot, entries, add, allow_unrealized)

    _add_remaining_paths(paths, by_path, add)
    return CodeAccessOwnership(entries, by_path)


def realization_component_paths(root, control_root, snapshot, folders):
    """Map realized Component paths using inventoried source ancestors."""
    candidates = {
        ancestor
        for folder in map(PurePosixPath, folders)
        for ancestor in (folder, *folder.parents)
    }
    ownership = build_code_access_ownership(
        root, control_root, replace(snapshot, packages={}), candidates
    )
    return {
        owner["path"]: owner["id"]
        for owner in ownership.entries.values()
        if owner["kind"] == "component"
    }


def _add_packages(root, snapshot, entries, add, allow_unrealized):
    for package_id, package in snapshot.packages.items():
        if package.component not in entries:
            if allow_unrealized:
                continue
            raise ValueError(
                "Missing Component realization for Component Seed: "
                f"{package_id}"
            )
        parent_path = PurePosixPath(entries[package.component]["path"])
        directory = root / parent_path
        candidates = [
            parent_path / p.name
            for p in directory.iterdir()
            if not p.is_symlink()
            and p.is_dir()
            and p.name.endswith("_" + package_id)
        ]
        if not candidates and allow_unrealized:
            continue
        if len(candidates) != 1:
            raise ValueError(
                "Missing or ambiguous Component Seed realization path: "
                f"{package_id}"
            )
        add(
            package_id,
            package.component,
            candidates[0],
            "package",
            package.fields,
        )


def _add_remaining_paths(paths, by_path, add):
    for path in sorted(paths, key=lambda p: (len(p.parts), p.as_posix())):
        if path.as_posix() in by_path:
            continue
        parent = path.parent
        while parent.as_posix() not in by_path:
            parent = parent.parent
        add(path.as_posix(), by_path[parent.as_posix()], path, "package", {})
