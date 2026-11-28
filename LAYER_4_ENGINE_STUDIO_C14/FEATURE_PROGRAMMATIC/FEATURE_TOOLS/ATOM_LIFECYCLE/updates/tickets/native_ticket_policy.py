"""Validate and preview native Ticket status transitions."""

from .. import native_update__shared as owner


def _check_ticket_transition(selected, template, status, project_statuses):
    if "atom_family" in selected["header_json"]:
        issue = template in {
            "problem",
            "question",
            "code_spec_mismatch",
            "opportunity",
        }
        planning = template in {"task", "epic"}
        if issue or planning:
            terminals = (
                {"resolved", "canceled"} if issue else {"done", "canceled"}
            )
            previous = selected["status"]
            work = {"in_queue", "active"} | project_statuses
            permitted = (
                (
                    previous == "backlog"
                    and status in {"in_queue"} | project_statuses
                )
                or (
                    previous in work and status in terminals | project_statuses
                )
                or (
                    previous in {"active"} | project_statuses
                    and status == "in_queue"
                )
            )
            if not permitted:
                raise owner.InputError(
                    "targetStatus",
                    "Ticket Status transition is not supported "
                    "for its Template.",
                )


def _ticket_template(selected, status, project_statuses):
    template = (
        owner.native_header_view(selected["header_json"])
        .get("context", {})
        .get("template")
    )
    context = owner.native_header_view(selected["header_json"]).get(
        "context", {}
    )
    detached_asset = owner.native_ticket_asset(
        template
    ) and "component" in context.get("container", {})
    if status == "complete" and not detached_asset:
        raise owner.InputError(
            "targetStatus", "Only a standalone Ticket Asset can be completed."
        )
    if (
        detached_asset
        and status == "complete"
        and selected["status"] not in {"in_queue"} | project_statuses
    ):
        raise owner.InputError(
            "targetStatus", "Only an In Queue Asset can be completed."
        )
    owner._check_ticket_transition(
        selected, template, status, project_statuses
    )
    return template


def _ticket_status_domain(domains):
    return set(
        domains["T"] if domains is not None else owner.CURRENT_STATUSES["T"]
    ) - {"active", "draft", "archived"}


def ticket_status_options(metadata, domains=None):
    """List candidate Current Status moves under the same policy as a write."""
    current = owner.native_header_view(metadata)["state"]["status"]
    selected = {"header_json": metadata, "status": current}
    allowed = owner._ticket_status_domain(domains)
    project_statuses = allowed - owner.CURRENT_STATUSES["T"]
    options = []
    for status in sorted(
        allowed - {current}, key=lambda value: (value == "canceled", value)
    ):
        try:
            owner._ticket_template(selected, status, project_statuses)
        except owner.InputError:
            continue
        options.append(status)
    return options


def _requested_status(value, allowed):
    if not isinstance(value, str) or value.casefold() not in allowed:
        raise owner.InputError(
            "targetStatus",
            "Supply a Current Ticket Status.",
            allowed_values=allowed,
        )
    return value.casefold()
