"""Identify source languages by file suffix, shebang, or executable bit."""

from pathlib import Path
import stat


_SUFFIX_LANGUAGES = {
    ".py": "python",
    ".sh": "script",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".cts": "typescript",
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
    if language is not None:
        return language
    try:
        executable = path.stat().st_mode & (
            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
    except OSError:
        return None
    return "executable" if executable else None
