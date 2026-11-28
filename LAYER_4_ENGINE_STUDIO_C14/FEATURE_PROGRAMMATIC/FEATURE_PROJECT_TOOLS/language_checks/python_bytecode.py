"""Find statically visible Python launches without bytecode containment."""

import ast
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tokenize

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    source_inventory.source_inventory__shared import (
    CODE_ROOTS,
    GENERATED_STATE_DIRECTORIES,
    repository_paths,
)

from ._python_launch_args import safe_prefix as safe_prefix
from ._python_launch_args import unsafe

DOCKER_COMMAND = re.compile(
    r"^(?:RUN(?: --\S+)*|ENTRYPOINT|CMD|HEALTHCHECK(?: --\S+)* CMD)\s+"
)


def literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "sys"
        and node.attr == "executable"
    ):
        return "python"
    if isinstance(node, ast.JoinedStr):
        return "".join(literal(item) for item in node.values)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
    ):
        return literal(node.args[0])
    if isinstance(node, ast.Starred):
        return "<spread>"
    return "<dynamic>"


_LAUNCH_CALLS = {
    "run",
    "Popen",
    "call",
    "check_call",
    "check_output",
    "bounded_run",
    "execv",
    "execve",
    "execvp",
    "execvpe",
}


def _python_call_value(node, found):
    value = None
    name = (
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else getattr(node.func, "id", "")
    )
    if name in _LAUNCH_CALLS:
        value = (
            node.args[1]
            if name.startswith("exec") and len(node.args) > 1
            else node.args[0]
        )
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            found.extend(
                value.lineno + line - 1 for line in shell_findings(value.value)
            )
    elif (
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "py_compile"
        and name == "compile"
        and len(node.args) == 1
        and not any(
            item.arg == "cfile"
            and not (
                isinstance(item.value, ast.Constant)
                and item.value.value is None
            )
            for item in node.keywords
        )
    ):
        found.append(node.lineno)
    return value


def python_findings(source):
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        value = None
        if isinstance(node, ast.Call) and node.args:
            value = _python_call_value(node, found)
        elif isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name)
                and target.id in {"command", "cmd", "argv", "args"}
                for target in node.targets
            ):
                value = node.value
        if isinstance(value, (ast.List, ast.Tuple)) and len(value.elts) > 1:
            tokens = [literal(item) for item in value.elts]
            if unsafe(tokens):
                found.append(value.lineno)
    return found


def _shell_lines(source, markdown):
    fence, pending = False, ""
    for number, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if markdown and stripped.startswith("```"):
            fence = (
                not fence
                if fence
                else stripped.lower()
                in {"```sh", "```shell", "```bash", "```console"}
            )
            continue
        if markdown and not fence:
            continue
        if stripped.startswith("#") and not stripped.startswith("#!"):
            continue
        if not pending:
            start = number
        pending += stripped.removeprefix("$ ").removeprefix("#!")
        if pending.endswith("\\"):
            pending = pending[:-1] + " "
            continue
        yield start, pending
        pending = ""


def shell_findings(source, markdown=False, docker=False):
    found = []
    for number, line in _shell_lines(source, markdown):
        if docker:
            directive = DOCKER_COMMAND.match(line)
            if directive is None:
                continue
            line = line[directive.end() :]
            if re.match(r'^\[\s*"', line):
                if unsafe(json.loads(line)):
                    found.append(number)
                continue
        try:
            lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|")
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            continue
        start = 0
        for end, token in enumerate([*tokens, ";"]):
            if token and all(character in ";&|" for character in token):
                if unsafe(tokens[start:end]):
                    found.append(number)
                    break
                start = end + 1
    return found


def _yaml_command(node):
    line = node.start_mark.line + 1
    if isinstance(node, yaml.ScalarNode):
        offset = line if node.style in {"|", ">"} else line - 1
        return [offset + found for found in shell_findings(node.value)]
    if isinstance(node, yaml.SequenceNode) and all(
        isinstance(child, yaml.ScalarNode) for child in node.value
    ):
        tokens = [child.value for child in node.value]
        if tokens[:1] == ["CMD-SHELL"]:
            return (
                [line]
                if len(tokens) == 2 and shell_findings(tokens[1])
                else []
            )
        return [line] if unsafe(tokens) else []
    return []


def yaml_findings(source):
    nodes = list(yaml.compose_all(source, Loader=yaml.SafeLoader))
    seen, result = set(), []
    while nodes:
        node = nodes.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, yaml.MappingNode):
            for key, value in node.value:
                if key.value in ("run", "command", "entrypoint", "test"):
                    result.extend(_yaml_command(value))
                elif isinstance(value, (yaml.MappingNode, yaml.SequenceNode)):
                    nodes.append(value)
        elif isinstance(node, yaml.SequenceNode):
            nodes.extend(node.value)
    return result


def paths(root):
    roots = (
        *CODE_ROOTS,
        ".github",
        ":(top,glob)*.md",
        ":(top,glob)*.sh",
        ":(top,glob)*.py",
    )
    return sorted(repository_paths(root, roots))


def findings(root):
    result = []
    for relative in paths(root):
        if any(
            part.lower()
            in {
                "archive",
                "archives",
                "archived",
                "node_modules",
                "dist",
                "build",
            }
            for part in relative.parts
        ):
            continue
        path = root / relative
        if not path.is_file() or path.is_symlink():
            continue
        if relative.suffix == ".py":
            with tokenize.open(path) as file:
                source = file.read()
            lines = python_findings(source)
            if source.startswith("#!"):
                lines.extend(
                    shell_findings(source.splitlines()[0] + " __script__")
                )
        elif relative.suffix in {".yml", ".yaml"}:
            lines = yaml_findings(path.read_text(encoding="utf-8"))
        elif (
            relative.suffix in {".sh", ".bash", ".md"}
            or relative.name == "Dockerfile"
        ):
            source = path.read_text(encoding="utf-8")
            lines = shell_findings(
                source, relative.suffix == ".md", relative.name == "Dockerfile"
            )
        else:
            continue
        result.extend(
            f"{relative}:{line}: Python launch may write bytecode "
            "outside .anechoic_tmp"
            for line in sorted(set(lines))
        )
    return result


def cache_findings(root):
    excluded = {".git", "node_modules", *GENERATED_STATE_DIRECTORIES}
    for directory, children, _ in os.walk(root):
        parent = Path(directory)
        if "__pycache__" in children:
            children.remove("__pycache__")
            relative = (parent / "__pycache__").relative_to(root)
            yield f"{relative}: bytecode cache outside .anechoic_tmp"
        children[:] = [name for name in children if name not in excluded]


def check(root: Path) -> int:
    try:
        print("Static check: Python bytecode", flush=True)
        violations = [*findings(root), *sorted(cache_findings(root))]
    except (
        OSError,
        ValueError,
        SyntaxError,
        subprocess.SubprocessError,
        yaml.YAMLError,
    ) as error:
        print(f"Static Python bytecode check failed: {error}", file=sys.stderr)
        return 1
    if violations:
        print("\n".join(violations), file=sys.stderr)
        print(f"{len(violations)} Python bytecode violations", file=sys.stderr)
    return int(bool(violations))
