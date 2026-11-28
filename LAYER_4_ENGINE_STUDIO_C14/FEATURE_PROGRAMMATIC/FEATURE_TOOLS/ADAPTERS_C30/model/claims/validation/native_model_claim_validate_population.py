"""Validate native Claim data in source order."""

from __future__ import annotations

import re

from ....model.claims.native_model_claim_values import _fail
from ....model.claims.native_model_claim_dependency_rules import (
    _validate_dependency_paths as _validate_dependency_paths,
    _validate_dependency_rules as _validate_dependency_rules,
)


def _validate_unique_paths(keys, present, declaration):
    for part in (keys, present):
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
                "population uniqueness paths must be distinct "
                "relative Property paths",
            )


def _unique_signature(rule, declaration):
    if not isinstance(rule, dict) or set(rule) not in (
        {"keys"},
        {"keys", "status", "single_value_paths"},
    ):
        _fail(
            declaration,
            "population uniqueness requires keys, optionally "
            "with a Status and single-value paths",
        )
    status = rule.get("status", "")
    if "status" in rule and (
        not isinstance(status, str) or not status or status != status.strip()
    ):
        _fail(
            declaration, "population uniqueness Status must be nonempty text"
        )
    keys, present = (
        rule["keys"],
        rule.get("single_value_paths", rule["keys"]),
    )
    _validate_unique_paths(keys, present, declaration)
    if set(keys) != set(present):
        _fail(declaration, "every unique key requires exactly one value")
    return tuple(keys), status.casefold()


def _validate_unique_rules(rules, declaration):
    seen = set()
    for rule in rules:
        signature = _unique_signature(rule, declaration)
        if signature in seen:
            _fail(declaration, "duplicate population uniqueness rule")
        seen.add(signature)


def _unique_population(arguments, declaration, function):
    class_declaration = (
        function == "declare_entity" and "entity_class" in arguments
    )
    constraint_owner = arguments.get("constraints_for")
    population = constraint_owner or arguments.get(
        "population_entity_path",
        arguments.get("base_path", arguments.get("entity_name")),
    )
    base = arguments.get("base_path")
    rules = arguments["population_unique_constraints"]
    property_declaration = (
        function == "declare_entity"
        and arguments.get("relation_name") == "IS_PROPERTY_OF"
        and isinstance(base, str)
        and isinstance(population, str)
        and (base == population or base.startswith(population + "."))
    )
    if (
        not (
            constraint_owner
            or property_declaration
            or (
                class_declaration
                and population == arguments.get("entity_name")
            )
        )
        or not isinstance(population, str)
        or not population.strip()
        or population != population.strip()
        or not isinstance(rules, (tuple, list))
        or not rules
    ):
        _fail(
            declaration,
            "population uniqueness requires a declared class "
            "or a Property and its population",
        )
    return rules


def _validate_uniqueness(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if "population_entity_path" in arguments and not (
        {"population_functional_dependencies", "population_unique_constraints"}
        & arguments.keys()
    ):
        _fail(
            declaration,
            "population_entity_path requires a population constraint",
        )
    if "population_unique_constraints" in arguments:
        rules = _unique_population(arguments, declaration, function)
        _validate_unique_rules(rules, declaration)


def _validate_dependencies(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if "population_functional_dependencies" in arguments:
        population = arguments.get(
            "population_entity_path", arguments.get("base_path")
        )
        base = arguments.get("base_path")
        if (
            not isinstance(population, str)
            or not population.strip()
            or population != population.strip()
            or not isinstance(base, str)
            or not (base == population or base.startswith(population + "."))
        ):
            _fail(
                declaration,
                "population must be the Property bearer or an ancestor",
            )
        dependencies = arguments["population_functional_dependencies"]
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
            or not isinstance(dependencies, (tuple, list))
            or not dependencies
        ):
            _fail(
                declaration,
                "population functional dependencies require a "
                "Property declaration",
            )
        _validate_dependency_rules(dependencies, population, declaration)


def _validate_ordered_roles(arguments, declaration):
    if "ordered_dependent_property_roles" in arguments:
        roles = arguments["ordered_dependent_property_roles"]
        if (
            "ordered_dependent_property_pairs" not in arguments
            or not isinstance(roles, (tuple, list))
            or not roles
            or any(
                not isinstance(role, str) or not role.strip() for role in roles
            )
        ):
            _fail(
                declaration,
                "ordered dependent Property roles require ordering "
                "pairs and nonempty Roles",
            )


def _validate_ordered(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    recursive_fields = {
        "recursive_dependent_property_cardinality",
        "recursive_dependent_property_name_format",
        "recursive_dependent_property_value_format",
    }
    if recursive_fields & arguments.keys():
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
        ):
            _fail(
                declaration,
                "recursive dependent Properties require a Property "
                "declaration",
            )
        if (
            "recursive_dependent_property_name_format" in arguments
            and "recursive_dependent_property_cardinality" not in arguments
        ):
            _fail(
                declaration,
                "recursive dependent Property name format requires "
                "cardinality",
            )
    _validate_ordered_pairs(arguments, declaration, function)
    _validate_ordered_roles(arguments, declaration)


def _validate_ordered_cycles(edges, declaration):
    following = dict(edges)
    for start in following:
        seen = set()
        current = start
        while current in following:
            if current in seen:
                _fail(
                    declaration,
                    "ordered dependent Property pairs must be acyclic",
                )
            seen.add(current)
            current = following[current]


def _validate_ordered_degree(edges, declaration):
    if len({left for left, _ in edges}) != len(edges) or len(
        {right for _, right in edges}
    ) != len(edges):
        _fail(
            declaration,
            "ordered dependent Properties require unique adjacent neighbors",
        )


def _validate_ordered_pairs(arguments, declaration, function):
    if "ordered_dependent_property_pairs" in arguments:
        pairs = arguments["ordered_dependent_property_pairs"]
        names = arguments.get("allowed_dependent_property_names")
        if (
            function != "declare_entity"
            or arguments.get("relation_name") != "IS_PROPERTY_OF"
            or (
                names is not None
                and (not isinstance(names, (tuple, list)) or not names)
            )
            or not isinstance(pairs, (tuple, list))
            or not pairs
        ):
            _fail(
                declaration,
                "ordered dependent Property pairs require a "
                "Property declaration",
            )
        if any(
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or any(
                not isinstance(name, str)
                or not name.strip()
                or (names is not None and name not in names)
                for name in pair
            )
            or pair[0] == pair[1]
            for pair in pairs
        ):
            _fail(
                declaration,
                "ordered dependent Property pairs must name "
                "distinct allowed children",
            )
        edges = [tuple(pair) for pair in pairs]
        _validate_ordered_degree(edges, declaration)
        _validate_ordered_cycles(edges, declaration)
