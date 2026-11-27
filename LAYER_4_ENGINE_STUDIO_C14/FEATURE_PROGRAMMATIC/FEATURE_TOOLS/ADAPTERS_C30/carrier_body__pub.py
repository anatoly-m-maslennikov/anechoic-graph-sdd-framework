"""Extract the body of a frontmatter carrier."""

from pathlib import Path
import re


_CLOSING_DELIMITER = re.compile(rb"\r?\n---\r?\n")


def frontmatter_bounds(raw: bytes) -> tuple[int, int, int] | None:
    if raw.startswith(b"---\n"):
        opening_end = len(b"---\n")
    elif raw.startswith(b"---\r\n"):
        opening_end = len(b"---\r\n")
    else:
        return None
    closing = _CLOSING_DELIMITER.search(raw, pos=opening_end - 1)
    return (
        None
        if closing is None
        else (opening_end, closing.start(), closing.end())
    )


def source_body(raw: bytes, path: Path) -> bytes:
    bounds = frontmatter_bounds(raw)
    if bounds is None:
        raise ValueError(f"{path}: unsupported frontmatter delimiter")
    return raw[bounds[2] :]
