"""Compare explicit, source-pinned obligations with Lean."""

import json
from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import run_lean_json
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import lean_string


_DIRECTIONS = (
    ("manifest", "contract"),
    ("manifest", "solution"),
    ("contract", "solution"),
)


def _literal(facts):
    return (
        "["
        + ", ".join(
            f"({lean_string(key)}, "
            + lean_string(
                json.dumps(
                    value,
                    sort_keys=True,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                )
            )
            + ")"
            for key, value in sorted(facts.items())
        )
        + "]"
    )


def _program(obligations, directions, roles):
    declarations = "\n".join(
        f"def {role} : List (String × String) := {_literal(obligations[role])}"
        for role in roles
    )
    calls = ", ".join(f"compare {left} {right}" for left, right in directions)
    return f"""import Lean
{declarations}
def sameValue (left right : String) : Bool :=
  if left == right then true else
    match Lean.Json.parse left, Lean.Json.parse right with
    | .ok a, .ok b => a.compress == b.compress
    | _, _ => false
def compare (left right : List (String × String)) : List String :=
  left.map fun fact =>
    match right.find? (fun candidate => candidate.1 == fact.1) with
    | none => "unresolved"
    | some candidate => if sameValue candidate.2 fact.2 then "matched" else \
"conflicting"
#eval IO.println (Lean.toJson [{calls}]).compress
"""


def _compare(sources, obligations, pairs, lean):
    roles = {role: None for pair in pairs for role in pair}
    for role in roles:
        if (
            role not in sources
            or role not in obligations
            or not isinstance(obligations[role], dict)
            or any(not isinstance(key, str) for key in obligations[role])
        ):
            raise ValueError(
                (
                    "sources and obligation dictionaries must contain each "
                    "comparison role"
                )
            )
    output = run_lean_json(_program(obligations, pairs, roles), lean)
    return _comparison_report(sources, obligations, pairs, output)


def _comparison_report(sources, obligations, pairs, output):
    if not isinstance(output, list) or len(output) != len(pairs):
        raise ValueError("unexpected Lean comparison output")
    directions = {}
    index = 0
    for pair in pairs:
        left, right = pair
        rows = output[index]
        index += 1
        if not isinstance(rows, list) or len(rows) != len(obligations[left]):
            raise ValueError("unexpected Lean comparison output")
        facts = []
        index_in_rows = 0
        for key in sorted(obligations[left].keys()):
            status = rows[index_in_rows]
            index_in_rows += 1
            value = obligations[left][key]
            if status not in ("matched", "conflicting", "unresolved"):
                raise ValueError("unexpected Lean comparison output")
            fact = {
                "key": key,
                "left": value,
                "right": obligations[right].get(key),
                "status": status,
            }
            facts.append(fact)
        directions[f"{left}_{right}"] = {
            "status": verdict(rows),
            "facts": facts,
        }
    statuses = [direction["status"] for direction in directions.values()]
    return {
        "status": verdict(statuses),
        "sources": sources,
        "directions": directions,
    }


def compare_obligations(sources, obligations, *, lean="lean"):
    """Compare Manifest, Contract, and Solution obligations."""
    return _compare(sources, obligations, _DIRECTIONS, lean)


def compare_delegation(
    sources, obligations, *, manifest_only=False, lean="lean"
):
    """Compare caller obligations with the provider Manifest
    or the legacy declarations.
    """
    pairs = (("caller", "manifest"),)
    if not manifest_only:
        pairs += (("caller", "contract"), ("caller", "solution"))
    return _compare(sources, obligations, pairs, lean)
