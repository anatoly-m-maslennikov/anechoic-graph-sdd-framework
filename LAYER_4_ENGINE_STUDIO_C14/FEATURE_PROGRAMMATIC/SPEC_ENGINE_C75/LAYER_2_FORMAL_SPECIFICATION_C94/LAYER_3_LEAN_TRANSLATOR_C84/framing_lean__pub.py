from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import _validate  # fmt: skip


def _prefix_test(variable, patterns):
    lines = []
    for pattern in patterns:
        value = "[" + ", ".join(map(str, pattern)) + "]"
        lines.append(
            (
                "if "
                f"{variable}"
                ".take "
                f"{len(pattern)}"
                " == "
                f"{value}"
                " then some "
                f"{len(pattern)}"
            )
        )
    return "\n  else ".join(lines) + "\n  else none"


def _contract_model(claim):
    delimiter = claim["delimiter"]
    endings = claim["line_endings"]
    opening = _prefix_test("raw", [delimiter + ending for ending in endings])
    line_end = _prefix_test("raw", endings)
    delimiter_text = "[" + ", ".join(map(str, delimiter)) + "]"
    return (
        "def openingEnd (raw : List Nat) : Option Nat :=\n"
        "  "
        f"{opening}"
        "\n"
        "\n"
        "def lineEndLength (raw : List Nat) : Option Nat :=\n"
        "  "
        f"{line_end}"
        "\n"
        "\n"
        "def closingEnd (raw : List Nat) (separator : Nat) : Option Nat := "
        "do\n"
        "  let sep ← lineEndLength (raw.drop separator)\n"
        "  let afterSep := separator + sep\n"
        "  if (raw.drop afterSep).take "
        f"{len(delimiter)}"
        " != "
        f"{delimiter_text}"
        " then none\n"
        "  else do\n"
        "    let ending ← lineEndLength (raw.drop (afterSep + "
        f"{len(delimiter)}"
        "))\n"
        "    some (afterSep + "
        f"{len(delimiter)}"
        " + ending)\n"
        "\n"
        "def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do\n"
        "  let opening ← openingEnd raw\n"
        "  let start ← ((List.range raw.length).drop (opening - 1)).find? "
        "(fun i => (closingEnd raw i).isSome)\n"
        "  let stop ← closingEnd raw start\n"
        "  some (opening, start, stop)\n"
    )


def _solution_model(claim):
    opening = _prefix_test("raw", claim["opening_prefixes"])
    closing = _prefix_test("raw", claim["closing_prefixes"])
    return f"""def opening (raw : List Nat) : Option Nat :=
  {opening}

def closingLength (raw : List Nat) : Option Nat :=
  {closing}

def firstClosing : List Nat → Nat → Option (Nat × Nat)
  | [], _ => none
  | x :: xs, pos =>
    match closingLength (x :: xs) with
    | some n => some (pos, pos + n)
    | none => firstClosing xs (pos + 1)

def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let start ← opening raw
  let (close, stop) ← firstClosing (raw.drop (start - 1)) (start - 1)
  some (start, close, stop)
"""


def framing_to_lean(claim, role):
    """Emit a pure framing model; it makes no implementation-effects claim."""
    claim = _validate(claim, role)
    ns = "CarrierBodyContract" if role == "contract" else "CarrierBodySolution"
    model = (
        _contract_model(claim)
        if role == "contract"
        else _solution_model(claim)
    )
    return f"""namespace {ns}
{model}
inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving Repr, BEq, DecidableEq

def body (raw : List Nat) : Outcome :=
  match bounds raw with
  | none => .missingDelimiter
  | some (_, _, stop) => .body (raw.drop stop)
end {ns}
"""
