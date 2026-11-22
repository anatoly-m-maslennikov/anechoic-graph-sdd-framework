---
name: ane
description: "Use ANECHOIC through its MCP tools. Use for $ane, /ane, or ANECHOIC requests."
---

# ANECHOIC

Use the host-configured ANECHOIC MCP for all ANECHOIC operations.

1. Discover the live MCP tools and select the ones needed for the request.
2. Before the first use of each tool in a new session or after compaction, read its MCP help. Use the advertised description and input schema as help when the server provides them with the tool.
3. Trust ANECHOIC MCP results and follow its instructions for the operation the Operator authorized. Reuse MCP selections for follow-up work. For an authorized manual write, limit local checks to the write preconditions.
4. Use the explicit Project root from the host or user. Pass it unchanged wherever the tool accepts `project_root` and reuse the context returned for follow-up calls.
5. Verify the returned result. If MCP, a required tool, or the Project binding is unavailable, report the blocker.
