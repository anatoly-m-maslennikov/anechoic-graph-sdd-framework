"""Convert the supported literal CFEL statements to Python model declarations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

_ENGINE = Path(__file__).resolve().parents[2]
if __package__ in (None, "") and str(_ENGINE) not in sys.path:
    sys.path.insert(0, str(_ENGINE))

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_migration_statements import convert_statement


def _parts(text: str) -> list[tuple[str, str]] | None:
    """Split statements at semicolons and retain whole-line comments."""
    parts = []
    pending = ''
    quote = None
    escaped = False
    for line in text.splitlines():
        if line.lstrip().startswith('#') and quote is None:
            if pending.strip():
                return None
            parts.append(('comment', line.strip()))
            continue
        for index, char in enumerate(line):
            if escaped:
                escaped = False
            elif quote and char == '\\':
                escaped = True
            elif char in {'"', "'"}:
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
            elif char == '#' and quote is None:
                return None
            if char == ';' and quote is None and line[index:index + 2] != ';>':
                if pending.strip():
                    parts.append(('statement', pending.strip()))
                pending = ''
            else:
                pending += char
        pending += '\n'
    if quote is not None:
        return None
    if pending.strip():
        parts.append(('statement', pending.strip()))
    return parts


def convert_claim(text: str) -> str | None:
    """Convert a complete Claim only when every statement is supported."""
    parts = _parts(text)
    if parts is None:
        return None
    output = []
    count = 0
    for kind, value in parts:
        if kind == 'comment':
            output.append(value)
        else:
            converted = convert_statement(value)
            if converted is None:
                return None
            count += 1
            output.append(converted)
    return '\n'.join(output) if count else None


def convert_markdown_claim(body: str) -> str | None:
    """Replace one complete Claim/Formal Claim fence, preserving other Markdown."""
    from markdown_it import MarkdownIt
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import content_key

    headings: list[tuple[int, str]] = []
    fences = []
    tokens = MarkdownIt('commonmark').parse(body)
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            level = int(token.tag[1:])
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append((level, content_key(tokens[index + 1].content)))
        elif token.type == 'fence' and tuple(name for _, name in headings) == ('claim', 'formal_claim'):
            fences.append(token)
    if len(fences) != 1 or fences[0].info.strip().casefold() != 'cfel' or fences[0].map is None:
        return None

    lines = body.splitlines(keepends=True)
    start, end = fences[0].map
    if end - start < 2:
        return None
    opening = re.fullmatch(r'(?P<indent> {0,3})(?P<marks>`{3,}|~{3,})[ \t]*[Cc][Ff][Ee][Ll][ \t]*(?P<ending>\r?\n)', lines[start])
    if opening is None:
        return None
    marks = opening['marks']
    if not re.fullmatch(rf" {{0,3}}{re.escape(marks[0])}{{{len(marks)},}}[ \t]*(?:\r?\n)?", lines[end - 1]):
        return None

    converted = convert_claim(fences[0].content)
    if converted is None:
        return None
    ending = opening['ending']
    rendered = ending.join(converted.split('\n')) + ending
    return ''.join(lines[:start]) + opening['indent'] + marks + 'python' + ending + rendered + ''.join(lines[end - 1:])


def convert_carrier(raw: bytes, path: Path) -> bytes | None:
    """Convert one carrier while preserving its exact Header and line endings."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier

    parsed = parse_carrier(raw, path)
    match = re.search(rb"\r?\n---\r?\n", raw)
    if match is None:
        return None
    start = match.end()
    body = raw[start:].decode('utf-8')
    if body.replace('\r\n', '\n') != parsed.body:
        return None
    converted = convert_markdown_claim(body)
    return None if converted is None else raw[:start] + converted.encode('utf-8')


def audit(frontier: Path, *, stage: Path | None = None) -> dict[str, object]:
    """Check the pinned frontier and optionally write a separate converted cohort."""
    from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.formal_claim_blocks__pub import formal_claim_blocks
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier

    manifest = json.loads(frontier.read_text())
    counts: dict[str, dict[str, int]] = {}
    conversions: dict[Path, bytes] = {}
    unsupported: list[dict[str, object]] = []
    for record in manifest['records']:
        group = record['status_group']
        if group == 'Current':
            candidate = record.get('source_path_check', {}).get('candidate')
            entries = [row for row in record['candidates'] if row['path'] == candidate and row['contains_cfel']]
        else:
            entries = [row for row in record['candidates'] if row['contains_cfel']]
        if len(entries) != 1:
            continue
        entry = entries[0]
        path = Path(entry['path'])
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError(f'Pinned source changed: {path}')
        body = parse_carrier(raw, path).body
        blocks = formal_claim_blocks(body)
        if not blocks:
            continue
        group_counts = counts.setdefault(group, {'claims': 0, 'convertible': 0})
        group_counts['claims'] += 1
        converted = convert_carrier(raw, path)
        if converted is not None:
            group_counts['convertible'] += 1
            conversions[path] = converted
        else:
            unsupported.append({'reference': record['reference'], 'version': entry.get('version'),
                                'status_group': group, 'path': str(path)})
    if stage is not None:
        for path in conversions:
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Stage requires repository-relative source paths: {path}')
        stage.mkdir(parents=True, exist_ok=False)
        for path, payload in conversions.items():
            output = stage / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
    return {'frontier': str(frontier), 'groups': counts, 'unsupported': unsupported}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', required=True, type=Path, help='Pinned CFEL source frontier JSON')
    parser.add_argument('--stage', type=Path, help='New directory for converted carrier copies')
    args = parser.parse_args()
    print(json.dumps(audit(args.audit, stage=args.stage), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
