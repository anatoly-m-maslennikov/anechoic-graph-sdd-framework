"""Validate framing projections in Lean."""

from ..LAYER_3_TEST_GENERATION_C92._package__shared import framing_expectation


def framing_checks(claim, role, witnesses):
    """Return finite Lean Boolean checks for the role's bounds and body projections."""
    namespace = {'contract': 'CarrierBodyContract', 'solution': 'CarrierBodySolution'}[role]
    checks = []
    for raw in witnesses:
        bounds, body = framing_expectation(raw, claim, role)
        bound_form = 'none' if bounds is None else f'some {bounds}'
        outcome = 'missingDelimiter' if body is None else f'body {list(body)}'
        checks.append(f'({namespace}.bounds {list(raw)} == {bound_form})')
        checks.append(f'({namespace}.body {list(raw)} == {namespace}.Outcome.{outcome})')
    return checks


def framing_observations(witnesses):
    """Project the two Lean framing models onto the same bounds and byte outputs."""
    inputs = [list(raw) for raw in witnesses]
    return f'''
def framingResult (bounds : Option (Nat × Nat × Nat)) (body : Option (List Nat)) : Lean.Json :=
  Lean.Json.mkObj [
    ("bounds", Lean.toJson (bounds.map fun (opening, start, stop) => [opening, start, stop])),
    ("body", Lean.toJson body)]

def framingCases : Lean.Json :=
  let inputs : List (List Nat) := {inputs}
  Lean.Json.arr <| inputs.toArray.map fun raw =>
    let manifestBody := match CarrierBodyContract.body raw with
      | .missingDelimiter => none
      | .body bytes => some bytes
    let solutionBody := match CarrierBodySolution.body raw with
      | .missingDelimiter => none
      | .body bytes => some bytes
    let manifestBounds := CarrierBodyContract.bounds raw
    let solutionBounds := CarrierBodySolution.bounds raw
    Lean.Json.arr #[
      Lean.toJson (manifestBounds == solutionBounds && manifestBody == solutionBody),
      framingResult manifestBounds manifestBody, framingResult solutionBounds solutionBody]
'''


def _valid_projection(row):
    if (not isinstance(row, dict) or len(row) != 2
            or 'bounds' not in row or 'body' not in row):
        return False
    bounds, body = row['bounds'], row['body']
    if bounds is None:
        return body is None
    if not isinstance(bounds, list) or len(bounds) != 3:
        return False
    for part in bounds:
        if (not isinstance(part, int) or isinstance(part, bool)
                or part < 0):
            return False
    if not isinstance(body, list):
        return False
    for byte in body:
        if (not isinstance(byte, int) or isinstance(byte, bool)
                or byte < 0 or byte > 255):
            return False
    return True


def _expected_projection(raw, claim, role):
    bounds, body = framing_expectation(raw, claim.get('framing', claim), role)
    return {'bounds': list(bounds) if bounds is not None else None,
            'body': list(body) if body is not None else None}


def _valid_comparison(values, expected_manifest, expected_solution):
    if not isinstance(values, list) or len(values) != 3 or not isinstance(values[0], bool):
        return False
    matched, manifest, solution = values
    return (_valid_projection(manifest) and _valid_projection(solution)
            and manifest == expected_manifest and solution == expected_solution
            and matched == (manifest == solution))


def framing_comparison(witnesses, observed, claims):
    if not isinstance(observed, list) or len(observed) != len(witnesses):
        raise ValueError('Unexpected Lean framing comparison output')
    cases, mismatches = [], []
    for raw, values in zip(witnesses, observed, strict=True):
        expected_manifest = _expected_projection(raw, claims['contract'], 'contract')
        expected_solution = _expected_projection(raw, claims['solution'], 'solution')
        if not _valid_comparison(values, expected_manifest, expected_solution):
            raise ValueError('Unexpected Lean framing comparison output')
        matched, manifest, solution = values
        case = {'input': list(raw), 'manifest': manifest, 'solution': solution}
        cases.append(case)
        if not matched:
            mismatches.append(case)
    status = 'conflicting' if mismatches else 'bounded_match'
    return {'status': status, 'cases': cases,
            'directions': {'manifest_solution': {'status': status, 'facts': mismatches}}}
