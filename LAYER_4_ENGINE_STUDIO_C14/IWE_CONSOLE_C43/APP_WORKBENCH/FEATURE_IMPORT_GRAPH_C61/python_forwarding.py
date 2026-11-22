"""Find direct module-level import bindings without inferring assignments."""

import ast
from collections import Counter


class _Bindings(ast.NodeVisitor):
    def __init__(self):
        self.names = Counter()
        self.wildcard = False

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names[node.id] += 1

    def visit_Import(self, node):
        for alias in node.names:
            self.names[alias.asname or alias.name.split(".")[0]] += 1

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == "*":
                self.wildcard = True
            else:
                self.names[alias.asname or alias.name] += 1

    def visit_FunctionDef(self, node):
        self.names[node.name] += 1
        for child in ast.walk(node):
            if isinstance(child, ast.Global):
                self.names.update(child.names)
        for expression in (*node.decorator_list, *node.args.defaults, *filter(None, node.args.kw_defaults)):
            self.visit(expression)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.names[node.name] += 1
        for expression in (*node.decorator_list, *node.bases, *(item.value for item in node.keywords)):
            self.visit(expression)

    def visit_ExceptHandler(self, node):
        if node.name:
            self.names[node.name] += 1
        self.generic_visit(node)

    def visit_MatchAs(self, node):
        if node.name:
            self.names[node.name] += 1
        self.generic_visit(node)

    def visit_MatchStar(self, node):
        if node.name:
            self.names[node.name] += 1

    def visit_MatchMapping(self, node):
        if node.rest:
            self.names[node.rest] += 1
        self.generic_visit(node)


def python_forwarded(tree):
    """Return only unambiguous direct imports at module scope."""
    bindings = _Bindings()
    bindings.visit(tree)
    if bindings.wildcard:
        return ()
    return tuple(
        (alias.asname or alias.name, alias.name, node.lineno, node.col_offset)
        for node in tree.body if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if alias.name != "*" and bindings.names[alias.asname or alias.name] == 1
    )
