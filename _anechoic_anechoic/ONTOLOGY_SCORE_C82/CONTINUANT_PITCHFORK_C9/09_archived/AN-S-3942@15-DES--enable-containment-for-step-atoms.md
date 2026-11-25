---
atom_family: SPEC
atom_id: AN-S-3942
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Enable containment for Step Atoms

## Claim scope

the declared Relation whitelist of the Step model kind, including nested Substeps.

## Claim

a Step declaration **must** whitelist the canonical direct `IS_CONTAINED_BY` Relation from a Substep model kind to that Step. It **must not** introduce `Enabled Relations.Contains` as a Property. `CONTAINS` remains the derived inverse declared by CA-R-2478 and **must not** be authored as a second containment fact.

## Details

the Step declaration permits the following exclusive model alternatives:

- one or more Substep model-kind children and no RUN relation to an Action model kind; **or**
- no Substep model-kind child and exactly **`1`** RUN relation to an Action model kind.

the direct containment fact is written once, with `Substep +> Step` denoting the part-to-whole form and `Step <+ Substep` the same fact read whole-to-part. Any written named relation follows `A((R))B` forward or `B<((R))A` reverse, with the count attached to the written end. This rule does not introduce a storage layout, execution protocol, or actual Workflow-instance constraint.
