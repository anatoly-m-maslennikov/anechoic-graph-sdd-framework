"""Project structured Python Claim helper calls."""

import json
import re

from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from .claim_constraint_common import (
    _OPERATOR_SUBJECT,
    _named_property_count,
    _record,
    _sibling_order,
)
from ._native_claim_helper_primitives import _helper_count, _native_relation


def _value_rule(args, source, rows, suffix):
    address, count = args["address"], _helper_count(args["values"])
    fmt = args.get("value_format")
    expression = (
        f"{address}::{' [' + fmt + ']' if fmt is not None else ''}"
        f"{{::{args['values']}}}"
    )
    rows.append(
        _record(
            source,
            expression,
            "property_constraint",
            property_selector=address,
            selection="values",
            name_format=None,
            occurrence_cardinality=None,
            effective_occurrence_cardinality=_named_property_count(
                None, count
            ),
            value_format=fmt,
            value_cardinality=count,
            **suffix,
        )
    )
    return True


def _composition(args, group, source, rows):
    left, *rest = (args["container"], *args["parts"])
    right = " <+ ".join(rest)
    expression = f"{left} <+ {right}"
    rows.append(
        _native_relation(
            source,
            left,
            right,
            notation="<+",
            expression=expression,
            group=group,
        )
    )
    return True


def _helper_call_0(
    name, args, group, source, carrier, rows, diagnostics, suffix
):
    if name == "composition":
        return _composition(args, group, source, rows)
    if (
        name == "property_rule"
        and args.get("occurrences") is None
        and args.get("values") is not None
    ):
        return _value_rule(args, source, rows, suffix)
    if name == "order_before":
        expression = f"{args['first']} ;> {args['second']}"
        order = _sibling_order(expression)
        if order is None:
            return False
        rows.append(
            _record(
                source, expression, "relation_cardinality", **order, **suffix
            )
        )
        return True
    if name == "classify" and args.get("notation") == "relation":
        left, right = args["address"], f"{args['axis']} == {args['value']}"
        rows.append(
            _native_relation(
                source,
                left,
                right,
                relation="HAS_AXIS",
                expression=f"{left} ((HAS_AXIS)) {right}",
                group=group,
            )
        )
        return True
    return None


def _targeted_relation(args, group, source, rows):
    left, right, relation = args["source"], args["target"], args["name"]
    lc, rc = (
        _helper_count(args.get("source_count")),
        _helper_count(args.get("target_count")),
    )
    ltext = (
        f"{{::{args['source_count']}}}"
        if args.get("source_count") is not None
        else ""
    )
    rtext = (
        f"{{::{args['target_count']}}}"
        if args.get("target_count") is not None
        else ""
    )
    reverse = args.get("reverse", False)
    expression = (
        f"{left} {ltext}{'<' if reverse else ''}(({relation})){rtext} {right}"
    )
    record = _native_relation(
        source,
        right if reverse else left,
        left if reverse else right,
        relation=relation,
        left_count=rc if reverse else lc,
        right_count=lc if reverse else rc,
        expression=expression,
        group=group,
    )
    record.update(
        written_direction="reverse" if reverse else "forward",
        written_source_selector=left,
        written_target_selector=right,
        written_source_cardinality=lc,
        written_target_cardinality=rc,
    )
    rows.append(record)
    return True


def _helper_call_1(
    name, args, group, source, carrier, rows, diagnostics, suffix
):
    if name == "relation" and args.get("target") is not None:
        return _targeted_relation(args, group, source, rows)
    if name == "relation" and not args.get("reverse", False):
        left, relation = args["source"], args["name"]
        text = (
            f"{{::{args['source_count']}}}"
            if args.get("source_count") is not None
            else ""
        )
        expression = f"{left} {text}(({relation}))"
        rows.append(
            _record(
                source,
                expression,
                "relation_cardinality",
                source_selector=left,
                relation=relation,
                relation_notation=None,
                target_selector=None,
                source_cardinality=_helper_count(args.get("source_count")),
                target_cardinality=None,
                selection="all_relations"
                if relation == "*"
                else "named_relation",
                written_direction="forward",
                target_domain="unresolved",
                **suffix,
            )
        )
        return True
    return None


def _operator_value(args, source, carrier, rows, suffix, match):
    subject = (carrier.get("subjects") or {}).get("governs") or (
        carrier.get("subjects") or {}
    ).get("active", "")
    owner = _OPERATOR_SUBJECT.search(subject)
    value = args["value"]
    symbol = (
        json.loads(value)
        if isinstance(value, str) and value.startswith('"')
        else value
    )
    if (
        owner
        and owner["name"] == match[1]
        and isinstance(symbol, str)
        and symbol
    ):
        expression = (
            f"{args['address']} == {json.dumps(symbol, ensure_ascii=False)}"
        )
        rows.append(
            _record(
                source,
                expression,
                "operator_symbol",
                operator=match[1],
                symbol=symbol,
                **suffix,
            )
        )
    else:
        return False
    return True


def _unsupported_path(name, expression, source, diagnostics, suffix):
    diagnostics.append(
        {
            "code": "python-formal-claim-unsupported",
            "message": (
                f"Python Formal Claim helper {name} is outside "
                "the graph projection."
            ),
            "expression": expression,
            "source": dict(source),
            **suffix,
        }
    )


def _path_or_delivery(name, args, group, source, rows, diagnostics, suffix):
    expression = (
        f"{args['source']} >> {args['carrier']}"
        if name == "deliver"
        else args["address"]
    )
    if name == "subject_path" and group in {None, "model"}:
        subject = _subject_parse_subject_expression(
            expression, subject_profile="approved"
        ).expression
        if (
            isinstance(subject, _subject_Path)
            and isinstance(subject.head, _subject_Name)
            and subject.value_format is None
            and subject.value_cardinality is None
            and all(
                step.operator in {"/", "."}
                and isinstance(
                    step.operand, (_subject_Name, _subject_Qualification)
                )
                for step in subject.steps
            )
        ):
            rows.append(
                _record(
                    source,
                    expression,
                    "subject_expression",
                    selector=_subject_render_subject(subject),
                    **suffix,
                )
            )
            return True
    _unsupported_path(name, expression, source, diagnostics, suffix)
    return True


def _helper_call_2(
    name, args, group, source, carrier, rows, diagnostics, suffix
):
    if (
        name == "set_value"
        and (
            match := re.fullmatch(
                r"Operator//([A-Za-z_][A-Za-z_0-9]*)", args["address"]
            )
        )
        and group == "model"
    ):
        return _operator_value(args, source, carrier, rows, suffix, match)
    if name in {"deliver", "subject_path"}:
        return _path_or_delivery(
            name, args, group, source, rows, diagnostics, suffix
        )
    return None
