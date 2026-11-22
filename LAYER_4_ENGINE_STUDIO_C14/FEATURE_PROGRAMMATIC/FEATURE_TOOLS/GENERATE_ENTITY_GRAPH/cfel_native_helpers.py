"""Project structured Python Claim helpers and special declarations."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import (
    _CONTROL, _COUNT, _OPERATOR_SUBJECT, _count, _named_property_count, _record, _sibling_order,
)

Record = dict[str, Any]


def _native_count(value: Any) -> Record | None:
    if type(value) is int and value >= 0:
        return {"minimum": value, "maximum": value}
    if isinstance(value, dict) and set(value) == {"minimum", "maximum"}:
        return value
    return None



def _native_relation(source: Mapping[str, Any], left: str, right: str, *,
                     relation: str | None = None, notation: str | None = None,
                     left_count: Record | None = None, right_count: Record | None = None,
                     expression: str, group: str | None) -> Record:
    return _record(source, expression, "relation_cardinality", source_selector=left,
                   relation=relation, relation_notation=notation, target_selector=right,
                   source_cardinality=left_count, target_cardinality=right_count,
                   written_direction="forward", written_source_selector=left,
                   written_target_selector=right, written_source_cardinality=left_count,
                   written_target_cardinality=right_count, **({"group": group} if group else {}))



def _helper_count(value: str | None) -> Record | None:
    if value is None:
        return None
    match = re.fullmatch(_COUNT, value)
    if match is None:
        raise ValueError(f"invalid cardinality: {value}")
    return _count(match["minimum"], match["tail"], match["maximum"])



def _helper_records(calls: tuple, carrier: Mapping[str, Any]) -> tuple[list[Record], list[Record]] | None:
    """Project the helper calls used by Current Claims without a CFEL round trip."""
    if any(call["name"] not in {"composition", "relation", "deliver", "set_value", "subject_path", "property_rule", "order_before", "classify"} for call in calls):
        return None
    source = carrier["source"]
    rows, diagnostics = [], []
    for call in calls:
        name, args, group = call["name"], call["arguments"], call["scope"]
        suffix = {"group": group} if group else {}
        for project in (_helper_call_0, _helper_call_1, _helper_call_2):
            accepted = project(name, args, group, source, carrier, rows, diagnostics, suffix)
            if accepted is not None:
                if not accepted:
                    return None
                break
        else:
            return None
    return rows, diagnostics



def _helper_call_0(name, args, group, source, carrier, rows, diagnostics, suffix):
    if name == "composition":
        left, *rest = (args["container"], *args["parts"])
        right = " <+ ".join(rest)
        expression = f"{left} <+ {right}"
        rows.append(_native_relation(source, left, right, notation="<+", expression=expression, group=group))
        return True
    if name == "property_rule" and args.get("occurrences") is None and args.get("values") is not None:
        address, count = args["address"], _helper_count(args["values"])
        fmt = args.get("value_format")
        expression = f'{address}::{" [" + fmt + "]" if fmt is not None else ""}{{::{args["values"]}}}'
        rows.append(_record(source, expression, "property_constraint", property_selector=address,
                            selection="values", name_format=None, occurrence_cardinality=None,
                            effective_occurrence_cardinality=_named_property_count(None, count),
                            value_format=fmt, value_cardinality=count, **suffix))
        return True
    if name == "order_before":
        expression = f'{args["first"]} ;> {args["second"]}'
        order = _sibling_order(expression)
        if order is None:
            return False
        rows.append(_record(source, expression, "relation_cardinality", **order, **suffix))
        return True
    if name == "classify" and args.get("notation") == "relation":
        left, right = args["address"], f'{args["axis"]} == {args["value"]}'
        rows.append(_native_relation(source, left, right, relation="HAS_CLASSIFICATION",
                                     expression=f'{left} ((HAS_CLASSIFICATION)) {right}', group=group))
        return True
    return None


def _helper_call_1(name, args, group, source, carrier, rows, diagnostics, suffix):
    if name == "relation" and args.get("target") is not None:
        left, right, relation = args["source"], args["target"], args["name"]
        lc, rc = _helper_count(args.get("source_count")), _helper_count(args.get("target_count"))
        ltext = f"{{::{args['source_count']}}}" if args.get("source_count") is not None else ""
        rtext = f"{{::{args['target_count']}}}" if args.get("target_count") is not None else ""
        reverse = args.get("reverse", False)
        expression = f"{left} {ltext}{'<' if reverse else ''}(({relation})){rtext} {right}"
        record = _native_relation(source, right if reverse else left, left if reverse else right,
                                  relation=relation, left_count=rc if reverse else lc,
                                  right_count=lc if reverse else rc, expression=expression, group=group)
        record.update(written_direction="reverse" if reverse else "forward", written_source_selector=left,
                      written_target_selector=right, written_source_cardinality=lc, written_target_cardinality=rc)
        rows.append(record)
        return True
    if name == "relation" and not args.get("reverse", False):
        left, relation = args["source"], args["name"]
        text = f"{{::{args['source_count']}}}" if args.get("source_count") is not None else ""
        expression = f"{left} {text}(({relation}))"
        rows.append(_record(source, expression, "relation_cardinality", source_selector=left,
                            relation=relation, relation_notation=None, target_selector=None,
                            source_cardinality=_helper_count(args.get("source_count")), target_cardinality=None,
                            selection="all_relations" if relation == "*" else "named_relation",
                            written_direction="forward", target_domain="unresolved", **suffix))
        return True
    return None


def _helper_call_2(name, args, group, source, carrier, rows, diagnostics, suffix):
    if name == "set_value" and (match := re.fullmatch(r"Operator//([A-Za-z_][A-Za-z_0-9]*)", args["address"])) and group == "model":
        subject = (carrier.get("subjects") or {}).get("governs") or (carrier.get("subjects") or {}).get("active", "")
        owner = _OPERATOR_SUBJECT.search(subject)
        value = args["value"]
        symbol = json.loads(value) if isinstance(value, str) and value.startswith('"') else value
        if owner and owner["name"] == match[1] and isinstance(symbol, str) and symbol:
            expression = f'{args["address"]} == {json.dumps(symbol, ensure_ascii=False)}'
            rows.append(_record(source, expression, "operator_symbol", operator=match[1], symbol=symbol, **suffix))
        else:
            return False
        return True
    if name in {"deliver", "subject_path"}:
        expression = (f'{args["source"]} >> {args["carrier"]}' if name == "deliver" else args["address"])
        if name == "subject_path" and group in {None, "model"}:
            subject = notation.parse_subject_expression(expression, subject_profile="approved").expression
            if (isinstance(subject, notation.Path) and isinstance(subject.head, notation.Name)
                    and subject.value_format is None and subject.value_cardinality is None
                    and all(step.operator in {"/", "."} and isinstance(step.operand, (notation.Name, notation.Qualification)) for step in subject.steps)):
                rows.append(_record(source, expression, "subject_expression", selector=notation.render_subject(subject), **suffix))
                return True
        message = ("CFEL control expression is outside the bounded projection extractor." if _CONTROL.search(expression)
                   else "CFEL expression is outside the bounded projection extractor.")
        diagnostics.append({"code": "cfel-expression-unsupported", "message": message,
                            "expression": expression, "source": dict(source), **suffix})
        return True
    return None


def _native_special(declaration: Mapping[str, Any], source: Mapping[str, Any]) -> list[Record]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import validate_aspect_hierarchy, validate_aspect_instance
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.dataclass_field_contract__pub import validate_field_contracts

    args = declaration["arguments"]
    rows = []
    if "structure_paths" in args:
        paths, memberships = validate_aspect_hierarchy(dict(args))
        group = "instances"
    elif args.get("instance", {}).get("type") == "Aspect":
        address = validate_aspect_instance(dict(args))
        paths, memberships = (address,), (address,)
        group = None
    else:
        paths, memberships = (), ()
        group = None
    for path in paths:
        left, right = path.split(" <+ ", 1)
        rows.append(_native_relation(source, left, right, notation="<+", expression=path, group=group))
    for address in memberships:
        left = f"({address})"
        rows.append(_native_relation(source, left, "Aspect", relation="INSTANCE_OF",
                                     expression=f"{left} ((INSTANCE_OF)) Aspect", group=group))
    for axis, values in args.get("allowed_classification_values", {}).items():
        for value in values:
            subject = args["entity_name"]
            expression = f"{subject} >| {axis}: {value}"
            rows.append(_record(source, expression, "classification_allowed_value", subject_selector=subject,
                                axis=axis, value=value, group="model"))
    _native_special_fields(declaration, source, args, rows, validate_field_contracts)
    return rows



def _native_special_fields(declaration, source, args, rows, validate_field_contracts):
    if declaration.get("classes"):
        validate_field_contracts(declaration)
        for field in declaration["classes"][0]["fields"]:
            meta = field["field"]["metadata"]
            occurrence, values = meta["property_occurrence_cardinality"], meta["value_cardinality"]
            selector = f"{args['entity_name']}.{field['name']}"
            annotation = field["annotation"]
            fmt = {"str": "string", "atom_id": "atom id"}.get(annotation, annotation)
            occurrence, values = _native_count(occurrence), _native_count(values)
            expression = f"{selector}{{::{_count_text(occurrence)}}} :: [{fmt}]{{::{_count_text(values)}}}"
            effective = _named_property_count(occurrence, values)
            rows.append(_record(source, expression, "property_constraint", property_selector=selector,
                                selection="property", name_format=None, occurrence_cardinality=occurrence,
                                effective_occurrence_cardinality=effective, occurrence_conflict=effective is None,
                                value_format=fmt, value_cardinality=values, group="model"))
        for rel in args.get("incoming_model_relations", ()):
            left, right, name = rel["source"], args["entity_name"], rel["relation"]
            left_count = _native_count(rel["source_cardinality"])
            right_count = _native_count(rel["target_cardinality"])
            expression = f"{left} {{::{_count_text(left_count)}}}(({name})){{::{_count_text(right_count)}}} {right}"
            rows.append(_native_relation(source, left, right, relation=name, left_count=left_count,
                                         right_count=right_count, expression=expression, group="model"))


def _count_text(count: Record) -> str:
    minimum, maximum = count["minimum"], count["maximum"]
    return f"{minimum}+" if maximum is None else str(minimum) if maximum == minimum else f"{minimum}..{maximum}"

