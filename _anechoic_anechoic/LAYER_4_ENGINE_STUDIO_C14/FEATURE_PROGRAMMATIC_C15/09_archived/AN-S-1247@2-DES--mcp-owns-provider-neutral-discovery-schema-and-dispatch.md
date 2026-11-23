---
atom_family: SPEC
atom_id: AN-S-1247
container:
  component: C15
tier: 0
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

MCP owns provider-neutral discovery, schema and dispatch

## Claim scope

MCP.

## Claim

MCP **must** own the provider-neutral Model Context Protocol discovery, schema, **and** dispatch interface through which an agent:

- invokes active ANECHOIC Tools;
- receives ACTION_PROMPTS **or** OPERATOR_PROMPTS; **and**
- starts **or** resumes Workflows.

MCP **must not** own **any** of the following:

- Tool behavior;
- Prompt content;
- Workflow coordination;
- Skill procedures;
- application behavior; **or**
- agent-host-specific packaging.
