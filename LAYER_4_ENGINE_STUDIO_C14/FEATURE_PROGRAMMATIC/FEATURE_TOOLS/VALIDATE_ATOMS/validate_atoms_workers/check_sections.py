"""Pinned Graph Rule authority sources."""

from __future__ import annotations

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import get_profile  # fmt: skip


GRAPH_RULE_SOURCES = (
    "CA-R-2001",
    "CA-D-637",
    "CA-R-1996",
    *(source.atom_id for source in get_profile("approved").grammar_pins),
)
