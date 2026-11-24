"""Generate the bounded carrier model from the admitted Python operations."""
import ast
import hashlib
from pathlib import Path

from WORKERS_beta_C69.WORKERS_beta_C69__shared import python_code_units

_SOURCE = ('LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/'
           'ADAPTERS_C30/carrier_body__pub.py')
_SHAPES = {
    '155908c527083c9c78349ed9f4b8d0905193bfd5a106a60661822b8e53d9cbb8': 'flags',
    '834eaeef5604b10c769c5cedb91e212ce057b7b4c8d10e6f5f3b3f27f83452e2': 'pos',
}
_BODY = '19c49cf5c4194d41149ad4b4edf7dac059023fdf19bc4b2b404a4e89478be486'


def _digest(node):
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()


def _analyze(root, source_bytes):
    source = Path(root) / _SOURCE
    raw = source.read_bytes() if source_bytes is None else source_bytes
    tree = ast.parse(raw, filename=_SOURCE)
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    functions = {node.name: node for node in definitions}
    if len(definitions) != 2 or set(functions) != {'frontmatter_bounds', 'source_body'}:
        raise ValueError('unsupported carrier functions')
    mode = _SHAPES.get(_digest(functions['frontmatter_bounds']))
    if mode is None or _digest(functions['source_body']) != _BODY:
        raise ValueError('unsupported carrier operation shape')
    expected = 'from pathlib import Path\nimport re\n'
    if mode == 'pos':
        expected += '_CLOSING_DELIMITER = re.compile(rb"\\r?\\n---\\r?\\n")\n'
    other = [n for n in tree.body if not isinstance(n, ast.FunctionDef)
             and not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                      and isinstance(n.value.value, str))]
    if ast.dump(ast.Module(body=other, type_ignores=[])) != ast.dump(ast.parse(expected)):
        raise ValueError('unsupported carrier module context')
    units, calls = python_code_units({_SOURCE: raw.decode('utf-8')}, {})
    selected = {u[3]: u for u in units if u[3] in functions}
    if set(selected) != set(functions) or not any(
        c[0] == selected['source_body'][0] and c[1] == selected['frontmatter_bounds'][0]
        for c in calls
    ):
        raise ValueError('Code Analysis does not bind the required symbols and call')
    f = functions['frontmatter_bounds']
    opening_lf = f.body[0].test.args[0].value
    opening_crlf = f.body[0].orelse[0].test.args[0].value
    if mode == 'flags':
        pattern = f.body[1].value.args[0].value
    else:
        pattern = next(n for n in tree.body if isinstance(n, ast.Assign)).value.args[0].value
    if pattern != rb'\r?\n---\r?\n':
        raise ValueError('unsupported closing regex')
    evidence = {'source': _SOURCE, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                'symbols': selected, 'calls': calls, 'search_mode': mode,
                'unresolved': ['Only the exact admitted AST shapes and byte regex are modeled.',
                               'Finite cases do not prove equivalence for all inputs.',
                               'Project state effects are outside this model.']}
    return opening_lf, opening_crlf, mode, evidence


def _model(opening_lf, opening_crlf, mode):
    def lean_bytes(value):
        return '[' + ', '.join(str(v) for v in value) + ']'
    endings = [b'\r\n---\r\n', b'\r\n---\n', b'\n---\r\n', b'\n---\n']
    search = 'findClosing raw 0' if mode == 'flags' else (
        'findClosing (raw.drop (openingEnd - 1)) (openingEnd - 1)')
    model = f'''import Lean

def openingLF : List Nat := {lean_bytes(opening_lf)}
def openingCRLF : List Nat := {lean_bytes(opening_crlf)}
def closingPatterns : List (List Nat) := {' :: '.join(map(lean_bytes, endings))} :: []
def closingLength (xs : List Nat) : Option Nat :=
  (closingPatterns.find? (fun p => xs.take p.length == p)).map List.length
def findClosing : List Nat → Nat → Option (Nat × Nat)
  | [], _ => none
  | x :: rest, pos =>
    match closingLength (x :: rest) with
    | some len => some (pos, pos + len)
    | none => findClosing rest (pos + 1)
def frontmatterBounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let openingEnd ←
    if raw.take openingLF.length == openingLF then some openingLF.length
    else if raw.take openingCRLF.length == openingCRLF then some openingCRLF.length
    else none
  let (start, stop) ← {search}
  return (openingEnd, start, stop)
def sourceBody (raw : List Nat) (path : String) : Except String (List Nat) :=
  match frontmatterBounds raw with
  | none => .error (path ++ ": unsupported frontmatter delimiter")
  | some (_, _, stop) => .ok (raw.drop stop)
'''
    return model


def generate(root, source_bytes=None):
    """Return Lean text and binding evidence, or reject an unsupported shape."""
    opening_lf, opening_crlf, mode, evidence = _analyze(root, source_bytes)
    return _model(opening_lf, opening_crlf, mode), evidence
