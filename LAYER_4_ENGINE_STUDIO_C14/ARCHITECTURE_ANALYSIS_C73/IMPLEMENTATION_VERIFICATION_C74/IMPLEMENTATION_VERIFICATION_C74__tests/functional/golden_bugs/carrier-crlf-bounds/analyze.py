"""Translate the admitted frontmatter delimiter operations into Lean."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def shape(node):
    return ast.dump(node, include_attributes=False)


def parse_stmt(text):
    return ast.parse(text).body[0]


def extract(source):
    tree = ast.parse(source)
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'frontmatter_bounds']
    if len(funcs) != 1:
        raise ValueError('expected one frontmatter_bounds')
    expected_args = ast.parse('def f(raw: bytes): pass').body[0].args
    if funcs[0].decorator_list or shape(funcs[0].args) != shape(expected_args):
        raise ValueError('unsupported bounds signature')
    body = [n for n in funcs[0].body if not isinstance(n, ast.Pass) and not (
        isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
    if len(body) != 3:
        raise ValueError('unsupported bounds body')
    opening, search, result = body
    expected_opening = '''if raw.startswith(b"---\\n"):
    opening_end = len(b"---\\n")
elif raw.startswith(b"---\\r\\n"):
    opening_end = len(b"---\\r\\n")
else:
    return None'''
    expected_return = 'return None if closing is None else (opening_end, closing.start(), closing.end())'
    if shape(opening) != shape(parse_stmt(expected_opening)) or shape(result) != shape(parse_stmt(expected_return)):
        raise ValueError('unsupported opening or return operation')
    if not isinstance(search, ast.Assign) or len(search.targets) != 1 or not isinstance(search.targets[0], ast.Name) or search.targets[0].id != 'closing' or not isinstance(search.value, ast.Call):
        raise ValueError('unsupported closing assignment')
    call = search.value
    position = shape(ast.parse('opening_end - 1', mode='eval').body)
    pattern = rb'\r?\n---\r?\n'
    old = (shape(call.func) == shape(ast.parse('re.search', mode='eval').body)
           and len(call.args) == 3 and not call.keywords and isinstance(call.args[0], ast.Constant)
           and call.args[0].value == pattern and shape(call.args[1]) == shape(ast.Name(id='raw', ctx=ast.Load()))
           and shape(call.args[2]) == position)
    fixed = (shape(call.func) == shape(ast.parse('_CLOSING_DELIMITER.search', mode='eval').body)
             and len(call.args) == 1 and shape(call.args[0]) == shape(ast.Name(id='raw', ctx=ast.Load()))
             and len(call.keywords) == 1 and call.keywords[0].arg == 'pos' and shape(call.keywords[0].value) == position)
    if fixed:
        assignments = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_CLOSING_DELIMITER' for t in n.targets)]
        expected = '_CLOSING_DELIMITER = re.compile(rb"\\r?\\n---\\r?\\n")'
        fixed = len(assignments) == 1 and shape(assignments[0]) == shape(parse_stmt(expected))
    if not (old or fixed):
        raise ValueError('unsupported regex operation or start argument')
    return 'findClosing raw 0' if old else 'findClosing (raw.drop (openingEnd - 1)) (openingEnd - 1)'


def analyze(checkout, lean):
    paths = list(checkout.glob('LAYER_*_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/carrier_body__pub.py'))
    if len(paths) != 1:
        raise ValueError(f'expected one carrier body source, found {len(paths)}')
    path = paths[0]
    search = extract(path.read_bytes())
    proof = (HERE / 'regression.lean').read_text()
    model = proof.split('namespace Before\n', 1)[1].split('\nend Before', 1)[0]
    model = model.replace('let (start, stop) ← findClosing raw 0', 'let (start, stop) ← ' + search)
    contract = proof.split('namespace CarrierBodyContract\n', 1)[1].split('\nend CarrierBodyContract', 1)[0]
    text = ('import Lean\n' + model + '\nnamespace CarrierBodyContract\n' + contract +
            '\nend CarrierBodyContract\n'
            '#eval IO.println (frontmatterBounds [45,45,45,13,10,45,45,45,13,10,88] == '
            'CarrierBodyContract.bounds [45,45,45,13,10,45,45,45,13,10,88])\n')
    with tempfile.TemporaryDirectory() as tmp:
        lean_file = Path(tmp) / 'carrier.lean'
        lean_file.write_text(text)
        run = subprocess.run([lean, str(lean_file)], capture_output=True, text=True, timeout=40)
    if run.returncode or run.stdout.strip() not in ('true', 'false'):
        raise ValueError('Lean comparison failed: ' + (run.stdout + run.stderr)[:1000])
    return path.relative_to(checkout).as_posix(), run.stdout.strip() == 'false'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    report = {'findings': [], 'unresolved': []}
    try:
        path, mismatch = analyze(args.checkout.resolve(strict=True), args.lean)
        if mismatch:
            report['findings'].append({'path': path, 'detail': 'CRLF empty frontmatter closing separator starts at byte 3 instead of byte 4.'})
    except (OSError, ValueError, SyntaxError, IndexError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
