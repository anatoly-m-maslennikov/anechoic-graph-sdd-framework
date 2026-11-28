"""Locate and rewrite the port in a formal release manifest."""

import ast

from markdown_it import MarkdownIt

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)


def _mapping_value(mapping, key):
    if isinstance(mapping, ast.Dict):
        return next(
            (
                value
                for index, value in zip(
                    mapping.keys, mapping.values, strict=True
                )
                if isinstance(index, ast.Constant) and index.value == key
            ),
            None,
        )
    return None


def _port_nodes(code, manifest_type):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == manifest_type
        ):
            parameters = next(
                (
                    arg.value
                    for arg in node.keywords
                    if arg.arg == "parameters"
                ),
                None,
            )
            port = _mapping_value(
                _mapping_value(parameters, "project_mcp"), "http_port"
            )
            if isinstance(port, ast.Constant) and type(port.value) is int:
                yield port


def _formal_claim_fences(text):
    tokens = MarkdownIt("commonmark").parse(text)
    headings = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append(
                (level, tokens[index + 1].content.strip().casefold())
            )
        elif token.type == "fence":
            section = tuple(name for _, name in headings)
            info = token.info.strip().casefold()
            if section == ("claim", "formal claim") and info == "python":
                yield token, "ProjectManifest"
            elif section == ("formal manifest",) and info in {
                "python",
                "python anechoic-edsl",
            }:
                yield token, "ComponentManifest"


def _rewrite_port(path, old_port, port):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = raw.splitlines(keepends=True)
    slots = []
    for token, manifest_type in _formal_claim_fences(text):
        for node in _port_nodes(token.content, manifest_type):
            if node.value == old_port:
                slots.append((token, node))
    if len(slots) != 1:
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    token, node = slots[0]
    index = token.map[0] + node.lineno
    code_line = token.content.splitlines()[node.lineno - 1].encode("utf-8")
    original_line = lines[index].rstrip(b"\r\n")
    if not original_line.endswith(code_line):
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    offset = len(original_line) - len(code_line)
    first, last = offset + node.col_offset, offset + node.end_col_offset
    lines[index] = (
        lines[index][:first] + str(port).encode("ascii") + lines[index][last:]
    )
    path.write_bytes(b"".join(lines))


def _project_port(selection):
    settings = selection.parameters.get("project_mcp")
    port = settings.get("http_port") if isinstance(settings, dict) else None
    if type(port) is not int or not 1 <= port <= 65535:
        raise LocalReleaseError("prepare-local-manifest-port-unavailable")
    return port
