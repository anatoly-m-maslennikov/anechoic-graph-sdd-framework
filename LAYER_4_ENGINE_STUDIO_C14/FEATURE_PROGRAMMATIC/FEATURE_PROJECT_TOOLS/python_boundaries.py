"""Check that owned Python sources import only from their own child root."""

from __future__ import annotations

import ast
import os
from pathlib import Path
import sys
import tokenize

PYTHON_CHILD_ROOTS = (
    "LAYER_4_ENGINE_STUDIO_C14",
    "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27",
    "LAYER_5_USER_SETUP_C65",
)
_EXCLUDED = frozenset({
    "archive", "archives", "build", "coverage", "dist", "dist-packages", "env",
    "generated", "gen", "history", "migration-evidence", "node_modules", "out",
    "site-packages", "target", "temp", "tmp", "vendor", "venv", "__pycache__",
})


def _sources(root: Path):
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith((".", "_anechoic_"))
                         and d.casefold() not in _EXCLUDED
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(files):
            path = Path(directory) / name
            if name.endswith(".py") and not path.is_symlink():
                yield path


def _modules(root: Path, paths: list[Path]) -> set[str]:
    modules = set()
    for path in paths:
        parts = list(path.relative_to(root).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        for end in range(1, len(parts) + 1):
            modules.add(".".join(parts[:end]))
    return modules


def _imports(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name, 0
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                target = ".".join(part for part in (module, alias.name) if part and part != "*")
                yield node.lineno, target or module, node.level
        elif (isinstance(node, ast.Call) and node.args
              and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
              and ((isinstance(node.func, ast.Name) and node.func.id == "__import__")
                   or (isinstance(node.func, ast.Attribute) and node.func.attr == "import_module"
                       and isinstance(node.func.value, ast.Name) and node.func.value.id == "importlib"))):
            name = node.args[0].value
            yield node.lineno, name.lstrip("."), len(name) - len(name.lstrip("."))


def _match_depth(target: str, modules: set[str]) -> int:
    parts = target.split(".")
    return max((end for end in range(1, len(parts) + 1)
                if ".".join(parts[:end]) in modules), default=0)


def check(repo_root: Path) -> int:
    """Print cross-child import sites and return the number of violations/errors."""
    repo_root = Path(repo_root)
    roots = {name: repo_root / name for name in PYTHON_CHILD_ROOTS}
    paths = {name: list(_sources(root)) if root.is_dir() else [] for name, root in roots.items()}
    modules = {name: _modules(roots[name], files) for name, files in paths.items()}
    errors = 0
    for owner, files in paths.items():
        for path in files:
            try:
                with tokenize.open(path) as source:
                    tree = ast.parse(source.read(), filename=str(path))
            except (OSError, SyntaxError, UnicodeError, LookupError) as exc:
                print(f"{path.relative_to(repo_root)}: {exc}", file=sys.stderr)
                errors += 1
                continue
            for line, target, level in _imports(tree):
                if level:
                    package = path.relative_to(roots[owner]).parts[:-1]
                    if level <= len(package) + 1:
                        continue
                    rest = level - len(package) - 2
                    if rest or not target:
                        continue
                first = target.split(".", 1)[0]
                sibling = next((name for name in roots if name.replace("/", ".") == target
                                or target.startswith(name.replace("/", ".") + ".")), None)
                if sibling == owner:
                    sibling = None
                if not sibling and not level and first not in roots:
                    depths = {name: _match_depth(target, inventory) for name, inventory in modules.items()}
                    best = max(depths.values())
                    matches = [name for name, depth in depths.items() if depth == best] if best else []
                    if len(matches) == 1 and matches[0] != owner:
                        sibling = matches[0]
                if sibling:
                    print(f"{path.relative_to(repo_root)}:{line}: cross-child import {target} ({sibling})", file=sys.stderr)
                    errors += 1
    return errors
