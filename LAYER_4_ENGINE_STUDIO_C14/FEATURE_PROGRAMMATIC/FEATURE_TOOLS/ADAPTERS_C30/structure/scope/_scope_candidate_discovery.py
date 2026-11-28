"""Read bounded declaration candidates from one authority directory."""

import os
from pathlib import Path

from ...ADAPTERS_C30__pub import ReadContext


def _declaration_candidates(
    reader: ReadContext,
    directory: Path,
    *,
    root: bool,
    open_regular,
    has_scope_declaration_form,
    has_projection_marker,
) -> tuple[tuple[Path, bytes], ...]:
    """Read only direct Current candidates in a declared authority location."""
    candidates = []
    try:
        directory = reader.allowed(directory)
        descriptor = open_regular(directory, directory=True)
    except FileNotFoundError:
        return ()
    try:
        with os.scandir(descriptor) as entries:
            names = sorted(
                entry.name
                for entry in entries
                if entry.name.endswith(".md")
                and (not root or entry.name.startswith("CA-R-"))
                and entry.is_file(follow_symlinks=False)
            )
        for name in names:
            path = directory / name
            try:
                raw = reader.read(
                    path, remember=False, directory_fd=descriptor
                )
            except FileNotFoundError:
                continue
            if has_scope_declaration_form(
                raw, path
            ) and not has_projection_marker(raw):
                candidates.append((path, raw))
    finally:
        os.close(descriptor)
    return tuple(candidates)
