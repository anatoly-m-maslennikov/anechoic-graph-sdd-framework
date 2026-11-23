---
atom_family: SPEC
atom_id: AN-S-4239
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Discovery reflects the released MCP tools

## Claim

The root discovery catalog must include the released MCP tools, their actual names, descriptions and input/output schemas, without inventing an executable capability. It keeps `discover_tools` at the root and groups Workspace tools under Workspaces, Query tools under Queries, View tools under Views and runtime maintenance under Service, including `workbench_reread`. Existing unrelated tools remain discoverable at the root; grouping does not remove them or change callable names.

Regenerate the catalog on each local release so added, removed and changed tools are reflected. A local release is not complete when its catalog generation fails. The catalog respects the exposed tool frontier, including its blacklist and quarantine decisions, and does not execute tools or Workflows. This generated catalog describes the released registry; it is not proof that every tool will succeed for every Project request.
