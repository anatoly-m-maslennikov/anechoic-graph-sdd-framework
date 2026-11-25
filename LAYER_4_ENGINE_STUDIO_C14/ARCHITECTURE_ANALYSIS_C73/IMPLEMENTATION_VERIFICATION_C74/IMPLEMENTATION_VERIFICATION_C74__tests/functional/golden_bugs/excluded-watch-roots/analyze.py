"""Check filtered-root watch coverage in a historical checkout."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def shape(node):
    return ast.dump(node, include_attributes=False)


def discover(root):
    found = []
    for path in root.glob('LAYER_*/**/source_watcher.py'):
        if any(x in {'.git', '.venv', 'node_modules', 'tests'} or x.endswith('__tests') for x in path.parts):
            continue
        try:
            text = path.read_text(encoding='utf-8')
            if 'class SourceWatcher' not in text:
                continue
            tree = ast.parse(text)
        except (OSError, UnicodeError, SyntaxError):
            continue
        found.extend((path, cls) for cls in tree.body if isinstance(cls, ast.ClassDef) and cls.name == 'SourceWatcher')
    if len(found) != 1:
        raise ValueError(f'Expected one source watcher, found {len(found)}')
    return found[0]


def extract(cls):
    starts = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'start']
    if len(starts) != 1:
        raise ValueError('Unsupported watcher start')
    schedule_blocks = [n for n in ast.walk(starts[0]) if isinstance(n, ast.Try) and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == 'schedule' for x in ast.walk(n))]
    if len(schedule_blocks) != 1:
        raise ValueError('Ambiguous scheduling block')
    body = [n for n in schedule_blocks[0].body if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == 'schedule' for x in ast.walk(n))]
    old = '''self._watched_directories = {
    path: observer.schedule(_Handler(self), str(path), recursive=True)
    for path in self._roots
}
'''
    fixed = '''for path in self._roots:
    filtered = self._exclude_directory is not None and path == self._root
    self._watched_directories[path] = observer.schedule(_Handler(self), str(path), recursive=not filtered)
    if filtered:
        for child in path.iterdir():
            if child.is_dir() and not child.is_symlink() and not self._exclude_directory(child.relative_to(self._root).as_posix()):
                self._watched_directories[child] = observer.schedule(_Handler(self), str(child), recursive=True)
'''
    actual = shape(ast.Module(body=body, type_ignores=[]))
    for text, root_recursive, child_recursive in ((old, 'true', 'false'), (fixed, '!hasFilter', 'hasFilter && isDir && !isSymlink && !excluded')):
        if actual == shape(ast.parse(text)):
            if root_recursive != 'true':
                check_filter_init(cls)
            return root_recursive, child_recursive
    raise ValueError('Unsupported watcher scheduling branch')


def check_filter_init(cls):
    initializers = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__']
    if len(initializers) != 1:
        raise ValueError('Unsupported watcher initializer')
    expected = ast.parse('self._exclude_directory = exclude_directory if self._root in self._roots else None').body[0]
    if not any(shape(n) == shape(expected) for n in initializers[0].body):
        raise ValueError('Unsupported exclusion filter binding')


def verify(lean, root_expr, child_expr):
    code = f'''set_option linter.unusedVariables false
def rootRecursive (hasFilter : Bool) : Bool := {root_expr}
def childRecursive (hasFilter isDir isSymlink excluded : Bool) : Bool := {child_expr}
def covered (r c : Bool) : Bool := r || c
#eval (covered (rootRecursive true) (childRecursive true true false true), covered (rootRecursive true) (childRecursive true true false false))
'''
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'proof.lean'
        path.write_text(code, encoding='utf-8')
        result = subprocess.run([lean, str(path)], capture_output=True, text=True, check=True, timeout=30)
    observed = result.stdout.strip()
    if observed not in {'(true, true)', '(false, true)', '(false, false)', '(true, false)'}:
        raise ValueError('Unexpected Lean observation')
    return observed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        path, cls = discover(args.checkout)
        root, child = extract(cls)
        observed = verify(args.lean, root, child)
        if observed != '(false, true)':
            result['findings'].append({'path': str(path.relative_to(args.checkout)), 'detail': f'Filtered top-level coverage is {observed} for excluded and included child, expected (false, true).'})
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result['unresolved'].append({'path': '.', 'detail': str(exc)})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
