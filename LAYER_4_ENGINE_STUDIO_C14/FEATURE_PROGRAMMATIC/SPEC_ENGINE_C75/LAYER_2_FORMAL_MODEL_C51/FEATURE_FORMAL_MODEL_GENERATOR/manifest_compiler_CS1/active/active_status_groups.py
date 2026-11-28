"""Expand authored family Status maps using the common Atom values."""

import ast

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)


def _inherit_status_groups(records):
    grouped = []
    for index, (_, _, claim) in enumerate(records):
        args = parse_native_model_claim(claim)["arguments"]
        if "status_groups" in args:
            grouped.append((index, args))
    common = {
        args["base_path"]: args["status_groups"]
        for _, args in grouped
        if "status_group_names" in args
    }
    for index, args in grouped:
        inherited = common.get(args["base_path"])
        if inherited is None or "applies_to_entity_classes" not in args:
            continue
        source, scope, claim = records[index]
        groups = args["status_groups"]
        if any(k in groups and groups[k] != v for k, v in inherited.items()):
            raise ValueError(f"{source}: cannot reassign an inherited Status")
        records[index] = (
            source,
            scope,
            _replace_groups(claim, inherited | groups),
        )


def _replace_groups(claim, groups):
    tree = ast.parse(claim)
    call = next(node.value for node in tree.body if isinstance(node, ast.Expr))
    values = {"allowed_values": tuple(groups), "status_groups": groups}
    for keyword in call.keywords:
        if keyword.arg in values:
            keyword.value = ast.parse(
                repr(values[keyword.arg]), mode="eval"
            ).body
    return ast.unparse(tree) + "\n"
