"""Check emitted Lean declaration values against the admitted source model."""

import json
from decimal import Decimal

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import finding, verdict
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    json_equal,
    normalize_spec,
)
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import run_lean_json
from ..LAYER_3_TEST_GENERATION_C92._package__shared import framing_witnesses
from .framing_validation import (
    framing_checks,
    framing_comparison,
    framing_observations,
)
from .shape_validation import shape_checks


def _evaluation(roles, framing, framing_inputs):
    values = ', '.join(f'AnechoicSpec.{role}' for role in roles)
    witnesses = ', '.join('[' + ', '.join(checks) + ']' for checks in framing.values())
    observations = framing_observations(framing_inputs) if framing_inputs else ''
    return observations + f'''
def translationValue : Except String Lean.Json → Lean.Json
  | .ok value => Lean.Json.arr #[value]
  | .error _ => Lean.Json.arr #[]
#eval IO.println ((Lean.Json.arr #[
  Lean.Json.arr (#[{values}].map translationValue),
  Lean.toJson ([{witnesses}] : List (List Bool)),
  {'framingCases' if framing_inputs else 'Lean.Json.null'}
]).compress ++ "]")
'''


def _projection_checks(model, claims, unresolved, bounded_framing):
    shape, framing = {}, {}
    for role in ('contract', 'solution'):
        if role not in claims:
            continue
        declaration = model[role]
        languages = [language for language, _ in declaration['claims']]
        if languages == ['python shape']:
            shape[role] = shape_checks(claims[role], role)
        if 'python framing' in languages:
            claim = claims[role]['framing'] if len(languages) > 1 else claims[role]
            try:
                framing[role] = (claim, framing_witnesses(
                    claim, role, include_overlap_cases=bounded_framing))
            except ValueError as error:
                unresolved.append(finding(declaration['source'], role, str(error)))
    shared = sorted({raw for _, cases in framing.values() for raw in cases}) if bounded_framing else []
    checks = {role: framing_checks(claim, role, shared or cases)
              for role, (claim, cases) in framing.items()}
    return shape, checks, shared if len(framing) == 2 else []


def _check_shape(model, claims, checks, results, issues):
    if not isinstance(results, list) or len(results) != len(checks):
        raise ValueError('Unexpected Lean shape validation output')
    for role, values in zip(checks, results, strict=True):
        claim = claims[role]
        fields = ['shape'] + [f'fields.{name}' for name in claim['fields']]
        if claim['base'] == claim['record']:
            fields.append('base')
        if (not isinstance(values, list) or len(values) != len(fields)
                or any(type(value) is not bool for value in values)):
            raise ValueError('Unexpected Lean shape validation output')
        for field, matches in zip(fields, values, strict=True):
            if not matches:
                issues.append(finding(model[role]['source'], f'{role}.{field}',
                                      'Lean shape differs from the normalized source'))


def _check_framing(model, checks, actual, issues, unresolved):
    if not isinstance(actual, list) or len(actual) != len(checks):
        raise ValueError('Unexpected Lean framing validation output')
    for (role, witnesses), results in zip(checks.items(), actual, strict=True):
        if (not isinstance(results, list) or len(results) != len(witnesses)
                or any(type(result) is not bool for result in results)):
            raise ValueError('Unexpected Lean framing witness output')
        source = model[role]['source']
        if False in results:
            witness = witnesses[results.index(False)]
            issues.append(finding(source, role, f'Lean framing witness disagrees: {witness}'))
        else:
            unresolved.append(finding(source, role,
                f'Framing passed {len(witnesses) // 2} byte witnesses. Unbounded equivalence remains unverified.'))


def _check_declarations(model, claims, actual, issues):
    if not isinstance(actual, list) or len(actual) != len(claims):
        raise ValueError('Unexpected Lean translation validation output')
    for (role, claim), observed in zip(claims.items(), actual, strict=True):
        source = model[role]['source']
        value = json.dumps({'source': source, 'claim': claim}, allow_nan=False)
        expected = json.loads(value, parse_float=Decimal)
        if not json_equal([expected], observed):
            issues.append(finding(source, role, 'Lean declaration differs from the normalized source'))


def validate_translation(model, program, *, lean='lean', bounded_framing=False):
    """Check emitted declarations, shape metadata, and bounded framing witnesses."""
    normalized = normalize_spec(model)
    claims = normalized['claims']
    comparison_fields = {'boundaries.code.imports', 'boundaries.code.exports', 'boundaries.io'}
    if model.get('embedded_contract'):
        comparison_fields.update(('boundaries.process', 'boundaries.state'))
    unresolved, coverage_unresolved = [], []
    for issue in normalized['unresolved']:
        if issue['field'] not in comparison_fields:
            unresolved.append(issue)
        elif bounded_framing:
            coverage_unresolved.append(issue)
    boundaries = claims.get('manifest', {}).get('boundaries') or {}
    if (bounded_framing and 'io' in boundaries
            and not any(issue['field'] == 'boundaries.io' for issue in coverage_unresolved)):
        coverage_unresolved.append(finding(model['manifest']['source'], 'boundaries.io',
                                           'Framing does not compare Manifest I/O obligations'))
    issues = list(normalized['issues'])
    witnesses = []
    pair_results = None
    if claims:
        shape, framing, witnesses = _projection_checks(model, claims, unresolved, bounded_framing)
        evaluation = run_lean_json(program + '\nrun_cmd liftM <| IO.print "["\n'
                                   + ''.join(shape.values()) + _evaluation(claims, framing, witnesses),
                                   lean, parse_float=Decimal)
        if not isinstance(evaluation, list) or len(evaluation) != len(shape) + 1:
            raise ValueError('Unexpected Lean translation validation output')
        _check_shape(model, claims, shape, evaluation[:-1], issues)
        evaluation = evaluation[-1]
        if not isinstance(evaluation, list) or len(evaluation) != 3:
            raise ValueError('Unexpected Lean translation validation output')
        actual, witness_results, pair_results = evaluation
        _check_declarations(model, claims, actual, issues)
        _check_framing(model, framing, witness_results, issues,
                       coverage_unresolved if witnesses else unresolved)
    statuses = ['conflicting'] if issues else ['unresolved'] if unresolved else ['matched']
    status = verdict(statuses)
    report = {'status': status, 'issues': issues, 'unresolved': unresolved,
              'claims': claims if status == 'matched' else {}}
    if bounded_framing:
        report['coverage_unresolved'] = coverage_unresolved
        if witnesses and status == 'matched':
            report.update(status='bounded_match', framing_comparison=framing_comparison(witnesses, pair_results, claims))
    return report
