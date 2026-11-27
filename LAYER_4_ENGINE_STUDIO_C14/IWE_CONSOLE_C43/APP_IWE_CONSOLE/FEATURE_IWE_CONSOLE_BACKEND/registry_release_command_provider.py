"""Return host commands for the Project release entry point."""

from __future__ import annotations

from mcp import types


RELEASE_COMMAND_TOOLS = frozenset(
    {"local_release_command", "public_release_command"}
)


class ReleaseCommandProvider:
    def __init__(self, project_root, gateway):
        self.workbench = gateway.workbench

    async def call(self, name, arguments):
        return await self.workbench.release_command(name, arguments)

    async def close(self):
        return None


def create_provider(project_root, gateway):
    return ReleaseCommandProvider(project_root, gateway)


def tool_descriptors():
    run_id = {
        "type": "string",
        "description": "Operator-selected release run ID.",
    }
    return tuple(
        types.Tool(
            name=name,
            description=f"Return the host uv command for {'Public Release' if name == 'public_release_command' else 'Local Release'}.",
            input_schema={
                "type": "object",
                "properties": {
                    "run_id": run_id,
                    **(
                        {
                            "base": {
                                "type": "string",
                                "description": "PR base Git ref. Defaults to origin/main.",
                            },
                            "head": {
                                "type": "string",
                                "description": "PR head Git ref. Defaults to amm/dev.",
                            },
                            "content_draft": {
                                "type": "string",
                                "description": "Host path to the reviewed changelog evidence JSON.",
                            },
                        }
                        if name == "public_release_command"
                        else {}
                    ),
                },
                "required": ["run_id"],
                "additionalProperties": False,
            },
        )
        for name in sorted(RELEASE_COMMAND_TOOLS)
    )
