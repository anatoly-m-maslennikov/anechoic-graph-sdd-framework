"""Check module bytes and function length and nesting."""

import ast
import json
from pathlib import Path
import subprocess
import sys
import tokenize

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_config import (
    load_suite_config,
)

from . import source_inventory__shared as sources
from ..source_folders import folder_findings

MODULE_LIMIT_BYTES = 6 * 1024
FUNCTION_LIMIT = 45
NESTING_LIMIT = 4
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_SCOPES = (*_FUNCTIONS, ast.ClassDef)
_CONTROL_FLOW = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.TryStar,
    ast.Match,
)
PROGRAMMATIC_ROOT = f"{sources.CODE_ROOTS[0]}/FEATURE_PROGRAMMATIC"
WEB_FUNCTIONS = {
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".cts",
    ".jsx",
    ".tsx",
    ".mts",
    ".svelte",
}


def nonblank_lines(lines):
    return sum(bool(line.strip()) for line in lines)


def check_module(path, size_bytes):
    if size_bytes > MODULE_LIMIT_BYTES:
        yield (
            f"{path}: module has {size_bytes} bytes "
            f"(maximum {MODULE_LIMIT_BYTES})"
        )


def _nesting_depth(node):
    if isinstance(node, _SCOPES):
        return 0
    level = int(isinstance(node, _CONTROL_FLOW))
    maximum = level
    elif_node = None
    if isinstance(node, ast.If) and len(node.orelse) == 1:
        candidate = node.orelse[0]
        if (
            isinstance(candidate, ast.If)
            and node.col_offset == candidate.col_offset
        ):
            elif_node = candidate
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.stmt, ast.ExceptHandler, ast.match_case)):
            nested = _nesting_depth(child)
            maximum = max(maximum, level + nested - (child is elif_node))
    return maximum


def python_functions(path, source):
    lines = source.split("\n")
    for node in ast.walk(ast.parse(source, filename=str(path))):
        if isinstance(node, _FUNCTIONS):
            decorators = [item.lineno for item in node.decorator_list]
            start = min([node.lineno, *decorators])
            size = nonblank_lines(lines[start - 1 : node.end_lineno])
            depth = max(map(_nesting_depth, node.body))
            yield start, node.name, size, depth
        elif isinstance(node, ast.Lambda):
            size = nonblank_lines(lines[node.lineno - 1 : node.end_lineno])
            yield node.lineno, "<lambda>", size, 0


def web_functions(root, files):
    script = sources.FRONTEND / "scripts/source-function-sizes.ts"
    result = subprocess.run(
        ["node", str(root / script)],
        input=json.dumps(files),
        encoding="utf-8",
        stdout=subprocess.PIPE,
        check=True,
        timeout=60,
    )
    return json.loads(result.stdout)


def check_functions(path, functions):
    findings = []
    for line, name, size, depth in sorted(functions):
        if size > FUNCTION_LIMIT:
            findings.append(
                f"{path}:{line}: {name} has {size} lines "
                f"(maximum {FUNCTION_LIMIT})"
            )
        if depth > NESTING_LIMIT:
            findings.append(
                f"{path}:{line}: {name} has nesting depth {depth} "
                f"(maximum {NESTING_LIMIT})"
            )
    return findings


def source_size_findings(
    root: Path,
    *,
    roots: tuple[str, ...] = sources.CODE_ROOTS,
) -> list[str]:
    "Measure the tracked and nonignored source files under the suite roots."
    findings, web = [], []
    for relative in sources.source_paths(root, WEB_FUNCTIONS | {".py"}, roots):
        path = root / relative
        if path.resolve() != path:
            raise ValueError(
                f"{relative}: source path traverses a symbolic link"
            )
        if not path.is_file():
            continue
        if relative.suffix == ".py":
            with tokenize.open(path) as file:
                source = file.read()
            findings.extend(
                check_functions(relative, python_functions(relative, source))
            )
        else:
            source = path.read_text(encoding="utf-8")
            web.append({"path": relative.as_posix(), "source": source})
        findings.extend(check_module(relative, path.stat().st_size))
    if web:
        for file, functions in zip(web, web_functions(root, web), strict=True):
            findings.extend(check_functions(file["path"], functions))
    return findings


def _enabled(root: Path) -> bool:
    try:
        config = load_suite_config(root)
    except FileNotFoundError:
        return False
    settings = config.get("tool", {}).get("anechoic", {}).get("test_suite", {})
    enabled = settings.get("enforce_source_size", False)
    if type(enabled) is not bool:
        raise ValueError("enforce_source_size must be a boolean")
    return enabled


def check(root: Path) -> int:
    try:
        if _enabled(root):
            roots = sources.CODE_ROOTS
        elif (root / PROGRAMMATIC_ROOT).is_dir():
            roots = (PROGRAMMATIC_ROOT,)
        else:
            return 0
        print("Static check: source size and 67 Rule", flush=True)
        findings = source_size_findings(root, roots=roots)
        findings.extend(folder_findings(root, roots))
    except (
        OSError,
        ValueError,
        SyntaxError,
        subprocess.SubprocessError,
    ) as error:
        print(f"Static source layout check failed: {error}", file=sys.stderr)
        return 1
    if findings:
        print("\n".join(findings), file=sys.stderr)
        print(f"{len(findings)} source layout violations", file=sys.stderr)
    return int(bool(findings))
