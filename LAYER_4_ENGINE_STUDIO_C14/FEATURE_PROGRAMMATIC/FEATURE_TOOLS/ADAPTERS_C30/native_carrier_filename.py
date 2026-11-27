"""Serialize native carrier names from authored fields."""

import re
import unicodedata


_ASSETS = {"analysis_report", "work_report", "work_log", "spec_proposal"}


def native_ticket_asset(template):
    return (
        isinstance(template, str)
        and re.sub(r"[ _-]+", "_", template.lower()) in _ASSETS
    )


def _token(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*", value
    ):
        raise ValueError("Unsupported authored filename token")
    return re.sub(r"[ _-]+", "_", value).upper()


def _slug(summary):
    if not isinstance(summary, str) or not summary.isprintable():
        raise ValueError("Unsupported Summary serialization")
    if any(
        not c.isascii() and not unicodedata.category(c).startswith("P")
        for c in summary
    ):
        raise ValueError("Summary requires an ASCII transliteration")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", summary).strip("-").lower()
    if not slug:
        raise ValueError("Summary has no usable slug")
    return slug


def native_ticket_label(
    template, owner_template, owner_label=None, *, label=None
):
    if label is not None:
        _token(label)
        return label
    owner_is_epic = owner_template == "epic" or (
        isinstance(owner_label, str)
        and owner_label.casefold() in {"epic", "sub-epic"}
    )
    if template == "epic":
        return "Sub-epic" if owner_is_epic else "Epic"
    return (
        "Subtask" if owner_template == "task" and not owner_is_epic else "Task"
    )


def project_goal_filename(name):
    return (
        re.fullmatch(r"[A-Z]+-S-[0-9]+-SPEC-PROJECT_GOAL--.+\.md", name)
        is not None
    )


def _validate_placement_status(family, status):
    model_ticket_status = (
        family == "TKT"
        and re.fullmatch(r"[a-z][a-z0-9_]*", status) is not None
    )
    if (
        not model_ticket_status
        and status
        not in {
            "active",
            "in_queue",
            "backlog",
            "done",
            "complete",
            "canceled",
            "resolved",
            "draft",
            "ready",
            "archived",
        }
        or (status == "ready" and family != "SPEC")
        or (status in {"in_queue", "complete"} and family != "TKT")
    ):
        raise ValueError("Unsupported authored Status")


def _revision_marker(
    status, atom_id, version, draft_directory, archive_directory
):
    revision = (
        draft_directory
        if status == "draft"
        else archive_directory
        if status == "archived"
        else None
    )
    marker = atom_id + (
        f"@{version}-draft"
        if status == "draft"
        else f"@{version}"
        if status == "archived"
        else ""
    )
    return revision, marker
