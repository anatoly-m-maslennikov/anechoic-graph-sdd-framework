#!/usr/bin/env -S python3 -B
"""Scan a checkout for the native Workbench status admission/dispatch invariant."""
import argparse
import ast
import json
import pathlib
import subprocess
import tempfile


def fail(message):
    raise ValueError(message)


def assignments(tree):
    result = {}
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if isinstance(target, ast.Name):
            result[target.id] = stmt.value
        elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(stmt.value, (ast.Tuple, ast.List)) and len(target.elts) == len(stmt.value.elts):
            for name, value in zip(target.elts, stmt.value.elts):
                if isinstance(name, ast.Name):
                    result[name.id] = value
    return result


def evaluate(node, bindings, seen=()):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in seen or node.id not in bindings:
            fail(f'unknown or recursive name {node.id}')
        return evaluate(bindings[node.id], bindings, seen + (node.id,))
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = []
        for part in node.elts:
            if isinstance(part, ast.Starred):
                val = evaluate(part.value, bindings, seen)
                if not isinstance(val, (tuple, frozenset)):
                    fail('starred value is not a collection')
                values.extend(val)
            else:
                values.append(evaluate(part, bindings, seen))
        return tuple(values)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'frozenset' and len(node.args) == 1 and not node.keywords:
        return frozenset(evaluate(node.args[0], bindings, seen))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return frozenset(evaluate(node.left, bindings, seen)) | frozenset(evaluate(node.right, bindings, seen))
    fail(f'unsupported expression {type(node).__name__}')


def lean_membership(node, bindings, target, seen=()):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return str(node.value == target).lower()
    if isinstance(node, ast.Name):
        if node.id in seen or node.id not in bindings:
            fail(f'unknown or recursive name {node.id}')
        return lean_membership(bindings[node.id], bindings, target, seen + (node.id,))
    if isinstance(node, ast.Starred):
        return lean_membership(node.value, bindings, target, seen)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        terms = [lean_membership(part, bindings, target, seen) for part in node.elts]
        return '(' + ' || '.join(terms or ['false']) + ')'
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'frozenset' and len(node.args) == 1 and not node.keywords:
        return lean_membership(node.args[0], bindings, target, seen)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return '(' + lean_membership(node.left, bindings, target, seen) + ' || ' + lean_membership(node.right, bindings, target, seen) + ')'
    fail(f'unsupported Lean expression {type(node).__name__}')


def discover(root):
    candidates = []
    for path in root.rglob('*.py'):
        if any(part in {'.git', '.venv', 'tests', '__tests__', 'node_modules'} or part.endswith('__tests') for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding='utf-8')
            if 'class DirectGateway' not in text or '_native_query' not in text:
                continue
            tree = ast.parse(text, filename=str(path))
        except (OSError, UnicodeError, SyntaxError):
            continue
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'DirectGateway'):
            for fn in (n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'initialize'):
                nodes = [n for n in ast.walk(fn) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'supported' for t in n.targets)]
                if nodes:
                    candidates.append((path, nodes, tree))
    if len(candidates) != 1:
        fail(f'expected one native gateway with supported assignment; found {len(candidates)}')
    gateway, nodes, gateway_tree = candidates[0]
    if len(nodes) != 1:
        fail('ambiguous supported assignment')
    native_guards = [n for n in ast.walk(gateway_tree) if isinstance(n, ast.If) and ast.dump(n.test, include_attributes=False) == ast.dump(ast.parse('self._native_query is not None', mode='eval').body, include_attributes=False)]
    guards_with_assignment = [n for n in native_guards if any(isinstance(child, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'supported' for t in child.targets) for child in ast.walk(n))]
    if len(guards_with_assignment) != 1:
        fail('supported assignment is not in one native guard')
    wanted = ast.dump(ast.parse('self.tool_blacklist |= frozenset(self.registry.routes) - supported').body[0], include_attributes=False)
    if not any(ast.dump(n, include_attributes=False) == wanted for n in ast.walk(guards_with_assignment[0])):
        fail('unsupported native blacklist computation')
    return gateway, nodes[0]


def load_components(gateway):
    helper = gateway.parent / 'workbench_tools.py'
    owner = gateway.parent / 'native_query.py'
    helper_tree = ast.parse(helper.read_text(encoding='utf-8'))
    owner_tree = ast.parse(owner.read_text(encoding='utf-8'))
    bindings = assignments(helper_tree) | assignments(owner_tree)
    status_name = evaluate(bindings['SYNC_STATUS'], bindings)
    if status_name != 'workbench_status':
        fail('status binding changed')
    native_tools = bindings.get('NATIVE_TOOLS')
    if not isinstance(native_tools, (ast.Tuple, ast.List, ast.Set)) or not any(isinstance(item, ast.Name) and item.id == 'SYNC_STATUS' for item in native_tools.elts):
        fail('status tool is not registered in native tools')
    return helper, owner, bindings, status_name, helper_tree, owner_tree


def status_dispatch(helper_tree):
    status_branches = [n for n in ast.walk(helper_tree) if isinstance(n, ast.If) and ast.dump(n.test, include_attributes=False) == ast.dump(ast.parse('name == SYNC_STATUS', mode='eval').body, include_attributes=False)]
    if len(status_branches) != 1:
        fail('unsupported native status branch')
    guards = [n for n in status_branches[0].body if isinstance(n, ast.If) and ast.dump(n.test, include_attributes=False) == ast.dump(ast.parse('self._query_owner is not None', mode='eval').body, include_attributes=False)]
    if len(guards) != 1 or len(guards[0].body) != 1:
        fail('unsupported native status dispatch guard')
    operation = guards[0].body[0]
    if ast.dump(operation, include_attributes=False) == ast.dump(ast.parse('return self._query_owner.status()').body[0], include_attributes=False):
        dispatches = True
    elif ast.dump(operation, include_attributes=False) == ast.dump(ast.parse('raise ValueError("Operation is unavailable for a native Project")').body[0], include_attributes=False):
        dispatches = False
    else:
        fail('unsupported native status dispatch operation')
    return dispatches


def analyze_owner(node, bindings, owner_tree):
    supported = evaluate(node.value, bindings)
    if not isinstance(supported, frozenset):
        fail('supported expression is not a set')
    owners = [n for n in owner_tree.body if isinstance(n, ast.ClassDef) and n.name == 'NativeQueryOwner']
    if len(owners) != 1:
        fail('native owner class missing or ambiguous')
    methods = [n for n in owners[0].body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'status']
    if len(methods) > 1:
        fail('ambiguous owner status')
    if methods:
        expected = ast.parse('def status(self):\n self._owner()\n return {"mode": "startup_snapshot"}\n').body[0]
        actual = methods[0]
        if not isinstance(actual, ast.FunctionDef) or len(actual.body) != 2 or ast.dump(ast.Module(body=actual.body, type_ignores=[]), include_attributes=False) != ast.dump(ast.Module(body=expected.body, type_ignores=[]), include_attributes=False):
            fail('unsupported owner status implementation')
    has_status = bool(methods)
    return supported, has_status


def verify_lean(lean, gateway, node, bindings, status_name, supported, dispatches, has_status):
    names = {name: evaluate(node, bindings) for name, node in bindings.items() if name in {'QUERY_TOOLS','INTERFACE_TOOLS','SAVE_VIEW','LOAD','SAVED_LIST','SYNC_STATUS'}}
    runtime = eval(compile(ast.Expression(node.value), str(gateway), 'eval'), {'__builtins__': {}, 'frozenset': frozenset}, names)
    if runtime != supported:
        fail('Python and extracted set disagree')
    translated = lean_membership(node.value, bindings, status_name)
    lean_source = f'''def admitted : Bool := {translated}\ndef dispatches : Bool := {str(dispatches).lower()}\ndef ownerStatus : Bool := {str(has_status).lower()}\ndef contract : Bool := admitted && dispatches && ownerStatus\n#eval contract\n'''
    with tempfile.TemporaryDirectory(prefix='native-status-lean-') as directory:
        source = pathlib.Path(directory) / 'check.lean'
        source.write_text(lean_source, encoding='utf-8')
        result = subprocess.run([str(lean.resolve()), str(source)], text=True, capture_output=True, timeout=30)
    if result.returncode or result.stdout.strip() not in {'true','false'}:
        fail('Lean evaluation failed: ' + result.stderr.strip())
    if (result.stdout.strip() == 'true') != (status_name in supported and dispatches and has_status):
        fail('Lean and Python observations disagree')


def make_findings(root, gateway, helper, owner, admitted, dispatches, has_status):
    findings = []
    if not admitted:
        findings.append({'path': str(gateway.relative_to(root)), 'detail': 'registered workbench_status is excluded from native supported tools'})
    if not dispatches:
        findings.append({'path': str(helper.relative_to(root)), 'detail': 'native status dispatch rejects the native query owner'})
    if not has_status:
        findings.append({'path': str(owner.relative_to(root)), 'detail': 'native query owner lacks the workbench_status dispatch method'})
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=pathlib.Path)
    parser.add_argument('--lean', required=True, type=pathlib.Path)
    args = parser.parse_args()
    root = args.checkout.resolve()
    findings, unresolved = [], []
    try:
        gateway, node = discover(root)
        helper, owner, bindings, status_name, helper_tree, owner_tree = load_components(gateway)
        dispatches = status_dispatch(helper_tree)
        supported, has_status = analyze_owner(node, bindings, owner_tree)
        admitted = status_name in supported
        verify_lean(args.lean, gateway, node, bindings, status_name, supported, dispatches, has_status)
        findings = make_findings(root, gateway, helper, owner, admitted, dispatches, has_status)
    except (ValueError, KeyError, OSError, SyntaxError, subprocess.SubprocessError) as exc:
        unresolved.append(str(exc))
    print(json.dumps({'findings': findings, 'unresolved': unresolved}, indent=2))
    return 1 if unresolved else 0

if __name__ == '__main__':
    raise SystemExit(main())
