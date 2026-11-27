"""Check the declared export against the translated module binding."""

import ast
import json
from hashlib import sha256

_CHECK = """
open Autoform.Core Autoform.Generated.Implementation

def hasDeclaredExport (symbol : String) : Bool :=
  (AnechoicSpec.manifest >>= (·.getObjVal? "claim") >>= (·.getObjVal? \
"boundaries")
    >>= (·.getObjVal? "code") >>= (·.getObjVal? "exports")
    >>= (·.getObjVal? ("_package__shared." ++ symbol))).isOk

def readExport (heap : Heap) (globals : Ref) (symbol : String) : Option \
String :=
  match heap.getField globals "<module>_package__shared.py" with
  | .ref address =>
    match heap.getField address symbol with
    | .fn name => some name
    | _ => none
  | _ => none
"""


def export_pin(directory, symbol, root, expected_sha256=None):
    path = directory / "_package__shared.py"
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError(
            "Public export source must be a regular file at its Project path"
        )
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError(
            (
                "Public export source digest changed: "
                f"{path.relative_to(root).as_posix()}"
            )
        )
    if not all(
        isinstance(node, ast.ImportFrom) and node.level == 1
        for node in ast.parse(raw).body
    ):
        raise ValueError(
            "Public export source must contain only sibling imports"
        )
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": digest,
        "symbol": f"_package__shared.{symbol}",
        "status": "unresolved",
        "unresolved": [
            (
                "Python module importability and consumer visibility require "
                "separate evidence."
            )
        ],
    }


def export_check(symbol, provider):
    name = json.dumps(symbol)
    target = json.dumps(f"{provider}:<module>.{symbol}")
    return (
        _CHECK
        + f"""
#eval show IO Unit from do
  if !hasDeclaredExport {name} then
    throw (IO.userError "Selected public export is absent from the \
pinned Manifest")
  let (heap, globals) := initGlobals program 4000 moduleInits
  let some bound := readExport heap globals {name} |
    throw (IO.userError "Selected public export has no translated \
function binding")
  if bound != {target} then
    throw (IO.userError ("Declared public export does not bind to the \
checked implementation. Found " ++ bound))
"""
    )
