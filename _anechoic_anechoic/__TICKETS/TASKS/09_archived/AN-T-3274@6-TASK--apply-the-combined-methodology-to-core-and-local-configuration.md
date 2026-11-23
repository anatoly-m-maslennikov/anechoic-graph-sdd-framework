---
atom_family: TKT
atom_id: AN-T-3274
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 22:16:42 +0400
---
## Summary

Apply the Combined Methodology to Core and Local Configuration

# Apply the Combined Methodology to Core and Local Configuration

**when** CA-P-945 is Done, **then** the Assignee **must** apply the combined active Core Meta-Model **and** Local Configuration authority to **all** Active Atoms in CORE_META_MODEL **and** LOCAL_CONFIGURATION.

## Scope

`((all Active RMEDO Atoms in CORE_META_MODEL) union (all Active RMEDO Atoms in LOCAL_CONFIGURATION) union (every deterministic replacement or archive required solely by their combined unambiguous authority) union (all combined Entity, Term, Subject, Claim, relation, dependency, and Carrier graph Projections))`

## Definition of Done

the Task is **not done if** (**any** unambiguous combined-authority conformance repair remains unapplied **or** **any** Core **or** Local Configuration Atom violates an applicable Claim, Claim-Scope, CCE, Term, Subject, relation, Entity, Type, Status, Summary, Carrier, revision, lifecycle, **or** graph invariant **or** **any** possible conflict, gap, ambiguity, unresolved dependency, duplicate definition, invalid cycle, source mismatch, **or** Projection drift is omitted from an exact reproducible finding set **or** a semantic conflict is silently resolved through layer order, path order, compiler preference, **or** inference **or** another combined-authority application pass changes an unreported part of the result).

## Details

apply **only** authority that has one unambiguous result. preserve every unresolved semantic choice for explicit conflict disposition **after** the Local Configuration expansion boundary is checked.
