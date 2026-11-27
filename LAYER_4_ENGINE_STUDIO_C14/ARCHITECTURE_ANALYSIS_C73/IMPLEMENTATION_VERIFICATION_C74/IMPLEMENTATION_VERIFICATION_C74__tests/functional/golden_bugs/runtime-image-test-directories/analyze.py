import argparse
import ast
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

NAMES = {'_TRANSIENT_DIRECTORIES': 'transient', '_CREDENTIAL_DIRECTORIES': 'credentials'}
CASES = {'FEATURE_MCP__tests': True, 'FEATURE_MCP__tests_old': False, 'FEATURE_MCP': False,
         '.git': True, 'credentials': True, '.anechoic_tmp': True}
SUFFIX = 'MCP_PATCHBAY_C21/FEATURE_MCP/docker'


def lower(node):
    match node:
        case ast.BoolOp(op=ast.Or(), values=values):
            return '(' + ' || '.join(lower(value) for value in values) + ')'
        case ast.Compare(left=ast.Name(id='name'), ops=[ast.In()], comparators=[ast.Name(id=key)]) if key in NAMES:
            return f'{NAMES[key]}.contains name'
        case ast.Call(func=ast.Attribute(value=ast.Name(id='name'), attr=attr), args=[argument], keywords=[]) if attr in ('startswith', 'endswith'):
            values = ast.literal_eval(argument)
            values = (values,) if isinstance(values, str) else values
            if isinstance(values, tuple) and values and all(isinstance(value, str) for value in values):
                method = 'startsWith' if attr == 'startswith' else 'endsWith'
                return '(' + ' || '.join(f'name.{method} {json.dumps(value, ensure_ascii=False)}' for value in values) + ')'
    raise ValueError('Unsupported runtime image exclusion expression')


def constants(tree):
    declarations = {}
    for statement in tree.body:
        match statement:
            case ast.Assign(targets=[ast.Name(id=key)], value=ast.Call(func=ast.Name(id='frozenset'), args=[argument], keywords=[])) if key in NAMES:
                values = ast.literal_eval(argument)
                if key in declarations or not isinstance(values, set) or not all(isinstance(value, str) for value in values):
                    raise ValueError('Unsupported runtime image exclusion constants')
                declarations[key] = f'def {NAMES[key]} : List String := {json.dumps(sorted(values), ensure_ascii=False)}'
    if declarations.keys() != NAMES.keys():
        raise ValueError('Runtime image exclusion constants are missing')
    return list(declarations.values())


def locate(root):
    sources = [path for layer in root.glob('LAYER_*_ENGINE_STUDIO*')
               for name in ('runtime_images.py', 'runtime_images_common.py')
               if (path := layer / SUFFIX / name).is_file()]
    matches = []
    for path in sources:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        matches.extend((path, tree, fn) for fn in tree.body
                       if isinstance(fn, ast.FunctionDef) and fn.name == '_excluded_directory')
    if len(matches) != 1:
        raise ValueError('Expected one runtime image directory predicate')
    return matches[0]


def program(tree, predicate):
    args = predicate.args
    if ([arg.arg for arg in args.args] != ['name'] or args.posonlyargs or args.kwonlyargs
            or args.vararg or args.kwarg or args.defaults or predicate.decorator_list
            or len(predicate.body) != 1 or not isinstance(predicate.body[0], ast.Return)):
        raise ValueError('Unsupported runtime image directory predicate')
    expression = lower(predicate.body[0].value)
    return '\n'.join(['import Lean', *constants(tree), f'def excluded (name : String) : Bool := {expression}',
                      f'#eval IO.println (Lean.toJson ({json.dumps(list(CASES))}.map excluded)).compress', ''])


def scan(root, lean):
    path, tree, predicate = locate(root)
    with TemporaryDirectory() as temp:
        target = Path(temp) / 'ExcludeDirectory.lean'
        target.write_text(program(tree, predicate), encoding='utf-8')
        result = subprocess.run([lean, target], capture_output=True, text=True, check=False, timeout=30)
    if result.returncode:
        raise ValueError('Lean refused runtime image predicate: ' + (result.stderr + result.stdout)[:1000])
    observed = json.loads(result.stdout)
    if not isinstance(observed, list) or len(observed) != len(CASES) or any(type(value) is not bool for value in observed):
        raise ValueError('Unexpected Lean runtime image exclusion result')
    findings = []
    for (name, expected), actual in zip(CASES.items(), observed, strict=True):
        if expected != actual:
            label = 'excluded' if expected else 'included'
            findings.append({'path': path.relative_to(root).as_posix(), 'detail': f'Expected {name!r} to be {label}.'})
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    report = {'findings': [], 'unresolved': []}
    try:
        report['findings'] = scan(args.checkout, args.lean)
    except (OSError, SyntaxError, ValueError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
