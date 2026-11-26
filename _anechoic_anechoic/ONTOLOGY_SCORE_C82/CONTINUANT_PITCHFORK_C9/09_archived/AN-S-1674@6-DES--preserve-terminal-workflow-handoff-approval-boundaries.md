---
atom_family: SPEC
atom_id: AN-S-1674
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Preserve terminal Workflow handoff approval boundaries

# Summary

Preserve terminal Workflow handoff approval boundaries

## Scope

a terminal Workflow handoff from an Agentic Step Invocation.

## Claim

a terminal Workflow handoff **must** end the predecessor Run **and** let the executor admit a separate successor under `CA-R-1520-CORE_META_MODEL-GENERAL-REQUIREMENT--return-workflow-handoffs-through-terminal-results`. a session instruction **must not** silently resume an ended Run **or** bypass approval.

## Details
