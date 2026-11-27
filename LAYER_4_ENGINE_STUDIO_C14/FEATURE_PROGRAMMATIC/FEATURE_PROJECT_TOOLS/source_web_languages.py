"""Require TypeScript for executable web source in the authored inventory."""

from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.source_comments import (
    FRONTEND,
    ROOT,
)


JAVASCRIPT_SUFFIXES = frozenset({".js", ".mjs", ".cjs", ".jsx"})
HTML_SUFFIXES = frozenset({".html", ".htm"})
JAVASCRIPT_MIME_TYPES = frozenset(
    {
        "application/ecmascript",
        "application/javascript",
        "application/x-ecmascript",
        "application/x-javascript",
        "text/ecmascript",
        "text/javascript",
        "text/jscript",
        "text/livescript",
        "text/x-ecmascript",
        "text/x-javascript",
        *(f"text/javascript1.{minor}" for minor in range(6)),
    }
)


class _InlineScripts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(scripting=True)
        self.lines: list[int] = []
        self.script_line: int | None = None

    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return
        attributes = dict(reversed(attrs))
        if "src" in attributes:
            return
        language = attributes.get("language")
        default_type = f"text/{language}" if language else ""
        script_type = (
            (attributes.get("type", default_type) or "").strip().lower()
        )
        if script_type in JAVASCRIPT_MIME_TYPES or script_type in {
            "",
            "module",
        }:
            self.script_line = self.getpos()[0]

    def handle_data(self, data):
        if self.script_line is not None and data.strip():
            self.lines.append(self.script_line)
            self.script_line = None

    def handle_endtag(self, tag):
        if tag == "script":
            self.script_line = None


def web_language_findings(root: Path, path: Path) -> list[str]:
    "Report JavaScript files and inline scripts in one authored inventory path."
    suffix = path.suffix.lower()
    if suffix in JAVASCRIPT_SUFFIXES:
        return [f"{path}: authored JavaScript source must use TypeScript"]
    if suffix not in HTML_SUFFIXES:
        return []
    scripts = _InlineScripts()
    scripts.feed((root / path).read_text(encoding="utf-8"))
    scripts.close()
    return [
        (
            f"{path}"
            ":"
            f"{line}"
            ": inline JavaScript must be built from TypeScript source"
        )
        for line in scripts.lines
    ]


def svelte_language_findings(root: Path, paths: list[Path]) -> list[str]:
    """Use the framework's Svelte compiler to check all selected Components."""
    sources = [
        {
            "path": str(path),
            "source": (root / path).read_text(encoding="utf-8"),
        }
        for path in paths
        if path.suffix.lower() == ".svelte"
    ]
    if not sources:
        return []
    script = ROOT / FRONTEND / "scripts/source-web-languages.ts"
    result = subprocess.run(
        ["node", str(script)],
        input=json.dumps(sources),
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            result.stderr.strip() or "Svelte language check failed"
        )
    return json.loads(result.stdout)
