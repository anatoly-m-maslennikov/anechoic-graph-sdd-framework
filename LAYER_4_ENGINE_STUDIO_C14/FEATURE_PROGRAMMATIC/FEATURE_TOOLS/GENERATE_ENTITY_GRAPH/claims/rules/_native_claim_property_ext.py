"""Project native declaration constraints."""

from ..primitives.primitives__shared import _record


def _native_property_rules(args, source, block, result, selector):
    _ordered_rules(args, source, result, selector)
    if "minimum_value" in args:
        minimum = args["minimum_value"]
        if type(minimum) not in (int, float):
            raise ValueError("minimum_value must be numeric")
        result.append(
            _record(
                source,
                f"{selector} >= {minimum}",
                "property_value_bound",
                group="model",
                property_selector=selector,
                operator=">=",
                value=minimum,
            )
        )
    for value in args.get("allowed_values", ()):
        result.append(
            _record(
                source,
                f"{selector} :: {value}",
                "allowed_literal",
                group="model",
                property_selector=selector,
                literal=value,
                applicable_entity_classes=args.get(
                    "applies_to_entity_classes"
                ),
            )
        )
    _status_rules(args, source, result)


def _native_property_fallbacks(args, source, block, result, selector):
    if "maximum_value" in args:
        result.append(
            _record(
                source,
                f"{selector} <= {args['maximum_value']}",
                "property_value_bound",
                group="model",
                property_selector=selector,
                operator="<=",
                value=args["maximum_value"],
            )
        )
    if "fallback_chain" in args:
        result.append(
            _record(
                source,
                block,
                "effective_value_fallback_chain",
                group="instances",
                property_selector=selector,
                branches=args["fallback_chain"],
                empty_values=("undefined", "null", ""),
                project_cardinality=1,
            )
        )
    if "fallback_value" in args:
        result.append(
            _record(
                source,
                f"{selector} ?== {args['fallback_value']}",
                "effective_value_fallback",
                group="instances",
                property_selector=selector,
                fallback_literal=args["fallback_value"],
                empty_values=("undefined", "null", ""),
            )
        )
    _fallback_property(args, source, result)


def _status_rules(args, source, result):
    for status, order in args.get("status_order_numbers", {}).items():
        subject = (
            f"Atom/(.Header.State.Status := {status}).Header.State.Status"
        )
        result.append(
            _record(
                source,
                f"{subject} >| (Status Order Number == {order})",
                "axis_condition",
                group="model",
                subject_selector=subject,
                axis="Status Order Number",
                operator="==",
                value=str(order),
            )
        )
    for status, group in args.get("status_groups", {}).items():
        role = args["applies_to_entity_classes"][0]
        subject = (
            f"Atom/(.Header.Context.Role := {role})/"
            f"(.Header.State.Status := {status}).Header.State.Status"
        )
        result.append(
            _record(
                source,
                f"{subject} >| Status Group == {group}",
                "axis_condition",
                group="model",
                subject_selector=subject,
                axis="Status Group",
                operator="==",
                value=group,
            )
        )


def _ordered_rules(args, source, result, selector):
    for first, second in args.get("ordered_dependent_property_pairs", ()):
        result.append(
            _record(
                source,
                f"{selector}.{first} ;> {selector}.{second}",
                "relation_cardinality",
                group="model",
                bearer=selector,
                relation="IS_ORDERED_RIGHT_BEFORE",
                source_selector=f"{selector}.{first}",
                target_selector=f"{selector}.{second}",
                source_cardinality=None,
                target_cardinality=None,
                written_direction="forward",
                applicable_entity_classes=args.get(
                    "applies_to_entity_classes"
                ),
                **(
                    {
                        "ordering_roles": args[
                            "ordered_dependent_property_roles"
                        ]
                    }
                    if "ordered_dependent_property_roles" in args
                    else {}
                ),
            )
        )


def _fallback_property(args, source, result):
    if args.get("fallback_property_name"):
        bearer = args["base_path"]
        result.append(
            _record(
                source,
                f"{bearer}.{args['entity_name']} ?== "
                f"{bearer}.{args['fallback_property_name']}",
                "effective_value_fallback",
                group="instances",
                property_selector=f"{bearer}.{args['entity_name']}",
                fallback_property_selector=(
                    f"{bearer}.{args['fallback_property_name']}"
                ),
                empty_values=("undefined", "null", ""),
            )
        )
