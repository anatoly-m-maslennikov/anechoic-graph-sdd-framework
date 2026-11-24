"""Lower a deliberately small Python subset to ordered action-effect events."""

import ast
from collections import Counter
from itertools import product


_REGISTRIES = {'os.environ': 'ENV', 'sys.modules': 'SYS_MODULES'}


def _module_bindings(tree):
    counts = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            counts[node.id] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            counts.update(a.asname or (a.name.split('.')[0] if isinstance(node, ast.Import) else a.name)
                          for a in node.names)
    imports = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                if counts[name] == 1 and alias.name in ('contextvars', 'threading', 'os', 'sys'):
                    imports[name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module in ('contextvars', 'threading', 'os', 'sys'):
            for alias in node.names:
                name = alias.asname or alias.name
                if counts[name] == 1:
                    imports[name] = node.module + '.' + alias.name
    channels = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if not isinstance(target, ast.Name) or counts[target.id] != 1 or not isinstance(value, ast.Call):
            continue
        constructor = _qualified(value.func, imports)
        if (constructor == 'contextvars.ContextVar' and len(value.args) == 1
                and isinstance(value.args[0], ast.Constant) and isinstance(value.args[0].value, str)
                and value.args[0].value and all(
                    kw.arg == 'default' and isinstance(kw.value, ast.Constant) for kw in value.keywords)):
            channels[target.id] = ('context', value.args[0].value)
        elif constructor == 'threading.local' and not value.args and not value.keywords:
            channels[target.id] = ('thread', 'threading.local:' + target.id)
    return imports, channels


def _env_key(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(node.value) and '=' not in node.value and '\x00' not in node.value


def _qualified(node, imports):
    if isinstance(node, ast.Name):
        return imports.get(node.id, '')
    if isinstance(node, ast.Attribute):
        parent = _qualified(node.value, imports)
        return parent + '.' + node.attr if parent else ''
    return ''


class _Lower:
    def __init__(self, imports, channels, owner, shadowed, call_sites=None):
        self.imports, self.channels, self.owner = imports, channels.copy(), owner
        self.shadowed, self.call_sites = shadowed, call_sites
        self.locals, self.globals = set(), set()
        self.tokens, self.booleans = {}, {}
        self.events, self.complete, self.stopped = [], True, False

    def event(self, kind, target, name, node):
        self.events.append(dict(kind=kind, target=target, name=name, line=node.lineno))

    def state(self, node):
        if (self.owner and isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == self.owner and node.attr.startswith('_')
                and not node.attr.startswith('__')):
            return 'local', '$owner'
        if isinstance(node, ast.Name) and node.id in self.globals and node.id.startswith('_'):
            return 'local', '$owner'
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            channel = self.channels.get(node.value.id)
            if channel and channel[0] == 'thread':
                return 'ambient', channel[1]
        if isinstance(node, ast.Subscript) and _env_key(node.slice):
            channel = _REGISTRIES.get(_qualified(node.value, self.imports))
            if channel:
                return 'ambient', channel
        return None

    def expr(self, node):
        state = self.state(node)
        if state:
            self.event('read', *state, node)
        elif isinstance(node, ast.Constant):
            pass
        elif isinstance(node, ast.Name) and node.id in self.locals:
            pass
        elif isinstance(node, (ast.Tuple, ast.List)) or (isinstance(node, ast.Set) and all(isinstance(item, ast.Constant) for item in node.elts)):
            for item in node.elts:
                self.expr(item)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if not isinstance(key, ast.Constant):
                    self.complete = False
                else:
                    self.expr(key)
                self.expr(value)
        elif (isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant) and isinstance(node.op, (ast.Not, ast.UAdd, ast.USub, ast.Invert))):
            self.expr(node.operand)
        elif isinstance(node, ast.Call):
            self.call(node)
        else:
            self.complete = False

    def call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print' and 'print' not in self.shadowed and not node.keywords:
            for arg in node.args:
                self.expr(arg)
            self.event('output', '', '', node)
            return
        if not isinstance(node.func, ast.Attribute) or node.keywords:
            self.complete = False
            return
        base, method = node.func.value, node.func.attr
        channel = self.channels.get(base.id) if isinstance(base, ast.Name) else None
        registry = _REGISTRIES.get(_qualified(base, self.imports))
        allowed = {'get': ('read', (0, 1)), 'set': ('write', (1,)), 'reset': ('write', (1,))}
        if channel and channel[0] == 'context' and method in allowed:
            kind, arities = allowed[method]
            if len(node.args) in arities:
                if method == 'reset':
                    token = node.args[0]
                    if not isinstance(token, ast.Name) or self.tokens.pop(token.id, None) != channel:
                        self.complete = False
                        return
                for arg in node.args:
                    self.expr(arg)
                self.event(kind, 'ambient', channel[1], node)
                return
        if (registry and method == 'get' and len(node.args) in (1, 2)
                and _env_key(node.args[0])):
            for arg in node.args:
                self.expr(arg)
            self.event('read', 'ambient', registry, node)
            return
        self.complete = False

    def target(self, node):
        state = self.state(node)
        if state:
            self.event('write', *state, node)
        elif isinstance(node, ast.Name) and node.id not in self.globals:
            self.locals.add(node.id)
            self.booleans.pop(node.id, None)
            self.channels.pop(node.id, None)
            self.tokens.pop(node.id, None)
        else:
            self.complete = False

    def assign(self, node):
        if (isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Name)
                and node.value.id in self.channels and node.targets[0].id not in self.globals):
            self.locals.add(node.targets[0].id)
            self.booleans.pop(node.targets[0].id, None)
            self.channels[node.targets[0].id] = self.channels[node.value.id]
        else:
            self.expr(node.value)
            target = node.targets[0]
            if self.state(target) == ('ambient', 'ENV') and not (
                    isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
                    and '\x00' not in node.value.value):
                self.complete = False
            self.target(target)
            if (isinstance(target, ast.Name) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'set'
                    and isinstance(node.value.func.value, ast.Name)):
                channel = self.channels.get(node.value.func.value.id)
                if channel and channel[0] == 'context':
                    self.tokens[target.id] = channel

    def graph_call(self, node, forward=False):
        if self.call_sites is None or not isinstance(node, ast.Call) or node.args or node.keywords:
            return False
        if isinstance(node.func, ast.Name) and node.func.id == 'print' and 'print' not in self.shadowed:
            return False
        target = self.call_sites.get((node.lineno, node.col_offset))
        if target is None:
            return False
        self.events.append(dict(kind='call', target='', name=target, line=node.lineno, forward=forward))
        return True

    def statement(self, node):
        if isinstance(node, ast.Global):
            self.globals.update(node.names)
        elif isinstance(node, ast.Pass):
            pass
        elif isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id in self.booleans:
            self.block(node.body if self.booleans[node.test.id] else node.orelse)
        elif isinstance(node, ast.Expr):
            if not self.graph_call(node.value):
                self.expr(node.value)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            self.assign(node)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            self.expr(node.value)
            if self.state(node.target) == ('ambient', 'ENV'):
                self.complete = False
            self.target(node.target)
        elif isinstance(node, ast.AugAssign):
            state = self.state(node.target)
            if state and state != ('ambient', 'ENV'):
                self.event('read', *state, node.target)
                self.expr(node.value)
                self.event('write', *state, node.target)
            else:
                self.complete = False
        elif isinstance(node, ast.Return):
            if node.value is not None and not self.graph_call(node.value, forward=True):
                self.expr(node.value)
                self.event('return' if self.call_sites is not None else 'output', '', '', node)
            self.stopped = True
        elif isinstance(node, ast.Raise):
            value = node.exc
            if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                    and value.func.id in ('Exception', 'ValueError', 'TypeError', 'RuntimeError')
                    and value.func.id not in self.shadowed and not value.keywords and node.cause is None):
                for arg in value.args:
                    self.expr(arg)
                self.event('raise' if self.call_sites is not None else 'output', '', '', node)
            else:
                self.complete = False
            self.stopped = True
        else:
            self.complete = False

    def block(self, statements):
        for stmt in statements:
            if self.stopped or not self.complete:
                break
            self.statement(stmt)


def _module_case(tree, imports, channels, shadowed):
    mutable = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name)
               and isinstance(n.value, (ast.Dict, ast.List, ast.Set))]
    if mutable:
        lower = _Lower(imports, channels, None, shadowed)
        for stmt in tree.body:
            if stmt in mutable:
                lower.expr(stmt.value)
                lower.event('write', 'local', '$owner', stmt)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                pass
            elif (isinstance(stmt, ast.FunctionDef) and stmt.name not in {n.targets[0].id for n in mutable}
                  and not stmt.decorator_list
                  and not stmt.args.defaults and not any(stmt.args.kw_defaults)
                  and stmt.returns is None and all(arg.annotation is None for arg in
                      (*stmt.args.posonlyargs, *stmt.args.args, *stmt.args.kwonlyargs))
                  and not stmt.args.vararg and not stmt.args.kwarg):
                pass
            else:
                lower.complete = False
        return dict(action='<module>', line=mutable[0].lineno,
                          input={} if lower.complete else None, reachable=True,
                          complete=lower.complete, declaredNoOp=False,
                          events=lower.events if lower.complete else [])
    return None


def python_state_cases(source: str, call_sites=None) -> list[dict]:
    """Return cases without importing or executing the analyzed source."""
    try:
        tree = ast.parse(source)
        compile(tree, '<state analysis>', 'exec')
    except (SyntaxError, ValueError):
        return [dict(action='<parse_error>', line=1, input=None, reachable=False,
                     complete=False, declaredNoOp=False, events=[])]
    imports, channels = _module_bindings(tree)
    shadowed = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))}
    shadowed.update(n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
    shadowed.update(a.asname or a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,
                    (ast.Import, ast.ImportFrom)) for a in n.names)
    module_case = _module_case(tree, imports, channels, shadowed)
    cases = [module_case] if module_case else []
    if module_case and call_sites is not None:
        module_case.update(column=0, inlineable=False)
    functions = [(node, None, node.name) for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        functions.extend((node, cls, cls.name + '.' + node.name) for node in cls.body
                         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    for node, cls, name in functions:
        args = node.args
        positional = args.posonlyargs + args.args
        owner = positional[0].arg if cls and positional and positional[0].arg == 'self' else None
        params = positional[1:] if owner else positional
        unsupported = (isinstance(node, ast.AsyncFunctionDef) or node.decorator_list or args.vararg or args.kwarg
                or (cls and (cls.bases or cls.keywords or cls.decorator_list or any(
                    isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and
                    (n.decorator_list or n.name in ('__getattribute__', '__setattr__', '__delattr__'))
                    or isinstance(n, (ast.Assign, ast.AnnAssign)) and not isinstance(n.value, ast.Constant)
                    for n in cls.body)))
                or len(params) > 2 or args.kwonlyargs or args.defaults or any(not isinstance(param.annotation, ast.Name) or param.annotation.id != 'bool' for param in params)
                or any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node)))
        params = None if unsupported else [param.arg for param in params]
        cases.extend(_action_cases(name, node, imports, channels, owner, shadowed, params, call_sites, cls is None))
    return cases


def _action_cases(name, node, imports, channels, owner, shadowed, params, call_sites, module_function):
    inputs = [None] if params is None else (dict(zip(params, values)) for values in product((False, True), repeat=len(params)))
    for witness in inputs:
        lower = _Lower(imports, channels, owner, shadowed, call_sites)
        lower.globals.update(name for stmt in ast.walk(node) if isinstance(stmt, ast.Global) for name in stmt.names)
        lower.complete = witness is not None
        lower.booleans.update(witness or {})
        lower.locals.update(witness or {})
        if owner:
            lower.locals.add(owner)
        lower.block(node.body)
        case = dict(action=name, line=node.lineno, input=witness if lower.complete else None,
                    reachable=True, complete=lower.complete, declaredNoOp=False, events=lower.events if lower.complete else [])
        if call_sites is not None:
            case.update(column=node.col_offset, inlineable=lower.complete and not params and module_function)
        yield case
