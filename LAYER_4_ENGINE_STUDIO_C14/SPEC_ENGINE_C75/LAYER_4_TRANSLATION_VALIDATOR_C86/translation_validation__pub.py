"""Check emitted Lean declaration values against the admitted source model."""

from decimal import Decimal
import json

from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import finding, verdict
from ..LAYER_2_FORMAL_MODEL_C85.claim_model__pub import normalize_spec
from ..LAYER_2_FORMAL_MODEL_C85.workflow_model__pub import json_equal
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_check__pub import run_lean_json
from .framing_validation import framing_checks
from .shape_validation import shape_checks


def _evaluation(roles, framing):
    values = ', '.join(f'AnechoicSpec.{role}' for role in roles)
    witnesses = ', '.join('[' + ', '.join(checks) + ']' for checks in framing.values())
    return f'''
def translationValue : Except String Lean.Json → Lean.Json
  | .ok value => Lean.Json.arr #[value]
  | .error _ => Lean.Json.arr #[]
#eval IO.println ((Lean.Json.arr #[
  Lean.Json.arr (#[{values}].map translationValue),
  Lean.toJson ([{witnesses}] : List (List Bool))
]).compress ++ "]")
'''


def _projection_checks(model, claims, unresolved):
    shape, framing = {}, {}
    for role in ('contract', 'solution'):
        if role not in claims:
            continue
        declaration = model[role]
        language = declaration['claims'][0][0]
        if language == 'python shape':
            shape[role] = shape_checks(claims[role], role)
        if language == 'python framing':
            try:
                framing[role] = framing_checks(claims[role], role)
            except ValueError as error:
                unresolved.append(finding(declaration['source'], role, str(error)))
    return shape, framing


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


def validate_translation(model, program, *, lean='lean'):
    """Check emitted declarations, shape metadata, and bounded framing witnesses."""
    normalized = normalize_spec(model)
    claims = normalized['claims']
    unresolved = list(normalized['unresolved'])
    issues = list(normalized['issues'])
    if claims:
        shape, framing = _projection_checks(model, claims, unresolved)
        evaluation = run_lean_json(program + '\nrun_cmd liftM <| IO.print "["\n'
                                   + ''.join(shape.values()) + _evaluation(claims, framing),
                                   lean, parse_float=Decimal)
        if not isinstance(evaluation, list) or len(evaluation) != len(shape) + 1:
            raise ValueError('Unexpected Lean translation validation output')
        _check_shape(model, claims, shape, evaluation[:-1], issues)
        evaluation = evaluation[-1]
        if not isinstance(evaluation, list) or len(evaluation) != 2:
            raise ValueError('Unexpected Lean translation validation output')
        actual, witness_results = evaluation
        if not isinstance(actual, list) or len(actual) != len(claims):
            raise ValueError('Unexpected Lean translation validation output')
        for (role, claim), observed in zip(claims.items(), actual, strict=True):
            source = model[role]['source']
            value = json.dumps({'source': source, 'claim': claim}, allow_nan=False)
            expected = json.loads(value, parse_float=Decimal)
            if not json_equal([expected], observed):
                issues.append(finding(source, role, 'Lean declaration differs from the normalized source'))
        _check_framing(model, framing, witness_results, issues, unresolved)
    statuses = ['conflicting'] if issues else ['unresolved'] if unresolved else ['matched']
    status = verdict(statuses)
    return {'status': status, 'issues': issues, 'unresolved': unresolved,
            'claims': claims if status == 'matched' else {}}
