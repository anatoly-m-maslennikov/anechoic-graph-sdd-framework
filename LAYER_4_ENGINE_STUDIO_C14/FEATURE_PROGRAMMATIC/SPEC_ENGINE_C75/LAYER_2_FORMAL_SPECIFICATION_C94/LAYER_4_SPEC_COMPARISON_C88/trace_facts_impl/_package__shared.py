"""Package entry points for comparison facts."""


def compare_http_workflow(sources, contract, workflow, lean):
    from .http_spec import compare_http_workflow as implementation

    return implementation(sources, contract, workflow, lean)


def trace_claims(model, claims, operation_claims):
    from .trace_facts import trace_claims as implementation

    return implementation(model, claims, operation_claims)


def workflow_facts(contract, workflow, statuses):
    from .trace_facts import workflow_facts as implementation

    return implementation(contract, workflow, statuses)


def _binding_directions(sources, claims, contract, workflow, lean):
    from .trace_manifest import _binding_directions as implementation

    return implementation(sources, claims, contract, workflow, lean)


def _manifest_binding(manifest, contract):
    from .trace_manifest import _manifest_binding as implementation

    return implementation(manifest, contract)


def _manifest_contract(cases, contract, lean):
    from .trace_manifest import _manifest_contract as implementation

    return implementation(cases, contract, lean)


def _solution_binding(workflow, binding):
    from .trace_manifest import _solution_binding as implementation

    return implementation(workflow, binding)


def _trace_cases(contract):
    from .trace_manifest import _trace_cases as implementation

    return implementation(contract)


def compare_trace_values(case, events, *, lean="lean"):
    from .trace_values import compare_trace_values as implementation

    return implementation(case, events, lean=lean)
