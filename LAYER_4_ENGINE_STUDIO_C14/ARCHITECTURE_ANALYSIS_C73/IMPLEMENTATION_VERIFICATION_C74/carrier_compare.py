"""Compare the admitted Python carrier, its Lean model, and a Spec model."""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .carrier_direct import compare_direct
from .carrier_formal import formal_inputs
from .carrier_model import _SOURCE, generate
from .carrier_observations import lean_bytes, observe, python_checks
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


def _checks(rows):
    checks = []
    for row in rows:
        raw = lean_bytes(row['raw'])
        b = row['bounds']
        expected = 'none' if b is None else f'some ({b[0]}, {b[1]}, {b[2]})'
        if row['body'] is None:
            suffix = 'missingDelimiter'
        else:
            suffix = 'body ' + lean_bytes(row['body'])
        checks.extend(python_checks(row))
        for namespace in ('CarrierBodyContract', 'CarrierBodySolution'):
            checks.extend([f'{namespace}.bounds {raw} == {expected}',
                           f'{namespace}.body {raw} == ({namespace}.Outcome.{suffix})'])
    return '#eval IO.println (Lean.toJson [' + ',\n'.join(checks) + ']).compress\n'


def compare(root, lean='lean', formal_only=False, *,
            manifest=None, solution=None, formal_verifier=None, implementation_sha256=None):
    """Return binding evidence, per-case findings, and explicit unresolved gaps."""
    if any(item is not None for item in (manifest, solution, formal_verifier, implementation_sha256)):
        if formal_only or manifest is None or solution is None or not callable(formal_verifier):
            raise ValueError('direct comparison requires two pins and a formal verifier')
        return compare_direct(root, manifest, solution, formal_verifier, lean,
                              implementation_sha256=implementation_sha256)
    if formal_only:
        return _formal_compare(root, lean)
    source = (Path(root) / _SOURCE).read_bytes()
    model, evidence = generate(root, source)
    evidence['effects'] = analyze_carrier(source)
    blocks, evidence['formal'] = formal_inputs(root)
    evidence['unresolved'].append('Spec Engine Python-to-Lean compilation is unsupported')
    rows = observe(root, evidence, source, _CASES)
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
    adapters = [('def normalizedBounds (b : Option (Nat × Nat × Nat)) : Option (List Nat) := '
                 'b.map (fun (a, c, d) => [a, c, d])')]
    for ns in ('CarrierBodyContract', 'CarrierBodySolution'):
        adapters.append(f"def {ns}Body (raw : List Nat) : Option (List Nat) := "
                        f"match {ns}.body raw with | .missingDelimiter => none "
                        f"| .body bytes => some bytes")
    rows = []
    for raw in _CASES.values():
        value = lean_bytes(raw)
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


def _validate_spec_pins(pins):
    for role in ('manifest', 'solution'):
        source = pins.get(role)
        if not isinstance(source, dict) or not _valid_digest(source.get('sha256')):
            raise ValueError(f'{role} pin requires a lowercase SHA-256 digest')


def _compare_pinned(root, path, lean, component):
    request = json.loads(path.read_text(encoding='utf-8'))
    keys = {'manifest', 'solution', 'implementation_sha256'}
    if component == 'C87':
        keys.add('witness')
    optional = {'export_sha256'} if component in ('C87', 'C90') else set()
    if not isinstance(request, dict) or request.keys() - optional != keys:
        raise ValueError('pins require ' + ', '.join(sorted(keys)))
    _validate_spec_pins(request)
    if 'export_sha256' in request and not _valid_digest(request['export_sha256']):
        raise ValueError('export_sha256 must be a lowercase SHA-256 digest')

    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
        verify_formal_chain,
    )

    digests = request['implementation_sha256']
    if component == 'C87':
        from .renderer_compare import RENDERER_SOURCE_NAMES, compare_renderer

        witness = request['witness']
        if not isinstance(witness, dict) or witness.keys() != {'manifest', 'solution'}:
            raise ValueError('renderer witness requires manifest and solution pins')
        _validate_spec_pins(witness)
        if (not isinstance(digests, dict) or digests.keys() != set(RENDERER_SOURCE_NAMES)
                or not all(map(_valid_digest, digests.values()))):
            raise ValueError('renderer implementation_sha256 requires both source names and lowercase SHA-256 digests')
        return compare_renderer(root, request, verify_formal_chain, lean)
    if not _valid_digest(digests):
        raise ValueError('implementation_sha256 must be a lowercase SHA-256 digest')
    if component == 'C90':
        from .diagnostic_compare import compare_diagnostic

        return compare_diagnostic(root, request, verify_formal_chain, lean)
    return compare(root, lean, formal_verifier=verify_formal_chain, **request)


def _valid_digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--lean', default='lean')
    parser.add_argument('--component', choices=('C30', 'C87', 'C90'), default='C30')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--formal-only', action='store_true')
    mode.add_argument('--pins', type=Path, help='JSON file with manifest, solution, and implementation_sha256')
    args = parser.parse_args()
    if args.component != 'C30' and args.pins is None:
        parser.error(f'{args.component} comparison requires --pins')
    try:
        if args.pins is None:
            report = compare(args.root, args.lean, formal_only=args.formal_only)
        else:
            report = _compare_pinned(args.root, args.pins, args.lean, args.component)
    except (OSError, ValueError, SyntaxError) as exc:
        report = {'status': 'unresolved', 'reason': str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'no_mismatch_in_cases' else 1


if __name__ == '__main__':
    raise SystemExit(main())
