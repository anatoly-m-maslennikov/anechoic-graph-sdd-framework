"""Conservative evidence for Python imports during module initialization."""

import ast
from collections import defaultdict


def _binding(node):
    # Evaluate only definitions whose creation cannot run arbitrary Python.
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = node.args
        if not node.decorator_list and not node.returns and not args.defaults and not any(args.kw_defaults) and not any(a.annotation for a in (*args.posonlyargs, *args.args, *args.kwonlyargs, *([args.vararg] if args.vararg else []), *([args.kwarg] if args.kwarg else []))):
            return {node.name}
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if all(isinstance(t, ast.Name) for t in targets) and value is not None:
            try:
                ast.literal_eval(value)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                pass
            else:
                # Annotations can execute arbitrary expressions.
                if not isinstance(node, ast.AnnAssign):
                    return {t.id for t in targets}
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        return set()
    if isinstance(node, ast.Pass):
        return set()
    return None


def _capture(texts, occurrences):
    trees = {}
    for path, text in texts.items():
        try:
            tree = ast.parse(text, filename=path)
            compile(tree, path, 'exec')
            trees[path] = tree
        except (SyntaxError, ValueError, RecursionError):
            continue
    sites, graph = defaultdict(list), defaultdict(set)
    for _, source, target, written, line, column, status, type_only in occurrences:
        if type_only or status != 'internal' or not source.startswith('module:') or not target or not target.startswith('module:'):
            continue
        src, dst = source[7:], target[7:]
        if src in trees and dst in trees:
            sites[src, line, column].append((dst, written))
            graph[src].add(dst)
    return trees, sites, graph


def _target(node, path, sites):
    candidates = sites.get((path, node.lineno, node.col_offset), [])
    if len(node.names) != 1 or len(candidates) != 1 or node.names[0].name == '*':
        return None
    dest, written = candidates[0]
    if isinstance(node, ast.ImportFrom):
        base = written.lstrip('.').replace('.', '/')
        if not base or not (dest.endswith('/' + base + '.py') or dest == base + '.py'):
            return None
    return dest


class _Traversal:
    def __init__(self, entry, trees, sites, confirmed_edges):
        self.entry, self.trees, self.sites = entry, trees, sites
        self.confirmed_edges = confirmed_edges
        self.active, self.bound, self.stack = set(), {}, []

    def _witness(self, path, dest, node, edge):
        alias = node.names[0]
        if not isinstance(node, ast.ImportFrom) or alias.name in self.bound[dest]:
            return None
        after = next((e[2] for e in self.stack if e[0] == dest), node.lineno)
        later = [n for n in self.trees[dest].body if n.lineno > after and alias.name in (_binding(n) or set())]
        hooks = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == '__getattr__' for n in self.trees[dest].body)
        if not later or hooks:
            return None
        witness = self.stack + [edge]
        detail = 'entry ' + self.entry + ': ' + ' -> '.join(f'{a}:{line} imports {b}' for a, b, line, _ in witness) + f'; reads {alias.name} before {dest}:{later[0].lineno} binds it'
        self.confirmed_edges.update((a, b) for a, b, _, _ in witness)
        return (path, node.lineno, node.col_offset, 'python_import_order', 'confirmed', detail)

    def visit(self, path):
        # Package initializers can execute before the captured module.
        if '/' in path or path.endswith('__init__.py') or len(self.stack) >= 64 or path in self.active:
            return None
        self.active.add(path)
        self.bound[path] = set()
        for node in self.trees[path].body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                dest = _target(node, path, self.sites)
                if dest is None:
                    break
                edge = (path, dest, node.lineno, node.col_offset)
                if dest in self.active:
                    return self._witness(path, dest, node, edge)
                self.stack.append(edge)
                result = self.visit(dest)
                self.stack.pop()
                if result:
                    return result
                break
            names = _binding(node)
            if names is None:
                break
            self.bound[path].update(names)
        self.active.remove(path)
        return None


def _reaches(graph, start, goal):
    pending, seen = [start], set()
    while pending:
        node = pending.pop()
        if node == goal:
            return True
        if node not in seen:
            seen.add(node)
            pending.extend(graph[node] - seen)
    return False


def python_import_order(texts, occurrences):
    """Return witnessed failures and unresolved structural cycles, without executing code."""
    trees, sites, graph = _capture(texts, occurrences)
    results, confirmed_edges = [], set()
    for entry in sorted(trees):
        result = _Traversal(entry, trees, sites, confirmed_edges).visit(entry)
        if result and result not in results:
            results.append(result)
    for (src, line, column), candidates in sorted(sites.items()):
        for dst, _ in sorted(set(candidates)):
            if (src, dst) not in confirmed_edges and _reaches(graph, dst, src):
                results.append((src, line, column, 'python_import_order', 'unresolved',
                                f'structural cycle includes {src}:{line} imports {dst}; execution order or premature read not established'))
    return results
