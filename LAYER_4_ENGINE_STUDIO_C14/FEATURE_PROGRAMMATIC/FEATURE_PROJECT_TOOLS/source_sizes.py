"""Check the 300-line module and 45-line function limits."""

import ast
import json
from pathlib import Path
import subprocess
import sys
import tokenize

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_config import load_suite_config

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import source_comments as sources

MODULE_LIMIT = 300
FUNCTION_LIMIT = 45
WEB_FUNCTIONS = {".js", ".mjs", ".cjs", ".ts", ".cts", ".svelte"}


def nonblank_lines(lines):
    return sum(bool(line.strip()) for line in lines)


def check_module(path, source):
    lines = source.split("\n")
    size = nonblank_lines(lines)
    if size > MODULE_LIMIT:
        yield f"{path}: module has {size} lines (maximum {MODULE_LIMIT})"


def python_functions(path, source):
    lines = source.split("\n")
    for node in ast.walk(ast.parse(source, filename=str(path))):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = [item.lineno for item in node.decorator_list]
            start = min([node.lineno, *decorators])
            size = nonblank_lines(lines[start - 1:node.end_lineno])
            yield start, node.name, size
        elif isinstance(node, ast.Lambda):
            size = nonblank_lines(lines[node.lineno - 1:node.end_lineno])
            yield node.lineno, "<lambda>", size


def web_functions(root, files):
    script = sources.FRONTEND / "scripts/source-function-sizes.ts"
    result = subprocess.run(
        ["node", str(root / script)],
        input=json.dumps(files), encoding="utf-8",
        stdout=subprocess.PIPE, check=True, timeout=60,
    )
    return json.loads(result.stdout)


def check_functions(path, functions):
    return [
        f"{path}:{line}: {name} has {size} lines (maximum {FUNCTION_LIMIT})"
        for line, name, size in sorted(functions) if size > FUNCTION_LIMIT
    ]



def source_size_findings(root: Path) -> list[str]:
    """Measure the tracked and nonignored source files under the suite roots."""
    findings, web = [], []
    for relative in sources.source_paths(root):
        if relative.suffix not in WEB_FUNCTIONS | {".py"}:
            continue
        path = root / relative
        if path.resolve() != path:
            raise ValueError(f"{relative}: source path traverses a symbolic link")
        if not path.is_file():
            continue
        if relative.suffix == ".py":
            with tokenize.open(path) as file:
                source = file.read()
            findings.extend(check_functions(relative, python_functions(relative, source)))
        else:
            source = path.read_text(encoding="utf-8")
            web.append({"path": relative.as_posix(), "source": source})
        findings.extend(check_module(relative, source))
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
        if not _enabled(root):
            return 0
        print("Static check: source size", flush=True)
        findings = source_size_findings(root)
    except (OSError, ValueError, SyntaxError, subprocess.SubprocessError) as error:
        print(f"Static source size check failed: {error}", file=sys.stderr)
        return 1
    if findings:
        print("\n".join(findings), file=sys.stderr)
        print(f"{len(findings)} source size violations", file=sys.stderr)
    return int(bool(findings))
