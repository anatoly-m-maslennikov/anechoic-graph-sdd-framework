"""Keep the legacy inverse projection consistent across Model readers."""


def emits_instance_inverse(arguments):
    """Return whether the legacy compiler emits an instance inverse binding."""
    # Ordering is read from the declared sequence of sibling Properties.
    if arguments["relation_name"] == "IS_ORDERED_RIGHT_AFTER":
        return False
    instance_levels = {"instances", "model_entities_or_instances"}
    pairs = arguments.get("endpoint_pairs", (arguments,))
    return any(
        pair["source_endpoint"]["level"] in instance_levels
        and pair["target_endpoint"]["level"] in instance_levels
        for pair in pairs
    )
