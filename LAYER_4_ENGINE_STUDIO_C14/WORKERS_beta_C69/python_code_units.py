"""Extract Python definitions and conservatively resolved static calls."""

import ast
from collections import Counter
from pathlib import PurePosixPath


def _collect(path, body, units, definitions, prefix=(), in_class=False):
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = 'class' if isinstance(node, ast.ClassDef) else ('method' if in_class else 'function')
            name = '.'.join((*prefix, node.name))
            key = f'code_unit:{path}:{node.lineno}:{node.col_offset}'
            units.append((key, f'module:{path}', kind, name, node.lineno, node.col_offset))
            definitions[id(node)] = key
            _collect(path, node.body, units, definitions, (*prefix, node.name), isinstance(node, ast.ClassDef))
        else:
            # Definitions under control flow are still useful units, but are
            # never treated as guaranteed bindings.
            for field in ('body', 'orelse', 'finalbody'):
                value = getattr(node, field, None)
                if isinstance(value, list):
                    _collect(path, value, units, definitions, prefix, in_class)
            for handler in getattr(node, 'handlers', []):
                _collect(path, handler.body, units, definitions, prefix, in_class)
            for case in getattr(node, 'cases', []):
                _collect(path, case.body, units, definitions, prefix, in_class)

class _Bindings(ast.NodeVisitor):
    def __init__(self):
        self.counts = Counter()
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.counts[node.id] += 1
    def visit_FunctionDef(self, node):
        self.counts[node.name] += 1
    visit_AsyncFunctionDef = visit_FunctionDef
    def visit_ClassDef(self, node):
        self.counts[node.name] += 1
    def visit_Import(self, node):
        for alias in node.names:
            self.counts[alias.asname or alias.name.split('.')[0]] += 1
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.counts[alias.asname or alias.name] += 1
    def visit_Lambda(self, node):
        pass
    def visit_Global(self, node):
        for name in node.names:
            self.counts[name] += 1
    visit_Nonlocal = visit_Global
    def visit_MatchAs(self, node):
        if node.name:
            self.counts[node.name] += 1
        self.generic_visit(node)
    def visit_MatchStar(self, node):
        if node.name:
            self.counts[node.name] += 1
    def visit_MatchMapping(self, node):
        if node.rest:
            self.counts[node.rest] += 1
        self.generic_visit(node)
    def visit_ExceptHandler(self, node):
        if node.name:
            self.counts[node.name] += 1
        self.generic_visit(node)

def _bindings(body, args=None):
    visitor = _Bindings()
    for node in body:
        visitor.visit(node)
    if args:
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
            visitor.counts[arg.arg] += 1
        for arg in (args.vararg, args.kwarg):
            if arg:
                visitor.counts[arg.arg] += 1
    return visitor.counts


def _resolve(expr, scopes, module_symbols, class_symbols):
    if isinstance(expr, ast.Name):
        for scope in scopes:
            if expr.id in scope:
                return scope[expr.id]
    if isinstance(expr, ast.Attribute):
        base = _resolve(expr.value, scopes, module_symbols, class_symbols)
        if base and base[0] == 'module_chain' and base[1][0] == expr.attr:
            return (('module_chain', base[1][1:], base[2]) if len(base[1]) > 1
                    else ('module', base[2]))
        if base and base[0] == 'module':
            return module_symbols[base[1]].get(expr.attr)
        if base and base[0] == 'class':
            return class_symbols.get(id(base[2]), {}).get(expr.attr)
    return None


class _Calls(ast.NodeVisitor):
    def __init__(self, path, module_symbols, class_symbols, definitions, calls):
        self.path = path
        self.module_symbols = module_symbols
        self.class_symbols = class_symbols
        self.definitions = definitions
        self.calls = calls
        self.scopes = [module_symbols[path]]
        self.source = None
    def visit_Call(self, node):
        if self.source:
            target = _resolve(node.func, self.scopes, self.module_symbols, self.class_symbols)
            if target and target[0] == 'unit':
                self.calls.append((self.source, target[1], node.lineno, node.col_offset))
        self.generic_visit(node)
    def function(self, node):
        old_source, old_scopes = self.source, self.scopes
        local_counts = _bindings(node.body, node.args)
        # Nested nonlocal declarations may rebind a closure's definitions.
        for child in ast.walk(node):
            if isinstance(child, ast.Nonlocal):
                local_counts.update(child.names)
        local = {name: None for name in local_counts}
        # Nested definitions are available only if uniquely bound and plain.
        for child in node.body:
            if (isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and local_counts[child.name] == 1 and not child.decorator_list):
                local[child.name] = ('unit', self.definitions[id(child)])
        self.scopes = [local, *old_scopes]
        self.source = self.definitions[id(node)]
        for child in node.body:
            self.visit(child)
        self.source, self.scopes = old_source, old_scopes
    visit_FunctionDef = function
    visit_AsyncFunctionDef = function
    def visit_ClassDef(self, node):
        # Class bodies do not form a lexical scope for method bodies.
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.visit(child)
    def visit_Lambda(self, node):
        pass


def _static_members(node, counts, definitions):
    members = {}
    class_counts = _bindings(node.body)
    for member in node.body:
        if (isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                and class_counts[member.name] == 1
                and len(member.decorator_list) == 1
                and isinstance(member.decorator_list[0], ast.Name)
                and member.decorator_list[0].id == 'staticmethod'
                and counts['staticmethod'] == 0):
            members[member.name] = ('unit', definitions[id(member)])
    return members


def _authored_symbols(trees, definitions):
    modules, classes = {}, {}
    for path, tree in trees.items():
        counts = _bindings(tree.body)
        symbols = {}
        for node in tree.body:
            if counts.get(getattr(node, 'name', None)) != 1:
                continue
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.decorator_list:
                symbols[node.name] = ('unit', definitions[id(node)])
            elif isinstance(node, ast.ClassDef) and not node.decorator_list and not node.bases and not node.keywords:
                symbols[node.name] = ('class', path, node)
                classes[id(node)] = _static_members(node, counts, definitions)
        modules[path] = symbols
    return modules, classes


def _remove_mutated_symbols(trees, modules, classes):
    changed_attrs = {node.attr for tree in trees.values() for node in ast.walk(tree)
                     if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del))}
    for symbols in classes.values():
        for name in changed_attrs:
            symbols.pop(name, None)
    for path, tree in trees.items():
        changed_globals = {name for node in ast.walk(tree) if isinstance(node, ast.Global)
                           for name in node.names}
        for name in changed_globals | changed_attrs:
            modules[path].pop(name, None)


def _import_from(node, path, counts, imports, authored, symbols):
    written = '.' * node.level + (node.module or '')
    target = imports.get(path, {}).get((node.lineno, written))
    for alias in node.names:
        local = alias.asname or alias.name
        if counts[local] != 1 or alias.name == '*' or target not in authored:
            continue
        child = tuple((node.module or '').split('.')) if node.module else ()
        child = (*child, alias.name + '.py')
        is_child = PurePosixPath(target).parts[-len(child):] == child
        value = ('module', target) if is_child else authored[target].get(alias.name)
        if value:
            symbols[local] = value


def _import_modules(node, path, counts, imports, trees, symbols):
    for alias in node.names:
        local = alias.asname or alias.name.split('.')[0]
        target = imports.get(path, {}).get((node.lineno, alias.name))
        if counts[local] == 1 and target in trees:
            parts = alias.name.split('.')
            symbols[local] = (('module', target) if alias.asname or len(parts) == 1
                              else ('module_chain', tuple(parts[1:]), target))


def _resolve_imports(trees, imports, modules):
    authored = {path: symbols.copy() for path, symbols in modules.items()}
    for path, tree in trees.items():
        counts = _bindings(tree.body)
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                counts.update(node.names)
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                _import_from(node, path, counts, imports, authored, modules[path])
            elif isinstance(node, ast.Import):
                _import_modules(node, path, counts, imports, trees, modules[path])


def python_code_units(texts, imports):
    """Return definitions and conservatively resolved calls from Python text."""
    trees = {}
    for path, text in texts.items():
        try:
            trees[path] = ast.parse(text, filename=path)
        except (SyntaxError, ValueError):
            continue
    units, calls, definitions = [], [], {}
    for path, tree in trees.items():
        _collect(path, tree.body, units, definitions)
    modules, classes = _authored_symbols(trees, definitions)
    _remove_mutated_symbols(trees, modules, classes)
    _resolve_imports(trees, imports, modules)
    for path, tree in trees.items():
        _Calls(path, modules, classes, definitions, calls).visit(tree)
    return units, calls
