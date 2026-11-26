---
atom_family: SPEC
atom_id: AN-S-1672
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: active
  version: 20
  updated_at: '2026-11-25T21:47:23.181838+00:00'
---
## Summary

Retain Agentic Step executor state **and** routing

## Claim

### Prose Claim


execution coordination during dispatch **or** resumption of an Agentic Step, involving the executor together with the participating session **or** separate Agent context.


the executor **must** retain execution state **and** select subsequent Steps from the Workflow's declared transitions. the participating session **or** separate Agent context performs the requested Action; it need **not** reconstruct **or** remember what the Workflow will do next.
