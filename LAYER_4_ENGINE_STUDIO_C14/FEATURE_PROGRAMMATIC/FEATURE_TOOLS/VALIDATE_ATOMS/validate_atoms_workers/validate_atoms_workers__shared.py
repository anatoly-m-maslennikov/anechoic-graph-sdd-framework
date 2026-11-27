"""Expose carrier parsing and the source-backed Graph Rule check."""

from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        CarrierError,
        ParsedCarrier,
        parse_carrier,
    )  # fmt: skip

from .authority import AuthorityContext, Obligation, Record
from .check_sections import GRAPH_RULE_SOURCES
from .check_support import Check
from .graph_rule_body import (
    ValidatedGraphRulePayload,
    validate_graph_rule_body,
    validated_graph_rule_payload,
)
from .support_authority import require_sources


class GraphRuleInspection(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    payload: ValidatedGraphRulePayload | None
    authority: list[dict] | None
    diagnostics: list[str]


def inspect_graph_rule(
    body: str, sources: list[Record]
) -> GraphRuleInspection:
    """Check a Graph Rule body against the supplied exact authority sources."""
    context = AuthorityContext([], 0, 0, 0, [], (), {}, True)
    obligation = Obligation(
        "declaration.graph_rule.body",
        [],
        True,
        "Validate the body under currently verified Graph Rule authority.",
    )
    check = Check(obligation, context, {"sources": sources})
    authority_ok = require_sources(check, GRAPH_RULE_SOURCES)
    payload = validated_graph_rule_payload(body, check)
    return GraphRuleInspection(
        payload=payload,
        authority=list(check.obligation.authority) if authority_ok else None,
        diagnostics=[
            finding["reason"] for finding in (*check.findings, *check.gaps)
        ],
    )


__all__ = [
    "CarrierError",
    "GraphRuleInspection",
    "ParsedCarrier",
    "inspect_graph_rule",
    "parse_carrier",
    "validate_graph_rule_body",
    "validated_graph_rule_payload",
]
