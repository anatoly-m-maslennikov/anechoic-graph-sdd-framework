"""Validate structured legacy Python Claim helpers."""

from __future__ import annotations

import json
import re

from .python_claim_values import (
    _RELATION, _count, _error, _items, _name, _reference, _text,
)


def _validate_structured_call(name, args, node, validate_reference, validate_relation_endpoint):
    """Validate helper arguments without constructing a legacy expression."""
    def ref(key, callback=validate_reference):
        return _reference(args[key], key, node, callback)

    def count(key):
        if args.get(key) is not None:
            _count(args[key], key, node)

    if name in {"composition", "unique", "allow_roles_for_form"}:
        _validate_structure(name, args, node, ref, validate_reference)
    elif name == "relation":
        _validate_relation(args, node, ref, count, validate_reference, validate_relation_endpoint)
    elif name == "order_before":
        ref("first")
        ref("second")
    elif name in {"deliver", "copy_value"}:
        for key in (("source", "carrier") if name == "deliver" else ("address", "source")):
            ref(key)
    elif name == "set_value":
        _validate_value(args, node, ref, validate_reference)
    else:
        ref("address")
        if name in {"property_rule", "allowed_children", "allowed_values"}:
            _validate_property(name, args, node, count)
        else:
            _validate_layout(name, args, node, count)


def _validate_structure(name, args, node, ref, validate_reference):
    if name == "composition":
        ref("container")
        parts = args["parts"]
        if not isinstance(parts, tuple) or not parts:
            raise _error(node, "parts must be a nonempty tuple")
        for part in parts:
            _reference(part, "part", node, validate_reference)
    elif name == "unique":
        ref("population")
        for key in _items(args["keys"], "keys", node):
            _reference(key, "key", node, None)
    elif name == "allow_roles_for_form":
        participant = _text(args.get("participant", "a"), "participant", node)
        if not _RELATION.fullmatch(participant):
            raise _error(node, "participant must be an identifier")
        _name(args["form"], "form", node)
        for role in _items(args["roles"], "roles", node):
            _name(role, "role", node)
        for address in ("Atom", "Atom.Header.Context.Form", "Atom.Header.Context.Role"):
            _reference(address, "address", node, validate_reference)


def _validate_relation(args, node, ref, count, validate_reference, validate_relation_endpoint):
    def endpoint(key):
        callback = validate_reference if validate_relation_endpoint is None else (
            lambda value: validate_relation_endpoint(value, args.get("name"), key))
        ref(key, callback)
    endpoint("source")
    relation_name = _text(args["name"], "name", node)
    if relation_name != "*" and not _RELATION.fullmatch(relation_name):
        raise _error(node, "name must be a Relation name")
    count("source_count")
    count("target_count")
    if args.get("target") is not None:
        endpoint("target")
    elif args.get("target_count") is not None:
        raise _error(node, "target_count requires target")
    if type(args.get("reverse", False)) is not bool:
        raise _error(node, "reverse must be a boolean")


def _validate_value(args, node, ref, validate_reference):
    address = _text(args["address"], "address", node)
    alias = re.match(r"alias\s*\(", address)
    if alias:
        match = re.fullmatch(r"alias\(Relation//([A-Za-z_][A-Za-z0-9_]*)\)", address)
        if match is None:
            raise _error(node, "invalid Relation alias address")
        _reference("Relation//" + match[1], "address", node, validate_reference)
    else:
        ref("address")
    value = args["value"]
    if alias and not isinstance(value, str):
        raise _error(node, "Relation alias must be a nonempty string")
    if isinstance(value, str):
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except (ValueError, TypeError) as error:
                raise _error(node, "value must be a valid quoted string") from error
            _text(value, "Relation alias" if alias else "value", node, empty=not alias)
        else:
            _text(value, "Relation alias" if alias else "value", node)
    elif type(value) not in (int, bool):
        raise _error(node, "value must be a string, integer, or boolean")


def _validate_property(name, args, node, count):
    if name == "property_rule":
        count("occurrences")
        count("values")
        fmt = args.get("value_format")
        if fmt is None and args.get("values") is None and args.get("occurrences") is None:
            raise _error(node, "property_rule requires a constraint")
        if fmt is not None:
            fmt = _text(fmt, "value_format", node, empty=True)
            if fmt and not re.fullmatch(r"[A-Za-z0-9_,. +()/$-]+", fmt):
                raise _error(node, "value_format contains an unsupported character")
    elif name == "allowed_children":
        for child in _items(args["names"], "names", node):
            _name(child, "child name", node)
        if args.get("name_format") not in (None, "string"):
            raise _error(node, "name_format must be 'string'")
        _count(args["occurrences"], "occurrences", node)
    elif name == "allowed_values":
        if type(args.get("quoted", False)) is not bool:
            raise _error(node, "quoted must be a boolean")
        for value in _items(args["values"], "values", node):
            _text(value, "value", node)
        count("occurrences")


def _validate_layout(name, args, node, count):
    if name == "children":
        fmt = args.get("name_format", "")
        if fmt not in ("", "string"):
            _reference(fmt, "name_format", node, None)
        if type(args.get("recursive", False)) is not bool:
            raise _error(node, "recursive must be a boolean")
        count("occurrences")
    elif name == "classify":
        _name(args["axis"], "axis", node)
        if type(args["value"]) is not int:
            _text(args["value"], "value", node)
        grouped = args.get("grouped", False)
        if type(grouped) is not bool:
            raise _error(node, "grouped must be a boolean")
        notation = args.get("notation", "assignment")
        if notation not in ("assignment", "allowed") and not (notation == "relation" and not grouped):
            raise _error(node, "notation must be 'assignment', 'allowed', or 'relation' without grouping")
    elif name == "path_template":
        _text(args["template"], "template", node)
    elif name == "minimum_value":
        if type(args["minimum"]) is not int:
            raise _error(node, "minimum must be an integer")
    elif name == "population":
        count("count")
