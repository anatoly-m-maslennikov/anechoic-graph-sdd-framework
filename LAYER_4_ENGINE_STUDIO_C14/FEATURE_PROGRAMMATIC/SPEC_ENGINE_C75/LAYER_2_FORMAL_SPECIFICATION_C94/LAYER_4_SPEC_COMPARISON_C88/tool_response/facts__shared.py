"""Project terminal Tool API response and delivery observations."""


def _record(facts, key, value):
    previous = facts.get(key)
    if isinstance(previous, dict) and "conflicting_values" in previous:
        if value not in previous["conflicting_values"]:
            previous["conflicting_values"].append(value)
    elif key in facts and previous != value:
        facts[key] = {"conflicting_values": [previous, value]}
    else:
        facts[key] = value


def _derived(facts, key, detail, expected, result):
    if all(
        name in detail and type(detail[name]) is type(value)
        for name, value in expected.items()
    ):
        observed = {name: detail[name] for name in expected}
        _record(facts, key, [result if observed == expected else observed])


def _delivery_facts(facts, detail):
    types = detail.get("result_types")
    if isinstance(types, dict):
        for name in ("text", "value"):
            if isinstance(types.get(name), str):
                _record(facts, "output_format." + name, [types[name]])
    delivery = {"delivery_mode": "requested", "include_submitted_sql": False}
    observed = {
        key: detail[key]
        for key, value in delivery.items()
        if key in detail and type(detail[key]) is type(value)
    }
    if len(observed) < len(delivery) and any(
        observed[key] != delivery[key] for key in observed
    ):
        _record(facts, "guarantees.query_output", [observed])
    _derived(
        facts,
        "guarantees.query_output",
        detail,
        delivery,
        "requested_delivery_without_submitted_sql",
    )
    _derived(
        facts,
        "effects.query_result",
        detail,
        {"retain_result_by": "query_id"},
        "retained",
    )
    _derived(
        facts,
        "effects.bookmark",
        detail,
        {"bookmark_requires_save": True},
        "explicit_save_only",
    )


def _unclassified_failure(detail, outcome, errors, outcomes):
    if outcome == "failed":
        for name in ("invalid_input", "internal_error"):
            outcomes.setdefault(name, []).append([None, None])
        fields = detail.get("response_fields")
        if isinstance(fields, list) and all(
            isinstance(field, str) for field in fields
        ):
            _record(errors, "unclassified", sorted(fields))


def _response_facts(facts, detail, outcome, errors, outcomes):
    name = detail.get("http_outcome")
    if isinstance(value := detail.get("response_format"), str):
        _record(facts, "interface.response_format", [value])
    if name not in ("success", "invalid_input", "internal_error"):
        if outcome == "succeeded":
            name = "success"
            outcomes.setdefault(name, []).append([None, None])
        else:
            _unclassified_failure(detail, outcome, errors, outcomes)
            return
    if outcome != ("succeeded" if name == "success" else "failed"):
        raise ValueError(
            f"Solution output classification disagrees with {name}"
        )
    code, envelope = detail.get("status_code"), detail.get("envelope")
    outcomes.setdefault(name, []).append(
        [
            code if type(code) is int else None,
            envelope if isinstance(envelope, str) else None,
        ]
    )
    if name == "internal_error" and isinstance(
        message := detail.get("message"), str
    ):
        _record(facts, "error_handling.internal_message", [message])
    fields = detail.get("response_fields")
    if not isinstance(fields, list) or not all(
        isinstance(field, str) for field in fields
    ):
        return
    if name == "success":
        _record(facts, "output_format.result_fields", sorted(fields))
    else:
        _record(errors, name, sorted(fields))


def _terminal_facts(facts, errors, outcomes, detail, outcome, dispatched):
    if outcome not in ("succeeded", "failed") or detail.get(
        "http_outcome"
    ) not in ("success", "invalid_input", "internal_error"):
        facts["_unclassified_terminal"] = True
    _response_facts(facts, detail, outcome, errors, outcomes)
    if outcome == "succeeded":
        _delivery_facts(facts, detail)
    if detail.get("http_outcome") == "invalid_input":
        if detail.get("provider_dispatched") is False and dispatched:
            raise ValueError(
                "Solution invalid input follows provider dispatch"
            )
        if dispatched:
            detail = {**detail, "provider_dispatched": True}
        _derived(
            facts,
            "effects.invalid_input_dispatch",
            detail,
            {"provider_dispatched": False},
            "none",
        )
    return detail


def _error_facts(facts, errors, expected):
    observed = {}
    for value in errors.values():
        for fields in (
            value.get("conflicting_values", [])
            if isinstance(value, dict)
            else [value]
        ):
            _record(observed, "error_handling.error_fields", fields)
    value = observed.get("error_handling.error_fields")
    if (
        isinstance(value, dict)
        or {"invalid_input", "internal_error"} <= errors.keys()
        or (
            expected
            and value is not None
            and value != expected.get("error_handling.error_fields")
        )
    ):
        facts.update(observed)


def _response_coverage(facts, responses, expected):
    for key, field, applicable in (
        ("interface.response_format", "response_format", lambda outcome: True),
        (
            "output_format.result_fields",
            "response_fields",
            lambda outcome: outcome == "succeeded",
        ),
        (
            "error_handling.error_fields",
            "response_fields",
            lambda outcome: outcome == "failed",
        ),
    ):
        details = [
            detail for detail, outcome in responses if applicable(outcome)
        ]
        missing = any(
            not isinstance(
                detail.get(field), str if field == "response_format" else list
            )
            or (
                field == "response_fields"
                and not all(isinstance(item, str) for item in detail[field])
            )
            for detail in details
        )
        value = facts.get(key)
        if (
            missing
            and not isinstance(value, dict)
            and (expected is None or value == expected.get(key))
        ):
            facts.pop(key, None)
    _dispatch_coverage(facts, responses, expected)


def _dispatch_coverage(facts, responses, expected):
    dispatch = "effects.invalid_input_dispatch"
    value = facts.get(dispatch)
    if (
        value == ["none"]
        and (expected is None or value == expected.get(dispatch, value))
        and any(
            detail.get("http_outcome") == "invalid_input"
            and detail.get("provider_dispatched") is not False
            for detail, _ in responses
        )
    ):
        del facts[dispatch]


_DELIVERY_SPECS = (
    (
        "output_format.text",
        ("result_types", "text"),
        str,
        ["string_or_null"],
    ),
    ("output_format.value", ("result_types", "value"), str, ["object"]),
    (
        "guarantees.query_output",
        ("delivery_mode", "include_submitted_sql"),
        (str, bool),
        ["requested_delivery_without_submitted_sql"],
    ),
    ("effects.query_result", ("retain_result_by",), (str,), ["retained"]),
    (
        "effects.bookmark",
        ("bookmark_requires_save",),
        (bool,),
        ["explicit_save_only"],
    ),
    ("error_handling.internal_message", ("message",), (str,), None),
)


def _delivery_coverage(facts, responses, expected):
    for key, fields, types, default in _DELIVERY_SPECS:
        details = [
            detail
            for detail, outcome in responses
            if (
                outcome == "succeeded"
                if default is not None
                else outcome == "failed"
                and detail.get("http_outcome") != "invalid_input"
            )
        ]
        missing = _delivery_missing(details, fields, types, default)
        value = facts.get(key)
        target = (expected or {}).get(key, default)
        if (
            missing
            and not isinstance(value, dict)
            and (value is None or value == target)
        ):
            facts.pop(key, None)


def _delivery_missing(details, fields, types, default):
    if isinstance(types, type):
        missing = any(
            not isinstance(detail.get(fields[0]), dict)
            or not isinstance(detail[fields[0]].get(fields[1]), types)
            for detail in details
        )
    else:
        missing = any(
            any(
                type(detail.get(field)) is not kind
                for field, kind in zip(fields, types)
            )
            for detail in details
        )
    if default is None and any(
        detail.get("http_outcome") != "internal_error" for detail in details
    ):
        missing = True
    return missing


def _outcome_facts(facts, outcomes, expected):
    for name, values in outcomes.items():
        conflicts = any(
            a is not None and b is not None and a != b
            for i, left in enumerate(values)
            for right in values[i + 1 :]
            for a, b in zip(left, right)
        )
        if conflicts:
            facts[f"outcomes.{name}"] = {"conflicting_values": values}
        elif all(None not in value for value in values):
            facts[f"outcomes.{name}"] = values[0]
        elif (target := (expected or {}).get(f"outcomes.{name}")) is not None:
            mismatch = next(
                (
                    value
                    for value in values
                    if any(
                        actual is not None and actual != wanted
                        for actual, wanted in zip(value, target)
                    )
                ),
                None,
            )
            if mismatch is not None:
                facts[f"outcomes.{name}"] = mismatch
