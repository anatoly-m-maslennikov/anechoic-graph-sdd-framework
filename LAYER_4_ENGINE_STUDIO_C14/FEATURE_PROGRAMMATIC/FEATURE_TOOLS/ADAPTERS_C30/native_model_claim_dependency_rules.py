"""Validate population functional dependency rules."""

import re

from .native_model_claim_values import _fail


def _validate_dependency_paths(dependency, declaration):
    for part in (dependency["keys"], dependency["dependents"]):
        if (
            not isinstance(part, (tuple, list))
            or not part
            or any(
                not isinstance(path, str)
                or not re.fullmatch(
                    r"[A-Za-z_][A-Za-z_0-9 -]*"
                    r"(?:\.[A-Za-z_][A-Za-z_0-9 -]*)*",
                    path,
                )
                or path != path.strip()
                or any(
                    segment != segment.strip() for segment in path.split(".")
                )
                for path in part
            )
            or len(part) != len(set(part))
        ):
            _fail(
                declaration,
                "functional dependency paths must be distinct "
                "nonempty relative Property paths",
            )


def _validate_dependency_rules(dependencies, population, declaration):
    seen = set()
    for dependency in dependencies:
        if (
            not isinstance(dependency, dict)
            or not {"keys", "dependents"} <= set(dependency)
            or set(dependency) - {"keys", "dependents", "status_groups"}
        ):
            _fail(
                declaration,
                "functional dependency requires keys and dependents",
            )
        if "status_groups" in dependency:
            groups = dependency["status_groups"]
            if (
                population != "Atom"
                or not isinstance(groups, (tuple, list))
                or not groups
                or any(
                    not isinstance(group, str)
                    or group not in {"Current", "Backlog", "Archived", "Draft"}
                    for group in groups
                )
                or len(groups) != len(set(groups))
            ):
                _fail(
                    declaration,
                    "status_groups requires distinct admitted Atom "
                    "Status Groups",
                )
        _validate_dependency_paths(dependency, declaration)
        signature = (
            tuple(dependency["keys"]),
            tuple(dependency["dependents"]),
            tuple(dependency.get("status_groups", ())),
        )
        if signature in seen:
            _fail(declaration, "duplicate functional dependency")
        seen.add(signature)
