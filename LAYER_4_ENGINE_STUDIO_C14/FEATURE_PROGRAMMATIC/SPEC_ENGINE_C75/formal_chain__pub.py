"""Coordinate pinned trace, HTTP, shape and framing checks."""

import json
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256

from .LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SourceError
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_1_DIAGNOSTICS_C90._package__shared import (
    finding,
)
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import (
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
        return next(
            (profile for profile in profiles.values() if _tool_api(profile)),
            {},
        )
    return {}


def _model_pin(value):
    encoded = json.dumps(value, sort_keys=True, allow_nan=False,
                         separators=(',', ':')).encode('utf-8')
    return sha256(encoded).hexdigest()


def _require_diagram(model, claim, observations, *, action=None):
    observations['rendering'] = {
        'solution_pin': _model_pin(claim), 'action': action}
    diagram = render_solution(model, claim, action=action)
    if not isinstance(diagram, str) or not diagram.strip():
        raise SourceError('solution', model['solution']['source'], 'mermaid',
                          'The selected Solution has no Mermaid diagram')
    observations['rendering']['diagram_pin'] = _model_pin(diagram)
    return diagram


def _compare_validated(model, canonical, action, lean, observations):
    claims = canonical['claims']
    contract = claims.get('contract', {})
    solution = claims.get('solution')
    languages = [model[role]['claims'][0][0] for role in ('contract', 'solution')]
    if model.get('embedded_contract') and languages[1] == 'python':
        profile = _selected_profile(contract, solution, action)
        if profile.get('transport') == 'cli':
            mermaid = _require_diagram(model, solution, observations,
                                       action=action)
            observations['comparison'] = {
                'claims_pin': _model_pin(canonical['claims']),
                'action': action, 'kind': 'cli'}
            return compare_cli_spec(model, canonical, interface=profile['interface'],
                                    action=action, lean=lean, mermaid=mermaid), None
        if _tool_api(profile or contract):
            mermaid = _require_diagram(
                model, solution, observations, action=action
            )
            observations["comparison"] = {
                "claims_pin": _model_pin(canonical["claims"]),
                "action": action,
                "kind": "tool_api",
            }
            return compare_tool_api_spec(
                model, canonical, action=action, lean=lean, mermaid=mermaid
            ), None
    if languages[1] == "python" and _supports_trace(model, contract):
        message = _comparison_gap(contract, action)
        if message is not None:
            return None, finding(model['contract']['source'], 'action', message)
        mermaid = _require_diagram(model, solution, observations,
                                   action=action)
        observations['comparison'] = {
            'claims_pin': _model_pin(canonical['claims']),
            'action': action, 'kind': 'trace'}
        return compare_trace_spec(model, canonical, action=action, lean=lean, mermaid=mermaid), None
    if languages == ['python shape', 'python shape'] and action is None:
        mermaid = _require_diagram(model, solution, observations)
        observations['comparison'] = {
            'claims_pin': _model_pin(canonical['claims']),
            'action': action, 'kind': 'shape'}
        return compare_shape_spec(model, canonical, lean=lean, mermaid=mermaid), None
    return None, finding(model['contract']['source'], 'contract', 'Unsupported formal chain comparison')


def _compare_framing(model, canonical, action, observations):
    if action not in (None, 'framing'):
        return None, finding(model['manifest']['source'], 'action', f'Unknown Contract Action {action!r}')
    sources = {role: model[role]['source'] for role in ('manifest', 'solution')}
    mermaid = _require_diagram(model, canonical['claims']['solution'],
                               observations)
    observations['framing_result'] = {
        'result_pin': _model_pin([canonical['claims'],
                                  canonical['framing_comparison']]),
        'action': action}
    return {**canonical['framing_comparison'], 'sources': sources, 'mermaid': mermaid}, None


def _coverage(comparison, action):
    selection = {'action': action} if action is not None else {}
    return [{'direction': direction, **selection, **fact}
            for direction, report in comparison.get('directions', {}).items()
            for fact in report.get('facts', [])]


def _observed_numbers(value, template):
    if isinstance(value, dict) and isinstance(template, dict):
        return {key: _observed_numbers(item, template.get(key))
                for key, item in value.items()}
    if isinstance(value, list) and isinstance(template, (list, tuple)):
        return [_observed_numbers(item, template[index]
                                  if index < len(template) else None)
                for index, item in enumerate(value)]
    if type(value) in (int, Decimal) and type(template) in (int, float):
        if value != Decimal(str(template)):
            raise ValueError('Generated and validated Model identities differ')
        return template
    if isinstance(value, Decimal):
        raise ValueError('Generated and validated Model identities differ')
    return value


def _validated_claims(programs, claims, model, lean_source):
    if len(programs) != 1:
        raise ValueError('Missing Lean validation observation')
    if not programs[0].get('program', '').startswith(lean_source + '\n'):
        raise ValueError('Lean validation used a different generated program')
    try:
        declarations, _, _ = json.loads(
            programs[0]['stdout'], parse_float=Decimal)[-1]
        if len(declarations) != len(claims):
            raise ValueError('Missing Lean declaration observation')
        actual = {}
        for role, row in zip(claims, declarations, strict=True):
            if len(row) != 1 or row[0]['source'] != model[role]['source']:
                raise ValueError('Validated declaration source differs')
            actual[role] = _observed_numbers(row[0]['claim'], claims[role])
        return actual
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError('Missing Lean declaration observation') from error


def _validated_pin(programs, claims, generated_pin, model, lean_source):
    if generated_pin is None:
        raise ValueError('Missing generated Model observation')
    pin = _model_pin(_validated_claims(programs, claims, model, lean_source))
    if generated_pin != pin or _model_pin(claims) != pin:
        raise ValueError('Generated and validated Model identities differ')
    return pin


def _check_observations(observations, solution_pin, model_pin, framing_pin,
                        action, claims):
    rendering = observations.get('rendering', {})
    if rendering.get('solution_pin') != solution_pin:
        raise ValueError('Rendering Solution identity is missing or differs')
    render_action = None if framing_pin is not None else action
    if rendering.get('action') != render_action:
        raise ValueError('Rendering Action differs from the selected Action')
    comparison = observations.get('comparison', {})
    if ((framing_pin is None and (comparison.get('claims_pin') != model_pin
                                 or comparison.get('action') != action))
            or _model_pin(claims) != model_pin):
        raise ValueError('Comparison Model identity is missing or differs')
    framing = observations.get('framing_result', {}).get('result_pin')
    if framing_pin is not None and framing != framing_pin:
        raise ValueError('Framing comparison identity is missing or differs')


def _evidence(comparison, action, programs, observations, model_pin,
              generated_pin):
    coverage = _coverage(comparison, action)
    actions = {fact['action'] for fact in coverage if fact.get('action')}
    selected = (next(iter(actions)) if action is None and len(actions) == 1
                else action)
    observations.update(generated_claims=generated_pin, lean_claims=model_pin)
    return {'sources': comparison['sources'], 'model_pin': model_pin,
            'action': selected,
            'coverage': coverage,
            'uncovered_outcomes': comparison.get('uncovered_outcomes', []),
            'validation_programs': programs[0],
            'comparison_programs': programs[1],
            'stages': observations}


def generate_framing_cases(root, component_id, manifest, solution):
    """Generate Python test inputs and expectations from two pinned framing Specs."""
    model = load_boundary_model(
        root, component_id, manifest, solution=solution
    )
    return build_python_framing_cases(select_formal_claims(model, "framing"))


def _translate(model, lean):
    compiled = compile_lean(deepcopy(model))
    generated_pin = (_model_pin(compiled['claims'])
                     if 'claims' in compiled else None)
    direct_framing = model.get('embedded_contract') and all(
        [language for language, _ in model[role]['claims']]
        == ['python framing']
        for role in ('contract', 'solution'))
    options = {'bounded_framing': True} if direct_framing else {}
    with capture_lean_json() as programs:
        translation = validate_translation(model, compiled['lean'], lean=lean,
                                           **options)
    return compiled, generated_pin, direct_framing, translation, programs


def _compare_selected(model, canonical, action, lean, direct_framing):
    roles = ('manifest', 'solution') if model.get('embedded_contract') else (
        'manifest', 'contract', 'solution')
    sources = deepcopy({role: model[role]['source'] for role in roles})
    observations = {}
    with capture_lean_json() as programs:
        if direct_framing:
            result, gap = _compare_framing(model, canonical, action,
                                            observations)
        else:
            result, gap = _compare_validated(model, canonical, action, lean,
                                              observations)
    if gap is None:
        if result.get('sources') != sources:
            raise ValueError('Comparison source identities differ')
        diagram_pin = observations.get('rendering', {}).get('diagram_pin')
        if _model_pin(result.get('mermaid')) != diagram_pin:
            raise ValueError('Comparison diagram differs from renderer output')
    return result, gap, programs, observations


def verify_formal_chain(root, component_id, manifest, contract=None, solution=None, *, action=None, lean='lean'):
    """Check emitted declarations before comparing a pinned chain."""
    source, stage = manifest, 'specification'
    try:
        model = select_formal_claims(load_boundary_model(root, component_id, manifest, contract, solution), action)
        source = model.get('manifest', {}).get('source', manifest)
        stage = 'translation'
        compiled, generated_pin, direct_framing, translation, programs = (
            _translate(model, lean))
        claims = translation.pop('claims', None)
        expected = 'bounded_match' if direct_framing else 'matched'
        if translation['status'] != expected:
            return {'outcome': 'incomplete', 'translation': translation,
                    'diagnostics': [*translation['issues'], *translation['unresolved']]}
        if claims is None:
            raise ValueError('Missing validated Model claims')
        validated_pin = _validated_pin(programs, claims, generated_pin,
                                       model, compiled['lean'])
        canonical = {**compiled, 'claims': claims}
        solution_pin = _model_pin(claims['solution'])
        framing_pin = translation.pop('framing_result_pin', None)
        if direct_framing and (not framing_pin
                               or 'framing_comparison' not in translation):
            raise ValueError('Missing validated framing comparison evidence')
        if direct_framing:
            canonical['framing_comparison'] = translation.pop(
                'framing_comparison')
        stage = 'comparison'
        comparison, gap, comparison_programs, observations = _compare_selected(
            model, canonical, action, lean, direct_framing)
        if gap is not None:
            return {'outcome': 'incomplete', 'translation': translation, 'unresolved': [gap], 'diagnostics': [gap]}
        _check_observations(observations, solution_pin, validated_pin,
                            framing_pin, action, canonical['claims'])
        evidence = _evidence(comparison, action,
                             (programs, comparison_programs),
                             observations, validated_pin, generated_pin)
        return {'outcome': 'compared', 'translation': translation, 'lean': compiled['lean'],
                **comparison, 'evidence': evidence}
    except SourceError as error:
        failed_source = error.source if isinstance(error.source, dict) else source
        return {'outcome': 'incomplete', 'diagnostics': [
            {**finding(failed_source, error.field, str(error)), 'role': error.role}]}
    except (OSError, ValueError) as error:
        return {'outcome': 'incomplete', 'diagnostics': [finding(source, stage, str(error))]}
