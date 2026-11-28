"""Measure structured Python models and JavaScript source in suite roots."""

from pathlib import Path
import subprocess
import sys
import tokenize

from ..source_inventory import source_inventory__shared as source_comments
from . import source_python_models, source_web_languages
from ..suite_config import load_suite_config

SUFFIXES = {".py", ".js", ".jsx", ".mjs", ".cjs", ".html", ".htm", ".svelte"}


def source_language_findings(root: Path) -> list[str]:
    findings, svelte = [], []
    for relative in source_comments.source_paths(root, SUFFIXES, (".",)):
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
                source_python_models.python_model_findings(relative, source)
            )
        elif relative.suffix == ".svelte":
            svelte.append(relative)
        else:
            findings.extend(
                source_web_languages.web_language_findings(root, relative)
            )
    if svelte:
        findings.extend(
            source_web_languages.svelte_language_findings(root, svelte)
        )
    return sorted(findings)


def _enabled(root: Path) -> bool:
    try:
        config = load_suite_config(root)
    except FileNotFoundError:
        return False
    settings = config.get("tool", {}).get("anechoic", {}).get("test_suite", {})
    enabled = settings.get("enforce_source_languages", False)
    if type(enabled) is not bool:
        raise ValueError("enforce_source_languages must be a boolean")
    return enabled


def check(root: Path) -> int:
    try:
        enabled = _enabled(root)
        findings = source_language_findings(root)
    except (
        OSError,
        ValueError,
        SyntaxError,
        subprocess.SubprocessError,
    ) as error:
        print(f"Static source language check failed: {error}", file=sys.stderr)
        return 1
    advisory = tuple(
        f": {message}" for message in source_python_models.ADVISORY_FINDINGS
    )
    review = [item for item in findings if item.endswith(advisory)]
    blocking = [item for item in findings if not item.endswith(advisory)]
    print(
        f"Static check: source languages: {len(blocking)} findings", flush=True
    )
    if review:
        print(f"Source language review: {len(review)} candidates", flush=True)
        print("\n".join(review), flush=True)
    if enabled and blocking:
        print("\n".join(blocking), file=sys.stderr)
    return int(enabled and bool(blocking))
