"""Compare the admitted Python carrier, its Lean model, and a Spec model."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import types
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    frontmatter_bounds,
    source_body,
)

from .carrier_formal import formal_inputs
from .carrier_model import _SOURCE, generate
from .carrier_runtime_effects import analyze_carrier

_CASES = {
    'lf': b'---\na: b\n---\nbody\x00\xff',
    'crlf': b'---\r\na: b\r\n---\r\nbody',
    'empty_lf': b'---\n---\nbody',
    'empty_crlf': b'---\r\n---\r\nbody',
    'missing_open': b'body',
    'missing_close': b'---\na: b\nbody',
    'mixed_lines': b'---\r\na\n---\r\nbody',
    'first_close': b'---\na\n---\nbody\n---\nlast',
}


def _lean_bytes(value):
    return '[' + ', '.join(map(str, value)) + ']'


def _loaded_matches(source, path):
    compiled = compile(source, str(path), 'exec')
    expected = {c.co_name: c for c in compiled.co_consts if isinstance(c, types.CodeType)}
    fields = ('co_code', 'co_consts', 'co_names', 'co_varnames',
              'co_argcount', 'co_kwonlyargcount')
    return all(fn.__name__ in expected and all(
        getattr(fn.__code__, field) == getattr(expected[fn.__name__], field)
        for field in fields) for fn in (frontmatter_bounds, source_body))


def _observations(root, evidence, source):
    path = Path(root) / evidence['source']
    if hashlib.sha256(source).hexdigest() != evidence['source_sha256']:
        raise ValueError('carrier source changed during analysis')
    if (not _loaded_matches(source, path) or any(
        Path(fn.__code__.co_filename).resolve() != path.resolve()
        for fn in (frontmatter_bounds, source_body)
    )):
        raise ValueError('loaded carrier functions do not match the analyzed path')
    rows = []
    for name, raw in _CASES.items():
        bounds = frontmatter_bounds(raw)
        try:
            body = list(source_body(raw, Path('carrier.md')))
            error = None
        except ValueError as exc:
            body, error = None, str(exc)
        rows.append({'name': name, 'raw': list(raw), 'bounds': bounds,
                     'body': body, 'error': error})
    return rows


def _checks(rows):
    checks = []
    for row in rows:
        raw = _lean_bytes(row['raw'])
        b = row['bounds']
        expected = 'none' if b is None else f'some ({b[0]}, {b[1]}, {b[2]})'
        if row['body'] is None:
            body = ('match sourceBody ' + raw + ' "carrier.md" with | .error e => e == '
                    + json.dumps(row['error']) + ' | .ok _ => false')
            suffix = 'missingDelimiter'
        else:
            value = _lean_bytes(row['body'])
            body = (f'match sourceBody {raw} "carrier.md" with '
                    f'| .ok b => b == {value} | .error _ => false')
            suffix = f'body {value}'
        checks.extend([f'frontmatterBounds {raw} == {expected}', f'({body})'])
        for namespace in ('CarrierBodyContract', 'CarrierBodySolution'):
            checks.extend([f'{namespace}.bounds {raw} == {expected}',
                           f'{namespace}.body {raw} == ({namespace}.Outcome.{suffix})'])
    return '#eval IO.println (Lean.toJson [' + ',\n'.join(checks) + ']).compress\n'


def compare(root, lean='lean', formal_only=False):
    """Return binding evidence, per-case findings, and explicit unresolved gaps."""
    if formal_only:
        return _formal_compare(root, lean)
    source = (Path(root) / _SOURCE).read_bytes()
    model, evidence = generate(root, source)
    evidence['effects'] = analyze_carrier(source)
    blocks, evidence['formal'] = formal_inputs(root)
    evidence['unresolved'].append('Spec Engine Python-to-Lean compilation is unsupported')
    rows = _observations(root, evidence, source)
    executable = shutil.which(lean)
    if executable is None:
        evidence['unresolved'].append('Lean executable unavailable')
        return {'status': 'unresolved', 'evidence': evidence, 'cases': rows}
    text = '\n'.join(re.sub(r'^\s*import Lean\s*\n', '', block, count=1)
                     for block in blocks)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'CarrierComparison.lean'
        path.write_text(model + '\n' + text + '\n' + _checks(rows))
        try:
            result = subprocess.run([executable, str(path)], capture_output=True,
                                    text=True, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            evidence['unresolved'].append('Lean comparison timed out')
            return {'status': 'unresolved', 'evidence': evidence, 'cases': rows}
    try:
        values = json.loads(result.stdout)
    except json.JSONDecodeError:
        values = None
    if (result.returncode or not isinstance(values, list)
            or len(values) != len(rows) * 6
            or not all(type(value) is bool for value in values)):
        evidence['unresolved'].append('Lean comparison failed: ' + (result.stderr + result.stdout)[:2000])
        return {'status': 'unresolved', 'evidence': evidence, 'cases': rows}
    return _findings(rows, values, evidence)


def _findings(rows, values, evidence):
    findings = []
    for i, row in enumerate(rows):
        code_bounds, code_body, cb, ct, sb, st = values[i * 6:i * 6 + 6]
        row['code_matches_python'] = code_bounds and code_body
        row['contract_matches_python'] = cb and ct
        row['solution_matches_python'] = sb and st
        if not row['code_matches_python']:
            evidence['unresolved'].append('Source model differs from Python: ' + row['name'])
        else:
            for model, bounds, body in (('contract', cb, ct), ('solution', sb, st)):
                if not bounds or not body:
                    findings.append({'model': model, 'case': row['name'], 'raw': row['raw'],
                                     'bounds': not bounds, 'body': not body,
                                     'source_symbols': evidence['symbols']})
    status = 'unresolved' if (evidence['effects']['status'] != 'permitted'
                              or any(not r['code_matches_python'] for r in rows)) else (
        'mismatch' if findings else 'no_mismatch_in_cases')
    return {'status': status, 'evidence': evidence, 'cases': rows, 'findings': findings}


def _formal_program(blocks):
    text = '\n'.join(re.sub(r'^\s*import Lean\s*\n', '', block, count=1)
                     for block in blocks)
    adapters = ['def normalizedBounds (b : Option (Nat × Nat × Nat)) : Option (List Nat) := '
                'b.map (fun (a, c, d) => [a, c, d])']
    for ns in ('CarrierBodyContract', 'CarrierBodySolution'):
        adapters.append(f"def {ns}Body (raw : List Nat) : Option (List Nat) := "
                        f"match {ns}.body raw with | .missingDelimiter => none "
                        f"| .body bytes => some bytes")
    rows = []
    for raw in _CASES.values():
        value = _lean_bytes(raw)
        rows.append(f'(normalizedBounds ({{ns}}.bounds {value}), {{ns}}Body {value})')
    expr = ', '.join(row.format(ns=ns) for row in rows
                     for ns in ('CarrierBodyContract', 'CarrierBodySolution'))
    return 'import Lean\n' + text + '\n' + '\n'.join(adapters) + (
        '\n#eval IO.println (Lean.toJson [' + expr + ']).compress\n')


def _formal_compare(root, lean):
    evidence = {'scope': 'Eight byte witnesses only; no inference for unmodeled boundary behavior.',
                'coverage_unresolved': ['Unmapped Manifest entries and unmodeled code, state, I/O and boundary behavior are not checked.'],
                'unresolved': []}
    findings = []
    try:
        blocks, evidence['formal'] = formal_inputs(root)
    except (OSError, ValueError, SyntaxError) as exc:
        evidence['unresolved'].append('Formal binding: ' + str(exc))
        return _formal_report('unresolved', evidence, [], findings)
    executable = shutil.which(lean)
    if executable is None:
        evidence['unresolved'].append('Lean executable unavailable')
        return _formal_report('unresolved', evidence, [], findings)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'FormalComparison.lean'
        path.write_text(_formal_program(blocks))
        try:
            result = subprocess.run([executable, str(path)], capture_output=True,
                                    text=True, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            evidence['unresolved'].append('Lean comparison timed out')
            return _formal_report('unresolved', evidence, [], findings)
    try:
        values = json.loads(result.stdout)
        if result.returncode or not _valid_formal_values(values):
            raise ValueError('unexpected Lean result')
    except (ValueError, TypeError):
        evidence['unresolved'].append('Lean comparison failed: ' + (result.stderr + result.stdout)[:2000])
        return _formal_report('unresolved', evidence, [], findings)
    cases = []
    for i, (name, raw) in enumerate(_CASES.items()):
        contract, solution = values[2 * i:2 * i + 2]
        row = {'name': name, 'raw': list(raw), 'contract': contract, 'solution': solution}
        cases.append(row)
        if contract != solution:
            findings.append({'kind': 'formal_disagreement', 'case': name, 'raw': list(raw),
                             'bounds': contract[0] != solution[0], 'body': contract[1] != solution[1]})
    return _formal_report('mismatch' if findings else 'no_mismatch_in_cases',
                          evidence, cases, findings)


def _formal_report(status, evidence, cases, findings):
    checked = len(cases) == len(_CASES)
    behavior = []
    for index, operation in enumerate(('bounds', 'body')):
        differing = [row['name'] for row in cases
                     if row['contract'][index] != row['solution'][index]]
        behavior.append({'contract_operation': operation, 'solution_operation': operation,
                         'verdict': ('mismatch' if differing else
                                     'no_mismatch_in_cases' if checked else 'unresolved'),
                         'differing_cases': differing})
    directions = {
        'manifest_to_contract': {'verdict': 'unresolved', 'reason': 'No comparable Manifest facts are modeled.'},
        'manifest_to_solution': {'verdict': 'unresolved', 'reason': 'No comparable Manifest facts are modeled.'},
        'contract_to_solution': {'behavioral_witnesses': behavior, 'case_count': len(cases)},
    }
    return {'status': status, 'evidence': evidence, 'cases': cases,
            'findings': findings, 'directions': directions}


def _valid_formal_values(values):
    def naturals(value):
        return isinstance(value, list) and all(type(n) is int and n >= 0 for n in value)
    def observation(value):
        if not isinstance(value, list) or len(value) != 2:
            return False
        bounds, body = value
        return ((bounds is None or (naturals(bounds) and len(bounds) == 3))
                and (body is None or (naturals(body) and all(n <= 255 for n in body))))
    return isinstance(values, list) and len(values) == len(_CASES) * 2 and all(map(observation, values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--lean', default='lean')
    parser.add_argument('--formal-only', action='store_true')
    args = parser.parse_args()
    try:
        report = compare(args.root, args.lean, formal_only=args.formal_only)
    except (OSError, ValueError, SyntaxError) as exc:
        report = {'status': 'unresolved', 'reason': str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'no_mismatch_in_cases' else 1


if __name__ == '__main__':
    raise SystemExit(main())
