"""Prepare public release drafts from pinned Git evidence without side effects."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
import subprocess
import tomllib
from typing import Literal

from pydantic import BaseModel, ConfigDict


_REVIEW_INSTRUCTIONS = (
    "Delegate a Luna review of the pinned Git diff against completed Task "
    "and Epic evidence. Start with the pinned --stat and --name-status "
    "commands, then inspect path-scoped patches to narrow the diff. Include "
    "missed changes. Return one UTF-8 JSON object matching "
    "content_draft_schema; use full commit pins."
)


class PublicReleaseError(ValueError):
    """The release comparison or reviewed content is invalid."""


class _CompletedTicket(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str
    content: str


class _ReleaseResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    run_id: str
    base_commit: str
    head_commit: str
    merge_base: str
    version: str


class _CompletedRelease(_ReleaseResult):
    outcome: Literal["completed"] = "completed"
    pr_description: str
    version_history_entry: str


class _ReleaseReview(_ReleaseResult):
    outcome: Literal["input_required"] = "input_required"
    completed_tickets: list[_CompletedTicket]
    diff_argv: list[str]
    instructions: str
    diff_stat_argv: list[str]
    diff_name_status_argv: list[str]
    content_draft_schema: dict[str, object]


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ("git", *args), cwd=root, capture_output=True, text=True, encoding="utf-8", check=False, timeout=120,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as error:
        raise PublicReleaseError(f"git {args[0]} could not read the release comparison") from error
    if result.returncode:
        raise PublicReleaseError(f"git {args[0]} failed")
    return result.stdout


def _commit(root: Path, ref: str) -> str:
    if not isinstance(ref, str) or not ref or ref.startswith("-"):
        raise PublicReleaseError("invalid Git ref")
    commit = _git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").strip()
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        raise PublicReleaseError("invalid Git commit resolved")
    return commit


def _validate_change(change):
    if not isinstance(change, Mapping) or set(change) != {
        "title", "details", "evidence", "highlight",
    }:
        raise PublicReleaseError(
            "each change must contain title, details, evidence and highlight"
        )
    if any(
        not isinstance(change[key], str) or not change[key].strip()
        or "\n" in change[key] for key in ("title", "details")
    ):
        raise PublicReleaseError(
            "change title and details must be non-empty single-line strings"
        )
    if not isinstance(change["highlight"], bool):
        raise PublicReleaseError("change highlight must be a boolean")
    if change["highlight"] and len(change["title"].strip()) > 120:
        raise PublicReleaseError("highlight titles must be at most 120 characters")
    evidence = change["evidence"]
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(item, str) or not item.strip() or "\n" in item
        for item in evidence
    ):
        raise PublicReleaseError(
            "change evidence must be a non-empty list of single-line strings"
        )


def _draft(draft: Mapping[str, object], base: str, head: str, version: str) -> tuple[str, str]:
    if not isinstance(draft, Mapping) or set(draft) != {"base_commit", "head_commit", "changes"}:
        raise PublicReleaseError("content_draft must contain base_commit, head_commit and changes")
    if draft["base_commit"] != base or draft["head_commit"] != head:
        raise PublicReleaseError("content_draft commit pins do not match the comparison")
    changes = draft["changes"]
    if not isinstance(changes, list) or not changes:
        raise PublicReleaseError("content_draft.changes must be a non-empty list")
    for change in changes:
        _validate_change(change)
    if not 1 <= sum(change["highlight"] for change in changes) <= 5:
        raise PublicReleaseError("mark between one and five changes as highlights")
    description = f"# ANECHOIC {version}\n\n## Changes\n\n"
    for change in changes:
        description += f"### {change['title'].strip()}\n\n{change['details'].strip()}\n\nEvidence: {', '.join(item.strip() for item in change['evidence'])}\n\n"
    history = f"## {version}\n\n" + "".join(f"- {change['title'].strip()}\n" for change in changes if change["highlight"])
    return description, history


def _ticket_candidates(root: Path, merge_base: str, head: str):
    raw = _git(root, "diff", "--raw", "--no-abbrev", "--no-renames", "-z", "--diff-filter=AM", merge_base, head, "--",
               *(f":(glob)[._]anechoic_*/{branch}/TASKS/**/*-{kind}--*.md"
                 for branch in ("__TICKETS", "001_TICKETS", "__TKT") for kind in ("TASK", "EPIC"))).split("\0")
    candidates = []
    for meta, path in zip(raw[0::2], raw[1::2], strict=False):
        fields = meta.split()
        parts = Path(path).parts
        name = re.fullmatch(r"([A-Z]+-T-[0-9]+)-(TASK|EPIC)--[^/]+\.md", parts[-1])
        if (len(fields) == 5 and fields[1] in ("100644", "100755") and name
                and not any(re.fullmatch(r"(?:[0-9]+_)?(?:archive|archived|snapshot|snapshots)", part, re.I) for part in parts)):
            candidates.append((path, fields[3], name.group(1), name.group(2).lower()))
    return candidates


def _ticket_blob(output, oid):
    header, separator, output = output.partition(b"\n")
    fields = header.split()
    if (
        not separator or len(fields) != 3 or fields[0].decode() != oid
        or fields[1] != b"blob"
    ):
        raise PublicReleaseError("invalid Git ticket batch")
    size = int(fields[2])
    content, output = output[:size], output[size:]
    if not output.startswith(b"\n") or len(content) != size:
        raise PublicReleaseError("invalid Git ticket batch")
    return content, output[1:]


def _ticket_evidence(root: Path, candidates) -> list[_CompletedTicket]:
    tickets = []
    if candidates:
        try:
            batch = subprocess.run(
                ("git", "cat-file", "--batch"), cwd=root,
                input="".join(f"{oid}\n" for _, oid, _, _ in candidates).encode(),
                capture_output=True, check=False, timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise PublicReleaseError("git cat-file could not read the ticket evidence") from error
        if batch.returncode:
            raise PublicReleaseError("git cat-file failed")
        output = batch.stdout
        seen = set()
        for path, oid, ticket_id, kind in candidates:
            content, output = _ticket_blob(output, oid)
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError as error:
                raise PublicReleaseError(f"ticket is not UTF-8: {path}") from error
            header = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
            if header is None:
                continue
            front = header[1].replace("\r\n", "\n")
            if (not re.search(rf"""(?m)^atom_id:[ \t]*(['"]?){re.escape(ticket_id)}\1[ \t]*$""", front)
                    or not re.search(rf"""(?m)^  template:[ \t]*(['"]?){kind}\1[ \t]*$""", front)
                    or not re.search(r"""(?m)^state:[ \t]*\n(?:  [^\n]*\n)*?  status:[ \t]*(['"]?)done\1[ \t]*$""", front)):
                continue
            if ticket_id in seen:
                raise PublicReleaseError(f"duplicate completed ticket ID: {ticket_id}")
            seen.add(ticket_id)
            tickets.append(_CompletedTicket(path=path, content=text))
    return tickets


def _draft_example(base: str, head: str) -> dict[str, object]:
    return {
        "base_commit": base,
        "head_commit": head,
        "changes": [{
            "title": "brief history bullet",
            "details": "detailed PR description",
            "evidence": ["ticket ID or changed path"],
            "highlight": True,
        }],
    }


def run_public_release(
    root: Path | str, *, run_id: str, base_ref: str = "origin/main", head_ref: str = "amm/dev",
    content_draft: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return evidence for review, or render drafts from a pinned reviewed mapping."""
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", run_id):
        raise PublicReleaseError("invalid run_id")
    try:
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError
    except (OSError, TypeError, ValueError) as error:
        raise PublicReleaseError("invalid project root") from error
    if _git(root, "rev-parse", "--show-toplevel").rstrip("\n") != str(root):
        raise PublicReleaseError("project root must be the Git checkout root")
    base, head = _commit(root, base_ref), _commit(root, head_ref)
    merge_base = _git(root, "merge-base", base, head).strip()
    try:
        version = tomllib.loads(_git(root, "show", f"{head}:version.toml"))["framework"]["version"]
        if not isinstance(version, str) or re.fullmatch(r"[0-9]+(?:\.[0-9]+){2,3}", version) is None:
            raise ValueError
    except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        raise PublicReleaseError("head version.toml must declare a framework version") from error
    fields = dict(run_id=run_id, base_commit=base, head_commit=head,
                  merge_base=merge_base, version=version)
    if content_draft is not None:
        description, history = _draft(content_draft, base, head, version)
        return _CompletedRelease(
            **fields, pr_description=description, version_history_entry=history,
        ).model_dump()
    candidates = _ticket_candidates(root, merge_base, head)
    return _ReleaseReview(
        **fields,
        completed_tickets=_ticket_evidence(root, candidates),
        diff_argv=["git", "diff", "--find-renames", merge_base, head, "--"],
        instructions=_REVIEW_INSTRUCTIONS,
        diff_stat_argv=["git", "diff", "--stat", merge_base, head, "--"],
        diff_name_status_argv=[
            "git", "diff", "--name-status", merge_base, head, "--"
        ],
        content_draft_schema=_draft_example(base, head),
    ).model_dump()
