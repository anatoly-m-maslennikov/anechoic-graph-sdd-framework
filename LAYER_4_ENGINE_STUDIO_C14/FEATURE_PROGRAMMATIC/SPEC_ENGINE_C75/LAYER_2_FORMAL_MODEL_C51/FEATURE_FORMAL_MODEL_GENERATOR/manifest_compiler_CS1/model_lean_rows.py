"""Resolve Model rows and addresses for Lean obligations."""

from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    canonical_model_address,
    model_class_target,
)
from ..FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _add_unambiguous_addresses,
    _class_property_aliases,
)


def _primary(parsed):
    nodes = []
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        kind = args.get("entity_kind")
        if declaration["kind"] != "entity":
            continue
        if "entity_class" in args and kind not in (None, "Primary"):
            raise ValueError(
                f"{source}: unsupported entity class kind {kind!r}"
            )
        if not (kind == "Primary" or kind is None and "entity_class" in args):
            continue
        name = args.get("entity_class")
        target = model_class_target(subject, args.get("entity_name"))
        classes = [
            item for item in declaration["classes"] if item["name"] == name
        ]
        if not isinstance(name, str) or not target or len(classes) != 1:
            raise ValueError(
                f"{source}: Primary Node class or resolved name is missing"
            )
        nodes.append(
            (
                source,
                name,
                canonical_model_address(target),
                classes[0]["bases"],
            )
        )
    return nodes


def _rows(records, bindings):
    sources = {}
    for source, subject, _ in records:
        if subject in sources:
            raise ValueError(f"{source}: duplicate Model Subject")
        sources[subject] = source
    parsed, seen = [], set()
    for subject, declaration in bindings["declarations"]:
        if subject not in sources or subject in seen:
            raise ValueError(
                f"{subject}: missing or duplicate resolved Model source"
            )
        seen.add(subject)
        parsed.append((sources[subject], subject, declaration))
    if not parsed:
        raise ValueError("Model has no resolved declarations")
    return sorted(parsed, key=lambda row: (row[1], row[0]))


def _addresses(parsed):
    addresses = {subject for _, subject, _ in parsed}
    addresses.update(_class_property_aliases(parsed))
    _add_unambiguous_addresses(addresses, parsed)
    result = set()
    for address in addresses:
        try:
            result.add(canonical_model_address(address))
        except ValueError:
            continue
    return sorted(result)


def _bucket(value):
    return sum(map(ord, value)) % 64


def _check_catalog_entry(source, args, name, catalog, expected, _string):
    for key, reverse in ((name, False), (args.get("inverse_alias"), True)):
        if key is None:
            continue
        _string(key)
        expected.append(key)
        entry = catalog.get(key)
        if (
            not isinstance(entry, (tuple, list))
            or len(entry) != 2
            or entry[0] != args
            or entry[1] is not reverse
        ):
            raise ValueError(
                f"{source}: Relation catalog entry differs: {key}"
            )
