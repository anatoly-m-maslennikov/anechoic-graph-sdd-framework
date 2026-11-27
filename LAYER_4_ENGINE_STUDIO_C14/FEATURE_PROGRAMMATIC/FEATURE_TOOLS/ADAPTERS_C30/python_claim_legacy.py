"""Render legacy Python Claim helpers as statements."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable

from .python_claim_values import (
    _RELATION, _count, _error, _items, _literal, _name, _optional_count, _reference, _text,
)


def _render_layout(name: str, args: dict, node: ast.AST, ref: Callable[[str], str]) -> str:
    if name == "deliver":
        return f"{ref('source')} >> {ref('carrier')}"
    if name == "copy_value":
        return f"{ref('address')} == {ref('source')}"
    if name == "minimum_value":
        minimum = args["minimum"]
        if type(minimum) is not int:
            raise _error(node, "minimum must be an integer")
        return f"{ref('address')} >= {minimum}"
    if name == "population":
        return f"{ref('address')}{_optional_count(args, 'count', node)}"
    if name == "path_template":
        template = json.dumps(_text(args["template"], "template", node), ensure_ascii=False)
        return f"{ref('address')} == PATH_TEMPLATE({template})"
    if name == "children":
        name_format = args.get("name_format", "")
        if name_format not in ("", "string"):
            _reference(name_format, "name_format", node, None)
        recursive = args.get("recursive", False)
        if type(recursive) is not bool:
            raise _error(node, "recursive must be a boolean")
        wildcard = "**" if recursive else "*"
        return f"{ref('address')}.{wildcard}[{name_format}]{_optional_count(args, 'occurrences', node)}"
    axis = _name(args["axis"], "axis", node)
    value = args["value"]
    if type(value) is int:
        value = str(value)
    else:
        value = _literal(value, node)
    grouped = args.get("grouped", False)
    if type(grouped) is not bool:
        raise _error(node, "grouped must be a boolean")
    notation = args.get("notation", "assignment")
    if notation == "relation" and not grouped:
        return f"{ref('address')} ((HAS_AXIS)) {axis} == {value}"
    if notation not in ("assignment", "allowed"):
        raise _error(node, "notation must be 'assignment', 'allowed', or 'relation' without grouping")
    assignment = f"{axis} == {value}" if notation == "assignment" else f"{axis}: {value}"
    return f"{ref('address')} >| " + (f"({assignment})" if grouped else assignment)


def _render(name: str, args: dict, node: ast.AST,
            validate_reference: Callable[[str], object] | None,
            validate_relation_endpoint: Callable[[str, object, str], object] | None = None) -> tuple[str, ...]:
    def ref(key: str) -> str:
        return _reference(args[key], key, node, validate_reference)

    if name in {"composition", "unique", "allow_roles_for_form", "children", "copy_value", "deliver",
                "classify", "path_template", "minimum_value", "population"}:
        return _render_structure(name, args, node, ref, validate_reference)
    if name == "property_rule":
        return _render_property_rule(args, node, ref)
    if name in {"allowed_children", "order_before", "allowed_values", "subject_path"}:
        return _render_property(name, args, node, ref)
    if name == "set_value":
        return _render_value(args, node, ref, validate_reference)
    return _render_relation(args, node, validate_reference, validate_relation_endpoint)


def _render_structure(name, args, node, ref, validate_reference):
    if name == "composition":
        parts = args["parts"]
        if not isinstance(parts, tuple) or not parts:
            raise _error(node, "parts must be a nonempty tuple")
        return (" <+ ".join([ref("container"), *(
            _reference(part, "part", node, validate_reference) for part in parts
        )]),)

    if name == "unique":
        keys = ", ".join(_reference(key, "key", node, None) for key in _items(args["keys"], "keys", node))
        return (f"UNIQUE({ref('population')}, ({keys}))",)

    if name == "allow_roles_for_form":
        participant = _text(args.get("participant", "a"), "participant", node)
        if not _RELATION.fullmatch(participant):
            raise _error(node, "participant must be an identifier")
        form = _name(args["form"], "form", node)
        roles = ", ".join(_name(role, "role", node) for role in _items(args["roles"], "roles", node))
        for address in ("Atom", "Atom.Header.Context.Form", "Atom.Header.Context.Role"):
            _reference(address, "address", node, validate_reference)
        return (f"FOR EACH ${participant}[<Atom>, (.Header.Context.Form = {form})]: "
                f"(${participant}.Header.Context.Role:: [in ({roles})]{{::1}})",)

    return (_render_layout(name, args, node, ref),)


def _render_property_rule(args, node, ref):
    address = ref("address")
    occurrence = _optional_count(args, "occurrences", node)
    value_count = _optional_count(args, "values", node)
    raw_format = args.get("value_format")
    if raw_format is None and not value_count:
        if occurrence:
            return (f"{address}{occurrence}",)
        raise _error(node, "property_rule requires a constraint")
    if raw_format is None:
        format_text = ""
    else:
        format_text = _text(raw_format, "value_format", node, empty=True)
        if format_text and not re.fullmatch(r"[A-Za-z0-9_,. +()/$-]+", format_text):
            raise _error(node, "value_format contains an unsupported character")
        format_text = f" [{format_text}]"
    return (f"{address}{occurrence}::{format_text}{value_count}",)


def _render_property(name, args, node, ref):
    if name == "allowed_children":
        address = ref("address")
        names = tuple(_name(item, "child name", node) for item in _items(args["names"], "names", node))
        name_format = args.get("name_format")
        if name_format is not None and name_format != "string":
            raise _error(node, "name_format must be 'string'")
        prefix = "string, " if name_format else ""
        return (f"{address}.*[{prefix}in ({', '.join(names)})]{{::{_count(args['occurrences'], 'occurrences', node)}}}",)

    if name == "order_before":
        return (f"{ref('first')} ;> {ref('second')}",)

    if name == "allowed_values":
        address = ref("address")
        quoted = args.get("quoted", False)
        if type(quoted) is not bool:
            raise _error(node, "quoted must be a boolean")
        values = tuple(
            json.dumps(_text(item, "value", node), ensure_ascii=False) if quoted else _literal(item, node)
            for item in _items(args["values"], "values", node)
        )
        count = _optional_count(args, "occurrences", node)
        if count:
            return (f"{address}:: [in ({', '.join(values)})]{count}",)
        return tuple(f"{address} :: {value}" for value in values)

    return (ref("address"),)


def _render_value(args, node, ref, validate_reference):
    address = _text(args["address"], "address", node)
    if re.match(r"alias\s*\(", address):
        match = re.fullmatch(r"alias\(Relation//([A-Za-z_][A-Za-z0-9_]*)\)", address)
        if match is None:
            raise _error(node, "invalid Relation alias address")
        _reference("Relation//" + match[1], "address", node, validate_reference)
        value = args["value"]
        if not isinstance(value, str):
            raise _error(node, "Relation alias must be a nonempty string")
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except (ValueError, TypeError) as error:
                raise _error(node, "value must be a valid quoted string") from error
        literal = json.dumps(_text(value, "Relation alias", node), ensure_ascii=False)
        return (f"{address} == {literal}",)
    address = ref("address")
    value = args["value"]
    if type(value) is bool:
        literal = str(value).lower()
    elif type(value) is int:
        literal = str(value)
    elif isinstance(value, str):
        if value.startswith('"'):
            try:
                decoded = json.loads(value)
            except (ValueError, TypeError) as error:
                raise _error(node, "value must be a valid quoted string") from error
            literal = json.dumps(_text(decoded, "value", node, empty=True), ensure_ascii=False)
        else:
            literal = _literal(value, node)
    else:
        raise _error(node, "value must be a string, integer, or boolean")
    return (f"{address} == {literal}",)


def _render_relation(args, node, validate_reference, validate_relation_endpoint):
    def endpoint(key):
        if validate_relation_endpoint is None:
            check = validate_reference
        else:
            def check(value):
                return validate_relation_endpoint(value, args.get("name"), key)
        return _reference(args[key], key, node, check)

    source = endpoint("source")
    relation_name = _text(args["name"], "name", node)
    if relation_name != "*" and not _RELATION.fullmatch(relation_name):
        raise _error(node, "name must be a Relation name")
    source_count = _optional_count(args, "source_count", node)
    target_count = _optional_count(args, "target_count", node)
    target = f" {endpoint('target')}" if args.get("target") is not None else ""
    if target_count and not target:
        raise _error(node, "target_count requires target")
    reverse = args.get("reverse", False)
    if type(reverse) is not bool:
        raise _error(node, "reverse must be a boolean")
    operator = "<" if reverse else ""
    return (f"{source} {source_count}{operator}(({relation_name})){target_count}{target}",)
