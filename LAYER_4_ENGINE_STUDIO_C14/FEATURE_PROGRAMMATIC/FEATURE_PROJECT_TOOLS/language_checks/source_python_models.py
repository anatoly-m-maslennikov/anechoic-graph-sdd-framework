"""Identify recognizable non-Pydantic structured model declarations."""

import ast

from ._python_model_shapes import (
    RECORD_METHODS as RECORD_METHODS,
    _dictionary_fields,
    _dictionary_record,
    _exemptions,
    _literal_tags,
    _name,
    _named_fields,
    _plain_record,
    _union_types,
)


FORBIDDEN = {
    "dataclasses.dataclass",
    "dataclasses.make_dataclass",
    "typing.TypedDict",
    "typing.NamedTuple",
    "typing_extensions.TypedDict",
    "typing_extensions.NamedTuple",
    "collections.namedtuple",
}
FACTORIES = FORBIDDEN - {"dataclasses.dataclass"}

NAMESPACE_EXEMPTION = "# pragma: anechoic-model-adapter - "
DICTIONARY_REVIEW = "possible dictionary record"
JSON_REVIEW = "Pydantic model_validate after json.loads"
BATCH_REVIEW = "Pydantic TypeAdapter constructed in a loop"
ADVISORY_FINDINGS = {DICTIONARY_REVIEW, JSON_REVIEW, BATCH_REVIEW}


class _ModelVisitor(ast.NodeVisitor):
    def __init__(self, path, source):
        self.path = path
        self.bindings = {}
        self.findings = []
        self.namespace_exemptions = _exemptions(source, NAMESPACE_EXEMPTION)
        self.dictionary_literals = {}
        self.model_tags = {}
        self.in_loop = False

    def report(self, node, name):
        self.findings.append(
            (node.lineno, f"{self.path}:{node.lineno}: {name}")
        )

    def visit_Import(self, node):
        for alias in node.names:
            key = alias.asname or alias.name.split(".")[0]
            self.bindings[key] = alias.name if alias.asname else key

    def visit_ImportFrom(self, node):
        if node.level or not node.module:
            return
        for alias in node.names:
            if alias.name != "*":
                self.bindings[alias.asname or alias.name] = (
                    f"{node.module}.{alias.name}"
                )

    def visit_ClassDef(self, node):
        if _plain_record(node, self.bindings):
            self.report(node, "plain class record")
        for decorator in node.decorator_list:
            target = (
                decorator.func
                if isinstance(decorator, ast.Call)
                else decorator
            )
            if _name(target, self.bindings) == "dataclasses.dataclass":
                self.report(decorator, "dataclasses.dataclass")
        for base in node.bases:
            name = _name(base, self.bindings)
            if name in FACTORIES:
                self.report(base, name)
        self._scope(node)
        self.bindings.pop(node.name, None)
        self.dictionary_literals.pop(node.name, None)
        self.model_tags.pop(node.name, None)
        if any(
            _name(base, self.bindings) == "pydantic.BaseModel"
            or isinstance(base, ast.Name)
            and base.id in self.model_tags
            for base in node.bases
        ):
            self.model_tags[node.name] = _literal_tags(node, self.bindings)

    def _scope(self, node):
        outer = self.bindings
        dictionaries = self.dictionary_literals
        tags, in_loop = self.model_tags, self.in_loop
        self.bindings = outer.copy()
        self.dictionary_literals = {}
        self.model_tags, self.in_loop = tags.copy(), False
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            for arg in [
                *args.posonlyargs,
                *args.args,
                *args.kwonlyargs,
                args.vararg,
                args.kwarg,
            ]:
                if arg is not None:
                    self.bindings.pop(arg.arg, None)
        for item in node.body:
            self.visit(item)
        self.bindings = outer
        self.dictionary_literals = dictionaries
        self.model_tags, self.in_loop = tags, in_loop

    def visit_FunctionDef(self, node):
        self._scope(node)
        self.bindings.pop(node.name, None)
        self.dictionary_literals.pop(node.name, None)
        self.model_tags.pop(node.name, None)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        name = _name(node.func, self.bindings)
        if name in FORBIDDEN:
            self.report(node, name)
        if (
            name == "types.SimpleNamespace"
            and node.lineno not in self.namespace_exemptions
        ):
            keys = self._namespace_fields(node)
            if _named_fields(keys):
                self.report(node, "types.SimpleNamespace record")
        if name == "pydantic.TypeAdapter" and self.in_loop:
            self.report(node, BATCH_REVIEW)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "model_validate"
            and len(node.args) == 1
        ):
            value = node.args[0]
            if (
                isinstance(value, ast.Call)
                and _name(value.func, self.bindings) == "json.loads"
                and len(value.args) == 1
                and not value.keywords
            ):
                self.report(node, JSON_REVIEW)
        self.generic_visit(node)

    def _visit_loop(self, body, after):
        previous = self.in_loop
        self.in_loop = True
        for item in body:
            self.visit(item)
        self.in_loop = previous
        for item in after:
            self.visit(item)

    def visit_For(self, node):
        self.visit(node.iter)
        self._unbind(node.target)
        self._visit_loop(node.body, node.orelse)

    visit_AsyncFor = visit_For

    def visit_While(self, node):
        self._visit_loop((node.test, *node.body), node.orelse)

    def _namespace_fields(self, node):
        keys = (
            _dictionary_fields(node.args[0], self.bindings)
            if len(node.args) == 1
            else []
        )
        for keyword in node.keywords:
            if keyword.arg is None:
                keys.extend(_dictionary_fields(keyword.value, self.bindings))
            else:
                keys.append(keyword.arg)
        return keys

    def visit_Assign(self, node):
        self.visit(node.value)
        self._check_union(node.value)
        for target in node.targets:
            self._unbind(target)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            keys = _dictionary_fields(node.value, self.bindings)
            if _named_fields(keys):
                self.dictionary_literals[node.targets[0].id] = (
                    node,
                    set(keys),
                    set(),
                )

    def visit_AnnAssign(self, node):
        self._check_union(node.annotation, node.value)
        if node.value:
            self.visit(node.value)
            if _name(node.annotation, self.bindings) in {
                "typing.TypeAlias",
                "typing_extensions.TypeAlias",
            }:
                self._check_union(node.value)
        if isinstance(node.target, ast.Name) and _dictionary_record(
            node, self.bindings
        ):
            self.report(node, DICTIONARY_REVIEW)
        self._unbind(node.target)

    def visit_TypeAlias(self, node):
        self._check_union(node.value)
        self._unbind(node.name)

    def _check_union(self, node, field=None):
        if (
            isinstance(field, ast.Call)
            and _name(field.func, self.bindings) == "pydantic.Field"
            and any(
                keyword.arg == "discriminator"
                and not (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is None
                )
                for keyword in field.keywords
            )
        ):
            return
        variants = _union_types(node, self.bindings)
        if len(variants) < 2 or any(
            not isinstance(v, ast.Name) or v.id not in self.model_tags
            for v in variants
        ):
            return
        tags = [self.model_tags[variant.id] for variant in variants]
        if any(
            len({fields.get(key) for fields in tags}) == len(tags)
            and all(key in fields for fields in tags)
            for key in tags[0]
        ):
            self.report(node, "Pydantic model union needs a discriminator")

    def visit_Subscript(self, node):
        if (
            isinstance(node.value, ast.Name)
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            name, field = node.value.id, node.slice.value
            if (candidate := self.dictionary_literals.get(name)) is not None:
                declaration, keys, used = candidate
                if field in keys:
                    used.add(field)
                    if len(used) == 2:
                        self.report(declaration, DICTIONARY_REVIEW)
                        del self.dictionary_literals[name]
        self.generic_visit(node)

    def _unbind(self, target):
        if isinstance(target, ast.Name):
            self.bindings.pop(target.id, None)
            self.dictionary_literals.pop(target.id, None)
            self.model_tags.pop(target.id, None)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self._unbind(item)


def python_model_findings(relative_path, source):
    """Return sorted findings; propagate syntax errors with the source path."""
    tree = ast.parse(source, filename=str(relative_path))
    visitor = _ModelVisitor(relative_path, source)
    visitor.visit(tree)
    return [message for _, message in sorted(visitor.findings)]
