"""Private fixture support for the Lean state effects tests."""

import ast
import importlib.util
import json
import subprocess
import sys


CONTEXT = """
open Autoform.Core Autoform.SpecsGen Autoform.Generated.AnechoicEffects
set_option maxRecDepth 20000
set_option maxHeartbeats 0
private def gp : Heap × Ref := initGlobals program 300 moduleInits
private def h0 : Heap := gp.1
private def base : Nat := h0.length
private def ctx : Ctx :=
  { dialect := program.dialect, table := program.table, globals := gp.2,
    builtinBases := program.builtinBases, properties := program.properties,
    excClasses := program.excClasses, classDecls := program.classDecls }
"""

SOURCE = """
def action(kind, state, sink, trace):
    if kind == 0:
        alias = state
        alias[0] = 1
    elif kind == 1:
        sink.append(7)
    elif kind == 2:
        old = state[0]
        state[0] = 1
        state[0] = old
    elif kind == 3:
        pass
    else:
        raise ValueError('unsupported fixture input')
"""


def _event(kind, target="", name="", line=1):
    return {"kind": kind, "target": target, "name": name, "line": line}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FixtureTrace(ast.NodeTransformer):
    """Record operations in the fixed fixture's selected state and output."""

    def visit_Assign(self, node):
        marker = None
        if isinstance(node.targets[0], ast.Subscript):
            marker = 1
        elif isinstance(node.value, ast.Subscript):
            marker = 0
        return node if marker is None else [node, self.record(node, marker)]

    def visit_Expr(self, node):
        return (
            [node, self.record(node, 2)]
            if isinstance(node.value, ast.Call)
            else node
        )

    @staticmethod
    def record(node, marker):
        return ast.parse(f"trace.append({10 * node.lineno + marker})").body[0]


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, timeout=480)


def _observations(folder, source, differential):
    module = _load(source, "lean_action_effects_fixture")
    identities = (
        differential.class_identity_index(
            json.loads((folder / "ast.json").read_text()),
            source.parent,
        )
        or {}
    )
    records, events = [], []
    markers = [
        _event("read", "ambient", "REQUEST_CTX"),
        _event("write", "ambient", "REQUEST_CTX"),
        _event("output"),
    ]
    for kind in range(4):
        state, sink, trace = [0], [], []
        encoder = differential.GraphEncoder(identities)
        args = [encoder.enc(value) for value in (kind, state, sink, trace)]
        encoder.freeze()
        value = module.action(kind, state, sink, trace)
        assert (state, sink) == [([1], []), ([0], [7]), ([0], []), ([0], [])][
            kind
        ]
        record = {
            "name": "instrumented.py:<module>.action",
            "self": None,
            "args": args,
            "outcome": ("val", encoder.enc_result(value)),
        }
        observation = differential.finish_record(encoder, record)
        assert "post_heap" in observation
        records.append(observation)
        events.append(
            [markers[marker % 10] | {"line": marker // 10} for marker in trace]
        )
        if kind == 2:
            trace.clear()
            tampered = differential.finish_record(encoder, dict(record))
    return records, events, tampered


def _prove(folder, checkout, source, observe=_observations):
    differential = _load(
        checkout / "scripts/differential.py", "ane_effect_diff"
    )
    synth = _load(checkout / "scripts/synth_specs.py", "ane_effect_synth")
    records, events, tampered = observe(folder, source, differential)
    model = (
        (folder / "Model.lean")
        .read_text()
        .replace(
            "import Autoform.Lang.Core.Semantics",
            "import Autoform.SpecsGen.Basis",
        )
    )
    proof = [model, CONTEXT]
    fn = synth.lean_ident("instrumented.py:<module>.action")
    for index, record in enumerate(records):
        proof.extend(
            [
                f"private def obs{index} : Obs := {synth.obs_lit(record)}",
                f"example : lawConform ctx 160 {fn} obs{index} = true "
                ":= by decide +kernel",
            ]
        )
    proof.extend(
        [
            f"private def tampered : Obs := {synth.obs_lit(tampered)}",
            f"example : lawConform ctx 160 {fn} tampered = false "
            ":= by decide +kernel",
            f"example : lawConform ctx 160 {{ {fn} with body := .skip }} "
            "obs0 = false := by decide +kernel",
        ]
    )
    path = folder / "Proof.lean"
    path.write_text("\n".join(proof) + "\n")
    _run(["lake", "env", "lean", path], checkout)
    return events


NATIVE_CONTEXT = """from contextvars import ContextVar
request = ContextVar('request', default=0)
def action(value, trace):
    token = request.set(value)
    trace.append(1)
    observed = request.get()
    request.reset(token)
    trace.append(1)
    return observed
"""

LOWERED_CONTEXT = """def action(value, cell, trace):
    token = cell[0]
    cell[0] = value
    trace.append(1)
    observed = cell[0]
    cell[0] = token
    trace.append(1)
    return observed
"""


def _context_observations(folder, source, differential):
    native = {}
    exec(NATIVE_CONTEXT, native)
    lowered = _load(source, "lean_context_fixture")
    identities = (
        differential.class_identity_index(
            json.loads((folder / "ast.json").read_text()),
            source.parent,
        )
        or {}
    )
    records = []
    for value in (0, 2):
        trace, cell, model_trace = [], [9], []
        token = native["request"].set(9)
        try:
            result = native["action"](value, trace)
            final = native["request"].get()
        finally:
            native["request"].reset(token)
        encoder = differential.GraphEncoder(identities)
        args = [encoder.enc(item) for item in (value, cell, model_trace)]
        encoder.freeze()
        actual = lowered.action(value, cell, model_trace)
        assert (
            (actual, cell[0], model_trace)
            == (result, final, trace)
            == (value, 9, [1, 1])
        )
        record = {
            "name": "instrumented.py:<module>.action",
            "self": None,
            "args": args,
            "outcome": ("val", encoder.enc_result(actual)),
        }
        observation = differential.finish_record(encoder, record)
        assert "post_heap" in observation
        records.append(observation)
        model_trace.clear()
        tampered = differential.finish_record(encoder, dict(record))
    return records, [], tampered


def _translate(folder, checkout, joern, source):
    _run(
        [
            joern / "joern-parse",
            source.parent,
            "--language",
            "PYTHONSRC",
            "--output",
            "cpg.bin",
        ],
        folder,
    )
    _run(
        [
            joern / "joern",
            "--script",
            checkout / "cartographer/export_ast.sc",
            "--param",
            "cpgPath=cpg.bin",
            "--param",
            "out=ast.json",
        ],
        folder,
    )
    _run(
        [
            sys.executable,
            checkout / "cartographer/render_lean.py",
            folder / "ast.json",
            folder / "Model.lean",
            "AnechoicEffects",
        ],
        folder,
    )
    _run(["lake", "build", "Autoform.SpecsGen.Basis"], checkout)
