"""Bounded updates for a selected Current native Ticket."""

from __future__ import annotations

from contextlib import nullcontext as nullcontext
from functools import partial as partial
from hashlib import sha256 as sha256


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view as native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_ticket_asset as native_ticket_asset,
    COMPLETE_DIRECTORY as COMPLETE_DIRECTORY,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    CURRENT_STATUSES as CURRENT_STATUSES,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    capture_native as capture_native,
    revalidate_native as revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds as frontmatter_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from ...ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext as ReadContext,
)

from .. import effects as effects
from ..effects import _project_write_lock as _project_write_lock
from .tickets.directory_effect import (
    _read_tree as _read_tree,
    move_directory as move_directory,
)
from ..common import (
    InputError as InputError,
    SourceChanged as SourceChanged,
    _create_parents as _create_parents,
    result as result,
    saved as saved,
)
from .native_update_selection import (
    _select_ticket as _select_ticket,
    _status_bytes as _status_bytes,
    _branch as _branch,
    _descendants as _descendants,
)
from .native_update_publish import _publish_ticket as _publish_ticket
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates._ticket_companion_checks import (
    _check_ticket_tree as _check_ticket_tree,
)
from .replacement.native_update_promotion import (
    promote_ticket_tree as promote_ticket_tree,
)


from .tickets import native_ticket_read as _ticket_read
from .tickets import native_ticket_move as _ticket_move
from .tickets import native_ticket_policy as _ticket_policy
from .tickets import native_ticket_actions__shared as _ticket_actions
from .tickets import native_ticket_status as _ticket_status


def _read_ticket(
    selection,
    target,
    selected,
    digest,
    path,
    *,
    close_tree=False,
    placement=False,
    require_terminal=False,
    previous_capture=None,
    domains=None,
):
    return _ticket_read.read_ticket(
        selection,
        target,
        selected,
        digest,
        path,
        close_tree=close_tree,
        placement=placement,
        require_terminal=require_terminal,
        previous_capture=previous_capture,
        domains=domains,
    )


def _prepare_ticket_directory(
    selection, destination, recorded, recorded_errors, check
):
    return _ticket_move.prepare_directory(
        selection, destination, recorded, recorded_errors, check
    )


def _ticket_source_intact(
    selection, path, digest, close_tree, tree, companion
):
    return _ticket_move.source_intact(
        selection, path, digest, close_tree, tree, companion
    )


def _ticket_definition_intact(check_definition, errors):
    return _ticket_move.definition_intact(check_definition, errors)


def _move_ticket(
    selection,
    target,
    selected,
    digest,
    path,
    destination,
    status,
    check_definition,
    *,
    close_tree=False,
    require_terminal=False,
    locked=False,
    preflight=None,
    previous_capture=None,
    domains=None,
    candidate=None,
):
    return _ticket_move.move_ticket(
        selection,
        target,
        selected,
        digest,
        path,
        destination,
        status,
        check_definition,
        close_tree=close_tree,
        require_terminal=require_terminal,
        locked=locked,
        preflight=preflight,
        previous_capture=previous_capture,
        domains=domains,
        candidate=candidate,
    )


def _check_ticket_transition(selected, template, status, project_statuses):
    return _ticket_policy._check_ticket_transition(
        selected, template, status, project_statuses
    )


def _apply_status_actions(
    selection,
    actions,
    selected,
    status,
    current_rows,
    terminal,
    check_definition,
    raw,
    bounds,
    tree,
    recorded,
    domains,
):
    return _ticket_actions.apply_actions(locals())


def _ticket_template(selected, status, project_statuses):
    return _ticket_policy._ticket_template(selected, status, project_statuses)


def _ticket_status_domain(domains):
    return _ticket_policy._ticket_status_domain(domains)


def ticket_status_options(metadata, domains=None):
    """List candidate Current Status moves under the same policy as a write."""
    return _ticket_policy.ticket_status_options(metadata, domains)


def _requested_status(value, allowed):
    return _ticket_policy._requested_status(value, allowed)


def change_ticket_status(
    selection, params, *, current_rows, check_definition, previous_capture=None
):
    return _ticket_status.change_status(locals())
