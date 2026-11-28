"""Shared gateway in-memory fixtures."""

from pathlib import Path
from mcp import types


def _tool(name="echo", field="request"):
    return types.Tool(
        name=name,
        inputSchema={
            "type": "object",
            "properties": {field: {"type": "string"}},
            "required": [field],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    )


class _Gateway:
    tools_by_root = {}
    blacklist_by_root = {}
    hold = None

    def __init__(self, root, *, selection):
        self.root, self.selection = Path(root), selection
        self.tool_blacklist = self.blacklist_by_root.get(
            str(root), frozenset()
        )
        self.ready = True
        self.tools = self.tools_by_root[str(root)]
        self.closed = False

    async def initialize(self):
        return None

    async def close(self):
        self.closed = True

    async def ensure_current(self):
        registry = getattr(self, "registry", None)
        if registry is not None:
            registry.ensure_current()

    async def call(self, _context, params, **_kwargs):
        if self.hold is not None:
            await self.hold.wait()
        return types.CallToolResult(
            content=[],
            structuredContent={
                "root": str(self.root),
                "arguments": params.arguments,
            },
        )


class _Session(_Gateway):
    def __init__(self, root, *, selection):
        super().__init__(root, selection=selection)
        self.tools = [
            tool.model_dump(mode="json", by_alias=True) for tool in self.tools
        ]

    async def call_tool(
        self,
        name,
        arguments,
        *,
        session_id,
        public_base_url,
        asserted_project_root,
    ):
        result = await self.call(
            None, types.CallToolRequestParams(name=name, arguments=arguments)
        )
        return {"value": result.structured_content, "text": None}
