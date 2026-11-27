"""Encode admitted trace captures for the Lean kernel's equality check."""

from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared \
    import run_lean_json  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared \
    import lean_string  # fmt: skip


def _literal(value):
    if value is None:
        return ".null"
    if type(value) is bool:
        return ".boolean " + str(value).lower()
    if type(value) is int:
        return f".integer ({value})"
    if isinstance(value, str):
        return f".text ({lean_string(value)})"
    raise ValueError("Unsupported typed trace literal")


def _detail(value):
    if (
        isinstance(value, dict)
        and set(value) == {"at_most"}
        and type(value["at_most"]) is int
        and value["at_most"] >= 0
    ):
        return f".atMost {value['at_most']}"
    return f".literal ({_literal(value)})"


def _option(value, wildcard):
    return "none" if wildcard else f"some ({lean_string(value)})"


def _binding_pairs(pairs):
    return (
        "["
        + ", ".join(
            f"({lean_string(key)}, {lean_string(value)})"
            for key, value in pairs
        )
        + "]"
    )


def _workflow(initial, edges):
    rows, exits = [], []
    for (
        source,
        target,
        kind,
        observed,
        outcome,
        wildcard,
        final,
        target_wildcard,
        missing,
        detail,
        event,
        bind,
        same_as,
    ) in edges:
        if kind not in ("effect", "trigger", "output"):
            raise ValueError("Unsupported typed trace event")
        values = ", ".join(
            f"({lean_string(key)}, {_detail(value)})"
            for key, value in sorted(detail.items())
        )
        guard = (
            f"⟨.{kind}, {lean_string(event)}, {_option(observed, target_wildcard)}, "
            f"{_option(outcome, wildcard)}, [{values}], {_binding_pairs(bind)}, {_binding_pairs(same_as)}⟩"
        )
        rows.append(f"⟨{lean_string(source)}, {lean_string(target)}, {guard}⟩")
        if final:
            if kind != "output" or missing:
                raise ValueError(
                    "Typed trace requires a named terminal output"
                )
            exits.append(f"({lean_string(target)}, {lean_string(outcome)})")
    return (
        f"⟨{lean_string(initial)}, [{', '.join(rows)}], [{', '.join(exits)}]⟩"
    )


def check_capture(source, target, lean):
    semantics = (Path(__file__).parents[2] / "TraceSemantics.lean").read_text(
        encoding="utf-8"
    )
    program = (
        semantics
        + f"""
open TraceSemantics
def capturedSource : SourceWorkflow := ⟨{_workflow(*source)}⟩
def capturedTarget : TargetWorkflow := ⟨{_workflow(*target)}⟩
theorem capturesPreserveTrace (bound : Nat) (trace : Trace) :
    sourceTrace capturedSource bound trace ↔ targetTrace capturedTarget bound trace :=
  check_sound capturedSource capturedTarget (by decide) bound trace
#eval IO.println "true"
"""
    )
    if run_lean_json(program, lean) is not True:
        raise ValueError("Unexpected typed trace check output")
