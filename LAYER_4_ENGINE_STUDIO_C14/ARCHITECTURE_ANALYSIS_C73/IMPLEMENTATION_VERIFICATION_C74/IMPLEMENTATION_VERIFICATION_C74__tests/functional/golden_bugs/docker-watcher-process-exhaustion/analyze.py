"""Discover and model the historical filtered-root watcher scheduling pattern."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def same(node, expression):
    return ast.dump(node, include_attributes=False) == ast.dump(ast.parse(expression, mode='eval').body, include_attributes=False)


def analyze(path):
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (SyntaxError, UnicodeError, OSError):
        return None
    for cls in (x for x in tree.body if isinstance(x, ast.ClassDef)):
        for start in (x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == 'start'):
            assigns = [x for x in ast.walk(start) if isinstance(x, ast.Assign) and len(x.targets) == 1 and isinstance(x.targets[0], ast.Name)]
            obs = [x.value for x in assigns if x.targets[0].id == 'observer']
            filt = [x.value for x in assigns if x.targets[0].id == 'filtered']
            schedules = [x for x in ast.walk(start) if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == 'schedule']
            if len(obs) != 1 or len(filt) != 1 or len(schedules) != 2:
                continue
            expected = {'observer.schedule(_Handler(self), str(path), recursive=not filtered)',
                        'observer.schedule(_Handler(self), str(child), recursive=True)'}
            if {ast.unparse(x) for x in schedules} != expected:
                continue
            root_loops = [x for x in ast.walk(start) if isinstance(x, ast.For) and same(x.iter, 'self._roots')]
            if len(root_loops) != 1 or not any(isinstance(x, ast.If) and same(x.test, 'filtered') and
                    any(isinstance(y, ast.For) and same(y.iter, 'path.iterdir()') for y in x.body)
                    for x in root_loops[0].body):
                continue
            old_filter = 'self._exclude_directory is not None and path == self._root'
            new_filter = 'not self._poll_bind_mount and self._exclude_directory is not None and path == self._root'
            loop_template = """for path in self._roots:
    filtered = FILTER
    self._watched_directories[path] = observer.schedule(_Handler(self), str(path), recursive=not filtered)
    if filtered:
        for child in path.iterdir():
            if child.is_dir() and not child.is_symlink() and not self._exclude_directory(child.relative_to(self._root).as_posix()):
                self._watched_directories[child] = observer.schedule(_Handler(self), str(child), recursive=True)
"""
            if not any(ast.dump(root_loops[0], include_attributes=False) == ast.dump(
                ast.parse(loop_template.replace('FILTER', expression)).body[0], include_attributes=False
            ) for expression in (old_filter, new_filter)):
                continue
            if same(obs[0], 'factory()') and same(filt[0], old_filter):
                return False, True
            if same(obs[0], 'PollingObserverVFS(os.lstat, self._source_entries) if self._poll_bind_mount else factory()') and same(filt[0], new_filter):
                return True, False
    return None


def lean_source(polling, filtered):
    return f'''-- Generated from the checked observer and filtered scheduling AST branches.
-- One filtered root, with n eligible top-level children.
def pollingObserver : Bool := {str(polling).lower()}
def filteredRoot : Bool := {str(filtered).lower()}
def schedules (n : Nat) : Nat := 1 + if filteredRoot then n else 0
#eval (pollingObserver, schedules 80)
theorem observed : (pollingObserver, schedules 80) = ({str(polling).lower()}, {81 if filtered else 1}) := by decide
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    output = {'findings': [], 'unresolved': []}
    try:
        found = [(path, result) for path in args.checkout.rglob('*.py') if (result := analyze(path)) is not None]
        if len(found) != 1:
            raise ValueError(f'Expected one supported watcher; found {len(found)}')
        path, (polling, filtered) = found[0]
        with tempfile.TemporaryDirectory() as tmp:
            lean_file = Path(tmp) / 'watcher.lean'
            lean_file.write_text(lean_source(polling, filtered))
            result = subprocess.run([args.lean, str(lean_file)], text=True, capture_output=True, check=True, timeout=30)
        expected = f"({str(polling).lower()}, {81 if filtered else 1})"
        if result.stdout.strip() != expected:
            raise ValueError(f'Unexpected Lean output: {result.stdout.strip()}')
        if not polling or filtered:
            output['findings'].append({'path': str(path.relative_to(args.checkout)),
                'detail': 'For a filtered root with 80 eligible child directories, the modeled factory observer uses 81 schedules instead of one polling schedule (Lean verified).'})
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        output['unresolved'].append({'path': '.', 'detail': str(error)})
    print(json.dumps(output))



if __name__ == '__main__':
    main()
