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
  version: 21
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Keep Workflow graphs separate from Step bindings

## Claim scope

Workflow graph schemes and Step bindings.

## Claim

a Workflow Atom **must** own **only** its graph scheme: Step references, declared order and structural Relations, entry points, **and** terminal outcomes. a Conditional Step definition owns its result-based routing; the Workflow graph does not use a separate result-transition Relation.

- the referenced Step Atoms own Action references, parameters, **and** input bindings.
- reusable Action Atoms own Action behavior.
- the graph **must not** independently repeat those Step bindings **or** Action definitions; folder nesting **and** file order **must not** replace its declared control flow.
