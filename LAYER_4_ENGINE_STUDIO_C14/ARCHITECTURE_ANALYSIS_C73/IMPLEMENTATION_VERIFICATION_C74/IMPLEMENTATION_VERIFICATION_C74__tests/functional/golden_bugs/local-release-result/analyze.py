"""Check the bounded local release result contract in a checkout."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
EXPECTED = {'run_id': 'arguments.run_id', 'project_root': 'str(root)'}


def fields_from_dict(node, runner_name, runner_fields):
    fields, diagnostics = {}, False
    if not isinstance(node, ast.Dict):
        raise ValueError('unsupported local return value')
    for key, value in zip(node.keys, node.values):
        if key is None:
            if not isinstance(value, ast.Name) or value.id != runner_name or diagnostics:
                raise ValueError('unsupported result spread')
            diagnostics = True
            fields.update(runner_fields)
        elif isinstance(key, ast.Constant) and isinstance(key.value, str):
            if any(isinstance(n, ast.Name) and n.id == runner_name for n in ast.walk(value)):
                raise ValueError('unsupported result value')
            fields[key.value] = ast.unparse(value)
        else:
            raise ValueError('unsupported result key')
    return fields, diagnostics


def result_facts(branch, call, returned):
    if returned.value is call:
        return {}, True
    assignments = [n for n in branch.body if isinstance(n, ast.Assign)
                   and n.value is call and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name)]
    if len(assignments) != 1 or returned not in branch.body:
        raise ValueError('unsupported runner assignment or return flow')
    assignment = assignments[0]
    name = assignment.targets[0].id
    start, end = branch.body.index(assignment), branch.body.index(returned)
    if start >= end:
        raise ValueError('unsupported result order')
    fields = {}
    for stmt in branch.body[start + 1:end]:
        uses = any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(stmt))
        if not uses:
            continue
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and ast.unparse(stmt.value.func) == name + '.update'
                and not stmt.value.args and all(k.arg for k in stmt.value.keywords)):
            raise ValueError('unsupported result mutation or flow')
        for keyword in stmt.value.keywords:
            if keyword.arg not in EXPECTED:
                raise ValueError('unsupported diagnostic mutation')
            if any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(keyword.value)):
                raise ValueError('unsupported result update value')
            fields[keyword.arg] = ast.unparse(keyword.value)
    value = returned.value
    if isinstance(value, ast.Name) and value.id == name:
        return fields, True
    extra, diagnostics = fields_from_dict(value, name, fields)
    if diagnostics:
        if any(key not in EXPECTED for key in extra):
            raise ValueError('unsupported diagnostic replacement')
        return extra, True
    if any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(value)):
        raise ValueError('unsupported result replacement')
    return extra, False


def lean_bytes(value):
    if value is None:
        return 'none'
    return '(some [' + ', '.join(str(byte) for byte in value.encode('utf-8')) + '])'


def extract(root, path=None):
    path = path or json.loads((HERE / 'case.json').read_text())['before']['source']
    target = (root / path).resolve(strict=True)
    if not target.is_relative_to(root) or Path(path).is_absolute():
        raise ValueError('source path must be relative to checkout')
    tree = ast.parse(target.read_text())
    branches = [n for n in ast.walk(tree) if isinstance(n, ast.If)
                and ast.unparse(n.test) == "arguments.operation == 'local'"]
    if len(branches) != 1:
        raise ValueError('expected one local operation branch')
    branch = branches[0]
    calls = [n for n in ast.walk(branch) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == 'run_local_release']
    returns = [n for n in ast.walk(branch) if isinstance(n, ast.Return)]
    if len(calls) != 1 or len(returns) != 1:
        raise ValueError('unsupported local runner or return')
    fields, diagnostics = result_facts(branch, calls[0], returns[0])
    details = [f'{key} is {"missing" if key not in fields else "incorrect"}.'
               for key, value in EXPECTED.items() if fields.get(key) != value]
    if not diagnostics:
        details.append('Runner diagnostics are discarded.')
    observed = [lean_bytes(fields.get(key)) for key in EXPECTED]
    expected = [lean_bytes(value) for value in EXPECTED.values()]
    program = f'''def runId : Option (List Nat) := {observed[0]}
def projectRoot : Option (List Nat) := {observed[1]}
def preservesDiagnostics : Bool := {str(diagnostics).lower()}
def violates : Bool := !(runId == {expected[0]} && projectRoot == {expected[1]} && preservesDiagnostics)
#eval violates
'''
    return path, details, program


def verify(program, expected, lean):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'check.lean'
        path.write_text(program)
        run = subprocess.run([lean, str(path)], capture_output=True, text=True, timeout=30)
    if run.returncode or run.stdout.strip() != expected:
        raise ValueError('Lean verification failed: ' + (run.stdout + run.stderr)[:1000])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    parser.add_argument('--file')
    args = parser.parse_args()
    report = {'findings': [], 'unresolved': []}
    try:
        path, details, program = extract(args.checkout.resolve(strict=True), args.file)
        verify(program, str(bool(details)).lower(), args.lean)
        if details:
            report['findings'].append({'path': path, 'detail': ' '.join(details)})
    except (OSError, SyntaxError, UnicodeError, ValueError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
