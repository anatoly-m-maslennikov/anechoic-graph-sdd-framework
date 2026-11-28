"""Promotion of a Ticket and its contained Tickets."""

from __future__ import annotations

from hashlib import sha256

from ....ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    DRAFT_DIRECTORY,
    native_header_view,
    native_ticket_asset,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds,
    parse_carrier,
)

from .._ticket_companion_checks import (
    _check_ticket_companion as _check_ticket_companion,
    _check_ticket_tree as _check_ticket_tree,
    _check_promotion_companion,
)
from ..tickets.directory_effect import _read_tree
from ...common import InputError, SourceChanged, result


from ..native_update_selection import _descendants, _status_bytes
from .native_replacement_promotion import (
    _archive_replacements,
    _check_replacement_activation,
    _plan_replacements,
)


def promote_ticket_tree(
    selection,
    selected,
    destination,
    status,
    original_rows,
    capture,
    check_definition,
):
    rows = capture.atoms
    root_path = selection.root / selected["source_path"]
    before = _descendants(original_rows, selected["id"], include_drafts=True)
    descendants = _descendants(rows, selected["id"], include_drafts=True)
    if before != descendants:
        raise SourceChanged("Ticket descendants changed after selection.")
    owners = {row["id"]: row for row in [selected, *descendants]}
    _check_promotion_companion(
        selection, root_path.with_suffix(""), rows, owners
    )
    actions = _promotion_actions(selection, descendants, owners, status)
    actions.append((selected, root_path, destination))
    replacements = {}
    for row, _, _ in actions:
        if row["status_group"] == "Draft":
            for plan in _plan_replacements(
                selection, row, original_rows, None, capture
            ):
                replacements.setdefault(plan[0]["id"], (plan, row))
    if status == "active":
        _check_replacement_activation(
            [row for row, _, _ in actions], rows, replacements
        )
    return _apply_promotions(
        selection, actions, status, check_definition, replacements.values()
    )


def _descendant_location(selection, row, owners, context):
    source = selection.root / row["source_path"]
    owner = owners[context["container"]["atom"]]
    owner_context = native_header_view(owner["header_json"]).get("context", {})
    branch = (selection.root / owner["source_path"]).with_suffix("")
    folder = {"draft": DRAFT_DIRECTORY, "active": "", "in_queue": ""}.get(
        row["status"], row["status"]
    )
    expected = {branch / folder}
    if row["status"] == "draft":
        expected.add(branch / "000_draft")
    if native_ticket_asset(context.get("template")):
        expected.add(branch / "ASSETS" / folder)
        if row["status"] == "draft":
            expected.add(branch / "ASSETS" / "000_draft")
    if (
        owner_context.get("template") not in ("task", "epic")
        or source.parent not in expected
    ):
        raise InputError(
            "target",
            "Ticket descendant placement disagrees with its container.",
        )
    return source, branch


def _promotion_actions(selection, descendants, owners, status):
    actions = []
    for row in descendants:
        context = native_header_view(row["header_json"]).get("context", {})
        source, branch = _descendant_location(selection, row, owners, context)
        if context.get("template") not in ("task", "epic") or (
            row["status"] != "draft"
            and (
                row["status"] != "backlog"
                or status not in {"active", "in_queue"}
            )
        ):
            continue
        name = source.name
        prefix = row["_exact_ref"] if row["status"] == "draft" else row["id"]
        if not name.startswith(prefix + "-"):
            raise InputError(
                "target", "Ticket descendant filename is invalid."
            )
        dest = (
            branch
            / ("" if status in {"active", "in_queue"} else status)
            / (row["id"] + name[len(prefix) :])
        )
        actions.append((row, source, dest))
    return actions


def _apply_promotions(
    selection, actions, status, check_definition, replacements
):
    from ..native_update__shared import _move_ticket

    prepared, failure = _prepare_promotions(selection, actions, status)
    if failure is not None:
        return failure
    recorded = []
    for plan, draft in replacements:
        outcome = _archive_replacements(selection, [plan], draft)
        recorded.extend(outcome["effects"])
        if outcome["errors"]:
            return result(effects=recorded, errors=outcome["errors"])
    for entry in prepared:
        row, source = entry[:2]
        try:
            tree = (
                _read_tree(selection.root, source.with_suffix(""))
                if source.with_suffix("").is_dir()
                else None
            )
        except (OSError, RuntimeError, ValueError) as error:
            return result(
                effects=recorded,
                errors=[
                    {
                        "code": "source_changed",
                        "target": row["id"],
                        "message": str(error),
                    }
                ],
            )
        outcome = _move_prepared(
            _move_ticket, selection, entry, status, check_definition, tree
        )
        recorded.extend(outcome.get("effects", ()))
        if outcome.get("errors"):
            return result(
                effects=recorded,
                errors=[
                    {**error, "target": row["id"]}
                    for error in outcome["errors"]
                ],
            )
    return result(effects=recorded, artifact=outcome["artifact"])


def _move_prepared(move, selection, entry, status, check_definition, tree):
    row, source, dest, raw, bounds = entry
    return move(
        selection,
        {"ref_id": row["ref"], "version": row["version"]},
        row,
        row["_source_sha256"],
        source,
        dest,
        status,
        check_definition,
        close_tree=True,
        locked=True,
        preflight=(raw, bounds, tree),
    )


def _destination_conflict(dest, planned):
    return (
        dest in planned
        or dest.exists()
        or dest.is_symlink()
        or dest.with_suffix("").exists()
        or dest.with_suffix("").is_symlink()
    )


def _prepare_promotions(selection, actions, status):
    planned_destinations = set()
    prepared = []
    for row, source, dest in actions:
        if _destination_conflict(dest, planned_destinations):
            return None, result(
                errors=[
                    {
                        "code": "destination_exists",
                        "message": "Ticket destination already exists.",
                        "target": row["id"],
                    }
                ]
            )
        planned_destinations.add(dest)
        try:
            reader = ReadContext(
                roots=[str(selection.control_root)], limits=dict(CEILINGS)
            )
            raw = reader.read(source)
            bounds = frontmatter_bounds(raw)
            if (
                bounds is None
                or sha256(raw).hexdigest() != row.get("_source_sha256")
                or parse_carrier(raw, source).metadata
                != row.get("header_json")
            ):
                raise ValueError("Ticket carrier changed.")
            if (
                source.with_suffix("").exists()
                or source.with_suffix("").is_symlink()
            ):
                _read_tree(selection.root, source.with_suffix(""))
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise SourceChanged(
                "Ticket or companion changed after selection."
            ) from error
        _status_bytes(raw, bounds, source, status)
        prepared.append((row, source, dest, raw, bounds))
    return prepared, None
