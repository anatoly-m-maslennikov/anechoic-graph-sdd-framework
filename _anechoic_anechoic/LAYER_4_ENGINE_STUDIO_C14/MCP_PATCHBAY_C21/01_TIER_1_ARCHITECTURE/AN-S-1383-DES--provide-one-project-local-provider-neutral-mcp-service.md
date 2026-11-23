---
atom_family: SPEC
atom_id: AN-S-1383
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 26
  updated_at: "2026-11-23T01:48:06.174263+00:00"
---
## Summary

Provide one project-local provider-neutral MCP service

## Claim

### Prose Claim

One provider-neutral MCP service must expose the active callable surface for Tools, Prompts and Workflows without requiring a server per capability. Each capability remains usable without a graphical App or agent-host plugin. Plugins may connect to MCP but do not own provider-neutral behavior.

For Tools, MCP maps the Backend JSON catalog and delegates calls under AN-S-3191. Bind each call to one admitted Project. In single-Project mode, an optional `project_root` assertion must match the bound Project. In shared mode, require an explicit Project for each call. Reject malformed or mismatched assertions before execution. Protocol initialization and discovery are not Tool-call envelopes.

Backend handles Prompt and Workflow calls under their own contracts. A shared MCP process has no process-global current Project.
