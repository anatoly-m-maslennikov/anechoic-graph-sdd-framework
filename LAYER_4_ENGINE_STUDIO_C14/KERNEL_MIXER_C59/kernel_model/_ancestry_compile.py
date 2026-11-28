"""Collect declaration paths and compile their edges."""

from collections import defaultdict
import re

from ._ancestry_path import _NAME, _path

_REL = re.compile(
    rf"^\s*({_NAME})\s*\(\((NARROWER_THAN|INSTANCE_OF)\)\)\s*(.+?)\s*$"
)
_PROPERTY = re.compile(r"\.(?:Content|Header)(?=\.|\s|\[|\{|::|$)")


def _collect_items(items):
    aliases = defaultdict(set)
    parsed_items = []
    relations = []
    direct_statements = []
    for statement, source in items:
        relation = _REL.fullmatch(statement)
        if relation:
            child_name, _, parent_path = relation.groups()
            parent = _path(parent_path) if "$" not in parent_path else None
            if parent:
                nodes, trailing = parent
                aliases[child_name.strip()].add((child_name.strip(),))
                _record_aliases(aliases, nodes)
                relations.append((child_name.strip(), nodes, trailing, source))
            continue
        prop = next(
            (
                m
                for m in _PROPERTY.finditer(statement)
                if statement[: m.start()].count("(")
                == statement[: m.start()].count(")")
            ),
            None,
        )
        parsed = _path(statement[: prop.start()] if prop else statement)
        if not parsed:
            if statement.startswith("Atom") and not re.match(
                r"Atom/\*", statement
            ):
                direct_statements.append((statement, source))
            continue
        nodes, trailing = parsed
        if statement.startswith("Atom") and (not prop or len(nodes) == 1):
            direct_statements.append((statement, source))
        _record_aliases(aliases, nodes)
        parsed_items.append((statement, source, prop, nodes, trailing))

    return aliases, parsed_items, relations, direct_statements


def _record_aliases(aliases, nodes):
    address = (nodes[0][0],)
    aliases[nodes[0][0]].add(address)
    for name, op, _ in nodes[1:]:
        address += (op, name)
        aliases[name].add(address)


def _resolve(aliases, name):
    choices = aliases.get(name, set())
    extended = {a for a in choices if len(a) > 1}
    choices = extended or choices
    return next(iter(choices)) if len(choices) == 1 else None


def _compile_edges(aliases, parsed_items, relations):
    edges = defaultdict(list)
    bindings = defaultdict(list)
    properties = []
    for statement, source, prop, nodes, trailing in parsed_items:
        first = _resolve(aliases, nodes[0][0]) or (nodes[0][0],)
        address = first
        for name, op, selector in nodes[1:]:
            child = address + (op, name)
            edges[child].append((address, selector, source))
            address = child
        if prop:
            suffix = statement[prop.start() :]
            properties.append((statement, source, address, trailing, suffix))
            binding = re.match(
                r"^\.Header\.(?:Context\.)?(Role|Form)"
                r"\s*::\s*\[\s*in\s*\(([^()]*)\)\s*\]",
                suffix,
            )
            if binding:
                field, raw = binding.groups()
                vals = frozenset(
                    v.strip().strip("\"'") for v in raw.split(",") if v.strip()
                )
                if vals:
                    bindings[address].append((field, vals, source))
    for child_name, nodes, trailing, source in relations:
        address = _resolve(aliases, nodes[0][0]) or (nodes[0][0],)
        for name, op, selector in nodes[1:]:
            child = address + (op, name)
            edges[child].append((address, selector, source))
            address = child
        child = _resolve(aliases, child_name)
        if child is not None:
            edges[child].append((address, trailing, source))
    return edges, bindings, properties


