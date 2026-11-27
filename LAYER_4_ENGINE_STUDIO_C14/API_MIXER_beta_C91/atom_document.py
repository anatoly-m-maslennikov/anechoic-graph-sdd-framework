"""Expose the selected Project's admitted Atom document."""
import httpx2
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .admission import failure, peer

NAME = "iwe_console_atom_document"


class DocumentArguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    ref_id: str = Field(pattern=r"^[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?$")


def descriptor():
    return {"name": NAME, "description": "Read an admitted Atom revision and its authored Markdown body.",
            "annotations": {"readOnlyHint": True, "destructiveHint": False,
                            "idempotentHint": True, "openWorldHint": False},
            "inputSchema": {"type": "object", "properties": {"ref_id": {"type": "string"}},
                            "required": ["ref_id"], "additionalProperties": False}}


async def invoke(args, orchestrator, binding, instance_id):
    try:
        request = DocumentArguments.model_validate(args)
    except ValidationError:
        return failure("tool_input_invalid", "Invalid Atom reference")
    if binding is None:
        return failure("workbench_unavailable", "Managed Orchestrator binding is unavailable")
    try:
        reply = await peer(orchestrator, "POST", "/jobs/atom-document", timeout=45,
                           json={**binding, "instance_id": instance_id, **request.model_dump()})
        if "error" in reply:
            return failure(reply['error']['code'], reply['error']['message'])
        if not isinstance(reply['result'], dict):
            raise ValueError("Invalid Atom document")
        return {"result": {"value": reply['result'], "text": None}}
    except (httpx2.HTTPError, ValueError, TypeError, KeyError):
        return failure("workbench_unavailable", "Atom document is unavailable")
