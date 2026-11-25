"""Check an editor input-before-dispatch protocol in a selected browser test."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def lean_pair(item):
    return f"({item['i']}, {list(item['value'].encode('utf-8'))})"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--title', default='keeps unsaved SQL usable when browser storage')
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        paths = [args.checkout / args.file] if args.file else list(args.checkout.glob('LAYER_*/**/FEATURE_WORKBENCH_FRONTEND__tests/standalone-url.e2e.spec.ts'))
        if len(paths) != 1 or not paths[0].is_file():
            raise ValueError(f'Expected one browser test file, found {len(paths)}')
        repo = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
        compiler = repo / 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/node_modules/typescript/lib/typescript.js'
        if not compiler.is_file():
            raise ValueError('TypeScript compiler dependency unavailable')
        run = subprocess.run(['node', str(Path(__file__).with_name('analyze.cts')), str(paths[0]), args.title], capture_output=True, text=True, timeout=30)
        if run.returncode:
            raise ValueError('AST extraction failed: ' + run.stderr.strip())
        facts = json.loads(run.stdout)
        checks = ', '.join(lean_pair(item) for item in facts['checks'])
        model = Path(__file__).with_name('check.lean').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as temp:
            proof = Path(temp) / 'check.lean'
            proof.write_text(f"{model}\n#eval checkedBeforeDispatch {lean_pair(facts['input'])} [{checks}] {facts['dispatch']}\n", encoding='utf-8')
            checked = subprocess.run([args.lean, str(proof)], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
        if checked not in {'true', 'false'}:
            raise ValueError('Unexpected Lean output')
        if checked == 'false':
            result['findings'].append({'path': str(paths[0].relative_to(args.checkout)), 'detail': 'The test dispatches without first checking the intended SQL input.'})
    except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError) as exc:
        result['unresolved'].append({'path': '.', 'detail': str(exc)})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
