"""Lower Python expressions and statements to effect events."""

import ast

if __package__:
    from .python_state_bindings import _env_key, _qualified
else:
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    _spec = spec_from_file_location(
        "python_state_bindings",
        Path(__file__).with_name("python_state_bindings.py"),
    )
    _bindings = module_from_spec(_spec)
    _spec.loader.exec_module(_bindings)
    _env_key, _qualified = _bindings._env_key, _bindings._qualified


_REGISTRIES = {"os.environ": "ENV", "sys.modules": "SYS_MODULES"}


class _Lower:
    def __init__(self, imports, channels, owner, shadowed, call_sites=None):
        self.imports, self.channels, self.owner = (
            imports,
            channels.copy(),
            owner,
        )
        self.shadowed, self.call_sites = shadowed, call_sites
        self.locals, self.globals = set(), set()
        self.tokens, self.booleans = {}, {}
        self.events, self.complete, self.stopped = [], True, False

    def event(self, kind, target, name, node):
        self.events.append(
            dict(kind=kind, target=target, name=name, line=node.lineno)
        )

    def state(self, node):
        if (
            self.owner
            and isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == self.owner
            and node.attr.startswith("_")
            and not node.attr.startswith("__")
        ):
            return "local", "$owner"
        if (
            isinstance(node, ast.Name)
            and node.id in self.globals
            and node.id.startswith("_")
        ):
            return "local", "$owner"
        if isinstance(node, ast.Attribute) and isinstance(
            node.value, ast.Name
        ):
            channel = self.channels.get(node.value.id)
            if channel and channel[0] == "thread":
                return "ambient", channel[1]
        if isinstance(node, ast.Subscript) and _env_key(node.slice):
            channel = _REGISTRIES.get(_qualified(node.value, self.imports))
            if channel:
                return "ambient", channel
        return None

    def expr(self, node):
        state = self.state(node)
        if state:
            self.event("read", *state, node)
        elif isinstance(node, ast.Constant) or (
            isinstance(node, ast.Name) and node.id in self.locals
        ):
            pass
        elif isinstance(node, (ast.Tuple, ast.List)) or (
            isinstance(node, ast.Set)
            and all(isinstance(item, ast.Constant) for item in node.elts)
        ):
            for item in node.elts:
                self.expr(item)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if not isinstance(key, ast.Constant):
                    self.complete = False
                else:
                    self.expr(key)
                self.expr(value)
        elif (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.operand, ast.Constant)
            and isinstance(node.op, (ast.Not, ast.UAdd, ast.USub, ast.Invert))
        ):
            self.expr(node.operand)
        elif isinstance(node, ast.Call):
            self.call(node)
        else:
            self.complete = False

    def call(self, node):
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and "print" not in self.shadowed
            and not node.keywords
        ):
            for arg in node.args:
                self.expr(arg)
            self.event("output", "", "", node)
            return
        if not isinstance(node.func, ast.Attribute) or node.keywords:
            self.complete = False
            return
        base, method = node.func.value, node.func.attr
        channel = (
            self.channels.get(base.id) if isinstance(base, ast.Name) else None
        )
        registry = _REGISTRIES.get(_qualified(base, self.imports))
        allowed = {
            "get": ("read", (0, 1)),
            "set": ("write", (1,)),
            "reset": ("write", (1,)),
        }
        if self.context_call(node, channel, method, allowed):
            return
        if (
            registry
            and method == "get"
            and len(node.args) in (1, 2)
            and _env_key(node.args[0])
        ):
            for arg in node.args:
                self.expr(arg)
            self.event("read", "ambient", registry, node)
            return
        self.complete = False

    def context_call(self, node, channel, method, allowed):
        if (
            channel
            and channel[0] == "context"
            and method in allowed
            and len(node.args) in allowed[method][1]
        ):
            kind, _ = allowed[method]
            if method == "reset":
                token = node.args[0]
                if (
                    not isinstance(token, ast.Name)
                    or self.tokens.pop(token.id, None) != channel
                ):
                    self.complete = False
                    return True
            for arg in node.args:
                self.expr(arg)
            self.event(kind, "ambient", channel[1], node)
            return True
        return False

    def target(self, node):
        state = self.state(node)
        if state:
            self.event("write", *state, node)
        elif isinstance(node, ast.Name) and node.id not in self.globals:
            self.locals.add(node.id)
            self.booleans.pop(node.id, None)
            self.channels.pop(node.id, None)
            self.tokens.pop(node.id, None)
        else:
            self.complete = False

    def assign(self, node):
        if (
            isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Name)
            and node.value.id in self.channels
            and node.targets[0].id not in self.globals
        ):
            self.locals.add(node.targets[0].id)
            self.booleans.pop(node.targets[0].id, None)
            self.channels[node.targets[0].id] = self.channels[node.value.id]
        else:
            self.expr(node.value)
            target = node.targets[0]
            if self.state(target) == ("ambient", "ENV") and not (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and "\x00" not in node.value.value
            ):
                self.complete = False
            self.target(target)
            if (
                isinstance(target, ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "set"
                and isinstance(node.value.func.value, ast.Name)
            ):
                channel = self.channels.get(node.value.func.value.id)
                if channel and channel[0] == "context":
                    self.tokens[target.id] = channel

    def graph_call(self, node, forward=False):
        if (
            self.call_sites is None
            or not isinstance(node, ast.Call)
            or node.args
            or node.keywords
        ):
            return False
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and "print" not in self.shadowed
        ):
            return False
        target = self.call_sites.get((node.lineno, node.col_offset))
        if target is None:
            return False
        self.events.append(
            dict(
                kind="call",
                target="",
                name=target,
                line=node.lineno,
                forward=forward,
            )
        )
        return True

    def statement(self, node):
        if isinstance(node, ast.Global):
            self.globals.update(node.names)
        elif isinstance(node, ast.Pass):
            pass
        elif (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id in self.booleans
        ):
            self.block(
                node.body if self.booleans[node.test.id] else node.orelse
            )
        elif isinstance(node, ast.Expr):
            if not self.graph_call(node.value):
                self.expr(node.value)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            self.assign(node)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            self.modified_assignment(node)
        elif isinstance(node, (ast.Return, ast.Raise)):
            self.terminate(node)
        else:
            self.complete = False

    def modified_assignment(self, node):
        if isinstance(node, ast.AnnAssign):
            if node.value is None:
                self.complete = False
                return
            self.expr(node.value)
            if self.state(node.target) == ("ambient", "ENV"):
                self.complete = False
            self.target(node.target)
        else:
            state = self.state(node.target)
            if state and state != ("ambient", "ENV"):
                self.event("read", *state, node.target)
                self.expr(node.value)
                self.event("write", *state, node.target)
            else:
                self.complete = False

    def terminate(self, node):
        if isinstance(node, ast.Return):
            if node.value is not None and not self.graph_call(
                node.value, forward=True
            ):
                self.expr(node.value)
                self.event(
                    "return" if self.call_sites is not None else "output",
                    "",
                    "",
                    node,
                )
            self.stopped = True
            return
        value = node.exc
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id
            in ("Exception", "ValueError", "TypeError", "RuntimeError")
            and value.func.id not in self.shadowed
            and not value.keywords
            and node.cause is None
        ):
            for arg in value.args:
                self.expr(arg)
            self.event(
                "raise" if self.call_sites is not None else "output",
                "",
                "",
                node,
            )
        else:
            self.complete = False
        self.stopped = True

    def block(self, statements):
        for stmt in statements:
            if self.stopped or not self.complete:
                break
            self.statement(stmt)
