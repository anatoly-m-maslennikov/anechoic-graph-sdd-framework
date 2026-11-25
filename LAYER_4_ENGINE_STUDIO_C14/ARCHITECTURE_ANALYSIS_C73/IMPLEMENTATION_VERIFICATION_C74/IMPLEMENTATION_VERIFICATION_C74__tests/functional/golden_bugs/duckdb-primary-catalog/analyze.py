"""Check the native reference catalog query in a historical checkout."""
import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('checkout', type=Path)
parser.add_argument('--lean', required=True)
parser.add_argument('--emit', type=Path)
args = parser.parse_args()
result = {'findings': [], 'unresolved': []}
seen = 0
roots = list(args.checkout.rglob('DATABASE_SERVER_beta_C71'))
if len(roots) != 1:
    result['unresolved'].append({'path': '.', 'detail': 'expected one C71 source directory'})
for root in roots:
    paths = list(root.rglob('*.py'))
    if len(paths) > 10000:
        result['unresolved'].append({'path': str(root), 'detail': 'source file limit exceeded'})
        continue
    for path in paths:
        rel = str(path.relative_to(args.checkout))
        try:
            text = path.read_text()
            if not all(word in text for word in ('replace_native_atoms', 'information_schema.tables', 'native_references')):
                continue
            tree = ast.parse(text)
            funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'replace_native_atoms']
            if not funcs:
                continue
            if len(funcs) != 1:
                raise ValueError('expected one replace_native_atoms')
            sql = [n.value for n in ast.walk(funcs[0]) if isinstance(n, ast.Constant)
                   and isinstance(n.value, str) and 'information_schema.tables' in n.value.lower()]
            if len(sql) != 1:
                raise ValueError('expected one literal tables query')
            query = ' '.join(sql[0].lower().split())
            old = "select table_type from information_schema.tables where table_schema = 'main' and table_name = 'native_references'"
            new = "select table_type from information_schema.tables where table_catalog = current_database() and table_schema = 'main' and table_name = 'native_references'"
            if query not in (old, new):
                raise ValueError('unsupported tables query')
            isolated = query == new
            source = '-- Source SQL: ' + query + '\n'
            source += f'def catalogFilter : Bool := {str(isolated).lower()}\n'
            source += 'def leaked (attachedMatch : Bool) : Bool := attachedMatch && !catalogFilter\n#eval leaked true\n'
            if args.emit:
                args.emit.write_text(source)
            with tempfile.TemporaryDirectory() as tmp:
                leanfile = Path(tmp) / 'check.lean'
                leanfile.write_text(source)
                run = subprocess.run([args.lean, str(leanfile)], capture_output=True, text=True, timeout=45)
            if run.returncode or run.stdout.strip() not in ('true', 'false'):
                raise ValueError('Lean failed: ' + run.stderr + run.stdout)
            seen += 1
            if run.stdout.strip() == 'true':
                result['findings'].append({'path': rel, 'detail': 'A matching native_references table in an attached catalog is selected as the primary catalog table.'})
        except (OSError, SyntaxError, ValueError, subprocess.TimeoutExpired) as error:
            result['unresolved'].append({'path': rel, 'detail': str(error)})
if not seen and not result['unresolved']:
    result['unresolved'].append({'path': '.', 'detail': 'native atom query source not found'})
print(json.dumps(result))
