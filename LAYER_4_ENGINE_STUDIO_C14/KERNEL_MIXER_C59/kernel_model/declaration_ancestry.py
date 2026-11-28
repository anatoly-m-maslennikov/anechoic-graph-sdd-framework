"""Compile the literal named ancestry needed by the Atom schema projection.

This is deliberately not a CFEL evaluator. Inputs are already extracted Formal
Claim statements; unrecognized expressions never introduce names or edges.
"""

from __future__ import annotations

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import re
from typing import Generic, Iterable, Iterator, TypeVar

from .declaration_cfel import filters
from ._ancestry_form_roles import _form_role_constraints
from ._ancestry_compile import _collect_items, _compile_edges

S = TypeVar("S")
_PROPERTY = re.compile(r"\.(?:Content|Header)(?=\.|\s|\[|\{|::|$)")


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class ProjectedStatement(Generic[S]):
    statement: str
    source: S
    roles: frozenset[str] | None = None
    forms: frozenset[str] | None = None
    provenance: tuple[S, ...] = ()
    original_statement: str = ""
    constraints: str = ""


def _intersect(
    a: frozenset[str] | None, b: frozenset[str] | None
) -> frozenset[str] | None:
    return b if a is None else a if b is None else a & b


def compile_ancestry(
    statements: Iterable[tuple[str, S]],
) -> tuple[ProjectedStatement[S], ...]:  # noqa: C901
    """Return direct Atom expressions and projected named properties."""
    items = tuple(statements)
    form_roles = _form_role_constraints(items)
    aliases, parsed_items, relations, direct_statements = _collect_items(items)
    edges, bindings, properties = _compile_edges(
        aliases, parsed_items, relations
    )
    result = _direct_projections(direct_statements, form_roles)
    _project_properties(properties, edges, bindings, result)
    return tuple(result)


def _direct_projections(direct_statements, form_roles):
    result = []
    for statement, source in direct_statements:
        roles = None
        prop = next(
            (
                m
                for m in _PROPERTY.finditer(statement)
                if statement[: m.start()].count("(")
                == statement[: m.start()].count(")")
            ),
            None,
        )
        if prop and statement.startswith("Atom/"):
            try:
                selected_forms = filters(statement[: prop.start()], "Form")
                matching_roles = (
                    allowed
                    for owner, form, allowed in form_roles
                    if owner == source and selected_forms == frozenset({form})
                )
                for allowed in matching_roles:
                    roles = _intersect(roles, allowed)
            except ValueError:
                pass
        result.append(
            ProjectedStatement(
                statement,
                source,
                roles=roles,
                provenance=(source,),
                original_statement=statement,
            )
        )

    return result


def _project_properties(properties, edges, bindings, result):
    from .declaration_cfel import _filter_groups

    for original, source, address, trailing, suffix in properties:
        if original.startswith("Atom") and address == ("Atom",):
            continue
        for selectors, provenance, names in _ancestry_paths(
            edges, address, frozenset()
        ):
            roles = forms = None
            for group in _filter_groups(selectors + trailing):
                try:
                    roles = _intersect(
                        roles, filters("/(" + group + ")", "Role")
                    )
                    forms = _intersect(
                        forms, filters("/(" + group + ")", "Form")
                    )
                except ValueError:
                    roles = frozenset()
            roles, forms, binding_sources = _apply_bindings(
                address, names, bindings, roles, forms
            )
            result.append(
                ProjectedStatement(
                    "Atom//$declared" + suffix,
                    source,
                    roles,
                    forms,
                    provenance + tuple(binding_sources) + (source,),
                    original,
                    selectors + trailing,
                )
            )


def _ancestry_paths(
    edges, address: tuple[str, ...], visited: frozenset[tuple[str, ...]]
) -> Iterator[tuple[str, tuple[S, ...], tuple[tuple[str, ...], ...]]]:
    if address == ("Atom",):
        yield "", (), ()
        return
    if address in visited:
        return
    for parent, selector, src in edges.get(address, ()):
        for prior, provenance, names in _ancestry_paths(
            edges, parent, visited | {address}
        ):
            yield prior + selector, provenance + (src,), names + (address,)


def _apply_bindings(address, names, bindings, roles, forms):
    binding_sources = []
    for node in names:
        for field, values, binding_source in bindings.get(node, ()):
            if field == "Role":
                roles = _intersect(roles, values)
            else:
                forms = _intersect(forms, values)
            binding_sources.append(binding_source)
    if not any(field == "Form" for field, _, _ in bindings.get(address, ())):
        roles = frozenset()
    return roles, forms, binding_sources
