"""Input and carrier helpers shared by the six Atom Lifecycle workflows."""

from __future__ import annotations

import os
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import open_regular  # fmt: skip

from . import effects


class InputError(ValueError):
    def __init__(self, field, message, *, format=None, allowed_values=None):
        super().__init__(message)
        self.field = field
        self.detail = {"error": message}
        if allowed_values is not None:
            self.detail["allowed_values"] = sorted(allowed_values)
        if format is not None or allowed_values is None:
            self.detail["format"] = format or "valid value"
        self.requested_input = {field: self.detail}

    @classmethod
    def combine(cls, errors):
        first = errors[0]
        first.requested_input = {
            field: detail
            for error in errors
            for field, detail in error.requested_input.items()
        }
        return first


class SourceChanged(ValueError):
    pass


def next_native_number(selection, capture, family):
    maxima = getattr(capture, "max_numbers", None)
    if maxima is not None:
        if family not in maxima:
            raise SourceChanged(
                "Admitted lifecycle context lacks the Atom number."
            )
        return maxima[family] + 1
    pattern = re.compile(
        re.escape(selection.project_prefix) + rf"-{family}-([0-9]+)"
    )
    return (
        max(
            (
                int(match[1])
                for row in capture.atoms
                if isinstance(row.get("id"), str)
                and (match := pattern.fullmatch(row["id"]))
            ),
            default=0,
        )
        + 1
    )


_SUMMARY = re.compile(
    r"(?m)^## Summary[ \t]*\r?\n(?:[ \t]*\r?\n)*([^\r\n]+)[ \t]*(?=\r?$)"
)


def atom_summary(body):
    matches = list(_SUMMARY.finditer(body))
    if len(matches) != 1 or not matches[0].group(1).strip():
        raise InputError(
            "summary",
            "Exactly one Summary is required.",
            format="A single nonempty Summary section",
        )
    return matches[0]


def logical_container(values, view):
    container = values.get("container", view.get("container"))
    if "scope_unit" in values:
        if "container" in values and container != {
            "scope_unit": values["scope_unit"]
        }:
            raise InputError(
                "container",
                "Container and Scope Unit disagree.",
                format="One logical container",
            )
        container = {"scope_unit": values["scope_unit"]}
    if (
        not isinstance(container, dict)
        or set(container) not in ({"scope_unit"}, {"atom"})
        or any(
            not isinstance(value, str) or not value.strip()
            for value in container.values()
        )
    ):
        field = "container" if container is not None else "scope_unit"
        raise InputError(
            field,
            "Supply one Scope Unit or containing Atom.",
            format="One nonempty reference",
        )
    return container


def result(*, effects=(), errors=(), warnings=(), **data):
    return {
        "outcome": "failed" if errors else "completed",
        "effects": list(effects),
        "errors": list(errors),
        "warnings": list(warnings),
        **data,
    }


def saved(selection, path, atom_id, ref_id, version, status):
    return {
        "atom_id": atom_id,
        "ref_id": ref_id,
        "version": version,
        "status": status,
        "path": Path(path).relative_to(selection.root).as_posix(),
    }


def _create_parents(root: Path, parent: Path, recorded: list[dict]) -> None:
    relative = parent.relative_to(root)
    if ".." in relative.parts:
        raise ValueError("Invalid destination path.")
    parent_fd = open_regular(root, directory=True)
    visited = Path()
    try:
        for name in relative.parts:
            visited /= name
            try:
                os.mkdir(name, dir_fd=parent_fd)
            except FileExistsError:
                pass
            else:
                recorded.append(
                    {
                        "operation": "create",
                        "target": visited.as_posix(),
                        "state": "known",
                        "evidence": "directory",
                    }
                )
            child = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent_fd,
            )
            os.close(parent_fd)
            parent_fd = child
    finally:
        os.close(parent_fd)


def write_destination(root, path, raw):
    created: list[dict] = []
    try:
        _create_parents(Path(root), Path(path).parent, created)
    except OSError, ValueError:
        return effects.Result(
            created,
            [
                {
                    "code": "backend_failure",
                    "message": "Cannot create the derived Carrier directory.",
                    "field": None,
                }
            ],
        )
    outcome = effects.create(root, path, raw)
    outcome.effects[:0] = created
    return outcome


def destination_collision(outcome):
    return (
        not outcome["effects"]
        and len(outcome["errors"]) == 1
        and outcome["errors"][0].get("code") == "stale_state"
        and outcome["errors"][0].get("message")
        == "Destination already exists."
    )
