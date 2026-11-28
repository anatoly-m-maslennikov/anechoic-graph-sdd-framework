"""Project structured Python Claim helpers and special declarations."""

from __future__ import annotations

import json as json
import re as re
from collections.abc import Mapping
from typing import Any

from ..primitives.primitives__shared import (
    _COUNT as _COUNT,
    _OPERATOR_SUBJECT as _OPERATOR_SUBJECT,
    _count as _count,
    _named_property_count as _named_property_count,
    _record as _record,
    _sibling_order as _sibling_order,
)

from ._native_claim_helper_primitives import (
    _native_count as _native_count,
    _native_relation as _native_relation,
    _helper_count as _helper_count,
    _count_text as _count_text,
)
from ._native_claim_helper_calls import (
    _helper_call_0 as _helper_call_0,
    _helper_call_1 as _helper_call_1,
    _helper_call_2 as _helper_call_2,
)
from ._native_claim_special_fields import (
    _native_special_fields as _native_special_fields,
)


Record = dict[str, Any]


def _helper_records(
    calls: tuple, carrier: Mapping[str, Any]
) -> tuple[list[Record], list[Record]] | None:
    """Project the helper calls used by Current Python Formal Claims."""
    if any(
        call["name"]
        not in {
            "composition",
            "relation",
            "deliver",
            "set_value",
            "subject_path",
            "property_rule",
            "order_before",
            "classify",
        }
        for call in calls
    ):
        return None
    source = carrier["source"]
    rows, diagnostics = [], []
    for call in calls:
        name, args, group = call["name"], call["arguments"], call["scope"]
        suffix = {"group": group} if group else {}
        for project in (_helper_call_0, _helper_call_1, _helper_call_2):
            accepted = project(
                name, args, group, source, carrier, rows, diagnostics, suffix
            )
            if accepted is not None:
                if not accepted:
                    return None
                break
        else:
            return None
    return rows, diagnostics


def _add_aspect_rows(paths, memberships, source, group, rows):
    for path in paths:
        left, right = path.split(" <+ ", 1)
        rows.append(
            _native_relation(
                source,
                left,
                right,
                notation="<+",
                expression=path,
                group=group,
            )
        )
    for address in memberships:
        left = f"({address})"
        rows.append(
            _native_relation(
                source,
                left,
                "Aspect",
                relation="INSTANCE_OF",
                expression=f"{left} ((INSTANCE_OF)) Aspect",
                group=group,
            )
        )


def _native_special(
    declaration: Mapping[str, Any], source: Mapping[str, Any]
) -> list[Record]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
        validate_aspect_hierarchy,
        validate_aspect_instance,
    )
    from ....ADAPTERS_C30.model.python.dataclass_field_contract__pub import (
        validate_field_contracts,
    )

    args = declaration["arguments"]
    rows = []
    if "structure_paths" in args:
        paths, memberships = validate_aspect_hierarchy(dict(args))
        group = "instances"
    elif args.get("instance", {}).get("type") == "Aspect":
        address = validate_aspect_instance(dict(args))
        paths, memberships = (address,), (address,)
        group = None
    else:
        paths, memberships = (), ()
        group = None
    _add_aspect_rows(paths, memberships, source, group, rows)
    for axis, values in args.get("allowed_axis_values", {}).items():
        for value in values:
            subject = args["entity_name"]
            expression = f"{subject} >| {axis}: {value}"
            rows.append(
                _record(
                    source,
                    expression,
                    "axis_allowed_value",
                    subject_selector=subject,
                    axis=axis,
                    value=value,
                    group="model",
                )
            )
    _native_special_fields(
        declaration, source, args, rows, validate_field_contracts
    )
    return rows
