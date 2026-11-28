"""Validate and render reviewed public release content."""

from collections.abc import Mapping


class PublicReleaseError(ValueError):
    """The release comparison or reviewed content is invalid."""


def _validate_change(change):
    if not isinstance(change, Mapping) or set(change) != {
        "title",
        "details",
        "evidence",
        "highlight",
    }:
        raise PublicReleaseError(
            "each change must contain title, details, evidence and highlight"
        )
    if any(
        not isinstance(change[key], str)
        or not change[key].strip()
        or "\n" in change[key]
        for key in ("title", "details")
    ):
        raise PublicReleaseError(
            "change title and details must be non-empty single-line strings"
        )
    if not isinstance(change["highlight"], bool):
        raise PublicReleaseError("change highlight must be a boolean")
    if change["highlight"] and len(change["title"].strip()) > 120:
        raise PublicReleaseError(
            "highlight titles must be at most 120 characters"
        )
    evidence = change["evidence"]
    if (
        not isinstance(evidence, list)
        or not evidence
        or any(
            not isinstance(item, str) or not item.strip() or "\n" in item
            for item in evidence
        )
    ):
        raise PublicReleaseError(
            "change evidence must be a non-empty list of single-line strings"
        )


def _draft(
    draft: Mapping[str, object], base: str, head: str, version: str
) -> tuple[str, str]:
    if not isinstance(draft, Mapping) or set(draft) != {
        "base_commit",
        "head_commit",
        "changes",
    }:
        raise PublicReleaseError(
            "content_draft must contain base_commit, head_commit and changes"
        )
    if draft["base_commit"] != base or draft["head_commit"] != head:
        raise PublicReleaseError(
            "content_draft commit pins do not match the comparison"
        )
    changes = draft["changes"]
    if not isinstance(changes, list) or not changes:
        raise PublicReleaseError(
            "content_draft.changes must be a non-empty list"
        )
    for change in changes:
        _validate_change(change)
    if not 1 <= sum(change["highlight"] for change in changes) <= 5:
        raise PublicReleaseError(
            "mark between one and five changes as highlights"
        )
    description = f"# ANECHOIC {version}\n\n## Changes\n\n"
    for change in changes:
        evidence = ", ".join(item.strip() for item in change["evidence"])
        description += (
            f"### {change['title'].strip()}\n\n"
            f"{change['details'].strip()}\n\nEvidence: {evidence}\n\n"
        )
    history = f"## {version}\n\n" + "".join(
        f"- {change['title'].strip()}\n"
        for change in changes
        if change["highlight"]
    )
    return description, history


def _draft_example(base: str, head: str) -> dict[str, object]:
    return {
        "base_commit": base,
        "head_commit": head,
        "changes": [
            {
                "title": "brief history bullet",
                "details": "detailed PR description",
                "evidence": ["ticket ID or changed path"],
                "highlight": True,
            }
        ],
    }
