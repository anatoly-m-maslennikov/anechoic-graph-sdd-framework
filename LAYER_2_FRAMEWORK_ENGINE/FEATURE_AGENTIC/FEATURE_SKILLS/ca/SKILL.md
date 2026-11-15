---
name: ca
description: "Use CAPRMEDIO through its MCP tools. Use for $ca, /ca, or CAPRMEDIO requests."
---

# CA

Use the host-configured CAPRMEDIO MCP for all CAPRMEDIO operations.

1. Discover the live MCP tools and select the ones needed for the request.
2. Before using each tool for the first time in the session, read its MCP help. If there is no dedicated help, read the advertised description and input schema. Follow the server and tool instructions, including prerequisites and required context.
3. Use the explicit Project root from the host or user. Pass it unchanged wherever the tool accepts `project_root` and reuse the context returned for follow-up calls.
4. Verify the returned result. If MCP, a required tool, or the Project binding is unavailable, report the blocker.
