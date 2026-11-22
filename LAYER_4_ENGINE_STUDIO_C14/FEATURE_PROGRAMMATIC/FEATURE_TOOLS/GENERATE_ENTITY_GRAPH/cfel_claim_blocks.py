"""Read fenced Claim blocks and bounded CFEL expressions."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view, matches_named_value

Record = dict[str, Any]
_FENCE_LINE = re.compile(r"^[ \t]*(?P<marker>`{3,}|~{3,})(?P<label>[^\r\n]*)\r?$")
_HEADING = re.compile(r"^(?P<hashes>#{1,6})[ \t]+(?P<name>[^\n#][^\n]*?)[ \t]*$", re.M)


def _fences(body: str) -> list[tuple[int, int, int | None, str]]:
    """Read top-level backtick/tilde fences with their actual marker width."""

    result: list[tuple[int, int, int | None, str]] = []
    active: tuple[str, int, int, int, str] | None = None
    offset = 0
    for line in body.splitlines(keepends=True):
        match = _FENCE_LINE.match(line)
        if active is None:
            if match is not None:
                marker = match.group("marker")
                active = (marker[0], len(marker), offset, offset + len(line), match.group("label").strip())
        elif match is not None:
            marker = match.group("marker")
            character, width, opening, content_start, label = active
            if marker[0] == character and len(marker) >= width and not match.group("label").strip():
                result.append((opening, content_start, offset, label))
                active = None
        offset += len(line)
    if active is not None:
        _, _, opening, content_start, label = active
        result.append((opening, content_start, None, label))
    return result



def _section_ranges(body: str, section_name: str) -> list[tuple[int, int]]:
    """Return named Markdown-section bodies, ignoring headings inside fences."""

    headings: list[tuple[int, int, int, str]] = []
    fenced = [(opening, closing if closing is not None else len(body)) for opening, _, closing, _ in _fences(body)]
    offset = 0
    for line in body.splitlines(keepends=True):
        if not any(opening <= offset < closing for opening, closing in fenced):
            match = _HEADING.match(line)
            if match is not None:
                headings.append((offset, offset + len(line), len(match.group("hashes")), match.group("name").strip()))
        offset += len(line)
    ranges = []
    for index, (_, content_start, level, heading_name) in enumerate(headings):
        if heading_name.casefold() != section_name.casefold():
            continue
        end = len(body)
        for next_start, _, next_level, _ in headings[index + 1:]:
            if next_level <= level:
                end = next_start
                break
        ranges.append((content_start, end))
    return ranges



def _claim_ranges(body: str) -> list[tuple[int, int]]:
    """Return Markdown Claim bodies, ignoring headings written inside fences."""

    return _section_ranges(body, "claim")



def _claim_parts(body: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]] | None:
    """Find named direct Claim children, leaving legacy Claims readable."""
    formal, prose = [], []
    headings = []
    fenced = [(a, c if c is not None else len(body)) for a, _, c, _ in _fences(body)]
    offset = 0
    for line in body.splitlines(keepends=True):
        match = _HEADING.match(line) if not any(a <= offset < c for a, c in fenced) else None
        if match:
            headings.append((offset, offset + len(line), len(match.group("hashes")), match.group("name").strip().casefold()))
        offset += len(line)
    for index, (_, _, level, name) in enumerate(headings):
        if name != "claim":
            continue
        end_index = next((i for i in range(index + 1, len(headings))
                          if headings[i][2] == level and headings[i][3] in {"summary", "claim", "semantics", "details"}), len(headings))
        children = [row for row in headings[index + 1:end_index]
                    if row[2] == level + 1 and row[3] in {"formal claim", "prose claim"}]
        end = headings[end_index][0] if end_index < len(headings) else len(body)
        for position, (_, start, _, child_name) in enumerate(children):
            child_end = children[position + 1][0] if position + 1 < len(children) else end
            (formal if child_name == "formal claim" else prose).append((start, child_end))
    return (formal, prose) if formal or prose else None



def section_text(carrier: Mapping[str, Any], name: str) -> str:
    """Return exact named-section text; this does not interpret its Markdown."""

    body = carrier.get("body")
    if not isinstance(body, str):
        return ""
    return "\n".join(body[start:end].strip() for start, end in _section_ranges(body, name) if body[start:end].strip())



def _split_expressions(block: str) -> list[str]:
    """Split only unquoted semicolons; unsupported quoted syntax stays whole."""

    values: list[str] = []
    start = 0
    quote: str | None = None
    escaped = False
    depth = 0
    for index, character in enumerate(block):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        elif character == ";" and depth == 0 and block[index:index + 2] != ";>" and (
            block[index - 1:index] != "<" or block[index - 2:index] == "<<"
        ):
            value = block[start:index].strip()
            if value:
                values.append(value)
            start = index + 1
    value = block[start:].strip()
    if value:
        values.append(value)
    return values



def _grouped_expressions(block: str) -> list[tuple[str, str | None]]:
    groups: list[tuple[str, str | None]] = []
    pending: list[str] = []
    group = None
    quote = None
    escaped = False
    for line in block.splitlines(keepends=True):
        if quote is None and line.lstrip().startswith('#'):
            groups.extend((value, group) for value in _split_expressions(''.join(pending)))
            pending = []
            marker = line.strip().casefold()
            if marker in {'# model', '# instances'}:
                group = marker[2:]
            continue
        pending.append(line)
        for character in line:
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == '\\':
                    escaped = True
                elif character == quote:
                    quote = None
            elif character in {'"', "'"}:
                quote = character
    groups.extend((value, group) for value in _split_expressions(''.join(pending)))
    return groups



def _balanced_parentheses(value: str) -> bool:
    depth = 0
    quote = None
    escaped = False
    for character in value:
        if quote:
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == '(':
            depth += 1
        elif character == ')':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and quote is None



def _expressions(body: str) -> tuple[list[tuple[str, str | None]], list[Record]]:
    """Read CFEL fences inside Claim; retain skipped fences as diagnostics."""

    values: list[tuple[str, str | None]] = []
    diagnostics: list[Record] = []
    parts = _claim_parts(body)
    claim_ranges = parts[0] if parts is not None else _claim_ranges(body)
    for opening, content_start, closing, label in _fences(body):
        if label.casefold() != "cfel":
            continue
        if parts is not None and any(start <= opening < end for start, end in parts[1]):
            continue
        in_claim = any(start <= opening < end for start, end in claim_ranges)
        if closing is None:
            diagnostics.append({
                "code": "cfel-fence-unclosed" if in_claim else "cfel-fence-outside-claim",
                "message": (
                    "CFEL fence has no closing fence; its contents were not interpreted."
                    if in_claim else "CFEL fence is outside Claim; its contents were not interpreted."
                ),
                "offset": opening,
            })
            continue
        if in_claim:
            values.extend(_grouped_expressions(body[content_start:closing]))
        else:
            diagnostics.append({
                "code": "cfel-fence-outside-claim",
                "message": "CFEL fence is outside Claim; its contents were not interpreted.",
                "offset": opening,
            })
    return values, diagnostics



def claim_cfel_blocks(carrier: Mapping[str, Any]) -> list[Record]:
    """Return complete CFEL Claim blocks without interpreting their clauses."""

    source, body = carrier.get("source"), carrier.get("body")
    if not isinstance(source, Mapping) or not isinstance(body, str):
        return []
    parts = _claim_parts(body)
    ranges = parts[0] if parts is not None else _claim_ranges(body)
    return [
        {"source": dict(source), "block": body[content_start:closing]}
        for opening, content_start, closing, label in _fences(body)
        if label.casefold() == "cfel" and closing is not None and any(start <= opening < end for start, end in ranges)
    ]



def claim_python_blocks(carrier: Mapping[str, Any]) -> list[Record]:
    """Select authored Python model Claims, never Workflow or prose examples."""
    view = carrier.get("read_view")
    if not isinstance(view, Mapping):
        metadata = carrier.get("metadata")
        view = carrier_read_view(dict(metadata)) if isinstance(metadata, Mapping) else {}
    if not any(matches_named_value(view.get("content_role"), role)
               for role in ("Requirement", "Method", "Evaluation", "Delivery")):
        return []
    source, body = carrier.get("source"), carrier.get("body")
    if not isinstance(source, Mapping) or not isinstance(body, str):
        return []
    parts = _claim_parts(body)
    ranges = parts[0] if parts is not None else _claim_ranges(body)
    return [
        {"source": dict(source), "block": body[start:closing], "label": label}
        for opening, start, closing, label in _fences(body)
        if label.casefold() == "python" and closing is not None
        and any(lo <= opening < hi for lo, hi in ranges)
    ]



def claim_fenced_blocks(carrier: Mapping[str, Any]) -> list[Record]:
    """Return every fenced Claim block with its original language label.

    Only blocks labelled ``CFEL`` are structurally extracted elsewhere.  Other
    labels, including no label, remain source evidence rather than being
    relabelled or interpreted as CFEL.
    """

    source, body = carrier.get("source"), carrier.get("body")
    if not isinstance(source, Mapping) or not isinstance(body, str):
        return []
    ranges = _claim_ranges(body)
    return [
        {"source": dict(source), "block": body[content_start:closing if closing is not None else len(body)],
         "label": label, "closed": closing is not None}
        for opening, content_start, closing, label in _fences(body)
        if any(start <= opening < end for start, end in ranges)
    ]



def claim_prose(carrier: Mapping[str, Any]) -> str:
    """Return Claim text after removing fenced blocks, without parsing prose."""

    body = carrier.get("body")
    if not isinstance(body, str):
        return ""
    parts = _claim_parts(body)
    if parts is not None:
        return "\n".join(body[start:end].strip() for start, end in parts[1] if body[start:end].strip())
    pieces = []
    for start, end in _claim_ranges(body):
        removed = []
        for opening, _, closing, _ in _fences(body):
            if not start <= opening < end:
                continue
            if closing is None:
                removed.append((opening, end))
                continue
            newline = body.find("\n", closing)
            removed.append((opening, len(body) if newline < 0 else newline + 1))
        cursor = start
        for opening, closing in removed:
            pieces.append(body[cursor:opening])
            cursor = closing
        pieces.append(body[cursor:end])
    return "\n".join(piece.strip() for piece in pieces if piece.strip())



def has_prose_claim(carrier: Mapping[str, Any]) -> bool:
    body = carrier.get("body")
    parts = _claim_parts(body) if isinstance(body, str) else None
    return parts is not None and bool(parts[1])

