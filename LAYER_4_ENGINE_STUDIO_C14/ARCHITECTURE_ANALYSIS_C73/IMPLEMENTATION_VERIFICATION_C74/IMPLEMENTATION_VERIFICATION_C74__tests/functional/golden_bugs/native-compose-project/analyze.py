"""Analyze the native-selection-to-Compose boundary in a supplied source tree."""
import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path


def unique(root, name):
    paths = list(root.glob('LAYER_*/**/' + name))
    paths = [p for p in paths if not any(x in {'tests', '.venv', 'node_modules'} or x.endswith('__tests') for x in p.parts)]
    if len(paths) != 1:
        raise ValueError(f'Expected one {name}, found {len(paths)}')
    return paths[0], ast.parse(paths[0].read_text(encoding='utf-8'))


def same(node, code):
    return ast.dump(node, include_attributes=False) == ast.dump(ast.parse(code, mode='eval').body, include_attributes=False)


def contains(tree, code):
    return any(same(n, code) for n in ast.walk(tree) if isinstance(n, ast.expr))


def selected_wiring(launcher, startup):
    alias = any(isinstance(n, ast.ImportFrom) and n.module == 'native_startup' and any(a.name == 'select_runtime_project' and a.asname == 'resolve_project' for a in n.names) for n in launcher.body)
    calls = all(contains(launcher, code) for code in ('resolve_project(project_root, control_root)', 'backend.start(selection, image_id, fingerprint, remaining, requested_port)'))
    selectors = [n for n in startup.body if isinstance(n, ast.FunctionDef) and n.name == 'select_runtime_project']
    if not alias or not calls or len(selectors) != 1:
        raise ValueError('Unsupported native launcher wiring')
    if not contains(selectors[0], 'resolve_native_project(root, relative, validate_manifest=validate_manifest)') or not contains(selectors[0], 'native(relative)'):
        raise ValueError('Unsupported native selector wiring')


def compose_boundary(backend, selection):
    classes = [n for n in backend.body if isinstance(n, ast.ClassDef) and n.name == 'ProjectMcpBackend']
    models = [n for n in selection.body if isinstance(n, ast.ClassDef) and n.name == 'NativeProjectSelection']
    if len(classes) != 1 or len(models) != 1:
        raise ValueError('Ambiguous backend or native selection')
    methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == '_compose_project']
    if len(methods) != 1 or not contains(methods[0], 'getattr(selection, "compose_project", None)') or not contains(methods[0], 're.fullmatch(r"anechoic-mcp-[0-9a-f]{24}", value)'):
        raise ValueError('Unsupported Compose namespace validation')
    if not contains(classes[0], 'self._compose_project(selection)'):
        raise ValueError('Unsupported Compose invocation')
    props = [n for n in models[0].body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'compose_project']
    if not props:
        return False
    if len(props) != 1 or not any(isinstance(d, ast.Name) and d.id == 'property' for d in props[0].decorator_list) or len(props[0].body) != 1 or not isinstance(props[0].body[0], ast.Return) or not same(props[0].body[0].value, '"anechoic-mcp-" + self.instance_id[:24]'):
        raise ValueError('Unsupported Compose property')
    return True


def verify(lean, available):
    code = f'''def nativeSelected : Bool := true
def backendRequiresProperty : Bool := true
def propertyAvailable : Bool := {str(available).lower()}
def startupContract : Bool := !nativeSelected || !backendRequiresProperty || propertyAvailable
#eval startupContract
'''
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'compose.lean'
        path.write_text(code, encoding='utf-8')
        run = subprocess.run([lean, str(path)], capture_output=True, text=True, check=True, timeout=30)
    if run.stdout.strip() not in ('true', 'false'):
        raise ValueError('Unexpected Lean output')
    return run.stdout.strip() == 'true'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        _, launcher = unique(args.checkout, 'project_mcp_launcher.py')
        _, startup = unique(args.checkout, 'native_startup.py')
        _, backend = unique(args.checkout, 'project_mcp_backend.py')
        path, selection = unique(args.checkout, 'native_project_selection.py')
        selected_wiring(launcher, startup)
        available = compose_boundary(backend, selection)
        if not verify(args.lean, available):
            result['findings'].append({'path': str(path.relative_to(args.checkout)), 'detail': 'Native selection lacks the Compose project property required by the native launcher backend.'})
    except (OSError, ValueError, SyntaxError, subprocess.SubprocessError) as exc:
        result['unresolved'].append({'path': '.', 'detail': str(exc)})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
