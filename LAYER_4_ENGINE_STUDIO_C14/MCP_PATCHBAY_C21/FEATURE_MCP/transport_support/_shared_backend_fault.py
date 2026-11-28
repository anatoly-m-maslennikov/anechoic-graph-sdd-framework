"""Fault decoding for the shared backend transport."""

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError


class SharedGatewayRefusal(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _raise_fault(envelope):
    fault = envelope.get("error")
    if (
        isinstance(fault, dict)
        and isinstance(fault.get("code"), str)
        and isinstance(fault.get("message"), str)
    ):
        if fault.get("scope") == "project":
            raise SharedGatewayRefusal(fault["code"])
        if fault.get("scope") == "tool":
            raise ToolProtocolError.from_fault(fault)
    raise ToolProtocolError(
        "tool_runtime_failure", "Invalid Shared Backend response"
    )


async def _call_tool_exchange(
    self, name, arguments, public_base_url, project_instance_id, context
):
    if (
        project_instance_id is None
        and isinstance(arguments, dict)
        and "project_root" in arguments
    ):
        selected = await self.select_project(arguments["project_root"])
        project_instance_id = selected["instance_id"]
    headers = (
        {"X-Anechoic-Project-Instance": project_instance_id}
        if project_instance_id is not None
        else {}
    )
    status, envelope = await self.tool_rest(
        "POST",
        json={
            "name": name,
            "arguments": arguments,
            "session_id": context.session_id if context else None,
            "public_base_url": public_base_url,
        },
        headers=headers,
    )
    return status, envelope, project_instance_id
