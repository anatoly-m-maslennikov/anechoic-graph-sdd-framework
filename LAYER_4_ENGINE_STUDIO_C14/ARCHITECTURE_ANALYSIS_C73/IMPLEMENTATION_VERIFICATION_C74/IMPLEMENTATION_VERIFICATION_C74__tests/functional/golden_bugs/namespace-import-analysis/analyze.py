"""Check the namespace import shadow traversal in a historical checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def analyze(checkout, lean):
    paths = list(checkout.glob('LAYER_*/**/FEATURE_IMPORT_GRAPH_C61/web_state_cases.mjs'))
    if len(paths) != 1:
        raise ValueError(f'expected one scanner, found {len(paths)}')
    source = paths[0]
    ts = os.environ.get('TYPESCRIPT_PATH')
    if not ts:
        repo = next(p for p in HERE.parents if (p / '.git').exists())
        ts = str(repo / 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/node_modules/typescript/lib/typescript.js')
    if not Path(ts).is_file():
        raise ValueError('TypeScript compiler unavailable; set TYPESCRIPT_PATH to typescript.js')
    parsed = subprocess.run(['node', str(HERE / 'shape.cts'), str(source)], capture_output=True, text=True, timeout=30)
    if parsed.returncode or parsed.stdout.strip() not in ('guarded', 'unguarded'):
        raise ValueError('unsupported scanner or TypeScript unavailable: ' + parsed.stderr[:500])
    guarded = parsed.stdout.strip() == 'guarded'
    model = (HERE / 'regression.lean').read_text() + '\nexample : scanner ' + str(guarded).lower() + (' = ' if guarded else ' ≠ ') + 'required := by decide\n'
    with tempfile.TemporaryDirectory() as tmp:
        proof = Path(tmp) / 'case.lean'
        proof.write_text(model)
        result = subprocess.run([lean, str(proof)], capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError('Lean failed: ' + (result.stdout + result.stderr)[:500])
    return source.relative_to(checkout), guarded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        path, guarded = analyze(args.checkout.resolve(strict=True), args.lean)
        if not guarded:
            result['findings'].append({'path': str(path), 'detail': 'Namespace import without a default name crashes shadow traversal.'})
    except (OSError, ValueError, StopIteration, subprocess.TimeoutExpired) as exc:
        result['unresolved'].append(str(exc))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
