---
identity:
  atom_id: AN-S-1926
context:
  container:
    component: C14
  tier: 3
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-12T01:57:07.734073+00:00'
---
## Summary

Verify Python Workflow execution with lifecycle cases

## Claim

### Prose Claim

Use disposable Projects to compare the existing Current Status route and the Python pilot. For accepted behavior, compare Action order, resulting Carriers, saved or removed references, and effects.

Check the following outcomes against the reviewed contract. Use that contract as the expected result where the old route has a known defect.

1. Moving a Backlog Epic to Active makes every Current contained Task Active at every depth. Include a direct Task, a nested Task, and an attached Draft. The Draft retains its own Status and does not block activation.
2. Invalid invocation input returns field-specific feedback before any write.
3. An Action failure after a committed effect returns the failing Action and the confirmed effect. Exercise an uncertain effect and verify it is reported as uncertain. Include pending Actions when the Workflow had already selected them. Exercise a branch that has no selected next Action.
4. Successful and failed calls retain their result details through the internal API and admitted MCP route. The Run retains the exact Workflow, Step, and Action revisions it used.
