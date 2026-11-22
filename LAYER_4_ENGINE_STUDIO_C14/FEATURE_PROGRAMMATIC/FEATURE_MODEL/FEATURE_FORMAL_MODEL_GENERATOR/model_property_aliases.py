"""Resolve unique declared and inherited Model class Property addresses."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import canonical_model_address
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import model_class_target


def _class_roots(parsed):
    roots, bases = {}, {}
    for _, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] != "entity" or "entity_class" not in args:
            continue
        root = model_class_target(subject, args["entity_name"])
        if root:
            name = args["entity_class"]
            roots.setdefault(name, []).append(canonical_model_address(root))
            for item in declaration["classes"]:
                if item["name"] == name:
                    bases[name] = item["bases"]
    return {name: paths[0] for name, paths in roots.items() if len(paths) == 1}, bases


def _ancestors(name, roots, bases):
    pending, seen = list(bases.get(name, ())), set()
    while pending:
        current = pending.pop()
        if current == "object" or current in seen:
            continue
        if current not in roots or current not in bases:
            return None
        seen.add(current)
        pending.extend(bases[current])
    return seen


def class_property_aliases(parsed):
    canonical = {canonical_model_address(subject) for _, subject, _ in parsed}
    roots, bases = _class_roots(parsed)
    properties = {name: {address[len(root):]: address for address in canonical
                         if address.startswith(root + ".")}
                  for name, root in roots.items()}
    aliases = set()
    for name in roots:
        direct = properties[name]
        ancestors = _ancestors(name, roots, bases)
        inherited = {}
        if ancestors is not None:
            for ancestor in ancestors:
                for suffix, address in properties[ancestor].items():
                    inherited.setdefault(suffix, set()).add(address)
        for suffix in direct.keys() | inherited.keys():
            if suffix in direct or len(inherited[suffix]) == 1:
                aliases.update({name + suffix, roots[name] + suffix} - canonical)
    return aliases
