"""Check whether the generated Ref ID follows later Atom state."""

import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

GENERATOR = (
    "LAYER_*_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/"
    "FEATURE_FORMAL_MODEL_GENERATOR/manifest_property_fields.py"
)
HELPER = (
    "LAYER_*_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/"
    "native_atom_reference.py"
)


def function(path, name):
    tree = ast.parse(path.read_text())
    found = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(found) != 1:
        raise ValueError("expected one " + name)
    return found[0]


def has_target(targets, node_type, name):
    for target in targets:
        if isinstance(target, node_type) and ast.unparse(target) == name:
            return True
    return False


def assigns_ref_id(node):
    return isinstance(node, ast.Assign) and has_target(
        node.targets, ast.Attribute, "self.ref_id"
    )


def assigns_expected(node):
    return has_target(node.targets, ast.Name, "expected")


def generated_method(body):
    method = body.body[0]
    derivation = "self._derive_ref_id(self.atom_id, self.version, self.status)"
    if method.name == "__post_init__":
        assigns = list(filter(assigns_ref_id, method.body))
        assignments = [n for n in method.body if isinstance(n, ast.Assign)]
        expected = list(filter(assigns_expected, assignments))
        if (
            len(assigns) != 1
            or ast.unparse(assigns[0].value) != "expected"
            or len(expected) != 1
        ):
            raise ValueError("unsupported initialization write")
        if ast.unparse(expected[0].value) != derivation:
            raise ValueError("unsupported derivation in initialization")
        return False
    if method.name == "ref_id":
        if (
            len(method.decorator_list) != 1
            or ast.unparse(method.decorator_list[0]) != "property"
        ):
            raise ValueError("Ref ID is not a property")
        returns = [n for n in method.body if isinstance(n, ast.Return)]
        if len(returns) != 1 or ast.unparse(returns[0].value) != derivation:
            raise ValueError("unsupported property return")
        return True
    raise ValueError("unsupported generated method name")


def extract(generator_path, helper_path):
    helper = function(helper_path, "derive_atom_ref")
    expected_helper = (
        "def derive_atom_ref(atom_id: str, version: int, "
        "status: str) -> str:\n"
        '    suffix = "-draft" if status.casefold() == "draft" '
        'else ""\n'
        '    return f"{atom_id}@{version}{suffix}"\n'
    )
    if ast.dump(helper, include_attributes=False) != ast.dump(
        ast.parse(expected_helper).body[0], include_attributes=False
    ):
        raise ValueError("unsupported Ref ID derivation helper")
    generator = function(generator_path, "_emit_derived")
    parses = [
        n
        for n in ast.walk(generator)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and ast.unparse(n.func) == "ast.parse"
        and n.args
        and isinstance(n.args[0], ast.Constant)
        and isinstance(n.args[0].value, str)
    ]
    if len(parses) != 1:
        raise ValueError("expected one literal generated method")
    appenders = [
        n
        for n in ast.walk(generator)
        if isinstance(n, ast.Call)
        and ast.unparse(n.func) == "classes[atom].body.append"
        and len(n.args) == 1
    ]
    if len(appenders) != 2 or not any(
        parses[0] in list(ast.walk(n)) for n in appenders
    ):
        raise ValueError("generated method is not attached to the Atom class")
    if not any(ast.unparse(n.args[0]) == "reference" for n in appenders):
        raise ValueError("derivation helper is not attached to the Atom class")
    body = ast.parse(parses[0].args[0].value)
    if len(body.body) != 1 or not isinstance(body.body[0], ast.FunctionDef):
        raise ValueError("unsupported generated method")
    return generated_method(body)


def _run_lean(code, lean):
    with tempfile.TemporaryDirectory() as tmp:
        leanfile = Path(tmp) / "check.lean"
        leanfile.write_text(code)
        return subprocess.run(
            [lean, str(leanfile)],
            capture_output=True,
            text=True,
            timeout=45,
        )


def analyze(checkout, lean):
    result = {"findings": [], "unresolved": []}
    generators = list(checkout.glob(GENERATOR))
    helpers = list(checkout.glob(HELPER))
    if len(generators) != 1 or len(helpers) != 1:
        generator_detail = "expected one helper and one derived-property "
        generator_detail += "generator"
        result["unresolved"].append(
            {
                "path": ".",
                "detail": generator_detail,
            }
        )
        return result
    rel = str(generators[0].relative_to(checkout))
    try:
        dynamic = extract(generators[0], helpers[0])
        code = f"def dynamicRead : Bool := {str(dynamic).lower()}\n"
        code += (
            'def derive (version : Nat) : String := "AN-S-1@" ++ '
            "toString version\n"
            "def read (initial current : Nat) : String := if dynamicRead then "
            "derive current else derive initial\n"
            "#eval read 1 2 != derive 2\n"
        )
        run = _run_lean(code, lean)
        if run.returncode or run.stdout.strip() not in ("true", "false"):
            raise ValueError("Lean failed: " + run.stderr + run.stdout)
        if run.stdout.strip() == "true":
            result["findings"].append(
                {
                    "path": rel,
                    "detail": "Ref ID remains the constructor value after a "
                    "valid Atom version change.",
                }
            )
    except (
        OSError,
        SyntaxError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        result["unresolved"].append({"path": rel, "detail": str(error)})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.checkout, args.lean)))


if __name__ == "__main__":
    main()
