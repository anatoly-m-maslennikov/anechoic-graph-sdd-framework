"""Bounded model view preserves legacy graph behavior and evidence."""

from __future__ import annotations

from pathlib import Path
import sys


TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

def source(atom_id: str) -> dict[str, object]:
    return {"atom_id": atom_id, "version": 1, "path": f"sources/{atom_id}.md", "sha256": "a" * 64}

def carrier(
    atom_id: str, subjects: dict, body: str = "", *, declaration: bool = False,
    role: str = "Requirement", form: str = "Declaration",
) -> dict[str, object]:
    row = {"source": source(atom_id), "subjects": subjects, "body": body}
    if declaration:
        row["read_view"] = {"content_role": role, "type": form}
    return row
