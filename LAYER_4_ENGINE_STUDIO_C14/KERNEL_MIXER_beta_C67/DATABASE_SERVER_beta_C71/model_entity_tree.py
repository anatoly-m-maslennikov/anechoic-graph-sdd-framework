"""Build the primary Model entity tree from admitted declarations."""

import re


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
