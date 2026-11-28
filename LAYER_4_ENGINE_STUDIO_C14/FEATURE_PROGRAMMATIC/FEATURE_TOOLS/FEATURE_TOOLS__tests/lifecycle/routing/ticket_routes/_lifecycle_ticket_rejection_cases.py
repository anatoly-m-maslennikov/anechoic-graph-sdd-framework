"""Ticket route rejection case construction."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
    archive_spec_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared import (
    change_spec_status,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    direct_update,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class TicketRejectionCases:
    def _ticket_calls(self, template, situation, target):
        calls = [
            (
                change_spec_status,
                {"target": target, "targetStatus": "active"},
            ),
            (archive_spec_draft, {"target": target}),
        ]
        if situation != "current":
            calls.append(
                (
                    change_ticket_status,
                    {"target": target, "targetStatus": "done"},
                )
            )
        if situation in ("draft", "archived") or (
            situation == "current" and template not in ("task", "epic")
        ):
            calls.append((create_draft, {"sourceCurrent": target}))
        return self._remaining_ticket_calls(calls, template, situation, target)

    def _remaining_ticket_calls(self, calls, template, situation, target):
        if situation in ("new", "archived") or template in (
            "task",
            "epic",
            "problem",
            "question",
            "code_spec_mismatch",
            "opportunity",
        ):
            calls.append(
                (
                    direct_update,
                    {
                        "target": target,
                        "changes": {"body": "\n## Summary\n\nExample\n"},
                    },
                )
            )
        if situation != "draft" or template not in (
            "task",
            "epic",
        ):
            calls.append(
                (
                    promote_draft,
                    {
                        "target": target,
                        "targetStatus": "backlog",
                    },
                )
            )
        return calls
