"""Check C30 framing against fresh witnesses from the two pinned claims."""

import json
import shutil
import subprocess
import tempfile
from hashlib import sha256
from pathlib import Path

from .carrier_formal import framing_exports
from .carrier_model import _SOURCE, generate
from .carrier_observations import lean_bytes, observe, python_checks
from .carrier_runtime_effects import analyze_carrier

_REQUIRED_PROOFS = ''.join(f'''
example (raw : List Nat) :
    frontmatterBounds raw = {namespace}.bounds raw :=
  C30ImplementationEquivalence.{role}_bounds raw

example (raw : List Nat) (path : String) :
    sourceBody raw path =
      (match {namespace}.body raw with
       | .missingDelimiter => .error (path ++ ": unsupported frontmatter delimiter")
       | .body bytes => .ok bytes) :=
  C30ImplementationEquivalence.{role}_body raw path
''' for role, namespace in (('manifest', 'CarrierBodyContract'), ('solution', 'CarrierBodySolution')))


def _linked_checks(row):
    raw = lean_bytes(row['raw'])
    path = json.dumps(row['path'])
    checks = python_checks(row)
    for namespace in ('CarrierBodyContract', 'CarrierBodySolution'):
        checks.append(f'({namespace}.bounds {raw} == frontmatterBounds {raw})')
        checks.append(
            f'(match {namespace}.body {raw}, sourceBody {raw} {path} with '
            '| .missingDelimiter, .error _ => true '
            '| .body expected, .ok actual => expected == actual '
            '| _, _ => false)'
        )
    return checks


def _compare_linked(program, lean, count):
    executable = shutil.which(lean)
    if executable is None:
        raise ValueError('Lean executable unavailable')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'CarrierImplementationComparison.lean'
        path.write_text(program, encoding='utf-8')
        result = subprocess.run([executable, str(path)], capture_output=True,
                                text=True, timeout=120, check=False)
    try:
        values = json.loads(result.stdout)
    except json.JSONDecodeError:
        values = None
    if (result.returncode or not isinstance(values, list) or len(values) != 6 * count
            or not all(type(value) is bool for value in values)):
        raise ValueError('Lean implementation comparison failed: ' + (result.stderr + result.stdout)[:2000])
    return values


def _prove_linked(program, lean):
    proof_file = Path(__file__).with_name('framing_equivalence_proof.lean')
    try:
        proof = proof_file.read_bytes()
        result = subprocess.run(
            [lean, '-DwarningAsError=true', '--stdin'],
            input=program + '\n' + proof.decode('utf-8') + _REQUIRED_PROOFS, capture_output=True,
            text=True, timeout=120, check=False,
        )
        if result.returncode:
            raise ValueError((result.stderr + result.stdout).strip()[-2000:])
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {'status': 'unresolved', 'reason': str(error)}
    return {'status': 'proved', 'quantified_over': ['input', 'path'],
            'sha256': sha256(proof).hexdigest()}


def _compare_cases(observations, comparisons, formal_cases, evidence):
    findings = []
    for index, (row, formal) in enumerate(zip(observations, formal_cases, strict=True)):
        matches = comparisons[6 * index:6 * index + 6]
        row['code_matches_python'] = all(matches[:2])
        if not row['code_matches_python']:
            evidence['unresolved'].append(f"Source model differs from Python in case {row['name']}")
        bounds = None if row['bounds'] is None else list(row['bounds'])
        for role, start in [('manifest', 2), ('solution', 4)]:
            expected = row[role] = formal[role]
            differences = [key for key, actual in [('bounds', bounds), ('body', row['body'])]
                           if expected[key] != actual]
            row[f'{role}_matches_python'] = not differences
            row[f'{role}_matches_code'] = all(matches[start:start + 2])
            if row['code_matches_python'] and matches[start:start + 2] != [
                key not in differences for key in ('bounds', 'body')
            ]:
                raise ValueError(f"Linked Lean results differ from validated {role} observations in case {row['name']}")
            if differences and row['code_matches_python']:
                findings.append({'model': role, 'case': row['name'],
                                 'raw': row['raw'], 'differences': differences})
    return findings


def compare_direct(root, manifest, solution, formal_verifier, lean, *, implementation_sha256=None):
    """Bind C75's fresh exact-pin result to the implementation and real Python results."""
    formal = formal_verifier(root, 'C30', manifest, solution=solution, lean=lean)
    evidence = {'unresolved': []}
    report = {'status': 'unresolved', 'evidence': evidence, 'cases': [], 'findings': [],
              'formal': {key: value for key, value in formal.items() if key != 'cases'}}
    if (formal.get('outcome') != 'compared' or formal.get('translation', {}).get('status') != 'bounded_match'
            or not formal.get('cases')):
        evidence['unresolved'].append('Formal verifier did not produce validated framing witnesses')
        return report
    try:
        exports = framing_exports(root, manifest, solution, formal.get('sources'))
        source = (Path(root) / _SOURCE).read_bytes()
        if implementation_sha256 is not None and sha256(source).hexdigest() != implementation_sha256:
            raise ValueError('Implementation source digest changed')
        model, binding = generate(root, source)
        evidence.update(binding)
        evidence['exports'] = {name: evidence['symbols'][name.split('.')[-1]][0] for name in exports}
        evidence['effects'] = analyze_carrier(source)
        cases = {i: bytes(row['input']) for i, row in enumerate(formal['cases'], 1)}
        paths = {name: f'case-{name}/carrier-{name}.md' for name in cases}
        rows = report['cases'] = observe(root, evidence, source, cases, paths=paths)
        checks = [check for row in rows for check in _linked_checks(row)]
        models = model + '\n' + formal['lean'].removeprefix('import Lean\n')
        program = models + '\n#eval IO.println (Lean.toJson [' + ',\n'.join(checks) + ']).compress\n'
        report.update(implementation_lean=model, comparison_lean=program)
        values = _compare_linked(program, lean, len(rows))
        findings = report['findings'] = _compare_cases(rows, values, formal['cases'], evidence)
    except (OSError, ValueError, SyntaxError, subprocess.TimeoutExpired) as error:
        evidence['unresolved'].append(str(error))
        return report
    if evidence['effects']['status'] != 'permitted':
        evidence['unresolved'].append('Scoped runtime effect review is not permitted')
    elif all(row['code_matches_python'] for row in rows):
        if findings:
            report['status'] = 'mismatch'
        else:
            report['proof'] = _prove_linked(models, lean)
            if report['proof']['status'] == 'proved':
                report['status'] = 'no_mismatch_in_cases'
            else:
                evidence['unresolved'].append('Universal equivalence of the generated framing models remains unproved.')
    return report
