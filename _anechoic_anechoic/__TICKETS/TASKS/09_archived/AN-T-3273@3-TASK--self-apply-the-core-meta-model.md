---
atom_family: TKT
atom_id: AN-T-3273
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 07:12:55 +0400
---
## Summary

Self-Apply the Core Meta-Model

# Self-Apply the Core Meta-Model

**when** CA-P-944 is Done, **then** the Assignee **must** apply the complete current Core Meta-Model authority to **all** Active Core Meta-Model Atoms **until** the Core-only authority reaches a reproducible fixed point.

## Scope

`((all CA-P-944 source entries whose owning Scope Unit is CORE_META_MODEL) union (every replacement, archive, or new Core Meta-Model Atom required solely to repair a discovered Core self-conformance defect) union (the Core-only Entity, Term, Subject, Claim, relation, dependency, and Carrier graph Projections))`

## Definition of Done

the Task is **not done if** (**any** in-scope Atom violates current Core authority **or** **any** one-Atom, one-Claim, Claim-Scope, CCE, Term, Subject, relation, Entity, Type, Status, Summary, filename, frontmatter, Carrier, revision, lifecycle, **or** graph invariant fails **or** **any** governed Term is missing, multiply defined, incorrectly capitalized, **or** absent from its governing Subjects **or** **any** prohibited cycle, unresolved dependency, duplicate identity, **or** stale replacement remains **or** Local Configuration authority is used to justify a Core invariant **or** another Core-only application pass changes the validated result **or** **any** semantic choice below 99 percent confidence is made **without** the Operator).

## Details

keep the Core Meta-Model necessary, sufficient, open to registered extensions, **and** independent from ANECHOIC-specific Local Configuration. archive every replaced revision **before** activating its successor.
