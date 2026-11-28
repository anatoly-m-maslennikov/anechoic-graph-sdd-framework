"""Resolve inherited values for axes introduced on Node."""

from graphlib import TopologicalSorter


def _inherit_node_axes(records):
    axes = {
        axis
        for _, subject, declaration in records
        for axis in declaration["arguments"].get("allowed_axis_values", {})
        if subject == f"MODEL//ANECHOIC <+ Graph/Node >| {axis}"
    }
    if not axes:
        return
    nodes = {
        node["name"]: (declaration["arguments"], node["bases"])
        for _, _, declaration in records
        for node in declaration["classes"]
        if node["name"] == declaration["arguments"].get("entity_class")
    }
    parents = {
        name: tuple(base for base in bases if base in nodes)
        for name, (_, bases) in nodes.items()
    }
    classes, declared = {}, {}
    for name in TopologicalSorter(parents).static_order():
        args, _ = nodes[name]
        cls = type(name, tuple(classes[base] for base in parents[name]), {})
        classes[name] = cls
        own = args.get("axes", {})
        declared[cls] = {axis: own[axis] for axis in axes & own.keys()}
        effective = {
            axis: value
            for ancestor in reversed(cls.__mro__[1:-1])
            for axis, value in declared[ancestor].items()
        }
        if effective:
            args["axes"] = effective | own
