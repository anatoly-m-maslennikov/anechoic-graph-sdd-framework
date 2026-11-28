"""Validate native Model paths, population and fallback references."""


def _validate_fallback_chain(
    args, relation_names, canonical_address, canonical, error
):
    if "fallback_chain" in args:
        lookup, project = args["fallback_chain"]
        if lookup["lookup_relation"] not in relation_names:
            return error(
                f"unknown fallback Relation: {lookup['lookup_relation']}"
            )
        for full in (lookup["lookup_property"], project["project_property"]):
            try:
                if canonical_address(full) not in canonical:
                    return error(f"unknown fallback Property address: {full}")
            except TypeError, ValueError:
                return error(f"invalid fallback Property address: {full}")
        try:
            if canonical_address(project["project_entity"]) not in canonical:
                return error(
                    (
                        "unknown Project model address: "
                        f"{project['project_entity']}"
                    )
                )
        except TypeError, ValueError:
            return error(
                f"invalid Project model address: {project['project_entity']}"
            )

    return ()


def _validate_fallback(
    args,
    relation_names,
    canonical_address,
    canonical,
    simple_address,
    declared,
    error,
):
    result = _validate_fallback_chain(
        args, relation_names, canonical_address, canonical, error
    )
    if result:
        return result

    if "fallback_property_name" in args:
        bearer = args.get("base_path")
        if not isinstance(bearer, str):
            return error("fallback requires a bearer")
        for member in (
            args.get("entity_name"),
            args["fallback_property_name"],
        ):
            full = f"{bearer}.{member}"
            try:
                if simple_address(full) not in declared:
                    return error(f"unknown declared fallback Property: {full}")
            except TypeError, ValueError:
                return error(f"invalid fallback Property: {full}")
    return ()


def _validate_population(
    args,
    canonical_address,
    canonical,
    resolve_address,
    declared,
    relation_names,
    error,
):
    for rule in args.get("population_unique_constraints", ()):
        population = args.get(
            "population_entity_path",
            args.get("base_path", args["entity_name"]),
        )
        for relative in (
            *rule["keys"],
            *(("Header.State.Status",) if "status" in rule else ()),
        ):
            full = f"{population}.{relative}"
            try:
                if canonical_address(full) in canonical or resolve_address(
                    full, declared, relation_names, {}
                ):
                    continue
                return error(f"unknown population Property address: {full}")
            except TypeError, ValueError:
                return error(f"unknown population Property address: {full}")

    for dependency in args.get("population_functional_dependencies", ()):
        population = args.get("population_entity_path", args["base_path"])
        paths = (*dependency["keys"], *dependency["dependents"])
        if "status_groups" in dependency:
            paths = (*paths, "Header.State.Status")
        for relative in paths:
            full = f"{population}.{relative}"
            try:
                if canonical_address(full) not in canonical:
                    return error(
                        f"unknown population Property address: {full}"
                    )
            except TypeError, ValueError:
                return error(f"invalid population Property address: {full}")
    return ()


def _validate_model_addresses(
    paths,
    canonical_address,
    canonical,
    resolve_address,
    declared,
    relation_names,
    error,
):
    for address in paths:
        if not isinstance(address, str):
            return error("Model address must be a string")
        try:
            if canonical_address(address) in canonical:
                continue
        except ValueError:
            pass
        try:
            if not resolve_address(address, declared, relation_names, {}):
                return error(f"unknown Model address: {address}")
        except ValueError as exc:
            return error(str(exc))
    return ()


def _collect_relation_constraints(args, paths, relations, error):
    for field in (
        "model_relation_constraints",
        "instance_relation_constraints",
    ):
        constraints = args.get(field, {})
        if not isinstance(constraints, dict) or any(
            not isinstance(item, dict) for item in constraints.values()
        ):
            return error(f"{field} must map Relation names to constraints")
        relations.extend(constraints)
        for constraint in constraints.values():
            targets = constraint.get("target_entity_paths", ())
            if not isinstance(targets, (tuple, list)):
                return error(
                    "target_entity_paths must be a list of Model addresses"
                )
            paths.extend(targets)
    return ()


def _path_inputs(args, error):
    paths = [
        args[key]
        for key in (
            "base_path",
            "qualification_property_path",
            "population_entity_path",
        )
        if key in args
    ]
    for pair in args.get("ordered_dependent_property_pairs", ()):
        paths.extend(
            f"{args['base_path']}.{args['entity_name']}.{name}"
            for name in pair
        )
    endpoints = [
        args.get("source_endpoint", {}),
        args.get("target_endpoint", {}),
    ]
    for pair in args.get("endpoint_pairs", ()):
        endpoints.extend((pair["source_endpoint"], pair["target_endpoint"]))
    for endpoint in endpoints:
        paths.extend(endpoint.get("entity_paths", ()))
    relations = (
        ["IS_ORDERED_RIGHT_BEFORE"]
        if args.get("ordered_dependent_property_pairs")
        else []
    )
    for incoming in args.get("incoming_model_relations", ()):
        paths.append(incoming["source"])
        relations.append(incoming["relation"])
    result = _collect_relation_constraints(args, paths, relations, error)
    if result:
        return None, None, result
    return paths, relations, ()


def _validate_paths(
    declaration,
    args,
    relation_names,
    resolve_address,
    canonical_address,
    canonical,
    declared,
    error,
):
    paths, relations, result = _path_inputs(args, error)
    if result:
        return result
    result = _validate_model_addresses(
        paths,
        canonical_address,
        canonical,
        resolve_address,
        declared,
        relation_names,
        error,
    )
    if result:
        return result
    if declaration["kind"] == "entity" and args.get("relation_name"):
        relations.append(args["relation_name"])
    for relation in relations:
        if relation not in relation_names:
            return error(f"unknown Relation: {relation}")
    return ()
