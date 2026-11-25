"""Compare a bounded HTTP Contract with observations from backend source."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .backend_http_checks import extract_backend_checks
from .backend_http_contract import _lean_string, contract_to_lean
from .backend_http_source import extract_http_observations

_CONTRACT = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/AN-S-3185-DES-COMPONENT_CONTRACT--run-one-read-only-workbench-query.md'
_SOURCE = 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/backend_tool_api.py'


def _actual(rows, checks):
    values = ', '.join(f'({json.dumps(row["outcome"])}, {row["status_code"]}, '
                       f'{json.dumps(row["envelope"])})' for row in rows)
    facts = ', '.join(f'({_lean_string(key)}, [{", ".join(_lean_string(v) for v in sorted(value))}])'
                      for key, value in sorted(checks.items()))
    return (f'namespace BackendHttpSource\ndef actual : List (String × Nat × String) := [{values}]\n'
            f'def actualChecks : List (String × List String) := [{facts}]\nend BackendHttpSource\n')


def _check():
    return '''def conformance : List Bool := BackendHttpSource.actual.map fun actual =>
  BackendHttpContract.expected.any fun expected => expected == actual
def checkConformance : List (Bool × Bool) := BackendHttpContract.expectedChecks.map fun expected =>
  (BackendHttpSource.actualChecks.any fun actual => actual.1 == expected.1,
   BackendHttpSource.actualChecks.any fun actual => actual == expected)
#eval IO.println (Lean.Json.mkObj [
  ("expected", Lean.toJson BackendHttpContract.expected),
  ("matches", Lean.toJson conformance),
  ("expectedChecks", Lean.toJson BackendHttpContract.expectedChecks),
  ("actualChecks", Lean.toJson BackendHttpSource.actualChecks),
  ("checkConformance", Lean.toJson checkConformance)]).compress
'''


def _run_lean(lean, expected, actual, emit):
    combined = 'import Lean\n' + expected + '\n' + actual + '\n' + _check()
    if emit is not None:
        output = Path(emit)
        output.mkdir(parents=True, exist_ok=True)
        (output / 'Expected.lean').write_text(expected)
        (output / 'Actual.lean').write_text(actual)
        (output / 'Comparison.lean').write_text(combined)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'Comparison.lean'
        path.write_text(combined)
        result = subprocess.run([lean, str(path)], capture_output=True, text=True,
                                timeout=120, check=False)
    if result.returncode:
        raise ValueError('Lean comparison failed: ' + (result.stderr + result.stdout)[:2000])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError('invalid Lean output: ' + result.stdout[:2000]) from exc


def _checks_report(output):
    expected, actual, verdicts = (output.get(key) for key in
                                  ('expectedChecks', 'actualChecks', 'checkConformance'))
    def valid(rows):
        return isinstance(rows, list) and all(
            isinstance(row, list) and len(row) == 2 and isinstance(row[0], str)
            and isinstance(row[1], list) and all(isinstance(v, str) for v in row[1])
            for row in rows)
    if (not valid(expected) or not valid(actual) or not isinstance(verdicts, list)
            or len(verdicts) != len(expected) or any(
                not isinstance(v, list) or len(v) != 2 or any(type(b) is not bool for b in v)
                or (v[1] and not v[0]) for v in verdicts)):
        raise ValueError('unexpected Lean check output')
    observed = dict(actual)
    return [{'check': key, 'expected': value, 'observed': observed.get(key),
             'status': 'match' if match else 'mismatch' if covered else 'unresolved'}
            for (key, value), (covered, match) in zip(expected, verdicts)]


def compare(root, lean='lean', emit=None):
    """Return Lean-computed per-observation conformance and source locations."""
    root = Path(root)
    expected = contract_to_lean(root / _CONTRACT)
    rows = extract_http_observations((root / _SOURCE).read_text())
    checks = extract_backend_checks(root)
    executable = shutil.which(str(lean))
    if executable is None:
        raise ValueError('Lean executable unavailable: ' + str(lean))
    output = _run_lean(executable, expected, _actual(rows, checks), emit)
    if not isinstance(output, dict):
        raise TypeError('unexpected Lean comparison output')
    expected_rows, matches = output.get('expected'), output.get('matches')
    if (not isinstance(expected_rows, list) or not isinstance(matches, list)
            or len(matches) != len(rows) or any(type(v) is not bool for v in matches)):
        raise ValueError('unexpected Lean comparison output')
    if any(not isinstance(row, list) or len(row) != 2
           or not isinstance(row[0], str) or not isinstance(row[1], list)
           or len(row[1]) != 2 or type(row[1][0]) is not int
           or not isinstance(row[1][1], str) for row in expected_rows):
        raise ValueError('unexpected Lean expected outcomes')
    expected_by_outcome = {row[0]: {'status_code': row[1][0], 'envelope': row[1][1]}
                           for row in expected_rows}
    for row, match in zip(rows, matches):
        row['matches'] = match
        row['expected'] = expected_by_outcome.get(row['outcome'])
    check_results = _checks_report(output)
    statuses = {row['status'] for row in check_results}
    status = ('mismatch' if not all(matches) or 'mismatch' in statuses else
              'unresolved' if 'unresolved' in statuses else 'no_mismatch_in_cases')
    return {'status': status, 'contract': _CONTRACT, 'source': _SOURCE,
            'cases': rows, 'checks': check_results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--lean', default='lean')
    parser.add_argument('--emit')
    args = parser.parse_args()
    try:
        report = compare(args.root, args.lean, args.emit)
    except (OSError, ValueError, TypeError, SyntaxError, subprocess.TimeoutExpired) as exc:
        report = {'status': 'unresolved', 'reason': str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'no_mismatch_in_cases' else 1


if __name__ == '__main__':
    raise SystemExit(main())
