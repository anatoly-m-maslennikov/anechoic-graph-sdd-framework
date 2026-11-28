"""Build rows for the primary Model projections."""

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.model_entity_tree import model_axes, project_tree_rows

_ENTITY_FIELDS = {
    "entity_name",
    "entity_class",
    "entity_kind",
    "axes",
    "classifications",
}


def model_links(metadata, subjects, display_paths, node_link_prefix):
    links = [
        (
            path + "//" + label,
            display_paths[path] + "//" + label,
            label,
            path,
            "//",
            target,
        )
        for subject, items in metadata["node_parts"].items()
        if subject in subjects
        for path in (subjects[subject],)
        for label, target in items
        if label.startswith(node_link_prefix)
    ]
    return links


def model_axis_values(properties, normalize, canonical_model_address):
    axis_values = {}
    for subject, args in properties:
        allowed = args.get(
            "allowed_axis_values", args.get("allowed_classification_values")
        )
        declared = canonical_model_address(subject)
        if allowed and " >| " in declared:
            root, axis = declared.split(" >| ", 1)
            axis_values.setdefault(normalize(root), {})[axis] = allowed[axis]
    return axis_values


def primary_rows(
    tree,
    effective,
    arguments,
    subject_by_path,
    metadata,
    axis_values,
    json_value,
):
    return [
        (
            path,
            concern,
            name,
            json_value(effective[path]),
            json_value(model_axes(arguments[path])),
            json_value(
                {
                    key: value
                    for key, value in arguments[path].items()
                    if key not in _ENTITY_FIELDS
                }
                | {
                    key: definitions[subject]
                    for key, definitions in metadata.items()
                    if subject in definitions
                }
                | (
                    {"allowed_axis_values": axis_values[path]}
                    if path in axis_values
                    else {}
                )
            ),
        )
        for path, concern, name, _, _ in tree
        for subject in [subject_by_path[path]]
    ]


def replace_rows(
    connection,
    tree,
    links,
    effective,
    arguments,
    subject_by_path,
    metadata,
    axis_values,
    _json,
):
    connection.execute("DELETE FROM mrt_model_tree")
    connection.execute("DELETE FROM mrt_model_primary_entities")
    if tree:
        connection.executemany(
            "INSERT INTO mrt_model_tree (entity_path, concern_path, "
            "entity_name, parent_path, parent_operator, reference_path, "
            "tree_order, tree_line, axes, allowed_values) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            project_tree_rows(tree, links, arguments, axis_values, _json),
        )
        connection.executemany(
            (
                "INSERT INTO mrt_model_primary_entities (entity_path, "
                "concern_path, entity_name, properties, axes, node_rules) "
                "VALUES (?, ?, ?, ?, ?, ?)"
            ),
            primary_rows(
                tree,
                effective,
                arguments,
                subject_by_path,
                metadata,
                axis_values,
                _json,
            ),
        )
