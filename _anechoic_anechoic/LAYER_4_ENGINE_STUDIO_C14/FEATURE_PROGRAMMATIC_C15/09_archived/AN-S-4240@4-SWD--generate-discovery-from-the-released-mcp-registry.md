---
atom_family: SPEC
atom_id: AN-S-4240
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Generate discovery from the released MCP registry

## Claim

After local release has started the new MCP and confirmed readiness, run one script that reads its complete native `tools/list` response, including any pagination, and regenerates the root discovery catalog. Use the existing MCP SDK and actual tool descriptors. Do not maintain a second list of tools or infer availability from source-folder names.

Use `discover_tools` for root discovery. An empty discovery request reads the generated catalog through the existing canonical provider; existing explicit query and Scope Unit selectors keep their declared source-discovery behavior. If the root catalog is missing or invalid, report an explicit error; do not silently rescan, repair, retry or invent a catalog.

Group `workspace_*` tools under Workspaces, `query_*` tools under Queries and `view_*` tools under Views. Group the existing MCP reload/status operations, `<service>_restart` maintenance tools and `workbench_reread` under Service. Put `discover_tools` first at the root; leave unclassified existing tools at the root, sorted by exact name. Every descriptor appears once. This is a discovery tree, not nested callable MCP names.

Preserve actual names, descriptions, schemas and annotations from the SDK. Write the generated JSON through the existing atomic writer, with temporary staging under the selected Project's `.anechoic_tmp/` and a verified same-filesystem replacement boundary. Do not create a temporary file beside the runtime catalog. A failed write must not expose half JSON. Report generation failures to stderr and fail the release step. Do not add a watcher, another registry, a database, aliases, tool execution or a Business Journal event.

## Sources

CA-R-2785.
