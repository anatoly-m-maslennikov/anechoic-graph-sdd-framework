"""Check stable-table freshness for a bounded full rebuild."""
import argparse
import ast
import json
import re
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('checkout', type=Path)
parser.add_argument('--lean', required=True)
parser.add_argument('--emit', type=Path)
parser.add_argument('--case', type=Path)
parser.add_argument('--file', type=Path)
args = parser.parse_args()
result = {'findings': [], 'unresolved': []}


def graph():
    data = json.loads(args.case.read_text()) if args.case else {
        'order': ['A', 'B'], 'edges': [['A', 'B']]}
    order, edges, released = data['order'], data['edges'], data.get('released', [])
    if (not isinstance(order, list) or not 1 <= len(order) <= 32
            or any(not isinstance(x, str) or not x for x in order)
            or len(set(order)) != len(order) or not isinstance(edges, list)
            or len(edges) > 256):
        raise ValueError('unsupported graph: expected 1..32 unique query identities and at most 256 edges')
    if (not isinstance(released, list) or any(not isinstance(x, str) or x not in order for x in released)
            or len(set(released)) != len(released)):
        raise ValueError('unsupported released observations')
    pairs = []
    for edge in edges:
        if (not isinstance(edge, list) or len(edge) != 2
                or any(not isinstance(x, str) or x not in order for x in edge)
                or edge[0] == edge[1] or edge in pairs):
            raise ValueError('unsupported graph edge: ' + repr(edge))
        pairs.append(edge)
    pending = set(order)
    while pending:
        ready = {x for x in pending if not any(b == x and a in pending for a, b in pairs)}
        if not ready:
            raise ValueError('unsupported graph: dependency cycle')
        pending -= ready
    return order, pairs, released


def allowed_guard(stmt, mode):
    if stmt.orelse:
        return False
    tests = {1: 'selected is not None and old_id not in selected',
             2: '(selected is not None or tables is not None) and old_id != selected'}
    return mode in tests and ast.dump(stmt.test, include_attributes=False) == ast.dump(ast.parse(tests[mode], mode='eval').body, include_attributes=False)


def loop_effects(loop, mode):
    body = []
    renamed = False
    retained, skip_released = False, False
    for stmt in loop.body:
        code = ast.unparse(stmt)
        if isinstance(stmt, ast.If) and not body and allowed_guard(stmt, mode):
            continue
        calls = [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]
        effects = [n for n in calls if isinstance(n.func, ast.Attribute)
                   and n.func.attr in ('_materialize', 'execute')]
        if effects:
            if len(effects) != 1 or isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try)):
                raise ValueError('unsupported conditional or nested effect')
            if code in ('new_id, result = self._materialize(old.sql, old.preview, admitted=True)',
                        'new_id, result = self._materialize(old.sql, old.preview, admitted=True, source=old)'):
                body.append('materialize')
            elif code in ("self._connection.execute(f'DROP TABLE workbench_results.{quote_identifier(old.table_name)}')",
                          'self._connection.execute(f"DROP TABLE workbench_results.{quote_identifier(f\'query_{old_id}\')}")'):
                body.append('drop')
            elif code == "self._connection.execute(f'ALTER TABLE workbench_results.{quote_identifier(result.table_name)} RENAME TO {quote_identifier(old.table_name)}')":
                if renamed:
                    raise ValueError('replacement table identity changed before bind')
                body.append('bind')
            else:
                raise ValueError('unsupported SQL or materialization effect: ' + code)
        elif isinstance(stmt, ast.If):
            guards = ('if old.table_name.lower() not in retained:\n    continue', 'if old.table_name.lower() not in retained or old.released:\n    continue')
            if body or retained or mode != 2 or code not in guards:
                raise ValueError('unsupported rebuild branch')
            retained, skip_released = True, code == guards[1]
        elif isinstance(stmt, (ast.For, ast.While, ast.Try, ast.With, ast.Match, ast.Break, ast.Continue, ast.Return, ast.Raise)):
            raise ValueError('unsupported rebuild control flow')
        elif code == 'result.table_name = old.table_name':
            renamed = True
        elif code not in ("affected_tables.add(f'workbench_results.{old.table_name}')",
                          'old = self._results[old_id]',
                          'result.created_at, result.pinned = (old.created_at, old.pinned)',
                          'result.created_at, result.pinned, result.released = (old.created_at, old.pinned, old.released)',
                          'affected_tables.add(old.table_name)',
                          'result.table_name = old.table_name', 'staged[old_id] = (new_id, result)'):
            raise ValueError('unsupported rebuild statement: ' + code)
    if mode == 2 and not retained:
        raise ValueError('missing retention guard')
    return body, skip_released


def validate_events(events, order, skipped):
    for i in range(len(order)):
        own = [event for event, query in events if query == i]
        if own.count('materialize') != (0 if i in skipped else 1) or own.count('drop') > 1 or own.count('bind') > 1:
            raise ValueError('unsupported effect order: ' + repr(own))
        if 'bind' in own and ('drop' not in own or own.index('bind') < own.index('materialize') or own.index('bind') < own.index('drop')):
            raise ValueError('unsupported effect order: ' + repr(own))


def expand_helper(tree, method):
    owners = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and method in n.body]
    if len(owners) != 1:
        raise ValueError('expected one rebuild owner')
    owner = owners[0]
    name = '_stage_result_replacement'
    calls = [n for n in ast.walk(method) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == name]
    if not calls:
        return
    helpers = [n for n in owner.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    overrides = [n for n in ast.walk(tree) if isinstance(n, (ast.Attribute, ast.Name))
                 and isinstance(n.ctx, (ast.Store, ast.Del)) and getattr(n, 'attr', getattr(n, 'id', None)) == name]
    definitions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    dynamic = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id in ('setattr', 'delattr') and any(isinstance(a, ast.Constant) and a.value == name for a in n.args)]
    if len(calls) != 1 or len(helpers) != 1 or len(definitions) != 1 or overrides or dynamic or owner.decorator_list:
        raise ValueError('unsupported helper binding')
    helper = helpers[0]
    a = helper.args
    if (not isinstance(helper, ast.FunctionDef) or helper.decorator_list or
            [arg.arg for arg in a.args] != ['self', 'old'] or a.posonlyargs or a.kwonlyargs or
            a.vararg or a.kwarg or a.defaults or a.kw_defaults or not helper.body or
            ast.unparse(helper.body[-1]) != 'return (new_id, result)'):
        raise ValueError('unsupported helper signature or return')
    names = {n.id for stmt in helper.body for n in ast.walk(stmt) if isinstance(n, ast.Name)}
    if names - {'self', 'old', 'new_id', 'result', 'quote_identifier'}:
        raise ValueError('unsupported helper name binding')
    call_code = 'new_id, result = self._stage_result_replacement(old)'
    for loop in (n for n in method.body if isinstance(n, ast.For)):
        for i, stmt in enumerate(loop.body):
            if ast.unparse(stmt) == call_code:
                loop.body[i:i + 1] = helper.body[:-1]
                return
    raise ValueError('unsupported helper call or binding')


def builtin_reversed(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == 'reversed' and not isinstance(node.ctx, ast.Load):
            return False
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == 'reversed':
            return False
        if isinstance(node, ast.arg) and node.arg == 'reversed':
            return False
        if isinstance(node, ast.alias) and (node.name == '*' or (node.asname or node.name.split('.')[0]) == 'reversed'):
            return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('exec', 'globals', 'locals'):
            return False
    return True


def skipped_results(skip_released, loops, order, released):
    if skip_released and len(loops) != 1:
        raise ValueError('unsupported released selection across loops')
    return {i for i, query in enumerate(order) if skip_released and query in released}


def extract(method, order, tree, released):
    events, loops = [], [n for n in method.body if isinstance(n, ast.For)]
    setup = [ast.unparse(stmt) for stmt in method.body if not isinstance(stmt, ast.For)
             and not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                      and isinstance(stmt.value.value, str))]
    valid_setup = [
        ["if query_id is not None and query_id not in self._results:\n    raise ValueError('unknown query_id')",
         'selected = list(self._results) if query_id is None else [query_id]', 'staged = {}', 'return staged'],
        ['selected = None if query_id is None else {self.resolve_result_selector(query_id)}', 'affected_tables: set[str] = set()', 'staged = {}', 'return staged'],
        ['selected = self.resolve_result_selector(query_id) if query_id is not None else None', 'retained = self._retained_result_tables(expire=True)',
         "if selected is not None and self._results[selected].table_name.lower() not in retained:\n    raise ValueError('unknown query_id')",
         "affected_tables = {name.rsplit('.', 1)[-1].lower() for name in tables or ()}", 'staged = {}', 'return staged'],
        ['staged = {}', 'return staged'],
    ]
    if (not loops or not isinstance(method.body[-1], ast.Return) or
            any(not isinstance(x, ast.For) for x in method.body[method.body.index(loops[0]):-1])):
        raise ValueError('unsupported rebuild control flow')
    if setup not in valid_setup:
        raise ValueError('unsupported rebuild setup or control flow')
    if setup == valid_setup[3] and (len(loops) != 1 or len(method.args.args) != 1 or method.args.posonlyargs or method.args.kwonlyargs or method.args.vararg or method.args.kwarg):
        raise ValueError('unsupported full rebuild signature')
    for loop in loops:
        if (ast.unparse(loop.target), ast.unparse(loop.iter)) not in (('old_id', 'selected'), ('(old_id, old)', 'self._results.items()'), ('(old_id, old)', 'reversed(self._results.items())')) or loop.orelse:
            raise ValueError('unsupported rebuild loop')
        reverse = ast.unparse(loop.iter) == 'reversed(self._results.items())'
        if reverse and not builtin_reversed(tree):
            raise ValueError('unsupported reversed binding')
        body, skip_released = loop_effects(loop, valid_setup.index(setup))
        skipped = skipped_results(skip_released, loops, order, released)
        codes = [ast.unparse(stmt) for stmt in loop.body]
        old_loop = ast.unparse(loop.target) == 'old_id'
        if old_loop != (setup == valid_setup[0]):
            raise ValueError('unsupported rebuild iteration binding')
        if old_loop and any('quote_identifier(old.table_name)' in code for code in codes):
            raise ValueError('unsupported table identity binding')
        if not old_loop and any("f'query_{old_id}'" in code for code in codes):
            raise ValueError('unsupported table identity binding')
        if 'bind' in body and 'materialize' not in body:
            raise ValueError('unsupported replacement binding across loops')
        if ast.unparse(loop.target) == 'old_id' and 'materialize' in body:
            if 'old = self._results[old_id]' not in codes or codes.index('old = self._results[old_id]') > codes.index('new_id, result = self._materialize(old.sql, old.preview, admitted=True)'):
                raise ValueError('unsupported result identity binding')
        events.extend((event, i) for i in (reversed(range(len(order))) if reverse else range(len(order))) if i not in skipped for event in body)
    validate_events(events, order, skipped)
    return events


def check(events, order, edges):
    root = next(p for p in Path(__file__).resolve().parents if (p / '_anechoic_anechoic').is_dir())
    solution = root / '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/_SWD/AN-S-1363-SWD--keep-duckdb-projection-ownership-in-the-existing-server.md'
    match = re.search(r'### Formal Claim\s+.*?```lean\n(.*?)```', solution.read_text(), re.DOTALL)
    if not match or 'namespace SavedQueryRebuild' not in match.group(1):
        raise ValueError('saved-query formal claim not found')
    source = match.group(1) + '\nopen SavedQueryRebuild\n'
    source += 'def extractedEvents : List Effect := [' + ', '.join(f'.{e} {i}' for e, i in events) + ']\n'
    for a, b in edges:
        source += f'#eval readsFresh extractedEvents {order.index(a)} {order.index(b)}\n'
    if args.emit:
        args.emit.write_text(source)
    with tempfile.TemporaryDirectory() as tmp:
        leanfile = Path(tmp) / 'check.lean'
        leanfile.write_text(source)
        run = subprocess.run([args.lean, str(leanfile)], capture_output=True, text=True, timeout=45)
    lines = run.stdout.splitlines()
    if run.returncode or len(lines) != len(edges) or any(x not in ('true', 'false') for x in lines):
        raise ValueError('Lean failed: ' + run.stderr + run.stdout)
    return [edge for edge, value in zip(edges, lines) if value == 'false']


seen = 0
try:
    order, edges, released = graph()
    checkout = args.checkout.resolve()
    if args.file:
        if args.file.is_absolute():
            raise ValueError('source file must be checkout-relative')
        path = (checkout / args.file).resolve()
        if not path.is_relative_to(checkout) or not path.is_file():
            raise ValueError('source file must be inside checkout')
        paths = [path]
    else:
        roots = [root for layer in checkout.glob('LAYER_*') if layer.is_dir()
                 for root in layer.rglob('FEATURE_WORKBENCH_BACKEND')]
        paths = [p for root in roots for p in root.rglob('query_store.py')]
        paths += list(checkout.glob('LAYER_*/KERNEL_MIXER_C59/query_results.py'))
        if len(paths) != 1:
            raise ValueError('expected one rebuild source')
    for path in paths:
        rel = str(path.relative_to(checkout))
        try:
            text = path.read_text()
            if not all(term in text for term in ('prepare_result_rebuild', '_materialize', 'workbench_results')):
                continue
            tree = ast.parse(text)
            methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'prepare_result_rebuild']
            if not methods:
                continue
            if len(methods) != 1:
                raise ValueError('expected one rebuild method')
            expand_helper(tree, methods[0])
            failed = check(extract(methods[0], order, tree, released), order, edges)
            seen += 1
            for a, b in failed:
                result['findings'].append({'path': rel, 'detail': f'The dependent saved query {b} reads {a} before its replacement is bound to its stable table.'})
        except (OSError, SyntaxError, ValueError, subprocess.TimeoutExpired) as error:
            result['unresolved'].append({'path': rel, 'detail': str(error)})
    if not seen and not result['unresolved']:
        result['unresolved'].append({'path': '.', 'detail': 'rebuild source not found'})
except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
    result['unresolved'].append({'path': '.', 'detail': str(error)})
print(json.dumps(result))
