from importlib import import_module

_BASE = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94."
)
_c85 = import_module(
    _BASE + "LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared"
)
_c87 = import_module(_BASE + "LAYER_3_MERMAID_RENDERER_C87._package__shared")
_c88 = import_module(_BASE + "LAYER_4_SPEC_COMPARISON_C88._package__shared")

parse_cli_contract = _c85.parse_cli_contract
parse_workflow = _c85.parse_workflow
normalize_claim = _c85.normalize_claim
render_solution = _c87.render_solution
_outcome_stdout = _c88._outcome_stdout
_workflow_facts = _c88._workflow_facts
check_cli_spec = _c88.check_cli_spec
compare_obligations = _c88.compare_obligations
feasible_terminals = _c88.feasible_terminals
