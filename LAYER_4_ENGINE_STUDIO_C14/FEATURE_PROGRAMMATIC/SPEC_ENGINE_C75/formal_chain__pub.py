"""Coordinate pinned trace, HTTP, shape and framing checks."""

import json
from copy import deepcopy
from hashlib import sha256

from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_1_DIAGNOSTICS_C90._package__shared import (
    finding,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import (
    SourceError,
    load_boundary_model,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    select_formal_claims,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    capture_lean_json,
    compile_lean,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_MERMAID_RENDERER_C87._package__shared import (
    render_solution,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_TEST_GENERATION_C92._package__shared import (
    build_python_framing_cases,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    _operation_claims,
    compare_cli_spec,
    compare_shape_spec,
    compare_tool_api_spec,
    compare_trace_spec,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_TRANSLATION_VALIDATOR_C86._package__shared import (
    validate_translation,
)


def _supports_trace(model, contract):
    trace = False
    for language, _ in model['contract']['claims']:
        if language not in ('python trace', 'python contract', 'python cli'):
            return False
        if language == 'python trace':
            trace = True
    if trace:
        return True
    if 'operations' not in contract:
        return contract.get('profile') == 'http'
    for profile in contract['operations'].values():
        if profile.get('profile') == 'http':
            return True
    return False


def _comparison_gap(contract, action):
    profiles = _operation_claims(contract)
    if action is not None and action not in profiles:
        return f'Unknown Contract Action {action!r}'
    selected = [profiles[action]] if action is not None else profiles.values()
    if any(profile.get('transport') == 'cli' for profile in selected):
        return 'Use check_cli_spec for CLI Actions or select an Action with a trace or HTTP Contract'
    if any(_tool_api(profile) for profile in selected):
        return 'Use check_tool_api_spec for Tool API Actions or select an Action with a trace or HTTP Contract'
    return None


def _tool_api(profile):
    return 'facts' in profile and profile.get('profile') != 'http'


def _selected_profile(contract, solution, action):
    if action is None:
        return contract
    profiles = _operation_claims(contract)
    if action in profiles:
        return profiles[action]
    if action in _operation_claims(solution):
        return next((profile for profile in profiles.values() if _tool_api(profile)), {})
    return {}


def _require_diagram(model, claim, *, action=None):
    diagram = render_solution(model, claim, action=action)
    if not isinstance(diagram, str) or not diagram.strip():
        raise SourceError('solution', model['solution']['source'], 'mermaid',
                          'The selected Solution has no Mermaid diagram')
    return diagram


def _compare_validated(model, canonical, action, lean):
    claims = canonical['claims']
    contract = claims.get('contract', {})
    solution = claims.get('solution')
    languages = [model[role]['claims'][0][0] for role in ('contract', 'solution')]
    if model.get('embedded_contract') and languages[1] == 'python':
        profile = _selected_profile(contract, solution, action)
        if profile.get('transport') == 'cli':
            mermaid = _require_diagram(model, solution, action=action)
            return compare_cli_spec(model, canonical, interface=profile['interface'],
                                    action=action, lean=lean, mermaid=mermaid), None
        if _tool_api(profile or contract):
            mermaid = _require_diagram(model, solution, action=action)
            return compare_tool_api_spec(model, canonical, action=action, lean=lean, mermaid=mermaid), None
    if languages[1] == 'python' and _supports_trace(model, contract):
        message = _comparison_gap(contract, action)
        if message is not None:
            return None, finding(model['contract']['source'], 'action', message)
        mermaid = _require_diagram(model, solution, action=action)
        return compare_trace_spec(model, canonical, action=action, lean=lean, mermaid=mermaid), None
    if languages == ['python shape', 'python shape'] and action is None:
        mermaid = _require_diagram(model, solution)
        return compare_shape_spec(model, canonical, lean=lean, mermaid=mermaid), None
    return None, finding(model['contract']['source'], 'contract', 'Unsupported formal chain comparison')


def _compare_framing(model, canonical, action):
    if action not in (None, 'framing'):
        return None, finding(model['manifest']['source'], 'action', f'Unknown Contract Action {action!r}')
    sources = {role: model[role]['source'] for role in ('manifest', 'solution')}
    mermaid = _require_diagram(model, canonical['claims']['solution'])
    return {**canonical['framing_comparison'], 'sources': sources, 'mermaid': mermaid}, None


def _coverage(comparison, action):
    selection = {'action': action} if action is not None else {}
    return [{'direction': direction, **selection, **fact}
            for direction, report in comparison.get('directions', {}).items()
            for fact in report.get('facts', [])]


def generate_framing_cases(root, component_id, manifest, solution):
    """Generate Python test inputs and expectations from two pinned framing Specs."""
    model = load_boundary_model(root, component_id, manifest, solution=solution)
    return build_python_framing_cases(select_formal_claims(model, 'framing'))


def verify_formal_chain(root, component_id, manifest, contract=None, solution=None, *, action=None, lean='lean'):
    """Check emitted declarations before comparing a pinned chain."""
    source, stage = manifest, 'specification'
    try:
        model = select_formal_claims(load_boundary_model(root, component_id, manifest, contract, solution), action)
        source = model.get('manifest', {}).get('source', manifest)
        stage = 'translation'
        compiled = compile_lean(deepcopy(model))
        direct_framing = model.get('embedded_contract') and all(
            [language for language, _ in model[role]['claims']] == ['python framing']
            for role in ('contract', 'solution'))
        options = {'bounded_framing': True} if direct_framing else {}
        with capture_lean_json() as validation_programs:
            translation = validate_translation(model, compiled['lean'], lean=lean, **options)
        claims = translation.pop('claims')
        expected = 'bounded_match' if direct_framing else 'matched'
        if translation['status'] != expected:
            return {'outcome': 'incomplete', 'translation': translation,
                    'diagnostics': [*translation['issues'], *translation['unresolved']]}
        canonical = {**compiled, 'claims': claims}
        stage = 'comparison'
        with capture_lean_json() as comparison_programs:
            if direct_framing:
                canonical['framing_comparison'] = translation.pop('framing_comparison')
                comparison, gap = _compare_framing(model, canonical, action)
            else:
                comparison, gap = _compare_validated(model, canonical, action, lean)
        if gap is not None:
            return {'outcome': 'incomplete', 'translation': translation, 'unresolved': [gap], 'diagnostics': [gap]}
        coverage = _coverage(comparison, action)
        actions = {fact['action'] for fact in coverage if fact.get('action')}
        model_pin = sha256(json.dumps(claims, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()).hexdigest()
        evidence = {'sources': comparison.get('sources', {}), 'model_pin': model_pin,
                    'action': next(iter(actions)) if action is None and len(actions) == 1 else action,
                    'coverage': coverage, 'uncovered_outcomes': comparison.get('uncovered_outcomes', []),
                    'validation_programs': validation_programs, 'comparison_programs': comparison_programs}
        return {'outcome': 'compared', 'translation': translation, 'lean': compiled['lean'],
                **comparison, 'evidence': evidence}
    except SourceError as error:
        failed_source = error.source if isinstance(error.source, dict) else source
        return {'outcome': 'incomplete', 'diagnostics': [
            {**finding(failed_source, error.field, str(error)), 'role': error.role}]}
    except (OSError, ValueError) as error:
        return {'outcome': 'incomplete', 'diagnostics': [finding(source, stage, str(error))]}
