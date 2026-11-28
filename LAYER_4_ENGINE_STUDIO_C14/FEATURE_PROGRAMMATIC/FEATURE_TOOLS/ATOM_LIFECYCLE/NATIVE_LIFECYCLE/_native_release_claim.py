"""Read a literal release command from native Project Config."""

import ast
from pathlib import Path

from ...ADAPTERS_C30.ADAPTERS_C30__shared import protected


def _parse_release_claim(source):
    statements = ast.parse(source).body
    call = (
        statements[0].value
        if len(statements) == 1 and isinstance(statements[0], ast.Expr)
        else None
    )
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "release_command"
        or call.args
        or len(call.keywords) != 2
    ):
        raise ValueError("Expected one release_command Formal Claim")
    fields = {
        kw.arg: kw.value.value
        for kw in call.keywords
        if isinstance(kw.value, ast.Constant)
    }
    if fields.keys() != {"operation", "entrypoint"}:
        raise ValueError(
            "Release command requires literal operation and entrypoint"
        )
    operation, entrypoint = fields["operation"], fields["entrypoint"]
    if (
        operation not in ("local", "public")
        or not isinstance(entrypoint, str)
        or not entrypoint.isprintable()
    ):
        raise ValueError("Invalid release command operation or entrypoint")
    path = Path(entrypoint)
    if (
        path.is_absolute()
        or ".." in path.parts
        or protected(path)
        or path.suffix != ".py"
        or path.as_posix() != entrypoint
    ):
        raise ValueError(
            "Release entrypoint must be a Project-relative Python file"
        )
    return operation, path
