---
atom_family: SPEC
atom_id: AN-S-1631
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Keep Workflow graphs separate from Step bindings

# Summary

Keep Workflow graphs separate from Step bindings

## Scope

Workflow graph schemes and Step bindings.

## Claim

a Workflow Atom **must** own **only** its graph scheme: Step references, typed directed Relations, entry points, transition conditions, **and** terminal outcomes.

- the referenced Step Atoms own Action references, parameters, **and** input bindings.
- reusable Action Atoms own Action behavior.
- the graph **must not** independently repeat those Step bindings **or** Action definitions; folder nesting **and** file order **must not** replace its declared control flow.

## Details
