"""Check the archived lifecycle wakeup pattern; other shapes are unresolved."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def shape(node):
    return ast.dump(node, include_attributes=False)


def function(tree):
    return [f for c in tree.body if isinstance(c, ast.ClassDef) and c.name == 'QueuedJobs'
            for f in c.body if isinstance(f, ast.FunctionDef) and f.name == '_watch_queue']


def classify(path, reference):
    methods = function(ast.parse(path.read_text(encoding='utf-8')))
    if len(methods) != 1:
        return None
    method = methods[0]
    old = shape(ast.parse('batch or due', mode='eval').body)
    new = shape(ast.parse('batch or due or self.lifecycle_job is not None', mode='eval').body)
    guards = [n for n in ast.walk(method) if isinstance(n, ast.If) and shape(n.test) in (old, new)]
    if len(guards) != 1:
        return None
    guarded = shape(guards[0].test) == new
    guards[0].test = ast.parse('batch or due', mode='eval').body
    return guarded if shape(method) == reference else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        reference = shape(function(ast.parse((Path(__file__).parent / 'before.py.txt').read_text()))[0])
        candidates = [p for p in args.checkout.rglob('jobs.py') if p.parent.name == 'ORCHESTRATOR_beta_C68']
        if len(candidates) != 1:
            raise ValueError(f'expected one orchestrator jobs.py, found {len(candidates)}')
        path = candidates[0]
        guarded = classify(path, reference)
        if guarded is None:
            raise ValueError('unsupported queue function structure')
        source = f'''def enters (batch due lifecycle : Bool) : Bool := batch || due || ({str(guarded).lower()} && lifecycle)
#eval enters false false true
example : enters false false true = {str(guarded).lower()} := by decide
'''
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp) / 'wakeup.lean'
            proof.write_text(source)
            run = subprocess.run([args.lean, str(proof)], capture_output=True, text=True, timeout=30)
        if run.returncode or run.stdout.strip() != str(guarded).lower():
            raise ValueError('Lean could not establish the modeled transition: ' + (run.stderr or run.stdout).strip())
        if not guarded:
            result['findings'].append({'path': str(path.relative_to(args.checkout)), 'detail':
                'A queued lifecycle job does not enter the service branch when batch and retry are empty.'})
    except (OSError, SyntaxError, UnicodeError, ValueError, IndexError, subprocess.TimeoutExpired) as exc:
        result['unresolved'].append({'detail': str(exc)})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
