"""Recognize the two archived receipt implementations; abstain on other shapes."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def shape(path):
    return ast.dump(ast.parse(path.read_text(encoding='utf-8')), include_attributes=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        candidates = [p for p in args.checkout.rglob('watcher_receipts.py')
                      if p.parent.name == 'ORCHESTRATOR_beta_C68']
        if len(candidates) != 1:
            raise ValueError(f'expected one orchestrator receipt module, found {len(candidates)}')
        path = candidates[0]
        reference = Path(__file__).parent
        actual = shape(path)
        if actual == shape(reference / 'before.py.txt'):
            supported = False
        elif actual == shape(reference / 'fixed.py.txt'):
            supported = True
        else:
            raise ValueError('unsupported receipt implementation structure')
        source = f'''def handled (recordsOrdinary acceptsOrdinary : Bool) : Bool := recordsOrdinary && acceptsOrdinary
#eval handled {str(supported).lower()} {str(supported).lower()}
example : handled {str(supported).lower()} {str(supported).lower()} = {str(supported).lower()} := by decide
'''
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp) / 'receipt.lean'
            proof.write_text(source)
            run = subprocess.run([args.lean, str(proof)], capture_output=True, text=True, timeout=30)
        if run.returncode or run.stdout.strip() != str(supported).lower():
            raise ValueError('Lean could not establish the modeled transition: ' + (run.stderr or run.stdout).strip())
        if not supported:
            result['findings'].append({'path': str(path.relative_to(args.checkout)), 'detail':
                'A known ordinary directory creation with a valid carrier witness is not recognized as handled when archive_epoch is absent.'})
    except (OSError, SyntaxError, UnicodeError, ValueError, subprocess.TimeoutExpired) as exc:
        result['unresolved'].append({'detail': str(exc)})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
