"""Select authored source files and extract Python imports without execution."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha256
import io
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tokenize
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class ImportSite:
    module: str
    name: str | None
    level: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Source:
    language: str
    status: str
    signature: str
    imports: tuple[ImportSite, ...] = ()
    error_message: str | None = None


_SUFFIX_LANGUAGES = {
    ".py": "python",
    ".sh": "script",
    ".js": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".svelte": "svelte",
    ".bash": "script",
    ".bat": "batch",
    ".c": "c",
    ".cc": "cpp",
    ".cljs": "clojure",
    ".clj": "clojure",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".cxx": "cpp",
    ".dart": "dart",
    ".el": "elisp",
    ".ex": "elixir",
    ".exs": "elixir",
    ".fish": "script",
    ".fs": "fsharp",
    ".go": "go",
    ".hs": "haskell",
    ".java": "java",
    ".jl": "julia",
    ".jsx": "javascript",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".lua": "lua",
    ".m": "objective-c",
    ".mm": "objective-cpp",
    ".ml": "ocaml",
    ".php": "php",
    ".pl": "perl",
    ".ps1": "powershell",
    ".r": "r",
    ".rb": "ruby",
    ".rs": "rust",
    ".scala": "scala",
    ".swift": "swift",
    ".tsx": "typescript",
    ".zig": "zig",
    ".zsh": "script",
}
_RESOLUTION_INPUTS = frozenset({".gitignore", "pyproject.toml", "package.json"})
_EXCLUDED_PARTS = frozenset({
    ".anechoic_archive", ".anechoic_install", ".anechoic_legacy", ".anechoic_runtime", ".anechoic_tmp",
    ".anechoic_anechoic", ".cache", ".git", ".hg", ".mypy_cache", ".nox", ".pytest_cache",
    ".ruff_cache", ".runtime", ".svn", ".tox", ".venv", "__pycache__", "archive", "archives", "build", "coverage",
    "dist", "dist-packages", "env", "generated", "gen", "history", "node_modules", "out",
    "migration-evidence", "site-packages", "target", "temp", "tmp", "vendor", "venv",
})


def _root_path(root: Path) -> Path:
    path = Path(root).resolve()
    if not path.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    return path


def _relative(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    result = path.as_posix()
    return None if result == "." else result


def _relative_path(root: Path, path: Path) -> str | None:
    try:
        return PurePosixPath(path.relative_to(root).as_posix()).as_posix()
    except ValueError:
        return None


def excluded_source_path(relative: str, *, directory: bool = False) -> bool:
    parts = PurePosixPath(relative).parts
    folder_parts = parts if directory else parts[:-1]
    return any(part.startswith(".") for part in folder_parts) or any(
        part.casefold() in _EXCLUDED_PARTS for part in parts
    )


def _has_symlink_ancestor(root: Path, path: Path) -> bool:
    current = path
    while current != root:
        if current.is_symlink():
            return True
        current = current.parent
    return root.is_symlink()


def _suffix_language(path: Path) -> str | None:
    return _SUFFIX_LANGUAGES.get(path.suffix.casefold())


def _shebang_language(first_line: bytes) -> str | None:
    if not first_line.startswith(b"#!"):
        return None
    text = first_line.decode("ascii", "ignore").casefold()
    if "python" in text:
        return "python"
    if any(name in text for name in ("node", "deno", "bun", "tsx", "ts-node")):
        return "javascript"
    return "script"


def _file_language(path: Path) -> str | None:
    language = _suffix_language(path)
    if language is not None:
        return language
    try:
        with path.open("rb") as handle:
            language = _shebang_language(handle.readline(512))
    except OSError:
        language = None
    return language or ("executable" if os.access(path, os.X_OK) else None)


def _iter_files(root: Path, *, source_only: bool = True) -> Iterable[Path]:
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name, reverse=True)
        except FileNotFoundError:
            continue
        for entry in entries:
            if entry.is_symlink():
                continue
            path = Path(entry.path)
            is_directory = entry.is_dir(follow_symlinks=False)
            if entry.name == ".git" or (source_only and excluded_source_path(
                path.relative_to(root).as_posix(), directory=is_directory
            )):
                continue
            if is_directory:
                pending.append(path)
            elif entry.is_file(follow_symlinks=False):
                yield path


def _git_ignored(root: Path, relatives: Iterable[str]) -> set[str]:
    values = tuple(sorted(set(relatives)))
    if not values:
        return set()
    try:
        repo = Path(subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()).resolve()
        root_relative = root.relative_to(repo)
        repo_values = {
            (root_relative / PurePosixPath(relative)).as_posix(): relative
            for relative in values
        }
        payload = "\0".join(repo_values) + "\0"
        result = subprocess.run(
            ["git", "-C", str(repo), "check-ignore", "--stdin", "-z"],
            input=payload.encode(), capture_output=True, check=False,
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        return set()
    if result.returncode not in {0, 1}:
        detail = result.stderr.decode("utf-8", "replace").strip() or f"exit {result.returncode}"
        raise RuntimeError(f"Git ignore check failed. {detail}")
    ignored = set()
    for item in result.stdout.split(b"\0"):
        if item:
            try:
                ignored.add(repo_values[item.decode()])
            except (KeyError, UnicodeDecodeError):
                pass
    return ignored


def _input_files(root: Path, changed: set[str] | None) -> Iterable[Path]:
    if changed is None:
        yield from _iter_files(root)
        return
    for relative in changed:
        if excluded_source_path(relative):
            continue
        path = _event_path(root, relative)
        if path is None:
            continue
        if path.is_dir():
            if not excluded_source_path(relative, directory=True):
                yield from _iter_files(path)
        elif path.is_file():
            yield path


def _discover(root: Path, include: tuple[str, ...], changed: set[str] | None) -> list[tuple[str, Path, str]]:
    candidates: dict[str, tuple[Path, str]] = {}
    for path in _input_files(root, changed):
        relative = _relative_path(root, path)
        language = _file_language(path)
        if relative is not None and language is not None:
            candidates[relative] = (path, language)

    explicit = set(map(_relative, include))
    ignored = _git_ignored(root, candidates.keys() - explicit)
    return [
        (relative, path, language)
        for relative, (path, language) in sorted(candidates.items())
        if relative not in ignored
    ]


def _stat_signature(path: Path) -> str:
    try:
        stat = path.stat()
        value = ":".join(str(getattr(stat, field)) for field in (
            "st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns",
        ))
    except OSError:
        value = f"missing:{path}"
    return f"stat:{sha256(value.encode()).hexdigest()}"


class _Imports(ast.NodeVisitor):
    def __init__(self) -> None:
        self.sites: list[ImportSite] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.sites.extend(
            ImportSite(alias.name, None, 0, node.lineno, node.col_offset)
            for alias in node.names
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.sites.extend(
            ImportSite(node.module or "", alias.name, node.level, node.lineno, node.col_offset)
            for alias in node.names
        )
        self.generic_visit(node)


def _parse(relative: str, language: str, data: bytes, signature: str) -> Source:
    if language != "python":
        return Source(language, "unsupported", signature)
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        tree = ast.parse(data.decode(encoding), filename=relative)
    except (LookupError, SyntaxError, UnicodeError, ValueError) as error:
        print(f"import graph: {relative}: parse error: {error}", file=sys.stderr)
        return Source(language, "parse_error", signature)
    visitor = _Imports()
    visitor.visit(tree)
    return Source(language, "parsed", signature, tuple(visitor.sites))


def _scan(relative: str, path: Path, language: str, previous: Source | None) -> Source:
    signature = _stat_signature(path)
    if (previous is not None and previous.status != "read_error"
            and previous.language == language and previous.signature == signature):
        return previous
    try:
        if language == "python":
            data = path.read_bytes()
        else:
            with path.open("rb") as handle:
                data = handle.read(1)
    except OSError as error:
        print(f"import graph: {relative}: read error: {error}", file=sys.stderr)
        return Source(language, "read_error", signature, error_message=str(error))
    return _parse(relative, language, data, signature)


def capture(
    root: Path, previous: Mapping[str, Source] | None, include: tuple[str, ...] = (),
    *, changes: list[dict[str, str | None]] | None = None,
) -> dict[str, Source]:
    """Capture selected source, reusing an unchanged file's parsed result."""
    root = _root_path(root)
    prior = previous or {}
    changed = _changed_paths(changes) if changes is not None else None
    if changed and any(PurePosixPath(path).name == ".gitignore" for path in changed):
        changed = None
    if changed is not None:
        changed.update(path for path, source in prior.items() if source.status == "read_error")
    retained = {} if changed is None else {
        path: source for path, source in prior.items()
        if not any(path == item or path.startswith(item + "/") for item in changed)
    }
    retained.update({
        relative: _scan(relative, path, language, prior.get(relative))
        for relative, path, language in _discover(root, include, changed)
    })
    return retained


def _changed_paths(changes: list[dict[str, str | None]]) -> set[str]:
    return {relative for change in changes for key in ("old_path", "new_path")
            if (relative := _relative(change.get(key))) is not None}


def _directory_has_source(directory: Path) -> bool:
    return any(_file_language(path) is not None for path in _iter_files(directory))


def _touches_previous(relative: str, previous: Mapping[str, Source]) -> bool:
    return relative in previous or any(item.startswith(relative + "/") for item in previous)


def _event_path(root: Path, relative: str) -> Path | None:
    path = root.joinpath(*PurePosixPath(relative).parts)
    if _has_symlink_ancestor(root, path):
        return None
    return path if path.resolve(strict=False).is_relative_to(root) else None


def _path_relevant(root: Path, relative: str, previous: Mapping[str, Source]) -> bool:
    if excluded_source_path(relative):
        return False
    if _touches_previous(relative, previous):
        return True
    path = _event_path(root, relative)
    if path is None:
        return False
    if PurePosixPath(relative).name.casefold() in _RESOLUTION_INPUTS:
        return True
    if path.is_dir():
        return not excluded_source_path(relative, directory=True) and _directory_has_source(path)
    return _suffix_language(path) is not None or _file_language(path) is not None


def relevant_change(
    root: Path, changes: list[dict[str, str | None]], previous: Mapping[str, Source] | None,
) -> bool:
    """Return whether a watcher batch can change source inventory or resolution."""
    root = Path(root).resolve()
    prior = previous or {}
    return any(_path_relevant(root, path, prior) for path in _changed_paths(changes))


__all__ = ["ImportSite", "Source", "capture", "excluded_source_path", "relevant_change"]
