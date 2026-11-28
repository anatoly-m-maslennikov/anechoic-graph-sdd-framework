"""Package entry points for comparison facts."""

_BINDING_FIELDS = (
    "transport",
    "runner",
    "path",
    "module",
    "command",
    "arguments",
    "input_fields",
    "optional_paired_inputs",
    "stdin",
)


def feasible_terminals(claim):
    from .cli_reachability import feasible_terminals as implementation

    return implementation(claim)


def _cli_profiles(claims, interface, *, action=None):
    from .cli_selection import _cli_profiles as implementation

    return implementation(claims, interface, action=action)


def _initial_trigger(claim):
    from .cli_selection import _initial_trigger as implementation

    return implementation(claim)


def _manifest_endpoint(manifest, interface):
    from .cli_selection import _manifest_endpoint as implementation

    return implementation(manifest, interface)


def _common_checks(details, names):
    from .cli_workflow_checks import _common_checks as implementation

    return implementation(details, names)


def _first_dispatch(states, starts, detail_fields):
    from .cli_workflow_checks import _first_dispatch as implementation

    return implementation(states, starts, detail_fields)


def _query_checks(claim, edges, successes, component_id):
    from .cli_workflow_checks import _query_checks as implementation

    return implementation(claim, edges, successes, component_id)


def _reachable_without(claim, blocked):
    from .cli_workflow_checks import _reachable_without as implementation

    return implementation(claim, blocked)


def _release_checks(claim, edges):
    from .cli_workflow_checks import _release_checks as implementation

    return implementation(claim, edges)


def _solution_outcomes(claim, contract):
    from .cli_workflow_checks import _solution_outcomes as implementation

    return implementation(claim, contract)


def _success_outputs(terminals):
    from .cli_workflow_checks import _success_outputs as implementation

    return implementation(terminals)


def _manifest_facts(endpoint, interface):
    from .cli_manifest_facts import _manifest_facts as implementation

    return implementation(endpoint, interface)
