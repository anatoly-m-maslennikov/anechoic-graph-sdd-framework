"""Check line length on new and edited lines in executable source."""

import argparse
from difflib import SequenceMatcher
from functools import cache
import json
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, check_output, run
import sys

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_config import load_suite_config

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.source_comments import CODE_ROOTS, ROOT

SOURCE_ROOTS = (*CODE_ROOTS, ".github/workflows")
NEXT_LINE_DIRECTIVE = b"editorconfig-checker-disable-" b"next-line"


def git(root, *args):
    return check_output(("git", *args), cwd=root, timeout=60)


def changed_files(root, base):
    changes = git(
        root, "diff", "--no-ext-diff", "--name-status", "-z",
        "--find-renames", "--diff-filter=AMRT", base, "--", *SOURCE_ROOTS,
    )
    fields = iter(changes.decode().split("\0")[:-1])
    files = {}
    for status in fields:
        previous = next(fields)
        current = next(fields) if status.startswith("R") else previous
        files[current] = None if status == "A" else previous
    untracked = git(
        root, "ls-files", "--others", "--exclude-standard", "-z",
        "--", *SOURCE_ROOTS,
    )
    for path in untracked.decode().split("\0")[:-1]:
        files.setdefault(path, None)
    return files


def new_lines(before, after):
    matcher = SequenceMatcher(
        None, before.splitlines(), after.splitlines(), autojunk=False,
    )
    return {
        line for tag, _, _, start, end in matcher.get_opcodes()
        if tag in {"insert", "replace"} for line in range(start + 1, end + 1)
    }


def checker_findings(root, paths):
    result = run(
        ("ec", "-no-color", "-format", "codeclimate", *paths),
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    if result.returncode == 0:
        return []
    message = result.stderr.strip() or "EditorConfig Checker failed"
    if result.returncode != 1 or not result.stdout.strip():
        raise ValueError(message)
    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(result.stdout.strip()) from error
    if not findings or result.stderr.strip():
        raise ValueError(message)
    return findings


def line_length_findings(root, base_ref):
    base = git(
        root, "rev-parse", "--verify", "--end-of-options",
        f"{base_ref}^{{commit}}",
    ).decode().strip()
    files = {
        path: previous for path, previous in changed_files(root, base).items()
        if (root / path).is_file() and not (root / path).is_symlink()
    }
    if not files:
        return []

    @cache
    def edited_lines(path):
        before = git(root, "show", f"{base}:{files[path]}")
        return new_lines(before, (root / path).read_bytes())

    findings = [
        (path, number, "Next-line suppression is disabled")
        for path in files
        for number, line in enumerate(
            (root / path).read_bytes().splitlines(), 1,
        )
        if NEXT_LINE_DIRECTIVE in line
    ]
    for item in checker_findings(root, files):
        location = item["location"]
        path = location["path"]
        start = location["lines"]["begin"]
        end = start + location["lines"]["end"]
        for line in range(start, end + 1):
            if files[path] is None or line in edited_lines(path):
                findings.append((path, line, item["description"]))
    return sorted(findings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", default="HEAD", help="Git base (default HEAD)",
    )
    parser.add_argument("--project-root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.project_root.resolve()
    try:
        config = load_suite_config(root)
        settings = config.get("tool", {}).get("anechoic", {})
        enabled = settings.get("test_suite", {}).get(
            "enforce_source_line_length", False,
        )
        if type(enabled) is not bool:
            raise ValueError("enforce_source_line_length must be a boolean")
        if not enabled:
            print("Source line length check is disabled")
            return 0
        findings = line_length_findings(root, args.base)
    except FileNotFoundError as error:
        if error.filename == "ec":
            print(
                "Install the checker with "
                "uv tool install editorconfig-checker==3.11.1",
                file=sys.stderr,
            )
        else:
            print(f"Line length check failed: {error}", file=sys.stderr)
        return 2
    except (OSError, CalledProcessError, TimeoutExpired, ValueError) as error:
        print(f"Line length check failed: {error}", file=sys.stderr)
        return 2
    for path, line, description in findings:
        print(f"{path}:{line}: {description}")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
