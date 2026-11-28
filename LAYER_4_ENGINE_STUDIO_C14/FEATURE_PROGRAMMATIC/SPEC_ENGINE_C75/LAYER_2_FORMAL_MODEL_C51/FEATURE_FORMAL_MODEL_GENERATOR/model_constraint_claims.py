"""Merge constraint Declarations into their Model class owners."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    model_class_target,
)


def _constraint_owners(parsed: list) -> dict:
    owners = {}
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] != "entity" or "entity_class" not in args:
            continue
        target = model_class_target(subject, args["entity_name"])
        if target in owners:
            raise ValueError(
                f"{source}: duplicate Model class target: {target}"
            )
        owners[target] = (source, declaration)
        if args.get("entity_kind") == "Primary":
            allowed = {
                "entity_name",
                "entity_class",
                "entity_kind",
                "identity_properties",
                "axes",
                "ssot_carrier_path",
                "creation_enabled",
            }
            if args.keys() - allowed or declaration.get("instance_check"):
                raise ValueError(
                    f"{source}: Primary class Declaration contains constraints"
                )
    return owners


def _merge_constraint_claims(parsed: list) -> list:
    """Attach constraint declarations to their canonical class owner."""
    owners = _constraint_owners(parsed)
    merged, seen = [], set()
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if "constraints_for" not in args:
            merged.append(
                (source, subject, {**declaration, "arguments": dict(args)})
            )
            continue
        target = args["constraints_for"]
        if target not in owners:
            raise ValueError(f"{source}: unknown constraint owner: {target}")
        if target in seen:
            raise ValueError(f"{source}: duplicate constraint owner: {target}")
        seen.add(target)
        owner = owners[target][1]
        allowed = {
            "entity_name",
            "constraints_for",
            "model_relation_constraints",
            "instance_relation_constraints",
            "population_unique_constraints",
            "instance_check",
        }
        if (
            declaration["kind"] != "entity"
            or args.keys() - allowed
            or args.get("entity_name")
            != owner["arguments"]["entity_name"] + " Constraints"
        ):
            raise ValueError(f"{source}: invalid constraint Declaration")
    _apply_constraints(merged, parsed, seen)
    return merged


def _apply_constraints(merged, parsed, seen):
    for source, subject, declaration in merged:
        args = declaration["arguments"]
        if "entity_class" not in args:
            continue
        target = model_class_target(subject, args["entity_name"])
        if target not in seen:
            continue
        constraint = next(
            item
            for _, _, item in parsed
            if item["arguments"].get("constraints_for") == target
        )
        for key in (
            "model_relation_constraints",
            "instance_relation_constraints",
            "population_unique_constraints",
        ):
            if key in constraint["arguments"]:
                if key in args:
                    raise ValueError(f"{source}: duplicate {key} for {target}")
                args[key] = constraint["arguments"][key]
        if constraint.get("instance_check"):
            if declaration.get("instance_check"):
                raise ValueError(
                    f"{source}: duplicate instance check for {target}"
                )
            declaration["instance_check"] = constraint["instance_check"]
