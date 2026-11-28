"""Observe the admitted C30 exports and compare their generated Lean model."""

import hashlib
import json
import types
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds,
    source_body,
)


def lean_bytes(value):
    return "[" + ", ".join(map(str, value)) + "]"


def _loaded_matches(source, path):
    compiled = compile(source, str(path), "exec")
    expected = {
        c.co_name: c
        for c in compiled.co_consts
        if isinstance(c, types.CodeType)
    }
    fields = (
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_argcount",
        "co_kwonlyargcount",
    )
    return all(
        fn.__name__ in expected
        and all(
            getattr(fn.__code__, field)
            == getattr(expected[fn.__name__], field)
            for field in fields
        )
        for fn in (frontmatter_bounds, source_body)
    )


def observe(root, evidence, source, cases, *, paths=None):
    path = Path(root) / evidence["source"]
    if hashlib.sha256(source).hexdigest() != evidence["source_sha256"]:
        raise ValueError("carrier source changed during analysis")
    if not _loaded_matches(source, path) or any(
        Path(fn.__code__.co_filename).resolve() != path.resolve()
        for fn in (frontmatter_bounds, source_body)
    ):
        raise ValueError(
            "loaded carrier functions do not match the analyzed path"
        )
    rows = []
    for name, raw in cases.items():
        location = Path(paths[name] if paths is not None else "carrier.md")
        bounds = frontmatter_bounds(raw)
        try:
            body = list(source_body(raw, location))
            error = None
        except ValueError as exc:
            body, error = None, str(exc)
        row = {
            "name": name,
            "raw": list(raw),
            "bounds": bounds,
            "body": body,
            "error": error,
        }
        if paths is not None:
            row["path"] = str(location)
        rows.append(row)
    return rows


def python_checks(row):
    raw = lean_bytes(row["raw"])
    bounds = row["bounds"]
    expected = (
        "none"
        if bounds is None
        else f"some ({bounds[0]}, {bounds[1]}, {bounds[2]})"
    )
    path = json.dumps(row.get("path", "carrier.md"))
    body = f"match sourceBody {raw} {path} with "
    if row["body"] is None:
        body += (
            f"| .error e => e == {json.dumps(row['error'])} | .ok _ => false"
        )
    else:
        body += (
            f"| .ok b => b == {lean_bytes(row['body'])} | .error _ => false"
        )
    return [f"frontmatterBounds {raw} == {expected}", f"({body})"]
