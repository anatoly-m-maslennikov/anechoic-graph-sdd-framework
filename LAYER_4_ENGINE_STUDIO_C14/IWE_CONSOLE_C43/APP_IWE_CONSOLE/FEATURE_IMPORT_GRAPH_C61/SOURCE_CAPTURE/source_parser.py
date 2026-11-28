"""Parse Python source imports without executing source code."""

from __future__ import annotations

import ast
import io
import sys
import tokenize

from pydantic import ConfigDict, ValidatorFunctionWrapHandler, field_validator
from pydantic.dataclasses import dataclass

from .python_forwarding import python_forwarded


_STRICT = ConfigDict(strict=True, extra="forbid")


@dataclass(frozen=True, slots=True, config=_STRICT)
class ImportSite:
    module: str
    name: str | None
    level: int
    line: int
    column: int
    type_only: bool = False
    previous_image: bool = False


@dataclass(frozen=True, slots=True, config=_STRICT)
class Source:
    language: str
    status: str
    signature: str
    imports: tuple[ImportSite, ...] = ()
    error_message: str | None = None
    forwarded: tuple[tuple[str, str, int, int], ...] = ()
    named_uses: tuple[tuple[str, int, int], ...] = ()

    @field_validator("imports", "forwarded", "named_uses", mode="wrap")
    @classmethod
    def _retain_sites(cls, value, validate: ValidatorFunctionWrapHandler):
        validated = validate(value)
        return (
            value
            if isinstance(value, tuple) and value == validated
            else validated
        )


class _Imports(ast.NodeVisitor):
    def __init__(self, image_lines: set[int]) -> None:
        self.sites: list[ImportSite] = []
        self.image_lines = image_lines

    def visit_Import(self, node: ast.Import) -> None:
        self.sites.extend(
            ImportSite(
                alias.name,
                None,
                0,
                node.lineno,
                node.col_offset,
                previous_image=node.lineno - 1 in self.image_lines,
            )
            for alias in node.names
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.sites.extend(
            ImportSite(
                node.module or "",
                alias.name,
                node.level,
                node.lineno,
                node.col_offset,
                previous_image=node.lineno - 1 in self.image_lines,
            )
            for alias in node.names
        )
        self.generic_visit(node)


def _parse(
    relative: str, language: str, data: bytes, signature: str
) -> Source:
    if language != "python":
        return Source(language, "unsupported", signature)
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        text = data.decode(encoding)
        tree = ast.parse(text, filename=relative)
        image_lines = {
            token.start[0]
            for token in tokenize.generate_tokens(io.StringIO(text).readline)
            if token.type == tokenize.COMMENT
            and token.string == "# import-graph: previous-image"
        }
    except (LookupError, SyntaxError, UnicodeError, ValueError) as error:
        print(
            f"import graph: {relative}: parse error: {error}", file=sys.stderr
        )
        return Source(language, "parse_error", signature)
    visitor = _Imports(image_lines)
    visitor.visit(tree)
    return Source(
        language,
        "parsed",
        signature,
        tuple(visitor.sites),
        forwarded=python_forwarded(tree),
    )
