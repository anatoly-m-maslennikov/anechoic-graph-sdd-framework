"""Check or remove ordinary comments in first-party source."""

from __future__ import annotations

import argparse
from io import BytesIO, StringIO
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
from tempfile import NamedTemporaryFile
import tokenize

CODE_ROOTS = ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "LAYER_5_USER_SETUP_C65")
ROOT = Path(__file__).resolve().parents[3]
FRONTEND = (
    Path(CODE_ROOTS[0]) / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
)
WEB_SUFFIXES = {".js", ".mjs", ".ts", ".svelte", ".css", ".html"}
DOCKER_FILES = {"Dockerfile", "Dockerfile.dockerignore", ".dockerignore"}
EDITORCONFIG_DIRECTIVE = r"editorconfig-checker-disable-line\b"
PYTHON_DIRECTIVE = re.compile(
    rf"#\s*(?:noqa\b|{EDITORCONFIG_DIRECTIVE}|"
    r"(?:type|ruff|flake8|pylint|pyright|mypy|fmt|isort|pragma):)"
)
ENCODING_COOKIE = re.compile(r"#.*?coding[:=]\s*[-\w.]+")
DOCKER_DIRECTIVE = re.compile(
    rf"#\s*(?:(?:syntax|escape|check)\s*=|{EDITORCONFIG_DIRECTIVE})",
    re.IGNORECASE,
)


def python_comments(source: str) -> list[tuple[int, int]]:
    lines = StringIO(source, newline="").readlines()
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    ranges = []
    for token in tokenize.generate_tokens(StringIO(source, newline="").readline):
        if token.type != tokenize.COMMENT:
            continue
        row, column = token.start
        if (row == 1 and column == 0 and token.string.startswith("#!")
                or row <= 2 and ENCODING_COOKIE.match(token.string)
                or PYTHON_DIRECTIVE.match(token.string)):
            continue
        start = offsets[row - 1] + column
        ranges.append((start, start + len(token.string)))
    return ranges


def docker_comments(path: Path, source: str) -> list[tuple[int, int]]:
    offset = 0
    ranges = []
    for line in StringIO(source, newline=""):
        stripped = line.lstrip(" \t")
        if path.name == "Dockerfile":
            if stripped.startswith("#") and not DOCKER_DIRECTIVE.match(stripped):
                start = offset + len(line) - len(stripped)
                ranges.append((start, offset + len(line.rstrip("\r\n"))))
            elif "<<" in stripped and not stripped.startswith("#"):
                raise ValueError(f"{path}: Dockerfile heredoc requires a syntax-aware parser")
        elif line.startswith("#"):
            ranges.append((offset, offset + len(line.rstrip("\r\n"))))
        offset += len(line)
    return ranges


def remove_line_comments(
    source: str, comments: list[tuple[int, int]]
) -> list[tuple[int, int, str]]:
    edits = []
    for start, end in comments:
        line_start = max(source.rfind("\n", 0, start), source.rfind("\r", 0, start)) + 1
        prefix = source[line_start:start].rstrip(" \t")
        if not prefix:
            if source.startswith("\r\n", end):
                end += 2
            elif source[end:end + 1] in {"\r", "\n"}:
                end += 1
        edits.append((line_start + len(prefix), end, ""))
    return edits


def source_paths(root: Path) -> list[Path]:
    result = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *CODE_ROOTS],
        cwd=root,
    )
    paths = {Path(item.decode("utf-8")) for item in result.split(b"\0") if item}
    return sorted(path for path in paths
                  if path.suffix in WEB_SUFFIXES | {".py"} or path.name in DOCKER_FILES)


def web_edits(root: Path, files: list[dict[str, str]]) -> list[list[tuple[int, int, str | None]]]:
    if not files:
        return []
    result = subprocess.run(
        ["node", str(root / FRONTEND / "scripts/source-comments.mjs")],
        input=json.dumps(files), encoding="utf-8", capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip())
    return [[(start, end, replacement) for start, end, replacement in edits]
            for edits in json.loads(result.stdout)]


def replace_source(path: Path, before: bytes, after: bytes) -> None:
    with NamedTemporaryFile(dir=path.parent, delete=False) as output:
        staged = Path(output.name)
        try:
            output.write(after)
            output.close()
            staged.chmod(stat.S_IMODE(path.stat().st_mode))
            if path.resolve() != path or path.read_bytes() != before:
                raise ValueError(f"{path}: source changed during scan, run the purge again")
            staged.replace(path)
        finally:
            staged.unlink(missing_ok=True)


def collect_edits(root: Path):
    pending = []
    web = []
    for relative in source_paths(root):
        path = root / relative
        if path.resolve() != path:
            raise ValueError(f"{relative}: source path traverses a symbolic link")
        if not path.is_file():
            continue
        raw = path.read_bytes()
        encoding = (tokenize.detect_encoding(BytesIO(raw).readline)[0]
                    if relative.suffix == ".py" else "utf-8")
        source = raw.decode(encoding)
        if relative.suffix in WEB_SUFFIXES:
            web.append((relative, raw, encoding, source))
        else:
            comments = python_comments(source) if relative.suffix == ".py" else docker_comments(
                relative, source
            )
            edits = remove_line_comments(source, comments) if relative.suffix == ".py" else [
                (start, end, "") for start, end in comments
            ]
            pending.append((relative, raw, encoding, source, edits))
    web_results = web_edits(root, [{"path": path.as_posix(), "source": source}
                                  for path, _, _, source in web])
    pending.extend((*file, edits) for file, edits in zip(web, web_results, strict=True))
    return sorted(pending)


def check_sources(root: Path, *, fix: bool = False) -> list[str]:
    findings = []
    updates = []
    for relative, raw, encoding, source, edits in collect_edits(root):
        for start, _, replacement in edits:
            line = len(StringIO(source[:start], newline="").readlines())
            if start == 0 or source[start - 1] in "\r\n":
                line += 1
            finding = f"{relative}:{line}: ordinary comment"
            if replacement is None:
                finding += " requires a manual edit to preserve CSS tokens"
                if fix:
                    raise ValueError(finding)
            findings.append(finding)
        if fix and edits:
            updated = source
            for start, end, replacement in sorted(edits, reverse=True):
                assert replacement is not None
                updated = updated[:start] + replacement + updated[end:]
            if relative.suffix == ".py":
                compile(updated, str(relative), "exec")
            updates.append((root / relative, raw, updated.encode(encoding)))
    for path, raw, updated_bytes in updates:
        replace_source(path, raw, updated_bytes)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--fix", action="store_true", help="remove reported comments")
    args = parser.parse_args()
    try:
        findings = check_sources(args.project_root.resolve(strict=True), fix=args.fix)
    except (OSError, ValueError, SyntaxError, tokenize.TokenError, subprocess.SubprocessError) as error:
        print(f"Source comment check failed: {error}", file=sys.stderr)
        return 2
    if findings:
        print(*findings, sep="\n")
    print(f"Source comments {'removed' if args.fix else 'found'}: {len(findings)}")
    return int(bool(findings) and not args.fix)


if __name__ == "__main__":
    raise SystemExit(main())
