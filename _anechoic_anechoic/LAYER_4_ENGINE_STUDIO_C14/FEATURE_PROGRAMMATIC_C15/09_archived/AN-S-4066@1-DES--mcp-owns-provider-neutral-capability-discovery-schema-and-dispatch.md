---
atom_family: SPEC
atom_id: AN-S-4066
container:
  component: C15
tier: 0
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 23:57:07 +0400
---
## Summary

MCP owns provider-neutral capability discovery, schema and dispatch

## Claim scope

MCP.

## Claim

MCP **must** own the provider-neutral Model Context Protocol discovery, schema, **and** dispatch interface through which an agent can perform **all** of the following:

- invoke active ANECHOIC Tools;
- receive ACTION_PROMPTS **or** OPERATOR_PROMPTS; **and**
- start **or** resume Workflows.

MCP **must not** own **any** of the following:

- Tool behavior;
- Prompt content;
- Workflow coordination;
- Skill procedures;
- application behavior; **or**
- agent-host-specific packaging.
