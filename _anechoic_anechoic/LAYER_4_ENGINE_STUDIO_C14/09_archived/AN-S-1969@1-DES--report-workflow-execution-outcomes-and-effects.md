---
atom_family: SPEC
atom_id: AN-S-1969
container:
  component: C14
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T01:57:01.398751+00:00'
---
## Summary

Report Workflow execution outcomes and effects

## Claim

### Prose Claim

The Engine returns a structured outcome for each Workflow invocation. A successful Run reports saved and removed Object references and confirmed effects, where applicable. If an Action fails, report the failed Action, the reason, and any confirmed effects already applied. Include the Actions left unrun when the Workflow had already selected them. Distinguish uncertain effects from confirmed effects.

Reject invalid Workflow invocation inputs before any Action can apply effects. Identify each rejected field that needs correction. If a later Action rejects an input or source revision, report that Action failure with the effects already applied. The internal API and admitted MCP routes preserve these outcome details.
