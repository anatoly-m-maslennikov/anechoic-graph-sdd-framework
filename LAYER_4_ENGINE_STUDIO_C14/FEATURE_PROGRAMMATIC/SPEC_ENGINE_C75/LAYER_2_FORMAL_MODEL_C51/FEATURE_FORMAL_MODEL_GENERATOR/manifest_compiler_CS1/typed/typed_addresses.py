"""Build unambiguous names from legacy and scoped typed sources."""

import ast
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    model_class_target,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)


def _symbol(part):
    return "".join(
        word[:1].upper() + word[1:]
        for word in re.findall(r"[A-Za-z0-9]+", part)
    )


def _collect_typed_addresses(typed, add, property_paths):
    unscoped = []
    for _, subject, text in typed:
        tree = ast.parse(text)
        classes = [
            item for item in tree.body if isinstance(item, ast.ClassDef)
        ]
        if len(classes) != 1:
            continue
        node = classes[0]
        bases = {base.id for base in node.bases if isinstance(base, ast.Name)}
        if not subject:
            unscoped.append(node)
            continue
        path = subject.split(" <+ ", 1)[1]
        if bases & {"Property", "Relation", "NodeConstraints"}:
            if "Property" in bases and "." in path:
                property_paths.add(path)
        else:
            add(node.name, path)
    return unscoped


def typed_addresses(records, typed):
    candidates, property_paths = {}, set()

    def add(key, value):
        candidates.setdefault(key, set()).add(value)

    for _, subject, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration["arguments"]
        if (name := args.get("entity_class")) and (
            target := model_class_target(subject, args["entity_name"])
        ):
            add(name, target)
        if args.get("entity_kind") == "Property":
            property_paths.add(args["base_path"] + "." + args["entity_name"])
    unscoped = _collect_typed_addresses(typed, add, property_paths)
    _resolve_unscoped(unscoped, candidates, add)
    roots = {
        key: next(iter(values))
        for key, values in candidates.items()
        if len(values) == 1
    }
    for name, root in roots.items():
        for path in property_paths:
            if path.startswith(root + "."):
                suffix = path[len(root) + 1 :]
                parts = suffix.split(".")
                for end in range(1, len(parts) + 1):
                    add(
                        name
                        + "."
                        + ".".join(_symbol(part) for part in parts[:end]),
                        root + "." + ".".join(parts[:end]),
                    )
    return {
        key: next(iter(values))
        for key, values in candidates.items()
        if len(values) == 1
    }


def _resolve_unscoped(unscoped, candidates, add):
    while unscoped:
        progress = False
        for node in unscoped[:]:
            if len(node.bases) != 1 or not isinstance(node.bases[0], ast.Name):
                continue
            values = candidates.get(node.bases[0].id, set())
            if len(values) == 1:
                add(node.name, next(iter(values)) + "//" + node.name)
                unscoped.remove(node)
                progress = True
        if not progress:
            break
