"""Build the primary Model entity tree from admitted declarations."""

import re
from collections import defaultdict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (
    NODE_LINK_PREFIX,
)

MODEL_TREE_COLUMNS = {
    "reference_path": "VARCHAR",
    "tree_order": "BIGINT",
    "tree_line": "VARCHAR",
    "axes": "JSON",
    "allowed_values": "JSON",
}


def ensure_model_tree(connection):
    tree_columns_sql = ", ".join(
        f"{name} {kind}" for name, kind in MODEL_TREE_COLUMNS.items()
    )
    connection.execute(f"""CREATE TABLE IF NOT EXISTS mrt_model_tree (
        entity_path VARCHAR PRIMARY KEY, concern_path VARCHAR, entity_name VARCHAR,
        parent_path VARCHAR, parent_operator VARCHAR, {tree_columns_sql})""")
    tree_columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info('mrt_model_tree')"
        ).fetchall()
    }
    for name, kind in MODEL_TREE_COLUMNS.items():
        if name not in tree_columns:
            connection.execute(
                f"ALTER TABLE mrt_model_tree ADD COLUMN {name} {kind}"
            )


def model_tree_rows(entities, locations, normalize):
    paths = {path for _, path, _ in entities}
    nodes = {}
    for subject, path, args in entities:
        parts = re.split(r"(//|/)", path)
        parent, operator, label = locations.get(
            subject,
            (
                "".join(parts[:-2]),
                parts[-2] if len(parts) > 1 else None,
                parts[-1],
            ),
        )
        parent = normalize(parent) if parent else None
        if parent not in paths:
            if subject not in locations:
                label = path
            parent, operator = None, None
        nodes[path] = (args["entity_name"], parent, operator, label)

    def display(path, visited):
        if path in visited:
            raise ValueError(f"Cycle in Model entity tree: {path}")
        _, parent, operator, label = nodes[path]
        return (
            display(parent, visited | {path}) + operator + label
            if parent
            else label
        )

    return [
        (path, display(path, set()), name, parent, operator)
        for path, (name, parent, operator, _) in sorted(nodes.items())
    ]


def model_axes(arguments):
    return arguments.get("axes", arguments.get("classifications", {}))


def project_tree_rows(tree, links, arguments, axis_values, json_value):
    rows = [(*row, None) for row in tree] + links
    domains = {}
    for path, concern, _, _, _ in tree:
        for axis, values in axis_values.get(path, {}).items():
            address = path + " >| " + axis
            rows.append(
                (address, concern + " >| " + axis, axis, path, " >| ", None)
            )
            domains[address] = values
    return render_tree_rows(rows, arguments, domains, json_value)


def render_tree_rows(rows, arguments, domains, json_value):
    concerns = {row[0]: row[1] for row in rows}
    children = defaultdict(list)
    for row in sorted(rows, key=lambda row: (row[1], row[0])):
        children[row[3]].append(row)
    result = []

    def visit(row, depth):
        path, concern, _, parent, operator, reference = row
        axes = model_axes(arguments.get(path, {}))
        label = (
            concern.removeprefix(concerns[parent] + operator)
            if parent is not None
            else concern
        )
        if reference is not None:
            label = label.removeprefix(NODE_LINK_PREFIX)
        result.append(
            (
                *row,
                len(result) + 1,
                "    " * depth + label,
                json_value(axes),
                json_value(domains[path]) if path in domains else None,
            )
        )
        for child in children[path]:
            visit(child, depth + 1)

    for row in children[None]:
        visit(row, 0)
    return result
