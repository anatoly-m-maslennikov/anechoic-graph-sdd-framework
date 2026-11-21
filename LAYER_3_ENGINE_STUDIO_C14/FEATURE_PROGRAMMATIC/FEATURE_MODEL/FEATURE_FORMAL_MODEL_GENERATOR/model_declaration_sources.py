"""Select complete native Claims from an already-selected Declaration set."""

from collections.abc import Iterable, Mapping
from functools import cache
from typing import Any

from markdown_it import MarkdownIt

import subject_notation as notation
from carrier_aliases import matches_named_value
from lint_python_model_claim import _canonical_address, _resolve, _simple_address
from model_class_subject import model_class_target
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import NativeModelClaimError, parse_native_model_claim
from FEATURE_FORMAL_MODEL_ENGINE.native_model_lint import _validate_field_contracts, lint_native_model_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_property_order import order_properties
from .model_property_aliases import class_property_aliases as _class_property_aliases


def _is_claim_language_reference(expression: notation.Path | notation.RelationChain) -> bool:
    local = notation.namespace_local_expression(expression)
    if isinstance(local, notation.Path):
        return isinstance(local.head, notation.Name) and local.head.value == "CFEL" and not local.steps
    if not isinstance(local, notation.RelationChain) or len(local.endpoints) != 2:
        return False
    left, right = local.endpoints
    link, = local.links
    return (isinstance(left.head, notation.Name) and left.head.value == "CFEL" and not left.steps
            and link.operator == "<+" and link.relation_type is None
            and isinstance(right.head, notation.Name) and right.head.value == "Operator")


def _model_subject(subject: object, source: str) -> str | None:
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError(f"{source}: Declaration needs one Main Subject")
    try:
        expression = notation.parse_subject_expression(subject, subject_profile="approved").expression
    except notation.SubjectNotationError as error:
        raise ValueError(f"{source}: invalid Main Subject: {error}") from error
    if isinstance(expression, notation.RelationChain):
        first = expression.endpoints[0]
        if not (isinstance(first.head, notation.Name) and first.head.value == "ANECHOIC_MODEL"
                and not first.steps and expression.links[0].operator == "<+"
                and expression.links[0].relation_type is None):
            return None
    elif not (isinstance(expression.head, notation.Name)
              and expression.head.value == "ANECHOIC_MODEL" and not expression.steps):
        return None
    # Legacy Claim syntax remains available to its transitional consumers.
    if _is_claim_language_reference(expression):
        return None
    return notation.render_subject(expression)


def _native_claim(body: object, source: str, subject: str) -> str:
    if not isinstance(body, str):
        raise ValueError(f"{source}: Declaration body is missing")
    try:
        records = parse_content(body)
    except ValueError as error:
        raise ValueError(f"{source}: invalid Markdown: {error}") from error
    sections = [record for record in records if record["property_path"] == ["claim", "formal_claim"]]
    if len(sections) != 1 or not isinstance(text := sections[0]["direct_markdown"], str):
        raise ValueError(f"{source}: expected one Formal Claim")
    tokens = MarkdownIt("commonmark").parse(text)
    if len(tokens) != 1 or tokens[0].type != "fence" or tokens[0].info.strip().casefold() != "python":
        raise ValueError(f"{source}: Formal Claim must contain one Python fence")
    token = tokens[0]
    last_line = text.splitlines()[token.map[1] - 1].strip()
    if len(last_line) < len(token.markup) or set(last_line) != {token.markup[0]}:
        raise ValueError(f"{source}: Python fence is not closed")
    try:
        declaration = parse_native_model_claim(token.content)
    except (NativeModelClaimError, SyntaxError, ValueError) as error:
        raise ValueError(f"{source}: invalid native Python Claim: {error}") from error
    if declaration is None:
        raise ValueError(f"{source}: Formal Claim is not a native Python Declaration")
    arguments = declaration["arguments"]
    if "entity_class" in arguments and model_class_target(subject, arguments["entity_name"]) is None:
        raise ValueError(f"{source}: declared class does not match its Main Subject")
    if pairs := arguments.get("ordered_dependent_property_pairs"):
        try:
            order_properties((), pairs)
        except ValueError as error:
            raise ValueError(f"{source}: {error}") from error
    return token.content


def _class_compatibility(actual: str, expected: str, classes: dict) -> bool | None:
    """Use only known Python inheritance; unresolved bases leave the result unknown."""
    if actual is None or expected is None:
        return None
    if actual == expected:
        return True
    if actual not in classes or expected not in classes:
        return None
    pending, seen, unknown = [actual], set(), False
    while pending:
        name = pending.pop()
        if name == expected:
            return True
        if name in seen:
            continue
        seen.add(name)
        if name not in classes:
            unknown = True
        else:
            pending.extend(base for base in classes[name] if base != "object")
    return None if unknown else False


def _endpoint_compatibility(endpoint: dict, level: str, name: str, kinds: dict, classes: dict) -> bool | None:
    if level is not None and endpoint["level"] not in (level, "model_entities_or_instances"):
        return False
    paths = endpoint.get("entity_paths")
    if not paths:
        return True
    actual = kinds.get(_canonical_address(name))
    results = [_class_compatibility(actual, kinds.get(_canonical_address(path)), classes) for path in paths]
    return True if True in results else None if None in results else False


def _constraint_compatibility(args: dict, reverse: bool, level: str, source: str,
                              targets: tuple, kinds: dict, classes: dict) -> bool:
    pairs = args.get("endpoint_pairs")
    if not pairs:
        pairs = ({"source_endpoint": args["source_endpoint"], "target_endpoint": args["target_endpoint"]},)
    for target in targets or (None,):
        possibilities = []
        for pair in pairs:
            left, right = (pair["target_endpoint"], pair["source_endpoint"]) if reverse else (
                pair["source_endpoint"], pair["target_endpoint"])
            source_ok = _endpoint_compatibility(left, level, source, kinds, classes)
            target_ok = True if target is None else _endpoint_compatibility(right, None, target, kinds, classes)
            possibilities.append(source_ok is not False and target_ok is not False)
        if not any(possibilities):
            return False
    return True


def _check_constraint_endpoints(parsed: list, relations: dict) -> None:
    classes, class_counts, candidates = {}, {}, {}
    for _, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] == "entity" and "entity_class" in args:
            candidates.setdefault(args["entity_name"], []).append(args["entity_class"])
            target = model_class_target(subject, args["entity_name"])
            if target and _canonical_address(target) != args["entity_name"]:
                candidates.setdefault(_canonical_address(target), []).append(args["entity_class"])
            for item in declaration["classes"]:
                classes[item["name"]] = item["bases"]
                class_counts[item["name"]] = class_counts.get(item["name"], 0) + 1
    classes = {name: bases for name, bases in classes.items() if class_counts[name] == 1}
    kinds = {name: values[0] for name, values in candidates.items()
             if len(values) == 1 and values[0] in classes}
    for source, subject, declaration in parsed:
        if declaration["kind"] != "entity":
            continue
        args = declaration["arguments"]
        for field, level in (("model_relation_constraints", "model_entities"),
                             ("instance_relation_constraints", "instances")):
            for name, constraint in args.get(field, {}).items():
                if constraint.get("targets_per_source") == 0 or constraint.get("sources_per_target") == 0:
                    continue
                if name not in relations:
                    continue  # The reference lint reports this error.
                relation, reverse = relations[name]
                if not _constraint_compatibility(relation, reverse, level, subject,
                                                 constraint.get("target_entity_paths", ()), kinds, classes):
                    raise ValueError(f"{source}: {field} {name} is incompatible with Relation endpoints")


def _relation_registry(records: list) -> dict:
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


def _check_relation_classifications(records: list, relations: dict) -> None:
    allowed = {
        axis: values
        for _, _, declaration in records
        if declaration["kind"] == "entity" and declaration["arguments"].get("entity_name") == "Relation"
        for axis, values in declaration["arguments"].get("allowed_classification_values", {}).items()
    }
    for name, (args, reverse) in relations.items():
        key = "inverse_classifications" if reverse else "classifications"
        for axis, value in args.get(key, {}).items():
            if value not in allowed.get(axis, ()):
                raise ValueError(f"{name}: unadmitted Relation classification {axis}={value}")


def _merge_constraint_claims(parsed: list) -> list:
    """Attach separate constraint declarations to their canonical class owner."""
    owners = {}
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] != "entity" or "entity_class" not in args:
            continue
        target = model_class_target(subject, args["entity_name"])
        if target in owners:
            raise ValueError(f"{source}: duplicate Model class target: {target}")
        owners[target] = (source, declaration)
        if args.get("entity_kind") == "Primary":
            allowed = {"entity_name", "entity_class", "entity_kind", "identity_properties"}
            if args.keys() - allowed or declaration.get("instance_check"):
                raise ValueError(f"{source}: Primary class Declaration contains constraints")
    merged, seen = [], set()
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if "constraints_for" not in args:
            merged.append((source, subject, {**declaration, "arguments": dict(args)}))
            continue
        target = args["constraints_for"]
        if target not in owners:
            raise ValueError(f"{source}: unknown constraint owner: {target}")
        if target in seen:
            raise ValueError(f"{source}: duplicate constraint owner: {target}")
        seen.add(target)
        owner = owners[target][1]
        allowed = {"entity_name", "constraints_for", "instance_relation_constraints",
                   "population_unique_constraints", "instance_check"}
        if (declaration["kind"] != "entity" or args.keys() - allowed
                or args.get("entity_name") != owner["arguments"]["entity_name"] + " Constraints"):
            raise ValueError(f"{source}: invalid constraint Declaration")
    for source, subject, declaration in merged:
        args = declaration["arguments"]
        if "entity_class" not in args:
            continue
        target = model_class_target(subject, args["entity_name"])
        if target not in seen:
            continue
        constraint = next(item for _, _, item in parsed
                          if item["arguments"].get("constraints_for") == target)
        for key in ("instance_relation_constraints", "population_unique_constraints"):
            if key in constraint["arguments"]:
                if key in args:
                    raise ValueError(f"{source}: duplicate {key} for {target}")
                args[key] = constraint["arguments"][key]
        if constraint.get("instance_check"):
            if declaration.get("instance_check"):
                raise ValueError(f"{source}: duplicate instance check for {target}")
            declaration["instance_check"] = constraint["instance_check"]
    return merged


def _check_manifest_property_bearers(parsed):
    owners = {model_class_target(subject, args["entity_name"])
              for _, subject, declaration in parsed
              if (args := declaration["arguments"]).get("entity_kind") == "Primary"}
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if args.get("entity_kind") != "Property":
            continue
        bearer = args.get("base_path")
        if not isinstance(bearer, str) or bearer.split(".", 1)[0] not in owners:
            raise ValueError(f"{source}: unresolved Property bearer: {bearer}")
        scoped = args.get("applies_to_entity_classes", ())
        if not isinstance(scoped, tuple) or any(not isinstance(path, str) or path not in owners for path in scoped):
            raise ValueError(f"{source}: unresolved Property refinement owner: {scoped}")
        suffix = bearer[len(bearer.split(".", 1)[0]):]
        expected = tuple(f"{owner}{suffix if scoped else ''}.{args['entity_name']}"
                         for owner in (scoped or (bearer,)))
        actual = _canonical_address(subject)
        if actual not in expected:
            raise ValueError(f"{source}: Property scope mismatch: expected {expected}, actual {actual}")


def _check_relation_references(records: list[tuple[str, str, str]]) -> None:
    """Build the Relation registry, then check Entity and Relation references."""
    parsed = _merge_constraint_claims(
        [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records]
    )
    _check_manifest_property_bearers(parsed)
    relations = _relation_registry(parsed)
    _check_relation_classifications(parsed, relations)
    addresses = {subject for _, subject, _ in records}
    addresses.update(_class_property_aliases(parsed))
    short_names = {}
    declarations = [(source, declaration) for source, _, declaration in parsed]
    for source, subject, declaration in parsed:
        local = notation.namespace_local_expression(notation.parse_subject_expression(subject).expression)
        if declaration["kind"] == "entity" and isinstance(local, notation.RelationChain):
            target = model_class_target(subject, declaration["arguments"]["entity_name"])
            if target and _simple_address(target):
                short_names.setdefault(target, set()).add(subject)
        if isinstance(local, notation.Path) and isinstance(local.head, notation.Name):
            if not local.steps:
                short_names.setdefault(local.head.value, set()).add(subject)
            elif all(step.operator == "/" and isinstance(step.operand, notation.Name) for step in local.steps):
                short_names.setdefault(local.steps[-1].operand.value, set()).add(subject)
    addresses.update(name for name, subjects in short_names.items() if len(subjects) == 1)
    simple_address = cache(_simple_address)
    canonical_address = cache(_canonical_address)
    keys = {
        "source_endpoint", "target_endpoint", "endpoint_pairs", "relation_name",
        "incoming_model_relations", "model_relation_constraints", "instance_relation_constraints",
        "population_unique_constraints", "population_entity_path", "base_path", "entity_name",
    }
    for source, declaration in sorted(declarations, key=lambda item: item[1]["kind"] != "relation"):
        try:
            _validate_field_contracts(declaration)
        except ValueError as error:
            raise ValueError(f"{source}:{declaration['line']}:1: {error}") from error
        arguments = {key: value for key, value in declaration["arguments"].items() if key in keys}
        # A Relation's own name defines it; only entity Relation references need resolving.
        if declaration["kind"] == "relation":
            arguments.pop("relation_name", None)
        check = {**declaration, "arguments": arguments, "imports": {}, "classes": ()}
        check.pop("instance_check", None)
        errors = lint_native_model_claim(
            check, declared_addresses=addresses, relation_names=set(relations), path=source,
            first_line=1, resolve_address=_resolve, simple_address=simple_address,
            canonical_address=canonical_address,
        )
        if errors:
            raise ValueError(errors[0])
    _check_constraint_endpoints(parsed, relations)


def select_model_declarations(carriers: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, str, str], ...]:
    """Read Current Requirement Declaration carriers under ANECHOIC_MODEL.

    The caller selects Declaration forms. Input records use the existing current
    carrier reader shape, including source, read_view, subjects and body.
    """
    subjects, identifiers, records = {}, set(), []
    for carrier in carriers:
        source = carrier.get("source")
        if not isinstance(source, Mapping) or not isinstance(source.get("path"), str):
            raise ValueError("Declaration source path is missing")
        path = source["path"]
        view = carrier.get("read_view")
        if not isinstance(view, Mapping):
            raise ValueError(f"{path}: Declaration Header is missing")
        status = view.get("status")
        if not isinstance(status, str) or not status.strip():
            raise ValueError(f"{path}: Declaration Status is missing")
        if status.casefold() in {"draft", "archived", "backlog"}:
            continue
        if not matches_named_value(view.get("content_role"), "Requirement"):
            raise ValueError(f"{path}: selected Declaration must have Requirement Role")
        values = carrier.get("subjects")
        if not isinstance(values, Mapping):
            raise ValueError(f"{path}: Declaration Main Subject is missing")
        subject = _model_subject(values.get("active", values.get("governs")), path)
        if subject is None:
            continue
        identifier = source.get("atom_id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{path}: Declaration Atom ID is missing")
        if identifier in identifiers:
            raise ValueError(f"{path}: duplicate Current Declaration ID {identifier}")
        if subject in subjects:
            raise ValueError(f"{path}: duplicate Declaration Subject also in {subjects[subject]}")
        identifiers.add(identifier)
        subjects[subject] = path
        claim = _native_claim(carrier.get("body"), path, subject)
        records.append((path, subject, claim))
    if not records:
        raise ValueError("No Current ANECHOIC_MODEL Declarations were selected")
    _check_relation_references(records)
    return tuple(records)


def select_model_claims(carriers: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(claim for _, _, claim in select_model_declarations(carriers))
