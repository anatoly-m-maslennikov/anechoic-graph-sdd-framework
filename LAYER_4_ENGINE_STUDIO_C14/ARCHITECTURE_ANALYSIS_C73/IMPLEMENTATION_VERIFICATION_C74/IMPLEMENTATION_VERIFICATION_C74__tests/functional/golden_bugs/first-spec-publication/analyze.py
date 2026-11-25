"""Translate the historical SPEC selection branch for one bounded witness."""
import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

ASSIGNS = (
    "atom_id, version = (match[1], target['version'])",
    "chosen = [row for row in current_rows if row.get('_exact_ref') == target['ref_id'] and row.get('status_group') == 'Draft']",
    "predecessors = [row for row in current_rows if row.get('id') == atom_id and row.get('status_group') == 'Current']",
)
TESTS = {
    "any((item[2] == target['ref_id'] for item in refs))": 'pinned',
    "'-S-' in atom_id and len(chosen) == 1 and (not predecessors)": 'chosen == 1 && predecessors == 0',
    'len(chosen) != 1 or len(predecessors) > 1': 'chosen != 1 || predecessors > 1',
    'not predecessors': 'predecessors == 0',
    "'-S-' in atom_id": 'true',
    "version != 1 or '-T-' not in atom_id": 'true',
    "version == 1 and '-T-' in atom_id": 'false',
}
RETURNS = {
    '_publish_first_pinned_spec(selection, chosen[0], structure_snapshot)': 'firstPinned',
    '_publish_first_spec(selection, chosen[0], structure_snapshot, pinned=True)': 'firstPinned',
    '_publish_first_spec(selection, chosen[0], structure_snapshot, pinned=False)': 'firstUnpinned',
    '_promote_new(selection, target, status, chosen[0], current_rows)': 'other',
}
RAISES = {
    "common.InputError('target', 'A migration-pinned Draft cannot be promoted.')": 'reject',
    "common.SourceChanged('Draft or Current predecessor is missing or ambiguous.')": 'ambiguous',
    "common.SourceChanged('Current predecessor is missing.')": 'missing',
}


def translate(statements, tail):
    for node in reversed(statements):
        if isinstance(node, ast.If) and not node.orelse:
            test = TESTS.get(ast.unparse(node.test))
            if test is None:
                raise ValueError(f'unsupported condition: {ast.unparse(node.test)}')
            tail = f'(if {test} then {translate(node.body, tail)} else {tail})'
        elif isinstance(node, ast.Return) and ast.unparse(node.value) in RETURNS:
            tail = '.' + RETURNS[ast.unparse(node.value)]
        elif isinstance(node, ast.Raise) and ast.unparse(node.exc) in RAISES:
            tail = '.' + RAISES[ast.unparse(node.exc)]
        elif isinstance(node, ast.Assign) and ast.unparse(node) in ASSIGNS:
            continue
        else:
            raise ValueError(f'unsupported statement: {ast.unparse(node)}')
    return tail


def extract(root):
    paths = [p for p in root.rglob('native_draft.py') if 'ATOM_LIFECYCLE' in p.parts and not any('test' in part.lower() or part.startswith('.') for part in p.relative_to(root).parts)]
    if len(paths) != 1:
        raise ValueError('expected one lifecycle native_draft.py')
    path = paths[0]
    tree = ast.parse(path.read_text(encoding='utf-8'))
    candidates = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = fn.body
        starts = [i for i, n in enumerate(body) if isinstance(n, ast.If) and ast.unparse(n.test) == next(iter(TESTS))]
        ends = [i for i, n in enumerate(body) if isinstance(n, ast.If) and ast.unparse(n.test) == 'not predecessors']
        if len(starts) == len(ends) == 1 and starts[0] < ends[0]:
            candidates.append((body, starts[0], ends[0]))
    if len(candidates) != 1:
        raise ValueError('expected one SPEC selection branch')
    body, start, end = candidates[0]
    before = body[max(0, start - 3):start]
    after = body[start + 1:start + 4]
    if not any(tuple(ast.unparse(n) for n in nodes) == ASSIGNS for nodes in (before, after)):
        raise ValueError('unsupported selection assignments')
    return path.relative_to(root).as_posix(), translate(body[start:end + 1], '.revision')


def main(pinned=False, case='first-spec-publication'):
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True, type=Path)
    args = parser.parse_args()
    report = {'findings': [], 'unresolved': []}
    try:
        path, route = extract(args.checkout.resolve(strict=True))
        expected = 'firstPinned' if pinned else 'firstUnpinned'
        source = f'''inductive Route where\n  | reject | ambiguous | missing | firstPinned | firstUnpinned | other | revision\n  deriving DecidableEq\ndef select (pinned : Bool) (chosen predecessors : Nat) : Route := {route}\n#eval select {str(pinned).lower()} 1 0 == .{expected}\n'''
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / 'selection.lean'
            program.write_text(source, encoding='utf-8')
            run = subprocess.run([str(args.lean.resolve(strict=True)), str(program)], capture_output=True, text=True, timeout=30)
        output = run.stdout.strip().splitlines()
        if run.returncode or output not in (['true'], ['false']):
            raise ValueError(f'Lean verification failed: {run.stdout} {run.stderr}')
        if output == ['false']:
            report['findings'].append({'path': path, 'detail': f'{case}: the valid SPEC witness does not select {expected}.'})
    except (OSError, SyntaxError, ValueError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    print(json.dumps(report, sort_keys=True))
    return 2 if report['unresolved'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
