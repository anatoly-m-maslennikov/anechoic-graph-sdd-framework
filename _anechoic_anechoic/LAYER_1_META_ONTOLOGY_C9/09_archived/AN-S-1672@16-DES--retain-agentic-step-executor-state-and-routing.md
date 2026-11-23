---
atom_family: SPEC
atom_id: AN-S-1672
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-29 07:45:28 +0400
---
## Summary

Retain Agentic Step executor state **and** routing

## Claim scope

execution coordination during dispatch **or** resumption of an Agentic Step, involving the executor together with the participating session **or** separate Agent context.

## Claim

the executor **must** retain execution state **and** select subsequent Steps from the Workflow's declared transitions. the participating session **or** separate Agent context performs the requested Action; it need **not** reconstruct **or** remember what the Workflow will do next.

## Details
