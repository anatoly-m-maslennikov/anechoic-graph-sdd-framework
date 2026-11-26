"""Check the formal Manifest, Contract and Solution for a Tool API invocation."""

from ..LAYER_3_MERMAID_RENDERER_C87.solution_diagram__pub import render_solution
from ..LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import finding
from .tool_api_obligations__pub import contract_tool_api, manifest_tool_api, solution_tool_api
from .top_down__pub import compare_obligations


def _tool_contract(claim):
    profiles = claim.get('operations', {'': claim})
    contracts = [profile for profile in profiles.values() if 'facts' in profile]
    return contracts[0] if len(contracts) == 1 else {}


def _tool_solution(workflow, operation, action):
    if 'operations' in workflow:
        profiles = workflow['operations']
        if action is None:
            candidates = [facts for profile in profiles.values()
                          if (observed := (facts := solution_tool_api(profile)).get('operation')) == [operation]
                          or (isinstance(observed, dict) and [operation] in observed['conflicting_values'])]
            return candidates[0] if len(candidates) == 1 else {}
        workflow = profiles.get(action, {})
    if not workflow or (action is not None and workflow.get('action') != action):
        return {}
    return solution_tool_api(workflow)


def check_tool_api_spec(root, component_id, manifest, contract, solution, *, action=None, lean='lean'):
    """Compare an exact specification chain and keep unmodeled obligations visible."""
    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    claims = compiled['claims']
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    manifest_fields = claims.get('manifest', {}).get('boundaries') or {}
    io = manifest_fields.get('io')
    server = io.get('server') if isinstance(io, dict) else None
    api = server.get('tool_api') if isinstance(server, dict) else None
    declared, extra = manifest_tool_api(api) if isinstance(api, dict) else ({}, {})
    tool_contract = _tool_contract(claims.get('contract', {}))
    obligations = {'manifest': declared,
                   'contract': contract_tool_api(tool_contract) if tool_contract else {},
                   'solution': _tool_solution(claims.get('solution', {}), tool_contract.get('operation'), action)}
    report = compare_obligations(sources, obligations, lean=lean)
    conflicts = [finding(sources['solution'], key, f'Solution declares inconsistent {key}: {value["conflicting_values"]}')
                 for key, value in obligations['solution'].items()
                 if isinstance(value, dict) and 'conflicting_values' in value]
    report.update(issues=[*compiled['issues'], *conflicts], unresolved=compiled['unresolved'],
                  unmodeled_tool_api=extra, mermaid=render_solution(model, claims.get('solution')))
    if conflicts:
        report['status'] = 'conflicting'
    if report['status'] == 'matched' and (report['issues'] or report['unresolved'] or extra):
        report['status'] = 'unresolved'
    return report
