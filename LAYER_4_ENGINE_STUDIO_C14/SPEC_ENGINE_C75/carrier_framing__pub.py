"""Lower the bounded carrier framing declarations to pure Lean models."""
import ast

_FIELDS = {
    'contract': ('delimiter', 'line_endings'),
    'solution': ('opening_prefixes', 'closing_prefixes'),
}


def _validate(claim, role):
    if role not in _FIELDS or not isinstance(claim, dict) or set(claim) != set(_FIELDS[role]):
        raise ValueError('invalid framing role or fields')
    result = {}
    for name in _FIELDS[role]:
        value = claim[name]
        patterns = [value] if name == 'delimiter' else value
        if not isinstance(patterns, (list, tuple)) or not patterns:
            raise ValueError('expected nonempty patterns')
        normalized = []
        for pattern in patterns:
            if (not isinstance(pattern, (list, tuple)) or not pattern
                    or any(type(b) is not int or not 0 <= b <= 255 for b in pattern)):
                raise ValueError('expected nonempty byte pattern')
            normalized.append(tuple(pattern))
        if len(set(normalized)) != len(normalized):
            raise ValueError('duplicate pattern')
        result[name] = normalized[0] if name == 'delimiter' else tuple(normalized)
    return result


def parse_framing(source, role):
    """Parse exactly one literal framing declaration; never execute the source."""
    if role not in _FIELDS:
        raise ValueError('invalid framing role')
    try:
        tree = ast.parse(source)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
            raise ValueError('expected one declaration')
        call = tree.body[0].value
        if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name)
                or call.func.id != 'declare_framing_' + role or call.args):
            raise ValueError('invalid framing declaration')
        names = [item.arg for item in call.keywords]
        if None in names or len(set(names)) != len(names) or set(names) != set(_FIELDS[role]):
            raise ValueError('invalid framing keywords')
        def literal_list(node):
            if not isinstance(node, ast.List):
                raise TypeError('expected list literal')
            return [literal_list(n) if isinstance(n, ast.List) else literal_byte(n)
                    for n in node.elts]

        def literal_byte(node):
            if not isinstance(node, ast.Constant) or type(node.value) is not int:
                raise ValueError('expected byte literal')
            return node.value

        return _validate({item.arg: literal_list(item.value) for item in call.keywords}, role)
    except (SyntaxError, TypeError) as exc:
        raise ValueError('invalid framing source') from exc


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


def framing_to_mermaid(claim):
    """Show the solution scanner and its framing outcomes."""
    claim = _validate(claim, 'solution')
    opening = ', '.join(str(list(pattern)) for pattern in claim['opening_prefixes'])
    closing = ', '.join(str(list(pattern)) for pattern in claim['closing_prefixes'])
    return (f'flowchart TD\n  A[Raw bytes] --> B{{"Opening prefix: {opening}"}}\n'
            f'  B -->|matched| C["Scan from opening minus one: {closing}"]\n'
            '  B -->|missing| M[Missing delimiter]\n'
            '  C -->|first match| D[Bounds and unchanged body tail]\n'
            '  C -->|missing| M\n')
