"""Project native declaration constraints without executing Claim code."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.topic_dependencies__pub import validate_dependencies_claim

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import _named_property_count, _record
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_native_helpers import _native_count

Record = dict[str, Any]


def _native_constraints(declaration: Mapping[str, Any], source: Mapping[str, Any], block: str) -> list[Record]:
    args = declaration["arguments"]
    result: list[Record] = []
    check = declaration.get("instance_check")
    if check is not None:
        scope_check = (args.get("base_path") == "Scope Unit" and args.get("entity_name") == "structural_level"
                       and check.get("name") == "check_structural_level" and check.get("parameter_type") == "ScopeUnit")
        if check.get("name") == "dependencies_are_distinct":
            validate_dependencies_claim(declaration)
        elif not (scope_check and args.get("relation_name") == "IS_PROPERTY_OF"
                  or args.get("entity_class") == check["parameter_type"]):
            raise ValueError("unsupported instance check")
        result.append(_record(source, f'{check["name"]}({check["parameter"]}: {check["parameter_type"]})',
                              "instance_check", group="instances", callback=check["name"]))
    if declaration["kind"] == "entity" and args.get("entity_class"):
        return _native_entity(declaration, source, block, result)
    if declaration["kind"] == "entity" and args.get("relation_name") == "IS_PROPERTY_OF":
        return _native_property(declaration, source, block, result)
    if declaration["kind"] == "relation":
        _native_relation(declaration, source, block, result)
    return result


def _native_entity(declaration, source, block, result):
    args = declaration["arguments"]
    row = next((row for row in declaration["classes"] if row["name"] == args["entity_class"]), None)
    if row is None:
        raise ValueError("declared entity class is unavailable")
    result.append(_record(source, block, "native_class", group="model",
                          entity_name=args["entity_name"], class_name=row["name"],
                          bases=row["bases"], qualification_property_path=args.get("qualification_property_path"),
                          fields=row["fields"], arguments=args))
    classifications = args.get("classifications", {})
    if not isinstance(classifications, Mapping) or any(
        not axis.strip() or type(value) not in (str, int, float, bool)
        for axis, value in classifications.items()
    ):
        raise ValueError("classifications must map names to literal values")
    for axis, value in classifications.items():
        result.append(_record(source, block, "classification_condition", group="model",
                              subject_selector=args["entity_name"], axis=axis, operator="==", value=str(value)))
    if args.get("qualification_property_path") == "Projection.Form" and row["bases"] == ("Projection",):
        result.append(_record(source, block, "allowed_literal", group="model",
                              property_selector="Projection.Form", literal=args["entity_name"]))
    if "instance_population_cardinality" in args:
        result.append(_record(source, block, "native_population_constraint", group="instances",
                              cardinality=_native_count(args["instance_population_cardinality"]),
                              scope=args.get("instance_population_scope")))
    _native_entity_dependents(args, source, block, result)
    _native_entity_population(args, source, block, result)
    return result


def _native_entity_dependents(args, source, block, result):
    if "dependent_property_cardinality" in args:
        count = _native_count(args["dependent_property_cardinality"])
        names = args.get("allowed_dependent_property_names")
        if names is not None and (not isinstance(names, (tuple, list)) or
                                  any(not isinstance(name, str) or not name for name in names)):
            raise ValueError("allowed dependent Property names must be strings")
        name_format = args.get("dependent_property_name_format")
        if names is not None:
            name_format = f"{name_format or 'string'},in({','.join(names)})"
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=args["entity_name"], selection="immediate_dependents",
                              name_format=name_format, occurrence_cardinality=count,
                              effective_occurrence_cardinality=count, occurrence_conflict=False,
                              value_format=None, value_cardinality=None, allowed_names=names))


def _native_entity_population(args, source, block, result):
    for rule in args.get("population_unique_constraints", ()):
        result.append(_record(source, block, "population_unique_constraint", group="instances",
                              population_selector=args.get("population_entity_path", args["entity_name"]),
                              keys=rule["keys"], **({"status": rule["status"], "single_value_paths": rule["single_value_paths"]} if "status" in rule else {})))
    for path, constraint in args.get("instance_property_constraints", {}).items():
        count = _native_count(constraint.get("value_cardinality"))
        if count is not None:
            result.append(_record(source, block, "property_constraint", group="instances",
                                  property_selector=f"{args['entity_name']}//$instance.{path}",
                                  selection="values", name_format=None, occurrence_cardinality=None,
                                  effective_occurrence_cardinality=_named_property_count(None, count),
                                  value_format="" if count == {"minimum": 0, "maximum": 0} else None,
                                  value_cardinality=count))


def _native_property(declaration, source, block, result):
    args = declaration["arguments"]
    if not isinstance(args.get("base_path"), str) or not args["base_path"]:
        raise ValueError("Property declaration requires a base_path")
    if forms := args.get("applies_to_forms"):
        import json
        role = args["applies_to_role"]
        role = json.dumps(role) if " " in role else role
        for form in forms:
            selector = f"Atom/(.Header.Context.Role in ({role}))/(.Header.Context.Form in ({form})).Header.State.Status"
            for value in args.get("allowed_values", ()):
                result.append(_record(source, f"{selector} :: {value}", "allowed_literal", group="model", property_selector=selector, literal=value))
        return result
    for rule in args.get("population_unique_constraints", ()):
        result.append(_record(source, block, "population_unique_constraint", group="instances",
                              population_selector=args.get("population_entity_path", args["base_path"]),
                              keys=rule["keys"], **({"status": rule["status"], "single_value_paths": rule["single_value_paths"]} if "status" in rule else {})))
    for dependency in args.get("population_functional_dependencies", ()):
        result.append(_record(source, block, "population_functional_dependency", group="instances",
                              population_selector=args.get("population_entity_path", args["base_path"]),
                              keys=dependency["keys"], dependents=dependency["dependents"],
                              **({"status_groups": dependency["status_groups"]} if "status_groups" in dependency else {})))
    selector = f"{args['base_path']}.{args['entity_name']}"
    _native_property_scalar(declaration, args, source, block, result, selector)
    _native_property_dependents(args, source, block, result, selector)
    _native_property_rules(args, source, block, result, selector)
    _native_property_fallbacks(args, source, block, result, selector)
    return result


def _native_property_scalar(declaration, args, source, block, result, selector):
    occurrence = _native_count(args.get("property_occurrence_cardinality"))
    values = _native_count(args.get("value_cardinality"))
    effective = _named_property_count(occurrence, values)
    if not args.get("allowed_values") or occurrence is not None or values is not None or "value_format" in args:
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=selector, selection="property", name_format=None,
                              occurrence_cardinality=occurrence, effective_occurrence_cardinality=effective,
                              occurrence_conflict=effective is None, value_format=args.get("value_format"),
                              value_cardinality=values,
                              **({"model_value_format": declaration["model_value_format"]} if declaration.get("model_value_format") else {}),
                              applicable_entity_classes=args.get("applies_to_entity_classes")))


def _native_property_dependents(args, source, block, result, selector):
    dependent_value_count = _native_count(args.get("dependent_property_value_cardinality"))
    dependent_value_format = args.get("dependent_property_value_format")
    if "dependent_property_cardinality" in args or (
        "dependent_property_value_format" in args and dependent_value_count is None
    ):
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=selector, selection="immediate_dependents",
                              name_format=args.get("dependent_property_name_format"),
                              occurrence_cardinality=_native_count(args.get("dependent_property_cardinality")),
                              effective_occurrence_cardinality=_native_count(args.get("dependent_property_cardinality")),
                              occurrence_conflict=False,
                              value_format=dependent_value_format if dependent_value_count is None else None,
                              value_cardinality=None,
                              allowed_names=args.get("allowed_dependent_property_names")))
    if dependent_value_count is not None:
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=selector, selection="immediate_dependent_values",
                              name_format=None, occurrence_cardinality=None,
                              value_format=dependent_value_format, value_cardinality=dependent_value_count))
    if "recursive_dependent_property_cardinality" in args:
        count = _native_count(args["recursive_dependent_property_cardinality"])
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=selector, selection="recursive_dependents",
                              name_format=args.get("recursive_dependent_property_name_format"),
                              occurrence_cardinality=count, effective_occurrence_cardinality=count,
                              occurrence_conflict=False, value_format=None, value_cardinality=None))
    if "recursive_dependent_property_value_format" in args:
        result.append(_record(source, block, "property_constraint", group="model",
                              property_selector=selector, selection="recursive_dependent_values",
                              name_format=None, occurrence_cardinality=None,
                              value_format=args["recursive_dependent_property_value_format"], value_cardinality=None))


def _native_property_rules(args, source, block, result, selector):
    for first, second in args.get("ordered_dependent_property_pairs", ()):
        result.append(_record(source, f"{selector}.{first} ;> {selector}.{second}", "relation_cardinality",
                              group="model", bearer=selector, relation="IS_ORDERED_RIGHT_BEFORE",
                              source_selector=f"{selector}.{first}", target_selector=f"{selector}.{second}",
                              source_cardinality=None, target_cardinality=None, written_direction="forward",
                              applicable_entity_classes=args.get("applies_to_entity_classes"),
                              **({"ordering_roles": args["ordered_dependent_property_roles"]}
                                 if "ordered_dependent_property_roles" in args else {})))
    if "minimum_value" in args:
        minimum = args["minimum_value"]
        if type(minimum) not in (int, float):
            raise ValueError("minimum_value must be numeric")
        result.append(_record(source, f"{selector} >= {minimum}", "property_value_bound",
                              group="model", property_selector=selector, operator=">=", value=minimum))
    for value in args.get("allowed_values", ()):
        result.append(_record(source, f"{selector} :: {value}", "allowed_literal",
                              group="model", property_selector=selector, literal=value,
                              applicable_entity_classes=args.get("applies_to_entity_classes")))
    for status, order in args.get("status_order_numbers", {}).items():
        subject = f"Atom/(.Header.State.Status := {status}).Header.State.Status"
        result.append(_record(source, f"{subject} >| (Status Order Number == {order})",
                              "classification_condition", group="model", subject_selector=subject,
                              axis="Status Order Number", operator="==", value=str(order)))
    for status, group in args.get("status_groups", {}).items():
        role = args["applies_to_entity_classes"][0]
        subject = f"Atom/(.Header.Context.Role := {role})/(.Header.State.Status := {status}).Header.State.Status"
        result.append(_record(source, f"{subject} >| Status Group == {group}", "classification_condition", group="model", subject_selector=subject, axis="Status Group", operator="==", value=group))


def _native_property_fallbacks(args, source, block, result, selector):
    if "maximum_value" in args:
        result.append(_record(source, f"{selector} <= {args['maximum_value']}", "property_value_bound",
                              group="model", property_selector=selector, operator="<=", value=args["maximum_value"]))
    if "fallback_chain" in args:
        result.append(_record(source, block, "effective_value_fallback_chain", group="instances",
                              property_selector=selector, branches=args["fallback_chain"],
                              empty_values=("undefined", "null", ""), project_cardinality=1))
    if "fallback_value" in args:
        result.append(_record(source, f"{selector} ?== {args['fallback_value']}",
                              "effective_value_fallback", group="instances", property_selector=selector,
                              fallback_literal=args["fallback_value"], empty_values=("undefined", "null", "")))
    if args.get("fallback_property_name"):
        bearer = args["base_path"]
        result.append(_record(source, f"{bearer}.{args['entity_name']} ?== {bearer}.{args['fallback_property_name']}",
                              "effective_value_fallback", group="instances",
                              property_selector=f"{bearer}.{args['entity_name']}",
                              fallback_property_selector=f"{bearer}.{args['fallback_property_name']}",
                              empty_values=("undefined", "null", "")))


def _native_relation(declaration, source, block, result):
    args = declaration["arguments"]
    name = args["relation_name"]
    result.append(_record(source, block, "native_relation_declaration", group="model",
                          relation=name, arguments={**args, **({"derivation": "Derived"} if "derived_from" in args else {})}))
    for key, relation in (("classifications", name), ("inverse_classifications", args.get("inverse_alias"))):
        for axis, value in args.get(key, {}).items():
            subject = f"Relation//{relation}"
            result.append(_record(source, f"{subject} >| {axis} == {value}", "classification_condition",
                                  group="model", subject_selector=subject, axis=axis, operator="==", value=value))
    if base := args.get("derived_from"):
        result.append(_record(source, block, "relation_cardinality", group="model",
                              source_selector=f"Relation//{name}", relation="IS_DERIVED_RELATION_OF",
                              target_selector=f"Relation//{base}", source_cardinality=None,
                              target_cardinality=None, written_direction="forward"))
    for selector, direction in ((args.get("source_endpoint"), "source"), (args.get("target_endpoint"), "target")):
        if isinstance(selector, dict):
            result.append(_record(source, block, "relation_endpoint", group="model", relation=name,
                                  direction=direction, endpoint=selector,
                                  targets_per_source=_native_count(args.get("targets_per_source")),
                                  sources_per_target=_native_count(args.get("sources_per_target"))))
    for pair in args.get("endpoint_pairs", ()):
        result.append(_record(source, block, "relation_endpoint_pair", group="model", relation=name,
                              source_endpoint=pair["source_endpoint"], target_endpoint=pair["target_endpoint"],
                              targets_per_source=_native_count(args.get("targets_per_source")),
                              sources_per_target=_native_count(args.get("sources_per_target"))))
    if inverse := args.get("inverse_alias"):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.legacy_relation__pub import emits_instance_inverse

        is_inverse = emits_instance_inverse(args)
        result.append(_record(source, block, "relation_cardinality", group="model",
                              source_selector=f"Relation//{name if is_inverse else inverse}",
                              relation="HAS_INVERSE" if is_inverse else "IS_INVERSE_ALIAS_FOR",
                              target_selector=f"Relation//{inverse if is_inverse else name}", source_cardinality=None,
                              target_cardinality=None, written_direction="forward"))
    if alias := args.get("written_alias"):
        result.append(_record(source, block, "relation_alias", group="model", relation=name, glyph=alias))
