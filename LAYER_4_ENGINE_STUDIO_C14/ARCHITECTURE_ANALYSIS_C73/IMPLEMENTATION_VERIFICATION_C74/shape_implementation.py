"""Compare pinned Python declaration shapes with verified formal Lean."""

import ast
import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from ._shape_compare_program import CHECK as _CHECK

_ROLES = ("contract", "solution")


def _name(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9_]*", value
    ):
        raise ValueError("Unsupported Python shape name")
    return value


def _check_owner(ownership, component_id, path, record, subtype):
    owner = ownership.owner(path.as_posix())
    while owner is not None and owner["kind"] != "component":
        owner = ownership.entries.get(owner["parent"])
    if owner is None or owner["id"] != component_id:
        raise ValueError(
            (
                "Implementation source is outside the admitted realization of "
                f"{component_id}"
            )
        )
    module = ".".join(path.relative_to(owner["path"]).with_suffix("").parts)
    exports = (
        owner["fields"]
        .get("boundaries", {})
        .get("code", {})
        .get("exports", {})
    )
    if not all(f"{module}.{name}" in exports for name in (record, subtype)):
        raise ValueError(
            (
                "Implementation module "
                f"{module}"
                " does not declare both shape exports"
            )
        )


def _read_source(root, pin, ownership, component_id, record, subtype):
    if not isinstance(pin, dict) or set(pin) != {"path", "sha256"}:
        raise ValueError("Implementation source requires path and sha256")
    if not isinstance(pin["path"], str) or not isinstance(pin["sha256"], str):
        raise TypeError("Invalid implementation source pin")
    relative = Path(pin["path"])
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix != ".py"
    ):
        raise ValueError("Expected a Project-relative Python source path")
    _check_owner(ownership, component_id, relative, record, subtype)
    path = Path(root).resolve(strict=True) / relative
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError(
            "Implementation source must be a regular file under the Project"
        )
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin["sha256"]:
        raise ValueError("Implementation source digest changed")
    return ast.parse(raw, str(relative))


def _select_class(tree, name):
    declarations = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == name
    ]
    if len(declarations) != 1:
        raise ValueError(f"Expected one top-level class {name}")
    return declarations[0]


def _fields(declaration):
    fields = {}
    for node in declaration.body:
        if isinstance(node, ast.Pass):
            continue
        if (
            not isinstance(node, ast.AnnAssign)
            or not node.simple
            or not isinstance(node.target, ast.Name)
            or not isinstance(node.annotation, ast.Name)
        ):
            raise ValueError(f"Unsupported declaration in {declaration.name}")
        key = _name(node.target.id)
        if key in fields:
            raise ValueError(f"Duplicate field {declaration.name}.{key}")
        fields[key] = _name(node.annotation.id)
    return fields


def _implementation_shape(tree, record, subtype):
    parent, child = _select_class(tree, record), _select_class(tree, subtype)
    if any(node.type_params or node.keywords for node in (parent, child)):
        raise ValueError(
            (
                "Generic classes and metaclasses are outside the Python shape "
                "check"
            )
        )
    if len(child.bases) > 1 or any(
        not isinstance(base, ast.Name) for base in child.bases
    ):
        raise ValueError(f"Unsupported direct base of {subtype}")
    base = _name(child.bases[0].id) if child.bases else None
    return {
        "record": parent.name,
        "subtype": child.name,
        "base": base,
        "fields": _fields(parent),
        "subtype_fields": _fields(child),
    }


def _shape_name(formal, key):
    names = {
        _name(fact.get("left"))
        for fact in formal.get("evidence", {}).get("coverage", [])
        if fact.get("key") == key and fact.get("status") == "matched"
    }
    if len(names) != 1:
        raise ValueError(f"Verified Specs must agree on the shape {key}")
    return names.pop()


def _emit(shape):
    payload = json.dumps(
        json.dumps(shape, sort_keys=True, separators=(",", ":"))
    )
    return (
        "import Lean\nnamespace ImplementationShape\n"
        f"def claim : Except String Lean.Json := Lean.Json.parse {payload}\n"
        "end ImplementationShape\n"
    )


def _validated_spec_lean(formal, manifest, solution):
    if (
        formal.get("outcome") != "compared"
        or formal.get("translation", {}).get("status") != "matched"
    ):
        raise ValueError("No validated shape Spec comparison")
    for role, requested in (("manifest", manifest), ("solution", solution)):
        source = formal.get("sources", {}).get(role, {})
        if not source.get("sha256") or any(
            source.get(key) != value for key, value in requested.items()
        ):
            raise ValueError(
                f"Verified {role} source does not match its request"
            )
    program = formal.get("lean")
    if not isinstance(program, str) or not program:
        raise ValueError("Verified shape Spec has no Lean declarations")
    return program


def _run(program, lean):
    with TemporaryDirectory() as tmp:
        file = Path(tmp) / "ShapeComparison.lean"
        file.write_text(program, encoding="utf-8")
        result = subprocess.run(
            [lean, str(file)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    if result.returncode:
        raise ValueError(
            "Lean shape comparison failed: "
            + (result.stderr + result.stdout)[:1000]
        )
    output = json.loads(result.stdout)
    if (
        not isinstance(output, list)
        or len(output) != len(_ROLES)
        or any(
            not isinstance(row, list)
            or not row
            or any(
                not isinstance(pair, list)
                or len(pair) != 2
                or not isinstance(pair[0], str)
                or type(pair[1]) is not bool
                for pair in row
            )
            for row in output
        )
    ):
        raise ValueError("Unexpected Lean shape comparison result")
    return output


def _directions(checks, actual):
    observed = {
        **actual,
        **{f"field.{key}": value for key, value in actual["fields"].items()},
    }
    return {
        f"{role}_implementation": {
            "status": "matched"
            if all(passed for _, passed in row)
            else "conflicting",
            "facts": [
                {
                    "key": key,
                    "actual": observed.get(key),
                    "status": "matched" if passed else "conflicting",
                }
                for key, passed in row
            ],
        }
        for role, row in zip(_ROLES, checks, strict=True)
    }


def _initial_report(formal):
    report = {
        "outcome": "incomplete",
        "status": "unresolved",
        "sources": formal.get("sources", {}),
        "directions": {},
        "formal": formal,
        "unresolved": list(formal.get("unresolved", [])),
    }
    report["unresolved"].append(
        (
            "Runtime annotation resolution, dataclass behavior, and effects "
            "require separate evidence"
        )
    )
    return report


def _compare_result(report, actual, formal_lean, lean):
    implementation_lean = _emit(actual)
    program = (
        formal_lean
        + "\n"
        + implementation_lean.removeprefix("import Lean\n")
        + _CHECK
    )
    report.update(
        implementation_lean=implementation_lean, comparison_lean=program
    )
    checks = _run(program, lean)
    report["outcome"] = "compared"
    report["directions"] = _directions(checks, actual)
    if any(
        direction["status"] == "conflicting"
        for direction in report["directions"].values()
    ):
        report["status"] = "conflicting"


def compare(
    root,
    component_id,
    manifest,
    solution,
    implementation,
    *,
    formal_verifier,
    ownership,
    lean="lean",
):
    """Compare a pinned Python declaration against trusted Spec evidence."""
    formal = formal_verifier(
        root, component_id, manifest, solution=solution, lean=lean
    )
    report = _initial_report(formal)
    if formal.get("status") == "conflicting":
        report["status"] = "conflicting"
        return report
    try:
        formal_lean = _validated_spec_lean(formal, manifest, solution)
        record, subtype = (
            _shape_name(formal, key) for key in ("record", "subtype")
        )
        tree = _read_source(
            root, implementation, ownership, component_id, record, subtype
        )
        actual = _implementation_shape(tree, record, subtype)
        report["sources"] = {
            **report["sources"],
            "implementation": dict(implementation),
        }
        report["implementation_component"] = component_id
        _compare_result(report, actual, formal_lean, lean)
    except (
        OSError,
        SyntaxError,
        TypeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        report["unresolved"].append(str(error))
    return report
