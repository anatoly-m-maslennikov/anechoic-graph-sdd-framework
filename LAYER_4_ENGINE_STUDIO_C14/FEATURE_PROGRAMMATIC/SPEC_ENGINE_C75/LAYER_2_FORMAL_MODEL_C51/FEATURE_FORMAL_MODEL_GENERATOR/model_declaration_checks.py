"""Validate Model declaration endpoints and axes."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    namespace_local_expression as _subject_namespace_local_expression,
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    simple_model_address,
    canonical_model_address,
    model_class_target,
)


def _class_compatibility(
    actual: str, expected: str, classes: dict
) -> bool | None:
    """Use known inheritance; unresolved bases leave the result unknown."""
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


def _endpoint_compatibility(
    endpoint: dict, level: str, name: str, kinds: dict, classes: dict
) -> bool | None:
    if level is not None and endpoint["level"] not in (
        level,
        "model_entities_or_instances",
    ):
        return False
    paths = endpoint.get("entity_paths")
    if not paths:
        return True
    actual = kinds.get(canonical_model_address(name))
    results = [
        _class_compatibility(
            actual, kinds.get(canonical_model_address(path)), classes
        )
        for path in paths
    ]
    return True if True in results else None if None in results else False


def _constraint_compatibility(
    args: dict,
    reverse: bool,
    level: str,
    source: str,
    targets: tuple,
    kinds: dict,
    classes: dict,
) -> bool:
    pairs = args.get("endpoint_pairs")
    if not pairs:
        pairs = (
            {
                "source_endpoint": args["source_endpoint"],
                "target_endpoint": args["target_endpoint"],
            },
        )
    for target in targets or (None,):
        possibilities = []
        for pair in pairs:
            left, right = (
                (pair["target_endpoint"], pair["source_endpoint"])
                if reverse
                else (pair["source_endpoint"], pair["target_endpoint"])
            )
            source_ok = _endpoint_compatibility(
                left, level, source, kinds, classes
            )
            target_ok = (
                True
                if target is None
                else _endpoint_compatibility(
                    right, None, target, kinds, classes
                )
            )
            possibilities.append(
                source_ok is not False and target_ok is not False
            )
        if not any(possibilities):
            return False
    return True


def _check_constraint_endpoints(parsed: list, relations: dict) -> None:
    kinds, classes = _constraint_classes(parsed)
    for source, subject, declaration in parsed:
        if declaration["kind"] != "entity":
            continue
        args = declaration["arguments"]
        for field, level in (
            ("model_relation_constraints", "model_entities"),
            ("instance_relation_constraints", "instances"),
        ):
            for name, constraint in args.get(field, {}).items():
                if (
                    constraint.get("targets_per_source") == 0
                    or constraint.get("sources_per_target") == 0
                ):
                    continue
                if name not in relations:
                    continue
                relation, reverse = relations[name]
                if not _constraint_compatibility(
                    relation,
                    reverse,
                    level,
                    subject,
                    constraint.get("target_entity_paths", ()),
                    kinds,
                    classes,
                ):
                    raise ValueError(
                        f"{source}: {field} {name} is incompatible "
                        "with Relation endpoints"
                    )


def _constraint_classes(parsed):
    classes, class_counts, candidates = {}, {}, {}
    for _, subject, declaration in parsed:
        args = declaration["arguments"]
        if declaration["kind"] == "entity" and "entity_class" in args:
            candidates.setdefault(args["entity_name"], []).append(
                args["entity_class"]
            )
            target = model_class_target(subject, args["entity_name"])
            if (
                target
                and canonical_model_address(target) != args["entity_name"]
            ):
                candidates.setdefault(
                    canonical_model_address(target), []
                ).append(args["entity_class"])
            for item in declaration["classes"]:
                classes[item["name"]] = item["bases"]
                class_counts[item["name"]] = (
                    class_counts.get(item["name"], 0) + 1
                )
    classes = {
        name: bases
        for name, bases in classes.items()
        if class_counts[name] == 1
    }
    kinds = {
        name: values[0]
        for name, values in candidates.items()
        if len(values) == 1 and values[0] in classes
    }
    return kinds, classes


def relation_axis_values(records):
    allowed = {}
    for source, subject, declaration in records:
        args = declaration["arguments"]
        if (
            declaration["kind"] != "entity"
            or args.get("entity_name") != "Relation"
        ):
            continue
        for axis, values in args.get("allowed_axis_values", {}).items():
            if axis in allowed:
                raise ValueError(f"{source}: duplicate Relation axis: {axis}")
            if subject != f"MODEL//ANECHOIC <+ Graph/Relation >| {axis}":
                raise ValueError(
                    f"{source}: invalid Relation axis scope: {axis}"
                )
            allowed[axis] = values
    return allowed


def _check_relation_axes(records: list, relations: dict) -> None:
    allowed = relation_axis_values(records)
    for name, (args, reverse) in relations.items():
        key = "inverse_axes" if reverse else "axes"
        for axis, value in args.get(key, {}).items():
            if value not in allowed.get(axis, ()):
                raise ValueError(
                    f"{name}: unadmitted Relation axis {axis}={value}"
                )


def _check_node_axes(records: list, typed_sources: set) -> None:
    allowed = {}
    for source, subject, declaration in records:
        args = declaration["arguments"]
        if declaration["kind"] != "entity" or args.get("entity_name") not in {
            "Node",
            "Axis",
            "Classification",
        }:
            continue
        for axis, values in args.get("allowed_axis_values", {}).items():
            if (
                subject
                != f"MODEL//ANECHOIC <+ Graph/{args['entity_name']} >| {axis}"
                or axis in allowed
            ):
                raise ValueError(
                    f"{source}: ambiguous or invalid axis: {axis}"
                )
            allowed[axis] = values
    for source, _, declaration in records:
        args = declaration["arguments"]
        if (
            source in typed_sources
            and declaration["kind"] == "entity"
            and args.get("entity_kind") == "Primary"
        ):
            for axis, value in args.get("axes", {}).items():
                if value not in allowed.get(axis, ()):
                    raise ValueError(
                        f"{source}: unadmitted Entity axis {axis}={value}"
                    )


def _check_manifest_property_bearers(parsed):
    owners = {
        model_class_target(subject, args["entity_name"])
        for _, subject, declaration in parsed
        if (args := declaration["arguments"]).get("entity_kind") == "Primary"
    }
    for source, subject, declaration in parsed:
        args = declaration["arguments"]
        if args.get("entity_kind") != "Property":
            continue
        bearer = args.get("base_path")
        if (
            not isinstance(bearer, str)
            or bearer.split(".", 1)[0] not in owners
        ):
            raise ValueError(f"{source}: unresolved Property bearer: {bearer}")
        scoped = args.get("applies_to_entity_classes", ())
        if not isinstance(scoped, tuple) or any(
            not isinstance(path, str) or path not in owners for path in scoped
        ):
            raise ValueError(
                f"{source}: unresolved Property refinement owner: {scoped}"
            )
        suffix = bearer[len(bearer.split(".", 1)[0]) :]
        expected = tuple(
            f"{owner}{suffix if scoped else ''}.{args['entity_name']}"
            for owner in (scoped or (bearer,))
        )
        actual = canonical_model_address(subject)
        if actual not in expected:
            raise ValueError(
                f"{source}: Property scope mismatch: expected {expected}, "
                f"actual {actual}"
            )


def _add_unambiguous_addresses(addresses: set, parsed: list) -> None:
    short_names = {}
    for source, subject, declaration in parsed:
        local = _subject_namespace_local_expression(
            _subject_parse_subject_expression(subject).expression
        )
        if declaration["kind"] == "entity" and isinstance(
            local, _subject_RelationChain
        ):
            target = model_class_target(
                subject, declaration["arguments"]["entity_name"]
            )
            if target and simple_model_address(target):
                short_names.setdefault(target, set()).add(subject)
        if isinstance(local, _subject_Path) and isinstance(
            local.head, _subject_Name
        ):
            if not local.steps:
                short_names.setdefault(local.head.value, set()).add(subject)
            elif all(
                step.operator == "/"
                and isinstance(step.operand, _subject_Name)
                for step in local.steps
            ):
                short_names.setdefault(
                    local.steps[-1].operand.value, set()
                ).add(subject)
    addresses.update(
        name for name, subjects in short_names.items() if len(subjects) == 1
    )
