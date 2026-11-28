"""Support native carrier capture."""

from pathlib import PurePosixPath
from ...sources.capture.native_capture_types import NativeCapture
from ...carriers.header.native_carrier_placement__pub import project_goal_filename


def _changed_scopes(root, control, selection, paths):
    scopes = set()
    for relative in paths:
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid changed carrier path")
        if (
            (root / relative).is_relative_to(control)
            or root / relative == selection.manifest_path
            or (
                relative.parent == PurePosixPath(".")
                and project_goal_filename(relative.name)
            )
        ):
            scopes.add(relative)
    return scopes


def _changed_inputs(reader, selection, previous, paths):
    root, control = selection.root, selection.control_root
    scopes = _changed_scopes(root, control, selection, paths)
    changed, directories = set(), set()
    previous_paths = {
        row["source_path"] for row in previous.atoms
    } | previous.errors.keys()
    for relative in scopes:
        if any(parent in scopes for parent in relative.parents):
            continue
        path = root / relative
        name = relative.as_posix()
        changed.update(
            item for item in previous_paths if item.startswith(name + "/")
        )
        if relative.suffix == ".md":
            changed.add(name)
        if path.is_dir():
            directories.add(name)
            changed.update(
                item.relative_to(root).as_posix()
                for item in reader.inventory(path)
                if item.suffix == ".md"
            )
    candidates = {
        row["source_path"]: (row, edge)
        for row, edge in zip(previous.atoms, previous.containment)
        if row["source_path"] not in changed
    }
    errors = {
        path: error
        for path, error in previous.errors.items()
        if path not in changed
    }
    return (
        candidates,
        errors,
        [root / path for path in sorted(changed - directories)],
    )


def _issue(relative_path, code, message, atom_ref=None, related_paths=None):
    return {
        "relative_path": relative_path,
        "code": code,
        "message": message,
        "atom_ref": atom_ref,
        "related_paths": related_paths or [],
    }


def _record_duplicates(
    revisions, currents, candidates, errors, issues, manifest_path
):
    for groups, code in (
        (revisions, "duplicate_revision"),
        (currents, "duplicate_current"),
    ):
        for paths in groups.values():
            if len(paths) < 2:
                continue
            for path in paths:
                if path == manifest_path:
                    continue
                message = "Duplicate native revision or Current identity"
                issues.append(
                    _issue(
                        path,
                        code,
                        message,
                        candidates[path][0]["_exact_ref"],
                        paths,
                    )
                )
                errors[path] = message


def _unique_revisions(
    candidates,
    errors,
    versions,
    issues,
    hashes,
    manifest_path,
    domains,
    classified,
):
    rows, containment = [], []
    revisions, currents = {}, {}
    ordered = sorted(candidates.items())
    for relative, (row, _) in ordered:
        revisions.setdefault(row["_exact_ref"], []).append(relative)
        if row["status_group"] == "Current":
            currents.setdefault(row["id"], []).append(relative)
    _record_duplicates(
        revisions, currents, candidates, errors, issues, manifest_path
    )
    for relative, (row, edge) in ordered:
        if relative in errors:
            continue
        rows.append(row)
        containment.append(edge)
    issues.sort(key=lambda item: (item["relative_path"] or "", item["code"]))
    classified = {
        path: value for path, value in classified.items() if path in errors
    }
    return NativeCapture(
        rows,
        containment,
        errors,
        versions,
        ingestion_issues=issues,
        carrier_hashes=hashes,
        status_domains=domains,
        classified_templates=classified,
    )
