"""Parse CLI and trace Contract claims without executing their source."""

import ast

from .contract_literals import _call, _checks, _literal_string
from .http_contract import parse_contract as parse_contract
from .trace_contract import TRACE_FIELDS, trace_profile
from .trace_manifest__pub import (
    HTTP_BINDING_FIELDS,
    HTTP_BINDING_INPUTS,
    http_binding,
)


def exit_status_class(value):
    """Validate the abstract class reported by a terminal trace."""
    if value not in ("zero", "nonzero"):
        raise ValueError("expected zero or nonzero exit status class")
    return value


def exit_code(value):
    """Validate a concrete CLI exit code."""
    if type(value) is not int or not 0 <= value <= 255:
        raise ValueError("expected an exit code from 0 through 255")
    return value


def _cli_outcomes(outcomes, parse_value):
    if not isinstance(outcomes, ast.Dict) or not outcomes.keys:
        raise ValueError("expected named CLI outcomes")
    rows = {}
    for key, value in zip(outcomes.keys, outcomes.values):
        name = _literal_string(key)
        if not name.strip() or name in rows:
            raise ValueError("empty or duplicate CLI outcome")
        rows[name] = parse_value(ast.literal_eval(value))
    return rows


def _cli_sequences(args, names):
    fields = {}
    for name in names:
        if name not in args:
            continue
        sequence = args[name]
        if not isinstance(sequence, (ast.List, ast.Tuple)):
            raise ValueError(f"expected a literal sequence for {name}")
        values = [_literal_string(item) for item in sequence.elts]
        if not all(values) or (
            name != "arguments" and len(set(values)) != len(values)
        ):
            raise ValueError(f"empty or duplicate item in {name}")
        fields[name] = sorted(values) if name == "output_fields" else values
    return fields


def _cli_subcommands(node):
    if not isinstance(node, ast.Dict) or not node.keys:
        raise ValueError("expected a nonempty subcommand map")
    pairs = [
        (_literal_string(key), _literal_string(value))
        for key, value in zip(node.keys, node.values)
    ]
    routes = dict(pairs)
    if len(routes) != len(pairs) or any(
        not command.strip() or not target.strip() for command, target in pairs
    ):
        raise ValueError("empty or duplicate subcommand binding")
    return routes


def _cli_stdout(node):
    if isinstance(node, ast.Dict):
        return {
            f"stdout.{name}": value
            for name, value in _cli_subcommands(node).items()
        }
    return {"stdout": _literal_string(node)}


def _cli_binding(args, binding, public):
    entry = {"path", "module"} & args.keys()
    if not public and len(entry) != 1:
        raise ValueError("expected exactly one CLI path or module")
    claim = {
        key: _literal_string(args[key]) for key in sorted(binding | entry)
    }
    for key in ("command", "stdin", "stdout"):
        if key in args:
            claim.update(
                _cli_stdout(args[key])
                if key == "stdout"
                else {key: _literal_string(args[key])}
            )
    if "subcommands" in args:
        claim["subcommands"] = _cli_subcommands(args["subcommands"])
    if any(
        not value.strip() for value in claim.values() if isinstance(value, str)
    ):
        raise ValueError("CLI binding fields must be nonempty")
    return claim


def parse_cli_contract(source, *, public=False):
    """Read the CLI binding and the declared public obligations."""
    binding = (
        {"interface", "action"}
        if public
        else {"interface", "action", "runner"}
    )
    implementation = set() if public else {"path", "module", "subcommands"}
    sequences = (
        "arguments",
        "input_fields",
        "optional_paired_inputs",
        "output_fields",
    )
    protocol = {
        "command",
        "outcomes",
        "exit_codes",
        "checks",
        "stdin",
        "stdout",
    }
    args = _call(
        source,
        "declare_cli_contract",
        binding,
        protocol.union(sequences, TRACE_FIELDS, implementation),
    )
    claim = _cli_binding(args, binding, public)
    claim.update(_cli_sequences(args, sequences))
    if {"outcomes", "exit_codes"} <= args.keys():
        raise ValueError("declare exit codes or exit status classes")
    for key, validator in (
        ("outcomes", exit_status_class),
        ("exit_codes", exit_code),
    ):
        if key in args:
            claim[key] = _cli_outcomes(args[key], validator)
    claim.update(trace_profile(args, claim["action"]))
    claim.update(_checks(args))
    return {**claim, "transport": "cli"}


_HTTP_TRACE_BINDING = ("interface", "transport", *HTTP_BINDING_FIELDS)
_IN_PROCESS_TRACE_BINDING = ("interface", "transport", "entry")


def parse_trace_contract(source, *, public=False):
    """Read a trace Contract's action, terminal output and required effects."""
    in_process = (
        _IN_PROCESS_TRACE_BINDING[:2] if public else _IN_PROCESS_TRACE_BINDING
    )
    binding = set(in_process)
    args = _call(
        source,
        "declare_trace_contract",
        {"action"},
        TRACE_FIELDS | binding | HTTP_BINDING_INPUTS,
    )
    present = binding & args.keys()
    fields = {key: _literal_string(args[key]) for key in present}
    literals = {
        key: _literal_string(args[key])
        for key in HTTP_BINDING_INPUTS & args.keys()
    }
    fields.update(http_binding(literals))
    profiles = {"http": _HTTP_TRACE_BINDING, "in_process": in_process}
    if fields and (
        set(profiles.get(fields.get("transport"), ())) != fields.keys()
        or any(not value.strip() for value in fields.values())
    ):
        raise ValueError("invalid trace interface binding")
    action = _literal_string(args["action"])
    if not action.strip():
        raise ValueError("expected nonempty action")
    profile = trace_profile(args, action)
    if not profile:
        raise ValueError("expected trace outcome cases or an action invariant")
    return {"action": action, **fields, **profile.pop("trace", {}), **profile}
