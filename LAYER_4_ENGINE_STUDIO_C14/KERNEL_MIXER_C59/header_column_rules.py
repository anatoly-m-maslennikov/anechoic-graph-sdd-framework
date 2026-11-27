"""Translate declared Header rules into column selectors and assets."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import matches_carrier_label  # fmt: skip
from .declaration_cfel import selector_key
from .declared_header_rules import HeaderRule


def _reader_name(rule: HeaderRule) -> str:
    return "atom_id" if rule.path == ("id",) else ".".join(rule.path)


def _selector_metadata(rule: HeaderRule) -> dict[str, Any]:
    if rule.roles is None or len(rule.roles) != 1:
        return {}
    return {"context": {"role": next(iter(rule.roles))}}


def _rule_applies(rule: HeaderRule, row: Mapping[str, Any]) -> bool:
    return (
        rule.roles is None
        or matches_carrier_label(row.get("role"), rule.roles)
    ) and (
        rule.forms is None
        or matches_carrier_label(row.get("form"), rule.forms)
    )


def _rule_shape(rule: HeaderRule) -> tuple[object, ...]:
    return (
        rule.path,
        rule.format,
        selector_key(rule.roles),
        selector_key(rule.forms),
    )


def _rule_key(rule: HeaderRule) -> tuple[object, ...]:
    format_source = rule.format_source
    return (
        *_rule_shape(rule),
        rule.source.reference or "",
        rule.source.version or -1,
        rule.source.source_path or "",
        format_source.reference or "" if format_source else "",
        format_source.version or -1 if format_source else -1,
        format_source.source_path or "" if format_source else "",
        tuple(
            (s.reference or "", s.version or -1, s.source_path or "")
            for s in rule.provenance
        ),
    )


def _rule_asset(rule: HeaderRule) -> dict[str, object]:
    return {
        "path": list(rule.path),
        "format": rule.format,
        "roles": sorted(rule.roles) if rule.roles is not None else None,
        "forms": sorted(rule.forms) if rule.forms is not None else None,
        "source": rule.source.asset(),
        "provenance": [source.asset() for source in rule.provenance],
        **(
            {"format_source": rule.format_source.asset()}
            if rule.format_source is not None
            else {}
        ),
    }
