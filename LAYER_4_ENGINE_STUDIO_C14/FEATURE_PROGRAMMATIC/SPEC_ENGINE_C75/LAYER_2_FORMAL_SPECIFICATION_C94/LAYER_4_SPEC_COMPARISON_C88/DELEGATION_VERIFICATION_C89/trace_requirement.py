"""Extract a provider requirement from a workflow effect."""

# fmt: off
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import (HTTP_BINDING_INPUTS, http_binding, json_equal)
# fmt: on
from .._package__shared import _operation_claims
from .manifest_delegation import CLI_INPUT_FIELDS


_TRACE_BINDING = {"interface", "transport", "entry", "route", "operation"}
_CLI_BINDING = {"command", *CLI_INPUT_FIELDS}
_CALL_BINDING = _TRACE_BINDING | _CLI_BINDING | HTTP_BINDING_INPUTS


def _call_detail(expect, manifest):
    detail = expect.get("detail", {})
    if not manifest or detail.get("transport") != "http":
        return detail
    try:
        binding = http_binding(detail)
    except ValueError:
        return {}
    return {
        **{key: detail[key] for key in detail.keys() - HTTP_BINDING_INPUTS},
        **binding,
    }


def _binding_fields(transport, manifest, manifest_pin):
    fields = (
        _TRACE_BINDING | HTTP_BINDING_INPUTS
        if transport == "http"
        else _TRACE_BINDING
    )
    if manifest or manifest_pin:
        fields = fields | {"manifest"}
        if manifest and transport == "cli":
            fields |= _CLI_BINDING
        elif manifest and transport == "http":
            fields.add("request_fields")
    return fields


def _requirement(
    workflow,
    event,
    interface=None,
    *,
    caller_action=None,
    manifest=False,
    manifest_pin=False,
    sibling=False,
):
    expect = _selected_effect(workflow, event, interface, caller_action)
    if expect is None:
        return {}
    detail = _call_detail(expect, manifest or sibling)
    names = {key: detail.get(key) for key in ("component", "action", "output")}
    effect = (expect.get("target"), expect.get("outcome"))
    if not all(
        isinstance(value, str) and value.strip()
        for value in (*effect, *names.values())
    ):
        return {}
    transport = detail.get("transport")
    if sibling and transport is None and "entry" in detail:
        detail = {**detail, "transport": "in_process"}
        transport = "in_process"
    fields = _binding_fields(transport, manifest, manifest_pin)
    qualifiers = {
        key: value
        for key, value in detail.items()
        if key not in fields and key not in names
    }
    if qualifiers:
        effect = (*effect, qualifiers)
    metadata = _requirement_metadata(
        detail, fields, transport, manifest, manifest_pin, sibling
    )
    return {**names, "effect": effect, **metadata}


def _selected_effect(workflow, event, interface, caller_action):
    if caller_action is None:
        operations = workflow.get("operations", {"": workflow}).values()
    else:
        operations = (_operation_claims(workflow).get(caller_action, {}),)
    selected = [
        row["expect"]
        for model in operations
        for state in model.get("states", [])
        for row in state["transitions"]
        if row["event"] == event
    ]
    if interface is not None and any(
        expect.get("detail", {}).get("interface") != interface
        for expect in selected
    ):
        raise ValueError(
            f"The selected event does not use interface {interface}"
        )
    if (
        not selected
        or selected[0]["kind"] != "effect"
        or any(not json_equal(expect, selected[0]) for expect in selected[1:])
    ):
        return None
    return selected[0]


def _requirement_metadata(
    detail, fields, transport, manifest, manifest_pin, sibling
):
    metadata = (
        {key: detail[key] for key in fields & detail.keys()}
        if manifest
        else (
            {"manifest": detail["manifest"]}
            if manifest_pin and "manifest" in detail
            else {}
        )
    )
    request_fields = metadata.get("request_fields")
    if isinstance(request_fields, list) and all(
        isinstance(field, str) for field in request_fields
    ):
        metadata["request_fields"] = sorted(request_fields)
    metadata.update(
        {
            key: detail[key]
            for key in (
                "interface",
                "transport",
                "entry",
                "endpoint",
                "route_name",
            )
            if sibling and transport is not None and key in detail
        }
    )
    return metadata
