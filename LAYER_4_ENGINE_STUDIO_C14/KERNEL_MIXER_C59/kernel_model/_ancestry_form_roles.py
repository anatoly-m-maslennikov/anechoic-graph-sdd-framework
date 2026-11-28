"""Recognize source-local Form and Role declarations."""

from __future__ import annotations

import re
from typing import TypeVar

from .declaration_cfel import filters

S = TypeVar("S")


def _form_role_constraints(
    items: tuple[tuple[str, S], ...],
) -> list[tuple[S, str, frozenset[str]]]:
    """Recognize the two literal, source-local population declarations."""
    populations: list[tuple[S, str, str]] = []
    constraints: list[tuple[S, str, frozenset[str]]] = []
    for statement, source in items:
        match = re.fullmatch(
            r"\s*Atom/\(\.Header\.(?:Context\.)?Form\s*:=\s*([^()]+)\)"
            r"//\$[A-Za-z_][A-Za-z_0-9]*"
            r"\.Header\.(?:Context\.)?Role\s*::\s*\[\s*in\s*"
            r"\(([^()]*)\)\s*\]\s*\{::1\}\s*",
            statement,
        )
        if match:
            form, value = match.groups()
            roles = filters("/(.Header.Role in (" + value + "))", "Role")
            if roles is not None:
                constraints.append((source, form.strip(), roles))
        population = re.fullmatch(
            r"\s*\$([A-Za-z_][A-Za-z_0-9]*)\[<Atom>,\s*"
            r"\(\.Header\.(?:Context\.)?Form\s*=\s*([^()]+)\)\]\s*",
            statement,
        )
        if population:
            variable, form = population.groups()
            populations.append((source, variable, form.strip()))
    for statement, source in items:
        match = re.fullmatch(
            r"\s*\$([A-Za-z_][A-Za-z_0-9]*)\.Header\.(?:Context\.)?Role"
            r"\s*==\s*([A-Za-z_][A-Za-z_0-9 ]*)\s*",
            statement,
        )
        if match:
            variable, role = match.groups()
            constraints.extend(
                (source, form, frozenset({role.strip()}))
                for owner, name, form in populations
                if owner == source and name == variable
            )
    return constraints
