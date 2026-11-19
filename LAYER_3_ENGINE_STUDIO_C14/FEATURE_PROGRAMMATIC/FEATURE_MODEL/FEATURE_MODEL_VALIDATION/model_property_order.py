"""Derive the order of present sibling Properties from declared pairs."""


def order_properties(properties, pairs):
    """Return the ordered Property names, skipping names that are absent."""
    names = list(properties)
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Property names must be distinct nonempty strings")
    successors = {}
    predecessors = {}
    for pair in pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("Each ordering pair must contain two Property names")
        first, second = pair
        if any(not isinstance(name, str) or not name for name in pair):
            raise ValueError("Ordering pairs require nonempty Property names")
        if first in successors or second in predecessors:
            raise ValueError("Ordering pairs have multiple predecessors or successors")
        successors[first] = second
        predecessors[second] = first
    ordered_names = set(successors) | set(predecessors)
    if not ordered_names:
        return names
    starts = ordered_names - predecessors.keys()
    if len(starts) != 1:
        raise ValueError("Ordering pairs contain a cycle or disconnected chains")
    chain = []
    current = starts.pop()
    while current is not None:
        chain.append(current)
        current = successors.get(current)
    if len(chain) != len(ordered_names):
        raise ValueError("Ordering pairs contain a cycle or disconnected chains")
    present = set(names)
    return [name for name in chain if name in present] + [name for name in names if name not in ordered_names]


def validate_property_order(properties, pairs):
    """Check observed order against the applicable Declaration's sibling pairs."""
    observed = list(properties)
    if observed != order_properties(observed, pairs):
        raise ValueError("Sibling Properties are out of their declared order")
