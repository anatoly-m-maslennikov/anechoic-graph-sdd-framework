"""Render Subject audit bodies."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def render_subject_audit(audit: Mapping[str, Any], kind: str) -> str:
    """Render a body only; callers own projection frontmatter and wrapping."""

    report = audit[kind] if kind in audit else audit

    if report["kind"] == "passive_only_subjects":
        lines = _passive_lines(report)
    elif report["kind"] == "subjects_without_declaration_coverage":
        lines = [
            "# Subjects Without Effective Requirement Declaration Coverage",
            "",
            "## Subjects",
            "",
        ]
        lines.extend(
            f"- `{row['subject']}` — {row['message']}; {_evidence(row)}"
            for row in report["subjects"]
        )
        lines.extend(["", "## Informational outside required scope", ""])
        lines.extend(
            f"- `{row['subject']}` — {row['message']}; {_evidence(row)}"
            + (
                f"; Term Definition: {', '.join(row['term_definition_refs'])}"
                if row.get("term_definition_refs")
                else ""
            )
            for row in report["informational"]
        )
        lines.extend(["", "## Unresolved coverage needing review", ""])
        lines.extend(
            f"- `{row['subject']}` — {row['message']}; {_evidence(row)}"
            for row in report["unresolved"]
        )
    else:
        lines = _entity_lines(report)
    if not any(line.startswith("- ") for line in lines):
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def _evidence(row: Mapping[str, Any]) -> str:
    keys = sorted({item["source_key"] for item in row.get("occurrences", [])})
    return f"pins: {', '.join(row.get('pins', []))}; keys: {', '.join(keys)}"


def _passive_lines(report):
    lines = ["# Subjects Used Only Passively", "", "## Subjects", ""]
    lines.extend(
        f"- `{row['subject']}` — {_evidence(row)}"
        + ("; unresolved syntax" if row["unresolved"] else "")
        for row in report["subjects"]
    )
    lines.extend(["", f"## Diagnostics ({len(report['diagnostics'])})", ""])
    lines.extend(
        f"- `{row['raw_value']}` — {row['pin']}; "
        f"{row['source_key']}; {row['message']}"
        for row in report["diagnostics"]
    )
    return lines


def _entity_lines(report):
    lines = [
        "# Entity Definition Summary",
        "",
        "| Entity | Kind | Defining atom | Active Subject |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["display_entities"]:
        lines.append(
            f"| `{row['identity']}` | {row['kind']} | "
            f"{_summary_cell(row, 'missing_definition', 'defining_refs')} | "
            f"{_summary_cell(row, 'missing_active', 'active_refs')} |"
        )
    return lines


def _summary_cell(row, missing, refs):
    return "missing" if row[missing] else ", ".join(row[refs])
