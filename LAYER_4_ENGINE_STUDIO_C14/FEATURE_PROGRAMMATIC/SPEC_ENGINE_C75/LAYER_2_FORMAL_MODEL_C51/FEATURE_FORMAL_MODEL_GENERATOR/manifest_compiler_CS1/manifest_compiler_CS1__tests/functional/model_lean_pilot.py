"""Check JSON Atom Header observations with the pilot Lean predicate.

Run as a module with CONTROL_ROOT and ONTOLOGY_ROOT.
Provide a nonempty JSON array on stdin.
Each item has family, model_class, status, tier and priority keys.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from ....FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    admit_active_model_records,
    compile_native_bindings,
)
from ...manifest_compiler_CS1__shared import (
    read_active_model_sources,
    render_atom_header_lean,
)


def _text(value):
    if any(
        ord(char) < 32
        or 0x7F <= ord(char) <= 0x9F
        or 0xD800 <= ord(char) <= 0xDFFF
        for char in value
    ):
        return (
            "String.ofList ["
            + ", ".join(f"Char.ofNat {ord(char)}" for char in value)
            + "]"
        )
    return json.dumps(value, ensure_ascii=False)


def _value(value):
    if value is None:
        return "none"
    if isinstance(value, str):
        return f"some (.text {_text(value)})"
    if type(value) is int:
        return f"some (.integer ({value}))"
    return "some .other"


def _observations(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("expected a nonempty observation array")
    result = []
    for index, row in enumerate(rows):
        if (
            not isinstance(row, dict)
            or set(row)
            != {"family", "model_class", "status", "tier", "priority"}
            or not all(
                isinstance(row[k], str) for k in ("family", "model_class")
            )
        ):
            raise ValueError(f"invalid observation {index}")
        args = [_text(row["family"]), _text(row["model_class"])]
        args.extend(_value(row[key]) for key in ("status", "tier", "priority"))
        result.append(
            f"example : atomHeaderValid ⟨{', '.join(args)}⟩ = "
            "true := by decide"
        )
    return "\n".join(result) + "\n"


def main():
    if len(sys.argv) != 3:
        raise ValueError("expected CONTROL_ROOT and ONTOLOGY_ROOT arguments")
    control, ontology = map(Path, sys.argv[1:])
    declarations = read_active_model_sources(control, ontology)
    records, originals, _ = admit_active_model_records(declarations)
    bindings = compile_native_bindings(records, originals)
    program = render_atom_header_lean(records, bindings) + _observations(
        json.load(sys.stdin)
    )
    executable = os.environ.get("LEAN_BIN") or shutil.which("lean")
    if not executable:
        raise ValueError(
            "Lean executable is missing; install Lean or set LEAN_BIN"
        )
    with tempfile.TemporaryDirectory(
        prefix="anechoic-header-lean-"
    ) as directory:
        path = Path(directory) / "Header.lean"
        path.write_text(program, encoding="utf-8")
        subprocess.run([executable, str(path)], timeout=120, check=True)


if __name__ == "__main__":
    main()
