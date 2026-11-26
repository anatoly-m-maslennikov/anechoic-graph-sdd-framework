from ..LAYER_2_FORMAL_MODEL_C85.carrier_framing__pub import _validate


def _prefix_test(variable, patterns):
    lines = []
    for pattern in patterns:
        value = '[' + ', '.join(map(str, pattern)) + ']'
        lines.append(f'if {variable}.take {len(pattern)} == {value} then some {len(pattern)}')
    return '\n  else '.join(lines) + '\n  else none'


def _contract_model(claim):
    delimiter = claim['delimiter']
    endings = claim['line_endings']
    opening = _prefix_test('raw', [delimiter + ending for ending in endings])
    line_end = _prefix_test('raw', endings)
    delimiter_text = '[' + ', '.join(map(str, delimiter)) + ']'
    return f'''def openingEnd (raw : List Nat) : Option Nat :=
  {opening}

def lineEndLength (raw : List Nat) : Option Nat :=
  {line_end}

def closingEnd (raw : List Nat) (separator : Nat) : Option Nat := do
  let sep ← lineEndLength (raw.drop separator)
  let afterSep := separator + sep
  if (raw.drop afterSep).take {len(delimiter)} != {delimiter_text} then none
  else do
    let ending ← lineEndLength (raw.drop (afterSep + {len(delimiter)}))
    some (afterSep + {len(delimiter)} + ending)

def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let opening ← openingEnd raw
  let start ← ((List.range raw.length).drop (opening - 1)).find? (fun i => (closingEnd raw i).isSome)
  let stop ← closingEnd raw start
  some (opening, start, stop)
'''


def _solution_model(claim):
    opening = _prefix_test('raw', claim['opening_prefixes'])
    closing = _prefix_test('raw', claim['closing_prefixes'])
    return f'''def opening (raw : List Nat) : Option Nat :=
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
'''


def framing_to_lean(claim, role):
    """Emit a pure framing model; it makes no implementation-effects claim."""
    claim = _validate(claim, role)
    ns = 'CarrierBodyContract' if role == 'contract' else 'CarrierBodySolution'
    model = _contract_model(claim) if role == 'contract' else _solution_model(claim)
    return f'''namespace {ns}
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
'''
