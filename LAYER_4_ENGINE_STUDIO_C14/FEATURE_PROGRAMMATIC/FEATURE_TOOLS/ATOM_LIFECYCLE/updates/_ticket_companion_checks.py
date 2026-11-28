"""Validate the Ticket companion against selected Atom descendants."""

from collections import defaultdict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view,
)
from ..common import InputError, SourceChanged
from .tickets.directory_effect import _read_tree
from .native_update_selection import _branch


def _check_ticket_tree(
    selection, path, selected, capture, tree, close_tree, require_terminal
):
    companion = path.with_suffix("")
    children = defaultdict(list)
    for row in capture.atoms:
        if row["status_group"] == "Current":
            owner = (
                native_header_view(row["header_json"])
                .get("context", {})
                .get("container", {})
                .get("atom")
            )
            if owner is not None:
                children[owner].append(row)
    pending = list(children.get(selected["id"], ()))
    if pending and (not close_tree or not companion.is_dir()):
        raise InputError(
            "target", "Ticket descendants require their companion directory."
        )
    visited = {selected["id"]}
    terminal = {"done", "canceled", "resolved", "complete"}
    while pending:
        child = pending.pop()
        if child["id"] in visited:
            raise InputError("target", "Ticket containment contains a cycle.")
        if require_terminal and child["status"] not in terminal:
            raise InputError(
                "target",
                (
                    "Current descendants must be terminal before this Status "
                    "change."
                ),
            )
        visited.add(child["id"])
        pending.extend(children.get(child["id"], ()))
    _check_ticket_companion(
        selection, path, selected, capture, tree, close_tree, visited
    )


def _check_ticket_companion(
    selection, path, selected, capture, tree, close_tree, visited
):
    companion = path.with_suffix("")
    if companion.exists() or companion.is_symlink():
        if not close_tree or companion.is_symlink() or not companion.is_dir():
            raise InputError(
                "target", "Direct updates of container Atoms are unsupported."
            )
        for child in capture.atoms:
            child_path = selection.root / child["source_path"]
            if child["id"] in visited - {
                selected["id"]
            } and not child_path.is_relative_to(companion):
                raise InputError(
                    "target",
                    (
                        "Ticket descendants disagree with the companion "
                        "directory."
                    ),
                )
            if child_path.is_relative_to(companion):
                owner = (
                    native_header_view(child["header_json"])
                    .get("context", {})
                    .get("container", {})
                    .get("atom")
                )
                if owner not in visited:
                    raise InputError(
                        "target",
                        "Ticket companion contains an unrelated Atom.",
                    )
                _branch(
                    selection,
                    child_path,
                    child["status"],
                    child,
                    capture.atoms,
                    allow_flat=False,
                )
        if _read_tree(selection.root, companion) != tree:
            raise SourceChanged("Ticket companion changed during validation.")


def _check_promotion_companion(selection, companion, rows, owners):
    for row in rows:
        row_path = selection.root / row["source_path"]
        if row["status_group"] == "Archived" or not row_path.is_relative_to(
            companion
        ):
            continue
        current = owners.get(row["id"])
        if (
            row["status_group"] == "Draft"
            and current is not None
            and current["status_group"] == "Current"
            and row["version"] == current["version"]
        ):
            raise InputError(
                "target",
                (
                    "Recover the interrupted child publication before "
                    "promoting its owner."
                ),
            )
        owner_id = (
            native_header_view(row["header_json"])
            .get("context", {})
            .get("container", {})
            .get("atom")
        )
        if owner_id not in owners:
            raise InputError(
                "target", "Ticket companion contains an unrelated Atom."
            )
