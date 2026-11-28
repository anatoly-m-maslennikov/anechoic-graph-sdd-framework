"""Check line length in authored source."""

import argparse
from difflib import SequenceMatcher
from functools import cache
import json
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, check_output, run
import sys

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_config import (
    load_suite_config,
)

from . import source_inventory__shared as sources
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    source_inventory.source_inventory__shared import (
    CODE_ROOTS,
    ROOT,
)

SOURCE_ROOTS = (*CODE_ROOTS, ".github/workflows")
STATIC_ROOTS = (
    "LAYER_3_DEVOPS_C80",
    "LAYER_4_ENGINE_STUDIO_C14",
    "LAYER_5_USER_SETUP_C65",
    ".github/workflows",
)
STATIC_SUFFIXES = {
    ".py",
    ".pyi",
    ".js",
    ".mjs",
    ".cjs",
    ".jsx",
    ".ts",
    ".mts",
    ".cts",
    ".tsx",
    ".svelte",
    ".html",
    ".css",
    ".lean",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".bat",
    ".cmd",
    ".sql",
}
NEXT_LINE_DIRECTIVE = b"editorconfig-checker-disable-next-line"


def git(root, *args):
    return check_output(("git", *args), cwd=root, timeout=60)


def changed_files(root, base):
    changes = git(
        root,
        "diff",
        "--no-ext-diff",
        "--name-status",
        "-z",
        "--find-renames",
        "--diff-filter=AMRT",
        base,
        "--",
        *SOURCE_ROOTS,
        *sources.GENERATED_STATE_PATHSPECS,
    )
    fields = iter(changes.decode().split("\0")[:-1])
    files = {}
    for status in fields:
        previous = next(fields)
        current = next(fields) if status.startswith("R") else previous
        files[current] = None if status == "A" else previous
    untracked = git(
        root,
        "ls-files",
        "--others",
        "--exclude-standard",
        *sources.GENERATED_STATE_IGNORES,
        "-z",
        "--",
        *SOURCE_ROOTS,
        *sources.GENERATED_STATE_PATHSPECS,
    )
    for path in untracked.decode().split("\0")[:-1]:
        files.setdefault(path, None)
    return files


def new_lines(before, after):
    matcher = SequenceMatcher(
        None,
        before.splitlines(),
        after.splitlines(),
        autojunk=False,
    )
    return {
        line
        for tag, _, _, start, end in matcher.get_opcodes()
        if tag in {"insert", "replace"}
        for line in range(start + 1, end + 1)
    }


def checker_findings(root, paths):
    result = run(
        ("ec", "-no-color", "-format", "codeclimate", *paths),
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
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
    contents = {}
    filtered = []
    for item in findings:
        path = item["location"]["path"]
        description = item["description"]
        if description.startswith("Line too long"):
            limit = int(description.removesuffix(")").rsplit(" ", 1)[1])
            if path not in contents:
                contents[path] = (
                    (root / path)
                    .read_text(
                        encoding="utf-8",
                    )
                    .split("\n")
                )
            number = item["location"]["lines"]["begin"]
            length = len(contents[path][number - 1])
            if length <= limit:
                continue
            item["description"] = (
                f"Line too long ({length} instead of {limit})"
            )
        filtered.append(item)
    return filtered


def line_length_findings(root, base_ref):
    base = (
        git(
            root,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{base_ref}^{{commit}}",
        )
        .decode()
        .strip()
    )
    files = {
        path: previous
        for path, previous in changed_files(root, base).items()
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
            (root / path).read_bytes().splitlines(),
            1,
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


def enabled(root):
    try:
        config = load_suite_config(root)
    except FileNotFoundError:
        return False
    settings = config.get("tool", {}).get("anechoic", {})
    value = settings.get("test_suite", {}).get(
        "enforce_source_line_length",
        False,
    )
    if type(value) is not bool:
        raise ValueError("enforce_source_line_length must be a boolean")
    return value


def static_findings(root):
    if not (root / ".editorconfig").is_file():
        raise FileNotFoundError(root / ".editorconfig")
    paths = set(sources.source_paths(root, STATIC_SUFFIXES, STATIC_ROOTS))
    paths.update(
        path
        for path in sources.source_paths(root, roots=STATIC_ROOTS)
        if path.name == "Dockerfile"
    )
    paths.update(
        sources.source_paths(root, {".yml", ".yaml"}, (".github/workflows",))
    )
    for path in paths:
        if (root / path).resolve() != root / path:
            raise ValueError(f"{path}: source path traverses a symbolic link")
    files = sorted(
        path.as_posix() for path in paths if (root / path).is_file()
    )
    findings = [
        (path, number, "Next-line suppression is disabled")
        for path in files
        for number, line in enumerate(
            (root / path).read_bytes().splitlines(), 1
        )
        if NEXT_LINE_DIRECTIVE in line
    ]
    for offset in range(0, len(files), 200):
        for item in checker_findings(root, files[offset : offset + 200]):
            location = item["location"]
            start = location["lines"]["begin"]
            end = start + location["lines"]["end"]
            findings.extend(
                (location["path"], line, item["description"])
                for line in range(start, end + 1)
            )
    return sorted(findings)


def report(root, base=None):
    try:
        if not enabled(root):
            print("Source line length check is disabled")
            return 0
        findings = (
            static_findings(root)
            if base is None
            else line_length_findings(root, base)
        )
    except FileNotFoundError as error:
        if error.filename == "ec":
            print(
                "Install the checker with "
                "uv sync --project "
                "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine",
                file=sys.stderr,
            )
        else:
            print(f"Line length check failed: {error}", file=sys.stderr)
        return 2
    except (
        OSError,
        CalledProcessError,
        TimeoutExpired,
        ValueError,
        IndexError,
        KeyError,
        TypeError,
        AttributeError,
    ) as error:
        print(f"Line length check failed: {error}", file=sys.stderr)
        return 2
    for path, line, description in findings:
        print(f"{path}:{line}: {description}")
    return int(bool(findings))


def check(root: Path) -> int:
    """Check all covered source files in the authored checkout."""
    return report(root.resolve())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="HEAD",
        help="Git base (default HEAD)",
    )
    parser.add_argument("--project-root", type=Path, default=ROOT)
    args = parser.parse_args()
    return report(args.project_root.resolve(), args.base)


if __name__ == "__main__":
    raise SystemExit(main())
