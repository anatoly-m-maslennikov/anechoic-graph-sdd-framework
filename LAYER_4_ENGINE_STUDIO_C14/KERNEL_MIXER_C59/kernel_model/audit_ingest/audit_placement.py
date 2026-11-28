"""Compare declared and physical Atom carrier placement."""

from pathlib import Path
import os


def _check_placement(
    row,
    file,
    scope_paths,
    role_folders,
    placement_audit,
    add,
    result,
    header_value,
    filename_issue,
    declared_table,
    physical_table,
):
    header = row.get("header_json")
    if not isinstance(header, dict):
        return
    _, destination = header_value(header, "destination")
    declared = (
        destination.get("file") if isinstance(destination, dict) else None
    )
    declared = declared if isinstance(declared, dict) else {}
    declared_path = declared.get("path")
    expected_name, expected_path = (
        placement_audit(row) if placement_audit is not None else (None, None)
    )
    _check_name(
        row,
        declared,
        declared_path,
        role_folders,
        expected_name,
        filename_issue,
        add,
        declared_table,
    )
    _, container = header_value(header, "container")
    owner = (
        container.get("scope_unit") if isinstance(container, dict) else None
    )
    owner_path = scope_paths.get(owner) if isinstance(owner, str) else None
    _check_path(declared_path, expected_path, owner_path, add, declared_table)
    if not result[declared_table]:
        _check_physical(file, declared, add, physical_table)


def _check_name(
    row,
    declared,
    declared_path,
    role_folders,
    expected_name,
    filename_issue,
    add,
    declared_table,
):
    if expected_name is not None and declared.get("name") != expected_name:
        add(
            declared_table,
            "declared_carrier_inconsistency",
            "file.name",
            declared.get("name"),
            expected_name,
            "Declared filename differs from the placement formula.",
        )
    elif expected_name is None and (
        issue := filename_issue(
            declared.get("name"), declared_path, row, role_folders
        )
    ):
        add(declared_table, "declared_carrier_inconsistency", *issue)


def _check_path(declared_path, expected_path, owner_path, add, declared_table):
    if expected_path is not None and declared_path != expected_path:
        add(
            declared_table,
            "declared_carrier_inconsistency",
            "file.path",
            declared_path,
            expected_path,
            "Declared path differs from the placement formula.",
        )
    elif (
        expected_path is None
        and owner_path is not None
        and isinstance(declared_path, str)
        and not Path(os.path.normpath(declared_path)).is_relative_to(
            Path(os.path.normpath(owner_path))
        )
    ):
        add(
            declared_table,
            "declared_carrier_inconsistency",
            "file.path",
            declared_path,
            owner_path,
            "Declared carrier path is outside its owning Scope Unit.",
        )


def _check_physical(file, declared, add, physical_table):
    for key, actual in (
        ("name", file.name),
        ("path", file.parent.as_posix()),
    ):
        expected = declared.get(key)
        if expected != actual:
            add(
                physical_table,
                "physical_carrier_mismatch",
                f"file.{key}",
                actual,
                expected,
                f"Actual carrier {key} differs from its declaration.",
            )
