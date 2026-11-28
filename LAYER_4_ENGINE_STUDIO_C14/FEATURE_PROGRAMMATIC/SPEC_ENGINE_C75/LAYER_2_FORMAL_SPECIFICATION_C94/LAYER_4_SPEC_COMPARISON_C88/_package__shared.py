from .cli_selection import (
    _cli_profiles as _cli_profiles,
    _initial_trigger as _initial_trigger,
    _manifest_endpoint as _manifest_endpoint,
)
from .cli_spec__pub import (
    _dispatch_facts as _dispatch_facts,
    _outcome_stdout as _outcome_stdout,
    _workflow_facts as _workflow_facts,
    check_cli_spec as check_cli_spec,
    compare_cli_spec as compare_cli_spec,
)
from .group_spec__pub import check_group_spec as check_group_spec
from .shape_spec__pub import (
    check_shape_spec as check_shape_spec,
    compare_shape_spec as compare_shape_spec,
)
from .tool_api_obligations__pub import (
    manifest_tool_api as manifest_tool_api,
    solution_tool_api as solution_tool_api,
)
from .tool_api_spec__pub import (
    _tool_contract as _tool_contract,
    _tool_solution as _tool_solution,
    check_tool_api_spec as check_tool_api_spec,
    compare_tool_api_spec as compare_tool_api_spec,
)
from .top_down__pub import (
    compare_delegation as compare_delegation,
    compare_obligations as compare_obligations,
)
from .trace_spec__pub import (
    _binding_directions as _binding_directions,
    _manifest_binding as _manifest_binding,
    _manifest_contract as _manifest_contract,
    _solution_binding as _solution_binding,
    _uncovered_outcomes as _uncovered_outcomes,
    check_trace_spec as check_trace_spec,
    compare_trace_spec as compare_trace_spec,
    compare_trace_workflow as compare_trace_workflow,
)
from .trace_values__pub import compare_trace_values as compare_trace_values
from .cli_reachability import feasible_terminals as feasible_terminals


def _operation_claims(claim):
    from ._direct_comparison import _operation_claims as implementation

    return implementation(claim)


def report_comparison(model, report, *, action=None):
    from ._direct_comparison import report_comparison as implementation

    return implementation(model, report, action=action)
