"""Promotion of a Ticket and its contained Tickets."""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    native_ticket_asset,
    DRAFT_DIRECTORY,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    frontmatter_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)

from .directory_effect import _read_tree
from .common import InputError, SourceChanged, result


from .native_update_selection import _branch, _descendants, _status_bytes
from .native_replacement_promotion import (
    _archive_replacements,
    _check_replacement_activation,
    _plan_replacements,
)


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
    pending = list(children.get(selected['id'], ()))
    if pending and (not close_tree or not companion.is_dir()):
        raise InputError(
            "target", "Ticket descendants require their companion directory."
        )
    visited = {selected['id']}
    terminal = {'done', 'canceled', 'resolved', 'complete'}
    while pending:
        child = pending.pop()
        if child["id"] in visited:
            raise InputError("target", "Ticket containment contains a cycle.")
        if require_terminal and child["status"] not in terminal:
            raise InputError(
                "target",
                "Current descendants must be terminal before this Status change.",
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
                    "Ticket descendants disagree with the companion directory.",
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
            raise SourceChanged('Ticket companion changed during validation.')


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
                    'Recover the interrupted child publication before '
                    'promoting its owner.'
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
    root_path = selection.root / selected['source_path']
    before = _descendants(original_rows, selected['id'], include_drafts=True)
    descendants = _descendants(rows, selected['id'], include_drafts=True)
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


def _promotion_actions(selection, descendants, owners, status):
    actions = []
    for row in descendants:
        context = native_header_view(row['header_json']).get('context', {})
        source = selection.root / row['source_path']
        owner = owners[context['container']['atom']]
        owner_context = native_header_view(owner['header_json']).get('context', {})
        branch = (selection.root / owner['source_path']).with_suffix('')
        folder = {'draft': DRAFT_DIRECTORY, 'active': '', 'in_queue': ''}.get(row['status'], row['status'])
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
    from .native_update import _move_ticket
    prepared, failure = _prepare_promotions(selection, actions, status)
    if failure is not None:
        return failure
    recorded = []
    for plan, draft in replacements:
        outcome = _archive_replacements(selection, [plan], draft)
        recorded.extend(outcome['effects'])
        if outcome['errors']:
            return result(effects=recorded, errors=outcome['errors'])
    for row, source, dest, raw, bounds in prepared:
        try:
            tree = (
                _read_tree(selection.root, source.with_suffix(""))
                if source.with_suffix("").is_dir()
                else None
            )
        except (OSError, RuntimeError, ValueError) as error:
            return result(effects=recorded, errors=[{'code': 'source_changed', 'target': row['id'],
                                                     'message': str(error)}])
        outcome = _move_ticket(selection, {'ref_id': row['ref'], 'version': row['version']}, row,
                               row['_source_sha256'], source, dest, status, check_definition,
                               close_tree=True, locked=True, preflight=(raw, bounds, tree))
        recorded.extend(outcome.get('effects', ()))
        if outcome.get('errors'):
            return result(effects=recorded, errors=[{**error, 'target': row['id']} for error in outcome['errors']])
    return result(effects=recorded, artifact=outcome['artifact'])


def _prepare_promotions(selection, actions, status):
    planned_destinations = set()
    prepared = []
    for row, source, dest in actions:
        if (
            dest in planned_destinations
            or dest.exists()
            or dest.is_symlink()
            or dest.with_suffix("").exists()
            or dest.with_suffix("").is_symlink()
        ):
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
            raise SourceChanged('Ticket or companion changed after selection.') from error
        _status_bytes(raw, bounds, source, status)
        prepared.append((row, source, dest, raw, bounds))
    return prepared, None
