"""Parse named declaration paths."""

import re

_NAME = r"[A-Za-z_][A-Za-z_0-9 -]*?"


def _path(  # noqa: C901
    text: str,
) -> tuple[list[tuple[str, str, str]], str] | None:
    """Return named nodes and incoming selectors; reject unsupported paths."""
    match = re.match(rf"\s*({_NAME})(?=\s*(?:/|$))", text)
    if not match:
        return None
    nodes = [(match.group(1).strip(), "", "")]
    pos = match.end()
    pending = ""
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos == len(text):
            break
        if text[pos] != "/":
            return None
        op = "//" if text.startswith("//", pos) else "/"
        pos += len(op)
        if pos < len(text) and text[pos] == "(":
            end = _selector_end(text, pos)
            if end is None:
                return None
            pending += "/" + text[pos:end]
            pos = end
            continue
        m = re.match(r"\s*([^/]+)", text[pos:])
        if not m:
            return None
        name = m.group(1).strip()
        if name.startswith("$"):
            if "/" in text[pos + m.end() :]:
                return None
            pos += m.end()
            break
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9 -]*", name):
            return None
        nodes.append((name, op, pending))
        pending = ""
        pos += m.end()
    return nodes, pending


def _selector_end(text: str, pos: int) -> int | None:
    depth = 0
    while pos < len(text):
        if text[pos] == "(":
            depth += 1
        if text[pos] == ")":
            depth -= 1
        pos += 1
        if depth == 0:
            break
    return None if depth else pos


