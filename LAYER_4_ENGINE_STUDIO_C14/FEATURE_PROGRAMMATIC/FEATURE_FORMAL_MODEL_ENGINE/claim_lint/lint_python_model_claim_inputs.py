"""Read Claim blocks and lint input catalogs."""

from __future__ import annotations
import json
from pathlib import Path
from markdown_it import MarkdownIt


def _blocks(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".py":
        yield text, 1
        return
    yield from _markdown_blocks(text)


def _markdown_blocks(text: str):
    headings: list[tuple[int, str]] = []
    tokens = MarkdownIt("commonmark").parse(text)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [(n, name) for n, name in headings if n < level]
            headings.append(
                (level, tokens[index + 1].content.strip().casefold())
            )
        elif (
            token.type == "fence" and token.info.strip().casefold() == "python"
        ):
            if tuple(name for _, name in headings[-2:]) == (
                "claim",
                "formal claim",
            ):
                yield token.content, token.map[0] + 2


def _names(path: Path, *, registry: bool = False) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if registry and isinstance(value, dict):
        names = value.get("registered_names")
        aliases = value.get("inverse_aliases", [])
        if (
            not isinstance(names, list)
            or not isinstance(aliases, list)
            or any(
                not isinstance(item, dict)
                or not isinstance(item.get("alias"), str)
                or item.get("canonical") not in names
                for item in aliases
            )
        ):
            raise ValueError(f"{path}: invalid inverse alias registry")
        value = names + [item["alias"] for item in aliases]
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise ValueError(
            f"{path}: expected a JSON array of strings"
            + (" or Workbench relation registry" if registry else "")
        )
    return value


def _address_catalog(
    path: Path,
) -> tuple[list[str], dict[str, list[str]] | None]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list) and all(
        isinstance(item, str) for item in value
    ):
        return value, None
    if not isinstance(value, dict) or set(value) != {
        "addresses",
        "python_classes",
    }:
        raise ValueError(
            f"{path}: expected an address array or a Model catalog"
        )
    addresses, bindings = value["addresses"], value["python_classes"]
    if (
        not isinstance(addresses, list)
        or any(not isinstance(item, str) for item in addresses)
        or not isinstance(bindings, dict)
        or any(
            not isinstance(name, str)
            or not name.isidentifier()
            or not isinstance(targets, list)
            or not targets
            or any(
                not isinstance(target, str) or not target for target in targets
            )
            for name, targets in bindings.items()
        )
    ):
        raise ValueError(f"{path}: invalid Model catalog")
    return addresses, bindings
