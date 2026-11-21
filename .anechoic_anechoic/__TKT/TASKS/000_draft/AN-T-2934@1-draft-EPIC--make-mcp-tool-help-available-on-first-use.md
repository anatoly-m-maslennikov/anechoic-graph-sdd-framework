---
atom_family: TKT
atom_id: AN-T-2934
structure:
  container:
    component: C21
  priority: 2
context:
  template: task
  label: Epic
relations:
  REFERENCES:
  - AN-S-1958
  - AN-S-511
  - AN-T-1658
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T19:47:08.788570+00:00'
---
## Summary

Make MCP tool help available on first use

## Objective

Give the AI Agent up to three lines of help for the selected MCP tool.
Use the same help in tool discovery and `$ane`. Load it only when needed,
before the first call to that tool in a new session or after compaction.

## Work

### Stage 1. Prepare the Spec

1. Update the MCP tool help Spec to use the existing registry as the
   single source of help.
2. Define the Codex fallback for help the agent has yet to read.
3. Update the Main Skill Spec for `$ane` and for following MCP
   instructions within the Operator's authorization.

### Stage 2. Implement and verify

1. Use Task creation as the first case. Reuse its tool description.
2. Test first use, repeated calls, and first use after compaction.

## Definition of Done

The agent receives the same short help before execution, at most once
per tool between compactions. Unused tools add no help to session
context.
