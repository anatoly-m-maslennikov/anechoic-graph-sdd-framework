
"""Read-only MCP Apps compatibility probe, served by the existing MCP gateway."""

from pathlib import Path
from typing import Any

from mcp import MCPError, types

URI = "ui://anechoic/iwe-console-compatibility-v2.html"
LEGACY_URI = "ui://anechoic/workbench-compatibility-v2.html"
WORKBENCH_URI = "ui://anechoic/iwe-console.html"
LEGACY_WORKBENCH_URI = "ui://anechoic/workbench.html"
MIME_TYPE = "text/html;profile=mcp-app"
TOOL_NAMES = ("iwe_console_ui_probe", "iwe_console_ui_ping", "workbench_ui_probe", "workbench_ui_ping")
WORKBENCH_HTML = (Path(__file__).resolve().parent.parent / "FEATURE_IWE_CONSOLE_FRONTEND" / "dist" / "mcp-app.html")


def tools() -> tuple[types.Tool, ...]:
    return tuple(types.Tool(
        name=name,
        description=("Render the ANECHOIC MCP App compatibility probe without a browser or project data."
                     if name in (TOOL_NAMES[0], TOOL_NAMES[2]) else "Read-only check of the MCP App tool bridge."),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
        output_schema={"type": "object", "properties": {"message": {"type": "string"}},
                       "required": ["message"], "additionalProperties": False},
        annotations=types.ToolAnnotations(read_only_hint=True, destructive_hint=False,
                                          idempotent_hint=True, open_world_hint=False),
        _meta={"ui": {"resourceUri": URI}} if name in (TOOL_NAMES[0], TOOL_NAMES[2]) else None,
    ) for name in TOOL_NAMES)


def call(name: str) -> dict[str, str]:
    if name not in TOOL_NAMES:
        raise ValueError("Unknown UI probe tool")
    return {"message": "ANECHOIC MCP App resource loaded" if name in (TOOL_NAMES[0], TOOL_NAMES[2]) else "Tool bridge passed"}


async def list_resources(_context: Any, _params: Any) -> types.ListResourcesResult:
    return types.ListResourcesResult(resources=[
        types.Resource(name="ANECHOIC UI compatibility probe", uri=URI, mime_type=MIME_TYPE),
        types.Resource(name="ANECHOIC IWE Console", uri=WORKBENCH_URI, mime_type=MIME_TYPE),
    ])


async def read_resource(_context: Any, params: types.ReadResourceRequestParams) -> types.ReadResourceResult:
    if str(params.uri) in (URI, LEGACY_URI):
        text = Path(__file__).with_suffix(".html").read_text()
    elif str(params.uri) in (WORKBENCH_URI, LEGACY_WORKBENCH_URI):
        try:
            text = WORKBENCH_HTML.read_text()
        except FileNotFoundError as error:
            raise MCPError(-32002, "Unknown UI resource") from error
    else:
        raise MCPError(-32002, "Unknown UI resource")
    return types.ReadResourceResult(contents=[types.TextResourceContents(
        uri=params.uri, mime_type=MIME_TYPE, text=text,
    )])
