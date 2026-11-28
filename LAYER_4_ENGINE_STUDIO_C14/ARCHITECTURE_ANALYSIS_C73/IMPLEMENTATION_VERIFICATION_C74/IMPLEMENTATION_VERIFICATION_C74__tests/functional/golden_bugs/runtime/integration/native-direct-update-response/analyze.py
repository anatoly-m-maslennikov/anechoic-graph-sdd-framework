"Check native direct-update response compatibility in a historical checkout."

import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def shape(node):
    return ast.dump(node, include_attributes=False)


def discover(root):
    found = []
    for path in root.glob("LAYER_*/**/registry_lifecycle_provider.py"):
        if any(
            x in {(".git"), (".venv"), ("node_modules"), ("tests")}
            or x.endswith(("__tests"))
            for x in path.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
            if "class NativeLifecycleProvider" not in text:
                continue
            tree = ast.parse(text)
        except OSError, UnicodeError, SyntaxError:
            continue
        classes = [
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef)
            and n.name == ("NativeLifecycleProvider")
        ]
        if classes:
            found.extend((path, tree, n) for n in classes)
    if len(found) != 1:
        raise ValueError(
            f"Expected one native lifecycle provider, found {len(found)}"
        )
    return found[0]


def ignorable(node):
    if isinstance(node, ast.Pass) or (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    ):
        return True
    return (
        isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and all(
            isinstance(target, ast.Name)
            and target.id not in {"response", "value", "name", "arguments"}
            for target in node.targets
        )
    )


def branch_expression(tree, cls):
    methods = [
        n
        for n in cls.body
        if isinstance(n, ast.AsyncFunctionDef) and n.name == ("call")
    ]
    if len(methods) != 1:
        raise ValueError("Unsupported provider call")
    fn = methods[0]
    body = [n for n in fn.body if not ignorable(n)]
    template = (
        "async def call(self, name, arguments):\n    with"
        " anyio.CancelScope(shield=True):\n        value "
        "= await anyio.to_thread.run_sync(self.owner.life"
        "cycle, name, arguments)\n    response = _result("
        "value)\n    pass\n    return response\n"
    )
    expected = ast.parse(template).body[0]
    if len(body) != 4 or any(
        shape(body[i]) != shape(expected.body[i]) for i in (0, 1, 3)
    ):
        raise ValueError("Unsupported provider call shell")
    branch = body[2]
    old = """if response['status'] == 'completed':
    for field in ('savedDraft', 'artifact'):
        if field in value:
            response[field] = value[field]
    if name == 'atom_lifecycle_update' and 'savedDraft' in response:
        response['status'] = 'draft_created'
"""
    fixed = """if response['status'] == 'completed':
    if 'savedDraft' in value:
        response['savedDraft'] = value['savedDraft']
        if name == 'atom_lifecycle_update':
            response['status'] = 'draft_created'
    if name == 'atom_lifecycle_promote_draft' and 'artifact' in value:
        response['artifact'] = value['artifact']
"""
    for text, expression in ((old, "completed && artifact"), (fixed, "false")):
        if shape(branch) == shape(ast.parse(text).body[0]):
            return expression
    raise ValueError("Unsupported native response branch")


def check_result(tree):
    funcs = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == ("_result")
    ]
    if len(funcs) != 1:
        raise ValueError("Unsupported result function")
    expected = ast.parse(
        (
            "if value.get('outcome') == 'completed' and not v"
            "alue.get('errors'):\n    if len(workflow.get('ac"
            "tion_results', ())) > 1:\n        return {'statu"
            "s': 'completed', **workflow}\n    return {'statu"
            "s': 'completed'}\n"
        )
    ).body[0]
    matches = [
        n
        for n in funcs[0].body
        if isinstance(n, ast.If) and shape(n) == shape(expected)
    ]
    if len(matches) != 1:
        raise ValueError("Unsupported ordinary completed result")


def verify(lean, expression):
    code = f"""set_option linter.unusedVariables false
def actual (completed artifact : Bool) : Bool := {expression}
def contract (returned : Bool) : Bool := !returned
#eval contract (actual true true)
"""
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "proof.lean"
        path.write_text(code, encoding="utf-8")
        result = subprocess.run(
            [lean, str(path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    if result.stdout.strip() not in {"true", "false"}:
        raise ValueError("Unexpected Lean output")
    return result.stdout.strip() == "true"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    result = {"findings": [], "unresolved": []}
    try:
        path, tree, cls = discover(args.checkout)
        check_result(tree)
        expression = branch_expression(tree, cls)
        if not verify(args.lean, expression):
            result["findings"].append(
                {
                    "path": str(path.relative_to(args.checkout)),
                    ("detail"): (
                        "A completed native direct update adds artifact t"
                        "o the prior public response shape."
                    ),
                }
            )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result["unresolved"].append({"path": ".", "detail": str(exc)})
    print(json.dumps(result))


if __name__ == "__main__":
    main()
