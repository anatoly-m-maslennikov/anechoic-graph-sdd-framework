"""Assemble a catalog of declared Relations and inverse aliases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation


def build_relation_declaration_catalog(records: list) -> dict:
    """Assemble canonical Relations and their inverse aliases before Entity checks."""
    relations = {}
    for source, subject, declaration in records:
        if declaration["kind"] != "relation":
            continue
        args = declaration["arguments"]
        local = notation.namespace_local_expression(notation.parse_subject_expression(subject).expression)
        endpoint = local.endpoints[-1] if isinstance(local, notation.RelationChain) else local
        if not (isinstance(endpoint, notation.Path) and isinstance(endpoint.head, notation.Name)
                and endpoint.head.value == "Relation" and len(endpoint.steps) == 1
                and endpoint.steps[0].operator == "//"
                and isinstance(endpoint.steps[0].operand, notation.Name)
                and endpoint.steps[0].operand.value == args["relation_name"]):
            raise ValueError(f"{source}: declared Relation does not match its Main Subject")
        for name, reverse in ((args["relation_name"], False), (args.get("inverse_alias"), True)):
            if name is None:
                continue
            if name in relations:
                raise ValueError(f"{source}: duplicate Relation name: {name}")
            relations[name] = (args, reverse)
    for source, _, declaration in records:
        if declaration["kind"] != "relation" or "derived_from" not in declaration["arguments"]:
            continue
        args = declaration["arguments"]
        derived = args["derived_from"]
        if not isinstance(derived, str) or derived not in relations:
            raise ValueError(f"{source}: unknown derived_from Relation: {derived}")
        if relations[derived][0] is args:
            raise ValueError(f"{source}: Relation cannot derive from itself: {derived}")
    return relations


