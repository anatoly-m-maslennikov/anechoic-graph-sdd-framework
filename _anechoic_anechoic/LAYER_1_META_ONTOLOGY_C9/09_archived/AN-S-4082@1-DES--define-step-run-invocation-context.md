---
atom_family: SPEC
atom_id: AN-S-4082
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 10:03:18 +0400
---
## Summary

Define Step Run Invocation Context

## Claim

Invocation Context is the structured information supplied when dispatching or resuming an Agentic Step Run. It binds the Workflow Run and Step Run, admitted definitions, inputs or accessible references, relevant results and effects, permissions, and required output. It has no direct scalar value. CA-R-1789 governs sufficiency and delivery; the context is not an Action definition, another workflow procedure, or an automatic grant of authority.

### Formal claim

```text
Entity/Object/Occurrent/Execution/Step Run.Invocation Context{0}
```
